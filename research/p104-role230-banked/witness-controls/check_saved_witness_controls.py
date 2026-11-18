#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the two exact rare saved-witness controls on the frozen banked graph.

The algebra and incidence checks are retained from Clear1nsight's guarded
role-transfer review, with substantial OpenAI Codex assistance. This adapter
uses only the public release package and exact source pins.
"""

from argparse import ArgumentParser
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import resource
import signal
import subprocess
import sys
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
DRIVER = "7acf26e997e8d659b8c61fbaa675d6478fcdffff1600f45c6722824497fdea37"
CHILD = "1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150"
CHILD_GZIP = "8e28c1d403145ca5d72521f4acd7e068603598334c87f18f2fefb738844a1970"
RECEIPT = "cde8b602d182ece20f55616decab1bf5c2b64e877770c20106afca44ff08752d"
EXPECTED = "b4c9d7dca9b3416572d48496f03ddee122dd0194d1b0388d4ea2000fa5bde3aa"


def require(ok, detail):
    if not ok:
        raise ValueError(detail)


def sha(data):
    return sha256(data).hexdigest()


def pinned(path, digest):
    data = path.read_bytes()
    require(sha(data) == digest, f"exact input bytes: {path.name}")
    return data


def graph_driver(path):
    pinned(path, DRIVER)
    spec = spec_from_file_location("banked_control_graph_driver", path)
    driver = module_from_spec(spec)
    spec.loader.exec_module(driver)
    return driver


def with_rows(engine, net, rows):
    return engine.Network(net.first_output, net.initial, net.final, net.moves, rows)


def column(net, order, index):
    values = {~index: Fraction(1)}
    for node in order:
        value = sum(coefficient * values[donor] for donor, coefficient in net.forms[node].items() if donor in values)
        if value:
            values[node] = value
    return values


def dot(entries, values):
    return sum(Fraction(amount) * values.get(key, 0) for key, amount in entries)


def residual(witness, values):
    return dot(witness["sender"], values) - dot(witness["combination"], values) - dot(witness["receiver"], values)


def gauge_control(driver, peer, contacts):
    engine, word, direct, keys = driver.bind_words(peer, None, None, contacts)
    pivots = json.loads(pinned(peer / "PIVOTS.json", driver.PINS["PIVOTS.json"]))
    net = driver.stable_fold(engine, word, direct, keys)
    for edit in pivots[:2]:
        require(edit["direction"] == "forward", "first two physical pivots")
        net = engine.pivot(net, edit)
    witness = pivots[2]
    require((witness["direction"], witness["remove"], witness["pivot"]) == ("transpose", 89622, 88983),
            "third fixed pivot")
    net = net.transpose()
    token = 97185
    require(token in net.moves and token not in net.forms[token], "internal token only")
    readers = sorted(j for j, row in net.forms.items() if token in row)
    require(readers, "nonempty real consumer set")
    changed = net.forms.copy()
    changed[token] = {donor: -value for donor, value in changed[token].items()}
    for node in readers:
        changed[node] = {**changed[node], token: -changed[node][token]}
    gauged = with_rows(engine, net, changed)
    old_order, new_order = net.schedule(), gauged.schedule()
    require(old_order == new_order and net.moves == gauged.moves, "same causal order and paid transfers")

    # Verify every scalar incidence c'_(j,k) = s_j c_(j,k) s_k.
    # All external signs are +1. Induction in the common schedule therefore
    # gives h'_j = s_j h_j on every column, preserving every external row.
    for node, row in net.forms.items():
        mutated = changed[node]
        require(mutated.keys() == row.keys(), "same scalar incidence")
        sign = -1 if node == token else 1
        for donor, coefficient in row.items():
            require(mutated[donor] == sign * coefficient * (-1 if donor == token else 1),
                    "exact conjugate sign on each scalar incidence")
    old, new = column(net, old_order, 17), column(gauged, new_order, 17)
    require(set(old) == set(new) and all(new[j] == (-v if j == token else v) for j, v in old.items()),
            "observed complete column obeys the algebraic gauge")
    original, stale = residual(witness, old), residual(witness, new)
    require(original == 0 and stale != 0, "unchanged witness must reject the endpoint-preserving mutation")
    verifier = driver.peer_module(peer, reference=True)
    verifier.verify_pivot(net, witness)
    try:
        verifier.verify_pivot(gauged, witness)
    except ValueError as error:
        require(str(error) == "saved signal identity", "stale witness rejected on the exact saved identity")
    else:
        raise ValueError("endpoint-preserving mutation accepted the stale saved-signal witness")
    return {"orientation": "transpose", "entry_zero_based": 2, "remove": 89622, "pivot": 88983,
            "gauge_token": token, "readers": readers, "public_endpoints_equal_by_algebra": True,
            "same_order": True, "paid_slots": len(net.moves), "column": 17,
            "original_token_value": str(old.get(token, 0)), "gauged_value": str(new.get(token, 0)),
            "original_residual_sender_minus_combination_minus_receiver": str(original),
            "stale_residual_sender_minus_combination_minus_receiver": str(stale),
            "source_checker": "saved signal identity",
            "expected_residual_reproduced": (old.get(token, 0), stale) == (2, -8)}


def omitted_read_control(driver, peer, candidate, receipt):
    record = json.loads(pinned(receipt, RECEIPT))
    require(record["status"] == "PASS_BANK24_WIRE_COMMUTATION"
            and record["graphs"]["candidate"]["canonical_sha256"] == CHILD
            and record["graphs"]["candidate"]["gzip_sha256"] == CHILD_GZIP, "candidate receipt binding")
    raw = gzip.decompress(pinned(candidate, CHILD_GZIP))
    require(sha(raw) == CHILD, "exact final candidate graph")
    graph = json.loads(raw)
    engine = driver.peer_module(peer)
    moves = {key: (start, end) for key, start, end in graph["moves"]}
    forms = {key: {donor: Fraction(amount) for donor, amount in row} for key, row in graph["forms"]}
    net = engine.Network(graph["first_output"], graph["initial"], graph["final"], moves, forms)
    require(net.moves[101174] == (912, 148), "retained exposed outgoing chart route")
    owner = 39
    coefficient = forms[101174][97471]
    require(coefficient == Fraction(-1, 3), "exact recovery term under test")
    after = forms.copy()
    after[101174] = {k: v for k, v in forms[101174].items() if k != 97471}
    bad = with_rows(engine, net, after)
    order, bad_order = net.schedule(), bad.schedule()
    require(order == graph["schedule"] and set(bad_order) == set(order)
            and len(order) == 7643 and len(moves) == 6142 and net.moves == bad.moves,
            "both graphs remain legal at the same paid invoice")
    old, new = column(net, order, owner), column(bad, bad_order, owner)
    expected, corrupt = old.get(101174, 0), new.get(101174, 0)
    difference = corrupt - expected
    require(difference == -coefficient * old.get(97471, 0) and difference,
            "missing incidence must change the exposed row")
    return {"source_slot": 97471, "exposed_slot": 101174, "helper_column": owner,
            "removed_coefficient": str(coefficient), "paid_slots": len(moves), "scheduled_nodes": len(order),
            "physical_route": [912, 148], "source_column_coefficient": str(old.get(97471, 0)),
            "correct_exposed_value": str(expected), "corrupted_exposed_value": str(corrupt),
            "corrupted_minus_correct": str(difference), "expected_exposed_change_reproduced": difference == Fraction(1, 12)}



def execute(package, candidate):
    peer = package / "peer"
    contacts = package / "data/CONTACTS.json"
    receipt = package / "evidence/WIRE-RESULT.json"
    driver_path = package / "engines/graph.py"
    driver = graph_driver(driver_path)
    gauge = gauge_control(driver, peer, contacts)
    omission = omitted_read_control(driver, peer, candidate, receipt)
    result = {"status": "PASS_SAVED_WITNESS_CONTROLS", "candidate": CHILD,
              "graph_driver_sha256": DRIVER, "fixed_pivots_sha256": driver.PINS["PIVOTS.json"],
              "banked_wire_receipt_sha256": RECEIPT, "endpoint_preserving_gauge": gauge,
              "omitted_c_reader_incidence": omission}
    require(result == json.loads(pinned(HERE / "EXPECTED.json", EXPECTED)),
            "all controls reproduce the exact guarded readback")
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=HERE.parent)
    parser.add_argument("--candidate", type=Path, help="use the rebuilt candidate from a retained exact core run")
    parser.add_argument("--out", required=True, type=Path, help="fresh JSON result path")
    args = parser.parse_args()
    require(sys.version_info[:2] == (3, 12) and sys.flags.isolated and sys.dont_write_bytecode and __debug__,
            "use Linux Python 3.12 -I -B with assertions")
    output = args.out.resolve()
    require(not output.exists(), "fresh result file")
    package = args.package.resolve()
    cap = 2 * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

    def timed_out(_signum, _frame):
        raise TimeoutError("saved-witness replay exceeded its 75-second inner wall limit")

    signal.signal(signal.SIGALRM, timed_out)
    signal.alarm(75)
    try:
        with TemporaryDirectory(prefix="banked-witness-") as scratch:
            work = Path(scratch)
            sys.pycache_prefix = str(work / "fresh-bytecode")
            if args.candidate is not None:
                result = execute(package, args.candidate.resolve())
            else:
                graph_out = work / "graphs"
                driver = package / "engines/graph.py"
                pinned(driver, DRIVER)
                subprocess.run([sys.executable, "-I", "-B", "-X", f"pycache_prefix={work / 'fresh-bytecode'}",
                                str(driver), "--peer-package", str(package / "peer"),
                                "--contacts-file", str(package / "data/CONTACTS.json"),
                                "--materialize-only", str(package / "evidence/WIRE-RESULT.json"),
                                "--out", str(graph_out)], check=True, timeout=60)
                result = execute(package, graph_out / "CANDIDATE-GRAPH.json.gz")
            with output.open("x", encoding="utf-8") as stream:
                json.dump(result, stream, indent=2, sort_keys=True)
                stream.write("\n")
    finally:
        signal.alarm(0)
    print(result["status"], sha(output.read_bytes()), flush=True)


if __name__ == "__main__":
    main()
