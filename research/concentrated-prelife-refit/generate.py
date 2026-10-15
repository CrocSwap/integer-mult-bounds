#!/usr/bin/env python3
"""Reconstruct the one-gate frame refit and its complete chained patch inputs.

Marius-Paul Dumitrean, with substantial OpenAI Codex assistance. Apache-2.0.
Frozen predecessor source packages and notices remain authoritative.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent/'concentrated-prelife-composition'
SOURCE = HERE.parent/'gmx-t74-borrow43-handoff'
OLD_GATE = ['add', 393, 515, 1, 1, [259, 132, 66, 36, 16, 9]]
NEW_FRAME = [259, 148, 66, 36, 9]
PROFILE = {'1':2368, '2':647, '3':297, '4':120, '5':26, '7':4, '8':4}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    data = json.dumps(value, separators=(',', ':')).encode()
    path.write_bytes(gzip.compress(data, mtime=0) if path.suffix == '.gz' else data+b'\n')


def authenticate():
    pins = read(HERE/'SOURCE-HEADS.json')
    need(sha(PARENT/'ARTIFACTS.json') == pins['published2733_artifacts_sha256'],
         'Frozen published PR2733 artifact manifest')
    for name, digest in read(PARENT/'ARTIFACTS.json').items():
        need(sha(PARENT/name) == digest, 'PR2733 source: '+name)
    for record in read(PARENT/'SOURCES.json')['files']:
        if record['usage'] == 'input':
            need(sha(HERE.parents[1]/record['path']) == record['sha256'],
                 'Frozen external source: '+record['path'])


def generate(work):
    need(__debug__, 'Assertions are required; run without optimized Python')
    authenticate()
    work = work.resolve()
    need(not work.exists() and not any(work.is_relative_to(p.resolve())
         for p in [HERE, PARENT, SOURCE]), 'Fresh output outside source packages required')
    shutil.copytree(PARENT/'expected', work)
    # A read-only source export must still produce writable private outputs.
    for path in [work, *work.rglob('*')]:
        path.chmod(path.stat().st_mode | 0o200)
    sys.path.insert(0, str(SOURCE/'new/borrow'))
    import alias_build
    widths = None
    for tag in ('base', 'extra'):
        word = read(PARENT/f'expected/words/{tag}.json.gz')
        need(word['B'][1149] == OLD_GATE, 'Exact changed gate '+tag)
        word['B'][1149][-1] = NEW_FRAME.copy()
        paid, inventory = alias_build.profile(word)
        need(paid == PROFILE, 'Complete changed local profile '+tag)
        if widths is None:
            widths = inventory
        need(inventory == widths, 'Both width inventories')
        word['report']['local_profile'] = paid
        write(work/f'words/{tag}.json.gz', word)
        refit = read(PARENT/f'expected/patches/refit563_43{tag}.json')
        need(refit['frames'] == [['B', 894, NEW_FRAME]], 'Original exact refit')
        refit['frames'].append(['B', 1149, NEW_FRAME.copy()])
        refit['local_profile']['1'] -= 2
        refit['local_profile']['2'] += 1
        write(work/f'patches/refit563_43{tag}.json', refit)
        alias = read(PARENT/f'expected/patches/alias1_43{tag}.json')
        need(alias['fields']['B'][1149] == OLD_GATE, 'Downstream alias input frame')
        alias['fields']['B'][1149][-1] = NEW_FRAME.copy()
        alias['report'] = copy.deepcopy(word['report'])
        write(work/f'patches/alias1_43{tag}.json', alias)
    providers = read(work/'PROVIDERS.json')
    for value in providers.values():
        value['actual_paid_profile'] = PROFILE.copy()
    write(work/'PROVIDERS.json', providers)
    profile = read(work/'PROFILE.json')
    profile['1'] -= 1332
    profile['2'] += 666
    need(sum(int(k)*v for k,v in profile.items()) == 4816512, 'Complete rank mass')
    write(work/'PROFILE.json', profile)
    manifest = {p.relative_to(work).as_posix():sha(p) for p in sorted(work.rglob('*'))
                if p.is_file() and p.name != 'MANIFEST.json'}
    write(work/'MANIFEST.json', manifest)
    authenticate()
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    generate(args.work)
    print('PASS_EXACT_ONE_GATE_REFIT_CONSTRUCTION')
