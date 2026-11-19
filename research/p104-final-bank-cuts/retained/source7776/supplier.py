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
from public_split import rotate_all, split as split_public
from graph_delta import apply as apply_delta, rename_senders, restore_relays
from network import Network, coefficients, encoded, need
from puncture import entrance_form, in_parallel_basis, pulse_response, puncture
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


def replay_events(net, events):
    for event in events:
        if "split" in event:
            if "relabel_before_split" in event:
                net = move_chart(net, *event["relabel_before_split"])
            net = split_public(net, event["split"])
        elif event.get("type") == "parallel_bank_puncture":
            oriented = net.transpose() if event["orientation"] else net
            oriented = in_parallel_basis(oriented, event["remove"], coefficients(event["receive_direction"]))
            oriented = puncture(oriented, event)
            net = oriented.transpose() if event["orientation"] else oriented
        elif "transposed" in event:
            net = split_public(net, event)
        else:
            net = split_bank(net, event)
        net.schedule()
    return net


def move_chart(net, before, after):
    """Move the local linear calculations and all of their incident endpoints."""
    def move(chart):
        return after if chart == before else chart
    return Network(net.first_output, [move(a) for a in net.initial], [move(b) for b in net.final],
                   {k: (move(a), move(b)) for k, (a, b) in net.moves.items()}, net.forms)


def check_peer_routes(stage, original):
    """Match the retired routes and the new paid distance to the cited edit."""
    old = {i: a for i, a, b in original["delta"]["moves"] if b is None}
    new = [b for i, a, b in original["delta"]["moves"] if a is None]
    need({i: a for i, a, b in stage["routes"] if b is None} == old and
         [b for i, a, b in stage["routes"] if a is None] == new, "published paid replacements")


def build():
    graph, layout = read(HERE / "GRAPH.json.gz"), read(HERE / "LAYOUT.json.gz")
    sources = read(HERE / "PARENT-SOURCES.json")
    for pin in sources["files"]:
        if "export" in pin:
            value = {"GRAPH.json.gz": graph, "LAYOUT.json.gz": layout}[pin["export"]]
            need(digest(value) == pin["content_sha256"], "parent export digest")
        elif "adapted_as" not in pin:
            need(sha256((SOURCE / pin["file"]).read_bytes()).hexdigest() == pin["sha256"], "retained source digest")
    frames = graph["frames"]
    moves = {k: (a, b) for k, a, b in graph["moves"]}
    rows = {k: {i: Fraction(v) for i, v in terms} for k, terms in graph["forms"]}
    net = Network(graph["first_output"], graph["initial"], graph["final"], moves, rows)
    relays = sources["relays"]
    for filename in ("DELTA.json", "STACK-DELTA.json"):
        raw = gzip.decompress((HERE / "relays" / (filename + ".gz")).read_bytes())
        need(sha256(raw).hexdigest() == relays["files"][filename], "published relay source")
        patch = json.loads(raw)
        need(digest(graph) == patch["parent_graph_sha256"], "relay input")
        net = restore_relays(net, patch)
        graph = dump_graph(net, frames)
        need(digest(graph) == patch["joint_graph_sha256"], "published relay result")
    net = rename_senders(net, {int(i): j for i, j in relays["new_sender_names"].items()})
    graph = dump_graph(net, frames)
    need(digest(graph) == relays["renamed_graph_sha256"], "renamed relay graph")
    journals = [read(HERE / "BANK-EDITS.json"), read(HERE / "PUBLIC-EDITS.json")]
    for journal in journals + read(HERE / "BASIS-EDITS.json.gz"):
        need(digest(graph) == journal["source_sha256"], "edit sequence input")
        net = replay_events(net, journal["events"])
        graph = dump_graph(net, frames)
        need(digest(graph) == journal["output_sha256"], "edit sequence output")
    later = sources["later_relays"]
    raw = gzip.decompress((HERE / "relays/7774-PAID-EDITS.json.gz").read_bytes())
    need(sha256(raw).hexdigest() == later["files"]["PAID-EDITS.json"], "second published relay source")
    peer_edits = json.loads(raw)["ordered_edits"]
    edits = read(HERE / "JOINT-EDITS.json.gz")
    need([e["peer_edit"] for e in edits if "peer_edit" in e] == later["included"], "ordered peer edits")
    for edit in edits:
        need(digest(graph) == edit["source"], "joint edit source")
        if "events" in edit:
            frames = frames + edit.get("new_frames", [])
            net = replay_events(net, edit["events"])
        elif "rotations" in edit:
            net = Network(net.first_output, net.initial, net.final, net.moves, rotate_all(net, edit["rotations"]))
        else:
            if "peer_edit" in edit:
                check_peer_routes(edit, peer_edits[edit["peer_edit"] - 1])
            net = apply_delta(net, edit)
        graph = dump_graph(net, frames)
        need(digest(graph) == edit["result"], "joint edit result")
    extra = len(net.initial) - layout["public"]
    need(extra >= 0, "positive number of added owners")
    next_label = 1 + max(layout["source_labels"])
    layout = dict(layout, public=len(net.initial), frames=frames,
                  source_labels=layout["source_labels"] + list(range(next_label, next_label + extra)))
    return graph, layout, net


def check_omissions(net):
    """Find a changed output coefficient if a new paid return is set to zero."""
    order = net.schedule()
    witnesses = read(HERE / "relays/OMISSIONS.json")
    expected = {(e["peer_edit"], key) for e in read(HERE / "JOINT-EDITS.json.gz") if "peer_edit" in e
                for key, before, _ in e["routes"] if before is None}
    need({(w["peer_one_based_edit"], w["paid"]) for w in witnesses} == expected
         and len(witnesses) == len(expected), "one omission witness for each new peer transfer")
    for w in witnesses:
        key = w["paid"]
        entry = entrance_form(net, order, {key: 1})
        exit_ = pulse_response(net, order, {key: 1})
        x = entry.get(w["source"], 0)
        y = exit_.get(net.first_output + w["terminal"], 0)
        need(x == Fraction(w["source_coefficient"]) and y == Fraction(w["terminal_coefficient"]) and
             x and y and -x*y == Fraction(w["difference_after_omission"]), "necessary paid restoration")
    return len(witnesses)


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
    result = apply(report, signed, guard, coefficients, conversion,
                   physical, price["claim"], price["tested"], price["lower"], price["upper"], bit_cap)
    return dict(graph_sha256=digest(graph), checked_relay_omissions=check_omissions(net),
                native=report, conversion=conversion, caller=signed,
                caller_guard=guard, caller_proof=proof, application=result)
