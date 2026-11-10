"""Bounded source join, actual construction, geometry and protection checks.

Long complete-MOVE attempts are separately labelled manual evidence.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from argparse import ArgumentParser
from dataclasses import replace
from hashlib import sha256
import json
import tempfile

from direct_sources import HERE, activate, authenticate, load, need
from direct_move import DirectMove
from check_move import HARDWARE, EVENT, factory, fixture, encode_header, put, Ordinary
from check_protection import check as protection_check

S = activate()


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",", ":"))


def source_join():
    need(S.common.shared.engine.Count is S.common.leaf.coefficient.Count
         is S.common.shared.source.counts.Count,
         "one identical current encoded Count class")
    need(S.common.shared.engine.Tape is S.common.leaf.coefficient.Tape
         is S.common.shared.source.records.Tape,
         "one identical virtual physical Tape class")
    serial_state = S.serial.__init__.__globals__["S"]
    child_state = S.child.__init__.__globals__["S"]
    need(serial_state.codec is child_state.common.codec is S.common.codec
         and serial_state.abi is child_state.common.abi is S.abi,
         "one identical coded-word codec and physical port ABI")
    proof = load("direct_move_independent_clifford_check", HERE/"vendor/leaf/clifford_certificate.py")
    word, entries, pairs, report = S.catalog.catalog()
    frozen = json.loads((HERE/"vendor/leaf/CATALOG-RESULT.json").read_text())
    need(canonical(report) == canonical(frozen["source"])
         and len(frozen["source_certificates"]) == len(pairs) == 2886,
         "unchanged complete finite source family and inherited certificate")
    checked = []
    for rank in range(1, 9):
        triple = next(t for t in entries.values() if t[1].rank == rank)
        actual, original, record = S.catalog.bind_move(triple)
        proof.certify(original, record)
        engine = DirectMove(actual, factory)
        need(engine.rank == rank and engine.owner == actual[1].fields[0]
             and engine.entry.native.rank == engine.exit.native.rank == 9
             and engine.child.view.rank == rank and engine.port_count == 4235,
             "all actual rank interfaces and complete concrete inventory")
        for side, key in ((engine.entry, "right"), (engine.exit, "left")):
            recipe = side.native.engine.recipe
            need(tuple(recipe.matrix) == tuple(record[key]["matrix_rows"])
                 and tuple(recipe.linear) == tuple(record[key]["linear_Z4"])
                 and recipe.offset == record[key]["offset"]
                 and recipe.constant == record[key]["phase"], "exact source orientation and phase")
        checked.append(dict(rank=rank, source_event=actual[1].token[1], owner=engine.owner, private_ports=engine.port_count))
    return dict(retained_public_files=authenticate(), shared_serial_dependencies=109,
                source_report=report, rank_representatives=checked,
                fresh_matrix_certificates=8, inherited_complete_chart_certificates=2886,
                full_family_matrix_rerun_claim=False, identical_Count_Tape_codec=True)


def interfaces():
    triple, header, initial, expected = fixture()
    engine = DirectMove(triple, factory)
    work = [HARDWARE.Tape(3+j % 5) for j in range(engine.port_count)]
    field, context = HARDWARE.Tape(9), HARDWARE.Tape(11)
    put(field, initial); put(context, encode_header(header))
    context_port = S.abi.BinaryContextPort(context)
    fields = {engine.owner:S.abi.CodedPort(field)}
    engine.bind(work, fields, context_port)
    need(engine.entry.field.tape is engine.stage.tape is engine.exit.field.tape
         and engine.entry.view.parent.tape is context
         and engine.child.parent.tape is context
         and engine.exit.view.parent.tape is context,
         "all factors use the same protected stage and unchanged parent")
    cohorts = (*engine.entry.work, *engine.child.work, *engine.exit.work)
    need(len(cohorts) == len(set(map(id,cohorts))) == engine.port_count-1
         and all(t is not work[0] for t in cohorts), "complete disjoint three-factor partition")
    larger = DirectMove(triple, lambda:factory(65))
    need(larger.port_count == 4247, "factory-dependent actual fixed inventory")
    grants = ((work[:-1], fields, context_port),
              (work[:-1]+[work[0]], fields, context_port),
              (work, {engine.owner:S.abi.CodedPort(context)}, context_port),
              (work, {engine.owner:S.abi.CodedPort(work[0])}, context_port),
              (work, {}, context_port))
    rejected = 0
    for grant, owners, parent in grants:
        try:
            DirectMove(triple, factory).bind(grant, owners, parent)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("bad direct source grant accepted")
    try:
        larger.bind(work, fields, context_port)
    except ValueError:
        rejected += 1
    else:
        raise ValueError("smaller constructor inventory accepted")
    middle = triple[1]
    raw_alias = tuple(int(x) if type(x) is bool else x for x in middle.token[2])
    variants = [triple[::-1], triple[:2]]
    for wrong in (replace(middle, rank=True), replace(middle, fields=(middle.fields[0]+1,)),
                  replace(middle,token=("local",middle.token[1],raw_alias)),
                  replace(middle,token=("caller-local",0,0,middle.token))):
        variants.append((triple[0], wrong, triple[2]))
    for wrong in variants:
        try:
            DirectMove(wrong, factory)
        except ValueError:
            pass
        else:
            raise ValueError("wrong typed whole source event accepted")
    original = Ordinary.run; detected = [0]
    def trap(*args, **kwargs):
        detected[0] += 1
        raise ValueError("ordinary-runtime-entry-trap")
    Ordinary.run = trap
    try:
        try:
            factory().run(None,None,None)
        except ValueError as error:
            need(str(error) == "ordinary-runtime-entry-trap", "ordinary runtime entry detector")
        else:
            raise ValueError("ordinary entry detector did not fire")
    finally:
        Ordinary.run = original
    return dict(concrete_ports=4235, capacity65_ports=4247, grant_rejections=rejected,
                typed_source_rejections=len(variants), ordinary_entry_detector=detected == [1],
                original_input_sha256=sha256(bytes(initial)).hexdigest(),
                independent_expected_sha256=sha256(bytes(expected)).hexdigest(),
                actual_full_numerical_replay_claim=False)


def source_corruption():
    row = next(r for r in json.loads((HERE/"DEPENDENCIES.json").read_text())["files"]
               if r["path"] == "vendor/serial/column_view.py")
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder); path = root/row["path"]; path.parent.mkdir(parents=True)
        path.write_bytes((HERE/row["path"]).read_bytes()+b"\n# altered\n")
        (root/"DEPENDENCIES.json").write_text(json.dumps(dict(files=[row])))
        (root/"SHARED-SOURCE-JOIN.json").write_text(json.dumps(dict(files=[])))
        try:
            authenticate(root)
        except ValueError:
            return True
        raise ValueError("changed serial computational bytes accepted")


def check():
    return dict(schema_version=1, source=source_join(), interface=interfaces(),
                protected_return_contract=protection_check(),
                hardware=HARDWARE.check(S.common.codec.DenseTape),
                source_corruption_rejected=source_corruption(), no_new_kappa=True,
                complete_actual_MOVE_executed_by_this_gate=False)


if __name__ == "__main__":
    parser = ArgumentParser(); parser.add_argument("--emit", action="store_true")
    args = parser.parse_args(); result = check(); path = HERE/"RESULT.json"
    if args.emit:
        path.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    else:
        need(canonical(result) == canonical(json.loads(path.read_text())), "exact source/interface/protection receipt")
    print("PASS_CURRENT_DIRECT_SOURCE_MOVE", json.dumps(dict(
        concrete_ports=result["interface"]["concrete_ports"],
        source_occurrences=result["source"]["source_report"]["raw_moves"],
        model_return_cases=len(result["protected_return_contract"]["cases"]),
        numeric_whole_replay=False),sort_keys=True))
