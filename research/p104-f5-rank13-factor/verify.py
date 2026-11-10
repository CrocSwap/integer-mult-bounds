#!/usr/bin/env python3
"""Check the 104 by 13 factorisation of the P104 odd-graph window.

The witness is a partition of the 104 ports into 13 cliques of the odd graph.
Port i is sent to the standard basis vector of its clique in F^13. The Gram
matrix is a 1-block pattern of rank 13 over every field: diagonal 1, and a
zero on every F_2-orthogonal pair because such a pair does not lie in a clique.

Standard library only. The port integers are pinned to the bytes shipped with
PR #6933; this program does not replay that paper's lower bound.
"""
import hashlib
import json
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORTS_PATH = ROOT / "data" / "ports_p104.json"
FRAMES_PATH = ROOT / "data" / "frames.json"
PORTS_SHA256 = "691c7b7d212112115b1bfc76db89f90d304ec448dc8c4a0c43d9a5954317146c"
FIELDS = (2, 3, 5, 7)


def dot2(a, b):
    return bin(a & b).count("1") & 1


def rank(rows, prime):
    matrix = [[entry % prime for entry in row] for row in rows]
    row_count, col_count = len(matrix), len(matrix[0])
    rank_value = 0
    for col in range(col_count):
        pivot = next((row for row in range(rank_value, row_count) if matrix[row][col] % prime), None)
        if pivot is None:
            continue
        matrix[rank_value], matrix[pivot] = matrix[pivot], matrix[rank_value]
        inverse = pow(matrix[rank_value][col], -1, prime)
        matrix[rank_value] = [(entry * inverse) % prime for entry in matrix[rank_value]]
        for row in range(row_count):
            if row != rank_value and matrix[row][col] % prime:
                factor = matrix[row][col]
                matrix[row] = [(matrix[row][col_index] - factor * matrix[rank_value][col_index]) % prime
                               for col_index in range(col_count)]
        rank_value += 1
        if rank_value == row_count:
            break
    return rank_value


def factor_rows(frames):
    width = len(frames)
    rows = []
    for frame_index, frame in enumerate(frames):
        for _port in frame:
            row = [0] * width
            row[frame_index] = 1
            rows.append(row)
    return rows


def identity_minor(frames):
    """One port from each frame, in frame order, is a permutation matrix."""
    width = len(frames)
    minor = []
    for frame_index, frame in enumerate(frames):
        row = [0] * width
        row[frame_index] = 1
        minor.append(row)
    return minor


def clique_faults(frames):
    faults = []
    for frame_index, frame in enumerate(frames):
        if len(frame) != 8 or len(set(frame)) != 8:
            faults.append(("frame-size", frame_index, len(frame)))
        for left, right in combinations(frame, 2):
            if dot2(left, right) == 0:
                faults.append(("orthogonal-inside-frame", frame_index, left, right))
    return faults


def mask_faults(frames):
    """Rebuild M = W W^T and test the 1-block mask on these ports."""
    ports = [port for frame in frames for port in frame]
    rows = factor_rows(frames)
    faults = []
    for index, (port, row) in enumerate(zip(ports, rows)):
        if sum(entry * entry for entry in row) % 5 != 1:
            faults.append(("diagonal", port))
        for other_index in range(index):
            other = ports[other_index]
            if dot2(port, other):
                continue
            dot = sum(left * right for left, right in zip(row, rows[other_index])) % 5
            if dot != 0:
                faults.append(("orthogonal-dot", port, other, dot))
    return faults


def load():
    port_bytes = PORTS_PATH.read_bytes()
    digest = hashlib.sha256(port_bytes).hexdigest()
    if digest != PORTS_SHA256:
        raise SystemExit("port-list sha256 mismatch: " + digest)
    ports = json.loads(port_bytes.decode())["ports"]
    frames_doc = json.loads(FRAMES_PATH.read_text(encoding="utf-8"))
    return ports, frames_doc["frames"], frames_doc["excluded_odd_cliques"]


def main():
    ports, frames, excluded = load()
    if len(ports) != 104 or len(set(ports)) != 104:
        raise SystemExit("expected 104 distinct ports")
    orthogonal_pairs = sum(
        1 for left, right in combinations(ports, 2) if dot2(left, right) == 0
    )
    if orthogonal_pairs != 2496:
        raise SystemExit("orthogonal-pair count is {0}, expected 2496".format(orthogonal_pairs))
    covered = [port for frame in frames for port in frame]
    if sorted(covered) != sorted(ports):
        raise SystemExit("frames are not a partition of the P104 port list")
    faults = clique_faults(frames) + mask_faults(frames)
    if faults:
        raise SystemExit("witness failed: " + repr(faults[:5]))
    rows = factor_rows(frames)
    ranks = {prime: rank(rows, prime) for prime in FIELDS}
    if any(value != 13 for value in ranks.values()):
        raise SystemExit("rank is not 13: " + repr(ranks))
    minor = identity_minor(frames)
    if any(rank(minor, prime) != 13 for prime in FIELDS):
        raise SystemExit("identity minor is singular")

    # Failure controls. Each mutant must trip the mask or the rank check.
    orthogonal_pair = None
    for left_index, left in enumerate(frames):
        for right in frames[left_index + 1:]:
            for a in left:
                for b in right:
                    if dot2(a, b) == 0:
                        orthogonal_pair = (left_index, a, b)
                        break
                if orthogonal_pair:
                    break
            if orthogonal_pair:
                break
        if orthogonal_pair:
            break
    if orthogonal_pair is None:
        raise SystemExit("control setup found no cross-frame orthogonal pair")
    frame_index, port_a, port_b = orthogonal_pair
    # Put both endpoints of an orthogonal pair in one frame.
    host = next(index for index, frame in enumerate(frames) if port_b in frame)
    moved = [list(frame) for frame in frames]
    moved[frame_index] = [port for port in moved[frame_index] if port != port_a]
    moved[host] = list(moved[host]) + [port_a]
    if not clique_faults(moved):
        raise SystemExit("orthogonal-pair mutant was accepted")
    shared = [list(frame) for frame in frames]
    # Give frame 0 and frame 1 the same factor coordinate by merging their labels.
    merged = [shared[0] + shared[1]] + shared[2:]
    if rank(factor_rows(merged), 5) != 12 or not mask_faults(merged):
        raise SystemExit("merged-frame mutant was accepted")

    excluded_faults = []
    flat_excluded = [port for clique in excluded for port in clique]
    if len(excluded) != 2 or any(len(clique) != 8 for clique in excluded):
        excluded_faults.append("shape")
    if len(set(flat_excluded)) != 16 or set(flat_excluded) & set(ports):
        excluded_faults.append("overlap")
    excluded_faults.extend(clique_faults(excluded))
    if excluded_faults:
        raise SystemExit("excluded cliques failed: " + repr(excluded_faults[:5]))
    p112_ranks = []
    for clique in excluded:
        p112_frames = list(frames) + [clique]
        p112_rows = factor_rows(p112_frames)
        p112_ranks.append({prime: rank(p112_rows, prime) for prime in FIELDS})
        if any(value != 14 for value in p112_ranks[-1].values()) or mask_faults(p112_frames):
            raise SystemExit("P112 extension failed")
    p120_rows = factor_rows(list(frames) + list(excluded))
    p120_ranks = {prime: rank(p120_rows, prime) for prime in FIELDS}
    if any(value != 15 for value in p120_ranks.values()):
        raise SystemExit("P120 extension rank is not 15")
    if mask_faults(list(frames) + list(excluded)):
        raise SystemExit("P120 mask failed")

    print(
        "PASS_P104_F5_RANK13 rank13=13 fields={fields} p112=14 p120=15 orth_pairs_split={pairs}".format(
            fields=",".join(str(prime) for prime in FIELDS),
            pairs=orthogonal_pairs,
        )
    )


if __name__ == "__main__":
    main()
