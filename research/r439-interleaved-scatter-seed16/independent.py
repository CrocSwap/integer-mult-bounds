#!/usr/bin/env python3
"""Independent suffix reconstruction: set-valued rows, forward right updates.

No primary or predecessor module is imported. The same elementary 2+2 lemma
is checked with a separately enumerated ball. This is algorithmic independence
of the coefficient reconstruction, not independent human review.
Sricharan Vagvala with substantial OpenAI Codex assistance. Apache-2.0.
"""
import gzip
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/r439-bsection-stars-seed01/candidate.json.gz"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def fingerprint(values):
    text = "".join(format(value, "028x") + "\n" for value in sorted(values))
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def responses(gates, size):
    # First compute the whole suffix at cut zero by LEFT row operations.
    matrix = [{r} for r in range(size)]
    for dst, src in gates:
        matrix[dst] = matrix[dst].symmetric_difference(matrix[src])
    atoms = set()
    for cut in range(len(gates) + 1):
        # Extract columns from the set-valued rows, rather than propagating
        # bit-packed columns backwards as the primary implementation does.
        for port in range(size):
            value = sum(2 ** row for row in range(size) if port in matrix[row])
            require(value != 0, "singular suffix")
            atoms.add(value)
        if cut < len(gates):
            dst, src = gates[cut]
            # Remove the first remaining involution by RIGHT multiplication.
            for row in matrix:
                if dst in row:
                    row.symmetric_difference_update({src})
    require(matrix == [{r} for r in range(size)], "suffix did not end at identity")
    return atoms


def witness_response(gates, taps, size):
    value = [False] * size
    require(len(taps) == len({tuple(t) for t in taps}), "duplicate witness tap")
    require(all(type(c) is int and type(p) is int and 0 <= c <= len(gates) and 0 <= p < size
                for c, p in taps), "witness cut/target range")
    for cut in range(len(gates) + 1):
        for time, port in taps:
            if time == cut:
                value[port] = not value[port]
        if cut < len(gates):
            dst, src = gates[cut]
            value[dst] = value[dst] != value[src]
    return sum(2 ** i for i, bit in enumerate(value) if bit)


def main():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    pin = next(p for p in pins["files"] if p["path"] == SOURCE and p["usage"] == "input")
    raw = (ROOT / SOURCE).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == pin["sha256"], "source SHA-256")
    require(hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest() == pin["git_blob"], "source blob")
    word = json.loads(gzip.decompress(raw))
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    size = word["v"]
    require((size, word["R"], len(word["ret"])) == (111, 439, 9), "frozen dimensions")
    require(type(certificate["column"]) is int and certificate["column"] == 7, "assigned column")
    last_read = -1
    for i, (_, dst, srcs) in enumerate(word["D"]):
        if size <= dst < 2 * size and all(s >= 2 * size for s in srcs):
            last_read = i
    require(last_read >= 0, "D helper reads")
    undo = []
    for frame, dst, srcs in word["D"][last_read + 1:]:
        if size <= dst < 2 * size and all(size <= s < 2 * size for s in srcs):
            require(frame == 0 and len(srcs) == 1, "undo gate shape")
            undo.append((dst - size, srcs[0] - size))
    require(len(undo) == 306, "frozen undo length")
    target = sum(2 ** row for row, terms in enumerate(word["scatter"]) if 7 in terms)
    require(set(certificate["problems"]) == {"literal306", "ideal303"}, "problem inventory")
    controls = 0
    for name in ("literal306", "ideal303"):
        gates = undo if name == "literal306" else [g for i, g in enumerate(undo) if i not in {31, 51, 52}]
        claimed = certificate["problems"][name]
        atoms = responses(gates, size)
        alphabet = [0] + sorted(atoms)
        # Includes equal operands, zero operands, and all unordered pairs.
        ball = {a ^ b for a, b in combinations_with_replacement(alphabet, 2)}
        intersections = sum((target ^ a) in ball for a in ball)
        require(intersections == 0, "four taps suffice")
        require(claimed["undo_gates"] == len(gates) and claimed["cuts"] == len(gates) + 1,
                "complete cut coverage")
        require(claimed["dictionary_size"] == len(atoms) and claimed["dictionary_sha256"] == fingerprint(atoms),
                "independent dictionary differs")
        require(claimed["ball_two_size"] == len(ball) and claimed["ball_two_sha256"] == fingerprint(ball),
                "independent ball differs")
        require(int(claimed["target"], 16) == target and claimed["four_tap_intersection_size"] == 0,
                "target/intersection certificate")
        taps = claimed["taps"]
        require(type(claimed["minimum_taps"]) is int and claimed["minimum_taps"] == len(taps) == 5,
                "claimed exact minimum")
        require(witness_response(gates, taps, size) == target, "forward five-tap witness")
        require(witness_response(gates, taps[:-1], size) != target, "omitted-tap control")
        controls += 1
        wrong = [list(t) for t in taps]
        wrong[0][1] = (wrong[0][1] + 1) % size
        require(witness_response(gates, wrong, size) != target, "wrong-target control")
        controls += 1
        short = 0
        for a in sorted(atoms)[:4]:
            short ^= a
        require(any((short ^ a) in ball for a in ball), "known four-tap control")
        controls += 1
    print(f"PASS_INDEPENDENT_INTERLEAVING_FLOOR column=7 minimum=5 orders=2 controls={controls}")


if __name__ == "__main__":
    main()
