"""Independently invert the exact caller and check two-root sector Gram ranks."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import perf_counter

PINS = {
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "next-root28/7398/inputs/reverse.py": "d763b974585a439472bcaacf0913fc5c8469ea24212545287a3a359526ff51cd",
}
PAIRS = {(7, 25): (7, 8), (10, 28): (9, 10)}
END = 4783
TOTAL = 38272
CAP = 30
ZERO = (Q(0), Q(0))
ONE = (Q(1), Q(0))
Z4 = (Q(0),) * 4
FINAL_PHASE = 3


def emit(result):
    print(dumps(result, indent=2, sort_keys=True, default=str), flush=True)


def unique(items):
    result = dict(items)
    assert len(result) == len(items), "duplicate receipt field"
    return result


def verify_hash(path, expected):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == expected, path
    return raw


def event_columns(diagonal, pair):
    columns = [[{} for _ in range(36)] for _ in pair]
    for role, col in zip(pair, columns, strict=True):
        phase, imag, *mask = diagonal[role]
        assert (phase, imag) == (-1, 0)
        col[role][FINAL_PHASE, tuple(mask)] = ONE
    return columns


def initial_columns(pair, columns):
    zero_mask = (0,) * 17
    for r, col in zip(pair, columns, strict=True):
        assert col[r] == {(0, zero_mask): ONE}
        assert all(not cell for j, cell in enumerate(col) if j != r)


def sector_columns(columns, sign):
    # Reverse keys contain full exponent vectors, unlike the forward encoding.
    rows = {}
    for col, vectors in enumerate(columns):
        for role, vector in enumerate(vectors):
            for (phase, mask), (a, b) in vector.items():
                key = role, mask, phase & 1
                weights = rows.setdefault(key, [Q(0), Q(0), Q(0), Q(0)])
                factor = sign if phase >= 2 else 1
                weights[2 * col] += factor * a
                weights[2 * col + 1] += factor * b
    return rows


def gram(rows):
    # Hermitian entries A, D, Re(B), Im(B), with B = conjugate(col0) * col1.
    sectors = {}
    total = list(Z4)
    for (_, mask, parity), (a, b, c, d) in rows.items():
        parts = sectors.setdefault((mask, parity), list(Z4))
        terms = a*a + b*b, c*c + d*d, a*c + b*d, a*d - b*c
        for i, term in enumerate(terms):
            parts[i] += term
            total[i] += term
    return total, sectors


def rank_and_det(gram_data, allowed):
    total, parts = gram_data
    a, d, real, imag = (x-y for x, y in zip(total, parts.get(allowed, Z4), strict=True))
    determinant = a*d - real*real - imag*imag
    assert determinant >= 0
    if determinant:
        return 2, determinant
    return int(bool(a or d)), determinant


def complex_product(a, b, c, d):
    return a*c-b*d, a*d+b*c


def dot(row, kernel):
    a, b, c, d = row
    e, f, g, h = kernel
    p, q = complex_product(a, b, e, f)
    r, s = complex_product(c, d, g, h)
    return p+r, q+s


def mask_from_stages(stages):
    powers = [0] * 17
    for stage in stages:
        assert 1 <= stage <= 17
        powers[stage - 1] += 1
    return tuple(powers)


def source_key(encoded):
    role, stages, parity = encoded
    return role, mask_from_stages(stages), parity


def check_minor(record, matrix, rank, desired):
    assert rank == record["rank"] == 2
    first, second = map(source_key, record["minor_keys"])
    assert first != second and all(key[1:] != desired for key in (first, second))
    x, y = (tuple(matrix[key]) for key in (first, second))
    assert all(tuple(Q(v) for entry in row for v in entry) == actual
               for row, actual in zip(record["minor_rows"], (x, y), strict=True))
    d1 = complex_product(*x[:2], *y[2:])
    d2 = complex_product(*y[:2], *x[2:])
    assert tuple(a-b for a, b in zip(d1, d2, strict=True)) == tuple(map(Q, record["determinant"])) != ZERO


def check_kernel(record, matrix, rank, desired):
    assert rank == record["rank"] <= 1
    kernel = tuple(Q(x) for entry in record["kernel"] for x in entry)
    assert len(kernel) == 4 and any(kernel)
    assert all(dot(row, kernel) == ZERO for key, row in matrix.items() if key[1:] != desired)
    expected = {key: value for key, row in matrix.items()
                if key[1:] == desired and (value := dot(row, kernel)) != ZERO}
    actual = {source_key(key): tuple(map(Q, value)) for key, value in record["allowed_terms"]}
    assert expected and expected == actual


def load_lead(path, digest):
    raw = verify_hash(path, digest)
    lines = iter(raw.splitlines())
    start = loads(next(lines), object_pairs_hook=unique)
    assert start["status"] == "START" and start["total_cases"] == TOTAL and start["runner_cap_seconds"] == CAP
    records, final = {}, None
    expected = ((pair, cut, stage, parity) for pair, stages in PAIRS.items()
                for cut in range(END + 1) for stage in stages for parity in (0, 1))
    for line in lines:
        row = loads(line, object_pairs_hook=unique)
        status = row["status"]
        assert final is None
        if status in ("UNRESOLVED_CAP", "PASS_COMPLETE_GROUPED_RANK17_PREFIX_CENSUS"):
            final = row
            continue
        assert status in ("EXCLUDED_RANK_TWO", "NECESSARY_GATE_SURVIVES")
        key = tuple(row["roles"]), row["cut"], row["first_body_stage"], row["first_parity"]
        assert key == next(expected) and key not in records
        records[key] = row
    assert final is not None and final["completed"] == len(records) and final["remaining"] == TOTAL - len(records)
    assert (final["status"] == "PASS_COMPLETE_GROUPED_RANK17_PREFIX_CENSUS") == (len(records) == TOTAL)
    assert len(final["survivors"]) == sum(row["status"] == "NECESSARY_GATE_SURVIVES" for row in records.values())
    return records


def controls():
    allowed, foreign = mask_from_stages((7,)), mask_from_stages(())
    base = {(0, allowed): ONE, (0, foreign): ONE, (2, foreign): ONE}
    second = {(0, foreign): ONE}
    columns = [[base], [second]]
    desired = allowed, 0
    for sign in (1, -1):
        rows = sector_columns(columns, sign)
        assert rank_and_det(gram(rows), desired) == (1, Q(0))
    columns = [[base, {}], [second, {(0, foreign): ONE}]]
    assert rank_and_det(gram(sector_columns(columns, 1)), desired) == (2, Q(4))
    # A nonreal Gaussian determinant must survive norm squaring.
    rows = {(0, foreign, 0): (Q(1), Q(1), Q(0), Q(0)),
            (1, foreign, 0): (Q(0), Q(0), Q(2), Q(-1))}
    assert rank_and_det(gram(rows), desired) == (2, Q(10))
    return ["rank_one_with_q2_sector_change", "rank_two_foreign_direction", "gaussian_minor_norm"]


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("lead_receipt", type=Path)
    parser.add_argument("lead_sha256")
    args = parser.parse_args()
    started = perf_counter()
    counts, survivors = {}, []
    examined = checked = 0
    current = None
    history = sha256()

    def cap(_signal, _frame):
        emit({"status": "UNRESOLVED_CAP", "examined": examined, "lead_cases_checked": checked,
              "total": TOTAL, "first_unresolved": current, "counts": counts,
              "survivors": survivors, "seconds": perf_counter() - started})
        raise SystemExit(124)

    signal(SIGALRM, cap)
    alarm(CAP)
    pins = {key: verify_hash(args.root / key, value) for key, value in PINS.items()}
    caller = loads(pins["inputs/7113-CALLER.json"], object_pairs_hook=unique)
    kind, tape = caller["types"]["A"], caller["events"]
    assert (caller["stages"], kind["roles"], kind["offset"], len(kind["ports"]), len(tape)) == (
        17, 36, 0, 96, END)
    undo = run_path(str(args.root / "next-root28/7398/inputs/reverse.py"))["undo"]
    alpha = Q(kind["alpha2"])
    tests = controls()
    lead = load_lead(args.lead_receipt, args.lead_sha256)
    for pair, stages in PAIRS.items():
        mask = mask_from_stages(stages)
        assert all(kind["diagonal"][r] == [-1, 0, *mask] for r in pair)
        count = counts["/".join(map(str, pair))] = Counter()
        columns = event_columns(kind["diagonal"], pair)
        previous = None
        stage_masks = {stage: mask_from_stages((stage,)) for stage in stages}
        for cut in range(END, -1, -1):
            # Adjacent caller events commonly leave both sparse columns fixed.
            snapshot = tuple(tuple(tuple(cell.items()) for cell in col) for col in columns)
            if snapshot != previous:
                previous = snapshot
                matrices = {sign: sector_columns(columns, sign) for sign in (1, -1)}
                grams = {sign: gram(rows) for sign, rows in matrices.items()}
                ranks = {(stage, parity): {sign: rank_and_det(g, (stage_mask, parity))[0]
                                           for sign, g in grams.items()}
                         for stage, stage_mask in stage_masks.items() for parity in (0, 1)}
            for stage, stage_mask in stage_masks.items():
                for parity in (0, 1):
                    current = (pair, cut, stage, parity)
                    rank = ranks[stage, parity]
                    count[f'{rank[1]}/{rank[-1]}'] += 1
                    survived = max(rank.values()) < 2
                    desired = stage_mask, parity
                    lead_case = lead.get(current)
                    if lead_case is not None:
                        assert survived == (lead_case["status"] == "NECESSARY_GATE_SURVIVES"), current
                        if survived:
                            for sign in (1, -1):
                                check_kernel(lead_case["sectors"][str(sign)], matrices[sign], rank[sign], desired)
                        else:
                            sign = lead_case["sector"]
                            assert sign == (1 if rank[1] == 2 else -1)
                            check_minor(lead_case, matrices[sign], rank[sign], desired)
                        checked += 1
                    if survived:
                        survivors.append({"roles": pair, "cut": cut, "first_body_stage": stage,
                                          "first_parity": parity, "ranks": rank})
                    history.update(f'{pair}:{cut}:{stage}:{parity}:{rank[1]}:{rank[-1]}\n'.encode())
                    examined += 1
            if cut:
                for col in columns:
                    undo(col, tape[cut-1], alpha)
        initial_columns(pair, columns)
    assert examined == TOTAL and checked == len(lead)
    emit({"status": "PASS_INDEPENDENT_GROUPED_RANK17_REVERSE", "examined": examined, "unresolved": [],
          "lead_cases_checked": checked, "lead_sha256": args.lead_sha256,
          "controls": tests, "counts": counts, "survivors": survivors,
          "rank_transcript_sha256": history.hexdigest(), "pins": PINS, "cap_seconds": CAP,
          "seconds": perf_counter()-started})
    alarm(0)


if __name__ == "__main__":
    main()
