#!/usr/bin/env python3
"""Exact finite K-triangle relocation census. Apache-2.0.

Charles Bethin, with substantial OpenAI Codex assistance.
Python 3.11+, standard library only. No supplier verifier is imported.
"""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = ROOT / "research/complex-k492-owner-repair"
SEED = 27


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


@lru_cache(None)
def basis(vectors):
    """Binary row elimination, with canonical reduced pivots."""
    rows = {}
    for x in vectors:
        for pivot in sorted(rows, reverse=True):
            if (x >> pivot) & 1:
                x ^= rows[pivot]
        if x:
            pivot = x.bit_length() - 1
            for other in rows:
                if (rows[other] >> pivot) & 1:
                    rows[other] ^= x
            rows[pivot] = x
    return tuple(rows[p] for p in sorted(rows, reverse=True))


@lru_cache(None)
def span(vectors):
    """Second representation: enumerate the vectors, without elimination."""
    values = {0}
    for x in vectors:
        values |= {x ^ y for y in values}
    return frozenset(values)


@lru_cache(None)
def span_join(left, right):
    return frozenset(x ^ y for x in left for y in right)


class Frames:
    def __init__(self, mode):
        self.mode = mode

    def of(self, vectors):
        return basis(tuple(vectors)) if self.mode == "basis" else span(tuple(vectors))

    def join(self, left, right):
        if self.mode == "basis":
            return basis(tuple(sorted(set(left + right))))
        return span_join(left, right)

    def dimension(self, value):
        return len(value) if self.mode == "basis" else len(value).bit_length() - 1

    def inside(self, left, right):
        return self.join(left, right) == right if self.mode == "basis" else left <= right

    def vectors(self, value):
        return span(value) if self.mode == "basis" else value


def caps_of(word, engine):
    return [engine.of(tuple(x for x in range(512) if not (x & p).bit_count() % 2))
            for p in word["ports"]]


def replay(events, start, caps, engine, adaptive=False, check_caps=True):
    current, paid, emitted = list(start), Counter(), []
    for index, event in enumerate(events):
        registers = event[1:3] if event[0] == "add" else event[1:2]
        frame = (engine.join(current[registers[0]], current[registers[1]])
                 if adaptive else engine.of(event[-1]))
        for register in registers:
            require(engine.inside(current[register], frame), "non-monotone fixed frame")
            if check_caps and 112 <= register < 224 and not engine.inside(frame, caps[register - 112]):
                witness = min(engine.vectors(frame) - engine.vectors(caps[register - 112]))
                return {"status": "frame_illegal", "step": index,
                        "register": register, "outside_vector": witness}
            difference = engine.dimension(frame) - engine.dimension(current[register])
            if difference:
                paid[difference] += 1
            current[register] = frame
        emitted.append(event[:-1] + [list(basis(tuple(engine.vectors(frame))))])
    return {"status": "legal", "frames": current, "profile": paid, "events": emitted}


def scalar_map(events, registers):
    """Exact arbitrary-input map on the twelve touched registers."""
    rows = {r: {r: Fraction(1)} for r in registers}
    for event in events:
        require(event[0] == "add", "window must contain only additions")
        _, target, source, numerator, denominator, _ = event
        q = Fraction(numerator, denominator)
        for column, value in list(rows[source].items()):
            result = rows[target].get(column, Fraction(0)) + q * value
            if result:
                rows[target][column] = result
            else:
                rows[target].pop(column, None)
    return rows


def orders_of(size):
    """Delete at i, insert at final zero-based position j; deduplicate."""
    orders = {}
    for i in range(size):
        for j in range(size):
            if i != j:
                order = list(range(size))
                order.insert(j, order.pop(i))
                orders.setdefault(tuple(order), [i, j])
    return orders


def initial(word, engine):
    return ([engine.of([p]) for p in word["ports"]]
            + [engine.of([])] * (112 + word["report"]["R"]))


def full_profile(word, engine):
    caps = caps_of(word, engine)
    result = replay(word["A"] + word["B"], initial(word, engine), caps, engine)
    require(result["status"] == "legal", "raw word fails frame replay")
    paid, current = result["profile"], result["frames"]
    # The eight centre scatters descend from rank eight to the target's zero frame.
    require(len(word["centers"]) == 8, "unexpected centre geometry")
    for frame in word["center_frames"]:
        paid[engine.dimension(engine.of(frame))] += 1
    full = engine.of([1 << i for i in range(9)])
    for register, old in enumerate(current):
        terminal = caps[register - 112] if 112 <= register < 224 else full
        require(engine.inside(old, terminal), "invalid terminal climb")
        difference = engine.dimension(terminal) - engine.dimension(old)
        if difference:
            paid[difference] += 1
    return paid


def run(word):
    triangle = SEED % 4
    schedule = json.loads((PACKAGE / "data/TRI-SCHEDULE.json").read_text())
    selected = schedule["triangles"][triangle]
    require(selected["p"] == [6, 7] and selected["e"] == -1, "wrong selected triangle")
    targets = {112 + read[0] for read in selected["reads"]}
    positions = [i for i, event in enumerate(word["B"]) if event[1] in targets][:30]
    require(positions == list(range(178, 208)), "unexpected raw window location")
    window = word["B"][178:208]
    require([e[1] - 112 for e in window] == [r[0] for r in selected["reads"]], "schedule binding")
    sources = {e[2] for e in window}
    require(len(sources) == len(targets) == 6 and not sources & targets, "window is not commuting reads")
    registers = sorted(sources | targets)
    scalar = scalar_map(window, registers)
    orders = orders_of(30)
    require(len(orders) == 841, "incomplete relocation domain")
    engine_data = []
    for mode in ("basis", "span"):
        engine = Frames(mode)
        caps = caps_of(word, engine)
        prefix = replay(word["A"] + word["B"][:178], initial(word, engine), caps, engine)
        require(prefix["status"] == "legal", "bad prefix")
        start = prefix["frames"]
        baseline = replay(window, start, caps, engine)
        minimal = replay(window, start, caps, engine, adaptive=True)
        require(minimal == baseline, "baseline does not use minimal joins")
        rows = []
        for order, move in sorted(orders.items()):
            candidate = [window[i] for i in order]
            result = replay(candidate, start, caps, engine, adaptive=True)
            record = {"move": move, "order": list(order), "status": result["status"]}
            if result["status"] != "legal":
                record.update({k: result[k] for k in ("step", "register", "outside_vector")})
                require((word["ports"][result["register"] - 112] & result["outside_vector"]).bit_count() % 2 == 1,
                        "rejection witness does not violate the target hyperplane")
            else:
                require(scalar_map(candidate, registers) == scalar, "changed arbitrary-input scalar map")
                record["status"] = ("same_endpoints" if result["frames"] == baseline["frames"]
                                    else "changed_terminal_frames")
                record["profile"] = dict(sorted(result["profile"].items()))
            rows.append(record)
        full = full_profile(word, engine)
        require(full == Counter({int(k): v for k, v in word["report"]["local_profile"].items()}),
                "complete raw profile mismatch")
        engine_data.append((rows, full))
    require(engine_data[0] == engine_data[1], "independent frame representations disagree")
    rows, full = engine_data[0]
    counts = Counter(row["status"] for row in rows)
    profiles = Counter(encode(row["profile"]).decode() for row in rows if "profile" in row)

    # Controls target actual failure modes, including costs the tempting screen omits.
    engine = Frames("basis")
    caps = caps_of(word, engine)
    start = replay(word["A"] + word["B"][:178], initial(word, engine), caps, engine)["frames"]
    baseline = replay(window, start, caps, engine)
    wrong = [list(e) for e in window]
    wrong[0][3] *= 2
    require(scalar_map(wrong, registers) != scalar, "coefficient mutation escaped")
    require(scalar_map(window[:-1], registers) != scalar, "missing read escaped")
    require(scalar_map(window[:-1] + [window[0]], registers) != scalar, "duplicate read escaped")
    bad = next(row for row in rows if row["status"] == "frame_illegal")
    bad_events = [window[i] for i in bad["order"]]
    require(replay(bad_events, start, caps, engine, adaptive=True)["status"] == "frame_illegal",
            "illegal relocation escaped")
    require(replay(bad_events, start, caps, engine, adaptive=True, check_caps=False)["status"] == "legal",
            "cap control is not sensitive to the cap check")
    source_mass = sum(engine.dimension(baseline["frames"][s]) - engine.dimension(start[s]) for s in sources)
    require(source_mass == 24, "unexpected source climb mass")
    require(sum(r * c for r, c in baseline["profile"].items()) - source_mass == 36,
            "target-only accounting control")
    controls = ["doubled_coefficient", "missing_read", "duplicate_read", "illegal_relocation",
                "disabled_cap_check_exposes_illegal_schedule", "omitted_source_climbs_undercharge_by_24"]
    require(counts == {"frame_illegal": 708, "same_endpoints": 133}, "unexpected census")
    require(profiles == {encode({1: 48, 2: 6}).decode(): 133}, "unexpected paid profile")
    return {"schema": "k-triangle-single-relocation-v1", "seed": SEED, "triangle": [6, 7],
            "sign": -1, "B_window": [178, 208], "raw_word_content_sha256": digest(word),
            "counts": dict(counts), "baseline_window_profile": {1: 48, 2: 6},
            "raw_full_profile": dict(sorted(full.items())), "raw_rank_mass": sum(r * c for r, c in full.items()),
            "scalar_columns_checked_per_legal_order": 12,
            "other_registers_untouched_by_window": 704,
            "controls": controls, "engines": ["binary_elimination", "explicit_vector_sets"], "cases": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a newly computed certificate instead of comparing EXPECTED.json")
    args = parser.parse_args()
    require(sys.version_info >= (3, 11), "Python 3.11 or later required")
    require(sys.flags.optimize == 0, "run without -O; the pinned constructor requires assertions")
    manifest = json.loads((HERE / "SOURCE.json").read_text())
    for name, expected in manifest["files"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, "source pin failed: " + name)
    with tempfile.TemporaryDirectory(prefix="k-triangle-relocation-") as directory:
        output = Path(directory) / "raw"
        process = subprocess.run([sys.executable, "-I", "-B", str(PACKAGE / "code/construct_k_triangle.py"),
                                  str(PACKAGE / "vendor/direct_delivery/inputs/hamming"), str(output),
                                  str(PACKAGE / "data/TRI-SCHEDULE.json")], capture_output=True, text=True)
        require(process.returncode == 0, "pinned constructor failed:\n" + process.stderr)
        word = json.loads(gzip.decompress((output / "FULL-WORD.json.gz").read_bytes()))
        result = run(word)
    if args.write:
        require(not args.write.exists(), "refuse to overwrite an existing certificate")
        # One case per line keeps the exhaustive certificate small and diffable.
        cases = result.pop("cases")
        header = json.dumps(result, indent=2, sort_keys=True).rstrip()[:-1]
        args.write.write_text(header + ',\n  "cases": [\n'
                              + ",\n".join("    " + json.dumps(case, sort_keys=True) for case in cases)
                              + "\n  ]\n}\n")
    else:
        require(encode(result) == encode(json.loads((HERE / "EXPECTED.json").read_text())), "certificate mismatch")
    print("PASS: 841 distinct relocations; 708 illegal; 133 unchanged profiles; two exact engines; six controls.")


if __name__ == "__main__":
    main()
