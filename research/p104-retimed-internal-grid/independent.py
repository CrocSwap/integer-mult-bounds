"""Separate dense integer scalar-prefix oracle. No main/kernel imports."""

import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
FACTORS = {
    "1": (1, 1),
    "-1": (-1, 1),
    "2": (2, 1),
    "-2": (-2, 1),
    "1/2": (1, 2),
    "-1/2": (-1, 2),
    "1/4": (1, 4),
    "-1/4": (-1, 4),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rational_string(value):
    g = math.gcd(value, 4)
    numerator, denominator = value // g, 4 // g
    return str(numerator) if denominator == 1 else f"{numerator}/{denominator}"


def dense(word):
    names = list(word["initial_frames"])
    require(len(names) == 358 and len(word["program"]) == 5268, "source dimensions")
    rows = {name: [4 * int(i == j) for j in range(358)] for i, name in enumerate(names)}
    products, erases, peak = 0, 0, 4
    for index, event in enumerate(word["program"]):
        op, target = event[:2]
        if op == "add":
            numerator, denominator = FACTORS[str(event[3])]
            raw = [numerator * v for v in rows[event[2]]]
            require(
                all(v % denominator == 0 for v in raw), "quarter-product divisibility"
            )
            delta = [v // denominator for v in raw]
            products += sum(v != 0 for v in delta)
            peak = max(peak, sum(map(abs, delta)))
            rows[target] = [a + b for a, b in zip(rows[target], delta, strict=True)]
        elif op == "sign":
            require(event[2] == "-1", "scalar sign")
            rows[target] = [-v for v in rows[target]]
        elif op == "zero":
            require(target == "C" and target not in rows, "fresh private role")
            rows[target] = [0] * 358
        elif op == "erase":
            require(target == "C" and not any(rows[target]), "exact private zero")
            del rows[target]
            erases += 1
        else:
            require(op == "transport", "scalar instruction")
        if op != "erase":
            peak = max(peak, sum(map(abs, rows[target])))
        if index == 2040:
            require(
                target == "D18" and rows[target][names.index("Y2")] == -1,
                "retimed sharp-cut coefficient",
            )
    require(
        products == 30007 and erases == 8 and peak == 254, "integer scalar envelope"
    )
    endpoint = {
        r: {s: rational_string(v) for s, v in zip(names, row, strict=True) if v}
        for r, row in rows.items()
    }
    text = json.dumps(endpoint, sort_keys=True, separators=(",", ":"))
    require(
        hashlib.sha256(text.encode()).hexdigest()
        == "8e738751d18e85e1395fa0a7affa2a81d283e41a1e7bdaa8a58b05b97d111e7d",
        "complete credited endpoint",
    )
    return {"products": products, "zero_erasures": erases, "scaled_l1_peak": peak}


def main():
    data = (HERE / "inputs/PR2725-WORD.json").read_bytes()
    pins = json.loads((HERE / "SOURCES.json").read_text())["vendored_files"]
    pin = next(p for p in pins if p["local"] == "inputs/PR2725-WORD.json")
    require(hashlib.sha256(data).hexdigest() == pin["sha256"], "source digest")
    result = dense(json.loads(data))
    print("PASS_P104_RETIMED_INTEGER_ORACLE " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
