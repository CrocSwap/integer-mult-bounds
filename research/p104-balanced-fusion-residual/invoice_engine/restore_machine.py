#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Restore the byte-pinned #8030 tree and exact #8035 numerical overlay.

Adapted from the p104-six-stage-resolution replay; only the two used stages are retained.
"""
from argparse import ArgumentParser
from hashlib import sha1,sha256
import json
from pathlib import Path,PurePosixPath
import shutil
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
PARENT = '6285dd829114705862e8d91facaedc1f31d3cfcb'
TREE = '3a1c001cbf175ae48ee1d56e56e4723eda1c8218'


def check(ok,message):
    if not ok:
        raise ValueError(message)


def git_oid(kind,raw):
    return sha1(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def tree_id(files):
    nodes={}; entries=[]
    for name,(mode,oid) in files.items():
        node,sep,rest=name.partition('/')
        if sep:
            nodes.setdefault(node,{})[rest]=(mode,oid)
        else:
            entries.append((node,mode,oid))
    entries.extend((name,'40000',tree_id(rows)) for name,rows in nodes.items())
    entries.sort(key=lambda row:(row[0]+('/' if row[1]=='40000' else '')).encode())
    return git_oid('tree',b''.join(mode.encode()+b' '+name.encode()+b'\0'+bytes.fromhex(oid)
                                  for name,mode,oid in entries))


def verify_ancestor_files():
    # Byte-bound to #8035 ea77647 and #8041 05f6172 respectively.
    pins = {
        'PREDECESSOR-SOURCES.json': '3634f7a15b8ca6f1832e48bdd4e83bd764509f804196d956149a9a82e7512a64',
        'OVERLAY.json': '73aaf56a8a199cf3b7fc6c87316ca50298f47561e4b7c227edec6230f12a8403',
        'RESULT.json': 'e1ccc49a75e17fab4f5aa03697db58a0a6c3ad335cd7b8bba156c9bc3d419179',
        'check_profile.py': '83561f0c2da467b9b657380e043b069de1e2f139d5231cccd0abcce665bd6352',
        'outer_budget.py': 'ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02',
        'verify_funding.py': 'b9596574f4ded80c2bee2d44fef4d1d4aff859f53eadacb089130f34bed6779e',
    }
    for name, digest in pins.items():
        check(sha256((HERE/name).read_bytes()).hexdigest()==digest, 'ancestor file '+name)


def restore(path):
    verify_ancestor_files()
    spec=json.loads((HERE/'PREDECESSOR-SOURCES.json').read_bytes())['offline_predecessor']
    check(spec['head']==PARENT and spec['tree']==TREE,'exact public predecessor head and package tree')
    archive=HERE/spec['archive']
    check(sha256(archive.read_bytes()).hexdigest()==spec['archive_sha256'],'portable archive')
    rows={}
    with tarfile.open(archive) as tar:
        for item in tar:
            name=item.name
            parts=PurePosixPath(name).parts
            check(parts and '/'.join(parts)==name and '\\' not in name and
                  all(x not in ('/', '.', '..') for x in parts) and name not in rows,'unique confined package path')
            expected=spec['files'].get(name)
            check(expected and item.isfile() and not item.linkname and
                  0<=item.size==expected['size']<=4*1024*1024,'registered regular source')
            with tar.extractfile(item) as content:
                data=content.read()
            check(len(data)==item.size and git_oid('blob',data)==expected['git_blob'] and
                  sha256(data).hexdigest()==expected['sha256'] and expected['mode'] in ('100644','100755'),f'literal provenance {name}')
            dest=path.joinpath(*parts);dest.parent.mkdir(exist_ok=True,parents=True)
            with dest.open('xb') as out:out.write(data)
            rows[name]=(expected['mode'],expected['git_blob'])
    check(len(rows)==91 and set(rows)==set(spec['files']) and tree_id(rows)==TREE,'complete exact #8030 Git package')


def apply_overlay(path):
    overlay=json.loads((HERE/'OVERLAY.json').read_bytes())
    expected={'band_product.py', 'calibration.py', 'check_product.py', 'strict_moment.py', 'strong_binary.py'}
    check(set(overlay)==expected,'exact list of changed modules')
    for name,info in overlay.items():
        source=path/name
        check(sha256(source.read_bytes()).hexdigest()==info['old_sha256'],'old code '+name)
        text=source.read_text()
        for before,after in info['edits']:
            check(text.count(before)==1,'unique patch anchor '+name)
            text=text.replace(before,after)
        data=text.encode()
        check(sha256(data).hexdigest()==info['new_sha256'],'new code '+name)
        source.write_bytes(data)
    # Rebuild the profile table via the actual code. Every predecessor row is retained.
    generated=subprocess.check_output([sys.executable,'-IB',path/'verify.py','resources'],cwd=path)
    previous=json.loads((path/'REQUIREMENTS.json').read_bytes());new=json.loads(generated)
    check({name:row for name,row in new.items() if name not in {'split-tariff','fixed-stock-stop','small-gap'}}==previous,'unchanged prior installations')
    (path/'REQUIREMENTS.json').write_bytes(generated)
    for name in ('check_profile.py','outer_budget.py'):
        shutil.copyfile(HERE/name,path/name)
