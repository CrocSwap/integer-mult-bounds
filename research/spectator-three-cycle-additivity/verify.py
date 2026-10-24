#!/usr/bin/env python3
"""Two coordinate 3-cycles with a spectator address coordinate cost twelve calls.

Standard library only. Needs a C compiler (cc) for the exact search.
The sparse C engine for M_2(F2[GL_4(F2)]) is bound to the merged Python
formal model (research/swap-component-cut/formal.py, n = 4, R = 2) by exact
state comparison on random words. It then reproduces distinct-state counts
and known minima before the main search.

Default mode (the registered replay) proves the length <= 9 exclusion
(depth 4 + 5). `--full` reruns the recorded local receipts: depth 4 + 6
(length <= 10, about a minute on 16 cores) and depth 5 + 6 (length <= 11,
the exact result; about 8 GB of memory). No new kappa is claimed.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "spectator-three-cycle-additivity"
sys.path.insert(0, str(ROOT / "research" / "swap-component-cut"))

import formal  # noqa: E402

COUNTS = {1: 73, 2: 4297, 3: 240565, 4: 13231207}
CONTROLS = (("c3e", 6), ("s01s01", 6))


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def pins() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
        need(digest == row["sha256"], "pin " + row["path"])
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    need(selected["kappa"] == "15108879/5000000000", "selected kappa (PR4610 frontier)")
    result = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    source = hashlib.sha256((PACKAGE / "search.c").read_bytes()).hexdigest()
    need(all(run["search_c_sha256"] == source for run in result["local_runs"]),
         "recorded local runs used this search.c")


def compile_engine(directory: Path) -> Path:
    compiler = shutil.which(os.environ.get("CC", "cc")) or shutil.which("gcc")
    need(compiler is not None, "a C11 compiler is required")
    binary = directory / "search"
    done = subprocess.run([compiler, "-std=c11", "-O3", "-Wall", "-Wextra", "-Werror", "-o", str(binary),
                           str(PACKAGE / "search.c")], capture_output=True, text=True)
    need(done.returncode == 0, "compile failed:\n" + done.stderr)
    return binary


def run(binary: Path, *args: str, timeout: int = 4 * 3600) -> str:
    done = subprocess.run([str(binary), *args], capture_output=True, text=True, timeout=timeout)
    need(done.returncode == 0, f"engine {' '.join(args)} exited {done.returncode}: {done.stderr}")
    return done.stdout


def c_int(group_element) -> int:
    return sum(row << (4 * i) for i, row in enumerate(group_element))


def bind_semantics(binary: Path) -> int:
    model = formal.Model(4, 2)
    need(len(model.generators) == 72, "72 paid factors")
    rng = random.Random(4974)
    checked = 0
    for length in list(range(0, 6)) * 6:
        word = [rng.randrange(72) for _ in range(length)]
        state = model.diagonal([])
        for g in word:
            state = formal.matrix_product(state, model.generators[g], 2, 4)
        expected = {(i, j): sorted(c_int(x) for x in state[i][j]) for i in range(2) for j in range(2)}
        got = {}
        for line in run(binary, "dump", *map(str, word)).splitlines():
            match = re.fullmatch(r"entry (\d) (\d):(.*)", line)
            need(match is not None, "dump format")
            got[(int(match[1]), int(match[2]))] = sorted(int(t) for t in match[3].split())
        need(got == expected, f"C and Python products differ on word {word}")
        checked += 1
    return checked


def upper_bound_word() -> None:
    """Twelve calls: a shortest 3-cycle CNOT word on register 0, then on register 1."""
    model = formal.Model(4, 2)
    c3 = formal.row_permutation(4, (1, 2, 0, 3))
    cnots = formal.cnots(4)
    need(formal.word_lengths(4)[c3] == 6, "3-cycle has CNOT length six in GL_4")
    word = None
    for w in product(range(12), repeat=6):
        g = formal.identity(4)
        for k in w:
            g = formal.mul(g, cnots[k], 4)
        if g == c3:
            word = w
            break
    need(word is not None, "six-letter 3-cycle word")
    projectors = [(u, v) for u in range(1, 4) for v in range(1, 4) if bin(u & v).count("1") % 2]
    e00, e11 = projectors.index((1, 1)), projectors.index((2, 2))
    calls = [6 * g + e00 for g in word] + [6 * g + e11 for g in word]
    state = model.diagonal([])
    for g in calls:
        state = formal.matrix_product(state, model.generators[g], 2, 4)
    need(state == model.diagonal([c3, c3]) and len(calls) == 12, "twelve-call attaining word")


def parse_result(text: str) -> dict:
    match = re.search(r"RESULT target=(\S+) max_length=(\d+) shortest=(-?\d+) key_matches=(\d+) backward_nodes=(\d+)", text)
    need(match is not None, "result line")
    return dict(target=match[1], max_length=int(match[2]), shortest=int(match[3]),
                key_matches=int(match[4]), nodes=int(match[5]))


def main() -> None:
    full = "--full" in sys.argv[1:]
    workers = str(min(16, max(1, os.cpu_count() or 1)))
    pins()
    upper_bound_word()
    with tempfile.TemporaryDirectory() as tmp:
        binary = compile_engine(Path(tmp))
        bound = bind_semantics(binary)
        need("selftest commuting_ordered_pairs=1584 ball2=4297 verified_words=12" in run(binary, "selftest"),
             "commuting pairs, exact radius-two ball and distance-five verification")
        counts = run(binary, "count", "4", "26")
        for depth, value in COUNTS.items():
            need(f"depth<={depth} distinct={value}" in counts, f"distinct states at depth <= {depth}")
        for target, cost in CONTROLS:
            for mode in ("sym", "nosym"):
                short = parse_result(run(binary, target, "3", "2", mode, workers, "24"))
                need(short["shortest"] == -1 and short["key_matches"] == 0, f"{target} {mode}: nothing at length <= 5")
                found = parse_result(run(binary, target, "3", "3", mode, workers, "24"))
                need(found["shortest"] == cost, f"{target} {mode}: shortest length {cost} found")
        nosym = parse_result(run(binary, "c3c3", "3", "3", "nosym", workers, "24"))
        need(nosym["shortest"] == -1 and nosym["key_matches"] == 0, "c3c3: nothing at length <= 6 without symmetry")
        mixed = parse_result(run(binary, "c3s01", "4", "4", "sym", workers, "26"))
        need(mixed["shortest"] == -1, "c3s01: nothing at length <= 8")
        main_run = run(binary, "c3c3", "4", "5", "sym", workers, "26")
        need("symmetries=36 pairs=142 mode=sym" in main_run, "symmetry group and pair representatives")
        need(f"forward_depth=4 distinct={COUNTS[4]}" in main_run, "forward depth-four ball")
        need(parse_result(main_run)["shortest"] == -1, "no word of length <= 9")
        proved = 9
        if full:
            for fwd, bwd, length, bits in (("4", "6", 10, "27"), ("5", "6", 11, "30")):
                out = parse_result(run(binary, "c3c3", fwd, bwd, "sym", workers, bits))
                need(out["shortest"] == -1, f"no word of length <= {length}")
                proved = length
    print(f"PASS_SPECTATOR_THREE_CYCLE_ADDITIVITY upper=12 no_word_le_{proved} semantics_bound={bound} "
          f"recorded_local_no_word_le_11 no_new_kappa")


if __name__ == "__main__":
    main()
