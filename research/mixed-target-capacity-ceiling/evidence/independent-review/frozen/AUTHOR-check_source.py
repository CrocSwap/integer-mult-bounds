#!/usr/bin/env python3
"""Only authenticate and inspect retained scalar source tables; no operators."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
    "outputs/released-operator-intersection-20261023/frozen/CODE.json":
        "8be7f3f073b7981ec91c6af43edff0ac8a89f4824ef6026ae758c287dd6c03d0",
    "outputs/released-operator-intersection-20261023/frozen/NORMALIZERS.json":
        "ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    files = []
    data = []
    for name, expected in EXPECTED.items():
        payload = (ROOT / name).read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if expected is not None:
            require(digest == expected, "Pinned source hash changed: " + name)
        files.append({"path": name, "sha256": digest})
        data.append(json.loads(payload))
    a = data[0]["A"]
    ports = data[1]["ports"]
    modes = data[1]["mode_columns"]
    require(len(a) == len(ports) == 112, "Owner count changed")
    require(all(len(row) == 112 for row in a), "Code shape changed")
    require(len(modes) == 8 and all(len(c) == 112 for c in modes),
            "Mode shape changed")
    require([p["port"] for p in ports] == list(range(112)), "Port order changed")
    edges = [(i, j) for i in range(112) for j in range(112) if a[i][j] != "0"]
    bad = [(i, j) for i, j in edges
           if (ports[i]["q"] & ports[j]["q"]).bit_count() % 2]
    require(len(edges) == 5824 and not bad, "Supported-edge orthogonality failed")
    require(len({p["q"] for p in ports}) == 112, "Distinct direction property failed")
    gram = [[sum(modes[i][k] * modes[j][k] for k in range(112))
             for j in range(8)] for i in range(8)]
    require(gram == [[56 * int(i == j) for j in range(8)] for i in range(8)],
            "Mode Gram identity failed")
    result = {
        "status": "PASS_SOURCE_ONLY_DOT_AND_MODE_FACTS",
        "scientific_pin": "4c0a359d88f22f05189d51f48387750b801a45d4",
        "ports": len(ports), "nonzero_A_edges": len(edges),
        "nonorthogonal_nonzero_A_edges": len(bad),
        "distinct_q": len({p["q"] for p in ports}), "mode_gram": gram,
        "source_files": files,
        "scope": "Reads existing finite scalar A, source q masks and eight mode columns only. "
                 "No operator evaluation, solver, native/emitter/compiler/Lean execution, "
                 "candidate enumeration or moment numerics.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
