"""Sparse rational replay at all cuts and projector certificate acceptance.

No predecessor checker or optimizer is imported.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import HERE, certificate, cli, digest, need, read, sources


def basis(frame):
    pivots = {}
    for value in frame:
        need(type(value) is int and 0 < value < 512, "binary frame value")
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    need(len(pivots) == len(frame), "dependent frame")
    for bit in sorted(pivots):
        for other in pivots:
            if other > bit and pivots[other] >> bit & 1:
                pivots[other] ^= pivots[bit]
    return tuple(pivots[bit] for bit in sorted(pivots))


def contained(left, right):
    pivots = {v.bit_length() - 1: v for v in right}
    for value in left:
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                return False
            value ^= pivots[bit]
    return True


def roots(fixture):
    result = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            result.add(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            result.add((1, *signs))
    removed = {tuple(r) for r in fixture["F0"] + fixture["C"]}
    need(len(result) == 120 and len(removed) == 16 and removed <= result,
         "P104 puncture binding")
    ports = sorted(result - removed)
    need(all(sum(p[i] * p[j] for p in ports) == 104 * (i == j)
             for i in range(8) for j in range(8)), "R R^T = 104 I")
    return ports


def insert(pivots, source):
    row = {i: Q(v) for i, v in source.items() if v}
    while row:
        pivot = min(row)
        factor = row[pivot]
        if pivot not in pivots:
            pivots[pivot] = {j: v / factor for j, v in row.items()}
            return True
        for j, value in pivots[pivot].items():
            new = row.get(j, Q(0)) - factor * value
            if new:
                row[j] = new
            else:
                row.pop(j, None)
    return False


def replay(data, terms):
    word = data["LOWRANK-WITNESS.json"]
    ports = roots(data["P104-FIXTURE.json"]["section4_explicit_P104"])
    names = list(word["initial_frames"])
    need(len(names) == len(set(names)) == 280 and
         names[:104] == ["X" + str(t) for t in range(104)], "boundary names")
    need({n for n in names if n.startswith("Y")} ==
         {"Y" + str(t) for t in range(104)}, "104 targets")
    state = {n: {j: Q(1)} for j, n in enumerate(names)}
    frames = {n: basis(f) for n, f in word["initial_frames"].items()}
    pools = [set() for _ in range(104)]
    identities, rows, occurrences = {}, [], [{} for _ in range(104)]
    requested = defaultdict(list)
    for index, (target, cut, reg, weight) in enumerate(terms):
        requested[cut].append((index, target, reg))
    contacts = {}

    def capture(cut):
        groups = defaultdict(list)
        for name, frame in frames.items():
            groups[frame].append(name)
        for group in groups.values():
            targets = [int(n[1:]) for n in group if n.startswith("Y")]
            if not targets:
                continue
            group_rows = {}
            for name in group:
                row = tuple(sorted(state[name].items()))
                if row not in identities:
                    identities[row] = len(rows)
                    rows.append(row)
                group_rows[name] = identities[row]
            for target in targets:
                for name, row_id in group_rows.items():
                    if name != "Y" + str(target):
                        pools[target].add(row_id)
                        occurrences[target].setdefault(row_id, (cut, name))
        for index, target, reg in requested[cut]:
            need(reg in state and reg != "Y" + str(target), "live other register")
            need(frames[reg] == frames["Y" + str(target)], "certificate chart contact")
            contacts[index] = tuple(sorted(state[reg].items()))

    profile, scalar = Counter(), Counter()
    capture(0)
    need(len(word["program"]) == 4058, "fixed word length")
    for index, event in enumerate(word["program"]):
        op, reg = event[:2]
        if op == "transport":
            _, _, old, new, rank = event
            old, new = basis(old), basis(new)
            need(reg in frames and frames[reg] == old, "transport entry")
            need(contained(old, new) or contained(new, old), "nested transport")
            need(type(rank) is int and rank == abs(len(old) - len(new)) > 0,
                 "transport rank")
            frames[reg] = new
            profile[rank] += 1
        elif op == "add":
            _, _, src, factor, frame = event
            need(reg != src and frames[reg] == frames[src] == basis(frame), "ADD common chart")
            for col, value in state[src].items():
                new = state[reg].get(col, Q(0)) + Q(factor) * value
                if new:
                    state[reg][col] = new
                else:
                    state[reg].pop(col, None)
            scalar[op] += 1
        elif op == "zero":
            need(reg == "C" and reg not in state, "private allocation")
            state[reg], frames[reg] = {}, basis(event[2])
            scalar[op] += 1
        elif op == "copy":
            need(reg == "C" and not state[reg] and
                 frames[reg] == frames[event[2]] == basis(event[3]), "private COPY")
            state[reg] = dict(state[event[2]])
            scalar[op] += 1
        elif op == "erase":
            need(reg == "C" and frames[reg] == basis(event[2]), "private discard")
            del state[reg], frames[reg]
            scalar[op] += 1
        else:
            raise ValueError("unknown event")
        capture(index + 1)
    need(set(state) == set(names), "private storage closed")
    for col, name in enumerate(names):
        wanted = {col: Q(1)}
        if name.startswith("Y"):
            target = int(name[1:])
            for j, port in enumerate(ports):
                value = Q(sum(x * y for x, y in zip(ports[target], port)), 8)
                if value:
                    wanted[j] = value
        need(state[name] == wanted, "all-input endpoint " + name)
        need(frames[name] == basis(word["final_frames"][name]), "endpoint frame")
    native = data["LOWRANK-RESULT.json"]
    need(dict(profile) == {int(k): v for k, v in native["paid_profile"].items()}
         and sum(k * v for k, v in profile.items()) == 2368, "inherited invoice")
    coefficients = []
    for row in rows:
        xx = {j: v for j, v in row if j < 104}
        coeff = [sum((v * ports[j][k] for j, v in xx.items()), Q(0)) / 104
                 for k in range(8)]
        need(all(sum(coeff[k] * ports[j][k] for k in range(8)) == xx.get(j, 0)
                 for j in range(104)), "every pooled X row lies in row(R)")
        coefficients.append(coeff)
    dimensions, local_bases = [], []
    for target, pool in enumerate(pools):
        missing = names.index("Y" + str(target))
        need(all(identities[((j, Q(1)),)] in pool
                 for j in range(104, 280) if j != missing), "initial dirty units")
        need(all(not dict(rows[r]).get(missing) for r in pool), "own Y excluded")
        pivots, chosen = {}, []
        for row_id in sorted(pool):
            if insert(pivots, dict(enumerate(coefficients[row_id]))):
                chosen.append(row_id)
        dimensions.append(len(pivots))
        local_bases.append(chosen)
    return dict(ports=ports, names=names, rows=rows, pools=pools,
                coefficients=coefficients, contacts=contacts,
                dimensions=dimensions, occurrences=occurrences,
                local_bases=local_bases, scalar=dict(scalar), profile=dict(profile))


def verify_witness(trace, cert):
    A = [[Q(0)] * 8 for _ in range(104)]
    for index, (target, cut, reg, weight) in enumerate(cert["terms"]):
        weight = Q(weight)
        need(weight and str(weight) == cert["terms"][index][3], "canonical weight")
        row = trace["contacts"][index]
        coeff = [sum((v * trace["ports"][j][k] for j, v in row if j < 104), Q(0)) / 104
                 for k in range(8)]
        for k in range(8):
            A[target][k] += weight * coeff[k]
    ports = trace["ports"]
    need(all(sum(ports[t][i] * A[t][j] for t in range(104)) == int(i == j)
             for i in range(8) for j in range(8)), "right inverse R A = I")
    C = [[Q(int(t == j)) - Q(sum(x * y for x, y in zip(ports[t], ports[j])), 8)
          for j in range(104)] for t in range(104)]
    H = [[C[t][j] + 12 * sum(A[t][k] * ports[j][k] for k in range(8))
          for j in range(104)] for t in range(104)]
    pivots = {}
    for row in H:
        insert(pivots, dict(enumerate(row)))
    need(len(pivots) == 96, "explicit H rank")
    # Right multiplication by C changes the kernel: C^-1 A = A - R^T/96.
    need(all(sum(H[t][j] * (A[j][k] - Q(ports[j][k], 96)) for j in range(104)) == 0
             for t in range(104) for k in range(8)), "explicit eight-column kernel")
    return A, H


def run(data=None, cert=None):
    data = sources() if data is None else data
    cert = certificate(read(HERE / "WITNESS.json") if cert is None else cert)
    trace = replay(data, cert["terms"])
    A, H = verify_witness(trace, cert)
    return {"schema": "p104-minimum-shared-space/1", "minimum_dimension": 96,
            "targets": 104, "arbitrary_input_columns": 280, "cuts": 4059,
            "captured_snapshot_rows": len(trace["rows"]),
            "pooled_x_rank_histogram": {str(k): v for k, v in sorted(Counter(trace["dimensions"]).items())},
            "pool_sizes": list(map(len, trace["pools"])),
            "certificate_terms": len(cert["terms"]),
            "nonzero_A_rows": sum(any(row) for row in A),
            "A_sha256": digest([[str(x) for x in row] for row in A]),
            "H_sha256": digest([[str(x) for x in row] for row in H]),
            "original_paid_profile": {str(k): v for k, v in sorted(trace["profile"].items())},
            "original_scalar_events": trace["scalar"],
            "scope": "Exact algebraic pooled-span minimum only; no chronological producer, transport price, supplier or new kappa."}


if __name__ == "__main__":
    cli(run, "PASS_P104_MINIMUM_SHARED_SPACE")
