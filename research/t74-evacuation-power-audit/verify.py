#!/usr/bin/env python3
"""Independent fixed-map audit. No predecessor code or floating point is used."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import json
from math import isqrt
from pathlib import Path
import sys

# Explicit local import path also works under Python -I, from any directory.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from allocation import audit_fill, bind_owners, bind_plan, canonical, inventory, schedule
from power import SCALE, hinge_certificate, need, power_interval


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def authenticate(root):
    index = read(root / "SOURCE-INDEX.json")
    names = [entry["file"] for entry in index]
    need(len(names) == len(set(names)), "source names")
    need(set(names) == {p.name for p in (root / "sources").iterdir()}, "source inventory")
    for entry in index:
        raw = (root / "sources" / entry["file"]).read_bytes()
        need(len(raw) == entry["bytes"], "source length: " + entry["file"])
        need(hashlib.sha256(raw).hexdigest() == entry["sha256"], "source SHA256: " + entry["file"])
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        need(hashlib.sha1(blob).hexdigest() == entry["git_blob"], "source Git blob: " + entry["file"])
    return {entry["file"]: entry["sha256"] for entry in index}


def reject(name, expected, action):
    try:
        action()
    except ValueError as error:
        need(str(error) == expected, "wrong rejection for " + name + ": " + str(error))
        return dict(name=name, rejected_by=expected)
    raise ValueError("accepted control: " + name)


def controls(context, widths, dispatch, fill, roles, delta):
    result = []
    def test_fill(name, expected, index, newrow):
        rows = list(fill["rows"])
        rows[index] = newrow
        result.append(reject(name, expected, lambda: audit_fill(context, widths, dispatch, dict(fill, rows=rows))))
    result.append(reject("missing role", "complete role count", lambda: audit_fill(context, widths, dispatch, dict(fill, rows=fill["rows"][:-1]))))
    row = list(fill["rows"][0]); row[0] = True
    test_fill("Boolean time", "integer role row", 0, row)
    row = list(fill["rows"][0]); row[-1] = -1
    test_fill("negative offset", "slice capacity", 0, row)
    index, owner = next((i, r) for i, row in enumerate(fill["rows"])
                        for r in range(74) if row[0] not in context["allowed"][r, row[3]])
    row = list(fill["rows"][index]); row[2] = owner
    test_fill("move past physical touch", "strict bridge-aware window", index, row)
    row = list(fill["rows"][1]); row[2:5] = fill["rows"][0][2:5]
    test_fill("alias physical family", "duplicate physical family", 1, row)
    per_bin = defaultdict(list)
    for i, row in enumerate(fill["rows"]):
        per_bin[tuple(row[2:5])].append(i)
    a, b = sorted(next(ids[:2] for ids in per_bin.values() if len(ids) >= 2))
    row = list(fill["rows"][b]); row[5] = fill["rows"][a][5]
    test_fill("overlap two time-separated slices", "slice overlap", b, row)
    for ids in per_bin.values():
        j = max(ids, key=lambda i: fill["rows"][i][5])
        row = list(fill["rows"][j])
        w = roles[row[0], row[1]][4]
        if row[5] + w < context["caps"][row[3]]:
            row[5] += 1
            test_fill("leave a pending prefix hole", "nonprefix occupancy", j, row)
            break
    else:
        raise ValueError("no prefix-hole fixture")
    result.append(reject("reverse price direction", "positive small-power limit", lambda: hinge_certificate({r: -n for r, n in delta.items()})))
    bad = dict(delta); bad[1] += 1
    result.append(reject("drop a rank unit", "equal rank mass", lambda: hinge_certificate(bad)))
    # Separate exact integer roots share neither logarithms nor Taylor recurrence.
    for rank in delta:
        root = isqrt(rank * SCALE * SCALE)
        lo, hi = power_interval(rank, Q(1, 2))
        need(lo <= root + 1 and root <= hi, "independent square-root enclosure")
        lo, hi = power_interval(rank, Q(1))
        need(lo <= rank * SCALE <= hi, "integer-power positive control")
    return result


def run(root=HERE):
    pins = authenticate(root)
    source = lambda name: read(root / "sources" / name)
    order = source("pr2530-order.json")
    need(order == source("pr2575-order.json"), "common order")
    dispatch = source("pr2575-dispatch.json")
    need(len(dispatch) == 666 and [x[:2] for x in dispatch] == order, "ordered dispatch")
    plan = source("pr2530-plan.json.gz")
    providers_old, providers_new = source("pr2530-providers.json"), source("pr2575-providers.json")
    widths, local, word_hashes = {}, {}, {}
    for tag, provider in [("base", "gauge44"), ("extra", "extra")]:
        before, after = source(f"pr2530-{tag}.json.gz"), source(f"pr2575-{tag}.json.gz")
        need(canonical(before) == canonical(after), "complete common word: " + provider)
        word_hashes[provider] = hashlib.sha256(canonical(before).encode()).hexdigest()
        widths[provider] = inventory(before)
        need(widths[provider] == providers_old[provider]["widths"] == providers_new[provider]["widths"], "source width registry")
        local[provider] = before["report"]["local_profile"]
        need(local[provider] == providers_old[provider]["actual_paid_profile"] == providers_new[provider]["actual_paid_profile"], "common local profile")
    context = schedule(source("pr2575-parent.json.gz"), order)
    bind_plan(context, plan, widths, dispatch)
    old_fill, new_fill = source("pr2530-fill.json.gz"), source("pr2575-fill.json.gz")
    old_roles, old_bins, old_idle = audit_fill(context, widths, dispatch, old_fill)
    new_roles, new_bins, new_idle = audit_fill(context, widths, dispatch, new_fill)
    bind_owners(context, new_roles, source("pr2575-owners.json.gz"))
    global_profiles = {}
    for name, idle in [("pr2530", old_idle), ("pr2575", new_idle)]:
        profile = Counter({r: n for r, n in idle.items() if r})
        for _, _, provider in dispatch:
            profile.update({int(r): n for r, n in local[provider].items()})
        need(profile == {int(r): n for r, n in source(name + "-profile.json").items()}, "global profile " + name)
        need(sum(r * n for r, n in profile.items()) == 73 * 66304 - 23680, "full rank mass")
        global_profiles[name] = dict(sorted(profile.items()))
    delta = {r: new_idle[r] - old_idle[r] for r in sorted(set(old_idle) | set(new_idle)) if r and new_idle[r] != old_idle[r]}
    proof = hinge_certificate(delta)
    changed = [key for key in old_roles if old_roles[key] != new_roles[key]]
    moved = [key for key in changed if old_roles[key][:3] != new_roles[key][:3]]
    bin_changes = Counter((old_bins[key], new_bins[key]) for key in old_bins if old_bins[key] != new_bins[key])
    checks = controls(context, widths, dispatch, new_fill, new_roles, delta)
    reordered = dict(new_fill, rows=list(reversed(new_fill["rows"])))
    roles2, bins2, idle2 = audit_fill(context, widths, dispatch, reordered)
    need(roles2 == new_roles and bins2 == new_bins and idle2 == new_idle, "row-order positive control")
    return dict(status="PASS_T74_EVACUATION_POWER_AUDIT", source_sha256=pins,
                common_word_semantic_sha256=word_hashes, calls=666, helpers_per_call=422,
                roles_per_map=len(new_roles), bins_per_map=len(new_bins),
                expanded_events=context["events"], bridges=context["bridges"],
                literal_windows=len(context["windows"]), dispatch=dict(Counter(x[2] for x in dispatch)),
                width_inventories={p: dict(sorted(Counter(ws).items())) for p, ws in widths.items()},
                idle_including_zero={"pr2530": dict(sorted(old_idle.items())), "pr2575": dict(sorted(new_idle.items()))},
                global_profiles_using_common_source_local_profiles=global_profiles,
                delta=delta, rank_mass_delta=sum(r * n for r, n in delta.items()),
                positive_children_delta=sum(delta.values()), changed_role_descriptors=len(changed),
                roles_moved_to_other_bins=len(moved), moved_widths=dict(sorted(Counter(old_roles[key][4] for key in moved).items())),
                changed_bin_residuals=sum(bin_changes.values()),
                residual_transition_counts=[[a, b, n] for (a, b), n in sorted(bin_changes.items())],
                proof_certificate=proof, controls=checks,
                positive_controls=["reversed fill row order", "independent integer square-root enclosures", "integer exponent one"],
                scope="Fixed source-bound allocation and recursive power-sum difference. No new supplier, endpoint, kappa, native phase, physical emitter, precision, or outer admission claim.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path, help="write a new receipt exclusively; default compares RESULT.json")
    parser.add_argument("--root", type=Path, default=HERE, help=argparse.SUPPRESS)
    args = parser.parse_args()
    receipt = run(args.root)
    if args.write_receipt:
        with args.write_receipt.open("x") as stream:
            stream.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        need(canonical(receipt) == canonical(read(args.root / "RESULT.json")), "committed receipt mismatch")
    print(receipt["status"], "roles_per_map=" + str(receipt["roles_per_map"]),
          "changed_bins=" + str(receipt["changed_bin_residuals"]),
          "crossover=(0.289994,0.289995)", "controls=" + str(len(receipt["controls"])))


if __name__ == "__main__":
    main()
