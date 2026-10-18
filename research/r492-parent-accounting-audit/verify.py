#!/usr/bin/env python3
"""Audit the selected R/R0 invoice, without importing its arithmetic engines.

Apache-2.0. Prepared for thakrarsagar with substantial OpenAI Codex assistance.
See README.md for the finite scope and predecessor attribution.
"""
import argparse
import ast
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = "research/complex-k492-owner-repair/"
REPLAY = "research/community-k492-audit/pr626/replay/mixed-global/"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_inputs():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    data = {}
    for name, expected in pins.items():
        raw = (ROOT / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == expected, "source hash: " + name)
        data[name] = gzip.decompress(raw) if name.endswith(".gz") else raw
    return data


def helper_count(word):
    require(len(word["start"]) == len(word["final"]), "word column dimensions")
    count = len(word["start"]) - 2 * word["v"]
    require(count == word["R"] > 0, "word helper count")
    return count


def recount(invoice, owner, spec, parent, words):
    """Use explicit charge categories and native dimensions, not source slicing."""
    counts = {pid: helper_count(word) for pid, word in words.items()}
    require(set(counts.values()) == {492}, "selected provider dimensions")
    r0 = helper_count(parent)
    require(r0 == 504, "fixed parent dimensions")
    require(all(w["v"] == 112 and w["h"] == 9 and len(w["centers"]) == 8
                for w in [parent, *words.values()]), "word geometry")
    calls = [(s, r, pid) for s, r, pid in spec["dispatch"]]
    require(len(calls) == 72 and {(s, r) for s, r, _ in calls} ==
            {(s, r) for s in range(9) for r in range(8)}, "complete dispatch")
    require(Counter(pid for _, _, pid in calls) == invoice["provider_counts"],
            "provider dispatch counts")
    rows = [invoice["providers"][pid]["local"]["forward" if s % 2 == 0 else "backward"]
            for s, _, pid in calls]
    scalar = sum(row["real_component_primitives"] for row in rows)
    wrappers = sum(row["pre_wrappers"] + row["post_wrappers"] for row in rows) * 144
    require(scalar == invoice["selected_real_component_primitives"], "scalar recount")
    require(wrappers == invoice["wrapper_elementary_factors_charged"], "wrapper recount")
    require(invoice["factors_per_wrapper"] == 144, "wrapper factor count")
    require(invoice["helpers"] == 492 and invoice["centres"] == 8, "provider stock")
    require(invoice["live"] == owner["live"] == 7168, "live stock")
    require(invoice["physical"] == owner["physical"] == 7168 + 492 + 8 + 2,
            "physical stock")
    require(invoice["physical_stock_identity"] == dict(data_and_owner_families=7168,
            local_helpers=492, private_centres=8, coefficient_work=2), "stock identity")
    require(owner["owners_per_call"] == 224 + 492, "owners per call")
    require(owner["actual_helper_owner_charts"] == owner["hosted_residuals"] ==
            sum(counts[pid] for _, _, pid in calls), "helper roles")
    require(owner["source_idle_children_charged"] == 16128, "parent idle charge")
    compiler = 64 * 74 ** 3
    adapters = max(16 * (max(row["macros"] for row in p["local"].values()) +
                         sum(p["paid_profile"].values()) + len(words[pid]["start"]) + 8)
                   + 64 * 73 for pid, p in invoice["providers"].items())
    require(compiler == invoice["compiler"] and adapters == invoice["local_adapters"],
            "compiler and adapter recount")
    parent_live = 7168 + 9 * r0
    parent_physical = parent_live + r0 + 8 + 2
    charges = dict(data_sweeps=4 * 112 * 8 * 9, source_sweeps=2 * 112 * 8 * 9,
                   helper_routes=sum(2 * counts[pid] for _, _, pid in calls),
                   parent_idle=16128, parent_banks=9 * r0, bridges=224 * 72,
                   shifts=4 * 112 * 8, moves=8 * 112 * 8, parent_live=parent_live,
                   parent_physical=parent_physical, wrappers=wrappers)
    outside = 8 * sum(charges.values()) + 64 * 73
    pervertex = (scalar + charges["bridges"] + charges["shifts"] + charges["moves"] +
                 parent_live + compiler * (72 * adapters + outside) + 64 * parent_physical)
    rebase_delta = -65 * (parent_physical - invoice["physical"]) - (parent_live - invoice["live"])
    require(pervertex == invoice["unhosted_pervertex"], "unhosted invoice")
    require(pervertex + rebase_delta == invoice["hosted_rebased_pervertex"], "rebased invoice")
    prior = invoice["retained_prior_overcharge"]
    require(prior["added_complete_new_pervertex"] == pervertex, "retained fresh charge")
    require(invoice["conservative_pervertex_used"] ==
            max(pervertex, pervertex + rebase_delta, prior["previous_pervertex_allowance"] + pervertex),
            "retained allowance sum")
    return dict(R=492, R0=r0, parent_live=parent_live, parent_physical=parent_physical,
                charges=charges, nonlocal_items=sum(charges.values()), outside=outside,
                compiler=compiler, adapters=adapters, pervertex=pervertex,
                rebase_delta=rebase_delta, rebased=pervertex + rebase_delta,
                conservative_pervertex=invoice["conservative_pervertex_used"])


def accounting_slice(source):
    function = next(node for node in ast.parse(source).body
                    if isinstance(node, ast.FunctionDef) and node.name == "assemble")
    starts = [i for i, node in enumerate(function.body) if isinstance(node, ast.Assign)
              and ast.unparse(node.targets[0]) == "(parent_live, parent_physical, parent_idle)"]
    stops = [i for i, node in enumerate(function.body) if isinstance(node, ast.Assign)
             and ast.unparse(node.targets[0]) == "bit_path"]
    require(len(starts) == len(stops) == 1 and starts[0] < stops[0], "unique accounting slice")
    return function.body[starts[0]:stops[0]]


def replay_slice(source, invoice, owner):
    body = accounting_slice(source)
    env = dict(invoice=deepcopy(invoice), owner=deepcopy(owner), R=invoice["helpers"],
               hash_ok=lambda x: isinstance(x, str) and len(x) == 64 and
               all(c in "0123456789abcdef" for c in x))
    # Preserve the original assertions even when the audit is invoked with -O.
    code = compile(ast.Module(body=body, type_ignores=[]), "<pinned-accounting-slice>",
                   "exec", optimize=0)
    exec(code, env)
    return {name: env[name] for name in ("parent_banks", "nonlocal_items", "outside",
            "pervertex", "rebased", "used", "actual_checks")}


def run():
    inputs = load_inputs()
    read = lambda name: json.loads(inputs[name])
    invoice = read(REPLAY + "audit/PREFIX-AND-INVOICE.json")
    owner = read(REPLAY + "audit/OWNERS-AND-PROFILE.json")
    spec = read(PACKAGE + "data/SPEC.json")
    parent = read(REPLAY + "base/split-centres/CANONICAL-WORD.json.gz")
    words = {pid: read(REPLAY + "base/providers/" + pid + "/CANONICAL-WORD.json.gz")
             for pid in invoice["providers"]}
    exact = recount(invoice, owner, spec, parent, words)
    source = inputs[PACKAGE + "code/assemble.py"].decode()
    baseline = replay_slice(source, invoice, owner)
    require(baseline["pervertex"] == exact["pervertex"] and
            baseline["rebased"] == exact["rebased"], "independent/source agreement")
    mutations = [
        ("routes_use_parent_R0", "2*72*R+", "2*72*504+", False),
        ("parent_banks_use_provider_R", "9*parent_banks+", "9*R+", False),
        ("parent_stock_uses_provider_R", "parent_live+parent_banks+8+2", "parent_live+R+8+2", False),
        ("parent_banks_literal_504", "9*parent_banks+", "9*504+", True),
        ("omit_helper_routes", "2*72*R+", "0+", False),
        ("omit_wrapper_charge", "+invoice['wrapper_elementary_factors_charged'])", "+0)", False),
        ("rebase_64_instead_of_65", "+65*(invoice['physical']", "+64*(invoice['physical']", False),
        ("omit_live_rebase", "+(invoice['live']-parent_live)", "+0", False),
    ]
    controls = []
    for name, old, new, should_pass in mutations:
        require(source.count(old) == 1, "unique mutation site: " + name)
        try:
            got = replay_slice(source.replace(old, new, 1), invoice, owner)
        except AssertionError as error:
            require(not should_pass, "equivalent control rejected: " + name)
            tb = error.__traceback__
            while tb.tb_next:
                tb = tb.tb_next
            controls.append(dict(name=name, outcome="rejected", source_line=tb.tb_lineno,
                                 assertion=source.splitlines()[tb.tb_lineno - 1].strip()))
        else:
            require(should_pass and got == baseline, "mutation unexpectedly accepted: " + name)
            controls.append(dict(name=name, outcome="accepted_identical"))
    input_controls = []
    for field, delta in [("physical", 12), ("wrapper_elementary_factors_charged", -144),
                         ("selected_real_component_primitives", -1), ("local_adapters", 192)]:
        bad = deepcopy(invoice)
        bad[field] += delta
        try:
            recount(bad, owner, spec, parent, words)
        except ValueError as error:
            input_controls.append(dict(field=field, delta=delta, rejection=str(error)))
        else:
            raise ValueError("independent recount accepted changed " + field)
    c = exact["compiler"]
    deltas = dict(routes_use_parent_R0=8 * c * 2 * 72 * (504 - 492),
                  parent_banks_use_provider_R=8 * c * 9 * (492 - 504),
                  rebase_64_instead_of_65=exact["parent_physical"] - invoice["physical"],
                  omit_live_rebase=exact["parent_live"] - invoice["live"])
    note = inputs[PACKAGE + "PROOF-NOTE-R.md"].decode()
    require("the R0 and cosmetic sites must pass" in note and
            "both R0 controls fail" in note, "pinned prose discrepancy")
    return dict(status="PASS_R492_PARENT_ACCOUNTING_AUDIT", exact=exact,
                source_slice=dict(first_line=accounting_slice(source)[0].lineno,
                                  last_line=accounting_slice(source)[-1].end_lineno,
                                  strict_checks=baseline["actual_checks"]),
                source_mutations=controls, input_controls=input_controls,
                pervertex_or_rebase_deltas=deltas,
                finding="The introductory R0 pass expectation contradicts the table and evidence; the accounting slice rejects R0-to-R substitutions.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print deterministic evidence as JSON")
    args = parser.parse_args()
    result = run()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(result == json.loads((HERE / "EXPECTED.json").read_text()), "EXPECTED.json mismatch")
        print(result["status"] + ": 9 finite guards, 7 source rejections, 1 identical control, 4 input rejections")
