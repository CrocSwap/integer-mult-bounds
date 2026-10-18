#!/usr/bin/env python3
"""Discovery search for multi-write shear programs on the ten phase-B blocks of
PR589's tuned punctured R439 word.

Class (strictly larger than the whole-block single-write class of PR #873/#891
and of PR #880's fixed factor splits, and equal to PR #884/#906's subtraction
class): any program of single-source additive gates `dest += src` on the
block's own registers that realizes the block's exact integer transfer matrix.
Equivalently, any path of legal nonnegative row or column subtractions from
the transfer matrix to the identity.  Multi-write interleavings and shared
intermediate rows are inside the class.  Programs using registers outside the
block are outside the class.

Three deterministic phases per block, one Mersenne Twister seeded
`20261013 + frame`:
  1. 6,000 min-excess greedy reductions with random tie-breaks;
  2. 4,000 uniform random legal trajectories (path cap 90);
  3. a width-6,000 beam searching strictly below the incumbent length.

The stopping rule is complete: all 10,000 trajectories and the beam phase run
to completion for every block; there is no adaptive stopping.  "Best found" is
not an impossibility theorem and no minimality is claimed.

Writes CANDIDATE.json.  Deterministic; standard library only.  Prepared with
help from opencode.  Apache-2.0.
"""
import gzip
import json
import random
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"

# The ten phase-B blocks of the tuned word: frame, first B index, last B index
# (inclusive), in B order.
BLOCKS = [
    (506, 102, 127),
    (507, 128, 162),
    (519, 163, 204),
    (508, 205, 241),
    (520, 242, 282),
    (509, 283, 313),
    (521, 314, 360),
    (522, 361, 403),
    (523, 404, 448),
    (524, 449, 489),
]
GREEDY_TRIALS = 6000
RANDOM_TRIALS = 4000
RANDOM_CAP = 90
BEAM_WIDTH = 6000
SEED_BASE = 20261013


def load_block(first, last):
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    blk = word["B"][first:last + 1]
    assert all(len(ss) == 1 for _, _, ss in blk)
    regs = sorted({t for _, t, _ in blk} | {s for _, _, ss in blk for s in ss})
    index = {r: i for i, r in enumerate(regs)}
    n = len(regs)
    ops = [(index[t], index[ss[0]]) for _, t, ss in blk]
    cols = []
    for c in range(n):
        x = [int(i == c) for i in range(n)]
        for a, b in ops:
            x[a] += x[b]
        cols.append(x)
    matrix = [list(r) for r in zip(*cols)]
    return regs, ops, matrix


def is_identity(mat):
    n = len(mat)
    return all(mat[i][j] == (1 if i == j else 0) for i in range(n) for j in range(n))


def excess(mat):
    n = len(mat)
    return sum(mat[i][j] - (1 if i == j else 0) for i in range(n) for j in range(n))


def legal_moves(mat):
    """(kind, t, s): subtract row s from row t ('r'), or column t from
    column s ('c').  Both keep the matrix nonnegative and both peel exactly
    one gate `t += s`."""
    n = len(mat)
    out = []
    for t in range(n):
        for s in range(n):
            if s == t:
                continue
            if any(mat[s][j] > 0 for j in range(n)) and all(mat[s][j] <= mat[t][j] for j in range(n)):
                out.append(("r", t, s))
            if any(mat[i][t] > 0 for i in range(n)) and all(mat[i][t] <= mat[i][s] for i in range(n)):
                out.append(("c", t, s))
    return out


def apply_move(mat, move):
    kind, t, s = move
    n = len(mat)
    new = [row[:] for row in mat]
    if kind == "r":
        for j in range(n):
            new[t][j] -= mat[s][j]
    else:
        for i in range(n):
            new[i][s] -= mat[i][t]
    return new


def greedy(matrix, rng):
    cur = matrix
    path = []
    while not is_identity(cur):
        moves = legal_moves(cur)
        if not moves:
            return None
        scored = []
        for move in moves:
            nxt = apply_move(cur, move)
            scored.append((excess(nxt), rng.random(), move))
        scored.sort(key=lambda x: (x[0], x[1]))
        move = scored[0][2]
        cur = apply_move(cur, move)
        path.append(move)
        if len(path) > 90:
            return None
    return path


def random_traj(matrix, rng, limit):
    cur = matrix
    path = []
    while not is_identity(cur):
        if len(path) >= limit:
            return None
        moves = legal_moves(cur)
        if not moves:
            return None
        move = moves[rng.randrange(len(moves))]
        cur = apply_move(cur, move)
        path.append(move)
    return path


def beam_search(matrix, rng, width, depth_cap):
    def key(m):
        return tuple(x for row in m for x in row)
    layer = [(matrix, [])]
    seen = {key(matrix)}
    for depth in range(1, depth_cap + 1):
        cand = []
        for state, path in layer:
            for move in legal_moves(state):
                nxt = apply_move(state, move)
                k = key(nxt)
                if k in seen:
                    continue
                seen.add(k)
                cand.append((excess(nxt) + rng.random() * 0.01, nxt, path + [move]))
        if not cand:
            break
        cand.sort(key=lambda x: x[0])
        layer = [(state, p) for _, state, p in cand[:width]]
        for state, p in layer:
            if is_identity(state):
                return depth, p, len(seen)
    return None, None, len(seen)


def path_to_gates(path):
    """Unpeel a reduction path into an apply-order gate list: iterate the path
    in reverse; a row peel appends its gate, a column peel prepends it."""
    gates = []
    for kind, t, s in reversed(path):
        if kind == "r":
            gates.append((t, s))
        else:
            gates.insert(0, (t, s))
    return gates


def check(matrix, path):
    n = len(matrix)
    gates = path_to_gates(path)
    cols = []
    for c in range(n):
        x = [int(i == c) for i in range(n)]
        for a, b in gates:
            x[a] += x[b]
        cols.append(x)
    return [list(r) for r in zip(*cols)] == matrix, gates


def run_block(spec):
    frame, first, last = spec
    regs, ops, matrix = load_block(first, last)
    rng = random.Random(SEED_BASE + frame)
    best = None
    hist = {}
    dead = 0
    for _ in range(GREEDY_TRIALS):
        path = greedy(matrix, rng)
        if path is None:
            dead += 1
            continue
        hist[len(path)] = hist.get(len(path), 0) + 1
        if best is None or len(path) < len(best):
            best = path
    for _ in range(RANDOM_TRIALS):
        path = random_traj(matrix, rng, RANDOM_CAP)
        if path is None:
            dead += 1
            continue
        hist[len(path)] = hist.get(len(path), 0) + 1
        if best is None or len(path) < len(best):
            best = path
    beam_states = 0
    if best is not None:
        _depth, path, beam_states = beam_search(matrix, rng, BEAM_WIDTH, len(best) - 1)
        if path is not None:
            best = path
            hist[len(path)] = hist.get(len(path), 0) + 1
    if best is None:
        return {"frame": frame, "slice": [first, last + 1], "registers": regs,
                "original_gates": len(ops), "new_gates": None, "dead_ends": dead}
    ok, gates = check(matrix, best)
    assert ok, frame
    touched = sorted({regs[t] for t, _ in gates} | {regs[s] for _, s in gates})
    return {
        "frame": frame,
        "slice": [first, last + 1],
        "registers": regs,
        "original_gates": len(ops),
        "new_gates": len(best),
        "gates": [[frame, regs[t], [regs[s]]] for t, s in gates],
        "all_registers_touched": touched == regs,
        "histogram": sorted(hist.items()),
        "dead_ends": dead,
        "beam_states": beam_states,
    }


def main():
    with ProcessPoolExecutor(max_workers=len(BLOCKS)) as pool:
        results = list(pool.map(run_block, BLOCKS))
    results.sort(key=lambda b: b["slice"][0])
    out = {
        "schema": "r439-bsection-multwrite/1",
        "base_commit": "007664306fff84fbb1c9a1b4053b69f439764034",
        "source": WORD,
        "search": {
            "track": "bit supplier (00-19)",
            "assignment_seed": 16,
            "class": "all programs of single-source additive gates dest += src on the block's own registers realizing the exact integer transfer matrix; equivalently all legal nonnegative row/column subtraction paths to the identity",
            "method": f"{GREEDY_TRIALS} min-excess greedy reductions with random tie-breaks, {RANDOM_TRIALS} uniform random legal trajectories (cap {RANDOM_CAP}), then a width-{BEAM_WIDTH} beam below the incumbent",
            "seed_rule": f"random.Random({SEED_BASE} + frame) per block (CPython Mersenne Twister)",
            "stopping_rule": "all trajectories and the beam phase complete for every block; no adaptive stopping",
            "coverage": "all ten phase-B blocks of the pinned tuned word",
            "minimality_claimed": False,
        },
        "blocks": results,
    }
    (HERE / "CANDIDATE.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    total_old = total_new = 0
    for b in results:
        print(b["frame"], b["original_gates"], "->", b["new_gates"],
              "touched", b.get("all_registers_touched"), flush=True)
        total_old += b["original_gates"]
        total_new += b["new_gates"] or b["original_gates"]
    print("PASS_R439_BSECTION_MULTWRITE_SEARCH",
          f"frames={','.join(str(b['frame']) for b in results)}",
          f"gates={total_old}->{total_new}")


if __name__ == "__main__":
    main()
