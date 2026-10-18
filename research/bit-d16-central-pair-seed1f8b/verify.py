"""Independent tuple-state replay of the exact D16 two-register search."""
from __future__ import annotations
import hashlib, itertools, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def group_mul(a: int, b: int) -> int:
    i, e = divmod(a, 2)
    j, f = divmod(b, 2)
    return 2 * ((i + (-j if e else j)) % 8) + (e ^ f)


G = tuple(tuple(group_mul(a, b) for b in range(16)) for a in range(16))
LABELS = (1, 3)
PROJECTORS = tuple((u, v) for u, v in itertools.product((1, 2, 3), repeat=2)
                   if (u & v).bit_count() == 1)
GENERATORS = tuple((g, u, v) for g in LABELS for u, v in PROJECTORS)
ID = (1, 0, 0, 1)
Z = 1 << 8
TARGET = (Z, 0, 0, Z)


def pack(state: tuple[int, int, int, int]) -> int:
    return sum(value << (16 * i) for i, value in enumerate(state))


def group_left(g: int, polynomial: int) -> int:
    result = 0
    while polynomial:
        low = polynomial & -polynomial
        h = low.bit_length() - 1
        result ^= 1 << G[g][h]
        polynomial ^= low
    return result


def transition(state: tuple[int, int, int, int], k: int) -> tuple[int, int, int, int]:
    g, u, v = GENERATORS[k]
    cells = list(state)
    for col in range(2):
        pulled = 0
        for row in range(2):
            if v & (1 << row):
                pulled ^= cells[2 * row + col]
        correction = pulled ^ group_left(g, pulled)
        for row in range(2):
            if u & (1 << row):
                cells[2 * row + col] ^= correction
    return tuple(cells)


def code_len(code: int) -> int:
    return (code.bit_length() - 1 + 3) // 4


def ball(start: tuple[int, int, int, int], depth_limit: int, cap: int):
    paths = {start: 1}
    front = [start]
    layers = [1]
    digest = hashlib.sha256(pack(start).to_bytes(8, 'little'))
    for depth in range(1, depth_limit + 1):
        next_front = []
        for state in front:
            code = paths[state]
            for k in range(len(GENERATORS)):
                value = transition(state, k)
                if value not in paths:
                    need(len(paths) + len(next_front) < cap, 'state cap exceeded')
                    paths[value] = (code << 4) | k
                    next_front.append(value)
                    digest.update(pack(value).to_bytes(8, 'little'))
        front = next_front
        layers.append(len(front))
        if not front:
            break
    return paths, layers, digest.hexdigest()


def poly_mul(a: int, b: int) -> int:
    result = 0
    while a:
        low = a & -a
        h = low.bit_length() - 1
        transported = b
        shifted = 0
        while transported:
            bit = transported & -transported
            j = bit.bit_length() - 1
            shifted ^= 1 << G[h][j]
            transported ^= bit
        result ^= shifted
        a ^= low
    return result


def matrix_mul(a: tuple[int, int, int, int], b: tuple[int, int, int, int]):
    out = [0, 0, 0, 0]
    for i, j, k in itertools.product(range(2), repeat=3):
        out[2 * i + j] ^= poly_mul(a[2 * i + k], b[2 * k + j])
    return tuple(out)


def formal_product(word: list[int]):
    current = ID
    for k in word:
        g, u, v = GENERATORS[k]
        q = (1 << 0) | (1 << g)
        factor = []
        for i in range(2):
            for j in range(2):
                value = q if (u >> i & 1) and (v >> j & 1) else 0
                if i == j:
                    value ^= 1
                factor.append(value)
        current = matrix_mul(tuple(factor), current)
    return current


def run() -> dict:
    task = json.loads((HERE / 'TASK.json').read_text())
    source = json.loads((HERE / 'SOURCES.json').read_text())
    cert = json.loads((HERE / 'CERTIFICATE.json').read_text())
    for item in source['files']:
        actual = hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest()
        need(actual == item['sha256'], 'pinned source changed: ' + item['path'])
    need(task['seed'] == '1f8b0e71668765ab2db464db5f28907f', 'seed pin')
    need(task['base_commit'] == source['base_commit'], 'base pin')
    need(task['selected_record_sha256'] == source['files'][0]['sha256'], 'selected record pin')
    need(len(PROJECTORS) == 6 and len(GENERATORS) == 12, 'complete legal alphabet')
    need(all(G[0][a] == a and G[a][0] == a for a in range(16)), 'group identity')
    need(all(G[G[a][b]][c] == G[a][G[b][c]]
             for a, b, c in itertools.product(range(16), repeat=3)), 'group associativity')
    need(G[1][1] == 0 and G[3][3] == 0, 'paid labels are involutions')
    xy = G[1][3]
    xy2 = G[xy][xy]
    need(G[xy2][xy2] == 8, '(xy)^4 must be r^4')
    need(G[8][8] == 0 and all(G[8][a] == G[a][8] for a in range(16)), 'central involution')

    direct = cert['direct_word']
    need(len(direct) == 16, 'direct paid call count')
    need(formal_product(direct) == TARGET, 'direct full group-algebra control')
    need(all(formal_product(direct[:i] + direct[i + 1:]) != TARGET
             for i in range(len(direct))), 'omission controls')
    index = {g: k for k, g in enumerate(GENERATORS)}
    altered = list(direct)
    g, u, v = GENERATORS[altered[0]]
    other = 3 if g == 1 else 1
    altered[0] = index[(other, u, v)]
    need(formal_product(altered) != TARGET, 'paid-label mutation control')
    wrong_target = (1 << 6, 0, 0, Z)
    need(formal_product(direct) != wrong_target, 'wrong-endpoint control')

    cap = cert['state_cap_per_ball']
    left, left_layers, left_hash = ball(ID, cert['identity_depth'], cap)
    right, right_layers, right_hash = ball(TARGET, cert['target_depth'], cap)
    need(left_layers == cert['identity_layers'], 'identity layer counts')
    need(right_layers == cert['target_layers'], 'target layer counts')
    need(left_hash == cert['identity_discovery_sha256'], 'identity state digest')
    need(right_hash == cert['target_discovery_sha256'], 'target state digest')
    common = left.keys() & right.keys()
    lengths = [code_len(left[s]) + code_len(right[s]) for s in common]
    need(len(common) == cert['common_states'] == 0, 'no midpoint in complete balls')
    need(all(n >= 16 for n in lengths), 'word-length split lower bound')
    need(cert['depths_cover_all_words_at_most_15'] and cert['no_word_at_most_15'], 'complete 15-call coverage')
    need(cert['status'] == 'EXACT_MINIMUM_16' and cert['lower_bound'] == 16, 'minimum receipt')
    return {
        'status': 'PASS_D16_TWO_REGISTER_MINIMUM',
        'group_order': 16,
        'registers': 2,
        'paid_generators': len(GENERATORS),
        'identity_layers': left_layers,
        'target_layers': right_layers,
        'identity_discovery_sha256': left_hash,
        'target_discovery_sha256': right_hash,
        'common_states': len(common),
        'exact_minimum': 16,
        'direct_omission_controls': 16,
        'paid_label_mutation_rejected': True,
        'wrong_endpoint_rejected': True,
        'supplier_mapping': 'not established; no kappa claim'
    }


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
