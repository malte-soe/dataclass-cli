import argparse
import dataclasses
from typing import Dict, List, Union


def add(
    cls,
    *,
    _classes: Dict[str, List[str]] = {},
    _parsed_args: Dict[str, Union[int, str]] = {},
    _parser=argparse.ArgumentParser(),
):
    assert dataclasses.is_dataclass(cls)
    name = cls.__name__.lower()
    assert name not in _classes
    _classes[name] = [arg.name for arg in dataclasses.fields(cls)]
    group = _parser.add_argument_group(name)
    for field in dataclasses.fields(cls):
        group.add_argument(
            f"--{name}_{field.name}", type=field.type, default=field.default,
        )

    original_init = cls.__init__

    def __init__(self):
        if not _parsed_args:
            _parsed_args.update(vars(_parser.parse_args()))

        cli_args = [f"{name}_{arg}" for arg in _classes[name]]
        args = {
            arg_name: _parsed_args[cli_arg]
            for arg_name, cli_arg in zip(_classes[name], cli_args)
        }

        original_init(self, **args)

    cls.__init__ = __init__

    return cls
