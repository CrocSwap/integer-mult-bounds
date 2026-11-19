#!/usr/bin/env python3
"""Rebuild and audit the 21 funded GF(2) helper births. Apache-2.0.

The #7776 eight-puncture graph, native emitter and paired caller are retained
with attribution to Ali Romman and the #7000/#7001 lineage. The new paid
subdivisions and calibrated helper returns are constructive replay records.
"""
import argparse
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ALI = Path("research/p104-dual-supplier-lift")
PAIRED = Path("research/paired-query-only-bit")
HEAD = "4f7c67ae387cc91580f469aeda4d508b372b9ec1"
EARLIER_HEAD = "0b86d0f618b8c64be9410a83a417067049076067"
PARENT = "07f5fe923b50ecc26983054cf8f462b1a2b4a008a5e2c7a472209363abaaa35c"
PROGRAM = "861f5181e4f34db638ab0c573c319fe26ff034d63b21242d67220a4a5d6433ff"
PAYLOAD = "e5871a4cf87d62aa90e6660d351636aa5ca47f50239916a0943cd433c7f3d323"
RECIPE = "9cdb651f7166c01abb9027535d36424da71944932f3b6f84057a12ae12ba6ad2"
GZIP = "a63f07a5f5ac4aa28b5b635c7836f36efafd03b735ab13f24c8b481d137d54e8"
SOURCE_PINS = {
    ALI / "bit_native.py": "4368c62a5d42f81189d6776b8dba8c85a311b6a199b816244b545c6bb7d3dc1e",
    ALI / "bit_application.py": "fa76543d0aa0d515b48eaa9516f73df2c34a5f482114080fe3bcd6d37c32bbbd",
    ALI / "BIT-RESULT.json": "907858ba4c6f4c110662c8ea9faa1209acca07a9ae281ba29e9291a41fe8e6e1",
    PAIRED / "EFREE-CALLER.json.gz": "757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b",
    PAIRED / "check.py": "460ed9a77d66264b00c31d0a7f8dab1db9aab21ec4cc0eaf0452bd4be4ef585e",
    PAIRED / "retained/audit_binary_mixed.py": "bb6616dbf536acf10163b8fff65ebfa69d01dfdeda3c0ead388c03377361b298",
    PAIRED / "retained/inputs/BIT-NATIVE-WORD.json.gz":
        "51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78",
}
HEAD_MASK = (1 << 111) - 1
CALLS = 36
BIRTHS = 21


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_sha(path, expected):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == expected, "SHA-256 pin: " + str(path))
    return raw


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


def bits(row):
    while row:
        least = row & -row
        yield least.bit_length() - 1
        row ^= least


def mask(labels):
    need(len(labels) == len(set(labels)) and all(type(r) is int and r >= 0 for r in labels),
         "distinct nonnegative basis labels")
    return sum(1 << r for r in labels)


def xor(row, values):
    result = 0
    for k in bits(row):
        result ^= values[k]
    return result


def transfer(column, reverse):
    """Full endpoint on a column in the selected orientation."""
    if reverse:
        return column ^ ((column >> 111) & HEAD_MASK)
    return column ^ ((column & HEAD_MASK) << 111)


def parity(u, v):
    return (u & v).bit_count() & 1


@dataclass
class Network:
    initial: dict
    final: dict
    moves: dict
    rows: dict

    def transpose(self):
        rows = dict.fromkeys(self.rows, 0)
        for k, row in self.rows.items():
            sender = ~k if k < 0 else k
            for j in bits(row):
                rows[~j if j in self.initial else j] ^= 1 << sender
        return Network(self.final, self.initial, {k: (b, a) for k, (a, b) in self.moves.items()}, rows)

    def validate(self, edge, reverse):
        order = edge.schedule(self.initial, self.final, self.moves, self.rows)
        values = {r: 1 << r for r in self.initial}
        for k in order:
            values[k] = xor(self.rows[k], values)
        columns = dict.fromkeys(values, 0)
        for r in self.initial:
            row = self.rows[~r]
            need(xor(row, values) == transfer(1 << r, not reverse),
                 f"forward public return at owner {r}")
            for k in bits(row):
                columns[k] ^= 1 << r
        for k in reversed(order):
            for j in bits(self.rows[k]):
                columns[j] ^= columns[k]
        for r in self.initial:
            need(columns[r] == transfer(1 << r, reverse),
                 f"adjoint public return at owner {r}")
        return order, values, columns


def make_baseline(root, edge):
    source = edge.read_pinned(root, edge.NATIVE, edge.NATIVE_SHA)
    initial, final, moves, rows, original_clocks = edge.extract(source)
    for r, *ordinals in edge.PUNCTURES:
        zero, alias, donor = [source["public"] + i for i in ordinals]
        order = edge.schedule(initial, final, moves, rows)
        impulse = edge.basis(initial, moves, rows, order)
        need(impulse[zero] == impulse[alias] ^ impulse[donor] == 1 << r,
             "retained helper puncture impulse")
        need(moves[alias][0] == moves[donor][0], "retained helper puncture sender")
        initial, final, moves, rows = edge.puncture(initial, final, moves, rows, r, zero, alias, donor)
    graph = Network(initial, final, moves, rows)
    order, _, _ = graph.validate(edge, False)
    word = edge.emit_word(source, initial, final, moves, rows, order)
    need(edge.digest(word) == PARENT, "canonical #7776 public BIT baseline")
    clocks = [j for j, op in enumerate(word["program"]) if op[0] == "MOVE"]
    need((len(initial), len(order), len(clocks)) == (651, 2855, 2855), "source inventory")
    return source, graph, original_clocks, dict(zip(order, clocks))


def strict_chain(frames, audit, a, c, b):
    source, middle, target = (frames[str(x)] for x in (a, c, b))
    if source["dim"] > target["dim"]:
        source, target = target, source
    return (source["dim"] < middle["dim"] < target["dim"]
            and audit.included(source, middle) and audit.included(middle, target))


def apply_birth(net, step, frames, edge, audit):
    """Subdivide the paid contact, then insert calibrated independent local input."""
    need(step["reverse"] is True, "recorded transposed birth orientation")
    witness = step["witness"]
    h, c = witness["role"], witness["chart"]
    e, f = step["source_packet"], step["new_packet"]
    a, b = net.moves[e]
    A, B = net.initial[h], net.final[h]
    need(h >= 222, "only a productive helper can split")
    need(([a, b], [A, B]) == (step["old_move_charts"], step["old_helper_charts"]),
         "paid and productive endpoint preimage")
    need(strict_chain(frames, audit, a, c, b) and strict_chain(frames, audit, A, c, B),
         "both intermediate rational nesting chains")
    dim = {key: frames[str(key)]["dim"] for key in (a, b, A, B, c)}
    paid_ranks = [abs(dim[a] - dim[c]), abs(dim[b] - dim[c])]
    target_ranks = [abs(dim[A] - dim[c]), abs(dim[B] - dim[c])]
    need((paid_ranks, target_ranks) == (step["paid_daughter_ranks"], step["target_daughter_ranks"]),
         "all four daughter grades")
    need(f == max(net.initial.keys() | net.moves.keys()) + 1, "fresh subdividing paid field")
    fresh = f + 1
    moves = net.moves | {f: (a, c), e: (c, b)}
    divided_rows = net.rows | {f: net.rows[e], e: 1 << f}
    subdivided = Network(net.initial, net.final, moves, divided_rows)

    q, k, d, readout, calibration, pulse = (
        mask(witness[name]) for name in ("q", "k", "d", "readout", "calibration", "pulse")
    )
    response = transfer(d, True)
    return_combination = transfer(k, False)
    pivot = 1 << h
    need(all(net.initial.get(i) == A for i in bits(q | d)), "cocharted entrance basis")
    need(all(net.final.get(i) == B for i in bits(response | return_combination)),
         "cocharted exit basis")
    need(response & pivot and parity(q, d) and parity(k, d), "nondegenerate calibration")
    schedule, values, columns = subdivided.validate(edge, True)
    donors = net.initial | {j: v for j, (_, v) in moves.items()}
    need(all(donors.get(j) == c for j in bits(readout | calibration)), "local readout and calibration")
    need(all(j in moves and moves[j][0] == c for j in bits(pulse)), "local injection at paid sender")
    need(xor(readout, values) == q and xor(calibration, values) == k, "exact measured basis rows")
    need(xor(pulse, columns) == response, "exact measured terminal impulse")

    # Propagate a common unit pulse on the subdivided graph with all
    # independent inputs set to zero. The added signal cannot feed either
    # local readout or calibration.
    feedback = 0
    for t in schedule:
        sender = 1 << t
        if parity(divided_rows[t], feedback) ^ bool(pulse & sender):
            feedback |= sender
    need(parity(feedback, readout) == parity(feedback, calibration) == 0,
         "zero pulse feedback into local readout and calibration")

    replacement = pivot | (q & ~pivot)

    def rewrite(row):
        return (row & ~pivot) ^ (replacement if parity(row, d) else 0)

    rows = {t: rewrite(row) for t, row in divided_rows.items()}
    correction = (1 << fresh) ^ rewrite(calibration)
    for t in bits(pulse):
        rows[t] ^= correction
    returned = 0
    for i in bits(return_combination):
        returned ^= rows[~i]
    old_pivot = rows[~h]
    for i in bits(response & ~pivot):
        rows[~i] ^= old_pivot
    rows[~h], rows[~fresh] = rewrite(readout), returned

    candidate = Network(net.initial | {fresh: c}, net.final | {h: c, fresh: B}, moves, rows)
    candidate.validate(edge, True)
    return candidate, fresh


def rejection(function, expected):
    try:
        function()
    except ValueError as error:
        need(expected in str(error), "wrong mutation failure: " + str(error))
        return str(error)
    raise ValueError("mutation was accepted: " + expected)


def zero_paid_packet(word, paid_slot):
    """Preserve events and charts, but replace the selected private payload by zero."""
    program = word["program"]
    moves = [j for j, event in enumerate(program) if event[0] == "MOVE"]
    clock = moves[paid_slot]
    field = program[clock][1]
    birth = next(j for j in range(clock - 1, -1, -1) if program[j][:2] == ["INIT", field])
    need(birth + 1 < clock and all(event[:2] == ["ADD", field]
                                   for event in program[birth + 1:clock]), "complete local accumulator")
    return word | {"program": program[:birth + 1] + program[clock:]}, clock, field


def counter(value):
    return Counter({int(rank): count for rank, count in value.items()})


def replay(root, *, frozen_word=HERE / "WORD.json.gz"):
    if (root / ".git").exists():
        actual_head = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"], check=True,
            capture_output=True, text=True,
        ).stdout.strip()
        need(actual_head in (HEAD, EARLIER_HEAD), "#7776 source checkout head")
    sys.dont_write_bytecode = True
    for path, digest in SOURCE_PINS.items():
        read_sha(root / path, digest)
    edge = module(root / ALI / "bit_native.py", "bit_native")
    app = module(root / ALI / "bit_application.py", "birth_parent_application")
    audit = module(root / PAIRED / "retained/audit_binary_mixed.py", "birth_parent_physical_audit")
    paired = module(root / PAIRED / "check.py", "birth_parent_paired_caller")
    recipe = json.loads(read_sha(HERE / "BIRTHS.json", RECIPE))
    need(recipe["schema"] == "binary-subdivided-helper-births-recipe/1"
         and (recipe["parent_pr"], recipe["parent_head"], recipe["previous_public_head"],
              recipe["parent_program_sha256"], recipe["program_sha256"], len(recipe["steps"]))
         == (7776, HEAD, EARLIER_HEAD, PARENT, PROGRAM, BIRTHS),
         "pinned recipe and both program identities")
    source, baseline, old_clocks, baseline_clocks = make_baseline(root, edge)
    adjoint = baseline.transpose()
    adjoint.validate(edge, True)
    base_receipt = json.loads((root / ALI / "BIT-RESULT.json").read_bytes())
    need(base_receipt["native"]["program_sha256"] == PARENT, "public #7776 result binding")
    expected_paid = counter(base_receipt["native_paid"])
    expected_targets = counter(base_receipt["native_targets"])
    controls = {}
    new_moves = []
    step_results = []
    for ordinal, step in enumerate(recipe["steps"], 1):
        e = step["source_packet"]
        need(old_clocks[e] == step["original_selected_source_clock"], "literal selected source clock")
        if ordinal == 1:
            broken = step | {"witness": step["witness"] | {"readout": []}}
            controls["omitted_readout"] = rejection(
                lambda: apply_birth(adjoint, broken, source["frames"], edge, audit),
                "exact measured basis rows")
        adjoint, new_helper = apply_birth(adjoint, step, source["frames"], edge, audit)
        paid = step["paid_daughter_ranks"]
        targets = step["target_daughter_ranks"]
        expected_paid[sum(paid)] -= 1
        expected_paid.update(paid)
        expected_targets[sum(targets)] -= 1
        expected_targets.update(targets)
        new_moves.append(step["new_packet"])
        step_results.append(dict(step=ordinal, helper_owner=step["witness"]["role"],
                                 new_helper_owner=new_helper, selected_original_clock=old_clocks[e],
                                 residual_forward_clock=baseline_clocks[e], source_packet=e,
                                 new_packet=step["new_packet"], internal_chart=step["witness"]["chart"]))
    forward = adjoint.transpose()
    schedule, _, _ = forward.validate(edge, False)
    need((len(forward.initial), len(schedule)) == (672, 2876), "candidate inventory")
    need(all(forward.initial[r] == baseline.initial[r] and forward.final[r] == baseline.final[r]
             for r in range(222)), "all 222 literal main boundaries")
    for r in set(baseline.initial) - {step["witness"]["role"] for step in recipe["steps"]}:
        need((forward.initial[r], forward.final[r]) == (baseline.initial[r], baseline.final[r]),
             f"unchanged helper boundary {r}")

    word = edge.emit_word(source, forward.initial, forward.final, forward.moves, forward.rows, schedule)
    need(edge.digest(word) == PROGRAM, "canonical emitted program")
    wire = (json.dumps(word, separators=(",", ":")) + "\n").encode()
    need(sha256(wire).hexdigest() == PAYLOAD, "exact emitted file payload")
    gzip_hash = None
    if frozen_word is not None:
        raw = read_sha(frozen_word, GZIP)
        need(gzip.decompress(raw) == wire, "frozen word is reproduced byte for byte")
        gzip_hash = sha256(raw).hexdigest()
    app.reverse(word)
    literal_paid, literal_targets, native = audit.source_audit(word)
    need(literal_paid == +expected_paid and literal_targets == +expected_targets, "native histograms")
    caller = app.read_pinned(root, PAIRED / "EFREE-CALLER.json.gz", app.CALLER_SHA)
    coefficients = paired.forward(caller)
    need(coefficients == audit.backward(caller) == 38 ** 2, "complete paired caller in both directions")
    targets, paid, contacts = app.frames_and_sites(word, caller, native, audit)
    for name, base, improved, native_base, native_improved in (
        ("paid", base_receipt["paid"], paid, base_receipt["native_paid"], literal_paid),
        ("targets", base_receipt["targets"], targets, base_receipt["native_targets"], literal_targets),
    ):
        predicted = counter(base)
        native_parent = counter(native_base)
        for rank in native_improved.keys() | native_parent.keys():
            predicted[rank] += CALLS * (native_improved[rank] - native_parent[rank])
        need(+predicted == improved, "signed 36-call " + name)
    need(contacts["rank_surplus"] == base_receipt["signed_positions"]["rank_surplus"]
         and contacts["native_calls"] == CALLS, "conserved rank mass and 36 actual invocations")
    ordinary = app.ordinary(word, caller, targets, paid)

    # Zero one demonstrably active fresh paid payload with all charts and
    # field lifetimes held fixed. Independent literal adjoint must reject.
    modified, clock, field = zero_paid_packet(word, schedule.index(new_moves[0]))
    controls["zero_first_new_paid"] = dict(clock=clock, field=field, rejection=rejection(
        lambda: app.reverse(modified), "independent emitted-word full transpose"))
    # Missing release of one owned full field is a physical lifetime failure.
    deleted_clear = dict(word, program=word["program"][:-1])
    controls["missing_clear"] = rejection(lambda: audit.source_audit(deleted_clear),
                                           "all endpoints and owned lifetimes")
    receipt = dict(
        schema="binary-subdivided-helper-births-replay/1", parent_pr=7776, source_head=HEAD,
        source_word_sha256=PARENT, word_sha256=PROGRAM, word_file_sha256=PAYLOAD,
        word_gzip_sha256=gzip_hash, recipe_sha256=RECIPE,
        source_inputs={str(k): v for k, v in SOURCE_PINS.items()},
        steps=step_results, added_helpers=BIRTHS, instruction_counts=dict(Counter(
            instruction[0] for instruction in word["program"])),
        checked_literal_coefficients_each_direction=word["public"] ** 2,
        caller_coefficients_each_way=coefficients,
        native_paid=dict(literal_paid), native_targets=dict(literal_targets),
        paid=dict(paid), targets=dict(targets), signed_positions=contacts, ordinary=ordinary,
        native={k: v for k, v in native.items() if k != "charts"},
        mutation_controls=controls,
    )
    return wire, receipt


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--source-root", type=Path, required=True,
                     help="checkout or unpacked source tree of #7776 at " + HEAD)
    cli.add_argument("--write-json", type=Path, help="write complete replay receipt")
    cli.add_argument("--rebuild-word", type=Path,
                     help="generate a new gzip from the pinned payload instead of reading WORD.json.gz")
    args = cli.parse_args()
    frozen = HERE / "WORD.json.gz" if args.rebuild_word is None else None
    wire, receipt = replay(args.source_root.resolve(), frozen_word=frozen)
    if args.rebuild_word is not None:
        raw = gzip.compress(wire, compresslevel=9, mtime=0)
        args.rebuild_word.write_bytes(raw)
        receipt["word_gzip_sha256"] = sha256(raw).hexdigest()
    if args.write_json:
        args.write_json.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS_21_BINARY_HELPER_BIRTHS", receipt["word_sha256"],
          receipt["native"]["public"], receipt["signed_positions"]["native_calls"])


if __name__ == "__main__":
    main()
