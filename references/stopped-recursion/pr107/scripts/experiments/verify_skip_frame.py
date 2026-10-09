#!/usr/bin/env python3
"""Replay the PR53/frame-compiler words, actual fixed profiles and assembly.

Every new XOR word, dirty basis column, frame incidence and fixed-basis
profile is checked. Unchanged data geometry and general transfer proofs
remain inherited dependencies; this is a finite conditional certificate.
"""
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import tempfile

from binary_frame_profile_prepare import prepare
from binary_frame_replay import replay
from skip_frame_compose import compose


def verify():
    here = Path(__file__).resolve().parent
    root = here.parents[1]
    certificates = root / 'certificates'
    stored = json.loads((certificates / 'skip-frame-compiler.json').read_text())
    axes = {}
    with tempfile.TemporaryDirectory(prefix='skip-frame-verify-') as directory:
        work = Path(directory)
        profiler = work / 'profiles'
        subprocess.run([
            'c++', '-O3', '-std=c++17',
            '-I', str(root / 'references/frame-compiler/pr48/scripts/partial_swap'),
            str(here / 'binary_frame_profiles.cpp'), '-o', str(profiler),
        ], check=True)
        for h in (23, 25):
            word = certificates / f'skip-frame-word-{h}.json.gz'
            receipt = replay(word)
            assert json.loads(json.dumps(receipt)) == stored['axes'][str(h)]['replay']
            transitions = work / f'word{h}.bin'
            prepared = prepare(word, transitions)
            expected = json.loads((certificates / f'skip-frame-transitions-{h}.json').read_text())
            assert json.loads(json.dumps(prepared)) == expected
            subprocess.run([str(profiler), str(transitions)], check=True, capture_output=True, text=True)
            profile = json.loads(Path(str(transitions)+'.profiles.json').read_text())
            expected = json.loads((certificates / f'skip-frame-profiles-{h}.json').read_text())
            assert profile == expected
            axes[str(h)] = dict(replay=receipt, transitions=prepared, profile=profile)
            print(f'PASS h={h}: full dirty basis, exact frame path, every fixed-basis profile', flush=True)
    result = compose()
    assert len(result['assembly']['constraints']) == 47
    assert len(result['assembly']['margins']) == 7
    validation = dict(
        status='PASS complete serialized-word replay, actual CRT profiles, exact recurrence and balanced assembly',
        axes=axes, kappa=str(result['kappa']), bit_saving=str(result['bit_saving']),
        strict_constraints=47, margins=7,
        certificate_sha256=sha256((certificates / 'skip-frame-kappa.json').read_bytes()).hexdigest(),
        source_binding='Source manifests, inherited manifest digest, compiler receipt source, both word digests, and all local compiler/verifier sources are bound by the exact composition certificate.',
        scope='Finite conditional witness; unchanged data geometry and general transfer proofs are inherited dependencies.')
    (certificates / 'skip-frame-validation.json').write_text(json.dumps(validation, indent=2, sort_keys=True)+'\n')
    print('PASS exact recurrence, 47 strict inequalities, seven margins, eventual cutoffs', flush=True)
    return result


if __name__ == '__main__':
    verify()
