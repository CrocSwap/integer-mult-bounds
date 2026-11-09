"""Bounded source/interface/administrative checks for the protected MOVE join.

Long physical evidence is separately labelled in VERIFICATION.md. No receipt
or finite matrix check is a proof of the complete multiplication theorem.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from argparse import ArgumentParser
from hashlib import sha256
import json
import tempfile
from types import SimpleNamespace

from move_sources import HERE, authenticate, need
from check_move import (AtomicMove, Code, Ordinary, S, controls, factorization_check,
                        ordinary_factory, source_boundary, source_matrix)
from check_wrapping import check as wrapping_check
from physical_hardware import check as hardware_check
from check_slices import reference_controls


def source_custody():
    count = authenticate()
    pins = json.loads((HERE / "REMOTE-SOURCE-TREES.json").read_text())
    canonical = {r["path"]: r["git_blob"] for r in json.loads((HERE/"SOURCES.json").read_text())["files"]}
    mono = {r["name"]: r["sha"] for r in pins["monomial"]["top"] if r["type"] == "file"}
    mono.update({"vendor/"+r["path"]: r["sha"] for r in pins["monomial"]["vendor"] if r["type"] == "blob"})
    leaf = {r["name"]: r["sha"] for r in pins["leaf"]["top"] if r["type"] == "file"}
    need(not pins["monomial"]["truncated"], "complete published monomial source subtree")
    for row in json.loads((HERE / "DEPENDENCIES.json").read_text())["files"]:
        origin = row["source_path"]
        if row["path"].startswith("vendor/monomial/"):
            need(row["commit"] == "7d1ff23714e6f9182c1d0ff9214f65def2f30e04", "public monomial pin")
            key = origin.removeprefix("research/current-coded-gaussian-monomial/")
            expected = mono[key]
        else:
            need(row["commit"] == "61edc4fe348f0aeadc82a3b642a802cbfb03aed8", "public leaf pin")
            key = origin.removeprefix("research/current-coded-gaussian-leaf/")
            expected = (canonical["research/physical-gaussian-leaf/"+key.removeprefix("vendor/leaf/")]
                        if key.startswith("vendor/leaf/") else leaf[key])
        need(row["git_blob"] == expected, "retrieved public/canonical source membership")
    return dict(retained_files=count, public_monomial=pins["monomial"]["commit"],
                public_leaf=pins["leaf"]["commit"])


def source_corruption_control():
    row = json.loads((HERE / "DEPENDENCIES.json").read_text())["files"][0]
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        copied = root / row["path"]
        copied.parent.mkdir(parents=True)
        copied.write_bytes((HERE / row["path"]).read_bytes()+b"\n# altered source\n")
        (root / "DEPENDENCIES.json").write_text(json.dumps({"files": [row]}))
        try:
            authenticate(root)
        except ValueError:
            return True
        raise ValueError("altered computational source accepted")


def factor_census():
    engine = AtomicMove(source_boundary()[0], ordinary_factory)
    result = {}
    for side in ("entry", "exit"):
        provider = getattr(engine, side)
        actions = [provider.engine.action(gate) for gate in provider.engine.recipe.word]
        late = sum(int(action[2]) for action in actions)
        early = len(actions)-late
        result[side] = dict(early=early, late=late, affine_gates=len(actions),
                            ordinary_calls_per_row_for_f_gt_one=4*early+12*late,
                            private_ports=provider.port_count)
    need(result["entry"] == dict(early=5, late=6, affine_gates=11,
         ordinary_calls_per_row_for_f_gt_one=92, private_ports=1878)
         and result["exit"] == dict(early=5, late=7, affine_gates=12,
         ordinary_calls_per_row_for_f_gt_one=104, private_ports=1878), "source factor and complete ordinary-call census")
    return result


def inventory_scaling_check():
    def larger_factory():
        return Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)),
                        SimpleNamespace(families=0), (Code((("unreachable",),), 0),), capacity=65)
    larger = AtomicMove(source_boundary()[0], larger_factory)
    need((larger.entry.port_count, larger.leaf.port_count, larger.exit.port_count, larger.port_count)
         == (1884, 349, 1884, 4118), "inventory depends on compiled ordinary register capacity")
    try:
        larger.bind([object() for _ in range(4106)], {}, None)
    except ValueError as error:
        need(str(error) == "exact fixed distinct whole-MOVE inventory", "undersized inventory fails at the exact inventory guard")
    else:
        raise ValueError("capacity-64 inventory accepted for capacity-65 template")
    return dict(ordinary_capacity=65, monomial_ports=1884, whole_move_ports=4118,
                undersized_4106_port_inventory_rejected=True,
                ordinary_numerical_admission_claim=False)


def evidence():
    custody = source_custody()
    columns, matrix = source_matrix()
    return dict(schema_version=1, source=source_boundary()[3], custody=custody,
                matrix=matrix, factorization=factorization_check(columns),
                controls=controls(columns), wrapper=wrapping_check(),
                hardware=hardware_check(S.codec.DenseTape),
                reference_join=reference_controls(),
                source_factor_census=factor_census(),
                inventory_scaling=inventory_scaling_check(),
                altered_source_rejected=source_corruption_control(), no_new_kappa=True,
                full_uninterrupted_physical_run_claim=False)


def main():
    ap = ArgumentParser()
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args()
    result = evidence()
    target = HERE / "SOURCE-RESULT.json"
    if args.emit:
        target.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n")
    else:
        wanted = json.loads(target.read_text())
        need(json.dumps(result, sort_keys=True, separators=(",", ":")) ==
             json.dumps(wanted, sort_keys=True, separators=(",", ":")), "complete canonical source receipt")
    print("PASS_CURRENT_CODED_ATOMIC_MOVE_SOURCE_AND_WRAPPER", json.dumps(dict(
        source_columns=result["matrix"]["columns"], retained_files=result["custody"]["retained_files"],
        wrapper_success_cases=len(result["wrapper"]["identity_cases"]),
        wrapper_rejection_cases=len(result["wrapper"]["rejection_cases"])), sort_keys=True))


if __name__ == "__main__":
    main()
