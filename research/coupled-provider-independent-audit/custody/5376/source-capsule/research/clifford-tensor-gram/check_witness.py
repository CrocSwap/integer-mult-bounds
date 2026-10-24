"""Check a tensor entry by a separate signed-word interpreter.

This module does not import the certificate producer or use Gram traces.
It shares only the frozen exact scalar arithmetic. Word support can grow.
Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))
from fields import Gaussian as G


def need(ok, message):
    if not ok:
        raise ValueError(message)


def star(a):
    return tuple(tuple(G.pair(a[j][i].real, -a[j][i].imag)
                       for j in range(len(a))) for i in range(len(a)))


def product(a, b):
    return tuple(tuple(sum((x*y for x, y in zip(row, column)), G(0))
                       for column in zip(*b)) for row in a)


def eye(d):
    return tuple(tuple(G(int(i == j)) for j in range(d)) for i in range(d))


def add_term(row, word, coefficient):
    row[word] = row.get(word, G(0))+coefficient
    if not row[word]:
        del row[word]


def word_endpoint(problem, instructions, input_role):
    r = problem["roles"]
    rows = [{(): G(1)} if j == input_role else {} for j in range(r)]
    for instruction in instructions:
        kind, d = instruction["op"], instruction["dst"]
        need(type(d) is int and 0 <= d < r, "Destination role")
        s = instruction.get("src", d)
        need(type(s) is int and 0 <= s < r, "Source role")
        if kind == "swap":
            rows[d], rows[s] = rows[s], rows[d]
            continue
        if kind == "scale":
            coefficient = G(instruction["coefficient"])
            rows[d] = {w: coefficient*c for w, c in rows[d].items() if coefficient*c}
            continue
        image = rows[s].copy()
        if kind in ("query", "apply"):
            symbol, inverse = instruction["symbol"], instruction.get("inverse", False)
            need(symbol in problem["operators"] and type(inverse) is bool, "Operator reference")
            letter = (symbol, inverse)
            image = {}
            for word, coefficient in rows[s].items():
                if word and word[0] == (symbol, not inverse):
                    new_word = word[1:]
                else:
                    new_word = (letter,)+word
                add_term(image, new_word, coefficient)
        if kind == "apply":
            rows[d] = image
        else:
            need(kind in ("add", "query"), "Instruction kind")
            coefficient = G(instruction.get("coefficient", 1))
            updated = rows[d].copy()
            for word, value in image.items():
                add_term(updated, word, coefficient*value)
            rows[d] = updated
    return rows


def matrices(problem):
    d = 1 << problem["axes"]
    bank = {}
    for name, rows in problem["operators"].items():
        a = tuple(tuple(G(x) for x in row) for row in rows)
        need(len(a) == d and all(len(row) == d for row in a), "Matrix shape")
        inverse = star(a)
        need(product(a, inverse) == eye(d), "Inverse requires a unitary matrix")
        bank[name, False], bank[name, True] = a, inverse
    return bank


def evaluate_word(word, bank, d):
    out = eye(d)
    for letter in word:
        out = product(out, bank[letter])
    return out


def discrepancy(problem, output_role, input_role, output_tuple, input_tuple):
    width = len(output_tuple)
    d, r = 1 << problem["axes"], problem["roles"]
    need(width > 0 and len(input_tuple) == width, "Positive tensor width")
    need(all(type(x) is int and 0 <= x < d for x in output_tuple+input_tuple), "Tensor coordinate")
    need(type(output_role) is int and 0 <= output_role < r and
         type(input_role) is int and 0 <= input_role < r, "Endpoint role")
    bank = matrices(problem)
    left = word_endpoint(problem, problem["program"], input_role)[output_role]
    right = word_endpoint(problem, problem["reference"], input_role)[output_role]
    words = left.copy()
    for word, coefficient in right.items():
        add_term(words, word, -coefficient)
    answer = G(0)
    for word, coefficient in words.items():
        a = evaluate_word(word, bank, d)
        value = coefficient
        for x, y in zip(output_tuple, input_tuple):
            value = value*a[x][y]
        answer = answer+value
    return answer


def check(problem, certificate):
    need(certificate.get("schema") == "clifford-tensor-gram/v1", "Certificate schema")
    digest = hashlib.sha256(json.dumps(problem, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    need(certificate.get("problem_sha256") == digest, "Problem digest")
    need(type(certificate.get("axes")) is int and certificate["axes"] == problem["axes"], "Axis count")
    need(type(certificate.get("cutoff")) is int and certificate["cutoff"] == 8*problem["axes"]+4, "Cutoff")
    need(certificate["equivalent_at_all_positive_widths"] is False, "Expected a negative certificate")
    failure = certificate["failure"]
    witness = failure["witness"]
    need(type(witness["width"]) is int and 1 <= witness["width"] <= certificate["cutoff"], "Witness width")
    need(witness["width"] == len(witness["input_tuple"]) == len(witness["output_tuple"]), "Width mismatch")
    value = discrepancy(problem, failure["output_role"], failure["input_role"],
                        witness["output_tuple"], witness["input_tuple"])
    need(value != 0 and value == G(witness["discrepancy"]), "The literal discrepancy does not match")
    return str(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", type=Path)
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    value = check(json.loads(args.problem.read_text()), json.loads(args.certificate.read_text()))
    print("PASS_LITERAL_TENSOR_WITNESS", value)


if __name__ == "__main__":
    main()
