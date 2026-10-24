"""Exact corroboration of the localized public-header argument; stdlib only."""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bytes(path):
    with path.open("rb") as stream:
        data = stream.read(262145)
    require(len(data) <= 262144, "input exceeds 256 KiB bound")
    return data


def source_hashes():
    manifest = json.loads(read_bytes(PACKAGE / "SOURCES.json"))
    require(len(manifest["files"]) == 4, "four source entries")
    hashes = {}
    for entry in manifest["files"]:
        if entry["usage"] == "input":
            path = entry["path"]
            digest = sha256(read_bytes(ROOT / path)).hexdigest()
            require(digest == entry["sha256"], "source hash: " + path)
            hashes[path] = digest
    for name in ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py"):
        hashes["package/" + name] = sha256(read_bytes(PACKAGE / name)).hexdigest()
    return hashes


def tax_table(certificate):
    """Transform cited flat data, without replaying or certifying its geometry."""
    table = []
    for rank_text, entries in certificate["flat_census"].items():
        rank = int(rank_text)
        if rank == 0:
            continue
        for entry in entries:
            leakage = Fraction(entry["cliques_hit"], 192)
            gap = rank - leakage
            require(gap >= Fraction(1, 3), "nonempty-source surcharge")
            table.append({"rank": rank, "lines": entry["lines"],
                          "leakage_coefficient": str(leakage),
                          "surcharge_coefficient": str(gap)})
    require(len(table) == 8, "eight cited nonempty flat types")
    require(min(Fraction(row["surcharge_coefficient"]) for row in table)
            == Fraction(1, 3), "attained geometric coefficient")
    return table


def influence_edges(table, variables):
    return tuple(sum(((table >> word) ^ (table >> (word | (1 << bit)))) & 1
                     for word in range(1 << variables) if not (word >> bit) & 1)
                 for bit in range(variables))


def boolean_headers():
    """Check entropy exactly by exponentiating, never by floating point."""
    census = Counter()
    equality = []
    for table in range(1 << 16):
        ones = table.bit_count()
        edges = influence_edges(table, 4)
        support = sum(value != 0 for value in edges)
        # 16 H(M) = 64 - log2(k^k (16-k)^(16-k)).
        entropy_denominator = ones ** ones * (16 - ones) ** (16 - ones)
        exponent = 64 * support - 2 * sum(edges)
        left = 1 << exponent
        right = entropy_denominator ** support
        require(left >= right, "source-sensitive entropy inequality")
        if left == right:
            equality.append(table)
        census[support] += 1
    affine = set()
    for mask in range(16):
        for offset in range(2):
            affine.add(sum((((word & mask).bit_count() + offset) % 2) << word
                           for word in range(16)))
    require(set(equality) == affine, "equality is exactly affine headers")
    return {"headers": 65536, "support_census": {str(key): value for key, value in sorted(census.items())},
            "equality_headers": len(equality), "nonlinear_headers": 65504}


def check_prefix(words):
    require(len(set(words)) == len(words), "duplicate codeword")
    require(all(not right.startswith(left) for left in words for right in words
                if left != right), "non-prefix code")


def header(word, mode):
    bits = tuple((word >> bit) & 1 for bit in range(6))
    if mode == "parity":
        return str(sum(bits) % 2)
    if mode == "nonlinear":
        return str(bits[0] ^ (bits[1] & bits[2]))
    if bits[0]:
        return "11"
    return "10" if bits[1] else "0"


def protocol(mode, omit=False):
    """Literal public observations; six sources occupy one cited rank-2 flat."""
    words = ("0", "10", "11") if mode == "variable" else ("0", "1")
    check_prefix(words)
    observations = tuple({} for _ in range(6))
    costs = []
    for word in range(64):
        code = header(word, mode)
        indices = tuple(range(1, 6))
        if mode == "variable" and code != "11":
            indices = tuple(range(2, 6))
        if code.endswith("1"):
            indices = tuple(reversed(indices))
        if omit:
            indices = tuple(bit for bit in indices if bit != 5)
        payload = tuple((word >> bit) & 1 for bit in indices)
        observation = (code, payload)
        for bit in range(6):
            value = (word >> bit) & 1
            previous = observations[bit].setdefault(observation, value)
            require(previous == value, "receiver conflict")
        costs.append(2 * len(code) + len(payload))
    expected = Fraction(sum(costs), 64)
    length = Fraction(sum(len(header(word, mode)) for word in range(64)), 64)
    entropy = Fraction(3, 2) if mode == "variable" else Fraction(1)
    lower = 4 + 2 * length - Fraction(5, 3) * entropy
    require(expected >= lower >= 4 + length / 3, "cost inequality")
    return {"mode": mode, "inputs": 64, "receiver_observations": 384,
            "expected_charge": str(expected), "expected_header_length": str(length),
            "header_entropy": str(entropy), "certified_lower_bound": str(lower)}


def parity_cuts():
    checked = 0
    for inside in range(1, 64):
        fibers = {}
        for word in range(64):
            outside = word & (63 ^ inside)
            counts = fibers.setdefault(outside, [0, 0])
            counts[word.bit_count() % 2] += 1
            checked += 1
        require(all(zero == one for zero, one in fibers.values()),
                "parity is conditionally uniform at each nonempty cut")
    return {"nonempty_cuts": 63, "input_cut_pairs": checked,
            "conditional_entropy_each_nonempty_cut": "1"}


def rejected(function, *arguments):
    try:
        function(*arguments)
    except ValueError:
        return 1
    raise ValueError("negative control was accepted")


def check_header_support(mode, source_mask):
    for word in range(64):
        for bit in range(6):
            if not (source_mask >> bit) & 1:
                require(header(word, mode) == header(word ^ (1 << bit), mode),
                        "undeclared header source")


def controls(certificate):
    corrupted = json.loads(json.dumps(certificate))
    corrupted["flat_census"]["1"][0]["cliques_hit"] = 200
    count = rejected(tax_table, corrupted)
    count += rejected(check_prefix, ("0", "01"))
    count += rejected(check_prefix, ("", "1"))
    count += rejected(check_prefix, ("0", "0"))
    for mode in ("parity", "nonlinear", "variable"):
        count += rejected(protocol, mode, True)
    count += rejected(check_header_support, "nonlinear", 3)
    return count


def calculate():
    hashes = source_hashes()
    certificate = json.loads(read_bytes(
        ROOT / "research/gaussian-clique-copy-bound/certificate.json"))
    return {"schema": "localized-gaussian-header/v1", "claim_type": "scoped proof",
            "geometry_status": "cited premise; not replayed",
            "source_hashes": hashes, "flat_tax_table": tax_table(certificate),
            "boolean_headers": boolean_headers(), "parity_witness": parity_cuts(),
            "protocols": [protocol(mode) for mode in ("parity", "nonlinear", "variable")],
            "rejecting_controls": controls(certificate)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a generated receipt exclusively")
    arguments = parser.parse_args()
    result = calculate()
    if arguments.output:
        with arguments.output.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        committed = json.loads(read_bytes(PACKAGE / "RESULT.json"))
        require(committed == result, "generated receipt mismatch")
    print("PASS_GAUSSIAN_LOCALIZED_HEADER_TAX surcharge=1/3 "
          "boolean_headers=65536 protocols=3 controls=8 no_new_kappa")


if __name__ == "__main__":
    main()
