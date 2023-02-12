import os
import sys
import unittest

from toml_argparse import argparse


class TestArgparse(unittest.TestCase):
    def test_cmdl_without_args(self):
        parser = argparse.ArgumentParser()
        sys.argv = ["test_argparse.py"]
        default_args, sys_args = parser._extract_args()
        changed_args = parser._find_changed_args(default_args, sys_args)
        self.assertEqual(changed_args, {})

    def test_cmdl_with_args(self):
        parser = argparse.ArgumentParser(description="Test ArgumentParser")
        sys.argv = [
            "test_argparse.py",
            "--config",
            "config.toml",
            "--section",
            "general",
        ]
        default_args, sys_args = parser._extract_args()
        changed_args = parser._find_changed_args(default_args, sys_args)
        self.assertEqual(changed_args, {"config": "config.toml", "section": "general"})

    def test_pop_keys(self):
        parser = argparse.ArgumentParser(description="Test ArgumentParser")
        sys.argv = [
            "test_argparse.py",
            "--config",
            "config.toml",
            "--section",
            "general",
        ]
        default_args, sys_args = parser._extract_args()
        changed_args = parser._find_changed_args(default_args, sys_args)
        self.assertEqual(changed_args, {"config": "config.toml", "section": "general"})
        parser._pop_keys(sys_args, ["config", "section"])
        self.assertEqual(vars(sys_args), {})

    def test_remove_nested_keys(self):
        parser = argparse.ArgumentParser(description="Test ArgumentParser")
        sys.argv = [
            "test_argparse.py",
            "--config",
            "config.toml",
            "--section",
            "general",
        ]
        default_args, sys_args = parser._extract_args()
        changed_args = parser._find_changed_args(default_args, sys_args)
        self.assertEqual(changed_args, {"config": "config.toml", "section": "general"})
        parser._pop_keys(sys_args, ["config", "section"])
        self.assertEqual(vars(sys_args), {})
        config = parser.load_from_toml("./tests/config.toml")
        self.assertEqual(config, {"foo": 10, "bar": "hello", "general": {"foo": 20}})
        config = parser._remove_nested_keys(config)
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
            "--section",
            "general",
        ]
        args = parser.parse_args()
        self.assertEqual(args.foo, 20)
        self.assertEqual(args.bar, "")

    def test_missing_toml(self):
        parser = argparse.ArgumentParser(description="Test ArgumentParser")
        sys.argv = ["test_argparse.py", "--config", "./tests/missing.toml"]
        with self.assertRaises(FileNotFoundError):
            parser.parse_args()

    def test_missing_section(self):
        parser = argparse.ArgumentParser(description="Test ArgumentParser")
        sys.argv = [
            "test_argparse.py",
            "--config",
            "./tests/config.toml",
            "--section",
            "missing",
        ]
        with self.assertRaises(KeyError):
            parser.parse_args()

    def test_non_specified_args(self):
        parser = argparse.ArgumentParser(description="Test ArgumentParser")
        sys.argv = ["test_argparse.py", "--config", "./tests/config.toml"]
        parser.add_argument("--foo", type=int, default=0)
        with self.assertRaises(SystemExit):
            parser.parse_args()

    def test_write_to_toml(self):
        parser = argparse.ArgumentParser(description="Test ArgumentParser")
        sys.argv = [
            "test_argparse.py",
            "--config",
            "./tests/config.toml",
            "--section",
            "general",
        ]
        parser.add_argument("--foo", type=int, default=0)
        parser.add_argument("--bar", type=str, default="")
        args = parser.parse_args()
        parser.write_to_toml(vars(args), "./tests/test_config.toml")
        config = parser.load_from_toml("./tests/test_config.toml")
        os.remove("./tests/test_config.toml")
        self.assertEqual(vars(args), config)


if __name__ == "__main__":
    unittest.main()
