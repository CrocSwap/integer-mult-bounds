"""Build the native circuit and check its finite physical invoice."""

from fractions import Fraction
from hashlib import sha256
from math import prod
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "retained"
sys.path[:0] = [str(HERE), str(SOURCE), str(SOURCE / "vendor")]

from bank_split import apply as split_bank
from public_split import split as split_public
from network import Network, encoded, need
import physical


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def digest(value):
    return sha256(encoded(value)).hexdigest()


def dump_graph(net, frames):
    return dict(frames=frames, initial=net.initial, final=net.final, first_output=net.first_output,
                moves=[[k, *v] for k, v in sorted(net.moves.items())],
                forms=[[k, [[i, str(v)] for i, v in sorted(row.items())]]
                       for k, row in sorted(net.forms.items())], schedule=net.schedule())


def build():
    graph, layout = read(HERE / "GRAPH.json.gz"), read(HERE / "LAYOUT.json.gz")
    for pin in read(HERE / "PARENT-SOURCES.json")["files"]:
        if "export" in pin:
            value = {"GRAPH.json.gz": graph, "LAYOUT.json.gz": layout}[pin["export"]]
            need(digest(value) == pin["content_sha256"], "parent export digest")
        elif "adapted_as" not in pin:
            need(sha256((SOURCE / pin["file"]).read_bytes()).hexdigest() == pin["sha256"], "retained source digest")
    frames = graph["frames"]
    moves = {k: (a, b) for k, a, b in graph["moves"]}
    rows = {k: {i: Fraction(v) for i, v in terms} for k, terms in graph["forms"]}
    net = Network(graph["first_output"], graph["initial"], graph["final"], moves, rows)
    for path, transform in (("BANK-EDITS.json", split_bank), ("PUBLIC-EDITS.json", split_public)):
        journal = read(HERE / path)
        need(digest(graph) == journal["source_sha256"], "edit sequence input")
        for event in journal["events"]:
            net = transform(net, event)
            net.schedule()
        graph = dump_graph(net, frames)
        need(digest(graph) == journal["output_sha256"], "edit sequence output")
    extra = len(net.initial) - layout["public"]
    need(extra >= 0, "positive number of added owners")
    next_label = 1 + max(layout["source_labels"])
    layout = dict(layout, public=len(net.initial),
                  source_labels=layout["source_labels"] + list(range(next_label, next_label + extra)))
    return graph, layout, net


def verify_conversions(public, grid, factors):
    odd, height = physical.grid_parts(grid)
    need(prod(factors) == odd and all(type(v) is int and 1 < v < 2**24 for v in factors),
         "complete factorization into bounded scalars")
    cases = 0
    for role in range(public):
        for axis in range(physical.PAYLOAD_AXES):
            value = ((role * (719 - 41 * axis) + 29 + 37 * axis) % 127 - 63) << height
            width = (abs(value) * odd).bit_length() + 2
            current = value
            for v in factors:
                current = physical.scalar_service(current, Fraction(v), width)
            need(current == odd * value, "exact installation of the complete odd scale")
            for v in reversed(factors):
                current = physical.scalar_service(current, Fraction(1, v), width)
            need(current == value, "exact removal of the odd scale")
            cases += 1
    return cases


def native(graph, layout, net):
    from closed_application import main_boundary
    main_boundary(graph, layout)
    h = layout["hosted"]
    second = list(zip(h["X2"], h["Y2"], strict=True))
    mains = set(layout["live"]) | {r + 112 for r in layout["live"]} | set(h["X2"]) | set(h["Y2"])
    need(len(mains) == 400 and len(second) == len(set(h["Dports"])) == 96, "complete real main interface")
    owners = mains, set(h["Dports"]), second
    rows = {k: sorted(row.items()) for k, row in net.forms.items()}
    report = physical.graph_bounds(graph, net.moves, rows, mains)
    manifest = read(HERE / "NATIVE-GRID.json")
    grid, factors = manifest["grid"], manifest["odd_factors"]
    need(report["path_grid"] % grid == 0, "coarse path grid contains the chosen grid")
    report["path_only_grid"] = report["path_grid"]
    report["path_grid"] = grid
    report["path_grid_odd"], report["path_grid_height"] = physical.grid_parts(grid)
    expected = physical.expected_rows(layout["public"], layout, owners, grid)
    report.update(physical.exact_basis_grid(graph, net.moves, rows, grid, expected))
    report.update(physical.held_schedule(graph, net.moves, rows, grid, expected, control=True))
    need(report["minimum_product_grid"] == grid and report["live_sender_alias_control_rejected"],
         "exact product grid and live sender control")
    cases = verify_conversions(layout["public"], grid, factors)
    scalars = physical.scalar_cases([rows], read(SOURCE / "data/CALLER.json.gz"), (2025, *factors))
    return report, dict(odd_factors=factors, round_trips=cases, scalar_cases=scalars,
                        partial_clear=physical.partial_clear_control())


def verify(bit_cap):
    from closed_application import apply, verify_caller
    graph, layout, net = build()
    report, conversion = native(graph, layout, net)
    caller = read(SOURCE / "data/CALLER.json.gz")
    signed, guard, proof, coefficients = verify_caller(caller, graph, layout, read(SOURCE / "data/CALLER-PHASE-BASES.json"))
    price = read(HERE / "PRICE.json")
    result = apply(report, signed, guard, coefficients, conversion["scalar_cases"]["coefficient_bits"],
                   physical, price["claim"], price["tested"], price["lower"], price["upper"], bit_cap)
    # Charge every boundary, including a caller boundary, for a full factor sequence.
    ordinary = result["ordinary"]
    scalars = ordinary["raw_scalar_incidence_allowance_before_factor_32"]
    extra = (len(conversion["odd_factors"]) - 1) * ordinary["odd_conversions"]
    scalars["additional_odd_factor_steps"] = extra
    ordinary["scalar_services"] = 32 * sum(scalars.values())
    return dict(graph_sha256=digest(graph), native=report, conversion=conversion, caller=signed,
                caller_guard=guard, caller_proof=proof, application=result)
