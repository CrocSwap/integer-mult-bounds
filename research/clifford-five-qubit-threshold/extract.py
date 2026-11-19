"""Regenerate the fixed-space projections from the official CTblLib 1.3.11 archive.

The three tables use integer entries, sums of roots of unity, Galois row
references, and tensor products by a rational sign row. No GAP expressions
are executed. The default mode compares the rebuilt numerical data.
apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction
from functools import cache
from hashlib import sha256
import json
from math import gcd
from pathlib import Path
import re
import tarfile

ROOT = Path(__file__).resolve().parent
ARCHIVE = "f201e9da571c681a7bbfb1e4683bdb2c80a23b005099ed0453521f59cb443434"
MEMBERS = {
    "ctosymp1.tbl": "461519e33cb31b2bc46f554b09f283f0afb7125fd805840d79bfc614fce75b6f",
    "ctoorth3.tbl": "736b8f34211dd8a20c51312015fa72c1bb0a4931db19b317ea436ac0e9644626",
}
GROUP = "S10(2)"
SUBGROUPS = ("O10+(2).2", "O10-(2).2")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value):
    value = Fraction(value)
    require(value.denominator == 1, "Nonintegral projected character sum")
    return value.numerator


def take_list(text):
    start = text.index("[")
    depth = 0
    for pos in range(start, len(text)):
        if text[pos] == "[":
            depth += 1
        elif text[pos] == "]":
            depth -= 1
            if depth == 0:
                return text[start:pos+1], text[pos+1:]
    raise ValueError("Unterminated table list")


@cache
def root_trace(n, k):
    """Normalized field trace of a root of unity of exact order m."""
    m = n // gcd(n, k)
    reduced, mu = m, 1
    for p in range(2, m+1):
        if reduced % p == 0:
            reduced //= p
            if reduced % p == 0:
                return Fraction(0)
            mu = -mu
    return Fraction(mu, sum(gcd(j, m) == 1 for j in range(m)))


@cache
def rational_trace(word):
    if "E(" not in word:
        return int(word)
    terms = re.findall(r"([+-]?)(?:(\d+)\*)?E\((\d+)\)(?:\^(\d+))?|([+-]?\d+)", word)
    rebuilt = "".join(const or sign + (coeff+"*" if coeff else "") + "E(" + n + ")" + ("^" + k if k else "")
                      for sign, coeff, n, k, const in terms)
    require(rebuilt == word, "Unrecognized cyclotomic table entry: "+word)
    return sum(int(const) if const else
               (-1 if sign == "-" else 1) * int(coeff or 1) * root_trace(int(n), int(k or 1))
               for sign, coeff, n, k, const in terms)


def character_data(source, name):
    rest = source.split(f'MOT("{name}",', 1)[1]
    _, rest = take_list(rest)
    centralizers, rest = take_list(rest)
    centralizers = json.loads(centralizers)
    _, rest = take_list(rest)
    raw, _ = take_list(rest)
    raw = "".join(raw[1:-1].split())
    rows = []
    while raw:
        record, raw = take_list(raw)
        raw = raw.removeprefix(",")
        reference = re.fullmatch(r"\[(GALOIS|TENSOR),\[(\d+),(\d+)\]\]", record)
        if reference:
            operation, index, exponent = reference.groups()
            row = rows[int(index)-1]
            if operation == "TENSOR":
                sign = rows[int(exponent)-1]
                require(all(v in (-1, 1) for v in sign), "Non-sign tensor factor")
                row = [a*b for a,b in zip(row, sign, strict=True)]
            rows.append(row)
        else:
            row = [rational_trace(word) for word in record[1:-1].split(",")]
            require(len(row) == len(centralizers), "Wrong class count")
            rows.append(row)
    require(len(rows) == len(centralizers), "Table is not square")
    return centralizers, rows


def fixed_dimensions(rows):
    summands = [row for row in rows if row[0] in (495, 527)]
    require(len(summands) == 2 and sum(row[0] for row in summands) == 1022,
            "Natural rank-three character constituents")
    counts = [integer(2 + a + b) for a,b in zip(*summands, strict=True)]
    require(all(x > 0 and x & (x-1) == 0 for x in counts), "Not a binary space size")
    return [x.bit_length()-1 for x in counts]


def projection(order, centralizers, rows, fixed):
    sizes = [order // c for c in centralizers]
    require(sum(sizes) == order and all(order % c == 0 for c in centralizers),
            "Class sizes do not partition the group")
    projected = []
    for row in rows:
        sums = [0] * 11
        for d, size, val in zip(fixed, sizes, row, strict=True):
            sums[d] += size*val
        projected.append([integer(row[0]), *map(integer, sums)])
    return {"order": order, "rows": projected}


def check_seven_pair_seed(centralizers, rows, fixed):
    # A nonzero alternating 4-by-4 shear has rank two (35 choices) or
    # four (28 choices). Class size and natural fixed dimension identify
    # the two columns uniquely in the full ordinary table.
    columns = []
    for size, dim in ((86955, 8), (21912660, 6)):
        hits = [i for i, (c, k) in enumerate(zip(centralizers, fixed, strict=True))
                if k == dim and centralizers[0] // c == size]
        require(len(hits) == 1, "Ambiguous alternating shear class")
        columns.append(hits[0])
    a, b = columns
    ranks = [integer(Fraction(row[0]+35*row[a]+28*row[b], 64)) for row in rows]
    require(len(ranks) == 198 and min(ranks) == ranks.count(1) == 1,
            "Seven-pair subgroup fixed spaces")
    print("PASS seven-pair seed: positive fixed space in all 198 ordinary irreducibles")


def extract(path):
    require(sha256(path.read_bytes()).hexdigest() == ARCHIVE, "Wrong CTblLib release")
    source = {}
    with tarfile.open(path, "r:gz") as t:
        for name, digest in MEMBERS.items():
            with t.extractfile("ctbllib-1.3.11/data/"+name) as f:
                data = f.read()
            require(sha256(data).hexdigest() == digest, "Original table file hash")
            source[name] = data.decode("latin-1")
    c, rows = character_data(source["ctosymp1.tbl"], GROUP)
    fixed = fixed_dimensions(rows)
    check_seven_pair_seed(c, rows, fixed)
    result = {GROUP: projection(c[0], c, rows, fixed)}
    text = source["ctoorth3.tbl"]
    for name in SUBGROUPS:
        c, rows = character_data(text, name)
        tail = text.split(f'ALF("{name}","{GROUP}",', 1)[1]
        fusion = json.loads(take_list(tail)[0])
        require(len(fusion) == len(c) and all(1 <= f <= len(fixed) for f in fusion),
                "Malformed class fusion")
        result[name] = projection(c[0], c, rows, [fixed[f-1] for f in fusion])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path, help="Write the projection to this new file")
    args = parser.parse_args()
    result = extract(args.archive)
    if args.output:
        with args.output.open("x", encoding="utf-8") as output:
            output.write("{\n")
            for i, (name, group) in enumerate(result.items()):
                lines = ",\n".join("  "+json.dumps(row, separators=(",", ":"))
                                   for row in group["rows"])
                output.write(f' {json.dumps(name)}: {{"order": {group["order"]}, "rows": [\n')
                output.write(lines+"\n ]}"+("," if i+1 != len(result) else "")+"\n")
            output.write("}\n")
    else:
        saved = json.loads((ROOT/"PROJECTION.json").read_text(encoding="utf-8"))
        require(result == saved, "Projected data differ")
    print("PASS_CTBLLIB_PROJECTION groups=3 rows=517 dimensions=11")


if __name__ == "__main__":
    main()
