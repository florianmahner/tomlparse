"""
Module for parsing command line arguments and TOML configuration files.

This module provides a class, `ArgumentParser`, which extends the functionality 
of `argparse.ArgumentParser` by allowing users to specify default values for 
arguments in a TOML file, in addition to the command line. 
"""

import argparse
import sys
from typing import Any, Dict, List, MutableMapping, Tuple

import toml


class ArgumentParser(argparse.ArgumentParser):
    """A wrapper of the argparse.ArgumentParser class that adds the ability to
    specify the values for arguments using a TOML file.

    This class extends the functionality of the standard argparse.ArgumentParser by allowing
    users to specify default values for arguments in a TOML file, in addition to the command line.
    We can use all functionalities from the argument parser as usual:

    Example:
        >>> from tomlparse import argparse
        >>> parser = argparse.ArgumentParser(description='Example argparse-toml app')
        >>> parser.add_argument('--foo', type=int, help='An example argument')
        >>> args = parser.parse_args()

    The above code will work as with the standard argparse.ArgumentParser class. We can also
    specify the default values for the arguments in a TOML file. For this the TOML ArgumentParser
    has two additional arguments: `--config` and `--table`. The `--config` argument is used
    to specify the path to the TOML file, and the `--table` argument is used to specify the
    table name in the TOML file to parse the arguments from. A TOML table is defined by a [name]
    in brackets preceding the arguments. If the `--table` argument is not specified, the arguments
    are parsed from the root table of the TOML file. We can also change
    the root table name by specifying the `--root_table` argument.

    We have the following hierarchy of arguments:
        1. Arguments passed through the command line are selected over TOML
           arguments, even if both are passed
        2. Arguments from the TOML file are preferred over the default arguments
        3. Arguments from the TOML with a table override the arguments without
           a table
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.add_argument(
            "--config",
            type=str,
            default="",
            help="Path to the configuration file.",
        )
        self.add_argument(
            "--root-table",
            type=str,
            default="",
            help="""Table in the config file that counts for all expriments. If not specified, then these
            are the top-level arguments without a [table]""",
        )
        self.add_argument(
            "--table",
            type=str,
            default="",
            help=(
                "Table name in the config file to parse arguments in addition to"
                " the root table"
            ),
        )

    def extract_args(self) -> Tuple[argparse.Namespace, argparse.Namespace]:
        """Find the default arguments of the argument parser if any and the
        ones that are passed through the command line"""
        sys_defaults = sys.argv.copy()
        sys.argv = []
        default_args = super().parse_args()
        sys.argv = sys_defaults
        cmdl_args = super().parse_args()

        return default_args, cmdl_args

    def find_changed_args(
        self, default_args: argparse.Namespace, sys_args: argparse.Namespace
    ) -> Dict[str, Any]:
        """Find the arguments that have been changed from the command
        line to replace the .toml arguments"""
        default_dict = vars(default_args)
        sys_dict = vars(sys_args)
        changed_dict: Dict[str, Any] = {}
        for key, value in default_dict.items():
            sys_value = sys_dict[key]
            if sys_value != value:
                changed_dict[key] = sys_value
        return changed_dict

    def pop_keys_(
        self, namespace: argparse.Namespace, keys: List[Any]
    ) -> argparse.Namespace:
        """Removes unnecessary keys from the namespace"""
        for key in keys:
            delattr(namespace, key)

    def load_toml(self, path: str) -> MutableMapping[str, Any]:
        try:
            config = toml.load(path)
        except FileNotFoundError as f:
            raise FileNotFoundError from f
        return config

    def remove_nested_keys(self, dictionary: Dict[str, Any]) -> Dict[str, Any]:
        new_dict = {}
        for key, value in dictionary.items():
            if not isinstance(value, dict):
                new_dict[key] = value
        return new_dict

    def parse_args(self) -> argparse.Namespace:  # type: ignore[override]
        """Parse the arguments from the command line and the TOML file
        and return the updated arguments. Same functionality as the
        `argparse.ArgumentParser.parse_args` method."""
        default_args, sys_args = self.extract_args()
        table = sys_args.table
        root_table = sys_args.root_table
        config = sys_args.config

        # These are the default arguments options updated by the command line
        if not config:
            self.pop_keys_(sys_args, ["root_table", "table", "config"])
            return sys_args

        # If a config file is passed, upodate the cmdl args with the config file unless
        # the argument is already specified in the command line
        config = self.load_toml(sys_args.config)
        changed_args = self.find_changed_args(default_args, sys_args)

        if table:
            try:
                table_config = config[table]
            except KeyError as key:
                raise KeyError from key

        else:
            self.pop_keys_(sys_args, ["table"])
            table_config = config
            table_config = self.remove_nested_keys(table_config)

        # If not empty and there exists a table and a root table, select the root
        #  table config
        if config.get(root_table):
            table_config.update(config[root_table])
        # Else merge the content without a table header
        else:
            config = self.remove_nested_keys(config)
            for key, value in config.items():
                if (
                    key not in table_config
                ):  # we assing priority to the table if specified
                    table_config[key] = value

        # Overwrite the TOML config with the command line arguments
        for key, value in table_config.items():
            if key in changed_args:
                table_config[key] = changed_args[key]
            else:
                setattr(sys_args, key, value)

        return sys_args

    def write_to_toml(self, args: Dict[str, Any], path: str) -> None:
        with open(path, "w") as f:
            toml.dump(args, f)

    def load_from_toml(self, path: str) -> MutableMapping[str, Any]:
        return self.load_toml(path)
