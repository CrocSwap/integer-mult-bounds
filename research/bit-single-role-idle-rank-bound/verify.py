"""Independent GF(128) rank and literal invoice audit for BIT idle pairs."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from functools import cache
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

TARGET = Q(10018846261809, 2500000000000000)
PINS = {
    "preflight/EFREE-CALLER.json.gz": "757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b",
    "native/inputs/WORD.json.gz": "51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78",
    "native/inputs/INVOICE.json": "a46b6c6040f75184cab5467656811ad988c216e3bc8e44d595a5015b6e49620b",
}


def unique(items):
    out = dict(items)
    assert len(out) == len(items), "duplicate JSON key"
    return out


def load_inputs(preflight, native, repo):
    if repo is None:
        paths = (preflight / "EFREE-CALLER.json.gz", native / "inputs/WORD.json.gz",
                 native / "inputs/INVOICE.json")
    else:
        source = repo / "research/paired-query-only-bit"
        paths = (source / "EFREE-CALLER.json.gz", source / "retained/inputs/BIT-NATIVE-WORD.json.gz",
                 source / "EFREE-RESULT.json")
    data = {}
    for (name, expected), path in zip(PINS.items(), paths, strict=True):
        blob = path.read_bytes()
        assert sha256(blob).hexdigest() == expected, f"changed source {name}"
        if path.suffix == ".gz":
            blob = gzip.decompress(blob)
        data[name] = json.loads(blob, object_pairs_hook=unique)
    return list(data.values())


class GF128:
    # X generates all nonzero elements in F2[X]/(X^7 + X + 1).
    # Verifying the complete cycle proves that the quotient is a field.
    polynomial = 0x83

    def __init__(self):
        self.powers = [1]
        for _ in range(127):
            x = self.powers[-1] << 1
            self.powers.append(x ^ self.polynomial if x & 128 else x)
        assert self.powers[-1] == 1 and set(self.powers[:-1]) == set(range(1, 128))
        self.logs = {x: i for i, x in enumerate(self.powers[:-1])}

    def mul(self, x, y):
        if not x or not y:
            return 0
        return self.powers[(self.logs[x] + self.logs[y]) % 127]

    def product(self, values):
        result = 1
        for value in values:
            result = self.mul(result, value)
        return result


def event_ops(caller, f, probe):
    for code, *args in caller["events"]:
        if code in ("ADD", "QUERY"):
            d, s = args
            yield (code, d, s, 1)
        elif code == "SWAP":
            d, s = args
            yield (code, d, s, 1)
        elif code == "LOCAL":
            stage, s, d = args
            yield (code, d, s, probe[stage - 1])
        else:
            assert code == "IDLE_ONE"
            d, stages = args
            yield (code, d, d, f.product(probe[s - 1] for s in stages))


def apply(f, vector, op, transposed=False):
    code, d, s, a = op
    if code == "SWAP":
        vector[d], vector[s] = vector[s], vector[d]
    elif code == "IDLE_ONE":
        vector[d] = f.mul(a, vector[d])
    elif code == "LOCAL":
        if transposed:
            vector[s], vector[d] = f.mul(a, vector[s] ^ vector[d]), f.mul(a, vector[d])
        else:
            vector[s], vector[d] = f.mul(a, vector[s]), f.mul(a, vector[d] ^ vector[s])
    else:
        assert code in ("ADD", "QUERY")
        if transposed:
            vector[s] ^= vector[d]
        else:
            vector[d] ^= vector[s]


def unit(n, i):
    return [int(j == i) for j in range(n)]


def evaluate(f, n, ops, omit=()):
    columns = []
    for i in range(n):
        v = unit(n, i)
        for t, op in enumerate(ops):
            if t not in omit:
                apply(f, v, op)
        columns.append(v)
    return columns


def pair_factors(f, n, ops, i, j):
    _, r, _, a = ops[i]
    _, s, _, b = ops[j]
    left = unit(n, r)
    right = unit(n, s)
    for t in range(i + 1, j):
        apply(f, left, ops[t])
    for t in range(j - 1, i, -1):
        apply(f, right, ops[t], transposed=True)
    l = next(((u, x) for u, x in enumerate(left) if u != s and x), None)
    h = next(((v, x) for v, x in enumerate(right) if v != r and x), None)
    if a == 1 or b == 1 or l is None or h is None:
        return None
    # Minor of the inner difference on rows (l[0], s), columns (r, h[0]).
    minor = f.product((a ^ 1, b ^ 1, l[1], h[1]))
    assert minor
    return {"left_off_axis": l, "right_off_axis": h, "minor": minor}


def rank_check(caller):
    f = GF128()
    n = caller["roles"]
    assert n == len(caller["diagonal"]) == 38 and caller["stages"] == 18
    assert caller["native_per_stage"] == 2 and caller["ports"] == 111
    probe = tuple(f.powers[1:19])
    ops = tuple(event_ops(caller, f, probe))
    original = evaluate(f, n, ops)
    expected = []
    for j, target in enumerate(caller["diagonal"]):
        col = unit(n, j)
        col[j] = f.product(probe[s - 1] for s in target["stages"])
        expected.append(col)
    assert original == expected
    idles = {i: set(e[2]) for i, e in enumerate(caller["events"]) if e[0] == "IDLE_ONE"}
    assert len(idles) == 32
    assert evaluate(f, n, ops, (min(idles),)) != original, "omitted paid idle not detected"
    toy = (("IDLE_ONE", 0, 0, 2), ("IDLE_ONE", 1, 1, 3))
    assert pair_factors(f, 2, toy, 0, 1) is not None
    repeated = (("IDLE_ONE", 0, 0, 2), ("IDLE_ONE", 0, 0, 3))
    assert pair_factors(f, 2, repeated, 0, 1) is None
    pairs = [(i, j) for i, j in combinations(idles, 2) if not idles[i] & idles[j]]
    assert len(pairs) == 256
    out = []
    for i, j in pairs:
        w = pair_factors(f, n, ops, i, j)
        assert w is not None, f"inconclusive specialization {i},{j}"
        out.append({"removed": [i, j], **w})
    return {"field": "F2[X]/(X^7+X+1)", "q": 1, "probe": probe,
            "baseline_coefficients": n * n, "pair_inventory": 496,
            "overlapping_masks_outside_scope": 240, "disjoint_pair_rank_two": len(out),
            "new_clocks_scanned": 0, "unresolved": 0, "minor_witnesses": out,
            "controls": ["omitted old idle", "independent diagonal axes", "repeated diagonal axis"]}


def linear_rank(rows):
    basis = {}
    for row in rows:
        v = list(row)
        for j in range(len(v)):
            x = v[j]
            if not x:
                continue
            if j in basis:
                v = [a - x * b for a, b in zip(v, basis[j], strict=True)]
            else:
                basis[j] = [a / x for a in v]
                break
    return len(basis)


def native_bill(word, drop_move=None):
    n = word["public"]
    m = word["owned_fields"]
    basis = {int(k): tuple(tuple(map(Q, row)) for row in v["B"])
             for k, v in word["frames"].items()}
    dims = {int(k): v["dim"] for k, v in word["frames"].items()}
    assert all(dims[k] == len(rows) == linear_rank(rows) for k, rows in basis.items())

    @cache
    def move_rank(a, b):
        assert dims[a] != dims[b]
        assert linear_rank(basis[a] + basis[b]) == max(dims[a], dims[b])
        return abs(dims[a] - dims[b])

    current = word["start"] + [None] * m
    last = current.copy()
    rows = [1 << i for i in range(n)] + [0] * m
    paid = Counter()
    literal = Counter()
    contacts = Counter()

    def touch(slot, frame):
        assert current[slot] == frame and last[slot] is not None
        contacts[last[slot], frame] += 1
        last[slot] = frame

    for t, (op, d, *args) in enumerate(word["program"]):
        if op == "MOVE":
            if t == drop_move:
                continue
            a, b = args
            assert current[d] == a
            paid[move_rank(a, b)] += 1
            literal[a, b] += 1
            current[d] = b
        elif op == "SWAP":
            s, = args
            for seq in (current, last, rows):
                seq[d], seq[s] = seq[s], seq[d]
        elif op == "INIT":
            assert d >= n and current[d] is None
            current[d], = args
            last[d] = current[d]
            rows[d] = 0
        elif op == "ADD":
            s, frame = args
            touch(d, frame)
            if s != d:
                touch(s, frame)
            rows[d] ^= rows[s]
        else:
            assert op == "CLEAR" and d >= n
            frame, = args
            touch(d, frame)
            current[d] = last[d] = None
            rows[d] = 0
    assert current == word["final"] + [None] * m
    expected = [1 << i for i in range(n)] + [0] * m
    for i in range(111):
        expected[111 + i] ^= 1 << i
    assert rows == expected
    for d, f in enumerate(word["final"]):
        touch(d, f)
    assert Counter({(a, b): c for (a, b), c in contacts.items() if a != b}) == literal
    assert sum(contacts.values()) == 62474
    targets = Counter()
    for a, b in zip(word["start"][222:], word["final"][222:], strict=True):
        assert dims[b] > dims[a]
        targets[move_rank(a, b)] += 1
    return paid, targets, sum(contacts.values())


def whole_bill(caller, native, invoice):
    n_paid, n_target, contacts = native_bill(native)
    assert sum(n_paid.values()) == 2871 and sum(n_target.values()) == 437
    assert n_paid == Counter({int(r): c for r, c in invoice["native_paid"].items()})
    assert n_target == Counter({int(r): c for r, c in invoice["native_helpers"].items()})
    ports, body = caller["ports"], caller["body_rank"]
    stages = Counter(e[1] for e in caller["events"] if e[0] == "LOCAL")
    assert stages == Counter({i: 2 for i in range(1, 19)})
    copies = stages.total()
    assert copies == invoice["native_calls"] == 36 and body == 7
    paid = Counter({r: copies * c for r, c in n_paid.items()})
    targets = Counter({r: copies * c for r, c in n_target.items()})
    idle = Counter()
    for code, *args in caller["events"]:
        if code == "IDLE_ONE":
            mask = args[-1]
            assert mask and len(mask) == len(set(mask))
            idle[body * len(mask)] += ports
        elif code == "QUERY":
            paid[1] += ports
    paid.update(idle)
    for d in caller["diagonal"]:
        targets[d["q"] + body * len(d["stages"])] += ports
    assert paid == Counter({int(r): c for r, c in invoice["paid"].items()})
    assert targets == Counter({int(r): c for r, c in invoice["targets"].items()})
    signed = {r: targets[r] - paid[r] for r in sorted(targets.keys() | paid.keys())}
    assert paid.total() == 107352 and targets.total() == 19950
    assert sum(r * c for r, c in signed.items()) == 1506
    omitted = next(t for t, e in enumerate(native["program"]) if e[0] == "MOVE")
    try:
        native_bill(native, drop_move=omitted)
    except AssertionError:
        pass
    else:
        raise AssertionError("omitted native payment survived")
    return {"native_copies": copies, "literal_native_moves": n_paid.total(),
            "native_contacts": contacts, "paid": paid, "targets": targets, "rank_surplus": 1506,
            "paid_total": paid.total(), "target_total": targets.total(), "idle_hist": idle,
            "signed": signed, "omitted_move_control": omitted}


def log_unit(x):
    t = (x - 1) / (x + 1)
    assert 0 <= t <= Q(1, 3)
    low = sum(2 * t**(2 * j + 1) / (2 * j + 1) for j in range(72))
    return low, low + 2 * t**145 / (145 * (1 - t * t))


GRID = 10**58


def downward(x):
    return Q((x * GRID).__floor__(), GRID)


def upward(x):
    return Q((x * GRID).__ceil__(), GRID)


def exp_at(x, last):
    assert 0 <= x < 1
    term, total = Q(1), Q(1)
    for j in range(1, last + 1):
        term *= -x / j
        total += term
    return total


@cache
def power(r):
    m = r.bit_length() - 1
    a, b = log_unit(Q(r, 1 << m))
    c, d = log_unit(Q(2))
    x0 = downward(TARGET * (a + m * c))
    x1 = upward(TARGET * (b + m * d))
    return downward(r * exp_at(x1, 43)), upward(r * exp_at(x0, 42))


def cost(hist):
    intervals = [sorted(c * x for x in power(r)) for r, c in hist.items()]
    return tuple(sum(row[i] for row in intervals) for i in (0, 1))


def audit(preflight, native, repo):
    caller, word, invoice = load_inputs(preflight, native, repo)
    assert invoice["caller_sha256"] == PINS["preflight/EFREE-CALLER.json.gz"]
    assert invoice["native_source_sha256"] == PINS["native/inputs/WORD.json.gz"]
    rank = rank_check(caller)
    bill = whole_bill(caller, word, invoice)
    net = cost(bill["signed"])
    discount = 1 - power(2)[0] / 2
    free_upper = discount * cost(bill["idle_hist"])[1]
    assert net[1] < 0 and net[1] + free_upper > 0
    assert Q(60) < -net[1] < Q(61) and Q(305) < free_upper < Q(306)
    return {"target": str(TARGET), "pins": PINS, "rank": rank, "invoice": bill,
            "signed_moment_interval": list(map(str, net)),
            "shortfall_lower": str(-net[1]), "shortfall_decimal": float(-net[1]),
            "whole_free_optimistic_upper": str(free_upper),
            "whole_free_upper_decimal": float(free_upper),
            "whole_realizable_upper": "0", "physical_sites": 0}


def main():
    p = ArgumentParser()
    p.add_argument("preflight", type=Path, nargs="?")
    p.add_argument("native", type=Path, nargs="?")
    p.add_argument("--repo-root", type=Path)
    args = p.parse_args()
    if args.repo_root is None and (args.preflight is None or args.native is None):
        p.error("provide both replay roots or --repo-root")
    if args.repo_root is not None and (args.preflight is not None or args.native is not None):
        p.error("provide replay roots or --repo-root")
    print(json.dumps(audit(args.preflight, args.native, args.repo_root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
