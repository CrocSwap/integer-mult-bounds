#!/usr/bin/env python3
"""Source-bound family-norm majorants for the selected PR1094 controller.

OpenAI Codex (GPT-6 Astra), substantial AI assistance. Apache-2.0.
Builds on eumemic's PR496 family-norm argument and Brody Arbon's PR821
replica counters. The retained local checker is replayed, not reimplemented.
No production precision charge or kappa is changed.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
MANIFEST = "research/community-frontier1094-audit/SELECTED-SOURCE.json"
REPLAY = "research/community-frontier1094-audit/REPLAY.json"
CHECKER = "research/complex-k492-owner-repair/code/hpe_audit_local.py"
INVOICE = "research/gauge44-slots-t16/code/invoice_allcold.py"
SUPPLIER_PROOF = "research/complex-double-replica-owners/PROOF.md"
INPUTS = {ARCHIVE, MANIFEST, REPLAY, CHECKER, INVOICE, SUPPLIER_PROOF}
BASE = "candidate/strict/global/base/"
PROVIDER = BASE + "providers/gauge44/"
HOSTED = "candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz"
PARENT = BASE + "split-centres/GLOBAL-TEMPLATE.json.gz"
PREFIX = "candidate/strict/global/audit/GLOBAL-PREFIX.json"
V, REPLICAS, PAIRS, HELPERS = 112, 16, 4, 480
LIVE = V * REPLICAS * PAIRS * 2


class AuditError(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise AuditError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def strict_bits(value):
    """Least nonnegative integer b with value < 2**b, using exact arithmetic."""
    value = Q(value)
    need(value > 0, "positive envelope")
    b = 0
    while value >= 1 << b:
        b += 1
    return b


def check_pins(root=ROOT):
    pins = json.loads((PACKAGE / "SOURCES.json").read_bytes())
    live = [p for p in pins["files"] if p["usage"] == "input"]
    need(len(live) == len(INPUTS) and {p["path"] for p in live} == INPUTS,
         "mandatory source inventory")
    for p in live:
        need(sha((root / p["path"]).read_bytes()) == p["sha256"],
             "source hash: " + p["path"])
    selected = json.loads((root / MANIFEST).read_bytes())["files"]
    need(selected[INVOICE] == sha((root / INVOICE).read_bytes()), "selected invoice binding")
    need(selected["research/complex-sw4-frame8/local/hpe_audit_local.py"]
         == sha((root / CHECKER).read_bytes()), "selected local checker binding")
    return {p["path"]: p["sha256"] for p in live}


def load(root=ROOT):
    hashes = check_pins(root)
    names = [HOSTED, PARENT, PREFIX] + [PROVIDER + n for n in (
        "CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz",
        "LOCAL-CHECKS.json", "INDEPENDENT-LOCAL-REPLAY.json")]
    blobs = {}
    with tarfile.open(root / ARCHIVE) as archive:
        for name in names:
            members = [m for m in archive.getmembers() if m.name == name]
            need(len(members) == 1 and members[0].isfile(), "unique regular member: " + name)
            blobs[name] = archive.extractfile(members[0]).read()

    def read(name):
        data = blobs[name]
        return json.loads(gzip.decompress(data) if name.endswith(".gz") else data)

    template, parent, prefix = map(read, (HOSTED, PARENT, PREFIX))
    word = read(PROVIDER + "CANONICAL-WORD.json.gz")
    programs = read(PROVIDER + "LOCAL-PROGRAMS.json.gz")
    local = read(PROVIDER + "INDEPENDENT-LOCAL-REPLAY.json")
    checks = read(PROVIDER + "LOCAL-CHECKS.json")
    need(sha(gzip.decompress(blobs[HOSTED])) == prefix["template_sha256"],
         "global prefix template binding")
    need((word["v"], word["R"], word["h"], template["m"], template["live"])
         == (V, HELPERS, 9, 73, LIVE), "selected dimensions")
    need(set(template["local_providers"]) == {"gauge44"}, "one selected provider")
    registry = template["local_providers"]["gauge44"]
    for name, field in [("CANONICAL-WORD.json.gz", "canonical_word_sha256"),
                        ("LOCAL-PROGRAMS.json.gz", "local_programs_sha256")]:
        need(sha(blobs[PROVIDER + name]) == local[field] == registry[field],
             "local artifact binding: " + name)
    need(registry["local_programs"] == programs and registry["local_program_checks"] == checks,
         "provider program/check binding")
    need(set(programs) == {"forward", "backward"}, "both local orientations")
    for name, events in programs.items():
        digest = sha(json.dumps(events, separators=(",", ":")).encode())
        need(digest == checks[name]["sha256"], "program digest")
    published = json.loads((root / REPLAY).read_bytes())
    need(published["prefix_bits"] == prefix["global_prefix_bits"] == 397
         and published["charged_prefix_bits"] == prefix["retained_payload_bits"] == 512,
         "published precision record")
    return dict(template=template, parent=parent, prefix=prefix, local=local,
                checks=checks, blobs=blobs, hashes=hashes)


def replay_local(context, root=ROOT):
    """Run the unchanged, pinned original checker with assertions enabled."""
    with tempfile.TemporaryDirectory(prefix="pr1094-wire-prefix-") as temp:
        work = Path(temp)
        for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
            (work / name).write_bytes(context["blobs"][PROVIDER + name])
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        env.pop("PYTHONOPTIMIZE", None)
        run = subprocess.run([sys.executable, "-B", str(root / CHECKER), str(work)],
                             cwd=work, env=env, capture_output=True, text=True, timeout=180)
        need(run.returncode == 0, "retained local replay failed: " + run.stdout + run.stderr)
        result = json.loads((work / "INDEPENDENT-LOCAL-REPLAY.json").read_bytes())
        need(result == context["local"], "fresh local receipt differs")
    return dict(status=result["status"], exact_columns_per_orientation=2 * V + HELPERS,
                orientations=["forward", "backward"],
                original_controls_rejected=result["negative_controls_rejected"],
                receipt_identical=True)


def stripped(event):
    return {k: v for k, v in event.items()
            if k not in {"replica", "replicas", "source_event", "time", "provider_id"}}


def validate_controller(template, parent, checks):
    """Check the specific structural hypotheses consumed by the norm proof."""
    need(template["recipe"] == parent["recipe"], "source recipe")
    need("each local invocation completes before the next" in template["loop_order"].lower(),
         "atomic invocation contract")
    recipe = {e["stage"]: e for e in parent["recipe"] if e["kind"] == "local"}
    need(set(recipe) == set(range(9)), "all source stages")
    calls = template["calls"]
    need(len(calls) == 9 * REPLICAS, "call count")
    by_call = {(c["stage"], c["replica"]): c for c in calls}
    need(set(by_call) == {(s, r) for s in range(9) for r in range(REPLICAS)},
         "complete distinct calls")
    cross = 0
    for c in calls:
        r, s = c["replica"], c["stage"]
        source = recipe[s]
        orientation = "backward" if source["reverse"] else "forward"
        need(c["pair"] == source["pair"] and c["orientation"] == orientation,
             "source local orientation/pair")
        need(c["provider_id"] == "gauge44" and
             c["local_program_sha256"] == checks[orientation]["sha256"], "call program binding")
        families = [f for f, route in c["owners"]]
        need(len(families) == 2 * V + HELPERS and
             all(type(f) is int and 0 <= f < LIVE for f in families), "owner family range/count")
        need(len(set(families)) == len(families), "one role per physical family")
        first = (r * 8 + source["pair"] * 2) * V
        need(families[:2 * V] == list(range(first, first + 2 * V)), "active data family/port binding")
        cross += sum(f // (8 * V) != r for f in families[2 * V:])

    schedule = template["execution_schedule"]
    need(len(schedule) == 30 * REPLICAS + 2, "source event count")
    per_replica = [[] for _ in range(REPLICAS)]
    order = []
    last_time = [None] * REPLICAS
    for e in schedule[:-2]:
        r = e["replica"]
        need(type(r) is int and 0 <= r < REPLICAS and e["replicas"] == [r], "event replica")
        j = e["source_event"]
        need(type(j) is int and j == len(per_replica[r]) and j < 30, "source event chronology")
        need(stripped(e) == stripped(parent["execution_schedule"][j]), "source event projection")
        if e["kind"] == "local_cover_sweep":
            c = by_call[e["stage"], r]
            need(e["time"] == c["time"] == len(order) and e["provider_id"] == c["provider_id"],
                 "call time/provider binding")
            order.append([e["stage"], r])
            last_time[r] = e["time"]
        need(e["time"] == last_time[r], "event block time")
        per_replica[r].append(j)
    need(all(row == list(range(30)) for row in per_replica), "complete source projection")
    need(order == template["async_schedule"]["order"], "async order binding")
    need(schedule[-2] == dict(kind="bank_padding_cover_sweep", source_event=30,
                             families=[LIVE, LIVE], children_source="bank_padding.children"),
         "empty terminal bank sweep")
    end = dict(parent["execution_schedule"][31], source_event=31,
               families=[0, LIVE], charged_calls_per_cover=LIVE)
    need(schedule[-1] == end, "terminal familywise translation")
    need(not template["bank_padding"]["children"] and
         not template["bank_padding"]["families"], "no bank roles")
    return by_call, recipe, cross


def norm_step(bounds, event, recipe):
    """Nonnegative transfer; no signed cancellation is used."""
    kind = event["kind"]
    r = event.get("replica", 0)
    if kind == "local_cover_sweep":
        call = recipe[event["stage"]]
        source, target = 8 * r + 2 * call["pair"], 8 * r + 2 * call["pair"] + 1
        if call["reverse"]:
            source, target = target, source
        bounds[target] += bounds[source]
    elif kind == "bridge":
        for side in range(2):
            bounds[8 * r + 2 * event["dst"] + side] += (
                abs(event["coefficient"]) * bounds[8 * r + 2 * event["src"] + side])
    elif kind == "terminal":
        # Conservatively allow either signed exchange within each final pair.
        for pair in range(PAIRS):
            a = 8 * r + 2 * pair
            bounds[a] = bounds[a + 1] = max(bounds[a:a + 2])
    else:
        need(kind in {"idle_cover_sweep", "terminal_Y_translations",
                      "bank_padding_cover_sweep", "translate_every_live_family"}, "unknown norm event")


def matrix_boundaries(parent):
    """Separate dense 8x8 transfer calculation on the unexpanded source recipe."""
    recipe = {e["stage"]: e for e in parent["recipe"] if e["kind"] == "local"}
    matrix = [[int(i == j) for j in range(8)] for i in range(8)]
    table = []
    for event in parent["execution_schedule"][:30]:
        step = [[int(i == j) for j in range(8)] for i in range(8)]
        if event["kind"] == "local_cover_sweep":
            q = recipe[event["stage"]]
            target = 2*q["pair"] + (0 if q["reverse"] else 1)
            source = 2*q["pair"] + (1 if q["reverse"] else 0)
            step[target][source] = 1
        elif event["kind"] == "bridge":
            for side in range(2):
                step[2*event["dst"]+side][2*event["src"]+side] = abs(event["coefficient"])
        matrix = [[sum(step[i][k]*matrix[k][j] for k in range(8))
                   for j in range(8)] for i in range(8)]
        if event["kind"] == "terminal":
            # Either signed exchange is bounded by the larger row sum.
            for pair in range(PAIRS):
                a = 2*pair
                row = max(matrix[a:a+2], key=sum)
                matrix[a], matrix[a+1] = row.copy(), row.copy()
        table.append([sum(row) for row in matrix])
    return table


def recount(context, template=None, entry_cap=8):
    template = context["template"] if template is None else template
    calls, recipe, cross = validate_controller(template, context["parent"], context["checks"])
    bounds = [1] * (8 * REPLICAS)
    matrix_table = matrix_boundaries(context["parent"])
    trace = hashlib.sha256()
    entries = []
    boundary_peak = 1
    for position, event in enumerate(template["execution_schedule"]):
        if event["kind"] == "local_cover_sweep":
            call = calls[event["stage"], event["replica"]]
            values = [bounds[f // V] for f, route in call["owners"]]
            need(max(values) <= entry_cap, "actual owner input cap")
            entries.append(dict(event=position, stage=call["stage"], replica=call["replica"],
                                orientation=call["orientation"],
                                active=max(values[:2 * V]), helper=max(values[2 * V:]),
                                input=max(values)))
        norm_step(bounds, event, recipe)
        if "replica" in event:
            r = event["replica"]
            need(bounds[8*r:8*r+8] == matrix_table[event["source_event"]],
                 "independent transfer matrix comparison")
        boundary_peak = max(boundary_peak, max(bounds))
        trace.update(canonical([position, bounds]))
    maxima = {o: max(e["input"] for e in entries if e["orientation"] == o)
              for o in ("forward", "backward")}
    local = context["local"]["local"]
    scaled = {o: Q(local[o]["prefix_l1_upper"]) * maxima[o] for o in maxima}
    prefix = context["prefix"]
    oldlocal = max(v["prefix_bits_upper"] for v in local.values())
    counts = Counter(e["kind"] for e in template["execution_schedule"])
    need(oldlocal == prefix["local_scalar_coefficient_work_prefix_bits"] and
         counts["local_cover_sweep"] == prefix["complete_invocation_cover_sweeps"] and
         counts["bridge"] == prefix["bridge_factor_two_sweeps"], "old growth charge binding")
    conversion, margin = prefix["stream_input_sup_to_l2_bits"], prefix["primitive_arithmetic_margin_bits"]
    need((conversion, margin) == (37, 4), "inherited conversion/margin")
    need(oldlocal + conversion + counts["local_cover_sweep"] + counts["bridge"] + margin
         == prefix["global_prefix_bits"], "old invoice arithmetic")
    combined = strict_bits(max(Q(boundary_peak), *scaled.values()))
    return dict(events=len(template["execution_schedule"]), event_counts=dict(counts),
                calls=len(entries), helper_roles=len(entries) * HELPERS, cross_replica_roles=cross,
                boundary_peak=boundary_peak, final_replica_bound=bounds[:8],
                all_replica_final_bounds_equal=all(bounds[8*r:8*r+8] == bounds[:8] for r in range(REPLICAS)),
                local_input_maxima=maxima,
                borrowed_exceeds_active_calls=sum(e["helper"] > e["active"] for e in entries),
                source_boundary_table=matrix_table,
                call_inputs=entries, boundary_trace_sha256=trace.hexdigest(),
                local_envelopes={o: str(Q(local[o]["prefix_l1_upper"])) for o in maxima},
                scaled_local_envelopes={o: str(value) for o, value in scaled.items()},
                combined_norm_bits=combined, input_conversion_bits=conversion, arithmetic_margin_bits=margin,
                old_sufficient_bits=prefix["global_prefix_bits"],
                refined_sufficient_bits=combined + conversion + margin,
                retained_payload_bits=prefix["retained_payload_bits"])


def scalar_borrow_witness(context):
    """Identity-unitary contract model before one actual borrow, not a physical replay."""
    template = context["template"]
    calls, recipe, _ = validate_controller(template, context["parent"], context["checks"])
    rows = [{j: 1} for j in range(8 * REPLICAS)]

    def add(target, source, coefficient):
        for j, value in list(rows[source].items()):
            v = rows[target].get(j, 0) + coefficient * value
            if v:
                rows[target][j] = v
            else:
                rows[target].pop(j, None)

    for position, event in enumerate(template["execution_schedule"]):
        kind = event["kind"]
        r = event.get("replica", 0)
        if kind == "local_cover_sweep":
            call = calls[event["stage"], r]
            active = max(sum(map(abs, rows[f // V].values())) for f, _ in call["owners"][:2 * V])
            for helper, (family, route) in enumerate(call["owners"][2 * V:]):
                row = rows[family // V]
                value = sum(map(abs, row.values()))
                if value > active:
                    return dict(event=position, stage=event["stage"], replica=r,
                                helper=helper, family=family, owner_replica=family // (8 * V),
                                active_upper=active, helper_attained=value,
                                helper_row=[[j, x] for j, x in sorted(row.items())],
                                input_nonzero=[[j, 1 if x > 0 else -1] for j, x in sorted(row.items())],
                                model="Scalar identity unitaries; all other initial coordinates zero. Not a physical supplier replay.")
            q = recipe[event["stage"]]
            source, target, coefficient = 8 * r + 2 * q["pair"], 8 * r + 2 * q["pair"] + 1, 1
            if q["reverse"]:
                source, target, coefficient = target, source, -1
            add(target, source, coefficient)
        elif kind == "bridge":
            for side in range(2):
                add(8 * r + 2 * event["dst"] + side,
                    8 * r + 2 * event["src"] + side, event["coefficient"])
        elif kind == "terminal":
            raise AuditError("no early borrowed-input witness")
    raise AuditError("missing borrowed-input witness")


def controls(context):
    rejected = []

    def editable():
        # The immutable local programs are large and are not mutated here.
        value = dict(context["template"])
        value["calls"] = copy.deepcopy(value["calls"])
        value["execution_schedule"] = copy.deepcopy(value["execution_schedule"])
        return value

    def reject(name, mutate, reason):
        value = editable()
        mutate(value)
        try:
            recount(context, value)
        except AuditError as error:
            need(str(error) == reason, name + " rejected by unexpected check: " + str(error))
            rejected.append(dict(name=name, predicate=reason))
        else:
            raise AuditError("accepted mutation: " + name)

    def bridge(t):
        return next(e for e in t["execution_schedule"] if e["kind"] == "bridge")

    reject("doubled_bridge", lambda t: bridge(t).__setitem__("coefficient", 2), "source event projection")
    reject("bridge_wrong_source", lambda t: bridge(t).__setitem__("src", 3), "source event projection")
    reject("wrong_local_orientation", lambda t: t["calls"][0].__setitem__("orientation", "backward"),
           "source local orientation/pair")
    reject("same_family_two_helpers", lambda t: t["calls"][0]["owners"][2*V+1].__setitem__(
        0, t["calls"][0]["owners"][2*V][0]), "one role per physical family")
    reject("helper_aliases_active_data", lambda t: t["calls"][0]["owners"][2*V].__setitem__(0, 0),
           "one role per physical family")
    reject("data_port_permutation", lambda t: t["calls"][0]["owners"].__setitem__(
        slice(0, 2), t["calls"][0]["owners"][1::-1]), "active data family/port binding")
    reject("wrong_program", lambda t: t["calls"][0].__setitem__("local_program_sha256", "0"*64),
           "call program binding")
    reject("missing_event", lambda t: t["execution_schedule"].pop(6), "source event count")
    reject("reordered_events", lambda t: t["execution_schedule"].__setitem__(
        slice(5, 7), t["execution_schedule"][6:4:-1]), "source event chronology")
    reject("unrecognized_event", lambda t: t["execution_schedule"][0].__setitem__("kind", "mix_families"),
           "source event projection")
    try:
        recount(context, entry_cap=7)
    except AuditError as error:
        need(str(error) == "actual owner input cap", "understated cap rejection")
        rejected.append(dict(name="understated_input_cap", predicate=str(error)))
    else:
        raise AuditError("accepted input cap seven")

    # Keep counts, family ranges and uniqueness, but borrow a family after its
    # final bridges raise its majorant to 14. This breaks the eightfold entry
    # bound; it also lies outside the admitted hosting windows.
    late = editable()
    schedule = late["execution_schedule"]
    end = next(i for i, e in enumerate(schedule) if e["kind"] == "terminal")
    replica = schedule[end]["replica"]
    event = next(e for e in schedule[end+1:] if e["kind"] == "local_cover_sweep")
    call = next(c for c in late["calls"] if (c["stage"], c["replica"]) == (event["stage"], event["replica"]))
    used = {f for f, _ in call["owners"]}
    family = next(f for f in range((8*replica+3)*V, (8*replica+4)*V) if f not in used)
    call["owners"][2*V][0] = family
    try:
        recount(context, late)
    except AuditError as error:
        need(str(error) == "actual owner input cap", "late helper rejection")
        rejected.append(dict(name="post_terminal_borrow", predicate=str(error), family=family,
                             stage=event["stage"], replica=event["replica"]))
    else:
        raise AuditError("accepted late helper")
    return rejected


def result(root=ROOT):
    context = load(root)
    local_replay = replay_local(context, root)
    report = recount(context)
    witness = scalar_borrow_witness(context)
    need(witness["helper_attained"] > witness["active_upper"], "borrow witness gap")
    return dict(status="PASS_SELECTED1094_WIRE_PREFIX_AUDIT", source_sha256=context["hashes"],
                local_replay=local_replay, controller=report, borrowed_input_witness=witness,
                controls_rejected=controls(context),
                scope="Conditional exact family-norm bound for the pinned finite controller. "
                      "Local scalar/frame checks replayed unchanged; familywise unitary physical "
                      "realization, cover bijections, recursive internals, roundoff/tape and analytic "
                      "transfer remain inherited. No production charge or kappa change.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a newly checked receipt to a new path")
    args = parser.parse_args()
    receipt = result()
    if args.write:
        with args.write.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(receipt, indent=2) + "\n")
    else:
        need(receipt == json.loads((PACKAGE / "EXPECTED.json").read_bytes()), "committed receipt differs")
    c = receipt["controller"]
    print(receipt["status"], "calls=" + str(c["calls"]),
          "boundary=" + str(c["boundary_peak"]), "entry=8",
          "conditional_bits=" + str(c["old_sufficient_bits"]) + "->" + str(c["refined_sufficient_bits"]),
          "retained_payload=512 no_new_kappa")


if __name__ == "__main__":
    main()
