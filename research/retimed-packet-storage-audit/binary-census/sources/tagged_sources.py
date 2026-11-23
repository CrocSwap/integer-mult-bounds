"""Read the ordered 36-call and 48-call words from their authenticated source."""

import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

from powered import Port, bit_word, complex_word

NATIVE = "a7f99a5f5f919dd3ffb2987f90c1e7d6527feb1e"
BASE = "e54523517d0f03e58352e647c403a5af3e525a57"
ROOT = "research/grade14-native-realization/retained/"
PINS = {
    "data/complex.json.gz": "1b1b3294e86979f1f41076fb056f3c0a08ace6df7bf80f2886bc579a22962f4b",
    "data/binary.json.gz": "d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9",
    "data/layout.json.gz": "b0f3ebc5710e469f3e8fc5ce159cbba048b563944182b50993431ef94f4fedbf",
    "data/CALLER.json.gz": "d889996a337f648087208ab51c98eaf052705d4fca88b5d01b6e9257a829897a",
    "data/CONJUGATE-CALLER.json.gz": "80009663da460229a57f09bde90e35294329a210ae7fc7ef6d1f05b61ffccbf4",
    "closed_caller.py": "b82b9710d85d62e0f98aa1a1d7c70f97bdbdd64a6e4c92406019ca580a8c52ce",
    "mixed_caller.py": "4824b2aaadb592550d3a25c16ff0a453705e10b8868f5c22fe10c2874bcb9bae",
}
BIT_CALLER = "research/paired-query-only-bit/EFREE-CALLER.json.gz"
BIT_PIN = "757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b"


def pinned(name, digest):
    path = Path(__file__).resolve().parent / "vendor" / Path(name).name
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError(f"Wrong source bytes at {name}")
    return data


def packed(buffer):
    return json.loads(gzip.decompress(buffer))


def binary_ports(graph, caller):
    starts, ends, frames = graph["start"], graph["final"], graph["frames"]
    dims = {int(k): f["dim"] for k, f in frames.items()}
    ports = caller["ports"]
    paid, targets = [], []
    for i, entry in enumerate(caller["diagonal"]):
        for p in range(ports):
            targets.append(Port(("root", i, p), 1 + 7 * len(entry["stages"])))
    moves = [(k, row[1], abs(dims[row[2]] - dims[row[3]]))
             for k, row in enumerate(graph["program"]) if row[0] == "MOVE"]
    for clock, event in enumerate(caller["events"]):
        if event[0] == "LOCAL":
            for i in range(2 * ports, len(starts)):
                targets.append(Port(("helper", clock, i), abs(dims[ends[i]] - dims[starts[i]])))
            for site, bank, rank in moves:
                paid.append(Port(("move", clock, site, bank), rank))
        elif event[0] in ("QUERY", "IDLE_ONE"):
            rank = 1 if event[0] == "QUERY" else 7 * len(event[2])
            for p in range(ports):
                paid.append(Port((event[0], clock, p), rank))
    return bit_word(targets, paid)


def import_file(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def complex_ports(graph, layout, caller, programs):
    with TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "data").mkdir()
        for name, data in programs.items():
            (root / name).write_bytes(data)
        mixed = import_file(root / "mixed_caller.py", "mixed_caller")
        old = sys.modules.get("mixed_caller")
        sys.modules["mixed_caller"] = mixed
        try:
            closed = import_file(root / "closed_caller.py", "closed_caller")
        finally:
            if old is None:
                del sys.modules["mixed_caller"]
            else:
                sys.modules["mixed_caller"] = old
        words, roots = closed.templates(caller), closed.placement(caller)
        binds, offsets, _ = mixed.layout_bindings(words, roots, layout, 48)
        dims = tuple(map(len, graph["frames"]))
        main = (set(layout["live"]) | {i + 112 for i in layout["live"]}
                | set(layout["hosted"]["X2"]) | set(layout["hosted"]["Y2"]))
        moves = {row: (a, b) for row, a, b in graph["moves"]}
        targets, paid = [], []
        for (kind, root_id), visits in roots.items():
            for i, (sign, entries) in enumerate(words[kind][1]):
                owner = offsets[kind, root_id] + i
                targets.append(Port(("root", kind, root_id, owner, sign), 1 + 8 * len(entries)))
        for clock, row in enumerate(mixed.instructions(words, roots, binds, offsets)):
            op = row[0]
            if op == "NATIVE":
                call = row[1]
                for i, (a, b) in enumerate(zip(graph["initial"], graph["final"], strict=True)):
                    if i not in main:
                        targets.append(Port(("helper", clock, call, layout["source_labels"][i]), dims[b] - dims[a]))
                for node in graph["schedule"]:
                    if node in moves:
                        a, b = moves[node]
                        paid.append(Port(("return", clock, call, node), abs(dims[b] - dims[a])))
            elif op == "QUERY" or op.startswith("IDLE_"):
                rank = 1 if op == "QUERY" else 8 * len(row[2]) + int(op == "IDLE_ODD")
                paid.append(Port((op, clock, row[1]), rank))
    return complex_word(targets, paid)


def read_words():
    sources = {name: pinned(name,digest) for name,digest in PINS.items()}
    bit_caller = packed(pinned(BIT_CALLER,BIT_PIN))
    bit = binary_ports(packed(sources["data/binary.json.gz"]), bit_caller)
    programs = {name: sources[name] for name in
                ("mixed_caller.py", "closed_caller.py", "data/CONJUGATE-CALLER.json.gz")}
    comp = complex_ports(packed(sources["data/complex.json.gz"]), packed(sources["data/layout.json.gz"]),
                         packed(sources["data/CALLER.json.gz"]), programs)
    return bit, comp
