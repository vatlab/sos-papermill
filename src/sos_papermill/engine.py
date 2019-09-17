#!/usr/bin/env python3
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.

from papermill.engines import PapermillEngines, Engine, PapermillExecutePreprocessor
from papermill.utils import merge_kwargs, remove_args
from papermill.log import logger

class SoSExecutorEngine(Engine):
    """
    A notebook engine representing an extended nbconvert process to execute SoS Notebook.
    """

    @classmethod
    def execute_managed_notebook(
        cls,
        nb_man,
        kernel_name,
        log_output=False,
        stdout_file=None,
        stderr_file=None,
        start_timeout=60,
        execution_timeout=None,
        **kwargs
    ):
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
            timeout=execution_timeout if execution_timeout else kwargs.get('timeout'),
            startup_timeout=start_timeout,
            kernel_name=kernel_name,
            log=logger,
            log_output=log_output,
            stdout_file=stdout_file,
            stderr_file=stderr_file,
        )
        preprocessor = PapermillExecutePreprocessor(**final_kwargs)
        preprocessor.preprocess(nb_man, safe_kwargs)


# Instantiate a PapermillEngines instance, register Handlers and entrypoints
papermill_engines = PapermillEngines()
papermill_engines.register(None, SoSExecutorEngine)
papermill_engines.register('sos', SoSExecutorEngine)
papermill_engines.register_entry_points()