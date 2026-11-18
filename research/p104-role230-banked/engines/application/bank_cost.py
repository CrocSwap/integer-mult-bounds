"""Paired full-field snapshot schedule and ordinary cost substitution."""

from collections import Counter
from fractions import Fraction

from caller16 import exact_div, require


def roots_for_fixture(word, unit):
    values = {
        role: (unit * ((19 * role + 7) % 91 - 45), unit * ((31 * role + 2) % 87 - 43))
        for role in range(word["public"])
    }
    out = dict(values)
    hosted = word["hosted"]
    ports = set(hosted["Dports"])
    for port, x in enumerate(word["live"]):
        y = x + 112
        a, b = values[x], values[y]
        if port in ports:
            out[y] = tuple(u + v for u, v in zip(a, b, strict=True))
        else:
            out[x] = tuple(u - v for u, v in zip(a, b, strict=True))
            out[y] = tuple(exact_div(u + v, 2) for u, v in zip(a, b, strict=True))
    for x, y in zip(hosted["X2"], hosted["Y2"], strict=True):
        out[x] = tuple(u - v for u, v in zip(values[x], values[y], strict=True))
    return values, out


def dispatch_fixture(word, graph, order, unit):
    """Replay the complete held-snapshot schedule in normalized coordinates.

    MOVE changes the named chart of a complete returned field. Its physical
    Gaussian maps are bound by the separate native catalogue receipt.
    """
    n = word["public"]
    k = len(graph.moves)
    entrance = {~r: r + 1 for r in range(n)}
    accum = {node: n + i + 1 for i, node in enumerate(sorted(graph.forms))}
    returned = {node: 2 * n + k + i + 1 for i, node in enumerate(sorted(graph.moves))}
    scratch = tuple(range(2 * n + 2 * k + 1, 2 * n + 2 * k + 5))
    slots = set(entrance.values()) | set(accum.values()) | set(returned.values()) | set(scratch)
    require(len(slots) == 2 * n + 2 * k + 4 and slots == set(range(1, len(slots) + 1)),
            "separate complete field homes")
    home_count = len(slots)
    guard_left, guard_right = ("borrowed external left guard",), ("borrowed external right guard",)
    alias = {0: ("unselected dummy bank",), home_count + 1: ("parked ancestor",)}
    occupied = {i: ("old dirty", -(i + 1), i + 1) for i in slots}
    head = 0
    visits = Counter()
    slot_total = 0

    def access(slot, operation, write=None):
        nonlocal head, slot_total
        require(head == 0 and 1 <= slot <= home_count, "selected complete-slot address")
        head = slot
        visits[operation] += 1
        slot_total += slot
        previous = occupied[slot]
        if write is not None:
            occupied[slot] = write
        head = 0
        return previous

    public, expected = roots_for_fixture(word, unit)
    original = dict(public)
    for slot in sorted(slots):
        access(slot, "full_init", (None, 0, 0))
    for role, value in public.items():
        access(entrance[~role], "entrance_snapshot_write", (graph.initial[role], *value))

    for node in order:
        paid = node in graph.moves
        a, b = graph.moves[node] if paid else (graph.final[node - graph.first_output], None)
        rx = ix = 0
        for donor, c in sorted(graph.forms[node].items()):
            slot = entrance[donor] if donor < 0 else returned[donor]
            chart, real, imag = access(slot, "intact_donor_read")
            require(chart == a, "held donor and accumulator in identical chart")
            rx += exact_div(c.numerator * real, c.denominator)
            ix += exact_div(c.numerator * imag, c.denominator)
        access(accum[node], "accumulator_write", (a, rx, ix))
        if paid:
            chart, x, y = access(accum[node], "paid_child_input_read")
            require(chart == a, "complete child input chart")
            access(returned[node], "completed_paid_snapshot_write", (b, x, y))
    require(public == original, "every external input retained until all terminal loads")
    for role in range(n):
        terminal = graph.first_output + role
        chart, real, imag = access(accum[terminal], "public_install_read")
        require(chart == graph.final[role], "public install chart")
        public[role] = (real, imag)
    require(public == expected, "complete signed normalized snapshot execution")
    for slot in sorted(slots):
        access(slot, "full_retire", ("raw blank",))
    require(all(payload == ("raw blank",) for payload in occupied.values()) and head == 0
            and alias == {0: ("unselected dummy bank",), home_count + 1: ("parked ancestor",)}
            and guard_left == ("borrowed external left guard",)
            and guard_right == ("borrowed external right guard",), "full-bank and guard restoration")
    return {"homes": home_count, "dummy_slots": 1, "logical_visits": dict(visits),
            "logical_selected_slot_distance_sum": slot_total,
            "signed_public_outputs_checked": len(public),
            "public_inputs_parked_until_install": True, "restored_head_and_kept_guards": True}


def ordinary_cost(word, graph, native, caller, compiler, published_budget, fixture):
    n, k, m = word["public"], len(graph.moves), native["terms"]
    calls = caller["calls"]
    k_homes = 2 * n + 2 * k + 4
    visits = fixture["logical_visits"]
    require((visits["full_init"], visits["full_retire"], visits["intact_donor_read"],
             visits["entrance_snapshot_write"], visits["accumulator_write"],
             visits["paid_child_input_read"], visits["completed_paid_snapshot_write"],
             visits["public_install_read"]) == (k_homes, k_homes, m, n, k+n, k, k, n),
            "literal ordinary snapshot/read/return/install counts")
    conversions = 2 * (caller["root_owners"] + calls * n)
    require(conversions == published_budget["odd_conversions"] == 55104,
            "literal caller/native scale and unscale counts")
    old_resets = calls * (2 * k_homes + 4 * (m + k + n))
    require(old_resets == published_budget["reset_services_upper"], "published reset allowance")
    resets = calls * (2 * k_homes + 8 * (m + k + n) + 4 * n)
    whole_copy_count = calls * (2 * m + 2 * (k + n) + 6 * k + 4 * n)
    require((resets + whole_copy_count) >= calls * sum(visits.values()),
            "complete visited-field and scratch allowance")
    # Charge the entire retained #7670 highest-slot reset service as an
    # upper bound on any addressed macro, including nonwriting selections.
    # Its source bound at ordinal 15,290 is 214069 L + 963637.
    require(k_homes == 15290, "fixed packed selector slot cap")
    selector_l = (resets + whole_copy_count) * 214069
    selector_const = (resets + whole_copy_count) * 963637
    require(len(caller["owners"]) == 3536, "fixed root ownership")
    maps = published_budget["monomial_slots_upper"] + caller["root_negative_corrections"]
    h = int(compiler["H"])
    c = published_budget["context_c"]
    k_star = 1920 * 153**1920 * (h + 1)**2
    require((c * k_star).bit_length() < h, "candidate-specific complete root guard")
    return {
        "raw_paid_nodes": k, "raw_terminal_nodes": n, "raw_form_terms": m,
        "homes_per_native": k_homes, "homes_plus_dummy_per_native": k_homes + 1,
        "raw_private_homes": calls * k_homes,
        "raw_private_homes_with_dummy": calls * (k_homes + 1),
        "logical_access_counts_per_native": visits,
        "all_field_boundary_conversions": conversions,
        "scales": {"caller": caller["odd_scale"], "native": native["odd"]},
        "scalar_services_upper": published_budget["scalar_services_upper"],
        "scalar_step_rate_per_padded_component_bit": published_budget["scalar_steps_per_bit_upper"],
        "full_copy_streams_charged_at_most": whole_copy_count,
        "stateful_reset_services_upper": resets,
        "published_reset_allowance_before_explicit_scratch": old_resets,
        "selector_charge": {"coefficient_of_L": selector_l, "constant": selector_const,
                            "meaning": "Use the full #7670 highest-slot reset rate for each addressed macro, including read-only selection and head return."},
        "reset_charge": {"coefficient_of_L": 2 * resets, "constant": 3 * resets},
        "copy_charge": {"coefficient_of_L": 128 * whole_copy_count, "constant": 320 * whole_copy_count},
        "layout": {"field_extent": "L=(2(W+26)+3)R 2^D",
                   "guide": "One immutable typed guide per equal packed view; charge whole-field production, alignment, return and retirement.",
                   "capacity_per_view": "(2n+2k+5)(L+2) + (L+2) for the guide, plus descriptors, public fields and other aux; reserve old backing and full parked ancestors.",
                   "view_wrappers": "Charge each public/child entrance and return, equal-view transfer and any shape change at the retained complete-view movement rate, with the full actual and historical extents."},
        "monomial_slots_with_root_q_corrections": maps,
        "elementary_records_upper_at_cap_153": maps * 4 * 154**2,
        "dyadic_height": published_budget["dyadic_height"],
        "context_mass_upper": published_budget["context_mass_upper"],
        "context_c": c, "H": h, "depth_guard_bits": (c * k_star).bit_length(),
        "compiled_stock": {"O": f"{k_homes + 1} J native homes including dummy, plus U caller tuples and all actual guide, historic, parked, compiler, adapter and BIT backing",
                           "G": "Sum the positive complete reads, copies, installs, restores, selectors, resets and guide layout costs, compiler wrappers and primitive movement; count actual complete shaped views.",
                           "substitution": "Z=Wp+O; E0=64(Z+N+P+G+1)^3; B0=P+E0; C0=32 N B0^2",
                           "cutoffs": "Recompute an eventual cutoff for each positive outer gap after finite constants and complete occurrence stock are fixed."},
    }
