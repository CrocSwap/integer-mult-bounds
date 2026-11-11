#!/usr/bin/env python3
"""Minimum clean support inside the dimension-1 frame family.

On the fixed PR #5745 source, every nonzero clean relation among the 119
dimension-1 frames has cancelled frame support at least 41, and two explicit
relations meet 41.  The argument is an exhaustive finite census: the F_3
projected code has 28 rays of weight at most 40, each lifts to one rational
ray, and every other rational word has projected weight at least 41.  Mode-zero
cancellation is exact because the six mode-zero generators have disjoint
supports.  Checks raise SystemExit, including under python -O.

The orthogonal census follows research/nine-channel-monotone-bound (Ali
Romman) and research/ten-channel-triple-span, Apache-2.0, and does not import
either program.  The 6-span bound is the companion program span_bound.c.
A C compiler (cc, gcc or clang) is required.
"""

import hashlib
import io
import itertools
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from collections import defaultdict
from fractions import Fraction
from math import comb, gcd, lcm
from pathlib import Path

Q = Fraction
ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
ARCHIVE = ROOT / "research/filtered-native-kappa004/inputs/original-packet.tar.gz"
WORD = "filtered_native_implementation/research/retained_state_next/F9-SOURCE-DAG-ALL8-WORD.json.gz"
MODES = "filtered_native_implementation/upstream/research/involutory-producer-raw-dual/inputs/R/R.json"
ARCHIVE_SHA256 = "595f988e748b1f3b25e7525a226da173966e4278a70f511b2919245cec1b45f7"
WORD_SHA256 = "934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775"
EXPECTED_KERNEL_PIVOTS = (0, 6, 12, 1, 2, 3, 4, 5, 17, 13, 19, 18, 35, 23)
EXPECTED_CLEAN = (0, 1, 3, 4, 5, 6, 7, 9)
EXPECTED_ZERO = (2, 8, 10, 11, 12, 13)
# Positive-first coefficient rays in the eight clean basis rows, and the
# cancelled-support histogram of all 28 projected rays of weight at most 40.
RAY_41_A = (0, 1, -1, -1, -1, 0, -1, 0)
RAY_41_B = (0, 1, -1, 0, 0, -1, 0, 1)
RAY_32 = (26, 0, 0, -1, 0, 0, 0, 0)
MODE_A = (0, 0, 0, 0, -728, 728, 728, -728)
MODE_B = (0, 0, 0, 0, -728, -728, -728, -728)
PHI_HISTOGRAM = {41: 2, 50: 1, 52: 1, 53: 24}
SPAN_MAX = {57: 33, 52: 31}


def fail(message):
    raise SystemExit("FAIL " + message)


def require(ok, message):
    if not ok:
        fail(message)


def add(a, b, c):
    for i, v in b.items():
        x = a.get(i, Q(0)) + c * v
        if x:
            a[i] = x
        else:
            a.pop(i, None)


def insert_pivot(basis, row):
    row = dict(row)
    while row:
        pivot = min(row)
        if pivot not in basis:
            scale = row[pivot]
            basis[pivot] = {i: v / scale for i, v in row.items()}
            return pivot
        add(row, basis[pivot], -row[pivot])
    return None


def idx(ref):
    return ref[1] + (632 if ref[0] == "C" else 0)


def census(word, modes):
    events = word["programs"]["backward"]
    n = 633 + word["owned_extra_slots_by_direction"]["backward"]
    cur = word["canonical"]["start"][:] + [None] * (n - 632)
    before = {}
    for k, event in enumerate(events):
        if event[0] == "scalar" and event[1][0] == "clear":
            d = idx(event[1][1])
            before[k] = cur[d]
            cur[d] = event[2]
        elif event[0] in ("climb", "warp"):
            d = event[2] if event[0] == "climb" else idx(event[1])
            require(cur[d] == event[3], "forward coframe")
            before[k] = cur[d]
            cur[d] = event[4]
    require(cur[:632] == word["canonical"]["final"], "final frames")
    cols = [{i: Q(1)} for i in range(632)] + [{} for _ in range(n - 632)]
    bases = {}
    seen = defaultdict(set)
    projected = {}
    contacts = 0

    def observe(d):
        nonlocal contacts
        frame = cur[d]
        if frame is None or len(word["canonical"]["frames"][frame]) >= 8 or not cols[d]:
            return
        contacts += 1
        key = tuple(sorted(cols[d].items()))
        if key in seen[frame]:
            return
        seen[frame].add(key)
        if key not in projected:
            row = {i: v for i, v in cols[d].items() if i < 224 or word["canonical"]["start"][i] != 0}
            mode = [sum((r[i] * v for i, v in cols[d].items() if i < 112), Q(0)) / 56 for r in modes]
            for j, a in enumerate(mode):
                if a:
                    add(row, {i: x for i, x in enumerate(modes[j]) if x}, -a)
                    row[632 + j] = a
            projected[key] = row
        pivot = insert_pivot(bases.setdefault(frame, {}), projected[key])
        require(pivot is None or pivot < 632, "single-frame clean response %s" % frame)

    for d in range(n):
        observe(d)
    for k in range(len(events) - 1, -1, -1):
        event = events[k]
        typ = event[0]
        changed = []
        if typ == "scalar":
            a = event[1]
            d = idx(a[1])
            kind = a[0]
            if kind == "add":
                src = idx(a[2])
                require(d != src and cur[d] == event[2] and cur[src] == event[2], "ADD coframe")
                add(cols[src], cols[d], Q(a[3], a[4]))
                changed = [src]
            elif kind == "scale":
                require(a[2] and cur[d] == event[2], "SCALE coframe")
                cols[d] = {i: v * Q(a[2], a[3]) for i, v in cols[d].items()}
                changed = [d]
            elif kind == "clear":
                cols[d] = {}
                changed = [d]
            else:
                fail("unhandled scalar %s" % kind)
        elif typ in ("climb", "warp"):
            d = event[2] if typ == "climb" else idx(event[1])
            changed = [d]
            require(cur[d] == event[4], "reverse coframe")
        elif typ not in ("physical_add", "adapter", "phase"):
            fail("unhandled event %s" % typ)
        if k in before:
            cur[d] = before[k]
        for d in changed:
            observe(d)
    meta = {
        "all_event_contacts": contacts,
        "distinct_frame_columns": sum(map(len, seen.values())),
        "projected_columns": len(projected),
        "frames": len(bases),
    }
    return bases, meta


def load_source():
    raw = ARCHIVE.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == ARCHIVE_SHA256, "archive sha256")
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        word_bytes = archive.extractfile(WORD).read()
        require(hashlib.sha256(word_bytes).hexdigest() == WORD_SHA256, "word sha256")
        word = json.loads(__import__("gzip").decompress(word_bytes))
        modes = json.loads(archive.extractfile(MODES).read())
    modes = [[Q(x) for x in row] for row in modes]
    gram = [sum(modes[i][k] * modes[j][k] for k in range(len(modes[0]))) for i in range(8) for j in range(8)]
    require(gram == [56 if i == j else 0 for i in range(8) for j in range(8)], "RR^T = 56 I")
    return word, modes


def dimension1_basis(bases):
    frames = sorted(frame for frame, basis in bases.items() if len(basis) == 1)
    require(len(frames) == 119, "dimension-1 count %s" % len(frames))
    coords = sorted({i for frame in frames for i in next(iter(bases[frame].values())) if i < 632})
    index = {c: j for j, c in enumerate(coords)}
    rows = []
    for frame in frames:
        row0 = next(iter(bases[frame].values()))
        row = {index[i]: v for i, v in row0.items() if i < 632}
        for j in range(8):
            value = row0.get(632 + j, Q(0))
            if value:
                row[1000 + j] = value
        rows.append(row)
    basis = {}
    kernel = []
    for g, row0 in enumerate(rows):
        row = {i: v for i, v in row0.items() if i < 1000}
        coeff = {g: Q(1)}
        mode = [row0.get(1000 + j, Q(0)) for j in range(8)]
        while row:
            pivot = min(row)
            if pivot not in basis:
                scale = row[pivot]
                basis[pivot] = (
                    {i: v / scale for i, v in row.items()},
                    {j: v / scale for j, v in coeff.items()},
                    [m / scale for m in mode],
                )
                break
            factor = row[pivot]
            br, bc, bm = basis[pivot]
            add(row, br, -factor)
            for j, v in bc.items():
                x = coeff.get(j, Q(0)) - factor * v
                if x:
                    coeff[j] = x
                else:
                    coeff.pop(j, None)
            mode = [m - factor * bb for m, bb in zip(mode, bm)]
        else:
            kernel.append((coeff, mode))
    require(len(basis) == 105 and len(kernel) == 14, "dimension-1 kernel shape")
    reduced = []
    pivots = []
    for coeff, mode in kernel:
        row = dict(coeff)
        for j, v in enumerate(mode):
            if v:
                row[1000 + j] = v
        for pivot, basis_row in zip(list(pivots), list(reduced)):
            if pivot in row:
                add(row, basis_row, -row[pivot])
        if not row:
            continue
        keys = [i for i in row if i < 1000]
        pivot = min(keys) if keys else min(row)
        scale = row[pivot]
        row = {i: v / scale for i, v in row.items()}
        new_rows = []
        for basis_row in reduced:
            if pivot in basis_row:
                basis_row = dict(basis_row)
                add(basis_row, row, -basis_row[pivot])
            new_rows.append(basis_row)
        reduced = new_rows + [row]
        pivots.append(pivot)
    require(tuple(pivots) == EXPECTED_KERNEL_PIVOTS, "kernel pivots %s" % (pivots,))
    require(len(reduced) == 14, "reduced rank %s" % len(reduced))
    return frames, rows, reduced


def witness_support(reduced):
    witness = (0, -1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0)
    original = {}
    mode = [Q(0)] * 8
    for coef, row in zip(witness, reduced):
        if not coef:
            continue
        for j, v in row.items():
            if j >= 1000:
                mode[j - 1000] += coef * v
            else:
                original[j] = original.get(j, Q(0)) + coef * v
    support = [j for j, v in original.items() if v]
    require(len(support) == 41, "published witness support %s" % len(support))
    require(mode == [Q(0), Q(0), Q(0), Q(0), Q(14), Q(-14), Q(-14), Q(14)], "published witness mode %s" % mode)


def integer_matrix(reduced):
    scale = 1
    for row in reduced:
        for value in row.values():
            scale = lcm(scale, value.denominator)
    require(scale == 52, "denominator lcm %s" % scale)
    matrix = []
    modes = []
    peak = 0
    for row in reduced:
        frame = []
        for j in range(119):
            value = row.get(j, Q(0)) * scale
            require(value.denominator == 1, "non-integral frame entry")
            frame.append(int(value))
            peak = max(peak, abs(frame[-1]))
        mode = []
        for j in range(8):
            value = row.get(1000 + j, Q(0)) * scale
            require(value.denominator == 1, "non-integral mode entry")
            mode.append(int(value))
        matrix.append(frame)
        modes.append(mode)
    require(peak == 208, "max frame entry %s" % peak)
    return matrix, modes


def dot_mode(coeffs, modes):
    return [sum(coeffs[i] * modes[i][k] for i in range(8)) for k in range(8)]


def frame_word(coeffs, matrix):
    word = [0] * 119
    for i, coef in enumerate(coeffs):
        if not coef:
            continue
        row = matrix[i]
        for j, value in enumerate(row):
            if value:
                word[j] += coef * value
    return word


def group_residual(word, positions, values):
    best = 5
    candidates = [(0, 1)]
    for t in range(5):
        candidates.append((-word[positions[t]], values[t]))
    for num, den in candidates:
        count = 0
        for t in range(5):
            if word[positions[t]] * den + num * values[t]:
                count += 1
        if count < best:
            best = count
    return best


def cancelled_weight(word, groups, outside):
    extra = 0
    for positions, values in groups:
        extra += group_residual(word, positions, values)
    raw_outside = sum(1 for j in outside if word[j])
    return raw_outside + extra, raw_outside, extra


def normalize(vector):
    g = 0
    for value in vector:
        g = gcd(g, abs(value))
    require(g > 0, "zero coefficient vector")
    vector = [value // g for value in vector]
    for value in vector:
        if value:
            if value < 0:
                vector = [-item for item in vector]
            break
    return tuple(vector)


def rref_kernel(columns):
    """One primitive generator of {c in Q^8 : c · column = 0 for every column}."""
    matrix = [[Q(int(entry)) for entry in column] for column in columns]
    width = 8
    pivot_at = []
    row_index = 0
    for col in range(width):
        pivot = None
        for i in range(row_index, len(matrix)):
            if matrix[i][col]:
                pivot = i
                break
        if pivot is None:
            continue
        matrix[row_index], matrix[pivot] = matrix[pivot], matrix[row_index]
        lead = matrix[row_index][col]
        matrix[row_index] = [value / lead for value in matrix[row_index]]
        for i in range(len(matrix)):
            if i != row_index and matrix[i][col]:
                factor = matrix[i][col]
                matrix[i] = [matrix[i][k] - factor * matrix[row_index][k] for k in range(width)]
        pivot_at.append(col)
        row_index += 1
    free = [j for j in range(width) if j not in pivot_at]
    require(len(free) == 1, "kernel dimension %s" % len(free))
    free_var = free[0]
    generator = [Q(0)] * width
    generator[free_var] = Q(1)
    for i, pivot in enumerate(pivot_at):
        generator[pivot] = -matrix[i][free_var]
    scale = 1
    for value in generator:
        scale = lcm(scale, value.denominator)
    return normalize([int(value * scale) for value in generator])


def rank_mod3(rows):
    matrix = [[entry % 3 for entry in row] for row in rows]
    rank = 0
    width = len(matrix[0])
    for col in range(width):
        pivot = None
        for i in range(rank, len(matrix)):
            if matrix[i][col] % 3:
                pivot = i
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inv = 1 if matrix[rank][col] % 3 == 1 else 2
        matrix[rank] = [(entry * inv) % 3 for entry in matrix[rank]]
        for i in range(len(matrix)):
            factor = matrix[i][col] % 3
            if i != rank and factor:
                matrix[i] = [(matrix[i][j] - factor * matrix[rank][j]) % 3 for j in range(width)]
        rank += 1
    return rank


def project_rows(generator, columns):
    units = [i for i, value in enumerate(generator) if abs(value) == 1]
    require(units, "kernel has no unit coordinate %s" % (generator,))
    unit = units[0]
    projected = []
    for column in columns:
        require(sum(generator[i] * column[i] for i in range(8)) == 0, "column misses the kernel")
        projected.append(tuple(column[i] for i in range(8) if i != unit))
    return projected


def first_span_count(rows):
    """Span size of the lexicographic first independent 6-tuple, over Q."""
    for choice in itertools.combinations(range(len(rows)), 6):
        matrix = [[Q(entry) for entry in rows[i]] for i in choice]
        pivots = []
        row_index = 0
        for col in range(7):
            pivot = None
            for i in range(row_index, 6):
                if matrix[i][col]:
                    pivot = i
                    break
            if pivot is None:
                continue
            matrix[row_index], matrix[pivot] = matrix[pivot], matrix[row_index]
            lead = matrix[row_index][col]
            matrix[row_index] = [value / lead for value in matrix[row_index]]
            for i in range(6):
                if i != row_index and matrix[i][col]:
                    factor = matrix[i][col]
                    matrix[i] = [matrix[i][k] - factor * matrix[row_index][k] for k in range(7)]
            pivots.append(col)
            row_index += 1
        if len(pivots) < 6:
            continue
        count = 0
        for row in rows:
            value = [Q(entry) for entry in row]
            for i, pivot in enumerate(pivots):
                factor = value[pivot]
                if factor:
                    value = [value[k] - factor * matrix[i][k] for k in range(7)]
            if all(entry == 0 for entry in value):
                count += 1
        return count
    fail("no independent 6-tuple")


def compile_span_bound():
    compiler = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    require(compiler is not None, "C compiler not found (cc, gcc or clang)")
    work = tempfile.TemporaryDirectory(prefix="dim1-span-")
    binary = str(Path(work.name) / "span_bound")
    compiled = subprocess.run(
        [compiler, "-O3", "-std=c11", "-o", binary, str(PACKAGE / "span_bound.c")],
        capture_output=True,
        text=True,
    )
    require(compiled.returncode == 0, "compiler failed: " + compiled.stderr[-500:])
    probe = subprocess.run([binary, "--self-test"], capture_output=True, text=True)
    require(probe.returncode == 0, "span self-test failed: " + probe.stderr[-500:])
    require(
        probe.stdout.strip()
        == "SPAN_BOUND n=9 seen=84 indep=24 best=8 first=7 ortho_failures=0 division_failures=0",
        "span self-test output %s" % probe.stdout.strip(),
    )
    return work, binary


def run_span_bounds(binary, jobs):
    processes = []
    for name, rows in jobs:
        handle = tempfile.NamedTemporaryFile("w", prefix="dim1-%s-" % name, suffix=".txt", delete=False)
        handle.write("%s\n" % len(rows))
        for row in rows:
            handle.write(" ".join(str(entry) for entry in row) + "\n")
        handle.close()
        processes.append((name, handle.name, rows, subprocess.Popen(
            [binary, handle.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )))
    results = {}
    try:
        for name, path, rows, process in processes:
            stdout, stderr = process.communicate()
            require(process.returncode == 0, "span bound %s failed: %s" % (name, stderr[-500:]))
            line = stdout.strip().splitlines()[-1]
            parts = dict(item.split("=", 1) for item in line.split()[1:])
            seen = int(parts["seen"])
            best = int(parts["best"])
            first = int(parts["first"])
            require(int(parts["n"]) == len(rows), "span n %s" % name)
            require(seen == comb(len(rows), 6), "span combinations %s %s" % (name, seen))
            require(int(parts["ortho_failures"]) == 0 and int(parts["division_failures"]) == 0, "span exactness")
            require(first == first_span_count(rows), "span first tuple %s C=%s" % (name, first))
            require(best == SPAN_MAX[len(rows)] and best < 49, "span maximum %s is %s" % (name, best))
            results[name] = best
    finally:
        for _name, path, _rows, process in processes:
            if process.poll() is None:
                process.kill()
                process.communicate()
            try:
                os.unlink(path)
            except OSError:
                pass
    return results


def low_weight_rays(projected):
    """Projective F_3 words of projected weight at most 40, first nonzero entry 1."""
    found = []
    histogram = defaultdict(int)
    total = 0
    for number in range(1, 6561):
        coeff = []
        value = number
        for _ in range(8):
            coeff.append(value % 3)
            value //= 3
        if not any(coeff):
            continue
        leading = next(entry for entry in coeff if entry)
        if leading != 1:
            continue
        total += 1
        dots = [sum(coeff[i] * projected[i][j] for i in range(8)) for j in range(len(projected[0]))]
        weight = sum(1 for dot in dots if dot % 3)
        histogram[weight] += 1
        if weight <= 40:
            zeros = [j for j, dot in enumerate(dots) if dot % 3 == 0]
            found.append((weight, tuple(coeff), zeros))
    require(total == 3280, "projective count %s" % total)
    require(histogram[32] == 1 and histogram[37] == 2 and histogram[40] == 25, "F3 weights %s" % dict(histogram))
    require(min(histogram) == 32, "F3 minimum %s" % min(histogram))
    require(len(found) == 28, "low rays %s" % len(found))
    return found


def chart_rank(rows):
    matrix = [[Q(entry) for entry in row] for row in rows]
    rank = 0
    for col in range(7):
        pivot = None
        for i in range(rank, len(matrix)):
            if matrix[i][col]:
                pivot = i
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        lead = matrix[rank][col]
        matrix[rank] = [value / lead for value in matrix[rank]]
        for i in range(len(matrix)):
            if i != rank and matrix[i][col]:
                factor = matrix[i][col]
                matrix[i] = [matrix[i][k] - factor * matrix[rank][k] for k in range(7)]
        rank += 1
        if rank == 7:
            break
    return rank


def certify_charts(clean, groups, outside):
    projected = [[row[j] for j in outside] for row in clean]
    jobs = []
    for weight, _coeff, zeros in low_weight_rays(projected):
        if len(zeros) <= 49:
            continue
        columns = [tuple(projected[i][j] for i in range(8)) for j in zeros]
        generator = rref_kernel(columns)
        rows = project_rows(generator, columns)
        require(chart_rank(rows) == 7, "chart rank")
        jobs.append(("f3-%s-%s-%s" % (weight, len(rows), len(jobs)), rows))
    require(len(jobs) == 3, "heavy jobs %s" % len(jobs))
    work, binary = compile_span_bound()
    try:
        run_span_bounds(binary, jobs)
    finally:
        work.cleanup()


def split_generators(matrix, modes):
    clean_index = tuple(i for i, mode in enumerate(modes) if any(mode))
    zero_index = tuple(i for i, mode in enumerate(modes) if not any(mode))
    require(clean_index == EXPECTED_CLEAN, "clean rows %s" % (clean_index,))
    require(zero_index == EXPECTED_ZERO, "mode-zero rows %s" % (zero_index,))
    groups = []
    covered = set()
    for index in zero_index:
        positions = [j for j, value in enumerate(matrix[index]) if value]
        require(len(positions) == 5, "mode-zero support %s" % positions)
        require(not covered.intersection(positions), "mode-zero supports meet")
        covered.update(positions)
        groups.append((positions, [matrix[index][j] for j in positions]))
    require(len(covered) == 30, "mode-zero union %s" % len(covered))
    outside = [j for j in range(119) if j not in covered]
    # A pure mode-zero generator cancels its own group and no other frame.
    for positions, values in groups:
        word = [0] * 119
        for position, value in zip(positions, values):
            word[position] = value
        phi, raw_outside, extra = cancelled_weight(word, groups, outside)
        require(phi == 0 and raw_outside == 0 and extra == 0, "mode-zero self-cancellation")
    clean = [matrix[i] for i in clean_index]
    clean_modes = [modes[i] for i in clean_index]
    # Mode map on the clean span is injective.
    mode_rows = [[Q(entry) for entry in row] for row in clean_modes]
    rank = 0
    for col in range(8):
        pivot = None
        for i in range(rank, 8):
            if mode_rows[i][col]:
                pivot = i
                break
        if pivot is None:
            continue
        mode_rows[rank], mode_rows[pivot] = mode_rows[pivot], mode_rows[rank]
        lead = mode_rows[rank][col]
        mode_rows[rank] = [value / lead for value in mode_rows[rank]]
        for i in range(8):
            if i != rank and mode_rows[i][col]:
                factor = mode_rows[i][col]
                mode_rows[i] = [mode_rows[i][k] - factor * mode_rows[rank][k] for k in range(8)]
        rank += 1
    require(rank == 8, "clean mode rank %s" % rank)
    return clean, clean_modes, groups, outside


def main():
    word, modes = load_source()
    bases, meta = census(word, modes)
    require(meta == {
        "all_event_contacts": 15752,
        "distinct_frame_columns": 14816,
        "projected_columns": 12240,
        "frames": 879,
    }, "census %s" % meta)
    _frames, _rows, reduced = dimension1_basis(bases)
    witness_support(reduced)
    matrix, mode_rows = integer_matrix(reduced)
    clean, clean_modes, groups, outside = split_generators(matrix, mode_rows)
    projected = [[row[j] for j in outside] for row in clean]
    require(rank_mod3(projected) == 8, "projected rank mod 3")
    require(len(projected[0]) == 89, "outside columns %s" % len(projected[0]))
    phi_of = {}
    seen = []
    for _weight, _coeff, zeros in low_weight_rays(projected):
        columns = [tuple(projected[i][j] for i in range(8)) for j in zeros]
        generator = rref_kernel(columns)
        mode = dot_mode(generator, clean_modes)
        require(any(mode), "clean mode vanished")
        phi, raw_outside, _extra = cancelled_weight(frame_word(generator, clean), groups, outside)
        require(raw_outside == 89 - len(zeros), "lifted projected weight")
        require(phi >= 41, "support below 41")
        phi_of[phi] = phi_of.get(phi, 0) + 1
        seen.append(generator)
    require(phi_of == PHI_HISTOGRAM, "phi histogram %s" % phi_of)
    require(RAY_41_A in seen and RAY_41_B in seen and RAY_32 in seen, "pinned rays missing")
    for ray, expected_phi, expected_mode in (
        (RAY_41_A, 41, MODE_A),
        (RAY_41_B, 41, MODE_B),
        (RAY_32, 50, None),
    ):
        phi, _raw, _extra = cancelled_weight(frame_word(ray, clean), groups, outside)
        require(phi == expected_phi, "direct pinned support %s" % phi)
        if expected_mode is not None:
            require(tuple(dot_mode(ray, clean_modes)) == expected_mode, "direct pinned mode")
    certify_charts(clean, groups, outside)
    print("PASS_DIMENSION_ONE_CLEAN_MINIMUM")


if __name__ == "__main__":
    main()
