"""Optional direct modular check against the original CTblLib 1.3.11 archive.

Evaluate full character rows at an exact root of unity in a prime field.
No extracted tables, symbolic expression evaluator, or third-party libraries
are required. apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""
from argparse import ArgumentParser
from functools import cache
from hashlib import sha256
from math import isqrt, prod
from pathlib import Path
import json
import re
import tarfile

PRIME = 37778931862957162935091
CONDUCTOR = 17 * 31 * 33
ARCHIVE_SHA = "f201e9da571c681a7bbfb1e4683bdb2c80a23b005099ed0453521f59cb443434"
CERTIFICATES = {
    PRIME: (2, (2, 3, 3, 3, 5, 11, 17, 31, 41, 588706395077371)),
    588706395077371: (2, (2, 3, 5, 19623546502579)),
    19623546502579: (3, (2, 3, 3, 3, 4217, 86174771)),
}
STEP = re.compile(r"[+-]?(?:\d+\*)?E\(\d+\)(?:\^\d+)?|[+-]?\d+")
ROOT_TERM = re.compile(r"([+-]?)(?:(\d+)\*)?E\((\d+)\)(?:\^(\d+))?")


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


@cache
def certify_prime(n):
    if n < 10**8:
        need(n >= 2 and all(n % k for k in range(2, isqrt(n) + 1)), "Composite trial factor")
        return
    generator, factors = CERTIFICATES[n]
    need(prod(factors) == n - 1 and pow(generator, n-1, n) == 1, "Primality factorization")
    for q in set(factors):
        certify_prime(q)
        need(pow(generator, (n-1)//q, n) != 1, "Generator order is too small")
    # An element of exact order n-1 in (Z/n)^* forces n prime.


def first_list(text):
    start = text.index("[")
    depth = 0
    for j in range(start, len(text)):
        depth += int(text[j] == "[") - int(text[j] == "]")
        if depth == 0:
            return text[start:j+1], text[j+1:]
    raise ValueError("Unterminated GAP list")


def evaluate_table(source, name, root):
    data = source.split('MOT("' + name + '",', 1)[1]
    _, data = first_list(data)
    centralizers, data = first_list(data)
    centralizers = json.loads(centralizers)
    _, data = first_list(data)
    values, _ = first_list(data)
    values = "".join(values[1:-1].split())
    descriptions = []
    while values:
        row, values = first_list(values)
        values = values.removeprefix(",")
        ref = re.fullmatch(r"\[(TENSOR|GALOIS),\[(\d+),(\d+)\]\]", row)
        descriptions.append(ref.groups() if ref else (None, row[1:-1].split(","), None))

    @cache
    def value(token, power):
        total = 0
        terms = STEP.findall(token)
        need("".join(terms) == token, "Unsupported cyclotomic expression")
        for term in terms:
            if "E(" not in term:
                total += int(term)
                continue
            sign, scale, order, exponent = ROOT_TERM.fullmatch(term).groups()
            n = int(order)
            need(CONDUCTOR % n == 0, "Unsupported root order")
            k = (CONDUCTOR//n) * power * int(exponent or 1) % CONDUCTOR
            total += (-1 if sign == "-" else 1) * int(scale or 1) * pow(root, k, PRIME)
        return total % PRIME

    @cache
    def row(index, power):
        op, a, b = descriptions[index]
        if op == "GALOIS":
            return row(int(a)-1, power * int(b) % CONDUCTOR)
        if op == "TENSOR":
            return [(x*y) % PRIME for x, y in zip(row(int(a)-1, power), row(int(b)-1, power), strict=True)]
        need(len(a) == len(centralizers), "Class count")
        return [value(entry, power) for entry in a]

    need(len(descriptions) == len(centralizers), "Non-square table")
    return centralizers, [row(j, 1) for j in range(len(descriptions))]


def check_blocks(centralizers, characters, dimensions, projection, t, width):
    order = centralizers[0]
    need(projection["order"] == order and order % PRIME, "Group order")
    class_sizes = [order//c for c in centralizers]
    need(sum(class_sizes) == order, "Class-size sum")
    weights = [size * t**d % PRIME for size, d in zip(class_sizes, dimensions, strict=True)]
    for char, (degree, *bins) in zip(characters, projection["rows"], strict=True):
        need(char[0] == degree and len(bins) == 11, "Degree or fixed-space bins")
        direct = sum(c*w for c, w in zip(char, weights, strict=True)) * pow(order, -1, PRIME) % PRIME
        integer, rem = divmod(sum(b*t**j for j, b in enumerate(bins)), order)
        need(rem == 0 and 0 <= integer <= 32**width and integer == direct,
             "Direct cyclic-root calculation disagrees with the projection")
    return len(characters)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    path = parser.parse_args().archive
    need(sha256(path.read_bytes()).hexdigest() == ARCHIVE_SHA, "Wrong CTblLib archive")
    certify_prime(PRIME)
    need(PRIME > 32**15 and (PRIME-1) % CONDUCTOR == 0, "Insufficient field")
    root = pow(2, (PRIME-1)//CONDUCTOR, PRIME)
    need(pow(root, CONDUCTOR, PRIME) == 1 and
         all(pow(root, CONDUCTOR//q, PRIME) != 1 for q in (3, 11, 17, 31)), "Root order")
    tables = json.loads(Path(__file__).with_name("PROJECTION.json").read_text(encoding="utf-8"))
    with tarfile.open(path, "r:gz") as archive:
        def source(name):
            with archive.extractfile("ctbllib-1.3.11/data/" + name) as f:
                return f.read().decode("latin-1")

        name = "S10(2)"
        cents, rows = evaluate_table(source("ctosymp1.tbl"), name, root)
        a, b = [v for v in rows if v[0] in (495, 527)]
        dims = []
        for x, y in zip(a, b, strict=True):
            count = (2+x+y) % PRIME
            need(count > 0 and count & (count-1) == 0, "Binary fixed-space count")
            dims.append(count.bit_length()-1)
        checked = sum(check_blocks(cents, rows, dims, tables[name], t, f)
                      for t, f in ((-64, 13), (128, 15)))
        orthogonal = source("ctoorth3.tbl")
        for name in ("O10+(2).2", "O10-(2).2"):
            cents, rows = evaluate_table(orthogonal, name, root)
            data = orthogonal.split('ALF("' + name + '","S10(2)",', 1)[1]
            fusion = json.loads(first_list(data)[0])
            need(len(fusion) == len(cents) and all(1 <= j <= len(dims) for j in fusion), "Class fusion")
            checked += check_blocks(cents, rows, [dims[j-1] for j in fusion], tables[name], -64, 14)
    need(checked == 715, "Incomplete width-specific check")
    print(f"PASS_DIRECT_MODULAR_ARCHIVE prime={PRIME} root_order={CONDUCTOR} "
          f"width_specific_multiplicities={checked}")


if __name__ == "__main__":
    main()
