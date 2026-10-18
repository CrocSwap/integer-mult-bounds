"""Checker-only literal inventory, signed integers and prefix oracle."""
import scalar_sources
scalar_sources.activate()
from fractions import Fraction
from literal_templates import TEMPLATES,POLICIES
from words import BLANK,need


def body(tape):
    tape = getattr(tape,"physical",tape)
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def encode(value,width):
    return bytes((value>>index)&1 for index in range(width))


def packet(values,width):
    return b"".join(encode(value,width) for value in values)


def fill(tape,raw):
    tape.clear()
    for bit in raw:
        tape.append(bit)
    tape.rewind()


def prefix_oracle(recipe,x,y,width):
    registers = [x,y,0]
    limit = 1<<(width-1)
    for operation in recipe.program:
        kind,target = operation[:2]
        value = registers[target]
        if kind == "add":
            value += operation[3]*registers[operation[2]]
        elif kind == "copy":
            need(value == 0, "checker COPY destination zero")
            value = registers[operation[2]]
        elif kind == "clear":
            value = 0
        elif kind == "neg":
            value = -value
        elif kind == "double":
            value *= 2
        else:
            need(kind == "half", "checker finite scalar alphabet")
            if value%2:
                return None,"inexact"
            value //= 2
        if not -limit <= value < limit:
            return None,"headroom"
        registers[target] = value
    expected = Fraction(x)+recipe.coefficient*y if recipe.kind == "add" else recipe.coefficient*x
    need(expected.denominator == 1 and registers == [expected,y,0], "independent scalar/source/scratch endpoint")
    return int(expected),None


def snapshot(values):
    return [(bytes(getattr(value.tape,"physical",value.tape).cells),value.tape.head) for value in values]


def closed_work(engine,include_output=False):
    tapes = (*engine.pool.tapes,engine.output) if include_output else engine.pool.tapes
    need(engine.closed and not engine.pool.live, "closed scalar inventory")
    need(all(tape.head == 1 and all(bit == BLANK for bit in tape.cells) for tape in tapes),
         "erased scalar scratch and local heads")
