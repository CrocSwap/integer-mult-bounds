#!/usr/bin/env python3
"""Verify the width-nine quotient calculation, optionally from its source archive."""

import argparse
from hashlib import sha256
from io import BytesIO
import json
from math import prod
from pathlib import Path
import re
import tarfile

ORDER = 47_377_612_800
N_CLASSES = 81
ARCHIVE_SHA256 = "f201e9da571c681a7bbfb1e4683bdb2c80a23b005099ed0453521f59cb443434"
TABLE_SHA256 = "461519e33cb31b2bc46f554b09f283f0afb7125fd805840d79bfc614fce75b6f"
TABLE_MEMBER = "ctbllib-1.3.11/data/ctosymp1.tbl"
MISSING_ROWS = [2, 4, 7, 14, 15, 17, 20, 23, 27, 32, 38, 40, 51, 52, 58, 59, 66, 68, 72, 73]


def require(test, message):
    if not test:
        raise ValueError(message)


def read_bounded(path, limit):
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, f"{path.name} exceeds its byte bound")
    return data


def read_table(archive):
    raw = read_bounded(archive, 20 * 1024 * 1024)
    require(sha256(raw).hexdigest() == ARCHIVE_SHA256, "CTblLib archive hash")
    with tarfile.open(fileobj=BytesIO(raw), mode="r:gz") as tar:
        member = tar.getmember(TABLE_MEMBER)
        require(member.isfile() and 0 < member.size < 256 * 1024, "table member size")
        stream = tar.extractfile(member)
        require(stream is not None, "missing table payload")
        with stream:
            data = stream.read(member.size + 1)
    require(sha256(data).hexdigest() == TABLE_SHA256, "CTblLib table hash")
    return data.decode("ascii")


def table_projection(table):
    block = table.split('MOT("S8(2)",\n', 1)[1].split('\nARC("S8(2)"', 1)[0]
    numbers = block.split("],\n", 1)[1]
    centralizers = json.loads(numbers.split("],\n", 1)[0] + "]")
    # This sequence follows the power-map argument in the MOT record.
    entries = block.split("\n[[1,1,1,", 1)[1].split("]],\n", 1)[0]
    entries = re.sub(r"\s+", "", "1,1,1," + entries)
    require(entries.count("[GALOIS,[72,3]]") == 1, "Galois row")
    entries = entries.replace("[GALOIS,[72,3]]", "GALOIS")
    rows = [row.split(",") for row in re.split(r"\],\[|\],(?=GALOIS)|(?<=GALOIS),\[", entries)]
    require(len(centralizers) == len(rows) == N_CLASSES, "table dimensions")
    require(rows[72] == ["GALOIS"], "Galois row index")
    # Galois rows agree on rational values. The only irrational entries
    # occur on dimension-zero columns, which carry zero weight.
    rows[72] = rows[71]
    require(all(len(row) == N_CLASSES for row in rows), "table row lengths")
    fixed = [2 + int(a) + int(b) for a, b in zip(rows[4], rows[5], strict=True)]
    require([int(rows[i][0]) for i in (4, 5)] == [119, 135], "point character rows")
    require(all(1 <= n <= 256 and n.bit_count() == 1 for n in fixed), "fixed-point powers")
    dims = [n.bit_length() - 1 for n in fixed]
    require(all(c > 0 and ORDER % c == 0 for c in centralizers), "centralizers")
    sizes = [ORDER // c for c in centralizers]
    columns = [tuple(j for j, dim in enumerate(dims) if dim == d) for d in range(9)]
    require(columns[8] == (0,) and sizes[0] == 1, "identity class")
    return {
        "class_counts": [len(column) for column in columns],
        "element_counts": [sum(sizes[j] for j in column) for column in columns],
        "rows": [
            [int(row[0]), *(sum(sizes[j] * int(row[j]) for j in column)
                            for column in columns[1:8])]
            for row in rows
        ],
    }


def gaussian_binomial(n, r):
    """Number of r-subspaces of a binary n-space for 0 <= r <= n <= 8."""
    top = prod(2**n - 2**i for i in range(r))
    bottom = prod(2**r - 2**i for i in range(r))
    return top // bottom


def tuple_orbits(length):
    """Count ordered-tuple orbits by the kernel and induced alternating form."""
    result = 0
    for rank in range(length + 1):
        for radical in range(rank % 2, rank + 1, 2):
            if rank + radical > 8:
                continue
            even = rank - radical
            gl_order = prod(2**even - 2**i for i in range(even))
            half = even // 2
            sp_order = 2**(half**2) * prod(2**(2*i) - 1 for i in range(1, half + 1))
            result += (gaussian_binomial(length, rank)
                       * gaussian_binomial(rank, radical) * (gl_order // sp_order))
    return result


def check_projection(data):
    class_counts = data["class_counts"]
    elements = data["element_counts"]
    rows = data["rows"]
    require(len(class_counts) == len(elements) == 9 and len(rows) == N_CLASSES, "projection shape")
    require(all(type(c) is int and 1 <= c <= N_CLASSES for c in class_counts), "class counts")
    require(all(type(e) is int and 1 <= e <= ORDER for e in elements), "element counts")
    require(sum(class_counts) == N_CLASSES and sum(elements) == ORDER, "class coverage")
    require(class_counts[8] == elements[8] == 1, "single identity")
    require(all(len(row) == 8 for row in rows), "projected row lengths")
    for degree, *sums in rows:
        require(type(degree) is int and 1 <= degree <= 68_850, "character degree")
        require(all(type(s) is int and abs(s) <= degree * e
                    for s, e in zip(sums, elements[1:8], strict=True)), "character sum bounds")

    for length in range(9):
        mass = sum(count * 2**(d * length) for d, count in enumerate(elements))
        require(mass == ORDER * tuple_orbits(length), "independent tuple orbit count")

    degrees = [row[0] for row in rows]
    require(degrees[0] == 1 and sum(d * d for d in degrees) == ORDER, "degree square sum")
    multiplicities = []
    for i, (degree, *sums) in enumerate(rows):
        moment = degree * (2**32 - 1)
        moment += sum(value * (2**(4*d) - 1) for d, value in enumerate(sums, 1))
        quotient, remainder = divmod(moment, ORDER)
        require(remainder == 0 and quotient >= 0, "nonintegral or negative multiplicity")
        multiplicities.append(quotient + (i == 0))
    require(sum(m * d for m, d in zip(multiplicities, degrees, strict=True)) == 2**32,
            "multiplicity dimension sum")
    require(sum(m * m for m in multiplicities) == tuple_orbits(8), "character norm")
    return degrees, multiplicities


def require_rejected(data, reason):
    try:
        check_projection(data)
    except ValueError as error:
        require(str(error) == reason, f"unexpected control failure: {error}")
        return
    raise ValueError(f"control accepted: {reason}")


def check_controls(data):
    rows = [row.copy() for row in data["rows"]]
    rows[1][1] += 1
    require_rejected({**data, "rows": rows}, "nonintegral or negative multiplicity")
    elements = data["element_counts"].copy()
    elements[0] -= 1
    elements[1] += 1
    require_rejected({**data, "element_counts": elements}, "independent tuple orbit count")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ctbllib-archive", type=Path, help="optional CTblLib 1.3.11 release archive")
    args = parser.parse_args()
    data = json.loads(read_bounded(Path(__file__).with_name("PROJECTION.json"), 64 * 1024))
    if args.ctbllib_archive is not None:
        require(table_projection(read_table(args.ctbllib_archive)) == data, "source projection differs")
        print("PASS_CTBL_SOURCE_PROJECTION classes=81 rows=81")
    degrees, multiplicities = check_projection(data)
    check_controls(data)
    missing = [i for i, m in enumerate(multiplicities, 1) if m == 0]
    require(missing == MISSING_ROWS, "missing character row indices")
    nullity = 256 * sum(degrees[i - 1]**2 for i in missing)
    rank = 256 * ORDER - nullity
    require((rank, nullity) == (10_107_260_791_808, 2_021_408_084_992), "Gram dimension result")
    print(f"PASS_CLIFFORD_FOUR_QUBIT_WIDTH_NINE classes={N_CLASSES} "
          f"present={N_CLASSES - len(missing)} missing={len(missing)} rank={rank} nullity={nullity} "
          "tuple_moments=9 controls=2")


if __name__ == "__main__":
    main()
