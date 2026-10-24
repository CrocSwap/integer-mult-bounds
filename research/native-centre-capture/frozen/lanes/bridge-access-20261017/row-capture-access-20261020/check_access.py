"""Check native path isolation and exact row-capture boundary views."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import argparse
import gzip
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
PINS = {
    "native": (
        "new-core-transfer-20261017/low-displacement-20261020/"
        "odd16-normal-v2/EXTENSION-PROGRAM.json.gz",
        "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4",
    ),
    "capture": (
        "controller-followthrough-20261017/row-capture-20261020/"
        "run-normal/ROW-CAPTURE.json",
        "4c98af5d7a1437a03f53e84f0f2cbc7cd2ac47d4c6d4ee1523c16bf469692eb7",
    ),
    "views": (
        "bridge-access-20261017/matched-stage-access-20261018/"
        "DIMENSION25-VIEWS.json",
        "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473",
    ),
    "phase": (
        "bridge-access-20261017/check_bridge_access.py",
        "9510c5624dfb51d98767728084851e4ee75a135e6d7b546569a47fe458485111",
    ),
}
PIVOTS = [0, 27, 36, 111, 20, 7, 57, 46, 1, 3, 6, 8, 17, 18, 24, 23]
PAIRS = [(0, 27), (36, 111), (20, 46), (7, 57)]


def need(value, message):
    if not value:
        raise ValueError(message)


def raw_source(name):
    path, pin = PINS[name]
    raw = (LANES / path).read_bytes()
    if path.endswith(".gz"):
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Source pin: " + name)
    return raw


def matrix(rows):
    return [{int(j): F(v) for j, v in row.items() if F(v)} for row in rows]


def multiply(a, b):
    result = []
    for row in a:
        acc = {}
        for j, v in row.items():
            for k, w in b[j].items():
                acc[k] = acc.get(k, F(0)) + v * w
        result.append({j: v for j, v in acc.items() if v})
    return result


def dump(rows):
    return [{str(j): str(v) for j, v in sorted(row.items())} for row in rows]


def native_isolation(word):
    selected = {112 + p for p in PIVOTS}
    live = list(word["start"])
    kept = []
    removed = []
    old_profile = Counter()
    removed_profile = Counter()
    scalar_removed = Counter()
    last_source = -1
    for i, event in enumerate(word["events"]):
        if event[0] == "native":
            _, target, old, new, rank, _ = event
            old_profile[rank] += 1
            omit = target in selected
            if omit:
                removed_profile[rank] += 1
            else:
                need(live[target] == old, "Retained native input frame")
                live[target] = new
        else:
            need(event[0] == "scalar", "Native event type")
            _, (op, target, source, coefficient), frame = event
            omit = target in selected
            if omit:
                scalar_removed[op + ":" + coefficient] += 1
            else:
                need(source not in selected, "Removed target is not read")
                need(live[target] == frame, "Retained scalar target frame")
                if source is not None:
                    need(live[source] == frame, "Retained scalar source frame")
            need(not (target < 112 and source is not None and source >= 112),
                 "Forward word has no target-to-source feedback")
        if target < 112:
            last_source = i
        (removed if omit else kept).append(i)
    need(len(removed) == 250 and removed_profile == {1: 128},
         "Exact selected path census")
    need(sum(scalar_removed.values()) == 122, "Exact scalar deletion census")
    need(last_source == 2638, "Last complete source cut")
    need(all(live[p] == 1 for p in range(112)), "All sources are FULL")
    need(all(live[t] == 0 for t in selected), "Selected targets stay at I")
    need(all(live[t] == word["final"][t] for t in range(len(live))
             if t not in selected), "Other endpoint frames are retained")
    need(len(word["frames"][1]) == 9, "FULL is the nine-axis frame")
    need(all(word["start"][i] == word["final"][i] for i in range(224, 640)),
         "The 416 outside fields are retained")
    for t in selected:
        live[t] = 1
    profile = old_profile - removed_profile
    profile[9] += 16
    need(profile == {1: 1392, 2: 64, 3: 48, 9: 16}, "Hybrid native profile")
    need(sum(k * v for k, v in profile.items()) == 1808, "Hybrid native rank")
    return {
        "removed_event_indices": removed,
        "retained_event_indices": kept,
        "removed_native_profile": dict(sorted(removed_profile.items())),
        "removed_scalar_census": dict(sorted(scalar_removed.items())),
        "last_source_event": last_source,
        "query_cut_after_original_event": len(word["events"]) - 1,
        "hybrid_final_frames": live,
        "native_profile": dict(sorted(profile.items())),
        "native_rank": 1808,
        "native_children": sum(profile.values()),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "run-normal")
    args = parser.parse_args()
    source = json.loads(raw_source("native"))
    capture = json.loads(raw_source("capture"))
    views = json.loads(raw_source("views"))
    raw_source("phase")
    spec = importlib.util.spec_from_file_location(
        "row_capture_phase", LANES / PINS["phase"][0])
    phase = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(phase)
    need(capture["pivots"] == PIVOTS, "Capture pivot order")
    c, ci, e = (matrix(capture[k]) for k in ("code", "code_inverse", "response"))
    ident = [{i: F(1)} for i in range(112)]
    need(multiply(c, ci) == multiply(ci, c) == ident, "Capture is a unit")
    need(e == matrix(source["model"]["response"]), "Same actual response")
    ce = multiply(c, e)
    for p in range(112):
        if p in PIVOTS:
            need(c[p].get(p) == 1 and set(c[p]) & set(PIVOTS) == {p},
                 "Capture reads only unchanged complement rows")
        else:
            need(c[p] == ident[p] and ce[p] == e[p],
                 "Capture leaves every complement row unchanged")
    providers = {
        name: native_isolation(words["forward"])
        for name, words in source["providers"].items()
    }
    unit = [1 << j for j in range(25)]
    entries = []
    counts = Counter()
    for record in views["entries"]:
        p, s, q = record["port"], record["stage"], record["q"]
        rho = record["route_columns"]
        align = record["literal_stage_alignment"]
        if p not in PIVOTS:
            continue
        exterior = [(v, 1) for v in unit[9:9 + 8 * s]]
        before = [] if not s else (
            [(v, 1) for v in unit[:9 + 8 * (s - 1)]] + [(q, -1)])
        entry = phase.add_phase(
            phase.product([(phase.act(rho, v), k) for v, k in before]),
            phase.line(phase.act(rho, align["entry_Y"]), 2))
        need(entry == phase.product(exterior), "Current-I selected Y entry")
        counts["current_I_entries"] += 1
        full = [(v, 1) for v in unit[:9 + 8 * s]]
        exit_phase = phase.add_phase(
            phase.product([(phase.act(rho, v), k) for v, k in full]),
            phase.line(align["exit_X"], 2))
        need(exit_phase == phase.product(full), "Selected FULL output phase")
        need(align["exit_X"] == align["exit_Y"],
             "Actual FULL and hole exit translations agree")
        counts["selected_FULL_exits"] += 1
        item = dict(record)
        item["hybrid_exit_translation"] = align["exit_X"]
        item["next_current_entries"] = []
        for nxt in views["entries"]:
            if nxt["port"] != p or nxt["stage"] <= s:
                continue
            t = nxt["stage"]
            rho_t = nxt["route_columns"]
            delta = phase.act(rho_t, nxt["literal_stage_alignment"]["entry_Y"])
            actual = phase.add_phase(
                phase.product([(phase.act(rho_t, v), k) for v, k in full]),
                phase.line(delta, 2))
            common_axes = unit[9:9 + 8 * s] + unit[9 + 8 * (t - 1):9 + 8 * t]
            expected = phase.product([(v, 1) for v in common_axes] + [(q, 1)])
            need(actual == expected, "Carried FULL centre has intrinsic Q")
            need(actual != phase.product([(v, 1) for v in common_axes]),
                 "Carried FULL centre is not an I input")
            counts["future_intrinsic_Q_entries"] += 1
            item["next_current_entries"].append({
                "stage": t, "common_exterior_axes": common_axes,
                "intrinsic_line": q, "intrinsic_exponent": 1,
                "translation_after_route": delta,
            })
        entries.append(item)
    need(counts == {"current_I_entries": 48, "selected_FULL_exits": 48,
                    "future_intrinsic_Q_entries": 48}, "All selected D25 cuts")
    program = {
        "schema": "row-capture-access-v1", "source_pins": PINS,
        "pivots": PIVOTS, "complete_large_pairs": PAIRS,
        "providers": providers, "selected_views": entries,
        "selected_output_rows": dump([ce[p] for p in PIVOTS]),
        "selected_input_rows": dump([c[p] for p in PIVOTS]),
        "owner_cover": "Regular O(25,2); use a complete cover sweep per stage.",
        "new_native_recipes_emitted_here": False,
        "recursive_hosting_proved_here": False,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(program, sort_keys=True, indent=2) + "\n").encode()
    (args.output / "ACCESS-PROGRAM.json").write_bytes(raw)
    receipt = {
        "status": "PASS_ROW_CAPTURE_NATIVE_ISOLATION_AND_D25_ACCESS",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_pins": PINS, "program_sha256": sha256(raw).hexdigest(),
        "phase_checks": dict(counts),
        "native_profile": {"1": 1392, "2": 64, "3": 48, "9": 16},
        "native_rank": 1808, "native_children": 1520,
        "outside_arbitrary_fields": 416,
        "next_interface": "FULL centre rows become Q at a future current-Y entry.",
        "complete_supplier_claimed": False,
    }
    (args.output / "CHECKS.json").write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
