"""Exact replay of one R420 block replacement. Python standard library only.

Jerry Lin, with substantial OpenAI Codex assistance; Apache-2.0.
The search is not imported. The original R420 checker is used separately for
the exact E8 geometry and its original H1-H5 interface.
"""
import argparse
import copy
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import struct
import sys
from collections import Counter

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
CHECKER = ROOT / "research/e8-bit-r420/code/xcheck.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def matrix(operations, n=12):
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    for dst, src in operations:
        rows[dst] = [a + b for a, b in zip(rows[dst], rows[src])]
    return rows


def dominated(smaller, larger):
    return all(a <= b for x, y in zip(smaller, larger) for a, b in zip(x, y))


def extract(word):
    blocks = []
    for frame, items in itertools.groupby(enumerate(word["B"]), lambda x: x[1][0]):
        items = list(items)
        if len(word["frames"][frame]) == 12:
            blocks.append((frame, items))
    require(len(blocks) == 10, "source block count")
    frame, items = blocks[8]
    start, end = items[0][0], items[-1][0] + 1
    registers = sorted({r for _, (_, dst, srcs) in items for r in [dst] + srcs})
    require((frame, start, end) == (550, 512, 559), "source block location")
    require(len(registers) == 12 and all(r < word["v"] for r in registers), "source block wires")
    require(all(len(g[2]) == 1 for _, g in items), "source block is not unary")
    index = {r: i for i, r in enumerate(registers)}
    operations = [[index[g[1]], index[g[2][0]]] for _, g in items]
    return frame, start, end, registers, operations


def certify_block(word, recipe):
    frame, start, end, registers, old = extract(word)
    require(type(recipe["block_index"]) is int and recipe["block_index"] == 8, "block index")
    require(recipe["frame"] == frame and recipe["b_slice"] == [start, end], "block binding")
    require(recipe["registers"] == registers, "ordered register binding")
    operations = recipe["operations"]
    require(isinstance(operations, list) and 0 < len(operations) < len(old), "strict primitive saving")
    for pair in operations:
        require(isinstance(pair, list) and len(pair) == 2, "gate shape")
        require(all(type(x) is int and 0 <= x < 12 for x in pair), "gate wire")
        require(pair[0] != pair[1], "self addition")
    forward = matrix(operations)
    old_reverse, new_reverse = matrix(reversed(old)), matrix(reversed(operations))
    require(forward == matrix(old), "integer forward map")
    require(dominated(new_reverse, old_reverse), "positive reverse domination")
    return dict(old_gates=len(old), new_gates=len(operations), forward_matrix=forward,
                old_positive_reverse=old_reverse, new_positive_reverse=new_reverse,
                strict_reverse_entries=sum(a < b for x, y in zip(new_reverse, old_reverse)
                                           for a, b in zip(x, y)))


def replace(word, recipe):
    frame, start, end, registers, _ = extract(word)
    result = copy.deepcopy(word)
    result["B"][start:end] = [[frame, registers[d], [registers[s]]] for d, s in recipe["operations"]]
    full = next(i for i, f in enumerate(word["frames"]) if len(f) == 120)
    v = word["v"]
    result["C"] = [[full, d, list(ss)] for _, d, ss in reversed(result["A"] + result["B"])
                   if not v <= d < 2 * v]
    return result


def rank(lines):
    basis = {}
    for row in lines:
        row = list(map(Fraction, row))
        for p, old in sorted(basis.items()):
            c = row[p]
            row = [a - c * b for a, b in zip(row, old)]
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is not None:
            scale = row[pivot]
            basis[pivot] = [x / scale for x in row]
    return len(basis)


def records(word, dimensions):
    """Build the primitive stream independently of the predecessor exporter."""
    v, n = word["v"], 2 * word["v"] + word["R"]
    current = list(word["start"])
    events = []
    paths = [[f] for f in current]

    def move(r, frame):
        if current[r] != frame:
            old = current[r]
            require(set(word["frames"][old]) <= set(word["frames"][frame]), "frame nesting")
            require(dimensions[old] < dimensions[frame], "strict frame growth")
            events.append((0, r, old, frame, dimensions[frame] - dimensions[old], 0))
            paths[r].append(frame)
            current[r] = frame

    def gates(section, phase):
        for frame, dst, srcs in word[section]:
            require(len({dst, *srcs}) == 1 + len(srcs), "duplicate gate operand")
            for r in [dst] + srcs:
                move(r, frame)
            events.extend((1, dst, src, 1, frame, phase) for src in srcs)

    gates("D", 1)
    gates("A", 2)
    for k, center in enumerate(word["ret"]):
        frame = current[center]
        events.append((2, center, n, frame, 0, dimensions[frame]))
        events.extend((1, v + t, n, 1, 0, 3) for t, row in enumerate(word["scatter"]) if k in row)
        events.append((3, center, n, frame, 0, 0))
    gates("B", 4)
    gates("C", 5)
    for r, f in enumerate(word["final"]):
        move(r, f)
    return events, paths


def replay(word, events, reverse=False, positive=False):
    v, n = word["v"], 2 * word["v"] + word["R"]
    values = [1] * (n + 1) if positive else [1 << r for r in range(n)] + [0]
    maximum, opened = 1, None
    for op, a, b, _, _, _ in reversed(events) if reverse else events:
        if op == 0:
            continue
        if reverse and op in (2, 3):
            op = 5 - op
        if op == 1:
            require(a != n and (b != n or opened is not None), "copy lifecycle")
            require(a != opened, "copied source changed")
            values[a] = values[a] + values[b] if positive else values[a] ^ values[b]
            maximum = max(maximum, values[a]) if positive else maximum
        elif op == 2:
            require(opened is None and b == n, "copy opening")
            values[n], opened = values[a], a
        else:
            require(op == 3 and opened == a and b == n, "copy closing")
            values[n], opened = 0, None
    require(opened is None, "open copy at exit")
    if positive:
        return maximum
    expected = [1 << r for r in range(n)] + [0]
    for t in range(v):
        expected[v + t] ^= 1 << t
    require(values == expected, "all-column endpoint")
    return n


def word_summary(word, dimensions):
    events, paths = records(word, dimensions)
    for reverse in (False, True):
        replay(word, events, reverse)
    forward = replay(word, events, positive=True)
    backward = replay(word, events, reverse=True, positive=True)
    histogram = Counter(e[4] for e in events if e[0] == 0)
    histogram.update(e[5] for e in events if e[0] == 2)
    payload = 64 * forward ** 3 * backward ** 2
    require(payload < 2 ** 104, "local payload cap")
    return dict(columns=2 * word["v"] + word["R"], scalar_additions=sum(e[0] == 1 for e in events),
                record_sha256=sha(b"".join(struct.pack("<6i", *event) for event in events)),
                copies=sum(e[0] == 2 for e in events), erasures=sum(e[0] == 3 for e in events),
                forward_positive_prefix=forward, reverse_positive_prefix=backward,
                five_stage_payload_bits=payload.bit_length(), five_stage_payload=str(payload),
                paid_histogram={str(k): v for k, v in sorted(histogram.items())},
                rank_mass=sum(k * v for k, v in histogram.items()), paths_sha256=sha(canonical(paths))), events, paths


def source_check():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for required in (SOURCE, CHECKER):
        path = required.relative_to(ROOT).as_posix()
        require(path in pins["files"], "missing source pin: " + path)
    for path, digest in pins["files"].items():
        require(sha((ROOT / path).read_bytes()) == digest, "source hash: " + path)


def import_checker():
    spec = importlib.util.spec_from_file_location("r420_original_checker", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reject(action, reason):
    try:
        action()
    except ValueError as exc:
        require(reason in str(exc), "wrong negative-control reason: " + str(exc))
        return
    raise ValueError("negative control was accepted: " + reason)


def controls(word, recipe, candidate, dimensions, checker):
    results = []
    shorter, longer = [(1, 2), (0, 1)], [(0, 1), (0, 2), (1, 2)]
    require(matrix(shorter, 3) == matrix(longer, 3), "three-wire forward calibration")
    reject(lambda: require(dominated(matrix(reversed(longer), 3), matrix(reversed(shorter), 3)),
                           "positive reverse domination"), "positive reverse domination")
    results.append("equal_forward_does_not_imply_reverse_domination")
    for label, edit, reason in (
        ("drop_operation", lambda r: r["operations"].pop(0), "integer forward map"),
        ("self_addition", lambda r: r["operations"].__setitem__(0, [0, 0]), "self addition"),
        ("boolean_wire", lambda r: r["operations"][0].__setitem__(0, True), "gate wire"),
        ("wrong_frame", lambda r: r.__setitem__("frame", 549), "block binding"),
        ("swapped_register_binding", lambda r: r["registers"].reverse(), "ordered register binding"),
        ("unpriced_cancelled_pair", lambda r: r["operations"].extend([[0, 1], [0, 1]]), "integer forward map"),
    ):
        mutant = copy.deepcopy(recipe)
        edit(mutant)
        reject(lambda: certify_block(word, mutant), reason)
        results.append(label)
    mutant = copy.deepcopy(candidate)
    mutant["C"].pop(158)
    reject(lambda: word_summary(mutant, dimensions), "all-column endpoint")
    results.append("missing_cleanup")
    stale = copy.deepcopy(candidate)
    stale["C"] = copy.deepcopy(word["C"])
    word_summary(stale, dimensions)  # Both lists invert the same F2 map.
    require(not checker.Word(stale).interface()[0]["H4_C_literal_reverse_at_full"], "stale cleanup H4 control")
    results.append("stale_cleanup_passes_endpoint_but_fails_H4")
    mutant = copy.deepcopy(candidate)
    mutant["B"][512][0] = word["start"][mutant["B"][512][1]]
    reject(lambda: records(mutant, dimensions), "frame nesting")
    results.append("illegal_frame_descent")
    return results


def verify(output=None):
    source_check()
    word = json.loads(gzip.decompress(SOURCE.read_bytes()))
    recipe = json.loads((HERE / "CANDIDATE.json").read_text())
    block = certify_block(word, recipe)
    candidate = replace(word, recipe)
    dimensions = [rank([word["lines"][i] for i in frame]) for frame in word["frames"]]
    before, _, old_paths = word_summary(word, dimensions)
    after, _, new_paths = word_summary(candidate, dimensions)
    require(old_paths == new_paths, "changed frame paths")
    require(before["paid_histogram"] == after["paid_histogram"], "changed paid profile")
    require(before["scalar_additions"] - after["scalar_additions"] == 2 * (block["old_gates"] - block["new_gates"]),
            "complete primitive saving")
    require(after["forward_positive_prefix"] <= before["forward_positive_prefix"] and
            after["reverse_positive_prefix"] <= before["reverse_positive_prefix"], "complete positive prefixes")
    checker = import_checker()
    original_check = checker.check(word)
    require(original_check[0].fdim == dimensions, "independent frame ranks")
    require(all(original_check[3].values()) and all(original_check[4].values()), "original interface")
    changed = checker.Word(candidate)
    changed.full()
    hypotheses, conclusions, _ = changed.interface()
    require(all(hypotheses.values()) and all(conclusions.values()), "candidate interface")
    report = dict(block=block, original=before, candidate=after,
                  word_content_sha256=sha(canonical(candidate)),
                  controls=controls(word, recipe, candidate, dimensions, checker))
    expected = json.loads((HERE / "CERTIFICATE.json").read_text())
    require(report == expected, "certificate mismatch")
    if output:
        with gzip.GzipFile(filename=str(output), mode="wb", mtime=0) as stream:
            stream.write(canonical(candidate))
    print("PASS_R420_BLOCK8_SCHEDULE gates=%d->%d ADDs=%d->%d columns=660 controls=%d rank_mass=%d kappa=not_recomputed" %
          (block["old_gates"], block["new_gates"], before["scalar_additions"], after["scalar_additions"],
           len(report["controls"]), after["rank_mass"]))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-word", type=Path, help="Write the rebuilt word to a new file.")
    args = parser.parse_args()
    if args.output_word:
        require(not args.output_word.exists(), "output file already exists")
        require(HERE not in args.output_word.resolve().parents and SOURCE.parent not in args.output_word.resolve().parents,
                "output must be outside source packages")
    verify(args.output_word)
