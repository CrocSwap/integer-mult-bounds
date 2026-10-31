#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Export the selected P104 bill from authenticated construction data.

The P104 word is by Pierre-Loic Doulcet (hexapode). The complete caller and
helper accounting are by Ali Romman; the controller is by Cinna Davis.
Jacob Alan Sussman supplied productive recursion. The invoice interface is
by zxv. This independent extractor is by Ali Romman with OpenAI Codex assistance.
This check does not replay scalar endpoints, native phases or compiler bounds.
"""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
WORD = "research/p104-helper-subspace-splits/WORD.json.gz"
CONTROLLER = "research/p104-productive-controller/CONTROLLER.json"
RESULT = "research/p104-helper-subspace-splits/RESULT.json"
SELECTED = "certificates/selected-result.json"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def histogram(counts):
    return {str(r): n for r, n in sorted(counts.items()) if n}


def index(value, size):
    require(type(value) is int and 0 <= value < size, "Invalid source index")
    return value


def extract(word, controller):
    """Count the supported source model, without using its stored invoice."""
    require(word.get("schema") == "p104-productive-source/1", "Unsupported word schema")
    public = word["public"]
    require(type(public) is int and 735 <= public <= 750, "Unsupported public inventory")
    frames = []
    for basis in word["frames"]:
        space = {0}
        for v in basis:
            require(type(v) is int and 0 < v < 512 and v not in space,
                    "Invalid independent binary frame")
            space |= {x ^ v for x in tuple(space)}
        frames.append(space)
    require(len(word["initial"]) == len(word["final"]) == public, "Public boundary size")
    for f in word["initial"] + word["final"]:
        index(f, len(frames))
    current = word["initial"][:] + [None] * 8
    owned, paid, operations = set(), Counter(), Counter()
    for event in word["program"]:
        op, role = event[:2]
        index(role, public + 8)
        operations[op] += 1
        if op == "MOVE":
            _, role, a, b, private = event
            index(a, len(frames)); index(b, len(frames))
            require(type(private) is bool and current[role] == a
                    and private == (role in owned), "MOVE source or ownership")
            require(frames[b] < frames[a] if private else frames[a] < frames[b],
                    "MOVE must follow strict frame inclusion")
            paid[abs(len(word["frames"][b]) - len(word["frames"][a]))] += 1
            current[role] = b
        elif op in ("INIT", "CLEAR"):
            _, role, frame = event
            index(frame, len(frames))
            require(role >= public, "Owned operation on a public field")
            if op == "INIT":
                require(role not in owned, "Repeated owned initialization")
                owned.add(role)
                current[role] = frame
            else:
                require(role in owned and current[role] == frame, "Invalid owned erasure")
                owned.remove(role)
                current[role] = None
        else:
            require(op in ("SCALE", "ADD", "COPY"), "Unsupported local opcode: " + str(op))
            require(len(event) == (4 if op == "SCALE" else 5), "Scalar event length")
            q, frame = Fraction(event[-2]), event[-1]
            index(frame, len(frames))
            require(q != 0 and current[role] == frame, "Scalar destination frame")
            if op != "SCALE":
                source = index(event[2], public + 8)
                require(source != role and current[source] == frame, "Scalar source frame")
            if op == "COPY":
                require(role in owned, "COPY destination must be owned")
    require(not owned and current[:public] == word["final"], "Incomplete public or owned exits")
    live = word["live"]
    require(len(live) == len(set(live)) == len(word["ports"]) == 104, "P104 main inventory")
    for role in live:
        index(role, 112)
    main_roles = set(live) | {r + 112 for r in live}
    helpers = Counter()
    for role in range(public):
        if role not in main_roles:
            a, b = word["initial"][role], word["final"][role]
            require(frames[a] < frames[b], "Productive helper inclusion")
            helpers[len(word["frames"][b]) - len(word["frames"][a])] += 1

    require((controller["kind"], controller["pairs"], controller["prefix_pairs"],
             controller["ambient_rank"]) == ("complex", 16, 7, 145),
            "Unsupported P104 controller")
    events, query, idle = Counter(), Counter(), Counter()
    for event in controller["physical_events"]:
        op = event[0]
        events[op] += 1
        if op in ("LOCAL", "QUERY_SHEAR"):
            _, stage, pair, back = event
            index(stage, 33); index(pair, 16)
            require(back is False, "Only forward P104 calls are supported")
            if op == "QUERY_SHEAR":
                query[1] += 104
        elif op == "IDLE":
            _, pair, stages = event
            index(pair, 16)
            require(stages and len(stages) == len(set(stages)), "Invalid whole IDLE stages")
            for stage in stages:
                index(stage, 33)
            idle[8 * len(stages)] += 208
        elif op == "Q_POWER":
            _, role, power = event
            index(role, 32)
            require(type(power) is int and power in (-2, 2), "Unsupported Q_POWER")
        elif op in ("ADD", "SWAP", "SIGNED_SWAP"):
            require(len(event) == (4 if op == "ADD" else 3), "Physical scalar event length")
            a, b = index(event[1], 32), index(event[2], 32)
            require(a != b, "Physical scalar roles must differ")
            if op == "ADD":
                require(type(event[3]) is int and event[3] in (-1, 1), "Unsupported physical ADD")
        else:
            raise ValueError("Unsupported physical opcode: " + str(op))
    main = Counter()
    require(len(controller["diagonal"]) == 32, "Main diagonal size")
    for term in controller["diagonal"]:
        require(len(term) == 34 and type(term[0]) is int and term[0] in (-1, 1)
                and all(type(x) is int and x in (0, 1) for x in term[1:]), "Main diagonal term")
        main[1 + 8 * sum(term[1:])] += 104
    local_paid = Counter({r: n * events["LOCAL"] for r, n in paid.items()})
    local_targets = Counter({r: n * events["LOCAL"] for r, n in helpers.items()})
    invoice = {"schema": "integer-mult-recursive-invoice/v1", "contract": {
        "model": "mixed-target-unnormalized-power-v1",
        "rank_semantics": "H_r costs r^(1-C); debit surrendered productive fields",
        "ambient_rank": 145,
        "boundary": "complete unit before the same mixed-target compiler"},
        "paid": histogram(local_paid + query + idle), "targets": histogram(local_targets + main)}
    components = {"local_paid": histogram(paid), "local_helpers": histogram(helpers),
                  "query_paid": histogram(query), "idle_paid": histogram(idle),
                  "main_targets": histogram(main), "local_events": dict(sorted(operations.items())),
                  "physical_events": dict(sorted(events.items()))}
    return invoice, components


def compare_receipt(invoice, components, receipt):
    """Reject disagreement with the authenticated local, native and caller checks."""
    for name, expected in (
        ("local_paid", receipt["local"]["paid"]),
        ("local_helpers", receipt["local"]["helpers"]),
        ("local_helpers", receipt["native"]["helpers"]),
        ("idle_paid", receipt["physical_caller"]["whole_idle_jobs"]),
        ("main_targets", receipt["physical_caller"]["main_targets"]),
    ):
        require(components[name] == expected, "Receipt mismatch: " + name)
    for name in ("paid", "targets"):
        require(invoice[name] == receipt["complete_cost"][name], "Receipt mismatch: " + name)


def invoice_bytes(invoice):
    """The exact UTF-8/LF payload bound by the evidence and written to stdout."""
    return (json.dumps(invoice, indent=2) + "\n").encode("utf-8")


def export(root=ROOT):
    root = Path(root).resolve()
    record_bytes = (root / SELECTED).read_bytes()
    record = json.loads(record_bytes)
    binding = runpy.run_path(str(ROOT / "scripts/verify_selected_result.py"))
    binding["check"](record, root)
    manifest = json.loads((root / record["source_manifest"]).read_bytes())
    require(manifest.get("format") == "repository-files-sha256-v1", "Explicit source inventory required")
    certificate = json.loads((root / record["certificate"]).read_bytes())
    require(certificate.get("source_result") == RESULT
            and record.get("source_certificate") == RESULT, "Unsupported selected source")
    inputs = {}
    for name in (WORD, CONTROLLER, RESULT):
        require(name in manifest["files"], "Unbound invoice input: " + name)
        raw = binding["explicit_file"](root, name).read_bytes()
        require(sha256(raw).hexdigest() == manifest["files"][name], "Invoice input bytes changed")
        inputs[name] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    invoice, components = extract(inputs[WORD], inputs[CONTROLLER])
    compare_receipt(invoice, components, inputs[RESULT])
    validator = runpy.run_path(str(ROOT / "scripts/compare_recursive_invoices.py"))
    validator["validate_invoice"](invoice)
    evidence = {"schema": "selected-p104-invoice-evidence/v1", "selected_kappa": record["kappa"],
                "invoice_sha256": sha256(invoice_bytes(invoice)).hexdigest(),
                "selected_record_sha256": sha256(record_bytes).hexdigest(),
                "source_head": record["audited_source_head"], "components": components,
                "inputs_sha256": {name: manifest["files"][name] for name in inputs},
                "scope": "Authenticated accounting reconstruction; no native, scalar endpoint or compiler replay"}
    return invoice, evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository or exported selected source tree")
    parser.add_argument("--evidence", type=Path, help="Write source hashes and separate accounting components")
    args = parser.parse_args()
    try:
        invoice, evidence = export(args.root)
        if args.evidence:
            args.evidence.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        # Text stdout can translate LF to CRLF or use another encoding, breaking
        # invoice_sha256 even though the parsed invoice is unchanged.
        sys.stdout.buffer.write(invoice_bytes(invoice))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("Invoice export failed: " + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
