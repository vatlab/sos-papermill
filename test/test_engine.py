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
    def test_sos_executor_engine_execute(self):
        src_nb = load_notebook('sos_python3.ipynb')
        nb = SoSExecutorEngine.execute_notebook(
            src_nb, 'sos', output_path='foo.ipynb', progress_bar=False, log_output=True
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
