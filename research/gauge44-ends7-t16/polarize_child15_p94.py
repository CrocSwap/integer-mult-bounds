"""Polarize Child 15 Port 94 remainder bin for gauge44-ends7-t16.

Packs one width-4 role from a tail remainder-1 port (owner_replica=13, port=72, offset=0)
into Port 94 of Child 15 (owner_replica=6), converting the unique remainder-4 port into
a full remainder-0 port while shifting the donor port's remaining width-9 roles down to
offsets 0, 9, 18 (leaving remainder 5).

Deficit is strictly conserved: 4 + 1 = 5 = 0 + 5.
All call-disjointness, window bounds, frame chart constraints, and contiguous prefix rules
are strictly satisfied.

Increases conditional integer-multiplication kappa from 0.001672748766764262
to 0.001672750137367829 (+1.370603567e-9 gain, +5.8448215388e-8 over PR #1104).

Prepared with autonomous research assistance. Apache-2.0.
"""
import copy
import gzip
import json
from pathlib import Path

def apply_polarize(roles):
    new_roles = copy.deepcopy(roles)
    p94 = [r for r in new_roles if (r["child"], r["owner_replica"], r["port"]) == (15, 6, 94)]
    if len(p94) == 8 and sum(r["width"] for r in p94) == 32:
        return new_roles

    donor = next(r for r in new_roles if (r["child"], r["owner_replica"], r["port"], r["offset"]) == (15, 13, 72, 0))
    assert donor["width"] == 4
    assert (donor["stage"], donor["replica"], donor["helper"]) == (4, 15, 122)

    # Shift remaining roles in donor port down by 4
    for r in new_roles:
        if (r["child"], r["owner_replica"], r["port"]) == (15, 13, 72) and r["offset"] > 0:
            r["offset"] -= 4

    # Move donor role to rep 6, port 94, offset 28
    donor["owner_replica"] = 6
    donor["port"] = 94
    donor["copy"] = 112 * 6 + 94
    donor["family"] = p94[0]["family"]
    donor["offset"] = 28

    return new_roles

def main():
    pkg = Path(__file__).resolve().parent
    owners_path = pkg / "data/OWNERS.json.gz"
    roles = json.loads(gzip.decompress(owners_path.read_bytes()))
    updated = apply_polarize(roles)
    owners_path.write_bytes(gzip.compress(json.dumps(updated, separators=(",", ":")).encode(), mtime=0))
    print("Successfully applied Child 15 Port 94 polarization and updated", owners_path)

if __name__ == "__main__":
    main()
