import argparse
import dataclasses
import enum
from functools import partial
from typing import Dict, List, Union


class Options(str, enum.Enum):
    POSSIBLE_VALUES = enum.auto()
    HELP_TEXT = enum.auto()


def add(cls=None, *, name=None, **kwargs):
    if cls is None:
        return partial(_add, name=name, **kwargs)
    return _add(cls, name=name, **kwargs)


def _add(
    cls,
    *,
    name: str = "",
    _classes: Dict[str, List[str]] = {},
    _parsed_args: Dict[str, Union[int, str]] = {},
    _parser=argparse.ArgumentParser(),
):
    assert dataclasses.is_dataclass(cls)

    name = name or cls.__name__.lower()
    assert name not in _classes
    _classes[name] = [arg.name for arg in dataclasses.fields(cls)]

    group = _parser.add_argument_group(name)
    for field in dataclasses.fields(cls):
        group.add_argument(
            f"--{name}_{field.name}",
            type=field.type,
            default=None if field.default is dataclasses.MISSING else field.default,
            required=field.default is dataclasses.MISSING,
            choices=field.metadata.get(Options.POSSIBLE_VALUES, None),
            help=field.metadata.get(Options.HELP_TEXT, None),
        )

    original_init = cls.__init__

    def __init__(self, **kwargs):
        if not _parsed_args:
            _parsed_args.update(vars(_parser.parse_args()))

        cli_args = [f"{name}_{arg}" for arg in _classes[name]]
        args = {
            arg_name: _parsed_args[cli_arg]
            for arg_name, cli_arg in zip(_classes[name], cli_args)
        }
        args.update(kwargs)

        original_init(self, **args)

    cls.__init__ = __init__

    return cls
