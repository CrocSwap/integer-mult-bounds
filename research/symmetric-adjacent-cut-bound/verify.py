#!/usr/bin/env python3
"""Exact formal coefficients and ordered-pair cuts; Apache-2.0.

Ross Richardson, with substantial OpenAI Codex assistance.
The universal statement is PROOF.md. This is finite corroboration.
Default replay consumes a fixed EXPECTED.json; only --write generates it.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class Failure(ValueError):
    pass


def need(condition, reason):
    if not condition:
        raise Failure(reason)


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "duplicate JSON key: " + key)
        out[key] = value
    return out


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length()-1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return len(pivots)


def eye(r):
    return sum(1 << (i*r+i) for i in range(r))


def rows(a, r):
    return [(a >> (i*r)) & ((1 << r)-1) for i in range(r)]


def mm(a, b, r):
    out, br = 0, rows(b, r)
    for i, row in enumerate(rows(a, r)):
        v = 0
        for j in range(r):
            if row >> j & 1:
                v ^= br[j]
        out |= v << (i*r)
    return out


def inverse_matrix(a, r):
    rr = [x | (1 << (r+i)) for i, x in enumerate(rows(a, r))]
    for c in range(r):
        p = next((i for i in range(c, r) if rr[i] >> c & 1), None)
        need(p is not None, "singular scalar map")
        rr[c], rr[p] = rr[p], rr[c]
        for i in range(r):
            if i != c and rr[i] >> c & 1:
                rr[i] ^= rr[c]
    return sum((v >> r) << (i*r) for i, v in enumerate(rr))


def projectors(r):
    answer = [sum(v << (i*r) for i in range(r) if u >> i & 1)
              for u in range(1, 1 << r) for v in range(1, 1 << r)
              if (u & v).bit_count() % 2]
    need(len(set(answer)) == (2**r-1)*2**(r-1), "projector inventory")
    return sorted(answer)


def identity(n):
    return tuple(range(n))


def compose(a, b):
    """a after b on columns."""
    return tuple(a[b[i]] for i in range(len(a)))


def invert(p):
    out = [0]*len(p)
    for i, v in enumerate(p):
        out[v] = i
    return tuple(out)


def adjacent(n, i):
    p = list(range(n))
    p[i], p[i+1] = p[i+1], p[i]
    return tuple(p)


def inversions(p):
    return sum(p[i] > p[j] for i in range(len(p)) for j in range(i+1, len(p)))


def sorting_word(p):
    """Chronological labels; the last factor is leftmost in the product."""
    a, word = list(p), []
    for end in range(len(a)-1, 0, -1):
        for i in range(end):
            if a[i] > a[i+1]:
                a[i], a[i+1] = a[i+1], a[i]
                word.append(i)
    need(tuple(a) == identity(len(a)), "sorting failure")
    return word


def formal_mul(a, b, r):
    """Independent group coefficients, each a complete binary role matrix."""
    out = {}
    for g, x in a.items():
        for h, y in b.items():
            k = compose(g, h)
            out[k] = out.get(k, 0) ^ mm(x, y, r)
    return {g: x for g, x in out.items() if x}


def paid(n, r, label, projector):
    need(type(label) is int and 0 <= label < n-1, "illegal adjacent label")
    need(type(projector) is int and 0 <= projector < 1 << (r*r), "projector dimensions")
    need(rank(rows(projector, r)) == 1, "paid scalar rank")
    need(mm(projector, projector, r) == projector, "paid scalar idempotence")
    out = {identity(n): eye(r) ^ projector, adjacent(n, label): projector}
    return {g: x for g, x in out.items() if x}


def scalar(n, r, s):
    need(type(s) is int and 0 <= s < 1 << (r*r), "scalar dimensions")
    need(rank(rows(s, r)) == r, "singular scalar map")
    return {identity(n): s}


def target(n, r, targets):
    need(len(targets) <= r, "too many targets")
    out = {}
    for i, p in enumerate(list(targets) + [identity(n)]*(r-len(targets))):
        need(sorted(p) == list(range(n)), "invalid target permutation")
        out[p] = out.get(p, 0) ^ (1 << (i*r+i))
    return out


def direct(n, r, targets):
    return [(label, 1 << (i*r+i)) for i, p in enumerate(targets) for label in sorting_word(p)]


def replay(n, r, word):
    out = {identity(n): eye(r)}
    for label, projector in word:
        out = formal_mul(paid(n, r, label, projector), out, r)
    return out


def endpoint(actual, expected):
    need(actual == expected, "full formal endpoint")


def crossing_rows(a, n, r):
    """Explicit represented K<-H block; no inversion formula here."""
    positive = [(i, j) for i in range(n) for j in range(i+1, n)]
    negative = {(j, i): k for k, (i, j) in enumerate(positive)}
    d, out = len(positive), [0]*(r*len(positive))
    for g, coeff in a.items():
        cr = rows(coeff, r)
        for col, (i, j) in enumerate(positive):
            image = (g[i], g[j])
            if image in negative:
                for t in range(r):
                    for s in range(r):
                        if cr[t] >> s & 1:
                            out[t*d+negative[image]] ^= 1 << (s*d+col)
    return out


def crossing(a, n, r):
    return rank(crossing_rows(a, n, r))


def reject(action, expected_reason):
    try:
        action()
    except Failure as e:
        need(str(e) == expected_reason, "control reached wrong detector: " + str(e))
        return
    raise Failure("control unexpectedly accepted: " + expected_reason)


def source_check():
    observed = {}
    for item in read_json(HERE / "SOURCES.json")["files"]:
        if item["usage"] == "input":
            actual = hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest()
            need(actual == item["sha256"], "source drift: " + item["path"])
            observed[item["path"]] = actual
    return observed


def compute():
    receipt = {"schema_version": 1, "status": "PASS_SYMMETRIC_ADJACENT_CUT_BOUND", "no_new_kappa": True,
               "source_sha256": source_check(), "permutations": [], "controls": {}}
    for n in range(2, 8):
        hist, stream = [0]*(n*(n-1)//2+1), []
        for p in itertools.permutations(range(n)):
            cost, word = inversions(p), direct(n, 1, [p])
            need(len(word) == cost, "sorting bill")
            actual = replay(n, 1, word)
            endpoint(actual, target(n, 1, [p]))
            need(crossing(actual, n, 1) == cost, "target crossing")
            hist[cost] += 1
            stream.append([p, cost, [i for i, _ in word]])
        receipt["permutations"].append({"n": n, "count": sum(hist), "inversion_histogram": hist,
                                        "word_stream_sha256": digest(stream)})
    count = 0
    for r in range(1, 5):
        for n in range(2, 6):
            for p in projectors(r):
                for label in range(n-1):
                    f = paid(n, r, label, p)
                    need(crossing(f, n, r) == 1, "generator crossing")
                    endpoint(formal_mul(f, f, r), {identity(n): eye(r)})
                    count += 1
    receipt["complete_projector_factor_checks"] = count
    n, r = 3, 2
    alphabet = [(i, p) for i in range(n-1) for p in projectors(r)]
    layers = []
    for length in range(4):
        count = diagonal = 0
        for word in itertools.product(alphabet, repeat=length):
            a = replay(n, r, word)
            need(crossing(a, n, r) <= length, "word cut subadditivity")
            count += 1
            diag = []
            for role in range(r):
                hits = [g for g, c in a.items() if c >> (role*r+role) & 1]
                if len(hits) != 1:
                    break
                diag.append(hits[0])
            if len(diag) == r and a == target(n, r, diag):
                need(sum(map(inversions, diag)) <= length, "short diagonal floor")
                diagonal += 1
        layers.append({"length": length, "words": count, "diagonal_words": diagonal})
    receipt["complete_short_words_n3_r2"] = layers
    n, r, pairs, omitted = 4, 3, 0, 0
    bills = {}
    for a, b in itertools.product(itertools.permutations(range(n)), repeat=2):
        word, t = direct(n, r, [a, b]), target(n, r, [a, b])
        endpoint(replay(n, r, word), t)
        endpoint(replay(n, r, list(reversed(word))), target(n, r, [invert(a), invert(b)]))
        need(crossing(t, n, r) == len(word), "pair lower bound")
        for j in range(len(word)):
            reject(lambda j=j: endpoint(replay(n, r, word[:j]+word[j+1:]), t), "full formal endpoint")
            omitted += 1
        bills[str(len(word))] = bills.get(str(len(word)), 0)+1
        pairs += 1
    receipt["all_s4_pairs"] = {"pairs": pairs, "cost_histogram": bills, "omission_rejections": omitted}
    tgs = [(2, 3, 0, 1), (1, 0, 3, 2)]
    word, t = direct(n, r, tgs), target(n, r, tgs)
    gl = [s for s in range(1 << (r*r)) if rank(rows(s, r)) == r]
    need(len(gl) == 168, "GL3 inventory")
    conjugations = 0
    for s in gl:
        si, a = inverse_matrix(s, r), scalar(n, r, s)
        need(mm(s, si, r) == eye(r), "scalar inverse")
        need(crossing(a, n, r) == 0, "free scalar crossing")
        for label, p in word:
            np = mm(mm(s, p, r), si, r)
            a = formal_mul(paid(n, r, label, np), a, r)
        a = formal_mul(scalar(n, r, si), a, r)
        endpoint(a, t)
        for p in projectors(r):
            np = mm(mm(s, p, r), si, r)
            f = paid(n, r, 1, np)
            other = formal_mul(scalar(n, r, s), formal_mul(paid(n, r, 1, p), scalar(n, r, si), r), r)
            endpoint(f, other)
            conjugations += 1
    receipt["scalar_GL3"] = {"full_dirty_interleavings": len(gl), "all_projector_conjugations": conjugations}
    controls = receipt["controls"]
    reject(lambda: paid(4, 3, 3, 1), "illegal adjacent label")
    controls["out_of_alphabet_label"] = True
    reject(lambda: paid(4, 3, 0, (1 << 0) | (1 << 4)), "paid scalar rank")
    controls["rank_two_unit_undercharge"] = True
    reject(lambda: paid(4, 3, 0, 1 << 1), "paid scalar idempotence")
    controls["nilpotent_scalar_projector"] = True
    reject(lambda: scalar(4, 3, 0), "singular scalar map")
    controls["singular_free_scalar"] = True
    nonadj = (2, 1, 0, 3)
    need(crossing({nonadj: 1}, 4, 1) == 3, "nonadjacent control crossing")
    reject(lambda: need(crossing({nonadj: 1}, 4, 1) <= 1, "unit crossing budget"), "unit crossing budget")
    controls["nonadjacent_unit_violates_cut_budget"] = 3
    reject(lambda: need(crossing({nonadj: 1}, 4, 1) == 0, "free address cut"), "free address cut")
    controls["free_address_map_violates_zero_budget"] = True
    leaky = dict(t)
    leaky[identity(n)] = leaky.get(identity(n), 0) ^ (1 << 2)
    active_mask = sum(1 << (row*r+col) for row in range(r) for col in range(2))
    need({g:c & active_mask for g,c in leaky.items() if c & active_mask} ==
         {g:c & active_mask for g,c in t.items() if c & active_mask}, "clean-only leak fixture")
    reject(lambda: endpoint(leaky, t), "full formal endpoint")
    controls["dirty_input_leak"] = True
    reject(lambda: endpoint(target(n, r, tgs + [adjacent(n, 0)]), t), "full formal endpoint")
    controls["unrestored_dirty_spectator"] = True
    residue = formal_mul(scalar(n, r, eye(r) ^ (1 << 1)), t, r)
    reject(lambda: endpoint(residue, t), "full formal endpoint")
    controls["free_scalar_residue"] = True
    c = (1, 2, 3, 0)
    cw = direct(n, r, [c])
    reject(lambda: endpoint(replay(n, r, list(reversed(cw))), target(n, r, [c])), "full formal endpoint")
    controls["noncommuting_order"] = True
    # A nonzero full-algebra defect invisible in the entire pair representation.
    omega = {p: 1 << 1 for p in itertools.permutations(range(4))}
    fake = dict(t)
    for g, coeff in omega.items():
        fake[g] = fake.get(g, 0) ^ coeff
        if not fake[g]:
            del fake[g]
    need(crossing_rows(fake, n, r) == crossing_rows(t, n, r), "representation kernel fixture")
    basis = [(i,j) for i in range(4) for j in range(4) if i != j]
    for u in basis:
        for v in basis:
            need(sum((g[u[0]],g[u[1]]) == v for g in omega) == 2, "whole representation kernel")
    reject(lambda: endpoint(fake, t), "full formal endpoint")
    controls["represented_equality_is_not_formal_equality"] = {"formal_nonzero_terms": 24, "pair_entries": len(basis)**2}
    large = []
    for n in (8, 12, 20):
        targets = [tuple(reversed(range(n))), tuple(range(1,n))+(0,), tuple((i+3)%n for i in range(n))]
        r = 5
        w = direct(n, r, targets)
        endpoint(replay(n, r, w), target(n, r, targets))
        endpoint(replay(n, r, list(reversed(w))), target(n, r, list(map(invert, targets))))
        large.append({"n": n, "roles": r, "targets": len(targets), "paid_calls": len(w)})
    receipt["larger_fixtures"] = large
    return receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="explicitly regenerate EXPECTED.json")
    ap.add_argument("--emit", action="store_true", help="print recomputed receipt without writing")
    args = ap.parse_args()
    expected = None if args.write else read_json(HERE / "EXPECTED.json")
    result = compute()
    if args.write:
        (HERE / "EXPECTED.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    else:
        need(result == expected, "fixed receipt mismatch")
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS_SYMMETRIC_ADJACENT_CUT_BOUND permutations=5912 s4_pairs=576 arbitrary_dirty_roles=written_proof no_new_kappa")


if __name__ == "__main__":
    main()
