#!/usr/bin/env python3
"""Scoped audit of the selected K492 assembly's provider/parent helper counts.

Gabriel Roa / @gaboroa14, with substantial OpenAI Codex assistance.
Apache-2.0. See README.md for attribution, mathematical scope and exclusions.
"""

import argparse
from collections import Counter
import copy
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = Path("research/complex-k492-owner-repair")
REPLAY = Path("research/community-k492-audit/pr626/replay")
BASE = REPLAY / "mixed-global/base"
AUDIT = REPLAY / "mixed-global/audit"
ASSEMBLER = PACKAGE / "code/assemble.py"


class AuditError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AuditError(message)


def canonical(value):
    """Normalize JSON object keys (in particular integer profile ranks)."""
    return json.loads(json.dumps(value))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(relative):
    path = ROOT / relative
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def check_pin(data, expected, label):
    require(sha(data) == expected, "source hash mismatch: " + label)


def rank_f2(rows, dimension):
    pivots = {}
    for row in rows:
        require(type(row) is int and 0 < row < 1 << dimension, "invalid frame vector")
        while row:
            bit = row.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = row
                break
            row ^= pivots[bit]
    return len(pivots)


def widths_from_word(word):
    v, helpers, dimension = word["v"], word["R"], word["h"]
    require(len(word["start"]) == len(word["final"]) == 2*v + helpers,
            "native register count")
    ranks = [rank_f2(frame, dimension) for frame in word["frames"]]
    require(all(rank == len(frame) for rank, frame in zip(ranks, word["frames"])),
            "dependent frame basis")
    starts = [ranks[f] for f in word["start"][2*v:]]
    ends = [ranks[f] for f in word["final"][2*v:]]
    widths = [end - start for start, end in zip(starts, ends)]
    require(all(0 < w <= dimension for w in widths), "invalid helper width")
    return widths, sum(starts), sum(dimension - end for end in ends)


def price_program(events):
    """Count the retained Horner implementation by a closed integer formula.

    Unlike invoice_allcold.py, this does not execute the Horner accumulator or
    propagate an l1 envelope. It checks only the charged operation count.
    """
    macros = primitives = coefficient_work = 0
    paid = Counter()
    wrappers = {"pre": set(), "post": set()}
    for event in events:
        tag = event[0]
        if tag == "climb":
            paid[event[5]] += 1
        elif tag == "center":
            paid[event[4]] += 1
        elif tag == "residual_adapter":
            side, register = event[1:3]
            require(side in wrappers and register not in wrappers[side], "duplicate wrapper")
            wrappers[side].add(register)
        elif tag == "scalar":
            macros += 1
            scalar = event[1]
            op = scalar[0]
            if op in ("copy", "clear"):
                cost = 1
            else:
                require(op in ("scale", "add"), "unknown scalar operation")
                q = Fraction(*scalar[-2:])
                numerator, denominator = abs(q.numerator), q.denominator
                require(numerator > 0 and denominator & (denominator-1) == 0,
                        "non-dyadic scalar coefficient")
                halvings = denominator.bit_length() - 1
                if op == "scale":
                    require(numerator & (numerator-1) == 0, "non-power-of-two scale")
                    cost = abs(numerator.bit_length()-1-halvings) + int(q < 0)
                else:
                    # Clear; b-1 doubles; popcount additions; e halvings;
                    # signed accumulation; clear. Total b+popcount+e+2.
                    require(scalar[1] != scalar[2], "self-addition")
                    cost = numerator.bit_length() + numerator.bit_count() + halvings + 2
                    coefficient_work += cost
            primitives += 2*cost  # Real and imaginary components.
        else:
            require(tag in ("adapter", "phase"), "unknown program event")
    require(wrappers["pre"] == wrappers["post"], "unpaired wrappers")
    return dict(events=len(events), macros=macros, real_component_primitives=primitives,
                coefficient_work_primitive_count=coefficient_work,
                pre_wrappers=len(wrappers["pre"]), post_wrappers=len(wrappers["post"]),
                paid_profile=dict(sorted(paid.items())))


def check_roles(roles, dispatch, widths):
    seen = set()
    for role in roles:
        call = role["stage"], role["replica"]
        require(call in dispatch, "unknown helper call")
        key = (*call, role["helper"])
        require(key not in seen, "duplicate helper role")
        seen.add(key)
        row = widths[dispatch[call]]
        require(0 <= role["helper"] < len(row), "helper index outside provider")
        require(role["width"] == row[role["helper"]], "literal helper width")
    expected = {(*call, h) for call, pid in dispatch.items() for h in range(len(widths[pid]))}
    require(seen == expected, "incomplete helper role coverage")
    return len(seen)


def recount(owner, invoice, spec):
    parent = read(BASE / "split-centres/CANONICAL-WORD.json.gz")
    plan = read(PACKAGE / "data/PLAN.json")
    dispatch = {(s, r): pid for s, r, pid in spec["dispatch"]}
    stages, replicas, blocks = plan["L"], plan["T"], plan["K"]
    v, dimension, parent_helpers = parent["v"], parent["h"], parent["R"]
    require(set(dispatch) == {(s, r) for s in range(stages) for r in range(replicas)},
            "incomplete call grid")
    require(len(dispatch) == len(spec["dispatch"]), "duplicate dispatch")
    providers, widths, program_counts = {}, {}, {}
    for pid, receipt in invoice["providers"].items():
        word = read(BASE / "providers" / pid / "CANONICAL-WORD.json.gz")
        programs = read(BASE / "providers" / pid / "LOCAL-PROGRAMS.json.gz")
        width, entrance, codim = widths_from_word(word)
        widths[pid] = width
        require((word["v"], word["h"]) == (v, dimension), "provider geometry")
        require(receipt["helpers"] == word["R"] == len(width), "provider helper count")
        require(receipt["n"] == 2*v + len(width), "provider column count")
        require(receipt["widths"] == width, "receipt width vector")
        require(receipt["entrance_rank"] == entrance and receipt["terminal_codimension"] == codim,
                "endpoint rank totals")
        require(sum(width) == dimension*len(width) - entrance - codim, "width conservation")
        require(set(programs) == {"forward", "backward"}, "missing orientation")
        counts = {orientation: price_program(events) for orientation, events in programs.items()}
        for orientation, count in counts.items():
            for key, value in count.items():
                expected = receipt["paid_profile"] if key == "paid_profile" else receipt["local"][orientation][key]
                require(canonical(value) == expected, "program recount: " + pid + ":" + orientation + ":" + key)
        program_counts[pid] = counts
        children = sum(counts["forward"]["paid_profile"].values())
        adapters = 16*(max(c["macros"] for c in counts.values()) + children + 2*v + len(width)
                       + len(word["centers"])) + 64*plan["M"]
        require(adapters == receipt["local_adapters"], "local adapter count")
        providers[pid] = dict(helpers=len(width), columns=2*v+len(width), entrance_rank=entrance,
                             terminal_codimension=codim, width_sum=sum(width),
                             width_inventory=dict(sorted(Counter(width).items())), local_adapters=adapters,
                             local=counts)
    require(set(providers) == set(dispatch.values()), "provider dispatch coverage")
    require(len({p["helpers"] for p in providers.values()}) == 1, "mixed helper counts")
    helpers = next(iter(providers.values()))["helpers"]
    require(invoice["helpers"] == helpers, "invoice helper count")
    roles = read(PACKAGE / "data/OWNERS.json.gz")
    role_count = check_roles(roles, dispatch, widths)
    require(role_count == owner["hosted_residuals"] == owner["actual_helper_owner_charts"],
            "hosted helper count")
    require(owner["owners_per_call"] == 2*v+helpers, "owner column count")

    helper_map = read(REPLAY / "ck-base-k_triangle-construction/HELPER-MAP.json")
    mapping = {int(a): b for a, b in helper_map["map"].items()}
    removed = set(helper_map["removed_504_helpers"])
    require(set(mapping).isdisjoint(removed) and set(mapping) | removed == set(range(2*v+parent_helpers)),
            "helper map domain")
    require(len(mapping) == len(set(mapping.values())) == 2*v+helpers
            and set(mapping.values()) == set(range(2*v+helpers)), "helper map bijection")
    original_spots = (270, 282, 294, 306)
    mapped_spots = [mapping[2*v+h] - 2*v for h in original_spots]
    require(mapped_spots == spec["width_spot_helpers"], "helper spot translation")
    require(all(row[h] == 8 for row in widths.values() for h in mapped_spots), "mapped spot widths")

    data = 2*v*blocks*replicas
    centres = len(parent["centers"])
    parent_live = data + stages*parent_helpers
    parent_physical = parent_live + parent_helpers + centres + 2
    physical = data + helpers + centres + 2
    require(data == invoice["live"] == owner["live"] and physical == invoice["physical"] == owner["physical"],
            "physical stock")
    require(invoice["physical_stock_identity"] == dict(data_and_owner_families=data, local_helpers=helpers,
            private_centres=centres, coefficient_work=2), "stock categories")
    selected = [program_counts[pid]["backward" if stage % 2 else "forward"]
                for (stage, replica), pid in dispatch.items()]
    scalar = sum(c["real_component_primitives"] for c in selected)
    factors_per_wrapper = 2*(plan["M"]-1)
    wrappers = factors_per_wrapper*sum(c["pre_wrappers"]+c["post_wrappers"] for c in selected)
    require(scalar == invoice["selected_real_component_primitives"], "selected scalar charge")
    require(wrappers == invoice["wrapper_elementary_factors_charged"], "selected wrapper charge")
    bridges, shifts = 2*v*len(dispatch), blocks*v*replicas
    # The parent idle count is a pinned inherited input, not independently
    # reconstructed from the omitted parent GLOBAL-TEMPLATE in this audit.
    terms = dict(data_routes=blocks*v*len(dispatch), port_routes=2*v*len(dispatch),
                 helper_routes=2*role_count, parent_idle=owner["source_idle_children_charged"],
                 parent_banks=parent_live-data, bridges=bridges, shifts=shifts, moves=2*shifts,
                 parent_live=parent_live, parent_physical=parent_physical, wrappers=wrappers)
    compiler = 64*(plan["M"]+1)**3
    adapters = max(p["local_adapters"] for p in providers.values())
    outside = 8*sum(terms.values()) + 64*plan["M"]
    unhosted = (scalar + bridges + 3*shifts + parent_live
                + (len(dispatch)*adapters + outside)*compiler + 64*parent_physical)
    rebased = unhosted + 65*(physical-parent_physical) + data-parent_live
    require((unhosted, rebased) == (invoice["unhosted_pervertex"], invoice["hosted_rebased_pervertex"]),
            "complete finite invoice recount")
    return dict(provider_helpers=helpers, parent_helpers=parent_helpers, helper_roles=role_count,
                data_rows=data, physical_rows=physical, parent_live=parent_live, parent_physical=parent_physical,
                removed_parent_registers=sorted(removed), mapped_spots=mapped_spots,
                old_spot_widths={pid: [row[h] for h in original_spots] for pid, row in widths.items()},
                providers=providers, nonlocal_items=terms, unhosted_pervertex=unhosted,
                hosted_rebased_pervertex=rebased,
                stale_provider_route_overcharge=2*len(dispatch)*(parent_helpers-helpers)*8*compiler,
                substituted_parent_bank_undercharge=stages*(parent_helpers-helpers)*8*compiler)


# Exactly the 14 assemble.* rows in the pinned PROOF-NOTE-R table. Replacements
# occur once in executable source, without mutating either input receipt.
MUTATIONS = [
    ("assemble.R", "R=invoice['helpers'];", "R=504;", "R=invoice['helpers'];"),
    ("assemble.owners_per_call", "owner['owners_per_call']==2*112+R", "owner['owners_per_call']==728", "assert owner['owners_per_call']"),
    ("assemble.hosted_72R", "==72*R==pin(", "==72*504==pin(", "assert owner['owners_per_call']"),
    ("assemble.stock_helpers", "local_helpers=R,", "local_helpers=504,", "assert invoice['physical_stock_identity']"),
    ("assemble.provider_helpers", "assert p['helpers']==R and", "assert p['helpers']==504 and", "assert p['helpers']==R and"),
    ("assemble.provider_n", "p['n']==2*112+R", "p['n']==728", "assert p['helpers']==R and"),
    ("assemble.width_sum", "==9*R-p['entrance_rank']", "==9*504-p['entrance_rank']", "assert sum(p['widths'])"),
    ("assemble.width_len", "len(p['widths'])==R", "len(p['widths'])==504", "assert sum(p['widths'])"),
    ("assemble.exact_columns", "z['all_exact_columns']==2*112+R", "z['all_exact_columns']==728", "assert z['all_exact_columns']"),
    ("assemble.dirty_columns", "z['dirty_helper_columns']==R", "z['dirty_helper_columns']==504", "assert z['all_exact_columns']"),
    ("assemble.local_adapters", "p['children']+2*112+R+8", "p['children']+728+8", "assert p['local_adapters']"),
    ("assemble.route_items", "+2*72*R+", "+2*72*504+", "assert invoice['unhosted_pervertex']"),
    ("assemble.parent_banks", "+9*parent_banks+", "+9*504+", None),
    ("assemble.spot_width8", "for h in SPOT)", "for h in (270,282,294,306))", "pin(K+'width_digest'"),
]


def replace_once(source, old, new):
    require(source.count(old) == 1, "mutation must match exactly once: " + old)
    require(old.count("\n") == new.count("\n"), "mutation changed line numbering")
    return source.replace(old, new)


def line_number(source, fragment):
    matches = [i for i, line in enumerate(source.splitlines(), 1) if fragment in line]
    require(len(matches) == 1, "ambiguous failure location: " + fragment)
    return matches[0]


def execute_source(source, filename):
    namespace = {"__name__": "k492_audit_subject", "__file__": str(ROOT/ASSEMBLER)}
    exec(compile(source, filename, "exec"), namespace)
    return namespace["assemble"]


def source_controls(owner, invoice, expected, spec_path, dependency):
    os.environ["WITNESS_SPEC"] = str(spec_path)
    os.environ["GAIN_PR564_SOURCE"] = str(dependency)
    os.environ.pop("WITNESS_DISCOVER", None)
    os.environ.pop("WITNESS_RECORD", None)
    witness_path = ROOT/PACKAGE/"code/witness.py"
    witness_spec = importlib.util.spec_from_file_location("witness", witness_path)
    witness = importlib.util.module_from_spec(witness_spec)
    witness_spec.loader.exec_module(witness)
    sys.modules["witness"] = witness
    source = (ROOT/ASSEMBLER).read_text()
    documented = (ROOT/PACKAGE/"PROOF-NOTE-R.md").read_text()
    documented_sites = {line.split("|")[1].strip() for line in documented.splitlines()
                        if line.startswith("| assemble.")}
    require({row[0] for row in MUTATIONS} == documented_sites, "documented assembly-site coverage")
    owner_hash = sha((ROOT/AUDIT/"OWNERS-AND-PROFILE.json").read_bytes())
    invoice_hash = sha((ROOT/AUDIT/"PREFIX-AND-INVOICE.json").read_bytes())

    def invoke(text, label):
        filename = str(ASSEMBLER) + "::" + label
        function = execute_source(text, filename)
        return filename, function

    _, baseline = invoke(source, "baseline")
    require(canonical(baseline(owner, invoice, owner_hash, invoice_hash)) == expected,
            "unchanged assembly differs from selected receipt")
    rows = []
    controls = MUTATIONS + [
        ("control.parent_banks_use_provider_R", "+9*parent_banks+", "+9*R+", "assert invoice['unhosted_pervertex']"),
        ("control.equivalent_provider_count", "R=invoice['helpers'];", "R=504-12;", None),
    ]
    for name, old, new, failure in controls:
        mutated = replace_once(source, old, new)
        filename, function = invoke(mutated, name)
        wanted_line = line_number(source, failure) if failure else None
        try:
            result = function(owner, invoice, owner_hash, invoice_hash)
        except AssertionError as error:
            trace = error.__traceback__
            while trace.tb_next:
                trace = trace.tb_next
            require(wanted_line is not None and trace.tb_frame.f_code.co_filename == filename
                    and trace.tb_lineno == wanted_line, "unrelated rejection: " + name)
            outcome = "rejected_at_expected_assertion"
        else:
            require(wanted_line is None, "invalid source reversion accepted: " + name)
            require(canonical(result) == expected, "positive control changed assembly: " + name)
            outcome = "accepted_identical_assembly"
        rows.append(dict(name=name, original=old, replacement=new, outcome=outcome,
                         assertion_line=wanted_line, mutated_source_sha256=sha(mutated.encode())))
    return rows


def negative_controls():
    caught = []

    def reject(name, fn, message):
        try:
            fn()
        except AuditError as error:
            require(str(error) == message, "unrelated audit rejection: " + name)
            caught.append(name)
        else:
            raise AuditError("audit control accepted: " + name)

    word = read(BASE/"providers/ck/CANONICAL-WORD.json.gz")
    bad = copy.deepcopy(word)
    bad["R"] = 504
    reject("stale_native_helper_count", lambda: widths_from_word(bad), "native register count")
    dependent = copy.deepcopy(word)
    dependent["frames"][1].append(dependent["frames"][1][0])
    reject("dependent_frame_basis", lambda: widths_from_word(dependent), "dependent frame basis")
    role = dict(stage=0, replica=0, helper=0, width=9)
    reject("missing_helper_role", lambda: check_roles([], {(0, 0): "p"}, {"p": [9]}),
           "incomplete helper role coverage")
    reject("duplicate_helper_role", lambda: check_roles([role, role], {(0, 0): "p"}, {"p": [9]}),
           "duplicate helper role")
    wrong = dict(role, width=8)
    reject("wrong_helper_width", lambda: check_roles([wrong], {(0, 0): "p"}, {"p": [9]}),
           "literal helper width")
    reject("unpinned_source", lambda: check_pin(b"changed", sha(b"original"), "control"),
           "source hash mismatch: control")
    reject("absent_mutation_anchor", lambda: replace_once("abc", "missing", "x"),
           "mutation must match exactly once: missing")
    reject("ambiguous_mutation_anchor", lambda: replace_once("abcabc", "abc", "x"),
           "mutation must match exactly once: abc")
    # Exact oracle for the independent scalar cost formula, including a signed
    # multi-bit numerator. These are counts of the retained implementation.
    toy = [["scalar", ["add", ["L", 0], ["L", 1], -13, 8], 0]]
    require(price_program(toy)["real_component_primitives"] == 24, "Horner formula control")
    toy[0][1][-1] = 16
    require(price_program(toy)["real_component_primitives"] == 26, "halving charge control")
    return caught


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a receipt instead of comparing EXPECTED.json")
    args = parser.parse_args()
    # Imported production verifiers use assert as admission checks.
    require(__debug__, "run without -O: the audited source requires assertions")
    sys.dont_write_bytecode = True
    sys.set_int_max_str_digits(0)
    pins = json.loads((HERE/"SOURCE.json").read_text())
    for relative, digest in pins["files"].items():
        check_pin((ROOT/relative).read_bytes(), digest, relative)
    owner = read(AUDIT/"OWNERS-AND-PROFILE.json")
    invoice = read(AUDIT/"PREFIX-AND-INVOICE.json")
    spec = read(PACKAGE/"data/SPEC.json")
    expected = read(REPLAY/"ASSEMBLY.json")
    accounting = recount(owner, invoice, spec)
    mutations = source_controls(owner, invoice, expected, ROOT/PACKAGE/"data/SPEC.json",
                               ROOT/pins["assembly_dependency"])
    controls = negative_controls()
    result = canonical(dict(status="PASS_SCOPED_K492_HELPER_ACCOUNTING_AUDIT", base_commit=pins["base_commit"],
                            selected_kappa=expected["kappa"], documented_sites=len(MUTATIONS),
                            accounting=accounting, source_controls=mutations, audit_controls=controls))
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    else:
        require(result == json.loads((HERE/"EXPECTED.json").read_text()), "audit receipt mismatch")
    print(result["status"], "documented_sites=14 rejected=13 equivalent=1",
          "additional_source_controls=2 audit_controls=" + str(len(controls)))


if __name__ == "__main__":
    main()
