"""Check the stored tape program, complete endpoint and instruction bill.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""

from itertools import batched, product
from pathlib import Path
import gzip
import hashlib
import importlib.util
import json
import sys


ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('tape', ROOT / 'tape.py')
tape = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tape)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def entrance(width, lengths, cases):
    cells = [['<'] + [0] * length + ['>'] for length in lengths[:10]]
    cells += [['<'] + ['_'] * (length + 1) for length in lengths[10:]]
    expected = [row.copy() for row in cells]
    limit = 1 << (width - 1)
    for lane, (donors, target, diagnostic) in enumerate(cases):
        for port, value in enumerate((*donors, target)):
            require(-limit <= value < limit, 'fixture outside signed input range')
            for bit in range(width):
                cells[port][bit + 1] |= ((value >> bit) & 1) << lane
                expected[port][bit + 1] |= ((value >> bit) & 1) << lane
        cells[9][1] |= diagnostic << lane
        numerator = sum(donors[:4]) - sum(donors[4:])
        quotient, remainder = divmod(numerator, 2)
        invalid = int(remainder != 0 or quotient < -limit or quotient >= limit)
        for bit in range(width):
            expected[8][bit + 1] ^= ((quotient >> bit) & 1) << lane
        expected[9][1] |= (diagnostic ^ invalid) << lane
    return cells, expected


def check_endpoint(width, lengths, program, cases):
    cells, expected = entrance(width, lengths, cases)
    state = tape.execute(program, cells)
    require(cells == expected, 'complete tape endpoint differs from exact integer oracle')
    require(state['heads'] == [0] * 25 and state['registers'] == [0, 0]
            and state['program_head'] == 0, 'heads or control bits are not restored')
    require(state['interpreter_steps'] == 19 * state['commands'] + 3, 'decoder step bill differs')
    return state


def mutation_controls():
    lengths, program, _ = tape.compile_tape(2)
    words = [program[position:position + 9] for position in range(1, len(program) - 1, 9)]
    cases = list(tape.load_source('verify').cases_for(2))[:256]
    cases += [((1,) * 4 + (-2,) * 4, -2, 0), ((-1, 0, 0, 0, 0, 0, 0, 0), -1, 0)]
    def encode(parts):
        return b'<' + b''.join(parts) + b'>'
    changed = []
    for op in (tape.INIT, tape.RETIRE):
        index = next(i for i, word in enumerate(words) if int(word, 2) >> 5 == op)
        changed.append(encode(words[:index] + words[index + 1:]))
    changed.append(encode(words[:-1]))
    changed.append(b'<' + b'2' + program[2:])
    index = next(i for i, word in enumerate(words) if int(word, 2) >> 5 == tape.FLIPA)
    altered = words.copy()
    altered[index] = format((tape.FLIPAB << 5) | (int(words[index], 2) & 31), '09b').encode()
    changed.append(encode(altered))
    for bad in changed:
        try:
            check_endpoint(2, lengths, bad, cases)
        except ValueError:
            continue
        raise ValueError('changed instruction stream was accepted')
    detour = encode(words + [format(tape.RIGHT << 5, '09b').encode(), b'000000000'])
    before = check_endpoint(2, lengths, program, cases)
    after = check_endpoint(2, lengths, detour, cases)
    require(after['commands'] == before['commands'] + 2
            and after['interpreter_steps'] == before['interpreter_steps'] + 38,
            'endpoint-preserving movement escaped the price')
    return dict(rejected_programs=len(changed), priced_endpoint_preserving_detour=38)


def main():
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())
    for row in pins:
        raw = (ROOT / row['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source byte pin differs')
        require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
                == row['git_blob'], 'source Git blob differs')
    circuit = tape.load_source('circuit')
    sys.modules['circuit'] = circuit
    source = tape.load_source('verify')
    source.main()
    receipt = json.loads((ROOT / 'RESULT.json').read_text())
    actual, checked = [], {}
    for width in (1, 2, 3, 4, 8, 16, 1076):
        lengths, program, row = tape.compile_tape(width)
        require(len(program) == row['program_bits'] + 2, 'marked program size differs')
        require(sum(lengths) == 23 * width + 40, 'data stock differs')
        require(row['initialize_bits'] == row['retire_bits'] == 14 * width + 39,
                'work allocation or retirement count differs')
        if width in (1, 2, 1076):
            cases = source.cases_for(width)
            if width == 1:
                cases = ((donors, target, diagnostic) for donors in product((-1, 0), repeat=8)
                         for target in (-1, 0) for diagnostic in (0, 1))
            count = 0
            for batch in batched(cases, 256):
                state = check_endpoint(width, lengths, program, batch)
                require(state['commands'] == row['commands']
                        and state['interpreter_steps'] == row['interpreter_steps'], 'execution bill differs')
                count += len(batch)
            checked[str(width)] = count
        if width == 1076:
            require(gzip.decompress((ROOT / 'PROGRAM-1076.bits.gz').read_bytes()) == program,
                    'retained program differs from compilation')
            require(hashlib.sha256(program).hexdigest() == receipt['program_sha256'], 'program hash differs')
        actual.append(row)
    require(actual == receipt['width_receipts'] and checked == receipt['executed_cases'], 'receipt differs')
    require(mutation_controls() == receipt['controls'], 'control receipt differs')
    print('PASS_HALF_SUM_CLEAR_FIXED_TAPE', checked, actual[-1]['interpreter_steps'])


if __name__ == '__main__':
    main()
