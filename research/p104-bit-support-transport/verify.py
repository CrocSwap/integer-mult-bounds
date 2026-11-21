#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate the source and verify the directed paid-support certificate."""
from hashlib import sha1,sha256
import json
from pathlib import Path,PurePosixPath
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


def main():
    meta=json.loads((HERE/'SOURCES.json').read_bytes())
    witness=HERE/'TRANSPORT.txt.gz'
    check(sha256(witness.read_bytes()).hexdigest()==meta['certificate_sha256'],'sealed transport bytes')
    with TemporaryDirectory(prefix='p104-bit-support-transport-') as work:
        source=Path(work)/'source'
        source.mkdir()
        restore(source)
        outcome=subprocess.run([sys.executable,'-IB',HERE/'support_flow.py',source,witness],
                               check=True,capture_output=True,text=True)
        rows=outcome.stdout.splitlines()
        receipt=json.loads(rows[-2])
        check(receipt['ordered'] and receipt['certificate_arcs']==114266 and
              receipt['target_count']==18906 and receipt['grouped_paid_count']==86730 and
              receipt['trial']=='3890115286594461129996943/1000000000000000000000000000',
              'exact source scope, rank order and certified endpoint')
        print(outcome.stdout,end='')


if __name__=='__main__':
    main()
