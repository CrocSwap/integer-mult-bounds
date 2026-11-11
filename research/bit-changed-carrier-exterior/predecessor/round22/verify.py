"""Round 22 causal read-only prebirth stocks, exact F2 quotient and matroid gate."""
from argparse import ArgumentParser
from collections import defaultdict, deque
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path
from time import monotonic


NATIVE = "research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz"
INVOICE = "research/paired-query-only-bit/EFREE-RESULT.json"


def encoded(indices):
    return sum(1 << i for i in indices)


def positions(value):
    result = []
    while value:
        bit = value & -value
        result.append(bit.bit_length()-1)
        value ^= bit
    return result


def insert(basis, row, tag=0):
    while row:
        p = row.bit_length()-1
        if p not in basis:
            basis[p] = row, tag
            return True, tag
        v, g = basis[p]
        row ^= v
        tag ^= g
    return False, tag


def reduce(basis, row):
    rem = tag = 0
    while row:
        p = row.bit_length()-1
        if p in basis:
            v, g = basis[p]
            row ^= v
            tag ^= g
        else:
            b = 1 << p
            row ^= b
            rem ^= b
    return rem, tag


def rnk(rows):
    basis = {}
    for v in rows:
        insert(basis, v)
    return len(basis)


def intersection_projection(rows, terminal):
    """Eliminate V's image outside W while retaining each literal row expression."""
    outside, quotient = {}, {}
    for row in rows:
        residual, _ = reduce(terminal, row)
        independent, inside = insert(outside, residual, row)
        if not independent:
            rem, coeff = reduce(terminal, inside)
            assert rem == 0
            insert(quotient, coeff, inside)
    return len(rows)-len(outside), [quotient[k] for k in sorted(quotient)]


def transversal(bases):
    """Matroid intersection. Return maximum independent representatives and Rado witness."""
    nodes = [(i, v, r) for i, part in enumerate(bases) for v, r in part]
    by_part = defaultdict(list)
    for e, (i, _, _) in enumerate(nodes):
        by_part[i].append(e)
    current = set()
    while True:
        represented = {nodes[e][0] for e in current}
        linear = {}
        for e in sorted(current):
            assert insert(linear, nodes[e][1], 1 << e)[0]
        pred = {e: None for e, (i, _, _) in enumerate(nodes) if i not in represented}
        queue = deque(pred)
        sink = None
        while queue:
            e = queue.popleft()
            if e in current:
                nxt = (f for f in by_part[nodes[e][0]] if f != e)
            else:
                rem, support = reduce(linear, nodes[e][1])
                if rem:
                    sink = e
                    break
                nxt = positions(support)
            for f in nxt:
                if f not in pred:
                    pred[f] = e
                    queue.append(f)
        if sink is None:
            restricted = sorted((set(range(len(bases))) - represented) |
                                {nodes[e][0] for e in current if e in pred})
            restricted_rank = rnk(v for i in restricted for v, _ in bases[i])
            assert len(current) == len(bases)-len(restricted)+restricted_rank
            return [nodes[e] for e in sorted(current)], restricted, restricted_rank
        e = sink
        before = len(current)
        while e is not None:
            current.symmetric_difference_update([e])
            e = pred[e]
        assert len(current) == before+1
        assert len({nodes[e][0] for e in current}) == len(current)
        assert rnk(nodes[e][1] for e in current) == len(current)


def endpoint_gate(bases, deadline):
    """Exhaust every option within disjoint support blocks of the same map."""
    n = len(bases)
    neighbors = [set([i]) for i in range(n)]
    choices = []
    for i, part in enumerate(bases):
        span = [0]
        for v, _ in part:
            span += [v ^ w for w in span]
            for j in positions(v):
                neighbors[i].add(j)
                neighbors[j].add(i)
        assert len(span) == len(set(span)) and 1 << i in span
        choices.append(sorted(span))
    found = set()
    blocks = []
    for i in range(n):
        if i in found:
            continue
        block = {i}
        todo = [i]
        while todo:
            new = neighbors[todo.pop()] - block
            block.update(new)
            todo.extend(sorted(new))
        found.update(block)
        blocks.append(sorted(block))

    reports = []
    for block in blocks:
        tested = feasible = best_nz = best_rank = 0
        witness = tuple(0 for _ in block)
        for delta in product(*(choices[i] for i in block)):
            tested += 1
            if monotonic() >= deadline:
                raise TimeoutError("same table endpoint consistency checks exceeded cap")
            final = [(1 << i) ^ v for i, v in zip(block, delta)]
            if rnk(final) != len(block):
                continue
            feasible += 1
            best_nz = max(best_nz, sum(bool(v) for v in delta))
            independent = rnk(delta)
            if independent > best_rank:
                best_rank = independent
                witness = delta
        assert feasible >= 1 and best_rank <= best_nz
        reports.append({"banks": block, "tested_choices": tested,
                        "endpoint_preserving_choices": feasible,
                        "maximum_nonzero_changes": best_nz,
                        "maximum_independent_return_directions": best_rank,
                        "rank_attaining_deltas": [positions(v) for v in witness]})
    return {"blocks": reports, "endpoint_preserving_nonzero_upper": sum(b["maximum_nonzero_changes"] for b in reports),
            "endpoint_preserving_independent_upper": sum(b["maximum_independent_return_directions"] for b in reports),
            "singleton_own_pivot_only": sum(len(b["banks"]) == 1 for b in reports),
            "own_pivot_only_delta_spaces": sum(len(part) == 1 for part in bases)}


def controls():
    # One initial greedy choice must be replaced to admit the second bank.
    a = transversal([[(1, 1), (2, 2)], [(1, 1)]])
    assert len(a[0]) == 2 and (0, 2, 2) in a[0]
    a = transversal([[(1, 1)], [(1, 1)], [], [(2, 2)]])
    assert len(a[0]) == 2 and len(a[1]) == 3 and a[2] == 1
    # Two raw outside-contaminated sources can yield one pure terminal direction.
    w = {}
    insert(w, 1, 0)
    insert(w, 2, 1)
    assert intersection_projection([5, 6], w) == (1, [(1, 3)])
    assert intersection_projection([5], w) == (0, [])
    # Two rows differing by an unchanged arrival have the same quotient.
    assert reduce(w, 3) == reduce(w, 2) == (0, 1)
    # A bare own-pivot direction cancels the original row under additive replacement.
    endpoint = endpoint_gate([[(1, 1)], [(2, 2), (1, 1)]], monotonic()+1)
    assert endpoint["endpoint_preserving_independent_upper"] == 1
    assert endpoint["endpoint_preserving_nonzero_upper"] == 1
    # Invertible endpoint can permit two off-diagonal-looking changes only when
    # their diagonal/cross-slot combination preserves the full row rank.
    endpoint = endpoint_gate([[(1, 1), (2, 2)], [(1, 1), (2, 2)]], monotonic()+1)
    assert endpoint["endpoint_preserving_independent_upper"] == 2


def timeline(w, deadline):
    n = w["public"]
    q = w["start"]+[None]*w["owned_fields"]
    x = [1 << j for j in range(n)]+[0]*w["owned_fields"]
    chart = defaultdict(dict)
    moves = {}
    touch = defaultdict(list)

    def observe(j, cut, kind):
        if x[j]:
            chart[q[j]].setdefault((j, x[j]), (cut, kind))

    for j in range(n):
        observe(j, 0, "initial")
    for t, (op, j, *a) in enumerate(w["program"]):
        if t % 1024 == 0 and monotonic() >= deadline:
            raise TimeoutError("one 22-bank prebirth map exceeded its cap")
        touch[j].append(t)
        if op == "MOVE":
            f, g = a
            assert q[j] == f and f != 1
            moves[t] = (j, f, g, x[j])
            q[j] = g
        elif op == "ADD":
            k, f = a
            assert q[j] == q[k] == f
            touch[k].append(t)
            x[j] ^= x[k]
        elif op == "SWAP":
            k, = a
            touch[k].append(t)
            q[j], q[k] = q[k], q[j]
            x[j], x[k] = x[k], x[j]
            observe(k, t+1, op)
        elif op == "INIT":
            assert q[j] is None and a[0] != 1
            q[j], x[j] = a[0], 0
        else:
            assert op == "CLEAR" and q[j] == a[0] != 1
            q[j], x[j] = None, 0
        observe(j, t+1, op)
    endpoint = [1 << j for j in range(n)]+[0]*w["owned_fields"]
    for j in range(111):
        endpoint[111+j] ^= 1 << j
    assert x == endpoint and q == w["final"]+[None]*w["owned_fields"]
    assert len(moves) == 2871
    windows = {}
    for t, (j, _, _, _) in moves.items():
        k = touch[j].index(t)
        windows[t] = [touch[j][k-1]+1 if k else 0,
                      touch[j][k+1] if k+1 < len(touch[j]) else len(w["program"])]
    return chart, moves, windows, endpoint


def library(mark, observations, moves, windows, retime):
    t = mark["event"]
    owner, source, target, original = moves[t]
    assert target == 1 and original == encoded(mark["prefix_input"])
    assert mark["pivot_quiet_window"] == windows[t]
    horizon = windows[t][1] if retime else t
    seen = {}
    routes = set()

    def add_chart(f):
        for (j, row), (cut, kind) in observations.get(f, {}).items():
            if cut <= horizon and (f, j, row) != (source, owner, original):
                witness = ("physical", f, cut, j, kind)
                seen.setdefault(row, witness)
                routes.add(witness)

    add_chart(source)
    for variant in mark["variants"]:
        f = variant["literal_chart"]
        if f is not None:
            add_chart(f)
        for e in variant["virtual_bank_events"]:
            if e == t:
                continue
            j, g, last, row = moves[e]
            assert last == 1
            available = windows[e][0] if retime else e+1
            if available <= horizon:
                witness = ("virtual", g, available, j, e)
                seen.setdefault(row, witness)
                routes.add(witness)
    return seen, len(routes), horizon


def raw_basis(rows):
    basis = {}
    for row in rows:
        insert(basis, row)
    return [value for value, _ in basis.values()]


def scope(marks, observations, moves, windows, terminal, retime, deadline):
    bank_rows, bases = [], []
    for mark in marks:
        source, count, horizon = library(mark, observations, moves, windows, retime)
        rows = raw_basis(sorted(source))
        inside, projected = intersection_projection(rows, terminal)
        bases.append(projected)
        digest = sha256(json.dumps(sorted((v, w) for v, w in source.items()), separators=(",", ":")).encode()).hexdigest()
        # Physical caches are observations at specific clocks. Virtual entries
        # are old paid input rows with an exact compatible midpoint certificate.
        bank_rows.append({"event": mark["event"], "deadline_cut": horizon,
                          "observed_coefficient_rows": len(source), "route_observations": count,
                          "source_rank": len(rows), "source_intersection_terminal_rank": inside,
                          "projected_rank": len(projected), "source_provenance_sha256": digest,
                          "source_witnesses": [{"row": positions(v), "path": list(w)}
                                               for v, w in sorted(source.items())],
                          "quotient_basis": [positions(c) for c, _ in projected]})
        if monotonic() >= deadline:
            raise TimeoutError("one 22-bank prebirth map exceeded its cap")
    assignment, restricted, subrank = transversal(bases)
    endpoint = endpoint_gate(bases, deadline)
    return {"scope": "quiet-window union" if retime else "literal birth clock",
            "banks": bank_rows, "compatible_stock_upper": len(assignment),
            "independent_assignment": [{"bank": i, "event": marks[i]["event"],
                                        "quotient": positions(v), "terminal_row": positions(r)}
                                       for i, v, r in assignment],
            "rado_restricted_banks": restricted, "rado_restricted_rank": subrank,
            "rado_exact_upper": len(marks)-len(restricted)+subrank,
            "endpoint_consistency": endpoint,
            "unresolved_target_clearing_assignments_within_scope": 0 if endpoint["endpoint_preserving_independent_upper"] < 21 else 22}


def main(root, seconds):
    deadline = monotonic()+seconds
    controls()
    pins = {}
    for line in Path(__file__).with_name("SOURCES.tsv").read_text().splitlines():
        name, digest, _ = line.split("\t")
        if name in pins:
            raise ValueError(f"duplicate source path {name}")
        pins[name] = digest

    def read(name):
        data = (root/name).read_bytes()
        if sha256(data).hexdigest() != pins[name]:
            raise ValueError(f"SHA-256 mismatch: {name}")
        return data

    for key in pins:
        read(key)
    peer = json.loads(read("pr7244/PROPOSED-CLAIM.json"))
    assert peer["kappa"] == "455671545979/125000000000000"
    assert peer["complex_BIT_premise"] == "376669/100000000"
    w = json.loads(gzip.decompress(read(NATIVE)))
    invoice = json.loads(read(INVOICE))
    maps = json.loads(read("pr7209/RESULT.json"))["bank_maps"]
    assert len(maps) == 22
    dims = {int(i): s["dim"] for i, s in w["frames"].items()}
    assert [i for i in dims if dims[i] == 8] == [1] and 1 not in w["start"]
    chart, moves, windows, endpoint = timeline(w, deadline)
    arrivals = {e: row for e, (_, _, g, row) in moves.items() if g == 1}
    chosen = [m["event"] for m in maps]
    assert len(arrivals) == 545 and len(set(chosen)) == 22
    basis = {}
    for t, row in arrivals.items():
        if t not in chosen:
            assert insert(basis, row)[0]
    assert len(basis) == 523
    for j, t in enumerate(chosen):
        assert dims[moves[t][1]] == 6
        assert insert(basis, arrivals[t], 1 << j)[0]
    assert len(basis) == 545
    assert all(not reduce(basis, row)[0] for f, row in zip(w["final"], endpoint) if f == 1)
    assert rnk(row for f, row in zip(w["final"], endpoint) if f == 1) == 545
    literal = scope(maps, chart, moves, windows, basis, False, deadline)
    quiet = scope(maps, chart, moves, windows, basis, True, deadline)
    assert literal["compatible_stock_upper"] <= quiet["compatible_stock_upper"]
    spec = spec_from_file_location("prior", root/"pr7209/verify.py")
    p = module_from_spec(spec)
    spec.loader.exec_module(p)
    ledger = p.terminal_ledger(w, dims)
    for s in (literal, quiet):
        s["raw_quotient_price"] = p.prices(root, invoice, w, dims, ledger, s["compatible_stock_upper"])
        endpoint = s["endpoint_consistency"]
        s["endpoint_preserving_price"] = p.prices(root, invoice, w, dims, ledger, endpoint["endpoint_preserving_independent_upper"])
        s["endpoint_preserving_nonzero_price"] = p.prices(root, invoice, w, dims, ledger, endpoint["endpoint_preserving_nonzero_upper"])
    return {"status": "NO VERIFIED GAIN", "seconds_cap": seconds, "pins": pins,
            "target": "10018846261809/2500000000000000", "retained_BIT_premise": peer["complex_BIT_premise"],
            "banks": len(maps), "pending_census_cases": 0, "new_sites": 0,
            "unchanged_terminal_rank": 523, "required_terminal_rank": 545,
            "scope": [literal, quiet]}


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--seconds", type=int, default=480)
    args = parser.parse_args()
    if not 1 <= args.seconds <= 480:
        parser.error("--seconds must be in 1..480")
    print(json.dumps(main(args.root, args.seconds), sort_keys=True, indent=2))
