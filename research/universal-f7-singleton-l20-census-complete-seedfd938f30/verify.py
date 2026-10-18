#!/usr/bin/env python3
"""Verification driver for the PR2634 census audit package.

Quick mode (default, ~2 s): compiles f7_census.c and checks the ten small
shards plus the four 5,000,000-node capped probes against AUDIT-RESULT.json.
Full mode (--full, ~3 min): runs the complete 15-shard census and checks
every shard count and the totals.

Standard library only; requires a C compiler with unsigned __int128.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULT = json.loads((HERE / "AUDIT-RESULT.json").read_text(encoding="utf-8"))

SHARD_LINE = re.compile(
    r"SHARD (\S+) nodes=(\d+) leaves=(\d+) hits=(\d+)")


def build(workdir):
    exe = Path(workdir) / "f7_census"
    subprocess.run(
        ["cc", "-O2", "-o", str(exe), str(HERE / "f7_census.c")],
        check=True)
    return exe


def run_shards(exe, workdir, specs):
    out = {}
    for spec in specs:
        proc = subprocess.run([str(exe), spec], cwd=workdir, check=True,
                              capture_output=True, text=True)
        m = SHARD_LINE.search(proc.stdout)
        assert m, f"no SHARD line for {spec}: {proc.stdout!r}"
        key = m.group(1)
        out[key] = dict(nodes=int(m.group(2)), leaves=int(m.group(3)),
                        hits=int(m.group(4)))
    return out


def main():
    full = "--full" in sys.argv
    with tempfile.TemporaryDirectory() as workdir:
        exe = build(workdir)

        # Capped probes: exact agreement with the reference engine's
        # max_nodes semantics, including label-3 prefix territory.
        probes = {p["prefix"]: p for p in
                  RESULT["cross_validation"]
                  ["capped_probe_agreement_max_nodes_5000000"]}
        got = run_shards(exe, workdir,
                         [f"{k}:5000000" for k in sorted(probes)])
        for k, want in probes.items():
            g = got[k]
            assert (g["nodes"], g["leaves"], g["hits"]) == (
                want["nodes"], want["leaves"], want["hits"]), (k, g, want)

        # Small completed shards (instant).
        small = [k for k, v in RESULT["cross_validation"]
                 ["completed_shards_reproduced_exactly"].items()
                 if v["nodes"] < 100]
        want_small = RESULT["cross_validation"][
            "completed_shards_reproduced_exactly"]
        got = run_shards(exe, workdir, small)
        for k in small:
            w = want_small[k]
            g = got[k]
            assert (g["nodes"], g["leaves"], g["hits"]) == (
                w["nodes"], w["leaves"], w["hits"]), (k, g, w)

        if full:
            all_shards = sorted(
                set(RESULT["cross_validation"]
                    ["completed_shards_reproduced_exactly"])
                | set(RESULT["new_shard_results"]))
            want_all = dict(RESULT["cross_validation"]
                            ["completed_shards_reproduced_exactly"])
            want_all.update(RESULT["new_shard_results"])
            got = run_shards(exe, workdir, all_shards)
            tn = tl = th = 0
            for k in all_shards:
                w = want_all[k]
                g = got[k]
                assert (g["nodes"], g["leaves"], g["hits"]) == (
                    w["nodes"], w["leaves"], w["hits"]), (k, g, w)
                tn += g["nodes"]
                tl += g["leaves"]
                th += g["hits"]
            tot = RESULT["census_total_15_of_15_shards"]
            assert tn == tot["nodes"], (tn, tot)
            assert tl == tot["simple_20_cycles"], (tl, tot)
            assert th == tot["universal_words"], (th, tot)

    mode = "FULL" if full else "QUICK"
    print(f"PASS_F7_L20_CENSUS_AUDIT_{mode} "
          f"nodes={RESULT['census_total_15_of_15_shards']['nodes']} "
          f"cycles={RESULT['census_total_15_of_15_shards']['simple_20_cycles']} "
          f"universal_words=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
