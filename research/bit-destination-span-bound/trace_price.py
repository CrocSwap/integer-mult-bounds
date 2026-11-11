"""Whole signed invoice and exact bitmask scalar replay from Round 29."""

from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORD = "research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz"
INVOICE = "research/paired-query-only-bit/EFREE-RESULT.json"
SCALE = 10**49


def read_inputs(root):
    pins = {}
    sources = HERE / "SOURCES.tsv"
    for line in sources.read_text().splitlines():
        key, expected, _ = line.split("\t")
        path = Path(key)
        if path.is_absolute() or ".." in path.parts or key in pins:
            raise ValueError(f"invalid source key {key}")
        contents = (root / path).read_bytes()
        if sha256(contents).hexdigest() != expected:
            raise ValueError(f"changed source {key}")
        pins[key] = expected
    return (
        json.loads(gzip.decompress((root / WORD).read_bytes())),
        json.loads((root / INVOICE).read_bytes()),
        pins,
    )


def walk(word, observe_move=None):
    """Track logical owner identities through transparent physical SWAPs."""
    public = word["public"]
    slots = [(j, f, 1 << j) for j, f in enumerate(word["start"])]
    slots.extend((None, None, 0) for _ in range(word["owned_fields"]))
    history = defaultdict(list)
    moves = {}
    ownership = Counter()
    for clock, (op, i, *args) in enumerate(word["program"]):
        owner, frame, row = slots[i]
        if op == "SWAP":
            (j,) = args
            slots[i], slots[j] = slots[j], slots[i]
            continue
        if op == "INIT":
            (f,) = args
            assert i >= public and slots[i] == (None, None, 0)
            slots[i] = (public + clock, f, 0)
            ownership["init"] += 1
            continue
        assert owner is not None
        history[owner].append((clock, op))
        if op == "MOVE":
            src, dst = args
            assert src == frame and src != dst
            if observe_move is not None:
                observe_move(clock, i, src, dst, row, slots)
            moves[clock] = (src, dst, row)
            slots[i] = (owner, dst, row)
        elif op == "ADD":
            j, f = args
            other, other_frame, other_row = slots[j]
            assert other is not None and frame == f == other_frame
            if other != owner:
                history[other].append((clock, op))
            slots[i] = (owner, frame, row ^ other_row)
        else:
            assert op == "CLEAR" and i >= public and args == [frame]
            ownership["clear"] += 1
            slots[i] = (None, None, 0)
    assert [x[1] for x in slots] == word["final"] + [None] * word["owned_fields"]
    expected = [1 << j if j < public else 0 for j in range(len(slots))]
    for j in range(111):
        expected[j + 111] ^= 1 << j
    assert [x[2] for x in slots] == expected

    runs = []
    for records in history.values():
        chain = []
        for clock, op in records:
            if op == "MOVE":
                chain.append(clock)
            elif chain:
                runs.append(tuple(chain))
                chain.clear()
        if chain:
            runs.append(tuple(chain))
    runs.sort()
    covered = [t for run in runs for t in run]
    assert len(covered) == len(set(covered)) == len(moves) and set(covered) == set(moves)
    assert all(moves[i][1] == moves[j][0] for run in runs for i, j in zip(run, run[1:]))
    return moves, runs, ownership


def rounded(x, upper):
    scaled = SCALE*x
    if upper:
        return Fraction(-((-scaled.numerator) // scaled.denominator), SCALE)
    return Fraction(scaled.numerator // scaled.denominator, SCALE)


@cache
def log_bounds(x):
    z = (x-1)/(x+1)
    terms = 60
    exact_partial = 2*sum(z**(2*i+1)/(2*i+1) for i in range(terms))
    tail = 2*z**(2*terms+1)/((2*terms+1)*(1-z*z))
    return rounded(exact_partial, False), rounded(exact_partial+tail, True)


@cache
def power_bounds(rank, k):
    binary = 2**(rank.bit_length()-1)
    shift = binary.bit_length()-1
    l2, u2 = log_bounds(Fraction(2))
    lo, hi = log_bounds(Fraction(rank, binary))
    lo, hi = k*(lo+shift*l2), k*(hi+shift*u2)
    assert 0 <= lo <= hi < 1

    def exponential(z, terms):
        total = term = Fraction(1)
        for i in range(1, terms+1):
            term *= -z/i
            total += term
        return total

    return rounded(rank*exponential(hi, 35), False), rounded(rank*exponential(lo, 34), True)


def cost(hist, k):
    lower = upper = Fraction(0)
    for r, n in hist.items():
        a, b = (n*x for x in power_bounds(r, k))
        lower += min(a, b)
        upper += max(a, b)
    return lower, upper


def profile(invoice, native, word, ranks):
    copies = invoice["native_calls"]
    assert copies == len(invoice["native_instances"]) == 36
    assert {tuple((r["stage"], r["copy"])) for r in invoice["native_instances"]} == {
        (stage, which) for stage in range(1, 19) for which in (0, 1)
    }
    assert all(r["ports"] == 111 for r in invoice["native_instances"])
    assert native == Counter({int(r): n for r, n in invoice["native_paid"].items()})
    assert sum(native.values()) == 2871
    caller_paid = {1: 444, **{r: 444 for r in range(7, 57, 7)}}
    assert invoice["event_counts"]["QUERY"]*111 == caller_paid[1]
    assert invoice["event_counts"]["IDLE_ONE"]*111 == 8*444
    full_paid = Counter({r: copies*n for r, n in native.items()})
    full_paid.update(caller_paid)

    helpers = Counter(ranks[word["final"][j]]-ranks[word["start"][j]]
                      for j in range(222, word["public"]))
    assert helpers == Counter({int(r): n for r, n in invoice["native_helpers"].items()})
    caller_targets = {**{r: 444 for r in range(8, 65, 7)}, 127: 222}
    full_targets = Counter({r: copies*n for r, n in helpers.items()})
    full_targets.update(caller_targets)
    assert full_paid == Counter({int(r): n for r, n in invoice["paid"].items()})
    assert full_targets == Counter({int(r): n for r, n in invoice["targets"].items()})
    assert sum(full_paid.values()) == invoice["paid_jobs"]
    assert sum(full_targets.values()) == invoice["productive_fields"]
    signed = full_targets.copy()
    signed.subtract(full_paid)
    assert sum(r*n for r, n in signed.items()) == invoice["rank_surplus"]
    return signed, copies
