#!/usr/bin/env python3
"""Exact bounded corroboration; the universal statement is in PROOF.md.

Default replay is read-only. --write-examples regenerates committed examples.
Prepared for Krzysztof Wójt with OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from copy import deepcopy
from itertools import product
import json
from pathlib import Path
import random

from algebra import compile_program, produce, row_times
from check_certificate import check, reconstruct
from certify import explicit_witness
from fields import Field
from oracles import apply_witness, literal_endpoint, reduced_word_endpoint
from syntax import fingerprint, validate

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def expect_reject(function, label):
    try:
        function()
    except (ValueError, TypeError, KeyError):
        return
    raise RuntimeError(f"negative control accepted: {label}")


def apply(dst, operator, direction=1):
    return {"op": "apply", "dst": dst, "operator": operator, "direction": direction}


def query(dst, src, operator, direction=1, coefficient=1):
    return {"op": "query", "dst": dst, "src": src, "operator": operator,
            "direction": direction, "coefficient": coefficient}


def linear(dst, terms):
    return {"op": "linear", "dst": dst, "terms": [[name, c] for name, c in terms]}


def program(left, right=(), roles=("x",), operators=("A", "B"), field=0):
    return {"schema": "inverse-dirty-program/v1", "field": field,
            "roles": list(roles), "operators": list(operators),
            "left": list(left), "right": list(right)}


def dirty_sandwich(field=0):
    # h is arbitrary dirty. Both programs finish at (x,h,y+B A x).
    left = [apply("h", "A", -1), linear("h", [("h", 1), ("x", 1)]),
            apply("h", "A"), query("y", "h", "B"), apply("h", "A", -1),
            linear("h", [("h", 1), ("x", -1)]), apply("h", "A"),
            query("y", "h", "B", coefficient=-1)]
    right = [apply("x", "A"), query("y", "x", "B"), apply("x", "A", -1)]
    return program(left, right, roles=("x", "h", "y"), field=field)


def wrong_order(field=0):
    return program([apply("x", "A"), apply("x", "B"),
                    apply("x", "A", -1), apply("x", "B", -1)], field=field)


def inverse_tail(degree, field=0):
    # G^-1 (I-G)^degree has an infinite series starting at degree.
    return program([query("x", "x", "A", coefficient=-1)] * degree + [apply("x", "A", -1)],
                   [linear("x", [])], operators=("A",), field=field)


def inspect(data, expected=None, literal=True):
    model = compile_program(data)
    f, u, t, v = reconstruct(data)
    require(model["U"] == u and model["T"] == t and model["V"] == v,
            "independent feedback compilers disagree")
    certificate = produce(data)
    summary = check(data, certificate)
    if expected is not None:
        require(certificate["verdict"] == expected, "unexpected universal verdict")
    if literal:
        endpoint = reduced_word_endpoint(data)
        require((not any(endpoint)) == (certificate["verdict"] == "equal"),
                "compact verdict disagrees with literal reduced group words")
    if certificate["verdict"] == "different":
        word = certificate["word"]
        require(len(word) < model["dimension"], "distinguishing length exceeds state bound")
        witness = apply_witness(data, word, data["roles"][certificate["input"]])
        require(witness[certificate["output"]][0] == f.parse(certificate["coefficient"]),
                "literal invertible matrices do not realize the coefficient")
    return certificate, summary


def inverse_word_cases():
    count = 0
    alphabet = [("A", 1), ("A", -1), ("B", 1), ("B", -1)]
    for length in range(1, 4):
        for word in product(alphabet, repeat=length):
            instructions = [apply("x", a, sign) for a, sign in word]
            inverse = [apply("x", a, -sign) for a, sign in reversed(word)]
            for characteristic in (0, 2, 5):
                p = program(instructions + inverse, roles=("x", "dirty"), field=characteristic)
                inspect(p, "equal")
                p["left"].pop()
                inspect(p, "different")
                count += 2
    return count


def differential_cases():
    rng = random.Random(20261023)
    count = positives = 0
    for characteristic in (0, 2, 3, 7):
        scalars = [-2, -1, 0, 1, 2, "1/5"]
        for trial in range(40):
            roles = ["x", "h", "y"]
            steps = []
            for _ in range(8):
                dst, src = rng.choice(roles), rng.choice(roles)
                symbol, sign = rng.choice(["A", "B"]), rng.choice([-1, 1])
                kind = rng.randrange(3)
                if kind == 0:
                    steps.append(apply(dst, symbol, sign))
                elif kind == 1:
                    steps.append(query(dst, src, symbol, sign, rng.choice(scalars)))
                else:
                    steps.append(linear(dst, [(dst, rng.choice(scalars)), (src, rng.choice(scalars))]))
            p = program(steps, deepcopy(steps), roles=roles, field=characteristic)
            position = rng.randrange(len(steps) + 1)
            dst, symbol = rng.choice(roles), rng.choice(["A", "B"])
            p["left"][position:position] = [apply(dst, symbol, -1), apply(dst, symbol)]
            if trial % 2:
                p["left"].append(query("y", "h", "A", -1, 1))
            certificate, _ = inspect(p)
            positives += certificate["verdict"] == "equal"
            count += 1
    return {"total": count, "equal": positives, "different": count - positives}


def boundary_cases():
    checked = 0
    for characteristic in (0, 2, 3, 5, 7):
        good = dirty_sandwich(characteristic)
        inspect(good, "equal")
        for i in range(len(good["left"])):
            bad = deepcopy(good)
            bad["left"].pop(i)
            inspect(bad, "different")
            checked += 1
        inspect(wrong_order(characteristic), "different")
        inspect(program([apply("h", "A")], roles=("x", "h"), field=characteristic), "different")
        self_query = program([query("x", "x", "A", -1), apply("x", "A")],
                             [query("x", "x", "A")], field=characteristic)
        inspect(self_query, "equal")
        checked += 4
    inspect(program([], operators=()), "equal")
    inspect(program([linear("x", [("x", 2)])], operators=()), "different")
    inspect(program([query("x", "x", "A", coefficient=2)], field=0), "different")
    inspect(program([query("x", "x", "A", coefficient=2)], field=2), "equal")
    return checked + 4


def shortest_and_infinite_tail_cases():
    count = 0
    for characteristic in (0, 2, 3, 5):
        for degree in range(1, 9):
            p = inverse_tail(degree, characteristic)
            certificate, _ = inspect(p)
            require(certificate["word"] == ["A"] * degree, "unexpected first inverse-tail coefficient")
            model = compile_program(p)
            f = model["field"]
            row = model["U"][0]
            for k in range(degree + 5):
                coefficient = row_times(row, model["V"], f)[0]
                expected = f.zero if k < degree else f.parse(-1 if k % 2 else 1)
                require(coefficient == expected, "inverse series truncated or wrong feedback sign")
                row = row_times(row, model["T"]["A"], f)
            count += 1
    for p in (2, 3, 5, 7):
        data = program([apply("x", "A")] * p, operators=("A",), field=p)
        certificate, summary = inspect(data, "different")
        require(len(certificate["word"]) == p and summary["witness_dimension"] == p + 1,
                "positive-characteristic delayed witness lost")
        count += 1
    return count


def matrix_cases():
    checked = 0
    for characteristic in (0, 2, 3, 5):
        p = dirty_sandwich(characteristic)
        for a, b, c, d in product(range(3), repeat=4):
            operators = {"A": [[1 + a*b, a], [b, 1]],
                         "B": [[1, c], [d, 1 + c*d]]}
            endpoint = literal_endpoint(p, operators)
            require(all(not value for output in endpoint for block in output for row in block for value in row),
                    "dirty sandwich fails on exact invertible matrices")
            checked += 1
        expect_reject(lambda: literal_endpoint(p, {"A": [[1, 0], [0, 0]], "B": [[1, 0], [0, 1]]}),
                      "singular actual inverse")
    return checked


def certificate_rejections():
    p = dirty_sandwich()
    good = produce(p)
    failures = []
    bad = deepcopy(good); bad["program_sha256"] = "0" * 64; failures.append((p, bad, "binding"))
    bad = deepcopy(good); bad["schema"] = "unknown"; failures.append((p, bad, "schema"))
    bad = deepcopy(good); bad["initial"].pop(); failures.append((p, bad, "omitted return"))
    bad = deepcopy(good); bad["closure"].pop("A"); failures.append((p, bad, "omitted generator"))
    bad = deepcopy(good); bad["initial"][0][0] = "999"; failures.append((p, bad, "initial coordinates"))
    bad = deepcopy(good); bad["closure"]["A"][0][0] = "999"; failures.append((p, bad, "closure coordinates"))
    bad = deepcopy(good); bad["paths"][0]["word"] = ["absent"]; failures.append((p, bad, "unknown path"))
    bad = deepcopy(good); bad["paths"][0]["output"] = 3; failures.append((p, bad, "outside role boundary"))
    bad = deepcopy(good); bad["paths"][0]["output"] = True; failures.append((p, bad, "bool index"))
    bad = deepcopy(good); bad["paths"][0]["word"] = ["A"] * 20; failures.append((p, bad, "path bound"))
    bad = deepcopy(good); bad["unexpected"] = 1; failures.append((p, bad, "extra field"))
    changed = deepcopy(p); changed["left"][0]["direction"] = 1; failures.append((changed, good, "changed inverse"))
    negative = wrong_order()
    different = produce(negative)
    bad = deepcopy(different); bad["coefficient"] = "0"; failures.append((negative, bad, "zero witness"))
    bad = deepcopy(different); bad["word"] = []; failures.append((negative, bad, "false scalar witness"))
    bad = deepcopy(different); bad["word"] = list(reversed(bad["word"])); failures.append((negative, bad, "reversed word coefficient"))
    scalar = program([linear("x", [("x", 2)])], operators=())
    forged = {"schema": "inverse-dirty-certificate/v1", "program_sha256": fingerprint(scalar),
              "verdict": "equal", "paths": [{"output": 0, "word": []}], "initial": [["1"]], "closure": {}}
    failures.append((scalar, forged, "nonzero projected invariant"))
    for data, certificate, label in failures:
        expect_reject(lambda: check(data, certificate), label)
    return len(failures)


def syntax_rejections():
    good = dirty_sandwich()
    cases = []
    for field in (1, 4, -1, True, 2**31):
        bad = deepcopy(good); bad["field"] = field; cases.append(bad)
    bad = deepcopy(good); bad["roles"] = ["x", "x", "y"]; cases.append(bad)
    bad = deepcopy(good); bad["roles"] = []; cases.append(bad)
    bad = deepcopy(good); bad["operators"] = ["A"]; cases.append(bad)
    bad = deepcopy(good); bad["left"][0]["direction"] = True; cases.append(bad)
    bad = deepcopy(good); bad["left"][0]["direction"] = 0; cases.append(bad)
    bad = deepcopy(good); bad["left"][0]["dst"] = "hidden"; cases.append(bad)
    bad = deepcopy(good); bad["left"][1]["terms"][0][1] = 1.5; cases.append(bad)
    bad = deepcopy(good); bad["left"][1]["terms"][0][1] = True; cases.append(bad)
    bad = deepcopy(good); bad["field"] = 2; bad["left"][1]["terms"][0][1] = "1/2"; cases.append(bad)
    bad = deepcopy(good); bad["outputs"] = ["x"]; cases.append(bad)
    for bad in cases:
        expect_reject(lambda: validate(bad), "invalid program syntax")
    return len(cases)


def stress_case(stages=64):
    steps = []
    for _ in range(stages):
        steps.extend([linear("h", [("x", 1)]), apply("x", "A"), query("x", "h", "B")])
    data = program(steps + [apply("x", "C", -1), apply("x", "C")], steps,
                   roles=("x", "h"), operators=("A", "B", "C"))
    _, summary = inspect(data, "equal", literal=False)
    summary["unexpanded_endpoint_words"] = str(2**stages)
    return summary


def examples(write=False):
    values = {"dirty-sandwich": dirty_sandwich(), "wrong-order": wrong_order(),
              "binary-inverse-tail": inverse_tail(5, 2)}
    directory = HERE / "examples"
    if write:
        directory.mkdir(exist_ok=True)
    for name, data in values.items():
        certificate = produce(data)
        artifacts = [(".json", data), (".certificate.json", certificate)]
        if certificate["verdict"] == "different":
            artifacts.append((".witness.json", explicit_witness(data, certificate)))
        for suffix, value in artifacts:
            path = directory / (name + suffix)
            text = json.dumps(value, indent=2) + "\n"
            if write:
                path.write_text(text, encoding="utf-8")
            else:
                require(path.read_text(encoding="utf-8") == text, "committed example does not regenerate")
        check(data, certificate)
    return len(values)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-examples", action="store_true")
    parser.add_argument("--quick", action="store_true", help="development smoke only, not a full replay")
    args = parser.parse_args()
    result = {"examples": examples(args.write_examples),
              "boundary_cases": boundary_cases(),
              "certificate_rejections": certificate_rejections(),
              "syntax_rejections": syntax_rejections()}
    if not args.quick:
        result.update(inverse_word_cases=inverse_word_cases(),
                      differential_cases=differential_cases(),
                      inverse_tail_cases=shortest_and_infinite_tail_cases(),
                      literal_matrix_cases=matrix_cases(), stress=stress_case())
    result["status"] = "PASS_INVERSE_DIRTY_CERTIFICATES" if not args.quick else "SMOKE_ONLY"
    result["scope"] = "Exact finite corroboration of PROOF.md; no native/physical admission or new kappa."
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
