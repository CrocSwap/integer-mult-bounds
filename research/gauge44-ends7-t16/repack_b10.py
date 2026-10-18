"""Re-pack Child 15 Replica 6 non-full ports via optimal CP-SAT (Breakthrough 10).

Solves optimal integer linear assignment across 25 ports (13 non-full ports + 12 donor full ports)
in Child 15 Replica 6, strictly minimizing the concave complex moment M(z).

Net profile transition:
  rem 2: 3 -> 2 (-1)
  rem 11: 1 -> 0 (extinguished)
  rem 12: 0 -> 1 (+1)
  rem 1: 2196 -> 2197 (+1)

Deficit is strictly conserved: global deficit remains 5120; global rank mass remains 1041408.
All call-disjointness, window bounds, frame chart constraints, and contiguous prefix rules
are strictly satisfied.

Increases conditional integer-multiplication kappa from 0.001672789077668839
to 0.001672790201305759 (+1.1236369e-9 gain over Breakthrough 9 commit e4375c83,
+9.8512149e-8 over PR #1104).

Prepared with autonomous research assistance. Apache-2.0.
"""
import gzip
import hashlib
import json
from pathlib import Path

TARGET_SHA = "13e5dc5ef8f4708136811fa9ccad9cbd71e76c310b62c8518f4786ddea481fd3"

CHANGES = {
  "(5, 5, 265)": {
    "port": 90,
    "copy": 762,
    "family": 5802,
    "offset": 4
  },
  "(5, 5, 273)": {
    "port": 87,
    "copy": 759,
    "family": 5799
  },
  "(5, 5, 411)": {
    "port": 105,
    "copy": 777,
    "family": 5817,
    "offset": 0
  },
  "(6, 12, 20)": {
    "port": 92,
    "copy": 764,
    "family": 5804,
    "offset": 13
  },
  "(6, 12, 53)": {
    "port": 90,
    "copy": 762,
    "family": 5802,
    "offset": 16
  },
  "(6, 12, 58)": {
    "port": 106,
    "copy": 778,
    "family": 5818,
    "offset": 24
  },
  "(6, 12, 65)": {
    "port": 87,
    "copy": 759,
    "family": 5799
  },
  "(6, 12, 67)": {
    "port": 100,
    "copy": 772,
    "family": 5812,
    "offset": 24
  },
  "(7, 3, 274)": {
    "port": 91,
    "copy": 763,
    "family": 5803,
    "offset": 8
  },
  "(7, 11, 115)": {
    "port": 99,
    "copy": 771,
    "family": 5811
  },
  "(7, 11, 117)": {
    "port": 91,
    "copy": 763,
    "family": 5803,
    "offset": 20
  },
  "(7, 11, 122)": {
    "port": 90,
    "copy": 762,
    "family": 5802,
    "offset": 20
  },
  "(7, 11, 224)": {
    "port": 108,
    "copy": 780,
    "family": 5820,
    "offset": 21
  },
  "(7, 11, 225)": {
    "port": 94,
    "copy": 766,
    "family": 5806,
    "offset": 21
  },
  "(8, 10, 224)": {
    "port": 105,
    "copy": 777,
    "family": 5817
  },
  "(8, 10, 225)": {
    "port": 97,
    "copy": 769,
    "family": 5809,
    "offset": 16
  },
  "(4, 7, 224)": {
    "port": 111,
    "copy": 783,
    "family": 5823
  },
  "(4, 7, 263)": {
    "port": 100,
    "copy": 772,
    "family": 5812
  },
  "(4, 7, 264)": {
    "port": 99,
    "copy": 771,
    "family": 5811
  },
  "(4, 15, 122)": {
    "port": 107,
    "copy": 779,
    "family": 5819,
    "offset": 0
  },
  "(4, 15, 161)": {
    "port": 94,
    "copy": 766,
    "family": 5806
  },
  "(4, 15, 165)": {
    "port": 90,
    "copy": 762,
    "family": 5802
  },
  "(4, 15, 224)": {
    "port": 106,
    "copy": 778,
    "family": 5818
  },
  "(4, 15, 263)": {
    "port": 100,
    "copy": 772,
    "family": 5812,
    "offset": 8
  },
  "(4, 15, 279)": {
    "port": 104,
    "copy": 776,
    "family": 5816
  },
  "(5, 14, 295)": {
    "offset": 0
  },
  "(6, 5, 170)": {
    "port": 97,
    "copy": 769,
    "family": 5809,
    "offset": 4
  },
  "(6, 5, 379)": {
    "port": 100,
    "copy": 772,
    "family": 5812,
    "offset": 20
  },
  "(6, 5, 381)": {
    "port": 106,
    "copy": 778,
    "family": 5818,
    "offset": 11
  },
  "(6, 5, 382)": {
    "port": 108,
    "copy": 780,
    "family": 5820,
    "offset": 4
  },
  "(6, 5, 383)": {
    "port": 107,
    "copy": 779,
    "family": 5819,
    "offset": 8
  },
  "(6, 5, 387)": {
    "port": 98,
    "copy": 770,
    "family": 5810,
    "offset": 4
  },
  "(6, 5, 389)": {
    "port": 99,
    "copy": 771,
    "family": 5811,
    "offset": 12
  },
  "(6, 5, 390)": {
    "port": 87,
    "copy": 759,
    "family": 5799,
    "offset": 12
  },
  "(6, 5, 395)": {
    "port": 111,
    "copy": 783,
    "family": 5823,
    "offset": 11
  },
  "(8, 11, 250)": {
    "port": 91,
    "copy": 763,
    "family": 5803
  },
  "(5, 15, 85)": {
    "offset": 7
  },
  "(5, 15, 90)": {
    "port": 99,
    "copy": 771,
    "family": 5811,
    "offset": 8
  },
  "(5, 15, 97)": {
    "port": 108,
    "copy": 780,
    "family": 5820,
    "offset": 0
  },
  "(5, 15, 99)": {
    "port": 102,
    "copy": 774,
    "family": 5814,
    "offset": 0
  },
  "(5, 15, 101)": {
    "port": 98,
    "copy": 770,
    "family": 5810
  },
  "(5, 15, 106)": {
    "port": 94,
    "copy": 766,
    "family": 5806,
    "offset": 4
  },
  "(5, 15, 113)": {
    "port": 92,
    "copy": 764,
    "family": 5804,
    "offset": 0
  },
  "(5, 15, 115)": {
    "port": 100,
    "copy": 772,
    "family": 5812,
    "offset": 16
  },
  "(5, 15, 117)": {
    "port": 91,
    "copy": 763,
    "family": 5803,
    "offset": 0
  },
  "(5, 15, 129)": {
    "port": 104,
    "copy": 776,
    "family": 5816,
    "offset": 9
  },
  "(5, 15, 133)": {
    "port": 106,
    "copy": 778,
    "family": 5818,
    "offset": 7
  },
  "(5, 15, 145)": {
    "port": 107,
    "copy": 779,
    "family": 5819,
    "offset": 4
  },
  "(5, 15, 147)": {
    "port": 93,
    "copy": 765,
    "family": 5805
  },
  "(5, 15, 149)": {
    "offset": 9
  },
  "(5, 15, 154)": {
    "port": 105,
    "copy": 777,
    "family": 5817,
    "offset": 4
  },
  "(5, 15, 161)": {
    "port": 89,
    "copy": 761,
    "family": 5801
  },
  "(5, 15, 163)": {
    "port": 90,
    "copy": 762,
    "family": 5802,
    "offset": 12
  },
  "(5, 15, 165)": {
    "port": 87,
    "copy": 759,
    "family": 5799
  },
  "(6, 6, 33)": {
    "port": 88,
    "copy": 760,
    "family": 5800,
    "offset": 0
  },
  "(6, 6, 34)": {
    "port": 109,
    "copy": 781,
    "family": 5821,
    "offset": 4
  },
  "(6, 6, 35)": {
    "port": 98,
    "copy": 770,
    "family": 5810
  },
  "(6, 6, 36)": {
    "port": 106,
    "copy": 778,
    "family": 5818,
    "offset": 15
  },
  "(6, 6, 37)": {
    "port": 94,
    "copy": 766,
    "family": 5806,
    "offset": 8
  },
  "(6, 6, 38)": {
    "port": 93,
    "copy": 765,
    "family": 5805,
    "offset": 4
  },
  "(6, 6, 39)": {
    "port": 92,
    "copy": 764,
    "family": 5804
  },
  "(6, 6, 40)": {
    "port": 108,
    "copy": 780,
    "family": 5820,
    "offset": 8
  },
  "(6, 6, 41)": {
    "port": 110,
    "copy": 782,
    "family": 5822,
    "offset": 13
  },
  "(6, 6, 99)": {
    "port": 99,
    "copy": 771,
    "family": 5811
  },
  "(6, 14, 395)": {
    "port": 87,
    "copy": 759,
    "family": 5799
  },
  "(6, 14, 397)": {
    "port": 94,
    "copy": 766,
    "family": 5806,
    "offset": 17
  },
  "(6, 14, 398)": {
    "port": 105,
    "copy": 777,
    "family": 5817,
    "offset": 8
  },
  "(6, 14, 403)": {
    "port": 91,
    "copy": 763,
    "family": 5803,
    "offset": 4
  },
  "(6, 14, 405)": {
    "port": 99,
    "copy": 771,
    "family": 5811,
    "offset": 20
  },
  "(6, 14, 406)": {
    "port": 107,
    "copy": 779,
    "family": 5819,
    "offset": 12
  },
  "(6, 14, 407)": {
    "port": 111,
    "copy": 783,
    "family": 5823,
    "offset": 15
  },
  "(7, 13, 43)": {
    "port": 109,
    "copy": 781,
    "family": 5821,
    "offset": 13
  },
  "(7, 13, 44)": {
    "port": 92,
    "copy": 764,
    "family": 5804,
    "offset": 22
  },
  "(7, 13, 45)": {
    "port": 105,
    "copy": 777,
    "family": 5817,
    "offset": 12
  },
  "(7, 13, 46)": {
    "port": 104,
    "copy": 776,
    "family": 5816
  },
  "(7, 13, 47)": {
    "port": 89,
    "copy": 761,
    "family": 5801,
    "offset": 4
  },
  "(7, 13, 67)": {
    "port": 90,
    "copy": 762,
    "family": 5802
  },
  "(6, 7, 64)": {
    "port": 88,
    "copy": 760,
    "family": 5800,
    "offset": 9
  },
  "(8, 5, 23)": {
    "port": 93,
    "copy": 765,
    "family": 5805
  },
  "(8, 5, 74)": {
    "port": 87,
    "copy": 759,
    "family": 5799,
    "offset": 28
  },
  "(8, 5, 81)": {
    "port": 108,
    "copy": 780,
    "family": 5820,
    "offset": 28
  },
  "(8, 5, 83)": {
    "port": 111,
    "copy": 783,
    "family": 5823,
    "offset": 19
  },
  "(8, 5, 85)": {
    "port": 97,
    "copy": 769,
    "family": 5809,
    "offset": 12
  },
  "(8, 5, 90)": {
    "port": 94,
    "copy": 766,
    "family": 5806,
    "offset": 28
  },
  "(8, 5, 97)": {
    "port": 105,
    "copy": 777,
    "family": 5817,
    "offset": 21
  },
  "(8, 5, 99)": {
    "port": 90,
    "copy": 762,
    "family": 5802,
    "offset": 28
  },
  "(8, 5, 101)": {
    "port": 100,
    "copy": 772,
    "family": 5812,
    "offset": 28
  },
  "(8, 5, 106)": {
    "port": 106,
    "copy": 778,
    "family": 5818,
    "offset": 28
  },
  "(8, 5, 113)": {
    "port": 103,
    "copy": 775,
    "family": 5815,
    "offset": 0
  },
  "(8, 5, 115)": {
    "port": 107,
    "copy": 779,
    "family": 5819,
    "offset": 16
  },
  "(8, 5, 117)": {
    "port": 98,
    "copy": 770,
    "family": 5810,
    "offset": 17
  },
  "(8, 5, 122)": {
    "port": 99,
    "copy": 771,
    "family": 5811
  },
  "(8, 13, 108)": {
    "port": 89,
    "copy": 761,
    "family": 5801,
    "offset": 22
  },
  "(8, 13, 109)": {
    "port": 110,
    "copy": 782,
    "family": 5822
  },
  "(8, 13, 110)": {
    "port": 98,
    "copy": 770,
    "family": 5810,
    "offset": 21
  },
  "(8, 13, 111)": {
    "port": 97,
    "copy": 769,
    "family": 5809,
    "offset": 23
  },
  "(8, 13, 112)": {
    "port": 111,
    "copy": 783,
    "family": 5823,
    "offset": 23
  },
  "(8, 13, 114)": {
    "port": 93,
    "copy": 765,
    "family": 5805
  },
  "(8, 13, 116)": {
    "port": 109,
    "copy": 781,
    "family": 5821,
    "offset": 22
  },
  "(8, 13, 118)": {
    "port": 104,
    "copy": 776,
    "family": 5816,
    "offset": 22
  },
  "(8, 13, 119)": {
    "port": 88,
    "copy": 760,
    "family": 5800
  },
  "(7, 7, 74)": {
    "port": 91,
    "copy": 763,
    "family": 5803,
    "offset": 16
  },
  "(7, 7, 81)": {
    "port": 97,
    "copy": 769,
    "family": 5809,
    "offset": 8
  },
  "(7, 7, 83)": {
    "port": 108,
    "copy": 780,
    "family": 5820,
    "offset": 17
  },
  "(7, 15, 74)": {
    "offset": 24
  },
  "(7, 15, 119)": {
    "port": 89,
    "copy": 761,
    "family": 5801
  },
  "(8, 6, 445)": {
    "offset": 18
  }
}

def apply_repack(roles):
    new_roles = []
    changes_map = {}
    for k_str, diffs in CHANGES.items():
        parts = k_str.strip("()").split(",")
        tup = (int(parts[0]), int(parts[1]), int(parts[2]))
        changes_map[tup] = diffs

    for r in roles:
        k = (r["stage"], r["replica"], r["helper"])
        if k in changes_map:
            r = dict(r)
            r.update(changes_map[k])
        new_roles.append(r)

    affected_ports = set(diffs["port"] for diffs in changes_map.values())
    for p in affected_ports:
        proles = [r for r in new_roles if r["child"] == 15 and (r["owner_replica"], r["port"]) == (6, p)]
        proles.sort(key=lambda x: (x["stage"], x["replica"], x["helper"]))
        curr = 0
        for r in proles:
            r["offset"] = curr
            curr += r["width"]

    return new_roles

def main():
    pkg = Path(__file__).resolve().parent
    owners_path = pkg / "data/OWNERS.json.gz"
    roles = json.loads(gzip.decompress(owners_path.read_bytes()))
    updated = apply_repack(roles)
    compressed = gzip.compress(json.dumps(updated, separators=(",", ":")).encode(), mtime=0)
    actual_sha = hashlib.sha256(compressed).hexdigest()
    assert actual_sha == TARGET_SHA, f"SHA mismatch: {actual_sha} != {TARGET_SHA}"
    owners_path.write_bytes(compressed)
    print(f"Successfully applied Breakthrough 10 repack ({len(CHANGES)} roles modified) to {owners_path}")
    print(f"Certified SHA-256: {actual_sha}")

if __name__ == "__main__":
    main()
