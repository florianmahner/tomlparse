import argparse
import sys

import toml


class ArgumentParser(argparse.ArgumentParser):
    """Convenience warpper around `argparse.ArgumentParser` that accepts
    TOML files as input"""

    def __init__(self, *args, **kwargs):
        """
        This class adds two optional arguments to the `argparse.ArgumentParser`:
        `--config` and `--section`.
        The `--config` argument specifies the path to a configuration file in the
        TOML format, and the `--section` argument specifies the name of a section
        in the configuration file. If `--config`is not provided, the default values
        specified add to the ` argparse.ArgumentParser` object will be used.
        If `--section` is not provided, all the arguments that do not have a
        section in the configuration file will be used.

        We have the following hierarchy of arguments:
            1. Arguments passed through the command line are selected over TOML
            arguments, even if both are passed
            2. Arguments from the TOML file are preferred over the default arguments
            3. Arguments from the TOML with a section override the arguments without
            a section

        Example of a TOML configuration file without a section:
        argument_1 = "value_1"
        argument_2 = "value_2"

        Example of a TOML configuration file with a section:
        [section_name]
        argument_1 = "value_1"
        argument_2 = "value_2"

        Here `argument_1` in [section_name] will override `argument_1` without
        a section.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """

        super().__init__(*args, **kwargs)
        self.add_argument(
            "--config",
            type=str,
            default="",
            help="Path to the configuration file.",
        )
        self.add_argument(
            "--section",
            type=str,
            default="",
            help="Section name in the config file to parse arguments from",
        )

    def _extract_args(self):
        """Find the default arguments of the argument parser if any and the
        ones that are passed through the command line"""
        sys_defaults = sys.argv.copy()
        sys.argv = []
        default_args = super().parse_args()
        sys.argv = sys_defaults
        cmdl_args = super().parse_args()

        return default_args, cmdl_args

    def _find_changed_args(self, default_args, sys_args):
        """Find the arguments that have been changed from the command
        line to replace the .toml arguments"""
        default_args = vars(default_args)
        sys_args = vars(sys_args)
        changed_args = {}

        for key, value in default_args.items():
            if sys_args[key] != value:
                changed_args[key] = sys_args[key]

        return changed_args

    def _pop_keys(self, namespace, keys):
        """Remove the keys from the argparse namespace that are not used by
        the parser"""
        for key in keys:
            delattr(namespace, key)
        return namespace

    def _load_toml(self, path):
        """Load the .toml file and return the config dictionary"""
        try:
            config = toml.load(path)
        except FileNotFoundError as f:
            raise FileNotFoundError from f
        return config

    def _remove_nested_keys(self, dictionary):
        """Remove nested keys from a dictionary during iterations on the fly"""
        new_dict = {}
        for key, value in dictionary.items():
            if not isinstance(value, dict):
                # breakpoint()
                new_dict[key] = value
        return new_dict

    def parse_args(self):
        """Parse the arguments from the command line and the configuration file.
        If a section name is provided, only the arguments in that section will be
        parsed from the .toml file"""
        default_args, sys_args = self._extract_args()

        # These are the default arguments options updated by the command line
        if not sys_args.config:
            self._pop_keys(sys_args, ("section", "config"))
            return sys_args

        # If a config file is passed, upodate the cmdl args with the config file unless
        # the argument is already specified in the command line
        config = self._load_toml(sys_args.config)

        changed_args = self._find_changed_args(default_args, sys_args)
        if sys_args.section:
            try:
                section_name = sys_args.section
                section_config = config[section_name]
            except KeyError as k:
                raise KeyError from k

        else:
            self._pop_keys(sys_args, ("section",))
            section_config = config
            section_config = self._remove_nested_keys(section_config)

        # This safely also ignores the section name in the nested dict
        for key, value in section_config.items():
            if key not in default_args:
                # Raise the default argparse error alongside the usage
                self.error(f"unrecognized arguments: '{key}''")

            # If the key has been passed in the command line, do not overwrite the
            # command line argument with the toml argument, but vice versa.
            if key in changed_args:
                section_config[key] = changed_args[key]
            else:
                setattr(sys_args, key, value)

        return sys_args

    def write_to_toml(self, args, path):
        """Write the config dictionary to a .toml file"""
        with open(path, "w") as f:
            toml.dump(args, f)

    def load_from_toml(self, path):
        """Load the config dictionary from a .toml file"""
        return self._load_toml(path)
