#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent structural identities, all-input replay and semantic controls.

The free-operator auditor and structural checker are unchanged PR2908 sources.
This check is local; native, actual owners and complete outer admission are separate.
"""
import argparse
import copy
import gzip
import hashlib
import json
import sys
import types
from pathlib import Path

P = Path(__file__).resolve().parent


def read(p):
    b = p.read_bytes()
    return json.loads(gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, p):
    m = types.ModuleType(name)
    m.__file__ = str(p)
    sys.modules[name] = m
    exec(compile(p.read_bytes(), str(p), 'exec'), m.__dict__)
    return m


def save_word(p, w):
    p.write_bytes(gzip.compress(json.dumps(w, separators=(',', ':')).encode(), mtime=0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', type=Path, required=True)
    a = ap.parse_args()
    assert __debug__, 'assertions required by the independent structural checker'
    out = a.work.resolve()
    assert not out.exists() and not out.is_relative_to(P)
    pins = read(P / 'PINS.json')
    assert {f.relative_to(P).as_posix(): sha(f) for d in ('vendor', 'data')
            for f in (P / d).rglob('*') if f.is_file()} == pins
    out.mkdir(parents=True)
    pm = load('preload_move', P / 'vendor/preload_move.py')
    gen = load('paired_producer', P / 'producer.py')
    aud = load('independent_paired_audit', P / 'vendor/audit_local.py')
    structural = load('independent_paired_structure', P / 'structure.py')
    transforms = [read(P / f'data/TRANSFORM-{h}.json') for h in gen.HELPERS]
    records = {}
    controls = {}
    for tag in ('base', 'extra'):
        parent = read(P / f'data/PARENT-{tag}.json.gz')
        w = parent
        steps = []
        for transform in transforms:
            steps.append(structural.check(gen.refit(w, transform), transform, aud))
            w = gen.apply_stage(w, transform)
            for mode in ('omit-final-output', 'wrong-final-sign'):
                bad = copy.deepcopy(w)
                if mode == 'omit-final-output':
                    bad['restore'].pop()
                else:
                    bad['restore'][-1][3] *= -1
                profile, inventory = pm.frame_report(bad)
                bad['report']['local_profile'], bad['report']['width_inventory'] = profile, inventory
                z = copy.deepcopy(bad)
                z['A'] = z['A'][z['prelude_events']:]
                bad['cleanup'] = pm.derive_cleanup(z, set(map(int, z['helper_final'])))
                name = f'{tag}-{transform["helper"]}-{mode}'
                path = out / (name + '.json.gz')
                save_word(path, bad)
                try:
                    aud.run(path, out / (name + '.json'))
                except (AssertionError, RuntimeError, ValueError) as error:
                    controls[name] = str(error)
                else:
                    raise AssertionError('semantic mutant accepted: ' + name)
        assert gen.apply(parent, transforms) == w == read(P / f'data/WORD-{tag}.json.gz')
        audit_path = out / f'AUDIT-{tag}.json'
        aud.run(P / f'data/WORD-{tag}.json.gz', audit_path)
        audit = read(audit_path)
        assert audit['independent_inputs'] == 632 and audit['restored_cold'] == audit['zero_buffers'] == gen.BUFFERS
        assert audit['local_profile'] == gen.PROFILE and audit['width_inventory'] == gen.INVENTORY
        records[tag] = {'parent_sha256': sha(P / f'data/PARENT-{tag}.json.gz'),
                        'word_sha256': sha(P / f'data/WORD-{tag}.json.gz'),
                        'structures': steps, 'audit': audit}
    assert all(sha(P / n) == h for n, h in pins.items()), 'input drift'
    assert len(controls) == 4 * len(gen.HELPERS)
    result = {'status': 'PASS_NINE_ADDITIONAL_PAIRED_EXTRACTIONS', 'providers': records,
              'semantic_controls': controls,
              'scope': 'Exact finite local identity and invoice; full native/owner/outer checks separate.'}
    (out / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
