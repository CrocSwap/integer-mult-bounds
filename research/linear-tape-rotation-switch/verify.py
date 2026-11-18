"""Check literal transitions, ownership, controls and source table bits.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import hashlib
import json
from pathlib import Path

import independent
from program import compile_query, source
from sources import load

PACKAGE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def graph_check(code):
    size = len(code)
    for ins in code:
        kind = ins[0]
        need(kind in ('R', 'W', 'M', 'J', 'H'), 'literal instruction alphabet')
        if kind in ('R', 'W', 'M'):
            need(type(ins[1]) is int and 0 <= ins[1] < 14, 'literal tape role')
        if kind == 'R':
            need(set(ins[2]) == set(range(5)), 'complete read alphabet')
            need(all(type(v) is int and 0 <= v < size for v in ins[2].values()), 'read targets')
        elif kind == 'W':
            need(type(ins[2]) is int and 0 <= ins[2] < 5, 'literal write')
            need(ins[1] >= 5, 'borrowed descriptor write in graph')
        elif kind == 'M':
            need(type(ins[2]) is int and ins[2] in (-1, 1), 'unit move')
        elif kind == 'J':
            need(type(ins[1]) is int and 0 <= ins[1] < size, 'jump target')
        else:
            need(ins[1] in ('DONE', 'REJECT'), 'terminal state')


def execute(hw, code, labels, args, expected, overrides=None, outcome='DONE'):
    tapes = hw.fixture(*args, overrides=overrides)
    before = [t.cells[:] for t in tapes]
    limit = 1024 * (args[0] + 4)
    separate = independent.run(code, tapes, limit)
    need(separate['outcome'] == outcome, 'separate outcome')
    independent.check_return(separate, tapes, before, expected)
    cpu = hw.CPU(code, tapes, labels)
    need(cpu.run(limit) == outcome, 'primary outcome')
    span = hw.check_return(tapes, before, outcome, expected)
    need(span <= 16 * (args[0] + 4), 'historical span bound')
    need(cpu.steps == separate['steps'], 'instruction-count disagreement')
    need([t.cells for t in tapes] == separate['cells'], 'interpreter state disagreement')
    need([t.head for t in tapes] == separate['heads'], 'interpreter head disagreement')
    need([t.low for t in tapes] == separate['low'] and [t.high for t in tapes] == separate['high'],
         'interpreter historical-span disagreement')
    return cpu.steps, span


def finite_checks(hw, canonical, query, code, labels):
    entries = networks = total = 0
    peak = [0, None]
    trace = hashlib.sha256()
    for h in range(1, 4):
        for s in range(1, (1 << h) + 1):
            for a in range(s):
                layers = canonical.benes(canonical.rotation(1 << h, s, a))
                for j, (_, row) in enumerate(layers):
                    for x, bit in enumerate(row):
                        args = h, s, a, j, x
                        need(query.switch_bit(*args) == bit, 'arithmetic versus canonical')
                        steps, span = execute(hw, code, labels, args, bit)
                        trace.update(json.dumps([list(args), bit, steps, span]).encode())
                        total += steps; entries += 1
                        if steps > peak[0]: peak = [steps, list(args)]
                networks += 1
    old_code, old_labels = source.compile_query()
    row_total = old_total = row_peak = 0
    row_bits = []
    for a in range(17):
        row = canonical.benes(canonical.rotation(32, 17, a))[6][1]
        for x, bit in enumerate(row):
            args = 5, 17, a, 6, x
            steps, _ = execute(hw, code, labels, args, bit)
            row_total += steps; row_peak = max(row_peak, steps); row_bits.append(bit)
            tapes = hw.fixture(*args); before = [t.cells[:] for t in tapes]
            cpu = hw.CPU(old_code, tapes, old_labels)
            need(cpu.run(1024 * 8**2) == 'DONE', 'retained physical query')
            hw.check_return(tapes, before, 'DONE', bit); old_total += cpu.steps
    need(old_total == 1473152, 'retained 544-query service count')
    return {'complete_networks': networks, 'canonical_entries_per_interpreter': entries,
            'small_primary_transitions': total, 'small_peak': peak,
            'small_trace_sha256': trace.hexdigest(), 'historical_row_queries': len(row_bits),
            'historical_row_new_transitions': row_total, 'historical_row_old_transitions': old_total,
            'historical_row_new_peak': row_peak,
            'historical_row_bits_sha256': hashlib.sha256(bytes(row_bits)).hexdigest()}


def wide_checks(hw, query, code, labels):
    rows = []
    for h in (7, 17, 65, 129, 513, 1025, 4096):
        n = 1 << h
        cases = [(n, n//2, h-1, 0), (n-1, 1, 0, n-1),
                 (n-1, n//2, 2*h-2, n//2+1), (n-1, n//2-1, h, n//3),
                 (n, n-1, h//2, n-1), (n-1, 0, h-1, n-1)]
        for s, a, j, x in cases:
            steps, span = execute(hw, code, labels, (h, s, a, j, x),
                                  query.switch_bit(h, s, a, j, x))
            rows.append({'height': h, 'row': j, 'steps': steps, 'span': span})
    return rows


def controls(hw, query, code, labels):
    bad = [((0, 0, 0, 0, 0), None), ((2, 0, 0, 0, 0), None),
           ((2, 5, 0, 0, 0), None), ((2, 3, 3, 0, 0), None),
           ((2, 3, 0, 3, 0), None), ((2, 3, 0, 0, 4), None),
           ((2, 3, 0, 0, 0), {0: []}), ((2, 3, 0, 0, 0), {0: [0]}),
           ((2, 3, 0, 0, 0), {0: [0, 1, 0]}),
           ((2, 3, 0, 0, 0), {1: [1, 1]}),
           ((2, 3, 0, 0, 0), {2: [0, 0, 0, 0]}),
           ((2, 3, 0, 0, 0), {3: [0, 4, 0]}),
           ((2, 3, 0, 0, 0), {4: [0, 2, 0]})]
    for args, override in bad:
        execute(hw, code, labels, args, None, overrides=override, outcome='REJECT')
    witnesses = {'wrong_complement': (2, 2, 1, 1, 1),
                 'lost_carry': (2, 3, 1, 1, 1),
                 'lost_identity': (2, 2, 1, 1, 1)}
    for name, args in witnesses.items():
        changed, positions = compile_query(name)
        try:
            execute(hw, changed, positions, args, query.switch_bit(*args))
        except ValueError as exc:
            need('owner state' in str(exc), 'semantic mutation failed for wrong reason')
        else:
            raise ValueError('undetected semantic graph mutation')
    changed = list(code)
    index = next(i for i in range(labels['success'], len(code)) if code[i] == ('W', 6, 2))
    changed[index] = ('W', 6, 0)
    try:
        execute(hw, tuple(changed), labels, (2, 3, 1, 1, 1), 1)
    except ValueError as exc:
        need('owner state' in str(exc), 'retirement control failed for wrong reason')
    else:
        raise ValueError('uncleared private body accepted')
    tapes = hw.fixture(2, 3, 1, 1, 1); tapes[7] = tapes[6]
    for constructor in (lambda: hw.CPU(code, tapes, labels),
                        lambda: independent.run(code, tapes, 10000)):
        try:
            constructor()
        except ValueError:
            continue
        raise ValueError('aliased owners accepted')
    return {'domain_rejections_per_interpreter': len(bad), 'semantic_graph_mutants': 3,
            'retirement_mutants': 1, 'alias_rejections': 2}


def calculate():
    for row in json.loads((PACKAGE / 'SOURCE-PINS.json').read_text()):
        need(hashlib.sha256((PACKAGE / row['path']).read_bytes()).hexdigest() == row['sha256'],
             'retained source hash')
    hw = load('physical_source_hardware', 'retained/pr7593/hardware.py')
    query = load('closed_query_reference', 'retained/pr7734/query.py')
    canonical = load('canonical_network_reference', 'retained/pr4100/check_batched_crt.py')
    code, labels = compile_query(); graph_check(code)
    result = {'instructions': len(code), 'graph_sha256': source.digest(code), 'tapes': 14,
              'transition_bound': '1024*(h+4)', 'historical_span_bound': '16*(h+4)'}
    result.update(finite_checks(hw, canonical, query, code, labels))
    result['wide_queries'] = wide_checks(hw, query, code, labels)
    result.update(controls(hw, query, code, labels))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args(); result = calculate()
    if args.write_result:
        (PACKAGE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(result == json.loads((PACKAGE / 'RESULT.json').read_text()), 'result mismatch')
    print('PASS_LINEAR_TAPE_ROTATION_SWITCH 14 tapes; 1024*(h+4) transitions')


if __name__ == '__main__':
    main()
