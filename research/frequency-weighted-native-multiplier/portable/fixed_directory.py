"""Read the compiler directory once and retain the installed roots."""

from functools import cache
from pathlib import Path

from compiler_state import bind
from tape_directory import load


@cache
def data():
    with Path(__file__).with_name("installed-native.dag").open("rb") as source:
        return bind(load(source))
