#!/usr/bin/env python3
"""Actual compiler-code faults after whole healthy three-way agreement.

Controls share the root source-execution adapter, not the expected algorithms.
ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gc
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SUPPORT_SHA = 'f55e8085b9a62314f125e6033f2334257478f476eca6209de6f7e158faeea827'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n').encode()


def support():
    raw = (HERE / 'source_eval.py').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SUPPORT_SHA, 'source adapter changed')
    namespace = {'__file__': str(HERE / 'source_eval.py'), '__name__': 'pinned_control_adapter'}
    exec(compile(raw, str(HERE / 'source_eval.py'), 'exec'), namespace)
    return namespace


def replace_once(text, old, new):
    need(text.count(old) == 1, 'mutation anchor must occur exactly once')
    return text.replace(old, new)


def differences(before, after):
    vectors = {}
    for name in before['vectors']:
        a, b = before['vectors'][name], after['vectors'][name]
        changed = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        if changed:
            i = changed[0]
            vectors[name] = {'count': len(changed), 'first_rank': i,
                             'healthy_hex': a[i], 'mutant_hex': b[i]}
    summaries = sorted(k for k in before['summary']
                       if canonical(before['summary'][k]) != canonical(after['summary'][k]))
    return vectors, summaries


def packet():
    adapter = support()
    cases = adapter['authenticate']()
    reference = (HERE / 'CERTIFICATE.json').read_bytes()
    healthy_raw = adapter['packet']()
    # Whole bytes, rather than Python dict equality (0 == False / 1 == True).
    need(reference == healthy_raw, 'healthy complete reference packet differs')
    healthy = json.loads(healthy_raw)['cases'][0]
    compiler = (HERE / 'inputs/verify.py.txt').read_text()
    fixtures = [
        ('omit-local-source-slots', [('f[\'source_count\']+sum(f[\'exits\'].values())',
                                     'sum(f[\'exits\'].values())')], {'slots'}, None, False),
        ('omit-child-slots', [('for records in (leaves, units, columns, slots):',
                               'for records in (leaves, units, columns):')], {'slots'}, None, False),
        ('zero-instance-and-slot-invoices', [
            ("units[n] = a*f['units']", 'units[n] = 0'),
            ("slots[n] = a*(f['source_count']+sum(f['exits'].values())+(W+calls)*f['units'])",
             'slots[n] = 0')], {'units', 'slots'}, None, False),
        ('omit-whole-child-divisor', [('copies = count*(a//widths[e])',
                                      'copies = count*a')], None, 'whole-word rank-one identity', False),
        ('wrong-source-complement', [('e = n-rank if complement else rank',
                                      'e = rank')], None, 'all recursive ranks strictly decrease', False),
        ('omit-local-column-mass', [("columns[n] = a*f['column_mass']", 'columns[n] = 0')],
         None, 'whole-word rank-one identity', False),
        ('force-unit-replication', [], None, 'whole integer subprogram batches', True),
    ]
    rows = []
    for label, edits, expected_vectors, guard_message, forced in fixtures:
        text = compiler
        for old, new in edits:
            text = replace_once(text, old, new)
        namespace = adapter['load_source'](compiler_text=text)
        row = {'name': label, 'mutated_compiler_sha256': hashlib.sha256(text.encode()).hexdigest(),
               'forced_unit_replication': forced, 'case': cases[0]['name'],
               'maximum': cases[0]['maximum'], 'actual_text_edits': len(edits)}
        try:
            actual = adapter['evaluate_case'](namespace, cases[0], force_unit_replication=forced)
        except ValueError as error:
            need(guard_message is not None and str(error) == guard_message,
                 'unexpected source rejection for ' + label + ': ' + str(error))
            row.update({'source_guards': 'REJECTED', 'message': str(error)})
        else:
            need(guard_message is None, 'expected actual source rejection: ' + label)
            changed, summary = differences(healthy, actual)
            need(set(changed) == expected_vectors, 'unexpected changed vector set: ' + label)
            need(canonical(actual) != canonical(healthy), 'mutant did not change complete output')
            row.update({'source_guards': 'PASSED', 'whole_output': 'DIFFERS',
                        'changed_vectors': changed, 'changed_summary_fields': summary,
                        'whole_mutant_case_sha256': hashlib.sha256(canonical(actual)).hexdigest()})
        rows.append(row)
        del namespace
        gc.collect()
    return canonical({'schema': 'direct-compiler-counts-controls/1',
                      'healthy_packet_sha256': hashlib.sha256(healthy_raw).hexdigest(),
                      'fixtures': rows, 'guard_pass_output_differences': 3, 'guard_rejections': 4,
                      'scope': 'Finite actual compiler fault discrimination only; no all-n or native/physical admission.'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--emit', action='store_true')
    group.add_argument('--reference', type=Path)
    args = parser.parse_args()
    raw = packet()
    if args.emit:
        sys.stdout.buffer.write(raw)
        return
    reference = args.reference if args.reference is not None else HERE / 'CONTROLS.json'
    need(reference.read_bytes() == raw, 'complete control reference packet differs')
    print(json.dumps({'status': 'PASS_ACTUAL_DIRECT_COMPILER_CONTROLS', 'bytes': len(raw),
                      'sha256': hashlib.sha256(raw).hexdigest(), 'fixtures': 7}, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise SystemExit('FAIL_ACTUAL_DIRECT_COMPILER_CONTROLS: ' + str(error))
