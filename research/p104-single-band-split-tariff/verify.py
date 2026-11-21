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


def restore(path):
    spec=json.loads((HERE/'SOURCES.json').read_bytes())['offline_predecessor']
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
    expected={'calibration.py', 'check_product.py', 'strict_moment.py', 'strong_binary.py'}
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
    check({name:row for name,row in new.items() if name!='split-tariff'}==previous,'unchanged prior installations')
    (path/'REQUIREMENTS.json').write_bytes(generated)
    shutil.copyfile(HERE/'check_profile.py',path/'check_profile.py')


def run(path,name,*args):
    subprocess.run([sys.executable,'-IB',path/name,*args],cwd=path,check=True)


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('case',choices=('price','band','dense','binary','grid','atlas','physical','product'))
    a=p.parse_args()
    check(sys.version_info[:2]==(3,12) and sys.implementation.name=='cpython' and __debug__,'CPython 3.12 with assertions')
    with TemporaryDirectory(prefix='single-band-split-tariff-') as work:
        root=Path(work);path=root/'package';path.mkdir()
        restore(path);apply_overlay(path)
        if a.case=='price':
            out=root/'result.json'
            run(path,'check_profile.py',out)
            check(out.read_bytes()==(HERE/'RESULT.json').read_bytes(),'sealed candidate receipt')
        if a.case=='product':
            # Exercise the actual public entry, a feasible post-admission body and a signed
            # Fourier product with physical rank-two CRT shuttles under the new profile.
            driver=path/'candidate_product.py'
            driver.write_text('import sys,json\nfrom pathlib import Path\nsys.path.insert(0,str(Path(__file__).resolve().parent))\nfrom calibration import SPLIT_TARIFF\nfrom check_product import physical_product\nr=physical_product(SPLIT_TARIFF)\nassert r["product"]=="-345550037539" and r["shuttles"]==138\nprint(json.dumps(r,sort_keys=True))\n')
            run(path,driver.name)
        else:
            run(path,'verify.py',a.case)
        print('PASS_SINGLE_BAND_SPLIT_TARIFF',a.case,flush=True)


if __name__=='__main__':
    main()
