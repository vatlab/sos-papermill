#!/usr/bin/env python3
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.

import re
from nbformat.v4 import output_from_msg

from papermill.engines import Engine
from papermill.utils import merge_kwargs, remove_args
from papermill.log import logger
from papermill.preprocess import PapermillExecutePreprocessor
from papermill.translators import papermill_translators, PythonTranslator

from sos.converter import extract_workflow


class SoSPaperMillPreprocessor(PapermillExecutePreprocessor):

    def __init__(self, filename, *args, **kwargs):
        super(SoSPaperMillPreprocessor, self).__init__(*args, **kwargs)
        self._filename = filename
        self._params_kernel = 'SoS'
        self._parameters = []

    def _prepare_meta(self, cell):

        if not hasattr(cell.metadata, 'kernel'):
            cell.metadata['kernel'] = 'SoS'

        if hasattr(cell.metadata, 'tags'):
            if 'parameters' in cell.metadata.tags:
                self._params_kernel = cell.metadata['kernel']
            if 'injected-parameters' in cell.metadata.tags and self._params_kernel != 'SoS':
                cell.source = f'%put {" ".join(self._parameters)} --to {self._params_kernel}\n' + cell.source

        meta = {
            'use_panel': False,
            'cell_id': '0',
            'path': self._filename,
            'batch_mode': True,
            'cell_kernel': cell.metadata.kernel
        }
        if re.search(
                r'^%sosrun($|\s)|^%sossave($|\s)|^%preview\s.*(-w|--workflow).*$',
                cell.source, re.MULTILINE):
            meta['workflow'] = self._workflow
        return meta

    def run_cell(self, cell, cell_index=0, store_history=True):
        # sos is the additional meta information sent to kernel
        sos_meta = self._prepare_meta(cell)
        content = dict(
            code=cell.source,
            silent=False,
            store_history=store_history,
            user_expressions='',
            allow_stdin=False,
            stop_on_error=False,
            sos=sos_meta)
        msg = self.kc.session.msg('execute_request', content)
        self.kc.shell_channel.send(msg)
        msg_id = msg['header']['msg_id']

        # the reset is copied from https://github.com/jupyter/nbconvert/blob/master/nbconvert/preprocessors/execute.py
        # because we only need to change the first line

        #  msg_id = self.kc.execute(cell.source)

        self.log.debug(
            f"Executing cell {cell_index} with kernel {content['sos']['cell_kernel']}:\n{cell.source}"
        )
        exec_reply = self._wait_for_reply(msg_id, cell)

        outs = cell.outputs = []

        while True:
            try:
                # We've already waited for execute_reply, so all output
                # should already be waiting. However, on slow networks, like
                # in certain CI systems, waiting < 1 second might miss messages.
                # So long as the kernel sends a status:idle message when it
                # finishes, we won't actually have to wait this long, anyway.
                msg = self.kc.iopub_channel.get_msg(timeout=self.iopub_timeout)
            except Empty:
                self.log.warning("Timeout waiting for IOPub output")
                if self.raise_on_iopub_timeout:
                    raise RuntimeError("Timeout waiting for IOPub output")
                else:
                    break
            if msg['parent_header'].get('msg_id') != msg_id:
                # not an output from our execution
                continue

            msg_type = msg['msg_type']
            self.log.debug("output: %s", msg_type)
            content = msg['content']

            # set the prompt number for the input and the output
            if 'execution_count' in content:
                cell['execution_count'] = content['execution_count']

            if msg_type == 'status':
                if content['execution_state'] == 'idle':
                    break
                else:
                    continue
            elif msg_type == 'execute_input':
                continue
            elif msg_type == 'clear_output':
                outs[:] = []
                # clear display_id mapping for this cell
                for display_id, cell_map in self._display_id_map.items():
                    if cell_index in cell_map:
                        cell_map[cell_index] = []
                continue
            elif msg_type.startswith('comm'):
                continue

            display_id = None
            if msg_type in {
                    'execute_result', 'display_data', 'update_display_data'
            }:
                display_id = msg['content'].get('transient',
                                                {}).get('display_id', None)
                if display_id:
                    self._update_display_id(display_id, msg)
                if msg_type == 'update_display_data':
                    # update_display_data doesn't get recorded
                    continue

            try:
                out = output_from_msg(msg)
            except ValueError:
                self.log.error("unhandled iopub msg: " + msg_type)
                continue
            if display_id:
                # record output index in:
                #   _display_id_map[display_id][cell_idx]
                cell_map = self._display_id_map.setdefault(display_id, {})
                output_idx_list = cell_map.setdefault(cell_index, [])
                output_idx_list.append(len(outs))

            outs.append(out)

        return exec_reply, outs

    def preprocess(self, nbman, *args, **kwargs):
        self._workflow = extract_workflow(nbman.nb)
        self._parameters = list(
            nbman.nb.metadata['papermill']['parameters'].keys())
        return super(SoSPaperMillPreprocessor,
                     self).preprocess(nbman, *args, **kwargs)


class SoSExecutorEngine(Engine):
    """
    A notebook engine representing an extended nbconvert process to execute SoS Notebook.
    """

    @classmethod
    def execute_managed_notebook(cls,
                                 nb_man,
                                 kernel_name,
                                 log_output=False,
                                 stdout_file=None,
                                 stderr_file=None,
                                 start_timeout=60,
                                 execution_timeout=None,
                                 **kwargs):
        """
        Performs the actual execution of the parameterized notebook locally.
        Args:
            nb (NotebookNode): Executable notebook object.
            kernel_name (str): Name of kernel to execute the notebook against.
            log_output (bool): Flag for whether or not to write notebook output to the
                               configured logger.
            start_timeout (int): Duration to wait for kernel start-up.
            execution_timeout (int): Duration to wait before failing execution (default: never).
        Note: The preprocessor concept in this method is similar to what is used
        by `nbconvert`, and it is somewhat misleading here. The preprocesser
        represents a notebook processor, not a preparation object.
        """

        # Exclude parameters that named differently downstream
        safe_kwargs = remove_args(['timeout', 'startup_timeout'], **kwargs)

        # Nicely handle preprocessor arguments prioritizing values set by engine
        final_kwargs = merge_kwargs(
            safe_kwargs,
            timeout=execution_timeout
            if execution_timeout else kwargs.get('timeout'),
            startup_timeout=start_timeout,
            kernel_name=kernel_name,
            log=logger,
            log_output=log_output,
            stdout_file=stdout_file,
            stderr_file=stderr_file,
        )
        preprocessor = SoSPaperMillPreprocessor(
            filename=nb_man.nb.metadata.papermill['input_path'], **final_kwargs)
        preprocessor.preprocess(nb_man, safe_kwargs)


# register Python Translater for kernel sos
papermill_translators.register("sos", PythonTranslator)