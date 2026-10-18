"""Build five Lean roots and reject four weakened contracts in the pinned environment."""

import argparse
import re
import subprocess
import tempfile
from pathlib import Path

from verify import PACKAGE, ROOT, authenticate, read_json, require

ROOTS = (
    "mixing_mul",
    "mixing_rank_mul_le",
    "word_rank_le",
    "moment_lower_bound",
    "word_moment_le",
)
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}


def execute(project, source):
    return subprocess.run(
        ["lake", "env", "lean", "-DwarningAsError=true", str(source)],
        cwd=project,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )


def check_project(project):
    sources = read_json(PACKAGE / "SOURCES.json")
    for item in sources["files"]:
        if item["path"].startswith("formal/lean/"):
            suffix = Path(item["path"]).relative_to("formal/lean")
            require(
                (project / suffix).read_bytes() == (ROOT / item["path"]).read_bytes(),
                "alternate formal project differs from pin",
            )
    version = subprocess.run(
        ["lake", "env", "lean", "--version"],
        cwd=project,
        text=True,
        capture_output=True,
        timeout=60,
        check=True,
    )
    require("version 4.21.0," in version.stdout, "Lean version")
    revision = subprocess.run(
        ["git", "-C", str(project / ".lake/packages/mathlib"), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        timeout=30,
        check=True,
    )
    require(
        revision.stdout.strip() == "308445d7985027f538e281e18df29ca16ede2ba3",
        "actual Mathlib source revision",
    )


def check_roots(output):
    reports = re.findall(
        r"'EndpointRank\.(\w+)' depends on axioms: \[([^]]*)\]", output
    )
    require(len(reports) == len(ROOTS), "five actual axiom reports")
    require({name for name, _ in reports} == set(ROOTS), "exact theorem roots")
    for name, axioms in reports:
        require(set(axioms.split(", ")) <= ALLOWED, "unexpected axiom in " + name)


def negative_controls(project, source):
    mutations = (
        (
            "false rank additivity",
            "≤ (mixing U).rank + (mixing V).rank",
            "= (mixing U).rank + (mixing V).rank",
        ),
        (
            "missing child charge",
            "hcharge : ∀ U ∈ word, (mixing U).rank ≤ charge U",
            "hcharge : ∀ U ∈ word, True",
        ),
        (
            "reversed rank budget",
            "hbudget : target ≤ ranks.sum",
            "hbudget : ranks.sum ≤ target",
        ),
        ("wrong exponent regime", "hp1 : p ≤ 1", "hp1 : 1 ≤ p"),
    )
    with tempfile.TemporaryDirectory(prefix="endpoint-rank-lean-") as directory:
        for number, (label, old, new) in enumerate(mutations):
            require(old in source, "control matches source")
            path = Path(directory) / f"Invalid{number}.lean"
            path.write_text(source.replace(old, new), encoding="utf-8")
            result = execute(project, path)
            diagnostic = result.stdout + result.stderr
            require(
                result.returncode != 0 and ": error:" in diagnostic,
                "invalid formal contract accepted: " + label,
            )
            require(
                "type mismatch" in diagnostic.lower() or "tactic" in diagnostic.lower(),
                "control failed outside proof elaboration: " + label,
            )
    return len(mutations)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=ROOT / "formal/lean")
    args = parser.parse_args()
    authenticate()
    project = args.project.resolve()
    check_project(project)
    source = PACKAGE / "EndpointRank.lean"
    result = execute(project, source)
    require(result.returncode == 0, result.stdout + result.stderr)
    check_roots(result.stdout)
    count = negative_controls(project, source.read_text(encoding="utf-8"))
    print(result.stdout, end="")
    print(f"PASS_ENDPOINT_RANK_LEAN roots={len(ROOTS)} invalid_contracts={count}")


if __name__ == "__main__":
    main()
