import unittest
from dataclasses import dataclass
from unittest import mock

import dataclass_cli


@dataclass_cli.cli
@dataclass
class Dataclass:
    name: str
    number: int


class TestDcCli(unittest.TestCase):
    def test_parsing(self):
        name = "Max"
        number = 1337
        testargs = f"test.py --dataclass_name {name}\
            --dataclass_number {number}".split()
        with mock.patch("sys.argv", testargs):
            parsed_dc = Dataclass()
            self.assertEqual(parsed_dc.name, name)
            self.assertEqual(parsed_dc.number, number)
