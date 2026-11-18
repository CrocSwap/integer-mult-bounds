#!/usr/bin/env python3
"""Materialize the chart-595 split from the pinned #7682 folded word."""

import argparse
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARENT = "1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150"
PARENT_GZIP = "8e28c1d403145ca5d72521f4acd7e068603598334c87f18f2fefb738844a1970"
EDIT = "c8a914049eb36f5f307dfabef080169bbee06c024eab77b75249566028ca3fcf"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(raw):
    return sha256(raw).hexdigest()


def load_inputs(parent, edit):
    packed_parent = parent.read_bytes()
    need(digest(packed_parent) == PARENT_GZIP, "exact transport bytes of #7682 graph")
    parent_raw = gzip.decompress(packed_parent)
    edit_raw = edit.read_bytes()
    need(digest(parent_raw) == PARENT and digest(edit_raw) == EDIT,
         "exact #7682 graph and nominated edit")
    source, change = json.loads(parent_raw), json.loads(edit_raw)
    need(canonical(source) == parent_raw and canonical(change) + b"\n" == edit_raw,
         "canonical source and edit representations")
    return source, change


def coefficients(entries):
    row = {key: Fraction(value) for key, value in entries}
    need(len(row) == len(entries) and all(row.values()), "exact nonzero coefficient list")
    return row


def accumulate(row, source, factor):
    for name, value in source.items():
        total = row.get(name, 0) + factor * value
        if total:
            row[name] = total
        else:
            row.pop(name, None)


def encode_row(row, substitutions):
    result = {}
    for name, value in row.items():
        source = substitutions.get(name)
        if source is None:
            accumulate(result, {name: Fraction(1)}, value)
        else:
            accumulate(result, source, value)
    return result


def span(frame):
    result = {0}
    for axis in frame:
        need(0 < axis < 512 and axis not in result, "independent chart axes")
        result |= {axis ^ value for value in result}
    return result


def verify_schedule(schedule, forms, moves, initial, final, first):
    expected = moves.keys() | set(range(first, first + len(final)))
    need(len(schedule) == len(forms) == len(expected) and set(schedule) == forms.keys() == expected,
         "complete one-to-one schedule")
    available = {~r: frame for r, frame in enumerate(initial)}
    for node in schedule:
        a, b = moves[node] if node in moves else (final[node - first], None)
        for donor in forms[node]:
            need(available.get(donor) == a, f"earlier cocharted donor {donor} in row {node}")
        if b is not None:
            available[node] = b


def construct(parent, edit):
    frames, first = parent["frames"], parent["first_output"]
    initial, final = parent["initial"][:], parent["final"][:]
    old_schedule = parent["schedule"]
    moves = {key: (a, b) for key, a, b in parent["moves"]}
    old_forms = {key: coefficients(row) for key, row in parent["forms"]}
    n, r, fresh = edit["old_public_roles"], edit["retired_role"], edit["fresh_role"]
    a, c, b = edit["charts"]
    need(n == fresh == len(initial) == len(final) == 1501 and r == 281 and first == 150522
         and len(moves) == 6142 and len(parent["moves"]) == len(moves), "fixed source role and paid inventory")
    need(span(frames[a]) < span(frames[c]) < span(frames[b])
         and [len(frames[c]) - len(frames[a]), len(frames[b]) - len(frames[c])] == edit["ranks"],
         "strict nested ordered productive boundary")
    need(parent["metadata"]["role230_direct_word_sha256"] == edit["source_word_sha256"]
         and parent["metadata"]["caller_sha256"] == edit["caller_sha256"], "exact source lineage")
    group = set(edit["group_roles"])
    need(len(group) == 615 and r in group and not group.intersection(edit["fixed_special_helpers"])
         and all((initial[j], final[j]) == (a, b) for j in group), "shared ordered helper endpoints")
    ell = coefficients(edit["functional"])
    v = coefficients(edit["return_direction"])
    need(r in ell and ell.keys() <= group and v.keys() <= group
         and sum(value * v.get(j, 0) for j, value in ell.items()) == 1, "normalized nominated group basis")

    # X = Ku + v u_r, where K's column j is e_j - (ell_j/ell_r)e_r.
    substitutions = {~j: {~j: Fraction(1), ~r: value} for j, value in v.items() if j != r}
    substitutions[~r] = {~j: -value / ell[r] for j, value in ell.items() if j != r}
    if r in v:
        substitutions[~r][~r] = v[r]
    forms = {key: encode_row(row, substitutions) for key, row in old_forms.items()}
    encoder_changed = [key for key in sorted(moves) if forms[key] != old_forms[key]]

    prefix = coefficients(edit["prefix"])
    injections = coefficients(edit["injection"])
    positions = {key: i for i, key in enumerate(old_schedule)}
    last_prefix = max(prefix, key=positions.__getitem__)
    need(len(prefix) == 8 and all(moves[key][1] == c for key in prefix)
         and len(injections) == 10 and all(moves[key][0] == c for key in injections),
         "exact nominated chart-local arrivals and departures")
    need([positions[last_prefix], min(positions[key] for key in injections)] == edit["reference_cut"]
         and positions[last_prefix] < min(positions[key] for key in injections), "causal cut in fixed paid order")
    protected = set(edit["protected_slots"])
    downstream = set()
    for key in old_schedule:
        if key in injections or not downstream.isdisjoint(old_forms[key]):
            downstream.add(key)
    need(downstream.isdisjoint(protected), "suffix injection cannot alter a protected predecessor direction")
    delta = {~fresh: Fraction(1)}
    accumulate(delta, prefix, Fraction(-1))
    for key, beta in injections.items():
        accumulate(forms[key], delta, beta)

    # Inline the B recovery in the final forms. Every terminal still reads
    # only its own chart's original entrance banks and paid return banks.
    terminal = {}
    for j, coefficient in ell.items():
        accumulate(terminal, forms[first + j], coefficient)
    decoded = {}
    for j, value in v.items():
        if j != r:
            updated = forms[first + j].copy()
            accumulate(updated, terminal, -value)
            decoded[first + j] = updated
    forms.update(decoded)
    forms[first + r] = prefix
    forms[first + fresh] = terminal
    initial.append(c)
    final[r] = c
    final.append(b)

    # Preserve the relative order of all paid operations. The chart-C
    # terminal is ready at the cut, and the B outputs can wait for every donor.
    old_retired = first + r
    schedule = []
    for key in old_schedule:
        if key != old_retired and key not in decoded:
            schedule.append(key)
        if key == last_prefix:
            schedule.append(old_retired)
    schedule.extend(sorted(decoded))
    schedule.append(first + fresh)
    verify_schedule(schedule, forms, moves, initial, final, first)
    need([key for key in schedule if key in moves] == [key for key in old_schedule if key in moves],
         "unchanged paid order")
    for j in edit["fixed_special_helpers"]:
        need(initial[j] == parent["initial"][j] and final[j] == parent["final"][j], "fixed specific helper boundary")
    return {
        "metadata": {**parent["metadata"], "source_bank_graph_sha256": PARENT,
                     "source_pr_head": edit["source_head"], "edit_sha256": EDIT,
                     "boundary_codec_sender_rows": encoder_changed,
                     "protected_sender_rows_with_inlined_boundary_codec": sorted(set(encoder_changed) & protected),
                     "chart595_prefix_row": old_retired, "suffix_injection_slots": sorted(injections)},
        "frames": frames, "first_output": first, "initial": initial, "final": final,
        "moves": parent["moves"], "schedule": schedule,
        "forms": [[key, [[donor, str(value)] for donor, value in sorted(row.items())]]
                  for key, row in sorted(forms.items())],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, default=HERE / "data/PARENT-GRAPH.json.gz")
    parser.add_argument("--edit", type=Path, default=HERE / "EDIT.json")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    args = parser.parse_args()
    parent, edit = load_inputs(args.parent, args.edit)
    result = canonical(construct(parent, edit))
    if args.check:
        need(gzip.decompress(args.check.read_bytes()) == result, "identical materialized candidate")
    else:
        with args.out.open("xb") as stream:
            stream.write(gzip.compress(result, mtime=0))
    print("PASS_P104_CHART595_CONSTRUCTION", digest(result), flush=True)


if __name__ == "__main__":
    main()
