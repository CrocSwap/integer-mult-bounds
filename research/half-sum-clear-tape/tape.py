"""Compile the retained half-sum circuit to unit tape instructions.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""

from collections import Counter
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LEFT, RIGHT, XORA, XORB, FLIPA, FLIPAB, INIT, RETIRE, MARK, UNMARK = range(10)


def load_source(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'retained/source' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compile_tape(width):
    if width < 1:
        raise ValueError('positive width required')
    lengths = [width] * 9 + [1] + [x for _ in range(7) for x in (width + 3, width + 2)] + [4]
    addresses = [(tape, bit) for tape, length in enumerate(lengths) for bit in range(1, length + 1)]
    size, gates = load_source('circuit').compile_row(width)
    if size != len(addresses):
        raise ValueError('source wire layout differs')
    for gate in gates:
        if len(gate) not in (2, 3) or len(set(gate)) != len(gate) or min(gate) < 0 or max(gate) >= size:
            raise ValueError('invalid source gate')
    heads = [0] * 25
    commands, phases = [], []

    def emit(op, tape):
        commands.append((op << 5) | tape)

    def goto(tape, position):
        op = RIGHT if position > heads[tape] else LEFT
        commands.extend([(op << 5) | tape] * abs(position - heads[tape]))
        heads[tape] = position

    def phase(name, action):
        before = len(commands)
        action()
        phases.append(dict(phase=name, commands=len(commands) - before))

    def initialize():
        for tape in range(10, 25):
            for position in range(1, lengths[tape] + 1):
                goto(tape, position)
                emit(INIT, tape)
            goto(tape, lengths[tape] + 1)
            emit(MARK, tape)
            goto(tape, 0)

    def block(sequence):
        for gate in sequence:
            for index, wire in enumerate(gate[:-1]):
                tape, position = addresses[wire]
                goto(tape, position)
                emit(XORA + index, tape)
            tape, position = addresses[gate[-1]]
            goto(tape, position)
            emit(FLIPA if len(gate) == 2 else FLIPAB, tape)
            for index in range(len(gate) - 2, -1, -1):
                tape, position = addresses[gate[index]]
                goto(tape, position)
                emit(XORA + index, tape)

    def home():
        for tape in range(25):
            goto(tape, 0)

    def retire():
        for tape in range(10, 25):
            goto(tape, lengths[tape] + 1)
            emit(UNMARK, tape)
            for position in range(lengths[tape], 0, -1):
                goto(tape, position)
                emit(RETIRE, tape)
            goto(tape, 0)

    half = (len(gates) - width - 1) // 2
    phase('initialize', initialize)
    phase('forward', lambda: block(gates[:half]))
    phase('copy', lambda: block(gates[half:half + width + 1]))
    phase('reverse', lambda: block(gates[half + width + 1:]))
    phase('home', home)
    phase('retire', retire)
    counts = Counter(command >> 5 for command in commands)
    operations = sum(counts[op] for op in (XORA, XORB, FLIPA, FLIPAB))
    length = len(commands)
    if operations != 317 * width + 689 or length > 1222 * width + 2952:
        raise ValueError('proved instruction bound differs')
    receipt = dict(width=width, commands=length, data_moves=counts[LEFT] + counts[RIGHT],
                   gate_bit_operations=operations, initialize_bits=counts[INIT],
                   retire_bits=counts[RETIRE], markers=counts[MARK] + counts[UNMARK],
                   program_bits=9 * length, interpreter_steps=19 * length + 3, phases=phases)
    program = ('<' + ''.join(format(command, '09b') for command in commands) + '>').encode('ascii')
    return lengths, program, receipt


def execute(program, tapes):
    """Read binary instructions and return the final heads, registers and bill.

    Integer bit planes permit independent inputs to share one instruction
    trace. Every lane has the same head positions and marker symbols.
    """
    if len(tapes) != 25 or not program or program[0] != ord('<'):
        raise ValueError('invalid tape entrance')
    heads, registers = [0] * 25, [0, 0]
    position, steps, commands = 1, 1, 0
    while position < len(program) and program[position] != ord('>'):
        code = 0
        for _ in range(9):
            if position >= len(program) or program[position] not in (48, 49):
                raise ValueError('invalid instruction bits')
            code = 2 * code + program[position] - 48
            position += 1
            steps += 1
        op, tape = code >> 5, code & 31
        if op >= 10 or tape >= 25:
            raise ValueError('invalid instruction code')
        head, cells = heads[tape], tapes[tape]
        if op in (LEFT, RIGHT):
            head += 1 if op == RIGHT else -1
            if not 0 <= head < len(cells):
                raise ValueError('head leaves reserved region')
            heads[tape] = head
        elif op in (XORA, XORB, FLIPA, FLIPAB):
            if type(cells[head]) is not int:
                raise ValueError('bit operation on a marker or blank')
            if op in (XORA, XORB):
                registers[op - XORA] ^= cells[head]
            else:
                cells[head] ^= registers[0] if op == FLIPA else registers[0] & registers[1]
        else:
            before, after = {INIT: ('_', 0), RETIRE: (0, '_'), MARK: ('_', '>'), UNMARK: ('>', '_')}[op]
            if cells[head] != before:
                raise ValueError('allocation or retirement precondition fails')
            cells[head] = after
        commands += 1
        steps += 1
    if position != len(program) - 1 or program[position] != ord('>'):
        raise ValueError('invalid program end')
    steps += 1
    while position:
        position -= 1
        steps += 1
    return dict(heads=heads, registers=registers, program_head=position,
                commands=commands, interpreter_steps=steps)
