#!/usr/bin/env python3
"""Fixed-order R439 single-column interleaving bound; standard library only.

Sricharan Vagvala, with substantial OpenAI Codex assistance. Apache-2.0.
Deferred basis and attaining ideal: Sagar Thakrar, PR2115. The all-ideal
bound of Charles Bethin, PR2279, explicitly excludes interleavings.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/r439-bsection-stars-seed01/candidate.json.gz"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
OWNER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
COLUMN = 16 % 9
IDEAL = (31, 51, 52)
TAPS = {
    "literal306": ((40, 54), (75, 5), (140, 7), (178, 88), (306, 43)),
    "ideal303": ((39, 54), (72, 5), (137, 7), (175, 88), (303, 43)),
}
PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def set_digest(values):
    return digest("".join(f"{x:028x}\n" for x in sorted(values)).encode("ascii"))


def inputs():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    data = {}
    for pin in pins["files"]:
        if pin["usage"] != "input":
            continue
        raw = (ROOT / pin["path"]).read_bytes()
        need(digest(raw) == pin["sha256"], "source SHA-256: " + pin["path"])
        blob = hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()
        need(blob == pin["git_blob"], "source Git blob: " + pin["path"])
        data[pin["path"]] = raw
    need(set(data) == {WORD, EXPORTER, OWNER}, "complete consumed source inventory")
    return data


def extract(w):
    v = w["v"]
    need((v, w["R"], len(w["ret"])) == (111, 439, 9), "source dimensions")
    is_y = lambda r: v <= r < 2 * v
    yy = lambda g: is_y(g[1]) and all(is_y(s) for s in g[2])
    reads = [i for i, g in enumerate(w["D"])
             if is_y(g[1]) and all(s >= 2 * v for s in g[2])]
    lo, hi = min(reads), max(reads)
    prep = [g for g in w["D"][:lo] if yy(g)]
    positions = [i for i, g in enumerate(w["D"]) if i > hi and yy(g)]
    undo = [w["D"][i] for i in positions]
    need(len(undo) == 306 and prep == undo[::-1], "frozen literal undo")
    need(not any(yy(g) for g in w["D"][lo:hi + 1]), "basis/read separation")
    need(all(g[0] == 0 and len(g[2]) == 1 and g[1] != g[2][0]
             for g in prep + undo), "elementary zero-frame target gates")
    need(all(not is_y(g[1]) and not any(is_y(s) for s in g[2])
             for g in w["A"]), "A isolates targets")
    need(all(not is_y(q) for q in w["ret"]), "retained values isolate targets")
    need(all(len(row) == len(set(row)) and all(type(j) is int and 0 <= j < 9 for j in row)
             for row in w["scatter"]), "scatter indices")
    S = [sum(1 << j for j in row) for row in w["scatter"]]
    P = S.copy()
    for _, d, (s,) in prep:
        P[d - v] ^= P[s - v]
    return prep, undo, positions, S, P


def split(w, extracted, keep):
    _, undo, positions, S, P = extracted
    v = w["v"]
    kept = [undo[i] for i in keep]
    rest = [g for i, g in enumerate(undo) if i not in keep]
    # Verify this reorder as a complete matrix, independently of the earlier
    # dependency-poset implementations.
    a, b = [1 << i for i in range(v)], [1 << i for i in range(v)]
    for gates, rows in ((undo, a), (kept + rest, b)):
        for _, d, (s,) in gates:
            rows[d - v] ^= rows[s - v]
    need(a == b, "kept/rest reorder changes the target operator")
    P = P.copy()
    for _, d, (s,) in kept:
        P[d - v] ^= P[s - v]
    baseline = copy.deepcopy(w)
    removed = set(positions)
    baseline["D"] = [g for i, g in enumerate(w["D"]) if i not in removed] + kept
    baseline["B"] = rest + w["B"]
    baseline["scatter"] = [[j for j in range(9) if row >> j & 1] for row in P]
    return baseline, rest, P


def suffixes(gates, v):
    """All final responses of a tap: column propagation backwards in time."""
    columns = [1 << i for i in range(v)]
    at = {len(gates): tuple(columns)}
    for cut in reversed(range(len(gates))):
        _, d, (s,) = gates[cut]
        columns[s - v] ^= columns[d - v]
        at[cut] = tuple(columns)
    return at


def ball_two(vectors):
    ordered = sorted(vectors)
    result = {0, *ordered}
    for i, a in enumerate(ordered):
        for j in range(i):
            result.add(a ^ ordered[j])
    return result


def four_taps_possible(ball, target):
    return any(target ^ a in ball for a in ball)


def prove_problem(gates, S, P, v, name):
    at = suffixes(gates, v)
    vectors = {x for cols in at.values() for x in cols}
    target = sum(1 << i for i, row in enumerate(S) if row >> COLUMN & 1)
    initial = 0
    for i, row in enumerate(P):
        if row >> COLUMN & 1:
            initial ^= at[0][i]
    need(initial == target, name + ": initial listing response")
    ball = ball_two(vectors)
    need(not four_taps_possible(ball, target), name + ": <=4 taps suffice")
    response = 0
    for cut, target_index in TAPS[name]:
        response ^= at[cut][target_index]
    need(response == target and len(TAPS[name]) == 5, name + ": five-tap attainment")
    return dict(undo_gates=len(gates), cuts=len(at), dictionary_size=len(vectors),
                dictionary_sha256=set_digest(vectors), ball_two_size=len(ball),
                ball_two_sha256=set_digest(ball), target=f"{target:028x}",
                initial_column_taps=sum(bool(row >> COLUMN & 1) for row in P),
                minimum_taps=5, taps=[list(t) for t in TAPS[name]],
                four_tap_intersection_size=0), vectors, ball, target


def export(w, data, directory):
    directory.mkdir()
    path = directory / "word.json"
    path.write_text(json.dumps(w))
    script = directory / "export_records.py"
    script.write_bytes(data[EXPORTER])
    subprocess.run([sys.executable, "-I", "-B", str(script), str(path), str(directory / "records")],
                   capture_output=True, check=True, timeout=60)
    raw = (directory / "records/249-records.bin").read_bytes()
    frames = json.loads((directory / "records/frames.json").read_text())["frames"]
    return list(struct.iter_unpack("<6i", raw)), frames


def interleave(records, w, rest, P, name):
    v, n = w["v"], 2 * w["v"] + w["R"]
    start = next(i for i, r in enumerate(records) if r[0] == 2)
    undo_start = max(i for i, r in enumerate(records) if r[0] == 3) + 1
    expected = [(1, d, ss[0], 1, 0, 4) for _, d, ss in rest]
    need(records[undo_start:undo_start + len(rest)] == expected, "undo records at zero frame")
    copies = {r[1]: r for r in records if r[0] == 2}
    erases = {r[1]: r for r in records if r[0] == 3}
    replacement = []
    for j, q in enumerate(w["ret"]):
        if j == COLUMN:
            continue
        replacement.append(copies[q])
        replacement.extend((1, v + i, n, 1, 0, 3) for i, row in enumerate(P) if row >> j & 1)
        replacement.append(erases[q])
    q = w["ret"][COLUMN]
    replacement.append(copies[q])
    for cut in range(len(rest) + 1):
        replacement.extend((1, v + i, n, 1, 0, 3) for c, i in TAPS[name] if c == cut)
        if cut < len(rest):
            replacement.append(expected[cut])
    replacement.append(erases[q])
    return records[:start] + replacement + records[undo_start + len(rest):]


def symbolic(records, w, reverse=False):
    n = 2 * w["v"] + w["R"]
    rows = [1 << i for i in range(n)] + [0]
    live = None
    for op, a, b, c, _, _ in (reversed(records) if reverse else records):
        if op == 0:
            continue
        if reverse and op in (2, 3):
            op = 5 - op
        if op == 1:
            need(c == 1, "binary ADD coefficient")
            rows[a] ^= rows[b]
        elif op == 2:
            need(live is None and not rows[b], "COPY into occupied workspace")
            rows[b], live = rows[a], (a, b)
        elif op == 3:
            need(live == (a, b) and rows[a] == rows[b], "ERASE of changed copied value")
            rows[b], live = 0, None
        else:
            raise ValueError("unknown opcode")
    need(live is None and rows[-1] == 0, "unrestored temporary")
    return rows[:-1]


def boundary(records, w):
    v, n = w["v"], 2 * w["v"] + w["R"]
    wanted = [(1 << i) ^ (1 << (i - v)) if v <= i < 2 * v else 1 << i for i in range(n)]
    for reverse in (False, True):
        need(symbolic(records, w, reverse) == wanted, "complete dirty boundary")


def invoice(records, w, frames):
    n = 2 * w["v"] + w["R"]
    cur = w["start"].copy() + [0]
    dim = {int(k): f["dim"] for k, f in frames.items()}
    spans = [set(f) for f in w["frames"]]
    profile = Counter()
    live = None
    peak_live = 0
    for op, a, b, c, f, phase in records:
        if op == 0:
            need(a < n and cur[a] == b and spans[b] < spans[c], "illegal frame MOVE")
            need(f == dim[c] - dim[b], "MOVE rank mismatch")
            cur[a] = c
            profile[f] += 1
        elif op == 1:
            need(cur[a] == cur[b] == f and c == 1, "ADD operands in different frames")
        elif op == 2:
            need(live is None and b == n and cur[a] == c and f == 0 and phase == dim[c], "COPY frame/rank")
            profile[phase] += 1
            cur[b], live, peak_live = f, (a, b), 1
        elif op == 3:
            need(live == (a, b) and cur[a] == c and cur[b] == f == 0, "ERASE frame/lifetime")
            live = None
    need(live is None and cur[:n] == w["final"], "final frame state")
    need(dict(profile) == PROFILE, "complete paid profile")
    bounds = []
    for reverse in (False, True):
        norm, peak = [1] * (n + 1), 1
        for op, a, b, c, _, _ in (reversed(records) if reverse else records):
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                norm[a] += abs(c) * norm[b]
                peak = max(peak, norm[a])
            elif op == 2:
                norm[b] = norm[a]
            elif op == 3:
                norm[b] = 0
        bounds.append(peak)
    F, B = bounds
    local, nine = 64 * F**3 * B**2, (1 << 18) * F**5 * B**4
    need(local < 1 << 104 and nine < 1 << 192, "inherited local/nine-stage guard")
    counts = Counter(r[0] for r in records)
    need(counts[2] == counts[3] == 9, "complete COPY/ERASE count")
    return dict(ADDs=counts[1], MOVEs=counts[0], COPYs=counts[2], ERASEs=counts[3],
                COPY_rank_sum=sum(r[5] for r in records if r[0] == 2),
                peak_copy_temporaries=peak_live, paid_profile={str(k): profile[k] for k in sorted(profile)},
                paid_rank_mass=sum(k * a for k, a in profile.items()), F=F, B=B,
                local_bits=local.bit_length(), nine_stage_bits=nine.bit_length(),
                record_sha256=digest(b"".join(struct.pack("<6i", *r) for r in records)))


def rejected(label, operation):
    try:
        operation()
    except ValueError:
        return label
    raise ValueError("control unexpectedly accepted: " + label)


def run(output=None):
    data = inputs()
    w = json.loads(gzip.decompress(data[WORD]))
    extracted = extract(w)
    S = extracted[3]
    # Consume the unchanged interface routine, not the native/lattice checker.
    owner = types.ModuleType("pinned_owner")
    exec(compile(data[OWNER], OWNER, "exec"), owner.__dict__)
    H, C, _ = owner.Word(w).interface()
    false_flags = sorted(k for k, ok in {**H, **C}.items() if not ok)
    need(false_flags == ["H2_D_frame0_targets_from_helpers", "K_equals_D"], "source interface pattern")
    result = dict(status="PASS_R439_INTERLEAVED_COLUMN_FLOOR", column=COLUMN, dirty_columns=661,
                  problems={}, schedules={}, controls=[], source_interface_false=false_flags,
                  new_kappa_claim=False, optimality_scope="Two fixed undo orders; single unmixed copied total only")
    with tempfile.TemporaryDirectory(prefix="r439-interleaved-") as tmp:
        tmp = Path(tmp)
        original, frames = export(w, data, tmp / "original")
        boundary(original, w)
        result["source_invoice"] = invoice(original, w, frames)
        for name, keep in (("literal306", ()), ("ideal303", IDEAL)):
            base, rest, P = split(w, extracted, keep)
            proof, vectors, ball, target = prove_problem(rest, S, P, w["v"], name)
            result["problems"][name] = proof
            baseline, fr = export(base, data, tmp / name)
            candidate = interleave(baseline, w, rest, P, name)
            boundary(baseline, w)
            boundary(candidate, w)
            need([r for r in original if r[0] == 0] == [r for r in candidate if r[0] == 0], "unchanged ordered MOVEs")
            bill = invoice(candidate, w, fr)
            scatter = sum(row.bit_count() for row in P) - proof["initial_column_taps"] + 5
            need(bill["ADDs"] == 11500 - 527 + scatter, "all undo and tap ADDs charged")
            bill.update(scatter_ADDs=scatter, undo_ADDs=len(rest) + len(keep),
                        kept_undo_indices=list(keep), target_frame_zero_through_interleaving=True)
            result["schedules"][name] = bill
            short = 0
            for x in sorted(vectors)[:4]:
                short ^= x
            need(four_taps_possible(ball, short), "positive <=4-tap control")
            result["controls"].append(name + ": known four-tap target detected")
            need(four_taps_possible(ball_two(vectors | {target}), target), "added target atom detected")
            result["controls"].append(name + ": added target atom invalidates bound")
            bad = list(candidate)
            copy_start = next(i for i, r in enumerate(bad)
                              if r[0] == 2 and r[1] == w["ret"][COLUMN])
            i = next(i for i in range(copy_start + 1, len(bad))
                     if bad[i][0] == 1 and bad[i][2] == 661)
            op, a, b, c, f, phase = bad[i]
            bad[i] = (op, 111 + (a - 111 + 1) % 111, b, c, f, phase)
            result["controls"].append(rejected(name + ": changed tap target", lambda: boundary(bad, w)))
            bad = list(candidate)
            i = next(i for i, r in enumerate(bad) if r == (1, rest[0][1], rest[0][2][0], 1, 0, 4))
            del bad[i]
            result["controls"].append(rejected(name + ": omitted undo", lambda: boundary(bad, w)))
            bad = list(candidate)
            i = next(i for i, r in enumerate(bad) if r[0] == 3)
            bad.insert(i, (1, 661, 111, 1, 0, 3))
            result["controls"].append(rejected(name + ": changed COPY before ERASE", lambda: boundary(bad, w)))
            bad = list(candidate)
            i = next(i for i, r in enumerate(bad) if r[0] == 2)
            op, a, b, c, f, rank = bad[i]
            bad[i] = (op, a, b, c, f, rank - 1)
            result["controls"].append(rejected(name + ": undercharged COPY", lambda: invoice(bad, w, fr)))
            if output is not None:
                output.mkdir(parents=True, exist_ok=True)
                (output / (name + "-records.bin")).write_bytes(b"".join(struct.pack("<6i", *r) for r in candidate))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true", help="regenerate the exact certificate")
    parser.add_argument("--output", type=Path, help="also export the two literal record streams")
    args = parser.parse_args()
    result = run(args.output)
    certificate = HERE / "CERTIFICATE.json"
    if args.write:
        certificate.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    expected = json.loads(certificate.read_text())
    need(json.dumps(expected, sort_keys=True) == json.dumps(result, sort_keys=True),
         "certificate differs from exact recomputation")
    print("PASS_R439_INTERLEAVED_COLUMN_FLOOR column=7 minimum=5 orders=2 dirty_columns=661 "
          "controls=12 ideal_scatter=94 no_new_kappa")


if __name__ == "__main__":
    main()
