# toml-argparse

[![Release](https://img.shields.io/github/v/release/florianmahner/toml-argparse)](https://img.shields.io/github/v/release/florianmahner/toml-argparse)
[![Build status](https://img.shields.io/github/actions/workflow/status/florianmahner/toml-argparse/main.yml?branch=main)](https://github.com/florianmahner/toml-argparse/actions/workflows/main.yml?query=branch%3Amain)
![example workflow](https://github.com/florianmahner/toml-argparse/actions/workflows/main.yml/badge.svg)
[![codecov](https://codecov.io/gh/florianmahner/toml-argparse/branch/main/graph/badge.svg)](https://codecov.io/gh/florianmahner/toml-argparse)
[![License](https://img.shields.io/github/license/florianmahner/toml-argparse)](https://img.shields.io/github/license/florianmahner/toml-argparse)
![code style](https://img.shields.io/badge/code%20style-black-black)



Command-line-tool to use [toml](https://toml.io/en/) files in combinations with [argparse](https://docs.python.org/3/library/argparse.html).


- **Github repository**: <https://github.com/florianmahner/toml-argparse/>
- **Documentation** <https://florianmahner.github.io/toml-argparse/>


## Example

[toml](https://toml.io/en/) files usually come in the following form:

```toml
# This is a TOML document
title = "TOML Example"

[owner]
name = "Florian P. Mahner"
id = 20
```

Say we want to use most of the fields from the toml file also for our python project. To do this we would commonly build an ArgumentParser with the following fields:

```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--title", type=str, default="")
parser.add_argument("--name", type=str, default="")
parser.add_argument("--id", type=int, default=0)
parser.parse_args()
```

For large projects with a lot of hyperparameters the number of arguments can become very large (especially for deep learning projects). To create reproducible experiments, we can now use the `toml_argparse.ArgumentParser()` to parse the toml arguments:

```python
from toml_argparse import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--title", type=str, default="")
parser.add_argument("--name", type=str, default="")
parser.add_argument("--id", type=int, default=0)
parser.parse_args()
```

We can then parse the toml file from the command line:

```bash
python experiment.py --config "example.toml"
```

This will replace our argparse defaults with the ones specified in the toml file.


## Contributing
Clone the repository first. Then, install the environment and the pre-commit hooks with

```bash
make install
```

The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
