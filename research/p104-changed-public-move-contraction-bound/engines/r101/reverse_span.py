"""Independent normalized reverse-contact and fraction-free donor-span gate."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from math import gcd, isqrt, lcm
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
WORD = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PRICE = "c9166ff18194a7e69f91a06f76329a2ff838bb65b08c4ed7a5a06038fdfa966d"
PRIME = 65521


def unique(pairs):
    values = dict(pairs)
    assert len(values) == len(pairs), "duplicate JSON key"
    return values


def checked(path, pin, compressed=False):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != pin:
        raise ValueError(f"changed input {path.name}")
    return loads(decompress(raw) if compressed else raw, object_pairs_hook=unique)


@cache
def coefficient(raw):
    q = Fraction(raw)
    assert q and q.denominator % PRIME, "nonunit native denominator"
    return q.numerator, q.denominator


def normalized(values, denominator):
    if not values:
        return {}, 1
    divisor = gcd(denominator, *values.values())
    if divisor != 1:
        return {j: a // divisor for j, a in values.items()}, denominator // divisor
    return values, denominator


def sum_scaled(first, second, factor):
    a, da = first
    b, db = second
    numerator, denom = factor
    if not b:
        return first
    common = lcm(da, db * denom)
    out = {j: v * (common // da) for j, v in a.items()}
    weight = numerator * (common // (db * denom))
    for j, v in b.items():
        val = out.get(j, 0) + weight * v
        if val:
            out[j] = val
        else:
            out.pop(j, None)
    return normalized(out, common)


def incidence(e):
    return e[1:3] if e[0] in ("ADD", "COPY") else e[1:2]


def candidates(word, quote):
    n = word["public"]
    tape = word["program"]
    stock = {}
    for case in quote["candidates"]:
        owner = case["owner"]
        left, right = case["move_clocks"]
        a, middle, c = case["chart_path"]
        original, entry = case["literal_ADD"]
        assert case["owner_access"] == "destination" and entry[0] == owner
        assert entry[1] == case["peer"] and entry[-1] == middle
        assert tape[left] == ["MOVE", owner, a, middle, True]
        assert tape[right] == ["MOVE", owner, middle, c, True]
        assert tape[original] == ["ADD", *entry]
        assert n <= owner and left < original < right
        assert [i for i in range(left + 1, right) if owner in incidence(tape[i])] == [original]
        assert case["cut_windows_pre_event"] == {"entrance": [left, right], "exit": [left + 1, right]}
        stock[owner, left, right] = case
    assert len(stock) == 3 and len({tuple(k) for k in quote["keys"]}) == quote["case_cap"] == 33
    return stock


def collect(word, cuts, observations, cap):
    """Forward structural pass only. Assign one ID to each requested live value."""
    n = word["public"]
    chart = list(word["initial"]) + [None] * word["owned_fields"]
    revisions = [0] * len(chart)
    fresh = set()
    starts = {}
    lifetimes = {}
    requests = defaultdict(list)
    observation_ids = {}
    bank_ids = {}
    value_id = {}
    paid = Counter()

    @cache
    def span(f):
        vectors = {0}
        for v in word["frames"][f]:
            assert v not in vectors
            vectors.update(v ^ t for t in tuple(vectors))
        return vectors

    def request(t, role):
        assert chart[role] is not None
        key = role, revisions[role]
        if key not in value_id:
            value_id[key] = len(value_id)
            requests[t].append((role, value_id[key]))
        return value_id[key]

    tape = word["program"]
    for t in range(len(tape) + 1):
        if t % 128 == 0 and monotonic() >= cap:
            raise TimeoutError("literal structural scan")
        for role in observations.get(t, ()):
            observation_ids[t, role] = request(t, role)
        for key, chart_id, exclude in cuts.get(t, ()):
            bank_ids[key] = [(r, request(t, r)) for r, c in enumerate(chart) if c == chart_id and r != exclude]
        if t == len(tape):
            break
        op, d, *args = tape[t]
        assert 0 <= d < len(chart)
        if op == "INIT":
            assert d >= n and chart[d] is None
            chart[d], starts[d] = args[0], t
            fresh.add(d)
        elif op == "CLEAR":
            assert d >= n and chart[d] == args[0] and d in starts
            lifetimes[d, starts.pop(d)] = t
            chart[d] = None
            fresh.discard(d)
        elif op == "MOVE":
            a, b, owned = args
            assert chart[d] == a and owned == (d >= n)
            assert span(a) < span(b) or owned and span(b) < span(a)
            paid[abs(len(word["frames"][b]) - len(word["frames"][a]))] += 1
            chart[d] = b
            fresh.discard(d)
            continue
        elif op == "SCALE":
            assert chart[d] == args[-1]
            coefficient(args[-2])
            fresh.discard(d)
        else:
            assert op in ("ADD", "COPY")
            src, coeff, f = args
            assert d != src and chart[d] == chart[src] == f
            coefficient(coeff)
            if op == "COPY":
                assert d >= n and d in fresh
            fresh.discard(d)
        revisions[d] += 1
    assert not starts and chart == word["final"] + [None] * word["owned_fields"]
    return requests, observation_ids, bank_ids, lifetimes, dict(paid), len(value_id)


def transpose_prefix(word, requests, count, cap):
    """Propagate all requested output covectors backward, then transpose to input rows."""
    n = word["public"]
    empty = ({}, 1)
    adjoint = [empty] * (n + word["owned_fields"])
    tape = word["program"]
    for t in range(max(requests), -1, -1):
        if t % 128 == 0 and monotonic() >= cap:
            raise TimeoutError("reverse normalized prefix")
        op, d, *args = tape[t]
        if op in ("INIT", "CLEAR"):
            adjoint[d] = empty
        elif op == "SCALE":
            adjoint[d] = sum_scaled(empty, adjoint[d], coefficient(args[-2]))
        elif op in ("ADD", "COPY"):
            src = args[0]
            adjoint[src] = sum_scaled(adjoint[src], adjoint[d], coefficient(args[-2]))
            if op == "COPY":
                adjoint[d] = empty
        else:
            assert op == "MOVE"
        for r, output in requests.get(t, ()):
            adjoint[r] = sum_scaled(adjoint[r], ({output: 1}, 1), (1, 1))
    assert not any(d for d, _ in adjoint[n:])
    by_output = [[] for _ in range(count)]
    for coord, (coeffs, d) in enumerate(adjoint[:n]):
        assert d % PRIME
        for i, v in coeffs.items():
            by_output[i].append((coord, v, d))
    rows = []
    for entries in by_output:
        common = lcm(*(d for _, _, d in entries))
        rows.append(normalized({i: v * (common // d) for i, v, d in entries}, common))
    return rows


def eliminate(v, basis, record=False):
    """Reverse-pivot integer elimination. All leading pivots are exact."""
    v = v.copy()
    reductions = []
    multiplier = 1
    while v:
        k = max(v)
        if k not in basis:
            break
        w = basis[k]
        a, b = w[k], v[k]
        d = gcd(a, b)
        a, b = a // d, b // d
        next_v = {j: a * x for j, x in v.items()}
        for j, x in w.items():
            z = next_v.get(j, 0) - b * x
            if z:
                next_v[j] = z
            else:
                next_v.pop(j, None)
        assert k not in next_v
        g = gcd(*next_v.values()) or 1
        v = {j: x // g for j, x in next_v.items()}
        if record:
            reductions.append((k, Fraction(b, a) * multiplier))
            multiplier *= Fraction(g, a)
    return v, reductions, multiplier


def dot(row, covector):
    numerator, denominator = row
    return sum((numerator.get(j, 0) * v for j, v in covector.items()), Fraction(0)) / denominator


def exact_span(bank, target):
    t, dt = target
    if not t:
        return dict(status="exact_span", coefficients={})
    exterior = next((j for j in sorted(t) if all(j not in row for _, (row, _) in bank)), None)
    basis = {}
    histories = {}
    for role, (v, d) in bank:
        reduced, steps, scale = eliminate(v, basis, record=True)
        if reduced:
            pivot = max(reduced)
            basis[pivot] = reduced
            histories[pivot] = (role, d, steps, scale)
    if exterior is not None:
        residue = t[exterior] * pow(dt, -1, PRIME) % PRIME
        return dict(status="absent_exterior_coordinate", donor_rank=len(basis), augmented_rank=len(basis)+1,
                    coordinate=exterior, target_coefficient=str(Fraction(t[exterior], dt)),
                    target_residue_mod_prime=residue)
    residual, steps, scale = eliminate(t, basis, record=True)
    if residual:
        k = max(residual)
        dual = {k: Fraction(1)}
        for p, v in sorted(basis.items()):
            coefficient = -sum((v.get(j, 0) * c for j, c in dual.items()), Fraction(0)) / v[p]
            if coefficient:
                dual[p] = coefficient
        target_value = dot(target, dual)
        assert target_value and all(dot(v, dual) == 0 for _, v in bank)
        return dict(status="exact_rank_exclusion", donor_rank=len(basis), augmented_rank=len(basis) + 1,
                    missing_reverse_pivot=k, residual_integer_row=residual,
                    separating_covector={j: str(v) for j, v in dual.items()}, separated_target=str(target_value))
    pending = dict(steps)
    solution = defaultdict(Fraction)
    for pivot in sorted(basis):
        if pivot not in pending:
            continue
        weight = pending.pop(pivot)
        if not weight:
            continue
        role, denom, reductions, factor = histories[pivot]
        weight /= factor
        solution[role] += weight * denom / dt
        for j, scalar in reductions:
            pending[j] = pending.get(j, Fraction(0)) - weight * scalar
    assert not pending
    check = ({}, 1)
    rows = dict(bank)
    for r, x in solution.items():
        check = sum_scaled(check, rows[r], (x.numerator, x.denominator))
    assert check == target, (check, target)
    return dict(status="exact_span", donor_rank=len(basis),
                coefficients={r: str(x) for r, x in sorted(solution.items()) if x})


def controls():
    toy = {"public": 4, "owned_fields": 1, "frames": [[]], "initial": [0] * 4, "final": [0] * 4,
           "program": [["INIT", 4, 0], ["COPY", 4, 0, "1/2", 0], ["ADD", 4, 1, "-3", 0],
                       ["ADD", 0, 2, "2", 0], ["CLEAR", 4, 0]]}
    req, ids, banks, _, _, count = collect(toy, {3:[((3,), 0, 4)], 4:[((4,), 0, 4)]}, {3:[4]}, float("inf"))
    rows = transpose_prefix(toy, req, count, float("inf"))
    target = rows[ids[3, 4]]
    before = [(r, rows[i]) for r, i in banks[3,] if r in (0, 1)]
    after = [(r, rows[i]) for r, i in banks[4,] if r in (0, 1)]
    assert exact_span(before, target)["coefficients"] == {0:"1/2", 1:"-3"}
    assert exact_span(after, target)["status"] == "exact_rank_exclusion"
    assert exact_span(before[1:], target)["status"] == "absent_exterior_coordinate"
    # Nontrivial exact dependency and reconstruction after a shared pivot.
    multi = [(5, ({0: 3, 1: -1}, 2)), (6, ({0: 1, 1: 4}, 3)), (7, ({0: 11, 1: 2}, 1))]
    hit = exact_span(multi, ({0: 11, 1: 2}, 1))
    assert hit["status"] == "exact_span" and len(hit["coefficients"]) == 2
    return ["signed_multi_source_and_owned_COPY", "intervening_write_blocks_span", "absent_exterior_coordinate",
            "dependent_donor_bank_exact_reconstruction"]


def audit(word, quote, cap, decisions):
    assert (word["public"], word["owned_fields"], len(word["program"])) == (1501, 68, 76466)
    stock = candidates(word, quote)
    observed = defaultdict(set)
    cuts = defaultdict(list)
    for row in quote["keys"]:
        key = tuple(row)
        owner, left, right, side, t = key
        item = stock[owner, left, right]
        chart = item["chart_path"][0 if side == "entrance" else 2]
        assert item["cut_windows_pre_event"][side][0] <= t <= item["cut_windows_pre_event"][side][1]
        cuts[t].append((key, chart, owner))
        observed[item["literal_ADD"][0]].add(item["peer"])
    requests, refs, banks, lifetimes, paid, count = collect(word, cuts, observed, cap)
    assert paid == {1:4000, 2:853, 3:829, 4:223, 5:345, 6:14, 7:10, 8:5}
    for item in stock.values():
        left, right = item["owner_lifetime"]
        assert lifetimes[item["owner"], left] == right
    rows = transpose_prefix(word, requests, count, cap)
    for entry in quote["keys"]:
        if monotonic() >= cap:
            raise TimeoutError("exact donor bank gate")
        owner, left, right, side, t = entry
        item = stock[owner, left, right]
        source = item["peer"]
        target_id = refs[item["literal_ADD"][0], source]
        target = rows[target_id]
        bank = [(r, rows[i]) for r, i in banks[tuple(entry)]]
        chart = item["chart_path"][0 if side == "entrance" else 2]
        decision = exact_span(bank, target)
        decisions.append(dict(key=entry, proposed_chart=chart, literal_read_peer=source,
            literal_read_clock=item["literal_ADD"][0], donors=len(bank), owned_donors=sum(r>=word["public"] for r,_ in bank),
            target_row_id=target_id, donor_role_row_ids=banks[tuple(entry)],
            donor_rowset_sha256=sha256(dumps(bank, sort_keys=True).encode()).hexdigest(), **decision))
    return rows


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path)
    parser.add_argument("--price", type=Path)
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    if args.controls_only:
        print(dumps(controls()))
        return
    assert args.word is not None and args.price is not None and __debug__
    start = monotonic()
    def stop(*_):
        raise TimeoutError("hard 20-second runner cap")
    signal(SIGALRM, stop)
    alarm(20)
    decisions = []
    keys = []
    rows = None
    tests = []
    timed_out = None
    try:
        tests = controls()
        assert all(PRIME % d for d in range(2, isqrt(PRIME)+1))
        quote = checked(args.price, PRICE)
        assert quote["head"] == HEAD and quote["word_sha256"] == WORD
        keys = quote["keys"]
        rows = audit(checked(args.word, WORD, compressed=True), quote, start+18, decisions)
    except TimeoutError as error:
        timed_out = str(error)
    finally:
        alarm(0)
    result = dict(head=HEAD, word_sha256=WORD, price_sha256=PRICE, prime=PRIME,
        case_cap=33, runner_cap_seconds=20, controls=tests, distinct_requested_rows=len(rows) if rows is not None else None,
        requested_integer_rows=rows,
        cases=decisions, disposition_counts=dict(Counter(r["status"] for r in decisions)),
        unresolved=keys[len(decisions):], timeout=timed_out,
        survivors=[r for r in decisions if r["status"] == "exact_span"])
    print(dumps(result, sort_keys=True, indent=2))
    if timed_out:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
