"""Recount six commuting #7277 ADD swaps and independently enclose their price."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import cache
from hashlib import sha256
from itertools import pairwise
import gzip
import json
from pathlib import Path
from signal import alarm

HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/EARLY-RESULT.json": "691025fe95c7938a6da211244d4d5b6187d88a9de1acff0862eeb7f0ce7deaa7",
    "inputs/WORD.json.gz": "2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756",
}


def read_inputs(root):
    result = {}
    for name, pin in PINS.items():
        raw = (root / name).read_bytes()
        if sha256(raw).hexdigest() != pin:
            raise ValueError(f"Changed source: {name}")
        result[name] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    return result["inputs/WORD.json.gz"], result["inputs/CALLER.json"], result["inputs/EARLY-RESULT.json"]


def spaces(frames):
    answer = []
    for axes in frames:
        frame = {0}
        for a in axes:
            next_layer = {a ^ b for b in frame}
            assert not frame & next_layer
            frame.update(next_layer)
        answer.append(frozenset(frame))
    return answer


def roles(row):
    return set(row[1:3]) if row[0] in ("ADD", "COPY") else {row[1]}


def sparse_add(row, domain):
    _, destination, source, scalar, _ = row
    result = {(r, r): F(1) for r in domain}
    key = destination, source
    result[key] = result.get(key, F(0)) + F(scalar)
    return result


def sparse_product(a, b):
    out = defaultdict(F)
    for (i, j), x in a.items():
        for (k, l), y in b.items():
            if j == k:
                out[i, l] += x * y
    return {key: value for key, value in out.items() if value}


def commute(a, b):
    domain = roles(a) | roles(b)
    A, B = sparse_add(a, domain), sparse_add(b, domain)
    return sparse_product(A, B) == sparse_product(B, A)


def literal_move_bill(program, word, relative):
    public = word["public"]
    chart = word["initial"] + [None] * word["owned_fields"]
    bill = Counter()
    for row in program:
        op, r, *args = row
        if op == "MOVE":
            start, end, owned = args
            assert chart[r] == start and owned == (r >= public)
            rank = relative(start, end)
            gap = len(word["frames"][end]) - len(word["frames"][start])
            assert rank == abs(gap) > 0 and (owned or gap > 0)
            bill[rank] += 1
            chart[r] = end
        elif op == "INIT":
            assert chart[r] is None and r >= public
            chart[r] = args[0]
        else:
            assert all(chart[v] == args[-1] for v in roles(row))
            if op == "CLEAR":
                assert r >= public
                chart[r] = None
    assert chart == word["final"] + [None] * word["owned_fields"]
    return bill


def whole_contact_recount(events, word, relative, focus=frozenset(), shared=frozenset()):
    public = word["public"]
    dims = list(map(len, word["frames"]))
    prior = {r: (-1, chart) for r, chart in enumerate(word["initial"])}
    paid = Counter()
    exterior = []
    edges = 0

    def contact(role, clock, chart):
        nonlocal edges
        a, f = prior[role]
        rank = relative(f, chart)
        edges += 1
        if role < public:
            assert rank == dims[chart] - dims[f]
        if rank:
            paid[rank] += 1
        if role in shared and ((a in focus) != (clock in focus)):
            exterior.append(rank)
        prior[role] = clock, chart

    for clock, row in events:
        if row[0] == "INIT":
            assert row[1] not in prior
            prior[row[1]] = clock, row[-1]
        else:
            for role in roles(row):
                contact(role, clock, row[-1])
            if row[0] == "CLEAR":
                del prior[row[1]]
    assert set(prior) == set(range(public))
    for role, chart in enumerate(word["final"]):
        contact(role, len(word["program"]), chart)
    assert edges == 137891
    return paid, tuple(sorted(exterior))


def full_bill(word, caller, native, relative):
    stages = [row[1] for row in caller["events"] if row[0] == "J"]
    assert stages == list(range(1, 18))
    copies = len(stages)
    main = set(word["live"]) | {r + 112 for r in word["live"]} | set(
        word["hosted"]["X2"] + word["hosted"]["Y2"]
    )
    assert len(main) == 400
    helpful = Counter(relative(a, b) for r, (a, b) in enumerate(
        zip(word["initial"], word["final"], strict=True)) if r not in main)
    assert sum(helpful.values()) == 1101 and 0 not in helpful
    paid, productive = (Counter({r: n * copies for r, n in h.items()})
                         for h in (native, helpful))
    for ty in caller["types"].values():
        for sign, offset, *bits in ty["diagonal"]:
            assert (sign, offset, len(bits)) == (-1, 0, copies)
            productive[1 + 8 * sum(bits)] += len(ty["ports"])
    for row in caller["events"]:
        if row[0] == "J":
            continue
        ty, op, _, *args = row
        ports = len(caller["types"][ty]["ports"])
        if op == "QUERY":
            paid[1] += ports
        elif op in ("IDLE_ONE", "IDLE_ODD"):
            paid[8 * len(args[0]) + (op == "IDLE_ODD")] += ports
    return paid, productive, copies


@cache
def log_interval(x):
    z = (x - 1) / (x + 1)
    partial = 2 * sum(z**i / i for i in range(1, 117, 2))
    return partial, partial + 2 * z**117 / (117 * (1 - z*z))


def positive_exp_interval(x):
    assert 0 <= x < 1
    term = total = F(1)
    for n in range(1, 39):
        term *= x / n
        total += term
    return total, total + term*x / (39 * (1-x/40))


@cache
def tariff(rank, k):
    if rank == 0:
        return F(0), F(0)
    e = rank.bit_length() - 1
    a, b = log_interval(F(rank, 1 << e))
    c, d = log_interval(F(2))
    grid = 10**50
    lo = rank / positive_exp_interval(k * (b + e*d))[1]
    hi = rank / positive_exp_interval(k * (a + e*c))[0]
    return F((grid*lo).__floor__(), grid), F((grid*hi).__ceil__(), grid)


def price(hist, k):
    lower = upper = F(0)
    for r, n in hist.items():
        lo, hi = tariff(r, k)
        lower += n * (lo if n >= 0 else hi)
        upper += n * (hi if n >= 0 else lo)
    return lower, upper


def run(root, declared_file):
    word, caller, early = read_inputs(root)
    declared_raw = declared_file.read_bytes()
    lead = json.loads(declared_raw)
    assert lead["head"] == HEAD
    assert {f"complex/source/{p}": h for p, h in PINS.items()}.items() <= lead["pins"].items()
    assert not lead["unresolved"] and not lead["positives"]
    k = F(early["price"]["independent_raw_bracket"][1])
    assert k == F(lead["crossing_upper"])
    frames = spaces(word["frames"])
    ranks = [len(frame).bit_length() - 1 for frame in frames]

    @cache
    def relative(a, b):
        if a == b:
            return 0
        intersection = len(frames[a] & frames[b])
        assert intersection > 0 and intersection & (intersection - 1) == 0
        intersection_rank = intersection.bit_length() - 1
        return ranks[a] + ranks[b] - 2 * intersection_rank

    def rank(a, b):
        return relative(min(a, b), max(a, b))

    full = word["program"]
    normalized = [(i, row) for i, row in enumerate(full) if row[0] != "MOVE"]
    literal = literal_move_bill(full, word, rank)
    reconstructed, _ = whole_contact_recount(normalized, word, rank)
    assert literal == reconstructed and sum(literal.values()) == 6280
    omission = next(i for i, row in enumerate(full) if row[0] == "MOVE")
    try:
        literal_move_bill(full[:omission] + full[omission+1:], word, rank)
    except AssertionError:
        pass
    else:
        raise AssertionError("omitted paid MOVE accepted")

    paid, targets, copies = full_bill(word, caller, literal, rank)
    frozen = early["invoice"]
    assert {str(r): n for r, n in paid.items()} == frozen["P"]
    assert {str(r): n for r, n in targets.items()} == frozen["T"]
    assert sum(r * (targets[r] - paid[r]) for r in paid.keys() | targets.keys()) == frozen["S"] == 1424
    assert copies == lead["copies"] == 17
    baseline = targets.copy()
    baseline.subtract(paid)
    base_l, base_u = price(baseline, k)
    assert F(lead["baseline_moment_interval"][0]) <= base_l <= base_u <= F(lead["baseline_moment_interval"][1]) < 0

    rows = {tuple(event): row for row in lead["rows"] for event in row["events"]}
    assert len(rows) == sum(len(r["events"]) for r in lead["rows"]) == 6
    census = Counter()
    verified = []
    signatures = set()
    for slot, ((ta, a), (tb, b)) in enumerate(pairwise(normalized)):
        if a[0] != "ADD" or b[0] != "ADD":
            continue
        census["adjacent_add_add"] += 1
        if a[-1] == b[-1]:
            continue
        census["different_chart"] += 1
        shared = roles(a) & roles(b)
        if not any(r >= word["public"] for r in shared):
            continue
        census["shared_owned"] += 1
        matrix_equal = commute(a, b)
        if min(shared) < word["public"] or not matrix_equal:
            census["excluded_commutation_or_public"] += 1
            continue
        focus = {ta, tb}
        prior, ext_old = whole_contact_recount(normalized, word, rank, focus, shared)
        changed = normalized.copy()
        changed[slot], changed[slot+1] = changed[slot+1], changed[slot]
        successor, ext_new = whole_contact_recount(changed, word, rank, focus, shared)
        assert prior == literal
        delta = prior.copy()
        delta.subtract(successor)
        exterior_delta = Counter(ext_old)
        exterior_delta.subtract(ext_new)
        assert all(delta[r] == exterior_delta[r] for r in delta.keys() | exterior_delta.keys() if r)
        quote = rows.pop((ta, tb))
        assert tuple(quote["old_exterior_ranks"]) == ext_old and tuple(quote["new_exterior_ranks"]) == ext_new
        signatures.add((ext_old, ext_new))
        saving = {r: copies*n for r, n in delta.items() if n}
        dl, du = price(saving, k)
        assert F(quote["delta_price"][0]) <= dl <= du <= F(quote["delta_price"][1])
        next_paid, next_targets, _ = full_bill(word, caller, successor, rank)
        assert next_targets == targets
        next_signed = next_targets.copy()
        next_signed.subtract(next_paid)
        _, margin = price(next_signed, k)
        assert margin <= F(quote["complete_margin_upper"]) < 0
        verified.append({"events":[ta,tb],"shared_roles":sorted(shared),
                         "old_exterior_ranks":ext_old,"new_exterior_ranks":ext_new,
                         "per_copy_old_minus_new":{r:n for r,n in delta.items() if n},
                         "independent_complete_margin_upper":str(margin)})
    assert not rows and census == lead["counts"] and len(signatures) == lead["signature_count"] == 3
    assert len(verified) == 6
    return {"status":"PASS_INDEPENDENT_ROUND35_ADD_EXCHANGE",
            "head":HEAD,"source_sha256":PINS,"lead_receipt_sha256":sha256(declared_raw).hexdigest(),
            "crossing_upper":str(k),"counts":dict(census),"signature_count":len(signatures),
            "original_native_paid":sum(literal.values()),"complete_paid":sum(paid.values()),
            "complete_productive":sum(targets.values()),"original_margin_interval":[str(base_l),str(base_u)],
            "verified":verified,"unresolved":0,"physical_site_tests":0,
            "controls":["REJECT_OMITTED_LITERAL_PAID_MOVE"]}


if __name__ == "__main__":
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("source_root", type=Path)
    parser.add_argument("lead_receipt", type=Path)
    args = parser.parse_args()
    alarm(90)
    print(json.dumps(run(args.source_root, args.lead_receipt),indent=2,sort_keys=True))
    alarm(0)
