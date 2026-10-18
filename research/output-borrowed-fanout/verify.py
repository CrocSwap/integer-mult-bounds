#!/usr/bin/env python3
"""Independent free-module, integer-matrix and resource replay of literal words.

Does not import the schedule generator. No third-party libraries required.
Copyright 2026 Ross Richardson. Apache-2.0. Substantial OpenAI Codex assistance.
"""
import argparse
import gzip
import hashlib
import itertools
import json
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def reverse(word):
    return [(s, t, f, -sign) for s, t, f, sign in word[::-1]]


def symbolic(word, roles, initial=None):
    state = ({r: {(r, ()): 1} for r in roles} if initial is None
             else {r: dict(p) for r, p in initial.items()})
    for source, target, factor, sign in word:
        require(source in state and target in state and source != target,
                "invalid or aliased leaf ports")
        require(sign in (-1, 1), "non-unit sign")
        for (origin, letters), value in list(state[source].items()):
            key = (origin, (factor,) + letters)
            new = state[target].get(key, 0) + sign * value
            if new:
                state[target][key] = new
            else:
                state[target].pop(key, None)
    return state


def expected(roles, factors, k):
    out = {r: {(r, ()): 1} for r in roles}
    for i in range(k):
        letters = tuple(reversed(factors[f"A{i}"])) + tuple(reversed(factors["B"]))
        out[f"y{i}"][("x", letters)] = 1
    return out


def leaf_count(n):
    if n == 1:
        return 1
    return 2 * leaf_count(n // 2) + 2 * leaf_count(n - n // 2)


def factor_counts(factors, multiplier=1):
    if len(factors) == 1:
        return Counter({factors[0]: multiplier})
    m = len(factors)//2
    return factor_counts(factors[:m], 2*multiplier) + factor_counts(factors[m:], 2*multiplier)


def matrix_vector(matrix, source):
    return [sum(a*b for a, b in zip(row, source)) for row in matrix]


def dense(word, matrices, initial, width=None):
    state = {r: list(v) for r, v in initial.items()}
    for s, t, f, sign in word:
        value = matrix_vector(matrices[f], state[s])
        state[t] = [a + sign*b for a, b in zip(state[t], value)]
        if width is not None:
            require(all(abs(v).bit_length()+1 <= width for a in state.values() for v in a),
                    "integer prefix width")
    return state


def invoice(word, roles, factor_order, L):
    """Visit each coefficient, source term and destination; return home per leaf."""
    slots = {r: i*L for i, r in enumerate(roles)}
    coeff = {f: len(roles)*L + i*L*L for i, f in enumerate(factor_order)}
    travel = 0
    for s, t, f, _ in word:
        head = 0
        for i in range(L):
            for j in range(L):
                for position in (coeff[f]+i*L+j, slots[s]+j):
                    travel += abs(position-head)
                    head = position
            position = slots[t]+i
            travel += abs(position-head)
            head = position
        travel += head
    # Independent closed summation: every coefficient is to the right of data.
    closed = 0
    for s, t, f, _ in word:
        so, de, co = slots[s], slots[t], coeff[f]
        for i in range(L):
            sum_coeff = L*(co+i*L) + L*(L-1)//2
            sum_source = L*so + L*(L-1)//2
            prev = 0 if i == 0 else de+i-1
            last_source = so+L-1
            closed += 2*sum_coeff - 2*sum_source + last_source - prev + abs(de+i-last_source)
        closed += de+L-1
    require(travel == closed, "tape trace/formula mismatch")
    n = len(word)
    return dict(leaves=n, coefficient_reads=n*L*L, source_reads=n*L*L,
                target_reads=n*L, target_writes=n*L, multiplications=n*L*L,
                additions=n*L*(L+1), negations=sum(t[3]<0 for t in word)*L,
                travel_word_slots=travel, data_words=len(roles)*L,
                coefficient_words=len(factor_order)*L*L, instruction_records=n)


def check_case(case, rng):
    k, factors = case["k"], case["factors"]
    require(k >= 2 and len(case["left_lengths"]) == k, "bad fanout")
    require(0 <= case["pivot"] < k, "bad pivot")
    require(len(factors["B"]) == case["b"], "B length")
    for i in range(k):
        require(len(factors[f"A{i}"]) == case["left_lengths"][i], "A length")
    factor_order = [f for name in ["B"] + [f"A{i}" for i in range(k)] for f in factors[name]]
    require(len(factor_order) == len(set(factor_order)), "factor labels must be distinct")
    private = max((len(v)-1).bit_length() for v in factors.values())
    input_seed = rng.randrange(1 << 63)
    rows = {}
    for kind, schedule in case["schedules"].items():
        require(kind in ("borrowed", "separate", "dedicated"), "unknown kind")
        word, roles = schedule["leaves"], schedule["roles"]
        wanted_roles = ["x"] + [f"y{i}" for i in range(k)] + [f"h{i}" for i in range(private)]
        if kind == "dedicated":
            wanted_roles += ["z"]
        require(roles == wanted_roles, "unpriced/aliased row")
        require(schedule["private_rows"] == private + (kind == "dedicated"), "private invoice")
        require(all(t[2] in factor_order for t in word), "unknown factor")
        require(symbolic(word, roles) == expected(roles, factors, k), "free noncommutative endpoint")
        initial = symbolic([], roles)
        require(symbolic(reverse(word), roles, symbolic(word, roles)) == initial, "literal inverse")
        macro_factors = {name: [name] for name in factors}
        outputs = {f"y{i}" for i in range(k)}
        for s, t, f, sign in schedule["macros"]:
            require(sign in (-1, 1), "macro sign")
            if f == "B":
                require(s == "x" and t in ({"z"} if kind == "dedicated" else outputs),
                        "B query outside the alphabet")
            else:
                require(f in factors and f.startswith("A") and t == "y"+f[1:] and
                        s in ({"z"} if kind == "dedicated" else outputs-{t}),
                        "A query outside the alphabet")
        require(symbolic(schedule["macros"], roles) == expected(roles, macro_factors, k), "macro endpoint")
        # Every macro is a complete child, with all other outputs excluded even
        # temporarily. This is the distinction from unsafe ancestor-port reuse.
        offset = 0
        for source, target, name, sign in schedule["macros"]:
            nchild = leaf_count(len(factors[name]))
            child = word[offset:offset+nchild]
            permitted = {source, target} | {f"h{i}" for i in range(private)}
            require(all(s in permitted and t in permitted for s,t,_,_ in child),
                    "child borrowed a reserved output/source")
            boundary = {r: {(r, ()): 1} for r in roles}
            boundary[target][(source, tuple(reversed(factors[name])))] = sign
            require(symbolic(child, roles) == boundary, "complete child boundary")
            offset += nchild
        require(offset == len(word), "unaccounted child suffix")
        bmult = {"borrowed": 4, "separate": 2*k, "dedicated": 2}[kind]
        count = bmult*leaf_count(len(factors["B"])) + 2*sum(leaf_count(len(factors[f"A{i}"])) for i in range(k))
        counts = factor_counts(factors["B"], bmult)
        for i in range(k):
            counts += factor_counts(factors[f"A{i}"], 2)
        require(len(word) == schedule["leaf_count"] == count, "leaf recurrence")
        require(Counter(t[2] for t in word) == counts == Counter(schedule["multiplicities"]), "factor invoice")
        macro_counts = Counter(t[2] for t in schedule["macros"])
        require(macro_counts == Counter({"B": bmult, **{f"A{i}": 2 for i in range(k)}}), "macro count")
        # Three price assignments; recursive factor multiplicities are re-derived.
        prices = [[1]*len(factor_order), [1+(59+7*j)%11 for j in range(len(factor_order))],
                  [1 << (j%5) for j in range(len(factor_order))]]
        weighted = [sum(counts[f]*c for f, c in zip(factor_order, price)) for price in prices]
        dense_cases = 0
        dense_digest = hashlib.sha256()
        for L in (1, 2, 3):
            # Identical factors and common-role data for every comparator.
            rng = random.Random(input_seed + 1000*L)
            matrices = {f: [[rng.randrange(-2, 3) for _ in range(L)] for _ in range(L)] for f in factor_order}
            values = {r: [rng.randrange(-7, 8) for _ in range(L)] for r in roles}
            want = {r: list(v) for r, v in values.items()}
            for i in range(k):
                v = list(values["x"])
                for f in factors["B"] + factors[f"A{i}"]:
                    v = matrix_vector(matrices[f], v)
                want[f"y{i}"] = [a+b for a, b in zip(want[f"y{i}"], v)]
            nmax = max(v["leaf_count"] for v in case["schedules"].values())
            width = 2 + (7).bit_length() + nmax*(1+2*L).bit_length()
            actual = dense(word, matrices, values, width)
            require(actual == want, "dense endpoint")
            require(dense(reverse(word), matrices, actual, width) == values, "dense inverse")
            dense_digest.update(json.dumps({r: actual[r] for r in ["x"]+[f"y{i}" for i in range(k)]},
                                           sort_keys=True).encode())
            dense_cases += 1
        rows[kind] = dict(leaves=count, private_rows=schedule["private_rows"],
                          weighted_prices=weighted, dense_cases=dense_cases,
                          dense_output_sha256=dense_digest.hexdigest(),
                          invoice=invoice(word, roles, factor_order, 3))
    require(set(rows) == {"borrowed", "separate", "dedicated"}, "missing comparator")
    require(len({r["dense_output_sha256"] for r in rows.values()}) == 1, "comparators used different inputs/results")
    return rows


def census():
    # The written degree argument proves these are every possible optimal word
    # for k=2. Replay full free polynomials, not just their degree-two truncation.
    roles = ["x", "y0", "y1"]
    queries = [("x", "y0", "B", 1), ("x", "y0", "B", -1),
               ("x", "y1", "B", 1), ("x", "y1", "B", -1),
               ("y1", "y0", "A0", 1), ("y1", "y0", "A0", -1),
               ("y0", "y1", "A1", 1), ("y0", "y1", "A1", -1)]
    want = expected(roles, {"B":["B"], "A0":["A0"], "A1":["A1"]}, 2)
    count = 0
    digest = hashlib.sha256()
    for perm in itertools.permutations(range(8)):
        if symbolic([queries[i] for i in perm], roles) == want:
            count += 1
            digest.update(bytes(perm))
    require(count > 0, "no optimal words")
    return dict(permutations=40320, correct_words=count, correct_permutation_sha256=digest.hexdigest())


def controls(fixture):
    import copy
    controls = []
    for kind, index in [("borrowed", 0), ("borrowed", -1), ("dedicated", 0)]:
        broken = copy.deepcopy(fixture)
        broken["schedules"][kind]["leaves"].pop(index)
        controls.append((f"omit_{kind}_{index}", broken))
    broken = copy.deepcopy(fixture)
    broken["schedules"]["borrowed"]["leaves"][0][3] *= -1
    controls.append(("wrong_sign", broken))
    broken = copy.deepcopy(fixture)
    broken["factors"]["B"].reverse()
    controls.append(("reverse_noncommuting_B", broken))
    broken = copy.deepcopy(fixture)
    broken["schedules"]["borrowed"]["roles"].pop()
    controls.append(("unpriced_scratch", broken))
    broken = copy.deepcopy(fixture)
    broken["schedules"]["borrowed"]["private_rows"] -= 1
    controls.append(("underpriced_scratch", broken))
    broken = copy.deepcopy(fixture)
    broken["schedules"]["borrowed"]["leaf_count"] -= 1
    controls.append(("underpriced_child", broken))
    for label, case in controls:
        try:
            check_case(case, random.Random(59))
        except ValueError:
            pass
        else:
            raise ValueError("accepted control: " + label)
    # A concrete nonlinear counterexample to substituting rounded maps as linear.
    # k=2, A0(t)=floor(t/2), A1(t)=t, B(t)=t, x=1, y0=y1=0.
    # Borrow y1 then borrow final y0: y0 remains 0 rather than 1/2.
    nonlinear = {"x": 1, "y0": 0, "y1": 0}
    word = [("y1","y0","A0",-1),("x","y1","B",1),("y1","y0","A0",1),("x","y1","B",-1),
            ("y0","y1","A1",-1),("x","y0","B",1),("y0","y1","A1",1),("x","y0","B",-1)]
    def nonlinear_run(seq, state):
        z = dict(state)
        for s,t,f,sign in seq:
            z[t] += sign*(z[s]//2 if f == "A0" else z[s])
        return z
    actual = nonlinear_run(word, nonlinear)
    require(actual == {"x":1,"y0":0,"y1":1}, "nonlinear scope control")
    require(nonlinear_run(reverse(word), actual) == nonlinear, "nonlinear inverse")
    other = nonlinear_run(word, {"x":1,"y0":0,"y1":1})
    require(other["y0"] == 1, "nonlinear dirt dependence")
    return [name for name, _ in controls] + ["nonlinear_not_linear", "nonlinear_dirt_dependence"]


def verify():
    pins = json.loads((HERE/"SOURCES.json").read_text())
    for ref in pins["references"]:
        data = (HERE/ref["retained"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == ref["sha256"], "reference SHA256")
        require(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == ref["git_blob"], "reference Git blob")
    cert = json.loads(gzip.decompress((HERE/"CERTIFICATE.json.gz").read_bytes()))
    require(cert["schema"] == 1 and cert["seed"] == 59 and len(cert["cases"]) == 40, "domain/header")
    rng = random.Random(59)
    evidence = []
    for index, case in enumerate(cert["cases"]):
        k, b = 2+index//8, 1+index%8
        require((case["k"],case["b"],case["left_lengths"],case["pivot"]) ==
                (k,b,[1+((b+3*i)%5) for i in range(k)],59%k), "case domain")
        evidence.append(check_case(case, rng))
    fixture = cert["fixture"]
    require((fixture["k"],fixture["b"],fixture["left_lengths"],fixture["pivot"]) ==
            (3,6,[5,3,1],2), "fixture domain")
    fixture_evidence = check_case(fixture, rng)
    return dict(seed=59, grid_cases=40, fixture=fixture_evidence, cases=evidence,
                census=census(), controls=controls(fixture),
                scope="exact recursive-interface construction; no new kappa")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.write:
        (HERE/"EXPECTED.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    else:
        require(result == json.loads((HERE/"EXPECTED.json").read_text()), "complete expected receipt")
    print("PASS_OUTPUT_BORROWED_FANOUT cases=41 leaves=318->238 private_rows=3 dedicated_rows=4 census=" + str(result["census"]["correct_words"]))
