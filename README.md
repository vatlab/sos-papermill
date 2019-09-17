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


## Note

The `parameters` cells have to in SoS kernel because papermill will only inject SoS cells.
A warning will be given if non-SoS parameter cells are encountered.