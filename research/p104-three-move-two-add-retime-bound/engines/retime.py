"""Check fixed-partner chronological placements for the priced triples."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PRICE = "d9074aad58d3ffdad995ba68b2ffa541ae2b7df833b757d8e1a9767118140f39"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def commute(add, event):
    _, dst, src, *_ = add
    op, other, *a = event
    if op == "MOVE":
        return True
    if op == "ADD":
        return src != other and dst != a[0]
    if op == "COPY":
        return not {dst, src}.intersection({other, a[0]})
    if op == "SCALE" and Fraction(a[0]) == 1:
        return True
    assert op in {"INIT", "CLEAR", "SCALE"}
    return other not in {dst, src}


def controls():
    add = ["ADD", 1, 2, "3", 3]
    assert commute(add, ["ADD", 1, 4, "-1", 3])
    assert not commute(add, ["ADD", 2, 4, "-1", 3])
    assert not commute(add, ["ADD", 4, 1, "-1", 3])
    assert not commute(add, ["COPY", 3, 1, "1", 3])
    assert commute(add, ["SCALE", 2, "1", 3])
    assert not commute(add, ["SCALE", 2, "2", 3])
    return ["commuting writes", "source and destination dependencies", "COPY guard", "nontrivial scale"]


def possible_interval(program, clock, other_clock, left, right):
    add = program[clock]
    lo, hi = left, right + 1
    for t in range(clock - 1, left - 1, -1):
        if t != other_clock and not commute(add, program[t]):
            lo = t + 1
            break
    for t in range(clock + 1, right + 1):
        if t != other_clock and not commute(add, program[t]):
            hi = t
            break
    return lo, hi


def positions(word, wanted):
    """Read the literal original pre-event chart of every scalar partner."""
    n = word["public"]
    state = word["initial"][:] + [None] * word["owned_fields"]
    chart_at = {r: [] for r in wanted}
    program = word["program"]
    for op, role, *a in program:
        for r in chart_at:
            chart_at[r].append(state[r])
        if op == "MOVE":
            before, after, owned = a
            assert state[role] == before and owned == (role >= n)
            state[role] = after
        elif op == "INIT":
            assert state[role] is None and role >= n
            state[role] = a[0]
        elif op == "CLEAR":
            assert state[role] == a[0] and role >= n
            state[role] = None
        else:
            assert state[role] == a[-1]
            if op in {"ADD", "COPY"}:
                assert state[a[0]] == state[role] and a[0] != role
            else:
                assert op == "SCALE"
    for r in chart_at:
        chart_at[r].append(state[r])
    assert state == word["final"] + [None] * word["owned_fields"]
    return chart_at


def main():
    assert __debug__
    helpers = run_path(str(ROOT / "lead/quote.py"))
    read, unique = helpers["authenticate"], helpers["unique"]
    price = loads(read("lead/PRICE.json", PRICE), object_pairs_hook=unique)
    deadline = monotonic() + price["runner_seconds"]
    raw = decompress(read("inputs/7334-WORD.json.gz", price["word_sha256"]))
    assert sha256(raw).hexdigest() == PAYLOAD
    word = loads(raw, object_pairs_hook=unique)
    program = word["program"]
    assert len(program) == price["event_cap"]
    candidates = price["candidates"]
    assert len(candidates) == 5

    def partner(role, event):
        dst, src = event[1:3]
        assert dst != src and role in (dst, src)
        return src if dst == role else dst

    wanted = {partner(row["role"], event) for row in candidates for _, event in row["contacts"]}
    chart_at = positions(word, wanted)
    visited, rows = 0, []
    for row in candidates:
        if monotonic() >= deadline:
            break
        role = row["role"]
        left, middle, right = row["clocks"]
        charts = row["charts"]
        for clock, a, b in zip(row["clocks"], charts[:-1], charts[1:], strict=True):
            assert program[clock] == ["MOVE", role, a, b, False]
        (c0, add0), (c1, add1) = row["contacts"]
        assert left < c0 < middle < c1 < right
        assert program[c0] == add0 and program[c1] == add1
        observed = [
            t for t in range(left + 1, right)
            if program[t][0] in {"ADD", "COPY"} and role in program[t][1:3]
            or program[t][0] == "SCALE" and program[t][1] == role
        ]
        assert observed == [c0, c1]
        intervals = [possible_interval(program, a, b, left, right) for a, b in [(c0, c1), (c1, c0)]]
        partners = [partner(role, e) for e in [add0, add1]]
        placements = []
        for clock in row["clocks"]:
            permitted = []
            for (lo, hi), peer in zip(intervals, partners, strict=True):
                visited += hi - lo + 1
                if visited > price["typed_cut_cap"] or monotonic() >= deadline:
                    break
                permitted.append([
                    t for t in range(lo, hi + 1)
                    if chart_at[peer][t] == (charts[0] if t <= clock else charts[-1])
                ])
            if len(permitted) != 2:
                break
            first, second = permitted
            witness = None
            if first:
                after = next((t for t in second if t >= first[0]), None)
                if after is not None:
                    witness = [first[0], after]
            placements.append({"retained_clock": clock, "slot_counts": list(map(len, permitted)), "witness": witness})
        if len(placements) != 3:
            break
        rows.append({"role": role, "clocks": row["clocks"], "partners": partners,
                     "commuting_intervals": intervals, "placements": placements})
    missing = [r["clocks"] for r in candidates[len(rows):]]
    print(dumps({"head": price["head"], "price": PRICE, "word": PAYLOAD, "rows": rows,
                 "typed_cut_checks": visited, "unvisited": missing, "controls": controls()},
                indent=2, sort_keys=True))
    if missing:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
