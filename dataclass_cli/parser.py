import argparse
import dataclasses
import enum
import logging
import typing
from functools import partial


class Options(str, enum.Enum):
    POSSIBLE_VALUES = "possible_values"
    HELP_TEXT = "help_text"


def add(cls=None, *, name=None, **kwargs):
    if cls is None:
        return partial(_add, name=name, **kwargs)
    return _add(cls, name=name, **kwargs)


def _add_type_basic(
    group: argparse._ArgumentGroup, field: dataclasses.Field, name: str
):
    group.add_argument(
        f"--{name}_{field.name}",
        type=field.type,
        default=None if field.default is dataclasses.MISSING else field.default,
        required=field.default is dataclasses.MISSING,
        choices=field.metadata.get(Options.POSSIBLE_VALUES, None),
        help=field.metadata.get(Options.HELP_TEXT, None),
    )


def _add_type_list(group: argparse._ArgumentGroup, field: dataclasses.Field, name: str):
    group.add_argument(
        f"--{name}_{field.name}",
        type=typing.get_args(field.type)[0],
        default=None
        if field.default_factory is dataclasses.MISSING  # type: ignore
        else field.default_factory(),  # type: ignore
        required=field.default_factory is dataclasses.MISSING,  # type: ignore
        choices=field.metadata.get(Options.POSSIBLE_VALUES, None),
        help=field.metadata.get(Options.HELP_TEXT, None),
        nargs="*",
    )


_add_argument_: typing.Dict[
    type, typing.Callable[[argparse._ArgumentGroup, dataclasses.Field, str], None]
] = {
    int: _add_type_basic,
    float: _add_type_basic,
    str: _add_type_basic,
    typing.List[int]: _add_type_list,
    typing.List[float]: _add_type_list,
    typing.List[str]: _add_type_list,
}


def _add(
    cls,
    *,
    name: str = "",
    _classes: typing.Dict[str, typing.List[str]] = {},
    _parser=argparse.ArgumentParser(),
):
    assert dataclasses.is_dataclass(cls)

    name = name or cls.__name__
    name = name.lower()
    assert name not in _classes
    _classes[name] = [arg.name for arg in dataclasses.fields(cls)]

    group = _parser.add_argument_group(name)
    for field in dataclasses.fields(cls):
        _add_argument_[field.type](group, field, name)

    original_init = cls.__init__

    def __init__(self, **kwargs):
        _parsed_args = vars(_parser.parse_args())

        cli_args = [f"{name}_{arg}" for arg in _classes[name]]
        args = {
            arg_name: _parsed_args[cli_arg]
            for arg_name, cli_arg in zip(_classes[name], cli_args)
        }
        args.update(kwargs)

        original_init(self, **args)

    cls.__init__ = __init__

    return cls
