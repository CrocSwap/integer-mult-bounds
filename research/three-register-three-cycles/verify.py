#!/usr/bin/env python3
"""Two coordinate 3-cycles with a dirty third register: no word of length <= 10.

Standard library only. Needs a C compiler (cc) for the exact search.
The C engine is bound to the merged Python formal model of #4968
(research/swap-component-cut/formal.py) at R = 3 by exact state comparison
on random words, then reproduces distinct-state counts, the merged radius-two
ball of research/gl3-order7-dirty-register-seed39ae and four known minima.

Default mode (the registered replay) proves the length <= 8 exclusion
(depth 3 + 5). `--full` reruns the recorded local receipts: depth 4 + 5
(length <= 9, about 2 minutes on 16 cores) and depth 4 + 6 (length <= 10,
about an hour on 16 cores, 9 GB of memory). No new kappa is claimed.
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
PACKAGE = ROOT / "research" / "three-register-three-cycles"
sys.path.insert(0, str(ROOT / "research" / "swap-component-cut"))

import formal  # noqa: E402

COUNTS = {1: 169, 2: 22051, 3: 2705791}
FORWARD4 = 325910698
CONTROLS = ("c3ee", "c7c7e", "s01s01e")


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


def run(binary: Path, *args: str, timeout: int = 7200) -> str:
    done = subprocess.run([str(binary), *args], capture_output=True, text=True, timeout=timeout)
    need(done.returncode == 0, f"engine {' '.join(args)} exited {done.returncode}: {done.stderr}")
    return done.stdout


def c_int(group_element) -> int:
    return sum(row << (3 * i) for i, row in enumerate(group_element))


def bind_semantics(binary: Path) -> int:
    model = formal.Model(3, 3)
    need(len(model.generators) == 168, "168 paid factors")
    rng = random.Random(5005)
    checked = 0
    for length in list(range(0, 6)) * 6:
        word = [rng.randrange(168) for _ in range(length)]
        product = model.diagonal([])
        for g in word:
            product = formal.matrix_product(product, model.generators[g], 3, 3)
        expected = {(i, j): sorted(c_int(x) for x in product[i][j]) for i in range(3) for j in range(3)}
        got = {}
        for line in run(binary, "dump", *map(str, word)).splitlines():
            match = re.fullmatch(r"entry (\d) (\d):(.*)", line)
            need(match is not None, "dump format")
            got[(int(match[1]), int(match[2]))] = sorted(int(t) for t in match[3].split())
        need(got == expected, f"C and Python products differ on word {word}")
        checked += 1
    return checked


def upper_bound_word() -> None:
    """Twelve calls: a shortest 3-cycle word on register 0, then on register 1."""
    model = formal.Model(3, 3)
    c3 = formal.row_permutation(3, (1, 2, 0))
    cnots = formal.cnots(3)
    need(formal.word_lengths(3)[c3] == 6, "3-cycle has CNOT length six")
    from itertools import product as words
    word = next(w for w in words(range(6), repeat=6)
                if formal.mul(formal.mul(formal.mul(cnots[w[0]], cnots[w[1]], 3), formal.mul(cnots[w[2]], cnots[w[3]], 3), 3),
                              formal.mul(cnots[w[4]], cnots[w[5]], 3), 3) == c3)
    projectors = [(u, v) for u in range(1, 8) for v in range(1, 8) if bin(u & v).count("1") % 2]
    e00, e11 = projectors.index((1, 1)), projectors.index((2, 2))
    calls = [28 * g + e00 for g in word] + [28 * g + e11 for g in word]
    product = model.diagonal([])
    for g in calls:
        product = formal.matrix_product(product, model.generators[g], 3, 3)
    need(product == model.diagonal([c3, c3]) and len(calls) == 12, "twelve-call attaining word")


def odd_relation() -> None:
    """Parity cannot help: the five calls 0, 28, 84, 0, 84 multiply to I (labels C01 C02 C12 C01 C12)."""
    model = formal.Model(3, 3)
    product = model.diagonal([])
    for g in (0, 28, 84, 0, 84):
        product = formal.matrix_product(product, model.generators[g], 3, 3)
    need(product == model.diagonal([]), "odd relation of length five")


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
    odd_relation()
    with tempfile.TemporaryDirectory() as tmp:
        binary = compile_engine(Path(tmp))
        bound = bind_semantics(binary)
        need("selftest children=33600 ok ball2=22051 verified_words=400" in run(binary, "selftest"),
             "batched fingerprints and exact radius-two verification")
        need("commuting_ordered_pairs=9912 of 28056" in run(binary, "commute"), "commuting pairs")
        counts = run(binary, "count", "3", "23")
        for depth, value in COUNTS.items():
            need(f"depth<={depth} distinct={value}" in counts, f"distinct states at depth <= {depth}")
        for target in CONTROLS:
            for mode in ("sym", "nosym"):
                short = parse_result(run(binary, target, "3", "2", mode, workers, "23"))
                need(short["shortest"] == -1 and short["key_matches"] == 0, f"{target} {mode}: nothing at length <= 5")
                six = parse_result(run(binary, target, "3", "3", mode, workers, "23"))
                need(six["shortest"] == 6, f"{target} {mode}: shortest length six found")
        deep = parse_result(run(binary, "c3ee", "3", "4", "sym", workers, "23"))
        need(deep["shortest"] == 6, "c3ee found with a depth-four backward search")
        nosym = parse_result(run(binary, "c3c3e", "3", "3", "nosym", workers, "23"))
        need(nosym["shortest"] == -1 and nosym["key_matches"] == 0, "c3c3e: nothing at length <= 6 without symmetry")
        main_run = run(binary, "c3c3e", "3", "5", "sym", workers, "23")
        need("symmetries=36 first_letters=7 pairs=827 mode=sym" in main_run, "symmetry group and pair representatives")
        reduced = parse_result(main_run)
        need(reduced["shortest"] == -1, "no word of length <= 8")
        proved = 8
        if full:
            for bwd, length in (("5", 9), ("6", 10)):
                out = run(binary, "c3c3e", "4", bwd, "sym", workers, "30", timeout=4 * 3600)
                need(f"forward_depth=4 distinct={FORWARD4}" in out, "forward depth-four ball size")
                need(parse_result(out)["shortest"] == -1, f"no word of length <= {length}")
                proved = length
    print(f"PASS_THREE_REGISTER_THREE_CYCLES upper=12 no_word_le_{proved} semantics_bound={bound} "
          f"recorded_local_no_word_le_10 no_new_kappa")


if __name__ == "__main__":
    main()
