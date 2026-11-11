"""Recount the pinned signed caller and apply the fixed-output census to both words.

Run with Python 3.12 and a Git repository containing the named commits. The
Clifford tableau classifier is reused from main. Scalar replay, elimination,
invoice reconstruction, and directed price arithmetic are local to this check.
"""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
from subprocess import check_output


BASE = "e54523517d0f03e58352e647c403a5af3e525a57"
BEFORE = "e3f8d39c43b07063dfc5b800f71c5d21015259e6"
AFTER = "215f67247f395c0e15f5ea3980f6a3e4aed155af"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PACKAGE = "research/p104-two-cut-funded-split"
PRIME = 65521


def git_bytes(repo, commit, path):
    return check_output(["git", "-C", str(repo), "show", f"{commit}:{path}"])


def span(vectors):
    members = {0}
    for value in vectors:
        members.update(value ^ x for x in tuple(members))
    return frozenset(members)


parse = cache(Fraction)


def replay(word, spaces):
    n = word["public"]
    chart = word["initial"] + [None] * word["owned_fields"]
    rows = [{r: Fraction(1)} for r in range(n)] + [None] * word["owned_fields"]
    last_touch = {}
    paid, moves, copies = Counter(), [], []
    contact_free = opens = closes = 0
    for t, (op, r, *args) in enumerate(word["program"]):
        touched = (r,)
        if op == "INIT":
            assert r >= n and chart[r] is None
            chart[r], rows[r] = args[0], {}
            opens += 1
        elif op == "CLEAR":
            assert r >= n and chart[r] == args[0] and rows[r] is not None
            chart[r], rows[r] = None, None
            closes += 1
        elif op == "MOVE":
            source, target, owned = args
            assert chart[r] == source and rows[r] is not None and owned == (r >= n)
            assert spaces[source] < spaces[target] or owned and spaces[target] < spaces[source]
            rank = abs(len(word["frames"][source]) - len(word["frames"][target]))
            paid[rank] += 1
            contact_free += last_touch.get(r) == "MOVE"
            moves.append((t, source, target, rows[r]))
            chart[r] = target
        elif op == "SCALE":
            coefficient, frame = args
            assert chart[r] == frame and rows[r] is not None
            rows[r] = {i: value for i, x in rows[r].items() if (value := parse(coefficient) * x)}
        else:
            assert op in ("ADD", "COPY")
            source, coefficient, frame = args
            assert chart[r] == chart[source] == frame and rows[r] is not None and rows[source] is not None
            touched = (r, source)
            if op == "COPY":
                if rows[r]:
                    raise ValueError(f"Dirty COPY destination at event {t}")
                copies.append((t, r, source))
            result = rows[r].copy()
            for i, x in rows[source].items():
                value = result.get(i, 0) + parse(coefficient) * x
                if value:
                    result[i] = value
                else:
                    result.pop(i, None)
            rows[r] = result
        last_touch.update((role, op) for role in touched)
    assert chart == word["final"] + [None] * word["owned_fields"]
    assert rows[n:] == [None] * word["owned_fields"] and opens == closes and len(copies) == 1
    return rows[:n], paid, moves, copies[0], contact_free, opens


@cache
def reduce_mod(x):
    return x.numerator * pow(x.denominator, -1, PRIME) % PRIME


def rank(rows, modular):
    basis = {}
    for row in rows:
        vector = {i: y for i, x in row.items() if (y := reduce_mod(x) if modular else x)}
        while vector:
            lead = min(vector)
            if lead not in basis:
                basis[lead] = vector
                break
            pivot = basis[lead]
            multiple = vector[lead] * pow(pivot[lead], -1, PRIME) if modular else vector[lead] / pivot[lead]
            for i, x in pivot.items():
                value = vector.get(i, 0) - multiple * x
                if modular:
                    value %= PRIME
                if value:
                    vector[i] = value
                else:
                    vector.pop(i, None)
    return len(basis)


def census(moves, source, frames):
    interpreter = {"__name__": "pinned_clifford"}
    exec(compile(source, "pinned native_verify.py", "exec"), interpreter)
    circuits = [interpreter["frame"](frame, 9) for frame in frames]
    adjoints = [interpreter["adjoint"](circuit) for circuit in circuits]
    tableau = interpreter["tableau"]
    cosets = [span(x | z << 9 for x, z, _ in tableau(inv)[9:]) for inv in adjoints]

    @cache
    def quotient(f, g):
        return tableau(adjoints[f] + circuits[g])

    signed, targets = defaultdict(list), defaultdict(list)
    for t, f, g, row in moves:
        signed[quotient(f, g)].append((t, row))
        targets[cosets[g]].append((t, row))
    result = {}
    for label, groups in (("signed_quotients", signed), ("target_cosets", targets)):
        modular_full = 0
        exact_defects = []
        for group in groups.values():
            vectors = [row for _, row in group]
            if rank(vectors, modular=True) == len(vectors):
                modular_full += 1
                continue
            exact = rank(vectors, modular=False)
            if exact != len(vectors):
                exact_defects.append({"size": len(vectors), "rank": exact, "events": [t for t, _ in group]})
        result[label] = {"classes": len(groups), "maximum_size": max(map(len, groups.values())),
                         "modular_full_classes": modular_full, "exact_defects": exact_defects}
    return result


def invoice(word, native_paid, caller):
    live = word["live"]
    main = {*live, *(r + 112 for r in live), *word["hosted"]["X2"], *word["hosted"]["Y2"]}
    assert len(main) == 400
    stages = [event[1] for event in caller["events"] if event[0] == "J"]
    assert stages == list(range(1, 18)) == list(range(1, caller["stages"] + 1))
    productive = Counter()
    for r, (f, g) in enumerate(zip(word["initial"], word["final"], strict=True)):
        if r not in main:
            difference = len(word["frames"][g]) - len(word["frames"][f])
            assert difference > 0
            productive[difference] += len(stages)
    for spec in caller["types"].values():
        ports = len(spec["ports"])
        for sign, head, *bits in spec["diagonal"]:
            assert (sign, head, len(bits)) == (-1, 0, len(stages)) and set(bits) <= {0, 1}
            productive[1 + 8 * sum(bits)] += ports
    paid = Counter({r: count * len(stages) for r, count in native_paid.items()})
    for event in caller["events"]:
        if event[0] == "J":
            continue
        kind, op, _, *args = event
        ports = len(caller["types"][kind]["ports"])
        if op == "QUERY":
            paid[1] += ports
        elif op in ("IDLE_ONE", "IDLE_ODD"):
            paid[8 * len(args[0]) + int(op == "IDLE_ODD")] += ports
    return productive, paid


def log_series(value):
    # With 1 <= value <= 2, bound the remaining atanh series by a geometric tail.
    x = (value - 1) / (value + 1)
    square = x * x
    term, total = x, Fraction(0)
    for j in range(64):
        total += term / (2 * j + 1)
        term *= square
    return 2 * total, 2 * (total + term / (129 * (1 - square)))


@cache
def log_bounds(n):
    exponent = n.bit_length() - 1
    a, b = log_series(Fraction(n, 2**exponent))
    c, d = log_series(Fraction(2))
    scale = 10**49
    return Fraction((a + exponent * c) * scale // 1, scale), Fraction(-(-(b + exponent * d) * scale // 1), scale)


def exp_bounds(x):
    # Alternating Taylor terms decrease for 0 <= x < 1. Degrees 31 and 32 enclose exp(-x).
    assert 0 <= x < 1
    value = term = Fraction(1)
    for degree in range(1, 32):
        term *= -x / degree
        value += term
    return value, value - term * x / 32


def moment(signed, k):
    lo = hi = Fraction(0)
    for r, count in signed.items():
        a, b = log_bounds(r)
        lower = r * exp_bounds(k * b)[0]
        upper = r * exp_bounds(k * a)[1]
        lo += count * (lower if count >= 0 else upper)
        hi += count * (upper if count >= 0 else lower)
    return lo, hi


def interval_text(bounds, digits=34):
    scale = 10**digits
    integers = (bounds[0] * scale // 1, -(-bounds[1] * scale // 1))
    return [f"{'-' if value < 0 else ''}{abs(value) // scale}.{abs(value) % scale:0{digits}d}" for value in integers]


def main(repo):
    raw = {
        "before": git_bytes(repo, BEFORE, "research/p104-rank8-exit-funded-split/WORD.json.gz"),
        "after": git_bytes(repo, AFTER, f"{PACKAGE}/WORD.json.gz"),
        "caller": git_bytes(repo, CALLER, "research/signed-caller-8x9/expected/ODD-TYPE-AB-CALLER.json"),
        "tableau": git_bytes(repo, BASE, "research/shared-wire-split-composition/frozen/native_verify.py"),
    }
    assert raw["before"] == git_bytes(repo, AFTER, f"{PACKAGE}/reference/WORD.json.gz")
    assert sha256(raw["caller"]).hexdigest() == "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
    assert sha256(raw["tableau"]).hexdigest() == "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38"
    before, after = [json.loads(gzip.decompress(raw[name])) for name in ("before", "after")]
    assert sha256(gzip.decompress(raw["after"])).hexdigest() == "56e1a5e60cecf14991b3169b4575f0b7388d48fa39f261d7a20c7627a8d9e540"
    assert before["frames"] == after["frames"] and before["initial"] == after["initial"][:-2]
    spaces = [span(frame) for frame in before["frames"]]
    assert all(len(s) == 2**len(f) for s, f in zip(spaces, before["frames"], strict=True))
    old, new = replay(before, spaces), replay(after, spaces)
    assert after["public"] == before["public"] + 2
    assert new[0] == old[0] + [{i: Fraction(1)} for i in range(before["public"], after["public"])]
    t, dst, src = new[3]
    dirty = dict(after, program=after["program"][:t] + [["ADD", dst, src, "1", after["program"][t][-1]]] + after["program"][t:])
    try:
        replay(dirty, spaces)
    except ValueError as error:
        assert str(error) == f"Dirty COPY destination at event {t + 1}"
    else:
        raise AssertionError("Dirty COPY control was accepted")
    caller = json.loads(raw["caller"])
    invoices = [invoice(word, result[1], caller) for word, result in ((before, old), (after, new))]
    receipt = json.loads(git_bytes(repo, AFTER, f"{PACKAGE}/RESULT.json"))["price"]
    signed = []
    for label, (productive, paid) in zip(("before", "after"), invoices, strict=True):
        expected = receipt[label]
        assert {str(r): count for r, count in productive.items()} == expected["T"]
        assert {str(r): count for r, count in paid.items()} == expected["P"]
        delta = productive.copy()
        delta.subtract(paid)
        assert sum(r * count for r, count in delta.items()) == expected["S"] == 1424
        signed.append(delta)
    claim = parse(receipt["gate"]["claim"])
    tested = parse(receipt["gate"]["tested"])
    candidate_bracket = (parse("0.0036453723678327048"), parse("0.0036453723678327049"))
    old_at_claim = moment(signed[0], claim)
    new_at_test = moment(signed[1], tested)
    at_low, at_high = [moment(signed[1], k) for k in candidate_bracket]
    assert old_at_claim[1] < 0 < new_at_test[0] and at_high[1] < 0 < at_low[0]
    rank_control = [{0: Fraction(1)}, {1: Fraction(1)}, {0: Fraction(2), 1: Fraction(3)}]
    assert rank(rank_control[:2], True) == rank(rank_control, True) == rank(rank_control, False) == 2
    stock = [census(result[2], raw["tableau"], before["frames"]) for result in (old, new)]
    assert stock[0]["signed_quotients"]["modular_full_classes"] == 2229
    assert stock[0]["target_cosets"]["modular_full_classes"] == 978
    return {
        "heads": {"base": BASE, "before": BEFORE, "after": AFTER, "caller": CALLER},
        "sha256": {name: sha256(content).hexdigest() for name, content in raw.items()},
        "scalar_check": {"old_output_rows_match": before["public"], "new_identity_rows": 2,
                         "dirty_copy_rejected": True, "closed_lifetimes_after": new[5]},
        "census": {"prime": PRIME, "before": stock[0], "after": stock[1],
                   "moves": [len(old[2]), len(new[2])], "contact_free_pairs": [old[4], new[4]]},
        "invoice": {label: {"productive": sum(t.values()), "paid": sum(p.values()), "T": dict(t), "P": dict(p)}
                    for label, (t, p) in zip(("before", "after"), invoices, strict=True)},
        "price": {"claim": str(claim), "tested": str(tested),
                  "old_at_claim": interval_text(old_at_claim), "new_at_test": interval_text(new_at_test),
                  "candidate_crossing_bracket": interval_text(candidate_bracket, 22),
                  "at_lower_endpoint": interval_text(at_low), "at_upper_endpoint": interval_text(at_high)},
    }


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    print(json.dumps(main(parser.parse_args().repo), indent=2, sort_keys=True))
