import argparse
from typing import Any, Dict, List, MutableMapping, Optional

try:
    import tomllib  # python ≥ 3.11
except ImportError:
    import tomli as tomllib


"""
Module for parsing command-line arguments and TOML configuration files.

It exposes :class:`ArgumentParser`, a thin wrapper around
:class:`argparse.ArgumentParser` that lets values defined in a TOML file act
as *defaults* for ordinary command-line options.

Precedence (highest first):

1. command-line flags
2. keys inside the table given via ``--table``
3. keys inside the table given via ``--root-table`` **or** the global keys
4. defaults supplied via :pymeth:`add_argument`
"""


class ArgumentParser(argparse.ArgumentParser):
    """Like :class:`argparse.ArgumentParser`, but with TOML awareness."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # helper flags (not meant for the target script itself)
        self.add_argument("--toml", help="Path to the TOML file.")
        self.add_argument(
            "--root-table",
            help=(
                "TOML table whose keys act as global defaults. "
                "If omitted, top-level keys are used."
            ),
        )
        self.add_argument(
            "--table",
            help=(
                "Extra TOML table whose keys override those coming from the "
                "root table (or from the top level)."
            ),
        )

    def flatten(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Return *data* with nested tables removed, only leaf values stay."""
        return {k: v for k, v in data.items() if not isinstance(v, dict)}

    def load_toml(self, path: str) -> MutableMapping[str, Any]:
        """Read *path* and return the parsed TOML mapping."""
        try:
            with open(path, "rb") as f:
                return tomllib.load(f)
        except FileNotFoundError:
            self.error(f"TOML file {path} does not exist")

    def add_arguments_from_toml(
        self,
        toml_path: str,
        root_table: Optional[str],
        table: Optional[str],
    ) -> None:
        """Add/override arguments according to *toml_path* and helper flags."""
        toml_data = self.load_toml(toml_path)

        # 1) defaults - either the requested root-table or the top level
        if root_table:
            if root_table not in toml_data:
                self.error(f"Specified root table {root_table} does not exist")
            base_defaults = self.flatten(toml_data[root_table])
            # Add any top-level keys that aren't in the root table
            top_level_defaults = self.flatten(toml_data)
            # Use top-level keys as fallback when not in root table
            for key, value in top_level_defaults.items():
                if key not in base_defaults:
                    base_defaults[key] = value
        else:
            base_defaults = self.flatten(toml_data)

        # 2) optional overrides - either the requested table or the top level
        if table:
            if table not in toml_data:
                self.error(f"Specified table {table} does not exist")
            override_defaults = self.flatten(toml_data[table])
        else:
            override_defaults = {}

        final_defaults = {**base_defaults, **override_defaults}

        for key, value in final_defaults.items():
            # already present? → update its default
            existing_action = next(
                (act for act in self._actions if act.dest == key), None
            )
            if existing_action is not None:
                existing_action.default = value
                continue

            # new argument inferred from TOML
            if isinstance(value, bool):
                action = "store_false" if value else "store_true"
                self.add_argument(f"--{key}", action=action, default=value)
            else:
                self.add_argument(f"--{key}", type=type(value), default=value)

    def parse_args(
        self,
        args: Optional[List[str]] = None,
        namespace: Optional[argparse.Namespace] = None,
    ) -> argparse.Namespace:
        """Parse *args* taking TOML defaults into account."""
        # first, sniff helper flags using a *fresh* namespace so that the
        # user-supplied namespace is not polluted with interim defaults
        helpers, _ = super().parse_known_args(args=args)

        if helpers.toml:
            self.add_arguments_from_toml(
                toml_path=helpers.toml,
                root_table=helpers.root_table,
                table=helpers.table,
            )

        # final parse - now with all dynamic arguments added
        result_ns = super().parse_args(args=args, namespace=namespace)

        # remove helper flags from the public namespace
        for attr in ("toml", "root_table", "table"):
            if hasattr(result_ns, attr):
                delattr(result_ns, attr)

        return result_ns
