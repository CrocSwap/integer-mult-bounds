"""Packed transition adapter for the pinned PR1443 replay. Apache-2.0."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PINS = (
    ('research/bit-dihedral-commutator/CERTIFICATE.json',
     '8ec4519a34ab5c6eca6dea92b90aa317c851c566040caf89d822d1d96c70a8c5'),
    ('research/bit-dihedral-commutator/SOURCES.json',
     '8b54ff152eaa87502cb88da77da0e73a2606e60f83c69ca5b9b60ff42f526ccd'),
    ('research/bit-dihedral-commutator/verify.py',
     'dff2985bc4ec27d0e527d017471f6e6d43bb7855e555385fc80027aad499735d'),
    ('research/bit-three-register-lower-bound/README.md',
     'c12b33ef388deece0cbf891505a2ce2c0779a0c3a6cf1f0f7f7039bab59cbebd'),
)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def source_bytes(root=ROOT):
    """Authenticate every executable/data input before executing fixed source."""
    contents = {}
    for name, digest in PINS:
        raw = (root / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest, "source pin: " + name)
        contents[name] = raw
    return contents


def load_original(root=ROOT):
    contents = source_bytes(root)
    name = "research/bit-dihedral-commutator/verify.py"
    path = root / name
    namespace = {"__file__": str(path), "__name__": "pinned_dihedral_original"}
    # This is only the hash-authenticated, fixed predecessor program. Its main
    # block, including the explicit --write option, is never entered.
    exec(compile(contents[name], str(path), "exec"), namespace)
    return namespace


def packed_step(permutations):
    require(set(permutations) == {1, 2}, "two paid label tables")
    tables = {}
    for label in (1, 2):
        values = permutations[label]
        require(len(values) == 256 and all(0 <= v < 256 for v in values),
                "byte permutation range")
        tables[label] = tuple(v ^ values[v] for v in range(256))
    scatter = (0, 1, 1 << 16, (1 << 16) + 1)

    def step(state, generator):
        label, x, y = generator
        # Each 16-bit row holds the two independent coefficient bytes.
        if y == 1:
            row = state
        elif y == 2:
            row = state >> 16
        else:
            row = state ^ (state >> 16)
        table = tables[label]
        delta = table[row & 255] | (table[(row >> 8) & 255] << 8)
        return state ^ (delta * scatter[x])

    return step


def replay():
    original = load_original()
    original["step"] = packed_step(original["PERM"])
    result = json.loads(json.dumps(original["run"]()))
    certificate = json.loads((original["H"] / "CERTIFICATE.json").read_text())
    require(result == certificate, "complete original certificate")
    return result


def main():
    require(len(sys.argv) == 1, "this replay accepts no arguments")
    result = replay()
    print(result["status"], "minimum=" + str(result["minimum"]),
          "layers=" + str(result["identity_layers"]),
          "meetings=" + str(result["meeting_lengths"]))


if __name__ == "__main__":
    main()
