#!/usr/bin/env python3
"""Verify the all-backward controller and complete conditional kappa.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The retained local checker and witnesses are from PR5383. Read README.md.
"""
import argparse
import json
import sys
from hashlib import sha256
sys.dont_write_bytecode = True
import native as N
import controller as C
import price

PREDECESSOR_PAYLOAD = '2aee5e997df99726fc763e510d9cb69fbe4f86114dc8d2cd33ad26c6c462a21d'
NATIVE_HASH = '3c8efab1f830868c054d33391ee2f8bc74f9bae9c134edf5b455790eb674c1c4'
WITNESS_HASH = '24599011da06325e1012619b2b84a4dd3aceb90ab42d3caaf6414879e7d16591'


def run():
    for name, digest in [('native.py', NATIVE_HASH), ('WITNESS.json', WITNESS_HASH)]:
        N.need(sha256((N.HERE / name).read_bytes()).hexdigest() == digest, 'Unchanged published predecessor: ' + name)
    N.authenticate()
    source = N.read(N.ROOT / N.SOURCE)
    local = N.construct(source)
    raw = (json.dumps(local, sort_keys=True, separators=(',', ':')) + '\n').encode()
    N.need(sha256(raw).hexdigest() == PREDECESSOR_PAYLOAD, 'Exact published PR5383 local word')
    c = local['canonical']
    before, after = {}, {}
    for direction in ('forward', 'backward'):
        back = direction == 'backward'
        before[direction] = N.replay(c, source['programs'][direction], back, False)
        N.need(before[direction]['paid'] == N.OLD_PAID and before[direction]['helpers'] == N.OLD_HELPERS, 'Selected source calibration')
    after['backward'] = N.replay(c, local['programs']['backward'], True, True)
    N.need(after['backward']['paid'] == N.NEW_PAID, 'Exact retained backward paid profile')
    native_controls = N.controls(c, local)
    identities = N.independent_source_identities(source)
    phase = N.phase_inheritance(source, local)
    word = C.construct()
    physical = C.physical(word)
    controls = C.controls(word)
    arithmetic = price.run(after, word)
    result = N.encode({'status': 'PASS_CONDITIONAL_KAPPA_00302728823_ALL_BACKWARD_CONTROLLER',
                       'source_native': before, 'backward_native': after['backward'],
                       'local_word_sha256': PREDECESSOR_PAYLOAD,
                       'unrestricted_source_identities': identities,
                       'source_phase_inheritance': phase,
                       'physical_wrapper': physical, 'native_controls': native_controls,
                       'controller_controls': controls, 'arithmetic': arithmetic})
    return word, result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    word, result = run()
    for name, value in [('CONTROLLER.json', word), ('RESULT.json', result)]:
        path = N.HERE / name
        if args.write:
            path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        else:
            N.need(json.loads(path.read_text()) == value, 'Exact published ' + name)
    print(json.dumps({'status': result['status'], **{k: result['arithmetic'][k] for k in ('kappa', 'gain_over_PR5392', 'raw_root_interval', 'paid_calls', 'productive_fields')}}, sort_keys=True))


if __name__ == '__main__':
    main()
