"""Independent proof-premise checker; imports no primary or predecessor code.

Exact rational column-span elimination, explicit registered owner matrices and
integer character orthogonality. Does not execute native child kernels.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
import gzip
import hashlib
import io
import json
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    def reject(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(Path(path).read_bytes(), object_pairs_hook=pairs, parse_constant=reject)


def span_rank(columns):
    basis = {}
    for column in columns:
        v = list(map(Q, column))
        for i in sorted(basis):
            if v[i]:
                q = v[i]
                v = [a - q * b for a, b in zip(v, basis[i])]
        pivot = next((i for i, x in enumerate(v) if x), None)
        if pivot is not None:
            q = v[pivot]
            basis[pivot] = [x / q for x in v]
    return len(basis)


def matvec(columns, vector):
    out = 0
    while vector:
        low = vector & -vector
        out ^= columns[low.bit_length() - 1]
        vector ^= low
    return out


def main():
    sources = read(HERE / 'SOURCES.json')
    live = {x['path']: x['sha256'] for x in sources['files'] if x['usage'] == 'input'}
    for path, digest in live.items():
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, 'source bytes')
    receipt, cert = read(HERE / 'RESULT.json'), read(HERE / 'CERTIFICATE.json')
    require(receipt['source_sha256'] == live, 'receipt source binding')
    require(receipt['certificate_sha256'] == hashlib.sha256((HERE / 'CERTIFICATE.json').read_bytes()).hexdigest(), 'certificate binding')
    packet = json.loads(gzip.decompress((ROOT / 'research/joint-query/certificate.json.gz').read_bytes()))
    with tarfile.open(fileobj=io.BytesIO((ROOT / 'research/community-frontier1042-audit/selected-replay.tar.gz').read_bytes()), mode='r:gz') as arc:
        path = 't16/global/base/work/complex-nine-native/DATA-PHASES.json'
        members = [m for m in arc.getmembers() if m.name == path]
        require(len(members) == 1 and members[0].isfile(), 'unique phase member')
        raw = arc.extractfile(members[0]).read()
        require(hashlib.sha256(raw).hexdigest() == 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa', 'phase member bytes')
        phases = json.loads(raw)
    U, A = packet['U_ports'], packet['A_ports']
    require(len(U) == 96 and len(A) == 8, 'partition dimensions')
    R = [[Q(row.get(str(p), '0')) for p in range(112)] for row in packet['R_rows']]
    columns = [[row[p] for row in R] for p in range(112)]
    require(span_rank([columns[p] for p in U]) == 8 and all(any(columns[p]) for p in U), 'source rank and nonzero columns')
    registry = {tuple(x['owner_right_matrix_columns']) for x in packet['map_registry'].values()}
    bases = [x['idle_children'][0]['orthogonal_axes'][:8] for x in phases['recipes']]
    routes = {}
    for p, b in enumerate(bases):
        local = [phases['recipes'][p]['q']] + b
        require(len(local) == 9 and all(0 < x < 512 for x in local), 'local basis dimension')
        require(all((x & y).bit_count() % 2 == int(i == j)
                    for i, x in enumerate(local) for j, y in enumerate(local)), 'local orthonormal basis')
        for stage in range(1, 9):
            out = []
            for i in range(73):
                v = 1 << i
                result = v
                for j, axis in enumerate(b):
                    slot = 1 << (9 + 8 * (stage - 1) + j)
                    if ((v & axis).bit_count() + int(bool(v & slot))) % 2:
                        result ^= axis ^ slot
                out.append(result)
            matrix = tuple(out)
            require(matrix in registry, 'registered actual route')
            require(all(matvec(matrix, axis) == 1 << (9 + 8 * (stage - 1) + j)
                        for j, axis in enumerate(b)), 'all-axis route identity')
            require(all(matvec(matrix, matrix[i]) == 1 << i for i in range(73)), 'route involution')
            routes[stage, p] = matrix
    require(set(cert['owner_words_by_prefix']) == {str(i) for i in range(512)}, 'all owner prefixes')
    owner_rows = []
    for prefix in range(512):
        row = 1
        word = cert['owner_words_by_prefix'][str(prefix)]
        require(len(word) <= 4 and all(type(p) is int and 0 <= p < 112 for p in word), 'owner word domain')
        for p in word:
            # Direct row-times-matrix, distinct from primary column-vector action.
            row = sum(((row & column).bit_count() % 2) << i
                      for i, column in enumerate(routes[1, p]))
        require(row & 511 == prefix, 'actual owner evaluation')
        owner_rows.append(row)
    axes = sorted({b for p in U for b in bases[p]})
    require(axes == cert['occurring_axes'], 'full axis inventory')
    masks = {b: sum(int((x & b).bit_count() % 2) << x for x in range(512)) for b in axes}
    require(all(masks[c].bit_count() - 2 * (masks[b] & masks[c]).bit_count() == (-256 if b == c else 0)
                for b in axes for c in axes), 'Walsh left inverse on actual owners')
    require(len({tuple(bases[p]) for p in U}) == 96, 'all complete chart tuples distinct')
    thresholds = []
    for level in receipt['axis_prefix_thresholds']:
        k = level['axes']
        groups = {}
        for p in U:
            groups.setdefault(tuple(bases[p][:k]), []).append(p)
        actual = [{'ports': g, 'rank': span_rank([columns[p] for p in g])} for g in groups.values()]
        require(actual == level['classes'], 'common-refinement class ranks')
        nullity = sum(len(g['ports']) - g['rank'] for g in actual)
        require(nullity == level['total_internal_nullity'], 'internal nullity bound')
        unread = level['attaining_unread']
        require(len(unread) == 8 + nullity, 'attaining unread cardinality')
        subgroups = {}
        for p in unread:
            subgroups.setdefault(tuple(bases[p][:k]), []).append(p)
        require(sum(span_rank([columns[p] for p in g]) for g in subgroups.values()) ==
                span_rank([columns[p] for p in unread]) == 8, 'attaining direct-sum rank')
        require(level['minimum_reads'] == 96 - len(unread), 'minimum read threshold')
        thresholds.append(level['minimum_reads'])
    require(thresholds == [66, 76, 84, 88, 88, 88, 88, 88], 'complete threshold hierarchy')
    fixtures = receipt['boundary_87_read_witnesses'] + receipt['deeper_axis_witnesses'] + [receipt['predecessor_66_read_set']]
    for witness in fixtures:
        c = {int(p): Q(x) for p, x in witness['coefficients'].items()}
        require(set(c) <= set(witness['unread_ports']), 'unread witness support')
        require(all(sum(row[p] * x for p, x in c.items()) == 0 for row in R), 'exact source relation')
        axis, vector = witness['axis_zero_based'], owner_rows[witness['owner_prefix']]
        H = [sum(row[p] * x * ((vector & bases[p][axis]).bit_count() % 2) for p, x in c.items()) for row in R]
        require(any(H) and list(map(str, H)) == witness['old_query_at_owner'], 'nonzero actual-owner query')
        initial = [-sum(R[k][p] * H[k] for k in range(8)) / 4 for p in A]
        require(any(initial) and list(map(str, initial)) == witness['initial_A_at_owner'], 'nonzero original selected input')
    for decoder in receipt['mixed_axis_decoders']:
        basis = decoder['completion_basis'];inv = [[Q(x) for x in row] for row in decoder['basis_inverse']]
        require(all(sum(R[i][basis[k]] * inv[k][j] for k in range(8)) == int(i == j)
                    for i in range(8) for j in range(8)), 'exact completion inverse')
    require(receipt['sharp_family_read_threshold'] == 88 and not receipt['full_controller_sufficiency'], 'scoped conclusion')
    print('PASS_INDEPENDENT_EIGHT_AXIS_CERTIFICATE', 'thresholds=' + ','.join(map(str, thresholds)),
          'owners=512', 'witnesses=' + str(len(fixtures)))


if __name__ == '__main__':
    main()
