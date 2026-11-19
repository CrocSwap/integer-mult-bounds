"""Verify the native circuit on the exact scalar grid and each independent owner."""
from pathlib import Path
from fractions import Fraction
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import digest, inputs, jobs, need, physical, read


def selected_interfaces():
    claim = read("vendor/selected-claim.json")
    bit, = [row for row in claim["uniform_templates"] if row["family"] == "BIT before cover"]
    validation = read("vendor/selected-validation.json")
    admission = read("vendor/selected-bit-ambient.json")
    need(bit["ambient"] == 134 and bit["rank_encoding"] == "2^296630000000000"
         and Fraction(bit["saving"]) > Fraction("0.00385248"), "selected BIT bound")
    need(validation["status"] == "admitted_conditional" and validation["registered_replays_complete"]
         and admission["exit_code"] == 0 and admission["source_unchanged"], "selected conditional record")
    assumptions = [entry["id"] for entry in claim["assumptions"]]
    need(assumptions == ["native_all_columns", "owned_erasure", "compiler", "precision_tape",
                         "analytic_recovery"], "selected compiler interfaces")
    return assumptions


def verify():
    graph, layout, moves, rows, owners = inputs()
    paid, helpers, _ = jobs(graph, owners[0], moves)
    native = physical.graph_bounds(graph, moves, rows, owners[0])
    need(paid == native["paid_native_ranks"] and helpers == native["positive_helper_ranks"],
         "independent rank census")
    grid = native["path_grid"]
    expected = physical.expected_rows(layout["public"], layout, owners, grid)
    native.update(physical.exact_basis_grid(graph, moves, rows, grid, expected))
    native.update(physical.held_schedule(graph, moves, rows, grid, expected, control=True))
    need(native["live_sender_alias_control_rejected"]
         and set(native["missing_odd_factor_controls"]) == {3, 5}, "grid and sender controls")
    missing_primes = []
    for prime in (7, 17):
        reduced = grid
        while reduced % prime == 0:
            reduced //= prime
        if reduced == grid:
            continue
        try:
            reduced_rows = physical.expected_rows(layout["public"], layout, owners, reduced)
            physical.exact_basis_grid(graph, moves, rows, reduced, reduced_rows)
        except ValueError as error:
            need(str(error) == "nonintegral scalar pre-product", "incorrect grid rejection")
        else:
            raise ValueError("inexact product accepted")
        missing_primes.append(prime)
    caller = read("data/CALLER.json.gz")
    scalars = physical.scalar_cases([rows], caller, (2025, native["path_grid_odd"]))
    return layout, dict(graph_sha256=digest(graph), conditional_interfaces=selected_interfaces(),
                        physical=dict(native=native, scalars=scalars, extra_prime_rejections=missing_primes,
                                      partial_clear_control=physical.partial_clear_control()))
