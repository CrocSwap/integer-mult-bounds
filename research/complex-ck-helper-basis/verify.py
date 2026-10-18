#!/usr/bin/env python3
"""Reproduce a scoped CK helper-basis circuit result; Python 3.11+, stdlib.
Substantial OpenAI Codex assistance. Apache-2.0; see README.md for attribution.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from circuit import block_replay, construct, digest, dual, price, require, search
from fractions import Fraction as Q


def load_sources():
    pins = json.loads((HERE / 'SOURCE-PINS.json').read_text())
    sources = {}
    for name, record in pins['files'].items():
        raw = (ROOT / record['path']).read_bytes()
        if record['path'].endswith('.gz'):
            raw = gzip.decompress(raw)
        require(hashlib.sha256(raw).hexdigest() == record['payload_sha256'],
                'source hash: ' + name)
        sources[name] = json.loads(raw) if '.json' in record['path'] else raw
    spec = sources['spec']['providers']['ck']
    for name, filename in [('word', 'CANONICAL-WORD.json.gz'),
                           ('programs', 'LOCAL-PROGRAMS.json.gz')]:
        require(pins['files'][name]['payload_sha256'] ==
                spec['artifact_semantic_sha256'][filename], 'selected SPEC binding')
    return pins, sources


def controls(word, gates):
    reference = block_replay(word['compensation'])[0][:716]
    rejected = []
    mutations = {}
    mutations['omit_preparation'] = gates[1:]
    mutations['omit_restoration'] = gates[:-1]
    bad = copy.deepcopy(gates)
    bad[0][3] *= -1
    mutations['wrong_preparation_sign'] = bad
    bad = copy.deepcopy(gates)
    bad[-1][3] *= -1
    mutations['wrong_restoration_sign'] = bad
    bad = copy.deepcopy(gates)
    middle = next(i for i, e in enumerate(bad) if e[1] < 224)
    bad[middle][3] *= -1
    mutations['wrong_compensation_coefficient'] = bad
    for name, mutant in mutations.items():
        require(block_replay(mutant)[0][:716] != reference,
                'accepted semantic mutation: ' + name)
        rejected.append(name)
    bad = copy.deepcopy(gates)
    bad[0][2] = bad[0][1]
    try:
        block_replay(bad)
    except ValueError:
        rejected.append('aliased_preparation')
    else:
        raise ValueError('accepted aliased preparation')
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True,
                        help='fresh directory for generated evidence (never overwrites)')
    parser.add_argument('--write-certificate', action='store_true',
                        help='maintainer regeneration of this package certificate')
    args = parser.parse_args()
    pins, sources = load_sources()
    word = sources['word']
    recipe = search(word)
    replacement = construct(word, recipe)
    before = sum(price(Q(e[3], e[4])) for e in word['compensation'])
    after = sum(price(Q(e[3], e[4])) for e in replacement)
    require(before == recipe['before'] and before - after == recipe['saving'], 'total cost')
    for backward in (False, True):
        old = dual(word['compensation']) if backward else word['compensation']
        new = dual(replacement) if backward else replacement
        expected = block_replay(old)[0][:716]
        result, real = block_replay(new, primitives=True)
        require(result[:716] == expected and not result[716], 'arbitrary-input block map')
        require(real == after, 'independent primitive cost')
    print('PASS block: both orientations, all 716 live columns + private work', flush=True)
    rejected = controls(word, replacement)
    candidate = copy.deepcopy(word)
    candidate['compensation'] = replacement
    # The output directory is exclusively ours. Existing output is never clobbered.
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / 'CANONICAL-WORD.json.gz').write_bytes(gzip.compress(
        json.dumps(candidate, sort_keys=True, separators=(',', ':')).encode(), mtime=0))
    # -E ignores PYTHONOPTIMIZE; assertions are required by the retained auditors.
    for name in ('emitter', 'auditor'):
        with (args.out / (name + '.log')).open('w') as log:
            subprocess.run([sys.executable, '-E', '-B', str(ROOT / pins['files'][name]['path']),
                            str(args.out)], stdout=log, stderr=subprocess.STDOUT, check=True)
        print('PASS native ' + name, flush=True)
    programs = json.loads(gzip.decompress((args.out / 'LOCAL-PROGRAMS.json.gz').read_bytes()))
    checks = json.loads((args.out / 'LOCAL-CHECKS.json').read_text())
    audit = json.loads((args.out / 'INDEPENDENT-LOCAL-REPLAY.json').read_text())
    for orientation, events in programs.items():
        require([e for e in events if e[0] != 'scalar'] ==
                [e for e in sources['programs'][orientation] if e[0] != 'scalar'],
                'non-scalar event change')
        expected = sources['checks'][orientation]['real_component_primitive_bound'] - recipe['saving']
        require(checks[orientation]['real_component_primitive_bound'] == expected, 'full-program invoice')
        require(checks[orientation]['paid_profile'] == sources['checks'][orientation]['paid_profile'],
                'paid profile change')
    report = dict(status='PASS_CK_RESTORED_HELPER_BASIS', search=recipe,
                  compensation_macros_before=len(word['compensation']),
                  compensation_macros_after=len(replacement),
                  compensation_real_before=before, compensation_real_after=after,
                  candidate_word_semantic_sha256=hashlib.sha256(gzip.decompress(
                      (args.out / 'CANONICAL-WORD.json.gz').read_bytes())).hexdigest(),
                  program_checks=checks, local_replay=audit['local'],
                  controls=rejected, native_controls=audit['negative_controls_rejected'],
                  source_pins=pins, kappa='unchanged')
    encoded = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if args.write_certificate:
        (HERE / 'CERTIFICATE.json').write_text(encoded)
    else:
        require(json.loads((HERE / 'CERTIFICATE.json').read_text()) == report,
                'certificate mismatch')
    (args.out / 'EVIDENCE.json').write_text(encoded)
    print(f"PASS_CK_RESTORED_HELPER_BASIS pairs={len(recipe['pairs'])} "
          f"real_saved={recipe['saving']} columns=716+1 orientations=2 "
          f"controls={len(rejected)}+{len(audit['negative_controls_rejected'])} kappa=unchanged")


if __name__ == '__main__':
    main()
