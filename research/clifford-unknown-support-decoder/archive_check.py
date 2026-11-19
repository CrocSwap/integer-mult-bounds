"""Compare the two retained table projections to the original CTblLib release."""

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
import tarfile


def check(condition, message):
    if not condition:
        raise ValueError(message)


def items(source):
    tokens = []
    depth, begin, quoted = 0, 0, False
    for i, c in enumerate(source):
        if c == '"':
            quoted = not quoted
        if quoted:
            continue
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif c == "," and depth == 0:
            tokens.append(source[begin:i].strip())
            begin = i+1
    check(depth == 0 and not quoted, "invalid table syntax")
    return tokens + [source[begin:].strip()]


def unpack(s):
    check(s.startswith("[") and s.endswith("]"), "expected a table list")
    return items(s[1:-1])


def verify(path):
    raw = path.read_bytes()
    check(sha256(raw).hexdigest() == "f201e9da571c681a7bbfb1e4683bdb2c80a23b005099ed0453521f59cb443434",
          "CTblLib archive digest")
    with tarfile.open(fileobj=BytesIO(raw)) as archive:
        table = archive.extractfile("ctbllib-1.3.11/data/ctosymp1.tbl").read()
    check(sha256(table).hexdigest() == "461519e33cb31b2bc46f554b09f283f0afb7125fd805840d79bfc614fce75b6f",
          "ordinary table member digest")
    begin = table.index(b'MOT("S8(2)",') + len(b'MOT(')
    end = table.index(b');', begin)
    name, credit, central, _, characters, _ = items(table[begin:end].decode("ascii"))
    check(name == '"S8(2)"' and "ATLAS" in credit, "table name or credit")
    centralizers = [int(c) for c in unpack(central)]
    rows = [unpack(r) for r in unpack(characters)]
    check(rows[72] == ["GALOIS", "[72,3]"], "Galois row description")
    # Only rational entries of this conjugate row enter the projection.
    rows[72] = rows[71]
    order = 47377612800
    check(all(order % c == 0 for c in centralizers), "class centralizers")
    sizes = [order//c for c in centralizers]
    fixed = [2+int(a)+int(b) for a, b in zip(rows[4], rows[5], strict=True)]
    dims = [v.bit_length()-1 for v in fixed]
    check(all(v == 2**d for v, d in zip(fixed, dims, strict=True)), "fixed point counts")
    tables = Path(__file__).resolve().parent / "tables"
    p = json.loads((tables/"PROJECTION.json").read_bytes())
    check(p["class_counts"] == [dims.count(d) for d in range(9)], "class counts")
    check(p["element_counts"] == [sum(v for v, j in zip(sizes, dims) if j == d) for d in range(9)],
          "element counts")
    for row, expected in zip(rows, p["rows"], strict=True):
        sums = [sum(int(v)*size for v,j,size in zip(row,dims,sizes,strict=True) if j == d)
                for d in range(1,8)]
        check(expected == [int(row[0]), *sums], "row projection")
    data = json.loads((tables/"CHARACTER-COLUMNS.json").read_bytes())
    for j, col in enumerate(data["columns"]):
        check(col["centralizer"] == centralizers[j] and col["index"] == j+1, "class indexing")
        check(col["values"] == [int(rows[i-1][j]) for i in data["one_based_rows"]], "character values")
    print("PASS_ARCHIVE_PROJECTION 81 projected rows and 324 character values")


if __name__ == "__main__":
    verify(Path(sys.argv[1]))
