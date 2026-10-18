#!/usr/bin/env python3
"""Compile and independently check the target-frame round trips."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
NATIVE = REPO / "research/p104-native-channel"
SOURCES = {
    "compile.py": "9d2fc2d81962ddb0b4dd7d6482d9918a87a6b05759690317dea79939ca5656a3",
    "check_native.py": "e67b874a061a4a28007b9a0fabaf30c8db4a587b1e1c7dd9396c77ff1e3a9fe6",
    "vendor/clifford_exact.py": "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
    "vendor/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    "inputs/LOWRANK-RESULT.json": "7143ec7780f6f38a8c294df8009c3621936b281d05ae79946ce22f581b73d1b1",
}
SELECTED_RESULT_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
GRID = 10**30


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def log_bounds(x: Fraction) -> tuple[Fraction, Fraction]:
    """Rational enclosure for log(x), sufficient for x in [1, 9]."""
    def unit(y: Fraction) -> tuple[Fraction, Fraction]:
        z = (y - 1) / (y + 1)
        lower = 2 * sum((z ** (2 * j + 1) / (2 * j + 1)
                         for j in range(80)), Fraction())
        upper = lower + 2 * z**161 / (161 * (1 - z*z))
        return lower, upper

    k = 0
    while x > 2:
        x /= 2
        k += 1
    lo, hi = unit(x)
    lo2, hi2 = unit(Fraction(2))
    lo, hi = lo + k*lo2, hi + k*hi2
    return Fraction((lo*GRID).__floor__(), GRID), Fraction((hi*GRID).__ceil__(), GRID)


def exp_bounds(x: Fraction) -> tuple[Fraction, Fraction]:
    """Rational Taylor enclosure for exp(x), 0 <= x < 1."""
    need(0 <= x < 1, "exponential enclosure out of range")
    term = total = Fraction(1)
    for j in range(1, 13):
        term *= x / j
        total += term
    tail = term * x / 13 / (1 - x / 14)
    return total, total + tail


def outward_decimal(value: Fraction, *, upper: bool) -> str:
    scaled = value * GRID
    integer = (-((-scaled.numerator) // scaled.denominator)
               if upper else scaled.numerator // scaled.denominator)
    whole, fractional = divmod(integer, GRID)
    return f"{whole}.{fractional:030d}"


def moment_sum_bounds(m: int, profile: dict[int, int], saving: Fraction):
    """Enclose W times the normalized moment, so W > upper is sufficient."""
    lo = hi = Fraction()
    for rank, count in profile.items():
        llog, ulog = log_bounds(Fraction(m, rank))
        loexp, _ = exp_bounds(saving * llog)
        _, upexp = exp_bounds(saving * ulog)
        weight = Fraction(rank * count, m)
        lo += weight * loexp
        hi += weight * upexp
    return lo, hi


def main() -> None:
    for path, expected in SOURCES.items():
        raw = (NATIVE / path).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == expected,
             f"pinned native source changed: {path}")

    spec = importlib.util.spec_from_file_location("p104_target_transport_compiler",
                                                  NATIVE / "compile.py")
    compiler = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = compiler
    spec.loader.exec_module(compiler)
    witness = json.loads((NATIVE / "inputs/LOWRANK-WITNESS.json").read_text())
    channel = json.loads((NATIVE / "inputs/LOWRANK-RESULT.json").read_text())
    fixture = json.loads((NATIVE / "inputs/P104-FIXTURE.json").read_text())["section4_explicit_P104"]
    channel_adds = sum(event[0] == "add" for event in witness["program"])
    need(channel["rank_mass"] == 2368 and channel_adds == 2624,
         "pinned native channel invoice changed")
    roots, _, physical_roots, transform, _ = compiler.label_isometry()
    removed = {tuple(v) for v in fixture["F0"] + fixture["C"]}
    ports = [root for root in roots if root not in removed]
    physical_root = dict(zip(roots, physical_roots))
    physical_frame = lambda frame: compiler.canon(transform(v) for v in frame)
    full = tuple(1 << i for i in range(9))
    full_chart = compiler.CE.canonical_frame(9, full)
    rank_mass = 0

    for target in range(104):
        reg = f"Y{target}"
        old = physical_frame(witness["final_frames"][reg])
        old_chart = compiler.CE.canonical_frame(9, old)
        need(len(old) == 8,
             f"{reg} final frame does not have rank eight")
        # F9 spans the entire physical nine-dimensional binary chart, so every
        # independent rank-eight endpoint frame is nested inside it.

        up, _ = compiler.CE.lower_child(old_chart.adjoint().then(full_chart))
        down, _ = compiler.CE.lower_child(full_chart.adjoint().then(old_chart))
        need(up["rank"] == down["rank"] == 1,
             f"{reg} common-chart round trip is not two rank-one transports")
        expected_up = compiler.N.adjoint(compiler.N.frame(old, 9)) + compiler.N.frame(full, 9)
        expected_down = compiler.N.adjoint(compiler.N.frame(full, 9)) + compiler.N.frame(old, 9)
        compiler.N.equal(compiler.N.recipe(up), expected_up, f"{reg} lift")
        compiler.N.equal(compiler.N.recipe(down), expected_down, f"{reg} return")
        rank_mass += up["rank"] + down["rank"]

    need(rank_mass == 208, "target round-trip rank mass changed")

    # Try moving the end-cut into each target's final transport. The direct
    # F9 endpoint raises that transport by rank one, while its output adapter
    # rises from rank zero to one. Check the complete operator at every target.
    last_y_write = {}
    for index, event in enumerate(witness["program"]):
        if event[0] in ("transport", "add") and event[1].startswith("Y"):
            last_y_write[event[1]] = index
    need(len(last_y_write) == 104, "missing target terminal writes")
    logical_frames = {name: tuple(frame)
                      for name, frame in witness["initial_frames"].items()}
    terminal_source_frames = {}
    for index, event in enumerate(witness["program"]):
        if event[0] == "transport":
            register = event[1]
            if register.startswith("Y") and index == last_y_write[register]:
                target = int(register[1:])
                terminal_source_frames[target] = logical_frames[f"X{target}"]
            logical_frames[register] = tuple(event[3])
        elif event[0] == "zero":
            logical_frames[event[1]] = tuple(event[2])
        elif event[0] == "erase":
            logical_frames.pop(event[1])
        elif event[0] == "copy":
            logical_frames[event[1]] = tuple(event[3])
    need(len(terminal_source_frames) == 104,
         "missing source frames at terminal target transports")
    endpoint_fusion_rank_mass = 0
    endpoint_profile = {int(rank): int(count)
                        for rank, count in channel["paid_profile"].items()}
    detour_profile = {int(rank): int(count)
                      for rank, count in channel["paid_profile"].items()}
    terminal_detour_rank_mass = 0
    fourier = compiler.N.fourier(9)
    for target in range(104):
        reg = f"Y{target}"
        event = witness["program"][last_y_write[reg]]
        need(event[0] == "transport" and
             event[3] == witness["final_frames"][reg],
             f"{reg} does not finish with its terminal transport")
        old_rank = int(event[4])
        endpoint_profile[old_rank] -= 1
        endpoint_profile[old_rank + 1] = endpoint_profile.get(old_rank + 1, 0) + 1
        old = physical_frame(event[2])
        old_final = physical_frame(event[3])
        source = physical_frame(terminal_source_frames[target])
        normal = physical_root[ports[target]]
        old_chart = compiler.CE.canonical_frame(9, old)
        old_final_chart = compiler.CE.canonical_frame(9, old_final)
        source_chart = compiler.CE.canonical_frame(9, source)
        changed_transport, _ = compiler.CE.lower_child(
            old_chart.adjoint().then(full_chart))
        detour_return, _ = compiler.CE.lower_child(
            full_chart.adjoint().then(old_final_chart))
        original_transport, _ = compiler.CE.lower_child(
            old_chart.adjoint().then(old_final_chart))
        old_adapter, _ = compiler.CE.lower_child(
            old_final_chart.adjoint().then(
                compiler.CE.cgate(9, normal, -1).then(compiler.CE.fourier(9))))
        full_adapter, _ = compiler.CE.lower_child(
            full_chart.adjoint().then(
                compiler.CE.cgate(9, normal, -1).then(compiler.CE.fourier(9))))
        need(changed_transport["rank"] == event[4] + 1,
             f"{reg} F9 terminal transport rank changed unexpectedly")
        need(source_chart == full_chart and detour_return["rank"] == 1 and
             original_transport["rank"] == event[4],
             f"{reg} source frame or terminal detour ranks changed")
        need(old_adapter["rank"] == 0 and full_adapter["rank"] == 1,
             f"{reg} endpoint adapter rank change is not zero-to-one")
        cminus = (("C", normal, -1),)
        compiler.N.equal(compiler.N.recipe(changed_transport),
                         compiler.N.adjoint(compiler.N.frame(old, 9)) +
                         compiler.N.frame(full, 9), f"{reg} rewritten transport")
        compiler.N.equal(
            compiler.N.recipe(changed_transport) +
            compiler.N.recipe(detour_return),
            compiler.N.recipe(original_transport),
            f"{reg} source-frame detour complete Clifford edge including phase")
        compiler.N.equal(compiler.N.recipe(old_adapter),
                         compiler.N.adjoint(compiler.N.frame(old_final, 9)) +
                         cminus + fourier,
                         f"{reg} original adapter")
        compiler.N.equal(compiler.N.recipe(full_adapter),
                         compiler.N.adjoint(compiler.N.frame(full, 9)) +
                         cminus + fourier,
                         f"{reg} rewritten adapter")
        original_endpoint = (
            compiler.N.adjoint(compiler.N.frame(old, 9)) +
            compiler.N.frame(old_final, 9) +
            compiler.N.adjoint(compiler.N.frame(old_final, 9)) +
            cminus + fourier)
        rewritten_endpoint = (
            compiler.N.adjoint(compiler.N.frame(old, 9)) +
            compiler.N.frame(full, 9) +
            compiler.N.adjoint(compiler.N.frame(full, 9)) +
            cminus + fourier)
        compiler.N.equal(original_endpoint, rewritten_endpoint,
                         f"{reg} terminal endpoint rewrite")
        endpoint_fusion_rank_mass += (
            changed_transport["rank"] - event[4] + full_adapter["rank"])
        detour_profile[event[4]] -= 1
        detour_profile[changed_transport["rank"]] = (
            detour_profile.get(changed_transport["rank"], 0) + 1)
        detour_profile[detour_return["rank"]] = (
            detour_profile.get(detour_return["rank"], 0) + 1)
        terminal_detour_rank_mass += (
            changed_transport["rank"] + detour_return["rank"] - event[4])
    endpoint_profile[1] += 104  # one rank-one output adapter per target
    endpoint_profile = {rank: count for rank, count in endpoint_profile.items() if count}
    need(endpoint_fusion_rank_mass == 208,
         "F9 endpoint rewrite did not cost rank mass 208")
    need(sum(rank * count for rank, count in endpoint_profile.items()) == 2576,
         "F9 endpoint profile rank mass changed")
    detour_profile = {rank: count for rank, count in detour_profile.items() if count}
    need(terminal_detour_rank_mass == 208 and detour_profile == endpoint_profile and
         sum(rank * count for rank, count in detour_profile.items()) == 2576,
         "source-frame detour rank profile differs from the direct-F9 profile")

    corrected_profile = {int(rank): int(count)
                         for rank, count in channel["paid_profile"].items()}
    corrected_profile[1] += rank_mass
    corrected_mass = sum(rank * count for rank, count in corrected_profile.items())
    width, roles = 9, int(channel["columns"])
    need(channel["helpers"] == 72 and roles == 104 + 104 + 72,
         "fixed P104 role inventory changed")
    need(max(corrected_profile) < width,
         "rank-mass moment monotonicity requires all child ranks below width")
    moment_at_zero = Fraction(corrected_mass, width * roles)
    need(corrected_mass == 2576 and width * roles == 2520 and
         moment_at_zero == Fraction(322, 315) > 1,
         "favorable zero-saving P104 moment obstruction changed")

    selected_path = REPO / "certificates/selected-result.json"
    selected_raw = selected_path.read_bytes()
    need(hashlib.sha256(selected_raw).hexdigest() == SELECTED_RESULT_SHA256,
         "selected result binding changed")
    selected_kappa = Fraction(json.loads(selected_raw)["kappa"])
    selected_saving = selected_kappa / (1 - selected_kappa)
    def role_thresholds(profile):
        bounds = {}
        for label, saving, lower_integer, upper_integer in (
            ("selected_kappa", selected_saving, 286, 287),
            ("kappa_0_01", Fraction(1, 99), 290, 291),
        ):
            lo, hi = moment_sum_bounds(width, profile, saving)
            need(lo > lower_integer and hi < upper_integer,
                 f"free-role threshold enclosure changed for {label}")
            bounds[label] = {
                "saving_a": str(saving),
                "moment_numerator_lower": outward_decimal(lo, upper=False),
                "moment_numerator_upper": outward_decimal(hi, upper=True),
                "minimum_W_if_new_roles_are_free": upper_integer,
                "additional_roles_over_280": upper_integer - roles,
                "moment_lower_at_minimum_W": outward_decimal(
                    lo / upper_integer, upper=False),
                "moment_upper_at_minimum_W": outward_decimal(
                    hi / upper_integer, upper=True),
                "strict_gap_lower_at_minimum_W": outward_decimal(
                    1 - hi / upper_integer, upper=False),
            }
        return bounds

    role_bounds = {
        "appended_round_trip_profile": role_thresholds(corrected_profile),
        "direct_F9_endpoint_profile": role_thresholds(endpoint_profile),
    }

    result_path = ROOT / "RESULT.json"
    result = json.loads(result_path.read_text())
    result["corrected_paid_profile"] = {
        str(rank): count for rank, count in sorted(corrected_profile.items())
    }
    result["fixed_interface_moment_obstruction"] = {
        "width_m": width,
        "roles_W": roles,
        "rank_mass": corrected_mass,
        "capacity_mW": width * roles,
        "deficit_D": width * roles - corrected_mass,
        "moment_at_zero_saving":
            f"{moment_at_zero.numerator}/{moment_at_zero.denominator}",
        "conclusion": "moment exceeds one for every nonnegative saving before hosting or idle charges",
        "scope": "Fixed P104 interface with 280 arbitrary input columns and width nine; does not exclude a fused schedule with a changed profile or interface.",
    }
    result["optimistic_role_count_thresholds"] = {
        "model": "retains the corrected paid profile and treats every added role as free",
        "thresholds": role_bounds,
    }
    result["terminal_full_chart_fusion_screen"] = {
        "targets": 104,
        "transport_rank_increase": 104,
        "exit_adapter_rank_increase": 104,
        "total_added_rank_mass": endpoint_fusion_rank_mass,
        "paid_profile": {str(rank): count for rank, count in sorted(endpoint_profile.items())},
        "operator_equivalence": "all 104 complete Clifford endpoint compositions checked including phase",
        "conclusion": "ending Y directly in F9 does not reduce the appended correction rank bill",
    }
    result["terminal_source_frame_detour_screen"] = {
        "targets": 104,
        "source_frame": "each X_t is in the full F9 chart at its target's terminal transport",
        "transport_rank_mass_increase": terminal_detour_rank_mass,
        "paid_profile": {str(rank): count
                          for rank, count in sorted(detour_profile.items())},
        "exact_edge_composition": "all 104 old->F9->old_final transport pairs equal the original old->old_final Clifford edge including phase",
        "relation_to_direct_F9_profile": "identical paid rank profile; detour retains the original endpoint adapter",
    }
    result_path.write_text(json.dumps(result, indent=2) + "\n")

    print("PASS_P104_TARGET_COMMON_CHART_ROUND_TRIPS",
          "targets=104", "transports=208", f"rank_mass={rank_mass}",
          "correction_adds=2376",
          f"channel_plus_correction_rank_mass={channel['rank_mass'] + rank_mass}",
          f"channel_plus_correction_adds={channel_adds + 2376}")
    print("PASS_P104_FIXED_INTERFACE_MOMENT_OBSTRUCTION",
          f"m={width}", f"W={roles}", f"D={width * roles - corrected_mass}",
          f"moment_at_a0={moment_at_zero.numerator}/{moment_at_zero.denominator}",
          "no_nonnegative_saving_even_before_hosting")
    print("PASS_P104_OPTIMISTIC_ROLE_THRESHOLDS",
          "appended_and_F9_profiles_agree",
          "selected_min_W=287", "selected_extra_free_roles=7",
          "kappa_0.01_min_W=291", "kappa_0.01_extra_free_roles=11")
    print("PASS_P104_TERMINAL_FULL_CHART_FUSION_SCREEN",
          "targets=104", "transport_rank_increase=104",
          "adapter_rank_increase=104",
          f"added_rank_mass={endpoint_fusion_rank_mass}")
    print("PASS_P104_TERMINAL_SOURCE_FRAME_DETOUR",
          "targets=104", "exact_phase_checked=104",
          f"rank_mass_increase={terminal_detour_rank_mass}",
          "profile_matches_direct_F9=True")


if __name__ == "__main__":
    main()
