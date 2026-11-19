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
