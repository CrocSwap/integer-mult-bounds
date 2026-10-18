#!/usr/bin/env python3
"""Exact three-coordinate temporal-gauge search and replay, standard library only."""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import io
import itertools
import json
from pathlib import Path
import subprocess
import tarfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
PR1380_HEAD = "c2bc6848cffb2e2203095d4c4bbc45b0848c22e7"
PR1380_CERT = HERE / "inputs/PR1380-CERTIFICATE.json"
PR1380_CERT_SHA256 = "3c59f72bcd0768bf0740edebcb09427bcd48659b8bcbba762a0e30ca53aa2afc"
PR1380_CERT_BLOB = "3f388682c45974d910a2629aaca523984dd429a5"
COORDS = (225, 350, 367)
BOUND = 4
VALUES = tuple(range(-BOUND, BOUND + 1))
PREFIX = "candidate/strict/global8/base/providers/gauge44/"
SOURCE_FILES = {
    "research/community-frontier1042-audit/selected-replay.tar.gz":
        "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754",
    "research/community-frontier1094-audit/selected-replay.tar.gz":
        "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6",
    "research/complex-dyadic-lowering/lower.py":
        "eb37d00063dc09323e9aca041d23da749ce17fbd71dade9aaf1c059cab0b9753",
}
MEMBERS = {
    "CANONICAL-WORD.json.gz": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "LOCAL-PROGRAMS.json.gz": "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
    "INDEPENDENT-LOCAL-REPLAY.json": "13dd18297162569532983db1a2ab67926b064330cd7edd3587e7b546b2dedf17",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def expect_error(action, message):
    try:
        action()
    except (ValueError, KeyError, IndexError):
        return
    raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_bytes(path):
    return subprocess.run(["git", "show", BASE + ":" + path], cwd=ROOT,
                          check=True, capture_output=True).stdout


def load_lowerer():
    spec = importlib.util.spec_from_file_location("seed21_lower", HERE / "inputs/lower.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.lower


def load_inputs():
    require((HERE / "inputs/lower.py").read_bytes() == source_bytes("research/complex-dyadic-lowering/lower.py"),
            "vendored lowerer differs from pinned base")
    archive = source_bytes("research/community-frontier1094-audit/selected-replay.tar.gz")
    require(sha(archive) == SOURCE_FILES["research/community-frontier1094-audit/selected-replay.tar.gz"],
            "PR1094 archive pin")
    extracted = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tf:
        for name, digest in MEMBERS.items():
            raw = tf.extractfile(PREFIX + name).read()
            require(sha(raw) == digest, "PR1094 archive member pin " + name)
            packaged_name = {
                "CANONICAL-WORD.json.gz": "PR1094-CANONICAL-WORD.json.gz",
                "LOCAL-PROGRAMS.json.gz": "PR1094-LOCAL-PROGRAMS.json.gz",
                "INDEPENDENT-LOCAL-REPLAY.json": "PR1094-INDEPENDENT-LOCAL-REPLAY.json",
            }[name]
            require((HERE / "inputs" / packaged_name).read_bytes() == raw, "packaged PR1094 input drift " + name)
            extracted[name] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    # PR1380 established that PR1094 and PR1042 retain the same local provider
    # word. Recheck that alias directly from the two exact base-pinned archives.
    old_archive = source_bytes("research/community-frontier1042-audit/selected-replay.tar.gz")
    require(sha(old_archive) == SOURCE_FILES["research/community-frontier1042-audit/selected-replay.tar.gz"],
            "PR1042 archive pin")
    with tarfile.open(fileobj=io.BytesIO(old_archive), mode="r:gz") as tf:
        for name, digest in MEMBERS.items():
            old_raw = tf.extractfile("slots/local/" + name).read()
            packaged_name = {
                "CANONICAL-WORD.json.gz": "PR1094-CANONICAL-WORD.json.gz",
                "LOCAL-PROGRAMS.json.gz": "PR1094-LOCAL-PROGRAMS.json.gz",
                "INDEPENDENT-LOCAL-REPLAY.json": "PR1094-INDEPENDENT-LOCAL-REPLAY.json",
            }[name]
            require(sha(old_raw) == digest and old_raw == (HERE / "inputs" / packaged_name).read_bytes(),
                    "PR1042/PR1094 local provider alias " + name)
    word = extracted["CANONICAL-WORD.json.gz"]
    programs = extracted["LOCAL-PROGRAMS.json.gz"]
    receipt = extracted["INDEPENDENT-LOCAL-REPLAY.json"]
    require(receipt["status"] == "PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY",
            "PR1094 independent local replay receipt")
    require(receipt["canonical_word_sha256"] == MEMBERS["CANONICAL-WORD.json.gz"], "word receipt binding")
    require(receipt["local_programs_sha256"] == MEMBERS["LOCAL-PROGRAMS.json.gz"], "program receipt binding")
    require((word["v"], word["h"], word["R"]) == (112, 9, 480), "PR1094 geometry")
    require(set(programs) == {"forward", "backward"}, "both orientations present")
    selected = json.loads(source_bytes("certificates/selected-result.json"))
    require(selected["kappa"] == "836330098538459/500000000000000000", "selected frontier at pinned base")
    excluded = set(word["centers"])
    for events in programs.values():
        for event in events:
            if event[0] == "residual_adapter":
                excluded.add(event[2])
            if event[0] == "scalar" and event[1][0] in ("copy", "clear"):
                excluded.update(register[1] for register in event[1][1:]
                                if isinstance(register, list) and register[0] == "L")
    eligible = [h for h in range(224, 704) if h not in excluded
                and word["start"][h] == 0 and word["final"][h] == 1]
    require(all(h in eligible for h in COORDS), "seed-selected helpers are not eligible")
    return word, programs, receipt, load_lowerer(), selected["kappa"], len(eligible)


def price(q):
    """PR696 exact real-component ADD lowerer length for a dyadic coefficient."""
    a, d = abs(q.numerator), q.denominator
    require(a > 0 and d & (d - 1) == 0, "nonzero dyadic coefficient")
    v = (a & -a).bit_length() - 1
    odd, exponent = a >> v, v - (d.bit_length() - 1)
    return 1 + odd.bit_length() + odd.bit_count() + abs(exponent) - int(odd == 1 and exponent == 0)


def power(k):
    return Q(2) ** k


def l1(a, b):
    return sum(abs(x - y) for x, y in zip(a, b))


def blocks(events, helpers):
    """Incident ADD runs, separated at every nonscalar word event."""
    answer, current = [], []
    for i, event in enumerate(events):
        if event[0] != "scalar":
            if current:
                answer.append(current)
                current = []
            continue
        gate = event[1]
        if gate[0] != "add":
            continue
        target, source = gate[1:3]
        signs = tuple(int(target == ["L", h]) - int(source == ["L", h]) for h in helpers)
        if any(signs):
            q = Q(gate[3], gate[4])
            current.append((i, q, signs))
    if current:
        answer.append(current)
    return answer


def distance_transform(costs, dimensions):
    """Min-plus L1 transform on the integer grid; retain original argmins."""
    states = tuple(costs)
    origins = {state: state for state in states}
    costs = dict(costs)
    n = len(next(iter(states)))
    for axis in range(n):
        other_axes = [j for j in range(n) if j != axis]
        groups = itertools.product(*(dimensions[j] for j in other_axes))
        new_costs, new_origins = {}, {}
        for other in groups:
            line = []
            for value in dimensions[axis]:
                state = [0] * n
                state[axis] = value
                for j, v in zip(other_axes, other):
                    state[j] = v
                line.append(tuple(state))
            base_cost = [costs[s] for s in line]
            base_origin = [origins[s] for s in line]
            forward, best = [], None
            for j in range(len(line)):
                direct = (base_cost[j], base_origin[j])
                best = direct if best is None else min(direct, (best[0] + 1, best[1]))
                forward.append(best)
            backward, best = [None] * len(line), None
            for j in range(len(line) - 1, -1, -1):
                direct = (base_cost[j], base_origin[j])
                best = direct if best is None else min(direct, (best[0] + 1, best[1]))
                backward[j] = best
            for j, state in enumerate(line):
                value, origin = min(forward[j], backward[j])
                new_costs[state] = value
                new_origins[state] = origin
        costs, origins = new_costs, new_origins
    return costs, origins


def optimize(event_blocks, helpers, bound=BOUND):
    dimensions = tuple(tuple(range(-bound, bound + 1)) for _ in helpers)
    states = tuple(itertools.product(*dimensions))
    zero = tuple(0 for _ in helpers)
    schedule, total = [], 0
    per_block = []
    for block in event_blocks:
        infinity = 10 ** 30
        dp = {s: (0 if s == zero else infinity) for s in states}
        parents = []
        for _, q, signs in block:
            transformed, origins = distance_transform(dp, dimensions)
            next_dp = {}
            for state in states:
                exponent = sum(k * sign for k, sign in zip(state, signs))
                next_dp[state] = transformed[state] + price(q * power(exponent)) - price(q)
            dp = next_dp
            parents.append(origins)
        final_cost, state = min((v + l1(s, zero), s) for s, v in dp.items())
        path = [None] * len(block)
        for i in range(len(block) - 1, -1, -1):
            path[i] = state
            state = parents[i][state]
        require(state == zero, "DP path does not start at zero")
        block_rows = [(event_index, *state) for (event_index, _, _), state in zip(block, path)]
        schedule.extend(block_rows)
        total += final_cost
        per_block.append({"first_event": block[0][0], "last_event": block[-1][0],
                          "incident_adds": len(block), "real_delta": final_cost})
    return schedule, total, per_block


def schedule_cost(event_blocks, schedule, helpers, bound=BOUND):
    expected = [row[0] for block in event_blocks for row in block]
    require([row[0] for row in schedule] == expected, "schedule coverage or order")
    by_index = {row[0]: tuple(row[1:]) for row in schedule}
    require(len(by_index) == len(schedule), "duplicate schedule row")
    total = 0
    zero = tuple(0 for _ in helpers)
    for block in event_blocks:
        old = zero
        for index, q, signs in block:
            state = by_index[index]
            require(len(state) == len(helpers) and all(type(k) is int and -bound <= k <= bound for k in state),
                    "schedule exponent domain")
            exponent = sum(k * sign for k, sign in zip(state, signs))
            total += l1(old, state) + price(q * power(exponent)) - price(q)
            old = state
        total += l1(old, zero)
    return total


def transform(events, word, helpers, schedule):
    block_rows = [row for row in schedule]
    by_index = {row[0]: tuple(row[1:]) for row in block_rows}
    require(len(by_index) == len(block_rows), "duplicate schedule event")
    current = tuple(0 for _ in helpers)
    frames = [word["start"][h] for h in helpers]
    result, scale_macros, scale_work = [], 0, 0

    def move(new):
        nonlocal current, scale_macros, scale_work
        for j, h in enumerate(helpers):
            delta = new[j] - current[j]
            if delta:
                q = power(delta)
                result.append(["scalar", ["scale", ["L", h], q.numerator, q.denominator], frames[j]])
                scale_macros += 1
                scale_work += abs(delta)
        current = new

    for index, original in enumerate(events):
        event = deepcopy(original)
        if event[0] != "scalar":
            move(tuple(0 for _ in helpers))
        if index in by_index:
            move(by_index[index])
            gate = event[1]
            signs = tuple(int(gate[1] == ["L", h]) - int(gate[2] == ["L", h]) for h in helpers)
            exponent = sum(k * sign for k, sign in zip(current, signs))
            q = Q(gate[3], gate[4]) * power(exponent)
            gate[3:5] = [q.numerator, q.denominator]
        result.append(event)
        if event[0] == "climb" and event[2] in helpers:
            j = helpers.index(event[2])
            require(frames[j] == event[3], "helper frame chronology")
            frames[j] = event[4]
    move(tuple(0 for _ in helpers))
    return result, scale_macros, scale_work


def apply(op, rows):
    tag, target = op[0], tuple(op[1])
    if tag == "clear":
        rows[target] = {}
    elif tag == "copy":
        rows[target] = dict(rows[tuple(op[2])])
    elif tag in ("scale", "double", "halve", "negate"):
        q = Q(op[2], op[3]) if tag == "scale" else {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
        rows[target] = {i: q * a for i, a in rows[target].items() if q * a}
    elif tag in ("add", "subtract"):
        source = tuple(op[2])
        q = Q(op[3], op[4]) if len(op) == 5 else Q(1 if tag == "add" else -1)
        for i, a in rows[source].items():
            value = rows[target].get(i, Q(0)) + q * a
            if value:
                rows[target][i] = value
            else:
                rows[target].pop(i, None)
    else:
        raise ValueError("unknown primitive " + tag)


def replay(events, orientation):
    rows = {("L", i): {i: Q(1)} for i in range(704)}
    rows.update({("C", i): {704 + i: Q(1)} for i in range(8)})
    for event in events:
        if event[0] == "scalar":
            gate = event[1]
            if gate[0] == "add":
                op = ["add", gate[1], gate[2], gate[3], gate[4]]
            else:
                op = gate
            apply(op, rows)
    for i in range(704):
        expected = {i: Q(1)}
        if orientation == "forward" and 112 <= i < 224:
            expected[i - 112] = Q(1)
        if orientation == "backward" and i < 112:
            expected[i + 112] = Q(-1)
        require(rows["L", i] == expected, "712-column endpoint " + str((orientation, i)))
    require(all(not rows["C", i] for i in range(8)), "private center cleanup")


def frame_check(events, word, helpers):
    frames = {h: word["start"][h] for h in helpers}
    for event in events:
        if event[0] == "climb" and event[2] in helpers:
            require(frames[event[2]] == event[3], "helper climb incidence")
            frames[event[2]] = event[4]
        elif event[0] == "scalar":
            gate = event[1]
            for h in helpers:
                if ["L", h] in gate:
                    require(frames[h] == event[2], "helper scalar frame")
                    require(gate[0] in ("add", "scale"), "eligible helper used by COPY/CLEAR")
        elif event[0] == "residual_adapter":
            require(event[2] not in helpers, "eligible helper used by residual adapter")
    require(all(frames[h] == word["final"][h] for h in helpers), "helper final frame")


def invoice(events, lower):
    env = {("L", i): Q(1) for i in range(704)}
    env.update({("C", i): Q(1) for i in range(8)})
    env["W", 0] = Q(1)
    depths = {r: 0 for r in env}
    peak, max_depth, count = Q(1), 0, 0
    paid = Counter()
    for event in events:
        if event[0] == "climb":
            paid[event[5]] += 1
        if event[0] == "center":
            paid[event[4]] += 1
        if event[0] != "scalar":
            continue
        gate = event[1]
        op = ["add", gate[1], gate[2], gate[3], gate[4]] if gate[0] == "add" else gate
        for primitive in lower(op):
            count += 1
            tag, target = primitive[0], tuple(primitive[1])
            if tag == "clear":
                env[target], depths[target] = Q(0), 0
            elif tag == "copy":
                env[target], depths[target] = env[tuple(primitive[2])], depths[tuple(primitive[2])]
            elif tag == "double":
                env[target] *= 2
                depths[target] = max(0, depths[target] - 1)
            elif tag == "halve":
                env[target] /= 2
                depths[target] += 1
            elif tag in ("add", "subtract"):
                env[target] += env[tuple(primitive[2])]
                depths[target] = max(depths[target], depths[tuple(primitive[2])])
            else:
                require(tag == "negate", "literal primitive tag")
            peak = max(peak, env[target])
            max_depth = max(max_depth, depths[target])
        if gate[0] == "add":
            require(env["W", 0] == 0, "arbitrary coefficient work cleared")
    bits = peak.numerator.bit_length() - peak.denominator.bit_length() + 1
    require(bits + max_depth < 192, "local signed fixed-point payload guard")
    return {"complex_primitives": 2 * count, "real_primitives": count,
            "prefix_l1": str(peak), "prefix_bits": bits,
            "grid_depth_upper": max_depth,
            "paid_profile": {str(k): v for k, v in sorted(paid.items())}}


def literal_price_check(events, lower):
    coefficients = set()
    for event in events:
        if event[0] == "scalar" and event[1][0] == "add":
            coefficients.add(Q(event[1][3], event[1][4]))
    for q in coefficients:
        op = ["add", ["L", 0], ["L", 1], q.numerator, q.denominator]
        rows = {("L", 0): {0: Q(1)}, ("L", 1): {1: Q(1)}, ("W", 0): {2: Q(1)}}
        for primitive in lower(op):
            apply(primitive, rows)
        require(rows == {("L", 0): {0: Q(1), 1: q}, ("L", 1): {1: Q(1)}, ("W", 0): {}},
                "literal arbitrary-work ADD map")
        require(len(lower(op)) == price(q), "literal ADD price")
    return len(coefficients)


def run():
    word, programs, receipt, lower, selected_kappa, eligible_helpers = load_inputs()
    cert_bytes = PR1380_CERT.read_bytes()
    require(sha(cert_bytes) == PR1380_CERT_SHA256, "PR1380 certificate SHA256")
    blob = subprocess.run(["git", "hash-object", str(PR1380_CERT)], cwd=ROOT,
                          check=True, capture_output=True, text=True).stdout.strip()
    require(blob == PR1380_CERT_BLOB, "PR1380 certificate Git blob")
    predecessor = json.loads(PR1380_CERT.read_bytes())
    require(predecessor["base"] == BASE and predecessor["seed"] == 23, "PR1380 control base/seed")
    output = {"schema_version": 1, "base_commit": BASE, "selected_kappa_at_base": selected_kappa,
              "seed": 21, "eligible_helper_count": eligible_helpers,
              "coordinates": list(COORDS), "domain": [-BOUND, BOUND], "status": "PASS_K8_THREE_COORDINATE_TEMPORAL"}
    orient_results = {}
    total_adds = 0
    total_blocks = 0
    total_opt = 0
    total_pair = 0
    for orientation in ("forward", "backward"):
        events = programs[orientation]
        event_blocks = blocks(events, COORDS)
        schedule, optimum, block_rows = optimize(event_blocks, COORDS)
        require(schedule_cost(event_blocks, schedule, COORDS) == optimum, "DP/certificate objective")
        zero_schedule = [(index, 0, 0, 0) for block in event_blocks for index, _, _ in block]
        require(schedule_cost(event_blocks, zero_schedule, COORDS) == 0, "zero-schedule objective")
        zero_word, zero_macros, zero_work = transform(events, word, COORDS, zero_schedule)
        require(zero_word == events and zero_macros == zero_work == 0, "zero-schedule identity")
        expect_error(lambda: schedule_cost(event_blocks, schedule[1:], COORDS), "missing schedule row accepted")
        outside = list(schedule)
        outside[0] = (outside[0][0], BOUND + 1, *outside[0][2:])
        expect_error(lambda: schedule_cost(event_blocks, outside, COORDS), "out-of-domain exponent accepted")
        candidate, macros, scale_work = transform(events, word, COORDS, schedule)
        frame_check(candidate, word, COORDS)
        replay(events, orientation)
        replay(candidate, orientation)
        baseline_invoice = invoice(events, lower)
        candidate_invoice = invoice(candidate, lower)
        objective_delta = candidate_invoice["real_primitives"] - baseline_invoice["real_primitives"]
        require(objective_delta == optimum, "complete invoice differs from DP")
        require(candidate_invoice["paid_profile"] == baseline_invoice["paid_profile"], "paid profile changed")
        candidate_sha = sha(canonical(candidate))
        bad_coefficient = deepcopy(candidate)
        for event in bad_coefficient:
            if event[0] == "scalar" and event[1][0] == "add":
                # Event indices are preserved only before inserted scales, so
                # locate the unique source operation by its 225/350 operands.
                gate = event[1]
                if {tuple(gate[1]), tuple(gate[2])} == {("L", 225), ("L", 350)}:
                    gate[3] = -gate[3]
                    break
        expect_error(lambda: replay(bad_coefficient, orientation), "wrong-sign shared ADD survived replay")

        # Pairwise positive control: replay PR1380's exact 225/350 winner and
        # independently recover its bounded optimum value before adding L367.
        pair = (225, 350)
        pair_blocks = blocks(events, pair)
        pair_result = predecessor["orientations"][orientation]
        pair_rows = pair_result["schedule"]
        pair_opt_schedule, pair_optimum, _ = optimize(pair_blocks, pair)
        pair_delta = schedule_cost(pair_blocks, pair_rows, pair)
        pair_candidate, pair_macros, pair_scale_work = transform(events, word, pair, pair_rows)
        pair_invoice = invoice(pair_candidate, lower)
        require(pair_delta == pair_result["winner"]["delta_real"], "PR1380 pair objective control")
        require(sha(canonical(pair_candidate)) == pair_result["candidate_sha256"], "PR1380 pair replay hash")
        require(pair_invoice["complex_primitives"] == pair_result["after"]["complex_primitives"],
                "PR1380 pair complete invoice")
        require(pair_optimum == pair_delta, "PR1380 pair schedule not optimal under independent DP")

        orient_results[orientation] = {
            "incident_adds": sum(len(b) for b in event_blocks),
            "block_count": len(event_blocks), "blocks": block_rows,
            "domain_states_per_incident_add": (2 * BOUND + 1) ** len(COORDS),
            "distance_transform_relaxations": sum(len(b) for b in event_blocks) *
                (2 * BOUND + 1) ** len(COORDS) * len(COORDS) * 2,
            "schedule": schedule, "real_delta": optimum,
            "complex_delta": 2 * optimum, "inserted_scale_macros": macros,
            "scale_real_work": scale_work, "baseline_invoice": baseline_invoice,
            "candidate_invoice": candidate_invoice, "candidate_sha256": candidate_sha,
            "additional_real_delta_vs_PR1380_pair": optimum - pair_delta,
            "additional_complex_saving_vs_PR1380_pair": 2 * (pair_delta - optimum),
            "predecessor_pair": {"pair": list(pair), "shared_control_delta_real": pair_delta,
                                  "pair_optimum_real": pair_optimum,
                                  "inserted_scale_macros": pair_macros,
                                  "scale_real_work": pair_scale_work,
                                  "complete_invoice": pair_invoice},
        }
        total_adds += orient_results[orientation]["incident_adds"]
        total_blocks += len(event_blocks)
        total_opt += optimum
        total_pair += pair_delta
    # Exact source-event topology and the seed-derived scope are part of the result.
    forward_events = programs["forward"]
    shared = {}
    for i, event in enumerate(forward_events):
        if event[0] != "scalar" or event[1][0] != "add":
            continue
        target, source = event[1][1:3]
        touched = {h for h in COORDS if target == ["L", h] or source == ["L", h]}
        if len(touched) >= 2:
            shared[str(i)] = sorted(touched)
    require(shared == {"19531": [225, 367], "22786": [225, 350]}, "shared-event support")
    output.update({"orientations": orient_results,
                   "incident_adds_both_orientations": total_adds,
                   "blocks_both_orientations": total_blocks,
                   "shared_adds_forward": shared,
                   "joint_real_delta_sum": total_opt,
                   "pair_control_real_delta_sum": total_pair,
                   "unique_add_coefficients_checked_forward": literal_price_check(programs["forward"], lower)})
    # Candidate lowerer coverage is checked for each orientation without retaining
    # two more event streams in the certificate.
    candidate_coeff_counts = {}
    for orientation in ("forward", "backward"):
        events = programs[orientation]
        candidate, _, _ = transform(events, word, COORDS, orient_results[orientation]["schedule"])
        candidate_coeff_counts[orientation] = literal_price_check(candidate, lower)
    output["unique_add_coefficients_checked_candidate"] = candidate_coeff_counts
    output["controls"] = {"predecessor_pair_replay_and_optimum": "PASS",
                          "zero_schedule_identity": "PASS",
                          "missing_schedule_event_rejected": "PASS",
                          "out_of_domain_exponent_rejected": "PASS",
                          "wrong_sign_shared_ADD_rejected_by_712_column_replay": "PASS",
                          "three_coordinate_shared_event_support": "PASS"}
    output["predecessor"] = {"pr": 1380, "head": PR1380_HEAD,
                             "certificate_sha256": PR1380_CERT_SHA256,
                             "certificate_git_blob": PR1380_CERT_BLOB}
    output["source_receipt"] = receipt["status"]
    return output


def main():
    result = run()
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS_K8_THREE_COORDINATE_TEMPORAL")
    for orientation in ("forward", "backward"):
        row = result["orientations"][orientation]
        print(orientation, "incident_adds", row["incident_adds"], "blocks", row["block_count"],
              "real_delta", row["real_delta"], "complex_delta", row["complex_delta"],
              "complex_primitives", row["candidate_invoice"]["complex_primitives"],
              "scales", row["inserted_scale_macros"], "all712=pass")
    print("shared_adds", result["shared_adds_forward"], "pair_control", result["pair_control_real_delta_sum"])


if __name__ == "__main__":
    main()
