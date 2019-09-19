[![PyPI version](https://badge.fury.io/py/sos-papermill.svg)](https://badge.fury.io/py/sos-papermill)
[![Build Status](https://travis-ci.org/vatlab/sos-papermill.svg?branch=master)](https://travis-ci.org/vatlab/sos-papermill)


# Papermill engine for SoS Notebook

[papermill](https://github.com/nteract/papermill) is a tool for parameterizing, executing, and analyzing Jupyter Notebooks. It lets you parameterize and execute notebooks in batch mode.

[SoS Notebook](https://github.com/vatlab/sos-notebook) is a [Jupyter](https://jupyter.org/) kernel that allows the use of multiple kernels in one Jupyter notebook. Using language modules that understand datatypes of underlying languages (modules [sos-bash](https://github.com/vatlab/sos-bash), [sos-r](https://github.com/vatlab/sos-r), [sos-matlab](https://github.com/vatlab/sos-matlab), etc), SoS Notebook allows data exchange among live kernels of supported languages. SoS Notebook is also a frontend to the [SoS Workflow](https://github.com/vatlab/sos) that allows the development and execution of workflows from Jupyter notebooks.

Because the default papermill executor assumes a single kernel for the entire notebook, `sos-papermill` is provided as a  customized engine for the execution of SoS notebooks.

## Installation

```
pip install sos-papermill
```

or

```
conda install sos-papermill -c conda-forge
```
if you are using a conda environment.

Note that you will need to install [`sos-notebook`](https://github.com/vatlab/sos-notebook), all relevant kernels (e.g. `bash_kernel`, `irkernel`) and related language modules (e.g. [sos-bash](https://github.com/vatlab/sos-bash), [sos-r](https://github.com/vatlab/sos-r)) to execute notebooks that use these kernels. Please refer to [Running SoS](https://vatlab.github.io/sos-docs/running.html#content) for details on how to install SoS Notebook.

## Documentation

`sos-papermill` provides `sos` engine for papermill. All you need to do is to add option `--engine sos` to any papermill command that you might use:

```
papermill --engine sos [other options]
```

For example, to execute a parametrized notebook with parameter `cutoff`, you can use command

```
papermill --engine sos my_experiment.ipynb experiment_cutoff_2.ipynb -y '{"cutoff": 2}'
```

Please refer to the [Papermill documentation](https://papermill.readthedocs.io/en/latest/) for details on the use of papermill.

Note that `parameters` can be defined in either a `SoS` or a subkernel cell but in both cases
parameters should be passed in Python syntax. Parameters defined in a subkernel will be automatically
transferred to the subkernel using a `%put` magic.
