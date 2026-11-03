#!/usr/bin/env python3
"""Finite five-tap exclusion for one frozen R439 response dictionary.

Produced by Nick Petalas. Apache-2.0. Suffix-response reduction follows
Sricharan Vagvala PR2356, Ross Richardson PR2407 and Sagar Thakrar PR2440.
No predecessor verifier is imported.
"""
from hashlib import sha1, sha256
from itertools import combinations
import gzip
import json
from pathlib import Path
import platform

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/r439-bsection-stars-seed01/candidate.json.gz"
FILES = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(raw, pin):
    require(sha256(raw).hexdigest() == pin["sha256"], "source SHA256 mismatch")
    blob = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    require(sha1(blob).hexdigest() == pin["git_blob"], "source Git blob mismatch")


def read_source():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    live = [p for p in pins["files"] if p["usage"] == "input"]
    require(len(live) == 1 and live[0]["path"] == WORD, "exact live source inventory")
    raw = (ROOT / WORD).read_bytes()
    authenticate(raw, live[0])
    return raw, live[0]


def decompose(raw):
    word = json.loads(gzip.decompress(raw))
    n = word["v"]
    require((n, word["R"], len(word["ret"])) == (111, 439, 9), "source dimensions")
    require(type(word["D"]) is list and len(word["D"]) < 20000, "bounded D word")
    reads = [i for i, (_, d, ss) in enumerate(word["D"])
             if n <= d < 2*n and ss and all(s >= 2*n for s in ss)]
    require(bool(reads), "retained helper reads")
    undo = []
    for index, (frame, d, ss) in enumerate(word["D"]):
        if index > max(reads) and n <= d < 2*n and all(n <= s < 2*n for s in ss):
            require(frame == 0 and len(ss) == 1 and ss[0] != d, "elementary target undo")
            undo.append((d-n, ss[0]-n))
    require(len(undo) == 306, "source target undo length")
    gates = tuple(g for i, g in enumerate(undo) if i not in (31, 51, 52))
    require(len(gates) == 303, "fixed ideal303 order")
    scatter = word["scatter"]
    require(len(scatter) == n, "scatter row count")
    for row in scatter:
        require(type(row) is list and len(row) <= 9 and len(set(row)) == len(row), "scatter support")
        require(all(type(j) is int and 0 <= j < 9 for j in row), "scatter column range")
    target = sum(1 << i for i, row in enumerate(scatter) if 0 in row)
    return n, gates, target


def suffix_columns(n, gates):
    """Backward multiplication: appending E_(d,s) changes column s by column d."""
    columns = [1 << i for i in range(n)]
    result = [tuple(columns)] * (len(gates)+1)
    for cut in range(len(gates)-1, -1, -1):
        d, s = gates[cut]
        columns[s] ^= columns[d]
        result[cut] = tuple(columns)
    return tuple(result)


def literal_responses(n, gates):
    """Independent oracle: inject one basis bit and execute the remaining gates."""
    result = []
    for cut in range(len(gates)+1):
        at_cut = []
        for port in range(n):
            state = 1 << port
            for index in range(cut, len(gates)):
                d, s = gates[index]
                if (state >> s) & 1:
                    state ^= 1 << d
            at_cut.append(state)
        result.append(tuple(at_cut))
    return tuple(result)


def pair_sums(values):
    require(type(values) is tuple and 1 <= len(values) <= 412, "response count domain")
    require(all(type(x) is int and 0 < x < (1 << 111) for x in values), "response value domain")
    require(len(set(values)) == len(values), "distinct responses required")
    pairs = {0, *values}
    for x, y in combinations(values, 2):
        pairs.add(x ^ y)
    require(len(pairs) <= 85079, "bounded pair storage")
    return pairs


def admits_five(values, target):
    """Exact 2+3 meet-in-the-middle coverage, including every shorter weight."""
    require(type(target) is int and 0 <= target < (1 << 111), "target domain")
    pairs = pair_sums(values)
    counts = []
    for size in range(4):
        checked = 0
        for subset in combinations(values, size):
            residual = target
            for value in subset:
                residual ^= value
            checked += 1
            if residual in pairs:
                return True, tuple(counts + [checked]), len(pairs)
        counts.append(checked)
    return False, tuple(counts), len(pairs)


def small_oracle():
    """Full subset enumeration, independent of splitting into two and three."""
    values = (1, 2, 3, 4, 8, 17, 32, 64)
    minimum = {}
    for mask in range(1 << len(values)):
        total = 0
        for index in range(len(values)):
            if (mask >> index) & 1:
                total ^= values[index]
        minimum[total] = min(minimum.get(total, 9), mask.bit_count())
    accepted = 0
    for target in range(128):
        found, _, _ = admits_five(values, target)
        require(found == (minimum.get(target, 9) <= 5), "literal small-domain decision")
        accepted += found
    require(0 < accepted < 128, "positive and negative small controls")
    # A response repeated twice cancels, so allowing repeated taps cannot help.
    require((values[0] ^ values[0] ^ values[1]) == values[1], "duplicate cancellation")
    return {"targets": 128, "subsets": 256, "accepted": accepted}


def rejection_controls(pin, raw):
    failures = 0
    for bad in ((), (1, 1), (0,), (-1,), (True,), (1 << 111,), tuple(range(1, 414))):
        try:
            pair_sums(bad)
        except ValueError:
            failures += 1
        else:
            raise ValueError("invalid response domain accepted")
    for bad in (-1, True, 1 << 111):
        try:
            admits_five((1,), bad)
        except ValueError:
            failures += 1
        else:
            raise ValueError("invalid target accepted")
    try:
        authenticate(raw + b"x", pin)
    except ValueError:
        failures += 1
    else:
        raise ValueError("source corruption accepted")
    return failures


def main():
    raw, pin = read_source()
    n, gates, target = decompose(raw)
    primary = suffix_columns(n, gates)
    independent = literal_responses(n, gates)
    require(primary == independent, "all literal cut/port responses")
    values = tuple(sorted({value for row in primary for value in row}))
    require(len(values) == 412, "fixed complete response inventory")
    admitted, counts, pairs = admits_five(values, target)
    require(not admitted, "column zero has a representation with at most five taps")
    require(counts == (1, 412, 84666, 11571020), "complete bounded search counters")
    require(pairs == 82435, "complete pair set")
    oracle = small_oracle()
    # A real five-response target must be accepted by the same entry point.
    positive = 0
    for value in values[:5]:
        positive ^= value
    require(admits_five(values, positive)[0], "actual-dictionary positive control")
    controls = rejection_controls(pin, raw)
    digest = sha256(b"".join(x.to_bytes(14, "little") for x in values)).hexdigest()
    files = {name: sha256((HERE / name).read_bytes()).hexdigest() for name in FILES}
    receipt = {
        "status": "PASS_R439_COLUMN0_SIX_TAP_FLOOR", "claim_type": "finite exclusion",
        "python": platform.python_version(), "source_sha256": pin["sha256"],
        "undo_gates": len(gates), "cut_port_responses": n*(len(gates)+1),
        "distinct_responses": len(values), "response_sha256": digest,
        "target_column": 0, "target_hex": hex(target), "pair_set_size": pairs,
        "right_subset_counts": counts, "representations_at_most_five": 0,
        "column_tap_lower_bound": 6, "small_oracle": oracle,
        "rejection_controls": controls, "package_sha256": files,
    }
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
