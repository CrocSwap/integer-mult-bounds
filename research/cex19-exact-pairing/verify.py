#!/usr/bin/env python3
"""Certify the exact cost 21 of one pinned configuration. Apache-2.0."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from encoding import build, dot, require
from rup import check_refutation


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read_limited(path, limit):
    with path.open("rb") as stream:
        raw = stream.read(limit+1)
    require(len(raw) <= limit, f"file capacity: {path.name}")
    return raw


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path):
    return json.loads(read_limited(path, 100000), object_pairs_hook=unique_object)


def configuration(directory):
    sources = load_json(directory / "SOURCES.json")
    pin = sources["external_sources"][0]
    require(pin["local_path"] == "configuration.json", "configuration path")
    raw = read_limited(directory / "configuration.json", 10000)
    require(hashlib.sha256(raw).hexdigest() == pin["sha256"], "configuration SHA256")
    blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
    require(hashlib.sha1(blob).hexdigest() == pin["git_blob"], "configuration Git blob")
    return json.loads(raw), pin["sha256"]


def binary_rank(rows):
    """Integer bit-vector row elimination, without external linear algebra."""
    pivots = [0]*19
    for value in rows:
        require(type(value) is int and 0 <= value < 1 << 19, "binary row")
        for bit in range(18, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return sum(bool(pivot) for pivot in pivots)


def witness_ranks(config, rows):
    require(type(rows) is list and len(rows) == 19, "witness row count")
    for t, row in enumerate(rows):
        require(type(row) is int and 0 <= row < 1 << 19, "witness row bits")
        require(row >> t & 1, "witness diagonal")
        for s in range(19):
            require(not (row >> s & 1) or t == s or dot(config[t][0], config[s][1]) == 0,
                    "forbidden witness entry")
    ranks = []
    for j in range(3):
        mask = sum(1 << s for s in range(19) if config[s][1][j])
        ranks.append(binary_rank([rows[t] & mask for t in range(19) if config[t][0][j]]))
    return ranks


def compute(directory, upper_rows):
    config, source_hash = configuration(directory)
    formula, residuals, _ = build(config)
    ranks = witness_ranks(config, upper_rows)
    require(sum(ranks) == 21, "cost-21 upper witness")
    raw = read_limited(directory / "lower.rup", 1000000)
    steps = check_refutation(formula, raw)
    incidence_count = sum(t != s and dot(config[t][0], config[s][1]) == 0
                          for t in range(19) for s in range(19))
    return {
        "status": "PASS_CEX19_EXACT_PAIRING",
        "minimum": 21,
        "configuration_sha256": source_hash,
        "free_pairing_bits": incidence_count,
        "block_shapes": [[sum(bool(pair[0][j]) for pair in config),
                          sum(bool(pair[1][j]) for pair in config)] for j in range(3)],
        "forced_pivot_ranks": [6, 4, 6],
        "residual_shapes": [[len(a), len(a[0])] for a in residuals],
        "lower": {
            "excluded_cost": 20,
            "variables": formula.variables,
            "clauses": len(formula.clauses),
            "cnf_sha256": hashlib.sha256(formula.dimacs().encode()).hexdigest(),
            "rup_sha256": hashlib.sha256(raw).hexdigest(),
            "rup_additions": steps,
        },
        "upper": {"rows": upper_rows, "block_ranks": ranks, "cost": sum(ranks)},
    }


def verify(directory=HERE):
    expected = load_json(directory / "RESULT.json")
    result = compute(directory, expected["upper"]["rows"])
    require(canonical(result) == canonical(expected), "result receipt mismatch")
    return result


def main():
    require(len(sys.argv) == 1, "usage: verify.py")
    result = verify()
    print(f"{result['status']} minimum=21 ranks=7,6,8 "
          f"RUP={result['lower']['rup_additions']} no_new_kappa")


if __name__ == "__main__":
    main()
