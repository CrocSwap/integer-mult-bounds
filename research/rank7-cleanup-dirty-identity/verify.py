#!/usr/bin/env python3
"""Exact private/live block identity for PR2979's literal cleanup only."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MAX_BYTES = 4_000_000
MAX_REGISTERS = 800
MAX_GATES = 6000
MAX_TERMS = 4096
MAX_WORD = 256
FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]
Term = tuple[int, tuple[int, ...]]
Polynomial = dict[Term, Fraction]


@dataclass(frozen=True)
class Gate:
    kind: str
    target: int
    source: int = 0
    coefficient: Fraction = Fraction(1)
    operator: int = 0


@dataclass(frozen=True)
class Model:
    gates: tuple[Gate, ...]
    live: tuple[int, ...]
    private: tuple[int, ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    require(path.stat().st_size <= MAX_BYTES, "input file too large")
    result = json.loads(path.read_bytes(), object_pairs_hook=unique_object)
    require(isinstance(result, dict), "expected JSON object")
    return result


def read_word(root: Path, entry: dict) -> dict:
    path = root / entry["path"]
    require(path.stat().st_size <= MAX_BYTES, "compressed source too large")
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == entry["sha256"], "source hash mismatch")
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        payload = stream.read(MAX_BYTES + 1)
    require(len(payload) <= MAX_BYTES, "decompressed source too large")
    word = json.loads(payload, object_pairs_hook=unique_object)
    require(isinstance(word, dict), "word must be an object")
    return word


def integer(value: object) -> int:
    require(type(value) is int and abs(value) <= 1_000_000, "invalid bounded integer")
    return value


def parse_gate(raw: list, allowed: set[int], operators: int) -> Gate:
    require(isinstance(raw, list) and len(raw) in (4, 5, 6), "gate shape")
    require(raw[-1] == FULL, "cleanup gate is not at FULL")
    kind, target = raw[0], integer(raw[1])
    require(target in allowed, "invalid target register")
    if kind == "warp":
        require(len(raw) == 4, "warp shape")
        op = integer(raw[2])
        require(0 < abs(op) <= operators, "invalid warp operator")
        return Gate(kind, target, operator=op)
    require(kind in ("add", "scale"), "unknown gate kind")
    require(len(raw) == (6 if kind == "add" else 5), "scalar gate shape")
    numerator, denominator = map(integer, raw[-3:-1])
    require(denominator != 0, "zero denominator")
    coefficient = Fraction(numerator, denominator)
    denominator = coefficient.denominator
    require(denominator & (denominator - 1) == 0, "dyadic denominator")
    require(coefficient != 0, "zero scalar")
    if kind == "scale":
        numerator = abs(coefficient.numerator)
        require(numerator & (numerator - 1) == 0, "nonunit scale")
        return Gate(kind, target, coefficient=coefficient)
    source = integer(raw[2])
    require(source in allowed and source != target, "invalid ADD source")
    return Gate(kind, target, source, coefficient)


def decode(word: dict) -> Model:
    require(word["kind"] == "BORROW-WORD", "wrong word kind")
    report = word["report"]
    require((report["v"], report["h"], report["R"]) == (112, 9, 480), "wrong geometry")
    removed = tuple(map(integer, word["removed"]))
    require(len(set(removed)) == len(removed) == 72, "removed inventory")
    require(all(224 <= r < 704 for r in removed), "removed range")
    live = tuple(r for r in range(704) if r not in removed)
    helpers = tuple(sorted(int(r) for r in word["helper_final"]))
    require(len(helpers) == len(set(helpers)) == 91, "private inventory")
    require(all(r in live and r >= 224 for r in helpers), "private owner range")
    private = tuple(r + 704 for r in helpers)
    require(len(live) == 632 and len(live + private) <= MAX_REGISTERS, "register bound")
    require(1 <= len(word["warps"]) <= 256, "operator count")
    require(len(word["cleanup"]) == 5207, "literal cleanup length")
    allowed = set(live + private)
    gates = tuple(parse_gate(g, allowed, len(word["warps"])) for g in word["cleanup"])
    return Model(gates, live, private)


def oriented(gate: Gate, dual: bool) -> Gate:
    if not dual:
        return gate
    if gate.kind == "add":
        return Gate("add", gate.source, gate.target, -gate.coefficient)
    if gate.kind == "scale":
        return Gate("scale", gate.target, coefficient=1 / gate.coefficient)
    # These symbols denote K_i^(-T), not K_i or K_i^T.
    return gate


def prepend(operator: int, word: tuple[int, ...]) -> tuple[int, ...]:
    # Signed names are independent generators. No inverse or commutation law.
    result = (operator,) + word
    require(len(result) <= MAX_WORD, "operator word capacity")
    return result


def bounded(polynomial: Polynomial) -> None:
    require(len(polynomial) <= MAX_TERMS, "polynomial capacity")
    require(all(abs(v.numerator).bit_length() <= 4096 and v.denominator.bit_length() <= 4096
                for v in polynomial.values()), "coefficient capacity")


def apply(gate: Gate, rows: dict[int, Polynomial]) -> None:
    target = rows[gate.target]
    if gate.kind == "add":
        for key, value in rows[gate.source].items():
            total = target.get(key, Fraction(0)) + gate.coefficient * value
            if total:
                target[key] = total
            else:
                target.pop(key, None)
    elif gate.kind == "scale":
        rows[gate.target] = {k: gate.coefficient * v for k, v in target.items()}
    elif gate.kind == "warp":
        rows[gate.target] = {(r, prepend(gate.operator, w)): v
                             for (r, w), v in target.items()}
    else:
        raise ValueError("unknown internal gate")
    bounded(rows[gate.target])


def identity(register: int) -> Polynomial:
    return {(register, ()): Fraction(1)}


def last_touches(model: Model) -> dict[int, int]:
    touches = {}
    private = set(model.private)
    for index, gate in enumerate(model.gates):
        registers = (gate.target, gate.source) if gate.kind == "add" else (gate.target,)
        for register in registers:
            if register in private:
                touches[register] = index
    require(set(touches) == private, "untouched private array")
    return touches


def matrix_digest(rows: dict[int, Polynomial]) -> str:
    digest = hashlib.sha256()
    for register, polynomial in sorted(rows.items()):
        for (source, word), value in sorted(polynomial.items()):
            digest.update(json.dumps([register, source, word, str(value)],
                                     separators=(",", ":")).encode())
            digest.update(b"\n")
    return digest.hexdigest()


def replay(model: Model, dual: bool) -> dict:
    require(len(model.gates) <= MAX_GATES, "gate capacity")
    require(len(model.live + model.private) <= MAX_REGISTERS, "register capacity")
    rows = {r: identity(r) for r in model.live + model.private}
    touches = last_touches(model)
    by_index = {}
    for register, index in touches.items():
        by_index.setdefault(index, []).append(register)
    max_terms = 1
    for index, raw in enumerate(model.gates):
        gate = oriented(raw, dual)
        apply(gate, rows)
        max_terms = max(max_terms, len(rows[gate.target]))
        for register in by_index.get(index, ()):
            require(rows[register] == identity(register), f"dirty private last touch: {register}")
    require(all(rows[r] == identity(r) for r in model.private), "private block is not identity")
    private = set(model.private)
    require(all(source not in private for r in model.live for source, _ in rows[r]),
            "private input leaked to live output")
    targets = [r for r in model.live if 112 <= r < 224]
    require(all(rows[r] == identity(r) for r in targets), "cleanup changed targets")
    return {"orientation": "dual" if dual else "forward", "gates": len(model.gates),
            "live": len(model.live), "private": len(model.private),
            "private_identity": True, "private_to_live_zero": True,
            "target_identity_count": len(targets), "max_row_terms": max_terms,
            "changed_live_rows": sum(rows[r] != identity(r) for r in model.live),
            "matrix_sha256": matrix_digest(rows),
            "last_touches": {str(r): index for r, index in sorted(touches.items())}}


def audit(root: Path = ROOT) -> dict:
    sources = read_json(PACKAGE / "SOURCES.json")
    entries = [e for e in sources["files"] if e["usage"] == "input"]
    require(len(entries) == 2, "expected exactly two providers")
    cases = {}
    for entry in entries:
        model = decode(read_word(root, entry))
        provider = "base" if entry["path"].endswith("WORD-base.json.gz") else "extra"
        require(provider not in cases, "duplicate provider")
        cases[provider] = [replay(model, dual) for dual in (False, True)]
    require(set(cases) == {"base", "extra"}, "provider coverage")
    return {"status": "PASS_RANK7_CLEANUP_DIRTY_IDENTITY", "cases": cases,
            "scope": "Literal FULL-frame scalar/free-associative-operator cleanup; no native or physical admission."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print receipt instead of comparing it")
    args = parser.parse_args()
    result = audit()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(result == read_json(PACKAGE / "RESULT.json"), "receipt mismatch")
        print("PASS_RANK7_CLEANUP_DIRTY_IDENTITY providers=2 orientations=2 private=91 arbitrary_dirty_entrance")


if __name__ == "__main__":
    main()
