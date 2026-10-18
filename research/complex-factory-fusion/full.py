"""Bind the factory circuit to the complete raw PR622 program.

Prepared for Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. The PR681 extraction and native checks retain their source notices.
"""
import copy
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

from circuit import need, variants, reference
from comparator import cache_word

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ("W", 0)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def write(path, value):
    data = canonical(value)
    path.write_bytes(gzip.compress(data, mtime=0) if path.suffix == ".gz" else data + b"\n")


def build(out, word):
    prior = load_module("factory681", ROOT / "research/complex-factory5-resynthesis/verify.py")
    folder = ROOT / "research/complex-factory5-resynthesis"
    prior.run(folder / "extract.py", [out / "original"], out / "constructor.log")
    windows = read(out / "original/WINDOWS.json")
    blocks, original = read(folder / "BLOCKS.json"), read(folder / "CIRCUIT.json")
    prior.bind_blocks(blocks, windows, original)
    raw = read(out / "original/FULL-WORD.json.gz")
    changed = copy.deepcopy(raw)
    for block in reversed(blocks):
        registers = [r - 16 if r >= 240 else r - 8
                     for r in block["registers_before_112_port_restriction"]]
        new = copy.deepcopy(word)
        for op in new:
            op[1] = registers[op[1]]
            if op[0] == "add":
                op[2] = registers[op[2]]
            op[-1] = block["frame"]
        begin, end = block["A_window_zero_based"]
        changed["A"][begin:end] = new
    changed["cleanup"] = prior.inverse([e for e in changed["A"] + changed["B"]
                                       if not 112 <= e[1] < 224])
    for op in changed["cleanup"]:
        op[-1] = [256, 128, 64, 32, 16, 8, 4, 2, 1]
    raw_path = out / "COMBINED-RAW.json.gz"
    write(raw_path, changed)
    local = out / "local"
    receipt, native = prior.native(raw_path, local, out)
    programs = read(local / "LOCAL-PROGRAMS.json.gz")
    # The native transport keeps helper identifiers and permutes the data ports.
    mapping = {}
    for old, new in zip(changed["A"] + changed["B"], native["A"] + native["B"]):
        for index in (1, 2) if old[0] == "add" else (1,):
            key, value = old[index], new[index]
            need(key not in mapping or mapping[key] == value, "inconsistent native transport")
            mapping[key] = value
    bindings = []
    for block in blocks:
        raw_registers = [r - 16 if r >= 240 else r - 8
                         for r in block["registers_before_112_port_restriction"]]
        registers = [mapping[r] for r in raw_registers]
        bindings.append({"block": block["index"], "registers": registers})
    need(native["R"] == 492 and not any(native["start"][224:]), "unexpected helper contract")
    return native, programs, bindings, receipt


def scalar_pattern(word, registers):
    result = []
    for op in word:
        if op[0] == "add":
            result.append(["add", ["L", registers[op[1]]], ["L", registers[op[2]]],
                           op[3], op[4]])
        else:
            result.append(["scale", ["L", registers[op[1]]], op[2], op[3]])
    return result


def locate(events, word, bindings, orientation):
    """Identify every complete block from its exact ordered scalar operators."""
    scalar = [(i, event) for i, event in enumerate(events) if event[0] == "scalar"]
    candidates = variants(word)
    found = []
    for binding in bindings:
        registers = binding["registers"]
        for suffix in ("main", "cleanup"):
            name = ("dual_" if orientation == "backward" else "") + suffix
            pattern = scalar_pattern(candidates[name], registers)
            matches = [j for j in range(len(scalar) - len(pattern) + 1)
                       if scalar[j][1][1] == pattern[0]
                       and [e[1] for _, e in scalar[j:j + len(pattern)]] == pattern]
            need(len(matches) == 1, "factory occurrence is not unique")
            j = matches[0]
            begin, end = scalar[j][0], scalar[j + len(pattern) - 1][0] + 1
            # Include the climbs immediately before the first scalar operator.
            while begin and events[begin - 1][0] == "climb":
                begin -= 1
            frame = scalar[j][1][2]
            seen, climbs = set(), []
            for event in events[begin:end]:
                if event[0] == "climb":
                    need(event[2] in registers and event[2] not in seen
                         and event[4] == frame, "climb cannot move to the block entry")
                    climbs.append(event)
                else:
                    need(event[0] == "scalar" and event[2] == frame,
                         "opaque event or frame change inside a factory block")
                    op = event[1]
                    operands = op[1:3] if op[0] == "add" else op[1:2]
                    seen.update(r[1] for r in operands)
            need(seen == set(registers), "incomplete factory register support")
            found.append({"begin": begin, "end": end, "frame": frame, "name": name,
                          "registers": registers, "climbs": climbs, "block": binding["block"]})
    found.sort(key=lambda x: x["begin"])
    need(len(found) == 28 and all(a["end"] <= b["begin"] for a, b in zip(found, found[1:])),
         "factory coverage or overlap")
    return found


def lower_program(events, windows, word, candidate, mode):
    original_lower = load_module("factory696", ROOT / "research/complex-dyadic-lowering/lower.py").lower
    accumulated_lower = load_module("factory999", HERE / "sources/pr999-lower.py").lower
    def lower(op):
        if mode == "pr696":
            return original_lower(op)
        part = accumulated_lower(op)[1]
        if mode in ("strong", "candidate") and op[0] == "add":
            q = Q(op[3], op[4])
            if q.denominator == 1 and abs(q.numerator) + 1 < len(part):
                add = "add" if q > 0 else "subtract"
                part = [(add, tuple(op[1]), tuple(op[2]))] * abs(q.numerator)
                part.append(("clear", WORK))
        return part
    scalar_words, primitive_words = variants(word), variants(candidate, True)
    by_start = {w["begin"]: w for w in windows}
    result, index = [], 0
    while index < len(events):
        window = by_start.get(index)
        if window and mode != "accumulated":
            name, frame, registers = window["name"], window["frame"], window["registers"]
            result.extend(copy.deepcopy(window["climbs"]))
            if mode == "candidate":
                circuit = primitive_words[name] + [["clear", 8]]
            elif mode == "strong":
                circuit = cache_word(scalar_words[name])
            else:
                circuit = reference(scalar_words[name], reuse=(mode == "cache"))
            for op in circuit:
                args = [WORK if r == 8 else ("L", registers[r]) for r in op[1:]]
                result.append(["primitive", [op[0], *args], frame])
            index = window["end"]
        else:
            event = events[index]
            if event[0] == "scalar":
                for primitive in lower(event[1]):
                    result.append(["primitive", list(primitive), event[2]])
            else:
                result.append(copy.deepcopy(event))
            index += 1
    need([e for e in result if e[0] != "primitive"] ==
         [e for e in events if e[0] != "scalar"], "non-scalar event inventory changed")
    return result


def replay(events, native, orientation):
    """Replay every input column on an exact integer dyadic grid."""
    n, centers, grid_bits = 716, 8, 256
    grid = 1 << grid_bits
    registers = [("L", r) for r in range(n)] + [("C", r) for r in range(centers)] + [WORK]
    rows = {r: {j: grid} for j, r in enumerate(registers)}
    envelope = {r: grid for r in registers}
    current = native["start"].copy()
    center_frames = {}
    paid, counts = Counter(), Counter()
    exact_peak, positive_peak, depth, reads = grid, grid, 0, 0
    for event in events:
        tag = event[0]
        if tag == "climb":
            _, _, register, old, new, rank = event
            need(current[register] == old, "wrong climb source frame")
            need(rank == len(native["frames"][new]) - len(native["frames"][old]), "wrong climb rank")
            current[register] = new
            paid[rank] += 1
        elif tag == "center":
            _, register, old, new, rank = event
            need(center_frames[register] == old, "wrong center source frame")
            center_frames[register] = new
            paid[rank] += 1
        elif tag == "primitive":
            op, frame = event[1:]
            name, target = op[0], tuple(op[1])
            operands = [tuple(r) for r in op[1:]]
            for register in operands:
                if register[0] == "L":
                    need(current[register[1]] == frame, "primitive outside its live common frame")
                elif register[0] == "C":
                    if name == "clear" and register == target:
                        center_frames[register[1]] = frame
                    need(center_frames.get(register[1]) == frame, "wrong private center frame")
                else:
                    need(register == WORK, "unknown private register")
            row = rows[target]
            if name == "clear":
                rows[target], envelope[target] = {}, 0
            elif name == "copy":
                source = tuple(op[2])
                rows[target], envelope[target] = rows[source].copy(), envelope[source]
            elif name in ("double", "halve", "negate"):
                if name == "halve":
                    need(all(value % 2 == 0 for value in row.values())
                         and envelope[target] % 2 == 0, "inexact integer-grid halving")
                    rows[target] = {j: value // 2 for j, value in row.items()}
                    envelope[target] //= 2
                else:
                    factor = 2 if name == "double" else -1
                    rows[target] = {j: factor * value for j, value in row.items()}
                    envelope[target] *= abs(factor)
            else:
                need(name in ("add", "subtract") and target != tuple(op[2]), "invalid primitive")
                source = tuple(op[2])
                for j, value in list(rows[source].items()):
                    value = row.get(j, 0) + (value if name == "add" else -value)
                    if value:
                        row[j] = value
                    else:
                        row.pop(j, None)
                envelope[target] += envelope[source]
            counts[name] += 2
            reads += 2 * (2 if name in ("add", "subtract") else int(name != "clear"))
            exact_peak = max(exact_peak, sum(map(abs, rows[target].values())))
            positive_peak = max(positive_peak, envelope[target])
            for value in rows[target].values():
                depth = max(depth, grid_bits - ((abs(value) & -abs(value)).bit_length() - 1))
        else:
            need(tag in ("phase", "adapter", "residual_adapter"), "unknown opaque event")
    for r in range(n):
        expected = {r: grid}
        if orientation == "forward" and 112 <= r < 224:
            expected[r - 112] = grid
        elif orientation == "backward" and r < 112:
            expected[r + 112] = -grid
        need(rows["L", r] == expected, "whole-word shear or dirty restoration")
    need(all(not rows[r] for r in registers[n:]), "private input not erased")
    need(current == native["final"], "wrong final frame inventory")
    need(dict(paid) == {int(k): v for k, v in native["local_profile"].items()}, "paid child profile")
    return {"all_columns": len(registers), "restored_dirty_helpers": 492,
            "real_primitives": sum(counts.values()), "primitive_tags": dict(sorted(counts.items())),
            "operand_reads": reads, "exact_peak_row_l1": str(Q(exact_peak, grid)),
            "positive_peak": str(Q(positive_peak, grid)), "fractional_depth": max(depth, 0),
            "paid_profile": dict(sorted(paid.items())), "word_sha256": digest(events)}
