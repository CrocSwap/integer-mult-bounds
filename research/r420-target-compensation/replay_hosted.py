"""Fresh native, nine-stage, hosted and invoice replay of the changed bit word.

Requires SymPy 1.14, a C++17 compiler and Boost headers. No optimizer or network.
Apache-2.0; prepared with substantial OpenAI Codex assistance.
"""

import argparse
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import HERE, ROOT, need
from verify import pins


def invoice_detail(adds, prefix, hosted, global_receipt, geometry):
    """Expand every term of the pinned assemble9.py finite invoice using ints."""
    m, stages, replicas, helpers = 64, 9, 32, 420
    live, physical, depth = hosted["live"], hosted["physical"], 2
    paid = sum(hosted["profile"].values())
    episodes = global_receipt["copy_erase_episodes"]
    operations = stages * replicas * adds + global_receipt["bridge_additions"]
    events = (8 * replicas * stages * (240 + helpers) + 8 * (8 * 120 * replicas)
              + 2 * stages * replicas * helpers + 2 * episodes)
    selectors = 2 * stages * replicas * (
        live - 1 + helpers * m * (geometry["max_route_factors"] + 144 + 2 + m - 1 + m))
    terms = {
        "local_and_bridge_adds": operations,
        "high_level_routing": events * 16 * (m * m + 1) ** 2,
        "physical_row_routing": events * physical,
        "good_calls_and_compiler": paid * (8 * m * m + 8 + 128 * (2 * m) ** 3),
        "fixed_setup": 16 * m ** 3,
        "copy_erase_episodes": episodes,
        "selectors": selectors,
        "prefix": prefix,
        "constant": 1,
    }
    coefficient = sum(terms.values())
    two = (coefficient + 1) ** depth * (paid + 1) ** depth
    return {"terms": {k: str(v) for k, v in terms.items()},
            "coefficient": str(coefficient), "coefficient_bits": coefficient.bit_length(),
            "two_level_coefficient": str(two), "two_level_bits": two.bit_length()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="fresh directory; default: unique directory under build/")
    parser.add_argument("--cxx", default="c++")
    parser.add_argument("--write-certificate", action="store_true", help="create a missing hosted certificate")
    args = parser.parse_args()
    need(not sys.flags.optimize, "assertions must be enabled")
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    except ImportError:
        pass
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    pins(manifest)
    if args.output:
        out = args.output.resolve()
        out.mkdir(parents=True, exist_ok=False)
    else:
        (ROOT / "build").mkdir(exist_ok=True)
        out = Path(tempfile.mkdtemp(prefix="r420-compensation-hosted-", dir=ROOT / "build"))
    (out / "logs").mkdir()
    (out / "bin").mkdir()
    (out / "tmp").mkdir()
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(out / "tmp"),
                       OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    commands = []

    def run(label, command, expected_error=None):
        command = [str(x) for x in command]
        commands.append({"label": label, "argv": command, "expected_error": expected_error})
        (out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        with (out / "logs" / (label + ".log")).open("w") as log:
            proc = subprocess.run(command, cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT)
        need((proc.returncode != 0) if expected_error else (proc.returncode == 0),
             f"{label}: unexpected exit {proc.returncode}; see {out / 'logs' / (label + '.log')}")
        if expected_error:
            need(expected_error in (out / "logs" / (label + ".log")).read_text(),
                 label + ": did not reject for the intended reason")
        print(("REJECT " if expected_error else "PASS ") + label, flush=True)

    def python(label, script, *arguments):
        run(label, [sys.executable, "-E", "-s", "-B", script, *arguments])

    def read(path):
        return json.loads(path.read_text())

    predecessor = ROOT / "research/e8-bit-carrier-skeleton"
    bit = predecessor / "code/bit"
    checkers = bit / "checkers"
    pricing = ROOT / "research/e8-bit-r420/vendor/pr510/e8-r480-nine-stage"
    vk = pricing / "vendor/e8-r715-eleven-stage-whole/code"
    local = out / "local"
    python("native", HERE / "verify.py", "--output", local)
    word = local / "word.json.gz"
    python("export", bit / "export_records.py", word, local / "records")
    python("stage", bit / "regression/stage_cohort.py", local / "records", local / "records",
           local / "cin", local / "cout")
    compile_flags = ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9", "-DVPORTS=120", "-DRHELP=420"]
    run("compile-legality", [args.cxx, *compile_flags, checkers / "legality_h.cpp", "-o", out / "bin/legality"])
    for k in (2, 4):
        run(f"compile-columns{k}", [args.cxx, *compile_flags, f"-DKPAIRS={k}", checkers / "columns_k.cpp",
                                     "-o", out / f"bin/columns{k}"])
    run("legality", [out / "bin/legality", local / "cin", local / "cout", local / "cout/legality.json"])
    records = local / "cout/COHORT249-RECORDS.bin"
    run("five-stage", [out / "bin/columns2", records, local / "cout/columns.json"])
    run("nine-stage", [out / "bin/columns4", records, local / "cout/columns_k4.json"])
    native = read(local / "report.json")
    legality = read(local / "cout/legality.json")
    nine = read(local / "cout/columns_k4.json")
    five = read(local / "cout/columns.json")
    need(legality["common_frame_ADDs"] == nine["local_scalar_additions"] == native["candidate_bill"]["total_adds"],
         "C++ addition census disagreement")
    need(legality["rank_mass"] == 5112 and dict(nine["local_raw_H"]) ==
         {int(k): v for k, v in native["geometry"]["paid_profile"].items()}, "C++ recursive profile disagreement")
    need(nine["formal_columns_checked"] == 1380 and five["formal_columns_checked"] == 900,
         "C++ formal-column coverage")
    need(len(nine["negative_controls"]) == 18 and all(c["rejected"] for c in nine["negative_controls"]),
         "nine-stage omitted-bridge controls")
    for item, key in zip(nine["signed_lift_prefix"], ("forward", "reverse")):
        need(int(item["cancellation_free_signed_row_l1_upper"]) == native["candidate_bill"][key],
             "C++ prefix disagreement")
    need(nine["payload_prefix_upper"] == native["candidate_bill"]["five_stage_prefix"],
         "C++ five-stage formula disagreement")

    # Detect errors in the serialized stream, not only in the word interpreter.
    raw = list(struct.iter_unpack("<6i", records.read_bytes()))
    first_basis = next(i for i, row in enumerate(raw) if row[0] == 1 and row[5] == 1)
    first_helper = next(i for i, row in enumerate(raw) if row[0] == 1 and row[5] == 1 and row[2] >= 240)
    first_copy = next(i for i, row in enumerate(raw) if row[0] == 2)
    first_move = next(i for i, row in enumerate(raw) if row[0] == 0 and row[4] > 0)
    mutations = []
    for name, index in (("omit-basis-add", first_basis), ("omit-helper-add", first_helper), ("omit-copy", first_copy)):
        path = out / (name + ".bin")
        path.write_bytes(b"".join(struct.pack("<6i", *row) for i, row in enumerate(raw) if i != index))
        reason = "bounderase" if name == "omit-copy" else "local defining-decoder full formal column"
        run(name, [out / "bin/columns4", path, out / (name + ".json")], expected_error=reason)
        mutations.append(name)
    mutated = [list(row) for row in raw]
    mutated[first_move][4] -= 1
    directory = out / "understated-move"
    directory.mkdir()
    for name in ("COHORT249-FRAMES.json", "COHORT249-INITIAL.json", "COHORT249-SELECTION.json"):
        shutil.copyfile(local / "cout" / name, directory / name)
    (directory / "COHORT249-RECORDS.bin").write_bytes(b"".join(struct.pack("<6i", *row) for row in mutated))
    run("understated-move", [out / "bin/legality", local / "cin", directory, directory / "receipt.json"],
        expected_error="illegal or mispriced MOVE")
    mutations.append("understated-move")

    python("geometry", predecessor / "code/nine/geometry.py", "--source", predecessor, "--out", local / "nine")
    python("global", vk / "global_k.py", "--word", word, "--local-check", local, "--out", local / "nine",
           "--isometries", predecessor / "data/eleven/residual-isometries.json")
    python("adapt-audit", pricing / "code/adapt.py", vk, out / "adapted")
    python("parent-audit", out / "adapted/audit_parent_k.py", "--local-check", local,
           "--out", local / "nine", "--word", word)
    python("host", vk / "emit_k.py", local / "nine", local, local / "hosted",
           "--selection", ROOT / "research/e8-bit-r420/data/selection9-r420.json", "--key", "bit")
    python("host-audit", vk / "audit_hosted_k.py", local, local / "hosted", local / "hosted/AUDIT.json")

    # The complex lower bound is a pinned input from the selected certificate,
    # not a claim to have rebuilt the complex supplier in this bit-only replay.
    selected = read(ROOT / "research/community-k492-audit/pr626/replay/ASSEMBLY.json")
    assembly_root = out / "assembly-input"
    engines = Path("code/hub/e8-r740-replica32/code/engines")
    (assembly_root / engines).mkdir(parents=True)
    for name in ("moment.py", "base_two_moment.py", "outer.py"):
        shutil.copyfile(predecessor / engines / name, assembly_root / engines / name)
    (assembly_root / "data").mkdir()
    (assembly_root / "data/complex-b.json").write_text(json.dumps({
        "suppliers": [{"name": "selected626", "b": selected["complex_lower"]}]}) + "\n")
    python("invoice", pricing / "code/assemble9.py", local, local / "hosted", local / "hosted/AUDIT.json",
           assembly_root, out / "INVOICE.json", "selected626")
    global_receipt = read(local / "nine/GLOBAL.json")
    parent = read(local / "nine/AUDIT.json")
    hosted = read(local / "hosted/AUDIT.json")
    invoice = read(out / "INVOICE.json")
    expected = read(ROOT / "research/e8-bit-r420/EXPECTED.json")
    need(invoice["bit_profile"] == expected["nine"]["profile"], "hosted paid profile changed")
    need(invoice["bit_lower"] == selected["bit_lower"], "bit saving changed")
    need(invoice["kappa"]["selected626"]["kappa"] == selected["kappa"], "selected assembly not reproduced")
    need(invoice["bit"]["charged_prefix_bits"] == 192 and
         invoice["bit"]["charged_two_level_coefficient_bits"] == 512, "invoice allowance increased")
    need(global_receipt["global_prefix_bound"] == native["candidate_bill"]["nine_stage_prefix"],
         "global nine-stage prefix disagreement")
    need(hosted["hosted_residuals"] == 120960 and hosted["bank_assignments"] == 0,
         "hosted helper census changed")
    geometry = read(local / "nine/GEOMETRY.json")
    detail = {name: invoice_detail(native[name + "_bill"]["total_adds"],
                                  int(native[name + "_bill"]["nine_stage_prefix"]),
                                  hosted, global_receipt, geometry)
              for name in ("original", "candidate")}
    need(detail["candidate"]["coefficient_bits"] == invoice["bit"]["coefficient_bits"] and
         detail["candidate"]["two_level_bits"] == invoice["bit"]["two_level_coefficient_bits"],
         "expanded candidate invoice disagreement")
    need(detail["original"]["coefficient_bits"] == expected["nine"]["bit"]["coefficient_bits"] and
         detail["original"]["two_level_bits"] == expected["nine"]["bit"]["two_level_coefficient_bits"],
         "expanded original invoice disagreement")
    result = {
        "status": "PASS_R420_TARGET_COMPENSATION_HOSTED",
        "word_sha256": native["word_sha256"],
        "local_adds": legality["common_frame_ADDs"],
        "local_records": legality["records"],
        "local_rank_mass": legality["rank_mass"],
        "five_stage_columns": five["formal_columns_checked"],
        "nine_stage_columns": nine["formal_columns_checked"],
        "nine_stage_bridge_controls": len(nine["negative_controls"]),
        "parent_unbanked_columns": global_receipt["independent_unbanked_scalar_columns"],
        "parent_bridge_controls": len(global_receipt["omitted_bridge_shears_rejected"]),
        "record_controls": mutations,
        "parent_mutations_rejected": parent["mutations_rejected"],
        "hosted_mutations_rejected": hosted["mutations_rejected"],
        "hosted_events": hosted["emitted_events"],
        "hosted_profile": hosted["profile"],
        "hosted_residuals": hosted["hosted_residuals"],
        "live": hosted["live"],
        "physical": hosted["physical"],
        "invoice": invoice["bit"],
        "expanded_invoice": detail,
        "unchanged_bit_lower": invoice["bit_lower"],
        "cited_complex_lower": selected["complex_lower"],
        "unchanged_kappa": invoice["kappa"]["selected626"]["kappa"],
        "outer_strict_constraints": invoice["kappa"]["selected626"]["strict_outer_constraints"],
        "outer_controls": invoice["kappa"]["selected626"]["outer_controls"],
    }
    certificate = HERE / "HOSTED-CERTIFICATE.json"
    if args.write_certificate:
        with certificate.open("x") as f:
            json.dump(result, f, indent=2)
            f.write("\n")
    else:
        need(result == read(certificate), "hosted certificate mismatch")
    (out / "report.json").write_text(json.dumps(result, indent=2) + "\n")
    pins(manifest)
    print(f"PASS_R420_TARGET_COMPENSATION_HOSTED local_adds=19037 hosted_events={result['hosted_events']} "
          "prefix_charge=192 coefficient_charge=512 kappa=unchanged", flush=True)
    print("Replay files: " + str(out), flush=True)


if __name__ == "__main__":
    main()
