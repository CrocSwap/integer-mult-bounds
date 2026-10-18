"""Fixed paired-plane block fitting; no physical COPY cost is modeled."""
from pathlib import Path
import hashlib
import io
import json
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
MATCHING = 'research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sources():
    raw = {}
    for manifest, root in [('SOURCES.json', ROOT), ('VENDOR.json', HERE)]:
        for row in json.loads((HERE / manifest).read_text())['files']:
            if row.get('usage', 'input') != 'input':
                continue
            data = (root / row['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256 ' + row['path'])
            blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            need(blob == row['git_blob'], 'source Git blob ' + row['path'])
            raw[row['path']] = data
    matching = json.loads(raw[MATCHING])
    with tarfile.open(fileobj=io.BytesIO(raw[ARCHIVE]), mode='r:gz') as archive:
        members = [m for m in archive.getmembers() if m.name == MEMBER]
        need(len(members) == 1 and members[0].isfile(), 'unique selected member')
        payload = archive.extractfile(members[0]).read()
    need(hashlib.sha256(payload).hexdigest() == matching['selected_payload_sha256'], 'selected payload binding')
    data = json.loads(payload)
    certificate = json.loads(raw['predecessor/PR2484-CERTIFICATE.json'])
    return data, matching, certificate


def geometry(data, matching):
    labels = [r['q'] for r in data['recipes']]
    pairs = matching['matching']
    need(len(labels) == 112 and len(set(labels)) == 112, '112 distinct selected labels')
    need(len(pairs) == 56 and sorted(x for pair in pairs for x in pair) == list(range(112)), 'perfect matching')
    dot = lambda x, y: (x & y).bit_count() % 2
    planes = []
    owner = [None] * 112
    for i, (a, b) in enumerate(pairs):
        need(dot(labels[a], labels[a]) == dot(labels[b], labels[b]) == 1 and dot(labels[a], labels[b]) == 0,
             'orthonormal matched basis')
        planes.append((labels[a], labels[b]))
        owner[a] = owner[b] = i
    orthogonal = [[all(dot(x, y) == 0 for x in a for y in b) for b in planes] for a in planes]
    allowed = [[i != j and orthogonal[owner[i]][owner[j]] for j in range(112)] for i in range(112)]
    return labels, pairs, owner, orthogonal, allowed


def premises(certificate, orthogonal):
    core, clique = certificate['c5_core'], certificate['clique22']
    need(len(core) == 5 and len(set(core)) == 5, 'five core planes')
    need(len(clique) == 22 and len(set(clique)) == 22 and not set(core) & set(clique), '22 disjoint clique planes')
    for i, x in enumerate(core):
        for j, y in enumerate(core):
            need(orthogonal[x][y] == ((i - j) % 5 in (1, 4)), 'induced orthogonality cycle')
    for x in clique:
        for y in clique:
            need(not orthogonal[x][y], 'clique nonorthogonality')
        for y in core:
            need(not orthogonal[x][y], 'clique-core forced zero')


def supports(certificate, allowed):
    blocks = certificate['rank49_supports']
    need(len(blocks) == 49 and sorted(x for s in blocks for x in s) == list(range(112)), '49 support partition')
    for s in blocks:
        for i in s:
            for j in s:
                need(i == j or allowed[i][j], 'support contains forbidden ordered pair')
    return blocks


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def tensor_fit(blocks, d):
    matrix = [[0] * (112 * d) for _ in range(112 * d)]
    for s in blocks:
        for i in s:
            for j in s:
                for a in range(d):
                    matrix[d*i+a][d*j+a] = 1
    return matrix


def fit(matrix, d, allowed):
    n = len(allowed)
    need(type(d) is int and d > 0 and len(matrix) == n*d and all(len(r) == n*d for r in matrix), 'block shape')
    for i in range(n):
        for j in range(n):
            if i == j or not allowed[i][j]:
                for a in range(d):
                    for b in range(d):
                        need(matrix[d*i+a][d*j+b] == int(i == j and a == b), 'ordered block mask')


def multiply(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def noncommuting_fit(blocks):
    """Integral port-chart conjugate of the credited 49-support construction."""
    triple = next(s for s in blocks if len(s) == 3)
    charts = [identity(2) for _ in range(112)]
    charts[triple[1]] = [[1, 1], [0, 1]]
    charts[triple[2]] = [[1, 0], [1, 1]]
    inverses = [[[p[1][1], -p[0][1]], [-p[1][0], p[0][0]]] for p in charts]
    matrix = [[0] * 224 for _ in range(224)]
    for s in blocks:
        for i in s:
            for j in s:
                block = multiply(charts[i], inverses[j])
                for a in range(2):
                    for b in range(2):
                        matrix[2*i+a][2*j+b] = block[a][b]
    return matrix, triple, charts


def cycle_fit(size):
    """C5 with size-dimensional ports: rank ceil(5 size/2), all fields."""
    groups = []
    for k in range(size // 2):
        for i in range(5):
            groups.append([size*i+2*k+1, size*((i+1) % 5)+2*k])
    if size % 2:
        groups.extend([[size*i+size-1 for i in s] for s in ([0, 1], [2, 3], [4])])
    matrix = [[0] * (5*size) for _ in range(5*size)]
    for group in groups:
        for i in group:
            for j in group:
                matrix[i][j] = 1
    return matrix, groups
