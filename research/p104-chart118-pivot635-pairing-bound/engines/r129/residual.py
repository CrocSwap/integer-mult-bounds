"""Rational support for the 72 retained exact chart-118 cuts, one pass per side."""
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
FROZEN = "lead/FROZEN.json"
ENGINE = "inputs/R128-two_keys.py"
CAP, SECONDS = 72, 35


def read(relative, expected):
    raw = (ROOT / relative).read_bytes()
    if sha256(raw).hexdigest() != expected:
        raise ValueError(f"changed dependency {relative}")
    return raw


def main():
    engine_pin = "b6d97bbe22649b18e745ae70cba60542beba1d91e34f9f827b28fe29854265f2"
    frozen_pin = "4efa924dc8768c3dfcdaae8d7dc39ca5fbc899d5fe820e782fd5f78d0851f0f6"
    read(ENGINE, engine_pin)
    core = run_path(str(ROOT / ENGINE))
    unique, check_time = core["unique"], core["check_time"]
    limits = {"cases": CAP, "runner_seconds": SECONDS}
    plan = loads(read(FROZEN, frozen_pin), object_pairs_hook=unique)
    assert __debug__ and plan["limits"] == limits
    assert Q(plan["pricing"]["complete_probe"][0]) > 0
    assert Q(plan["pricing"]["extra_rank_one_at_crossing_lower"][1]) < 0
    keys = plan["cases"]
    assert len(keys) == len({tuple(x["key"]) for x in keys}) == CAP
    assert all(r["key"][1] == 118 and not r["owned"] and 635 in r["pivots"] for r in keys)
    assert len({tuple(r["public"]) for r in keys}) == 1
    assert all(r["status"] == "no exact unit pairing" for r in plan["known_exact_controls"])
    path_pins = {name: core["PINS"][name] for name in
                 (core["WORD"], core["PAIR"], core["TRACE"], core["HISTORY"])}
    raw = {name: read(name, pin) for name, pin in path_pins.items()}
    solve, rank = (run_path(str(ROOT / key)) for key in (core["PAIR"], core["TRACE"]))
    earlier = loads(raw[core["HISTORY"]], object_pairs_hook=unique)
    tests = core["controls"](solve, earlier)
    result = dict(head=plan["head"], caller=plan["caller"], cap=limits,
        pins={FROZEN:frozen_pin, ENGINE:engine_pin, **path_pins}, results=[],
        controls=tests, known_exact_keys=[r["key"] for r in plan["known_exact_controls"]],
        identical_role_sets_do_not_imply_equivalence=True, timeout=None,
        scope="Frozen 72 residual keys, exact rational pairing, optimistic relaxed suffix guard")

    def stop(*_):
        raise TimeoutError("35-second hard limit")

    signal(SIGALRM, stop)
    alarm(SECONDS)
    deadline = monotonic() + 32
    try:
        payload = decompress(raw[core["WORD"]])
        if sha256(payload).hexdigest() != core["PAYLOAD"]:
            raise ValueError("changed literal payload")
        word = loads(payload, object_pairs_hook=unique)
        cohort, _ = solve["initial_groups"](word)
        assert cohort == set(plan["endpoint_cohort"]) and len(cohort) == 615
        banks, result["ranks"] = core["geometry"](word, keys, deadline)
        forward = rank["side"](word, banks, cohort, deadline, False)
        reverse = rank["side"](word, banks, cohort, deadline, True)
        for row in keys:
            check_time(deadline)
            t = row["key"][0]
            if t not in forward or t not in reverse:
                raise TimeoutError(f"rational sides unavailable at {t}")
            result["results"].append(core["classify"](row, forward, reverse, solve, rank, deadline))
    except (TimeoutError, solve["Capped"]) as error:
        result["timeout"] = str(error) or "paired-support cap"
    finally:
        alarm(0)
    result["counts"] = Counter(r["status"] for r in result["results"])
    result["unvisited"] = [r["key"] for r in keys[len(result["results"]):]]
    result["provisional"] = [r["key"] for r in result["results"] if r["witness"]]
    print(dumps(result, sort_keys=True, indent=2))
    return 124 if result["timeout"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
