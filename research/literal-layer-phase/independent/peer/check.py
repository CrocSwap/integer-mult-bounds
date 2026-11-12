"""Independent literal-graph structural, amortization and history review.

No author interpreter, oracle or verifier is called. Numerical Gaussian
correctness is separately reviewed by the lead agent. OpenAI-assisted.
"""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import types

PACKAGE = Path('/workspace/scratch/be42ab5b7196/worker-c2/research/literal-layer-phase')
EXPECTED = '9a360817b80e869398927f38a4f110de0b5a1f9620eeb23b19e166f112b83f23'
EXPECTED_TABLE = '50505d6bd350224021d88d8e7e142a3188649a1d391c34ade732fced19336624'
BLANK = '_'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def gamma(n):
    word = bin(n)[2:]
    return '0' * (len(word) - 1) + word


def load_subject():
    source = (PACKAGE / 'phase.py').read_bytes()
    need(hashlib.sha256(source).hexdigest() == EXPECTED, 'source pin')
    spec = importlib.util.spec_from_file_location('peer_phase_subject', PACKAGE / 'phase.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Surface:
    def __init__(self, origin, index):
        self.origin = origin
        self.head = origin
        self.low = origin - (1 if index >= 2 else 0)
        self.high = origin + (index % 7 if index >= 2 else 0)
        self.cells = {origin - 2: '|', origin + 1000000: '1'}

    def get(self):
        return self.cells.get(self.head, BLANK)

    def move(self, amount):
        self.head += amount
        self.low = min(self.low, self.head)
        self.high = max(self.high, self.head)


def table_hash(code):
    return hashlib.sha256(json.dumps(code, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def validate_graph(code):
    operations = Counter()
    for instruction in code:
        opcode, *args = instruction
        need(opcode in ('read', 'write', 'move', 'goto', 'halt'), 'nonliteral opcode')
        operations[opcode] += 1
        if opcode in ('read', 'write', 'move'):
            need(type(args[0]) is int and 0 <= args[0] < 20, 'unfixed tape selector')
        if opcode == 'read':
            need(set(args[1]) <= {'_', '0', '1', '|'}, 'unfixed read alphabet')
            need(all(type(v) is int and 0 <= v < len(code) for v in args[1].values()), 'unfixed branch')
        if opcode == 'write':
            need(args[1] in ('_', '0', '1', '|'), 'unfixed write alphabet')
        if opcode == 'move':
            need(args[1] in (-1, 1), 'nonunit move')
        if opcode == 'goto':
            need(type(args[0]) is int and 0 <= args[0] < len(code), 'unfixed jump')
    return dict(sorted(operations.items()))


def fresh_surfaces():
    return [Surface((i * 19) - 113, i) for i in range(20)]


def set_public(tape, word, *, header=False):
    # Separately paid caller acquisition; private histories/heads never reset.
    tape.cells = {tape.origin - 2: '|', tape.origin + 1000000: '1'}
    for i, symbol in enumerate(word):
        tape.cells[tape.origin + i] = symbol
    if header:
        tape.cells[tape.origin + len(word)] = '|'


def execute(code, parameters, *, surfaces=None, extra=False, missing=False,
            expect_reject=False, check_counter_bill=True):
    p, d, r, D, P, S, K, rho, w = parameters
    L, Q = D * K, 2 ** (D * K)
    N, V = P * Q * S * r, 2 * P * Q * S * r * w
    words = (p, d, r, D, P, S, K, rho + 1, w)
    header = ''.join(map(gamma, words))
    packet = '0' * V + ('0' if extra else '')
    if missing:
        packet = packet[:-1]
    tapes = fresh_surfaces() if surfaces is None else surfaces
    need(all(t.head == t.origin for t in tapes), 'entry head')
    private_before = [dict(t.cells) for t in tapes[2:]]
    history_before = sum(t.high - t.low + 1 for t in tapes[2:])
    set_public(tapes[0], header, header=True)
    set_public(tapes[1], packet)
    public_before = [dict(t.cells) for t in tapes[:2]]
    records = [i for i, ins in enumerate(code)
               if ins[0] == 'read' and ins[1] == 11 and set(ins[2]) == {'_', '1'}
               and tuple(code[i + 1][:2]) == ('read', 8) and ins[2]['1'] == i + 1]
    need(len(records) == 4, 'four phase-entry locations')
    phase_at = dict(zip(records, range(4)))
    counters = {'read': Counter(), 'write': Counter(), 'move': Counter()}
    flips = 0
    record_ordinal = 0
    pc, steps, rejected = 0, 0, False
    for _ in range(5000000):
        if pc in phase_at and tapes[11].get() == '1':
            position = record_ordinal
            actual_bits = [tapes[16].cells.get(tapes[16].origin + j, BLANK) for j in range(L)]
            actual_mask = [tapes[15].cells.get(tapes[15].origin + j, BLANK) for j in range(L)]
            need(actual_mask == ['1' if j % K == rho else '0' for j in range(L)], 'generated mask')
            need(all(b in ('0', '1') for b in actual_bits), 'counter shape')
            value = sum((b == '1') << j for j, b in enumerate(actual_bits))
            phase = sum(b == '1' and m == '1' for b, m in zip(actual_bits, actual_mask)) % 4
            need(value == (position // S) % Q, 'full-domain address order')
            need(phase_at[pc] == phase, 'incremental phase invariant')
            need(tapes[10].head - tapes[10].origin == position // (Q * S), 'P repetition')
            need(tapes[11].head - tapes[11].origin == position % S, 'S repetition')
            need(tapes[8].head == tapes[8].origin, 'r repeat reset')
            need(tapes[1].head - tapes[1].origin == 2 * w * r * position, 'r complete coefficients')
            record_ordinal += 1
        opcode, *args = code[pc]
        pc += 1
        steps += 1
        if opcode == 'halt':
            break
        if opcode == 'goto':
            pc = args[0]
            continue
        tape = tapes[args[0]]
        counters[opcode][args[0]] += 1
        if opcode == 'read':
            symbol = tape.get()
            if symbol not in args[1]:
                rejected = True
                break
            pc = args[1][symbol]
        elif opcode == 'write':
            old = tape.get()
            if args[0] == 16 and old in ('0', '1') and args[1] in ('0', '1'):
                need(old != args[1], 'counter flip')
                flips += 1
            if args[1] == BLANK:
                tape.cells.pop(tape.head, None)
            else:
                tape.cells[tape.head] = args[1]
        else:
            tape.move(args[1])
    else:
        raise ValueError('review execution cap')
    need(rejected == expect_reject, 'rejection outcome')
    need(counters['write'][0] == 0, 'header was written')
    if rejected:
        need(counters['write'][1] == 0 and [dict(t.cells) for t in tapes[:2]] == public_before,
             'rejection modified public input')
        return {'rejected': True, 'steps': steps}
    need(record_ordinal == P * Q * S, 'exact full record cardinality')
    need(counters['read'][1] == V + 1 and counters['write'][1] == V, 'payload read/write cardinality')
    need(counters['read'][0] == len(header), 'header source-read extent')
    need(counters['move'][1] == 4 * V and counters['move'][0] == 2 * len(header), 'paid public returns')
    need([dict(t.cells) for t in tapes[:2]] == public_before, 'zero packet/public exterior changed')
    need([dict(t.cells) for t in tapes[2:]] == private_before, 'private body or guard not retired')
    need(all(t.head == t.origin for t in tapes), 'head not restored')
    need(flips == P * (2 * Q - 2), 'geometric ripple flip census')
    if check_counter_bill:
        expected_moves = 4 * L + 8 + P * (6 * Q - 4)
        need(counters['move'][15] == counters['move'][16] == expected_moves, 'exact carry/return move census')
    budget = len(header) + p + d + L + N * w + 1
    need(steps <= 65536 * budget, 'complete literal time envelope')
    history_after = sum(t.high - t.low + 1 for t in tapes[2:])
    need(history_before <= history_after <= history_before + 4 * V + 32 * (len(header) + p + d + L + w + 1),
         'retained history envelope')
    return {'parameters': parameters, 'steps': steps, 'records': record_ordinal,
            'flips': flips, 'counter_moves': counters['move'][16],
            'history_before': history_before, 'history_after': history_after,
            'budget_base': budget, 'payload_bits': V}


def changed_graph(label, old, new):
    source = (PACKAGE / 'phase.py').read_text()
    need(source.count(old) == 1, 'mutation anchor ' + label)
    module = types.ModuleType('phase_peer_mutant_' + label)
    module.__file__ = str(PACKAGE / 'phase.py')
    sys.modules[module.__name__] = module
    exec(compile(source.replace(old, new), module.__file__, 'exec'), module.__dict__)
    return module.compile_phase()[0]


def diagnostic(label, action, expected):
    try:
        action()
    except ValueError as error:
        need(expected in str(error), 'unexpected failure for ' + label + ': ' + str(error))
        return {'mutation': label, 'diagnostic': str(error)}
    raise ValueError('mutation escaped ' + label)


def main():
    subject = load_subject()
    code, alphabet = subject.compile_phase()
    need(len(code) == 2146 and table_hash(code) == EXPECTED_TABLE, 'frozen literal graph')
    opcodes = validate_graph(code)
    cases = [
        (1, 1, 1, 1, 1, 1, 1, 0, 3),
        (2, 4, 3, 2, 2, 3, 2, 0, 4),
        (3, 6, 2, 3, 3, 2, 2, 1, 5),
        (1, 4, 1, 4, 2, 1, 1, 0, 3),
        (2, 1, 3, 1, 2, 2, 4, 3, 4),
        (2, 3, 1, 1, 1, 2, 7, 6, 4),
        (3, 3, 2, 3, 1, 1, 3, 0, 5),
        (1, 1, 1, 1, 5, 4, 1, 0, 3),
        (2, 2, 5, 2, 1, 3, 2, 1, 6),
        (17, 29, 1, 2, 1, 1, 1, 0, 19),
        (1, 257, 1, 1, 1, 1, 1, 0, 3),
        (1, 1, 31, 1, 1, 1, 1, 0, 3),
    ]
    runs = [execute(code, case) for case in cases]
    surfaces = fresh_surfaces()
    identities = tuple(map(id, surfaces))
    reuse = []
    for case in (cases[2], cases[0], cases[5]):
        reuse.append(execute(code, case, surfaces=surfaces))
        need(tuple(map(id, surfaces)) == identities, 'physical role identity changed')
    need(reuse[1]['steps'] == runs[0]['steps'], 'small call rescanned historical capacity')
    rejection = [execute(code, cases[1], extra=True, expect_reject=True),
                 execute(code, cases[1], missing=True, expect_reject=True)]
    fixture = (1, 2, 1, 2, 2, 2, 2, 0, 3)
    bad_mask = changed_graph('wrong_mask', "('mask_active', ONE, 'build_after')",
                             "('mask_active', '0', 'build_after')")
    mutants = [diagnostic('wrong generated mask', lambda: execute(bad_mask, fixture), 'generated mask')]
    bad_cleanup = changed_graph('missing_cleanup', 'for tape in (MASK, COUNT):', 'for tape in (MASK,):')
    mutants.append(diagnostic('missing counter retirement', lambda: execute(bad_cleanup, fixture),
                              'private body or guard not retired'))
    long_scan = """a.mark('advanced'+str(mode))
        a.mark('peer_scan'+str(mode))
        a.op('read', COUNT, {'0': 'peer_step'+str(mode), ONE: 'peer_step'+str(mode),
                            BLANK: 'peer_done'+str(mode)})
        a.mark('peer_step'+str(mode))
        a.op('move', COUNT, 1)
        a.op('move', MASK, 1)
        a.op('goto', 'peer_scan'+str(mode))
        a.mark('peer_done'+str(mode))
        a.rewind(COUNT, BITS)"""
    bad_carry = changed_graph('full_scan_return',
                             "a.mark('advanced'+str(mode))\n        a.rewind(COUNT, BITS)", long_scan)
    functional = execute(bad_carry, fixture, check_counter_bill=False)
    mutants.append(diagnostic('unpriced full-width carry return', lambda: execute(bad_carry, fixture),
                              'exact carry/return move census'))
    output = {'status': 'PASS_INDEPENDENT_PHASE_STRUCTURE_REVIEW', 'source_sha256': EXPECTED,
              'program_sha256': EXPECTED_TABLE,
              'proof_sha256': hashlib.sha256((PACKAGE / 'PROOF.md').read_bytes()).hexdigest(),
              'reviewer_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'instruction_locations': len(code), 'opcodes': opcodes, 'alphabet': alphabet,
              'cases': runs, 'reuse': reuse, 'rejection_checks': rejection, 'mutations': mutants,
              'functionally_correct_full_scan_mutant': functional,
              'successful_runs': len(runs) + len(reuse),
              'record_entries': sum(x['records'] for x in runs + reuse),
              'successful_steps': sum(x['steps'] for x in runs + reuse),
              'scope': 'Independent interpreter and structural/cost/history evidence; root separately verifies Gaussian arithmetic.'}
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
