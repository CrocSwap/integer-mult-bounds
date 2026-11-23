"""Separate exact tests for source-time cuts and the normalized interval lemma.

No author audit, source factory or source matrix helper is imported.  Rational
fixtures test the general DAG implication; the source grammar is reviewed in
REVIEW.md.  Principal-minor PSD tests give a separate spectral-norm oracle.
"""
from fractions import Fraction as F
from functools import cache
from hashlib import sha1, sha256
from itertools import combinations
from pathlib import Path
import argparse
import json
import time

PROOF_SHA = "e942012e66adc2d696cde3fedd6ae9c73df98e77a71b16e5004f5a74ccdfaa07"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def eye(n):
    return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))


def matrix(rows):
    return tuple(tuple(F(x) for x in row) for row in rows)


def tr(a):
    return tuple(zip(*a))


def mul(a, b):
    bt = tr(b)
    return tuple(tuple(sum(x*y for x, y in zip(row, col)) for col in bt) for row in a)


def add(a, b, scale=1):
    return tuple(tuple(x+scale*y for x, y in zip(row, col)) for row, col in zip(a, b))


@cache
def inv(a):
    n = len(a)
    w = [list(row)+list(eye(n)[i]) for i, row in enumerate(a)]
    for k in range(n):
        p = next((i for i in range(n-1, k-1, -1) if w[i][k]), None)
        need(p is not None, "singular matrix")
        w[p], w[k] = w[k], w[p]
        d = w[k][k]
        w[k] = [x/d for x in w[k]]
        for i in range(n):
            if i != k:
                d = w[i][k]
                w[i] = [x-d*y for x, y in zip(w[i], w[k])]
    return tuple(tuple(row[n:]) for row in w)


def determinant(a):
    if not a:
        return F(1)
    if len(a) == 1:
        return a[0][0]
    # Laplace expansion is intentionally different from the author's PSD test.
    return sum((-1)**j*a[0][j]*determinant(tuple(tuple(x for k, x in enumerate(row) if k != j)
                   for row in a[1:])) for j in range(len(a)))


def psd(a):
    need(a == tr(a), "PSD oracle needs a symmetric rational matrix")
    return all(determinant(tuple(tuple(a[i][j] for j in ids) for i in ids)) >= 0
               for size in range(1, len(a)+1) for ids in combinations(range(len(a)), size))


def spectral_below(a, cap):
    return psd(add(tuple(tuple(cap*cap*x for x in row) for row in eye(len(a))), mul(tr(a), a), -1))


def norm_majorant(a):
    """max(induced 1-norm, induced infinity-norm), also an operator-2 bound."""
    return max(max(map(lambda row: sum(map(abs, row)), a)),
               max(map(lambda row: sum(map(abs, row)), tr(a))))


def embed(local, ids, n=4):
    out = [list(row) for row in eye(n)]
    for i, u in enumerate(ids):
        for j, v in enumerate(ids):
            out[u][v] = local[i][j]
    return matrix(out)


def forward(matrices, n=4):
    out = eye(n)
    for a in matrices:
        out = mul(a, out)
    return out


def all_subsets(values):
    values = tuple(values)
    for mask in range(1 << len(values)):
        yield frozenset(values[j] for j in range(len(values)) if mask >> j & 1)


def shear(a, upper=True):
    return matrix([[1, a], [0, 1]]) if upper else matrix([[1, 0], [a, 1]])


def primitive():
    rotation = matrix([[F(3, 5), F(4, 5)], [-F(4, 5), F(3, 5)]])
    layers = [
        [(embed(rotation, (0, 1)), (0, 1)), (embed(tr(rotation), (2, 3)), (2, 3))],
        [(embed(shear(F(1, 3), False), (0, 2)), (0, 2)),
         (embed(shear(F(-1, 5), False), (1, 3)), (1, 3))],
        [(embed(tr(rotation), (0, 1)), (0, 1)), (embed(rotation, (2, 3)), (2, 3))],
        [(embed(shear(F(-1, 7), False), (0, 2)), (0, 2)),
         (embed(shear(F(2, 9), False), (1, 3)), (1, 3))],
    ]
    cuts = []; completed = eye(4)
    for k, layer in enumerate(layers):
        for selected in all_subsets(range(len(layer))):
            cuts.append((k, selected, mul(forward([layer[j][0] for j in sorted(selected)]), completed)))
        completed = mul(forward([gate for gate, _ in layer]), completed)
    cuts.append((len(layers), frozenset(), completed))
    cap = 1+F(1, 3)+F(2, 9)
    cases = 0
    for ku, su, u in cuts:
        for kv, sv, v in cuts:
            if ku > kv or (ku == kv and not su <= sv):
                continue
            segment = mul(v, inv(u))
            need(spectral_below(segment, cap) and spectral_below(inv(segment), cap),
                 "two spectral matchings exceeded the unchanged cap")
            cases += 1
    return {"cuts": len(cuts), "ordered_intervals": cases, "principal_minor_norm_certificates": 2*cases,
            "unchanged_cap": str(cap)}


def tree_fixture():
    # The logical recurrence matches R; parallel children; L.  It is a
    # deliberately synthetic rational fixture, not a source-factory replay.
    physical = (2, 0, 3, 1)
    delta = F(1, 1 << 30)
    atoms = {}

    def atom(name, logical, coeffs, upper=True, predecessors=()):
        ids = tuple(physical[i] for i in logical)
        layers = []; ideals = []
        for k, coeff in enumerate(coeffs):
            gates = []; want = []
            pairs = [(ids[0], ids[-1])] if len(ids) == 2 else [(ids[0], ids[2]), (ids[1], ids[3])]
            for j, pair in enumerate(pairs):
                amount = coeff/F(j+1)
                gates.append((embed(shear(amount+delta if k == 0 else amount, upper), pair), pair))
                want.append(embed(shear(amount, upper), pair))
            layers.append(gates);ideals.extend(want)
        atoms[name] = {"name": name, "support": frozenset(ids), "layers": layers,
                       "ideal": forward(ideals), "stored": forward([g for layer in layers for g, _ in layer]),
                       "pred": frozenset(predecessors)}
        return name

    def leaf(name, logical, value, predecessors):
        ids = (physical[logical],)
        atoms[name] = {"name": name, "support": frozenset(ids),
                       "layers": [[(embed(matrix([[value+delta]]), ids), ids)]],
                       "ideal": embed(matrix([[value]]), ids), "stored": embed(matrix([[value+delta]]), ids),
                       "pred": frozenset(predecessors)}
        return name

    atom("R", range(4), [F(1, 7), F(-1, 11)], predecessors=[])
    atom("R0", (0, 1), [F(1, 5)]*3, predecessors=["R"])
    atom("R1", (2, 3), [], predecessors=["R"])
    leaf("D0", 0, F(5, 4), ["R0"]);leaf("D1", 1, F(3, 4), ["R0"])
    leaf("D2", 2, F(7, 6), ["R1"]);leaf("D3", 3, F(6, 7), ["R1"])
    atom("L0", (0, 1), [F(1, 9), F(-1, 13)], False, ["D0", "D1"])
    atom("L1", (2, 3), [F(1, 11)]*5, False, ["D2", "D3"])
    atom("L", range(4), [F(1, 17)]*3, False, ["L0", "L1"])

    def topo(chosen, done=()):
        remaining = set(chosen);done = set(done);out = []
        while remaining:
            ready = sorted(name for name in remaining if atoms[name]["pred"] <= done)
            need(ready, "not a topological block")
            name = ready[-1]  # reverse lexical order deliberately differs from source chronology
            out.append(name);done.add(name);remaining.remove(name)
        return out

    labels = frozenset(atoms)
    order = topo(labels)
    layers = []
    for name in order:
        a = atoms[name]
        a["start"] = max((atoms[p]["stop"] for p in a["pred"]), default=0)
        a["stop"] = a["start"]+len(a["layers"])
        for offset, layer in enumerate(a["layers"]):
            k = a["start"]+offset
            while len(layers) <= k:
                layers.append([])
            layers[k].extend((name, j, gate, ids) for j, (gate, ids) in enumerate(layer))
    for layer in layers:
        used = [i for _, _, _, ids in layer for i in ids]
        need(len(used) == len(set(used)), "fixture layer is not a matching")
    downsets = [s for s in all_subsets(sorted(labels)) if all(atoms[x]["pred"] <= s for x in s)]
    exact = {s: forward([atoms[x]["ideal"] for x in topo(s)]) for s in downsets}
    stored = {s: forward([atoms[x]["stored"] for x in topo(s)]) for s in downsets}
    B = max(norm_majorant(m) for s in downsets for m in (exact[s], inv(exact[s])))
    eta = max(norm_majorant(add(a["stored"], a["ideal"], -1)) for a in atoms.values())
    theta = len(atoms)*B*B*eta
    need(theta <= F(1, 4), "fixture perturbation budget is not small")

    nested = 0;wrong = 0
    for u in downsets:
        for v in downsets:
            if not u <= v:
                continue
            same_order = topo(u)+topo(v-u, u)+topo(labels-v, v)
            need(len(same_order) == len(atoms) and len(set(same_order)) == len(atoms), "missing atom")
            q = eye(4); z = eye(4); gs = []; qs = [q]; zs = [z]; qh = eye(4); qhs = [qh]
            for name in same_order:
                a = atoms[name];old = q;q = mul(a["ideal"], q)
                g = mul(mul(inv(q), add(a["stored"], a["ideal"], -1)), old)
                gs.append(g);z = mul(add(eye(4), g), z);qs.append(q);zs.append(z)
                qh = mul(a["stored"], qh);qhs.append(qh)
                need(mul(q, z) == qh, "left normalized perturbation recurrence")
            i, j = len(u), len(v)
            w = forward([add(eye(4), g) for g in gs[i:j]])
            relative = mul(stored[v], inv(stored[u]))
            need(w == mul(zs[j], inv(zs[i])), "noncommutative consecutive cancellation")
            need(relative == mul(mul(qs[j], w), inv(qs[i])), "relative endpoint factor order")
            actual_sum = sum(norm_majorant(g) for g in gs[i:j])
            need(actual_sum <= theta, "normalized perturbations exceed declared sum")
            cap = 1/(1-actual_sum)
            need(norm_majorant(w) <= cap and norm_majorant(inv(w)) <= cap,
                 "exact relative normalized bound")
            need(norm_majorant(relative) <= B*B/(1-theta), "relative endpoint envelope")
            if relative != mul(inv(stored[u]), stored[v]):
                wrong += 1
            nested += 1
    need(wrong, "fixture never challenged noncommutative relative order")

    cuts = [];completed = eye(4);H = F(1);simultaneous = 0;empty_predecessor = 0
    for k in range(len(layers)+1):
        layer = layers[k] if k < len(layers) else []
        for selected in all_subsets(range(len(layer))):
            c = mul(forward([layer[j][2] for j in sorted(selected)]), completed)
            done = frozenset(name for name, a in atoms.items() if a["stop"] <= k)
            active = frozenset(name for name, a in atoms.items() if a["start"] <= k < a["stop"])
            need(done in exact and done | active in exact, "timestamp sets are not downsets")
            supports = [atoms[name]["support"] for name in active]
            need(sum(map(len, supports)) == len(set().union(*supports)) if supports else True,
                 "active atoms overlap")
            f = eye(4);tails = eye(4);nonempty = 0
            for name in sorted(active):
                a = atoms[name];local = k-a["start"]
                preceding = [g for lay in a["layers"][:local] for g, _ in lay]
                pick = {layer[j][1] for j in selected if layer[j][0] == name}
                part = forward(preceding+[g for j, (g, _) in enumerate(a["layers"][local]) if j in pick])
                tail = mul(a["stored"], inv(part))
                nonempty += bool(preceding or pick)
                H = max(H, *(norm_majorant(x) for x in (part, inv(part), tail, inv(tail))))
                f = mul(part, f);tails = mul(tail, tails)
            need(c == mul(f, stored[done]), "source-time prefix factorization")
            rest = topo(labels-(done | active), done | active)
            suffix = mul(forward([atoms[x]["stored"] for x in rest]), tails)
            need(mul(suffix, c) == stored[labels], "source-time suffix factorization")
            simultaneous += nonempty >= 2
            empty_predecessor += "R1" in done and any(x in active for x in ("D2", "D3", "L1"))
            cuts.append((k, selected, c, done, f))
        completed = mul(forward([gate for _, _, gate, _ in layer]), completed)
    interval_cap = B*B*H*H/(1-theta)
    intervals = 0;same_layer = 0
    for ku, su, u, iu, fu in cuts:
        for kv, sv, v, iv, fv in cuts:
            if ku > kv or (ku == kv and not su <= sv):
                continue
            need(iu <= iv, "completed sets are not nested")
            segment = mul(v, inv(u))
            need(segment == mul(mul(mul(fv, stored[iv]), inv(stored[iu])), inv(fu)),
                 "two actual-cut normalized factorization")
            need(norm_majorant(segment) <= interval_cap and norm_majorant(inv(segment)) <= interval_cap,
                 "complete interval envelope")
            intervals += 1;same_layer += ku == kv
    need(simultaneous and empty_predecessor, "asynchronous/empty-atom cases missing")
    return {"atoms": len(atoms), "downsets": len(downsets), "nested_downset_pairs": nested,
            "noncommuting_wrong_order_controls": wrong, "matching_cuts": len(cuts),
            "ordered_intervals": intervals, "same_layer_intervals": same_layer,
            "simultaneous_nonempty_fragments": simultaneous, "zero_atom_predecessor_cases": empty_predecessor,
            "B": str(B), "eta": str(eta), "theta": str(theta), "H": str(H),
            "relative_interval_cap": str(interval_cap), "physical_wire_order": physical,
            "scope": "synthetic rational DAG, not a source-factory execution"}


def generator_check():
    p = matrix([[1, F(1, 4)], [0, 1]])
    h = matrix([[F(1, 7), F(2, 9)], [-F(1, 8), F(1, 11)]])
    a = matrix([[F(1, 5), 0], [F(1, 13), F(-1, 7)]])
    later = matrix([[F(1, 3), F(-1, 8)], [0, F(1, 17)]])
    zero = matrix([[0, 0], [0, 0]])

    def block(b, d):
        return matrix([list(b[0])+list(zero[0]), list(b[1])+list(zero[1]),
                       list(d[0])+list(eye(2)[0]), list(d[1])+list(eye(2)[1])])

    def s(d):
        return block(eye(2), d)

    term = mul(h, add(p, eye(2), -1))
    c = add(term, later)  # Crucially includes the current complete term.
    gates = [block(p, zero), s(h), block(inv(p), zero), s(add(zero, h, -1))]
    prefixes = [block(p, a), block(p, add(a, mul(h, p))), s(add(a, mul(h, p))), s(add(a, term))]
    suffixes = [block(inv(p), mul(c, inv(p))), block(inv(p), add(mul(c, inv(p)), h, -1)),
                s(add(c, mul(h, p), -1)), s(add(c, term, -1))]
    for k in range(4):
        pref = mul(forward(gates[:k+1]), s(a))
        suff = mul(s(later), forward(gates[k+1:]))
        need(pref == prefixes[k] and suff == suffixes[k], "generator checkpoint formula")
        need(mul(suff, pref) == s(add(add(a, term), later)), "generator total order")
    need(suffixes[0] != block(inv(p), mul(later, inv(p))), "wrong C meaning did not fail")
    return {"prefix_suffix_checkpoint_equalities": 8, "current_term_required_in_C": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args();started = time.monotonic();source = args.source.resolve()
    need(sha256((source/"PROOF.md").read_bytes()).hexdigest() == PROOF_SHA, "reviewed author proof moved")
    origins = json.loads((source/"ORIGINS.json").read_text())
    for row in origins["files"]:
        data = (source/row["local"]).read_bytes()
        need(sha256(data).hexdigest() == row["sha256"], "origin SHA-256 mismatch")
        need(sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest() == row["git_blob"],
             "origin Git blob mismatch")
    result = {"status": "PASS_INDEPENDENT_NESTED_DOWNSET_REVIEW", "proof_sha256": PROOF_SHA,
              "authenticated_origins": len(origins["files"]), "primitive": primitive(),
              "dag": tree_fixture(), "generator": generator_check(),
              "scope": "Exact synthetic rational corroboration and independent written proof/source review; no all-size enumeration"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "seconds": time.monotonic()-started,
                      "primitive_intervals": result["primitive"]["ordered_intervals"],
                      "nested_pairs": result["dag"]["nested_downset_pairs"],
                      "cut_intervals": result["dag"]["ordered_intervals"]}))


if __name__ == "__main__":
    main()
