"""Source-bound constant-two butterfly reduction after Petalas's unit rewrite.

The producer's setup, residue, allocation and executed-initializer contracts
are premises. These structural gates do not certify arbitrary programs.
"""
from dataclasses import dataclass

P = 65537
VALUE, TEMP, ZERO, ONE = 8, 9, 10, 11
THRESHOLDS = tuple(range(20, 36))
SCRATCH = frozenset((VALUE, TEMP, ZERO, ONE, *THRESHOLDS))
MAX_PROGRAM = 600_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(program):
    require(type(program) is list and 0 < len(program) <= MAX_PROGRAM, 'program capacity')
    arities = {'one': 2, 'add': 4, 'sub': 4, 'mul': 4, 'bltz': 3, 'accept': 1}
    for pc, instruction in enumerate(program):
        require(type(instruction) is tuple and instruction, 'instruction tuple')
        require(instruction[0] in arities and len(instruction) == arities[instruction[0]], 'ISA')
        require(all(type(x) is int for x in instruction[1:]), 'integer operands')
        if instruction[0] == 'bltz':
            require(pc < instruction[2] < len(program), 'forward branch')
    require(program[-1] == ('accept',), 'terminal accept')


def double_lifetimes(program):
    writes = {}
    for pc, instruction in enumerate(program):
        if instruction[0] in ('one', 'add', 'sub', 'mul'):
            writes.setdefault(instruction[1], []).append(pc)
    result = {}
    for cell, sites in writes.items():
        if cell in SCRATCH or len(sites) != 3:
            continue
        first, doubled, cleared = sites
        if (doubled == first + 1 and program[first] == ('one', cell)
                and program[doubled] == ('add', cell, cell, cell)
                and program[cleared] == ('sub', cell, cell, cell)):
            result[cell] = (first, doubled, cleared)
    return result


def macro(program, pc):
    first = program[pc]
    require(first[0] == 'mul' and first[1] == VALUE, 'macro entry')
    require(first[2] not in SCRATCH and first[3] not in SCRATCH
            and first[2] != first[3], 'data/coefficient ABI')
    expected = [first]
    for threshold in reversed(THRESHOLDS):
        sub_pc = pc + len(expected)
        expected.extend((('sub', TEMP, VALUE, threshold),
                         ('bltz', TEMP, sub_pc + 3), ('add', VALUE, TEMP, ZERO)))
    require(program[pc:pc + 49] == expected, 'generic reduction macro')
    # Retain the original last branch's OLD exit label. Relocate exactly once.
    return (first, *program[pc + 46:pc + 49])


@dataclass(frozen=True)
class Refinement:
    program: list
    replacements: tuple
    old_to_new: dict


def refine(program):
    validate(program)
    lifetimes = double_lifetimes(program)
    pieces, replacements, mapping = [], [], {}
    pc = new_pc = 0
    for _ in range(len(program)):
        if pc == len(program):
            break
        instruction = program[pc]
        mapping[pc] = new_pc
        hit = (instruction[0] == 'mul' and instruction[1] == VALUE
               and instruction[3] in lifetimes)
        if hit:
            first, doubled, cleared = lifetimes[instruction[3]]
            require(first < doubled < pc and pc + 49 <= cleared, 'double lifetime')
            replacement = macro(program, pc)
            pieces.append(replacement)
            replacements.append((pc, instruction[3], instruction[2]))
            pc += 49
            new_pc += 4
        else:
            pieces.append((instruction,))
            pc += 1
            new_pc += 1
    require(pc == len(program), 'bounded scan finished')
    require(replacements, 'no constant-two sites')
    output = []
    for instructions in pieces:
        for instruction in instructions:
            if instruction[0] == 'bltz':
                require(instruction[2] in mapping, 'branch into removed macro')
                instruction = ('bltz', instruction[1], mapping[instruction[2]])
            output.append(instruction)
    require(len(output) == len(program) - 45 * len(replacements), 'static delta')
    validate(output)
    return Refinement(output, tuple(replacements), mapping)
