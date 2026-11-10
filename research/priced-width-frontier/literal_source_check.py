#!/usr/bin/env python3
"""Rebuild both invoices from literal #4507 paths without calling its compiler or the menu solver."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from math import gcd, lcm
from pathlib import Path
from runpy import run_path
import sys

PACKAGE = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def literal_enumerator():
    pins = {"4507-batches.py": "73e7ab4a1925ee7d412d0f2b5d28b70f3a9e43e427c2ec6f6d89f193b84655ef",
            "4507-verify.py": "ce4fd4854662cdfb3dbcc892aeec5f4c30f229f4138b48d47f4637099d575998"}
    for name, digest in pins.items():
        require(sha256((PACKAGE/"source"/name).read_bytes()).hexdigest() == digest, "literal source binding")

    def blocked(*args, **kwargs):
        raise RuntimeError("compressed compiler called from literal check")

    spec = spec_from_file_location("batches", PACKAGE/"source/4507-batches.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in ("compile_widths", "direct_flow", "requirements", "check_batches", "multiplier"):
        setattr(module, name, blocked)
    sys.modules["batches"] = module
    return run_path(str(PACKAGE/"source/4507-verify.py"))["literal_flow"]


def literal_cuts():
    enumerate_flow = literal_enumerator()
    records = {}
    for n in range(3, 13):
        src, exits, cut_counts, _, _ = enumerate_flow({2: 4, 3: 1}, [1]*6 + [2]*2, n)
        calls = [(n-r, q) for r, q in src.items() if r < n]
        for (_, _, _, r, q), count in cut_counts.items():
            calls.extend([(r, q)]*count)
        records[n] = sum(src.values()), calls
        if n == 12:
            require((src, exits) == ({6: 60, 8: 64, 9: 6, 12: 28}, {1: 216, 2: 216, 4: 72, 8: 8}),
                    "literal rank-12 source and exit census")
    return records


def library(records, nested):
    widths = [1, 1, 1]
    child_counts = [Counter(), Counter(), Counter()]
    for n in range(3, 9):
        parent, calls = records[n]
        a = widths[-1] if nested else lcm(*(widths[r]//gcd(widths[r], q) for r, q in calls))
        widths.append(a*parent)
        children = Counter()
        for r, q in calls:
            count, rem = divmod(a*q, widths[r])
            require(rem == 0 and r < n, "literal indivisible child")
            children[r] += count
        child_counts.append(children)
    # Propagate one root's population from higher to lower ranks, without a cost recurrence.
    programs = []
    for root in range(9):
        population = Counter({root: 1}) if root else Counter()
        for n in range(root, 2, -1):
            for r, count in child_counts[n].items():
                population[r] += population[n]*count
        programs.append((widths[root], population[1]+2*population[2], sum(population.values())))
    return programs


def point_bill(a, grouped, small, large, recursive):
    total = 0
    for (r, q), occurrences in grouped.items():
        w, leaves, nodes = small[r]
        b, old_leaves, old_nodes = large[r]
        c = leaves + (nodes if recursive else 1)
        d = old_leaves + (old_nodes if recursive else 1)
        narrow, rest = divmod(a*q, w)
        wide, leftover = divmod(a*q, b)
        require(rest == 0 and b%w == 0, "literal parent feasibility")
        # With divisible widths, price is affine in the number of wide invocations.
        total += occurrences*min(narrow*c, wide*d + (leftover//w)*c)
    return total


def recount():
    records = literal_cuts()
    small, large = library(records, False), library(records, True)
    parent, calls = records[12]
    grouped = Counter(calls)
    stride = lcm(*(small[r][0]//gcd(small[r][0],q) for r,q in calls))
    end = lcm(*(large[r][0]//gcd(large[r][0],q) for r,q in calls))
    require((parent,len(calls),grouped[8,1],stride,end) == (158,515,8,700,2744000), "literal parent rows")
    stored = json.loads((PACKAGE/"RESULT.json").read_text(encoding="utf-8"))
    receipts = {}
    for field, recursive in (("rank12",False), ("recursive_dispatch",True)):
        points = []
        for a in range(stride, end+1, stride):
            cost = Fraction(point_bill(a, grouped, small, large, recursive), parent*a)
            if not points or cost < points[-1][1]:
                points.append((a,cost))
        expected = [(r["a"],Fraction(r["cost"])) for r in stored[field]["frontier"]]
        require(points == expected, "literal Pareto agreement")
        receipts[field] = [[a,str(c)] for a,c in points]
    node_counts = stored["recursive_dispatch"]["libraries"]
    for tag, programs in (("smaller", small), ("nested", large)):
        require([row[2] for row in programs] == node_counts[tag]["nodes_by_program_rank"], "literal library node counts")
    return dict(status="PASS_PRICED_WIDTH_LITERAL_SOURCE", ranks=list(records), cut_occurrences=len(calls),
                rank8_separate_cuts=grouped[8,1], feasible_replications=end//stride, models=receipts)


if __name__ == "__main__":
    print(json.dumps(recount(), sort_keys=True))
