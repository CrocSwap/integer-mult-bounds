"""Integer-lattice crosscheck; no rational envelope engine. Apache-2.0.

Integer arithmetic primitives are retained from commdata2338/PR3226.
This separate dispatcher checks every carried cut and native-interior digest.
"""

import hashlib
import json
from collections import Counter

import sources

sources.authenticate()
from vendor.pr3226 import independent as alt  # noqa: E402

require = sources.require


def price(packet, ledger):
    cost = Counter()
    for name in ("F_0", "B_1_2"):
        for event in sources.expand(packet, name):
            if event[0] == "scalar":
                gate = event[1]
                if gate[0] == "clear":
                    cost["clear_component_writes"] += 1024
                    continue
                n0, d0 = gate[-2:]
                n, d = alt.normalize_coefficient(n0, d0)
                cost["constant_product_calls"] += 1024
                cost["constant_product_component_copies"] += 1024 * n.bit_count()
                cost["constant_product_additions"] += 1024 * (n.bit_count() - 1)
                cost["constant_product_left_shifts"] += 1024 * (n.bit_count() - (n & 1))
                cost["constant_product_negations"] += 1024 * ((n0 < 0) != (d0 < 0))
                cost["constant_product_right_shifts"] += 1024 * (d > 1)
                cost["scalar_real_additions"] += 1024 * (gate[0] == "add")
            elif event[0] == "adapter":
                d = event[2]
                live = (event[1] == "old_to_new" and d < 112) or (
                    event[1] == "new_to_old" and 112 <= d < 224
                )
                cost["adapter_identity_labels"] += int(not live)
            elif event[0] == "phase":
                cost["phase_labels"] += 1
            elif event[0] == "cover_map":
                cost["full_cover_maps"] += 1
                cost["cover_component_transfers"] += 2048
    cost.update(
        {
            "native_gaussian_lines": ledger.lines,
            "native_real_additions": 2048 * ledger.lines,
            "native_exact_halvings": 1024 * ledger.lines,
            "native_pair_component_copies": 2048 * ledger.lines,
            "native_recipe_calls": ledger.recipes,
            "monomial_calls": ledger.monomials,
            "monomial_component_copies": 2048 * ledger.monomials,
            "monomial_component_negations_upper_bound": 1024 * ledger.monomials,
            "final_owned_scratch_clear_writes": 1036,
        }
    )
    return dict(cost)


def apply(event, fields, ledger, packet, children):
    kind = event[0]
    if kind == "scalar":
        gate = event[1]
        dest = alt.register(gate[1])
        if gate[0] == "clear":
            fields[dest] = (0, 0)
        elif gate[0] == "scale":
            fields[dest] = ledger.coefficient(fields[dest], *gate[-2:])
        else:
            term = ledger.coefficient(fields[alt.register(gate[2])], *gate[-2:])
            fields[dest] = ledger.mark(alt.add(fields[dest], term), "scalar-add")
    elif kind == "climb":
        dest = event[2]
        fields[dest] = ledger.recipe(fields[dest], children[event[3], event[4]])
    elif kind == "native_line":
        dest = alt.register(event[1])
        fields[dest] = ledger.recipe(
            fields[dest], packet["native_line_recipes"][event[2]]["recipe"]
        )
    elif kind == "cover_map":
        dest = alt.register(event[1])
        ledger.mark(fields[dest], "cover-uniform-bound")
    else:
        require(kind in ("adapter", "residual_adapter"), "integer event kind")
        dest = event[2]
        if (
            kind == "residual_adapter"
            or (event[1] == "old_to_new" and dest < 112)
            or (event[1] == "new_to_old" and 112 <= dest < 224)
        ):
            fields[dest] = ledger.monomial(fields[dest])
    return dest


def stage(packet, name, fields, ledger, children, offset):
    events = []
    for wrapper in packet["programs"][name]:
        if wrapper[0] == "retained_core":
            events += packet["core_words"][wrapper[1]]
        elif wrapper[0] in ("private_sweep", "cover_sweep"):
            events += wrapper[2]
        else:
            events.append(wrapper)
    completed = hashlib.sha256()
    for index, event in enumerate(events):
        ledger.event = offset + index
        if event[0] == "phase":
            continue
        dest = apply(event, fields, ledger, packet, children)
        ledger.mark(fields[dest], "completed-event")
        completed.update(
            alt.encode(
                [offset + index, dest, [alt.text_pair(fields[dest]), fields[dest][1]]]
            )
            + b"\n"
        )
    return {
        "events": len(events),
        "event_sha256": alt.sha(events),
        "completed_bound_sha256": completed.hexdigest(),
        "final_bounds_sha256": alt.sha([[alt.text_pair(x), x[1]] for x in fields]),
        "max_grid_so_far": ledger.max_grid,
        "max_range_so_far": alt.text_pair(ledger.max_range),
    }


def audit():
    packet, recipes, _ = sources.load()
    children = {(r["old"], r["new"]): r for r in recipes["children"]}
    fields = [(1, 0)] * 704 + [(0, 0)] * 8
    ledger = alt.IntegerLedger()
    stages, offset = {}, 0
    for name in ("F_0", "B_1_2"):
        stages[name] = stage(packet, name, fields, ledger, children, offset)
        offset += stages[name]["events"]
    n, grid = ledger.max_range
    range_bits = n.bit_length() - (n & (n - 1) == 0) - grid
    result = json.loads((sources.HERE / "RESULT.json").read_text())
    expected = {
        "stages": stages,
        "events": offset,
        "grid_guard": ledger.max_grid,
        "grid_site": ledger.grid_site,
        "range_site": ledger.range_site,
        "max_range_exact": alt.text_pair(ledger.max_range),
        "range_power_of_two": range_bits,
        "signed_width_P_plus": range_bits + ledger.max_grid + 1,
        "primitive_bound_observations": ledger.count,
        "primitive_bound_sha256": ledger.trace.hexdigest(),
        "direct_cost": price(packet, ledger),
    }
    for key, value in expected.items():
        require(result[key] == value, "integer disagreement: " + key)
    print("PASS_QQ16_F0_B1_INTEGER_CROSSCHECK", "observations=" + str(ledger.count))
    return expected


if __name__ == "__main__":
    audit()
