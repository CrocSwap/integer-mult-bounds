#!/usr/bin/env python3
"""Exact fixed-alphabet lender cleanup certificate; standard library only.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
Apache-2.0. No predecessor replay or arithmetic implementation is imported.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def decode(data):
    return json.loads(data, object_pairs_hook=unique_object)


def canonical(value):
    # JSON encoding distinguishes integer 1 from boolean true.
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sources():
    pins = decode((HERE / "SOURCE-PINS.json").read_bytes())
    need(pins["source_pr"] == 2226 and pins["head"] ==
         "dacaf3d81f1936bb55b8454b1244e5d014272754", "predecessor head binding")
    for entry in pins["files"]:
        data = (HERE / entry["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == entry["sha256"],
             "source SHA256 mismatch: " + entry["path"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        need(hashlib.sha1(blob).hexdigest() == entry["git_blob"],
             "source Git blob mismatch: " + entry["path"])
        if "payload_sha256" in entry:
            need(hashlib.sha256(gzip.decompress(data)).hexdigest()
                 == entry["payload_sha256"], "word payload mismatch")
    return (
        decode(gzip.decompress((HERE / "inputs/word.json.gz").read_bytes())),
        decode((HERE / "inputs/witness.json").read_bytes()),
        decode((HERE / "inputs/blocks.json").read_bytes())["sources"][0]["blocks"],
    )


def incident(gate):
    need(gate[0] in ("add", "scale"), "unknown scalar operation")
    return gate[1:3] if gate[0] == "add" else gate[1:2]


def coefficient(gate):
    return Q(gate[3], gate[4]) if gate[0] == "add" else Q(gate[2], gate[3])


def plus(row, other, factor):
    out = row.copy()
    for index, value in other.items():
        new = out.get(index, Q(0)) + factor * value
        if new:
            out[index] = new
        else:
            out.pop(index, None)
    return out


def scaled(row, factor):
    return {index: factor * value for index, value in row.items() if factor * value}


def serial(row):
    return [[index, str(value)] for index, value in sorted(row.items())]


def span(basis):
    result = {0}
    for vector in basis:
        need(type(vector) is int and 0 <= vector < 512, "nonbinary frame label")
        result |= {vector ^ value for value in tuple(result)}
    need(len(result) == 1 << len(basis), "dependent frame basis")
    return frozenset(result)


def strict_rank_one(before, after):
    need(before < after and len(after) == 2 * len(before),
         "rank-one climb must be a proper nested inclusion")
    return 1


def changed_slots(word, witness, blocks):
    """Reconstruct virtual B instructions before physical alias resolution.

    High corrections move to first input; low early prefixes are replaced.
    The cleanup under study is absent. Observations precede both handoffs.
    """
    skipped = set()
    deferred = defaultdict(list)
    for block in blocks:
        helpers = set(block["helpers"])
        for i in range(block["first_correction"], block["first_input"]):
            gate = word["B"][i]
            if set(incident(gate)) <= helpers:
                need(i not in skipped, "overlapping deferred blocks")
                skipped.add(i)
                deferred[block["first_input"]].append(gate)
    deleted, rewrites = set(), {}
    for pair in witness["pairs"]:
        need(not pair.get("handoff_echo_coefficients"), "unexpected handoff echo")
        if pair["low"]:
            deleted.update(pair.get("deleted_prefix_indices", pair["deleted_echo_indices"]))
            for raw_i, gates in pair.get("early_prefix_rewrites", {}).items():
                i = int(raw_i)
                need(i not in rewrites, "overlapping prefix rewrites")
                rewrites[i] = gates
    result = []
    for i, gate in enumerate(word["B"]):
        events = deferred[i] + rewrites.get(i, [])
        if i not in skipped and i not in deleted:
            events = events + [gate]
        result.append(events)
    return result


def forward_rows(word, witness, slots):
    """Forward propagation on all 512 remaining non-target inputs."""
    v = word["v"]
    removed = {pair["register"] for pair in witness["pairs"]}
    active = set(range(2 * v + word["R"])) - removed
    non_target = active - set(range(v, 2 * v))
    rows = {r: {r: Q(1)} for r in non_target}

    def execute(gate):
        d = gate[1]
        if v <= d < 2 * v:
            return
        need(d in rows, "unallocated forward destination")
        if gate[0] == "scale":
            rows[d] = scaled(rows[d], coefficient(gate))
        else:
            s = gate[2]
            need(s in rows, "non-target reads removed helper or target")
            rows[d] = plus(rows[d], rows[s], coefficient(gate))

    for section in ("precondition", "compensation", "A", "cut"):
        for gate in word[section]:
            if section in ("precondition", "compensation") and gate[0] == "add" and gate[2] in removed:
                need(v <= gate[1] < 2 * v, "removed compensation is not Y-only")
                continue
            execute(gate)
    first_handoff = min(pair["handoff_B"] for pair in witness["pairs"])
    for events in slots[:first_handoff]:
        for gate in events:
            execute(gate)
    return rows, first_handoff, len(active)


def backwards_row(register, raw_prefix):
    """Independent functional pullback through the original 704-role prefix.

    No alias deletion, changed B compilation or forward row-add is used.
    """
    weights = {register: Q(1)}
    for gate in reversed(raw_prefix):
        d = gate[1]
        if d not in weights:
            continue
        if gate[0] == "scale":
            weights[d] *= Q(gate[2], gate[3])
        else:
            s = gate[2]
            weights[s] = weights.get(s, Q(0)) + weights[d] * Q(gate[3], gate[4])
            if not weights[s]:
                del weights[s]
    return weights


def apply_subset(row, source_row, gates, mask):
    for i, gate in enumerate(gates):
        if mask & (1 << i):
            if gate[0] == "add":
                row = plus(row, source_row, coefficient(gate))
            else:
                row = scaled(row, coefficient(gate))
    return row


def check_schedule(components, schedule):
    for c in components:
        times = schedule[c["lender"]]
        need(len(times) == c["gate_count"], "schedule arity")
        need(all(type(time) is int for time in times), "integer event cuts")
        need(c["release_B"] <= times[0] <= c["addition_deadline_B"],
             "addition violates frame release or source withdrawal")
        if len(times) == 2:
            need(times[0] <= times[1] <= c["lender_handoff_B"],
                 "negation violates dependency or lender withdrawal")


def trace_frames(word, witness, slots, schedule):
    """Execute frame transitions in order, including all 80 physical loans.

    This does not use the derived release/deadline intervals. It checks the
    actual before-handoff ordering and subspace inclusions, so an early or
    late mutation is tested against the source event stream itself.
    Logical scalar identities and exact Clifford phases are separate.
    """
    v = word["v"]
    F = list(map(span, word["frames"]))
    removed = {p["register"] for p in witness["pairs"]}
    cur = {r: F[f] for r, f in enumerate(word["start"]) if r not in removed}
    aliases, withdrawn = {}, set()
    profile, cleanup_profile = Counter(), Counter()

    def climb(r, space, cleanup=False):
        need(r in cur and cur[r] <= space, "actual event has a nonnested frame")
        gap = len(space).bit_length() - len(cur[r]).bit_length()
        if gap:
            profile[gap] += 1
            if cleanup:
                cleanup_profile[gap] += 1
        cur[r] = space

    def event(gate, cleanup=False):
        for r in incident(gate):
            if cleanup:
                need(r not in withdrawn, "cleanup reads a withdrawn physical role")
            climb(aliases.get(r, r), F[gate[-1]], cleanup)

    target_pins = {r: word["start"][r] for r in range(v, 2 * v)}
    for section in ("precondition", "compensation"):
        for gate in word[section]:
            for r in incident(gate):
                if v <= r < 2 * v:
                    target_pins[r] = gate[-1]
            if gate[0] == "add" and gate[2] in removed:
                continue
            event(gate)
    for gate in word["A"]:
        event(gate)
    for r, f in target_pins.items():
        climb(r, F[f])
    for r, f in zip(word["centers"], word["center_frames"]):
        need(cur[r] == F[f], "centre frame binding")
        profile[len(F[f]).bit_length() - 1] += 1
    scheduled = defaultdict(list)
    local_indices = Counter()
    for entry in witness["early_tail_events"]:
        d = entry["gate"][1]
        j = local_indices[d]
        local_indices[d] += 1
        scheduled[schedule[d][j]].append(entry["gate"])
    starts = defaultdict(list)
    for pair in witness["pairs"]:
        starts[pair["handoff_B"]].append(pair)
    executed_cleanup = 0
    for i, events in enumerate(slots):
        for gate in scheduled[i]:
            event(gate, cleanup=True)
            executed_cleanup += 1
        for pair in starts[i]:
            old, new = pair["borrow_from"], pair["register"]
            need(old not in withdrawn and new not in aliases, "duplicate physical loan")
            need(cur[old] == F[pair["retirement_frame"]], "actual loan retirement frame")
            entrance = span(pair["handoff_basis"])
            need(len(cur[old]) == len(entrance) and pair["handoff_paid_rank"] == 0,
                 "fixed rank-zero handoff")
            aliases[new] = old
            withdrawn.add(old)
            cur[old] = entrance
        for gate in events:
            event(gate)
    need(len(aliases) == 80, "all physical handoffs traced")
    need(executed_cleanup == 48, "all scheduled cleanup operations executed")
    payload = [[r, sorted(space)] for r, space in sorted(cur.items())]
    return {"through_B_events": len(slots), "handoffs": len(aliases),
            "profile_including_COPY": dict(sorted(profile.items())),
            "cleanup_profile": dict(sorted(cleanup_profile.items())),
            "final_frames_sha256": hashlib.sha256(canonical(payload).encode()).hexdigest()}


def trace_operator_rows(word, witness, slots, schedule):
    """Whole B prefix over exact rationals and noncommuting loan symbols.

    This validates complete prefix equality after retiming, including every
    arbitrary input and the Y endpoint, without asserting native phase or
    final inverse-cleanup coverage. Reference operators are free generators.
    """
    v = word["v"]
    removed = {p["register"] for p in witness["pairs"]}
    rows = {r: {(r, ()): Q(1)} for r in range(2 * v + word["R"]) if r not in removed}
    aliases = {}
    for term in witness["initial_corrections"]:
        key = (term["source"], tuple(term["operator_word"]))
        rows[term["target"]] = plus(rows[term["target"]], {key: Q(1)}, Q(term["coefficient"]))

    def execute(gate):
        d = aliases.get(gate[1], gate[1])
        need(d in rows, "unallocated operator destination")
        if gate[0] == "scale":
            rows[d] = scaled(rows[d], coefficient(gate))
        else:
            s = aliases.get(gate[2], gate[2])
            need(s in rows, "unallocated operator source")
            rows[d] = plus(rows[d], rows[s], coefficient(gate))

    for section in ("precondition", "compensation", "A", "cut"):
        for gate in word[section]:
            if section in ("precondition", "compensation") and gate[0] == "add" and gate[2] in removed:
                continue
            execute(gate)
    scheduled, local_index = defaultdict(list), Counter()
    for entry in witness["early_tail_events"]:
        d = entry["gate"][1]
        scheduled[schedule[d][local_index[d]]].append(entry["gate"])
        local_index[d] += 1
    starts = defaultdict(list)
    for token, pair in enumerate(witness["pairs"], 1):
        starts[pair["handoff_B"]].append((token, pair))
    low_checks = 0
    for i, events in enumerate(slots):
        for gate in scheduled[i]:
            execute(gate)
        for token, pair in starts[i]:
            old = pair["borrow_from"]
            if pair["low"]:
                need(rows[old] == {(old, ()): Q(1)}, "actual low-lender row at handoff")
                low_checks += 1
            transformed = {}
            for (variable, operators), value in rows[old].items():
                reduced = operators[1:] if operators and operators[0] == -token else (token,) + operators
                transformed[variable, reduced] = value
            rows[old] = transformed
            aliases[pair["register"]] = old
        for gate in events:
            execute(gate)
    need(low_checks == 32 and len(aliases) == 80, "complete scalar loan coverage")
    for y in range(v, 2 * v):
        need(rows[y] == {(y, ()): Q(1), (y - v, ()): Q(1)}, "Y endpoint in free operator algebra")
    return rows


def operator_rows_digest(rows):
    data = [[r, [[var, list(ops), str(value)] for (var, ops), value in sorted(row.items())]]
            for r, row in sorted(rows.items())]
    return hashlib.sha256(canonical(data).encode()).hexdigest()


def rejected(function, message):
    try:
        function()
    except ValueError:
        return
    raise ValueError("negative control accepted: " + message)


def analyze(word, witness, blocks):
    v, n = word["v"], 2 * word["v"] + word["R"]
    need((word["h"], v, n) == (9, 112, 704), "source dimensions")
    pairs = witness["pairs"]
    loans = {pair["borrow_from"]: pair for pair in pairs}
    need(len(pairs) == len(loans) == 80, "distinct loan inventory")
    low = {pair["borrow_from"]: pair for pair in pairs if pair["low"]}
    need(len(low) == 32, "low lender inventory")
    tails = witness["early_tail_events"]
    need(len(tails) == 48, "fixed tail alphabet")
    groups, indices = defaultdict(list), set()
    for entry in tails:
        index, gate = entry["old_tail_index"], entry["gate"]
        need(index not in indices and gate == word["tail"][index], "tail source binding")
        indices.add(index)
        groups[gate[1]].append(entry)
    need(set(groups) == set(low), "exact cleanup destinations")
    source_registers = {entries[0]["gate"][2] for entries in groups.values()}
    need(len(source_registers) == 32 and source_registers.isdisjoint(low),
         "independent cleanup components")
    observed = set(low) | source_registers
    frames = list(map(span, word["frames"]))
    slots = changed_slots(word, witness, blocks)
    rows, first_handoff, active_count = forward_rows(word, witness, slots)
    need(active_count == 624 and first_handoff == 1054, "actual prefix boundary")
    raw_prefix = sum((word[s] for s in ("precondition", "compensation", "A", "cut")), [])
    # B only reads these roles until physical withdrawal. This proves that
    # omitted tails in one component cannot affect another component.
    for events in slots:
        for gate in events:
            need(gate[1] not in observed, "B writes a cleanup component")
    for r in sorted(observed):
        need(rows[r] == backwards_row(r, raw_prefix), "forward/backward row disagreement")
    cur = word["start"].copy()
    for section in ("precondition", "compensation", "A"):
        for gate in word[section]:
            for r in incident(gate):
                cur[r] = gate[-1]
    # The cut is logical and unframed in the pinned source contract.
    histories = {r: [] for r in observed}
    for i, events in enumerate(slots):
        for gate in events:
            for r in incident(gate):
                if r in observed:
                    histories[r].append((i, gate[-1], gate))
    components, distribution = [], Counter({(0, 0): 1})
    time_assignments = 1
    for d in sorted(low):
        entries = groups[d]
        gates = [entry["gate"] for entry in entries]
        s = gates[0][2]
        need(gates[0][0] == "add" and coefficient(gates[0]) == -1, "cleanup subtraction")
        need(len(gates) in (1, 2), "component size")
        if len(gates) == 2:
            need(gates[1][0] == "scale" and coefficient(gates[1]) == -1, "cleanup negation")
        need(all(gate[-1] == gates[0][-1] for gate in gates), "common cleanup frame")
        U = frames[gates[0][-1]]
        need(len(U) == 16 and frames[cur[d]] == U and not histories[d],
             "lender stays at rank four before borrowing")
        h = histories[s]
        need(bool(h), "source has no last ordinary read")
        previous = frames[cur[s]]
        for _, frame_id, _ in h:
            after = frames[frame_id]
            need(previous <= after <= U, "ordinary source frame is not nested")
            previous = after
        release = h[-1][0] + 1
        need(all(entry["before_B"] == release for entry in entries), "earliest witness cut")
        need(h[-1][2] == word["B"][release - 1], "raw last-read binding")
        need(len(previous) == 8, "last source read must have rank three")
        strict_rank_one(previous, U)
        need(release < first_handoff, "prefix must cover cleanup release")
        need(not U <= previous, "early-frame obstruction disappeared")
        unit = {d: Q(1)}
        sign = 1 if len(gates) == 1 else -1
        need(rows[d] == plus(rows[s], unit, Q(sign)), "lender row normal form")
        need(rows[s] and all(r < v for r in rows[s]), "source is nonzero pure X data")
        need(d not in rows[s], "source depends on lender dirt")
        own_deadline = low[d]["handoff_B"]
        source_deadline = loans[s]["handoff_B"] if s in loans else None
        upper = min(own_deadline, source_deadline or own_deadline)
        need(release <= upper, "no legal restoration window")
        need(frames[low[d]["retirement_frame"]] == U, "lender retirement frame")
        if s in loans:
            need(frames[loans[s]["retirement_frame"]] == U, "source retirement frame")
        choices, local = [], Counter()
        for mask in range(1 << len(gates)):
            out = apply_subset(rows[d], rows[s], gates, mask)
            restored = out == unit
            need(restored == (mask == (1 << len(gates)) - 1), "non-full local restoration")
            local[mask.bit_count(), int(restored)] += 1
            choices.append({"mask": mask, "gates": mask.bit_count(),
                            "restored": restored, "row": serial(out)})
        nxt = Counter()
        for (cost, restored), count in distribution.items():
            for (dc, dr), multiplicity in local.items():
                nxt[cost + dc, restored + dr] += count * multiplicity
        distribution = nxt
        count = upper - release + 1
        if len(gates) == 2:
            count = count * (own_deadline + 1) - (release + upper) * count // 2
        time_assignments *= count
        components.append({
            "lender": d, "recipient": low[d]["register"], "source": s,
            "gate_count": len(gates), "tail_indices": [e["old_tail_index"] for e in entries],
            "release_B": release, "addition_deadline_B": upper,
            "lender_handoff_B": own_deadline, "source_handoff_B": source_deadline,
            "last_read": {"B_index": release - 1, "gate": h[-1][2]},
            "rank_three_basis": word["frames"][h[-1][1]],
            "rank_four_basis": word["frames"][gates[0][-1]],
            "source_climb_rank": 1, "lender_row": serial(rows[d]),
            "source_row": serial(rows[s]), "subset_choices": choices,
            "full_restore_cut_assignments": count,
        })
    need(Counter(c["gate_count"] for c in components) == {1: 16, 2: 16}, "component census")
    minimum = [min(cost for cost, number in distribution if number == k) for k in range(33)]
    need(minimum == [k + max(0, k - 16) for k in range(33)], "sharp local tradeoff")
    need(sum(distribution.values()) == 2 ** 48 and distribution[48, 32] == 1,
         "complete subset product")
    early = {c["lender"]: [c["release_B"]] * c["gate_count"] for c in components}
    late = {c["lender"]: [c["addition_deadline_B"]] +
            ([c["lender_handoff_B"]] if c["gate_count"] == 2 else []) for c in components}
    check_schedule(components, early)
    check_schedule(components, late)
    early_trace = trace_frames(word, witness, slots, early)
    late_trace = trace_frames(word, witness, slots, late)
    need(early_trace == late_trace, "retiming changes the actual prefix frame bill")
    need(early_trace["cleanup_profile"] == {1: 32}, "32 actual cleanup source climbs")
    early_rows = trace_operator_rows(word, witness, slots, early)
    late_rows = trace_operator_rows(word, witness, slots, late)
    need(early_rows == late_rows, "retiming changes a complete free-operator prefix row")
    controls = Counter()
    for c in components:
        d = c["lender"]
        gates = [e["gate"] for e in groups[d]]
        full_mask = (1 << len(gates)) - 1
        for j in range(len(gates)):
            need(apply_subset(rows[d], rows[c["source"]], gates, full_mask ^ (1 << j)) != {d: Q(1)},
                 "omission control missed")
            controls["single_gate_omission"] += 1
        if len(gates) == 2:
            wrong = apply_subset(rows[d], rows[c["source"]], list(reversed(gates)), 3)
            need(wrong != {d: Q(1)}, "reversed dependency control missed")
            controls["negation_before_subtraction"] += 1
        bad = {r: ts[:] for r, ts in early.items()}
        bad[d][0] -= 1
        rejected(lambda: check_schedule(components, bad), "before last rank-three read")
        rejected(lambda: trace_frames(word, witness, slots, bad), "actual early frame event")
        controls["early_frame_cut"] += 1
        if c["addition_deadline_B"] < c["lender_handoff_B"]:
            bad = {r: ts[:] for r, ts in late.items()}
            bad[d][0] += 1
            rejected(lambda: check_schedule(components, bad), "source borrowed first")
            rejected(lambda: trace_frames(word, witness, slots, bad), "actual source withdrawal")
            controls["source_withdrawal_cut"] += 1
        U = span(c["rank_four_basis"])
        basis = c["rank_three_basis"][:]
        basis[0] = next(x for x in range(1, 512) if x not in U)
        wrong_space = span(basis)
        need(len(wrong_space) == 8, "wrong-axis control must preserve dimension")
        rejected(lambda: strict_rank_one(wrong_space, U), "same rank, wrong subspace")
        controls["equal_rank_wrong_axis"] += 1
        basis = c["rank_three_basis"][:]
        basis[0] ^= basis[1]
        need(span(basis) == span(c["rank_three_basis"]), "equivalent basis control")
        strict_rank_one(span(basis), U)
        controls["equivalent_basis_positive"] += 1
    need(controls["source_withdrawal_cut"] == 5, "source-limited deadlines")
    d = components[0]["lender"]
    wrong = {r + 704: q for r, q in rows[d].items()}
    need(wrong != backwards_row(d, raw_prefix), "input-role binding control")
    controls["wrong_input_roles"] += 1
    changed = decode(canonical(witness))
    changed["initial_corrections"] = []
    rejected(lambda: trace_operator_rows(word, changed, slots, late), "missing initial compensation")
    controls["missing_initial_compensation"] += 1
    changed = decode(canonical(witness))
    changed["initial_corrections"][0]["coefficient"] = str(-Q(changed["initial_corrections"][0]["coefficient"]))
    rejected(lambda: trace_operator_rows(word, changed, slots, late), "wrong initial compensation sign")
    controls["wrong_initial_compensation_sign"] += 1
    return {
        "status": "PASS_ANTICIPATORY_LENDER_CLEANUP",
        "scope": "PR2226 fixed cleanup alphabet, monotone frames, and pre-handoff operand identity; no supplier or kappa claim",
        "source_pr": 2226, "source_head": "dacaf3d81f1936bb55b8454b1244e5d014272754",
        "remaining_inputs": active_count, "forward_non_target_inputs": len(rows),
        "backward_original_inputs": n, "independently_bound_rows": len(observed),
        "lenders": 32, "local_subsets_checked": 96, "global_subsets_certified": 2 ** 48,
        "minimum_gates_for_exactly_k_restored": minimum,
        "all_restored": {"subtractions": 32, "negations": 16, "source_rank_one_climbs": 32,
                         "source_limited_deadlines": 5, "full_restore_cut_assignments": time_assignments},
        "subset_polynomial": "(1+x*y)^16 * (1+2*x+x^2*y)^16",
        "earliest_and_latest_full_B_frame_trace": early_trace,
        "earliest_and_latest_full_B_operator_trace": {
            "arbitrary_input_columns": 624, "output_rows": len(early_rows),
            "low_handoff_row_checks_per_schedule": 32, "Y_endpoint": "Y+=X",
            "complete_rows_sha256": operator_rows_digest(early_rows),
            "scope": "before final inverse cleanup; symbolic operators, not native Gaussian phases"},
        "subset_distribution": [[cost, restored, count] for (cost, restored), count in sorted(distribution.items())],
        "components": components, "controls": dict(sorted(controls.items())),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, help="write a new result file exclusively")
    args = parser.parse_args()
    result = analyze(*sources())
    if args.record:
        with args.record.open("x") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        expected = decode((HERE / "RESULT.json").read_bytes())
        need(canonical(result) == canonical(expected), "typed canonical receipt mismatch")
    print("PASS_ANTICIPATORY_LENDER_CLEANUP lenders=32 subsets=281474976710656 "
          "tail_gates=48 rank1=32 source_deadlines=5 no_new_kappa")


if __name__ == "__main__":
    main()
