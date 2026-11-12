"""Independently verify R97's 310 frozen R96 bank keys modulo 65537."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from math import isqrt
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic
import sys

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
WORD = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PINS = {
    "inputs/PRICE.json": "a78be64c3e3ae8a0e532237c4dd3541aa9ad3fcbbc3c25d79c8a03fb7e07c525",
    "inputs/GEOMETRY.json": "c6f9f018df8b58fcdf4f44356bd59bcac6d411b7845104ff4ad372ed4a95cfbd",
    "inputs/REMAINING.json": "3597499663a57702856945e91214a65e1d0f94db8643b93c0234c2bbf9291b1a",
    "inputs/7334-WORD.json.gz": WORD,
}
PRIME = 65537
CASES = 310
SECONDS = 25
EVENTS = 76466


def unique(items):
    data = dict(items)
    if len(items) != len(data):
        raise ValueError("duplicate JSON key")
    return data


def authenticate(root):
    raw = {}
    for rel, expected in PINS.items():
        data = (root / rel).read_bytes()
        if sha256(data).hexdigest() != expected:
            raise ValueError(f"changed dependency: {rel}")
        raw[rel] = data
    return raw


@cache
def coefficient(value):
    q = Fraction(value)
    if not q or q.denominator % PRIME == 0:
        raise ValueError("zero scalar or denominator divisible by modulus")
    return q.numerator * pow(q.denominator, -1, PRIME) % PRIME, q.denominator


def axpy(target, source, scale):
    if scale:
        for role, old in source.items():
            current = (target.get(role, 0) + scale * old) % PRIME
            if current:
                target[role] = current
            else:
                target.pop(role, None)


def scaled(vector, scale):
    return {i: y for i, x in vector.items() if (y := x * scale % PRIME)}


def verify_minor(vectors, columns):
    """Independently recompute a minor on the original projected rows."""
    matrix = [[row.get(c, 0) for c in columns] for row in vectors]
    determinant = 1
    for c in range(len(matrix)):
        pivot = next((r for r in range(c, len(matrix)) if matrix[r][c]), None)
        if pivot is None:
            return 0
        if pivot != c:
            matrix[c], matrix[pivot] = matrix[pivot], matrix[c]
            determinant = -determinant
        diag = matrix[c][c]
        determinant = determinant * diag % PRIME
        inverse = pow(diag, -1, PRIME)
        for r in range(c + 1, len(matrix)):
            factor = matrix[r][c] * inverse % PRIME
            if factor:
                for k in range(c + 1, len(matrix)):
                    matrix[r][k] = (matrix[r][k] - factor * matrix[c][k]) % PRIME
                matrix[r][c] = 0
    return determinant % PRIME


def classify(bank, vectors, cohort):
    full_rows = [vectors[r] for r in bank]
    exterior = [{i: x for i, x in row.items() if i not in cohort} for row in full_rows]
    basis, kernel = [], []
    determinant = 1
    for index, vector in enumerate(exterior):
        work = vector.copy()
        combination = {index: 1}
        for col, known, combo in basis:
            factor = -work.get(col, 0)
            axpy(work, known, factor)
            axpy(combination, combo, factor)
        if not work:
            image = {}
            for i, factor in combination.items():
                axpy(image, full_rows[i], factor)
            assert image.keys() <= cohort
            kernel.append(dict(cut={bank[i]: x for i, x in combination.items()}, endpoint=image))
            continue
        col = max(work)
        pivot = work[col]
        determinant = determinant * pivot % PRIME
        inverse = pow(pivot, -1, PRIME)
        basis.append((col, scaled(work, inverse), scaled(combination, inverse)))
    rank = len(basis)
    assert rank + len(kernel) == len(bank)
    columns = [col for col, _, _ in basis]
    if kernel:
        return dict(rank=rank, kernel=kernel, minor_axes=None, determinant=None)
    assert columns and verify_minor(exterior, columns) == determinant != 0
    return dict(rank=rank, kernel=[], minor_axes=columns, determinant=determinant)


def apply(event, state, vectors, fresh, n, denominators, backward):
    op, r, *args = event
    current = state[r]
    if op == "MOVE":
        old, new, owned = args
        assert owned == (r >= n)
        assert current == (new if backward else old)
        state[r] = old if backward else new
        fresh.discard(r)
        return
    if op in ("INIT", "CLEAR"):
        assert r >= n
        c, = args
        entering = (op == "CLEAR") if backward else (op == "INIT")
        if entering:
            assert current is None and vectors[r] is None
            state[r], vectors[r] = c, {}
            if not backward:
                fresh.add(r)
        else:
            assert current == c and vectors[r] is not None
            state[r] = vectors[r] = None
            fresh.discard(r)
        return
    assert op in ("SCALE", "ADD", "COPY") and current == args[-1] and vectors[r] is not None
    factor, denominator = coefficient(args[-2])
    denominators.add(denominator)
    if op == "SCALE":
        vectors[r] = scaled(vectors[r], factor)
    else:
        src = args[0]
        assert src != r and state[src] == current and vectors[src] is not None
        if backward:
            axpy(vectors[src], vectors[r], factor)
            if op == "COPY":
                assert r >= n
                vectors[r] = {}
        elif op == "COPY":
            assert r >= n and r in fresh and not vectors[r]
            vectors[r] = scaled(vectors[src], factor)
        else:
            axpy(vectors[r], vectors[src], factor)
    fresh.discard(r)


def controls():
    assert all(PRIME % i for i in range(2, isqrt(PRIME) + 1))
    witness = classify([0, 1], [{3: 2, 8: 1}, {3: 3, 8: 4}], set())
    assert witness["minor_axes"] == [8, 3] and witness["determinant"] == PRIME - 5
    dropped = classify([0, 1], [{0: 1, 8: 1}, {1: 1, 8: 1}], {0, 1})
    assert dropped["kernel"] == [dict(cut={0: PRIME - 1, 1: 1}, endpoint={0: PRIME - 1, 1: 1})]
    tape = [("ADD", 1, 0, "-3/2", 4), ("SCALE", 0, "2", 4), ("INIT", 2, 4),
            ("COPY", 2, 1, "1", 4), ("ADD", 0, 2, "5", 4), ("CLEAR", 2, 4)]
    result = []
    for backward in (False, True):
        state, vectors, fresh, denoms = [4, 4, None], [{0: 1}, {1: 1}, None], set(), set()
        for event in reversed(tape) if backward else tape:
            apply(event, state, vectors, fresh, 2, denoms, backward)
        assert state == [4, 4, None] and not fresh and denoms == {1, 2}
        result.append(vectors)
    assert result[0] == [{0: coefficient("-11/2")[0], 1: 5}, {0: coefficient("-3/2")[0], 1: 1}, None]
    assert result[1] == [{0: coefficient("-11/2")[0], 1: coefficient("-3/2")[0]}, {0: 5, 1: 1}, None]
    try:
        coefficient("1/65537")
    except ValueError:
        pass
    else:
        raise AssertionError("nonunit denominator admitted")
    return ["prime and signed nonzero minor", "planted pure kernel", "owned COPY forward and adjoint",
            "nonunit denominator rejection"]


def span(frame):
    vectors = {0}
    for v in frame:
        assert v not in vectors
        vectors |= {v ^ w for w in vectors}
    return vectors


def sweep(word, keys, cohort, deadline, result, progress, backward, previous=None):
    tape, n, owned = (word[k] for k in ("program", "public", "owned_fields"))
    assert (len(tape), n, owned) == (EVENTS, 1501, 68)
    origin, target = ("final", "initial") if backward else ("initial", "final")
    state = word[origin] + [None] * owned
    vectors = [{r: 1} for r in range(n)] + [None] * owned
    fresh, denoms = set(), set()
    request = defaultdict(list)
    frames = word["frames"]
    low, high = span(frames[3]), span(frames[245])
    for cut, chart in keys:
        assert 0 <= cut <= EVENTS and len(frames[chart]) == 4 and low < span(frames[chart]) < high
        request[cut].append(chart)
    boundaries = range(EVENTS, -1, -1) if backward else range(EVENTS + 1)
    progress.update(events=0, first_unvisited_cut=boundaries.start, denominator_units=[])
    for cut in boundaries:
        progress["first_unvisited_cut"] = cut
        if (cut % 128 == 0 or cut in request) and monotonic() >= deadline:
            break
        for chart in request.get(cut, []):
            key = (cut, chart)
            public_bank = [r for r in range(n) if state[r] == chart]
            owned_bank = [r for r in range(n, n + owned) if state[r] == chart]
            pivots = sorted(set(public_bank) & cohort)
            assert public_bank and pivots
            if cut:
                event = tape[cut - 1]
                assert chart in (event[2:4] if event[0] == "MOVE" else event[-1:])
            bank = dict(public=public_bank, owned=owned_bank, pivots=pivots)
            if previous is not None:
                assert bank == previous[key]["bank"]
            result[key] = dict(bank=bank, **classify(public_bank, vectors, cohort))
        if cut == (0 if backward else EVENTS):
            assert state == word[target] + [None] * owned and not fresh
            assert set(result) == set(keys)
            progress["first_unvisited_cut"] = None
            break
        apply(tape[cut - 1 if backward else cut], state, vectors, fresh, n, denoms, backward)
        progress["events"] += 1
    progress["denominator_units"] = sorted(denoms)


def pairing(prefix, suffix):
    def dot(left, right):
        return sum(v * right.get(i, 0) for i, v in left.items()) % PRIME

    return [[dict(cut=dot(a["cut"], b["cut"]), endpoint=dot(a["endpoint"], b["endpoint"]))
             for b in suffix["kernel"]] for a in prefix["kernel"]]


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    assert __debug__ and sys.version_info[:2] == (3, 12)
    checks = controls()
    if args.controls_only:
        print(dumps(checks))
        return

    def stop(*_):
        raise TimeoutError("hard 25-second cap")

    start = monotonic()
    signal(SIGALRM, stop)
    alarm(SECONDS)
    timeout = None
    keys, prior, prefix, suffix = [], [], {}, {}
    prefix_progress, suffix_progress = {}, {}
    try:
        raw = authenticate(args.root)
        price, geom, remaining = [loads(raw[f"inputs/{name}.json"], object_pairs_hook=unique)
                                  for name in ("PRICE", "GEOMETRY", "REMAINING")]
        assert price["head"] == geom["head"] == remaining["head"] == HEAD and price["caller"] == CALLER
        assert price["word_sha256"] == geom["word_sha256"] == WORD
        assert geom["price_sha256"] == PINS["inputs/PRICE.json"]
        assert remaining["input_sha256"]["lead/GEOMETRY.json"] == PINS["inputs/GEOMETRY.json"]
        assert geom["status"] == "EXHAUSTED" and geom["visited_events"] == EVENTS
        keys = list(map(tuple, remaining["unvisited_prefix"]))
        prior = remaining["dual_drops_requiring_rational"]
        assert len(keys) == len(set(keys)) == remaining["next_modular_cases"] == CASES
        assert remaining["next_modular_runner_seconds"] == SECONDS
        assert keys == list(map(tuple, geom["unvisited_keys"]))
        selected = {tuple(row["key"]) for row in geom["selected"]}
        assert len(selected) == 16 and not set(keys) & selected and set(map(tuple, prior)) <= selected
        assert set(keys) | selected == set(map(tuple, geom["all_representative_keys"]))
        assert prior == [[41740, 242], [45266, 242]]
        payload = decompress(raw["inputs/7334-WORD.json.gz"])
        assert sha256(payload).hexdigest() == PAYLOAD
        word = loads(payload, object_pairs_hook=unique)
        cohort = set(price["cohort"])
        assert len(cohort) == 15 and all((word["initial"][r], word["final"][r]) == (3, 245) for r in cohort)
        deadline = start + SECONDS - 2
        sweep(word, keys, cohort, deadline, prefix, prefix_progress, False)
        candidates = [key for key in keys if key in prefix and prefix[key]["kernel"]]
        if candidates:
            sweep(word, candidates, cohort, deadline, suffix, suffix_progress, True, prefix)
        else:
            suffix_progress.update(events=0, first_unvisited_cut=None, denominator_units=[])
    except TimeoutError as error:
        timeout = str(error)
    finally:
        alarm(0)

    results = []
    for key in keys:
        left, right = prefix.get(key), suffix.get(key)
        pair = None
        if left and not left["kernel"]:
            status = "prefix_exclusion"
        elif right and not right["kernel"]:
            status = "suffix_exclusion"
        elif right:
            status = "dual_drop"
            pair = pairing(left, right)
        else:
            status = "unvisited"
        results.append(dict(key=key, status=status, prefix=left, suffix=right, modular_pairings=pair))
    complete = (timeout is None and prefix_progress.get("first_unvisited_cut", 0) is None
                and suffix_progress.get("first_unvisited_cut", 0) is None)
    print(dumps(dict(head=HEAD, caller=CALLER, pins=PINS, modulus=PRIME, controls=checks,
        cap_cases=CASES, cap_seconds=SECONDS, prefix_progress=prefix_progress, suffix_progress=suffix_progress,
        timeout=timeout, complete=complete, results=results,
        counts=Counter(row["status"] for row in results), previously_frozen_exact_keys=prior),
        indent=2, sort_keys=True))
    if not complete:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
