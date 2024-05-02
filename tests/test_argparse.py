import contextlib
import sys
import unittest
from io import StringIO

from tomlparse import argparse


class TestArgparse(unittest.TestCase):
    def test_cmdl_without_args(self):
        parser = argparse.ArgumentParser()
        sys.argv = ["test_argparse.py"]
        default_args, sys_args = parser.extract_args()
        changed_args = parser.find_changed_args(default_args, sys_args)
        self.assertEqual(changed_args, [])

    def test_cmdl_with_args(self):
        parser = argparse.ArgumentParser(description="Test ArgumentParser")
        sys.argv = [
            "test_argparse.py",
            "--config",
            "config.toml",
            "--table",
            "general",
        ]
        default_args, sys_args = parser.extract_args()
        changed_args = parser.find_changed_args(default_args, sys_args)
        self.assertEqual(changed_args, ["config", "table"])

    def test_cmdl_with_args_as_param(self):
        parser = argparse.ArgumentParser(description="Test ArgumentParser")
        args = [
            "--config",
            "config.toml",
            "--table",
            "general",
        ]
        default_args, sys_args = parser.extract_args(args)
        changed_args = parser.find_changed_args(default_args, sys_args)
        self.assertEqual(changed_args, ["config", "table"])

    def test_cmdl_with_namespace(self):
        parser = argparse.ArgumentParser(description="Test ArgumentParser")
        args = [
            "--config",
            "config.toml",
            "--table",
            "general",
        ]

        class Namespace:
            pass

        namespace = Namespace()
        default_args, sys_args = parser.extract_args(args, namespace)
        changed_args = parser.find_changed_args(default_args, sys_args)
        self.assertEqual(changed_args, ["config", "table"])
        self.assertIs(sys_args, namespace)

    def test_remove_nested_keys(self):
        parser = argparse.ArgumentParser(description="Test ArgumentParser")
        sys.argv = [
            "test_argparse.py",
            "--config",
            "config.toml",
            "--table",
            "general",
            "--root-table",
            "main",
        ]
        default_args, sys_args = parser.extract_args()
        changed_args = parser.find_changed_args(default_args, sys_args)
        self.assertEqual(changed_args, ["config", "root_table", "table"])
        for key in ["config", "table", "root_table"]:
            delattr(sys_args, key)
        self.assertEqual(vars(sys_args), {})
        config = parser.load_toml("./tests/config.toml")
        self.assertEqual(
            config,
            {"foo": 10, "bar": "hello", "general": {"foo": 20}, "main": {"bar": "hey"}},
        )
        config = parser.remove_nested_keys(config)
        self.assertEqual(config, {"foo": 10, "bar": "hello"})

    def test_parse_args(self):
        # Test general arguments
        parser = argparse.ArgumentParser(description="Test ArgumentParser")
        sys.argv = ["test_argparse.py"]
        parser.add_argument("--foo", type=int, default=0)
        parser.add_argument("--bar", type=str, default="")

        args = parser.parse_args()
        self.assertEqual(args.foo, 0)
        self.assertEqual(args.bar, "")

        # Test loading toml but without a section
        sys.argv = ["test_argparse.py", "--config", "./tests/config.toml"]
        args = parser.parse_args()
        self.assertEqual(args.foo, 10)
        self.assertEqual(args.bar, "hello")

        # Test loading toml with a section
        sys.argv = [
            "test_argparse.py",
            "--config",
            "./tests/config.toml",
            "--table",
            "general",
        ]
        args = parser.parse_args()
        self.assertEqual(args.foo, 20)
        self.assertEqual(args.bar, "hello")

    def test_parse_args_with_namespace(self):
        parser = argparse.ArgumentParser(description="Test ArgumentParser")
        parser.add_argument("--foo", type=int, default=0)
        parser.add_argument("--bar", type=str, default="")

        class Namespace:
            pass

        namespace = Namespace()

        args = parser.parse_args(
            args=["--config", "./tests/config.toml"],
            namespace=namespace,
        )
        self.assertIs(namespace, args)
        self.assertEqual(args.foo, 10)
        self.assertEqual(args.bar, "hello")

    def test_missing_toml(self):
        parser = argparse.ArgumentParser(description="Test ArgumentParser")
        sys.argv = ["test_argparse.py", "--config", "./tests/missing.toml"]
        stderr = StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(stderr):
            parser.parse_args()
        self.assertIn(
            'Configuration file "./tests/missing.toml" doesn\'t exist',
            stderr.getvalue(),
        )

    def test_missing_section(self):
        parser = argparse.ArgumentParser(description="Test ArgumentParser")
        sys.argv = [
            "test_argparse.py",
            "--config",
            "./tests/config.toml",
            "--table",
            "missing",
        ]
        stderr = StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(stderr):
            parser.parse_args()
        self.assertIn(
            'No table "missing" present in the configuration file',
            stderr.getvalue(),
        )

    def test_combined_section(self):
        parser = argparse.ArgumentParser(description="Test ArgumentParser")
        sys.argv = [
            "test_argparse.py",
            "--config",
            "./tests/config.toml",
            "--root-table",
            "general",
            "--table",
            "main",
        ]
        parser.add_argument("--foo", type=int, default=0)
        parser.add_argument("--bar", type=str, default="")
        args = parser.parse_args()
        self.assertEqual(args.foo, 20)
        self.assertEqual(args.bar, "hey")
        self.assertFalse(hasattr(args, "table"))


if __name__ == "__main__":
    unittest.main()
