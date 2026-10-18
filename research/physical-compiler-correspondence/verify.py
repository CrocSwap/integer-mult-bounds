"""Source-bound compiler ordering audit. Run with isolated bytecode imports."""

import json
import sys
from dataclasses import replace
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = ROOT / "research/selected-bit-physical-caller"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    require(1 <= len(sources["files"]) <= 200, "bounded source inventory")
    for row in sources["files"]:
        if row["usage"] == "input":
            data = (ROOT / row["path"]).read_bytes()
            require(
                sha256(data).hexdigest() == row["sha256"],
                "changed input: " + row["path"],
            )


def load():
    authenticate()
    sys.path.insert(0, str(PREDECESSOR))
    import loader

    loader.activate()  # Authenticates complete snapshots and repository dependencies.
    sys.path.insert(0, str(HERE))
    import semantics
    from macro_code import compile_node

    return semantics, compile_node


def mutation_controls(s, compile_node):
    topology = s.Topology(1)
    code = compile_node(topology, s.Binding())
    reference = s.logical(topology)
    operations = code.operations
    bridge = next(i for i, op in enumerate(operations) if op[0] == "family_xor")
    exchange = next(i for i, op in enumerate(operations) if op[0] == "exchange")
    copy = next(i for i, op in enumerate(operations) if op[0] == "copy")
    xors = [i for i, op in enumerate(operations) if op[0] == "xor"]
    require(xors[1] == xors[0] + 1, "fixture has cancelling private XORs")
    backwards = ("family_xor", operations[bridge][2], operations[bridge][1])
    candidates = {
        "omit_bridge": operations[:bridge] + operations[bridge + 1 :],
        "reverse_bridge": operations[:bridge] + (backwards,) + operations[bridge + 1 :],
        "omit_exchange": operations[:exchange] + operations[exchange + 1 :],
        "omit_copy": operations[:copy] + operations[copy + 1 :],
        "omit_cancelling_private_xors": tuple(
            op for i, op in enumerate(operations) if i not in xors[:2]
        ),
    }
    results = {}
    for label, candidate in candidates.items():
        try:
            actual = s.compiled(topology, replace(code, operations=candidate))
        except (ValueError, KeyError):
            results[label] = "rejected_at_boundary"
            continue
        require(actual != reference, "semantic defect escaped: " + label)
        results[label] = {key: actual[key] == reference[key] for key in reference}
    invisible = results["omit_cancelling_private_xors"]
    require(
        isinstance(invisible, dict)
        and invisible["final"]
        and invisible["cuts"]
        and invisible["residuals"]
        and not invisible["xors"],
        "private transient defect is invisible at every global endpoint",
    )
    return results


def admission_controls(s, compile_node):
    class DuplicateOwner(s.Topology):
        def call(self, stage, replica):
            original = super().call(stage, replica)
            return replace(
                original,
                owners=(original.owners[0], original.owners[0], *original.owners[2:]),
            )

    duplicate = DuplicateOwner(1)
    duplicate.schedule = ({"kind": "local_cover_sweep", "stage": 0},)
    bridge = s.Topology(1)
    bridge.schedule = ({"kind": "bridge", "dst": 0, "src": 0, "coefficient": 1},)
    results = {}
    for label, topology, expected in (
        ("duplicate_owner", duplicate, "disjoint complete owned low packets"),
        ("self_bridge", bridge, "native bridge scalar"),
    ):
        code = compile_node(topology, s.Binding())
        require(len(code.operations) > 2, "compiler materializes the inadmissible word")
        try:
            s.logical(topology)
        except ValueError as error:
            require(
                str(error) == expected, "source rejects at the named admission guard"
            )
            results[label] = {
                "compiled_instructions": len(code.operations),
                "source_rejection": str(error),
            }
            continue
        raise ValueError("source guard did not reject: " + label)
    return results


def run():
    s, compile_node = load()
    cases = []
    for reverse_lows in (False, True):
        for replicas in (1, 2):
            for reverse in (False, True):
                topology = s.Topology(replicas, reverse, reverse_lows)
                code = compile_node(topology, s.Binding())
                require(
                    len(code.operations) < 40000, "bounded complete compiled fixture"
                )
                reference = s.logical(topology)
                actual = s.compiled(topology, code)
                require(actual == reference, "compiler differs from source chronology")
                cases.append(
                    {
                        "q": 3,
                        "replicas": replicas,
                        "reverse_schedule": reverse,
                        "reverse_lows": reverse_lows,
                        "instructions": len(code.operations),
                        "global_cuts": len(actual["cuts"]),
                        "residuals": len(actual["residuals"]),
                        "xors": len(actual["xors"]),
                        "symbolic_input_bits": 4
                        * topology.families
                        * topology.catalogue.codes.size,
                        "semantic_sha256": s.fingerprint(actual),
                    }
                )
    import owners

    return {
        "status": "PASS_PHYSICAL_COMPILER_CORRESPONDENCE",
        "cases": cases,
        "controls": mutation_controls(s, compile_node),
        "admission": admission_controls(s, compile_node),
        "selected_owners": owners.run(),
        "scope": "Whole-word ordering and selected all-low owner separation; not tape or residual refinement",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
