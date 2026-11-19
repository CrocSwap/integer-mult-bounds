#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Rebuild the rational successor and its two-return control from #7781."""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import paid_projection as projection
from word_delta import restore


FIRST = ("0408fbe51fdd524e68ee4a17595338e9871fed7bd8b834a67314301272d55e68",
         "e245f29ebb3056e97d7f54b25d5ef4051988edbf95fb147d104edbb109abc1cd")
THREE = ("0359414004d493d92dd3a64b85a1748bd187c57f954150d1e4ce8e363b3a45bd",
         "0a31c788ebbe7109097d8185cbe7274ac2a0749882c40aa8557a053fd5868b18")
BOUNDARY = "91a6ffbfa0c20741daca5a973c31a66ae5405ebfda1c821072531101962e2edb"
PINS = {
    "BIRTHS.json": "cafb95f801d7f8a2b04875f929eff07909621115ee0b730f569d0f066fa5926b",
    "PROJECTIONS.json": "1a0f09e46f52a71dcde6aa682722c60d8a75856e4c67edd40ab89d029c05135e",
    "THREE-BIRTHS.json": "7b785272b7e937f8feb6bf03f3663b33dc927675651b8a232bd552dd2bb17c90",
    "BOUNDARY-PROJECTION.json": "3a89548848fdf5ed6c5d8f605f1ad8ce0ddfa07ac988b933ae054608519cc5c5",
}


def run(script, *arguments):
    subprocess.run([sys.executable, "-I", "-B", str(script), *map(str, arguments)], check=True)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def pin(filename, expected):
    need(Path(filename).name == filename, "construction data must be in this package")
    path = HERE / filename
    need(sha256(path.read_bytes()).hexdigest() == expected, f"construction data digest {filename}")
    return path


def mark_pair(word, layout, required, name):
    got = projection.digest(word), projection.digest(layout)
    need(got == required and word["frames"] == layout["frames"], f"{name} word and layout pins")
    return dict(word_sha256=got[0], layout_sha256=got[1], public=len(word["initial"]))


def read_pair(directory):
    return tuple(projection.load(directory / f"{field}.json.gz") for field in ("WORD", "LAYOUT"))


def write_pair(directory, word, layout):
    directory.mkdir(parents=True, exist_ok=True)
    for field, value in (("WORD", word), ("LAYOUT", layout)):
        (directory / f"{field}.json.gz").write_bytes(gzip.compress(projection.canonical(value), mtime=0))


def project(cache, word, layout, source, expected, journal, out):
    run(HERE / "paid_projection.py", "--source-root", cache / "source", "--word", word,
        "--layout", layout, "--word-sha", source[0], "--layout-sha", source[1],
        "--expected", expected, "--journal", journal, "--out", out)
    report = projection.load(out / "PROJECTIONS-REPLAY.json")
    need(report["child_sha256"] == expected and all(step["omission"]["coefficient_difference"] != "0"
                                                   for step in report["steps"]),
         "actual projection restoration witnesses")
    return report


def counter_difference(new, old):
    result = Counter(new)
    result.subtract(old)
    return {str(rank): count for rank, count in sorted(result.items()) if count}


def network_for(network, raw):
    result = network.Network(raw["first_output"], raw["initial"], raw["final"],
                             {t: (a, b) for t, a, b in raw["moves"]},
                             {t: network.coefficients(row) for t, row in raw["forms"]})
    need(projection.dump_graph(result, raw["frames"]) == raw, "canonical causal paid-chain word")
    return result


def omission(net, keys, puncture):
    order = net.schedule()
    results = []
    for key in keys:
        first = net.first_output
        response = puncture.pulse_response(net, order, {key: Fraction(1)})
        seen = sorted((k - first, q) for k, q in response.items() if k >= first)
        payload = puncture.entrance_form(net, order, {key: Fraction(1)})
        need(seen and payload, f"inserted paid field {key} must have an observable nonzero payload")
        row, coefficient = seen[0]
        column, value = min(payload.items())
        results.append(dict(position=key, row=row, column=column,
                            omitted_coefficient_difference=str(-coefficient * value)))
    return results


def chains(cache, word, layout, plan):
    need(plan["schema"] == "p104-paid-chain-sequence/1" and plan["stages"], "paid-chain declaration")
    layout_sha = plan["layout_sha256"]
    mark_pair(word, layout, (plan["source_word_sha256"], layout_sha), "paid-chain predecessor")
    network, puncture = projection.engines(cache / "source")
    source_net = network_for(network, word)
    old_net = source_net
    records = []
    for stage in plan["stages"]:
        journal = projection.load(pin(stage["journal"], stage["journal_sha256"]))
        need(journal["schema_version"] == 1, "literal sparse paid-chain journal schema")
        next_word = restore(word, journal)
        need(restore(next_word, journal, reverse=True) == word, "reversible exact paid-chain journal")
        claim = mark_pair(next_word, layout, (stage["word_sha256"], layout_sha), "paid chain")
        changed = network_for(network, next_word)
        old_positions, new_positions = set(old_net.moves), set(changed.moves)
        added, removed = sorted(new_positions - old_positions), sorted(old_positions - new_positions)
        need((added, removed) == (stage["added_paid"], stage["removed_paid"]), "literal paid-chain positions")
        frames = next_word["frames"]
        old_ranks = Counter(projection.rank(frames, leg) for leg in old_net.moves.values())
        new_ranks = Counter(projection.rank(frames, leg) for leg in changed.moves.values())
        delta = counter_difference(new_ranks, old_ranks)
        need(delta == stage["paid_delta"], "complete signed paid-chain delta")
        changed_width = max(max(abs(q.numerator).bit_length(), q.denominator.bit_length())
                            for key, row in changed.forms.items()
                            if old_net.forms.get(key) != row for q in row.values())
        need(changed_width <= 24, "paid-chain changed scalar bit width")
        records.append(claim | dict(added_paid=added, removed_paid=removed, paid_delta=delta,
                                    max_changed_scalar_bits=changed_width,
                                    omission=omission(changed, added, puncture),
                                    opposite_omission=omission(changed.transpose(), added, puncture)))
        word, old_net = next_word, changed
    n = len(source_net.initial)
    need(projection.endpoints(source_net) == projection.endpoints(old_net)
         and projection.endpoints(source_net.transpose()) == projection.endpoints(old_net.transpose()),
         "full forward and adjoint operators across the complete paid-chain sequence")
    return word, dict(stages=records, all_forward_and_adjoint_rows_each=n, productive_delta={})


def rotated_splits(cache, word, layout, plan):
    rotated = plan["schema"] == "p104-rotated-splits/1" and plan["stages"]
    continued = (plan["schema"] == "p104-continued-births/1" and not plan["stages"]
                 and plan["continuation"] and all(step["kind"] == "birth" for step in plan["continuation"]))
    need(rotated or continued, "nonempty rotated-split or continued-birth declaration")
    source = plan["source"]
    mark_pair(word, layout, (source["word_sha256"], source["layout_sha256"]), "rotated-split predecessor")
    source_root = cache / "source"
    network, puncture = projection.engines(source_root)
    import bank_split
    import public_split

    donor = source_root.resolve() / projection.ENGINE
    need(Path(public_split.__file__).resolve() == donor / "public_split.py"
         and Path(bank_split.__file__).resolve() == donor / "bank_split.py", "use verified split modules")
    current = network_for(network, word)
    hosted = layout["hosted"]
    main = set(layout["live"]) | {i + 112 for i in layout["live"]} | set(hosted["X2"]) | set(hosted["Y2"])
    count = len(current.initial)
    need(len(main) == 400 and count == len(current.final) == layout["public"]
         == len(set(layout["source_labels"])), "rotated-split public owner inventory")
    main_placement = {i: (current.initial[i], current.final[i]) for i in main}

    def inventory(net, frames):
        paid = Counter(projection.rank(frames, leg) for leg in net.moves.values())
        productive = Counter(projection.rank(frames, (a, b), productive=True)
                             for i, (a, b) in enumerate(zip(net.initial, net.final, strict=True)) if i not in main)
        return paid, productive

    endpoints = projection.endpoints(current), projection.endpoints(current.transpose())
    paid, productive = inventory(current, word["frames"])
    rotations, rescalings, continuation = [], [], []
    steps = [("rotation", step, rotations) for step in plan["stages"]]
    steps += [("paid_rescaling", step, rescalings) for step in plan.get("paid_rescalings", [])]
    steps += [(step["kind"], step, continuation) for step in plan.get("continuation", [])]
    for kind, stage, records in steps:
        before = dict(word_sha256=projection.digest(word), layout_sha256=projection.digest(layout))
        frames = word["frames"] + stage.get("frames", [])
        if kind == "rotation":
            event = stage["event"]
            need(set(event) == {"old", "new", "transposed", "arrivals", "sends", "rotations", "generators", "removed_paid"}
                 and type(event["transposed"]) is bool and event["rotations"], "literal rotated-split event")
            projection.rank(frames, (event["old"], event["new"]))
            changed = public_split.split(current, event)
            added_paid = sorted(g["slot"] for g in event["generators"])
            removed_paid = sorted(event["removed_paid"])
            details = {}
        elif kind == "paid_rescaling":
            slot, scalar = stage["slot"], stage["scale"]
            scale = Fraction(scalar)
            need(type(slot) is int and slot in current.moves and type(scalar) is str
                 and str(scale) == scalar and scale not in (0, 1), "nontrivial rational internal paid rescaling")
            forms = current.forms.copy()
            forms[slot] = {i: q * scale for i, q in current.forms[slot].items()}
            readers = sorted(i for i, row in current.forms.items() if slot in row)
            need(readers, "rescaled paid scalar has retained readers")
            for i in readers:
                row = current.forms[i]
                forms[i] = {**row, slot: row[slot] / scale}
            changed = network.Network(current.first_output, current.initial, current.final, current.moves, forms)
            added_paid, removed_paid = [], []
            details = dict(slot=slot, scale=scalar, readers=readers)
        elif kind == "birth":
            from birth_event import apply_split
            from portable_chain import edit, operator_check

            need(Path(sys.modules[apply_split.__module__].__file__).resolve() == donor / "birth_event.py",
                 "use the verified birth engine")
            role = stage["event"]["role"]
            need(type(role) is int and 0 <= role < count and role not in main
                 and type(stage["reverse"]) is bool and stage["event"]["pulse"], "one existing helper to split")
            changed = edit(current, stage, apply_split)
            need(all((changed.initial[i], changed.final[i]) == (current.initial[i], current.final[i])
                     for i in range(count) if i != role), "all other old owner charts after helper birth")
            endpoints = tuple(rows + [{count: Fraction(1)}] for rows in endpoints)
            count += 1
            labels = layout["source_labels"]
            layout = dict(layout, public=count, source_labels=labels + [max(labels) + 1])
            added_paid = sorted(leg["new_key"] for leg in stage["paid_subdivisions"])
            removed_paid = []
            controls = {}
            faults = ["no_pulse"]
            event = stage["event"]
            if event.get("fresh_source_chart", event["split_chart"]) == event["split_chart"]:
                faults.append("fresh_into_old")
            for fault in faults:
                broken = edit(current, stage, apply_split, fault=fault)
                forward = operator_check(broken, endpoints[0])
                adjoint = operator_check(broken.transpose(), endpoints[1])
                need(forward is not None and adjoint is not None, f"observable helper-birth fault {fault}")
                controls[fault] = dict(forward=forward, adjoint=adjoint)
            details = dict(split_role=role, independent_new_owner=count - 1, controls=controls,
                           omission=omission(changed, added_paid, puncture),
                           opposite_omission=omission(changed.transpose(), added_paid, puncture))
        else:
            raise ValueError(f"unknown rotated continuation step {kind}")

        next_word = projection.dump_graph(changed, frames)
        layout = dict(layout, frames=frames)
        mark = mark_pair(next_word, layout, (stage["word_sha256"], stage["layout_sha256"]), kind)
        need(len(changed.initial) == len(changed.final) == count == layout["public"]
             and all((changed.initial[i], changed.final[i]) == leg for i, leg in main_placement.items()),
             "all main head placements and public slots remain fixed")
        if kind == "paid_rescaling":
            need(all(next_word[key] == word[key] for key in ("frames", "initial", "final", "first_output", "moves", "schedule")),
                 "internal rescaling preserves every paid route, public owner and clock")
        need(added_paid == sorted(changed.moves.keys() - current.moves.keys())
             and removed_paid == sorted(current.moves.keys() - changed.moves.keys()), "literal added and removed paid legs")
        new_paid, new_productive = inventory(changed, frames)
        paid_delta = counter_difference(new_paid, paid)
        productive_delta = counter_difference(new_productive, productive)
        expected_delta = ({}, {}) if kind == "paid_rescaling" else (stage["paid_delta"], stage["productive_delta"])
        need((paid_delta, productive_delta) == expected_delta, "every realized paid and independent productive rank change")
        need(endpoints == (projection.endpoints(changed), projection.endpoints(changed.transpose())),
             f"all exact forward and adjoint endpoint rows after {kind}")
        records.append(mark | dict(kind=kind, preimage=before, added_paid=added_paid, removed_paid=removed_paid,
                                   paid_delta=paid_delta, productive_delta=productive_delta) | details)
        current, word, paid, productive = changed, next_word, new_paid, new_productive
    final = plan["final"]
    mark = mark_pair(word, layout, (final["word_sha256"], final["layout_sha256"]), "rotated-split final word")
    return word, layout, dict(final=mark, stages=rotations, paid_rescalings=rescalings, continuation=continuation,
                              all_forward_and_adjoint_rows_each=count)


def construct(cache, word_path, layout_path, out, first_only=False):
    run(HERE.parent / "prepare_sources.py", cache)
    journal = {name: pin(name, digest) for name, digest in PINS.items()}
    base = mark_pair(projection.load(word_path), projection.load(layout_path),
                     (projection.WORD, projection.LAYOUT), "submitted #7781")
    stages = {}
    projected = out / "projected"
    stages["first_projections"] = project(cache, word_path, layout_path,
                                          (projection.WORD, projection.LAYOUT), projection.CANDIDATE,
                                          journal["PROJECTIONS.json"], projected)
    first, births = out / "first", out / "births"
    if first_only:
        run(HERE / "births.py", "--cache", cache, "--word", projected / "WORD.json.gz",
            "--layout", projected / "LAYOUT.json.gz", "--journal", journal["BIRTHS.json"],
            "--parent-layout", projection.LAYOUT, "--child-layout", FIRST[1], "--out", first)
        control = mark_pair(*read_pair(first), FIRST, "two-return control")
        receipt = dict(schema="p104-complex-construction-replay/1", base=base, control=control,
                       final=control, stages=stages)
        (out / "CONSTRUCTION-REPLAY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print("PASS_P104_COMPLEX_CONSTRUCTION_CONTROL", *FIRST, flush=True)
        return
    run(HERE / "portable_chain.py", "--supplier", cache / "source/research/p104-dual-supplier-lift",
        "--word", projected / "WORD.json.gz", "--layout", projected / "LAYOUT.json.gz",
        "--journal", journal["THREE-BIRTHS.json"], "--faults", "--checkpoint", first, "--out", births)
    control = mark_pair(*read_pair(first), FIRST, "two-return control")
    mark_pair(*read_pair(births), THREE, "three-return word")
    stages["births"] = projection.load(births / "REPLAY.json")
    need(len(stages["births"]["steps"]) == 3 and all(step["controls"] for step in stages["births"]["steps"]),
         "all three explicit birth omission controls")
    boundary = out / "boundary"
    stages["boundary_projection"] = project(cache, births / "WORD.json.gz", births / "LAYOUT.json.gz",
                                             THREE, BOUNDARY, journal["BOUNDARY-PROJECTION.json"], boundary)
    current, layout = read_pair(boundary)
    mark_pair(current, layout, (BOUNDARY, THREE[1]), "additional paid projection")
    plan = projection.load(HERE / "PAID-CHAINS.json")
    final, stages["paid_chains"] = chains(cache, current, layout, plan)
    final_mark = stages["paid_chains"]["stages"][-1]
    if addition := plan.get("continued_births"):
        chain = out / "chains"
        write_pair(chain, final, layout)
        addition_journal = pin(addition["journal"], addition["journal_sha256"])
        continued = out / "continued"
        run(HERE / "portable_chain.py", "--supplier", cache / "source/research/p104-dual-supplier-lift",
            "--word", chain / "WORD.json.gz", "--layout", chain / "LAYOUT.json.gz", "--journal", addition_journal,
            "--faults", "--out", continued)
        final, layout = read_pair(continued)
        final_mark = mark_pair(final, layout, (addition["word_sha256"], addition["layout_sha256"]), "continued birth")
        stages["continued_births"] = projection.load(continued / "REPLAY.json")
    if post_birth := plan.get("post_birth_chains"):
        need("continued_births" in stages, "post-birth paid changes require the continued productive word")
        final, stages["post_birth_chains"] = chains(cache, final, layout, post_birth)
        final_mark = stages["post_birth_chains"]["stages"][-1]
    claim = projection.load(HERE.parent / "CLAIM.json")
    rotation_path = HERE / "ROTATED-SPLITS.json"
    if rotation_path.exists() or "rotated_splits_sha256" in claim:
        need("post_birth_chains" in stages and "rotated_splits_sha256" in claim, "claimed post-birth rotated splits")
        rotations = projection.load(pin(rotation_path.name, claim["rotated_splits_sha256"]))
        final, layout, stages["rotated_splits"] = rotated_splits(cache, final, layout, rotations)
        final_mark = mark_pair(final, layout, (claim["complex_word"], claim["layout"]), "claimed rotated word")
        need((final, layout) == read_pair(HERE), "claimed rotated word and layout match packaged files")
    write_pair(out, final, layout)
    report = dict(schema="p104-complex-construction-replay/1", base=base, control=control,
                  final=final_mark, stages=stages)
    (out / "CONSTRUCTION-REPLAY.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("PASS_P104_COMPLEX_CONSTRUCTION", projection.digest(final), projection.digest(layout), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("cache", "word", "layout", "out"):
        parser.add_argument("--" + key, type=Path, required=True)
    parser.add_argument("--first-only", action="store_true", help="rebuild the two-return control and exit")
    args = parser.parse_args()
    construct(args.cache.resolve(), args.word.resolve(), args.layout.resolve(), args.out.resolve(), args.first_only)
