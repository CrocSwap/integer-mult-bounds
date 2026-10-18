#!/usr/bin/env python3
"""Exact conditional depth/stock refinement for the selected BIT producer.

Nick Petalas. Apache-2.0. No predecessor verifier is imported or executed.
"""
from __future__ import annotations

import ast
from bisect import bisect_right
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SELECTED = "certificates/selected-result.json"
ASSEMBLY = "research/community-frontier1094-audit/ASSEMBLY.json"
BIT = "research/e8-bit-p111-tuned/tune/EXPECTED.json"
ARCHIVE = "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_ATOM_BITS = 4097
MAX_DEPTH = 2 * MAX_ATOM_BITS
FINITE_WIDTH = 100000


class Rejected(ValueError):
    """A source, model premise or required receipt did not match."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Rejected(message)


def authenticate(data: bytes, pin: dict) -> bytes:
    require(len(data) <= MAX_SOURCE_BYTES, "source capacity")
    digest = hashlib.sha256(data).hexdigest()
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    require(digest == pin["sha256"], "source SHA256: " + pin["path"])
    require(hashlib.sha1(header + data).hexdigest() == pin["git_blob"],
            "source Git blob: " + pin["path"])
    return data


def read_inputs() -> dict[str, bytes]:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_bytes())
    require(len(manifest["files"]) <= 16, "source count capacity")
    result = {}
    for pin in manifest["files"]:
        if pin["usage"] == "input":
            path = ROOT / pin["path"]
            require(path.stat().st_size <= MAX_SOURCE_BYTES, "source file capacity")
            result[pin["path"]] = authenticate(path.read_bytes(), pin)
    return result


def assembler(data: bytes) -> ast.Module:
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for _ in range(1024):
            member = archive.next()
            if member is None:
                break
            if member.name == "code/assemble.py":
                require(member.isfile() and member.size <= 65536, "assembler member capacity")
                stream = archive.extractfile(member)
                require(stream is not None, "assembler member missing")
                with stream:
                    payload = stream.read(65537)
                require(hashlib.sha256(payload).hexdigest() ==
                        "15f6986a476bac76bcdc0bfcf51da115389b46f1950d2766b6822f757888b13a",
                        "assembler member SHA256")
                return ast.parse(payload)
    raise Rejected("assembler not found within archive scan capacity")


def assignment(tree: ast.Module, name: str) -> ast.expr:
    found = [node.value for node in tree.body if isinstance(node, ast.Assign)
             and any(isinstance(target, ast.Name) and target.id == name
                     for target in node.targets)]
    require(len(found) == 1, "unique selected assembler assignment: " + name)
    return found[0]


def selected_parameters(inputs: dict[str, bytes]) -> tuple[dict, tuple[int, ...]]:
    selected = json.loads(inputs[SELECTED])
    assembly = json.loads(inputs[ASSEMBLY])
    bit = json.loads(inputs[BIT])
    require(selected["certificate"] == ASSEMBLY, "selected certificate path")
    require(selected["certificate_sha256"] == hashlib.sha256(inputs[ASSEMBLY]).hexdigest(),
            "selected certificate hash")
    require(selected["kappa"] == assembly["kappa"], "selected exponent binding")
    citation = assembly["bit_supplier"]
    require(citation["pr"] == 589 and citation["path"] == BIT, "selected ordinary BIT producer")
    header = b"blob " + str(len(inputs[BIT])).encode("ascii") + b"\0"
    require(citation["git_blob_sha1"] == hashlib.sha1(header + inputs[BIT]).hexdigest(),
            "selected BIT blob")
    tree = assembler(inputs[ARCHIVE])
    require(ast.literal_eval(assignment(tree, "BIT_BLOB")) == citation["git_blob_sha1"],
            "assembler BIT source binding")
    expression = ast.parse("1 + 7 * BIT_L", mode="eval").body
    require(ast.dump(assignment(tree, "BIT_M")) == ast.dump(expression), "BIT dimension formula")
    stages = [node.value for node in tree.body if isinstance(node, ast.Assign)
              and any(isinstance(t, ast.Tuple) and ast.dump(t) ==
                      ast.dump(ast.parse("BIT_L, BIT_T = 0").body[0].targets[0])
                      for t in node.targets)]
    require(len(stages) == 1 and ast.literal_eval(stages[0]) == (9, 32), "nine-stage binding")
    profile = bit["nine"]["profile"]
    require(len(profile) <= 64, "rank inventory capacity")
    ranks = tuple(sorted(int(key) for key in profile))
    require(all(type(value) is int and value > 0 for value in profile.values()), "rank counts")
    record = bit["nine"]["bit"]
    require(ranks[-1] == record["maxchild"] == 42 and ranks[0] == 1, "selected rank boundary")
    require(record["physical"] == record["live"] + 9 == 28425, "all physical work roles")
    require(record["row_coefficient"] == 2 * (64 ** 2 + 1) + 9909 + 252, "source row bill")
    require(assembly["bit_lower"] == bit["nine"]["bit_lower"], "selected saving")
    return assembly, ranks


def depth_certificate(m: int, r: int, steps: int, bits: int, terminal: int) -> None:
    require(all(type(x) is int for x in (m, r, steps, bits, terminal)), "integer certificate")
    require(2 <= m <= 128 and 1 <= r < m and 1 <= steps <= 64 and 1 <= bits <= 64,
            "bounded contraction domain")
    require(1 <= terminal <= m, "terminal domain")
    require((1 << bits) * r ** steps < m ** steps, "strict contraction certificate")
    require((1 << bits) <= terminal ** steps, "terminal slack, not an additive constant")


def forward_depth(n: int, m: int = 64, r: int = 42) -> int:
    require(type(n) is int and n >= 0 and n.bit_length() <= MAX_ATOM_BITS, "atom count capacity")
    require(m == 64 and r == 42, "selected forward recurrence")
    for depth in range(MAX_DEPTH + 1):
        if n < m:
            return depth
        n = r * (n // m)
    raise Rejected("depth capacity exhausted")


def finite_checks(ranks: tuple[int, ...]) -> dict:
    require(len(ranks) <= 64 and all(1 <= r <= 42 for r in ranks) and 42 in ranks,
            "selected child domain")
    # A separate all-child dynamic program, not the forward maximum-rank loop.
    depths = [0] * (FINITE_WIDTH + 1)
    for n in range(64, FINITE_WIDTH + 1):
        depths[n] = 1 + max(depths[r * (n // 64)] for r in ranks)
        require((1 << (17 * depths[n])) <= n ** 28, "finite ceiling-free inequality")
    for n in range(FINITE_WIDTH + 1):
        require(depths[n] == forward_depth(n), "all-child versus forward depth")
    # Independent inverse thresholds, including both sides of each floor cut.
    thresholds = [64]
    for _ in range(63):
        thresholds.append(64 * ((thresholds[-1] + 41) // 42))
    probes = {0, 1, 63, 64, 95, 96, 127, 128}
    for threshold in thresholds:
        probes.update((threshold - 1, threshold, threshold + 1))
    for n in sorted(probes):
        require(forward_depth(n) == bisect_right(thresholds, n), "inverse threshold boundary")
    large = []
    for bits in (7, 64, 256, 1024, 4096):
        for offset in (-1, 0, 1):
            n = (1 << bits) + offset
            d = forward_depth(n)
            require((1 << (17 * d)) <= n ** 28, "large-width ceiling-free inequality")
            large.append([bits, offset, d])
    return {"all_child_widths": FINITE_WIDTH + 1, "threshold_probes": len(probes),
            "large_widths": large}


def first_cutoff(assembly: dict, sigma: int) -> dict:
    require(type(sigma) is int and sigma == 6748, "derived stock coefficient")
    s = min(Fraction(assembly["bit_lower"]),
            (1 - Fraction(1, 10 ** 24)) * Fraction(assembly["complex_lower"])) - Fraction(1, 10 ** 27)
    old = Fraction(384599, 10 ** 10)
    new = (1 - s) * s + s * old
    delta = min(s - new, 1 - new - s, 1 - new - s * (1 - old), 1 - s)
    first = assembly["bootstrap"][0]
    require(Fraction(first["exponent"]) == new and Fraction(first["gap"]) == delta,
            "selected native first-stage formula")
    cutoff = int(first["cutoff_log2"])
    ell = (8 * sigma - 1).bit_length()
    require(0 < delta <= 1 - s and cutoff >= 3, "stock-fit domain")
    require(cutoff * delta ** 2 >= 36 and cutoff * delta >= 2 * (4 + ell), "stock-fit guard")
    return {"branch": "native", "stage": 1, "cutoff_log2": cutoff, "ell": ell,
            "gap": str(delta)}


def reconstruct(inputs: dict[str, bytes]) -> dict:
    assembly, ranks = selected_parameters(inputs)
    depth_certificate(64, 42, 28, 17, 64)
    sigma = (64 ** 2 + 1) * Fraction(28, 17)
    require(sigma.denominator == 1 and sigma == 6748, "exact stock coefficient")
    require(6748 * 17 == 8194 * 14, "coefficient comparison")
    return {"status": "PASS_SELECTED_BIT_CEILING_FREE_STOCK", "m": 64, "maxchild": 42,
            "physical_roles": 28425, "depth_allowance": "28/17", "sigma": int(sigma),
            "predecessor_sigma": 8194, "coefficient_ratio": "14/17",
            "finite_checks": finite_checks(ranks), "first_cutoff": first_cutoff(assembly, int(sigma)),
            "scope": "Conditional packet/completed-leaf envelope only; no new kappa or supplier admission."}


def check_receipt(actual: dict, receipt: dict) -> None:
    require(actual == receipt, "required canonical RESULT.json mismatch")


def main() -> None:
    actual = reconstruct(read_inputs())
    receipt = json.loads((PACKAGE / "RESULT.json").read_bytes())
    check_receipt(actual, receipt)
    print(f"{actual['status']} sigma=6748 predecessor=8194 ratio=14/17 "
          f"widths={actual['finite_checks']['all_child_widths']} ell=16 no_new_kappa")


if __name__ == "__main__":
    main()
