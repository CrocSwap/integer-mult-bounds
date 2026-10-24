#!/usr/bin/env python3
"""Verify source-capsule SHA256 and Git origin bindings without Git or scientific imports."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent

def require(condition, message):
    if not condition: raise ValueError(message)

def verify(number):
    root=HERE/number
    report=json.loads((root/'SOURCE-CUSTODY.json').read_text())
    inventory=json.loads((root/'PRE-EXECUTION-HASHES.json').read_text())
    for row in inventory['files']:
        path=root/row['path']
        data=path.read_bytes()
        require(not path.is_symlink(),'symlink')
        require(len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],'changed inventory file '+row['path'])
        require(path.stat().st_mode & 0o222 == 0,'source file writable')
    def object_bytes(oid,kind):
        row=report['raw_git_origin_objects'][oid]
        data=(root/row['path']).read_bytes()
        require(row['kind']==kind,'wrong object kind')
        require(hashlib.sha1(kind.encode()+b' '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid,'wrong Git identity')
        return data
    def tree_entries(data):
        entries={}
        while data:
            split=data.index(b'\0')
            mode,name=data[:split].split(b' ',1)
            oid=data[split+1:split+21].hex()
            entries[name.decode()]=(mode.decode(),oid)
            data=data[split+21:]
        return entries
    def origin(binding,data):
        commit=object_bytes(binding['commit'],'commit')
        tree=commit.splitlines()[0].split()[1].decode()
        parts=Path(binding['path']).parts
        for part in parts:
            mode,oid=tree_entries(object_bytes(tree,'tree'))[part]
            tree=oid
        require(oid==binding['git_blob'] and mode==binding['git_mode'],'tree path binding')
        require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid,'blob bytes binding')
    for row in report['runtime_files']:
        data=(root/'source-capsule'/row['path']).read_bytes()
        require(hashlib.sha256(data).hexdigest()==row['sha256'],'runtime SHA')
        origin(row['origin'],data)
    for row in report['source_rows']:
        data=(root/row['stored_source']).read_bytes()
        origin(row['origin'],data)
        require(hashlib.sha256(data).hexdigest()==row['declared']['sha256'],'SOURCES SHA')
        require(row['origin']['git_blob']==row['declared']['git_blob'],'SOURCES blob')
        if row['declared'].get('retained_copy'):
            retained=root/'source-capsule'/report['package']/row['declared']['retained_copy']
            require(retained.read_bytes()==data,'retained source copy')
    result={'status':'PASS_OFFLINE_SOURCE_CUSTODY','source_pr':int(number),'head':report['head'],
            'inventory_files_checked':len(inventory['files']),'runtime_files_bound':len(report['runtime_files']),
            'source_rows_bound':len(report['source_rows']),'all_source_bytes_unchanged':True,
            'raw_commit_tree_blob_chain_verified':True,'git_invocations':0,'scientific_executions':0}
    (root/'OFFLINE-CUSTODY-VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':
    for number in ['5402','5376']:
        verify(number)
