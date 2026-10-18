#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound, read-only frame -> owner -> moment bridge and failure controls."""
import gzip
import hashlib
import json
from pathlib import Path
import sys

P = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(P))
from owners import invoice, need
from test_owners import run_controls
from moments import certify
from frames import analyze


def digest(data):
    return hashlib.sha256(data).hexdigest()


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def read(name):
    raw = (P / 'inputs' / name).read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw,
                      object_pairs_hook=strict_object)


def source_binding():
    need(digest((P / 'INPUTS.json').read_bytes()) == '7f9a48928e0de34cf6df4023558ae382739a5129cbf0cdabb37728e3571e1e2b',
         'exact source inventory manifest')
    manifest = json.loads((P / 'INPUTS.json').read_bytes(), object_pairs_hook=strict_object)
    need(set(manifest) == {f.name for f in (P / 'inputs').iterdir() if f.is_file()},
         'complete frozen input inventory')
    for name, row in manifest.items():
        raw = (P / 'inputs' / name).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(len(raw) == row['bytes'] and digest(raw) == row['sha256'] and blob == row['git_blob'],
             'frozen source bytes: ' + name)
    return {name: row['sha256'] for name, row in sorted(manifest.items())}


def main():
    pins = source_binding()
    records, parent_records = {}, {}
    for tag, name in [('base', 'gauge44'), ('extra', 'extra')]:
        records[name] = analyze(read('WORD-' + tag + '.json.gz'))
        parent_records[name] = analyze(read('PARENT-' + tag + '.json.gz'))
    registry = read('PROVIDERS.json')
    for name, record in records.items():
        need(record['widths'] == registry[name]['widths'], 'ordered helper registry binding')
        need(record['profile'] == {int(k): v for k, v in registry[name]['actual_paid_profile'].items()},
             'local frame registry binding')
        need(record['buffer_count'] == 86 and parent_records[name]['buffer_count'] == 82,
             'four extra private buffers')
        need(record['helper_ids'] == parent_records[name]['helper_ids'],
             'unchanged actual helper identities and ordering')
        changed = [(helper, old, new) for helper, old, new in
                   zip(record['helper_ids'], parent_records[name]['widths'], record['widths'])
                   if old != new]
        need(changed == [(249, 9, 8), (251, 9, 8), (265, 9, 8), (267, 9, 8)],
             'exact four whole-helper width changes')

    order, fill, dispatch = read('ORDER.json'), read('FILL.json.gz'), read('DISPATCH.json')
    plan, template = read('PLAN.json.gz'), read('TEMPLATE.json.gz')
    profile, claim = read('PROFILE.json'), read('CLAIM.json')
    result = invoice(order, fill, dispatch, plan, template, records, profile,
                     claim['physical_families'])
    need(claim['physical_families'] == 66808 and claim['replicas'] == 74
         and claim['calls'] == 666 and claim['zero_buffers'] == 86, 'pinned claimed invoice')
    need({int(k): v for k, v in claim['profile'].items()} == result['profile'],
         'claim binds reconstructed profile')
    controls = run_controls(order, fill, dispatch, plan, template, records, profile)
    # A stale helper width must fail actual placement, independently of report equality.
    stale = {name: {**record, 'widths': list(record['widths'])}
             for name, record in records.items()}
    for name in stale:
        stale[name]['widths'][stale[name]['helper_ids'].index(249)] = 9
    try:
        invoice(order, fill, dispatch, plan, template, stale)
    except ValueError as error:
        need(str(error) in ('owner capacity', 'disjoint owner intervals'),
             'stale width fails placement, not an unrelated check')
        controls['rejecting']['restore_one_width_to_nine'] = str(error)
    else:
        raise ValueError('stale nine-wide helper fits unchanged fill')
    moment = certify(result['profile'], read('baseline-PROFILE.json'), read('baseline-CLAIM.json'))
    need(source_binding() == pins, 'input drift during replay')
    output = dict(status='PASS_NORMAL45_OWNER_COST_BRIDGE_NO_NEW_KAPPA',
                  source_sha256=pins, providers=records, parent_providers=parent_records,
                  owner_invoice=result, owner_controls=controls, moment=moment,
                  scope='Source-pinned finite frame/whole-owner/recursive-rank accounting; private namespace count. Operator/native realization, physical storage/precision/outer and all-size implications are not certified here.')
    rendered = json.dumps(output, sort_keys=True, indent=2) + '\n'
    if len(sys.argv) == 2 and sys.argv[1] == '--check-result':
        need(json.loads((P / 'RESULT.json').read_bytes()) == json.loads(rendered),
             'stored result equals fresh derivation')
        print(output['status'])
    else:
        need(len(sys.argv) == 1, 'only --check-result is supported')
        print(rendered, end='')


if __name__ == '__main__':
    main()
