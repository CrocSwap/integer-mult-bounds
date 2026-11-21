#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay two independent prices and the signed application of their ordinary cap."""
from hashlib import sha1, sha256
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
import json
import subprocess
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BRIDGE = 'research/p104-shared-native-helper-splits/retained/compiler/bit-audit/retained/DELAYED-COVER-BRIDGE.md'
PEER_ARCHIVE = '8d376948e23de166f8f015cfc7d5ba28d0ce6732ae865ff129905c2a29fa3fa0'
PEER_TREE = 'b14720ac48ff13a93d0dd094cfddeba285c5aa74'
EXPECTED = {
    'primary/PRICE.json': '228b7c47572c9b1c7568db2f59248af454296a1e3ad094da585073bbd594f5cb',
    'independent/PRICE.json': '5c723ea9c6b085b6e0aa792f34cfa64daed551a9bf2f629efc54d219008596d2',
    'independent/ACCEPT.json': 'babc9a23a60da353403b4d6f0a3a346c0523a42645618890a592929747fb019a',
    'application/RESULT.json': '419d4bdfb95c4484d0ddc81f34c89ee45bdefc0955a85dd496c1043396260e37',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_map(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key '+key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique_map)


def authenticate(path, digest):
    require(sha256(path.read_bytes()).hexdigest() == digest, 'SHA-256 mismatch for '+path.name)


def unpack(destination):
    source = read_json(HERE/'SOURCES.json')['offline_peer']
    require(source['archive_sha256'] == PEER_ARCHIVE and source['tree'] == PEER_TREE,
            'incorrect peer source')
    archive = HERE/'peer-8027.tar.gz'
    authenticate(archive, PEER_ARCHIVE)
    expected = source['files']
    require(len(expected) == 30, 'expected 30 peer source files')
    destination.mkdir()
    seen = set()
    objects = []
    with tarfile.open(archive, 'r:gz') as members:
        for member in members:
            name = member.name
            require(name in expected and name not in seen, 'unknown or duplicated peer archive path')
            require(name not in ('.','..') and PurePosixPath(name).parts == (name,)
                    and '/' not in name and '\\' not in name, 'invalid peer archive path')
            spec = expected[name]
            require(member.isreg() and member.type in (tarfile.REGTYPE, tarfile.AREGTYPE)
                    and not member.linkname and member.size == spec['size']
                    and 0 <= member.size <= 4*1024*1024, 'invalid peer member')
            file = members.extractfile(member)
            require(file is not None, 'missing peer data')
            with file:
                data = file.read()
            require(len(data) == member.size and sha256(data).hexdigest() == spec['sha256'],
                    'corrupt peer member '+name)
            blob = sha1(b'blob '+str(len(data)).encode()+b'\0'+data).digest()
            require(blob.hex() == spec['git_blob'] and spec['git_mode'] in ('100644','100755'),
                    'Git object mismatch '+name)
            # Write only individually authenticated single-level regular files into a fresh directory.
            with (destination/name).open('xb') as output:
                output.write(data)
            objects.append((name, spec['git_mode'], blob))
            seen.add(name)
    require(seen == set(expected), 'missing peer source')
    tree = b''.join(mode.encode()+b' '+name.encode()+b'\0'+blob for name,mode,blob in sorted(objects))
    require(sha1(b'tree '+str(len(tree)).encode()+b'\0'+tree).hexdigest() == PEER_TREE,
            'peer tree hash mismatch')


def run(script, *arguments):
    subprocess.run([sys.executable, '-I', '-B', str(HERE/script), *map(str,arguments)], check=True)


def prices(peer, work, bridge):
    first, second = work/'primary.json', work/'independent.json'
    run('primary/price.py', '--peer-package', peer, '--bridge', bridge, '--out', first)
    run('independent/price.py', '--peer', peer, '--bridge', bridge, '--out', second)
    # Only the primary discovery runner records wall-clock events.
    fixed = read_json(HERE/'primary/PRICE.json')
    rebuilt = read_json(first)
    for event_key in ('events','supervisor'):
        del rebuilt[event_key]
        del fixed[event_key]
    require(rebuilt == fixed and rebuilt['decision'] == 'ADVANCE_ONE_COMPLETE_SIGNED_REPLAY',
            'fresh primary scientific price differs')
    authenticate(second, EXPECTED['independent/PRICE.json'])


def main():
    require(sys.implementation.name == 'cpython' and sys.version_info[:2] == (3,12) and __debug__,
            'requires CPython 3.12 with assertions')
    for name,digest in EXPECTED.items():
        authenticate(HERE/name,digest)
    with TemporaryDirectory(prefix='paired-cover-') as name:
        work = Path(name)
        peer = work/'peer'
        unpack(peer)
        prices(peer, work, ROOT/BRIDGE)
        cold = work/'signed'
        run('application/replay.py', '--peer-package', peer, '--primary', HERE/'primary/PRICE.json',
            '--independent', HERE/'independent/PRICE.json', '--out', cold)
        authenticate(cold/'REPLAY.json', EXPECTED['application/RESULT.json'])
        result = read_json(HERE/'application/RESULT.json')
        require(set(result['output_sha256']) == {'BINARY.json','PHYSICAL.json','APPLICATION.json'},
                'signed evidence inventory')
        for filename,digest in result['output_sha256'].items():
            authenticate(cold/filename,digest)
        accept = work/'accepted.json'
        run('independent/accept.py', '--peer', peer, '--run', cold, '--adapter', HERE/'application/replay.py',
            '--primary', HERE/'primary/PRICE.json', '--independent', HERE/'independent/PRICE.json', '--out', accept)
        authenticate(accept, EXPECTED['independent/ACCEPT.json'])
        print('PASS_PAIRED_DELAYED_COVER', result['claim'], result['difference'])


if __name__ == '__main__':
    main()
