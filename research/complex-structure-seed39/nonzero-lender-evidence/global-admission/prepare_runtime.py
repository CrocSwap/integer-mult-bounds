#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Prepare FOUR428 from immutable compiler/geometry sources and bound native outputs.

This is preparation, not admission. In particular it does not synthesize a
successful PR2269 RESULT from the earlier failed aggregate replay. The new
candidate runs its own global, independent, finite and outer checks.
"""
import argparse
import gzip
import hashlib
import json
import shutil
import sys
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent
PARENT = CANDIDATE.parent / 'anticipatory-stage-evidence/parent'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    require(__debug__, 'retained assertions must be enabled')
    out = a.out.resolve()
    require(not out.exists() and not out.is_relative_to(PARENT), 'fresh output required')
    require(sha(PARENT/'MANIFEST.json') == '84996cc11a6b6946e8f5b1d65050fe8842ae02d8b4d4e0f6c8915d14d20b59ef', 'parent manifest')
    manifest = read(PARENT/'MANIFEST.json')
    actual = {p.relative_to(PARENT).as_posix() for p in PARENT.rglob('*') if p.is_file() and p != PARENT/'MANIFEST.json'}
    require(actual == set(manifest), 'immutable compiler source file set')
    for name, value in manifest.items():
        require(sha(PARENT/name) == value, 'immutable input: '+name)
    native = read(CANDIDATE/'NATIVE-RESULT.json')
    require(native['status'] == 'PASS_FINITE_NATIVE_BOTH_FOUR_ALIAS_WORDS_NO_GLOBAL_ADMISSION', 'native status')
    for name, value in native['outputs_sha256'].items():
        require(sha(CANDIDATE/'native-evidence'/name) == value, 'native output: '+name)
    for tag in ('base', 'extra'):
        require(gzip.decompress((CANDIDATE/'words'/('FOUR-'+tag+'.json.gz')).read_bytes()) ==
                gzip.decompress((CANDIDATE/'native-evidence'/tag/'FULL-WORD.json.gz').read_bytes()), 'actual native source word')
    files = ('PLAN.json', 'SPEC.json', 'PROFILE.json', 'OWNERS.json.gz', 'DISPATCH.json', 'CONSTRUCTION.json', 'GLOBAL-TEMPLATE.json.gz')
    require(all((HERE/'owners'/f).is_file() for f in files), 'complete candidate data')
    overlay = HERE/'runtime-overlay'
    require((overlay/'code/emit_allcold.py').is_file() and (overlay/'independent_core.py').is_file(), 'complete runtime overlay')
    layout = out/'layout'
    layout.mkdir(parents=True)
    archive = PARENT/'vendor/pr1297/upstream-layout.tar.gz'
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            require(member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts, 'archive member')
        tar.extractall(layout, filter='data')
    runtime = layout/'packing428'
    runtime.mkdir()
    for f in ('replay.py', 'freeze_spec.py', 'audit_mixed.py', 'independent_core.py', 'geometry_controls.py', 'audit_fast.py'):
        shutil.copy2(PARENT/f, runtime/f)
    for folder in ('code', 'construction'):
        shutil.copytree(PARENT/folder, runtime/folder)
    (runtime/'inputs').mkdir()
    shutil.copy2(PARENT/'inputs/PR589-EXPECTED.json', runtime/'inputs/PR589-EXPECTED.json')
    for path in overlay.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            target = runtime/path.relative_to(overlay)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    data = runtime/'candidate'
    data.mkdir()
    for f in files:
        shutil.copy2(HERE/'owners'/f, data/f)
    shutil.copy2(HERE/'GLOBAL-BUFFER-BINDING.json.gz', data/'GLOBAL-BUFFER-BINDING.json.gz')
    for tag in ('base', 'extra'):
        (runtime/('native-'+tag)).mkdir()
        shutil.copytree(CANDIDATE/'native-evidence'/tag, runtime/('native-'+tag)/'local')
    receipt = {
        'status': 'PREPARED_FOUR428_RUNTIME_NOT_ADMISSION',
        'parent_manifest_sha256': sha(PARENT/'MANIFEST.json'),
        'layout_archive_sha256': sha(archive),
        'native_result_sha256': sha(CANDIDATE/'NATIVE-RESULT.json'),
        'source_inputs': {str(p.relative_to(HERE)): sha(p) for folder in ('runtime-overlay', 'owners') for p in (HERE/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts},
        'runtime_files': {str(p.relative_to(runtime)): sha(p) for p in runtime.rglob('*') if p.is_file()},
        'commands': {mode: [sys.executable, '-B', str(runtime/'replay.py'), '--data', str(data), '--work', str(out/mode), '--local', str(runtime/'native-base/local')] + (['--discover'] if mode == 'discovery' else []) for mode in ('discovery', 'strict')},
        'scope': 'Extracts exact pinned geometry/compiler sources and copies verified native inputs. No PR2269 aggregate admission is assumed or fabricated. New candidate must pass its own strict program, ownership, finite overhead and outer checks.'
    }
    (out/'PREPARATION.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(receipt['status'])
    print(json.dumps(receipt['commands'], indent=2))


if __name__ == '__main__':
    main()
