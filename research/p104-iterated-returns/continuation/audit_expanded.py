#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Audit emitted 24-bit scalar plans against the literal native word and complete invoice."""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from math import gcd
from pathlib import Path
import sys


SOURCE_LOCK_SHA = "4fad450ab3a7e237784d2d4b173ca6b33501b1c7f25241765d5bc7a597966093"
SOURCE_LOADER_SHA = "c70c3be6e48717c6a9a561ef2294d23437a60d7dbcbbddc1305a6fc54001bb3d"
LITERAL_SHA = "0b428bc6fac4dc6ec014114bf4119782553fbb58d92b2a632b51629f4abe563b"
INTERVAL_SHA = "8dc2bc4c64cba3f83c664373984a075f1a14b4d53958084091345c8cab189dec"
SUPPLIER_GATE_SHA = "3796b2e5a27f3caa142d16364154788e60d0099f1e24a8dcd028e4fbd35a84ca"
ORIGINAL_APP_SHA = "2ec405d37c8af8e85824601b6b0bfe4317dd908f8bed1e5381f895f397167615"
REFERENCE_APP_SHA = "88486d49f2ba1fc0e6c9f4a7402c82e91c44026cf90cd1387d1e5c45cf5e88d3"
CALLER = "156fdf3a4a129b39225fd6ca51011de27974d7f104e8b04907c17ed5344bc858"
BINARY_WORD = "d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d"
BINARY_INDEPENDENT_SHA = "5865e19155488b80ccb1faa1ba74c2ffbc5ac22e8f22f10c5f4496ae49fc1229"
PREMISES = ["native_all_columns", "owned_erasure", "compiler", "precision_tape", "analytic_recovery"]
TARGET = "0.00387981257853"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def checked_bytes(path, pin):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == pin, f"pinned bytes at {path}")
    return raw


def load(name, path, pin):
    code = compile(checked_bytes(path, pin), str(path), "exec", dont_inherit=True)
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    exec(code, module.__dict__)
    return module


def width(q):
    return max(abs(q.numerator).bit_length(), q.denominator.bit_length())


def canonical(path, pin):
    raw = path.read_bytes()
    value = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
    digest = sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    need(digest == pin, f"exact canonical bytes at {path}")
    return value


def pinned_context(cache):
    parent = cache / "parent"
    checked_bytes(parent / "SOURCE-LOCK.json", SOURCE_LOCK_SHA)
    loader = load("bounded_review_lock", parent / "prepare_sources.py", SOURCE_LOADER_SHA)
    verified = loader.sources(cache)
    reader = load("bounded_review_literal", parent / "complex/independent.py", LITERAL_SHA)
    intervals = load("bounded_review_intervals", cache /
                     "source/research/paired-query-only-bit/independent/interval_gate.py", INTERVAL_SHA)
    return reader, intervals, verified


def audit_program(coefficient, instructions, result_stream):
    """Work symbolically on an arbitrary installed donor and count dirty replacements."""
    owner_values = {0: Fraction(1)}
    bound = max(Fraction(1), abs(coefficient))
    pre_clears = 0
    for op, out, source, arg in instructions:
        need(out in (0, 1, 2) and source in owner_values, "three initialized term streams only")
        if op == "ADD":
            need(out == source != arg and arg in owner_values, "ripple addition into resident partial stream")
            result = owner_values[source] + owner_values[arg]
        else:
            need(op in ("DIV", "MUL") and source != out and 0 < abs(arg) < 2**24,
                 "short scalar with disjoint input/output streams")
            if op == "DIV":
                need(arg > 0, "positive exact divisor")
            result = owner_values[source] / arg if op == "DIV" else owner_values[source] * arg
            if out in owner_values:
                del owner_values[out]
                pre_clears += 1
        # A reduced a/b maps an integer donor to an integer iff b divides it.
        # This checks every installed quotient for the entire set of such donors.
        need((result * coefficient.denominator).denominator == 1, "exact for all grid-legal donors")
        need(abs(result) <= bound, "intermediate installed value fits whenever both original endpoints fit")
        owner_values[out] = result
    need(owner_values.get(result_stream) == coefficient, "exact scalar on arbitrary signed donor")
    final_clears = len(owner_values)
    owner_values.clear()
    need(final_clears <= 3, "term retirement charged in the original native allowance")
    return pre_clears, final_clears


def short_scalar(op, value, constant, w):
    """Read the retained fixed-pass multiply/divide scans in W+26 bits."""
    magnitude = abs(value)
    padding = w + 26
    if op == "MUL":
        product = carry = 0
        for column in range(padding):
            carry += abs(constant)*((magnitude >> column) & 1)
            need(carry < 2**25, "short numerator carry fits in 25 bits")
            product |= (carry & 1) << column
            carry >>= 1
        need(carry == 0, "fixed multiply loop retires every carried bit")
        return -product if (value < 0) != (constant < 0) else product
    quotient = remainder = 0
    for column in range(padding - 1, -1, -1):
        trial = 2*remainder + ((magnitude >> column) & 1)
        need(trial < 2**25, "short denominator compare fits in 25 bits")
        bit = int(trial >= constant)
        remainder = trial - constant*bit
        quotient = 2*quotient + bit
    need(remainder == 0, "inexact short divisor rejected")
    return -quotient if value < 0 else quotient


def ripple_add(a, b, w):
    """One signed W-digit addition retaining only one carry bit."""
    product = carry = 0
    for column in range(w):
        carry += ((a >> column) & 1) + ((b >> column) & 1)
        product |= (carry & 1) << column
        carry >>= 1
    return product - (1 << w) if product >> (w - 1) else product


def execute_program(steps, result_stream, x, w, omit_clear_at=None):
    """Check concrete signed boundary fixtures with closed, disjoint dirty homes."""
    limit = 1 << (w - 1)
    need(-limit < x < limit, "fixture donor fits W signed bits")
    registers = [x, None, None]
    for clock, (op, out, source, arg) in enumerate(steps):
        src = registers[source]
        if op == "ADD":
            value = ripple_add(src, registers[arg], w)
            need(value == src + registers[arg], "signed ripple add has correct value with no overflow")
        else:
            if registers[out] is not None and clock != omit_clear_at:
                registers[out] = None
            need(registers[out] is None, "dirty scalar stream installation rejected")
            value = short_scalar(op, src, arg, w)
        need(-limit < value < limit, "installed width in signed fixture")
        registers[out] = value
    value = registers[result_stream]
    for address in range(len(registers)):
        registers[address] = None
    return value


def audit_plans(word, scalar):
    census = Counter(Fraction(q) for _, terms in word["forms"] for _, q in terms)
    required = Counter({q: n for q, n in census.items() if width(q) > 24})
    covered, primitives = Counter(), Counter()
    plans = {}
    pre_clears = final_clears = fixtures = 0
    clear_control = None
    for proof in scalar["local_plans"]:
        q = Fraction(proof["coefficient"])
        steps = proof["instructions"]
        result = proof["result_stream"]
        count = proof["occurrences"]
        need(q in required and q not in covered and count == required[q], "each emitted plan has all and only its actual incidences")
        covered[q] = count
        plans[q] = steps, result
        pre, post = audit_program(q, steps, result)
        pre_clears += count * pre
        final_clears += count * post
        primitives.update({op: n * count for op, n in Counter(step[0] for step in steps).items()})
        for w in (width(q) + 1, max(width(q) + 2, 96)):
            largest = ((1 << (w - 1)) - 1) // max(abs(q.numerator), q.denominator)
            for multiplier in (0, 1, -1, largest, -largest):
                x = multiplier * q.denominator
                need(execute_program(steps, result, x, w) == multiplier * q.numerator,
                     "independent signed boundary fixture")
                fixtures += 1
        if pre and clear_control is None:
            live = {0}
            for clock, (op, out, _, _) in enumerate(steps):
                if op != "ADD" and out in live:
                    try:
                        execute_program(steps, result, q.denominator, 96, omit_clear_at=clock)
                    except ValueError as failure:
                        need(str(failure) == "dirty scalar stream installation rejected", "omitted clear fails at the changed stream")
                    else:
                        raise ValueError("required temporary clear was not detected")
                    clear_control = {"coefficient": str(q), "instruction": clock, "stream": out, "rejected": True}
                    break
                live.add(out)
    need(required == covered and sum(covered.values()) == scalar["expanded_terms"] and
         len(covered) == scalar["expanded_coefficient_count"], "complete normalized literal expansion census")
    need(dict(primitives) == scalar["expanded_primitive_histogram"], "exact primitive occurrences")
    charged = scalar["extra_component_pass_allowance_per_native"]
    need(charged >= sum(primitives.values()) + pre_clears and scalar["extra_scratch_streams"] == 0,
         "ordinary bill covers every expanded primitive and overwrite")
    report = {"literal_terms": sum(census.values()), "max_literal_bits": max(map(width, census)),
              "expanded_terms": sum(covered.values()), "expanded_coefficients": len(covered),
              "lowered_primitives_per_native": dict(primitives), "extra_clean_replacements_per_native": pre_clears,
              "retirement_of_wide_term_streams_in_existing_allowance": final_clears,
              "charged_extra_services_per_native": charged, "concrete_signed_inputs_tested": fixtures,
              "omitted_extra_clear_control": clear_control}
    return report, plans


def basis_grid(graph, expected, native, conversion):
    """Independently establish every exact product division for arbitrary basis inputs."""
    grid = native["minimum_product_grid"]
    height = (grid & -grid).bit_length() - 1
    odd = grid >> height
    factored = 1
    for factor in conversion["odd_factors"]:
        need(type(factor) is int and 1 < factor < 2**24, "short odd conversion primitive")
        factored *= factor
    need(grid > 0 and factored == odd and (grid, odd, height) ==
         (native["path_grid"], native["path_grid_odd"], native["path_grid_height"]), "complete entrance grid")
    stocks = {~i: {i: grid} for i in range(graph.size)}
    masses = {k: Fraction(1) for k in stocks}
    peak_mass = Fraction(1)
    all_products, nontrivial, common_divisor = 0, 0, grid
    for k in graph.order:
        row = {}
        mass = Fraction(0)
        for donor, q in graph.forms[k]:
            a, b = q.numerator, q.denominator
            stock = stocks[donor]
            all_products += len(stock)
            nontrivial += len(stock) if b != 1 else 0
            mass += abs(q)*masses[donor]
            for j, value in stock.items():
                quotient, remainder = divmod(value, b)
                need(remainder == 0, f"uncovered exact division at literal {k}:{donor} on basis {j}")
                product = a*quotient
                if common_divisor != 1:
                    common_divisor = gcd(common_divisor, product)
                row[j] = row.get(j, 0) + product
        peak_mass = max(peak_mass, mass)
        if k in graph.moves:
            stocks[k] = {j: entry for j, entry in row.items() if entry}
            masses[k] = mass
        else:
            wanted = {j: grid*q for j, q in expected[k-graph.first].items()}
            need({j: entry for j, entry in row.items() if entry} == wanted,
                 "complete arbitrary exact terminal operator on the claimed grid")
    need(common_divisor == 1 and peak_mass == Fraction(native["positive_path_mass_bound_unscaled"]),
         "minimal common product grid and positive no-cancellation path mass")
    need((all_products, nontrivial) == (native["coefficient_products"], native["checked_nontrivial_divisions"]),
         "regenerated full per-basis product and nontrivial division census")
    return {"product_grid": grid, "dyadic_height": height, "odd_factors": conversion["odd_factors"],
            "all_basis_products": all_products, "nontrivial_basis_divisions": nontrivial,
            "minimal_grid": True, "positive_path_mass": str(peak_mass), "exact_basis_owners": graph.size}


def replay_grid(graph, expected, native, plans):
    """Run each expanded incidence with real cut values on the audited grid."""
    grid = native["minimum_product_grid"]
    sample = {i: tuple(grid * ((i*(37+6*j) + 15+3*j) % 127 - 63) for j in range(4)) for i in range(graph.size)}
    stocks = {~i: values for i, values in sample.items()}
    height = (63*grid*Fraction(native["positive_path_mass_bound_unscaled"])).__ceil__().bit_length() + 1
    peak, executed = 0, 0
    for k in graph.order:
        accumulator = [0]*4
        for donor, q in graph.forms[k]:
            for axis, x in enumerate(stocks[donor]):
                if q in plans:
                    contribution = execute_program(*plans[q], x, height)
                    executed += 1
                else:
                    contribution, residue = divmod(q.numerator*x, q.denominator)
                    need(residue == 0, "exact original coefficient on real fixture")
                accumulator[axis] += contribution
                bits = abs(accumulator[axis]).bit_length()
                need(bits < height, "actual row prefix under complete positive path bound")
                peak = max(peak, bits)
        if k in graph.moves:
            stocks[k] = tuple(accumulator)
        else:
            row = expected[k-graph.first]
            want = [sum(q * sample[j][axis] for j, q in row.items()) for axis in range(4)]
            need(accumulator == want, "same-owner output under the actual expanded fixture tape")
    return {"native_independent_wide_incidences_executed": executed,
            "native_signed_components": 4, "minimum_product_grid": grid,
            "whole_prefix_width_bits": peak, "fixture_signed_width": height, "exact_outputs_each": graph.size}


def audit_ordinary(word, physical, counts, direct_price):
    native, application = physical["native"], physical["application"]
    ordinary, caller = application["ordinary"], physical["caller_census"]
    stages, roots = caller["calls"], caller["root_owners"]
    n, k, m = len(word["initial"]), len(word["moves"]), counts["literal_terms"]
    h = 2*n + k + 5
    need(stages == 48 and roots == 9840 and (n, k, m, h) ==
         tuple(native[key] for key in ("public", "slots", "terms", "numerical_homes")), "literal calls, homes, rows and forms")
    need(native["additional_independent_guarded_streams"] == 4, "four live scalar streams")
    uses = Counter(caller["uses"])
    gaussian = caller["gaussian_literal_uses"]
    base_scalar = (stages*(m + 4*(k+n) + 2*n + h + 2*k) + sum(uses.values()) +
                   2*(roots + stages*n) + 64*(gaussian+uses["LAMBDA"]))
    conversion = physical["conversion"]
    conversions = 2*(roots + stages*n)
    extra_grid = (len(conversion["odd_factors"]) - 1) * conversions
    extras = stages * counts["charged_extra_services_per_native"]
    need(32*(base_scalar + extra_grid + extras) == ordinary["scalar_services"],
         "complete independent ordinary scalar recount including every lowered incidence")
    need(ordinary["scalar_step_rate"] == 2**32, "24-bit primitive scalar service rate")
    need((application["invoice"]["paid"], application["invoice"]["targets"]) ==
         (direct_price["paid"], direct_price["productive"]), "ordinary and independently regenerated signed histograms")
    resets = 2*h + 8*(m+k+n) + 4*n + 2*k
    transfers = 2*m + 2*(k+n) + 6*k + 4*n
    constant_select = 63*h - 7*h.bit_count() + 27*h.bit_length() + 59
    selected_steps = [stages*(resets*(14*h+11) + transfers*(14*h+137)),
                      stages*(resets*(constant_select+3) + transfers*(constant_select+320))]
    need(stages*resets == ordinary["reset_services_all_native_stages"] and
         stages*transfers == ordinary["typed_selected_transfer_legs_all_native_stages"] and
         selected_steps == ordinary["selected_total_steps_raw_L_and_constant"],
         "ordinary charged selected homes, resets, transfer loops and constants")
    map_slots = 2*(sum(direct_price["paid"].values()) + sum(direct_price["productive"].values()) + stages*400)
    map_slots += 2*(uses["IDLE_ONE"] + uses["IDLE_ODD"]) + 3*uses["QUERY"] + uses["LAMBDA"]
    map_slots += uses["IDLE_ODD"] + caller["root_negative_q"] + 2*gaussian + 4*400*stages
    need(map_slots == ordinary["ordinary_map_slots"] and map_slots*4*154**2 == ordinary["ordinary_elementary_record_upper"],
         "ordinary map and elementary record inventory")
    root = physical["common_root"]
    guards = physical["common_depth_guards"]
    for receipt in guards.values():
        compiler_h = int(receipt["compiler_H"])
        actual_length = (root["context_c"] * 1920 * 153**1920 * (compiler_h + 1)**2).bit_length()
        need(actual_length == receipt["argument_bit_length"] < compiler_h and receipt["strict_guard_passed"],
             "one depth envelope covers each recorded compiler H")
    return {"ordinary_scalar_services": ordinary["scalar_services"], "ordinary_scalar_step_rate": 2**32,
            "common_depth_guards": guards,
            "extra_allowance_all_48_native_calls": extras, "native_numeric_homes": h,
            "native_selected_resets": stages*resets, "native_selected_transfers": stages*transfers,
            "selected_steps_linear_and_constant": selected_steps, "ordinary_map_slots": map_slots,
            "ordinary_elementary_record_upper": map_slots*4*154**2}


def same_counter(hist, reference):
    return {int(k): v for k, v in hist.items()} == {int(k): v for k, v in reference.items()}


def wire_bounds(interval, pair, digits=26):
    scale = 10**digits
    rounded = (pair[0]*scale // interval.B, -(-pair[1]*scale // interval.B))
    rendered = []
    for number in rounded:
        whole, fractional = divmod(abs(number), scale)
        sign = '-' if number < 0 else ''
        rendered.append(f'{sign}{whole}.{fractional:0{digits}d}')
    return rendered


def signed_readback(reader, interval, supplier, graph, layout, mains, spans, physical):
    fixed_paid, fixed_productive, caller = reader.signed_caller(supplier, graph, layout)
    need(physical["caller"] == caller["readback"]["event_stream_sha256"] == CALLER and
         physical["caller_proof"]["readback"] == caller["readback"], "one identical literal 48-call caller")
    census = physical["caller_census"]
    need(census["finite_binding"] == caller["finite_binding"] and
         same_counter(census["fixed_caller_paid"], fixed_paid) and
         same_counter(census["fixed_root_targets"], fixed_productive), "all caller binds and fixed signed ranks")
    native = reader.ranks(graph, mains, spans)
    need(same_counter(physical["native"]["paid_native_ranks"], native[0]) and
         same_counter(physical["native"]["positive_helper_ranks"], native[1]), "all native paid and productive ranks")
    paid, productive = reader.invoice(native, (fixed_paid, fixed_productive))
    bracket = physical["application"]["bracket"]
    lower, upper = map(Fraction, bracket)
    need(upper - lower == Fraction(1, 10**14), "adjacent exact crossing ticks")

    def margin(point):
        return interval.sub(interval.moment(productive, point), interval.moment(paid, point))

    low, high = margin(lower), margin(upper)
    need(low[0] > 0 and high[1] < 0, "independently directed raw crossing")
    target = margin(Fraction(TARGET))
    a, b = map(Fraction, physical["target_signed_margin"])
    need(max(Fraction(target[0], interval.B), a) <= min(Fraction(target[1], interval.B), b),
         "actual signed price matches the compiler receipt")
    return {"candidate_raw_bracket": bracket, "signed_target_margin": wire_bounds(interval, target),
            "target": TARGET, "paid": {str(k): n for k, n in paid.items()},
            "productive": {str(k): n for k, n in productive.items()},
            "native_calls": 48, "caller_sha256": CALLER}


def audit_root(cache, supplier_path, word, layout, physical, reference_app):
    import supplier
    from closed_application import verify_caller

    need(Path(supplier.__file__).resolve() == (supplier_path / "complex/supplier.py").resolve(),
         "pinned physical adapter and exact caller routines")
    caller = supplier.read(supplier.SOURCE / "data/CALLER.json.gz")
    phase = supplier.read(supplier.SOURCE / "data/CALLER-PHASE-BASES.json")
    census, guard, proof, _ = verify_caller(caller, word, layout, phase)
    actual = json.loads(json.dumps(census))
    need(actual == physical["caller_census"] and proof["readback"]["event_stream_sha256"] == CALLER,
         "regenerated literal caller and ordinary scopes")
    original = json.loads(checked_bytes(cache / "parent/evidence/application.json", ORIGINAL_APP_SHA))
    native = {"tested": physical["native"], "original_7781": original["native"]}
    if reference_app:
        e40b = json.loads(checked_bytes(reference_app, REFERENCE_APP_SHA))
        native["current_7786"] = e40b["native"]
    required_root = supplier.physical.root_envelope(native, guard)
    actual_root = physical["common_root"]
    if reference_app:
        need(required_root == actual_root, "one recomputed exact-root envelope for both comparators and the candidate")
    else:
        need(required_root["context_c"] <= actual_root["context_c"], "candidate and #7781 covered by common root")
    need(actual_root["temporary_width"] == "W+26" and actual_root["signed_width"] == "W=p+h+2D+3",
         "retained root and component widths")
    return {"replayed_context_c": required_root["context_c"], "common_context_c": actual_root["context_c"],
            "W": required_root["signed_width"], "temporary_width": required_root["temporary_width"],
            "reference_words_in_recount": list(native)}


def audit_outer(interval, gate_path, binary_path, physical, price):
    binary = json.loads(checked_bytes(binary_path, BINARY_INDEPENDENT_SHA))
    need(binary["word_sha256"] == BINARY_WORD and binary["native_calls"] == 36, "independent checked 36-call binary cap")
    claim = physical["application"]["claim"]
    lower, upper = price["candidate_raw_bracket"]
    cap = Fraction(binary["ordinary_admitted"])
    tested = Fraction(claim) + Fraction(7, 10**14)
    need(tested < cap <= Fraction('0.0069'), "independent ordinary headroom")

    # L(0)=0. The positive terms contribute nonnegative curvature for
    # kappa≥0. The negative log-square terms bound all negative curvature.
    positive, negative = {7: 1, 3: 1, 5: 1}, {9: 1, 4: 1, 1: 2}
    d1_upper = sum(Fraction(interval.log(r)[1], interval.B)*r*n for r, n in positive.items())
    d1_upper -= sum(Fraction(interval.log(r)[0], interval.B)*r*n for r, n in negative.items())
    curvature = sum(Fraction(interval.log(r)[1], interval.B)**2*r*n for r, n in negative.items())
    derivative_upper = d1_upper + cap*curvature
    need(derivative_upper < 0, "independent signed curvature certifies input lift over entire interval")

    supplier_gate = load("bounded_review_gate", gate_path, SUPPLIER_GATE_SHA)
    supplier_gate.BIT_PIN = binary["ordinary_admitted"]
    gate = supplier_gate.gate({"T": price["productive"], "P": price["paid"]}, claim, tested, lower, upper, cap)
    producer_gate = physical["application"]["compiler"]
    exact_fields = ("H", "minimum_log_power", "written_log_power", "compiler_gap", "moment_margins")
    need(all(gate[key] == producer_gate[key] for key in exact_fields), "finite compiler and recurrence replay agreement")
    return {"claim": claim, "pinned_binary_cap": binary["ordinary_admitted"],
            "outer_checks": gate["outer"], "input_lift": gate["input_lift"], "signed_curvature_bound": str(derivative_upper),
            "finite_compiler": gate}


def main(args):
    need(__debug__, "proof routines require assertions")
    word_pin, layout_pin = args.word_sha, args.layout_sha
    word = canonical(args.word, word_pin)
    layout = canonical(args.layout, layout_pin)
    physical = json.loads(args.receipt.read_bytes())
    need((physical["word_sha256"], physical["layout_sha256"]) == (word_pin, layout_pin),
         "scalar plans and ordinary receipt refer to the exact nominated word")
    need(physical["premises"] == PREMISES and physical["target"] == TARGET and physical["binary_word"] == BINARY_WORD,
         "exact five premises, unchanged target and binary supplier")
    cache = args.cache.resolve()
    supplier = cache / "source/research/p104-dual-supplier-lift"
    reader, interval, verified = pinned_context(cache)
    graph = reader.Graph.parse(word)
    spans = list(map(reader.span, graph.frames))
    expected, mains = reader.public_operator(graph, layout, spans)
    grid = basis_grid(graph, expected, physical["native"], physical["conversion"])
    counts, plans = audit_plans(word, physical["conversion"]["scalar_cases"])
    fixture = replay_grid(graph, expected, physical["native"], plans)
    need(fixture["native_independent_wide_incidences_executed"] == 4*counts["expanded_terms"],
         "all wide literal instructions ran on the actual four-component fixture")
    print("PASS exact basis products, short scalar programs, dirty overwrite and fixture tape", flush=True)
    signed = signed_readback(reader, interval, supplier, graph, layout, mains, spans, physical)
    ordinary = audit_ordinary(word, physical, counts, signed)
    root = audit_root(cache, supplier, word, layout, physical, args.reference_application)
    outer = audit_outer(interval, supplier / "complex/supplier_gate.py", args.binary_receipt, physical, signed)
    report = {"schema": "p104-24-bit-expanded-independent-recount/v1", "word": word_pin, "layout": layout_pin,
              "compiler_report_sha256": sha256(args.receipt.read_bytes()).hexdigest(), "locked_inputs_verified": verified,
              "audit_program_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "premises": PREMISES, "scalar_plans": counts, "basis_grid": grid,
              "actual_grid_fixture": fixture, "ordinary": ordinary, "signed": signed, "common_root": root,
              "outer": outer}
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("PASS exact lowered stream plans, full ordinary recount and fixed-grid finite outer", outer["claim"], flush=True)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ("cache", "word", "layout", "receipt", "binary-receipt", "out"):
        cli.add_argument("--" + name, required=True, type=Path)
    cli.add_argument("--reference-application", type=Path, help="pinned #7786 e40b comparator application for the common envelope")
    cli.add_argument("--word-sha", required=True)
    cli.add_argument("--layout-sha", required=True)
    main(cli.parse_args())
