"""Check the fixed-code projector on the pinned interface."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    source = args.source_root / "lanes/circuit-interface/INTERFACE.json"
    raw = source.read_bytes()
    require(sha256(raw).hexdigest() ==
            "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3",
            "The interface pin differs")
    data = json.loads(raw)
    r = [[F(row.get(str(j), 0)) for j in range(112)] for row in data["R"]]
    require(len(r) == 8, "The query row count differs")
    gram = [[sum(x*y for x, y in zip(a, b)) for b in r] for a in r]
    require(gram == [[56*int(i == j) for j in range(8)] for i in range(8)],
            "The query Gram differs")
    a = [[sum(row[i]*row[j] for row in r) for j in range(112)]
         for i in range(112)]
    p = [[F(i == j)-a[i][j]/56 for j in range(112)] for i in range(112)]
    require(all(p[i][j] == p[j][i] for i in range(112) for j in range(112)),
            "The projector is not symmetric")
    require(all(sum(r[k][i]*p[i][j] for i in range(112)) == 0
                for k in range(8) for j in range(112)), "The image is not in the kernel")
    # The Gram identity gives (R^T R)^2=56 R^T R and proves P^2=P.
    require(sum(p[i][i] for i in range(112)) == 104, "The code dimension differs")
    parent = list(range(112))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    edges = 0
    for i in range(112):
        for j in range(i):
            if p[i][j]:
                parent[root(i)] = root(j)
                edges += 1
    components = {}
    for i in range(112):
        components.setdefault(root(i), []).append(i)
    sizes = sorted(len(v) for v in components.values())
    require(sizes == [112], "The projector graph is not connected")
    require(0 < p[0][0] < 1, "The unequal-operator control is absent")
    leakage = (1-p[0][0])*p[0][0]
    require(leakage != 0, "A single-port scalar projection preserved the code")
    result = {
        "status": "PASS_FIXED_CODE_PROJECTOR_GRAPH",
        "interface_sha256": sha256(raw).hexdigest(),
        "query_gram": "56 I8", "code_dimension": 104,
        "component_sizes": sizes, "undirected_edges": edges,
        "single_port_operator_leakage_00": str(leakage),
        "scope": "Exact source application. The separate proof review proves the general operator-valued criterion.",
        "not_checked": ["Native phases", "Changing codes", "Joint array operators", "Recursive admission"],
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(result["status"])


if __name__ == "__main__":
    main()
