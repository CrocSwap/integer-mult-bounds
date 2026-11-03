#!/usr/bin/env python3
"""Reject concrete counterfactuals in private package copies, in both Python modes."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
FILES = ("verify.py", "pricing.py", "checks.py", "execution.py", "oracles.py", "rank12.py", "recursive_dispatch.py",
         "CASES.json", "RESULT.json", "SOURCES.json", "source/6658-README.md",
         "source/6658-PROOF.md", "source/LICENSE", "source/4507-batches.py", "source/4507-RESULT.json")

# (name, file, exact substitution, expected scientific rejection)
FAULTS = [
    ("record ties", "pricing.py", "price < records[-1][1]", "price <= records[-1][1]",
     "aggregate Pareto records"),
    ("ignore productive width", "pricing.py", "/ (parent*a)", "/ a",
     "aggregate Pareto records"),
    ("gcd alone admits cheapest fill", "pricing.py", "if all(m.cheap_counts(a*q) is not None for q, m in cuts):",
     "if True:", "aggregate Pareto records"),
    ("apply tail below its anchor", "pricing.py", "if n >= label.size:", "if True:",
     "aggregate Pareto records"),
    ("size before price", "pricing.py", "value < (old.loss, old.size)", "value[1] < old.size",
     "least common onset"),
    ("wrong width in witness", "pricing.py", "counts[self.best[0]] += (n - label.size)",
     "counts[0] += (n - label.size)", "witness fills the wrong cut"),
    ("fabricate unreachable label", "pricing.py", "label = self.refined[n % self.anchor]",
     "label = self.refined[n % self.anchor] or self.refined[0]", "aggregate Pareto records"),
    ("ignore q in period", "pricing.py", "period = lcm(*(m.h // gcd(m.h, q) for q, m in cuts))",
     "period = lcm(*(m.h for q, m in cuts))", "nonminimal excess period"),
    ("discard tied cheapest widths", "pricing.py", "self.h = gcd(*cheap)", "self.h = cheap[0]",
     "nonminimal excess period"),
    ("max of separate onsets", "pricing.py", "    validate_cuts(cuts, 1)\n    accessible",
     "    if len(cuts) > 1:\n        return max(first_periodic_replication([cut]) for cut in cuts)\n"
     "    validate_cuts(cuts, 1)\n    accessible", "least common onset"),
    ("truncate fractional price", "pricing.py", "tuple(Fraction(c) for _, c in rows)",
     "tuple(Fraction(int(c)) for _, c in rows)", "aggregate Pareto records"),
    ("misplace last exception", "pricing.py", "return last_bad + 1", "return last_bad",
     "least common onset"),
    ("drop dispatch fee", "execution.py", "charges += 1\n                for i",
     "charges += 0\n                for i", "observed dispatch and addition bill"),
    ("damage dirty endpoint", "execution.py", "xs[i] += ys[i]", "xs[i] += ys[i]\n                    dirty[i] += 1",
     "incomplete chronological endpoint"),
    ("pool source cut copies", "rank12.py", 'counts[cut["rank"], cut["count"]] += cut["copies"]',
     'counts[cut["rank"], cut["count"]*cut["copies"]] += 1', "rank-12 base"),
    ("drop repeated dispatches", "rank12.py", "dispatches += copies * (big+narrow)",
     "dispatches += big+narrow", "rank-12 dispatch plateau"),
    ("omit recursive program root", "recursive_dispatch.py", "fees.append(1 + sum(",
     "fees.append(sum(", "literal recursive node inventory"),
    ("pool recursive cut copies", "recursive_dispatch.py", "children[child] += copies * count",
     "children[child] += count", "recursive leaves disagree with retained compiler"),
    ("change source", "source/6658-PROOF.md", "## 5. Cost boundary", "## 5. Modified cost boundary",
     "retained source hash"),
    ("change result", "RESULT.json", '"amount_targets": 50127', '"amount_targets": 50128',
     "stored research result differs"),
]


def invoke(tmp, optimized):
    mode = ["-O"] if optimized else []
    return subprocess.run([sys.executable, "-I", *mode, "-W", "error", "-B", str(tmp / "verify.py")],
                          cwd=tmp, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, encoding="utf-8", timeout=90)


def audit():
    rejected = []
    with tempfile.TemporaryDirectory(prefix="width-fee-") as tmp:
        copy = Path(tmp)
        for name in FILES:
            (copy/name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PACKAGE/name, copy/name)
        receipts = []
        for optimized in (False, True):
            control = invoke(copy, optimized)
            if control.returncode:
                raise RuntimeError(control.stderr[-1000:])
            receipts.append(json.loads(control.stdout))
        if receipts[0] != receipts[1] or receipts[0]["status"] != "PASS_PRICED_WIDTH_FRONTIER":
            raise ValueError("positive private-copy controls")
        for name, file, old, new, reason in FAULTS:
            path = copy/file
            original = path.read_bytes()
            if original.count(old.encode()) != 1:
                raise ValueError("ambiguous fault target " + name)
            path.write_bytes(original.replace(old.encode(), new.encode()))
            for optimized in (False, True):
                outcome = invoke(copy, optimized)
                last = outcome.stderr.strip().splitlines()[-1:] or [""]
                if outcome.returncode == 0 or last[0] != "ValueError: " + reason:
                    raise ValueError(f"{name} optimized={optimized} expected {reason!r}, got {last[0]!r}")
                rejected.append([name, optimized, reason])
            path.write_bytes(original)
    return dict(status="PASS_PRICED_WIDTH_MUTATIONS", rejections=len(rejected), tests=rejected)


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
