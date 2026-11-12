"""Check diagonal rigidity of the six remaining Type A erased endpoints."""
import argparse
import hashlib
from itertools import combinations
import json
from pathlib import Path
import runpy
import signal

ROOT = Path(__file__).resolve().parent
CALLER_SHA256 = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
ENGINE_SHA256 = "9e99b716a78afb9d90fee8cf66d6eb1ead88a45c93e89e735cd626e4471756e7"
ANCHOR_ROWS = (0, 1, 18, 19)
ANCHOR_COLUMNS = (2, 9, 20, 27)
ROLES = 36
LIMIT = 20


def alarm_handler(_signum, _frame):
    raise TimeoutError("20-second diagonal-anchor cap")


def read_pinned(path, expected):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("changed input " + path.name)
    return raw


def determinant2(matrix, rows, columns):
    i, j = rows
    a, b = columns
    return matrix[i][a] * matrix[j][b] - matrix[i][b] * matrix[j][a]


def determinant3(matrix, rows, columns):
    ((a, b, c), (d, e, f), (g, h, i)) = [[matrix[r][s] for s in columns] for r in rows]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def first_anchor(matrix, row_pairs, col_pairs, root=None):
    for rows in row_pairs:
        if root in rows:
            continue
        for columns in col_pairs:
            if root in columns or not set(rows).isdisjoint(columns):
                continue
            value = determinant2(matrix, rows, columns)
            if value:
                return rows, columns, value
    return None


def choose_anchors(matrix):
    main_rows = list(combinations(ANCHOR_ROWS, 2))
    main_columns = list(combinations(ANCHOR_COLUMNS, 2))
    origin = first_anchor(matrix, main_rows, main_columns)
    assert origin is not None
    basis_rows, basis_columns, _ = origin

    # For a rank-two matrix the anchor factors A[:,basis_columns] and
    # A[basis_rows,:] have rank two.  Cauchy--Binet excludes exactly the
    # row or column pairs with zero determinant in their respective factors.
    all_pairs = list(combinations(range(ROLES), 2))
    usable_rows = [rows for rows in all_pairs if determinant2(matrix, rows, basis_columns)]
    usable_columns = [cols for cols in all_pairs if determinant2(matrix, basis_rows, cols)]

    anchors = {}
    missing = []
    for root in range(ROLES):
        witness = first_anchor(matrix, main_rows, main_columns, root)
        if witness is None:
            witness = first_anchor(matrix, usable_rows, usable_columns, root)
        if witness is None:
            missing.append(root)
            continue
        rows, cols, determinant = witness
        assert root not in rows and root not in cols and set(rows).isdisjoint(cols)
        r3, c3 = (*rows, root), (*cols, root)
        assert determinant3(matrix, r3, c3) == 0
        # Corrupt only the new corner. Every other entry is off diagonal
        # and fixed by the unchanged erased endpoint.
        matrix[root][root] += 1
        assert determinant3(matrix, r3, c3) == determinant
        matrix[root][root] -= 1
        anchors[str(root)] = dict(rows=rows, columns=cols, determinant=determinant)
    return anchors, missing


def fallback_pair(matrices, rank):
    pair = (0, 17)
    ranks = []
    for _, matrix in matrices:
        residual = [row[:] for row in matrix]
        for root in pair:
            residual[root][root] -= 2
        ranks.append(rank(residual)[0])
    return dict(roots=pair, evaluated=True, residual_ranks=ranks)


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caller", type=Path, default=ROOT/"inputs/CALLER.json")
    parser.add_argument("--engine", type=Path, default=ROOT/"replay_r164.py")
    args = parser.parse_args()
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(LIMIT)

    read_pinned(args.engine, ENGINE_SHA256)
    engine = runpy.run_path(str(args.engine))
    caller = json.loads(read_pinned(args.caller, CALLER_SHA256))
    events = caller["events"]
    type_a = caller["types"]["A"]
    assert len(events) == 4783 and type_a["roles"] == ROLES
    assert type_a["alpha2"] == "-1" and type_a["beta2"] == "0"
    assert [e[1] for e in events if e[0] == "J"] == list(range(1, 18))
    clocks = engine["QUERY_CLOCKS"]
    assert tuple(i for i, e in enumerate(events) if e[:2] == ["A", "QUERY"]) == clocks

    rank = engine["rank"]
    configs = [tuple(1 if i in plus else -1 for i in range(4)) for plus in combinations(range(4), 2)]
    matrices = []
    cases = []
    for constants in configs:
        matrix = engine["pullback"](engine["specialized"](events, -1, constants))
        for i in range(ROLES):
            matrix[i][i] += 1
        assert rank(matrix)[0] == 2
        off_diagonal = [[matrix[i][j] for j in ANCHOR_COLUMNS] for i in ANCHOR_ROWS]
        assert rank(off_diagonal)[0] == 2
        anchors, missing = choose_anchors(matrix)
        assert len(anchors) + len(missing) == ROLES
        cases.append(dict(constants=constants, full_rank=2, off_diagonal_rank=2,
                          anchors=anchors, missing=missing))
        matrices.append((constants, matrix))

    total = sum(len(case["anchors"]) for case in cases)
    if total < len(configs) * ROLES:
        next_pair = fallback_pair(matrices, rank)
    else:
        next_pair = dict(roots=(0, 17), evaluated=False, reason="All diagonal entries are fixed by anchors.")
    receipt = dict(
        head=engine["HEAD"], caller_head=engine["CALLER_HEAD"],
        pins={"inputs/CALLER.json": CALLER_SHA256, "replay_r164.py": ENGINE_SHA256},
        roles=ROLES, events=len(events), fixed_J_stages=17, zero_based_query_clocks=clocks,
        unit_body=True, q=-1, words=len(configs), checks=len(configs) * ROLES,
        anchors=total, missing=len(configs) * ROLES - total, cases=cases,
        standard_offdiagonal_rows=ANCHOR_ROWS, standard_offdiagonal_columns=ANCHOR_COLUMNS,
        next_pair=next_pair, hard_cap_seconds=LIMIT,
        controls=["original minus endpoint inherited from R164",
                  "changing each anchored diagonal alone produces a nonzero rank-three minor"],
    )
    signal.alarm(0)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
