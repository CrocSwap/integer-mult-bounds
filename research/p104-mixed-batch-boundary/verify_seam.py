#!/usr/bin/env python3
"""Verify the finite-batch seam from pinned P104 data. Apache-2.0."""

import argparse
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys


HEAD = "6b0044123aad114cf71ca2bb0e98741e5a27c7b5"
PARENT_STREAM = "d82aa7d2ac4974f58b8a4e9f15a8ec9286bc79e26ab5d53f9d748db9f9a04ca8"
NATIVE_GRAPH = "c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84"
SOURCE_FILES = {
    "data/CALLER.json.gz": "d889996a337f648087208ab51c98eaf052705d4fca88b5d01b6e9257a829897a",
    "data/CONJUGATE-CALLER.json.gz": "80009663da460229a57f09bde90e35294329a210ae7fc7ef6d1f05b61ffccbf4",
    "data/BASE-INTERFACE.json": "1cd2de69e6e49fb74abc3b1dea2366901e1a227704c62e0f624096b22853d582",
    "data/CALLER-PHASE-BASES.json": "325a1eb4aa7fe5f918b1d8344b88ad132ef4606268bccec20f223ace5feda18b",
    "results/application.json": "c736b04bed2be2e597cdc807dec38600008d80e8612e995f6d3a5c1df52f095d",
}
GRAPH_SOURCE_FILES = {
    "construction.py": "037c66277636cf5cd860e88f4f5998de46d34c726280c787fcb9f611091d634b",
    "linear.py": "bc0aaa0e4ce28260907d29083e4f788e08ae60f050800257b39d1070d545e30e",
    "vendor/network.py": "a9169fd6ad0a13c69cf39bd32649d53256f6d6fa2ed2ceda854f848b64f4c546",
    "data/BASE-GRAPH.json.gz": "843ac970a0ea02f0852f0b03b71f9bc473d792a739ac44efa288b553ddb8b275",
    "EDITS.json": "7ced0e7a5d39f1ebc1468899e1f66da84d2f7160d8c979763ee33bcd2e6e93c0",
}
RECIPE = {"A": "A" * 16, "B": "B" * 16, "mixed": "AAAAAAABBAAAAAAA"}
KINDS = tuple(RECIPE)
CENTRAL = tuple(1 << j for j in range(9))
BODIES = tuple(255 << (9 + 8 * c) for c in range(16))
TWO_REGISTERS = {"ADD", "QUERY", "SWAP"}
IDLES = {"IDLE_ONE", "IDLE_ODD"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compact(value, *, ordered=False):
    return json.dumps(value, sort_keys=ordered, separators=(",", ":")).encode()


def read_bytes(path, expected):
    raw = path.read_bytes()
    if expected:
        require(sha256(raw).hexdigest() == expected, f"source bytes: {path.name}")
    return raw


def read(path, expected=None):
    raw = read_bytes(path, expected)
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def export_graph(package):
    base_interface = "data/BASE-INTERFACE.json"
    required = GRAPH_SOURCE_FILES | {base_interface: SOURCE_FILES[base_interface]}
    for name, digest in required.items():
        read_bytes(package / name, digest)
    source = """
import json
import sys
sys.path.insert(0, sys.argv[1])
from construction import build
graph, layout, _ = build()
print(json.dumps([graph, layout], separators=(",", ":")))
"""
    return json.loads(subprocess.check_output([sys.executable, "-I", "-B", "-c", source, str(package.resolve())]))


@dataclass
class Template:
    contacts: list
    chunks: list
    targets: list


def read_templates(homogeneous, mixed):
    templates = {}
    require((homogeneous["stages"], homogeneous["roles"]) == (16, 68), "homogeneous dimensions")
    require((mixed["local_calls"], mixed["roles"]) == (16, 30), "mixed dimensions")
    for kind in KINDS:
        if kind == "mixed":
            events = mixed["events"]
            targets = mixed["diagonal"]
        else:
            spec = homogeneous["types"][kind]
            offset = spec["offset"]
            require(spec["roles"] == 34, "homogeneous root width")
            if kind == "A":
                require(tuple(map(Fraction, (spec["alpha2"], spec["beta2"]))) == (-1, 0),
                        "template secondary shear")
            events = []
            for tag, *entry in homogeneous["events"]:
                if tag == "J":
                    slot, a, b = entry
                    if kind == "B":
                        require(tuple(map(Fraction, b[2:])) == (-1, Fraction(1, 2)),
                                "template coupled port")
                    fields = a if kind == "A" else b[:2]
                    events.append(["HOST_" + kind, slot - 1, *(r - offset for r in fields)])
                elif tag == kind:
                    op, field, *args = entry
                    if op in TWO_REGISTERS:
                        args[0] -= offset
                    if op in {"ADD", "SCALE"}:
                        args[-1] = [args[-1], "0"]
                    if op in IDLES:
                        args[0] = [c - 1 for c in args[0]]
                    events.append([op, field - offset, *args])
            targets = []
            for phase, scalar, *indicator in spec["diagonal"]:
                require(scalar == 0 and len(indicator) == 16 and set(indicator) <= {0, 1},
                        "homogeneous target mask")
                targets.append([phase, [j for j, bit in enumerate(indicator) if bit]])
        contacts = []
        chunks = [[]]
        width = len(targets)
        for op, *args in events:
            if op in {"HOST_A", "HOST_B"}:
                slot, *fields = args
                color_type = op[-1]
                require(slot == len(contacts) and len(fields) == len(set(fields))
                        == (4 if color_type == "A" else 2), "ordered literal contact")
                contacts.append((color_type, tuple(fields)))
                chunks.append([])
            else:
                fields = args[:2] if op in TWO_REGISTERS else args[:1]
                require(op in TWO_REGISTERS | IDLES | {"SCALE", "LAMBDA"}, "caller opcode")
                if op in {"ADD", "SCALE"}:
                    require(len(args[-1]) == 2 and any(map(Fraction, args[-1])), "Gaussian literal")
                if op in IDLES:
                    mask = args[1]
                    require(mask and set(mask) <= set(range(16)) and len(mask) == len(set(mask)),
                            "paid idle color mask")
                if op in {"QUERY", "LAMBDA", "IDLE_ODD"}:
                    require(args[-1] in (-1, 1), "signed caller opcode")
                chunks[-1].append((op, *args))
            require(all(0 <= r < width for r in fields), "local source and destination owners")
        require("".join(group for group, _ in contacts) == RECIPE[kind], "literal contact template")
        require(all(sign in (-1, 1) and mask and set(mask) <= set(range(16))
                    and len(mask) == len(set(mask)) for sign, mask in targets), "literal targets")
        templates[kind] = Template(contacts, chunks, targets)
    return templates


def port_inventory(base, layout, graph, homogeneous):
    for key in {"live", "ports", "hosted"}:
        require(layout[key] == base[key], "fixed native port and signed layout")
    require(layout["source_labels"] == base["source_labels"] + [max(base["source_labels"]) + i for i in (1, 2)],
            "two fresh native helper labels")
    labels = layout["source_labels"]
    public = layout["public"]
    require(public == len(labels) == len(set(labels)) == len(graph["initial"]) == len(graph["final"]) == 1262,
            "fixed native independent public owner count")
    hosted = layout["hosted"]
    slots = [(r, r + 112) for r in layout["live"]]
    for p, x, y in zip(hosted["Dports"], hosted["X2"], hosted["Y2"], strict=True):
        slots[p] += (x, y)
    require(tuple(Fraction(hosted[k]) for k in ("alpha", "beta", "alpha2", "beta2"))
            == (-1, Fraction(1, 2), -1, 0), "physical port coefficients")
    ports = {kind: tuple(p for p, fields in enumerate(slots) if len(fields) == width)
             for kind, width in (("A", 4), ("B", 2))}
    require(tuple(map(len, ports.values())) == (96, 8), "96 A and 8 B ports")
    require(all(ports[k] == tuple(homogeneous["types"][k]["ports"]) for k in ("A", "B")),
            "literal template port type matches geometry")
    all_main = set(sum(slots, ()))
    require(len(all_main) == 400 and all_main <= set(range(public)), "distinct compact main addresses")
    helpers = set(range(public)) - all_main
    require(len(helpers) == 862, "fresh helper count per call")
    protected = []
    frames = graph["frames"]
    entry = [frames[i] for i in graph["initial"]]
    exit_ = [frames[i] for i in graph["final"]]
    for regs, q in zip(slots, layout["ports"], strict=True):
        x, y = regs[:2]
        require(entry[x] == [q] and entry[y] == [] and exit_[x] == list(CENTRAL)
                and len(exit_[y]) == 8 and all((q & a).bit_count() % 2 == 0 for a in exit_[y]),
                "literal native entry and exit frames")
        if len(regs) == 4:
            u, v = regs[2:]
            require((entry[u], entry[v], exit_[u], exit_[v]) == (entry[x], entry[y], exit_[x], exit_[y]),
                    "independent hosted second plane")
    for label in (325, 1087):
        role = labels.index(label)
        require(role in helpers and (graph["initial"][role], graph["final"][role]) == (3, 237)
                and entry[role] == [] and exit_[role] == [30, 75, 138, 266], "protected helper boundary")
        protected.append({"compact_role": role, "source_label": label, "target_rank": 4})
    return ports, slots, protected


def parity(a, k):
    return (a & k).bit_count() % 2


def apply_matrix(frame, value):
    out = 0
    for axis, image in zip(CENTRAL, frame, strict=True):
        if value & axis:
            out ^= image
    return out


def check_view(frame, source_head, target_head, shift):
    """Check the X and Y endpoint phase functions on every central character."""
    mapped_head = apply_matrix(frame, source_head)
    for k in range(512):
        mapped = sum(parity(a, k) for a in frame)
        require((k.bit_count() - mapped) % 4 == 2 * parity(shift, k),
                "absolute view translation")
        require(parity(mapped_head, k) == parity(target_head, k),
                "absolute signed head in both X and Y frames")


def views(heads, by_q):
    atlas = []
    for q in heads:
        frame = (q, *by_q[str(q)])
        require(len(frame) == 9 and all(0 < a < 512 for a in frame)
                and all(parity(a, b) == (i == j) for i, a in enumerate(frame) for j, b in enumerate(frame)),
                "orthogonal central phase basis")
        inverse = tuple(sum(axis for axis, image in zip(CENTRAL, frame, strict=True) if image & a)
                        for a in CENTRAL)
        shift = sum(a for a in CENTRAL if sum(bool(a & b) for b in frame) % 4 == 3)
        back = sum(a for a in CENTRAL if sum(bool(a & b) for b in inverse) % 4 == 3)
        check_view(frame, 1, q, shift)
        check_view(inverse, q, 1, back)
        require(all(apply_matrix(inverse, apply_matrix(frame, x) ^ shift) ^ back == x
                    for x in range(512)), "entry and exit affine maps are exact inverses")
        atlas.append((frame, inverse, shift, back))
    require(len(heads) == len(set(heads)) == 104 and all(row[2] for row in atlas),
            "one checked pair of nontrivial views per native port")
    reject(lambda: check_view(atlas[0][0], 1, heads[0], 0), "absolute view translation")
    return atlas


def optimum(calls):
    require(calls >= 16 and calls % 16 == 0, "positive full-color batch length")
    return {"A": 5 * calls // 2 + 56, "B": 8, "mixed": 4 * calls - 64}


def build_schedule(calls, ports):
    """Fill the oldest live mixed cohort first, then the homogeneous color queues."""
    expected = optimum(calls)
    mixed = [[] for _ in range(expected["mixed"])]
    free = {kind: [[] for _ in range(16)] for kind in ("A", "B")}
    for t in range(calls):
        used = {"A": 0, "B": 0}
        for slot in reversed(range(16)):
            start = t - slot
            if start % 2 or start < 2 or start > calls - 16:
                continue
            first_root = 4 * (start - 2)
            kind = RECIPE["mixed"][slot]
            first_port = used[kind]
            batch = ports[kind][first_port:first_port + 8]
            require(len(batch) == 8, "mixed physical capacity")
            for lane, p in enumerate(batch):
                mixed[first_root + lane].append((t, p))
            used[kind] += 8
        for kind in free:
            free[kind][t % 16].extend((t, p) for p in ports[kind][used[kind]:])
    return {kind: [sorted(row) for row in zip(*free[kind], strict=True)] if kind in free else mixed
            for kind in KINDS}


def check_contact_block(t, table, records):
    require(tuple(records) == (
        ("PORT_VIEWS", "ENTER", t, table),
        ("NATIVE", t, t % 16, table),
        ("PORT_VIEWS", "EXIT", t, table),
    ), "both views surround exactly the same main owner table")


def verify_schedule(calls, ports, slots, templates, plan):
    tables = [[None] * 104 for _ in range(calls)]
    blocks = [[] for _ in range(calls + 1)]
    color_uses = {kind: Counter() for kind in KINDS}
    port_colors = set()
    all_owners = 0
    for kind, roots in plan.items():
        template = templates[kind]
        for visits in roots:
            times = [t for t, _ in visits]
            require(len(times) == 16 and times == sorted(set(times)) and 0 <= times[0] <= times[-1] < calls,
                    "one visit per root per call in causal order")
            colors = tuple(t % 16 for t in times)
            require(len(set(colors)) == 16, "root has all sixteen colors")
            color_uses[kind][colors] += 1
            for (t, port), (port_type, fields) in zip(visits, template.contacts, strict=True):
                require(port in ports[port_type], "physical port type at the literal contact")
                require(tables[t][port] is None, "each native port occupied once")
                require(len(fields) == len(set(fields)) == len(slots[port]), "injective plane binding")
                tables[t][port] = [all_owners + field for field in fields]
                port_colors.add((port, t % 16))
            for index, t in enumerate(times + [calls]):
                # Local instructions execute only in cuts with the canonical view active.
                blocks[t].append((kind, index, colors, all_owners))
            all_owners += len(template.targets)
    require({kind: len(roots) for kind, roots in plan.items()} == optimum(calls), "attained endpoint counts")
    require(len(port_colors) == 104 * 16, "all physical port and color pairs")
    width = Counter()
    for table in tables:
        require(all(fields is not None for fields in table), "all physical ports occupied")
        owners = [owner for fields in table for owner in fields]
        require(len(owners) == len(set(owners)) == 400, "distinct arbitrary main owners at each call")
        width.update(map(len, table))
    require(width == Counter({4: 96 * calls, 2: 8 * calls}), "fixed per-call interface widths")
    return tables, blocks, color_uses, all_owners


def read_histograms(template, colors):
    paid = Counter()
    target = Counter()
    uses = Counter()
    gaussian = 0
    coef_width = 0
    negative_heads = 0
    for chunk in template.chunks:
        for op, *args in chunk:
            uses[op] += 1
            if op in {"ADD", "SCALE"}:
                real, imag = map(Fraction, args[-1])
                gaussian += bool(imag)
                coef_width = max(coef_width, *(max(abs(x.numerator).bit_length(), x.denominator.bit_length())
                                               for x in (real, imag)))
            if op == "QUERY":
                paid[1] += 1
            elif op in IDLES:
                mask = sum(BODIES[colors[j]] for j in args[1])
                rank = (mask | int(op == "IDLE_ODD")).bit_count()
                require(rank == 8 * len(args[1]) + (op == "IDLE_ODD"), "physical paid mask rank")
                paid[rank] += 1
    for phase, mask in template.targets:
        negative_heads += phase == -1
        rank = (1 | sum(BODIES[colors[j]] for j in mask)).bit_count()
        require(rank == 8 * len(mask) + 1, "physical target mask rank")
        target[rank] += 1
    return dict(paid=paid, targets=target, uses=uses, gaussian_literals=gaussian,
                negative_heads=negative_heads, coefficient_bits=coef_width)


def count_profiles(templates, color_uses):
    profile = dict(paid=Counter(), targets=Counter(), uses=Counter(),
                   gaussian_literals=0, negative_heads=0, coefficient_bits=0)
    for kind, permutations in color_uses.items():
        for colors, count in permutations.items():
            row = read_histograms(templates[kind], colors)
            for name in ("paid", "targets", "uses"):
                profile[name].update({r: count * n for r, n in row[name].items()})
            for name in ("gaussian_literals", "negative_heads"):
                profile[name] += count * row[name]
            profile["coefficient_bits"] = max(profile["coefficient_bits"], row["coefficient_bits"])
    return profile


def compile_chunk(chunk, colors):
    encoded = []
    for op, *args in chunk:
        count = 2 if op in TWO_REGISTERS else 1
        fields = tuple(args[:count])
        literal = args[count:]
        if op in IDLES:
            literal[0] = [colors[j] for j in literal[0]]
        line = compact([op, *(["%d"] * count), *literal]).replace(b'"%d"', b"%d")
        encoded.append((line, fields))
    return encoded


def stream_digest(templates, tables, blocks, slots, labels):
    """Hash the entire interleaving with no emitted-file storage."""
    compiled = {}
    digest = sha256()
    address_binding = sha256()
    main_addresses = set(sum(slots, ()))
    helpers = sorted(label for i, label in enumerate(labels) if i not in main_addresses)
    helper_hash = sha256(compact(helpers)).hexdigest()
    total = 0
    for t, work in enumerate(blocks):
        for kind, index, colors, offset in work:
            key = (kind, index, colors)
            if key not in compiled:
                compiled[key] = compile_chunk(templates[kind].chunks[index], colors)
            chunk = compiled[key]
            digest.update(b"".join(line % tuple(offset + r for r in fields) for line, fields in chunk))
            total += len(chunk)
        if t < len(tables):
            table = tables[t]
            block = (("PORT_VIEWS", "ENTER", t, table), ("NATIVE", t, t % 16, table),
                     ("PORT_VIEWS", "EXIT", t, table))
            check_contact_block(t, table, block)
            for row in block:
                digest.update(compact(row))
            bindings = [(r, owner) for addresses, owners in zip(slots, table, strict=True)
                        for r, owner in zip(addresses, owners, strict=True)]
            require({r for r, _ in bindings} == main_addresses, "exact compact native address coverage")
            address_binding.update(compact([t, t % 16, sorted(bindings), helper_hash]))
            total += len(block)
    return dict(events=total, stream_sha256=digest.hexdigest(), compact_binding_sha256=address_binding.hexdigest(),
                native_helper_labels_sha256=helper_hash)


def reject(run, expected):
    try:
        run()
    except ValueError as error:
        require(str(error) == expected, f"mutation rejected for unexpected reason: {error}")
    else:
        raise ValueError(f"mutation accepted: {expected}")


def scratch_control(*, leave_last_cell=False):
    """Exercise one serial two-summand service on sixteen guarded array homes."""
    arrays = [[0, 0] for _ in range(16)]
    for op in ("LAMBDA", "LAMBDA", "QUERY"):
        require(all(cell == 0 for home in arrays for cell in home), "caller scratch blank on reuse")
        # Two source, two shifted, eight product and four component-sum arrays.
        extent = 16 if op == "LAMBDA" else 2
        for i in range(extent):
            arrays[i][:] = [1 + i, 2 + i]
        for i in range(extent):
            arrays[i][0] = 0
            if not (leave_last_cell and i == extent - 1):
                arrays[i][1] = 0
    require(all(cell == 0 for home in arrays for cell in home), "caller scratch blank at exit")


def mutations(ports, slots, templates):
    plan = build_schedule(32, ports)
    visits = plan["mixed"][0]
    saved = visits[7]
    visits[7] = (visits[6][0], saved[1])
    reject(lambda: verify_schedule(32, ports, slots, templates, plan), "one visit per root per call in causal order")
    visits[7] = (saved[0], ports["A"][0])
    reject(lambda: verify_schedule(32, ports, slots, templates, plan), "physical port type at the literal contact")
    visits[7] = saved
    visits = plan["B"][0]
    saved = visits[8]
    require((visits[7][0], saved[0], visits[9][0]) == (7, 8, 25), "repeated color control setup")
    visits[8] = (23, saved[1])
    reject(lambda: verify_schedule(32, ports, slots, templates, plan), "root has all sixteen colors")
    visits[8] = saved
    a_first = plan["A"][0][0]
    saved = plan["A"][1][0]
    require(a_first[0] == saved[0], "port collision control setup")
    plan["A"][1][0] = a_first
    reject(lambda: verify_schedule(32, ports, slots, templates, plan), "each native port occupied once")
    plan["A"][1][0] = saved
    tables, *_ = verify_schedule(32, ports, slots, templates, plan)
    table = tables[0]
    incomplete = (("PORT_VIEWS", "ENTER", 0, table), ("NATIVE", 0, 0, table))
    reject(lambda: check_contact_block(0, table, incomplete), "both views surround exactly the same main owner table")
    scratch_control()
    reject(lambda: scratch_control(leave_last_cell=True), "caller scratch blank on reuse")
    return ["same-root simultaneous visits", "wrong physical port type", "repeated root color",
            "same-call physical port collision",
            "missing exit view", "omitted head translation", "dirty scratch reuse"]


def subtract(new, old, copies=2):
    return {key: new.get(key, 0) - copies * old.get(key, 0)
            for key in new.keys() | old.keys() if new.get(key, 0) != copies * old.get(key, 0)}


def validate(package, graph, layout):
    data = {key: read(package / key, digest) for key, digest in SOURCE_FILES.items()}
    require(sha256(compact(graph, ordered=True)).hexdigest() == NATIVE_GRAPH, "exact compact native graph")
    native = data["results/application.json"]
    require(native["graph_sha256"] == NATIVE_GRAPH, "source physical receipt binding")
    held = native["physical"]["native"]
    require(held["exact_all_public_rows"] == held["same_owner_complete_fixture_outputs"] == layout["public"]
            and held["all_public_inputs_preserved_until_final_installs"] and held["retired_and_guards_restored"],
            "inherited native arbitrary-input and cleanup certificate")
    homogeneous = data["data/CALLER.json.gz"]
    templates = read_templates(homogeneous, data["data/CONJUGATE-CALLER.json.gz"])
    ports, slots, protected = port_inventory(data["data/BASE-INTERFACE.json"], layout, graph, homogeneous)
    atlas = views(layout["ports"], data["data/CALLER-PHASE-BASES.json"]["by_q"])
    controls = mutations(ports, slots, templates)
    batches = {}
    for calls in (16, 32, 1024, 2048):
        plan = build_schedule(calls, ports)
        tables, blocks, color_uses, owners = verify_schedule(calls, ports, slots, templates, plan)
        profile = count_profiles(templates, color_uses)
        require(owners == sum(profile["targets"].values()), "complete independent target owners")
        batches[calls] = dict(roots=optimum(calls), owners=owners, profile=profile,
                              native_main_bindings=400 * calls, native_helper_owners=862 * calls,
                              protected_helper_returns=len(protected) * calls,
                              permutations=2 * 400 * calls, translations=2 * 400 * calls,
                              **stream_digest(templates, tables, blocks, slots, layout["source_labels"]))
    parent, candidate = batches[1024], batches[2048]
    require(parent["stream_sha256"] == PARENT_STREAM, "exact full parent event stream")
    require(parent["events"] == 17_777_792, "parent event count")
    recorded = native["caller"]
    require(parent["owners"] == recorded["root_owners"]
            and parent["compact_binding_sha256"] == recorded["finite_binding"]["stage_binding_sha256"]
            and parent["native_helper_labels_sha256"] == recorded["finite_binding"]["helper_label_sha256"]
            and parent["profile"]["paid"] == Counter({int(r): n for r, n in recorded["fixed_caller_paid"].items()})
            and parent["profile"]["targets"] == Counter({int(r): n for r, n in recorded["fixed_root_targets"].items()})
            and parent["profile"]["uses"] == Counter(recorded["uses"])
            and parent["profile"]["gaussian_literals"] == recorded["gaussian_literal_uses"]
            and parent["profile"]["negative_heads"] == recorded["root_negative_q"],
            "independent parent caller census")
    root_delta = subtract(candidate["roots"], parent["roots"])
    require(root_delta == {"A": -56, "B": -8, "mixed": 64}, "exact root exchange")
    local_profiles = {kind: read_histograms(template, tuple(range(16))) for kind, template in templates.items()}
    old_profile, new_profile = parent["profile"], candidate["profile"]
    paid_delta = subtract(new_profile["paid"], old_profile["paid"])
    target_delta = subtract(new_profile["targets"], old_profile["targets"])
    signed_delta = subtract(target_delta, paid_delta, copies=1)
    uses_delta = subtract(new_profile["uses"], old_profile["uses"])
    require(paid_delta == {1: -224, 8: -224, 9: -32} and target_delta == {9: -256},
            "exact signed rank delta")
    gaussian_delta = new_profile["gaussian_literals"] - 2 * old_profile["gaussian_literals"]
    negative_delta = new_profile["negative_heads"] - 2 * old_profile["negative_heads"]
    old_bits = max(native["physical"]["scalars"]["coefficient_bits"], old_profile["coefficient_bits"])
    new_bits = max(native["physical"]["scalars"]["coefficient_bits"], new_profile["coefficient_bits"])
    require(old_bits == new_bits == native["physical"]["components"]["coefficient_bits"],
            "unchanged scalar width from identical literal coefficients")
    scalar_rate = 2 ** max(20, new_bits + 8)
    require(scalar_rate == native["physical"]["ordinary"]["scalar_step_rate"], "retained scalar rate")
    require(all(candidate[k] == 2 * parent[k] for k in
                ("native_main_bindings", "native_helper_owners", "protected_helper_returns", "permutations", "translations")),
            "same native and view occurrence rates at equal call count")
    map_delta = (2 * (sum(paid_delta.values()) + sum(target_delta.values()))
                 + 2 * (uses_delta["IDLE_ONE"] + uses_delta["IDLE_ODD"])
                 + 3 * uses_delta["QUERY"] + uses_delta["LAMBDA"] + uses_delta["IDLE_ODD"]
                 + negative_delta + 2 * gaussian_delta)
    conversions_delta = 2 * sum(target_delta.values())
    raw_components_delta = 64 * (gaussian_delta + uses_delta["LAMBDA"])
    return {
        "scope": "full-occupancy, strict chronological, all-color schedules using these three literal templates",
        "input_identities": ["pinned source's exact local Gaussian signed diagonal identities",
                             "pinned native arbitrary-input direct sum and native cleanup"],
        "first_call_homogeneous_B_owner_lower_bound": len(ports["B"]),
        "source": {"head": HEAD, "native_graph_sha256": NATIVE_GRAPH, "files": SOURCE_FILES,
                   "graph_export_files": GRAPH_SOURCE_FILES},
        "port_capacity": {kind: len(group) for kind, group in ports.items()},
        "standalone_view_atlas_sha256": sha256(compact(atlas)).hexdigest(),
        "protected_helpers": protected,
        "controls_rejected": controls,
        "templates": local_profiles,
        "batches": batches,
        "contiguous_2048_minus_two_sealed_1024": {
            "native_calls": 0, "root_counts": root_delta, "paid_ranks": paid_delta,
            "productive_ranks": target_delta, "caller_operations": uses_delta,
            "net_signed_margin_ranks": signed_delta,
            "nonreal_literals": gaussian_delta, "negative_head_corrections": negative_delta,
            "port_view_permutations": 0, "port_view_translations": 0,
            "odd_conversions": conversions_delta, "ordinary_map_slots": map_delta,
            "extra_gaussian_component_slots_before_factor_32": raw_components_delta,
            "ordinary_scalar_services_after_factor_32": 32 * (sum(uses_delta.values())
                                                               + conversions_delta + raw_components_delta),
            "same_scalar_width": new_bits, "same_scalar_step_rate": scalar_rate,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="pinned PR 7756 source package")
    parser.add_argument("--native-graph", type=Path, help="optional JSON or gzip graph export")
    parser.add_argument("--native-layout", type=Path, help="optional JSON layout for the exported graph")
    parser.add_argument("--output", type=Path, help="write the deterministic JSON receipt to this path")
    args = parser.parse_args()
    if bool(args.native_graph) != bool(args.native_layout):
        parser.error("supply --native-graph and --native-layout together")
    graph, layout = (read(args.native_graph), read(args.native_layout)) if args.native_graph else export_graph(args.source)
    receipt = json.dumps(validate(args.source, graph, layout), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(receipt, encoding="utf-8")
    else:
        print(receipt, end="")


if __name__ == "__main__":
    main()
