"""Recheck the seven audited numerical bodies inside the actual sparse archive.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from hashlib import sha1,sha256
from io import BytesIO
import json
import tarfile
from join_sources import HERE,ROOT,authenticate,need

def blob(raw):return sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def main():
    pins=authenticate()
    audit_raw=(HERE/'review/normalized-audit-sources.json').read_bytes()
    receipt=json.loads((HERE/'NORMALIZED-SOURCE-COMPATIBILITY.json').read_text())
    need(blob(audit_raw)==receipt['audit_manifest_git_blob'],'exact published #6895 audit manifest')
    audit=json.loads(audit_raw)
    raw=(ROOT/'research/physical-gaussian-core/inputs/word-export.tar').read_bytes()
    need(blob(raw)==receipt['archive_git_blob'] and sha256(raw).hexdigest()==receipt['archive_sha256']
         and len(raw)==receipt['archive_bytes'],'exact actual sparse scalar outer archive')
    with tarfile.open(fileobj=BytesIO(raw),mode='r:') as outer:
        nested=outer.extractfile('research/physical-fft-word/inputs/ring-export.tar').read()
    rows={r['path']:r for r in audit['files']}
    checked=[]
    with tarfile.open(fileobj=BytesIO(nested),mode='r:') as ring:
        for row in receipt['files']:
            expected=rows[row['path']]
            body=ring.extractfile(row['path']).read()
            need(blob(body)==row['git_blob']==expected['git_blob'] and
                 sha256(body).hexdigest()==row['sha256']==expected['sha256'] and
                 len(body)==row['bytes'],'same audited numerical body '+row['path'])
            checked.append(row['path'])
    need(len(checked)==len(set(checked))==7,'all seven audited numerical files')
    print(json.dumps(dict(status='PASS_ACTUAL_NORMALIZED_SOURCE_COMPATIBILITY',
        authenticated_inputs=len(pins),audit_commit=receipt['audit_commit'],
        audit_manifest_git_blob=receipt['audit_manifest_git_blob'],
        actual_archive_sha256=receipt['archive_sha256'],files=checked,
        scope='Exact numerical source identity; physical/native supplier premises retained.'),
        indent=2,sort_keys=True))

if __name__=='__main__':main()
