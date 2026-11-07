#!/usr/bin/env python3
"""Passive source-archive integrity check. Never extracts or imports a candidate."""
from pathlib import Path, PurePosixPath
import hashlib
import io
import json
import tarfile

ROOT=Path(__file__).resolve().parent
MAX_ARCHIVE=32*1024*1024
MAX_TOTAL=96*1024*1024
MAX_MEMBER=32*1024*1024
MAX_MEMBERS=2048


def need(ok,why):
    if ok is not True:raise ValueError(why)


def digest(path,cap):
    before=path.stat();need(path.is_file() and not path.is_symlink() and before.st_size<=cap,'ordinary bounded file')
    h=hashlib.sha256();count=0
    with path.open('rb') as stream:
        while True:
            block=stream.read(65536)
            if not block:break
            count+=len(block);need(count<=cap,'file cap');h.update(block)
    after=path.stat()
    need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==
         (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),'stable file')
    return count,h.hexdigest()


def main():
    spec=json.loads((ROOT/'SOURCE-MAP.json').read_text())
    need(spec['schema']=='h25-caller-inert-source-archive-v1','archive schema')
    pieces=[]
    need(0<len(spec['archive']['parts'])<=64,'bounded ordered archive parts')
    for index,part in enumerate(spec['archive']['parts']):
        need(part['path']=='source-snapshot.tar.gz.part'+format(index,'03d'),'exact ordered part path')
        path=ROOT/part['path']
        need(digest(path,524288)==(part['bytes'],part['sha256']),'exact compressed part bytes')
        pieces.append(path.read_bytes())
    compressed=b''.join(pieces)
    need(len(compressed)==spec['archive']['bytes']<=MAX_ARCHIVE and
         hashlib.sha256(compressed).hexdigest()==spec['archive']['sha256'],'exact concatenated compressed bytes')
    expected={row['member']:row for row in spec['members']}
    need(len(expected)==len(spec['members'])<=MAX_MEMBERS,'unique bounded source map')
    origins={row['source_path']:row for row in spec['files']}
    need(len(origins)==len(spec['files'])==spec['source_file_count']<=MAX_MEMBERS,
         'unique bounded original path map')
    path_total=0
    for row in origins.values():
        need(type(row['source_path']) is str and len(row['source_path'])<=4096,
             'bounded source provenance path')
        obj=expected[row['member']]
        need(all(row[key]==obj[key] for key in ('bytes','sha256','source_mode')),
             'each original file maps to its exact source object')
        path_total+=row['bytes']
    need(path_total==spec['uncompressed_path_bytes']<=MAX_TOTAL,'complete original path byte sum')
    seen=set();total=0
    with tarfile.open(fileobj=io.BytesIO(compressed),mode='r|gz') as tar:
        for member in tar:
            path=PurePosixPath(member.name)
            need(member.name in expected and member.name not in seen and not path.is_absolute() and
                 '..' not in path.parts and member.isfile() and not member.issym() and not member.islnk(),
                 'only exact mapped ordinary members')
            row=expected[member.name]
            need(member.size==row['bytes']<=MAX_MEMBER and member.mode==row['source_mode'],'exact source extent/mode')
            stream=tar.extractfile(member);need(stream is not None,'ordinary archive body')
            h=hashlib.sha256();count=0
            while True:
                block=stream.read(65536)
                if not block:break
                count+=len(block);total+=len(block)
                need(count<=member.size and total<=MAX_TOTAL,'decoded-source cap');h.update(block)
            need(count==row['bytes'] and h.hexdigest()==row['sha256'],'complete member bytes')
            seen.add(member.name)
    need(seen==set(expected),'complete archive census')
    need(total==spec['unique_decoded_bytes'],'complete unique object byte sum')
    for row in spec['readable_files']:
        p=PurePosixPath(row['path'])
        need(not p.is_absolute() and '..' not in p.parts,'relative readable snapshot')
        source=origins[row['source_path']]
        need(all(row[key]==source[key] for key in ('bytes','sha256','source_mode')),
             'readable snapshot joins its exact archived source')
        need(digest(ROOT/row['path'],MAX_MEMBER)==(row['bytes'],row['sha256']),'readable snapshot matches exact source')
    print(json.dumps({'archive_integrity':'PASS','members':len(seen),'decoded_source_bytes':total,
          'readable_files':len(spec['readable_files']),'candidate_imports':False,
          'native_or_scientific_execution':False,'current_runtime_qualification':False},sort_keys=True))


if __name__=='__main__':main()
