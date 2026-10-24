"""Nonlinear zero-error messages keep the A7+A1 nine-term COPY floor at 72.

Standard library only. Rebuilds the 120 E8 root lines, A7+A1 readers and the
two pinned sharp shift witnesses of research/a7-a1-decoder-floor, then checks
two finite certificates per term:

  fooling   rho_k source lines S and reader lines R inside the term with
            B[S,R] invertible over F2 (any message, linear or not, needs
            2^rho_k values: no side information);
  sideinfo  readers know every orthogonal input: either an induced
            "Petersen + (rho_k - 5) isolated" subgraph of the orthogonality
            graph (broadcast rate rho_k; the rho=9 case is the 14-vertex
            witness of p112-characteristic-two-minrank) or a pairwise
            non-orthogonal set of size rho_k (independence bound).

The stored RESULT.json must equal the rebuilt certificate.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PRED = ROOT / "research" / "a7-a1-decoder-floor"


def pinned_inputs():
    """Every usage=input file must match its SOURCES.json SHA256 before use."""
    rows = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]
    for row in rows:
        if row["usage"] == "input":
            data = (ROOT / row["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row["sha256"], "input drift: " + row["path"])


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def canonical(vector):
    first = next(x for x in vector if x)
    return tuple(vector) if first > 0 else tuple(-x for x in vector)


def roots():
    # Same enumeration and ordering as research/a7-a1-decoder-floor/verify.py.
    values = set()
    for i, j in itertools.combinations(range(8), 2):
        for a, b in itertools.product((-2, 2), repeat=2):
            row = [0] * 8
            row[i], row[j] = a, b
            values.add(canonical(row))
    for row in itertools.product((-1, 1), repeat=8):
        if sum(x < 0 for x in row) % 2 == 0:
            values.add(canonical(row))
    return sorted(values, reverse=True)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def f2_rank(rows):
    pivots = {}
    for value in rows:
        while value:
            top = value.bit_length() - 1
            if top in pivots:
                value ^= pivots[top]
            else:
                pivots[top] = value
                break
    return len(pivots)


def model():
    rr = roots()
    require(len(rr) == 120 and all(dot(x, x) == 8 for x in rr), "E8 root model")
    # B_ij = 1 iff the true inner product is even: orthogonal or the same line.
    pairing = [[(dot(x, y) // 4 + 1) % 2 for y in rr] for x in rr]
    orth = [[i != j and dot(rr[i], rr[j]) == 0 for j in range(120)] for i in range(120)]
    t16 = [[8 * r[k] - sum(r) for k in range(8)] + [4 * sum(r)] for r in rr]
    readers = [frozenset(i for i in range(120) if t16[i][k]) for k in range(9)]
    return rr, pairing, orth, t16, readers


def decoder(rr, shifts):
    return [[4 * (r[k] + shifts[i]) for k in range(8)] + [sum(r)] for i, r in enumerate(rr)]


def exact(d4, t16, rr):
    return all(dot(d4[i], t16[j]) == 32 * dot(rr[i], rr[j]) for i in range(120) for j in range(120))


def invoice(d4, pairing, readers):
    sources = [frozenset(i for i in range(120) if d4[i][k]) for k in range(9)]
    costs = []
    for k in range(9):
        rows = [sum(pairing[i][j] << j for j in readers[k]) for i in sorted(sources[k])]
        costs.append(f2_rank(rows))
    return sources, costs


def fooling(pairing, src, rdr, rho):
    """Greedy rho x rho invertible submatrix B[S,R]; returns sorted (S, R)."""
    if rho == 0:
        return [], []
    S, basis_rows = [], []
    for i in sorted(src):
        row = sum(pairing[i][j] << j for j in rdr)
        if f2_rank(basis_rows + [row]) > len(basis_rows):
            S.append(i)
            basis_rows.append(row)
    require(len(S) == rho, "fooling sources reach the rank")
    R = []
    for j in sorted(rdr):
        cand = R + [j]
        cols = [sum(pairing[i][c] << t for t, c in enumerate(cand)) for i in S]
        if f2_rank(cols) == len(cand):
            R = cand
    require(len(R) == rho, "fooling readers reach the rank")
    return S, R


def check_fooling(pairing, src, rdr, S, R):
    """Distinct inputs on S give distinct reader vectors on R."""
    require(set(S) <= src and set(R) <= rdr and len(S) == len(R), "fooling support")
    require(len(set(S)) == len(S) and len(set(R)) == len(R), "fooling repeats")
    rows = [sum(pairing[i][j] << t for t, j in enumerate(R)) for i in S]
    require(f2_rank(rows) == len(S), "fooling block invertible")
    return len(S)


KNESER = list(itertools.combinations(range(5), 2))


def petersen_witness(orth, S, extra=4):
    """Induced Petersen (edges = orthogonal pairs) plus `extra` lines that are
    pairwise non-orthogonal and non-orthogonal to all ten, inside S."""
    S = sorted(S)
    assign = []

    def bt(t):
        if t == 10:
            cand = [c for c in S if c not in assign and not any(orth[c][p] for p in assign)]
            for quad in itertools.combinations(cand, extra):
                if not any(orth[a][b] for a, b in itertools.combinations(quad, 2)):
                    return list(assign), list(quad)
            return None
        v = KNESER[t]
        for line in S:
            if line in assign:
                continue
            if all(orth[line][assign[u]] == (not set(KNESER[u]) & set(v)) for u in range(t)):
                assign.append(line)
                found = bt(t + 1)
                if found:
                    return found
                assign.pop()
        return None
    return bt(0)


def check_petersen(orth, S, petersen, isolated):
    lines = petersen + isolated
    require(len(petersen) == 10 and len(isolated) <= 4, "witness shape")
    require(len(set(lines)) == len(lines) and set(lines) <= S, "witness inside the term")
    for a, b in itertools.combinations(range(10), 2):
        require(orth[petersen[a]][petersen[b]] == (not set(KNESER[a]) & set(KNESER[b])),
                "Petersen adjacency")
    for c in isolated:
        require(not any(orth[c][x] for x in lines if x != c), "isolated vertex")
    # Broadcast rate of Petersen is 5; isolated receivers add one each.
    return 5 + len(isolated)


def clique(orth, S, size):
    """Pairwise non-orthogonal set of the requested size inside S."""
    S = sorted(S)

    def bt(chosen, start):
        if len(chosen) == size:
            return list(chosen)
        for t in range(start, len(S)):
            c = S[t]
            if not any(orth[c][x] for x in chosen):
                found = bt(chosen + [c], t + 1)
                if found:
                    return found
        return None
    return bt([], 0)


def check_clique(orth, S, lines, rho):
    require(len(lines) == rho and len(set(lines)) == rho and set(lines) <= S, "clique support")
    require(not any(orth[a][b] for a, b in itertools.combinations(lines, 2)), "clique non-orthogonal")
    return rho


def term_certificates(pairing, orth, sources, readers, costs):
    out = []
    for k in range(9):
        src, rdr, rho = sources[k], readers[k], costs[k]
        S, R = fooling(pairing, src, rdr, rho)
        demand = src & rdr
        row = {"term": k, "rank": rho, "sources": len(src), "demand_lines": len(demand),
               "fooling_sources": S, "fooling_readers": R}
        if rho >= 5:
            found = petersen_witness(orth, demand, rho - 5)
            require(found is not None, "Petersen witness in term %d" % k)
            row["sideinfo"] = {"kind": "petersen+isolated", "petersen": found[0], "isolated": found[1]}
        elif rho > 0:
            found = clique(orth, demand, rho)
            require(found is not None, "independent set in term %d" % k)
            row["sideinfo"] = {"kind": "independent", "lines": found}
        else:
            row["sideinfo"] = {"kind": "empty"}
        out.append(row)
    return out


def check_terms(pairing, orth, sources, readers, costs, rows):
    fool, side = [], []
    for k, row in enumerate(rows):
        require(row["term"] == k and row["rank"] == costs[k], "term row binding")
        fool.append(check_fooling(pairing, sources[k], readers[k],
                                  row["fooling_sources"], row["fooling_readers"]))
        demand = sources[k] & readers[k]
        info = row["sideinfo"]
        if info["kind"] == "petersen+isolated":
            side.append(check_petersen(orth, demand, info["petersen"], info["isolated"]))
        elif info["kind"] == "independent":
            side.append(check_clique(orth, demand, info["lines"], costs[k]))
        else:
            require(info["kind"] == "empty" and costs[k] == 0, "empty term")
            side.append(0)
    require(fool == costs, "no-side-information bounds equal the linear invoice")
    require(side == costs, "side-information bounds equal the linear invoice")
    return sum(fool), sum(side)


def source_shifts():
    pinned_inputs()
    data = json.loads((PRED / "RESULT.json").read_text(encoding="utf-8"))
    w = data["witness"]
    nine = list(w["row_shifts"])
    rr = roots()
    eight = [-r[0] for r in rr]
    idx = w["changed_root_index"]
    require(rr[idx] == tuple(w["changed_root"]), "pinned changed root")
    require(nine[:idx] + nine[idx + 1:] == eight[:idx] + eight[idx + 1:], "pinned shifts differ only at one row")
    return {"eight_active": (eight, w["eight_active_costs"]), "nine_active": (nine, w["nine_active_costs"])}


def result():
    rr, pairing, orth, t16, readers = model()
    out = {"schema_version": 1, "root_lines": 120, "petersen_terms": 0,
           "orthogonal_pairs": sum(orth[i][j] for i in range(120) for j in range(i)),
           "witnesses": {}}
    for name, (shifts, pinned_costs) in source_shifts().items():
        d4 = decoder(rr, shifts)
        require(exact(d4, t16, rr), name + " all-pairs identity")
        sources, costs = invoice(d4, pairing, readers)
        require(costs == pinned_costs, name + " invoice equals pinned predecessor")
        rows = term_certificates(pairing, orth, sources, readers, costs)
        fool, side = check_terms(pairing, orth, sources, readers, costs, rows)
        require(fool == side == 72, name + " totals")
        out["petersen_terms"] += sum(r["sideinfo"]["kind"] == "petersen+isolated" for r in rows)
        out["witnesses"][name] = {"costs": costs, "no_side_info_floor": fool,
                                  "orthogonal_side_info_floor": side, "terms": rows}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="explicitly regenerate RESULT.json")
    args = ap.parse_args()
    evidence = result()
    path = HERE / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(evidence, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    else:
        stored = json.loads(path.read_text(encoding="utf-8"))
        require(stored == json.loads(json.dumps(evidence)), "stored certificate mismatch")
        # Re-check the stored certificate itself, not only its regeneration.
        rr, pairing, orth, t16, readers = model()
        for name, (shifts, _) in source_shifts().items():
            sources, costs = invoice(decoder(rr, shifts), pairing, readers)
            check_terms(pairing, orth, sources, readers, costs, stored["witnesses"][name]["terms"])
    digest = hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest()[:16]
    print("PASS_A7_A1_NONLINEAR_COPY_FLOOR roots=120 witnesses=2 no_side_info=72 "
          "orthogonal_side_info=72 petersen_terms=%d certificate=" % evidence["petersen_terms"] + digest + " no_new_kappa")


if __name__ == "__main__":
    main()
