"""Independent exact matrix action for the paired BIT caller and inverse."""
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

PINS = {
    "EFREE-CALLER.json.gz": "757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b",
    "EFREE-RESULT.json": "a46b6c6040f75184cab5467656811ad988c216e3bc8e44d595a5015b6e49620b",
    "retained/inputs/BIT-NATIVE-WORD.json.gz": "51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78",
}
CANONICAL = "e54523517d0f03e58352e647c403a5af3e525a57"
SOURCE = f"https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/{CANONICAL}/research/paired-query-only-bit"


def load(root, key):
    raw = (root / key).read_bytes()
    if sha256(raw).hexdigest() != PINS[key]:
        raise ValueError(f"sha256 mismatch: {key}")
    return json.loads(gzip.decompress(raw) if key.endswith(".gz") else raw)


def run(w, changed_locals, new_query, reverse=False):
    # A row maps a Laurent body monomial and q parity to all 38 coefficients,
    # stored together in a bitmask. Every operation is over F2.
    zero = (0,) * w["stages"]
    rows = [{(0, zero): 1 << i} for i in range(w["roles"])]
    steps = list(enumerate(w["events"]))

    def shift(row, q=0, stages=(), sign=1):
        deltas = set(stages)
        return {(parity ^ q, tuple(a + sign * ((i + 1) in deltas)
                                  for i, a in enumerate(powers))): bits
                for (parity, powers), bits in row.items()}

    def add(left, right):
        output = dict(left)
        for monomial, bits in right.items():
            coefficient = output.pop(monomial, 0) ^ bits
            if coefficient:
                output[monomial] = coefficient
        return output

    for index, (op, *args) in (reversed(steps) if reverse else steps):
        if op == "SWAP":
            x, y = args
            rows[x], rows[y] = rows[y], rows[x]
        elif op == "IDLE_ONE":
            x, stages = args
            rows[x] = shift(rows[x], stages=stages, sign=-1 if reverse else 1)
        elif op in ("ADD", "QUERY"):
            y, x = args
            rows[y] = add(rows[y], shift(rows[x], q=int(op == "QUERY" and index != new_query)))
        elif op == "LOCAL":
            stage, x, y = args
            new = index in changed_locals
            if reverse:
                bx = shift(rows[x], stages=(stage,), sign=-1, q=int(new))
                by = shift(rows[y], stages=(stage,), sign=-1)
                rows[x] = bx
                rows[y] = add(by, shift(bx, q=int(not new)))
            else:
                rows[y] = shift(add(rows[y], shift(rows[x], q=int(not new))), stages=(stage,))
                rows[x] = shift(rows[x], q=int(new), stages=(stage,))
        else:
            raise ValueError(op)

    wrong = []
    for i, spec in enumerate(w["diagonal"]):
        expected = shift({(0, zero): 1 << i}, q=spec["q"], stages=spec["stages"],
                         sign=-1 if reverse else 1)
        residue = add(rows[i], expected)
        touched = 0
        for mask in residue.values():
            touched |= mask
        for j in range(w["roles"]):
            if touched >> j & 1:
                wrong.append((i, j))
    return wrong


def main(root):
    w = load(root, "EFREE-CALLER.json.gz")
    result = load(root, "EFREE-RESULT.json")
    load(root, "retained/inputs/BIT-NATIVE-WORD.json.gz")
    order = Counter()
    changed = []
    for i, (op, *args) in enumerate(w["events"]):
        if op == "LOCAL":
            stage, x, y = args
            order[stage] += 1
            if order[stage] == 2:
                assert (x, y) == (20, 19)
                changed.append(i)
    assert order == dict.fromkeys(range(1, 19), 2)
    assert w["events"][349] == ["QUERY", 19, 20] and w["ports"] == 111
    assert result["caller_sha256"] == PINS["EFREE-CALLER.json.gz"]
    assert result["native_source_sha256"] == PINS["retained/inputs/BIT-NATIVE-WORD.json.gz"]
    modes = {}
    for label, locals_, query in (
        ("predecessor", [], None),
        ("candidate", changed, 349),
        ("revert_first_changed_local", changed[1:], 349),
        ("retain_query_349", changed, None),
    ):
        modes[label] = {"forward_mismatches": run(w, locals_, query),
                        "reverse_mismatches": run(w, locals_, query, reverse=True)}
    assert not any(modes["predecessor"].values()) and not any(modes["candidate"].values())
    assert all(modes["revert_first_changed_local"].values()) and all(modes["retain_query_349"].values())
    return {"pins": PINS, "source_urls": {p:f"{SOURCE}/{p}" for p in PINS},
            "events": len(w["events"]), "coefficients_per_direction": w["roles"] ** 2,
            "changed_second_locals": changed, "query_to_add": 349, "modes": modes}


if __name__ == "__main__":
    print(json.dumps(main(Path(sys.argv[1])), sort_keys=True, indent=2))
