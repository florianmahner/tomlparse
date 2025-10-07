import contextlib
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import tomlparse


class TestArgumentParser(unittest.TestCase):
    def test_parse_args_defaults(self):
        parser = tomlparse.ArgumentParser(description="Test ArgumentParser")
        parser.add_argument("--foo", type=int, default=0)
        parser.add_argument("--bar", type=str, default="")
        args = parser.parse_args([])
        self.assertEqual(args.foo, 0)
        self.assertEqual(args.bar, "")

    def test_parse_args_with_toml(self):
        parser = tomlparse.ArgumentParser(description="Test ArgumentParser")
        parser.add_argument("--foo", type=int, default=0)
        parser.add_argument("--bar", type=str, default="")
        args = parser.parse_args(["--toml", str(Path("tests/config.toml"))])
        self.assertEqual(args.foo, 10)
        self.assertEqual(args.bar, "hello")

    def test_parse_args_with_table(self):
        parser = tomlparse.ArgumentParser(description="Test ArgumentParser")
        parser.add_argument("--foo", type=int, default=0)
        parser.add_argument("--bar", type=str, default="")
        args = parser.parse_args(
            [
                "--toml",
                str(Path("tests/config.toml")),
                "--table",
                "general",
            ]
        )
        self.assertEqual(args.foo, 20)
        self.assertEqual(args.bar, "hello")

    def test_parse_args_with_namespace(self):
        parser = tomlparse.ArgumentParser(description="Test ArgumentParser")
        parser.add_argument("--foo", type=int, default=0)
        parser.add_argument("--bar", type=str, default="")

        class Namespace:
            pass

        namespace = Namespace()
        args = parser.parse_args(
            args=["--toml", str(Path("tests/config.toml"))], namespace=namespace
        )
        self.assertIs(args, namespace)
        self.assertEqual(args.foo, 10)
        self.assertEqual(args.bar, "hello")

    def test_missing_toml_file(self):
        parser = tomlparse.ArgumentParser(description="Test ArgumentParser")
        stderr = StringIO()
        missing_path = "./tests/missing.toml"
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(stderr):
            parser.parse_args(["--toml", missing_path])
        self.assertIn("TOML file not found", stderr.getvalue())

    def test_missing_table(self):
        parser = tomlparse.ArgumentParser(description="Test ArgumentParser")
        stderr = StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(stderr):
            parser.parse_args(
                [
                    "--toml",
                    str(Path("tests/config.toml")),
                    "--table",
                    "missing",
                ]
            )
        self.assertIn("Table 'missing' not found", stderr.getvalue())

    def test_combined_root_and_table(self):
        parser = tomlparse.ArgumentParser(description="Test ArgumentParser")
        parser.add_argument("--foo", type=int, default=0)
        parser.add_argument("--bar", type=str, default="")
        args = parser.parse_args(
            [
                "--toml",
                str(Path("tests/config.toml")),
                "--root-table",
                "general",
                "--table",
                "main",
            ]
        )
        self.assertEqual(args.foo, 20)
        self.assertEqual(args.bar, "hey")
        self.assertFalse(hasattr(args, "table"))
        self.assertFalse(hasattr(args, "toml"))
        self.assertFalse(hasattr(args, "root_table"))

    def test_parse_toml_without_arguments(self):
        parser = tomlparse.ArgumentParser(description="Test ArgumentParser")
        # No arguments added
        args = parser.parse_args(["--toml", str(Path("tests/config.toml"))])
        # Check that top-level config values are accessible
        self.assertEqual(args.foo, 10)
        self.assertEqual(args.bar, "hello")

    def test_parse_toml_with_root_table(self):
        parser = tomlparse.ArgumentParser(description="Test ArgumentParser")
        # No arguments added
        args = parser.parse_args(
            [
                "--toml",
                str(Path("tests/config.toml")),
                "--root-table",
                "general",
            ]
        )
        # Check that top-level config values are accessible
        self.assertEqual(args.foo, 20)
        self.assertEqual(args.bar, "hello")

    def test_parse_toml_with_boolean_defaults(self):
        parser = tomlparse.ArgumentParser(description="Test ArgumentParser")
        toml_path = Path("tests/bool_config.toml")
        args = parser.parse_args(["--toml", str(toml_path)])
        self.assertTrue(args.flag)
        self.assertFalse(args.feature)
        toggled = parser.parse_args(["--toml", str(toml_path), "--flag", "--feature"])
        self.assertFalse(toggled.flag)
        self.assertTrue(toggled.feature)

    def test_toml_backend_falls_back_to_tomli(self):
        fallback = object()
        with patch("tomlparse.argparse.import_module") as mock_import:
            mock_import.side_effect = [ModuleNotFoundError, fallback]
            result = tomlparse.argparse._load_toml_backend()
        self.assertIs(result, fallback)


if __name__ == "__main__":
    unittest.main()
