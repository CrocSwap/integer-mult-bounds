"""Replace authenticated unit-twiddle macros, preserving their entire memory effect."""
from dataclasses import dataclass

P = 65537
VALUE, TEMP, ZERO = 8, 9, 10
THRESHOLDS = tuple(range(20, 36))
MAX_PROGRAM = 600_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(program):
    require(0 < len(program) <= MAX_PROGRAM, "program capacity")
    arities = {"one": 2, "add": 4, "sub": 4, "mul": 4,
               "bltz": 3, "accept": 1}
    for pc, ins in enumerate(program):
        require(isinstance(ins, tuple) and ins, "instruction tuple")
        require(ins[0] in arities and len(ins) == arities[ins[0]], "ISA")
        require(all(type(x) is int for x in ins[1:]), "integer operands")
        if ins[0] == "bltz":
            require(pc < ins[2] < len(program), "forward branch")
    require(program[-1] == ("accept",), "terminal accept")


def unit_lifetimes(program):
    writes = {}
    for pc, ins in enumerate(program):
        if ins[0] in ("one", "add", "sub", "mul"):
            writes.setdefault(ins[1], []).append(pc)
    result = {}
    for cell, sites in writes.items():
        if len(sites) == 2:
            first, last = sites
            if (program[first] == ("one", cell)
                    and program[last] == ("sub", cell, cell, cell)):
                result[cell] = (first, last)
    return result


def macro(program, pc):
    first = program[pc]
    require(first[0] == "mul" and first[1] == VALUE, "macro entry")
    expected = [first]
    for threshold in reversed(THRESHOLDS):
        pos = pc + len(expected)
        expected.extend((("sub", TEMP, VALUE, threshold),
                         ("bltz", TEMP, pos + 3),
                         ("add", VALUE, TEMP, ZERO)))
    require(program[pc:pc + 49] == expected, "generic reduction macro")
    require(first[2] not in (VALUE, TEMP, ZERO, *THRESHOLDS), "data ABI")
    return (("add", VALUE, first[2], ZERO),
            ("sub", TEMP, VALUE, THRESHOLDS[0]))


@dataclass(frozen=True)
class Refinement:
    program: list
    replacements: tuple
    old_to_new: dict


def refine(program):
    """Requires the pinned producer's coefficient/range and setup invariants."""
    validate(program)
    units = unit_lifetimes(program)
    pieces, replacements, mapping = [], [], {}
    pc = new_pc = 0
    for _ in range(len(program)):
        if pc == len(program):
            break
        ins = program[pc]
        mapping[pc] = new_pc
        hit = ins[0] == "mul" and ins[1] == VALUE and ins[3] in units
        if hit:
            first, last = units[ins[3]]
            require(first < pc and pc + 49 <= last, "unit lifetime")
            replacement = macro(program, pc)
            pieces.append((pc, replacement))
            replacements.append(pc)
            pc += 49
            new_pc += 2
        else:
            pieces.append((pc, (ins,)))
            pc += 1
            new_pc += 1
    require(pc == len(program), "bounded scan finished")
    output = []
    for old_pc, instructions in pieces:
        for ins in instructions:
            if ins[0] == "bltz":
                require(ins[2] in mapping, "branch into removed macro")
                ins = ("bltz", ins[1], mapping[ins[2]])
            output.append(ins)
    require(len(output) == len(program) - 47 * len(replacements), "static delta")
    validate(output)
    return Refinement(output, tuple(replacements), mapping)
