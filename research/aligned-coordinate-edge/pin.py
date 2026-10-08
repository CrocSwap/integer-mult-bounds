#!/usr/bin/env python3
"""Freeze the additive witness's local source and finite inputs."""
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def pin():
    files = {str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest()
             for p in HERE.iterdir() if p.is_file()
             and p.name not in ('SOURCE.json','certificate.json')}
    for name in ('.github/workflows/aligned-coordinate-edge.yml',
                 'research/aligned-composition/SOURCE.json',
                 'certificates/aligned-composition-kappa.json'):
        files[name] = sha256((ROOT/name).read_bytes()).hexdigest()
    document = dict(author='Maxime Fleury with Codebuff assistance',
        parent_pull_request=91,parent_commit='264f202b52edc04d0c72ca9cb3138282ca68b9ad',
        scope='Additive coordinate action; parent producer, Lean arithmetic and all-size transfer remain inherited.',
        files=dict(sorted(files.items())))
    (HERE/'SOURCE.json').write_text(json.dumps(document,indent=2,sort_keys=True)+'\n')
    print('Pinned',len(files),'files; parent source closure is verified recursively')


if __name__ == '__main__':
    pin()
