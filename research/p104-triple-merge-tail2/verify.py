#!/usr/bin/env python3
"""Finite certificate for the source-retaining triple-merge rank floor.

Produced by Nick Petalas. Apache-2.0.
"""

import argparse
from collections import Counter
import gzip
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/p104-helper470-twin-rung-removal/WORD.json.gz"
CODE = "research/p104-network-coded-carriers/RESULT.json"
MAX_BYTES = 16 * 1024 * 1024


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_bytes(path: Path) -> bytes:
    with path.open("rb") as stream:
        payload = stream.read(MAX_BYTES + 1)
    require(len(payload) <= MAX_BYTES, "input exceeds size limit")
    return payload


def dot(left: int, right: int) -> int:
    return (left & right).bit_count() & 1


def vector_span(vectors: tuple[int, ...]) -> frozenset[int]:
    require(len(vectors) <= 9, "too many span generators")
    require(all(type(v) is int and 0 <= v < 512 for v in vectors),
            "invalid binary vector")
    result = {0}
    for vector in vectors:
        result |= {entry ^ vector for entry in result}
    return frozenset(result)


def quotient_count(points: tuple[int, ...], group: frozenset[int]) -> int:
    """Explicit cosets, without elimination or any predecessor implementation."""
    require(len(points) <= 104 and len(group) == 8, "invalid quotient sizes")
    cosets = {frozenset(point ^ entry for entry in group) for point in points}
    require(all(len(coset) == 8 for coset in cosets), "invalid coset size")
    require(len(set().union(*cosets)) == 8 * len(cosets) if cosets else True,
            "cosets overlap without equality")
    return len(cosets)


def load_inputs() -> tuple[list[int], list[int], list[int], dict[str, str]]:
    manifest = json.loads(read_bytes(HERE / "SOURCES.json"))
    hashes = {}
    for source in manifest["files"]:
        if source["usage"] == "input":
            path = source["path"]
            require(path in {WORD, CODE,
                    "research/p104-network-coded-carriers/PROOF.md",
                    "research/carrier-merge-relay-premise/PROOF.md"},
                    "unexpected live source")
            digest = sha256(read_bytes(ROOT / path)).hexdigest()
            require(digest == source["sha256"], "source hash mismatch: " + path)
            hashes[path] = digest
    require(len(hashes) == 4, "missing source")
    with gzip.open(ROOT / WORD, "rb") as stream:
        decoded = stream.read(MAX_BYTES + 1)
    require(len(decoded) <= MAX_BYTES, "decoded word exceeds size limit")
    ports = json.loads(decoded)["ports"]
    carrier = json.loads(read_bytes(ROOT / CODE))["carriers"]
    lines, normals = carrier["lines"], carrier["normals_g"]
    require(len(ports) == len(set(ports)) == 104, "invalid port inventory")
    require(len(lines) == len(normals) == 8, "invalid carrier inventory")
    require(all(type(v) is int and 0 < v < 512
                for v in ports + lines + normals), "invalid geometry")
    return ports, lines, normals, hashes


def certify_quotients(ports: list[int], lines: list[int], normals: list[int]) -> list[dict]:
    records = []
    for triple in combinations(range(8), 3):
        group = vector_span(tuple(normals[index] for index in triple))
        require(len(group) == 8, "source triple is dependent")
        for left, right in combinations(triple, 2):
            points = tuple(port for port in ports
                           if dot(port, lines[left]) != dot(port, lines[right]))
            count = quotient_count(points, group)
            require(count > 28, "two seven-dimensional paths are not excluded")
            records.append({"triple": triple, "pair": [left, right],
                            "receivers": len(points), "cosets": count})
    require(len(records) == 168, "incomplete triple/pair domain")
    return records


def four_plane_masks() -> tuple[int, ...]:
    """Every 4-space of F2^6 via its unique 2-space annihilator."""
    annihilators = {tuple(sorted((left, right, left ^ right)))
                    for left, right in combinations(range(1, 64), 2)}
    require(len(annihilators) == 651, "annihilator inventory")
    masks = tuple(sum(1 << vector for vector in range(64)
                      if all(dot(vector, normal) == 0 for normal in plane))
                  for plane in sorted(annihilators))
    require(len(set(masks)) == 651 and all(mask.bit_count() == 16 for mask in masks),
            "four-space inventory")
    return masks


def controls() -> dict[str, int]:
    masks = four_plane_masks()
    maximum = max((left | right).bit_count() for left, right in product(masks, repeat=2))
    require(maximum == 28, "two-four-space cover capacity")
    require((masks[0] | masks[-1]).bit_count() <= 28, "synthetic cover")
    require(29 > maximum and not 28 > maximum, "strict threshold control")
    group = vector_span((1, 2, 4))
    require(quotient_count((0, 1, 2, 7, 8, 9, 16, 24), group) == 4,
            "explicit quotient fixture")
    require(quotient_count((), group) == 0, "empty quotient fixture")
    invalid = 0
    for vectors in ((True,), (512,), tuple(range(10))):
        try:
            vector_span(vectors)
        except ValueError:
            invalid += 1
    require(invalid == 3, "invalid vector controls")
    try:
        quotient_count((0,), frozenset((0,)))
    except ValueError:
        invalid += 1
    require(invalid == 4, "missing source-dimension control")
    rejected_geometry = 0
    for normals in ([1] * 8, [1 << index for index in range(8)]):
        try:
            certify_quotients([1], [1] * 8, normals)
        except ValueError:
            rejected_geometry += 1
    require(rejected_geometry == 2, "dependent or empty-demand geometry accepted")
    surviving = []
    for costs in product(range(22), repeat=3):
        if min(costs) >= 6 and sum(value <= 6 for value in costs) <= 1:
            surviving.append(sum(costs) + 2)
    require(min(surviving) == 22, "integer paid-rank consequence")
    return {"four_spaces": len(masks), "ordered_space_pairs": len(masks) ** 2,
            "maximum_cover": maximum, "rejected_invalid_inputs": invalid,
            "rejected_geometry": rejected_geometry,
            "cost_tuples": 22 ** 3, "rank_floor": min(surviving)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    ports, lines, normals, input_hashes = load_inputs()
    records = certify_quotients(ports, lines, normals)
    control_report = controls()
    receipt = {"claim_type": "scoped proof with finite certificate",
               "triples": 56, "triple_pair_cases": len(records),
               "quotient_histogram": dict(sorted(Counter(r["cosets"] for r in records).items())),
               "records": records, "controls": control_report,
               "input_sha256": input_hashes,
               "package_sha256": {path.name: sha256(read_bytes(path)).hexdigest()
                                  for path in sorted(HERE.iterdir()) if path.is_file()}}
    payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        require(args.output.is_absolute(), "receipt path must be absolute")
        output = args.output.resolve()
        require(ROOT not in output.parents,
                "receipt must be outside checkout")
        with output.open("x", encoding="utf-8") as stream:
            require(stream.write(payload) == len(payload), "incomplete receipt write")
    print(json.dumps({key: value for key, value in receipt.items()
                      if key not in {"records", "package_sha256", "input_sha256"}}, sort_keys=True))
    print("PASS_P104_TRIPLE_MERGE_TAIL2")


if __name__ == "__main__":
    main()
