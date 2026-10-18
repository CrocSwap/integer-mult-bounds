"""Exact bounded word synthesis in F2[D16] for two scalar registers."""
from __future__ import annotations
import argparse, hashlib, itertools, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ID_DEPTH = 7
TARGET_DEPTH = 8
DEFAULT_CAP = 4_000_000
LABELS = (1, 3)  # s and r*s in (rotation exponent, reflection bit) encoding


def group_product(a: int, b: int) -> int:
    ia, ea = divmod(a, 2)
    ib, eb = divmod(b, 2)
    return (2 * ((ia + (-ib if ea else ib)) % 8)) + (ea ^ eb)


GROUP = tuple(tuple(group_product(a, b) for b in range(16)) for a in range(16))
IDENTITY = 1 | (1 << 48)
Z = 1 << 8  # r^4
TARGET = Z | (Z << 48)
PROJECTORS = tuple((u, v) for u, v in itertools.product((1, 2, 3), repeat=2)
                   if (u & v).bit_count() % 2 == 1)
GENERATORS = tuple((g, u, v) for g in LABELS for u, v in PROJECTORS)
PERM = tuple(tuple(sum(1 << GROUP[g][j] for j in range(16) if poly >> j & 1)
                   for poly in range(1 << 16)) for g in LABELS)
LABEL_SLOT = {g: k for k, g in enumerate(LABELS)}


def step(state: int, generator: tuple[int, int, int]) -> int:
    g, u, v = generator
    cells = [(state >> (16 * i)) & 0xFFFF for i in range(4)]
    permutation = PERM[LABEL_SLOT[g]]
    for col in range(2):
        value = 0
        for row in range(2):
            if v >> row & 1:
                value ^= cells[2 * row + col]
        delta = value ^ permutation[value]
        for row in range(2):
            if u >> row & 1:
                cells[2 * row + col] ^= delta
    return sum(cell << (16 * i) for i, cell in enumerate(cells))


def path_length(code: int) -> int:
    return (code.bit_length() - 1 + 3) // 4


def decode_path(code: int) -> list[int]:
    out = []
    while code != 1:
        out.append(code & 15)
        code >>= 4
    return list(reversed(out))


class StateCap(Exception):
    def __init__(self, depth: int, seen: int, reached: int):
        self.depth, self.seen, self.reached = depth, seen, reached


def ball(start: int, depth_limit: int, cap: int) -> tuple[dict[int, int], list[int], str]:
    """Return state->packed path, complete layer sizes, and discovery-order hash."""
    paths = {start: 1}
    front = [start]
    layers = [1]
    digest = hashlib.sha256(start.to_bytes(8, 'little'))
    for depth in range(1, depth_limit + 1):
        nxt = []
        for state in front:
            code = paths[state]
            for k, gen in enumerate(GENERATORS):
                value = step(state, gen)
                if value not in paths:
                    if len(paths) + len(nxt) >= cap:
                        raise StateCap(depth - 1, len(paths), len(nxt))
                    nxt.append(value)
                    paths[value] = (code << 4) | k
                    digest.update(value.to_bytes(8, 'little'))
        front = nxt
        layers.append(len(front))
        if not front:
            break
    return paths, layers, digest.hexdigest()


def matrix_product(word: list[int]) -> list[list[set[int]]]:
    """Independent literal coefficient-set engine for exact F2[D16] products."""
    out = [[{0} if i == j else set() for j in range(2)] for i in range(2)]

    def scalar_mul(left: set[int], right: set[int]) -> set[int]:
        result = set()
        for a in left:
            for b in right:
                result.symmetric_difference_update((GROUP[a][b],))
        return result

    for k in word:
        g, u, v = GENERATORS[k]
        q = {0, g}
        factor = [[set() for _ in range(2)] for _ in range(2)]
        for i in range(2):
            for j in range(2):
                if u >> i & 1 and v >> j & 1:
                    factor[i][j] = set(q)
                if i == j:
                    factor[i][j].symmetric_difference_update((0,))
        nxt = [[set() for _ in range(2)] for _ in range(2)]
        for i, j, k2 in itertools.product(range(2), repeat=3):
            nxt[i][j].symmetric_difference_update(scalar_mul(factor[i][k2], out[k2][j]))
        out = nxt
    return out


def target_matrix() -> list[list[set[int]]]:
    return [[{8}, set()], [set(), {8}]]


def direct_word() -> list[int]:
    indices = {(g, u, v): k for k, (g, u, v) in enumerate(GENERATORS)}
    word = []
    for reg in range(2):
        projector = 1 << reg
        word.extend(indices[(g, projector, projector)] for g in (1, 3) * 4)
    return word


def run(id_depth: int = ID_DEPTH, target_depth: int = TARGET_DEPTH,
        cap: int = DEFAULT_CAP) -> dict:
    direct = direct_word()
    assert len(PROJECTORS) == 6 and len(GENERATORS) == 12
    assert all(GROUP[0][a] == a and GROUP[a][0] == a for a in range(16))
    assert all(GROUP[GROUP[a][b]][c] == GROUP[a][GROUP[b][c]]
               for a, b, c in itertools.product(range(16), repeat=3))
    xy = GROUP[1][3]
    xy2 = GROUP[xy][xy]
    assert GROUP[xy2][xy2] == 8  # (xy)^4=r^4
    assert GROUP[8][8] == 0 and all(GROUP[8][a] == GROUP[a][8] for a in range(16))
    assert matrix_product(direct) == target_matrix(), 'direct 16-call control'

    result = {
        'group': 'D16=<r,s | r^8=s^2=1, srs=r^-1>',
        'encoding': 'element 2*i+e represents r^i s^e',
        'labels': {'x': 1, 'y': 3, 'z': 8},
        'registers': 2,
        'projector_count': len(PROJECTORS),
        'paid_generator_count': len(GENERATORS),
        'identity_depth': id_depth,
        'target_depth': target_depth,
        'state_cap_per_ball': cap,
        'direct_paid_calls': len(direct),
        'direct_word': direct,
        'direct_exact': True,
        'status': 'INCOMPLETE',
    }
    left = right = None
    try:
        left, ll, lh = ball(IDENTITY, id_depth, cap)
        result['identity_layers'] = ll
        result['identity_discovery_sha256'] = lh
        right, rr, rh = ball(TARGET, target_depth, cap)
        result['target_layers'] = rr
        result['target_discovery_sha256'] = rh
    except StateCap as e:
        result['status'] = 'STATE_CAP'
        result['cap_depth_completed'] = e.depth
        result['cap_seen_before_layer'] = e.seen
        result['cap_new_states_seen'] = e.reached
        result['exact_coverage'] = 'only the complete layers in *_layers'
        return result

    meeting = []
    for state in left.keys() & right.keys():
        lcode, rcode = left[state], right[state]
        total = path_length(lcode) + path_length(rcode)
        meeting.append((total, state, lcode, rcode))
    under16 = [m for m in meeting if m[0] <= 15]
    result['common_states'] = len(meeting)
    result['meeting_length_histogram'] = {}
    for total, *_ in meeting:
        result['meeting_length_histogram'][str(total)] = result['meeting_length_histogram'].get(str(total), 0) + 1
    complete_depth_coverage = ((id_depth >= 7 and target_depth >= 8) or
                               (id_depth >= 8 and target_depth >= 7))
    result['depths_cover_all_words_at_most_15'] = complete_depth_coverage
    result['no_word_at_most_15'] = (not under16) if complete_depth_coverage else None
    if under16:
        total, state, lcode, rcode = min(under16)
        witness = decode_path(lcode) + list(reversed(decode_path(rcode)))
        assert len(witness) == total and matrix_product(witness) == target_matrix()
        result['status'] = 'SHORTER_WITNESS'
        result['witness'] = witness
        result['witness_length'] = total
        result['witness_omission_controls'] = all(
            matrix_product(witness[:i] + witness[i + 1:]) != target_matrix()
            for i in range(len(witness)))
    elif complete_depth_coverage:
        result['status'] = 'EXACT_MINIMUM_16' if not meeting else 'NO_WORD_AT_MOST_15'
        result['lower_bound'] = 16
    else:
        result['status'] = 'INCOMPLETE_DEPTH'
    result['exact_full_group_algebra'] = True
    result['scalar_mixing'] = 'all six rank-one idempotents; GL2(F2) conjugation is transitive on them'
    result['supplier_mapping'] = 'not established; no kappa claim'
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--identity-depth', type=int, default=ID_DEPTH)
    parser.add_argument('--target-depth', type=int, default=TARGET_DEPTH)
    parser.add_argument('--max-states', type=int, default=DEFAULT_CAP)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    cert = run(args.identity_depth, args.target_depth, args.max_states)
    if args.write:
        (HERE / 'CERTIFICATE.json').write_text(json.dumps(cert, indent=2) + '\n')
    print(json.dumps({k: cert[k] for k in cert if k.endswith('_layers') or k in ('status','common_states','meeting_length_histogram','witness_length','lower_bound','cap_depth_completed','cap_seen_before_layer','cap_new_states_seen')}, indent=2))


if __name__ == '__main__':
    main()
