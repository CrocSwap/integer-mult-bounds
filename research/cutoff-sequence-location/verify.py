#!/usr/bin/env python3
"""Location of the two complex bootstrap cutoff sequences.

The checker reads the frozen assembler. It does not recompute the fourteen stages.
"""

import hashlib
import json
import tarfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_CUTOFF_SEQUENCE_LOCATION calls=2 complex_binds=true no_new_kappa"
ASSEMBLY = "research/community-frontier1094-audit/ASSEMBLY.json"
TARBALL = "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz"
FACTS = {
    206: "eta=beta=Q(1,10**24);s=min(c,(1-beta)*bb)-Q(1,10**27);assert 0<s<c and s<(1-beta)*bb",
    221: "conservative_k,conservative_cuts,conservative_outer,conservative_controls=outer_witness(conservative_b)",
    225: "native_moments=check_moment('complex',H,73,owner['live'],b,5120,False)",
    226: "k,cuts,outer,controls=outer_witness(b)",
}


def fail(message):
    raise SystemExit("FAIL_CUTOFF_SEQUENCE_LOCATION " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(
        set(pinned) == {ASSEMBLY, TARBALL},
        "input inventory changed",
    )
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000", "decimal": "0.001672660197076918"}
    receipt = json.loads((ROOT / ASSEMBLY).read_text(encoding="utf-8"))
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    require(selected["decimal"] == receipt["kappa_decimal"] == "0.001672660197076918", "the selected decimal moved")
    with tarfile.open(ROOT / TARBALL, "r:gz") as archive:
        member = archive.extractfile("code/assemble.py").read().decode("utf-8")
        mentions = 0
        python_files = 0
        for item in archive.getmembers():
            if item.name.endswith(".py"):
                python_files += 1
                text = archive.extractfile(item).read().decode("utf-8", "replace")
                mentions += text.count("cuts.append") + text.count("cutoff_log2")
    lines = member.splitlines()
    for number, text in FACTS.items():
        require(lines[number - 1].strip() == text, "a source line moved")
    require(member.count("cuts.append") == 1, "the append site count moved")
    calls = [index + 1 for index, line in enumerate(lines) if "outer_witness(" in line and "def outer_witness" not in line]
    require(calls == [221, 226], "the witness calls moved")
    require(sum("def outer_witness" in line for line in lines) == 1, "the witness definition moved")
    require("bootstrap=cuts" in member and "conservative_bootstrap=conservative_cuts" in member, "an emitted sequence moved")
    require(member.count("check_moment('complex',H,73,") == 1, "the native pricing moved")
    require(member.count("check_moment('conservative_complex',H,73,") == 1, "the conservative pricing moved")
    require(python_files == 57 and mentions == 2, "the archive scan moved")
    beta = Fraction(1, 10 ** 24)
    bit_lower = Fraction(receipt["bit_lower"])
    require((1 - beta) * Fraction(receipt["complex_lower"]) < bit_lower, "the native complex lower does not bind")
    require((1 - beta) * Fraction(receipt["conservative_complex_lower"]) < bit_lower, "the conservative complex lower does not bind")
    return {
        "append_sites": 1,
        "witness_calls": 2,
        "python_files": python_files,
        "cutoff_mentions": mentions,
        "complex_binds": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
