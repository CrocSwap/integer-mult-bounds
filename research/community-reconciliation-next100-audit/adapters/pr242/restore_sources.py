#!/usr/bin/env python3
"""Restore only omitted FILES.json-pinned bytes from retained original Git objects."""
import argparse, hashlib, json, subprocess
from pathlib import Path, PurePosixPath
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package',type=Path,required=True);p.add_argument('--repository',type=Path,required=True);a=p.parse_args();root=a.package.resolve()
for row in json.loads(Path(__file__).with_name('MISSING-SOURCES.json').read_text()):
 rel=PurePosixPath(row['path']);assert not rel.is_absolute() and '..'not in rel.parts
 dest=(root/rel).resolve();assert dest.is_relative_to(root)
 raw=subprocess.check_output(['git','-C',str(a.repository),'cat-file','blob',row['available']['blob']])
 assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
 if dest.exists():assert dest.read_bytes()==raw, 'Existing file differs: '+str(dest)
 else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
archive=root/'references/source527/source_inputs.rar'
if archive.exists():
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='a510f15cf54ec6c954b268d56fa662f603af7033668d432d7a7c0466c4e48cb1'
    dest=root.parent/(root.name+'-source_inputs-original.rar')
    assert not dest.exists(), 'Preserve any pre-existing archive destination'
    archive.rename(dest)
print('PASS 28 exact manifest-pinned missing files restored; convenience archive retained outside checked root')
