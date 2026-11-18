"""Check complete physical rows, owner returns and literal source composition.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import hashlib
import json
from pathlib import Path

from interpreters import dense, sparse
from program import compile_row, point
from sources import load

PACKAGE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def graph_check(code, labels):
    for ins in code:
        kind = ins[0]
        need(kind in ('R', 'W', 'M', 'J', 'H'), 'literal opcode')
        if kind in ('R', 'W', 'M'):
            need(type(ins[1]) is int and 0 <= ins[1] < 15, 'literal owner')
        if kind == 'R':
            need(set(ins[2]) == set(range(5)), 'read alphabet')
            need(all(type(v) is int and 0 <= v < len(code) for v in ins[2].values()), 'read targets')
        elif kind == 'W':
            need(ins[1] >= 4 and type(ins[2]) is int and 0 <= ins[2] < 5, 'write boundary')
        elif kind == 'M':
            need(type(ins[2]) is int and ins[2] in (-1, 1), 'unit move')
        elif kind == 'J':
            need(type(ins[1]) is int and 0 <= ins[1] < len(code), 'jump target')
        else:
            need(ins[1] in ('DONE', 'REJECT'), 'outcome')
    retained, _ = point.compile_query()
    need(len(retained) == 3237 and point.source.digest(retained) ==
         '530e83add1f22dcbb2b207e7ede64b2cecc44cce71db5fb26706ce18b842f92c', 'point graph pin')
    for pc, ins in enumerate(retained):
        expected = ins
        if ins[0] == 'R':
            expected = ('R', ins[1], {s: labels['point_' + str(t)] for s, t in ins[2].items()})
        elif ins[0] == 'J':
            expected = ('J', labels['point_' + str(ins[1])])
        elif ins[0] == 'H':
            expected = ('J', labels['row_return' if ins[1] == 'DONE' else 'row_reject'])
        need(code[labels['point_' + str(pc)]] == expected, 'source instruction changed')
    return len(retained)


def fixture(hw, args):
    h, s, a, j = args
    bodies = [hw.bits(h, h.bit_length())] + [hw.bits(v, h+1) for v in (s, a, j)]
    tapes = [hw.Tape(body, origin=3+i%4) for i, body in enumerate(bodies)]
    tapes.extend(hw.Tape((), origin=3+i%5, private=True, capacity=h+2) for i in range(10))
    tapes.append(hw.Tape((), origin=7, capacity=1 << h))
    return tapes


def execute(hw, code, args, expected, outcome='DONE'):
    h = args[0]; n = 1 << h
    tapes = fixture(hw, args); before = [t.cells[:] for t in tapes]
    limit = 1280 * n * (h+4)
    independent = sparse(code, tapes, limit)
    result = dense(code, tapes, limit)
    need(result == independent, 'instruction path disagreement')
    need(result['outcome'] == outcome, 'wrong outcome')
    need(result['heads'] == [t.origin for t in tapes], 'head return')
    for i, tape in enumerate(tapes):
        wanted = before[i][:]
        if i == 14 and outcome == 'DONE':
            wanted[tape.origin:tape.origin+n] = expected
        need(result['cells'][i] == wanted, 'returned owner state')
        need(result['low'][i] >= tape.origin-1, 'opaque left access')
    need(not any(result['writes'][:4]), 'borrowed write')
    need(result['writes'][14] == (n if outcome == 'DONE' else 0), 'output lifetime')
    for i in range(4, 14):
        expected_guards = [3, 2] * (n if i >= 6 and outcome == 'DONE' else 1)
        if i == 6:
            expected_guards = [3, 2] + expected_guards
        need(tapes[i].guard_writes == expected_guards, 'private guard lifetime')
    need(not any(t.guard_writes for t in tapes[:4] + tapes[14:]), 'permanent guard write')
    span = sum(high-low+1 for low, high in zip(result['low'], result['high']))
    need(span <= n+20*(h+4), 'historical span bound')
    return result['steps'], span


def calculate():
    for row in json.loads((PACKAGE/'SOURCE-PINS.json').read_text()):
        need(hashlib.sha256((PACKAGE/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source hash')
    hw = load('row_source_hardware', 'retained/pr7593/hardware.py')
    canonical = load('row_canonical_network', 'retained/pr4100/check_batched_crt.py')
    query = load('row_closed_query', 'retained/pr7734/query.py')
    code, labels = compile_row(); retained_count = graph_check(code, labels)
    result = dict(instructions=len(code), graph_sha256=point.source.digest(code), tapes=15,
                  retained_point_instructions=retained_count, transition_bound='1280*2^h*(h+4)',
                  historical_span_bound='2^h+20*(h+4)')
    trace = hashlib.sha256(); networks = rows = entries = total = peak = 0
    for h in range(1, 4):
        for s in range(1, (1 << h)+1):
            for a in range(s):
                network = canonical.benes(canonical.rotation(1 << h, s, a)); networks += 1
                for j, (_, row) in enumerate(network):
                    args = (h, s, a, j); steps, span = execute(hw, code, args, row)
                    need([query.switch_bit(h, s, a, j, x) for x in range(1 << h)] == list(row), 'point oracle')
                    trace.update(json.dumps([args, row, steps, span]).encode())
                    rows += 1; entries += len(row); total += steps; peak = max(peak, steps)
    result.update(complete_networks=networks, complete_rows_per_interpreter=rows,
                  canonical_bits_per_interpreter=entries, small_transitions=total,
                  small_max_transitions=peak, small_trace_sha256=trace.hexdigest())
    row_bits = []; row_total = 0; row_peak = 0
    for a in range(17):
        args = (5, 17, a, 6); row = canonical.benes(canonical.rotation(32, 17, a))[6][1]
        steps, _ = execute(hw, code, args, row); row_total += steps; row_peak = max(row_peak, steps)
        row_bits.extend(row)
    result.update(historical_rows=17, historical_bits=544, historical_transitions=row_total,
                  historical_max_transitions=row_peak, historical_bits_sha256=hashlib.sha256(bytes(row_bits)).hexdigest())
    larger = []
    for h, s, a, j in [(6, 53, 25, 7), (7, 127, 1, 0), (8, 255, 127, 8),
                        (9, 511, 255, 16), (10, 1024, 512, 9), (12, 4095, 2047, 12)]:
        row = [query.switch_bit(h, s, a, j, x) for x in range(1 << h)]
        steps, span = execute(hw, code, (h, s, a, j), row)
        larger.append(dict(args=[h, s, a, j], bits=len(row), steps=steps, span=span,
                           bits_sha256=hashlib.sha256(bytes(row)).hexdigest()))
    result['larger_complete_rows'] = larger
    invalid = [(2, 0, 0, 0), (2, 5, 0, 0), (2, 3, 3, 0), (2, 3, 0, 3)]
    for args in invalid:
        execute(hw, code, args, [], outcome='REJECT')
    mutations = []
    bad = list(code); pos = next(i for i, ins in enumerate(code) if ins == ('W', 14, 0))
    bad[pos] = ('W', 14, 1); mutations.append(('wrong_output_bit', bad))
    bad = list(code); bad[labels['row_return']] = ('J', labels['row_done']); mutations.append(('missing_row_tail', bad))
    bad = list(code)
    pos = next(i for i in range(labels['row_done'], labels['row_reject']) if code[i] == ('W', 4, 2))
    bad[pos] = ('W', 4, 0); mutations.append(('failed_private_retirement', bad))
    args = (3, 7, 3, 2); expected = canonical.benes(canonical.rotation(8, 7, 3))[2][1]
    for name, changed in mutations:
        try:
            execute(hw, tuple(changed), args, expected)
        except ValueError as exc:
            need(str(exc) in ('returned owner state', 'head return'), 'wrong mutation failure')
        else:
            raise ValueError('mutation survived: '+name)
    for interpreter in (dense, sparse):
        tapes = fixture(hw, args); tapes[7] = tapes[6]
        try:
            interpreter(code, tapes, 10000)
        except ValueError as exc:
            need(str(exc) == 'fifteen distinct owners required', 'wrong alias failure')
        else:
            raise ValueError('aliased owners accepted')
    result.update(numeric_domain_rejections_per_interpreter=len(invalid), semantic_and_retirement_controls=[x[0] for x in mutations], alias_rejections=2)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args(); result = calculate()
    if args.write_result:
        (PACKAGE/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(result == json.loads((PACKAGE/'RESULT.json').read_text()), 'result mismatch')
    print('PASS_OWNED_CANONICAL_ROW_PRODUCER 15 tapes; complete owned rows and returns')


if __name__ == '__main__':
    main()
