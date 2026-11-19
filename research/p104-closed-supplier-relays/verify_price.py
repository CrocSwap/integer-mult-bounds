#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independently reconstruct and price the complete f30 and successor invoices."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import resource
import sys

HERE = Path(__file__).resolve().parent
PUBLIC_COMMIT = "6b0b2f7de0f068834264fc50b75a39a72c52ea22"
ORACLE_COMMIT = "e54523517d0f03e58352e647c403a5af3e525a57"
F30 = "f30aece9bbf9da00a428e61bc489dde0278f604b7cfd9fb3b1d2707990af2647"
PUBLIC_STREAM = "156fdf3a4a129b39225fd6ca51011de27974d7f104e8b04907c17ed5344bc858"
CALLS = 48
BIT = Fraction("0.00385248")
PUBLIC_RAW = ("0.00384022183445", "0.00384022183446")
COMPARATOR_UPPER = "0.00382069832566"
TARGET = "0.00383069832566"
BODY_AXES = (1 << 8) - 1
ORACLE_SHA256 = {
    "evaluate_recursive_power.py":
        "52b20f41fd0bb55fa88dccd6015af2ce358917817b9506720f3e60ce681cc3ad",
    "compare_recursive_invoices.py":
        "3930c22c11da7bc6042cfeb6e459ecb06e4478430037bee3469d034353855fc6",
}
DONOR_INPUTS = {
    "RESULT.json":
        "d583e3ac82ff447f58f014b0145f4b9a184f2b641b3c9ed0b3d7b0a263b007b1",
    "LAYOUT.json.gz":
        "6ca5f70604fbb81fc44e498f7b1450c37214b7cc95f9848e7b8be031adb99b34",
    "retained/data/CALLER.json.gz":
        "d889996a337f648087208ab51c98eaf052705d4fca88b5d01b6e9257a829897a",
    "retained/data/CONJUGATE-CALLER.json.gz":
        "80009663da460229a57f09bde90e35294329a210ae7fc7ef6d1f05b61ffccbf4",
}
DONOR_REBUILD_INPUTS = {
    "GRAPH.json.gz": "584a1bc9e6d6ea5e9abf0c115c66c56f9447466f19b1a0393e7d8b6128c45f92",
    "BANK-EDITS.json": "f3b788f5fc76aff76ab0a67628481def1d5ece77a9792b85735745dcb3127330",
    "PUBLIC-EDITS.json": "8193168c9be0014582ec007fdb9431ddf8e31014f812b8a877d6a6d9af816098",
    "bank_split.py": "d02590768a74bf326f9c331bcf3e4b514abe8ff8b19fafc8d4e4e2fb0100becc",
    "public_split.py": "a69c9128d7bb582c63dc60c1b7fa8eb42eaae9ed95eca4f0b0a9dfd006dbdf0d",
    "birth_event.py": "b64c955e5183b93cc48fe7a1a6149b242d5e3b0e9abcdd0c64bbb4de9361995a",
    "retained/vendor/network.py": "a9169fd6ad0a13c69cf39bd32649d53256f6d6fa2ed2ceda854f848b64f4c546",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encoded(value, *, canonical=False):
    return json.dumps(value, separators=(",", ":"), sort_keys=canonical).encode()


def digest(value, *, canonical=False):
    return sha256(encoded(value, canonical=canonical)).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def validate_sources(directory, inputs):
    for name, expected in inputs.items():
        require(sha256((directory / name).read_bytes()).hexdigest() == expected,
                f"pinned public input {name}")


def rebuild_predecessor(donor):
    validate_sources(donor, DONOR_REBUILD_INPUTS)
    sys.path[:0] = [str(donor), str(donor / "retained/vendor")]
    from bank_split import apply as apply_bank
    from public_split import split as apply_public
    from network import Network

    graph = read(donor / "GRAPH.json.gz")
    frames = graph["frames"]
    net = Network(
        graph["first_output"], graph["initial"], graph["final"],
        {k: (a, b) for k, a, b in graph["moves"]},
        {k: {donor: Fraction(q) for donor, q in terms} for k, terms in graph["forms"]},
    )
    for name, apply in (("BANK-EDITS.json", apply_bank), ("PUBLIC-EDITS.json", apply_public)):
        journal = read(donor / name)
        require(digest(graph, canonical=True) == journal["source_sha256"], f"{name} preimage")
        for event in journal["events"]:
            net = apply(net, event)
            order = net.schedule()
        graph = dict(
            frames=frames, initial=net.initial, final=net.final, first_output=net.first_output,
            moves=[[k, a, b] for k, (a, b) in sorted(net.moves.items())],
            forms=[[k, [[sender, str(q)] for sender, q in sorted(form.items())]]
                   for k, form in sorted(net.forms.items())],
            schedule=order,
        )
        require(digest(graph, canonical=True) == journal["output_sha256"], f"{name} postimage")
    return graph


def chart_span(axes):
    points = {0}
    for axis in axes:
        require(type(axis) is int and 0 < axis < 512 and axis not in points, "literal chart basis")
        points |= {point ^ axis for point in points}
    return points


def physical_ports(layout, graph):
    live, hosted, heads = layout["live"], layout["hosted"], layout["ports"]
    secondary = dict(zip(hosted["Dports"], zip(hosted["X2"], hosted["Y2"], strict=True), strict=True))
    require(len(live) == len(heads) == len(set(heads)) == 104 and len(secondary) == 96,
            "exact 96 A and 8 B native ports")
    starts, ends, frames = graph["initial"], graph["final"], graph["frames"]
    ports = {}
    for i, (x, head) in enumerate(zip(live, heads, strict=True)):
        y = x + 112
        cols = (x, y) + secondary.get(i, ())
        require(frames[starts[x]] == [head] and frames[starts[y]] == []
                and set(frames[ends[x]]) == {1 << k for k in range(9)}, "primary X and Y physical endpoints")
        require(chart_span(frames[ends[y]]) == {
            j for j in range(512) if (j & head).bit_count() % 2 == 0
        }, "complete Y⊥ physical endpoint")
        if len(cols) == 4:
            require(all((starts[a], ends[a]) == (starts[b], ends[b])
                        for a, b in zip(cols[:2], cols[2:], strict=True)), "independent secondary A endpoints")
        ports[i] = cols
    mains = set().union(*ports.values())
    require(len(mains) == sum(map(len, ports.values())) == 400, "unique physical port addresses")
    return ports, mains


def native_inventory(graph, layout):
    first, initial, final, frames = (graph[k] for k in ("first_output", "initial", "final", "frames"))
    require((len(initial), len(final), layout["public"]) == (1264, 1264, 1264),
            "complete f30 public inventory")
    require(graph["frames"] == layout["frames"], "pinned native frames")
    labels = layout["source_labels"]
    require(len(labels) == len(set(labels)) == 1264, "independent source labels")
    ports, mains = physical_ports(layout, graph)
    spans = [chart_span(axes) for axes in frames]
    paid, targets, helpers = Counter(), Counter(), {}
    move_rows, move_ranks = {}, {}
    for k, source, dest in graph["moves"]:
        require(0 <= k < first and k not in move_rows, "unique native paid key")
        a, b = spans[source], spans[dest]
        require(a < b or b < a, "strict signed nesting on literal native paid move")
        rank = abs(len(frames[source]) - len(frames[dest]))
        paid[rank] += 1
        move_rows[k] = (source, dest)
        move_ranks[k] = rank
    for owner, (source, dest) in enumerate(zip(initial, final, strict=True)):
        if owner in mains:
            continue
        require(spans[source] < spans[dest], "positive native same-owner conversion")
        rank = len(frames[dest]) - len(frames[source])
        targets[rank] += 1
        helpers[owner] = [labels[owner], source, dest, rank]
    require(len(helpers) == 864, "native helper census")
    require({tuple(values) for values in helpers.values()} >= {(325, 3, 237, 4), (1087, 3, 237, 4)},
            "protected rank-four helper charts")
    forms = dict(graph["forms"])
    schedule = graph["schedule"]
    require(len(forms) == len(graph["forms"]) == len(schedule) == len(set(schedule))
            and forms.keys() == set(schedule)
            and forms.keys() == move_rows.keys() | set(range(first, first + len(initial))),
            "every paid move and public terminal appears exactly once")
    available = {~i: chart for i, chart in enumerate(initial)}
    for k in schedule:
        source = move_rows[k][0] if k < first else final[k - first]
        form = forms[k]
        require(form and [u for u, _ in form] == sorted({u for u, _ in form}),
                "nonempty unique literal donor rows")
        require(all(u in available and available[u] == source and Fraction(v) for u, v in form),
                "paid and terminal rows read available cocharted inputs")
        if k in move_rows:
            available[k] = move_rows[k][1]
    return dict(paid=paid, targets=targets), helpers, move_rows, move_ranks, ports


def local_words(donor):
    homogeneous = read(donor / "retained/data/CALLER.json.gz")
    conjugate = read(donor / "retained/data/CONJUGATE-CALLER.json.gz")
    require(sha256(gzip.decompress((donor / "retained/data/CONJUGATE-CALLER.json.gz").read_bytes())).hexdigest()
            == "54a44134a6f9bb3d9e1a27d3bd7ba5fb1cffea3cdfe00f6a72e80f0bbd99d2d7",
            "complete pinned mixed caller")
    spec = homogeneous["types"]["A"]
    offset = spec["offset"]
    events = []
    for row in homogeneous["events"]:
        if row[0] == "J":
            events.append(["HOST_A", row[1] - 1, *[r - offset for r in row[2]]])
        elif row[0] == "A":
            op, label, *args = row[1:]
            if op == "ADD":
                args = [args[0] - offset, [args[1], "0"]]
            elif op == "SCALE":
                args = [[args[0], "0"]]
            elif op in ("SWAP", "QUERY"):
                args[0] -= offset
            elif op in ("IDLE_ONE", "IDLE_ODD"):
                args[0] = [j - 1 for j in args[0]]
            else:
                require(op == "LAMBDA", "known homogeneous caller operation")
            events.append([op, label - offset, *args])
    require(all(len(bits) == 16 and scalar == 0 and sign in (-1, 1) and set(bits) <= {0, 1}
                for sign, scalar, *bits in spec["diagonal"]), "literal homogeneous output mask")
    a_targets = [[sign, [i for i, bit in enumerate(bits) if bit]] for sign, _, *bits in spec["diagonal"]]
    rotated = deepcopy(conjugate["events"][1641:] + conjugate["events"][:1641])
    for event in rotated:
        if event[0].startswith("HOST_"):
            event[1] = (event[1] + 8) % 16
        elif event[0].startswith("IDLE_"):
            event[2] = [(i + 8) % 16 for i in event[2]]
    rotated_targets = [[sign, [(i + 8) % 16 for i in mask]] for sign, mask in conjugate["diagonal"]]
    require(digest([rotated, rotated_targets]) == "cb3b76c34d4b9ad93316d44297a1e918232c0491c8d3e028df5a01b60d7bf454",
            "literal signed cyclic seam")
    return {"A": (events, a_targets), "rotated": (rotated, rotated_targets)}


def place_roots(ports):
    b_ports = [port for port, address in ports.items() if len(address) == 2]
    a_ports = [port for port, address in ports.items() if len(address) == 4]
    cohorts = {start: [(start, b_ports), (start + 24, b_ports)] for start in range(24)}
    used = [{port for port in b_ports} for _ in range(CALLS)]
    a_queues = []
    for color in range(16):
        outstanding = {start for start in cohorts if color not in (start % 16, (start + 24) % 16)}
        visits = []
        for clock in range(color, CALLS, 16):
            ordered = sorted(start for start in outstanding if start < clock < start + 24)
            for index, start in enumerate(ordered[:len(a_ports) // 8]):
                slots = a_ports[8 * index:8 * (index + 1)]
                cohorts[start].append((clock, slots))
                used[clock].update(slots)
                outstanding.remove(start)
            visits.extend((clock, port) for port in a_ports if port not in used[clock])
        require(not outstanding and len(visits) == 120, "literal full interior allocation")
        a_queues.append(visits)
    roots = {}
    for index, visits in enumerate(zip(*a_queues, strict=True)):
        roots[("A", index)] = sorted(visits)
    for start, visits in cohorts.items():
        for member in range(8):
            roots[("rotated", 8 * start + member)] = sorted((clock, slots[member]) for clock, slots in visits)
    return roots


def global_mask(local, colors):
    require(len(local) == len(set(local)) and all(0 <= axis < 16 for axis in local),
            "literal distinct local body mask")
    return sum(BODY_AXES << (9 + 8 * colors[axis]) for axis in local)


def signed_caller(ports, helpers, result, donor):
    words = local_words(donor)
    roots = place_roots(ports)
    chunks, hosts = {}, {}
    for name, (events, targets) in words.items():
        chunks[name], hosts[name] = [[]], []
        for event in events:
            if event[0].startswith("HOST_"):
                hosts[name].append(event)
                chunks[name].append([])
            else:
                chunks[name][-1].append(event)
        require([e[1] for e in hosts[name]] == list(range(16)), "literal sixteen signed native contacts")
        need_types = ["HOST_A"] * 16 if name == "A" else ["HOST_B"] + ["HOST_A"] * 14 + ["HOST_B"]
        require([e[0] for e in hosts[name]] == need_types, "literal A and B port word")
        require(len(targets) == (34 if name == "A" else 30), "all arbitrary root owners")
    paid, productive = Counter(), Counter()
    active_ports, root_blocks = [{} for _ in range(CALLS)], [[] for _ in range(CALLS + 1)]
    offset = 0
    physical_masks = sha256()
    for root, visits in sorted(roots.items()):
        name = root[0]
        colors = tuple(clock % 16 for clock, _ in visits)
        require(len(colors) == 16 and set(colors) == set(range(16))
                and len(set(clock for clock, _ in visits)) == 16, "strict chronological all-color root")
        word, targets = words[name]
        for (clock, port), (op, _, *roles) in zip(visits, hosts[name], strict=True):
            require(port not in active_ports[clock] and len(roles) == len(set(roles)) == len(ports[port])
                    and op == ("HOST_B" if len(ports[port]) == 2 else "HOST_A")
                    and all(0 <= role < len(targets) for role in roles), "physical root/port owner placement")
            active_ports[clock][port] = [offset + role for role in roles]
        for clock, block in zip([t for t, _ in visits] + [CALLS], chunks[name], strict=True):
            root_blocks[clock].append((offset, colors, block))
        for event in word:
            if not (event[0].startswith("IDLE_") or event[0] == "QUERY"):
                continue
            op, owner, *args = event
            if op == "QUERY":
                rank, mask = 1, 1
            else:
                mask = global_mask(args[0], colors) | int(op == "IDLE_ODD")
                rank = mask.bit_count()
            require(rank > 0, "literal nonzero paid caller rank")
            physical_masks.update(encoded([root, op, owner + offset, hex(mask)]))
            paid[rank] += 1
        for role, (sign, local) in enumerate(targets):
            require(sign in (-1, 1), "literal odd signed productive target")
            mask = global_mask(local, colors) | 1
            physical_masks.update(encoded([root, "TARGET", role + offset, sign, hex(mask)]))
            productive[mask.bit_count()] += 1
        offset += len(targets)
    require(offset == 9840 and Counter(root[0] for root in roots) == {"A": 120, "rotated": 192},
            "full distinct root census")

    stream, binding = sha256(), sha256()
    helper_hash = digest(sorted(r[0] for r in helpers.values()))
    events, per_time = 0, []
    for clock, blocks in enumerate(root_blocks):
        for start, colors, block in blocks:
            for original in block:
                op, owner, *args = original
                if op in ("ADD", "QUERY", "SWAP"):
                    args[0] += start
                elif op.startswith("IDLE_"):
                    args[0] = [colors[c] for c in args[0]]
                stream.update(encoded([op, owner + start, *args]))
                events += 1
        if clock == CALLS:
            continue
        table = active_ports[clock]
        require(table.keys() == ports.keys(), "all 104 physical ports filled")
        assigned = sorted((physical, local) for p, roles in table.items()
                          for physical, local in zip(ports[p], roles, strict=True))
        require(len(assigned) == len({physical for physical, _ in assigned})
                == len({local for _, local in assigned}) == 400, "all native main owners independent")
        views = [table[p] for p in range(104)]
        for event in (["PORT_VIEWS", "ENTER", clock, views],
                      ["NATIVE", clock, clock % 16, views],
                      ["PORT_VIEWS", "EXIT", clock, views]):
            stream.update(encoded(event))
        binding.update(encoded([clock, clock % 16, assigned, helper_hash]))
        events += 3
        per_time.append([clock, sum(len(table[p]) == 4 for p in table),
                         sum(len(table[p]) == 2 for p in table)])
    require(events == 840912 and stream.hexdigest() == PUBLIC_STREAM
            and result["caller_proof"]["readback"]["event_stream_sha256"] == PUBLIC_STREAM,
            "complete signed 48-call emitter has the literal source stream hash")
    require(binding.hexdigest() == result["caller"]["finite_binding"]["stage_binding_sha256"]
            and helper_hash == result["caller"]["finite_binding"]["helper_label_sha256"],
            "literal roster of all native main and helper owners")
    for side, counts in (("fixed_caller_paid", paid), ("fixed_root_targets", productive)):
        require(counts == integer_hist(result["caller"][side]), f"literal caller matches deposited {side}")
    return dict(paid=paid, targets=productive), dict(
        stream_sha256=stream.hexdigest(), events=events, ports_per_call=per_time,
        signed_mask_sha256=physical_masks.hexdigest(), root_owners=offset,
        a_roots=120, rotated_roots=192, active_b_visits=sum(row[2] for row in per_time),
        stage_binding_sha256=binding.hexdigest(), helper_label_sha256=helper_hash,
    )


def integer_hist(histogram):
    return Counter({int(r): n for r, n in histogram.items()})


def finite_invoice(native, caller):
    return {side: caller[side] + Counter({r: n * CALLS for r, n in native[side].items()})
            for side in ("paid", "targets")}


def require_invoice(reconstructed, declared):
    require(all(reconstructed[side] == integer_hist(declared[side]) for side in ("paid", "targets")),
            "declared paid/target histogram differs from the literal finite invoice")


def signed_counts(invoice):
    signed = invoice["targets"].copy()
    signed.subtract(invoice["paid"])
    return {r: n for r, n in signed.items() if n}


@cache
def price(rank, point):
    return power_bounds(rank, 1 - point, 224)


def margin(invoice, point):
    lo = hi = Fraction()
    for r, count in signed_counts(invoice).items():
        lower, upper = price(r, point)
        if count < 0:
            lower, upper = upper, lower
        lo += count * lower
        hi += count * upper
    return lo, hi


def log_series(y):
    terms = 32
    partial = sum((2 * y ** (2*i + 1) / (2*i + 1) for i in range(terms)), Fraction())
    tail = 2 * y ** (2*terms + 1) / ((2*terms + 1) * (1 - y*y))
    return partial, partial + tail


@cache
def log_bounds(rank):
    power = rank.bit_length() - 1
    a, b = log_series(Fraction(1, 3))
    c, d = log_series(Fraction(rank - (1 << power), rank + (1 << power)))
    return power*a + c, power*b + d


def derivative_bounds(invoice):
    """Bound the signed derivative simultaneously for 0 <= kappa <= BIT."""
    lo = hi = Fraction()
    for r, count in signed_counts(invoice).items():
        minlog, maxlog = log_bounds(r)
        low, high = price(r, BIT)[0] * minlog, r * maxlog
        if count > 0:
            low, high = high, low
        lo -= count * low
        hi -= count * high
    require(lo <= hi < 0, "complete signed cost is strictly monotone through old BIT")
    return lo, hi


def tick(value):
    return f"{value // 10**14}.{value % 10**14:014d}"


def bracket(invoice):
    derivative_bounds(invoice)
    lo, hi = 1, int(BIT * 10**14)
    require(margin(invoice, Fraction(lo, 10**14))[0] > 0 > margin(invoice, BIT)[1],
            "unique crossing lies strictly below old BIT")
    while hi - lo > 1:
        mid = (lo + hi) // 2
        a, b = margin(invoice, Fraction(mid, 10**14))
        if a > 0:
            lo = mid
        elif b < 0:
            hi = mid
        else:
            raise ValueError("need more than 224 directed bits")
    return tick(lo), tick(hi)


def decimal(v, digits=32):
    scale = 10 ** digits
    q, remainder = divmod(abs(v), scale)
    return f"{'-' if v < 0 else ''}{q}.{remainder:0{digits}d}"


def enclose(interval, digits=32):
    a, b = interval
    scale = 10 ** digits
    return [decimal(a * scale // 1, digits), decimal(-(-b * scale // 1), digits)]


def graph_delta(predecessor, candidate, old_ranks, new_ranks):
    changed = []
    for k in sorted(predecessor.keys() | candidate.keys()):
        old, new = predecessor.get(k), candidate.get(k)
        if old != new:
            changed.append(dict(key=k, old_chart_pair=old, new_chart_pair=new,
                                old_rank=old_ranks.get(k), new_rank=new_ranks.get(k)))
    return changed


def audit_negative_controls(graph, source_layout, invoice):
    missing = deepcopy(graph)
    keys = {row[0] for row in graph["moves"]}
    key = next(d for _, form in graph["forms"] for d, _ in form if d in keys)
    missing["moves"] = [row for row in missing["moves"] if row[0] != key]
    missing["forms"] = [row for row in missing["forms"] if row[0] != key]
    missing["schedule"].remove(key)
    try:
        native_inventory(missing, source_layout)
    except ValueError as failure:
        require(str(failure) == "paid and terminal rows read available cocharted inputs",
                "a missing charged transfer must break the structural reconstruction")
    else:
        raise ValueError("missing native payment was accepted")
    retagged = dict(graph, final=graph["final"].copy())
    role = source_layout["source_labels"].index(325)
    rank_three = next(index for index, axes in enumerate(graph["frames"]) if len(axes) == 3)
    retagged["final"][role] = rank_three
    try:
        native_inventory(retagged, source_layout)
    except ValueError as failure:
        require(str(failure) == "protected rank-four helper charts",
                "rank mutation at protected helper must fail independently")
    else:
        raise ValueError("protected native rank change was accepted")
    changed = {side: counts.copy() for side, counts in invoice.items()}
    rank = max(changed["targets"])
    changed["targets"][rank] -= 1
    changed["targets"][rank-1] += 1
    try:
        require_invoice(invoice, changed)
    except ValueError as failure:
        require(str(failure) == "declared paid/target histogram differs from the literal finite invoice",
                "productive rank control must fail at literal invoice comparison")
    else:
        raise ValueError("mutated productive rank was accepted")
    point = Fraction(PUBLIC_RAW[1])
    actual, fault = margin(invoice, point), margin(changed, point)
    require(actual[0] > fault[1], "productive rank control lowers the actual directed margin")
    return dict(missing_paid_key=key, missing_paid_rejected=True,
                protected_helper_rank_change=[325, 4, 3], protected_helper_rank_change_rejected=True,
                changed_productive_rank=[rank, rank-1], changed_productive_rank_rejected=True,
                margin_decrease_on_changed_rank=enclose((actual[0]-fault[1], actual[1]-fault[0])))


def case_report(invoice, point):
    lower, upper = bracket(invoice)
    lo_tick = int(Fraction(lower) * 10**14)
    claim, tested = tick(lo_tick - 8), tick(lo_tick - 1)
    require(Fraction(tested) < BIT and margin(invoice, Fraction(tested))[0] > 0,
            "fixed seven-grid claim/probe distance and old BIT")
    return dict(
        raw_bracket=[lower, upper], claim_candidate=claim, tested=tested,
        productive_count=sum(invoice["targets"].values()), paid_count=sum(invoice["paid"].values()),
        signed_rank_mass=sum(r*n for r, n in signed_counts(invoice).items()),
        derivative_interval_0_to_old_bit=enclose(derivative_bounds(invoice)),
        margin_at_lower=enclose(margin(invoice, Fraction(lower))),
        margin_at_upper=enclose(margin(invoice, Fraction(upper))),
        margin_at_tested=enclose(margin(invoice, Fraction(tested))),
        margin_at_target=enclose(margin(invoice, point)),
        margin_at_public_f30_upper=enclose(margin(invoice, Fraction(PUBLIC_RAW[1]))),
        margin_at_old_bit=enclose(margin(invoice, BIT)),
        old_bit_minus_tested=enclose((BIT-Fraction(tested), BIT-Fraction(tested))),
    )


def check_all(args, baseline, layout, result):
    target = Fraction(TARGET)
    comparator_upper = Fraction(COMPARATOR_UPPER)
    require(digest(baseline, canonical=True) == result["graph_sha256"] == F30, "pinned complete f30 graph")
    old_native, helpers, moves, ranks, ports = native_inventory(baseline, layout)
    for side, receipt_key in (("paid", "paid_native_ranks"), ("targets", "positive_helper_ranks")):
        require(old_native[side] == integer_hist(result["native"][receipt_key]), "literal predecessor native census")
    caller, caller_check = signed_caller(ports, helpers, result, args.donor_dir)
    old_invoice = finite_invoice(old_native, caller)
    require_invoice(old_invoice, result["application"]["invoice"])
    public = case_report(old_invoice, target)
    require(tuple(public["raw_bracket"]) == tuple(result["application"]["bracket"]) == PUBLIC_RAW,
            "independently reproduced f30 raw price")
    report = dict(
        tool="directed dyadic square roots, 224 bits, with independent rational logarithm derivative",
        source_commit=PUBLIC_COMMIT, oracle_commit=ORACLE_COMMIT, target=TARGET, original_bit="0.00385248",
        original_comparator_raw_upper=COMPARATOR_UPPER,
        deposited_public_bit=result["application"]["compiler"]["BIT_pin"], native_calls=CALLS,
        predecessor=dict(graph_sha256=F30, native=old_native, invoice=old_invoice, **public),
        caller=caller_check, caller_invoice=caller,
        protected_native_owner_labels=[325, 1087],
        negative_controls={"predecessor": audit_negative_controls(baseline, layout, old_invoice)},
    )
    if args.candidate is None:
        return report
    candidate = read(args.candidate)
    candidate_hash = digest(candidate, canonical=True)
    require(candidate_hash != F30 and candidate_hash == args.candidate_sha,
            "candidate canonical SHA-256 must match the explicit freeze pointer")
    require(all(candidate[k] == baseline[k] for k in ("initial", "final", "frames", "first_output")),
            "candidate must retain every independent public owner and its original endpoints")
    new_native, new_helpers, new_moves, new_ranks, new_ports = native_inventory(candidate, layout)
    require(new_helpers == helpers and new_ports == ports and new_native["targets"] == old_native["targets"],
            "identical native productive owner ranks and physical main ports")
    new_invoice = finite_invoice(new_native, caller)
    candidate_report = case_report(new_invoice, target)
    require(candidate_report["raw_bracket"][0] > PUBLIC_RAW[1]
            and margin(new_invoice, Fraction(PUBLIC_RAW[1]))[0] > 0,
            "candidate must strictly exceed the public f30 raw upper")
    if args.candidate_bill:
        declared = read(args.candidate_bill)
        require_invoice(new_invoice, declared["price"]["invoice"])
        require(candidate_report["raw_bracket"] == declared["price"]["raw_bracket"],
                "independently reproduced candidate raw crossing")
    delta = new_native["paid"].copy()
    delta.subtract(old_native["paid"])
    price_claim = Fraction(candidate_report["claim_candidate"])
    over_comparator = price_claim - comparator_upper
    over_donor = price_claim - Fraction(PUBLIC_RAW[1])
    require(over_comparator >= Fraction("0.00001") and price_claim > target > comparator_upper,
            "price-side claim exceeds original target and threshold")
    report["candidate"] = dict(
        graph_sha256=candidate_hash, compressed_file_sha256=sha256(args.candidate.read_bytes()).hexdigest(),
        native=new_native, invoice=new_invoice, native_paid_delta={r: n for r, n in delta.items() if n},
        literal_paid_edits=graph_delta(moves, new_moves, ranks, new_ranks), **candidate_report,
        price_claim_gain_over_original_7761_upper=enclose((over_comparator, over_comparator)),
        price_claim_gain_over_f30_raw_upper=enclose((over_donor, over_donor)),
    )
    report["negative_controls"]["candidate"] = audit_negative_controls(candidate, layout, new_invoice)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--donor-dir", type=Path, required=True, help="exact public research/p104-dual-supplier-lift/complex directory")
    parser.add_argument("--price-oracle", type=Path, required=True, help="pinned evaluate_recursive_power.py file")
    parser.add_argument("--predecessor", type=Path,
                        help="optional canonical f30 graph previously reconstructed from the public package")
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--candidate-sha")
    parser.add_argument("--candidate-bill", type=Path,
                        help="optional producer receipt containing price.invoice and price.raw_bracket")
    parser.add_argument("--output", type=Path, default=Path("independent-price.json"))
    args = parser.parse_args()
    require(bool(args.candidate) == bool(args.candidate_sha), "pair --candidate with --candidate-sha")
    require(sys.flags.optimize == 0, "donor journal replay retains its assertions")
    args.donor_dir = args.donor_dir.resolve()
    oracle = args.price_oracle.resolve()
    resource.setrlimit(resource.RLIMIT_CPU, (238, 240))
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    require(oracle.name == "evaluate_recursive_power.py", "path to exact price oracle script")
    validate_sources(oracle.parent, ORACLE_SHA256)
    sys.path.insert(0, str(oracle.parent))
    global power_bounds
    from evaluate_recursive_power import power_bounds

    validate_sources(args.donor_dir, DONOR_INPUTS)
    baseline = read(args.predecessor) if args.predecessor else rebuild_predecessor(args.donor_dir)
    require(digest(baseline, canonical=True) == F30, "complete pinned f30 graph")
    layout = read(args.donor_dir / "LAYOUT.json.gz")
    extra = len(baseline["initial"]) - layout["public"]
    require(extra == 2, "native word adds two independent helper labels")
    start = 1 + max(layout["source_labels"])
    layout["source_labels"].extend(range(start, start + extra))
    layout["public"] = len(baseline["initial"])
    result = read(args.donor_dir / "RESULT.json")
    report = check_all(args, baseline, layout, result)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: report[k]["raw_bracket"] for k in ("predecessor", "candidate") if k in report}))


if __name__ == "__main__":
    main()
