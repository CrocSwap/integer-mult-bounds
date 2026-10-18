"""Exact pinned fixed-plane model; no historical verifier is imported."""
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
PAYLOAD_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def authenticated_model(root=ROOT):
    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for record in sources['files']:
        if record['usage'] != 'input':
            continue
        data = (root / record['path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == record['sha256'],
                'source sha256: ' + record['path'])
        git_blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(git_blob == record['git_blob'], 'source git blob: ' + record['path'])
    with tarfile.open(root / 'research/community-frontier1094-audit/selected-replay.tar.gz', 'r:gz') as archive:
        stream = archive.extractfile(MEMBER)
        require(stream is not None, 'archive member missing')
        data = stream.read()
    require(hashlib.sha256(data).hexdigest() == PAYLOAD_SHA, 'selected payload sha256')
    recipes = sorted(json.loads(data)['recipes'], key=lambda row: row['port'])
    require([row['port'] for row in recipes] == list(range(112)), 'port order')
    labels = [row['q'] for row in recipes]
    require(len(set(labels)) == 112 and all(0 < q < 512 and dot(q, q) for q in labels), 'odd labels')
    certificate = json.loads((root / 'research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json').read_text(encoding='utf-8'))
    pairs = certificate['matching']
    require(len(pairs) == 56 and all(len(pair) == 2 for pair in pairs), '56 pairs')
    require(sorted(port for pair in pairs for port in pair) == list(range(112)), 'matching partition')
    planes = [[labels[port] for port in pair] for pair in pairs]
    require(all(dot(p[0], p[1]) == 0 for p in planes), 'nondegenerate matched planes')
    nonorthogonal = [[any(dot(x, y) for x in p for y in q) for q in planes] for p in planes]
    return labels, pairs, nonorthogonal


def dot(x, y):
    return (x & y).bit_count() & 1


def fitting(matrix, pairs, nonorthogonal):
    if len(matrix) != 112 or any(len(row) != 112 for row in matrix):
        return False
    owner = {port: plane for plane, pair in enumerate(pairs) for port in pair}
    return all(matrix[i][j] == int(i == j)
               for i in range(112) for j in range(112)
               if i == j or nonorthogonal[owner[i]][owner[j]])


def construct(classes, pairs):
    supports = [[pairs[plane][slot] for plane in group]
                for group in classes for slot in range(2)]
    matrix = [[0] * 112 for _ in range(112)]
    for support in supports:
        for i in support:
            for j in support:
                matrix[i][j] += 1
    return supports, matrix
