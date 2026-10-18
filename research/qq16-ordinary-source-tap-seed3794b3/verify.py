#!/usr/bin/env python3
"""Replay one exact QQ16 ordinary-source tap through the retained tail."""
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PR2093 = PACKAGE / "references/pr2093"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def load_b2():
    path = PR2093 / "verify.py"
    module_name = "qq16_b2_reference"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    module.PACKAGE = PR2093
    module.ROOT = ROOT
    return module


def pre_f0_state(model, b2):
    h = [{} for _ in range(112)]
    for port, coefficient in b2.COEFFICIENTS.items():
        h[port] = {model.bases[port][0]: Q(coefficient)}
    b0 = model.query(0, h)
    initial_a = model.inject(0, b2.A, b0)
    x, y = [row.copy() for row in h], [{} for _ in range(112)]
    for port in b2.A:
        x[port] = b2.linear((-1, initial_a[port]))
        y[port] = b2.linear((-1, x[port]))
    input_a_identity = [str(b2.at_identity(x[p])) for p in b2.A]
    x, y, f0 = model.forward(0, x, y)
    need(not any(f0), "pinned h witness has nonzero F0 history")
    need(not any(x[p] or y[p] for p in b2.A + b2.T),
         "pinned h witness has nonzero selected state after F0")
    return h, x, y, f0, input_a_identity


def add_a_shear(x, y, b2):
    x, y = [row.copy() for row in x], [row.copy() for row in y]
    for source, target in zip(b2.A, b2.T):
        before = b2.linear((1, x[target]), (1, y[target]))
        x[target] = b2.linear((1, x[target]), (1, x[source]))
        y[target] = b2.linear((1, y[target]), (-1, x[source]))
        need(b2.linear((1, x[target]), (1, y[target])) == before,
             "inherited A-to-T shear changed selected sum")
    return x, y


def add_single_tap(x, y, source_port, target_port, b2, sign=-1):
    """Apply X_t += X_u, Y_t -= X_u, or a deliberately wrong-sign control."""
    x, y = [row.copy() for row in x], [row.copy() for row in y]
    before = b2.linear((1, x[target_port]), (1, y[target_port]))
    source = x[source_port].copy()
    x[target_port] = b2.linear((1, x[target_port]), (1, source))
    y[target_port] = b2.linear((1, y[target_port]), (sign, source))
    after = b2.linear((1, x[target_port]), (1, y[target_port]))
    return x, y, before, after, source


def replay_tail(model, template, f0, bx, by, b2):
    empty = lambda: [{} for _ in range(112)]
    banks = [[bx, by]] + [[empty(), empty()] for _ in range(3)]
    histories = {0: f0}
    completed_x = []
    for event in template["recipe"][2:]:
        kind = event["kind"]
        if kind == "bridge":
            src, dst, coefficient = event["src"], event["dst"], event["coefficient"]
            for port in b2.U:
                banks[dst][0][port] = b2.linear(
                    (1, banks[dst][0][port]), (coefficient, banks[src][0][port]))
                banks[src][1][port] = b2.linear(
                    (1, banks[src][1][port]), (-coefficient, banks[dst][1][port]))
        elif kind == "local":
            stage, pair = event["stage"], event["pair"]
            bx0, by0 = banks[pair]
            if event["reverse"]:
                banks[pair] = list(model.backward(stage, stage + 1, bx0, by0))
            else:
                bx0, by0, history = model.forward(stage, bx0, by0)
                banks[pair] = [bx0, by0]
                histories[stage] = history
        else:
            need(kind == "terminal", "unexpected retained-template event")
            completed_x = [row.copy() for pair in banks for row in pair[0]]
            banks = [[by0, [b2.linear((-1, row)) for row in bx0]]
                     for bx0, by0 in banks]

    observations = []
    for bank, pair in enumerate(banks):
        for component, fields in zip(("X", "Y"), pair):
            for port in b2.A + b2.T:
                if fields[port]:
                    observations.append({
                        "kind": "selected", "bank": bank, "component": component,
                        "port": port, "map": {str(k): str(v)
                                                for k, v in sorted(fields[port].items())}})
    for stage, history in sorted(histories.items()):
        for index, row in enumerate(history):
            if row:
                observations.append({
                    "kind": "history", "stage": stage, "index": index,
                    "map": {str(k): str(v) for k, v in sorted(row.items())}})
    for index, row in enumerate(completed_x):
        if row:
            observations.append({
                "kind": "completed-X", "index": index,
                "map": {str(k): str(v) for k, v in sorted(row.items())}})
    return observations


def build_result():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    external = {row["path"]: row for row in manifest["external_references"]}
    for relative, reference in external.items():
        payload = (PACKAGE / relative).read_bytes()
        need(hashlib.sha256(payload).hexdigest() == reference["sha256"],
             "external reference hash: " + relative)
    pr2216_manifest = json.loads(
        (PACKAGE / "references/pr2216/SOURCES.json").read_text())
    for row in pr2216_manifest["files"]:
        if row.get("usage") == "input":
            # The task catalogue records the predecessor's research context;
            # it is not consumed by either mathematical replay. Authenticate its
            # original Git bytes while live computational dependencies stay bound.
            if row["path"] == "docs/research/agent-task-catalog.json":
                payload = subprocess.check_output(
                    ["git", "show", pr2216_manifest["base_commit"] + ":" + row["path"]],
                    cwd=ROOT)
            else:
                payload = (ROOT / row["path"]).read_bytes()
            need(hashlib.sha256(payload).hexdigest() == row["sha256"],
                 "PR2216 base input hash: " + row["path"])

    b2 = load_b2()
    inputs = {row["path"]: row["sha256"] for row in manifest["files"]
              if row["usage"] == "input"}
    need(inputs == b2.INPUTS, "the source inventory differs from PR2093's pinned inputs")
    members, certificate, previous = b2.load_sources()
    word = members["CANONICAL-WORD.json.gz"]
    programs = members["LOCAL-PROGRAMS.json.gz"]
    phases = members["DATA-PHASES.json"]
    template = members["GLOBAL-TEMPLATE.json.gz"]
    R = b2.reconstruct_R(word, programs)
    need(R == [[Q(row.get(str(p), "0")) for p in range(112)]
               for row in certificate["R_rows"]], "operation-derived R binding")
    model = b2.Model(R, phases)
    h, x0, y0, f0, input_a_identity = pre_f0_state(model, b2)
    need(all(model.routes[p][0] == b2.AXES for p in range(112)),
         "the 112 fields do not share the completed(0) coordinate map")

    # The released A-to-T shear alone leaves this witness hidden at B1 and later.
    xa, ya = add_a_shear(x0, y0, b2)
    old_bx, old_by = model.backward(1, 2, xa, ya)
    need(not any(old_bx[p] or old_by[p] for p in b2.A + b2.T),
         "A-to-T-only control no longer erases the selected state")
    old_signature = replay_tail(model, template, f0, old_bx, old_by, b2)
    need(not old_signature, "A-to-T-only control became observable in the retained tail")

    # One ordinary port, one selected pair. The source is left unchanged.
    x, y, before, after, source = add_single_tap(xa, ya, 2, 21, b2, sign=-1)
    need(source == h[2] and source, "U2 is not the pinned live h source")
    need(after == before, "the paired tap did not preserve X21 + Y21")
    bx, by = model.backward(1, 2, x, y)
    observations = replay_tail(model, template, f0, bx, by, b2)
    counts = Counter(row["kind"] for row in observations)
    need(counts == Counter({"selected": 34, "history": 4, "completed-X": 65}),
         "the exact retained-tail observation census changed")
    witness_row = next((row for row in observations
                        if row["kind"] == "selected" and row["bank"] == 0
                        and row["component"] == "X" and row["port"] == 21), None)
    need(witness_row == {"kind": "selected", "bank": 0, "component": "X",
                         "port": 21, "map": {"37": "11"}},
         "expected exact final selected witness changed")

    # An off-support source is an exact negative control.
    wx, wy, _, _, wrong_source = add_single_tap(xa, ya, 1, 21, b2, sign=-1)
    need(not wrong_source, "off-support U1 unexpectedly carries the witness")
    wrong_bx, wrong_by = model.backward(1, 2, wx, wy)
    need(not replay_tail(model, template, f0, wrong_bx, wrong_by, b2),
         "off-support source control unexpectedly became visible")

    # A one-sided mutation is rejected by the paired-sum contract.
    _, _, bad_before, bad_after, bad_source = add_single_tap(xa, ya, 2, 21, b2, sign=1)
    need(bad_source and bad_before != bad_after,
         "wrong-sign control failed to break the selected-sum invariant")

    # Re-run the PR2216 eight-direction witness with this tap at the B1 cut.
    check = subprocess.run([sys.executable, "-I", "-B", str(PACKAGE / "verify_b1_tap.py")],
                           cwd=ROOT, text=True, capture_output=True, check=False, timeout=540)
    need(check.returncode == 0, "eight-direction B1 control failed: " + check.stderr)
    need(check.stdout.splitlines() == [
        "PASS_QQ16_F0_B1_IDENTITY_SHEAR_WITNESS",
        "source_A_rank=8; zero_shear_T_rank=0; A_shear_plus_U2_T21_tap_rank=8",
        "exact_nonzero_8x8_minor_det=-1/4096"], "unexpected eight-direction verifier output")

    return {
        "status": "PASS_QQ16_ORDINARY_SOURCE_TAP",
        "scope": "The exact PR2093 ordinary-source h witness, with the PR2216 A-to-T shear retained and one paired U2-to-T21 tap, through the full retained QQ16 tail.",
        "base_commit": manifest["base_commit"],
        "external_references": external,
        "witness": {
            "definition": "h_p(d)=c_p bit_0(d b_(p,0))",
            "coefficients": {str(p): c for p, c in b2.COEFFICIENTS.items()},
            "post_F0_active_U_ports": [2, 8, 85],
            "pre_F0_B2_and_B1_zero": True,
            "required_initial_A_at_identity": input_a_identity,
        },
        "mechanism": {
            "existing_shear": "X_T += X_A; Y_T -= X_A",
            "added_tap": "X_21 += X_2; Y_21 -= X_2",
            "common_frame": "completed(0), verified identity map on all 112 fields",
            "added_scalar_additions_per_owner": 2,
            "added_helpers": 0,
            "added_recursive_children": 0,
            "coefficient_precision": "unchanged; tap coefficients are +1 and -1",
            "selected_sum_preserved": True,
            "changed_pair_magnitude_envelope": "at most 2x by the triangle bound (one extra magnitude bit charged)",
        },
        "retained_tail": {
            "observable_rows": dict(sorted(counts.items())),
            "exact_final_witness_output": witness_row,
            "at_identity": "11",
            "complete_observations": observations,
        },
        "existing_eight_direction_control": {
            "status": check.stdout.splitlines()[0],
            "post_B1_T_rank": 8,
            "minor_determinant": "-1/4096",
        },
        "negative_controls": {
            "A_to_T_shear_only_full_tail_observations": 0,
            "off_support_U1_tap_full_tail_observations": 0,
            "wrong_sign_breaks_selected_sum": True,
        },
        "limits": [
            "This disables one exact kernel witness; it does not prove full controller injectivity.",
            "The PR2216 eight-direction family is rechecked only at B1, not through the tail.",
            "The one-bit payload envelope is a local triangle bound; global precision, hosting, and supplier admission remain open.",
            "No supplier, selected exponent, or kappa improvement is claimed.",
        ],
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path,
                        help="write the exact receipt exclusively to a new path")
    args = parser.parse_args()
    result = build_result()
    if args.write_result:
        with args.write_result.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        recorded = json.loads((PACKAGE / "RESULT.json").read_text())
        need(canonical(recorded) == canonical(result), "complete canonical receipt mismatch")
    print("PASS_QQ16_ORDINARY_SOURCE_TAP selected=34 histories=4 completedX=65")
    print("tap=U2->T21 additions=2 children=0 tail_output_X21=11*f37 at_identity=11")
    print("PR2216_B1_rank=8; controls=3; no_full_controller; no_kappa")


if __name__ == "__main__":
    main()
