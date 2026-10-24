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
import native as N
import price


def run():
    N.need(sha256((N.HERE/'PREDECESSOR-5383.json').read_bytes()).hexdigest() == 'd6a99bd75c6b7a2146b0fc4cfa038890aaf1d4adcdef42d767fdb40b687e61aa', 'Pinned PR5383 receipt')
    N.authenticate()
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
    result = N.encode({'status': 'PASS_CONDITIONAL_KAPPA_003026674765_COMPILER_MARGIN',
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
        (N.HERE / 'WORD.json.gz').write_bytes(gzip.compress(data, mtime=0))
        (N.HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    else:
        N.need(gzip.decompress((N.HERE / 'WORD.json.gz').read_bytes()) == data, 'Exact literal published word')
        N.need(N.read(N.HERE / 'RESULT.json') == result, 'Exact published replay result')
    if args.out:
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], **{k: result['arithmetic'][k] for k in ('kappa', 'gain_over_PR4610', 'raw_root_interval', 'paid_calls', 'productive_fields')}}, sort_keys=True))


if __name__ == '__main__':
    main()
