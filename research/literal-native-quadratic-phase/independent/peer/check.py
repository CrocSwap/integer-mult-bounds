"""Independent local-graph geometry, phase-state, cost and history review.

Uses the supplied graph builder, never its Machine/Tape, oracle or verifier.
Zero payloads isolate structural obligations; root separately checks arithmetic.
Prepared for Jerry Chen / CubeJerry with OpenAI assistance. No new kappa.
"""
from collections import Counter
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import types

EXPECTED = '2be149aa1be504509bb480f85396f0be302082d638e81422f747daee5a3c1ce7'
EXPECTED_TABLE = 'e10a0070af3331d23963fb97ebcd4bb7e81314d94a43d41ce00d4c84c5747638'
EXPECTED_PROOF = '55f0a575f618bf467d0e25a25802053455d701cee1f23fb8811a671a1bd59ff3'
BLANK = '_'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def gamma(n):
    word = bin(n)[2:]
    return '0' * (len(word) - 1) + word


def load_subject(package):
    need(hashlib.sha256((package / 'phase.py').read_bytes()).hexdigest() == EXPECTED, 'source pin')
    need(hashlib.sha256((package / 'PROOF.md').read_bytes()).hexdigest() == EXPECTED_PROOF, 'proof pin')
    spec = importlib.util.spec_from_file_location('b3_peer_subject', package / 'phase.py')
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


def fresh_surfaces():
    return [Surface(i * 19 - 113, i) for i in range(23)]


def set_public(tape, word, header=False):
    # Separately paid caller acquisition; preserve private histories and objects.
    tape.cells = {tape.origin - 2: '|', tape.origin + 1000000: '1'}
    tape.cells.update({tape.origin + i: bit for i, bit in enumerate(word)})
    if header:
        tape.cells[tape.origin + len(word)] = '|'


def table_hash(code):
    return hashlib.sha256(json.dumps(code, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def validate_graph(code):
    operations = Counter()
    for instruction in code:
        opcode, *args = instruction
        need(opcode in ('read', 'write', 'move', 'goto', 'halt'), 'nonliteral opcode')
        operations[opcode] += 1
        if opcode in ('read', 'write', 'move'):
            need(type(args[0]) is int and 0 <= args[0] < 23, 'unfixed tape selector')
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


def execute(code, recipe, parameters, *, surfaces=None, extra=False, missing=False,
            expect_reject=False, check_counter_bill=True):
    linear, rows, constant = recipe
    m = len(linear)
    f, r, P, S, w = parameters
    radix, Q = 2 ** f, 2 ** (m * f)
    V = 2 * P * Q * S * r * w
    header = ''.join(map(gamma, parameters))
    packet = '0' * V + ('0' if extra else '')
    if missing:
        packet = packet[:-1]
    tapes = fresh_surfaces() if surfaces is None else surfaces
    need(all(t.head == t.origin for t in tapes), 'entry head')
    private_before = [dict(t.cells) for t in tapes[2:]]
    history_before = sum(t.high - t.low + 1 for t in tapes[2:])
    set_public(tapes[0], header, True)
    set_public(tapes[1], packet)
    public_before = [dict(t.cells) for t in tapes[:2]]
    records = [i for i, ins in enumerate(code)
               if ins[0] == 'read' and ins[1] == 9 and set(ins[2]) == {'_', '1'}
               and tuple(code[i + 1][:2]) == ('read', 7) and ins[2]['1'] == i + 1]
    need(len(records) == 4, 'four phase-entry locations')
    phase_at = dict(zip(records, range(4)))
    counters = {'read': Counter(), 'write': Counter(), 'move': Counter()}
    flips = Counter()
    record_ordinal, pc, steps, rejected = 0, 0, 0, False
    for _ in range(5000000):
        if pc in phase_at and tapes[9].get() == '1':
            pos = record_ordinal
            values = []
            for i in range(m):
                tape = tapes[14 + i]
                bits = [tape.cells.get(tape.origin + j, BLANK) for j in range(f)]
                need(all(bit in ('0', '1') for bit in bits), 'counter shape')
                need(tape.head == tape.origin, 'record counter origin')
                values.append(sum((bit == '1') << j for j, bit in enumerate(bits)))
            expected = [((pos // S) // radix ** (m - 1 - i)) % radix for i in range(m)]
            need(values == expected, 'full-domain address order')
            phase = constant * f + sum(a.bit_count() * alpha for a, alpha in zip(values, linear))
            phase += 2 * sum((values[i] & values[j]).bit_count()
                             for i in range(m) for j in range(i + 1, m) if rows[i] >> j & 1)
            need(phase_at[pc] == phase % 4, 'absolute quadratic phase invariant')
            need(tapes[8].head - tapes[8].origin == pos // (Q * S), 'P repetition')
            need(tapes[9].head - tapes[9].origin == pos % S, 'S repetition')
            need(tapes[7].head == tapes[7].origin, 'r repeat reset')
            need(tapes[1].head - tapes[1].origin == 2 * w * r * pos, 'r complete coefficients')
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
            if 14 <= args[0] < 14 + m and old in ('0', '1') and args[1] in ('0', '1'):
                need(old != args[1], 'counter flip')
                need(len({t.head - t.origin for t in tapes[14:14 + m]}) == 1,
                     'synchronized counter column')
                flips[args[0]] += 1
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
    F = 2 * Q - 2
    segments = sum(radix ** j for j in range(1, m + 1))
    need(sum(flips.values()) == P * F, 'geometric ripple flip census')
    need(all(flips[14 + i] == P * (2 * radix - 2) * radix ** i for i in range(m)),
         'per-coordinate flip census')
    if check_counter_bill:
        expected_moves = 4 * f + 8 + P * (2 * F + 2 * segments)
        need(all(counters['move'][14 + i] == expected_moves for i in range(m)),
             'exact carry/return move census')
        need(all(counters['move'][14 + i] == 4 for i in range(m, 9)), 'unused counter motion')
    budget = len(header) + (m + 1) * f + r + P + S + w + (m + 1) ** 2 * P * Q + V + 1
    need(steps <= 65536 * budget, 'complete literal time envelope')
    history_after = sum(t.high - t.low + 1 for t in tapes[2:])
    history_budget = 2 * V + 4 * len(header) + (m + 4) * f + 4 * (r + P + S) + 8 * w + 256
    need(history_before <= history_after <= history_before + history_budget, 'retained history envelope')
    return {'parameters': parameters, 'dimension': m, 'steps': steps, 'records': record_ordinal,
            'flips': sum(flips.values()), 'counter_moves': counters['move'][14],
            'history_before': history_before, 'history_after': history_after,
            'budget_base': budget, 'payload_bits': V}


def changed_graph(package, label, old, new, recipe):
    source = (package / 'phase.py').read_text()
    need(source.count(old) == 1, 'mutation anchor ' + label)
    module = types.ModuleType('b3_peer_mutant_' + label)
    module.__file__ = str(package / 'phase.py')
    sys.modules[module.__name__] = module
    exec(compile(source.replace(old, new), module.__file__, 'exec'), module.__dict__)
    return module.compile_phase(*recipe)[0]


def diagnostic(label, action, expected):
    try:
        action()
    except ValueError as error:
        need(expected in str(error), 'unexpected failure for ' + label + ': ' + str(error))
        return {'mutation': label, 'diagnostic': str(error)}
    raise ValueError('mutation escaped ' + label)


def shared_helpers(package):
    old = (package / 'reference' / 'outer-phase.py').read_bytes()
    need(hashlib.sha256(old).hexdigest() == '9a360817b80e869398927f38a4f110de0b5a1f9620eeb23b19e166f112b83f23',
         'C2 source pin')
    before = {node.name: ast.dump(node, include_attributes=False) for node in ast.parse(old).body
              if isinstance(node, ast.FunctionDef)}
    after = {node.name: ast.dump(node, include_attributes=False)
             for node in ast.parse((package / 'phase.py').read_text()).body
             if isinstance(node, ast.FunctionDef)}
    names = ('fresh', 'clear', 'unary_copy', 'header_step', 'gamma', 'trace_return',
             'load_component', 'negate', 'stage_component')
    need(all(before[name] == after[name] for name in names), 'retained helper AST identity')
    return names


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('package', type=Path)
    args = parser.parse_args()
    package = args.package.resolve()
    subject = load_subject(package)
    selected = (subject.SELECTED_LINEAR, subject.SELECTED_ROWS, subject.SELECTED_CONSTANT)
    code, alphabet = subject.compile_phase()
    need(len(code) == 8211 and table_hash(code) == EXPECTED_TABLE, 'frozen literal graph')
    opcodes = validate_graph(code)
    helpers = shared_helpers(package)
    one = ((3,), (1,), 1)
    two = ((1, 3), (3, 3), 2)
    three = ((3, 2, 1), (7, 1, 5), 3)
    four = ((0, 1, 2, 3), (14, 15, 11, 15), 1)
    fixtures = [
        (selected, (1, 1, 1, 1, 1)),
        (selected, (1, 2, 2, 2, 3)),
        (one, (9, 1, 1, 1, 2)),
        (two, (3, 2, 2, 2, 3)),
        (three, (2, 1, 3, 2, 4)),
        (three, (3, 1, 2, 1, 2)),
        (four, (2, 2, 1, 2, 2)),
        (one, (1, 31, 3, 3, 7)),
    ]
    runs = []
    for recipe, parameters in fixtures:
        graph = subject.compile_phase(*recipe)[0]
        validate_graph(graph)
        runs.append(execute(graph, recipe, parameters))
    tapes = fresh_surfaces()
    identities = tuple(map(id, tapes))
    reuse = []
    for parameters in ((1, 2, 2, 2, 3), (1, 1, 1, 1, 1), (1, 3, 3, 1, 3)):
        reuse.append(execute(code, selected, parameters, surfaces=tapes))
        need(tuple(map(id, tapes)) == identities, 'physical role identity changed')
    need(reuse[1]['steps'] == runs[0]['steps'], 'small call rescanned historical capacity')
    rejection = [execute(code, selected, (1, 1, 1, 1, 1), extra=True, expect_reject=True),
                 execute(code, selected, (1, 1, 1, 1, 1), missing=True, expect_reject=True)]
    recipe, parameters = two, (3, 1, 2, 2, 2)
    bad_constant = changed_graph(package, 'missing_tensor_constant', '(mode+constant) % 4',
                                 '(mode+0) % 4', recipe)
    mutants = [diagnostic('missing tensor constant', lambda: execute(bad_constant, recipe, parameters),
                          'absolute quadratic phase invariant')]
    bad_geometry = changed_graph(package, 'unsynchronized_counters',
        "for tape in counters:\n                        a.op('move', tape, 1)",
        "for tape in (counters[i],):\n                        a.op('move', tape, 1)", recipe)
    mutants.append(diagnostic('unsynchronized counters', lambda: execute(bad_geometry, recipe, parameters),
                              'synchronized counter column'))
    long_scan = """a.mark('advanced'+str(mode))
        a.mark('peer_scan'+str(mode))
        a.op('read', counters[0], {'0': 'peer_step'+str(mode), ONE: 'peer_step'+str(mode),
                                  BLANK: 'peer_done'+str(mode)})
        a.mark('peer_step'+str(mode))
        for tape in counters:
            a.op('move', tape, 1)
        a.op('goto', 'peer_scan'+str(mode))
        a.mark('peer_done'+str(mode))"""
    bad_cost = changed_graph(package, 'full_width_return', "a.mark('advanced'+str(mode))", long_scan, recipe)
    # Establish that the third mutation passes functionality and only loses the
    # independently derived exact amortized movement bill.
    functional_mutant = execute(bad_cost, recipe, parameters, check_counter_bill=False)
    mutants.append(diagnostic('functionally correct full-width return',
        lambda: execute(bad_cost, recipe, parameters), 'exact carry/return move census'))
    result = {
        'status': 'PASS_B3_INDEPENDENT_STRUCTURE', 'source_sha256': EXPECTED,
        'proof_sha256': EXPECTED_PROOF, 'table_sha256': EXPECTED_TABLE,
        'locations': len(code), 'tapes': 23, 'opcodes': opcodes,
        'identical_C2_helpers': list(helpers), 'runs': runs, 'same_owner_reuse': reuse,
        'cardinality_rejections': rejection, 'mutation_checks': mutants,
        'functional_full_width_mutant_steps': functional_mutant['steps'],
        'complete_selected_dimensions': {'m': 9, 'f': [1]},
        'all_success_steps': sum(run['steps'] for run in runs + reuse),
        'all_success_records': sum(run['records'] for run in runs + reuse),
        'scope': 'Zero-valued structural fixtures; no claim of complete selected f>1 enumeration.'
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
