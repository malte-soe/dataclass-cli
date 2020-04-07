import argparse
import dataclasses
from typing import Dict, Union, List

__CLASSES__: List[str] = []
__PARSED_ARGS__: Dict[str, Union[int, str]] = {}
__PARSER__ = argparse.ArgumentParser()


def get_parsed_values(name):
    if not __PARSED_ARGS__:
        __PARSED_ARGS__.update(vars(__PARSER__.parse_args()))

    prefix_length = len(name) + 1
    return {
        k[prefix_length:]: v for k, v in __PARSED_ARGS__.items() if k.startswith(name)
    }


def cli(cls):
    assert dataclasses.is_dataclass(cls)
    name = cls.__name__.lower()
    assert name not in __CLASSES__
    __CLASSES__.append(name)
    for field in dataclasses.fields(cls):
        __PARSER__.add_argument(
            f"--{name}_{field.name}", type=field.type, default=field.default
        )

    old_init = cls.__init__

    def __init__(self):
        args = get_parsed_values(name)
        old_init(self, **args)

    cls.__init__ = __init__

    return cls
