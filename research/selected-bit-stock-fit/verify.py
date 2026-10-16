#!/usr/bin/env python3
"""Exact certificate for one conditional selected-BIT reserve, not its compiler."""

import argparse
import hashlib
import json
import math
import tarfile
from fractions import Fraction as Q
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
TAIL = 1 << 20
INPUTS = (
    "certificates/selected-result.json",
    "research/community-frontier1094-audit/ASSEMBLY.json",
    "research/e8-bit-p111-tuned/tune/EXPECTED.json",
    "research/five-stage-source527-banks/proof/three-stage-cover-bit.tex",
    "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bounded(path, maximum):
    with path.open("rb") as stream:
        data = stream.read(maximum + 1)
    require(len(data) <= maximum, "input capacity exceeded: " + str(path))
    return data


def canonical(value):
    # JSON encoding distinguishes true from 1, unlike Python container equality.
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def load_sources(root=ROOT, package=PACKAGE):
    manifest = json.loads(read_bounded(package / "SOURCES.json", 32768))
    require(len(manifest["files"]) <= 8, "source inventory capacity exceeded")
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    require(len(rows) == len(INPUTS), "live input inventory changed")
    require({row["path"] for row in rows} == set(INPUTS), "live input paths changed")
    data = {}
    for row in rows:
        name = row["path"]
        raw = read_bounded(root / name, 8 << 20)
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256: " + name)
        blob = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source blob: " + name)
        data[name] = raw
    return data, manifest["archive_member"]


def assembler_bytes(root, pin):
    archive = root / INPUTS[-1]
    require(pin["path"] == "code/assemble.py", "archive member path changed")
    found = []
    with tarfile.open(archive, "r:gz") as source:
        for index, member in enumerate(source):
            require(index < 1024, "archive member count exceeded")
            if member.name == pin["path"]:
                require(member.isfile() and member.size <= 65536, "invalid archive member")
                stream = source.extractfile(member)
                require(stream is not None, "missing archive member stream")
                with stream:
                    found.append(stream.read(65537))
    require(len(found) == 1, "archive member is missing or duplicated")
    require(hashlib.sha256(found[0]).hexdigest() == pin["sha256"], "archive member SHA256")
    return found[0].decode("utf-8")


def selected_parameters(data, assembler):
    selected, assembly, expected = [json.loads(data[name]) for name in INPUTS[:3]]
    require(selected["certificate"] == INPUTS[1], "selected certificate path")
    require(hashlib.sha256(data[INPUTS[1]]).hexdigest() == selected["certificate_sha256"],
            "selected certificate binding")
    supplier = assembly["bit_supplier"]
    require(supplier["path"] == INPUTS[2], "selected BIT supplier path")
    raw = data[INPUTS[2]]
    blob = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    require(hashlib.sha1(blob).hexdigest() == supplier["git_blob_sha1"], "BIT citation")
    require("BIT_L,BIT_T=9,32;BIT_K=(BIT_L-1)//2;BIT_M=1+7*BIT_L" in assembler,
            "selected dimension formula")
    require("s=min(c,(1-beta)*bb)-Q(1,10**27)" in assembler, "atom exponent formula")
    require("eta=beta=Q(1,10**24)" in assembler, "atom beta formula")
    nine = expected["nine"]
    require(nine["bit"]["physical"] == 28425, "complete physical packet")
    require(max(map(int, nine["profile"])) == nine["bit"]["maxchild"] == 42,
            "largest selected child")
    require("M=64" in supplier["deficit_formula"], "ordinary BIT dimension")
    exponents = {}
    for branch, key in (("native", "complex_lower"), ("conservative", "conservative_complex_lower")):
        s = min(Q(assembly["bit_lower"]), (1 - Q(1, 10**24)) * Q(assembly[key])) - Q(1, 10**27)
        require(0 < s <= Q(1, 500), "selected atom exponent outside proved domain")
        exponents[branch] = str(s)
    return exponents


def depth(n):
    require(type(n) is int and 0 <= n < 1 << 1024, "depth domain")
    for count in range(2049):
        if n < 64:
            return count
        n = 42 * (n // 64)
    raise ValueError("depth iteration capacity exceeded")


def thresholds():
    values = [64]
    for _ in range(40):
        if values[-1] >= TAIL:
            return values
        values.append(64 * ((values[-1] + 41) // 42))
    raise ValueError("threshold capacity exceeded")


def staircase(cutoff):
    require(type(cutoff) is int and 64 <= cutoff < TAIL, "cutoff domain")
    require(28425 < 1 << 15, "packet logarithm bound")
    values = thresholds()
    rows = []
    for d in range(1, len(values)):
        first = max(cutoff, values[d - 1])
        last = min(TAIL - 1, values[d] - 1)
        if first <= last:
            k_bound = 8192 * d + (3 * d + 15) // 16
            require(first > 2 * k_bound, "strict fit fails in staircase")
            rows.append({"depth": d, "first": first, "last": last, "k_upper": k_bound})
    require(rows and rows[-1]["last"] == TAIL - 1, "incomplete staircase")
    return {"thresholds": values, "intervals": rows}


def tail_certificate():
    require(2 * 42**2 < 64**2, "two levels do not halve")
    require(Q(21, 500) <= Q(1, 20), "tail atom exponent")
    require(9**20 > 2 * 8**20, "tail power comparison")
    base = Q(2 * 8193 * 21 * 9, 8) + 1
    ratio = Q(22 * 9, 21 * 8)
    require(base < 1 << 19, "dyadic tail base does not fit")
    require(ratio < 2, "dyadic tail induction does not contract")
    return {"from_width": TAIL, "base_upper": str(base), "growth_upper": str(ratio)}


def proth_prime(k=15, exponent=78, witness=11):
    require(type(k) is type(exponent) is type(witness) is int, "prime certificate types")
    require(1 <= k <= 1999 and k % 2 == 1 and 1 <= exponent <= 512,
            "prime certificate domain")
    require(2 <= witness <= 32, "prime witness domain")
    q = k * (1 << exponent) + 1
    require((1 << exponent) ** 2 > q, "insufficient known prime-power factor")
    require(pow(witness, q - 1, q) == 1, "prime Fermat condition")
    require(math.gcd(pow(witness, (q - 1) // 2, q) - 1, q) == 1,
            "prime order condition")
    return q


def sharpness():
    q = proth_prime()
    require(q > 1 << 80 and q > 2 * 64 * 19, "sharpness prime domain")
    # Bernoulli: product_(i=1)^64 (1-q^-i)^19 > 1-1216/q > 1/2.
    require(28425**19 > 2 * q**3, "sharpness lower stock bound")
    require(28425**19 < q**4, "sharpness upper stock bound")
    k = 8192 * 19 + 4
    width = 2 * k
    require(depth(width) == 19, "sharpness depth")
    require(1 < width < TAIL, "sharpness atom width is not two")
    return {"q": str(q), "k": k, "failing_width": width,
            "prime_certificate": {"odd_multiplier": 15, "power_of_two": 78, "witness": 11}}


def certificate(root=ROOT, package=PACKAGE):
    data, pin = load_sources(root, package)
    exponents = selected_parameters(data, assembler_bytes(root, pin))
    failure = sharpness()
    cutoff = failure["failing_width"] + 1
    return {"status": "PASS_SELECTED_BIT_STOCK_FIT", "uniform_cutoff": cutoff,
            "stock_domain": "PR2084/2120 original-width reserve; conditional interfaces",
            "selected_atom_exponents": exponents, "staircase": staircase(cutoff),
            "tail": tail_certificate(), "sharpness": failure}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path, help="create an external result; never overwrite")
    args = parser.parse_args()
    result = certificate()
    if args.write_result is not None:
        with args.write_result.open("x", encoding="utf-8") as output:
            output.write(json.dumps(result, indent=2) + "\n")
    else:
        stored = json.loads(read_bounded(PACKAGE / "RESULT.json", 32768))
        require(canonical(stored) == canonical(result), "required result differs from certificate")
    print(f"PASS_SELECTED_BIT_STOCK_FIT uniform_cutoff={result['uniform_cutoff']} "
          f"failure={result['sharpness']['failing_width']} no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, tarfile.TarError) as error:
        raise SystemExit("FAIL_SELECTED_BIT_STOCK_FIT: " + str(error)) from error
