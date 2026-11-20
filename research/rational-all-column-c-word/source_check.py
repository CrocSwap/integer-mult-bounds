"""Authenticate the exact attributed reference bytes; no source imports."""
from pathlib import Path
from hashlib import sha1,sha256
import json

HERE=Path(__file__).resolve().parent


def hashes(data):
    return sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),sha256(data).hexdigest()


def main():
    source=json.loads((HERE/'SOURCES.json').read_text())
    checked=0
    for row in source['files']:
        if 'local_input' not in row:
            continue
        data=(HERE.parents[1]/row['local_input']).read_bytes()
        expected=row['git_blob'],row['sha256']
        if hashes(data)!=expected:
            raise RuntimeError('source byte mismatch: '+row['local_input'])
        if hashes(data+b' ') == expected:
            raise RuntimeError('source mutation control failed')
        checked+=1
    if checked!=4:
        raise RuntimeError('incomplete source closure')
    print(json.dumps({'status':'PASS_RATIONAL_SOURCE_PINS','authenticated_inputs':checked,
                      'byte_mutation_rejected':True},sort_keys=True))


if __name__=='__main__':
    main()
