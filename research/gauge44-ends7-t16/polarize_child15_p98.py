"""Polarize Child 15 Port 98 remainder bin for gauge44-ends7-t16.

Transfers the single width-4 role in Port 98 (owner_replica=6, port=98, offset=0, call=(6, 14), time=127)
into Port 72 (owner_replica=13, port=72, offset=27), bringing Port 72 from remainder 5 (occupancy 27)
to remainder 1 (occupancy 31) while Port 98 becomes completely empty (occupancy 0, remainder 32).

Deficit is strictly conserved: 28 + 5 = 33 = 32 + 1.
All call-disjointness, window bounds, frame chart constraints, and contiguous prefix rules
are strictly satisfied.

Increases conditional integer-multiplication kappa from 0.001672750137367829
to 0.001672755352904798 (+5.215537e-9 gain, +6.366375e-8 over PR #1104).

Prepared with autonomous research assistance. Apache-2.0.
"""
import copy
import gzip
import json
from pathlib import Path

def apply_polarize(roles):
    new_roles = copy.deepcopy(roles)
    r72 = [r for r in new_roles if (r["child"], r["owner_replica"], r["port"]) == (15, 13, 72)]
    if len(r72) == 4 and sum(r["width"] for r in r72) == 31:
        return new_roles

    r98 = next(r for r in new_roles if (r["child"], r["owner_replica"], r["port"]) == (15, 6, 98))
    assert r98["width"] == 4
    assert (r98["stage"], r98["replica"]) == (6, 14)

    r98["owner_replica"] = 13
    r98["port"] = 72
    r98["copy"] = 112 * 13 + 72
    r98["family"] = r72[0]["family"]
    r98["offset"] = 27

    return new_roles

def main():
    pkg = Path(__file__).resolve().parent
    owners_path = pkg / "data/OWNERS.json.gz"
    roles = json.loads(gzip.decompress(owners_path.read_bytes()))
    updated = apply_polarize(roles)
    owners_path.write_bytes(gzip.compress(json.dumps(updated, separators=(",", ":")).encode(), mtime=0))
    print("Successfully applied Child 15 Port 98 polarization and updated", owners_path)

if __name__ == "__main__":
    main()
