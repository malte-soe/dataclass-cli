import argparse
import unittest
from dataclasses import dataclass, field
from functools import partial
from io import StringIO
from unittest import mock

import dataclass_cli


class TestDcCli(unittest.TestCase):
    def setUp(self):
        self.add = partial(
            dataclass_cli.add,
            _classes={},
            _parsed_args={},
            _parser=argparse.ArgumentParser(),
        )

    def tearDown(self):
        del self.add

    def test_single_dataclass_parsing(self):
        @self.add
        @dataclass
        class Dataclass:
            name: str
            number: int

        name = "Max"
        number = 1337
        testargs = f"test.py --dataclass_name {name}\
            --dataclass_number {number}".split()
        with mock.patch("sys.argv", testargs):
            parsed_dc = Dataclass()
            self.assertEqual(parsed_dc.name, name)
            self.assertEqual(parsed_dc.number, number)

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

        testargs = f"test.py -h".split()
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

        testargs = f"test.py".split()
        with mock.patch("sys.argv", testargs), self.assertRaises(
            SystemExit
        ), mock.patch("sys.stderr", new=StringIO()) as fake_out:
            _ = DataclassWithNoDefault()

        self.assertIn("the following arguments are required", fake_out.getvalue())
