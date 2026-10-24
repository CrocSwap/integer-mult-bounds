"""Source-bound global chart optimum. Apache-2.0; substantial Codex assistance."""
import argparse
from collections import Counter
import copy
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = ROOT / "research/swap-contact-fusion-gate"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compile_module(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def authenticated_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    for row in inputs:
        require(sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                "Exact source pin: " + row["path"])
    original_path = sys.path[:]
    old_module = sys.modules.get("contact_graph")
    try:
        graph_module = compile_module(PREDECESSOR / "contact_graph.py", "contact_graph")
        sys.modules["contact_graph"] = graph_module
        loader = compile_module(PREDECESSOR / "verify.py", "retained_graph_loader")
        # The retained loader authenticates all six ORIGINS entries, compiles
        # native_core directly, removes --write and reruns the original source
        # endpoint/frame/paid-profile checks. It does not run PR4997's census.
        source = loader.load_source()
    finally:
        sys.path[:] = original_path
        if old_module is None:
            sys.modules.pop("contact_graph", None)
        else:
            sys.modules["contact_graph"] = old_module
    return source, graph_module.Graph, {row["path"]: row["sha256"] for row in inputs}


def coefficient_checks(optimizer):
    width = 10
    def vector(values):
        return tuple(values) + (0,) * (width - len(values))
    def curvature(k):
        return tuple(2 * int(r == k) - int(r == k-1) - int(r == k+1) for r in range(width))
    b = vector((-4, 12, -8, -4, 4))
    e = vector((-4, 12, -8, -8, 12, -4))
    f = vector((-4, 7, -3, 5, -9, 4))
    require(e == tuple(x + 4*y for x, y in zip(b, curvature(4))), "E = B + 4 C4")
    require(f == tuple(4*a+b+c-4*d for a,b,c,d in zip(curvature(1),curvature(2),curvature(3),curvature(4))),
            "F = 4(C1-C4) + C2 + C3")
    # Exact premises of the inherited B,D derivative proofs. The calculus
    # arguments and the two new identities are written out in PROOF.md.
    require(3**5 < 2**8 and 8*5**3 - 8**3 - 2*5**3 > 0, "B derivative sign")
    require(2**23 < 5**10 and 23**3 > 11*10**3, "D derivative sign")
    require(16 < 27 and 375 < 32768 and 5**15 * 27 < 2**42, "Negative endpoint derivatives")
    for shape, name in optimizer.POWER_CERTIFICATES.items():
        difference = vector(shape)
        old = tuple(max(-x, 0) for x in difference)
        new = tuple(max(x, 0) for x in difference)
        require(optimizer.certify(old, new) == name, "Registered inequality has its exact coefficient vector")
        require(optimizer.certify(new, old) is None, "Reverse strict inequality is rejected")
    return ["two_new_coefficient_identities", "inherited_derivative_integer_premises", "five_inequality_directions"]


def controls(optimizer, source, Graph):
    passed = []
    def rejects(name, operation):
        try:
            operation()
        except ValueError:
            passed.append(name)
        else:
            raise ValueError("Control was accepted: " + name)
    identity = (1, 2)
    rejects("nonbinary_interval", lambda: optimizer.solve({0:1,1:3,2:15}, {0,2}, [(0,1,identity),(1,2,identity)], 2))
    rejects("noninvertible_map", lambda: optimizer.solve({0:1,1:3,2:15}, {0,2}, [(0,1,(1,1)),(1,2,identity)], 2))
    rejects("invalid_source_chart", lambda: optimizer.solve({0:5,1:3,2:15}, {0,2}, [(0,1,identity),(1,2,identity)], 2))
    rejects("omitted_owned_edge", lambda: optimizer.certify((1,0,1), (0,1,0)))
    rejects("changed_rank_mass", lambda: optimizer.certify((1,0,1), (0,1,1)))
    require(optimizer.certify((1,0,1),(0,2,0)) == "majorization", "Strict concavity positive control")
    require(optimizer.certify((0,2,0),(1,0,1)) is None, "Profitable fusion cannot be certified as a loss")
    passed.append("reversed_profitable_fusion")
    # Source-binding regression, credited to the #4571/#4979/#4997 lineage.
    word, _, _ = source["construct"](source["a"]["programs"]["forward"])
    mutant = copy.deepcopy(word)
    index = next(i for i,event in enumerate(mutant) if event[0] == "warp" and event[3:5] == [0,0])
    mutant[index][4] = 1
    rejects("false_native_image_label", lambda: Graph(source["c"],mutant))
    return passed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Regenerate only this package's receipt and witnesses")
    args = parser.parse_args()
    optimizer = compile_module(HERE / "optimizer.py", "global_region_optimizer")
    oracle = compile_module(HERE / "oracle_checks.py", "independent_small_graph_oracle")
    source, Graph, source_hashes = authenticated_sources()
    result = {
        "claim": "Global optimum for the fixed-boundary intact-region model, every 0<t<1; no new kappa.",
        "source_payload_sha256": source["V"].SOURCE_SHA,
        "input_sha256": source_hashes,
        "proof_and_code_sha256": {name:sha256((HERE/name).read_bytes()).hexdigest() for name in
                                   ("PROOF.md","optimizer.py","oracle_checks.py","verify.py")},
        "orientations": {},
        "power_inequality_checks": coefficient_checks(optimizer),
        "rejection_controls": controls(optimizer,source,Graph),
        "independent_small_graph_oracle": oracle.run_checks(optimizer.solve),
    }
    witnesses = {}
    for direction in ("forward","backward"):
        word, swaps, unequal = source["construct"](source["a"]["programs"][direction])
        graph = Graph(source["c"], word)
        require(dict(graph.histogram()) == source["res"][direction]["paid"], "Literal graph equals full source invoice")
        groups, roots = graph.regions()
        labels = {root:graph.labels[nodes[0]] for root,nodes in groups.items()}
        require(all(graph.labels[node] == labels[root] for root,nodes in groups.items() for node in nodes),
                "Intact source regions have one chart")
        fixed = {root for root,nodes in groups.items() if any(graph.fixed[node] for node in nodes)}
        edges = [(roots[u],roots[v],matrix) for u,v,matrix in graph.edges]
        solved = optimizer.solve(labels,fixed,edges,9)
        original_histogram = list(optimizer.histogram(labels,edges,9))
        require(solved["histogram"] == original_histogram, "Global optimum equals source histogram")
        paid = Counter({rank:count for rank,count in enumerate(solved["histogram"]) if rank and count})
        paid.update(graph.centers)
        require(dict(paid) == dict(graph.histogram()), "All centers and strand charges retained")
        result["orientations"][direction] = {
            **solved["stats"], "original_nodes":len(graph.labels),
            "swaps":swaps, "unequal_swaps":unequal,
            "strand_histogram_including_zero":original_histogram,
            "center_histogram":dict(sorted(graph.centers.items())),
            "complete_paid_histogram":dict(sorted(paid.items())),
            "fixed_charts_preserved":True,
            "source_chart_assignment_attains_global_minimum":True,
        }
        witnesses[direction] = {
            "bounds": {node:[list(optimizer.basis(lo)),list(optimizer.basis(hi))]
                       for node,(lo,hi) in sorted(solved["bounds"].items())},
            "minimizing_assignment": {node:list(optimizer.basis(space)) for node,space in sorted(solved["assignment"].items())},
            "elimination":solved["trace"],
        }
    witness_bytes = json.dumps(witnesses,sort_keys=True,separators=(",",":")).encode()
    result["witness_payload_sha256"] = sha256(witness_bytes).hexdigest()
    result = json.loads(json.dumps(result))
    receipt, witness_file = HERE/"RESULT.json", HERE/"WITNESSES.json.gz"
    if args.write:
        receipt.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
        witness_file.write_bytes(gzip.compress(witness_bytes,mtime=0))
    else:
        require(result == json.loads(receipt.read_text(encoding="utf-8")), "Exact committed result")
        require(witness_bytes == gzip.decompress(witness_file.read_bytes()), "Every bound and elimination certificate")
    for direction, summary in result["orientations"].items():
        print(direction,json.dumps(summary,sort_keys=True))
    print("oracle",json.dumps(result["independent_small_graph_oracle"],sort_keys=True))
    print("PASS_GLOBAL_INTACT_REGION_OPTIMUM no_new_kappa")


if __name__ == "__main__":
    main()
