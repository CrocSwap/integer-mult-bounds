#!/usr/bin/env python3
"""Reconstruct the fixed #7674 pivots with the independent role-230 splice."""
from argparse import ArgumentParser
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
from graphlib import CycleError
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import signal
import sys
from types import ModuleType

PEER_HEAD = "28b2af322a1fab01b3734365988930920f9dda48"
PEER_SCIENCE = "26b6c469aa6c4aa04322ce25a22150f90e5fb14e"
PARENT = "ee251f6005d2a92b887c5b804bd7aac05989d278b2c9ccb3c3091b50d533b08d"
DIRECT = "ab5653d6b6007f8a7987e7ffc6ebab24c662ba852a0d0b446c3a1be19b88db8a"
CALLER = "62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf"
CONTACTS = "9e1d2b56750dee78be16b4514deae18dc886767dc9f92f21e1c6e0f10f6215dd"
PINS = {
    "network.py": "a9169fd6ad0a13c69cf39bd32649d53256f6d6fa2ed2ceda854f848b64f4c546",
    "native.py": "788465324eb8693a698c75cb3dfdf1b82297324d5583910107ecad4600645e43",
    "PIVOTS.json": "fb22afc8aaf543e62709fa682f222577e6bdf4e1f1994d307784468314c3da85",
    "RESULT.json": "00340c699fd7e2895d31a41d1eb60aebf91d7ba2c1c193dc002f69315298cd38",
}
REWRITTEN = {97471, 97473, 97475, 97479, 102393, 101174, 101176, 102653}
INNER = {97471, 97473, 97475}
ROUTES = {97471: ((261, 730), (261, 912)), 102393: ((730, 127), (912, 127))}
RECOVERY = {101174: Q(-1, 2), 101176: Q(-1, 2), 102653: Q(1)}


def require(ok, detail):
    if not ok:
        raise ValueError(detail)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(raw):
    return sha256(raw).hexdigest()


def pinned(path, expected):
    raw = path.read_bytes()
    require(digest(raw) == expected, f"source byte pin {path.name}")
    return raw


def write(out, name, item, *, exact=False):
    data = item if exact else canonical(item) + b"\n"
    with (out / name).open("xb") as f:
        f.write(data)
    return digest(data)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def peer_module(package, *, reference=False):
    path = package / ("native.py" if reference else "network.py")
    name = "_bank24_peer_native" if reference else "_bank24_peer_network"
    if name in sys.modules and sys.modules[name].__file__ == str(path):
        return sys.modules[name]
    raw = pinned(path, PINS[path.name])
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    saved = sys.path[:]
    prior = sys.modules.get("network")
    try:
        if reference:
            sys.modules["network"] = peer_module(package)
        exec(compile(raw, str(path), "exec"), module.__dict__)
    finally:
        sys.path[:] = saved
        if prior is None:
            sys.modules.pop("network", None)
        else:
            sys.modules["network"] = prior
    return module


def bind_words(package, source_word, direct_word, contacts):
    engine = peer_module(package)
    word = engine.source_word()
    require(digest(canonical(word)) == PARENT, "exact published source word")
    if source_word is not None:
        require(digest(gzip.decompress(source_word.read_bytes())) == PARENT, "optional source canonical pin")
    contact = json.loads(pinned(contacts, CONTACTS))
    require(contact["source_word"] == PARENT, "role-230 splice source")
    for clock, event in contact["anchors"].items():
        require(word["program"][int(clock)] == event, f"literal splice anchor {clock}")
    edits = {int(clock): events for clock, events in contact["splice"].items()}
    program, move_keys = [], {}
    for clock, current in enumerate(word["program"]):
        emitted = edits.get(clock, [current])
        moves = [(len(program) + i, event) for i, event in enumerate(emitted) if event[0] == "MOVE"]
        if current[0] == "MOVE":
            require(len(moves) == 1 and moves[0][1][1] == current[1], f"stable MOVE owner {clock}")
            move_keys[moves[0][0]] = clock
        else:
            require(not moves, f"new MOVE key {clock}")
        program.extend(emitted)
    direct = {**word, "program": program}
    require(digest(canonical(direct)) == DIRECT and len(program) == 150525, "exact reconstructed child")
    if direct_word is not None:
        require(digest(gzip.decompress(direct_word.read_bytes())) == DIRECT, "optional direct canonical pin")
    return engine, word, direct, move_keys


def stable_fold(engine, word, direct, move_keys):
    net = engine.fold(direct)
    anchor = len(word["program"])
    require(net.moves.keys() == move_keys.keys(), "all native child MOVE slots mapped")
    require(len(set(move_keys.values())) == len(net.moves) == 6157, "stable MOVE key injection")

    def resolve(k):
        if k < 0:
            return k
        if k >= net.first_output:
            return anchor + (k - net.first_output)
        return move_keys[k]

    moves = {resolve(k): value for k, value in net.moves.items()}
    forms = {resolve(k): {resolve(donor): coefficient for donor, coefficient in row.items()}
             for k, row in net.forms.items()}
    return engine.Network(anchor, net.initial, net.final, moves, forms)


def local_rewrite(engine, net):
    x = {89727: Q(1), 89728: Q(1), 97321: Q(-4)}
    z = {91754: Q(1), 95209: Q(-1)}
    forms = net.forms.copy()
    moves = net.moves.copy()
    old = {
        97471: x, 97473: z, 97475: {97470: Q(1), 97471: Q(1)},
        97479: {97473: Q(1), 97470: Q(-1), 97471: Q(-1)},
        102393: {97471: Q(1, 2), 97473: Q(1, 2), 97470: Q(-1, 2)},
    }
    require(all(forms[k] == row for k, row in old.items()), "exact folded local preimage")
    for key, (before, after) in ROUTES.items():
        require(moves[key] == before, f"exact route preimage at {key}")
        moves[key] = after
    forms[97471] = x.copy()
    engine.add_scaled(forms[97471], z, Q(1, 2))
    forms[97473] = {k: Q(2, 3) * c for k, c in z.items()}
    engine.add_scaled(forms[97473], x, Q(-2, 3))
    forms[97475] = {97470: Q(1), 97473: Q(-1, 2)}
    forms[97479] = {97473: Q(3, 2), 97470: Q(-1)}
    forms[102393] = {97471: Q(2, 3), 97475: Q(-1, 2)}
    for slot, coefficient in RECOVERY.items():
        row = net.forms[slot]
        require(row.get(97475) == coefficient and 97471 not in row, f"exact recovered C read at {slot}")
        forms[slot] = {**row, 97471: Q(2, 3) * coefficient}
    require({k for k, row in net.forms.items() if 97475 in row} == RECOVERY.keys(),
            "complete old C-reader incidence")
    return engine.Network(net.first_output, net.initial, net.final, moves, forms)


def equal_graph(one, two, context):
    require((one.first_output, one.initial, one.final, one.moves) ==
            (two.first_output, two.initial, two.final, two.moves), f"graph move/boundary mismatch {context}")
    delta = [k for k in one.forms.keys() | two.forms.keys() if one.forms.get(k) != two.forms.get(k)]
    require(not delta, f"graph form mismatch {context}: {sorted(delta)[:8]}")


def oriented(net, edit):
    return net.transpose() if edit["direction"] == "transpose" else net


def pivots_in_lockstep(engine, old, direct, edits):
    equal_graph(local_rewrite(engine, old), direct, "initial stable child fold")
    steps = []
    for index, edit in enumerate(edits):
        before, child_before = oriented(old, edit), oriented(direct, edit)
        drop, lead = edit["remove"], edit["pivot"]
        old_reads = {k: row[drop] for k, row in before.forms.items() if drop in row}
        new_reads = {k: row[drop] for k, row in child_before.forms.items() if drop in row}
        require(old_reads == new_reads and old_reads, f"pivot uses at entry {index}")
        require(before.moves[drop] == child_before.moves[drop] and before.moves[lead] == child_before.moves[lead],
                f"pivot route preimage at entry {index}")
        old = oriented(engine.pivot(before, edit), edit)
        direct = oriented(engine.pivot(child_before, edit), edit)
        orders = (old.schedule(), direct.schedule())
        equal_graph(local_rewrite(engine, old), direct, f"commutation at pivot {index}")
        require(len(old.moves) == len(direct.moves) == 6156 - index, f"slot decrement {index}")
        steps.append({"index": index, "direction": edit["direction"], "remove": drop, "lead": lead,
                      "surviving_slots": len(old.moves), "cocharted_use_count": len(old_reads),
                      "lead_before_in_direction": before.moves[lead], "lead_final_forward": old.moves[lead],
                      "same_directed_forms_after_commutation": True,
                      "scheduled_nodes_each": [len(order) for order in orders]})
    return old, direct, steps


def build_graphs(package, source_word, direct_word, contacts):
    engine, word, direct_word_value, keys = bind_words(package, source_word, direct_word, contacts)
    edits = json.loads(pinned(package / "PIVOTS.json", PINS["PIVOTS.json"]))
    result = json.loads(pinned(package / "RESULT.json", PINS["RESULT.json"]))
    require(len(edits) == result["pivot_checks"] == 15, "frozen pivot denominator")
    require(Counter(e["direction"] for e in edits) == {"forward": 7, "transpose": 8},
            "frozen pivot orientation counts")
    old = engine.fold(word)
    direct = stable_fold(engine, word, direct_word_value, keys)
    peer, combined, steps = pivots_in_lockstep(engine, old, direct, edits)
    require([[s["direction"], s["remove"], s["lead"], s["surviving_slots"]] for s in steps] ==
            result["application"]["pivots"], "published exact pivot schedule inventory")
    require({k for k in peer.moves if peer.moves[k] != combined.moves[k]} == ROUTES.keys(),
            "only the two role-230 paid routes changed")
    require({k for k in peer.forms if peer.forms[k] != combined.forms[k]} == REWRITTEN,
            "only the exact folded role-230 row forms changed")
    return word, peer, combined, {
        "published_pivot_inventory_reproduced": True, "stages": steps,
        "changed_move_keys": sorted(ROUTES), "changed_forms": sorted(REWRITTEN),
        "first_output": peer.first_output,
        "local_semantic_clock_map": {str(k): v for k, v in keys.items()
                                     if v in REWRITTEN or v in {97470, 97476, 98347, 98350}},
    }


def record(net, word, kind):
    return {
        "metadata": {"schema": "p104-exact-banked-dag/v1", "kind": kind,
                     "peer_head": PEER_HEAD, "scientific_commit": PEER_SCIENCE,
                     "source_word_sha256": PARENT,
                     "role230_direct_word_sha256": DIRECT if kind == "candidate" else None,
                     "caller_sha256": CALLER, "fixed_pivot_sha256": PINS["PIVOTS.json"],
                     "published_result_sha256": PINS["RESULT.json"]},
        "frames": word["frames"], "initial": net.initial, "final": net.final,
        "first_output": net.first_output,
        "moves": [[key, *route] for key, route in sorted(net.moves.items())],
        "forms": [[key, [[donor, str(coef)] for donor, coef in sorted(row.items())]]
                  for key, row in sorted(net.forms.items())],
        "schedule": net.schedule(),
    }


def freeze(out, word, peer, child, stage):
    graphs = {}
    for kind, net in (("peer", peer), ("candidate", child)):
        raw = canonical(record(net, word, kind))
        filename = kind.upper() + "-GRAPH.json.gz"
        byte_sha = write(out, filename, gzip.compress(raw, mtime=0), exact=True)
        graphs[kind] = {"file": filename, "canonical_sha256": digest(raw), "gzip_sha256": byte_sha}
    result = {"status": "FROZEN_BOTH_ORDERS_WITH_EXACT_STABLE_KEYS",
              "observed_at": stamp(), "graphs": graphs, **stage}
    write(out, "GRAPH-BINDING.json", result)
    for kind, info in graphs.items():
        print("FROZEN_BANK24_GRAPH", kind, info["canonical_sha256"], info["gzip_sha256"], flush=True)
    return result


def verify_saved_signals(package, source_word, direct_word, contacts):
    engine, word, direct, keys = bind_words(package, source_word, direct_word, contacts)
    native = peer_module(package, reference=True)
    edits = json.loads(pinned(package / "PIVOTS.json", PINS["PIVOTS.json"]))
    child = stable_fold(engine, word, direct, keys)
    checked = []
    for index, edit in enumerate(edits):
        before = oriented(child, edit)
        native.verify_pivot(before, edit)
        child = oriented(engine.pivot(before, edit), edit)
        checked.append({"index": index, "orientation": edit["direction"],
                        "remove": edit["remove"], "lead": edit["pivot"], "saved_signal_equal": True})
        print("PASS_BANK24_SAVED_SIGNAL", index, edit["direction"], flush=True)
    return child, checked


def normalized_equal(lrow, lgrid, rrow, rgrid):
    return len(lrow) == len(rrow) and all(v * rgrid == rrow.get(col, 0) * lgrid for col, v in lrow.items())


def census_native(word, net, total, peak, work):
    dyadic = (total & -total).bit_length() - 1
    bits = max(max(abs(c.numerator).bit_length(), c.denominator.bit_length())
               for row in net.forms.values() for c in row.values())
    mains = set(word["live"]) | {r + 112 for r in word["live"]} | set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    return {"grid": str(total), "odd": total >> dyadic, "dyadic_height": dyadic,
            "peak_scaled_mass": str(Q(peak, 1 << dyadic)), "checked_products": work,
            "terms": sum(map(len, net.forms.values())), "slots": len(net.moves),
            "coefficient_bits": bits, "public": word["public"], "mains": len(mains)}


def replay_pair(package, word, peer, child, *, transpose=False):
    native = peer_module(package, reference=True)
    peer_net, child_net = (peer.transpose(), child.transpose()) if transpose else (peer, child)
    a, old, peak_a, work_a = native.evaluate(peer_net)
    b, new, peak_b, work_b = native.evaluate(child_net)
    require(old.keys() == new.keys(), "matched arbitrary-input row keys")
    mismatches = [i for i in old if i not in INNER and not normalized_equal(old[i], a, new[i], b)]
    require(not mismatches, f"changed exposed row in {'adjoint' if transpose else 'forward'}: {mismatches[:8]}")
    first = peer.first_output
    endpoints = [first + role for role in range(word["public"])]
    expected = native.expected(word, a)
    if transpose:
        swapped = [{} for _ in endpoints]
        for r, row in enumerate(expected):
            for src, value in row.items():
                swapped[src][r] = value
        expected = swapped
    require([old[i] for i in endpoints] == expected, "exact published matrix and direction")
    output = {"direction": "adjoint" if transpose else "forward", "public_outputs": len(endpoints),
              "equal_exposed_noninput_rows": sum(i >= 0 and i not in INNER for i in old),
              "differing_internal_rows": sorted(i for i in INNER if not normalized_equal(old[i], a, new[i], b)),
              "old_grid": str(a), "new_grid": str(b), "old_products": work_a, "new_products": work_b}
    if not transpose:
        restore = {k: 3 * v for k, v in new[97475].items()}
        peer_module(package).add_scaled(restore, new[97471], 2)
        require(normalized_equal(old[97475], a, restore, 3 * b), "exposed Y restoration in chart 912")
        output["restored_y_in_c"] = True
        output["published_native"] = census_native(word, peer, a, peak_a, work_a)
        output["candidate_native"] = census_native(word, child, b, peak_b, work_b)
    return output


def controls(package, child):
    engine = peer_module(package)
    native = peer_module(package, reference=True)
    def with_rows(rows, moves=None):
        return engine.Network(child.first_output, child.initial, child.final,
                              child.moves if moves is None else moves, rows)
    rows = child.forms.copy()
    rows[97473] = {**rows[97473], 89727: -rows[97473][89727]}
    wrong = with_rows(rows)
    a, old, _, _ = native.evaluate(child, {97479})
    b, new, _, _ = native.evaluate(wrong, {97479})
    require(wrong.moves == child.moves and not normalized_equal(old[97479], a, new[97479], b),
            "same-price wrong scalar escaped")
    rows = child.forms.copy()
    rows[97471] = {**rows[97471], 97470: Q(1)}
    try:
        with_rows(rows).schedule()
    except ValueError as failure:
        require(str(failure) == "nonlocal scalar", "wrong coframe rejection boundary")
    else:
        raise ValueError("wrong coframe accepted")
    rows, moves = child.forms.copy(), child.moves.copy()
    m, n = child.first_output - 2, child.first_output - 1
    require(m not in moves and n not in moves, "cycle-control spare stable keys")
    rows.update({m: {n: Q(1)}, n: {m: Q(1)}})
    moves.update({m: (261, 912), n: (912, 261)})
    try:
        with_rows(rows, moves).schedule()
    except CycleError:
        pass
    else:
        raise ValueError("cocharted two-node cycle accepted")
    return {"same_price_wrong_scalar": "rejected at exposed Z slot 97479",
            "nonlocal_chart": "rejected before schedule", "cocharted_cycle": "rejected by topological order"}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--peer-package", type=Path, required=True)
    parser.add_argument("--contacts-file", type=Path, required=True)
    parser.add_argument("--parent-word", type=Path)
    parser.add_argument("--direct-word", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--materialize-only", type=Path, metavar="EXACT_RESULT",
                        help="Rebuild both ordered graphs and compare their hashes to a completed exact receipt")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_CPU, (240, 240))
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
    signal.alarm(420)
    started = stamp()
    out = args.out.resolve()
    out.mkdir()
    package = args.peer_package.resolve()
    inputs = (package, args.parent_word, args.direct_word, args.contacts_file.resolve())
    start_sha = write(out, "START.json", {
        "status": "RUNNING_BANK24_WIRE_COMMUTATION", "time": started,
        "pid": os.getpid(), "affinity": sorted(os.sched_getaffinity(0)),
        "cpu_limit_seconds": 240, "address_space_bytes": 2 * 1024**3, "wall_limit_seconds": 420,
        "head": PEER_HEAD, "source_word": PARENT, "direct_word": DIRECT, "input_pins": PINS,
        "authorization_receipt": "progress.kappa-leading-20261118t0540z.00000026",
        "scope": "https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19702865",
        "driver_sha256": digest(Path(__file__).read_bytes()),
    })
    print("START_BANK24_WIRE_COMMUTATION", start_sha, flush=True)
    try:
        word, peer, child, stages = build_graphs(*inputs)
        binding = freeze(out, word, peer, child, stages)
        if args.materialize_only is not None:
            exact_raw = args.materialize_only.read_bytes()
            exact = json.loads(exact_raw)
            require(exact["status"] == "PASS_BANK24_WIRE_COMMUTATION"
                    and exact["graphs"] == binding["graphs"] and exact["input_pins"] == PINS,
                    "proven deterministic graph bindings")
            write(out, "MATERIALIZATION.json", {
                "status": "PASS_BANK24_MATERIALIZATION_ONLY", "graphs": binding["graphs"],
                "exact_result_sha256": digest(exact_raw),
            })
            print("PASS_BANK24_MATERIALIZATION_ONLY", flush=True)
            return
        candidate_from_saved, pivots = verify_saved_signals(*inputs)
        equal_graph(candidate_from_saved, child, "fresh saved-signal branch")
        checked = controls(package, child)
        forward = replay_pair(package, word, peer, child)
        reference = json.loads(pinned(package / "RESULT.json", PINS["RESULT.json"]))
        require(forward["published_native"] == reference["native"], "complete published native receipt reproduced")
        adjoint = replay_pair(package, word, peer, child, transpose=True)
        for filename, pin in PINS.items():
            pinned(package / filename, pin)
        pinned(args.contacts_file, CONTACTS)
        result = {
            "status": "PASS_BANK24_WIRE_COMMUTATION", "started_at": started, "completed_at": stamp(),
            "start_sha256": start_sha,
            "binding_sha256": digest((out / "GRAPH-BINDING.json").read_bytes()),
            "graphs": binding["graphs"], "input_pins": PINS, "parent_source_word": PARENT,
            "direct_child_word": DIRECT, "caller_sha256": CALLER, "peer_head": PEER_HEAD,
            "exact_whole_graph_both_orders": True, "published_native_receipt_reproduced": True,
            "changed_move_keys": sorted(ROUTES), "changed_forms": sorted(REWRITTEN),
            "pivot_checks": pivots, "forward": forward, "adjoint": adjoint, "controls": checked,
            "resource": {"cpu_seconds": os.times().user + os.times().system,
                         "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},
            "scope": "Exact normalized graph construction, exposed rows, stable routes, chronology and fixed saved-signal identities. Physical Gaussian recipes and complete signed application have their own gates.",
        }
        result_sha = write(out, "RESULT.json", result)
        print("PASS_BANK24_WIRE_COMMUTATION", binding["graphs"]["candidate"]["canonical_sha256"], result_sha, flush=True)
    except (ValueError, CycleError, OSError, KeyError) as error:
        write(out, "FAILURE.json", {
            "status": "FAIL_BANK24_WIRE_COMMUTATION", "time": stamp(),
            "error_type": type(error).__name__, "detail": str(error),
            "start_sha256": start_sha,
        })
        raise


if __name__ == "__main__":
    main()
