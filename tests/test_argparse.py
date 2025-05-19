import contextlib
import unittest
from io import StringIO

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
        args = parser.parse_args(["--toml", "./tests/config.toml"])
        self.assertEqual(args.foo, 10)
        self.assertEqual(args.bar, "hello")

    def test_parse_args_with_table(self):
        parser = tomlparse.ArgumentParser(description="Test ArgumentParser")
        parser.add_argument("--foo", type=int, default=0)
        parser.add_argument("--bar", type=str, default="")
        args = parser.parse_args(
            ["--toml", "./tests/config.toml", "--table", "general"]
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
            args=["--toml", "./tests/config.toml"], namespace=namespace
        )
        self.assertIs(args, namespace)
        self.assertEqual(args.foo, 10)
        self.assertEqual(args.bar, "hello")

    def test_missing_toml_file(self):
        parser = tomlparse.ArgumentParser(description="Test ArgumentParser")
        stderr = StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(stderr):
            parser.parse_args(["--toml", "./tests/missing.toml"])
        self.assertIn(
            "TOML file ./tests/missing.toml does not exist", stderr.getvalue()
        )

    def test_missing_table(self):
        parser = tomlparse.ArgumentParser(description="Test ArgumentParser")
        stderr = StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(stderr):
            parser.parse_args(["--toml", "./tests/config.toml", "--table", "missing"])
        self.assertIn("Specified table missing does not exist", stderr.getvalue())

    def test_combined_root_and_table(self):
        parser = tomlparse.ArgumentParser(description="Test ArgumentParser")
        parser.add_argument("--foo", type=int, default=0)
        parser.add_argument("--bar", type=str, default="")
        args = parser.parse_args(
            [
                "--toml",
                "./tests/config.toml",
                "--root-table",
                "general",
                "--table",
                "main",
            ]
        )
        self.assertEqual(args.foo, 20)
        self.assertEqual(args.bar, "hey")
        self.assertFalse(hasattr(args, "table"))

    def test_parse_toml_without_arguments(self):
        parser = tomlparse.ArgumentParser(description="Test ArgumentParser")
        # No arguments added
        args = parser.parse_args(["--toml", "./tests/config.toml"])
        # Check that top-level config values are accessible
        self.assertEqual(args.foo, 10)
        self.assertEqual(args.bar, "hello")

    def test_parse_toml_with_root_table(self):
        parser = tomlparse.ArgumentParser(description="Test ArgumentParser")
        # No arguments added
        args = parser.parse_args(
            ["--toml", "./tests/config.toml", "--root-table", "general"]
        )
        # Check that top-level config values are accessible
        self.assertEqual(args.foo, 20)
        self.assertEqual(args.bar, "hello")


if __name__ == "__main__":
    unittest.main()
