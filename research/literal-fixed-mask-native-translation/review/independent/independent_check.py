#!/usr/bin/env python3
"""Independent GF(2) and packed-address review of the frozen fixed-mask join.

No imports from the author package.  The only package reads are for exact
source/freeze authentication.  All checks remain active under python -O.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_FREEZE = "de2753cb42a012e07aa7ace263bedce5c4be8506ae30ab768af9e165a6edd6e0"
EXPECTED_PROOF = "f43040c6331dc29ecf3f435e980cc71f00a60e421f50f4e843192a23e733bd44"
EXPECTED_AFFINE = "9387d4caa6ea6ad9e232f4a2a07112fa1a681d34af19e5aae64d1d8adc5ebd2c"
N = 9
IDENTITY = tuple(1 << i for i in range(N))


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def authenticate(package: Path) -> dict:
    freeze_raw = (package / "FREEZE.json").read_bytes()
    require(sha(freeze_raw) == EXPECTED_FREEZE, "affine package freeze drift")
    freeze = json.loads(freeze_raw)
    require(freeze["status"] == "FROZEN", "author package is not frozen")
    require(freeze["canonical_main"] == "e54523517d0f03e58352e647c403a5af3e525a57",
            "canonical base drift")
    files = {row["path"]: row for row in freeze["files"]}
    require("PROOF.md" in files and "affine.py" in files and "SOURCES.json" in files,
            "freeze lacks review targets")
    for rel, row in files.items():
        raw = (package / rel).read_bytes()
        require(len(raw) == row["bytes"] and sha(raw) == row["sha256"],
                "frozen byte drift: " + rel)
    require(files["PROOF.md"]["sha256"] == EXPECTED_PROOF, "proof pin mismatch")
    require(files["affine.py"]["sha256"] == EXPECTED_AFFINE, "affine implementation pin mismatch")
    listed = set(files)
    excluded = set(freeze.get("excluded_generated_paths", []))
    actual = {p.relative_to(package).as_posix() for p in package.rglob("*") if p.is_file()}
    actual.discard("FREEZE.json")
    require(actual - listed <= excluded, "unfrozen package files found")
    require(listed <= actual, "frozen package file missing")
    sources = json.loads((package / "SOURCES.json").read_text())
    require(sources["canonical_main"] == freeze["canonical_main"], "source inventory base drift")
    require(sources["translation_head"] == "1dbdaa414cfe4a4a0f015e88a04b52e146566786",
            "#7428 translation source head drift")
    require(sources["translation_proof_blob"] == "5c6325471aaed465737491870443f063c821b7a0",
            "#7428 proof Git blob drift")
    require(sources["parent_rank2_freeze_sha256"] ==
            "072dfea997d4db796d492eaf746e0bd99630964741b88862d0f10f5fc1e00275",
            "rank2 parent source drift")
    rank2_sources = json.loads((package / "reference/rank2/SOURCES.json").read_text())
    cnot_rows = [row for row in rank2_sources["files"]
                 if row.get("path") == "research/literal-selected-linear-maps/linear.py"
                 and row.get("commit") == "39b40c465f7636a4bb6d70af28595fe8f70f4f3f"]
    require(len(cnot_rows) == 1 and cnot_rows[0].get("blob") ==
            "6aad40a6c47ed4415917c86fabbd5227a3819a41",
            "#7430 generic CNOT source pin drift")
    return freeze


def gate_matrix(target: int, control: int) -> tuple[int, ...]:
    rows = list(IDENTITY)
    rows[target] ^= 1 << control
    return tuple(rows)


def matmul(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    """GF(2) row-matrix product, rows stored as integer bit masks."""
    out = []
    for row in a:
        product = 0
        for j in range(N):
            if (row >> j) & 1:
                product ^= b[j]
        out.append(product)
    return tuple(out)


def apply_matrix(matrix: tuple[int, ...], vector: int) -> int:
    image = 0
    for i, row in enumerate(matrix):
        if (row & vector).bit_count() & 1:
            image |= 1 << i
    return image


def word_matrix(word: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    result = IDENTITY
    for target, control in word:
        result = matmul(gate_matrix(target, control), result)
    return result


def conjugator(mask: int) -> tuple[tuple[int, int], ...]:
    """Independent construction: send e_0 to the fixed output mask."""
    if mask == 0:
        return ()
    pivot = (mask & -mask).bit_length() - 1
    word: list[tuple[int, int]] = []
    if pivot:
        word.extend(((0, pivot), (pivot, 0), (0, pivot)))
    for slot in range(N):
        if slot != pivot and ((mask >> slot) & 1):
            word.append((slot, pivot))
    return tuple(word)


def one_column_algebra() -> dict:
    length_histogram: dict[str, int] = {}
    matrix_cases = 0
    relation_cases = 0
    worst = (-1, -1)
    for mask in range(1 << N):
        word = conjugator(mask)
        k = len(word)
        length_histogram[str(k)] = length_histogram.get(str(k), 0) + 1
        expected_k = 0 if mask == 0 else (mask.bit_count() - 1 if (mask & 1) else mask.bit_count() + 2)
        require(k == expected_k, "fixed word-length formula mismatch")
        require(all(0 <= t < N and 0 <= c < N and t != c for t, c in word),
                "invalid fixed CNOT pair")
        if k > worst[1]:
            worst = (mask, k)
        if mask == 0:
            require(not word, "zero mask must emit identity word")
            continue
        inverse = tuple(reversed(word))
        G = word_matrix(word)
        Ginv = word_matrix(inverse)
        require(matmul(G, Ginv) == IDENTITY and matmul(Ginv, G) == IDENTITY,
                "reversed CNOT word is not the matrix inverse")
        require(apply_matrix(G, 1) == mask, "G e0 does not equal fixed mask")
        matrix_cases += 1
        for x in range(1 << N):
            # Chronology: G^{-1}; X_0; G.
            y = apply_matrix(G, apply_matrix(Ginv, x) ^ 1)
            require(y == (x ^ mask),
                    f"GF(2) conjugation mismatch mask={mask} x={x} got={y}")
            relation_cases += 1
    require(worst == (510, 10), "maximum fixed word should be mask 510, length 10")
    require(length_histogram.get("10") == 1, "unexpected count of length-ten masks")
    return {"masks": 512, "nonzero_matrix_checks": matrix_cases,
            "conjugation_address_checks": relation_cases,
            "maximum_word": {"mask": worst[0], "length": worst[1]},
            "length_histogram": dict(sorted(length_histogram.items(), key=lambda kv: int(kv[0])))}


def packed_mask(mask: int, f: int) -> int:
    full = (1 << f) - 1
    return sum(full << ((8 - slot) * f)
               for slot in range(N) if (mask >> slot) & 1)


def address_chunks(address: int, f: int) -> list[int]:
    full = (1 << f) - 1
    return [(address >> ((8 - slot) * f)) & full for slot in range(N)]


def pack_chunks(values: list[int], f: int) -> int:
    return sum(value << ((8 - slot) * f) for slot, value in enumerate(values))


def apply_word_to_fbit_slots(values: list[int], word: tuple[tuple[int, int], ...]) -> None:
    for target, control in word:
        values[target] ^= values[control]


def f2_full_address_checks() -> dict:
    f = 2
    address_count = 1 << (N * f)
    full = (1 << f) - 1
    cases: dict[str, int] = {}
    for mask in (264, 510, 511):
        word = conjugator(mask)
        inverse = tuple(reversed(word))
        packed = packed_mask(mask, f)
        for address in range(address_count):
            values = address_chunks(address, f)
            apply_word_to_fbit_slots(values, inverse)
            values[0] ^= full
            apply_word_to_fbit_slots(values, word)
            expected_values = [value ^ (full if ((mask >> i) & 1) else 0)
                              for i, value in enumerate(address_chunks(address, f))]
            require(values == expected_values,
                    f"f=2 tuple mismatch mask={mask} address={address}")
            require(pack_chunks(values, f) == (address ^ packed),
                    f"f=2 packed mask/order mismatch mask={mask} address={address}")
        cases[str(mask)] = address_count
    return {"f": f, "masks": cases, "total_complete_addresses": sum(cases.values()),
            "slot_order": "slot 0 is the most-significant f-bit chunk; slot 8 is the least-significant chunk"}


def full_packet_block_check() -> dict:
    """Check one whole row-major packet, with all named spectators present."""
    f, P, S, coeffs, w, mask = 2, 2, 2, 2, 3, 510
    addresses = 1 << (N * f)
    per_address = S * coeffs * 2 * w
    volume = P * addresses * per_address
    packed = packed_mask(mask, f)
    # Bytes are opaque component labels.  Treat each address's S/coefficient/
    # Re-Im/width cells as one complete record block and move it unchanged.
    data = bytearray((i * 73 + i // 257 + 19) & 255 for i in range(volume))
    output = bytearray(volume)
    for outer in range(P):
        row = outer * addresses * per_address
        for address in range(addresses):
            src = row + (address ^ packed) * per_address
            dst = row + address * per_address
            output[dst:dst + per_address] = data[src:src + per_address]
    # A separate direct address-index expectation checks every retained byte.
    for outer in range(P):
        row = outer * addresses * per_address
        for address in range(addresses):
            src = row + (address ^ packed) * per_address
            dst = row + address * per_address
            require(output[dst:dst + per_address] == data[src:src + per_address],
                    "complete packet record/spectator permutation mismatch")
    require(len(output) == volume == 2 * P * S * coeffs * w * addresses,
            "complete packet volume mismatch")
    return {"offset": mask, "f": f, "P": P, "S": S, "coefficients": coeffs,
            "width": w, "addresses_per_outer_row": addresses,
            "record_block_bytes_per_address": per_address,
            "row_major_representation_sanity_cells": volume,
            "outer_rows_preserved_by_direct_index_formula": True,
            "all_S_coefficient_component_width_cells_represented": True,
            "independent_whole_packet_routing_check": False,
            "description": "Direct address-index block-copy sanity only; no emitted tape graph is executed."}


def f3_column_lift_checks() -> dict:
    f = 3
    full = (1 << f) - 1
    checked = 0
    vectors = [
        [0] * 9,
        [full] * 9,
        [((i * 5 + 3) & full) for i in range(9)],
        [((i * 3 + 1) & full) for i in range(9)],
    ]
    for mask in range(512):
        word = conjugator(mask)
        inverse = tuple(reversed(word))
        for original in vectors:
            values = original.copy()
            if mask:
                apply_word_to_fbit_slots(values, inverse)
                values[0] ^= full
                apply_word_to_fbit_slots(values, word)
            expected = [v ^ (full if ((mask >> i) & 1) else 0)
                        for i, v in enumerate(original)] if mask else original
            require(values == expected, f"f=3 column lift mismatch mask={mask}")
            checked += 1
    return {"f": f, "all_masks": 512, "deterministic_column_vectors_per_mask": len(vectors),
            "checks": checked}


def run(package: Path) -> dict:
    freeze = authenticate(package)
    algebra = one_column_algebra()
    f2 = f2_full_address_checks()
    packet = full_packet_block_check()
    f3 = f3_column_lift_checks()
    return {
        "status": "PASS_INDEPENDENT_FIXED_MASK_GF2_REVIEW",
        "source": {
            "canonical_main": freeze["canonical_main"],
            "author_freeze_sha256": EXPECTED_FREEZE,
            "proof_sha256": EXPECTED_PROOF,
            "affine_py_sha256": EXPECTED_AFFINE,
            "translation_head_7428": "1dbdaa414cfe4a4a0f015e88a04b52e146566786",
            "generic_cnot_head_7430": "39b40c465f7636a4bb6d70af28595fe8f70f4f3f",
            "generic_cnot_linear_blob": "6aad40a6c47ed4415917c86fabbd5227a3819a41",
            "method": "Separate GF(2) row-matrix products and direct packed-address enumeration; no author imports."
        },
        "one_column": algebra,
        "full_f2_address_space": f2,
        "f3_lift_controls": f3,
        "complete_packet_block": packet,
        "checks": [
            "G e0 equals each nonzero fixed coordinate mask",
            "reverse word is the GF(2) inverse",
            "G after X0 after G^-1 equals XOR by b for every one-column address",
            "bit0-absent maximum word and slow/fast packed slot ordering",
            "P/S/coefficient/Re-Im/width record-index representation sanity only"
        ],
        "limits": [
            "The checker proves the finite GF(2) identities and their per-column lift; it does not execute the tape graph.",
            "The direct f=2 record-block slice calculation is only a row-major representation sanity check, not an independent whole-packet routing result.",
            "The source proof and inherited #7428/#7430 guarantees remain responsible for the universal literal routing and tariff.",
            "No selected full MOVE, phase, caller, or nonleaf admission is proved by this translation-only review."
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", nargs="?", type=Path,
                        default=Path("worker-a/research/generic-affine-native-translation"))
    parser.add_argument("--write", action="store_true", help="write RESULT.json beside this checker")
    args = parser.parse_args()
    result = run(args.package.resolve())
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        (Path(__file__).resolve().parent / "RESULT.json").write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
