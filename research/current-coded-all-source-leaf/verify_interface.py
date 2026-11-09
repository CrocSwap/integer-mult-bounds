"""Physical metadata, source binding, inventory and primitive checks.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from argparse import ArgumentParser
import json
import tempfile
from types import SimpleNamespace

from all_leaf_sources import HERE, activate, authenticate, need
from check_catalog import controls
from check_child import HARDWARE
from check_view import check as header_check
from check_receipts import check as receipt_check
from selected_leaf import Move, PaidService
from source_catalog import bind_move, catalog
from ordinary import Ordinary
from macro_code import Code

S = activate()


def ordinary_factory(capacity):
    return lambda: Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)),
        SimpleNamespace(families=0), (Code((("unreachable",),), 0),), capacity=capacity)


def interfaces():
    entries = catalog()[1]
    triples = [next(t for t in entries.values() if t[1].rank == r) for r in range(1, 9)]
    need(all(PaidService(t[1]).port_count == 388 for t in triples), "all selected rank child inventories")
    move = Move(triples[1], ordinary_factory(64))
    larger = Move(triples[1], ordinary_factory(65))
    need(move.port_count == 4145 and larger.port_count == 4157,
         "whole source template retains factory-dependent inventory")
    need(Move.run is S.core.AtomicMove.run and Move.commit is S.core.AtomicMove.commit,
         "unchanged public whole-stage control")
    for triple in ((triples[1][2], triples[1][1], triples[1][0]), triples[1][:2]):
        try:
            bind_move(triple)
        except ValueError:
            pass
        else:
            raise ValueError("incomplete or nonchronological MOVE accepted")
    try:
        larger.bind([object() for _ in range(4145)], {}, None)
    except ValueError as error:
        need(str(error) == "complete source-dependent fixed MOVE inventory", "exact undersized inventory rejection")
    else:
        raise ValueError("smaller factory's port bill accepted")
    source = triples[1][1]
    paid = PaidService(source)
    work = [HARDWARE.Tape() for _ in range(388)]
    context = S.common.abi.BinaryContextPort(HARDWARE.Tape())
    field = S.common.abi.CodedPort(HARDWARE.Tape())
    failures = 0
    for grant, fields in ((work[:-1], {paid.owner:field}),
                          (work[:-1]+[work[0]], {paid.owner:field}),
                          (work, {paid.owner:S.common.abi.CodedPort(context.tape)}),
                          (work, {paid.owner:S.common.abi.CodedPort(work[0])}),
                          (work, {})):
        try:
            PaidService(source).bind(grant, fields, context)
        except ValueError:
            failures += 1
        else:
            raise ValueError("incorrect physical source child grant accepted")
    return dict(ranks_checked=8, child_ports=388, capacity64_move_ports=4145,
                capacity65_move_ports=4157, inventory_rejection=True,
                chronology_rejections=2, child_grant_rejections=failures,
                unchanged_protected_control=True, ordinary_numeric_admission_claim=False)


def corruption():
    row = json.loads((HERE/"DEPENDENCIES.json").read_text())["files"][0]
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); copy = root/row["path"]
        copy.parent.mkdir(parents=True)
        copy.write_bytes((HERE/row["path"]).read_bytes()+b"\n# altered source\n")
        (root/"DEPENDENCIES.json").write_text(json.dumps(dict(files=[row])))
        try:
            authenticate(root)
        except ValueError:
            return True
        raise ValueError("altered public source accepted")


def check():
    return dict(schema_version=1, retained_files=authenticate(),
                header=header_check(), source_controls=controls(),
                interface=interfaces(), hardware=HARDWARE.check(S.common.codec.DenseTape),
                saved_receipts=receipt_check(),
                altered_source_rejected=corruption(), no_new_kappa=True,
                complete_move_physical_replay_claim=False)


if __name__ == "__main__":
    parser = ArgumentParser(); parser.add_argument("--emit", action="store_true")
    args = parser.parse_args(); result = check(); target = HERE/"INTERFACE-RESULT.json"
    if args.emit:
        target.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n")
    else:
        need(json.dumps(result, sort_keys=True) == json.dumps(json.loads(target.read_text()), sort_keys=True),
             "exact physical metadata and interface receipt")
    print("PASS_CURRENT_CODED_ALL_SOURCE_INTERFACE", json.dumps(dict(
        retained_files=result["retained_files"], header_cases=len(result["header"]["cases"]),
        all_ranks=True, physical_ports=388), sort_keys=True))
