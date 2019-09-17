[![PyPI version](https://badge.fury.io/py/sos-papermill.svg)](https://badge.fury.io/py/sos-papermill)
[![Build Status](https://travis-ci.org/vatlab/sos-papermill.svg?branch=master)](https://travis-ci.org/vatlab/sos-papermill)


# Papermill engine for SoS Notebook

This is a papermill engine for the batch execution of SoS Polyglot Notebook.

## Installation

```
pip install sos-papermill
```

or

```
conda install sos-papermill -c conda-forge
```
if you are using a conda environment.

## Usage

```
papermill --engine sos [other options]
```

Note that `parameters` can be defined in either a `SoS` or a subkernel cell but in both cases
parameters should be passed in Python syntax. Parameters defined in a subkernel will be automatically
transferred to the subkernel using a `%put` magic.
