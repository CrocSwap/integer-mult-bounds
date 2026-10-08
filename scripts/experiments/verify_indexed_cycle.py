#!/usr/bin/env python3
"""Replay the aligned indexed-cycle/interval words with profile-cost pending live compilation and exact profiles.

Every new XOR word, dirty basis column, frame incidence and fixed-basis
profile is checked. Unchanged data geometry and general transfer proofs
remain inherited dependencies; this is a finite conditional certificate.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')

from hashlib import sha256
from pathlib import Path
import json
import os
import shlex
import subprocess
import tempfile

from binary_frame_profile_prepare import prepare
from binary_frame_replay import replay
from indexed_cycle_compose import compose, check_sources
from indexed_cycle_compiler import compile_axis


def verify_one_axis(args):
    h, work_str, profiler_str, cert_str = args
    work = Path(work_str)
    profiler = Path(profiler_str)
    certificates = Path(cert_str)
    stored = json.loads((certificates / 'indexed-cycle-compiler.json').read_text())
    word = certificates / f'indexed-cycle-word-{h}.json.gz'
    import gzip
    compiled, regenerated = compile_axis(h)
    assert json.loads(json.dumps(compiled)) == stored['axes'][str(h)]['compiled'], 'Regenerated compiler receipt differs'
    regenerated_raw = (json.dumps(regenerated, separators=(',', ':'))+'\n').encode()
    assert regenerated_raw == gzip.decompress(word.read_bytes()), 'Regenerated physical word differs'
    receipt = replay(word)
    assert json.loads(json.dumps(receipt)) == stored['axes'][str(h)]['replay']
    transitions = work / f'word{h}.bin'
    prepared = prepare(word, transitions)
    expected = json.loads((certificates / f'indexed-cycle-transitions-{h}.json').read_text())
    assert json.loads(json.dumps(prepared)) == expected
    subprocess.run([str(profiler), str(transitions)], check=True, capture_output=True, text=True)
    profile = json.loads(Path(str(transitions)+'.profiles.json').read_text())
    expected = json.loads((certificates / f'indexed-cycle-profiles-{h}.json').read_text())
    assert profile == expected
    print(f'PASS h={h}: full dirty basis, exact frame path, every fixed-basis profile', flush=True)
    return h, dict(replay=receipt, transitions=prepared, profile=profile)


def verify():
    import sys
    if sys.flags.optimize:
        raise ValueError('Assertions must remain enabled')
    check_sources()
    here = Path(__file__).resolve().parent
    root = here.parents[1]
    certificates = root / 'certificates'
    axes = {}
    with tempfile.TemporaryDirectory(prefix='indexed-cycle-verify-') as directory:
        work = Path(directory)
        profiler = work / 'profiles'
        subprocess.run([
            *shlex.split(os.environ.get('CXX', 'c++')), '-O3', '-std=c++17',
            '-I', str(root / 'references/frame-compiler/pr48/scripts/partial_swap'),
            str(here / 'binary_frame_profiles.cpp'), '-o', str(profiler),
        ], check=True)
        from concurrent.futures import ProcessPoolExecutor
        tasks = [(h, str(work), str(profiler), str(certificates)) for h in (23, 25)]
        with ProcessPoolExecutor(max_workers=2) as pool:
            for h, data in pool.map(verify_one_axis, tasks):
                axes[str(h)] = data
    result = compose()
    assert len(result['assembly']['constraints']) == 47
    assert len(result['assembly']['margins']) == 7
    validation = dict(
        status='PASS complete serialized-word replay, actual CRT profiles, exact recurrence and balanced assembly',
        axes=axes, kappa=str(result['kappa']), bit_saving=str(result['bit_saving']),
        strict_constraints=47, margins=7,
        certificate_sha256=sha256((certificates / 'indexed-cycle-kappa.json').read_bytes()).hexdigest(),
        source_binding='Source manifests, inherited manifest digest, compiler receipt source, both word digests, and all local compiler/verifier sources are bound by the exact composition certificate.',
        producer_words_regenerated_and_matched=True,
        scope='Finite conditional witness; unchanged data geometry and general transfer proofs are inherited dependencies.')
    (certificates / 'indexed-cycle-validation.json').write_text(json.dumps(validation, indent=2, sort_keys=True)+'\n')
    print('PASS exact recurrence, 47 strict inequalities, seven margins, eventual cutoffs', flush=True)
    return result


if __name__ == '__main__':
    verify()
