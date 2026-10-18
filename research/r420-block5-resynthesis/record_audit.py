"""Replay stock records on every scalar column and count paid moves and prefix bounds.

This audit checks one local R420 word in both directions. It does not run a
global hosting or price pipeline. Output receipts omit paths and timing.

Prepared for x0hu with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
EXPORTER = ROOT / "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
FIVE_FORMULA = ROOT / "research/e8-bit-carrier-skeleton/code/bit/checkers/columns_h.cpp"
NINE_FORMULA = ROOT / ("research/e8-bit-r420/vendor/pr510/e8-r480-nine-stage/"
                       "vendor/e8-r715-eleven-stage-whole/code/global_k.py")


class Reject(ValueError):
    """A record violates the checked local contract."""


def require(condition, message):
    if not condition:
        raise Reject(message)


def replay(records, states, frames, reverse=False):
    """Replay MOVE/ADD/COPY/ERASE records, including arbitrary helper dirt."""
    n, v, h = states["n"], states["v"], states["h"]
    require((n, v, h, states["R"]) == (660, 120, 8, 420), "wrong R420 header")
    dim = {int(k): x["dim"] for k, x in frames.items()}
    src, dest = ("final", "initial") if reverse else ("initial", "final")
    cur = [states[src][str(i)] for i in range(n)] + [-1]
    vals = [1 << i for i in range(n)] + [0]
    norm = [1] * n + [0]
    maximum, maximum_at, center = 1, None, None
    hist, counts = Counter(), Counter()
    for index, row in enumerate(reversed(records) if reverse else records):
        require(len(row) == 6, "malformed record")
        op, x, y, c, f, z = row
        require(op in (0, 1, 2, 3) and 0 <= x < n, "invalid operation or destination")
        counts[op] += 1
        if op == 0:
            old, new = (c, y) if reverse else (y, c)
            require(old in dim and new in dim, "unknown MOVE frame")
            require(cur[x] == old, "MOVE source frame mismatch")
            rank = dim[old] - dim[new] if reverse else dim[new] - dim[old]
            require(rank == f and f > 0, "MOVE rank mismatch")
            lo, hi = (new, old) if reverse else (old, new)
            require(all(sum(a*b for a, b in zip(ann, basis)) == 0
                        for ann in frames[str(hi)]["A"] for basis in frames[str(lo)]["B"]),
                    "MOVE frames not nested")
            cur[x] = new
            hist[f] += 1
        elif op == 1:
            require(0 <= y <= n and x != y and f in dim, "invalid ADD operands")
            require(cur[x] == cur[y] == f, "ADD frame mismatch")
            require(center is None or x != center, "copied center modified")
            require(y != n or center is not None, "ADD reads closed copy workspace")
            if c & 1:
                vals[x] ^= vals[y]
            norm[x] += abs(c) * norm[y]
            if norm[x] > maximum:
                maximum = norm[x]
                maximum_at = dict(record_in_direction=index, destination=x, phase=z)
        elif op == (3 if reverse else 2):
            require(center is None, "copy workspace already open")
            require(y == n and c in dim and f in dim and cur[x] == c and vals[n] == 0,
                    "COPY source frame or workspace mismatch")
            rank = abs(dim[c] - dim[f])
            require(rank == 8 and z == (0 if reverse else rank), "COPY rank mismatch")
            center, cur[n], vals[n], norm[n] = x, f, vals[x], norm[x]
            hist[rank] += 1
        else:
            require(op == (2 if reverse else 3), "unexpected operation")
            require(center == x and y == n and cur[x] == c and cur[n] == f,
                    "ERASE source frame or workspace mismatch")
            require(z == (8 if reverse else 0), "ERASE rank field mismatch")
            require(vals[n] == vals[x], "ERASE copy contents mismatch")
            center, cur[n], vals[n], norm[n] = None, -1, 0, 0
    require(center is None and vals[n] == 0, "copy workspace not closed")
    require(counts[2] == counts[3] == len(states["retained_totals"]) == 9, "COPY/ERASE count mismatch")
    require(cur[:n] == [states[dest][str(i)] for i in range(n)], "final frames mismatch")
    require(all(vals[i] == ((1 << i) ^ ((1 << (i-v)) if v <= i < 2*v else 0))
                for i in range(n)), "scalar endpoint mismatch")
    return dict(cancellation_free_row_l1=maximum, bits=maximum.bit_length(),
                maximum_at=maximum_at, all_columns=n, paid_histogram=dict(sorted(hist.items())))


def negative_controls(records, states, frames):
    """Four mutations exercise scalar, move-rank and copy lifecycle checks."""
    add = next(i for i, r in enumerate(records) if r[0] == 1 and r[5] == 4 and r[1] < 120)
    move = next(i for i, r in enumerate(records) if r[0] == 0)
    copy = next(i for i, r in enumerate(records) if r[0] == 2)
    erase = next(i for i, r in enumerate(records) if r[0] == 3)
    bad_rank = list(records[move]); bad_rank[4] += 1
    bad_copy = list(records[copy]); bad_copy[1] = (bad_copy[1] + 1) % states["n"]
    mutants = {
        "omitted_B_source_ADD": records[:add] + records[add+1:],
        "modified_MOVE_rank": records[:move] + [bad_rank] + records[move+1:],
        "broken_COPY_source": records[:copy] + [bad_copy] + records[copy+1:],
        "missing_ERASE": records[:erase] + records[erase+1:],
    }
    rejected = {}
    for name, mutant in mutants.items():
        try:
            replay(mutant, states, frames)
            replay(mutant, states, frames, reverse=True)
        except Reject as error:
            rejected[name] = str(error)
        else:
            raise Reject("negative control accepted: " + name)
    return rejected


def audit(word_path, output_path):
    output_path.mkdir(parents=True, exist_ok=True)
    # -I ignores PYTHONOPTIMIZE and PYTHONPATH; stock exporter assertions stay on.
    subprocess.run([sys.executable, "-I", "-B", str(EXPORTER), str(word_path), str(output_path)],
                   check=True, stdout=subprocess.DEVNULL)
    records = list(struct.iter_unpack("<6i", (output_path / "249-records.bin").read_bytes()))
    states = json.loads((output_path / "249-states.json").read_text())
    frames = json.loads((output_path / "frames.json").read_text())["frames"]
    forward = replay(records, states, frames)
    reverse = replay(records, states, frames, reverse=True)
    require(forward["paid_histogram"] == reverse["paid_histogram"], "direction profiles differ")
    histogram = forward.pop("paid_histogram")
    reverse.pop("paid_histogram")
    cf, cb = forward["cancellation_free_row_l1"], reverse["cancellation_free_row_l1"]
    # columns_h.cpp: payload = 64 * F^3 * B^2.
    five = 64 * cf**3 * cb**2
    require(five < 2**104, "five-stage payload exceeds inherited bound")
    # global_k.py with K=4: nb=6*(K-1)=18, prefix=2^nb*F^(K+1)*B^K.
    nine = 2**18 * cf**5 * cb**4
    paths = {str(i): [states["initial"][str(i)]] for i in range(states["n"])}
    for op, x, y, c, f, z in records:
        if op == 0:
            paths[str(x)].append(c)
    result = dict(records=len(records),
                  operations=dict(sorted(Counter(r[0] for r in records).items())),
                  adds_by_phase=dict(sorted(Counter(r[5] for r in records if r[0] == 1).items())),
                  forward=forward, reverse=reverse, paid_histogram=histogram,
                  paid_rank_mass=sum(r*z for r, z in histogram.items()),
                  five_stage_payload_bound=str(five), five_stage_payload_bits=five.bit_length(),
                  nine_stage_prefix_bound=str(nine), nine_stage_prefix_bits=nine.bit_length(),
                  nine_stage_charged_prefix_bits=max(192, 64*((nine.bit_length()+63)//64)),
                  negative_controls=negative_controls(records, states, frames))
    return result, paths


def compare(baseline_path, candidate_path, output_path):
    """Write exported records and receipt.json below output_path; return receipt."""
    output_path = Path(output_path)
    base, base_paths = audit(Path(baseline_path), output_path / "baseline-records")
    candidate, candidate_paths = audit(Path(candidate_path), output_path / "candidate-records")
    require(base_paths == candidate_paths, "register frame paths changed")
    require(base["paid_histogram"] == candidate["paid_histogram"], "paid histogram changed")
    sources = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
               for path in (EXPORTER, FIVE_FORMULA, NINE_FORMULA)}
    receipt = dict(status="PASS_LOCAL_SCALAR_PROFILE_AND_PREFIX_AUDIT", same_frame_paths=True,
                   formula_and_exporter_sources=sources, baseline=base, candidate=candidate)
    (output_path / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(args.baseline, args.candidate, args.output), indent=2))
