"""Independent exact read-lineage, geometry and disjoint-price audit."""

from argparse import ArgumentParser
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
TARGET = "10018846261809/2500000000000000"
TRIAL = "1002040748181/250000000000000"
SCALE = 10**49


def read_inputs(root):
    pins = {}
    sources = HERE / "replay/bit/SOURCES.tsv"
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


def annihilator(rows):
    """Exact RREF, then a basis of the right nullspace of each chart."""
    matrix = [list(map(Fraction, row)) for row in rows]
    pivots = []
    for col in range(8):
        pivot = len(pivots)
        hit = next((i for i in range(pivot, len(matrix)) if matrix[i][col]), None)
        if hit is None:
            continue
        matrix[hit], matrix[pivot] = matrix[pivot], matrix[hit]
        a = matrix[pivot]
        p = a[col]
        matrix[pivot] = [x / p for x in a]
        for i, row in enumerate(matrix):
            if i != pivot and row[col]:
                b = row[col]
                matrix[i] = [x - b*y for x, y in zip(row, matrix[pivot], strict=True)]
        pivots.append(col)
    assert len(pivots) == len(rows)
    normals = []
    for f in set(range(8)) - set(pivots):
        v = [Fraction(0)] * 8
        v[f] = Fraction(1)
        for i, p in enumerate(pivots):
            v[p] = -matrix[i][f]
        normals.append(v)
    return normals


def verify_incidence(word, moves, runs):
    ranks = {int(f): v["dim"] for f, v in word["frames"].items()}
    bases = {int(f): [[Fraction(x) for x in row] for row in v["B"]]
             for f, v in word["frames"].items()}
    assert all(len(bases[f]) == r for f, r in ranks.items())

    @cache
    def normals(frame):
        return annihilator(bases[frame])

    @cache
    def endpoint_type(src, dst):
        if src == dst:
            return "identical"
        if ranks[src] == ranks[dst]:
            return "equal_rank_distinct"
        low, high = sorted((src, dst), key=ranks.__getitem__)
        if any(sum(a*b for a, b in zip(row, normal, strict=True))
               for row in bases[low] for normal in normals(high)):
            return "nonnested"
        return "nested"

    total = Counter()
    domains = []
    for chain in runs:
        starting = defaultdict(list)
        for i, a in enumerate(chain):
            for j in range(i + 1, len(chain)):
                b = chain[j]
                src, dst = moves[a][0], moves[b][1]
                kind = endpoint_type(src, dst)
                total[kind] += 1
                if kind in ("identical", "nested"):
                    delta = Counter(abs(ranks[moves[t][0]] - ranks[moves[t][1]])
                                    for t in chain[i:j+1])
                    if src != dst:
                        delta[abs(ranks[src] - ranks[dst])] -= 1
                    starting[i].append((j+1, (a, b, src, dst), delta))
        domains.append((len(chain), starting))
    old = Counter(abs(ranks[src] - ranks[dst]) for src, dst, _ in moves.values())
    return total, domains, old, ranks


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


def optimize(domains, copies, k, declared):
    valid = {}
    totals = [Fraction(0), Fraction(0)]
    for chain, (n, starts) in enumerate(domains):
        def extreme(side):
            suffix = [Fraction(0)] * (n+1)
            for i in range(n-1, -1, -1):
                suffix[i] = max(
                    [suffix[i+1]]
                    + [suffix[j] + cost(delta, k)[side] for j, _, delta in starts[i]]
                )
            return suffix[0]
        for side in (0, 1):
            totals[side] += copies*extreme(side)
        for i, intervals in starts.items():
            for j, key, delta in intervals:
                assert key not in valid
                valid[key] = (chain, i, j, delta)
    seen = set()
    chosen = Counter()
    for item in declared:
        key = tuple(item)
        if key not in valid:
            raise ValueError(f"invalid chosen interval {item}")
        chain, i, j, delta = valid[key]
        paid = {(chain, x) for x in range(i, j)}
        if seen & paid:
            raise ValueError(f"overlapping chosen interval {item}")
        seen.update(paid)
        chosen.update(delta)
    return totals, cost({r: copies*n for r, n in chosen.items()}, k)


def intersect(a, b):
    return max(a[0], b[0]) <= min(a[1], b[1])


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


def audit(root, receipt):
    word, invoice, pins = read_inputs(root)
    assert receipt["status"] == "PASS_WHOLE_WORD_FUSION_UPPER"
    assert receipt["pins"] == pins
    assert invoice["native_source_sha256"] == pins[WORD]
    moves, runs, ownership = walk(word)
    counts, domains, old, ranks = verify_incidence(word, moves, runs)
    signed, copies = profile(invoice, old, word, ranks)
    path_lengths = Counter(map(len, runs))
    assert {str(r): n for r, n in path_lengths.items()} == receipt["path_length_histogram"]
    assert {str(r): n for r, n in old.items()} == receipt["charged_ranks"]
    assert receipt["native_paid_moves"] == sum(old.values()) and receipt["native_instances"] == copies
    assert receipt["physical_sites"] == 0
    audit_result = {}
    for trial, declared in receipt["result"].items():
        k = Fraction(trial)
        expected_case_count = sum(counts.values())
        expected_eligible_count = counts["nested"] + counts["identical"]
        if declared["cases_visited"] != expected_case_count or declared["eligible_intervals"] != expected_eligible_count:
            raise ValueError("incorrect exhaustive incidence counters")
        savings, chosen = optimize(domains, copies, k, declared["optimistic_argmax"])
        baseline = cost(signed, k)
        net = [a+b for a,b in zip(baseline, savings, strict=True)]
        for field, v in (("saving_interval", savings), ("raw_comparator_net", baseline),
                         ("net_after_free_fusion", net)):
            if not intersect(v, list(map(Fraction, declared[field]))):
                raise ValueError(f"forged {field}")
        if not intersect(chosen, list(map(Fraction, declared["saving_interval"]))):
            raise ValueError("selected intervals fail to realize claimed upper at price precision")
        audit_result[trial] = {
            "baseline": list(map(str, baseline)),
            "saving": list(map(str, savings)),
            "net": list(map(str, net)),
            "selected_interval_saving": list(map(str, chosen)),
        }
    assert TARGET in audit_result
    if Fraction(audit_result[TARGET]["net"][1]) < 0:
        assert set(audit_result) == {TARGET}
    return {
        "status": "PASS_INDEPENDENT_FUSION_AUDIT",
        "paid_moves": len(moves),
        "ownership": dict(ownership),
        "paths": len(runs),
        "incidence_by_endpoint": dict(counts),
        "source_sha256": pins[WORD],
        "invoice_sha256": pins[INVOICE],
        "independent_result": audit_result,
    }


def control():
    e1 = [1, 0, 0, 0, 0, 0, 0, 0]
    e2 = [0, 1, 0, 0, 0, 0, 0, 0]
    frames = {"0": {"dim": 0, "B": []}, "1": {"dim": 1, "B": [e1]},
              "2": {"dim": 2, "B": [e1, e2]}}
    moves = {0: (0, 1, 0), 2: (1, 2, 0), 4: (2, 0, 0)}
    counts, domains, _, _ = verify_incidence({"frames": frames}, moves, [(0, 2, 4)])
    assert counts == {"nested": 2, "identical": 1}
    savings, selected = optimize(domains, 36, Fraction(TARGET), [(0, 4, 0, 0)])
    assert tuple(savings) == selected and savings[0] > 0
    try:
        optimize(domains, 36, Fraction(TARGET), [(0, 2, 0, 2), (0, 4, 0, 0)])
    except ValueError as error:
        assert "overlapping" in str(error)
    else:
        raise AssertionError("overlap control accepted a double-spent paid MOVE")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("input_root", type=Path)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    assert __debug__
    control()
    receipt = json.loads(args.receipt.read_bytes())
    print(json.dumps(audit(args.input_root, receipt), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
