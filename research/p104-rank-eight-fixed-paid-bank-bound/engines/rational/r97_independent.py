"""Independently replay the frozen R97 cohort cuts using exact dual-direction traces."""
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
KEYS = ((41740, 242), (45266, 242))
FOLLOWUP_KEYS = ((40243, 242), (45675, 1091))
FOLLOWUP_SHA = "53f3a3b08bd6e97514e7077e7c0b55c9d272b0527f3a1b0e415f0924514fddf1"
SECONDS = 35
CASE_CAP = 4
PINS = {
    "inputs/REMAINING.json": "3597499663a57702856945e91214a65e1d0f94db8643b93c0234c2bbf9291b1a",
    "inputs/PREFIX.json": "45b6c8992dcff04b7252dfec809fc64812b86f094531ed3964ff967408057ed2",
    "inputs/SUFFIX.json": "77d78eb692bf6d3f0433730b48dbf8a0178c3288eeca961f94b2aaa6683eb59a",
    "inputs/PRICE.json": "a78be64c3e3ae8a0e532237c4dd3541aa9ad3fcbbc3c25d79c8a03fb7e07c525",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "reused/exact_six.py": "5bffcbbbdc5b0622e29fbc778540cc240b41e7d252e3e5c68d708d48808fcb5a",
    "reused/rolling_exterior.py": "ffc6dfa01554974f2b913b65c39230d3a7f7b6c06da1c940617b7938afe2b9c7",
}
BANK = ("key", "public", "owned", "pivots")


def checked(path, expected):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != expected:
        raise ValueError(f"Changed input {path.name}")
    return raw


def index(rows):
    out = {tuple(r["key"]): r for r in rows}
    assert len(out) == len(rows)
    return out


def inherited_keys(remaining, prefix, suffix):
    assert remaining["head"] == prefix["head"] == suffix["head"] == HEAD
    assert remaining["input_sha256"]["lead/RESULT.json"] == PINS["inputs/PREFIX.json"]
    assert remaining["input_sha256"]["lead/SUFFIX.json"] == PINS["inputs/SUFFIX.json"]
    assert [tuple(k) for k in remaining["dual_drops_requiring_rational"]] == list(KEYS)
    assert remaining["next_exact_cases"] == CASE_CAP and remaining["next_exact_runner_seconds"] == SECONDS
    assert len(remaining["unvisited_prefix"]) == 310 and remaining["unresolved"] == 312
    p, s = index(prefix["rows"]), index(suffix["rows"])
    out = []
    for key in KEYS:
        a, b = p[key], s[key]
        assert all(a[k] == b[k] for k in BANK)
        assert a["disposition"] == b["disposition"] == "rank drop" and not a["owned"]
        out.append({k: a[k] for k in BANK} | dict(
            prefix_modular_rank=a["exterior_rank"], suffix_modular_rank=b["exterior_rank"]))
    return out


def cut_check(word, rows, cohort):
    def span(basis):
        seen = {0}
        for v in basis:
            assert v not in seen
            seen |= {u ^ v for u in seen}
        return seen

    frames = word["frames"]
    lo, hi = span(frames[3]), span(frames[245])
    requested = {}
    for row in rows:
        t, label = row["key"]
        assert len(frames[label]) == 4 and lo < span(frames[label]) < hi
        requested.setdefault(t, []).append(row)
    n = word["public"]
    chart = word["initial"] + [None] * word["owned_fields"]
    for t, (op, dst, *args) in enumerate(word["program"]):
        for row in requested.pop(t, ()):
            _, target = row["key"]
            live = [r for r, label in enumerate(chart) if label == target]
            assert row["public"] == [r for r in live if r < n]
            assert row["owned"] == [r for r in live if r >= n]
            assert row["pivots"] == sorted(cohort.intersection(live)) and row["pivots"]
        if op == "MOVE":
            chart[dst] = args[1]
        elif op == "INIT":
            chart[dst] = args[0]
        elif op == "CLEAR":
            chart[dst] = None
    assert not requested and chart == word["final"] + [None] * word["owned_fields"]


def rational_row(vec):
    return {str(k): str(v) for k, v in sorted(vec.items())}


def evaluate(exact, row, prefix, suffix, cohort, deadline):
    a_rank, a_basis = exact["pure"](prefix, cohort)
    b_rank, b_basis = exact["pure"](suffix, cohort)
    assert a_rank >= row.get("prefix_modular_rank", 0)
    assert b_rank >= row.get("suffix_modular_rank", 0)
    a_images = sum(bool(c) for _, c in a_basis)
    b_images = sum(bool(d) for _, d in b_basis)
    pair = exact["pair"](a_basis, b_basis, deadline)
    status = ("exact_unit_pair" if pair else "no_nonzero_pure_prefix" if not a_images else
              "no_nonzero_pure_suffix" if not b_images else "no_exact_unit_pair")
    a_form = [[str(exact["dot"](a, b)) for b, _ in b_basis] for a, _ in a_basis]
    c_form = [[str(exact["dot"](c, d)) for _, d in b_basis] for _, c in a_basis]
    if len(a_basis) == len(b_basis) == 1:
        assert bool(pair) == (a_form[0][0] != "0" and a_form == c_form)
    pub = row["public"]

    def at_cut(weights):
        return rational_row({pub[j]: value for j, value in weights.items()})

    entry = row | dict(status=status, prefix_rank=a_rank, suffix_rank=b_rank,
        prefix_nullity=len(a_basis), suffix_nullity=len(b_basis),
        nonzero_prefix_basis_images=a_images, nonzero_suffix_basis_images=b_images,
        prefix_rows=[rational_row(vec) for vec in prefix],
        suffix_columns=[rational_row(vec) for vec in suffix],
        prefix_pure_basis=[dict(a=at_cut(a), c=rational_row(c)) for a, c in a_basis],
        suffix_pure_basis=[dict(b=at_cut(b), d=rational_row(d)) for b, d in b_basis],
        cut_pairing_matrix=a_form, endpoint_pairing_matrix=c_form)
    if pair:
        assert exact["compose"](pair["a"], prefix) == pair["c"]
        assert exact["compose"](pair["b"], suffix) == pair["d"]
        assert pair["c"].keys() <= cohort and pair["d"].keys() <= cohort
        assert exact["dot"](pair["a"], pair["b"]) == exact["dot"](pair["c"], pair["d"]) == 1
        pair["a"] = {pub[j]: v for j, v in pair["a"].items()}
        pair["b"] = {pub[j]: v for j, v in pair["b"].items()}
        entry["physical_coefficient_preflight"] = exact["physical_screen"](pair, row["pivots"])
        entry["witness"] = {k: rational_row(v) for k, v in pair.items()}
    return entry


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--followup", type=Path)
    parser.add_argument("--followup-sha")
    parser.add_argument("--only-followup", action="store_true")
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    if bool(args.followup) != bool(args.followup_sha) or args.only_followup and not args.followup:
        parser.error("Use a pinned follow-up file and its exact SHA together")
    for rel in ("reused/exact_six.py", "reused/rolling_exterior.py"):
        checked(ROOT / rel, PINS[rel])
    exact = run_path(str(ROOT / "reused/exact_six.py"))
    checks = exact["checks"]()
    if args.controls_only:
        print(dumps(checks))
        return

    def read(name):
        rel = f"inputs/{name}.json"
        return loads(checked(args.root / rel, PINS[rel]), object_pairs_hook=exact["unique"])

    def stop(*_):
        raise TimeoutError("Hard 35-second exact cap")

    selected, results, fail = [], [], None
    input_pins = dict(PINS)
    signal(SIGALRM, stop)
    phase_seconds = SECONDS - int(args.only_followup)
    alarm(phase_seconds)
    deadline = monotonic() + phase_seconds - 2
    try:
        remaining, prefix, suffix, price = (read(k) for k in ("REMAINING", "PREFIX", "SUFFIX", "PRICE"))
        assert price["head"] == HEAD and price["word_sha256"] == PINS["inputs/7334-WORD.json.gz"]
        inherited = inherited_keys(remaining, prefix, suffix)
        selected = [] if args.only_followup else inherited
        if args.followup:
            assert args.followup_sha == FOLLOWUP_SHA
            raw = checked(args.followup, FOLLOWUP_SHA)
            followup = loads(raw, object_pairs_hook=exact["unique"])
            assert followup["inputs"]["input/lead/SUFFIX.json"] == PINS["inputs/SUFFIX.json"]
            assert len(followup["selected"]) == CASE_CAP and len(followup["unselected"]) == 29
            first, added = followup["selected"][:len(KEYS)], followup["selected"][len(KEYS):]
            for saved, previous in zip(first, inherited, strict=True):
                assert all(saved[k] == previous[k] for k in BANK)
            assert tuple(tuple(r["key"]) for r in added) == FOLLOWUP_KEYS
            assert index(added).keys() <= {tuple(k) for k in remaining["unvisited_prefix"]}
            selected = selected + added
            input_pins["inputs/R97-SELECTION.json"] = FOLLOWUP_SHA
        assert 0 < len(selected) <= CASE_CAP
        word = exact["checked"](args.root / "inputs/7334-WORD.json.gz", "word")
        cohort = set(price["cohort"])
        assert len(cohort) == 15 and len(word["program"]) == 76466
        assert all((word["initial"][r], word["final"][r]) == (3, 245) for r in cohort)
        cut_check(word, selected, cohort)
        for row, (p, s) in zip(selected, exact["trace"](word, selected, deadline), strict=True):
            exact["stop_at"](deadline)
            results.append(evaluate(exact, row, p, s, cohort, deadline))
    except TimeoutError as err:
        fail = str(err)
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD, input_sha256=input_pins, case_cap=CASE_CAP,
        runner_seconds_cap=SECONDS, controls=checks, results=results,
        selected_unvisited=[row["key"] for row in selected[len(results):]],
        counts=dict(Counter(row["status"] for row in results)), timeout=fail),
        indent=2, sort_keys=True))
    if fail:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
