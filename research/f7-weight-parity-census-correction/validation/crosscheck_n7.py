#!/usr/bin/env python3
"""Capped n=7 C/Python cross-check with matching DFS/node semantics.

The Python oracle recomputes every pair-support set from scratch at each novel
prefix. It does not use the C bitsets, incremental pair collision bookkeeping,
or the earlier slow engine's soft budget flags.
"""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def require(condition, detail):
    if not condition:
        raise RuntimeError(detail)


def supports(group):
    return {a ^ b for i, a in enumerate(group) for b in group[i+1:]}


def reference(n, length, split, prefix, cap, even_on=True, odd_on=True):
    s, t = split
    even_budget = s * (s-1) // 2 + t * (t-1) // 2 - ((1 << (n-1))-1)
    odd_budget = s * t - (1 << (n-1))
    out = {"nodes": 0, "candidate_restored_leaves": 0, "hits": 0,
           "even_budget_prunes": 0, "odd_budget_prunes": 0,
           "aborted": False}
    if (even_on and even_budget < 0) or (odd_on and odd_budget < 0):
        return out
    counts = [0] * n

    def visit(depth, q, used, evens, odds):
        if out["aborted"]:
            return
        if cap and out["nodes"] >= cap:
            out["aborted"] = True
            return
        out["nodes"] += 1
        if depth == length:
            if q or used != n or any(c % 2 for c in counts) or len(evens) != s or len(odds) != t:
                return
            out["candidate_restored_leaves"] += 1
            states = evens + odds
            if len({a ^ b for a in states for b in states}) == 1 << n:
                out["hits"] += 1
            return
        if sum(c % 2 for c in counts) + 2 * (n-used) > length-depth:
            return
        candidates = range(min(used+1, n))
        for label in candidates:
            if out["aborted"]:
                return
            if counts[label] >= length - 2 * (n-1):
                continue
            if depth < len(prefix) and label != prefix[depth]:
                continue
            nq = q ^ (1 << label)
            last = depth == length-1
            if last and nq:
                continue
            fresh = not last and nq not in evens and nq not in odds
            e2, o2 = evens, odds
            if fresh:
                if nq.bit_count() % 2:
                    o2 = odds + [nq]
                else:
                    e2 = evens + [nq]
            rem_e = sum(p % 2 == 0 for p in range(depth+2, length))
            rem_o = sum(p % 2 == 1 for p in range(depth+2, length))
            if len(e2) > s or len(o2) > t or len(e2)+rem_e < s or len(o2)+rem_o < t:
                continue
            if fresh:
                e_ex = (len(e2)*(len(e2)-1)//2 - len(supports(e2)) +
                        len(o2)*(len(o2)-1)//2 - len(supports(o2)))
                if even_on and e_ex > even_budget:
                    out["even_budget_prunes"] += 1
                    continue
                odd_ex = len(e2)*len(o2) - len({a ^ b for a in e2 for b in o2})
                if odd_on and odd_ex > odd_budget:
                    out["odd_budget_prunes"] += 1
                    continue
            counts[label] += 1
            visit(depth+1, nq, used+(label == used), e2, o2)
            counts[label] -= 1

    visit(0, 0, 0, [0], [])
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine-source", type=Path, default=HERE.parent / "engine" / "corrected_census.c")
    parser.add_argument("--cap", type=int, default=5000)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    output_dir = args.output_dir or Path(tempfile.mkdtemp(prefix="f7-n7-crosscheck-"))
    output_dir.mkdir(parents=True, exist_ok=True)
    require(args.cap > 0, "cap must be positive")
    cases = [(20, (10, 10)), (20, (10, 9)), (20, (10, 8)),
             (20, (9, 9)), (20, (10, 7)), (18, (9, 9))]
    records = []
    binaries = {}
    for length in (18, 20):
        binary = output_dir / f"corrected_n7_l{length}"
        command = ["cc", "-O2", "-std=c11", "-Wall", "-Wextra", "-Werror", "-DN=7",
                   f"-DL={length}", str(args.engine_source.resolve()), "-o", str(binary)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        binaries[length] = binary
    for length, split in cases:
        for text_prefix in ("0012", "0102", "0123"):
            prefix = tuple(map(int, text_prefix))
            for mode in ("both", "even"):
                expected = reference(7, length, split, prefix, args.cap, odd_on=mode == "both")
                with tempfile.TemporaryDirectory(prefix="n7gate-", dir=output_dir) as temporary:
                    directory = Path(temporary)
                    datafile = directory / "result.json"
                    command = [str(binaries[length]), ",".join(map(str, split)), "--hits", str(directory / "hits.txt"),
                               "--json", str(datafile), "--cap", str(args.cap), text_prefix]
                    if mode == "even":
                        command.append("--no-odd-budget")
                    proc = subprocess.run(command, capture_output=True, text=True)
                    data = json.loads(datafile.read_text())
                actual = data["total"][0]
                for key, value in expected.items():
                    require(actual[key] == value, (length, split, text_prefix, mode, key, actual, expected))
                require(proc.returncode == (2 if expected["aborted"] else 0), (proc, expected))
                require(data["complete"] == (not expected["aborted"]), data)
                records.append({"n": 7, "L": length, "split": list(split), "prefix": text_prefix,
                                "mode": mode, "cap": args.cap, **expected, "pass": True})
    target = output_dir / "n7_crosscheck_results.json"
    target.write_text(json.dumps({"method": __doc__, "runs": records, "pass": True}, indent=2) + "\n")
    print(f"PASS: {len(records)} exact node/leaf/hit/prune-count comparisons; {target}")


if __name__ == "__main__":
    main()
