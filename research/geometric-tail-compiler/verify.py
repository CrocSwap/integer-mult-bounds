#!/usr/bin/env python3
"""Replay the eight-relation native word and its complete conditional kappa.

Derived from Ali Romman PR5377; new construction by Dugongue,
with substantial OpenAI Codex assistance. Apache-2.0.
Read README.md for the source credit and inherited proof obligations.
"""
from hashlib import sha256
import argparse
import gzip
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import importlib.util
HERE=Path(__file__).resolve().parent
vendor=HERE/'vendor'
manifest=json.loads((HERE/'VENDOR.json').read_text())
for name,digest in manifest['files'].items():
    if sha256((vendor/name).read_bytes()).hexdigest()!=digest:raise ValueError('Frozen vendor drift: '+name)
spec=importlib.util.spec_from_file_location('native',vendor/'native.py')
N=importlib.util.module_from_spec(spec);sys.modules['native']=N;spec.loader.exec_module(N)
N.ROOT=HERE.parents[1]
import price



def run():
    N.need(sha256((N.HERE/'PREDECESSOR-5383.json').read_bytes()).hexdigest() == 'd6a99bd75c6b7a2146b0fc4cfa038890aaf1d4adcdef42d767fdb40b687e61aa', 'Pinned PR5383 receipt')
    N.authenticate()
    from strictify import completed_upper, logarithm_power, finite_threshold
    for args in [(1,0,price.Q(1,2),price.Q(1,2)),(1,price.Q(1,2),price.Q(1),price.Q(1,2)),(1,0.1,price.Q(1,2),price.Q(1,2))]:
        try:completed_upper(*args)
        except ValueError:pass
        else:raise ValueError('Invalid or inexact completion input accepted')
    for call in [lambda:logarithm_power(price.Q(1),price.Q(1,2),price.Q(2)),lambda:finite_threshold(price.Q(0),2)]:
        try:call()
        except ValueError:pass
        else:raise ValueError('Invalid compiler input accepted')
    relation_basis=N.check_relation_basis()
    source = N.read(N.ROOT / N.SOURCE)
    candidate = N.construct(source)
    c = candidate['canonical']
    before, after = {}, {}
    for direction in ('forward', 'backward'):
        back = direction == 'backward'
        before[direction] = N.replay(c, source['programs'][direction], back, False)
        after[direction] = N.replay(c, candidate['programs'][direction], back, back)
        N.need(before[direction]['paid'] == N.OLD_PAID and before[direction]['helpers'] == N.OLD_HELPERS, 'Pinned source census')
        N.need(after[direction]['paid'] == candidate['paid_profiles'][direction], 'Emitted direction-specific paid profile')
        helpers = dict(N.OLD_HELPERS)
        if back: helpers[9] -= 8
        N.need(after[direction]['paid'] == (N.NEW_PAID if back else N.OLD_PAID) and after[direction]['helpers'] == helpers, 'Actual complete changed native census')
    identities = N.independent_source_identities(source)
    phase = N.phase_inheritance(source, candidate)
    controls = N.controls(c, candidate)
    arithmetic = price.run(after)
    data = (json.dumps(candidate, sort_keys=True, separators=(',', ':')) + '\n').encode()
    result = N.encode({'status': 'PASS_CONDITIONAL_KAPPA_0030266747680744_GEOMETRIC_TAILS',
                       'relation_basis': relation_basis, 'source_payload_sha256': N.PAYLOAD, 'word_payload_sha256': sha256(data).hexdigest(),
                       'source_native': before, 'candidate_native': after, 'independent_source_identities': identities,
                       'phase_inheritance': phase, 'native_negative_controls': controls, 'arithmetic': arithmetic,
                       'scope': 'Exact finite word, full all-column endpoints, ownership, p16 bill and compiler arithmetic. Retains source native phase, allowed owned erasure, mixed-target all-size, analytic, precision, tape, prime and exact-recovery contracts. No selected-frontier update.'})
    return data, result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true', help='Write only this package word and result after all checks pass.')
    ap.add_argument('--out', type=Path, help='Write a replay result to a separate path.')
    args = ap.parse_args()
    data, result = run()
    if args.write:
        N.need(gzip.decompress((N.HERE/'WORD.json.gz').read_bytes())==data,'Frozen predecessor word unchanged')
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    else:
        N.need(gzip.decompress((N.HERE / 'WORD.json.gz').read_bytes()) == data, 'Exact literal published word')
        N.need(N.read(HERE / 'RESULT.json') == result, 'Exact published replay result')
    if args.out:
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], **{k: result['arithmetic'][k] for k in ('kappa', 'gain_over_PR4610', 'raw_root_interval', 'paid_calls', 'productive_fields')}}, sort_keys=True))


if __name__ == '__main__':
    main()
