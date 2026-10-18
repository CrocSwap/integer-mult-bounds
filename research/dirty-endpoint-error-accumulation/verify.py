#!/usr/bin/env python3
"""Exact endpoint defect responses for PR628. Adam Gall + Codex; Apache-2.0."""
import argparse
import ast
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/dirty-cubic-precision/vendor/628/dirty.py"
INPUTS = {
    SOURCE,
    "research/dirty-cubic-precision/PROOF.md",
    "research/dirty-interval-coefficient-boundary/vendor/PR1085-PROOF.md",
    "research/leaf-destination-transport/README.md",
    "research/single-register-interval-transport/PROOF.md",
    "research/commuting-dirty-precision/PROOF.md",
}
DOMAIN = tuple(range(1, 33)) + (63, 64, 65, 127, 128)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def bindings(root=ROOT):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    need({row["path"] for row in rows} == INPUTS, "complete input inventory")
    for row in rows:
        raw = (root / row["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source drift: " + row["path"])
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == row["git_blob"], "source Git blob: " + row["path"])
    selection = json.loads((HERE / "SELECTION.json").read_text())
    need(selection["seed"] == "dc96b7ed19e1045ea40350f775120d39", "selection seed")
    need(selection["base_commit"] == manifest["base_commit"], "selection base")
    return {row["path"]: row["sha256"] for row in rows}


def source_compose(leaf):
    """Execute the unchanged compose AST; no numerical dependency imports."""
    tree = ast.parse((ROOT / SOURCE).read_text())
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "compose"]
    need(len(functions) == 1, "unique source compose")
    module = ast.Module(body=functions, type_ignores=[])
    namespace = {"leaf": leaf, "c": SimpleNamespace(need=need, norm2=lambda x: x*x)}
    exec(compile(module, SOURCE, "exec"), namespace)
    return namespace["compose"]


def source_events(n, orientation):
    arrays = [[0] for _ in range((n-1).bit_length()+2)]
    indices = {id(array): j for j, array in enumerate(arrays)}
    events = []

    def leaf(x, y, factor, phases, beta, bits, direction, sign, stats):
        events.append((indices[id(x)], indices[id(y)], factor, sign))

    source_compose(leaf)(arrays[0], arrays[1], list(range(n)), arrays[2:], [1], Q(1, 2), 32, 1, orientation)
    return tuple(events)


def reverse(word):
    return tuple((x, y, j, -sign) for x, y, j, sign in reversed(word))


@lru_cache(None)
def emit(n, x=0, y=1, z=2, offset=0):
    need(n >= 1, "positive number of factors")
    if n == 1:
        return ((x, y, offset, 1),)
    left = n//2
    u = emit(left, x, z, z+1, offset)
    v = emit(n-left, z, y, z+1, offset+left)
    return u + v + reverse(u) + reverse(v)


@lru_cache(None)
def counts(n):
    """All-size proof recurrence, separate from the suffix engine."""
    need(n >= 1, "positive recurrence domain")
    if n == 1:
        return (0, 1)
    left, right = counts(n//2), counts(n-n//2)
    deeper = max(len(left), len(right))-2
    return (0, left[1]+2*right[1], 2*left[1]) + tuple(
        2*((left[k+2] if k+2 < len(left) else 0) +
           (right[k+2] if k+2 < len(right) else 0)) for k in range(deeper))


def leaf_count(n):
    q = 1 << (n.bit_length()-1)
    return 3*q*n - 2*q*q


def formal_responses(word, dimension):
    """Right-multiply suffix matrices; free words keep order and repetitions."""
    suffix = [[{(): 1} if i == j else {} for j in range(dimension)] for i in range(dimension)]
    responses = [None]*len(word)
    for t in range(len(word)-1, -1, -1):
        x, y, factor, sign = word[t]
        need(x != y, "distinct shear registers")
        column = tuple(dict(suffix[i][y]) for i in range(dimension))
        for polynomial in column:
            need(len(polynomial) <= 1, "endpoint response has multiple monomials")
            for monomial, coefficient in polynomial.items():
                need(abs(coefficient) == 1, "endpoint coefficient not a unit")
                need(all(a > b for a, b in zip(monomial, monomial[1:])), "unordered endpoint monomial")
        responses[t] = column
        # S <- S E_t. This appends A_factor on the RIGHT, not the left.
        for i in range(dimension):
            for monomial, coefficient in suffix[i][y].items():
                key = monomial + (factor,)
                value = suffix[i][x].get(key, 0) + sign*coefficient
                if value:
                    suffix[i][x][key] = value
                else:
                    suffix[i][x].pop(key, None)
    return responses, suffix


def encode_responses(responses):
    return [[[list(m), c] for m, c in sorted(poly.items())] for col in responses for poly in col]


def scalar_execute(word, factors, initial, errors):
    need(len(errors) == len(word), "one defect per executed leaf")
    state = list(initial)
    for (x, y, factor, sign), error in zip(word, errors):
        state[y] += sign*factors[factor]*state[x] + error
    return state


def census(n, orientation):
    word = emit(n) if orientation == 1 else reverse(emit(n))
    need(word == source_events(n, orientation), "source dispatcher sequence")
    need(len(word) == leaf_count(n), "complete paid leaf count")
    dimension = (n-1).bit_length()+2
    responses, endpoint = formal_responses(word, dimension)
    total = tuple(sum(bool(col[row]) for col in responses) for row in range(dimension))
    need(total == counts(n), "endpoint response count recurrence")
    expected = [[{(): 1} if i == j else {} for j in range(dimension)] for i in range(dimension)]
    expected[1][0] = {tuple(range(n-1, -1, -1)): orientation}
    need(endpoint == expected, "full product shear and restoration")
    witnesses = []
    for row in sorted({1, max(range(dimension), key=total.__getitem__)}):
        errors = [sum(col[row].values()) for col in responses]
        final = scalar_execute(word, [1]*n, [0]*dimension, errors)
        need(final[row] == total[row], "simultaneous signed-defect attainment")
        witnesses.append({"row": row, "error_signs_sha256": hashlib.sha256(canonical(errors)).hexdigest(),
                          "final_state": final})
    return {"n": n, "orientation": orientation, "paid_leaves": len(word), "response_counts": total,
            "response_sha256": hashlib.sha256(canonical(encode_responses(responses))).hexdigest(),
            "attainment": witnesses}


def rounded_models():
    """Exact rounded model leaves on the actual AST, not PR628 numerical kernels."""
    rows = []
    for n in (2, 3, 4, 5, 8, 12):
        for orientation in (1, -1):
            factors = tuple((Q(2, 3), Q(-3, 5), Q(4, 7))[j % 3] for j in range(n))
            dimension = (n-1).bit_length()+2
            for dirt in (-11, 1, 7):
                initial = [dirt+2*i+1 for i in range(dimension)]
                arrays = [[value] for value in initial]
                errors = []

                def leaf(x, y, factor, phases, beta, bits, direction, sign, stats):
                    ideal = factors[factor]*x[0]
                    rounded = (ideal + Q(1, 2)).numerator // (ideal + Q(1, 2)).denominator
                    errors.append(sign*(rounded-ideal))
                    y[0] += sign*rounded

                compose = source_compose(leaf)
                compose(arrays[0], arrays[1], list(range(n)), arrays[2:], [1], Q(1, 2), 32, 1, orientation)
                word = source_events(n, orientation)
                actual = [array[0] for array in arrays]
                ideal = scalar_execute(word, factors, initial, [Q(0)]*len(word))
                need(scalar_execute(word, factors, initial, errors) == actual, "actual-trajectory variation of constants")
                need(actual[0] == initial[0] and actual[2:] == initial[2:], "rounded model dirty restoration")
                need(max(map(abs, errors)) <= Q(1, 2), "nearest rounding local error")
                need(any(errors), "genuine nonzero rounded defects")
                error = abs(actual[1]-ideal[1])
                need(error <= Q(counts(n)[1], 2), "cumulative target bound")
                compose(arrays[0], arrays[1], list(range(n)), arrays[2:], [1], Q(1, 2), 32, 1, -orientation)
                need([array[0] for array in arrays] == initial, "literal rounded inverse")
                rows.append({"n": n, "orientation": orientation, "dirt": dirt, "target_error": str(error),
                             "largest_leaf_error": str(max(map(abs, errors[:len(word)])))})
    return rows


def ceil_log2(n):
    need(n >= 1, "positive logarithm argument")
    return (n-1).bit_length()


def budget_terms(N, T, K, J, H, A, p, m, closure=0, input_grid=0):
    need(N >= T >= 1, "endpoint and paid call counts")
    need(min(K, J, H, A, p, m, closure, input_grid) >= 0, "nonnegative budget exponents")
    return {"input_grid": input_grid, "closure": closure,
            "feedback": 1+ceil_log2(N)+H+A,
            "target_accuracy": p+3+ceil_log2(T)+K+A+m+J}


def precision_example():
    # Exactly PR1295/commuting-dirty-precision's PR1054 contract, not PR905.
    r, p, m, phi = 64, 128, 20, 32
    n = r-1
    ell, h = ceil_log2(r), ceil_log2(n)
    d0 = 1+2*ell+r*n*phi
    a0 = 2*d0+r+2
    g = d0+ell+2*r+2
    K = a0+2*r+ell
    c = ceil_log2(h+2)
    J, H = K+c, K+2*c
    A = 5*g+ceil_log2(68*(r+1))
    N, T = leaf_count(n), counts(n)[1]
    terms = budget_terms(N, T, K, J, H, A, p, m, closure=4*g+16)
    old = max(0, 4*g+16, p+3+ceil_log2(N)+A+m+J+H)
    width = max(terms.values())
    # Exact powers-of-two exponents certify, without constructing million-bit rationals.
    feedback_exponent = ceil_log2(N)+H+A-width
    error_exponent = 1+ceil_log2(T)+K+A+(J+m+1)-width
    need(feedback_exponent <= -1, "interior feedback retained")
    need(error_exponent <= -p-1, "target half-error allowance")
    return {"contract": "PR1054 via PR1295; all inherited preparation and leaf premises",
            "r": r, "p": p, "m": m, "N": N, "T": T, "dirty_arrays": h,
            "K": K, "J": J, "H": H, "A": A, "old_fractional_bits": old,
            "new_fractional_bits": width, "terms": terms,
            "feedback_power_of_two_exponent": feedback_exponent,
            "target_error_power_of_two_exponent": error_exponent,
            "unchanged_signed_integer_bits": J+m+8*g+2*ell+16,
            "unchanged_factor_bits": max(n*ell, max(d0+1, a0+1, p+2*a0+m+4)+r+3)}


def run():
    pins = bindings()
    rows = [census(n, sign) for n in DOMAIN for sign in (1, -1)]
    for h in range(21):
        expected = (0, 3**h) + tuple(2*4**(k-1)*3**(h-k) for k in range(1, h+1))
        need(counts(2**h) == expected, "power-of-two closed formula")
    result = {"status": "PASS_DIRTY_ENDPOINT_ERROR_ACCUMULATION", "source_sha256": pins,
              "rows": rows, "paid_leaf_occurrences": sum(row["paid_leaves"] for row in rows),
              "power_of_two_formula_checks": 21, "rounded_model_cases": rounded_models(),
              "precision_example": precision_example(), "new_kappa": False,
              "scope": "All-size written endpoint theorem; finite source and algebra evidence, not physical/rounded-kernel admission"}
    # Normalize tuples identically across direct and JSON receipt modes.
    return json.loads(json.dumps(result))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path, help="authoring only; refuse existing paths")
    args = parser.parse_args()
    result = run()
    if args.write:
        with args.write.open("x") as output:
            json.dump(result, output, indent=2)
            output.write("\n")
    else:
        need(result == json.loads((HERE / "RESULT.json").read_text()), "complete receipt mismatch")
    example = result["precision_example"]
    print(result["status"], "leaf_occurrences="+str(result["paid_leaf_occurrences"]),
          "T63="+str(example["T"]), "conditional_fractional_bits="+
          str(example["old_fractional_bits"])+"->"+str(example["new_fractional_bits"]), "no_new_kappa")


if __name__ == "__main__":
    main()
