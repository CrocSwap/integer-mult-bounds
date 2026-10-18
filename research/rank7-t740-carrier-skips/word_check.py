# SPDX-License-Identifier: Apache-2.0
"""Check the exact two-block action and unchanged allocation boundary."""

from collections import Counter
from fractions import Fraction


def need(condition, message):
    if not condition:
        raise ValueError(message)


def action(gates, registers):
    """Apply each gate to all basis columns, including arbitrary dirty state."""
    need(1 <= len(gates) <= 64 and 1 <= len(registers) <= 32, "edit size")
    rows = {r: {r: Fraction(1)} for r in registers}
    for gate in gates:
        if gate[0] == "scale":
            need(len(gate) == 5 and gate[1] in rows, "declared scale gate")
            _, target, numerator, denominator, _ = gate
            need(type(numerator) is int and type(denominator) is int and denominator != 0,
                 "rational scale coefficient")
            rows[target] = {r: Fraction(numerator, denominator) * x
                            for r, x in rows[target].items()}
            continue
        need(len(gate) == 6 and gate[0] == "add", "declared add gate")
        _, target, source, numerator, denominator, _ = gate
        need(target != source and target in rows and source in rows, "edit registers")
        need(type(numerator) is int and type(denominator) is int and denominator != 0,
             "rational edit coefficient")
        coefficient = Fraction(numerator, denominator)
        rows[target] = {r: rows[target].get(r, 0) + coefficient * rows[source].get(r, 0)
                        for r in registers}
    return {r: {c: x for c, x in row.items() if x} for r, row in rows.items()}


def check_word(old, new, edits, cleanup):
    need(set(old) == set(new), "word fields")
    need(type(edits) is list and len(edits) == 2, "two declared edit blocks")
    expected = [("R1_E42", 162, 188), ("R2_E7", 190, 203)]
    restored = old["restore"].copy()
    for edit, (name, start, stop) in zip(edits, expected, strict=True):
        need((edit["id"], edit["section"], edit["start"], edit["stop"]) ==
             (name, "restore", start, stop), "declared edit address")
        need(old["restore"][start:stop] == edit["old"], "literal edit preimage")
        registers = sorted({r for g in edit["old"] + edit["new"]
                            for r in (g[1:3] if g[0] == "add" else g[1:2])})
        need(action(edit["old"], registers) == action(edit["new"], registers),
             "exact dirty-input block action")
    for edit in reversed(edits):
        restored[edit["start"]:edit["stop"]] = edit["new"]
    need(new["restore"] == restored, "literal two-block composition")
    need({k for k in old if old[k] != new[k]} == {"restore", "report", "cleanup"},
         "unchanged source, frames, endpoints and wrapper boundary")
    before, after = old["report"], new["report"]
    need(before.keys() == after.keys(), "report keys")
    need(all(before[k] == after[k] for k in before if k != "local_profile"),
         "unchanged report boundary")
    delta = Counter({int(k): n for k, n in after["local_profile"].items()})
    delta.subtract({int(k): n for k, n in before["local_profile"].items()})
    need({r: n for r, n in delta.items() if n} == {1: -12, 2: 6}, "six-skip profile")
    need(len(old["helper_final"]) == len(new["helper_final"]) == 91, "91 private returns")
    need(cleanup(old) == old["cleanup"] and cleanup(new) == new["cleanup"],
         "exact inverse cleanup")
    return {"blocks": 2, "skips": 6, "private_buffers": 91,
            "scalar_action": "exact rational equality on every dirty basis column"}


def check_providers(before, after, declared):
    need(set(before) == set(after) == {"gauge44", "extra"}, "provider identities")
    for name in sorted(after):
        need(after[name]["widths"] == before[name]["widths"], "ordered helper widths")
        need(Counter(map(str, after[name]["widths"])) == Counter(declared["width_inventory"]),
             "helper width inventory")
        need(after[name]["actual_paid_profile"] == declared["local_profile"],
             "word and provider local profile")
