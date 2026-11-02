#!/usr/bin/env python3
"""Exact finite certificate for an unbiased reversible rotation. Apache-2.0."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from construct import construct


def require(condition, message):
    if not condition:
        raise ValueError(message)


def class_key(point, scale=1):
    x, y = point
    return ((3 * x + 4 * y) % (25 * scale),
            (3 * y - 4 * x) % (25 * scale))


def read_tables():
    path = HERE / "TABLE.json"
    require(not path.is_symlink() and path.stat().st_size <= 65536,
            "table input is linked or oversized")
    document = json.loads(path.read_text(encoding="utf-8"))
    require(set(document) == {"schema_version", "tables"}, "table keys")
    require(type(document["schema_version"]) is int and
            document["schema_version"] == 1, "table schema")
    tables = document["tables"]
    require(type(tables) is list and len(tables) == 5, "seed count")
    for table in tables:
        require(type(table) is list and len(table) == 25, "table size")
        for point in table:
            require(type(point) is list and len(point) == 2, "point shape")
            require(all(type(v) is int and -16 <= v <= 16 for v in point),
                    "point coordinate")
    require(document == construct(), "table differs from exact constructor")
    return tables


def quotient_check(tables):
    keys = {class_key((x, y)) for x in range(25) for y in range(25)}
    require(len(keys) == 25, "incorrect quotient order")
    for table in tables:
        require({class_key(point) for point in table} == keys,
                "outputs are not a quotient transversal")


def moment_check(tables):
    nonintegral = 0
    worst = 0
    for i in range(25):
        x, y = divmod(i, 5)
        a, b = 3 * x - 4 * y, 4 * x + 3 * y
        require(sum(table[i][0] for table in tables) == a, "first moment x")
        require(sum(table[i][1] for table in tables) == b, "first moment y")
        total = 0
        for table in tables:
            u, v = table[i]
            require(a // 5 <= u <= -((-a) // 5), "x outside nearest cell")
            require(b // 5 <= v <= -((-b) // 5), "y outside nearest cell")
            residual = (5 * u - a) ** 2 + (5 * v - b) ** 2
            total += residual
            worst = max(worst, residual)
        fractional = bool(a % 5 or b % 5)
        nonintegral += fractional
        require(total == (50 if fractional else 0), "squared error moment")
    require(nonintegral == 20 and worst == 20, "error census")
    return nonintegral, worst


def forward(point, table):
    x, y = point
    q, r = divmod(x, 5)
    s, t = divmod(y, 5)
    u, v = table[5 * r + t]
    return (3 * q - 4 * s + u, 4 * q + 3 * s + v)


def inverse(point, table, lookup):
    i = lookup[class_key(point)]
    x, y = divmod(i, 5)
    u, v = table[i]
    a, b = point[0] - u, point[1] - v
    q, r = divmod(3 * a + 4 * b, 25)
    s, t = divmod(3 * b - 4 * a, 25)
    require(r == 0 and t == 0, "inverse lattice membership")
    return (5 * q + x, 5 * s + y)


def literal_checks(tables):
    roundtrips = 0
    for table in tables:
        lookup = {class_key(point): i for i, point in enumerate(table)}
        for x in range(-20, 21):
            for y in range(-20, 21):
                point = (x, y)
                require(inverse(forward(point, table), table, lookup) == point,
                        "left inverse")
                require(forward(inverse(point, table, lookup), table) == point,
                        "right inverse")
                roundtrips += 2
    return roundtrips


def quotient_oracle(tables):
    """Independent direct formula on four larger lattice quotients."""
    cases = 0
    for scale in range(1, 5):
        for table in tables:
            images = set()
            for x in range(5 * scale):
                for y in range(5 * scale):
                    q, s = x // 5, y // 5
                    u, v = table[(x % 5) * 5 + y % 5]
                    point = (3 * q - 4 * s + u, 4 * q + 3 * s + v)
                    images.add(class_key(point, scale))
                    cases += 1
            require(len(images) == 25 * scale * scale, "larger quotient alias")
    return cases


def large_checks(tables):
    cases = 0
    for bits in (1, 17, 64, 256, 1024):
        for sign in (-1, 1):
            shift = (sign * (1 << bits), -sign * ((1 << bits) + 3))
            for table in tables:
                lookup = {class_key(point): i for i, point in enumerate(table)}
                for i in range(25):
                    r, t = divmod(i, 5)
                    point = (5 * shift[0] + r, 5 * shift[1] + t)
                    result = forward(point, table)
                    u, v = table[i]
                    require(result == (3 * shift[0] - 4 * shift[1] + u,
                                       4 * shift[0] + 3 * shift[1] + v),
                            "signed covariance")
                    require(inverse(result, table, lookup) == point,
                            "large inverse")
                    cases += 1
    return cases


def rejection_controls(tables):
    controls = 0
    broken = [[list(point) for point in table] for table in tables]
    broken[0][1] = list(broken[0][0])
    try:
        quotient_check(broken)
    except ValueError:
        controls += 1
    else:
        raise ValueError("duplicate-output mutant accepted")
    broken = [[list(point) for point in table] for table in tables]
    broken[0][0][0] += 3
    broken[0][0][1] += 4
    quotient_check(broken)  # Same coset, so bijection alone cannot check the mean.
    try:
        moment_check(broken)
    except ValueError:
        controls += 1
    else:
        raise ValueError("biased-transversal mutant accepted")
    require(any(inverse(forward((x, y), tables[0]), tables[1],
                        {class_key(p): i for i, p in enumerate(tables[1])}) != (x, y)
                for x in range(5) for y in range(5)), "forgotten seed control")
    controls += 1
    require(5 * tables[0][5][0] != 3 or 5 * tables[0][5][1] != 4,
            "fixed seed incorrectly claimed unbiased")
    return controls + 1


def independent_rounding_control():
    """Independent coordinate rounding has the right mean but wrong capacity."""
    columns = {}
    for x in range(5):
        for y in range(5):
            u, a = divmod(3 * x - 4 * y, 5)
            v, b = divmod(4 * x + 3 * y, 5)
            for dx in range(2):
                for dy in range(2):
                    weight = (a if dx else 5 - a) * (b if dy else 5 - b)
                    key = class_key((u + dx, v + dy))
                    columns[key] = columns.get(key, 0) + weight
    require(sum(columns.values()) == 625, "independent rounding row mass")
    require(any(value != 25 for value in columns.values()),
            "independent rounding unexpectedly preserves output capacity")
    return 1


def receipt():
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "construct.py", "verify.py", "TABLE.json")
    hashes = {}
    for name in names:
        path = HERE / name
        require(not path.is_symlink() and path.stat().st_size <= 1048576,
                "linked or oversized package file")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    require(len(sys.argv) == 1, "no command arguments are supported")
    tables = read_tables()
    quotient_check(tables)
    nonintegral, worst = moment_check(tables)
    result = {"seed_count": 5, "residue_classes": 25,
              "nonintegral_classes": nonintegral,
              "nonintegral_minimum_squared_error": "2/5",
              "maximum_squared_error": f"{worst}/25",
              "two_sided_roundtrips": literal_checks(tables),
              "larger_quotient_images": quotient_oracle(tables),
              "large_signed_cases": large_checks(tables),
              "controls": rejection_controls(tables) + independent_rounding_control(),
              "sha256": receipt()}
    print(json.dumps(result, sort_keys=True))
    print("PASS_UNBIASED_PERIODIC_ROTATION")


if __name__ == "__main__":
    main()
