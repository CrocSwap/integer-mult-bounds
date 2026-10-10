#!/usr/bin/env python3
"""Check the prose against the artifacts.

The two documents in this directory quote a lot of exact numbers. This script
reads every value out of the three artifacts (`beats.json` for the five-family
screen, `beats-six.json` for six, `instantiate.json` for the bank-rung analysis)
and checks two things:

* every number of six or more digits written in a markdown **table row** matches a
  value of the artifact it belongs to, within a relative `2e-12` (the documents
  render 14-15 significant digits), and
* a list of required headline claims is still present, so a rewrite cannot quietly
  drop the values the package is about.

    python3 -B check_docs.py
"""
import json
import re
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOCS = {
    "README.md": ("beats.json", "beats-six.json"),
    "INSTANTIATE.md": ("instantiate.json", "beats.json"),
}
REQUIRED = {
    "README.md": [
        "6.831904550365e-4",       # the certificate's own kappa
        "6.831904550366e-4",       # this package's ladder zero point
        "6.83657523331095e-4",     # a_bit
        "7.00918443859411e-4",     # a_complex
        "1.4e-16", "2.1e-13",      # the a_bit residual
        "+2.167%", "+2.523%", "+3.674%",
        "6.979968750671e-4", "7.004275013051e-4", "7.082915705907e-4",
        "1.3783316708213e-3",      # five-family best rung
        "1.52739614292328e-3",     # six-family bit top
        "2.30539885681005e-3",     # six-family complex top
        "1.5250667618335e-3",      # six-family best rung
        "3,512", "3,502", "991", "10,318", "2,725",
        "9 new residual types", "11 new residual types", "33,261",
        "SOURCE.json",             # the pin hashes are verified at run time
    ],
    "INSTANTIATE.md": [
        "12,096", "4,032", "1,008", "336", "72,576", "55,394", "56,402",
        "4,055,136", "3,982,560", "5,808",
        "6.98484415006068e-4", "6.979968750671e-4", "+2.1672%",
        "2,200", "5,500", "396,000", "144", "112",
        "coordinated-bank-proof.md",
    ],
}


def values(path):
    """Every exact value an artifact carries, as floats."""
    found = []
    def walk(node):
        if isinstance(node, dict):
            for item in node.values():
                walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, str):
            try:
                found.append(float(Q(node)))
            except Exception:
                pass
        elif isinstance(node, (int, float)) and not isinstance(node, bool):
            found.append(float(node))
    walk(json.loads(path.read_text()))
    return found


def main():
    artifacts = {name: values(HERE / name)
                 for name in {n for names in DOCS.values() for n in names}}
    problems, checked = [], 0
    for doc, sources in DOCS.items():
        text = (HERE / doc).read_text(encoding="utf-8")
        pool = [v for name in sources for v in artifacts[name]]
        for raw in text.splitlines():
            if not raw.startswith("|"):
                continue
            line = re.sub(r"`[^`]*`", " ", raw)
            line = re.sub(r"(?<=\d),(?=\d{3}\b)", "", line)     # 33,261 -> 33261
            for token in re.findall(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", line):
                if re.search(re.escape(token) + r"\s*%", line):
                    continue                                    # a gain percentage
                if len(re.sub(r"\D", "", token.split("e")[0].split("E")[0])) <= 5:
                    continue                                    # family/type counts
                value = float(token)
                checked += 1
                if not any(abs(value - v) <= max(abs(v), abs(value)) * 2e-12
                           for v in pool):
                    problems.append(f"{doc}: table number {token!r} matches no value "
                                    f"in {'/'.join(sources)}")
        for claim in REQUIRED[doc]:
            if claim not in text:
                problems.append(f"{doc}: required claim {claim!r} is missing")
    print(f"checked {checked} table numbers and "
          f"{sum(len(v) for v in REQUIRED.values())} required claims "
          f"against {len(artifacts)} artifacts")
    if problems:
        print("MISMATCHES:")
        for line in problems:
            print("  -", line)
        return 1
    print("every quoted number and required claim matches the artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
