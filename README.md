[![PyPI version](https://badge.fury.io/py/sos-papermill.svg)](https://badge.fury.io/py/sos-papermill)
[![Build Status](https://travis-ci.org/vatlab/sos-papermill.svg?branch=master)](https://travis-ci.org/vatlab/sos-papermill)


# Papermill engine for SoS Notebook

This is a paper mill engine for the execution of SoS Polyglot Notebook.

## Installation

```
pip install sos-papermill
```

## Usage

```
papermill --engine sos [other options]
```

Note that `parameters` can be defined in both `SoS` and subkernel cells. In the latter case
the parameters should be passed in Python syntax and the parameters will be automatically
transferred to the subkernel using a `%put` magic.