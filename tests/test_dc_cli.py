import argparse
import unittest
from dataclasses import dataclass
from functools import partial
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
