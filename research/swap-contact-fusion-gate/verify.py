"""Read-only, exact local retiming certificate. Apache-2.0; Codex assistance."""
from contextlib import redirect_stdout
from hashlib import sha256
from pathlib import Path
import argparse
import copy
import gzip
import io
import json
import sys
import types

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from contact_graph import Graph, certificate, dimension, interval_spaces, require, span, study


def load_source():
    inputs = HERE / "inputs"
    origins = json.loads((inputs / "ORIGINS.json").read_text())
    for row in origins:
        require(sha256((inputs / row["file"]).read_bytes()).hexdigest() == row["sha256"], "Exact retained input: " + row["file"])
    # Compile authenticated source bytes directly, avoiding preexisting bytecode.
    module = types.ModuleType("native_core")
    module.__file__ = str(inputs / "native_core.py")
    exec(compile((inputs / "native_core.py").read_bytes(), module.__file__, "exec"), module.__dict__)
    old_module = sys.modules.get("native_core")
    old_argv, old_path = sys.argv[:], sys.path[:]
    namespace = {"__file__": str(inputs / "verify.py"), "__name__": "retained_swap_replay"}
    try:
        sys.modules["native_core"] = module
        # The original --write switch must never receive this verifier's argv.
        sys.argv = [namespace["__file__"]]
        with redirect_stdout(io.StringIO()):
            exec(compile((inputs / "verify.py").read_bytes(), namespace["__file__"], "exec"), namespace)
    finally:
        sys.argv, sys.path = old_argv, old_path
        if old_module is None:
            del sys.modules["native_core"]
        else:
            sys.modules["native_core"] = old_module
    return namespace


def controls(canonical, program, graph):
    checks = []
    mutant = copy.deepcopy(program)
    warp = next(e for e in mutant if e[0] == "warp" and e[3] == e[4] == 0)
    warp[4] = 1
    try:
        Graph(canonical, mutant)
    except ValueError as error:
        require(str(error) == "Operator carries warp chart", "Specific operator/chart rejection")
        checks.append("zero_to_full_operator_mismatch")
    else:
        raise ValueError("Operator/chart mutation accepted")
    mutant = copy.deepcopy(program)
    swap = next(e for e in mutant if e[0] == "weighted_swap" and e[5][0] != e[5][1])
    swap[6] = swap[5][:]
    try:
        Graph(canonical, mutant)
    except ValueError as error:
        require(str(error) == "Swap carries charts", "Specific swap/frame rejection")
        checks.append("dropped_unequal_frame_carry")
    else:
        raise ValueError("Frame-carry mutation accepted")
    mutant_graph = copy.deepcopy(graph)
    edge = next(e for e in mutant_graph.edges if dimension(mutant_graph.labels[e[0]]) > 0)
    mutant_graph.labels[edge[1]] = span([])
    try:
        mutant_graph.validate()
    except ValueError:
        checks.append("broken_edge_containment")
    else:
        raise ValueError("Broken graph containment accepted")
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Regenerate only this package's RESULT.json")
    args = parser.parse_args()
    source = load_source()
    output = {"scope": "Exact at-most-two-region moment and adjacent identity-edge fusion gate; inherited physical maps, no new kappa.",
              "source_payload_sha256": source["V"].SOURCE_SHA, "orientations": {}}
    for direction in ("forward", "backward"):
        word, swaps, unequal = source["construct"](source["a"]["programs"][direction])
        graph = Graph(source["c"], word)
        require(dict(graph.histogram()) == source["res"][direction]["paid"], "Graph recount equals actual paid profile")
        result = study(graph)
        result.update(swaps=swaps, unequal_swaps=unequal, mutation_controls=controls(source["c"], word, graph))
        output["orientations"][direction] = result
    require(set(interval_spaces(span([]), span([1, 2]))) == {span([]), span([1]), span([2]), span([3]), span([1, 2])},
            "Complete interval includes noncoordinate quotient lines")
    for old, new in (([1, 1], [2, 0]), ([1], [0])):
        try:
            certificate(old, new)
        except ValueError:
            pass
        else:
            raise ValueError("Profitable or undercharged mutation accepted")
    output["additional_controls"] = ["noncoordinate_quotient_line", "profitable_fusion_rejected", "omitted_paid_rank_rejected"]
    # Exact integer premises used in PROOF.md's two derivative arguments.
    require(3**5 < 2**8 and 8 * 5**3 - 8**3 - 2 * 5**3 > 0, "Four/three/two logarithm bounds")
    require(2**23 < 5**10 and 23**3 > 11 * 10**3, "Five/four/three/two logarithm bounds")
    require(16 < 27 and 375 < 32768 and 5**15 * 27 < 2**42, "Negative endpoint derivatives")
    witnesses = {}
    for direction, result in output["orientations"].items():
        witnesses[direction] = {key: result.pop(key) for key in (
            "single_region_witnesses", "two_region_witnesses", "infeasible_identity_edge_fusions")}
    witness_bytes = json.dumps(witnesses, sort_keys=True, separators=(",", ":")).encode()
    output["witness_payload_sha256"] = sha256(witness_bytes).hexdigest()
    output = json.loads(json.dumps(output))
    path = HERE / "RESULT.json"
    witness_path = HERE / "WITNESSES.json.gz"
    if args.write:
        path.write_text(json.dumps(output, indent=2) + "\n")
        witness_path.write_bytes(gzip.compress(witness_bytes, mtime=0))
    else:
        require(output == json.loads(path.read_text()), "Committed exact result matches replay")
        require(witness_bytes == gzip.decompress(witness_path.read_bytes()), "Every exact witness matches replay")
    for direction, result in output["orientations"].items():
        print(direction, {k: v for k, v in result.items() if not k.endswith("witnesses") and k != "infeasible_identity_edge_fusions"})
    print("PASS_SWAP_CONTACT_FUSION_GATE no_new_kappa")


if __name__ == "__main__":
    main()
