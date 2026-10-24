"""Bind the all-width clean physical word to the original selected owners."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
import gzip
import json
from pathlib import Path
import tarfile


ARCHIVE = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBERS = {
    "template": ("candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz",
                 "2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760"),
    "word": ("candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz",
             "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"),
    "phases": ("candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json",
               "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"),
    "audit": ("candidate/strict/global/audit/OWNERS-AND-PROFILE.json",
              "30bafff060afcfb3644e951214d66cfaffe58242881c652e28003958b42127cc"),
}
INPUTS = {
    "core": "f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205",
    "clean": "abfcbfc40bac24e284be63623d9b18f1bb6d4d6ec1b9fa7e9bba27330f323667",
    "local_review": "679b94dbb4dbb8ba8d1c12aadf3a37f9b9e5176296905e6bf8007dfb3925cbfa",
    "owners": "ee7cb00286581bfc041174e2bf6ed2c1a46481acc74488007198adc7c21f27a1",
    "old_phase_review": "8b8c4d814b44c2fc42cf9ad995f8451512309fcfc46bea9317ebe4b4d79e8a4d",
}
MODES = [225, 226, 229, 232, 241, 242, 257, 258]


def need(value, reason):
    if not value:
        raise ValueError(reason)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check_call(call, slots):
    owners = call["owners"]
    need(len(owners) == 704 and len({owner[0] for owner in owners}) == 704,
         "The atomic call has an owner alias")
    need(set(slots) == set(range(480)), "The call does not have all old helper jobs")
    for helper, row in slots.items():
        family, route = owners[224 + helper]
        need(family == row["family"] and route[1:3] == [row["child"], row["offset"]],
             "The old helper owner or route changed")
        if 224 + helper in MODES:
            need(row["width"] == 9 and route == [3, row["child"], row["offset"]],
                 "A restored mode is not its old complete width-nine job")


def main(args):
    need(sha256(args.archive.read_bytes()).hexdigest() == ARCHIVE, "Selected archive pin")
    source = {}
    with tarfile.open(args.archive) as archive:
        for key, (name, pin) in MEMBERS.items():
            raw = archive.extractfile(name).read()
            need(sha256(raw).hexdigest() == pin, key + " source pin")
            source[key] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    inputs = {}
    for key, pin in INPUTS.items():
        raw = getattr(args, key).read_bytes()
        if key in ("core", "clean"):
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == pin, key + " accepted input pin")
        inputs[key] = json.loads(raw)
    template, word, phases, audit = [source[key] for key in MEMBERS]
    core, clean, review, inventory, phase_review = [inputs[key] for key in INPUTS]
    need(review["status"] == "PASS_INDEPENDENT_ORIGINAL_COMPLEX_CLEAN_SOURCE_COMPONENT"
         and review["reviewed_source_pins"]["payload"] == INPUTS["clean"]
         and review["reviewed_source_pins"]["core"] == INPUTS["core"], "Exact local review binding")
    need(clean["core_payload_sha256"] == INPUTS["core"] and clean["mode_carriers"] == MODES,
         "Raw core and role binding")
    need(clean["schema"] == "original-complex-clean-source-v1"
         and clean["width_requirement"] == "Every positive integer lambda", "Original all-width word")
    need(phase_review["status"] == "PASS_INDEPENDENT_ORIGINAL_COMPLEX_MODE_PHASES_AND_OWNERS"
         and phase_review["source_archive_sha256"] == ARCHIVE
         and phase_review["original_phase_member_sha256"] == MEMBERS["phases"][1],
         "Exact original phase-history dependency")
    need(inventory["archive_sha256"] == ARCHIVE
         and inventory["member_sha256"] == {key: pin for key, (_, pin) in MEMBERS.items()},
         "Original owner inventory source binding")
    need(all(word["start"][role] == 0 and word["final"][role] == 1 for role in MODES)
         and word["frames"][0] == [] and set(word["frames"][1]) == {1 << j for j in range(9)},
         "The eight physical helper endpoints are not I to F9")
    counts, scalar_subtotal, native_digests = Counter(), 0, {}
    for orientation in ("forward", "backward"):
        local = review["checks"][orientation]
        need(local["arbitrary_input_columns"] == 704 and local["restored_helper_fields"] == 480
             and local["helper_input_coefficients_in_data"] == 0, "Complete arbitrary helper contract")
        old = template["local_providers"]["gauge44"]["local_programs"][orientation]
        old_native = [op for op in old if op[0] not in ("scalar", "phase", "center")]
        new_native = [op for op in core[orientation] if op[0] not in ("scalar", "phase", "center")]
        need(old_native == new_native and len(new_native) == 5056, "The old native stream changed")
        need(sum(op[0] == "center" for op in old) == 8
             and all(op[0] != "center" for op in core[orientation]), "Centre removal count")
        native_digests[orientation] = digest(new_native)
        program = clean["programs"][orientation]
        allowed = set(range(224)) | set(MODES)
        gate_counts = Counter()
        for boundary in ("prefix", "suffix"):
            for gate in program[boundary]:
                need(gate["endpoint"] == ("input" if boundary == "prefix" else "output"),
                     "The physical gate is at the wrong endpoint")
                need(gate["target"] in allowed, "The wrapper writes another helper or private field")
                need(gate["kind"] in ("physical_add", "physical_scale"), "The wrapper adds a native map")
                if gate["kind"] == "physical_add":
                    need(gate["source"] in allowed and gate["source"] != gate["target"],
                         "The physical ADD has an alias or a private source")
                    coefficient = Fraction(gate["coefficient"])
                    need(coefficient.denominator & (coefficient.denominator - 1) == 0,
                         "The ADD coefficient is not dyadic")
                else:
                    need(gate["target"] in MODES and gate["coefficient"] == "-1", "Mode sign")
                gate_counts[gate["kind"]] += 1
        need(gate_counts == {"physical_add": 1792, "physical_scale": 8}, "Complete added scalar lists")
        need([gate["target"] for gate in program["suffix"][-8:]] == MODES, "The final signs are absent")
        need(local["new_fields"] == local["new_native_children"] == local["new_address_or_phase_maps"] == 0,
             "The local review has an added stock or map obligation")

    slots, source_jobs = defaultdict(dict), template["hosting"]["pooled_slots"]
    for index, row in enumerate(source_jobs):
        need(row["helper"] not in slots[row["time"]], "Duplicate helper slot")
        slots[row["time"]][row["helper"]] = row
    inventory_records = {(row["time"], row["role"]): row for row in inventory["records"]}
    positions = {event["time"]: position for position, event in enumerate(template["execution_schedule"])
                 if event["kind"] == "local_cover_sweep"}
    bindings, helper_stream = [], []
    for call in template["calls"]:
        check_call(call, slots[call["time"]])
        orientation = call["orientation"]
        counts[orientation] += 1
        scalar_subtotal += review["checks"][orientation]["core_and_added_real_primitives"]
        external = ((1 << (9 + 8 * call["stage"])) - 1) ^ 511
        need(external & 511 == 0, "The data exterior meets the local nine axes")
        modes = []
        for role in MODES:
            record = inventory_records[call["time"], role]
            job = slots[call["time"]][role - 224]
            need(record["position"] == positions[call["time"]]
                 and source_jobs[record["source_job"]] == job
                 and record["family"] == call["owners"][role][0]
                 and record["route"] == call["owners"][role][1], "Actual restored helper occurrence")
            need(record["active_Y_reference_mask"] == external
                 and record["invocation_exterior_mask"] & 511 == 0, "Actual exterior decomposition")
            need(record["sigma_column_order"][:9] == record["pending_axes"]
                 and sorted(record["sigma_column_order"]) == list(range(73)), "Exact complete helper chart")
            modes.append({key: record[key] for key in ("role", "family", "source_job", "route",
                         "pending_axes", "sigma_column_order", "inherited_owner_mask",
                         "invocation_exterior_mask")})
        for helper, job in sorted(slots[call["time"]].items()):
            helper_stream.append([call["time"], helper, call["owners"][224 + helper], job])
        bindings.append(dict(time=call["time"], position=positions[call["time"]], stage=call["stage"],
            replica=call["replica"], orientation=orientation, data_exterior_mask=external,
            owner_digest=digest(call["owners"]), restored_modes=modes))
    need(counts == {"forward": 80, "backward": 64} and len(bindings) == 144
         and len(helper_stream) == 69120 and len(inventory_records) == 1152, "Complete call inventory")
    need(scalar_subtotal == 32234016, "Complete local scalar subtotal")
    profile = {int(rank): count for rank, count in audit["paid_profile"].items()}
    need(profile.pop(8) == 1152, "All old private centres removed")
    mass = sum(rank * count for rank, count in profile.items())
    need(mass == 1032192 and template["live"] == 14336 and template["physical"] == 14826,
         "Actual profile or stock")
    controls = {}
    for label in ("owner_alias", "wrong_mode_job_width"):
        call = json.loads(json.dumps(template["calls"][0]))
        jobs = json.loads(json.dumps(slots[call["time"]]))
        jobs = {int(key): value for key, value in jobs.items()}
        if label == "owner_alias":
            call["owners"][MODES[0]] = call["owners"][0]
        else:
            jobs[MODES[0] - 224]["width"] = 8
        try:
            check_call(call, jobs)
        except ValueError as error:
            controls[label] = str(error)
        else:
            raise ValueError("The semantic control was not rejected: " + label)
    report = dict(status="PASS_ALL_WIDTH_ORIGINAL_CLEAN_SOURCE_OWNER_BINDING",
        source_archive_sha256=ARCHIVE, source_members={key: pin for key, (_, pin) in MEMBERS.items()},
        dependency_sha256=INPUTS, local_native_stream_sha256=native_digests,
        expansion=["unchanged original entry view", "new orientation prefix", "unchanged raw core",
                   "new orientation suffix including all eight signs", "unchanged original exit and owner view"],
        atomic_body_and_complete_cover_sweep=True, new_stage_idle_or_terminal_maps=0,
        unchanged_schedule_sha256=digest(template["execution_schedule"]),
        unchanged_data_phase_recipe_sha256=digest(phases),
        exact_old_helper_job_stream_sha256=digest(helper_stream), call_counts=dict(counts),
        schedule_positions=482, restored_helper_occurrences=69120, restored_full_nine_occurrences=1152,
        inherited_idle_suffixes=7526, inherited_bridge_frame_pairs=32256, bindings=bindings,
        old_phase_dependency_scope="Only the exact original complex phase and owner history is inherited; no altered mode swap or endpoint repair from that review is used.",
        owner_inventory_dependency_scope="Only the source-derived original schedule, axis histories, routes and owner distinctness are inherited; its even-width wrapper is not used.",
        width_requirement="Every positive integer lambda", live=14336, physical=14826,
        new_fields=0, new_owner_jobs=0, new_native_children=0, removed_rank_eight_centres=1152,
        paid_profile=profile, paid_rank=mass, rank_deficit=73 * 14336 - mass,
        local_scalar_subtotal=scalar_subtotal, new_address_or_phase_maps=0, semantic_controls=controls,
        data_kernels=clean["content_contract"],
        complete_data_condition="E=W^-1, where E is the routed data word before the retained terminal and W is the old signed bank exchange.",
        remaining=["Complete changing-chart D_plus/D_minus data controller", "Literal parser lowering of the new physical scalar macros",
                   "Complete prefix, precision, control and recursive invoice", "Supplier and final assembly admission"],
        scope="Actual original-owner and native-job admission of the stated local replacement, not a complete Fourier supplier or a kappa improvement.")
    args.out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "call_counts", "restored_helper_occurrences",
        "restored_full_nine_occurrences", "paid_rank", "rank_deficit", "local_scalar_subtotal", "live", "physical")}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("archive", *INPUTS):
        parser.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("ORIGINAL-CLEAN-BINDING.json"))
    main(parser.parse_args())
