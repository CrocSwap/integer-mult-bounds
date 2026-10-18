"""Source-bound finite corroboration of the written all-height Omega proof."""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/leaf-destination-transport-bound/"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    for item in manifest["files"]:
        if item["usage"] != "input":
            continue
        data = (ROOT / item["path"]).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(hashlib.sha256(data).hexdigest() == item["sha256"], "source SHA256: " + item["path"])
        require(blob == item["git_blob"], "source Git blob: " + item["path"])


def source_functions():
    authenticate()  # No predecessor code executes before every source is checked.
    scope = {}
    for filename, names in (("check2.py", ("gen", "fl")),
                            ("omega.py", ("omega", "profile_at", "profile"))):
        path = ROOT / SOURCE / filename
        module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        nodes = [node for node in module.body
                 if isinstance(node, ast.FunctionDef) and node.name in names]
        require({node.name for node in nodes} == set(names), "source function set")
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), scope)
    return scope


def plus(*terms):
    """Each term is (integer multiplier, coefficient list)."""
    result = [0] * max(len(p) for _, p in terms)
    for scale, poly in terms:
        for i, value in enumerate(poly):
            result[i] += scale * value
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def recurrence(height):
    g, h = [0, 1], [0, 1]
    a, b = None, None
    rows = []
    for k in range(height + 1):
        if k == 1:
            a = b = [0, 1]
        elif k >= 2:
            a, b = plus((1, a), (1, old_g)), plus((1, old_g), (1, a), (2, b))
        omega = plus((1, b), (1, old_g)) if k >= 2 else None
        rows.append({"height": k, "G": g, "H": h, "A": a, "B": b, "Omega": omega})
        old_g = g
        g, h = plus((4, g), (1, [0] + h), (-1, h)), plus((2, h), (1, [0] + h))
    return rows


def coefficients(masses):
    counts = Counter(masses)
    return [counts[i] for i in range(max(counts, default=0) + 1)]


def mass(poly):
    return sum(i * count for i, count in enumerate(poly))


def prefix_row(word, count, readout):
    """Exact reverse covector, with cancellation retained inside each polynomial."""
    row = {readout: {(): 1}}
    masses = []
    for x, y, factor, sign in reversed(word[:count]):
        p = row.get(y, {})
        if p:
            masses.append(sum(abs(c) for c in p.values()))
            q = row.setdefault(x, {})
            for monomial, c in list(p.items()):
                key = monomial + (factor,)
                value = q.get(key, 0) + sign * c
                if value:
                    q[key] = value
                else:
                    q.pop(key, None)
    return {r: p for r, p in row.items() if p}, coefficients(masses)


def expected_row(height):
    n = 2 ** height
    return {0 if level == 0 else level + 1:
            {tuple(range(n - 2, n - 2 ** (height - level) - 1, -1)): 1}
            for level in range(height + 1)}


def canonical(value):
    # JSON booleans, floats and integers remain distinct in this comparison.
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def calculate():
    source = source_functions()
    table = recurrence(100)
    for entry in table:
        h = entry["height"]
        g, hp = entry["G"], entry["H"]
        require(all(type(x) is int and x >= 0 for p in (g, hp) for x in p), "nonnegative exit profiles")
        require(sum(g) == 4 ** h and sum(hp) == 3 ** h, "exit channel counts")
        require(mass(g) == 2 * 4 ** h - 3 ** h, "exit mass formula")
        if h >= 1:
            require(mass(entry["A"]) == (4 ** (h + 1) - 3 ** (h + 1) - 1) // 6, "A mass")
            require(mass(entry["B"]) == (2 * 4 ** (h + 1) - 9 * 3 ** h + 1) // 6, "B mass")
        if h >= 2:
            o = entry["Omega"]
            require(all(type(x) is int and x >= 0 for p in (entry["A"], entry["B"], o) for x in p), "nonnegative cut profiles")
            require(mass(o) == (11 * 4 ** h - 11 * 3 ** h + 1) // 6, "Omega mass")
            require(len(o) == h + 1 and o[h] == 2 and o[h - 1] == 4 * h + 1, "leading coefficients")
            if h >= 3:
                require(o[h - 2] == 4 * h * h - 2 * h + 6, "third coefficient")
    observations = []
    row_checks = 0
    for h in range(1, 9):
        n, full = 2 ** h, 4 ** h
        p, q = (full + 2) // 3, (2 * full - 2) // 3
        require(p + q == full, "complementary cuts")
        record = {"height": h, "n": n, "positive_prefix": p, "negative_prefix": q}
        for name, sign, count in (("A", 1, p), ("B", -1, q)):
            literal = source["profile_at"](n, count - 1, h + 1, sign)
            require(coefficients(literal) == table[h][name], "source " + name + str(h))
            word = [event for event, _ in source["gen"](n, sign)]
            row, profile = prefix_row(word, count, h + 1)
            require(row == expected_row(h), "exact prefix row " + name + str(h))
            require(profile == table[h][name], "separate row profile")
            row_checks += 1
            record[name] = profile
        if h >= 2:
            t, register = source["omega"](n)
            require(t + 1 == 3 * 4 ** (h - 1) + (2 * 4 ** (h - 1) - 2) // 3,
                    "source Omega cut location")
            require(register == h + 1, "source Omega register")
            o = coefficients(source["profile"](n))
            require(o == table[h]["Omega"], "source Omega" + str(h))
            record["Omega"] = o
            record["Omega_mass"] = mass(o)
        observations.append(record)

    n, h = 8, 3
    t, register = source["omega"](n)
    expected = table[h]["Omega"]
    wrong_order = [event for event, _ in source["gen"](n, 1, mode="unrev")]
    require(prefix_row(wrong_order, t + 1, register)[1] != expected, "wrong inverse order survived")
    require(coefficients(source["profile_at"](n, t - 1, register)) != expected, "wrong cut survived")
    require(coefficients(source["profile_at"](n, t, register - 1)) != expected, "wrong register survived")
    return {"schema_version": 1, "claim": "fixed Omega cut C2; no global maximum claim",
            "recurrence_heights": 101, "literal_heights": list(range(1, 9)),
            "literal_profiles": 23, "exact_prefix_rows": row_checks,
            "source": "PR2177 exact generator and reverse Omega checker",
            "controls": ["unreversed inverse", "preceding cut", "wrong register"],
            "observations": observations}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is not None:
        require(not args.output.exists(), "output already exists")
    result = calculate()
    if args.output is None:
        expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        require(canonical(expected) == canonical(result), "typed receipt mismatch")
    else:
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2, ensure_ascii=True)
            stream.write("\n")
    print("PASS_OMEGA_PROFILE: 23 literal profiles, 16 exact rows, 101 recurrence heights, 3 semantic controls")


if __name__ == "__main__":
    main()
