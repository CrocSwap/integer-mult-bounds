#!/usr/bin/env python3
"""Whole-tree source impact of the unsound bit-0 word-census prune.

Default mode:
  1. recompute the 01021323 calibration (bit-0 versus weight-parity budgets);
  2. load the faulty PR2542 engine from authenticated bytes and compare it with
     an independent oracle on the complete n=4, L=8 simple restored domain;
  3. authenticate every pinned inventory file and its quoted evidence, with
     role-specific structural checks;
  4. run rejection controls (tampered role, tampered hash, planted unclassified
     consumer, budget and grouping mutants).
--rescan additionally walks the working tree and requires every file that
mentions the faulty engine, its callers, the native rule or the old receipts to
fall under a classified prefix. That walk is bound to the recorded base commit;
later trees may legitimately add consumers.

Python 3.12 standard library only. Explicit checks, not assert, so -O is safe.
Prepared by JoyboyBrian with substantial assistance from Anthropic Claude.
Apache-2.0.
"""

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
import types
from itertools import combinations
from math import comb
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = "01021323"
MARKER = "PASS_CENSUS_PRUNE_SOURCE_IMPACT"
CODE_SUFFIXES = (".py", ".c", ".cpp", ".cc", ".h")
TEXT_SUFFIXES = (".md", ".json", ".txt")
SCAN_DIRS = ("research", "docs", "certificates", "scripts", "tests")
PROSE_TRIGGERS = {
    "l18_receipt": re.compile(r"15,?775,?992"),
    "l20_pr2634_partial_receipt": re.compile(r"798,?901,?058"),
    "l20_pr2691_receipt": re.compile(r"6,?305,?209,?079"),
    "f7_ge_20": re.compile(r"20\s*(<=|≤)\s*f\(7\)|f\(7\)\s*(>=|≥)\s*20\b"),
}
CALL = re.compile(r"(?<!def )cyclic_census\s*\(")
NATIVE_RULE = re.compile(r"nq\s*&\s*1")
CALLER_ROLES = {"RETIRED_EXCLUSION_CALLER", "HISTORICAL_ANCHOR_CALLER", "AUDIT_CALLER"}
REPLACEMENT_ROLES = {"REPLACEMENT_ENGINE", "REPLACEMENT_DRIVER", "REPLACEMENT_SET_LEVEL"}


class Fail(Exception):
    pass


def require(cond, msg):
    if not cond:
        raise Fail(msg)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------- calibration

def prefix_states(word):
    q, out = 0, [0]
    for ch in word:
        q ^= 1 << int(ch)
        out.append(q)
    return out


def covers(points, n):
    return {a ^ b for a in points for b in points} == set(range(1 << n))


def weight(x):
    return x.bit_count() & 1


def bit0(x):
    return x & 1


def classes(points, functional):
    side = ([], [])
    for p in points:
        side[functional(p)].append(p)
    return side


def within_excess(points, functional):
    """Sum over the two classes of C(size,2) minus distinct within-class XORs."""
    total = 0
    for part in classes(points, functional):
        diffs = {a ^ b for a, b in combinations(part, 2)}
        total += comb(len(part), 2) - len(diffs)
    return total


def budget(s, t, n):
    return comb(s, 2) + comb(t, 2) - ((1 << (n - 1)) - 1)


def first_violation(word, functional, cap):
    """Index of the first prefix whose within-class excess exceeds cap, else None."""
    states = prefix_states(word)[:-1]
    for i in range(1, len(states) + 1):
        if within_excess(states[:i], functional) > cap:
            return i
    return None


def calibration():
    states = prefix_states(WORD)
    points = states[:-1]
    require(states == [0, 1, 3, 2, 6, 4, 12, 8, 0], "prefix states changed")
    require(len(set(points)) == 8 and covers(points, 4), "01021323 is not a simple universal word")
    w_split = tuple(len(c) for c in classes(points, weight))
    b_split = tuple(len(c) for c in classes(points, bit0))
    require(w_split == (4, 4) and b_split == (6, 2), "class sizes changed")
    balanced, actual = budget(4, 4, 4), budget(*b_split, 4)
    w_ex, b_ex = within_excess(points, weight), within_excess(points, bit0)
    require((balanced, actual, w_ex, b_ex) == (5, 9, 0, 8), "budgets or excesses changed")
    old_prune_at = first_violation(WORD, bit0, balanced)
    require(old_prune_at is not None, "old rule no longer prunes the calibration word")
    require(first_violation(WORD, weight, balanced) is None, "weight-parity rule prunes the calibration word")
    require(first_violation(WORD, bit0, actual) is None, "actual-size bit-0 budget prunes the calibration word")
    return {
        "word": WORD,
        "prefix_states": states,
        "weight_split": list(w_split),
        "bit0_split": list(b_split),
        "weight_excess": w_ex,
        "bit0_excess": b_ex,
        "balanced_budget": balanced,
        "bit0_actual_budget": actual,
        "old_rule_first_prune_prefix": old_prune_at,
    }


# ------------------------------------------------------- faulty engine binding

def load_faulty_engine(inventory):
    path = ROOT / inventory["pinned"][0]["path"]
    data = path.read_bytes()
    require(sha256(data) == inventory["faulty_engine_sha256"], "faulty engine bytes changed")
    module = types.ModuleType("pr2542_engine_pinned")
    module.__file__ = str(path)
    exec(compile(data, str(path), "exec"), module.__dict__)
    return module


def oracle_simple_universal(n, length):
    """Restricted-growth words, every label used an even number >= 2 of times,
    restored, with `length` distinct nonclosing states, universal."""
    out = []

    def rec(prefix, top):
        if len(prefix) == length:
            word = "".join(map(str, prefix))
            if any(prefix.count(a) % 2 or prefix.count(a) == 0 for a in range(n)):
                return
            pts = prefix_states(word)
            if pts[-1] != 0 or len(set(pts[:-1])) != length:
                return
            if covers(pts[:-1], n):
                out.append(word)
            return
        for a in range(min(top + 1, n)):
            rec(prefix + [a], max(top, a + 1))

    rec([], 0)
    return out


def small_domain(engine, functional_for_corrected=weight):
    n, length = 4, 8
    truth = oracle_simple_universal(n, length)
    balanced = budget(length // 2, length // 2, n)
    plain = engine.cyclic_census(n, length, budget=None, simple=True)
    pruned = engine.cyclic_census(n, length, budget=balanced, simple=True)
    plain_w = sorted("".join(map(str, w)) for w in plain["words"])
    pruned_w = sorted("".join(map(str, w)) for w in pruned["words"])
    require(plain_w == sorted(truth), "faulty engine without budget disagrees with the oracle")
    false_prunes = sorted(set(truth) - set(pruned_w))
    require(set(pruned_w) <= set(truth), "faulty engine reports a non-universal word")
    corrected_rejects = [w for w in truth if first_violation(w, functional_for_corrected, balanced) is not None]
    old_rule_rejects = sorted(w for w in truth if first_violation(w, bit0, balanced) is not None)
    return {
        "n": n,
        "length": length,
        "balanced_budget": balanced,
        "simple_universal_words": len(truth),
        "engine_hits_without_budget": plain["hits"],
        "engine_hits_with_balanced_budget": pruned["hits"],
        "engine_false_prunes": false_prunes,
        "independent_bit0_balanced_rejects": old_rule_rejects,
        "weight_parity_balanced_rejects": len(corrected_rejects),
    }


# ----------------------------------------------------------------- inventory

def validate_inventory(inventory, root):
    faulty = inventory["faulty_engine_sha256"]
    roles = {}
    for row in inventory["pinned"]:
        data = (root / row["path"]).read_bytes()
        require(sha256(data) == row["sha256"], "pinned bytes changed: " + row["path"])
        text = data.decode("utf-8")
        for pattern in row["evidence"]:
            require(re.search(pattern, text), f"evidence {pattern!r} missing in {row['path']}")
        role = row["role"]
        has_call = bool(CALL.search(text))
        require((row["sha256"] == faulty) == (role == "FAULTY_ENGINE"), "faulty bytes must carry FAULTY_ENGINE: " + row["path"])
        if role == "FAULTY_ENGINE":
            require(row["sha256"] == faulty, "faulty-engine row is not the faulty bytes: " + row["path"])
        elif role == "FAULTY_NATIVE_RULE":
            require(NATIVE_RULE.search(text) and re.search(r"#define BUDGET 27\b", text),
                    "native rule row lacks bit-0 grouping with the balanced budget 27")
        elif role in CALLER_ROLES:
            require(has_call, "caller row does not call cyclic_census: " + row["path"])
        elif role in REPLACEMENT_ROLES:
            require(row["sha256"] != faulty and not has_call and "def cyclic_census" not in text,
                    "replacement row uses the faulty engine: " + row["path"])
            require(not NATIVE_RULE.search(text), "replacement row groups by nq&1: " + row["path"])
        roles[row["path"]] = role
    retired = {r["pr"] for r in inventory["pinned"] if r["role"].startswith(("FAULTY", "RETIRED"))}
    replacement = {r["pr"] for r in inventory["pinned"] if r["role"] in REPLACEMENT_ROLES}
    require(retired == {2542, 2634, 2691, 2773} and not retired & replacement, "retired/replacement split changed")
    return sorted(set(roles.values()))


def classify(path, coverage):
    for entry in coverage:
        if path.startswith(entry["prefix"]):
            return entry
    return None


def triggers(rel, data, faulty):
    found = []
    if rel.endswith(CODE_SUFFIXES):
        if sha256(data) == faulty:
            found.append("faulty_engine_bytes")
        text = data.decode("utf-8", "ignore")
        if CALL.search(text) or "def cyclic_census" in text:
            found.append("cyclic_census")
        if rel.endswith((".c", ".cpp", ".cc", ".h")) and NATIVE_RULE.search(text) and "BUDGET" in text:
            found.append("native_bit0_rule")
    if rel.endswith(TEXT_SUFFIXES + CODE_SUFFIXES):
        text = data.decode("utf-8", "ignore")
        found += [k for k, rx in PROSE_TRIGGERS.items() if rx.search(text)]
    return found


def rescan(inventory, root, dirs=SCAN_DIRS):
    by_class, unclassified, hit_prefixes, files = {}, [], set(), 0
    skip = os.path.relpath(PACKAGE, root) + os.sep
    for top in dirs:
        base = root / top
        if not base.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if d not in (".git", "__pycache__"))
            for name in sorted(filenames):
                full = Path(dirpath) / name
                rel = full.relative_to(root).as_posix()
                if rel.startswith(skip.replace(os.sep, "/")) or not rel.endswith(TEXT_SUFFIXES + CODE_SUFFIXES):
                    continue
                files += 1
                found = triggers(rel, full.read_bytes(), inventory["faulty_engine_sha256"])
                if not found:
                    continue
                entry = classify(rel, inventory["coverage"])
                if entry is None:
                    unclassified.append((rel, found))
                    continue
                hit_prefixes.add(entry["prefix"])
                by_class[entry["class"]] = by_class.get(entry["class"], 0) + 1
    stale = sorted(e["prefix"] for e in inventory["coverage"] if e["must_trigger"] and e["prefix"] not in hit_prefixes)
    return {"files_scanned": files, "trigger_files_by_class": dict(sorted(by_class.items())),
            "unclassified": unclassified, "stale_prefixes": stale}


# ------------------------------------------------------------------ controls

def expect_fail(fn, label):
    try:
        fn()
    except Fail:
        return label
    raise Fail("control did not fail: " + label)


def controls(inventory, engine):
    done = []
    bad = copy.deepcopy(inventory)
    idx = next(i for i, r in enumerate(bad["pinned"]) if r["path"].endswith("f7-bit0-false-prune/verify.py"))
    bad["pinned"][idx]["role"] = "REPLACEMENT_ENGINE"
    done.append(expect_fail(lambda: validate_inventory(bad, ROOT), "audit caller relabelled as replacement"))
    bad = copy.deepcopy(inventory)
    bad["pinned"][3]["role"] = "REPLACEMENT_ENGINE"
    done.append(expect_fail(lambda: validate_inventory(bad, ROOT), "native bit-0 rule relabelled as replacement"))
    bad = copy.deepcopy(inventory)
    bad["pinned"][-1]["sha256"] = "0" * 64
    done.append(expect_fail(lambda: validate_inventory(bad, ROOT), "tampered pinned hash"))
    bad = copy.deepcopy(inventory)
    bad["pinned"][-1]["evidence"] = [r"f\(7\) >= 20 follows from sections 1-2 alone"]
    done.append(expect_fail(lambda: validate_inventory(bad, ROOT), "replacement evidence weakened to f(7)>=20"))
    with tempfile.TemporaryDirectory() as tmp:
        troot = Path(tmp)
        (troot / "research" / "planted").mkdir(parents=True)
        (troot / "research" / "planted" / "x.py").write_text("r = cyclic_census(7, 18, budget=9)\n")
        (troot / "research" / "planted" / "y.md").write_text("gap 20 <= f(7) <= 24\n")
        (troot / "research" / "community-x").mkdir()
        (troot / "research" / "community-x" / "p.json").write_text('{"n": "15,775,992"}\n')
        result = rescan(inventory, troot)
        require(sorted(p for p, _ in result["unclassified"]) == ["research/planted/x.py", "research/planted/y.md"]
                and result["trigger_files_by_class"] == {"INTAKE_ARCHIVE": 1},
                "rescan control misclassified planted files")
        done.append("planted unclassified consumers flagged")
    require(first_violation(WORD, bit0, budget(4, 4, 4)) is not None, "balanced bit-0 mutant")
    done.append("balanced bit-0 budget rejects 01021323")
    mutant = small_domain(engine, functional_for_corrected=bit0)
    require(mutant["weight_parity_balanced_rejects"] > 0, "grouping mutant undetected")
    done.append("bit-0 grouping substituted into corrected rule loses universal words")
    return done


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rescan", action="store_true", help="also walk the working tree (base-bound)")
    parser.add_argument("--emit", action="store_true", help="print the observed result and exit 0")
    args = parser.parse_args()
    inventory = json.loads((PACKAGE / "INVENTORY.json").read_text(encoding="utf-8"))
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    try:
        engine = load_faulty_engine(inventory)
        observed = {
            "calibration": calibration(),
            "small_domain": small_domain(engine),
            "inventory_roles": validate_inventory(inventory, ROOT),
            "pinned_rows": len(inventory["pinned"]),
            "controls": controls(inventory, engine),
            "no_new_kappa": True,
        }
        if args.rescan:
            observed["rescan"] = rescan(inventory, ROOT)
        if args.emit:
            print(json.dumps(observed, indent=1, sort_keys=True))
            return 0
        for key, value in observed.items():
            require(expected.get(key) == value, f"RESULT.json mismatch for {key}: {json.dumps(value)}")
        if args.rescan:
            require(not observed["rescan"]["unclassified"] and not observed["rescan"]["stale_prefixes"],
                    "rescan found unclassified consumers or stale prefixes")
    except Fail as exc:
        print("FAIL:", exc)
        return 1
    sd = observed["small_domain"]
    print(f"{MARKER} pinned={observed['pinned_rows']} false_prunes_n4L8={len(sd['engine_false_prunes'])}"
          f"/{sd['simple_universal_words']} controls={len(observed['controls'])}"
          + (f" rescan_files={observed['rescan']['files_scanned']}" if args.rescan else "")
          + " no_new_kappa")
    return 0


if __name__ == "__main__":
    sys.exit(main())
