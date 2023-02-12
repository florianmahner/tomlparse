# toml-argparse

[![Release](https://img.shields.io/github/v/release/florianmahner/toml-argparse)](https://img.shields.io/github/v/release/florianmahner/toml-argparse)
[![Build status](https://img.shields.io/github/actions/workflow/status/florianmahner/toml-argparse/main.yml?branch=main)](https://github.com/florianmahner/toml-argparse/actions/workflows/main.yml?query=branch%3Amain)
![example workflow](https://github.com/florianmahner/toml-argparse/actions/workflows/main.yml/badge.svg)
[![codecov](https://codecov.io/gh/florianmahner/toml-argparse/branch/main/graph/badge.svg)](https://codecov.io/gh/florianmahner/toml-argparse)
[![License](https://img.shields.io/github/license/florianmahner/toml-argparse)](https://img.shields.io/github/license/florianmahner/toml-argparse)
![code style](https://img.shields.io/badge/code%20style-black-black)


toml-argparse is a Python library and command-line tool that allows you to use [TOML](https://toml.io/en/) configuration files in conjunction with the [argparse module](https://docs.python.org/3/library/argparse.html), providing a simple and convenient way to handle configuration for your Python scripts. The library leverages the strengths of both TOML and argparse to offer a flexible and powerful solution for managing your project configurations.


§# Table of Contents
1. [Installation](#Installation)
2. [Usage](#usage)
3. [Basic Example](#basic-example)
4. [Extended Example](#extended-example)
5. Contributing


## Installation

You can install the library using pip

```bash
pip install toml-argparse
```


## Usage

Using toml-argparse is straightforward and requires only a few extra steps compared to using argparse alone. You first define your configuration options in a TOML file, then use the [TOML ArgumentParser](https://github.com/florianmahner/toml-argparse/blob/main/toml_argparse/argparse.py). 

### Basic Example

[TOML](https://toml.io/en/) files usually come in the following form:

```toml
# This is a very basic TOML file without a section
foo = 10
bar = "hello"
```


The [TOML ArgumentParser](https://github.com/florianmahner/toml-argparse/blob/main/toml_argparse/argparse.py) is a simple wrapper of the original argparse module. It therefore provides the exact same fumctionality. To use the TOML arguments for our project, we we would create an `ArgumentParser` as usual:

```python
from toml_argparse import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--foo", type-int, default=0)
parser.add_argumetn("--bar", type=str, default="")
parser.parse_args()
```

This is just a simple example with two arguments. But for larger projects with many hyperparameters, the number of arguments can quickly grow, and the TOML file provides an easy way to collect and store different hyperparameter configurations. To parse parameters from the TOML file, you would use the following command-line syntax:

```bash
python experiment.py --config "example.toml"
```

### Extended Example

TOML files have the ability to separate arguments into different sections, which are represented by nested dictionaries:

```toml
# This is a TOML File

# These are parameters not part of a section
foo = 10
bar = "hello"

[general]
foo = 20
```

If you load this TOML file as usual, it would return the following dictionary: `{"foo": 10, "bar": "hello", "General": {"foo": 20}}`. Note that `foo` is overloaded and defined twice. To load arguments from a specific section, you can use the corresponding section keyword:

```bash
python experiment.py --config "example.toml" --section "general"
```

This would return the following dict `{"foo": 20, "bar": "hello"}`. Note that section arguments override arguments without a section.

In general, we have the following hierarchy of arguments:
1. Arguments passed through the command line are selected over TOML
           arguments, even if both are passed
2. Arguments from the TOML file are preferred over the default arguments
3. Arguments from the TOML with a section override the arguments without a section

This means that we can also override arguments in the TOML file from the command-line:


```bash
python experiment.py --config "example.toml" --section "general" --foo 100
```


## Contributing

Please have a look at the contribution guidlines in `Contributing.rst`.

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
