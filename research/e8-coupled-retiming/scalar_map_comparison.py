"""Compare every row of the complete rational scalar maps of two certificates."""

from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import sys


def word(certificate):
    additions = []
    for phase in ("A", "B"):
        if phase == "B":
            retained = {k: register for k, register, _ in certificate["ret"]}
            for target, terms in enumerate(certificate["scat"]["table"]):
                additions.extend((certificate["v"] + target, retained[k], Fraction(a, b)) for k, a, b in terms)
        for gate in certificate[phase]:
            tag, _, pivot, terms = gate[:4]
            for register, a, b in terms:
                target, source = (pivot, register) if tag == "in" else (register, pivot)
                additions.append((target, source, Fraction(a, b)))
    return additions


def row(additions, output):
    result = {output: Fraction(1)}
    for target, source, coefficient in reversed(additions):
        value = result.get(target, 0)
        if value:
            result[source] = result.get(source, 0) + coefficient * value
            if not result[source]:
                del result[source]
    return result


def compare(certificates):
    """Compare the complete scalar maps, including all initial helper values."""
    a, b = certificates
    assert all(a[key] == b[key] for key in ("h", "v", "R", "ports", "scat"))
    n = 2 * a["v"] + a["R"]
    words = [word(certificate) for certificate in certificates]
    assert len(words[0]) == len(words[1])
    counts = []
    for output in range(n):
        original, candidate = (row(additions, output) for additions in words)
        assert original == candidate, output
        counts.append(len(original))
    return {
        "complete_scalar_maps_equal": True,
        "rows": n,
        "columns": n,
        "nonzero_entries": sum(counts),
        "elementary_additions": len(words[0]),
        "scope": "Exact full rational scalar map, including arbitrary source, target, and helper initial values. Frame transforms and compiled cleanup are separate obligations."
    }


def main():
    if sys.flags.optimize:
        raise SystemExit("Assertions must remain enabled for verification")
    assert len(sys.argv) == 3
    raws = [gzip.decompress(Path(path).read_bytes()) for path in sys.argv[1:]]
    result = compare([json.loads(raw) for raw in raws])
    result["uncompressed_sha256"] = [hashlib.sha256(raw).hexdigest() for raw in raws]
    result["source_files"] = sys.argv[1:]
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
