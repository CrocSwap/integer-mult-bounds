"""Check all QQ16 owner paths, native phases, and local invoices.

Adapted from the independent full-cover QQ16 review. No emitter is
imported. New code is Apache-2.0. Verification used Codex assistance.
"""

from collections import Counter
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache


def need(value, reason):
    if not value:
        raise ValueError(reason)


def bits(value):
    while value:
        bit = value & -value
        yield bit.bit_length() - 1
        value ^= bit


AXES = tuple(1 << i for i in range(73))
UNIT_MAP = (AXES, 0)


def act(columns, vector):
    result = 0
    for i in bits(vector):
        result ^= columns[i]
    return result


def product(left, right):
    g, a = left
    h, b = right
    return tuple(act(g, v) for v in h), a ^ act(g, b)


@lru_cache(None)
def inverse(mapping):
    g, a = mapping
    gt = tuple(sum(((g[j] >> i) & 1) << j for j in range(73)) for i in range(73))
    result = gt, act(gt, a)
    need(product(mapping, result) == product(result, mapping) == UNIT_MAP, "Both affine inverse orders")
    return result


def terms(entries):
    counts = Counter()
    for axis, value in entries:
        need(0 <= axis < 1 << 73, "A 73-bit line")
        if axis:
            counts[axis] = (counts[axis] + value) % 4
    return tuple((axis, value) for axis, value in sorted(counts.items()) if value)


@lru_cache(None)
def polynomial(frame):
    # XOR expansion modulo four has degree at most two.
    linear, cross = [0] * 73, [0] * 73
    for axis, value in frame:
        support = tuple(bits(axis))
        for i in support:
            linear[i] = (linear[i] + value) % 4
            if value % 2:
                for j in support:
                    if j > i:
                        cross[i] ^= 1 << j
    return tuple(linear), tuple(cross)


@lru_cache(None)
def move_frame(frame, mapping):
    columns, shift = mapping
    return terms([(act(columns, axis), value) for axis, value in frame]
                 + [(AXES[j], 2) for j in bits(shift)])


def completed(stage):
    return terms((axis, 1) for axis in AXES[:9 + 8 * stage])


def register(token):
    name, index = token
    need(name in ("L", "C") and 0 <= index < (704 if name == "L" else 8), "Declared register")
    return index + (704 if name == "C" else 0)


def verify(data, packet, scalar, scalar_cost):
    core, word = data["clean_programs"], data["word"]
    need(packet["core_words"] == core, "Both retained source words")
    A, T, U = (packet[key] for key in ("A_ports", "T_ports", "U_ports"))
    need((A, T) == ([0, 7, 20, 27, 36, 46, 57, 111], [21, 37, 47, 76, 81, 87, 92, 110]), "Exact selected minors")
    need(U == [p for p in range(112) if p not in A + T], "Ordinary ports")
    labels = word["ports"]
    basis, route, beta = [], [], []
    phases = data["phases"]
    need(phases["m"] == 73 and len(phases["recipes"]) == 112, "Actual phase source dimensions")
    for p, record in enumerate(phases["recipes"]):
        b = tuple([record["q"]] + record["idle_children"][0]["orthogonal_axes"][:8]) + AXES[9:]
        need(record["port"] == p and b[0] == labels[p], "Actual source port and normal")
        need(all(((b[i] & b[j]).bit_count() % 2) == (i == j) for i in range(9) for j in range(9)),
             "Actual source chart is orthonormal")
        basis.append(b)
        coefficient = sum(1 << i for i, v in enumerate(b[1:9]) if (v.bit_count() - 1) // 2 % 2)
        beta.append(coefficient)
        stages = []
        for stage in range(9):
            if stage == 0:
                actual = AXES
                entry = exit_value = 0
            else:
                swaps = [b[i+1] ^ AXES[9+8*(stage-1)+i] for i in range(8)]
                actual = tuple(v ^ act(swaps, sum(((v & axis).bit_count() % 2) << i for i, axis in enumerate(swaps))) for v in AXES)
                entry = labels[p] ^ act(b[1:9], coefficient)
                exit_value = act(b[1:9], coefficient) ^ (coefficient << (9+8*(stage-1)))
            need(product((actual, 0), (actual, 0)) == UNIT_MAP, "Actual route involution")
            expected = {"entry_X": entry, "entry_Y": entry, "exit_X": exit_value, "exit_Y": exit_value}
            need(record["stage_alignment"][stage] == expected, "Actual source entry and exit translations")
            stages.append(actual)
        route.append(stages)

    @lru_cache(None)
    def alignment(side, stage, port):
        if stage == 0:
            need(side == "X", "Only completed X has a stage-zero alignment")
            return UNIT_MAP
        shift = beta[port] << (9 + 8 * (stage - 1))
        shift ^= labels[port] if side == "Y" else act(basis[port][1:9], beta[port])
        return route[port][stage], shift

    maps = {key: (tuple(value["owner_right_matrix_columns"]), value["payload_translation_at_identity_owner"])
            for key, value in packet["map_registry"].items()}
    for key, mapping in maps.items():
        need(len(mapping[0]) == 73 and 0 <= mapping[1] < 1 << 73, "Map dimensions")
        inverse(mapping)
        need(packet["map_registry"][key]["action"] == "out(d,z_1,...,z_lambda)=in(d*g,z_1 XOR d*delta,...,z_lambda XOR d*delta)", "Owner action declaration")
    frames = {}
    for key, value in packet["native_frame_registry"].items():
        phase = polynomial(terms(value["line_terms_Z4"]))
        need(phase == (tuple(value["linear_Z4"]), tuple(value["quadratic_rows"])), "Exact frame polynomial")
        frames[key] = phase

    def mono(recipe, address):
        indices = tuple(bits(address))
        exponent = recipe["phase"] + sum(recipe["linear_Z4"][j] for j in indices)
        exponent += 2 * sum(((recipe["quadratic_rows"][j] & address).bit_count()) for j in indices)
        mapped = recipe["offset"]
        for j, row in enumerate(recipe["matrix_rows"]):
            mapped ^= ((row & address).bit_count() % 2) << j
        return mapped, exponent % 4

    def kernel(recipe, address):
        middle, phase = mono(recipe["right"], address)
        result = {}
        for at, value in ((middle, (1, 1)), (middle ^ 1, (1, -1))):
            dest, other = mono(recipe["left"], at)
            a, b = value
            for _ in range((phase + other) % 4):
                a, b = -b, a
            old = result.get(dest, (0, 0))
            result[dest] = (old[0] + a, old[1] + b)
        return {key: value for key, value in result.items() if value != (0, 0)}

    lines = packet["native_line_recipes"]
    kernel_columns = 0
    for key, item in lines.items():
        port, sign, q = item["port"], item["sign"], item["label"]
        need(port in A + T and sign in (-1, 1) and q == labels[port], "Exact used native line")
        need(item["rank"] == item["recipe"]["rank"] == 1, "Single rank-one child")
        want = item["recipe"]
        for side in ("left", "right"):
            need(all(row >> (j+1) << (j+1) == row for j, row in enumerate(want[side]["quadratic_rows"])), "Strict upper quadratic rows")
        for address in range(512):
            need(kernel(item["recipe"], address) == {address: (1, sign), address ^ q: (1, -sign)}, "Exact Gaussian line column")
            kernel_columns += 1
        bad = deepcopy(item["recipe"])
        bad["left"]["phase"] += 1
        need(kernel(bad, 0) != kernel(item["recipe"], 0), "Scalar phase control")
    need(len(lines) == 32, "All signed selected lines")
    core_profiles = {}
    for side, events in core.items():
        state, profile = word["start"][:] + [None] * 8, Counter()
        for event in events:
            if event[0] == "climb":
                _, _, at, old, new, rank = event
                need(state[at] == old, "Retained child entry frame")
                state[at] = new
                profile[rank] += 1
            elif event[0] == "scalar":
                gate, frame = event[1:]
                at = register(gate[1])
                if gate[0] == "clear":
                    need(at >= 704, "Retained clear is owned")
                    state[at] = frame
                else:
                    need(state[at] == frame, "Retained scalar target")
                    if gate[0] == "add":
                        need(state[register(gate[2])] == frame and gate[1] != gate[2], "Retained scalar source")
            else:
                need(event[0] in ("phase", "adapter", "residual_adapter"), "Known inherited endpoint event")
        need(state == word["final"] + [0] * 8, "Every retained endpoint")
        need(profile == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82}, "Retained profile")
        core_profiles[side] = profile

    def boundary(stage):
        full = completed(stage)
        return [full] * 112 + [terms(full + ((q, -1),)) for q in labels]

    def specification(side, stage, future=None):
        out = []
        move = lambda at, pair: out.append(("map", at, pair))
        line = lambda at, port, sign: out.append(("line", at, port, sign))
        sweep = lambda name: out.append(("sweep", name, [v[1] for v in scalar[side + "_blocks"][name]]))
        core_event = ("core", "backward" if side == "B" else "forward", stage)

        def copies():
            for entry in scalar[side + "_typed_A_copies"]:
                port = entry["target_port"]
                source_key = "current_normalized_X_T_read" if side == "B" else "current_completed_X_T_read"
                initial_key = "same_port_Y_read" if side == "B" else "same_port_X_read"
                selected = entry[source_key]
                paths = []
                for read_event in selected:
                    source_port = read_event[1][2][1]
                    axis = "Y" if side == "B" else "X"
                    path = product(inverse(alignment(axis, stage, port)), alignment(axis, stage, source_port))
                    if stage:
                        move(source_port, path)
                        paths.append((source_port, path))
                body = [("scalar", v[1]) for v in entry[initial_key] + selected]
                body += [("line", 704, port, 1 if side == "B" else -1)]
                body += [("scalar", v[1]) for v in entry["target_add_and_clear"]]
                out.append(("private", side + "_A_copy_" + str(port), body))
                for at, path in reversed(paths):
                    move(at, inverse(path))

        if side == "B":
            for port in T:
                line(port, port, -1)
            copies()
            for at in range(112, 224):
                move(at, alignment("Y", future, at - 112))
            sweep("future_E_t")
            for at in range(112, 224):
                move(at, inverse(alignment("Y", future, at - 112)))
            active = list(range(112, 224)) + T
            for at in active:
                move(at, alignment("Y", stage, at % 112))
            for name in ("Y_U_from_X_T", "eight_unsigned_swaps", "Y_T_query_subtract"):
                sweep(name)
            for at in active:
                move(at, inverse(alignment("Y", stage, at % 112)))
            for port in T:
                line(port, port, 1)
            out.append(core_event)
        else:
            out.append(core_event)
            if stage:
                for at in range(112):
                    move(at, alignment("X", stage, at))
            for name in ("X_A_fused_query", "X_T_query_subtract", "X_A_restore_selected", "X_T_sign", "X_U_query_subtract"):
                sweep(name)
            if stage:
                for at in range(112):
                    move(at, inverse(alignment("X", stage, at)))
            copies()
        return out

    cases, scalar_projections = {}, {}
    for name, events in packet["programs"].items():
        parts = name.split("_")
        side, stage = parts[0], int(parts[1])
        future = int(parts[2]) if side == "B" else None
        # The F entry itself is supplied by the pinned retained-core lift.
        state = boundary(stage - 1 if side == "B" else stage) + [None] * 480 + [()] * 8
        normalized, projection = [], []
        counts = Counter()

        def consume(event, in_private=False):
            kind = event[0]
            if kind == "cover_map":
                _, token, label, old, new = event
                at, pair = register(token), maps[label]
                need(at < 224 and not in_private, "A full cover map acts only on data")
                need(polynomial(state[at]) == frames[old], "Map input phase")
                state[at] = move_frame(state[at], pair)
                need(polynomial(state[at]) == frames[new], "Map output phase")
                counts["maps"] += 1
                return "map", at, pair
            if kind == "native_line":
                _, token, label, old, new = event
                item, at = lines[label], register(token)
                need(at < 224 or at == 704 and in_private, "Native line field and lifetime")
                need(polynomial(state[at]) == frames[old], "Line input phase")
                state[at] = terms(state[at] + ((item["label"], item["sign"]),))
                need(polynomial(state[at]) == frames[new], "Line output phase")
                counts["lines"] += 1
                return "line", at, item["port"], item["sign"]
            if kind == "scalar":
                _, gate, label = event
                at = register(gate[1])
                need(at < 224 or at == 704 and in_private, "No new helper update")
                if gate[0] == "clear":
                    need(at == 704 and in_private, "Only owned C0 is newly cleared")
                    state[at] = terms(packet["native_frame_registry"][label]["line_terms_Z4"])
                else:
                    need(polynomial(state[at]) == frames[label], "Scalar target phase")
                    if gate[0] == "add":
                        src = register(gate[2])
                        need(src != at and (src < 224 or src == 704 and in_private), "Legal wrapper source")
                        need(polynomial(state[src]) == frames[label], "Exact scalar source phase")
                        counts["reads"] += 1
                    else:
                        need(gate[0] == "scale" and at < 224, "Data scalar sign")
                projection.append(gate)
                return "scalar", gate
            if kind == "cover_sweep":
                need(event[3] == "Complete this full-cover sweep before the next event.", "Full-cover barrier")
                body = [consume(child) for child in event[2]]
                need(all(child[0] == "scalar" for child in body), "Only scalar gates in a common sweep")
                counts["cover_sweeps"] += 1
                return "sweep", event[1], [child[1] for child in body]
            if kind == "private_sweep":
                need(event[3] == "For each cover owner, execute the whole body before the next owner. One ownedC0 is reused.", "Owner-serial private contract")
                need(event[2][0][0:2] == ["scalar", ["clear", ["C", 0]]] and event[2][-1][0:2] == ["scalar", ["clear", ["C", 0]]], "Private lifetime bounds")
                body = [consume(child, True) for child in event[2]]
                need(polynomial(state[704]) == polynomial(()), "Private output is zero in I")
                counts["private_sweeps"] += 1
                return "private", event[1], body
            need(kind == "retained_core", "No unrecognized event")
            need(event[1:3] == ["backward" if side == "B" else "forward", stage], "Core orientation and stage")
            if side == "B":
                need([polynomial(v) for v in state[:224]] == [polynomial(v) for v in boundary(stage-1)], "All core entrance data phases restored")
            state[:224] = boundary(stage)
            state[704:] = [()] * 8
            projection.extend(v[1] for v in core[event[1]] if v[0] == "scalar")
            counts["cores"] += 1
            return "core", event[1], stage

        normalized = [consume(event) for event in events]
        need(normalized == specification(side, stage, future), "Full owner paths, native signs, copy sources, and event order: " + name)
        need([polynomial(v) for v in state[:224]] == [polynomial(v) for v in boundary(stage)], "Every data output native phase")
        need(state[224:704] == [None]*480 and state[704:] == [()]*8, "Wrapper helper isolation and private endpoints")
        need(counts["private_sweeps"] == 8 and counts["cores"] == 1, "Eight serial row copies and one core")
        need(counts["lines"] == (24 if side == "B" else 8), "Exact added child count")
        need(counts["maps"] == (528 if side == "B" else 288 if stage else 0), "Exact cover map count")
        need(counts["reads"] == (1288 if side == "B" else 912), "All scalar reads checked")
        recorded = packet["case_parameters"][name]
        expected_record = {"orientation": side, "stage": stage,
                           "added_rank1_children": counts["lines"],
                           "explicit_cover_maps": counts["maps"],
                           "native_wrapper_maps": 2 * counts["lines"],
                           "matching_phase_ADD_reads": counts["reads"]}
        if side == "B":
            expected_record["future"] = future
        need(recorded == expected_record, "Complete case invoice")
        blocks = scalar[side + "_blocks"]
        expected = [v[1] for block in scalar[side + "_order"] if block in blocks for v in blocks[block]]
        core_scalar = [v[1] for v in core["backward" if side == "B" else "forward"] if v[0] == "scalar"]
        expected = expected + core_scalar if side == "B" else core_scalar + expected
        need(projection == expected, "Accepted full scalar word in every native instance")
        if side in scalar_projections:
            need(projection == scalar_projections[side], "Same scalar word for all stage instances")
        scalar_projections[side] = projection
        cases[name] = dict(counts)
        cases[name]['native_wrapper_maps'] = 2 * counts['lines']
        cases[name]['added_map_bound'] = counts['maps'] + 2 * counts['lines']
    need(set(cases) == {"B_%d_%d" % (s, t) for s in range(1, 8) for t in range(s+1, 9)} | {"F_%d" % s for s in range(9)}, "Complete 37-case family")

    invoices = {}
    for side, gates in scalar_projections.items():
        values, peak = [Fraction(1)]*712, Fraction(1)
        for gate in gates:
            at = register(gate[1])
            if gate[0] == "clear":
                values[at] = 0
            elif gate[0] == "scale":
                values[at] *= abs(Fraction(gate[2], gate[3]))
            else:
                src = register(gate[2])
                coefficient = abs(Fraction(gate[3], gate[4]))
                peak = max(peak, coefficient.numerator * values[src])
                values[at] += coefficient * values[src]
            peak = max(peak, values[at])
        width = 0
        while (1 << width) < peak:
            width += 1
        profile = core_profiles["backward" if side == "B" else "forward"].copy()
        profile[1] += 24 if side == "B" else 8
        invoice = {"complete_scalar": {"macros": len(gates), "operations": dict(Counter(g[0] for g in gates)), "real_primitives": sum(map(scalar_cost, gates))},
                   "native_profile": {str(k): v for k, v in sorted(profile.items())}, "native_mass": sum(k*v for k, v in profile.items()),
                   "formal_prefix": {"formal_triangle_Horner_bound": str(peak), "formal_prefix_ceiling_log2": width}}
        expected_bill = (214986, 5546, 73, "573411134169296526275133/64") if side == "B" else (211210, 5530, 55, "5413950274051752469/256")
        need((invoice["complete_scalar"]["real_primitives"], invoice["native_mass"], width, str(peak)) == expected_bill,
             "Complete invoice and finite scalar guard")
        invoices[side] = invoice

    sample = alignment("Y", 2, A[0])
    incoming = boundary(0)[112+A[0]]
    need(sample[0] != AXES, "Nontrivial owner witness")
    need(polynomial(move_frame(incoming, sample)) != polynomial(move_frame(incoming, (sample[0], 0))), "Translation is necessary")
    need(kernel(lines["positive_" + str(T[0])]["recipe"], 0) != kernel(lines["inverse_" + str(T[0])]["recipe"], 0), "Inverse sign is necessary")
    need(packet["owner_route_negative_control"] == {
        "owner_I_input": 0, "owner_rho_input": 1, "payload_address": 0,
        "correct_owner_view_output_at_I": 1, "incorrect_payload_only_output_at_I": 0},
        "Independent owner inputs distinguish an owner view from a payload permutation")
    return {
        "status": "PASS_QQ16_NATIVE_OWNER_PATHS_AND_PHASES",
        "actual_routes_reconstructed": 112 * 9,
        "affine_map_registry_entries": len(maps),
        "phase_registry_entries": len(frames),
        "exact_gaussian_kernel_columns": kernel_columns,
        "scalar_phase_mutations_rejected": len(lines),
        "cases": cases, "invoices": invoices,
        "retained_core_event_counts": {side: dict(Counter(event[0] for event in events)) for side, events in core.items()},
        "native_controls": ["wrong inverse sign", "missing payload translation", "payload-only owner permutation"],
        "inherited_native_scope": "Exact core bytes and local frame ledger are checked. The pinned bridge proof supplies the global owner embedding and endpoint adapters. Old child kernels are not rerun.",
        "scope": "Local full-cover words under bijective views and sweep barriers. No new-child hosting, global controller closure, physical address costs, recursive precision, complete supplier or kappa claim."
    }
