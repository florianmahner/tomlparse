from __future__ import annotations

import argparse
from importlib import import_module
from pathlib import Path
from typing import Any, Final, Literal, Mapping, MutableMapping, Sequence, TypeVar, cast
from collections import ChainMap

def _load_toml_backend() -> Any:
    """Load tomllib (Python 3.11+) or fall back to tomli."""
    try:
        return import_module("tomllib")
    except ModuleNotFoundError:
        return import_module("tomli")


tomllib = _load_toml_backend()

_HELPER_ARGS: Final[tuple[str, ...]] = ("toml", "root_table", "table")

_Namespace = TypeVar("_Namespace", bound=argparse.Namespace)


class ArgumentParser(argparse.ArgumentParser):
    """
    ArgumentParser with TOML configuration file support.

    Extends the standard argparse.ArgumentParser to allow defaults to be
    loaded from TOML configuration files with hierarchical table overrides.

    Precedence (highest to lowest):
        1. Command-line arguments
        2. Values from --table (if specified)
        3. Values from --root-table or top-level keys
        4. Parser defaults from add_argument()

    Example:
        >>> parser = ArgumentParser(description="My app")
        >>> parser.add_argument("--verbose", action="store_true")
        >>> args = parser.parse_args(["--toml", "config.toml"])

    The parser automatically adds three helper arguments:
        --toml: Path to TOML configuration file
        --root-table: Base table for defaults
        --table: Override table
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._add_helper_arguments()

    def _add_helper_arguments(self) -> None:
        """Add TOML-specific helper arguments to parser."""
        self.add_argument(
            "--toml",
            metavar="PATH",
            help="Path to TOML configuration file",
        )
        self.add_argument(
            "--root-table",
            metavar="TABLE",
            help="Base TOML table for defaults (top-level if omitted)",
        )
        self.add_argument(
            "--table",
            metavar="TABLE",
            help="Override TOML table (takes precedence over root-table)",
        )

    def load_toml(self, path: str) -> MutableMapping[str, Any]:
        """
        Load and parse TOML configuration file.

        Args:
            path: Path to TOML file

        Returns:
            Parsed TOML data as mutable mapping

        Raises:
            SystemExit: If file not found or invalid TOML syntax
        """
        file_path = Path(path)

        try:
            with file_path.open("rb") as handle:
                return cast(MutableMapping[str, Any], tomllib.load(handle))
        except FileNotFoundError:
            self.error(
                f"TOML file not found: {path}\nSearched at: {file_path.resolve()}"
            )
        except Exception as exc:
            self.error(
                f"Failed to parse TOML file '{path}': {exc}\n"
                "Ensure the file contains valid TOML syntax"
            )

    def _extract_leaf_values(self, data: Mapping[str, Any]) -> dict[str, Any]:
        """
        Extract leaf (non-table) values from TOML data.

        Tables (nested dicts) are filtered out, only scalar values remain.

        Args:
            data: TOML data mapping

        Returns:
            Dictionary of leaf values only

        Example:
            >>> data = {"foo": 1, "section": {"bar": 2}}
            >>> self._extract_leaf_values(data)
            {"foo": 1}
        """
        return {k: v for k, v in data.items() if not isinstance(v, dict)}

    def _extract_base_defaults(
        self,
        toml_data: Mapping[str, Any],
        root_table: str | None,
    ) -> dict[str, Any]:
        """
        Extract base defaults from TOML data.

        If root_table is specified, uses that table's values with top-level
        values as fallback. Otherwise, uses only top-level values.

        Args:
            toml_data: Parsed TOML data
            root_table: Optional root table name

        Returns:
            Dictionary of base default values
        """
        if not root_table:
            return self._extract_leaf_values(toml_data)

        if root_table not in toml_data:
            self.error(f"Root table '{root_table}' not found in TOML file")

        base_defaults = self._extract_leaf_values(toml_data[root_table])
        top_level_defaults = self._extract_leaf_values(toml_data)

        return ChainMap(base_defaults, top_level_defaults)

    def _extract_override_defaults(
        self,
        toml_data: Mapping[str, Any],
        table: str | None,
    ) -> dict[str, Any]:
        """
        Extract override defaults from specified table.

        Args:
            toml_data: Parsed TOML data
            table: Optional table name for overrides

        Returns:
            Dictionary of override values (empty if no table specified)
        """
        if not table:
            return {}

        if table not in toml_data:
            self.error(f"Table '{table}' not found in TOML file")

        return self._extract_leaf_values(toml_data[table])

    def _find_action_by_dest(self, dest: str) -> argparse.Action | None:
        """
        Find existing action by destination name.

        Args:
            dest: Argument destination name

        Returns:
            Matching Action or None if not found
        """
        return next((act for act in self._actions if act.dest == dest), None)

    def _add_dynamic_argument(self, key: str, value: Any) -> None:
        """
        Add dynamically inferred argument from TOML value.

        Boolean values create store_true/store_false actions.
        Other types create typed arguments with inferred type.

        Args:
            key: Argument name (will be prefixed with --)
            value: TOML value used to infer type
        """
        if isinstance(value, bool):
            action: Literal["store_true", "store_false"] = (
                "store_false" if value else "store_true"
            )
            self.add_argument(f"--{key}", action=action, default=value)
        elif isinstance(value, (int, float, str)):
            self.add_argument(f"--{key}", type=type(value), default=value)
        else:
            self.error(
                f"Unsupported TOML value type for '{key}': {type(value).__name__}\n"
                "Supported types: bool, int, float, str"
            )

    def _update_or_add_argument(self, key: str, value: Any) -> None:
        """
        Update existing argument default or add new dynamic argument.

        Args:
            key: Argument destination name
            value: Default value to set
        """
        existing_action = self._find_action_by_dest(key)

        if existing_action is not None:
            existing_action.default = value
        else:
            self._add_dynamic_argument(key, value)

    def _apply_defaults(self, defaults: Mapping[str, Any]) -> None:
        """
        Apply default values to parser arguments.

        Args:
            defaults: Dictionary of key-value pairs to apply
        """
        for key, value in defaults.items():
            self._update_or_add_argument(key, value)

    def add_arguments_from_toml(
        self,
        toml_path: str,
        root_table: str | None,
        table: str | None,
    ) -> None:
        """
        Load and apply arguments from TOML configuration.

        Merges defaults from root_table (or top-level) with overrides from
        table, then updates or creates parser arguments accordingly.

        Args:
            toml_path: Path to TOML configuration file
            root_table: Optional base table name for defaults
            table: Optional override table name
        """
        toml_data = self.load_toml(toml_path)

        base_defaults = self._extract_base_defaults(toml_data, root_table)
        override_defaults = self._extract_override_defaults(toml_data, table)
        final_defaults = ChainMap(override_defaults, base_defaults)

        self._apply_defaults(final_defaults)

    def _cleanup_helper_arguments(self, namespace: argparse.Namespace) -> None:
        """Remove internal TOML helper arguments from result namespace."""
        for attr in _HELPER_ARGS:
            namespace.__dict__.pop(attr, None)

    def parse_args(  # type: ignore[override]
        self,
        args: Sequence[str] | None = None,
        namespace: _Namespace | None = None,
    ) -> argparse.Namespace | _Namespace:
        """
        Parse arguments with TOML configuration support.

        First sniffs for TOML-related helper flags, loads configuration if
        present, then performs final parse with all arguments registered.

        Args:
            args: Argument strings to parse (sys.argv[1:] if None)
            namespace: Object to populate with attributes (new Namespace if None)

        Returns:
            Populated namespace object (same instance if provided)
        """
        helpers, _ = super().parse_known_args(args=args)

        if helpers.toml:
            self.add_arguments_from_toml(
                toml_path=helpers.toml,
                root_table=helpers.root_table,
                table=helpers.table,
            )

        result_ns = super().parse_args(args=args, namespace=namespace)
        self._cleanup_helper_arguments(result_ns)

        return result_ns
