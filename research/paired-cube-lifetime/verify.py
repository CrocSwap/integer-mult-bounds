#!/usr/bin/env python3
"""Reconstruct both physical words before certifying the conditional exponent.

Apache-2.0. huxint, with substantial OpenAI Codex assistance. See NOTICE.
Standard-library Python; run without -O. No search is performed here.
"""

from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import bit
import bit_merge
import parameters
from structured_bulk_assembly import js


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sources():
    """Pin the construction, checks, arithmetic and written proof inputs."""
    paths = [HERE/name for name in
             ('bit.py', 'bit_merge.py', 'complex.py', 'parameters.py', 'verify.py', 'PROOF.md', 'NOTICE')]
    paths += [p for p in (HERE/'selected').rglob('*')
              if p.is_file() and '__pycache__' not in p.parts]
    paths += list((ROOT/'scripts/paired_cube').glob('*.py'))
    paths += [ROOT/name for name in (
        'scripts/paired_cube_physical.py', 'scripts/paired_cube_producer.py',
        'scripts/paired_cube_network.py', 'scripts/three_stage_cover_network.py',
        'scripts/structured_bulk_assembly.py', 'scripts/audit_community_candidate.py',
        'scripts/certify.py', 'certificates/copied-centers-network.json',
        'research/paired-cube-bit/paired_cube_bit_word.py',
        'research/paired-cube-bit/check_paired_cube_bit.py',
        'research/paired-cube-bit/data/pair_module_p12.json',
        'research/paired-cube-bit/LEMMA.md',
        'notes/general-clifford-frames.tex', 'notes/paired-cube-construction.tex',
        'notes/paired-cube-sharing.tex', 'notes/paired-cube-assembly.tex',
        'notes/three-stage-cover-bit.tex', 'notes/three-stage-cover-rows.tex')]
    paths += [p for p in (ROOT/'references/paired-cube/sources').rglob('*') if p.is_file()]
    return {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}


def source_manifest():
    return dict(base_pr=161, base_commit='d14e29157bc905be1ced0776dd893d0714013f3a',
                complex_fusion_pr=163, source_sha256=sources(),
                assistance='Prepared by huxint with substantial OpenAI Codex assistance.')


def verify():
    need(not sys.flags.optimize, 'Run without -O; assertions must remain enabled')
    manifest = json.loads((HERE/'SOURCE.json').read_text())
    need(manifest == source_manifest(), 'Construction/proof source pins differ')
    spec = importlib.util.spec_from_file_location('lifetime_complex', HERE/'complex.py')
    complex_word = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(complex_word)
    print('Checking regenerated signed complex graph, frames and compensated reads...', flush=True)
    complex_result = complex_word.checked_record()
    print('Regenerating merged bit word from the frozen matching...', flush=True)
    (ROOT/'build').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='paired-cube-lifetime-', dir=ROOT/'build') as directory:
        baseline = Path(directory)
        arcs = json.loads((HERE/'selected/bit/arcs.json').read_text())
        merge = bit_merge.regenerate(baseline, arcs)
        print('Checking physical bit frames, every alias and all formal F2 inputs...', flush=True)
        bit_result = bit.checked_record(HERE/'selected/bit/frames.json',
                                        HERE/'selected/bit/profile.json', baseline=baseline, p=12)
    result = parameters.certificate(complex_result['profile'], bit_result, complex_result['scalar'])
    result['construction'] = dict(
        complex=complex_result,
        bit=bit_result,
        bit_merge={key: merge[key] for key in ('merge', 'checked', 'input_sha256')})
    # Numerical roots are discovery diagnostics, not certificate inputs.
    result['construction']['bit'].pop('numerical_root', None)
    result['source_manifest_sha256'] = sha256((HERE/'SOURCE.json').read_bytes()).hexdigest()
    return js(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Write the reconstructed certificate')
    parser.add_argument('--refresh-sources', action='store_true', help='Explicitly regenerate source pins before checking')
    args = parser.parse_args()
    need(not sys.flags.optimize, 'Run without -O; assertions must remain enabled')
    if args.refresh_sources:
        (HERE/'SOURCE.json').write_text(json.dumps(source_manifest(), indent=2, sort_keys=True)+'\n')
    result = verify()
    certificate = HERE/'certificate.json'
    if args.write:
        certificate.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(result == json.loads(certificate.read_text()), 'Saved certificate differs from complete reconstruction')
    print('PASS conditional kappa=%s; both physical words, exact supplier/assembly successors, 47 strict constraints'
          % result['kappa'], flush=True)


if __name__ == '__main__':
    main()
