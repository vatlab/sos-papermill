#!/usr/bin/env python3
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.
#
import os
import unittest

from papermill.iorw import load_notebook_node
from papermill.engines import NotebookExecutionManager

from sos_papermill.engine import SoSExecutorEngine


def load_notebook(notebook_name):
    notebook_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notebooks', notebook_name)
    nb = load_notebook_node(notebook_path)
    nb.metadata.papermill['input_path'] = notebook_name
    return nb

class TestSoSExecutorEngine(unittest.TestCase):

    def assertOutput(self, text, cell):
        res = ''
        for output in cell.outputs:
            if output['output_type'] == 'stream':
                res += output['text']
            elif output['output_type'] == 'execute_result':
                if 'text/plain' in output['data']:
                    res += output['data']['text/plain']
            elif output['output_type'] == 'display_data':
                if 'text/plain' in output['data']:
                    res += output['data']['text/plain']
                if 'text/markdown' in output['data']:
                    res += output['data']['text/markdown']
        self.assertTrue(text in res, f'"{text}" not seem in output, "{res}" obtained')

    def assertOutputType(self, output_type, cell):
        resTypes = []
        for output in cell.outputs:
            print(output)
            if output['output_type'] == 'stream':
                resTypes.append(output['name'])
            elif output['output_type'] in ('execute_result', 'display_data'):
                resTypes.extend(list(output['data'].keys()))
        self.assertTrue(output_type in resTypes, f'Output of type "{output_type}" not seem in output, "{resTypes}" obtained')

    def test_sos_executor_engine_execute(self):
        src_nb = load_notebook('sos_python3.ipynb')
        nb = SoSExecutorEngine.execute_notebook(
            src_nb, 'sos', output_path='foo.ipynb', progress_bar=False, log_output=False
        )
        self.assertIsNotNone(nb.metadata.papermill['start_time'])
        self.assertIsNotNone(nb.metadata.papermill['end_time'])
        self.assertFalse(nb.metadata.papermill['exception'])

        for cell in nb.cells:
            self.assertIsNotNone(cell.metadata.papermill['start_time'])
            self.assertIsNotNone(cell.metadata.papermill['end_time'])
            self.assertFalse(cell.metadata.papermill['exception'])
            self.assertEqual(
                cell.metadata.papermill['status'], NotebookExecutionManager.COMPLETED
            )
        self.assertOutput('101', nb.cells[2])

    def test_capture_expand_render(self):
        src_nb = load_notebook('capture_expand_render.ipynb')
        nb = SoSExecutorEngine.execute_notebook(
            src_nb, 'sos', output_path='foo.ipynb', progress_bar=False, log_output=False
        )
        self.assertOutput('10', nb.cells[1])
        self.assertOutput('hello', nb.cells[2])
        self.assertOutput('hello', nb.cells[3])
        self.assertOutput('header', nb.cells[4])
        self.assertOutputType('text/markdown', nb.cells[4])