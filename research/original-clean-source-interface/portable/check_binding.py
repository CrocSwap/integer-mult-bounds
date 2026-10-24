"""Check the original owner binding against accepted physical contracts."""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import gzip
import json
from pathlib import Path


LANES = Path(__file__).resolve().parents[1] / 'frozen' / 'work/centre-encoding-campaign-20261014/lanes'
OWNER = LANES / "source-domain/restored-helper-interface"
MODES = [225, 226, 229, 232, 241, 242, 257, 258]
ARCHIVE = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PINS = {
    "proof": (OWNER / "ORIGINAL-CLEAN-BINDING.md", "c9fef9921185aa18e20d8c1b9f1b10289d488fc74d674f9afc408fb404040d65"),
    "producer": (OWNER / "bind_original_clean.py", "3e9dd5c811dd2f4783766a3c7ff41b0a3efb7c6656abe889d8537377c134e0c3"),
    "binding": (OWNER / "ORIGINAL-CLEAN-BINDING.json", "31fae7f2aa4a1f6b9cd5f55a8a34a7679ae6c77cafd37da465f3cb51a7e59141"),
    "inventory": (OWNER / "OWNERS.json", "ee7cb00286581bfc041174e2bf6ed2c1a46481acc74488007198adc7c21f27a1"),
    "local_physical_review": (LANES / "paired-package-review/original-clean-native-review/REVIEW.json", "56b08d1b2772b61b2a5cbea0b0ff827d79c0fd335eb1f004168783b637dfee7e"),
    "checked_old_owner_history": (LANES / "paired-package-review/even-global-review/REVIEW.json", "46db6bef10039a3123403c26825709e69c4af612ad5d943c2f46ee12b75ec4f4"),
    "original_phase_review": (LANES / "interface-proof/ORIGINAL-COMPLEX-MODES-REVIEW.json", "8b8c4d814b44c2fc42cf9ad995f8451512309fcfc46bea9317ebe4b4d79e8a4d"),
}
MEMBERS = {
    "template": ("candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz", "2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760"),
    "phases": ("candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json", "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"),
    "audit": ("candidate/strict/global/audit/OWNERS-AND-PROFILE.json", "30bafff060afcfb3644e951214d66cfaffe58242881c652e28003958b42127cc"),
}


def need(value, reason):
    if not value:
        raise ValueError(reason)


def semantic_hash(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main(args):
    data = {}
    for key, (path, pin) in PINS.items():
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == pin, "Source pin: " + key)
        data[key] = json.loads(raw) if path.suffix == ".json" else raw
    for key, (name, pin) in MEMBERS.items():
        raw = (args.members / name).read_bytes()
        need(sha256(raw).hexdigest() == pin, "Archive member: " + key)
        data[key] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    binding, inventory, physical = (data[k] for k in ("binding", "inventory", "local_physical_review"))
    template, phases, audit = (data[k] for k in MEMBERS)
    need(physical["status"] == "PASS_INDEPENDENT_ORIGINAL_CLEAN_PHYSICAL_HELPER_BINDING"
         and binding["dependency_sha256"]["clean"] == physical["payload_decompressed_sha256"]
         and binding["dependency_sha256"]["local_review"] == physical["content_review_sha256"]
         and binding["dependency_sha256"]["core"] == physical["raw_core_sha256"], "New physical hypothesis")
    need(binding["dependency_sha256"]["owners"] == PINS["inventory"][1], "Exact original owner inventory")
    need(data["checked_old_owner_history"]["independent_counts"]["restored_mode_jobs"] == 1152,
         "Accepted independent old-axis history")
    need(binding["unchanged_schedule_sha256"] == semantic_hash(template["execution_schedule"])
         and binding["unchanged_data_phase_recipe_sha256"] == semantic_hash(phases), "Unchanged original phase schedule")
    mode_records = {(r["time"], r["role"]): r for r in inventory["records"]}
    source_slots = defaultdict(dict)
    for job in template["hosting"]["pooled_slots"]:
        need(job["helper"] not in source_slots[job["time"]], "Unique source slot")
        source_slots[job["time"]][job["helper"]] = job
    entries = {entry["time"]: entry for entry in binding["bindings"]}
    positions = {event["time"]: i for i, event in enumerate(template["execution_schedule"])
                 if event["kind"] == "local_cover_sweep"}
    counts, stream, local_scalar = Counter(), [], 0
    for call in template["calls"]:
        time, owners = call["time"], call["owners"]
        row = entries[time]
        need(len(owners) == len({o[0] for o in owners}) == 704, "Actual atomic owner distinctness")
        need(row["position"] == positions[time] and row["stage"] == call["stage"]
             and row["replica"] == call["replica"] and row["orientation"] == call["orientation"]
             and row["owner_digest"] == semantic_hash(owners), "Literal invocation binding")
        need(set(source_slots[time]) == set(range(480)), "Complete source helper list")
        modes = {mode["role"]: mode for mode in row["restored_modes"]}
        need(set(modes) == set(MODES), "Exact selected mode list")
        for helper, job in sorted(source_slots[time].items()):
            role = 224 + helper
            family, route = owners[role]
            need(family == job["family"] and route[1:3] == [job["child"], job["offset"]],
                 "Literal complete helper job")
            stream.append([time, helper, owners[role], job])
            if role in MODES:
                record = mode_records[time, role]
                need(modes[role] == {key: record[key] for key in modes[role]}, "Accepted exact owner history")
                need(route == [3, job["child"], job["offset"]] and job["width"] == 9, "Complete F9 owner job")
                recipe = phases["recipes"][job["port"]]
                basis = [recipe["q"]] + recipe["idle_children"][0]["orthogonal_axes"][:8]
                basis += [1 << j for j in range(9, 73)]
                vectors = recipe["idle_children"][job["child"]]["orthogonal_axes"][job["offset"]:job["offset"] + 9]
                axes = [basis.index(v) for v in vectors]
                order = axes + [j for j in range(73) if j not in axes]
                need(record["pending_axes"] == axes and record["sigma_column_order"] == order
                     and all(not (record["inherited_owner_mask"] >> j & 1) for j in axes),
                     "Independent whole-job covariance and exterior")
                counts["complete_F9_jobs"] += 1
            counts["helper_jobs"] += 1
        counts[call["orientation"]] += 1
        local_scalar += physical["checks"][call["orientation"]]["complete_local_scalar_bound"]
    need(semantic_hash(stream) == binding["exact_old_helper_job_stream_sha256"], "Complete original job stream")
    need(counts == {"complete_F9_jobs": 1152, "helper_jobs": 69120, "forward": 80, "backward": 64},
         "All source occurrences")
    need(local_scalar == binding["local_scalar_subtotal"] == 32234016, "Complete local scalar subtotal")
    profile = Counter()
    for call in template["calls"]:
        program = template["local_providers"]["gauge44"]["local_programs"][call["orientation"]]
        profile.update(e[5] for e in program if e[0] == "climb")
    profile.update(item["rank"] for item in template["idle_children"] if item["rank"])
    need(dict(profile) == {int(k): v for k, v in binding["paid_profile"].items()}, "Independent retained profile")
    need(dict(profile + Counter({8: 1152})) == {int(k): v for k, v in audit["paid_profile"].items()},
         "Exact private-centre removal")
    report = dict(status="PASS_INDEPENDENT_ORIGINAL_CLEAN_OWNER_BINDING",
                  source_pins={key: pin for key, (_, pin) in PINS.items()}, archive_sha256=ARCHIVE,
                  archive_members={key: pin for key, (_, pin) in MEMBERS.items()},
                  counts=dict(counts), source_positions=len(template["execution_schedule"]),
                  source_helper_stream_sha256=semantic_hash(stream),
                  native_profile=dict(sorted(profile.items())), native_rank_mass=sum(r * n for r, n in profile.items()),
                  local_scalar_subtotal=local_scalar, changed_old_phase_or_owner_events=0,
                  inherited_history_scope="Only exact original jobs, axis histories, owner distinctness and native phase identities. No characteristic maps or altered mode repairs.",
                  terminal_equation="F W diag(I,Q) E diag(Q^-1,I)=F if and only if E=W^-1.",
                  remaining="Changed routed D_plus/D_minus controller, parser lowering, finite precision, complete recursive invoice and supplier admission.")
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "counts", "native_rank_mass", "local_scalar_subtotal")}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--members", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("CHECKS.json"))
    main(parser.parse_args())
