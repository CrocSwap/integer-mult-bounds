#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify the portable #8030 tree, apply the reviewed extension, and replay one check."""
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


def apply_candidate(path):
    overlay=json.loads((HERE/'CANDIDATE-OVERLAY.json').read_bytes())
    check(set(overlay)=={'calibration.py','strict_moment.py','strong_binary.py'},'candidate module set')
    for name,info in overlay.items():
        dest=path/name
        check(sha256(dest.read_bytes()).hexdigest()==info['old_sha256'],'candidate parent '+name)
        data=info['new_text'].encode()
        check(sha256(data).hexdigest()==info['new_sha256'],'candidate source '+name)
        dest.write_bytes(data)
    previous=json.loads((path/'REQUIREMENTS.json').read_bytes())
    generated=subprocess.check_output([sys.executable,'-IB',path/'verify.py','resources'],cwd=path)
    profiles=json.loads(generated)
    check({k:v for k,v in profiles.items() if k!='near-raw'}==previous,'all inherited profiles unchanged')
    (path/'REQUIREMENTS.json').write_bytes(generated)
    shutil.copyfile(HERE/'check_candidate.py',path/'check_candidate.py')


def apply_last_tick(path):
    overlay=json.loads((HERE/'LAST-TICK-OVERLAY.json').read_bytes())
    check(set(overlay)=={'calibration.py','strict_moment.py','strong_binary.py','check_product.py'},
          'last-tick module set')
    previous=json.loads((path/'REQUIREMENTS.json').read_bytes())
    for name,info in overlay.items():
        dest=path/name
        check(sha256(dest.read_bytes()).hexdigest()==info['old_sha256'],'last-tick parent '+name)
        data=info['new_text'].encode()
        check(sha256(data).hexdigest()==info['new_sha256'],'last-tick source '+name)
        dest.write_bytes(data)
    generated=subprocess.check_output([sys.executable,'-IB',path/'verify.py','resources'],cwd=path)
    profiles=json.loads(generated)
    check({k:v for k,v in profiles.items() if k!='last-tick'}==previous,
          'all inherited profiles unchanged by last-tick overlay')
    (path/'REQUIREMENTS.json').write_bytes(generated)
    for name in ('check_last_tick.py','check_last_product.py','check_product_profiles.py'):
        shutil.copyfile(HERE/name,path/name)


def run(path,name,*args):
    subprocess.run([sys.executable,'-IB',path/name,*args],cwd=path,check=True)


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('case',choices=('price','band','dense','binary','grid','atlas','physical','product'))
    a=p.parse_args()
    check(sys.version_info[:2]==(3,12) and sys.implementation.name=='cpython' and __debug__,'CPython 3.12 with assertions')
    with TemporaryDirectory(prefix='single-band-signed-margin-') as work:
        root=Path(work);path=root/'package';path.mkdir()
        restore(path);apply_overlay(path);apply_candidate(path);apply_last_tick(path)
        if a.case=='price':
            out=root/'result.json'
            run(path,'check_profile.py',out)
            check(out.read_bytes()==(HERE/'RESULT.json').read_bytes(),'sealed inherited receipt')
            out2=root/'candidate.json'
            run(path,'check_candidate.py',out2)
            check(out2.read_bytes()==(HERE/'CANDIDATE.json').read_bytes(),'sealed near-raw receipt')
            last=root/'last-tick.json'
            run(path,'check_last_tick.py',last)
            observed=json.loads(last.read_bytes())
            expected=json.loads((HERE/'LAST-TICK-RECEIPT.json').read_bytes())
            # sys.maxsize is evidence about the replay host, not a mathematical constant.
            check(type(observed.pop('host_py_ssize_max')) is int and
                  type(expected.pop('host_py_ssize_max')) is int and observed==expected,
                  'sealed last-tick receipt, excluding host word-size field')
            scaling=subprocess.check_output([sys.executable,'-IB',HERE/'check_scaling.py',path],cwd=path)
            check(scaling==(HERE/'SCALING.json').read_bytes(),'sealed exact scaling receipt')
            print('PASS_SCALING_AND_SIX_STAGE_CEILING',flush=True)
            bridge=subprocess.check_output([sys.executable,'-IB',HERE/'check_bridge.py',path],cwd=path)
            marker=b'PASS_TAPE_BRIDGE_SMALL_CONTROLS_AND_EXACT_GUARDS\n'
            check(bridge.endswith(marker) and json.loads(bridge[:-len(marker)])==
                  json.loads((HERE/'BRIDGE.json').read_bytes()),'sealed tape-bridge receipt')
            print('PASS_TAPE_BRIDGE_SMALL_CONTROLS_AND_EXACT_GUARDS',flush=True)
            subprocess.run([sys.executable,'-IB',HERE/'check_dispatch.py',path],cwd=path,check=True)
        if a.case=='product':
            run(path,'check_product_profiles.py')
        else:
            run(path,'verify.py',a.case)
        print('PASS_SIX_STAGE_RESOLUTION',a.case,flush=True)


if __name__=='__main__':
    main()
