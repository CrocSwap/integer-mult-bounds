"""Complete census conformance. Produced by Nick Petalas. Apache-2.0."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import (HERE, authenticate, build, comparison_source, compile_text,
                   need, source_bytes)

CASES = ((2, 2), (2, 3), (2, 4), (2, 5), (3, 2), (3, 3), (3, 4),
         (4, 2), (4, 3), (5, 2), (5, 3))


def run(binary, arguments=(), success=True):
    result = subprocess.run([str(binary), *map(str, arguments)],
                            capture_output=True, timeout=120)
    need((result.returncode == 0) == success, "subprocess outcome")
    need(not result.stderr, "unexpected subprocess diagnostics")
    return result.stdout


def mutations(work, kernel):
    changes = (
        ("NEG[product]", "product"),
        ("ADD[gi[0][j]][gi[1][j]]", "gi[0][j]"),
        ("MUL[g[i][request]][gi[request][j]]",
         "MUL[g[request][i]][gi[j][request]]"),
        ("[MUL[g[i][1]][gi[1][j]]]", "[0]"),
    )
    for index, (old, new) in enumerate(changes):
        need(kernel.count(old) == 1, "unique semantic mutation site")
        changed = kernel.replace(old, new, 1)
        binary = compile_text(work, "mutant" + str(index),
                              comparison_source(changed))
        run(binary, success=False)
    return len(changes)


def main():
    need(len(sys.argv) == 1, "no verifier arguments supported")
    source = source_bytes()
    try:
        authenticate(source + b"\n")
    except ValueError:
        pass
    else:
        raise ValueError("source corruption accepted")
    kernel = (HERE / "conjugate.h").read_text()
    with tempfile.TemporaryDirectory(prefix="header-conjugation-") as directory:
        work = Path(directory)
        baseline, candidate = build(work)
        comparisons = []
        for case in CASES:
            before = run(baseline, case)
            after = run(candidate, case)
            need(before == after and before.startswith(b"q="),
                 "complete census output equality")
            comparisons.append(after.decode().strip())
        compare = compile_text(work, "compare", comparison_source(kernel))
        cells = run(compare).decode().strip()
        need(cells.startswith("PASS_CONJUGATION_EQUIVALENCE"), "entry checker")
        killed = mutations(work, kernel)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(HERE.iterdir()) if p.is_file()}
    receipt = {"complete_commands": comparisons, "matrix_entries": cells,
               "semantic_mutations_rejected": killed,
               "source_corruptions_rejected": 1, "package_sha256": hashes}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_LOW_RANK_HEADER_CONJUGATION complete_cases=11 mutations=4")


if __name__ == "__main__":
    main()
