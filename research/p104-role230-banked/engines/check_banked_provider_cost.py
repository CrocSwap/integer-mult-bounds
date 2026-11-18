#!/usr/bin/env python3
"""Check physical ownership, safe path grids and complete ordinary bank costs."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from math import lcm
from pathlib import Path
import argparse
import gzip
import json


HEAD = "28b2af322a1fab01b3734365988930920f9dda48"
GRAPH = {
    "peer": "d81ec9f47740852a4bf7bd83100feff5cb66b70e1973466e1609bbac8af75098",
    "candidate": "1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150",
}
PEER_RESULT = "00340c699fd7e2895d31a41d1eb60aebf91d7ba2c1c193dc002f69315298cd38"
PIVOTS = "fb22afc8aaf543e62709fa682f222577e6bdf4e1f1994d307784468314c3da85"
CALLER = "62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf"
CALLER_ODD = 2025
NATIVE_STAGES = 16
SELECTOR_TAPES = 7
STREAM_ROLES = ("running row accumulator", "staged read-only donor or field transfer",
                "full product and arithmetic work", "quotient and completed install payload")


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(raw):
    return sha256(raw).hexdigest()


def import_graph(path, metadata, side):
    packed = path.read_bytes()
    require(digest(packed) == metadata["gzip_sha256"], f"exact {side} gzip")
    raw = gzip.decompress(packed)
    require(digest(raw) == metadata["canonical_sha256"] == GRAPH[side], f"exact {side} graph")
    graph = json.loads(raw)
    stamp = graph["metadata"]
    require(encode(graph) == raw and stamp["schema"] == "p104-exact-banked-dag/v1"
            and stamp["kind"] == side and stamp["peer_head"] == HEAD
            and stamp["fixed_pivot_sha256"] == PIVOTS and stamp["published_result_sha256"] == PEER_RESULT
            and stamp["caller_sha256"] == CALLER, f"{side} immutable graph contract")
    return graph


def span(basis):
    values = {0}
    for item in basis:
        require(type(item) is int and 0 < item < 512 and item not in values, "independent chart rows")
        values.update({value ^ item for value in values})
    return values


def provider(graph):
    n = len(graph["initial"])
    require(n == len(graph["final"]) == 1501, "same public boundary")
    first = graph["first_output"]
    moves = {int(key): (source, target) for key, source, target in graph["moves"]}
    rows = {int(key): [(int(donor), Fraction(value)) for donor, value in data]
            for key, data in graph["forms"]}
    terminal_keys = set(range(first, first+n))
    order = graph["schedule"]
    k = len(moves)
    require(k == len(graph["moves"]) == 6142 and len(rows) == len(graph["forms"]) == n+k,
            "one record per paid or terminal row")
    require(set(moves).isdisjoint(terminal_keys) and set(rows) == set(moves) | terminal_keys
            and set(order) == set(rows) and len(order) == len(rows), "exact scheduled graph denominator")
    spaces = [span(v) for v in graph["frames"]]
    returns = {node: 2*n+k+1+j for j, node in enumerate(sorted(moves))}
    accum = {node: n+1+j for j, node in enumerate(sorted(rows))}
    tags = [r+1 for r in range(n)] + list(accum.values()) + list(returns.values())
    homes = 2*n+2*k+4
    tags += list(range(homes-3, homes+1))
    require(len(set(tags)) == len(tags) == homes and set(tags) == set(range(1, homes+1)),
            "separate data homes and four scratch slots, excluding charged dummy")

    # Only entrances and completed paid returns can be GET donors.
    available = {~r: (chart, r+1, 1, Fraction(1)) for r, chart in enumerate(graph["initial"])}
    live_terminal = set()
    p_ranks, directions = Counter(), Counter()
    denominator, largest_mass, peak = 1, Fraction(1), None
    terms = 0
    numeric_numerator_bits, numeric_denominator_bits = 0, 0
    schedule_hash = sha256()
    for key in order:
        source = moves[key][0] if key in moves else graph["final"][key-first]
        row_mass = Fraction()
        row_bound = 1
        seen = set()
        schedule_hash.update(encode(["ZERO_ACC", accum[key], source]))
        for donor, value in rows[key]:
            require(donor in available and donor not in seen and value, f"no early, duplicate or zero GET at {key}")
            chart, slot, donor_bound, donor_mass = available[donor]
            require(source == chart and slot != accum[key], f"coframe GET or alias failure at {key}")
            seen.add(donor)
            row_mass += abs(value)*donor_mass
            row_bound = lcm(row_bound, donor_bound*value.denominator)
            numeric_numerator_bits = max(numeric_numerator_bits, abs(value.numerator).bit_length())
            numeric_denominator_bits = max(numeric_denominator_bits, value.denominator.bit_length())
            schedule_hash.update(encode(["GET", slot, accum[key], chart, str(value)]))
            terms += 1
        if row_mass > largest_mass:
            largest_mass, peak = row_mass, key
        denominator = lcm(denominator, row_bound)
        if key in moves:
            dest = moves[key][1]
            require(spaces[source] < spaces[dest] or spaces[dest] < spaces[source],
                    "relative paid Gauss chart needs the retained nested normal form")
            rank = abs(len(graph["frames"][dest])-len(graph["frames"][source]))
            require(rank > 0, "nondegenerate declared paid child")
            p_ranks[rank] += 1
            directions["ascending" if spaces[source] < spaces[dest] else "descending"] += 1
            schedule_hash.update(encode(["MOVE_AND_SAVE", accum[key], returns[key], source, dest, rank]))
            available[key] = dest, returns[key], row_bound, row_mass
        else:
            live_terminal.add(key)
    require(live_terminal == terminal_keys and len(available) == n+k, "all deferred terminal/public installs")
    for role in range(n):
        schedule_hash.update(encode(["PUBLIC_INSTALL", accum[first+role], role, graph["final"][role]]))
    dyadic = (denominator & -denominator).bit_length()-1
    return {"entrance_snapshots": n, "paid_children_and_saved_returns": k, "terminal_installs": n,
            "actual_form_accumulators": n+k, "private_get_terms": terms, "private_homes": homes,
            "home_slots_with_dummy": homes+1, "scheduled_provider_digest": schedule_hash.hexdigest(),
            "paid_native_ranks": dict(p_ranks), "paid_native_directions": dict(directions),
            "path_grid": denominator, "path_grid_odd": denominator >> dyadic,
            "path_grid_height": dyadic, "positive_path_mass_bound_unscaled": str(largest_mass),
            "positive_path_mass_peak_node": peak,
            "literal_bits_num_den": [numeric_numerator_bits, numeric_denominator_bits]}


def raw_caller(caller_file):
    raw = gzip.decompress(caller_file.read_bytes())
    require(digest(raw) == CALLER, "exact 16-call caller decode")
    word = json.loads(raw)
    require(word["ambient_rank"] == 137 and word["stages"] == 16, "cookie-free complete caller geometry")
    require([event[1] for event in word["events"] if event[0] == "J"] == list(range(1,17)),
            "literal joint schedule")
    ports = {key: len(group["ports"]) for key, group in word["types"].items()}
    uses = Counter()
    max_literal_bits = 0
    for event in word["events"]:
        if event[0] != "J":
            uses[event[1]] += ports[event[0]]
            if event[1] in {"SCALE", "ADD"}:
                factor = Fraction(event[-1])
                max_literal_bits = max(max_literal_bits, abs(factor.numerator).bit_length(),
                                       factor.denominator.bit_length())
    roots = sum(ports[key]*group["roles"] for key, group in word["types"].items())
    negative = sum(ports[key] * sum(row[0] < 0 for row in group["diagonal"])
                   for key, group in word["types"].items())
    require((roots,negative,uses["IDLE_ODD"]) == (3536,3536,32),
            "actual root ordinary q translation and signed idle census")
    return roots, negative, uses, max_literal_bits


def addressed_budget(counts, uses, roots, negative, coefficient_bits):
    n,k,t,h = [counts[name] for name in ("entrance_snapshots", "paid_children_and_saved_returns",
                                        "private_get_terms", "private_homes")]
    conversions = 2*(roots+16*n)
    resets = 2*h+8*(t+k+n)+4*n
    transfers = 2*t+2*(k+n)+6*k+4*n
    selector_l = 14*h+9
    selector_const = 63*h-7*h.bit_count()+27*h.bit_length()+59
    stream_count = len(STREAM_ROLES)
    local_tracks = SELECTOR_TAPES+stream_count
    layout_guard_cells = 2*NATIVE_STAGES*local_tracks
    charged_pairs = 2*(101824+21152+16*400) + 2*(uses["IDLE_ONE"]+uses["IDLE_ODD"])
    charged_pairs += 3*uses["QUERY"]+uses["LAMBDA"]+uses["IDLE_ODD"]+negative
    require(charged_pairs == 280480, "all ordinary native/caller monomial slots")
    scalar_count = 32*(16*(t+4*(k+n)+2*n+h)+sum(uses.values())+conversions)
    return {
        "baseline_counting_units": "matched guarded finite exact implementation",
        "actual_data_homes_per_native": h, "addressed_slots_per_native": h+1,
        "actual_data_homes_raw": NATIVE_STAGES*h, "addressed_slots_raw": NATIVE_STAGES*(h+1),
        "separate_guarded_streams_per_native": stream_count,
        "separate_guarded_streams_raw": NATIVE_STAGES*stream_count,
        "added_separate_stream_cells_per_native": "4(L'+2)",
        "separate_stream_functions": STREAM_ROLES,
        "selector_and_stream_tracks_per_stage": local_tracks,
        "raw_stage_volume_M": "sum_stage[(h+6)(L'+2)+ell(N_c)+ell(W')+max(ell(N_c),ell(W'),ell(h))+max(N_c,h)+max(W',ell(h))+10]",
        "layout_shadow_cells_upper": f"M+{layout_guard_cells}",
        "raw_construction_complete_entry_exit_retirement_steps_upper": f"34*(256(M+{layout_guard_cells})+128) plus descriptor polynomial",
        "actual_odd_scale_and_unscale_conversions": conversions,
        "primitive_reset_services_upper_per_native": resets,
        "typed_selected_transfers_upper_per_native": transfers,
        "maximum_rebased_selector_instructions_L_and_constant": [selector_l,selector_const],
        "complete_wrapper_reset_copy_instructions_per_native_L_and_constant": [
            resets*selector_l+transfers*(selector_l+128),
            resets*selector_const+transfers*(selector_const+320)],
        "per_raw_scalar_services_upper": scalar_count,
        "maximum_literal_or_odd_scale_bits": coefficient_bits,
        "scalar_steps_per_padded_payload_cell_upper": 2**max(20, coefficient_bits+8),
        "ordinary_map_slots": charged_pairs,
        "ordinary_elementary_record_upper": charged_pairs*4*154**2,
        "view_extent": "L'=N_c(2(W+26)+3)",
        "booked_additional_ordinary_work": "guide production/retirement, disjoint staging backing, explicit 34 raw local layout scans, bounded descriptor polynomials, per-stage guard and history spans, all numerical adapters and child view returns",
        "positive_recursive_bank_get_copy_reset_charges": 0,
    }


def actual_application(path, counted):
    inputs = json.loads((path / "INPUTS.json").read_bytes())
    result = json.loads((path / "RESULT.json").read_bytes())
    caller = json.loads((path / "CALLER.json").read_bytes())["signed"]
    require(inputs["public_parent_head"] == HEAD and inputs["caller_sha256"] == CALLER
            and {name: record[0] for name, record in inputs["graph_pins"].items()} == GRAPH
            and result["status"] == "PASS_BANK24_ACTUAL16_APPLICATION_COMPONENT",
            "actual signed application pins")
    require(caller["odd_scale"] == CALLER_ODD and caller["dyadic_height"] == 9
            and Fraction(caller["peak_scaled_mass"]) == Fraction(495734175,2),
            "actual caller scale, dyadic height and measured pre-product envelope")
    prices = json.loads((path / "PRICE-OUTER.json").read_bytes())
    invoices = json.loads((path / "INVOICES.json").read_bytes())
    grids = json.loads((path / "GRAPH-GRID.json").read_bytes())
    records = {}
    for side in ("peer", "candidate"):
        scoped = prices[side]["compiler"]
        require(scoped["outer"]["strict_count"] == 54 and scoped["outer"]["functional_count"] == 4,
                "paired actual signed outer scope")
        grid, independent = grids[side], counted[side]
        require(independent["path_grid"] % int(grid["grid"]) == 0
                and grid["terms"] == independent["private_get_terms"]
                and grid["slots"] == independent["paid_children_and_saved_returns"], "signed actual grid receipt")
        require(Fraction(grid["peak_scaled_mass"])/grid["odd"]
                <= Fraction(independent["positive_path_mass_bound_unscaled"]), "validated exact mass bounded")
        bill = invoices[side]
        require(sum(bill["paid"].values()) == 101824 and sum(bill["targets"].values()) == 21152,
                "actual complete signed totals")
        records[side] = {"H": int(scoped["H"]), "native_odd": grid["odd"],
                         "native_height": grid["dyadic_height"], "scaled_mass": grid["peak_scaled_mass"]}
    a, b = [invoices[s]["paid"] for s in ("peer", "candidate")]
    delta = {int(k): b.get(k,0)-a.get(k,0) for k in a.keys() | b.keys() if a.get(k,0) != b.get(k,0)}
    require(delta == {2:16,3:-32,4:16}
            and invoices["peer"]["targets"] == invoices["candidate"]["targets"], "actual matched P/T")
    return records


def main(args):
    binder = json.loads(args.binding.read_bytes())
    require(binder["status"] == "FROZEN_BOTH_ORDERS_WITH_EXACT_STABLE_KEYS", "frozen graph custody")
    peer_raw = args.peer_result.read_bytes()
    require(digest(peer_raw) == PEER_RESULT, "actual submitted #7674 result")
    reported_peer = json.loads(peer_raw)
    graphs = {side: import_graph(args.binding.parent / binder["graphs"][side]["file"],
                                binder["graphs"][side], side) for side in ("peer", "candidate")}
    require(all(graphs["peer"][key] == graphs["candidate"][key]
                for key in ("frames","initial","final","first_output")), "matched actual boundary and atlas")
    a, b = [{key: (source, dest) for key, source, dest in graphs[side]["moves"]}
            for side in ("peer", "candidate")]
    require(a.keys() == b.keys() and {k for k in a if a[k] != b[k]} == {97471,102393},
            "exact fixed stable paid keys and only the two scoped charts")
    counted = {side: provider(graphs[side]) for side in graphs}
    old, new = counted["peer"], counted["candidate"]
    require(old["path_grid"] == int(reported_peer["native"]["grid"])
            and old["private_get_terms"] == reported_peer["native"]["terms"] == 169343
            and new["private_get_terms"] == 169349, "independent filed and transferred term/grid census")
    paid_change = {r: 16*(new["paid_native_ranks"].get(r,0)-old["paid_native_ranks"].get(r,0))
                   for r in old["paid_native_ranks"] | new["paid_native_ranks"]}
    require({r: v for r,v in paid_change.items() if v} == {2:16,3:-32,4:16}, "no extra paid rank position")
    roots, negative, uses, caller_bits = raw_caller(args.caller)
    odd = lcm(old["path_grid_odd"],new["path_grid_odd"])
    height = max(old["path_grid_height"],new["path_grid_height"])
    # Deliberately cancellation-free to cover all materialized partial sums.
    native_mass = odd*max(Fraction(entry["positive_path_mass_bound_unscaled"]) for entry in counted.values())
    context_mass = native_mass*Fraction(495734175,2)
    mass_bits = ((context_mass.numerator + context_mass.denominator - 1)//context_mass.denominator).bit_length()
    c = 2*max(height+9,mass_bits)
    coefficient_bits = max(odd.bit_length(), CALLER_ODD.bit_length(), caller_bits,
                           *old["literal_bits_num_den"], *new["literal_bits_num_den"])
    require(coefficient_bits <= 24, "matched W+26 checked exact scalar service")
    ordinary = {side: addressed_budget(counts, uses, roots, negative, coefficient_bits)
                for side, counts in counted.items()}
    peer_h = reported_peer["application"]["physical"]["H"]
    bound = actual_application(args.application_dir, counted) if args.application_dir else None
    thresholds = [int(peer_h)] if bound is None else [bound[side]["H"] for side in ("peer", "candidate")]
    require(thresholds[0] == int(peer_h), "actual peer threshold matches submitted object")
    K = 1920*153**1920*(max(thresholds)+1)**2
    require((c*K).bit_length() < min(thresholds), "retained rank threshold and common exact grid")
    output = {"status": "PASS_PAIRED_BANKED_PHYSICAL_COST_COMPONENT",
              "scope": "Explicit full held-field, addressed ordinary proof and independent safe context audit; no complete fixed tape or arbitrary-input operator replay",
              "graphs": GRAPH, "caller_decode": CALLER, "head": HEAD, "native": counted,
              "normalized_physical_bounds": ordinary, "same_signed_delta": {"paid": {2:16,3:-32,4:16}, "targets": {}},
              "common_exact_root": {"native_odd": odd, "native_height": height, "caller_odd": CALLER_ODD,
                                    "caller_height": 9, "safe_native_absolute_scaled_mass": str(native_mass),
                                    "safe_context_absolute_scaled_mass": str(context_mass), "context_mass_bits": mass_bits,
                                    "context_c": c,"compared_H_values": thresholds,
                                    "bounded_depth_guard_bits": (c*K).bit_length(),
                                    "actual_candidate_H_bound": bound is not None,
                                    "grid": "2^-(p+D)", "W": "p+h+2D+3", "temporary": "W+26"}}
    if bound is not None:
        output["actual_signed_grid_and_compiler"] = bound
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(output, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print(output["status"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("binding","peer-result","caller","out"):
        parser.add_argument("--"+name,type=Path,required=True)
    parser.add_argument("--application-dir",type=Path)
    main(parser.parse_args())
