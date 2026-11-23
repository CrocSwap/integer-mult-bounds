"""Bind the unpowered 36-call binary word to its actual physical owners."""

from collections import Counter
from functools import cache

from installations import BINARY_C
from strong_binary import caller, fixed_binary_charts, graph
from tagged_sources import binary_ports
from transport import Recipe
from unpowered_price import certify


class BinaryWord:
    def __init__(self):
        # This entry constructs the labelled raw port lists. No tensor tuples are requested.
        self.tagged = binary_ports(graph(), caller())
        fixed_binary_charts()
        self.targets = tuple(p.rank for p in self.tagged.targets)
        self.paid = tuple(p.rank for p in self.tagged.paid)
        margin, self.cells = certify(BINARY_C, (Counter(self.targets), Counter(self.paid)))
        if self.cells is None or margin <= 0:
            raise ArithmeticError("The binary raw word has insufficient paid capacity")

    def native(self, jobs, columns, physical):
        entries = []
        for port, job in zip(self.tagged.targets, jobs, strict=True):
            if len(job.axes) != port.rank * columns:
                raise ArithmeticError("The external binary job has the wrong extent")
            entries.append((port.tag, job))
        actual = iter(physical.raw(entries, columns))
        for port in self.tagged.paid:
            tag, job = next(actual)
            if tag != port.tag or len(job.axes) != port.rank * columns:
                raise ArithmeticError("The binary native cut differs from its physical label")
            yield job
        if next(actual, None) is not None:
            raise ArithmeticError("The binary native word has an extra paid cut")


@cache
def binary_word():
    return BinaryWord()


@cache
def binary_recipe(height):
    word = binary_word()
    return Recipe(height, word.tagged.ambient, word.targets, word.paid, word.cells, BINARY_C)


def run(recipe, fields, machine):
    if recipe is not None:
        recipe.open().run(fields, machine)
        return
    for field in fields:
        for axis in range(len(field.axes)):
            machine.leaf(field.select((axis,)))
