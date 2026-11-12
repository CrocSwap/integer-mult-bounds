"""Check one chart-242 split by exact guarded suffix span."""
from collections import defaultdict
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "price/PRICE-STOCK.json": "ac4207f548684468b9d09369f3a7866192ae9ffa5e3c3adb284b41bb3f61166d",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/donor_span.py": "4d5306e2c0b7e91c79d22c82e8e760aed2c311979298c558e631975d4d1ae5b1",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def checked(rel):
    raw = (ROOT / rel).read_bytes()
    if sha256(raw).hexdigest() != PINS[rel]:
        raise ValueError(f"changed dependency {rel}")
    return raw


def span(frame):
    out = {0}
    for axis in frame:
        assert axis not in out
        out |= {x ^ axis for x in out}
    return out


def reverse(word, requests, chart, engine, deadline):
    n, owned, tape = (word[k] for k in ("public", "owned_fields", "program"))
    size = n + owned
    active = word["final"] + [None] * owned
    cols = [{r: Fraction(1)} for r in range(size)]
    first = min(requests)
    snapshots = {}
    for t in range(len(tape), first - 1, -1):
        if (t % 128 == 0 or t in requests) and monotonic() >= deadline:
            raise TimeoutError("guarded suffix cap")
        if t in requests:
            bank = requests[t]
            assert [i for i, value in enumerate(active) if value == chart] == bank["public"]
            for role in bank["injection_targets"]:
                snapshots[t, role] = cols[role].copy()
        if t == first:
            break
        op, dest, *args = tape[t - 1]
        if op == "MOVE":
            before, after, owned_flag = args
            assert owned_flag == (dest >= n) and active[dest] == after
            active[dest] = before
        elif op == "CLEAR":
            assert dest >= n and active[dest] is None
            active[dest] = args[0]
            cols[dest] = {}
        elif op == "INIT":
            assert dest >= n and active[dest] == args[0]
            active[dest] = None
            cols[dest] = {}
        elif op == "SCALE":
            q, c = args
            assert active[dest] == c and Fraction(q)
            cols[dest] = {i: Fraction(q) * a for i, a in cols[dest].items()}
        else:
            assert op in ("ADD", "COPY")
            source, q, c = args
            assert source != dest and active[dest] == active[source] == c
            engine["axpy"](cols[source], cols[dest], Fraction(q))
            if op == "COPY":
                assert dest >= n
                cols[dest] = {size + t - 1: Fraction(1)}
    return snapshots, len(tape) - first


def controls(engine):
    toy = {
        "public": 1, "owned_fields": 1, "final": [0],
        "program": [["INIT", 1, 0], ["COPY", 1, 0, "1", 0], ["CLEAR", 1, 0]],
    }
    req = {1: {"public": [0, 1], "injection_targets": [0, 1]}}
    response, _ = reverse(toy, req, 0, engine, monotonic() + 1)
    assert response[1, 0] == {0: Fraction(1)} and response[1, 1] == {3: Fraction(1)}
    return engine["controls"]() + ["output-invisible perturbation retains a pre-COPY guard"]


def legal(value):
    return (value != 0 and (1125 * 2**25) % value.denominator == 0
            and abs(value.numerator).bit_length() <= 24 and abs(value) + 1 < 2**16)


def stop(*_):
    raise TimeoutError("35-second exact support cap")


def main():
    assert __debug__
    price = loads(checked("price/PRICE-STOCK.json"), object_pairs_hook=unique)
    checked("inputs/donor_span.py")
    engine = run_path(str(ROOT / "inputs/donor_span.py"))
    tests = controls(engine)
    signal(SIGALRM, stop)
    alarm(35)
    deadline = monotonic() + 32
    outcome, reason = {}, None
    try:
        payload = decompress(checked("inputs/7334-WORD.json.gz"))
        assert sha256(payload).hexdigest() == PAYLOAD
        word = loads(payload, object_pairs_hook=unique)
        n = word["public"]
        limits = price["limits"]
        assert len(word["program"]) == limits["events_per_pass"] == 76466
        cut, chart, pivot = (price["retirement"][k] for k in ("cut", "chart", "pivot"))
        cohort = set(price["cohort"])
        assert (cut, chart, pivot) == (41740, 242, 1123) and pivot in cohort and len(cohort) == 15
        low, mid, high = (span(word["frames"][f]) for f in (3, chart, 245))
        assert low < mid < high and (len(low), len(mid), len(high)) == (1, 16, 256)
        assert all([word["initial"][r], word["final"][r]] == [3, 245] for r in cohort)
        banks = {b["cut"]: b for b in price["injection_banks"]}
        assert len(banks) == limits["banks"] == 19 and min(banks) == cut
        assert all(r < n and r not in price["protected"] for b in banks.values() for r in b["injection_targets"])
        _, prefix = engine["snapshot"](word, defaultdict(set), {cut: {pivot}}, deadline)
        if (cut, pivot) not in prefix:
            raise TimeoutError("retirement prefix cap")
        assert prefix[cut, pivot] == {pivot: Fraction(1)}
        responses, suffix_events = reverse(word, banks, chart, engine, deadline)
        keys = sorted(responses)
        assert len(keys) == limits["injection_keys"] == 354
        exterior = {i: {k: q for k, q in responses[key].items() if k not in cohort or k == pivot}
                    for i, key in enumerate(keys)}
        certificate = engine["solve"]({pivot: Fraction(1)}, exterior, deadline)
        if certificate is None:
            raise TimeoutError("exact projected span cap")
        match = certificate["matching_coefficients"]
        status, correction, injections = "no guarded temporal span", {}, []
        if match is not None:
            for i, coefficient in sorted((int(i), Fraction(q)) for i, q in match.items()):
                t, role = keys[i]
                engine["axpy"](correction, responses[t, role], coefficient)
                injections.append([t, role, str(coefficient)])
            assert set(correction) <= cohort and correction[pivot] == 1
            scalars = [Fraction(q) for _, _, q in injections]
            scalars += [q for r, q in correction.items() if r != pivot]
            status = ("exact coefficient survivor" if len(injections) <= limits["max_literal_injections"]
                      and all(legal(q) for q in scalars) else "coefficient gate unresolved")
        outcome = {
            "status": status, "key": [cut, chart, pivot], "banks": len(banks), "injection_keys": len(keys),
            "prefix_events": cut, "suffix_events": suffix_events, "prefix": {str(pivot): "1"},
            "full_projection": certificate, "injections": injections,
            "correction": {i: str(q) for i, q in correction.items()},
            "copy_guards": len({k for v in responses.values() for k in v if k >= n + word["owned_fields"]}),
        }
    except TimeoutError as error:
        reason = str(error)
    finally:
        alarm(0)
    print(dumps({
        "pins": PINS, "head": price["head"], "caller": price["caller"], "controls": tests,
        "timeout": reason, "unresolved_frozen_form": not outcome or outcome["status"] == "coefficient gate unresolved",
        **outcome,
    }, indent=2, sort_keys=True))
    return 124 if reason else 0


if __name__ == "__main__":
    raise SystemExit(main())
