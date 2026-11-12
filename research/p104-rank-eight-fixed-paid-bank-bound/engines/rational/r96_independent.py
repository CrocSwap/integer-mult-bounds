"""Check four frozen R96 banks using independent exact dual-direction replay."""
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/GEOMETRY.json": "c6f9f018df8b58fcdf4f44356bd59bcac6d411b7845104ff4ad372ed4a95cfbd",
    "inputs/SELECTION.json": "b95765ffa0bd426b3dae781aaafc1c21e3b25bcebc71b71a3871824f9009fd5f",
    "inputs/SUFFIX.json": "77d78eb692bf6d3f0433730b48dbf8a0178c3288eeca961f94b2aaa6683eb59a",
    "inputs/PRICE.json": "a78be64c3e3ae8a0e532237c4dd3541aa9ad3fcbbc3c25d79c8a03fb7e07c525",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "reused/exact_six.py": "5bffcbbbdc5b0622e29fbc778540cc240b41e7d252e3e5c68d708d48808fcb5a",
    "reused/rolling_exterior.py": "ffc6dfa01554974f2b913b65c39230d3a7f7b6c06da1c940617b7938afe2b9c7",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
KEYS = [[45269, 242], [45276, 242], [45434, 242], [40242, 242]]
CAP = 4
SECONDS = 35
FIELDS = ("key", "owned", "pivots", "public")


def pinned(path, rel):
    data = path.read_bytes()
    if sha256(data).hexdigest() != PINS[rel]:
        raise ValueError(f"Changed input {rel}")
    return data


def selected_banks(selection, geometry, suffix, price):
    assert selection["case_cap"] == price["exact_cap"] == CAP
    assert selection["seconds_cap"] == price["exact_runner_seconds"] == SECONDS
    assert geometry["head"] == suffix["head"] == price["head"] == HEAD
    assert geometry["price_sha256"] == PINS["inputs/PRICE.json"]
    assert geometry["word_sha256"] == price["word_sha256"] == PINS["inputs/7334-WORD.json.gz"]
    assert geometry["eligible_bank_count"] == 326 and geometry["eligible_chart_count"] == 3
    assert not suffix["unvisited"]
    geo = {tuple(row["key"]): row for row in geometry["selected"]}
    mod = {tuple(row["key"]): row for row in suffix["rows"] if row["disposition"] == "rank drop"}
    assert len(geo) == 16 and len(mod) == 6
    selected = selection["selected"]
    assert [row["key"] for row in selected] == KEYS
    assert len(selection["unselected"]) == len({tuple(k) for k in selection["unselected"]}) == 312
    assert set(mod) - {tuple(k) for k in KEYS} == {(41740, 242), (45266, 242)}
    assert {tuple(k) for k in selection["unselected"]} == (
        {tuple(k) for k in geometry["unvisited_keys"]} | {(41740, 242), (45266, 242)})
    for row in selected:
        key = tuple(row["key"])
        assert row["disposition"] == "rank drop" and not row["owned"] and row["pivots"]
        assert all(row[k] == geo[key][k] == mod[key][k] for k in FIELDS)
    return selected, mod


def validate_cuts(word, rows, cohort):
    requests = {r["key"][0]: r for r in rows}
    n = word["public"]
    chart = word["initial"] + [None] * word["owned_fields"]
    assert len(word["program"]) == 76466 and len(requests) == CAP
    for t, (op, role, *args) in enumerate(word["program"]):
        if t in requests:
            row = requests.pop(t)
            label = row["key"][1]
            live = [i for i, loc in enumerate(chart) if loc == label]
            assert row["public"] == [i for i in live if i < n]
            assert row["owned"] == [i for i in live if i >= n] == []
            assert row["pivots"] == sorted(cohort.intersection(live))
        if op == "MOVE":
            chart[role] = args[1]
        elif op == "INIT":
            chart[role] = args[0]
        elif op == "CLEAR":
            chart[role] = None
    assert not requests and chart == word["final"] + [None] * word["owned_fields"]


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    assert __debug__
    for rel in ("reused/exact_six.py", "reused/rolling_exterior.py"):
        pinned(ROOT / rel, rel)
    engine = run_path(str(ROOT / "reused/exact_six.py"))
    checks = engine["checks"]()
    if args.controls_only:
        print(dumps(checks))
        return

    def stop(*_):
        raise TimeoutError("Hard 35-second exact cap")

    selected, results = [], []
    timeout = None
    signal(SIGALRM, stop)
    alarm(SECONDS)
    deadline = monotonic() + SECONDS - 2
    try:
        def read(name):
            rel = f"inputs/{name}.json"
            return loads(pinned(args.root / rel, rel), object_pairs_hook=engine["unique"])

        selection, geometry, suffix, price = (read(x) for x in ("SELECTION", "GEOMETRY", "SUFFIX", "PRICE"))
        selected, mod = selected_banks(selection, geometry, suffix, price)
        word = engine["checked"](args.root / "inputs/7334-WORD.json.gz", "word")
        cohort = set(price["cohort"])
        assert len(cohort) == len(price["cohort"]) == 15
        assert all((word["initial"][r], word["final"][r]) == (3, 245) for r in cohort)
        validate_cuts(word, selected, cohort)
        exact = engine["trace"](word, selected, deadline)
        for row, (p, s) in zip(selected, exact, strict=True):
            engine["stop_at"](deadline)
            pre_rank, pre = engine["pure"](p, cohort)
            suf_rank, suf = engine["pure"](s, cohort)
            mod_rank = mod[tuple(row["key"])]["exterior_rank"]
            assert pre_rank >= row["exterior_rank"] and suf_rank >= mod_rank
            a_count = sum(bool(v) for _, v in pre)
            b_count = sum(bool(v) for _, v in suf)
            pair = engine["pair"](pre, suf, deadline)
            status = ("exact_unit_pair" if pair else "no_nonzero_pure_prefix" if not a_count else
                      "no_nonzero_pure_suffix" if not b_count else "no_exact_unit_pair")
            record = {k: row[k] for k in FIELDS}
            record.update(prefix_rank=pre_rank, suffix_rank=suf_rank,
                          prefix_nullity=len(pre), suffix_nullity=len(suf),
                          nonzero_prefix_basis_images=a_count, nonzero_suffix_basis_images=b_count,
                          prefix_modular_rank=row["exterior_rank"], suffix_modular_rank=mod_rank,
                          status=status)
            if pair:
                assert engine["compose"](pair["a"], p) == pair["c"]
                assert engine["compose"](pair["b"], s) == pair["d"]
                assert pair["c"].keys() <= cohort and pair["d"].keys() <= cohort
                assert engine["dot"](pair["a"], pair["b"]) == engine["dot"](pair["c"], pair["d"]) == 1
                for name in ("a", "b"):
                    pair[name] = {row["public"][j]: v for j, v in pair[name].items()}
                record["physical_coefficient_preflight"] = engine["physical_screen"](pair, row["pivots"])
                record["witness"] = {name: {j: str(v) for j, v in vec.items()} for name, vec in pair.items()}
            results.append(record)
    except TimeoutError as error:
        timeout = str(error)
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD, input_sha256=PINS, exact_case_cap=CAP, runner_seconds_cap=SECONDS,
        controls=checks, timeout=timeout, results=results,
        selected_unvisited=[row["key"] for row in selected[len(results):]] if selected else KEYS,
        counts=dict(Counter(r["status"] for r in results)),
        modular_dual_drops_outside_exact_scope=2, unvisited_modular_representatives=310),
        indent=2, sort_keys=True))
    if timeout:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
