# tomlparse

[![Release](https://img.shields.io/github/v/release/florianmahner/toml-argparse)](https://img.shields.io/github/v/release/florianmahner/toml-argparse)
[![Build status](https://img.shields.io/github/actions/workflow/status/florianmahner/toml-argparse/main.yml?branch=main)](https://github.com/florianmahner/toml-argparse/actions/workflows/main.yml?query=branch%3Amain)
![example workflow](https://github.com/florianmahner/toml-argparse/actions/workflows/main.yml/badge.svg)
[![codecov](https://codecov.io/gh/florianmahner/toml-argparse/branch/main/graph/badge.svg)](https://codecov.io/gh/florianmahner/toml-argparse)
[![License](https://img.shields.io/github/license/florianmahner/toml-argparse)](https://img.shields.io/github/license/florianmahner/toml-argparse)
![code style](https://img.shields.io/badge/code%20style-black-black)


toml-argparse is a Python library and command-line tool that allows you to use [TOML](https://toml.io/en/) configuration files in conjunction with the [argparse module](https://docs.python.org/3/library/argparse.html). It provides a simple and convenient way to handle your python projects, leveraging the strengths of both TOML and argparse.


# Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
    1. [Basic Example](#basic-example)
    2. [Extended Example](#extended-example)
5. [Contributing](#contributing)


## Installation

You can install the library using pip

```bash
pip install toml-argparse
```


## Usage

Using toml-argparse is straightforward and requires only a few extra steps compared to using argparse alone.

### Basic Example

You first define your configuration options in a TOML file. TOML files are highly flexible and include a lot of native types. Have look [here](https://toml.io/en/v1.0.0) for an extensive list.  TOML files usually come in the following form:

```toml
# This is a very basic TOML file
foo = 10
bar = "hello"
```

At the core of this module is the  [TOML ArgumentParser](https://github.com/florianmahner/toml-argparse/blob/main/toml_argparse/argparse.py), a simple wrapper of the original argparse module. To use the TOML arguments for our project, we we would create an `ArgumentParser` as usual:

```python
from toml_argparse import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--foo", type-int, default=0)
parser.add_argumetn("--bar", type=str, default="")
parser.parse_args()
```

This is just a simple example with two arguments. But for larger projects with many hyperparameters, the number of arguments can quickly grow, and the TOML file provides an easy way to collect and store different hyperparameter configurations. Every TOML ArgumentParser has a `config` argument defined that we can pass using the following command-line syntax:

```bash
python experiment.py --config "example.toml"
```

This will replace the default values from the ArgumentParser with the TOML values.

### Extended Example

TOML files have the ability to separate arguments into different sections (called `tables`), which are represented by nested dictionaries:

```toml
# This is a TOML File

# Parameters without a prededing [] are not part of a table (called root-table)
foo = 10
bar = "hello"

# These arguments are part of the table [general]
[general]
foo = 20

# These arguments are part of the table [root]
[root]
bar = "hey"
```

If we would load this TOML file as usual this would return a dict `{"foo": 10, "bar": "hello", "general": {"foo": 20}, "root" : {"bar": "hey"}}`. Note that `foo` and `bar` are overloaded and defined twice. To specify the values we wish to take each TOML ArgumentParser has two arguments defined:

1. `table`
2. `root-table`

We can use these directly from the command-line:

```bash
python experiment.py --config "example.toml" --table "general"
```

In this case the `root-table` is not defined. In this case the arguments at the top of the file without a table are taken and parsing would return the following dict `{"foo": 20, "bar": "hello"}`. Note that `table` arguments override arguments from the `root-table`. 

We can also specify the root-table:

```bash
python experiment.py --config "example.toml" --table "general" --root-table "root"
```

which would return the following dict `{"foo: 20", "bar": "hey"}` and override the arguments from the top of the TOML file.

In general, we have the following hierarchy of arguments:
1. Arguments passed through the command line are selected over TOML
           arguments, even if both are passed
2. Arguments from the TOML file are preferred over the default arguments
3. Arguments from the TOML with a section override the arguments without a section

This means that we can also override arguments in the TOML file from the command-line:

```bash
python experiment.py --config "example.toml" --table "general" --foo 100
```


## Contributing

Please have a look at the contribution guidlines in `Contributing.rst`.

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
