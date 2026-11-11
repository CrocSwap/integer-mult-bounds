"""Jointly price marked library expansions and separate BIT split charges."""
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path
import runpy
import sys


PRICE = "pr7209/verify.py"
BIT_ROOT = "research/paired-query-only-bit"
GATE = f"{BIT_ROOT}/independent/interval_gate.py"
INVOICE = f"{BIT_ROOT}/EFREE-RESULT.json"
WORD = f"{BIT_ROOT}/retained/inputs/BIT-NATIVE-WORD.json.gz"
PINS = {
    PRICE: "e153760831952878b5def1776811ea182ea6f3876f09262f7e81a10991ddbd94",
    GATE:
        "8dc2bc4c64cba3f83c664373984a075f1a14b4d53958084091345c8cab189dec",
    INVOICE:
        "a46b6c6040f75184cab5467656811ad988c216e3bc8e44d595a5015b6e49620b",
    WORD:
        "51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78",
}
INCIDENCE = "1acd03fec0213cda8c44f4914c4c0b0c2e2124d7a0dc0586689e80bbc0fb8646"


def auth(path, pin):
    contents = path.read_bytes()
    if sha256(contents).hexdigest() != pin:
        raise ValueError(f"SHA-256 mismatch: {path.name}")
    return contents


def main(root, incidence):
    sources = {path: auth(root / path, pin) for path, pin in PINS.items()}
    data = json.loads(auth(incidence, INCIDENCE))
    assert data["completed_incidence_ports"] == 185 and data["pending_incidence_ports"] == 0
    assert len(data["scopes"]) == 2
    for scope in data["scopes"]:
        assert not scope["additional_useful_slots_with_old_paid_ingress"]
        assert scope["t"]["rank"] == scope["s"]["rank"] == 1
    price = runpy.run_path(str(root / PRICE))
    gate = runpy.run_path(str(root / GATE))
    invoice = json.loads(sources[INVOICE])
    word = json.loads(gzip.decompress(sources[WORD]))
    dims = {int(frame): info["dim"] for frame, info in word["frames"].items()}
    ledger = price["terminal_ledger"](word, dims)
    full = [price["prices"](root, invoice, word, dims, ledger, n) for n in range(23)]
    output = {}
    for key in (data["target"], data["trial"]):
        exponent = Q(key)
        charge = gate["smul"](gate["sub"](gate["exact"](2), gate["power"](2, exponent)), 36)
        fee_lo, fee_hi = map(Q, gate["show"](charge))
        paid = []
        for h in range(3):
            table = []
            for entry in full:
                lo, hi = map(Q, entry[key]["net_upper"])
                table.append((lo - h * fee_hi, hi - h * fee_lo))
            n = next((j for j, bounds in enumerate(table) if bounds[1] > 0), None)
            if n is None:
                assert table[-1][1] < 0
                paid.append({"h": h, "unaffordable": True, "full_net_upper": str(table[-1][1])})
            else:
                assert table[n - 1][1] < 0 < table[n][0]
                paid.append({"h": h, "needed_marked_returns": n,
                             "needed_singleton_expansions": n - 12 - 2 * (1 + h),
                             "previous_net_upper": str(table[n - 1][1]),
                             "first_net_lower": str(table[n][0])})
        output[key] = paid
    print(json.dumps(output, sort_keys=True, indent=2))


if __name__ == "__main__":
    assert __debug__
    main(Path(sys.argv[1]), Path(sys.argv[2]))
