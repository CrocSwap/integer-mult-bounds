#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate exact PR2843 auditor sources and replay every P53 adapter edit."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)

def sha(data):return hashlib.sha256(data).hexdigest()

def replay(record,original):
    need(sha(original)==record['source_sha256'],'source hash')
    lines=original.decode().splitlines(keepends=True)
    previous=0;result=[]
    for patch in record['patches']:
        i,j=patch['start_line_zero_based'],patch['end_line_exclusive']
        need(type(i)is int and type(j)is int and previous<=i<=j<=len(lines),'ordered disjoint patch bounds')
        need(''.join(lines[i:j])==patch['preimage'],'exact patch preimage')
        result.extend(lines[previous:i]);result.append(patch['postimage']);previous=j
    result.extend(lines[previous:]);output=''.join(result).encode()
    need(sha(output)==record['target_sha256'],'target hash')
    return output

def check():
    manifest=json.loads((HERE/'AUDITOR-DERIVATION.json').read_text())
    need(len(manifest['files'])==3,'three distinct auditors')
    targets=[]
    for row in manifest['files']:
        data=(HERE/row['source_file']).read_bytes()
        need(replay(row,data)==(HERE/row['target']).read_bytes(),'exact committed auditor bytes')
        targets.append(row['target'])
    need(len(set(targets))==3,'unique auditor targets')
    row=manifest['files'][0];data=(HERE/row['source_file']).read_bytes();controls=[]
    def reject(name,record,source):
        try:replay(record,source)
        except ValueError as e:controls.append({'name':name,'reason':str(e)})
        else:raise ValueError('accepted corrupted adapter '+name)
    reject('changed_source',row,data+b'\n')
    bad=json.loads(json.dumps(row));bad['patches'][0]['preimage']+='x';reject('changed_preimage',bad,data)
    bad=json.loads(json.dumps(row));bad['patches'][0]['postimage']+='x';reject('changed_postimage',bad,data)
    bad=json.loads(json.dumps(row));bad['patches'].pop();reject('omitted_patch',bad,data)
    bad=json.loads(json.dumps(row));bad['patches'].append(bad['patches'][0]);reject('duplicate_patch',bad,data)
    return {'status':'PASS_EXACT_SOURCE_AUDITOR_DERIVATION','targets':targets,'controls':controls}

if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
