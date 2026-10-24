#!/usr/bin/env python3
"""Two coordinate 3-cycles cost twelve calls in M_2(F2[GL_3(F2)]).

Standard library only. Needs a C compiler (cc) for the exact search.
The C engine is bound to the merged Python formal model of #4968
(research/swap-component-cut/formal.py) by exact state comparison on random
words, then reproduces distinct-state counts and three known minima before
the main search. The main search is run twice: with the symmetry reduction,
and without it in parallel first-letter shards. No new kappa is claimed.
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
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "two-three-cycle-additivity"
sys.path.insert(0, str(ROOT / "research" / "swap-component-cut"))

import formal  # noqa: E402

COUNTS = {1: 37, 2: 1033, 3: 26551, 4: 663496}
FORWARD_DISTINCT = 16292362


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def pins() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
        need(digest == row["sha256"], "pin " + row["path"])
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.


def compile_engine(directory: Path) -> Path:
    compiler = shutil.which(os.environ.get("CC", "cc")) or shutil.which("gcc")
    need(compiler is not None, "a C11 compiler is required")
    binary = directory / "search"
    done = subprocess.run([compiler, "-std=c11", "-O3", "-Wall", "-Wextra", "-Werror", "-o", str(binary),
                           str(PACKAGE / "search.c")], capture_output=True, text=True)
    need(done.returncode == 0, "compile failed:\n" + done.stderr)
    return binary


def run(binary: Path, *args: str, timeout: int = 900) -> str:
    done = subprocess.run([str(binary), *args], capture_output=True, text=True, timeout=timeout)
    need(done.returncode == 0, f"engine {' '.join(args)} exited {done.returncode}: {done.stderr}")
    return done.stdout


def c_int(group_element) -> int:
    return sum(row << (3 * i) for i, row in enumerate(group_element))


def bind_semantics(binary: Path) -> int:
    model = formal.Model(3, 2)
    rng = random.Random(4968)
    checked = 0
    for length in list(range(0, 7)) * 12:
        word = [rng.randrange(36) for _ in range(length)]
        product = model.diagonal([])
        for g in word:
            product = formal.matrix_product(product, model.generators[g], 2, 3)
        expected = {}
        for i in range(2):
            for j in range(2):
                expected[(i, j)] = sorted(c_int(x) for x in product[i][j])
        got = {}
        for line in run(binary, "dump", *map(str, word)).splitlines():
            match = re.fullmatch(r"entry (\d) (\d):(.*)", line)
            need(match is not None, "dump format")
            got[(int(match[1]), int(match[2]))] = sorted(int(t) for t in match[3].split())
        need(got == expected, f"C and Python products differ on word {word}")
        checked += 1
    return checked


def upper_bound_word() -> None:
    """The 12-call word: a shortest 3-cycle word on each register (projectors E00, E11)."""
    model = formal.Model(3, 2)
    c3 = formal.row_permutation(3, (1, 2, 0))
    cnots = formal.cnots(3)
    lengths = formal.word_lengths(3)
    need(lengths[c3] == 6, "3-cycle has CNOT length six")
    # find a six-letter CNOT word whose formal product is c3
    from itertools import product as words
    word = next(w for w in words(range(6), repeat=6)
                if formal.mul(formal.mul(formal.mul(cnots[w[0]], cnots[w[1]], 3), formal.mul(cnots[w[2]], cnots[w[3]], 3), 3),
                              formal.mul(cnots[w[4]], cnots[w[5]], 3), 3) == c3)
    e00, e11 = 0, 2      # projector order (1,1),(1,3),(2,2),(2,3),(3,1),(3,2)
    calls = [6 * g + e00 for g in word] + [6 * g + e11 for g in word]
    product = model.diagonal([])
    for g in calls:
        product = formal.matrix_product(product, model.generators[g], 2, 3)
    need(product == model.diagonal([c3, c3]) and len(calls) == 12, "twelve-call attaining word")


def parse_result(text: str) -> dict:
    match = re.search(r"RESULT target=(\S+) max_length=(\d+) shortest=(-?\d+) key_matches=(\d+) backward_nodes=(\d+)", text)
    need(match is not None, "result line")
    return dict(target=match[1], max_length=int(match[2]), shortest=int(match[3]),
                key_matches=int(match[4]), nodes=int(match[5]))


def main() -> None:
    pins()
    upper_bound_word()
    with tempfile.TemporaryDirectory() as tmp:
        binary = compile_engine(Path(tmp))
        bound = bind_semantics(binary)
        counts = run(binary, "count", "4")
        for depth, value in COUNTS.items():
            need(f"depth<={depth} distinct={value}" in counts, f"distinct states at depth <= {depth}")
        for target in ("c3e", "s01s12", "s01s01"):
            short = parse_result(run(binary, target, "3", "2"))
            need(short["shortest"] == -1 and short["key_matches"] == 0, f"{target}: nothing at length <= 5")
            six = parse_result(run(binary, target, "3", "3"))
            need(six["shortest"] == 6, f"{target}: shortest length six found")
        main_run = run(binary, "c3c3", "5", "6", "sym")
        need("symmetries=36 first_letters=1 mode=sym" in main_run, "symmetry group and orbit representatives")
        need(f"forward_depth=5 distinct={FORWARD_DISTINCT}" in main_run, "forward ball size")
        reduced = parse_result(main_run)
        need(reduced["shortest"] == -1 and reduced["key_matches"] == 0, "no word of length <= 11 (symmetry-reduced)")
        # Symmetry-free confirmation: every first letter, in parallel shards.
        shards = min(9, max(1, (os.cpu_count() or 1)))
        bounds = [round(36 * k / shards) for k in range(shards + 1)]
        processes = [subprocess.Popen([str(binary), "c3c3", "5", "6", "nosym", str(lo), str(hi)],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                     for lo, hi in zip(bounds, bounds[1:]) if lo < hi]
        letters = matches = 0
        for process in processes:
            out, err = process.communicate(timeout=1500)
            need(process.returncode == 0, "nosym shard failed: " + err)
            letters += int(re.search(r"first_letters=(\d+)", out)[1])
            result = parse_result(out)
            need(result["shortest"] == -1, "nosym shard found a short word")
            matches += result["key_matches"]
        need(letters == 36 and matches == 0, "symmetry-free search covers all 36 first letters with no key match")
    print(f"PASS_TWO_THREE_CYCLE_ADDITIVITY shortest=12 no_word_le_11 semantics_bound={bound} "
          f"forward_distinct={FORWARD_DISTINCT} nosym_shards={len(processes)} no_new_kappa")


if __name__ == "__main__":
    main()
