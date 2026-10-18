# SPDX-License-Identifier: Apache-2.0
"""Source-bound staged-isolation obstruction. Adam Gall, with OpenAI assistance.

No predecessor executable is imported. Acceptance uses integers/Fractions only.
"""
import argparse
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import itertools
import json
from math import isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
WORD_SHA256 = "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f"
HELPER, TARGET, CUT = 465, 163, 10
STAGE = [(507, 465, 0), (507, 163, 465), (512, 381, 465), (512, 474, 465)]
CHAIN = [(48, 163, 48), (117, 48, 5), (493, 5, 243), (601, 243, 111)]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bits(value):
    while value:
        bit = value & -value
        yield bit.bit_length() - 1
        value ^= bit


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def authenticated_word(raw):
    require(hashlib.sha256(raw).hexdigest() == WORD_SHA256, "word source hash")
    return json.loads(gzip.decompress(raw))


def load(root=ROOT):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for item in manifest["files"]:
        if item["usage"] == "input":
            raw = (root / item["path"]).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == item["sha256"], "source hash: " + item["path"])
    return authenticated_word((root / WORD).read_bytes())


def basis(vectors):
    """Canonical rational RREF; dimension is eight, never reduced modulo two."""
    rows = [list(map(Fraction, row)) for row in vectors]
    pivot = 0
    for column in range(8):
        selected = next((i for i in range(pivot, len(rows)) if rows[i][column]), None)
        if selected is None:
            continue
        rows[pivot], rows[selected] = rows[selected], rows[pivot]
        divisor = rows[pivot][column]
        rows[pivot] = [value / divisor for value in rows[pivot]]
        for i, row in enumerate(rows):
            if i != pivot and row[column]:
                multiplier = row[column]
                rows[i] = [x - multiplier * y for x, y in zip(row, rows[pivot])]
        pivot += 1
        if pivot == 8:
            break
    return tuple(tuple(row) for row in rows[:pivot])


@lru_cache(maxsize=None)
def join(left, right):
    if left == right:
        return left
    return basis(left + right)


def contains(outer, inner):
    return join(outer, inner) == outer


def elementary(word, section, start=0):
    for index, (frame, target, donors) in enumerate(word[section]):
        if index < start:
            continue
        require(target not in donors and len(donors) == len(set(donors)), "non-transvection source record")
        for offset, source in enumerate(donors):
            yield (section, index, offset, frame, target, source)


def execute(rows, gates):
    result = rows[:]
    for gate in gates:
        target, source = gate[-2:]
        require(target != source, "self ADD")
        result[target] ^= result[source]
    return result


def expected_rows(word):
    v, n = word["v"], 2 * word["v"] + word["R"]
    return [(1 << r) ^ ((1 << (r - v)) if v <= r < 2 * v else 0) for r in range(n)]


def prefix(word, frame_bases, corrupt_copy=False):
    """Actual retained snapshot lifecycle; scalar flattening only after ERASE."""
    v, n = word["v"], 2 * word["v"] + word["R"]
    rows, frames = [1 << r for r in range(n)], word["start"][:]
    gates = []
    histogram = Counter()
    move_count = 0
    for section in ("D", "A"):
        for gate in elementary(word, section):
            _, _, _, f, t, s = gate
            for r in (t, s):
                require(contains(frame_bases[f], frame_bases[frames[r]]), "prefix monotonicity")
                if frames[r] != f:
                    increment = len(frame_bases[f]) - len(frame_bases[frames[r]])
                    require(increment > 0, "prefix zero-rank frame alias")
                    histogram[increment] += 1
                    move_count += 1
                    frames[r] = f
            rows[t] ^= rows[s]
            gates.append(gate)
    copy_ranks = [len(frame_bases[frames[r]]) for r in word["ret"]]
    histogram.update(copy_ranks)
    # Match the pinned exporter's retained-major chronology. The same temp661
    # is created, read and erased once per retained source, before the next COPY.
    live = {}
    for total, source in enumerate(word["ret"]):
        require(n not in live, "COPY over live temporary")
        live[n] = rows[source]
        for target, totals in enumerate(word["scatter"]):
            if total in totals:
                value = live[n] ^ ((1 << 0) if corrupt_copy and total == 0 else 0)
                rows[v + target] ^= value
                gates.append(("scatter", target, totals.index(total), 0, v + target, source))
        require(live.pop(n) == rows[source], "ERASE source changed")
    require(not live, "live copy at retirement cut")
    for gate in elementary(word, "B"):
        if gate[1] >= CUT:
            break
        _, _, _, f, t, s = gate
        for r in (t, s):
            require(contains(frame_bases[f], frame_bases[frames[r]]), "B-prefix monotonicity")
            if frames[r] != f:
                histogram[len(frame_bases[f]) - len(frame_bases[frames[r]])] += 1
                move_count += 1
                frames[r] = f
        rows[t] ^= rows[s]
        gates.append(gate)
    return rows, frames, gates, histogram, move_count, copy_ranks


def isolation_boundary(rows):
    return [(1 << HELPER) if r == HELPER else value ^ (((value >> HELPER) & 1) << HELPER)
            for r, value in enumerate(rows)]


def inlined_suffix(word):
    """Track the removed helper's non-dirty signal in current active coordinates.

    A ghost expression is an algebraic calculation, NOT a free physical role.
    Every actual donor read is emitted as one charged scalar ADD.
    """
    ghost = 1 << 0
    gates, dropped, inlined = [], [], []
    for section, start in (("B", CUT), ("C", 0)):
        for gate in elementary(word, section, start):
            _, index, offset, frame, target, source = gate
            if target == HELPER:
                ghost ^= 1 << source
                dropped.append(list(gate))
                continue
            donors = list(bits(ghost)) if source == HELPER else [source]
            require(target not in donors, "noninvertible ghost substitution")
            if source == HELPER:
                inlined.append({"section": section, "index": index, "donor_offset": offset,
                                "target": target, "donors": donors})
            for donor in donors:
                gates.append((section, index, offset, frame, target, donor))
                if ghost >> target & 1:
                    ghost ^= 1 << donor
    require(ghost == 0, "nonzero final ghost")
    return gates, dropped, inlined


def least_joins(word, frame_bases, initial, gates, caps=None):
    """All-rational monotone lower envelope, ignoring all old suffix gate frames."""
    current = initial[:]
    if caps is None:
        caps = [frame_bases[f] for f in word["final"]]
        caps[HELPER] = frame_bases[512]
    histogram = Counter()
    for ordinal, gate in enumerate(gates):
        section, index, offset, _, target, source = gate
        common = join(current[target], current[source])
        for r in (target, source):
            if current[r] != common:
                histogram[len(common) - len(current[r])] += 1
                current[r] = common
            if not contains(caps[r], common):
                return {"section": section, "index": index, "donor_offset": offset,
                        "ordinal": ordinal, "target": target, "source": source,
                        "failed_register": r, "required_rank": len(common),
                        "cap_rank": len(caps[r])}, current, histogram
    for r in range(len(current)):
        require(contains(caps[r], current[r]), "final closure incompatibility")
        if caps[r] != current[r]:
            histogram[len(caps[r]) - len(current[r])] += 1
            current[r] = caps[r]
    return None, current, histogram


def shortest_contact_path(gates, start, finish, last_index):
    paths = {start: []}
    for section, index, offset, _, t, s in gates:
        if section != "B" or index > last_index:
            break
        before_t, before_s = paths.get(t), paths.get(s)
        if before_t is not None and (before_s is None or len(before_t) + 1 < len(before_s)):
            paths[s] = before_t + [[index, offset, t, s]]
        if before_s is not None and (before_t is None or len(before_s) + 1 < len(before_t)):
            paths[t] = before_s + [[index, offset, s, t]]
    return paths.get(finish)


def check_chain(word, chain=CHAIN, normal=(1, 0, 0, 0, 0, 0, 0, 0)):
    position, previous = TARGET, CUT - 1
    for index, source, destination in chain:
        require(index > previous and source == position, "chain chronology/connectivity")
        _, target, donors = word["B"][index]
        require((target == source and destination in donors) or
                (target == destination and source in donors), "chain source contact")
        previous, position = index, destination
    require(position == 111, "chain terminal role")
    dot = lambda row: sum(a * b for a, b in zip(normal, row))
    require(any(dot(word["lines"][i]) for i in word["frames"][507]), "missing separating direction")
    require(all(dot(word["lines"][i]) == 0 for i in word["frames"][word["final"][111]]),
            "terminal normal does not annihilate cap")


def sqrt_interval(number, scale=10**40):
    lower = isqrt(number * scale * scale)
    upper = lower if lower * lower == number * scale * scale else lower + 1
    return Fraction(lower, scale), Fraction(upper, scale)


def budget():
    result = []
    for remainder in (2, 4, 6):
        delta = Counter({3: 1, 2: -1, 1: -2, 7: -1})
        delta[remainder + 8] += 1
        delta[remainder] -= 1
        require(sum(rank * count for rank, count in delta.items()) == 0, "optimistic rank conservation")
        require(sum(delta.values()) == -3, "optimistic child-count delta")
        low = high = Fraction(0)
        for rank, count in delta.items():
            left, right = sqrt_interval(rank)
            low += count * (left if count > 0 else right)
            high += count * (right if count > 0 else left)
        require(high < 0, "square-root moment control")
        result.append({"old_remainder": remainder, "histogram_delta": dict(sorted(delta.items())),
                       "rank_mass_delta": 0, "child_count_delta": -3,
                       "p_half_interval": [str(low), str(high)]})
    return result


def expect_failure(action, name):
    try:
        action()
    except ValueError:
        return name
    raise ValueError("control accepted: " + name)


def derive(word):
    v, n = word["v"], 2 * word["v"] + word["R"]
    require((v, n) == (111, 661), "source dimensions")
    fb = [basis([word["lines"][i] for i in frame]) for frame in word["frames"]]
    rows, frames, prefix_gates, prefix_hist, prefix_moves, copy_ranks = prefix(word, fb)
    require(rows[HELPER] == (1 << HELPER) ^ 1, "cut helper signal")
    dirt = [r for r, value in enumerate(rows) if value >> HELPER & 1]
    require(dirt == [163, 381, 465, 474], "cut dirty support")
    require(frames[HELPER] == 507 and frames[TARGET] == 0, "cut frame binding")
    inverse = [1 << r for r in range(n)]
    inverse = execute(inverse, reversed(prefix_gates))
    require(inverse[HELPER] == (1 << HELPER) ^ 1, "restoration covector")
    # Target163 must acquire the independent current coordinate465.
    isolation_cut_row = (1 << TARGET) ^ inverse[HELPER]
    require(list(bits(isolation_cut_row)) == [0, 163, 465], "mandatory target dependency")
    baseline_tail = list(elementary(word, "B", CUT)) + list(elementary(word, "C"))
    require(execute(rows, baseline_tail) == expected_rows(word), "baseline complete scalar endpoint")
    baseline_frames = word["start"][:]
    baseline_hist = Counter(copy_ranks)
    helper_path = [len(fb[baseline_frames[HELPER]])]
    for section in ("D", "A", "B", "C"):
        for _, _, _, frame, target, source in elementary(word, section):
            for r in (target, source):
                require(contains(fb[frame], fb[baseline_frames[r]]), "baseline frame legality")
                if frame != baseline_frames[r]:
                    baseline_hist[len(fb[frame]) - len(fb[baseline_frames[r]])] += 1
                    baseline_frames[r] = frame
                    if r == HELPER:
                        helper_path.append(len(fb[frame]))
    for r, final in enumerate(word["final"]):
        require(contains(fb[final], fb[baseline_frames[r]]), "baseline final frame")
        if final != baseline_frames[r]:
            baseline_hist[len(fb[final]) - len(fb[baseline_frames[r]])] += 1
            if r == HELPER:
                helper_path.append(len(fb[final]))
    require(helper_path == [0, 1, 4, 6, 7, 8], "baseline helper path")
    require(sum(baseline_hist.values()) == 2920 and
            sum(rank * count for rank, count in baseline_hist.items()) == 5129,
            "baseline complete local profile")
    stage_gates = [("isolation", i, 0, f, t, s) for i, (f, t, s) in enumerate(STAGE)]
    isolated = execute(rows, stage_gates)
    require(isolated == isolation_boundary(rows), "exact staged isolation boundary")
    tail, dropped, inlined = inlined_suffix(word)
    complete = prefix_gates + stage_gates + tail
    require(execute(isolated, tail) == expected_rows(word), "complete inlined scalar endpoint")
    require(execute(expected_rows(word), reversed(complete)) == [1 << r for r in range(n)], "complete inverse endpoint")
    require(all(HELPER not in gate[-2:] for gate in tail), "retired role reused")
    # Exact legal stage controls: only the two orders clearing target163 first.
    stage_orders = []
    for order in itertools.permutations((163, 381, 474)):
        gates = [("isolation", 0, 0, 0, HELPER, 0)] + [
            ("isolation", i + 1, 0, 0, r, HELPER) for i, r in enumerate(order)]
        failure, _, _ = least_joins(word, fb, [fb[f] for f in frames], gates)
        stage_orders.append({"order": list(order), "legal": failure is None})
    require(sum(item["legal"] for item in stage_orders) == 2, "stage order classification")
    # A lower bound for EVERY exact isolation block, not just the four ADDs.
    relaxed_start = [fb[f] for f in frames]
    relaxed_start[TARGET] = join(relaxed_start[TARGET], fb[507])
    # This endpoint is granted for free; h is never touched again in this tail.
    relaxed_start[HELPER] = fb[512]
    failure, _, _ = least_joins(word, fb, relaxed_start, tail)
    require(failure is not None and (failure["section"], failure["index"], failure["failed_register"],
            failure["required_rank"]) == ("B", 601, 111, 8), "least-join obstruction")
    check_chain(word)
    path = shortest_contact_path(tail, TARGET, 111, 601)
    require(path is not None and len(path) == 4, "shortest contact witness")
    # Relaxing ALL target endpoints to full makes the COMPLETE scalar word legal.
    # This changes the interface and is only a positive geometry control.
    full_caps = [fb[1] for _ in range(n)]
    full_caps[HELPER] = fb[512]
    relaxed_failure, _, relaxed_hist = least_joins(word, fb, [fb[f] for f in frames], stage_gates + tail, full_caps)
    require(relaxed_failure is None, "full-target positive geometry control")
    relaxed_hist.update(prefix_hist)
    controls = []
    for omitted in range(len(stage_gates)):
        bad = execute(rows, stage_gates[:omitted] + stage_gates[omitted + 1:])
        controls.append(expect_failure(lambda bad=bad: require(bad == isolation_boundary(rows), "isolation mutation"),
                                       "omit_isolation_" + str(omitted)))
    bad_copy_rows = prefix(word, fb, corrupt_copy=True)[0]
    controls.append(expect_failure(lambda: require(execute(bad_copy_rows, baseline_tail) == expected_rows(word), "COPY mutation"), "wrong_copy_snapshot"))
    bad_tail = tail[:]
    inline_index = next(i for i, gate in enumerate(bad_tail) if gate[0] == "B" and gate[1] == 653)
    bad_tail.pop(inline_index)
    controls.append(expect_failure(lambda: require(execute(isolated, bad_tail) == expected_rows(word), "ghost mutation"), "omit_ghost_donor"))
    bad_tail = [gate for gate in tail if not (gate[0] == "B" and gate[1] == 601)]
    controls.append(expect_failure(lambda: require(execute(isolated, bad_tail) == expected_rows(word), "contact mutation"), "omit_B601"))
    for omitted in range(4):
        controls.append(expect_failure(lambda omitted=omitted: check_chain(word, CHAIN[:omitted] + CHAIN[omitted + 1:]),
                                       "omit_witness_edge_" + str(omitted)))
    controls.append(expect_failure(lambda: check_chain(word, normal=(0, 1, 0, 0, 0, 0, 0, 0)), "wrong_separating_normal"))
    controls.append(expect_failure(lambda: authenticated_word(b"not the pinned compressed input"), "source_corruption"))
    # A priced conditional screen, not a falsely admitted invoice.
    baseline_count = len(prefix_gates) + len(baseline_tail)
    require(baseline_count == 24305 and len(complete) == 24304, "scalar invoice")
    return {"schema_version": 1, "status": "SCOPED_ALL_LENGTH_FOUR_CONTACT_OBSTRUCTION",
            "source_sha256": WORD_SHA256, "cut": CUT, "helper": HELPER, "columns": n,
            "copy_ranks": copy_ranks, "copies_erased_before_cut": len(copy_ranks),
            "restore_cut_coordinates": list(bits(inverse[HELPER])), "dirty_support": dirt,
            "isolation_target_cut_coordinates": list(bits(isolation_cut_row)),
            "isolation_program": [list(gate) for gate in STAGE], "isolation_orders": stage_orders,
            "first_least_join_failure": failure, "four_contact_witness": [list(edge) for edge in CHAIN],
            "shortest_contact_path": path, "separating_normal": [1, 0, 0, 0, 0, 0, 0, 0],
            "cap_frame": 525, "cap_rank": len(fb[525]), "enlarged_cap_rank": len(join(fb[507], fb[525])),
            "inlined_reads": inlined, "dropped_helper_adds": dropped,
            "baseline_adds": baseline_count, "complete_scalar_adds": len(complete),
            "complete_scalar_word_sha256": digest(complete), "tail_adds": len(tail),
            "baseline_paid_histogram": dict(sorted(baseline_hist.items())),
            "baseline_paid_children": sum(baseline_hist.values()),
            "baseline_paid_rank_mass": sum(rank * count for rank, count in baseline_hist.items()),
            "baseline_helper_frame_dimensions": helper_path,
            "staged_helper_frame_dimensions": [0, 1, 4, 7],
            "optimistic_two_slot_budget": budget(),
            "full_target_relaxation": {"status": "CHANGED_ENDPOINT_POSITIVE_CONTROL_ONLY",
                "paid_histogram": dict(sorted(relaxed_hist.items())),
                "paid_rank_mass": sum(rank * count for rank, count in relaxed_hist.items()),
                "paid_children": sum(relaxed_hist.values()), "includes_nine_copies": True},
            "negative_controls": controls, "new_supplier": False, "new_kappa": False}


def verify_receipt(actual, expected):
    # Normalize histogram keys before sorting: numeric 2/10 and parsed strings
    # "2"/"10" have different sort orders. Preserve typed JSON values.
    normalized = json.loads(json.dumps(actual))
    require(digest(normalized) == digest(expected), "certificate mismatch")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = derive(load(args.root))
    if args.emit:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        verify_receipt(result, json.loads((HERE / "CERTIFICATE.json").read_text()))
        print("PASS_R439_STAGED_RETIREMENT columns=661 contacts=4 first_failure=B601 "
              "scalar_ADDs=24305->24304 controls=" + str(len(result["negative_controls"])) + " no_new_kappa")


if __name__ == "__main__":
    main()
