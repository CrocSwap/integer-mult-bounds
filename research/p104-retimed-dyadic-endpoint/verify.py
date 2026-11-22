#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate the e264 source and replay a single bounded refit case."""
from argparse import ArgumentParser
from hashlib import sha1,sha256
import json
from pathlib import Path, PurePosixPath
import subprocess
import shutil
import sys
import tarfile
from tempfile import TemporaryDirectory

HERE=Path(__file__).resolve().parent
HEAD='e26425171238e142cc9ffb510fd953f344bd41c7'
TREE='173859e6ffac6f43f1cd40357967e366d55f5a42'


def check(ok,message):
    if not ok:
        raise ValueError(message)


def git_oid(kind,data):
    return sha1(kind.encode()+b' '+str(len(data)).encode()+b'\0'+data).hexdigest()


def tree_id(rows):
    nodes={};entries=[]
    for name,oid in rows.items():
        node,sep,tail=name.partition('/')
        if sep:
            nodes.setdefault(node,{})[tail]=oid
        else:
            entries.append((node,'100644',oid))
    entries.extend((n,'40000',tree_id(v)) for n,v in nodes.items())
    entries.sort(key=lambda row:(row[0]+('/' if row[1]=='40000' else '')).encode())
    return git_oid('tree',b''.join(mode.encode()+b' '+name.encode()+b'\0'+bytes.fromhex(oid)
                                  for name,mode,oid in entries))


def checked_source(dest):
    spec=json.loads((HERE/'SOURCE-E264.json').read_bytes())
    check(spec['head']==HEAD and spec['source_tree']==TREE,'pinned e264 head and source tree')
    raw=(HERE/'source-e264.tar.gz').read_bytes()
    check(sha256(raw).hexdigest()==spec['source_archive_sha256'],'e264 archive checksum')
    records={x['path']:x for x in spec['files']}
    check(len(records)==len(spec['files'])==72,'complete distinct e264 metadata')
    seen={}
    with tarfile.open(HERE/'source-e264.tar.gz','r:gz') as archive:
        for item in archive:
            name=item.name;parts=PurePosixPath(name).parts
            check(parts and '/'.join(parts)==name and '\\' not in name and
                  all(x not in ('/', '.', '..') for x in parts) and name not in seen and
                  name in records and item.isfile() and not item.linkname,
                  'confined unique regular source file '+name)
            row=records[name]
            check(item.size==row['size'] and 0<=item.size<=4*1024*1024,'source size '+name)
            with archive.extractfile(item) as f:
                data=f.read()
            check(len(data)==item.size and sha256(data).hexdigest()==row['sha256'] and
                  git_oid('blob',data)==row['git_blob'],'literal e264 blob '+name)
            path=dest.joinpath(*parts);path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('xb') as out:out.write(data)
            seen[name]=row['git_blob']
    check(set(seen)==set(records),'complete e264 archive')
    pin=spec['large_blob'];data=(HERE/'predecessor-8030.tar.gz').read_bytes()
    check(pin['path']=='predecessor/predecessor-8030.tar.gz' and
          sha256(data).hexdigest()==pin['sha256'] and git_oid('blob',data)==pin['git_blob'],
          'complete predecessor archive')
    path=dest/pin['path'];path.parent.mkdir(exist_ok=True,parents=True)
    with path.open('xb') as out:out.write(data)
    seen[pin['path']]=pin['git_blob']
    check(tree_id(seen)==TREE,'exact complete e264 Git package tree')
    print('PASS_PINNED_E264_TREE',HEAD,TREE,len(seen),flush=True)


def run(*args):
    subprocess.run([sys.executable,'-I','-B',*(str(x) for x in args)],check=True)



def changed_source(source,dest):
    shutil.copytree(source,dest)
    spec=json.loads((HERE/'ENDPOINT-OVERLAY.json').read_bytes())
    check(spec['parent_head']==HEAD and spec['path']=='installations.py','overlay parent')
    path=dest/spec['path'];raw=path.read_bytes()
    check(sha256(raw).hexdigest()==spec['old_sha256'],'overlay original')
    text=raw.decode()
    for old,new in spec['edits']:
        check(text.count(old)==1,'unique overlay anchor')
        text=text.replace(old,new)
    data=(text+spec['append']).encode()
    check(sha256(data).hexdigest()==spec['new_sha256'],'overlay changed source')
    path.write_bytes(data)
    print('PASS_ENDPOINT_OVERLAY_C_AND_NAMED_PROFILE',flush=True)


def install(source,machine):
    subprocess.run([sys.executable,'-I','-B',str(source/'bootstrap.py'),str(machine)],check=True)
    helpers=('activation.py','check_complete.py','check_installation.py','ordinary_clock.py',
             'outer_clock.py','outer_budget.py','resolution.py','equal_rate.py','RESULT.json')
    for name in helpers:
        shutil.copyfile(source/name,machine/name)


def compare_json(actual,expected):
    check(json.loads(actual.read_bytes())==json.loads((HERE/expected).read_bytes()),
          'sealed receipt '+expected)


def main():
    cli=ArgumentParser(description=__doc__)
    cli.add_argument('case',choices=('baseline','price','install','schedule','physical','receiver','slabs','product'))
    args=cli.parse_args()
    check(sys.version_info[:2]==(3,12) and sys.implementation.name=='cpython' and __debug__,
          'CPython 3.12 with assertions required')
    with TemporaryDirectory(prefix='p104-e264-endpoint-') as work:
        root=Path(work);source=root/'source';source.mkdir();checked_source(source)
        if args.case=='baseline':
            run(source/'verify.py','cost')
        elif args.case=='price':
            # Source baseline and its fixed-c .460 control use the old c in a
            # separate interpreter before the 66-bit candidate is installed.
            run(source/'verify.py','cost')
            oldmachine=root/'oldmachine';install(source,oldmachine)
            control=root/'fixed-c.json'
            run(HERE/'fixed_c_control.py',oldmachine,source,control)
            compare_json(control,'FIXED-C-CONTROL.json')
            run(HERE/'old_c_negative.py',oldmachine)
            changed=root/'changed';changed_source(source,changed)
            machine=root/'machine';install(changed,machine)
            for script,expected in (('endpoint_price.py','ENDPOINT-PRICE.json'),
                                    ('endpoint_tariff.py','ENDPOINT-TARIFF.json'),
                                    ('endpoint_setup.py','ENDPOINT-SETUP.json'),
                                    ('uniform_ranges.py','UNIFORM-RANGES.json')):
                out=root/(script+'.json');run(HERE/script,machine,out);compare_json(out,expected)
            out=subprocess.check_output([sys.executable,'-I','-B',str(HERE/'global_crossing.py'),str(machine)])
            check(json.loads(out)==json.loads((HERE/'GLOBAL-CROSSING.json').read_bytes()),'global crossing receipt')
            print('PASS_GLOBAL_RAW_CROSSING',flush=True)
            run(HERE/'denominator_design.py')
            run(HERE/'dfd_checks.py',machine)
            run(HERE/'check_integrity.py')
        else:
            changed=root/'changed';changed_source(source,changed)
            if args.case in ('schedule','physical','receiver','slabs'):
                run(changed/'verify.py',args.case)
            else:
                machine=root/'machine';install(changed,machine)
                if args.case=='install':
                    out=root/'runtime.json'
                    run(HERE/'endpoint_monitored.py',source,machine,out)
                    compare_json(out,'ENDPOINT-RUNTIME.json')
                elif args.case=='product':
                    run(HERE/'endpoint_product.py',machine)
    print('PASS_E264_ENDPOINT',args.case,flush=True)


if __name__=='__main__':
    main()
