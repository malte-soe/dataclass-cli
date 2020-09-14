import argparse
import typing
import unittest
from dataclasses import dataclass, field
from functools import partial
from io import StringIO
from unittest import mock

import dataclass_cli


class TestDcCli(unittest.TestCase):
    def setUp(self):
        self.add = partial(
            dataclass_cli.add, _classes={}, _parser=argparse.ArgumentParser(),
        )

    def tearDown(self):
        del self.add

    def test_single_dataclass_parsing(self):
        @self.add
        @dataclass
        class Dataclass:
            name: str
            number: int
            flag: bool
            no_flag: bool

        name = "Max"
        number = 1337
        testargs = [
            "test.py",
            f"--dataclass_name={name}",
            f"--dataclass_number={number}",
            "--dataclass_flag",
            "--no-dataclass_no_flag",
        ]
        with mock.patch("sys.argv", testargs):
            parsed_dc = Dataclass()
        self.assertEqual(parsed_dc.name, name)
        self.assertEqual(parsed_dc.number, number)
        self.assertTrue(parsed_dc.flag)
        self.assertFalse(parsed_dc.no_flag)

    def test_multiple_dataclass_parsing(self):
        @self.add
        @dataclass
        class Dataclass1:
            name: str
            number: int

        @self.add
        @dataclass
        class Dataclass2:
            name: str
            number: int

        name1 = "Max"
        name2 = "Muster"
        number1 = 1337
        number2 = 42
        testargs = f"test.py\
            --dataclass1_name {name1}\
            --dataclass1_number {number1}\
            --dataclass2_name {name2}\
            --dataclass2_number {number2}".split()
        with mock.patch("sys.argv", testargs):
            parsed_dc = Dataclass1()
            self.assertEqual(parsed_dc.name, name1)
            self.assertEqual(parsed_dc.number, number1)
            parsed_dc = Dataclass2()
            self.assertEqual(parsed_dc.name, name2)
            self.assertEqual(parsed_dc.number, number2)

    def test_no_possible_value_option(self):
        possible_values = [1, 2, 3]

        @self.add
        @dataclass
        class DataclassWithChoices:
            number: int = field(
                default=1,
                metadata={dataclass_cli.Options.POSSIBLE_VALUES: possible_values},
            )

        number = 0
        testargs = f"test.py --dataclasswithchoices_number {number}".split()
        with mock.patch("sys.argv", testargs), self.assertRaises(
            SystemExit
        ), mock.patch("sys.stderr", new=StringIO()) as fake_out:
            _ = DataclassWithChoices()
        self.assertIn("invalid choice", fake_out.getvalue())

    def test_ignore_value_option(self):
        @self.add
        @dataclass
        class DataclassWithIgnoredValue:
            number: int = field(
                default=1, metadata={dataclass_cli.Options.IGNORE: True},
            )

        number = 0
        testargs = f"test.py --dataclasswithignoredvalue_number {number}".split()
        with mock.patch("sys.argv", testargs), self.assertRaises(SystemExit):
            _ = DataclassWithIgnoredValue()

        testargs = f"test.py --help".split()
        with mock.patch("sys.argv", testargs), self.assertRaises(
            SystemExit
        ), mock.patch("sys.stderr", new=StringIO()) as fake_out:
            _ = DataclassWithIgnoredValue()
        self.assertNotIn("number", fake_out.getvalue())

    def test_possible_value_option(self):
        possible_values = [1, 2, 3]

        @self.add
        @dataclass
        class DataclassWithChoices:
            number: int = field(
                default=1,
                metadata={dataclass_cli.Options.POSSIBLE_VALUES: possible_values},
            )

        number = possible_values[0]
        testargs = f"test.py --dataclasswithchoices_number {number}".split()
        with mock.patch("sys.argv", testargs):
            parsed_dc = DataclassWithChoices()
        self.assertEqual(parsed_dc.number, number)

    def test_help_text(self):
        help_text = "This is a help message!"

        @self.add
        @dataclass
        class DataclassWithHelp:
            number: int = field(
                default=1, metadata={dataclass_cli.Options.HELP_TEXT: help_text},
            )

        testargs = "test.py -h".split()
        with mock.patch("sys.argv", testargs), self.assertRaises(
            SystemExit
        ), mock.patch("sys.stdout", new=StringIO()) as fake_out:
            _ = DataclassWithHelp()

        self.assertIn(help_text, fake_out.getvalue())

    def test_no_default_value(self):
        @self.add
        @dataclass
        class DataclassWithNoDefault:
            number: int

        testargs = "test.py".split()
        with mock.patch("sys.argv", testargs), self.assertRaises(
            SystemExit
        ), mock.patch("sys.stderr", new=StringIO()) as fake_out:
            _ = DataclassWithNoDefault()

        self.assertIn("the following arguments are required", fake_out.getvalue())

    def test_custom_name(self):
        name = "custom42"
        number = 42

        @self.add(name=name)
        @dataclass
        class Dataclass:
            number: int

        testargs = f"test.py --{name}_number {number}".split()
        with mock.patch("sys.argv", testargs):
            dc = Dataclass()
        self.assertEqual(number, dc.number)

    def test_overwrite_cli_args(self):
        name = "custom42"
        number = 42
        number_cli = 1337

        @self.add(name=name)
        @dataclass
        class Dataclass:
            number: int

        testargs = f"test.py --{name}_number {number_cli}".split()
        with mock.patch("sys.argv", testargs):
            dc = Dataclass(number=number)
        self.assertEqual(number, dc.number)

    def test_default_list_arg(self):
        testing_lists = [
            [],
            [1],
            [1, 2],
            ["a"],
            ["a", "b"],
            [0.5],
            [0.5, 0.2],
        ]
        for idx, test_list in enumerate(testing_lists):

            element_type = int if (len(test_list) == 0) else type(test_list[0])

            @self.add(name=f"dataclass_{idx}")
            @dataclass
            class Dataclass:
                args: typing.List[element_type] = field(
                    default_factory=lambda: test_list
                )

            testargs = ["test.py"]
            with mock.patch("sys.argv", testargs):
                dc = Dataclass()
            self.assertEqual(test_list, dc.args)

    def test_list_arg(self):
        testing_lists = [
            [1],
            [1, 2],
            ["a"],
            ["a", "b"],
            [0.5],
            [0.5, 0.2],
        ]
        for idx, test_list in enumerate(testing_lists):

            element_type = int if (len(test_list) == 0) else type(test_list[0])
            name = f"dataclass_{idx}"

            @self.add(name=name)
            @dataclass
            class Dataclass:
                args: typing.List[element_type] = field(default_factory=lambda: [])

            testargs = ["test.py", f"--{name}_args"]
            testargs.extend(map(str, test_list))
            with mock.patch("sys.argv", testargs):
                dc = Dataclass()
            self.assertEqual(test_list, dc.args)

    def test_possible_values_list_arg(self):
        testing_lists = [
            [1],
            [1, 2],
            ["a"],
            ["a", "b"],
            [0.5],
            [0.5, 0.2],
        ]
        for idx, test_list in enumerate(testing_lists):

            element_type = int if (len(test_list) == 0) else type(test_list[0])
            name = f"dataclass_{idx}"

            @self.add(name=name)
            @dataclass
            class Dataclass:
                args: typing.List[element_type] = field(
                    default_factory=lambda: [],
                    metadata={dataclass_cli.Options.POSSIBLE_VALUES: test_list},
                )

            testargs = ["test.py", f"--{name}_args"]
            testargs.extend(map(str, test_list))
            with mock.patch("sys.argv", testargs):
                dc = Dataclass()
            self.assertEqual(test_list, dc.args)

    def test_no_possible_values_list_arg(self):
        testing_lists = [
            [1],
            [1, 2],
            ["a"],
            ["a", "b"],
            [0.5],
            [0.5, 0.2],
        ]
        for idx, test_list in enumerate(testing_lists):

            element_type = int if (len(test_list) == 0) else type(test_list[0])
            name = f"dataclass_{idx}"

            @self.add(name=name)
            @dataclass
            class Dataclass:
                args: typing.List[element_type] = field(
                    default_factory=lambda: [],
                    metadata={dataclass_cli.Options.POSSIBLE_VALUES: test_list},
                )

            testargs = ["test.py", f"--{name}_args"]
            testargs.extend(map(str, test_list + ["10"]))
            with mock.patch("sys.argv", testargs), self.assertRaises(
                SystemExit
            ), mock.patch("sys.stderr", new=StringIO()) as fake_out:
                _ = Dataclass()
            self.assertIn("invalid choice", fake_out.getvalue())
