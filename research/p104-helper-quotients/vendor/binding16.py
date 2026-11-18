"""Complete occurrence and source-bound phase specialization of #7000/#7113.

The degree-two phase polynomial and translation checks are reused unchanged
from Douglas Colkitt's retained upstream_application.py. See SOURCE-PINS.json.
"""

from collections import Counter

from caller16 import literal_layout, require
from upstream_application import boundary, digest, dot, polynomial, sub, terms, translation


def route(q, basis, stage, ambient):
    native = [q, *basis]
    require(len(native) == 9 and all(0 < v < 512 for v in native),
            "nine central directions")
    require(all(dot(a, b) == (i == j) for i, a in enumerate(native)
                for j, b in enumerate(native)), "orthonormal central directions")
    fresh = [1 << (9 + 8 * (stage - 1) + j) for j in range(8)]
    mask = 511 | sum(fresh)

    def transform(value):
        central = value & 511
        out = value & ~mask
        if dot(central, q):
            out ^= q
        for basis_vector, axis in zip(basis, fresh, strict=True):
            if dot(central, basis_vector):
                out ^= axis
            if value & axis:
                out ^= basis_vector
        return out

    axes = [1 << j for j in range(ambient)]
    require(all(transform(transform(a)) == a for a in axes), "full route involution")
    require(transform(q) == q, "preserved head direction")
    require(all(transform(a) == a for a in axes if not mask & a), "complete spectators")
    return transform


def contact_phase(q, basis, stage, ambient):
    move = route(q, basis, stage, ambient)
    before_axes = [1 << j for j in range(9 + 8 * (stage - 1))]
    after_axes = [1 << j for j in range(9 + 8 * stage)]
    spectator = [1 << j for j in range(9, 9 + 8 * stage)]
    x0 = terms((a, 1) for a in before_axes)
    y0 = terms([*x0.items(), (q, -1)])
    x1 = terms((a, 1) for a in after_axes)
    y1 = terms([*x1.items(), (q, -1)])
    nx0 = terms([(a, 1) for a in spectator] + [(q, 1)])
    ny0 = terms((a, 1) for a in spectator)
    nx1 = terms((a, 1) for a in [*spectator, *[1 << j for j in range(9)]])
    ny1 = terms([*nx1.items(), (q, -1)])
    pairs = ((x0, nx0), (y0, ny0), (nx1, x1), (ny1, y1))
    shifts = [boundary(a, b, move) for a, b in pairs]
    body = terms((1 << j, 1) for j in range(9 + 8 * (stage - 1), 9 + 8 * stage))
    require(not polynomial(sub(sub(x1, x0), body))
            and not polynomial(sub(sub(y1, y0), body))
            and not polynomial(sub(sub(y1, x0), terms([*body.items(), (q, -1)])))
            and not polynomial(sub(sub(x1, y0), terms([*body.items(), (q, 1)]))),
            "all four signed contact operators")
    require(polynomial(sub(terms([(q, 1)]), terms([(q, -1)]))),
            "query orientation discrimination")
    # The two signed head corrections and the Q^2 term of LAMBDA.
    require(translation(sub(terms([(q, 1)]), terms([(q, -1)]))) == q
            and translation(terms([(q, 2)])) == q, "ordinary head translations")
    first_shift = next((i for i, shift in enumerate(shifts) if shift), None)
    return shifts, (move, pairs[first_shift]) if first_shift is not None else None


def native_inventory(word, helpers):
    dimensions = [len(frame) for frame in word["frames"]]
    public = word["public"]
    owned = {}
    lifetimes = []
    moves = []
    paid = Counter()
    opcodes = Counter()
    live_peak = 0
    for clock, event in enumerate(word["program"]):
        op, role, *args = event
        opcodes[op] += 1
        if op == "INIT":
            require(public <= role < public + word["owned_fields"] and role not in owned,
                    "fresh owned lifetime")
            owned[role] = len(lifetimes)
            lifetimes.append([role, clock, args[0], None, None])
            live_peak = max(live_peak, len(owned))
        elif op == "CLEAR":
            require(role in owned, "ordered owned retirement")
            lifetime = lifetimes[owned.pop(role)]
            lifetime[3:] = [clock, args[0]]
        elif op == "MOVE":
            first, last, is_owned = args
            rank = abs(dimensions[last] - dimensions[first])
            require(rank > 0 and is_owned == (role >= public), "positive paid native rank")
            require(not is_owned or role in owned, "current private MOVE owner")
            moves.append((clock, role, first, last, rank, owned.get(role)))
            paid[rank] += 1
    require(not owned and len(lifetimes) == 235 and live_peak == 51, "full 235-lifetime closure")
    targets = Counter()
    for role in helpers:
        rank = dimensions[word["final"][role]] - dimensions[word["initial"][role]]
        require(rank > 0, "positive independently owned helper target")
        targets[rank] += 1
    return lifetimes, moves, paid, targets, opcodes


def complete_binding(word, caller, phases, signed):
    stages, types, role_sets = literal_layout(caller, word)
    ambient = caller["ambient_rank"]
    public = word["public"]
    require(public == 1501 and word["owned_fields"] == 68, "exact native public/private header")
    ports = word["ports"]
    live = word["live"]
    h = word["hosted"]
    second = dict(zip(h["Dports"], zip(h["X2"], h["Y2"], strict=True), strict=True))
    main = set(live) | {r + 112 for r in live} | set(h["X2"]) | set(h["Y2"])
    helpers = sorted(set(range(public)) - main)
    require(len(live) == len(ports) == 104 and len(set(ports)) == 104
            and len(main) == 400 and len(helpers) == 1101, "actual native partition")
    special_helpers = (325, 1087)
    for role in special_helpers:
        pair = [word["initial"][role], word["final"][role]]
        require(role in helpers and pair == [3, 237]
                and not word["frames"][pair[0]]
                and word["frames"][pair[1]] == [30, 75, 138, 266],
                "explicit arbitrary-input rank-four helper boundary")
    by_q = {row["q"]: row["idle_children"][0]["orthogonal_axes"][:8]
            for row in phases["recipes"]}
    require(set(ports) <= set(by_q), "every actual port has a pinned phase basis")
    for port, (first, q) in enumerate(zip(live, ports, strict=True)):
        companion = first + 112
        fin = word["frames"][word["final"][companion]]
        require(word["frames"][word["initial"][first]] == [q]
                and not word["frames"][word["initial"][companion]]
                and word["frames"][word["final"][first]] == [1 << j for j in range(9)]
                and len(fin) == 8 and all(dot(q, axis) == 0 for axis in fin),
                "actual main source and target charts")
        if port in second:
            x2, y2 = second[port]
            require(all(word[key][a] == word[key][b]
                        for key in ("initial", "final")
                        for a, b in ((first, x2), (companion, y2))),
                    "separate second plane with identical charts")

    lifetime_plan, moves, native_paid, helper_targets, opcodes = native_inventory(word, helpers)
    roots = {("main", port, role) for kind, spec in types.items()
             for port in spec["ports"] for role in role_sets[kind]}
    require(len(roots) == signed["root_owners"] == 3536, "distinct root owner count")
    fresh_helpers = set()
    paid = Counter()
    targets = Counter()
    phase_rows = []
    occurrences = []
    owner_maps = []
    phase_fault_rejected = False
    signed_idles = 0
    special_owners = []
    for clock, event in enumerate(caller["events"]):
        if event[0] == "J":
            _, stage, a, b = event
            owners = {}
            for port, first in enumerate(live):
                pair = a[:2] if port in second else b[:2]
                first_pair = ((first, pair[0]), (first + 112, pair[1]))
                if port in second:
                    first_pair += tuple(zip(second[port], a[2:], strict=True))
                for slot, role in first_pair:
                    tag = ("main", port, role)
                    require(tag in roots and slot not in owners, "injective main assignment")
                    owners[slot] = tag
                shifts, fault = contact_phase(ports[port], by_q[ports[port]], stage, ambient)
                phase_rows.append([clock, port, shifts, 2 if port in second else 1])
                if fault and not phase_fault_rejected:
                    transform, (before, after) = fault
                    try:
                        boundary(before, after, transform, omit_translation=True)
                    except ValueError as exc:
                        require(str(exc) == "forward contact includes its phase",
                                "phase control rejection reason")
                        phase_fault_rejected = True
                    else:
                        raise ValueError("omitted contact translation escaped")
            require(set(owners) == main and len(set(owners.values())) == 400,
                    "all source main slots have different physical owners")
            for role in helpers:
                tag = ("helper", stage, role)
                require(tag not in fresh_helpers and tag not in roots, "fresh arbitrary helper")
                fresh_helpers.add(tag)
                owners[role] = tag
                if role in special_helpers:
                    special_owners.append({
                        "tag": tag, "stage": stage, "caller_clock": clock,
                        "initial_chart": 3, "final_chart": 237, "target_rank": 4,
                        "exit_ordered_basis": word["frames"][237],
                    })
            require(set(owners) == set(range(public)) and len(set(owners.values())) == public,
                    "full public-field injection")
            owner_maps.append([stage, sorted(owners.items())])
            for native_clock, role, first, last, rank, owned in moves:
                tag = owners[role] if owned is None else ("owned", stage, owned)
                require(tag not in roots or owned is None, "private owner separation")
                paid[rank] += 1
                occurrences.append([clock, native_clock, tag, rank, first, last])
            targets.update(helper_targets)
            continue

        kind, op, role, *args = event
        if op not in {"QUERY", "IDLE_ONE", "IDLE_ODD"}:
            continue
        if op == "QUERY":
            rank = 1
        else:
            rank = 8 * len(args[0]) + int(op == "IDLE_ODD")
        for port in types[kind]["ports"]:
            tag = ("query_scratch", clock, port) if op == "QUERY" else ("main", port, role)
            require((tag not in roots) if op == "QUERY" else tag in roots, "caller paid owner")
            occurrences.append([clock, op, tag, rank])
            paid[rank] += 1
            signed_idles += int(op == "IDLE_ODD")
    require(len(owner_maps) == stages and len(fresh_helpers) == 17616 and phase_fault_rejected,
            "complete 16-call owners and phase control")
    require(len(special_owners) == len({row["tag"] for row in special_owners}) == 32,
            "distinct stage-tagged arbitrary helper 325 and 1087 ingress/egress")
    root_targets = Counter()
    root_negative = 0
    for kind, spec in types.items():
        for phase, coeff_phase, *selection in spec["diagonal"]:
            require(coeff_phase == 0 and any(selection), "whole positive target endpoint")
            for port in spec["ports"]:
                q = ports[port]
                axes = [1 << (9 + 8 * j + offset) for j, yes in enumerate(selection)
                        if yes for offset in range(8)]
                require(len(axes) == len(set(axes)) and all(a < 1 << ambient for a in axes),
                        "positive target complete distinct axes")
                actual = terms([(q, phase)] + [(axis, 1) for axis in axes])
                positive = terms((a, 1) for a in ([q] if phase else []) + axes)
                require(translation(sub(positive, actual)) == (q if phase == -1 else 0),
                        "exact negative root translation")
                root_targets[len(axes) + int(bool(phase))] += 1
                root_negative += int(phase < 0)
    targets.update(root_targets)
    references = Counter({rank: stages * count for rank, count in native_paid.items()})
    references.update(signed["fixed_caller_paid"])
    require(paid == references and root_targets == Counter(signed["fixed_root_targets"]),
            "independent decomposition and occurrence invoices agree")
    require(len(occurrences) == sum(paid.values()) and sum(targets.values()) == 21152,
            "complete paid and productive owner count")
    contacts = sum(4 * row[3] for row in phase_rows)
    nonzero = sum(row[3] * sum(bool(v) for v in row[2]) for row in phase_rows)
    require(contacts == nonzero == 12800, "all 12,800 absolute phase translations charged")
    return {
        "ambient": ambient,
        "calls": stages,
        "native_public": public,
        "main_per_native": len(main),
        "fresh_helpers": len(fresh_helpers),
        "role_325_and_1087_helper_owners": special_owners,
        "root_owners": len(roots),
        "productive_fields": sum(targets.values()),
        "paid_positions": len(occurrences),
        "native_paid": dict(native_paid),
        "native_targets": dict(helper_targets),
        "paid": dict(paid),
        "targets": dict(targets),
        "phase_digest": digest(phase_rows),
        "owner_map_digest": digest(owner_maps),
        "ordered_paid_digest": digest(occurrences),
        "contacts": contacts,
        "nonzero_contact_translations": nonzero,
        "phase_omission_rejected": phase_fault_rejected,
        "signed_idle_ordinary_corrections": signed_idles,
        "negative_root_ordinary_corrections": root_negative,
        "owned_lifetimes_per_native": len(lifetime_plan),
        "owned_lifetime_plan_digest": digest(lifetime_plan),
        "owned_fresh_homes_per_raw_caller": stages * len(lifetime_plan),
        "owned_resets_per_raw_caller": 2 * stages * len(lifetime_plan),
        "native_opcodes": dict(opcodes),
    }
