# SPDX-License-Identifier: Apache-2.0
"""Set-valued scalar replay and integer-normal proof check; no primary imports."""
import gzip
import hashlib
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
PIN = "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f"


def check(value, message):
    if not value:
        raise ValueError(message)


def integer_rank(vectors):
    pivots = {}
    for vector in vectors:
        row = list(vector)
        for column in sorted(pivots):
            pivot = pivots[column]
            if row[column]:
                a, b = pivot[column], row[column]
                row = [a * x - b * y for x, y in zip(row, pivot)]
                divisor = 0
                for x in row:
                    divisor = gcd(divisor, abs(x))
                if divisor:
                    row = [x // divisor for x in row]
        leading = next((i for i, x in enumerate(row) if x), None)
        if leading is not None:
            pivots[leading] = row
    return len(pivots)


def run():
    raw = (ROOT / WORD).read_bytes()
    check(hashlib.sha256(raw).hexdigest() == PIN, "source bytes")
    w = json.loads(gzip.decompress(raw))
    receipt = json.loads((HERE / "CERTIFICATE.json").read_text())
    n, v = 2 * w["v"] + w["R"], w["v"]
    state = [{i} for i in range(n)]
    scalar_word = []
    frame_ids = w["start"][:]
    for section in ("D", "A"):
        for i, (f, t, donors) in enumerate(w[section]):
            for j, s in enumerate(donors):
                state[t].symmetric_difference_update(state[s])
                frame_ids[t] = frame_ids[s] = f
                scalar_word.append([section, i, j, f, t, s])
    copies = {}
    check([integer_rank([w["lines"][j] for j in w["frames"][frame_ids[r]]]) for r in w["ret"]] == [7] * 9,
          "COPY ranks")
    for i, r in enumerate(w["ret"]):
        check(n not in copies, "no live correlated temporary before COPY")
        copies[n] = set(state[r])
        for t, totals in enumerate(w["scatter"]):
            if i in totals:
                state[v + t].symmetric_difference_update(copies[n])
                scalar_word.append(["scatter", t, totals.index(i), 0, v + t, r])
        check(copies.pop(n) == state[r], "dirty ERASE contract")
    check(not copies, "copy lifecycle closed")
    for i, (f, t, donors) in enumerate(w["B"][:10]):
        for j, s in enumerate(donors):
            state[t].symmetric_difference_update(state[s])
            frame_ids[t] = frame_ids[s] = f
            scalar_word.append(["B", i, j, f, t, s])
    cut = [set(row) for row in state]
    check(cut[465] == {0, 465} and cut[0] == {0}, "independent restoration equation")
    check([r for r in range(n) if 465 in cut[r]] == [163, 381, 465, 474], "dirty occurrences")
    check(frame_ids[465] == 507 and frame_ids[163] == 0, "cut frames")
    # Independently multiply the claimed isolation row by the cut matrix.
    check(cut[163] ^ cut[465] ^ cut[0] == cut[163] ^ {465}, "mandatory independent cut coordinate")
    stage = [(507, 465, 0), (507, 163, 465), (512, 381, 465), (512, 474, 465)]
    for i, (f, t, s) in enumerate(stage):
        state[t].symmetric_difference_update(state[s])
        scalar_word.append(["isolation", i, 0, f, t, s])
    for r in range(n):
        check(state[r] == ({465} if r == 465 else cut[r] - {465}), "full isolation state")
    # A set-valued ghost, updated directly under physical transvections.
    signal = {0}
    inlined = []
    dropped = 0
    for section, start in (("B", 10), ("C", 0)):
        for i, (f, t, donors) in enumerate(w[section]):
            if i < start:
                continue
            for j, s in enumerate(donors):
                if t == 465:
                    signal.symmetric_difference_update({s})
                    dropped += 1
                    continue
                sources = sorted(signal) if s == 465 else [s]
                check(t not in sources, "active inlining reversible")
                if s == 465:
                    inlined.append((section, i, t, sources))
                for donor in sources:
                    state[t].symmetric_difference_update(state[donor])
                    if t in signal:
                        signal.symmetric_difference_update({donor})
                    scalar_word.append([section, i, j, f, t, donor])
    check(not signal, "helper signal restored")
    for r in range(n):
        desired = {r, r - v} if v <= r < 2 * v else {r}
        check(state[r] == desired, "complete set-valued endpoint")
    check(len(scalar_word) == 24304 and dropped == 13, "full scalar invoice")
    encoding = json.dumps(scalar_word, sort_keys=True, separators=(",", ":")).encode()
    check(hashlib.sha256(encoding).hexdigest() == receipt["complete_scalar_word_sha256"], "complete word identity")
    check(inlined == [("B", 653, 163, [0, 11, 63, 72, 247, 323, 345, 373, 432]),
                      ("C", 583, 381, [0])], "inlined donor lists")
    # Proof geometry uses only integral vectors: e0 belongs to507 and normal e0*
    # annihilates525. Seven independent rows in525 make the rank-eight witness exact.
    plane507 = [w["lines"][i] for i in w["frames"][507]]
    plane525 = [w["lines"][i] for i in w["frames"][525]]
    check([2, 0, 0, 0, 0, 0, 0, 0] in plane507, "separating vector present")
    check(all(row[0] == 0 for row in plane525), "normal annihilation")
    check(integer_rank(plane507) == 4 and integer_rank(plane525) == 7 and
          integer_rank(plane525 + [[1, 0, 0, 0, 0, 0, 0, 0]]) == 8, "integer rank witnesses")
    chain = [(48, 163, 48), (117, 48, 5), (493, 5, 243), (601, 243, 111)]
    for i, a, b in chain:
        _, t, ss = w["B"][i]
        check((t == a and b in ss) or (t == b and a in ss), "original contact pin")
    # Independent one-direction chronological reachability, not rational joins.
    distance = {163: 0}
    for section, i, _, _, t, s in scalar_word:
        if section != "B" or not 10 <= i <= 601:
            continue
        dt, ds = distance.get(t, 10**6), distance.get(s, 10**6)
        if dt < 10**6:
            distance[s] = min(ds, dt + 1)
        if ds < 10**6:
            distance[t] = min(dt, ds + 1)
    check(distance[111] == 4, "four-contact temporal distance")
    check(receipt["first_least_join_failure"]["index"] == 601 and receipt["cap_frame"] == 525,
          "primary claim binding")
    print("PASS_R439_STAGED_INDEPENDENT columns=661 ADDs=24304 copies=9 contacts=4 integer_ranks=4,7,8")


if __name__ == "__main__":
    run()
