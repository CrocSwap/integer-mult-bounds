#!/usr/bin/env python3
"""In-memory semantic controls for the complete composed caller.

ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
"""
from decimal import Decimal
import json
from pathlib import Path
from unittest.mock import patch

import compare_logs as C


def edit(files, name, change):
    value = C.closed.strict.read_json(files[name])
    change(value)
    files[name] = C.encoded(value)


def log_links(files, index, digest):
    edit(files, 'STAGES.json', lambda rows: rows[index].update(log_sha256=digest))
    edit(files, 'REPLAY.json', lambda doc: doc['stages'][index].update(log_sha256=digest))


def exercise(left, right, left_context, right_context, left_outer, right_outer):
    positives, rejected = [], []

    def accepted(files, outer=right_outer):
        return C.compare(left, files, left_context, right_context, left_outer, outer)['equivalent']

    def negative(label, change=None, outer=right_outer):
        files = dict(right)
        if change:
            change(files)
        try:
            okay = accepted(files, outer)
        except (ValueError, KeyError, TypeError, UnicodeError):
            okay = False
        C.require(not okay, 'negative control accepted: ' + label)
        rejected.append(label)

    C.require(accepted(right), 'native fresh positive failed')
    positives.append('native-fresh-composition')
    C.require(C.compare(left, left, left_context, left_context, left_outer, left_outer)['equivalent'],
              'reference identity failed')
    positives.append('reference-identity')

    for style in ('lf', 'crlf', 'mixed'):
        files = dict(right)
        for index, name in enumerate(C.closed.STAGES):
            raw = C.canonical_log(files[name + '.log'])
            if style == 'crlf' or style == 'mixed' and index % 2:
                raw = raw.replace(b'\n', b'\r\n')
            files[name + '.log'] = raw
            log_links(files, index, C.closed.digest(raw))
        outer = C.canonical_log(right_outer)
        if style == 'crlf':
            outer = outer.replace(b'\n', b'\r\n')
        C.require(accepted(files, outer), 'valid log representation rejected: ' + style)
        positives.append('all-logs-' + style)

    for name in sorted(right):
        negative('missing:' + name, lambda f, n=name: f.pop(n))
    negative('extra-output', lambda f: f.update({'extra.log': b'not declared\n'}))

    for index, stage in enumerate(C.closed.STAGES):
        name = stage + '.log'
        def repaired(f, data, i=index, n=name):
            f[n] = data
            log_links(f, i, C.closed.digest(data))
        negative('semantic-log-with-repaired-links:' + stage,
                 lambda f, n=name, fn=repaired: fn(f, f[n] + b'CHANGED\n'))
        negative('bare-CR-with-repaired-links:' + stage,
                 lambda f, n=name, fn=repaired: fn(f, b'\r' + f[n]))
        negative('wrong-raw-link:' + stage,
                 lambda f, i=index: log_links(f, i, '0' * 64))
        def stale(f, n=name):
            # A legitimate representation change is invalid with OLD raw links.
            raw = C.canonical_log(f[n])
            f[n] = raw if raw != f[n] else raw.replace(b'\n', b'\r\n')
            C.require(f[n] != right[n], 'stale-edge fixture did not change bytes')
        negative('unrepaired-line-ending:' + stage, stale)
        for receipt in ('STAGES.json', 'REPLAY.json'):
            def missing_timing(f, p=receipt, i=index):
                def mutate(doc):
                    (doc if p == 'STAGES.json' else doc['stages'])[i].pop('seconds')
                edit(f, p, mutate)
            negative('missing-time:' + receipt + ':' + stage, missing_timing)

    lines = C.canonical_log(right_outer).splitlines(keepends=True)
    for index in range(13):
        changed = list(lines)
        changed[index] = b'WRONG ' + changed[index]
        negative('outer-line:' + str(index), outer=b''.join(changed))
    negative('outer-bare-CR', outer=b'\r' + right_outer)
    negative('outer-extra-line', outer=right_outer + b'EXTRA\n')
    negative('outer-missing-line', outer=b''.join(lines[:-1]))
    negative('outer-missing-final-newline', outer=C.canonical_log(right_outer).rstrip(b'\n'))

    roles = C.closed.strict.read_json(right['INDEPENDENT-T16.json'])['input_sha256']
    for index, key in enumerate(roles):
        negative('misbound-input-role:' + str(index),
                 lambda f, k=key: edit(f, 'INDEPENDENT-T16.json',
                                      lambda d: d['input_sha256'].update({k: '0' * 64})))
    negative('undeclared-seconds', lambda f: edit(f, 'ASSEMBLY.json', lambda d: d.update(seconds=1)))
    negative('scientific-CR-value', lambda f: edit(f, 'ASSEMBLY.json', lambda d: d.update(value='a\rb')))
    negative('changed-kappa', lambda f: edit(f, 'REPLAY.json', lambda d: d.update(kappa_decimal='0.01')))
    negative('boolean-stage-exit', lambda f: edit(f, 'STAGES.json',
                                                 lambda d: d[0].update(exit_code=False)))

    def invoice_with_repaired_links(f):
        name = 'global/audit/PREFIX-AND-INVOICE.json'
        edit(f, name, lambda d: d.update(changed_scientific_value=1))
        digest = C.closed.digest(f[name])
        for consumer in ('ASSEMBLY.json', 'ADMISSION-CONTROLS.json'):
            edit(f, consumer, lambda d: d['input_sha256'].update(fresh_invoice=digest))
    negative('changed-invoice-with-repaired-links', invoice_with_repaired_links)

    for raw in (b'{"x":1,"x":2}', b'{"x":NaN}'):
        negative('invalid-JSON:' + raw.decode('ascii'), lambda f, data=raw: f.update({'STAGES.json': data}))
    exact = {'large': 9007199254740993, 'decimal': Decimal('1.00000000000000000001'),
             'integral_decimal': Decimal('1.0'), 'integer': 1, 'boolean': True,
             'nested': [None, '\u03ba', Decimal('1E-1000')]}
    C.require(C.closed.strict.tree(exact) == C.closed.strict.tree(C.closed.strict.read_json(C.encoded(exact))),
              'serializer changed an exact typed value')
    positives.append('exact-typed-serialization')

    target = C.HERE / 'vendor/pr2344/compare_roles.py'
    original = Path.read_bytes
    def corrupted(path):
        value = original(path)
        return value + b'\n' if path == target else value
    with patch.object(Path, 'read_bytes', corrupted):
        try:
            C.authenticate_vendors()
        except ValueError:
            rejected.append('immutable-predecessor-mutation')
        else:
            raise ValueError('changed vendor accepted')

    C.require(accepted(right), 'controls altered original fresh output')
    return {'positive_count': len(positives), 'negative_count': len(rejected),
            'positives': positives, 'negative_cases': rejected}
