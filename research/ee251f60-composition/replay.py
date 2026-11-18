"""Source-bound reconstruction and scoped checks, not a universal acceptance gate.
Apache-2.0; prepared with substantial OpenAI Codex assistance.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":")).encode()

def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()

def need(x, message):
    if not x:
        raise ValueError(message)

def read(p):
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)

def reconstruct(source, patch):
    need(digest(source) == patch["source"], "wrong predecessor for this edit, not another candidate gate")
    word = copy.deepcopy(source)
    previous = 0
    program = []
    for e in patch["edits"]:
        i, j = e["start"], e["stop"]
        need(type(i) is int and type(j) is int and previous <= i <= j <= len(source["program"]), "invalid edit interval")
        need(source["program"][i:j] == e["before"], "edit preimage mismatch")
        program.extend(source["program"][previous:i])
        program.extend(e["after"])
        previous = j
    program.extend(source["program"][previous:])
    word["program"] = program
    need(digest(word) == patch["candidate"], "wrong reconstructed artifact")
    return word

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    out = args.out.resolve()
    need(not out.exists(), "fresh output directory required")
    manifest = read(root / "MANIFEST.json")
    for entry in manifest["files"]:
        p = (root / entry["path"]).resolve()
        need(p.is_relative_to(root), "manifest path escape")
        need(hashlib.sha256(p.read_bytes()).hexdigest() == entry["sha256"], "changed input: " + entry["path"])
    source = read(root / "data/K372-2-WORD.json.gz")
    patch = read(root / "EDIT.json")
    word = reconstruct(source, patch)
    out.mkdir(parents=True)
    candidate_path = out / "WORD.json.gz"
    candidate_path.write_bytes(gzip.compress(canonical(word), mtime=0))
    audit = load(root / "src/integer_grid_audit.py", "ee251_audit")
    finite = audit.run_audit(candidate_path, root / "data/CERTS.json", root / "data/HEADER.json", out / "finite", 225 * 2**40)
    need(finite["status"] == "PASS_FINITE_INTEGER_ROWS_AND_CLEAR_RELATIONS", "finite audit failed")
    counts = load(root / "src/ordinary_tape_audit.py", "ee251_counts")
    caller = read(root / "data/CALLER.json.gz")
    counts.validate_caller(caller)
    inventory = counts.native_inventory(word)
    paid, targets, empty = counts.invoice_counts(caller, inventory)
    invoice = read(root / "data/INVOICE.json")
    need({str(k):v for k,v in paid.items()} == invoice["paid"], "paid histogram mismatch")
    need({str(k):v for k,v in targets.items()} == invoice["targets"], "target histogram mismatch")
    expected = read(root / "evidence/PRICE-SUMMARY.json")
    prices = []
    for point in expected["outcomes"]:
        exponent = str(__import__('decimal').Decimal(1) - __import__('decimal').Decimal(point["kappa"]))
        command = [sys.executable, "-I", "-B", str(root / "src/evaluate_recursive_power.py"), str(root / "data/INVOICE-ZERO.json"), str(root / "data/INVOICE.json"), "--exponent", exponent, "--bits", "256"]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=120, check=True)
        actual = json.loads(result.stdout)
        need(actual["classification"] == point["classification"] and actual["new_minus_old"] == point["new_minus_old"], "directed price result mismatch")
        (out / ("price-" + point["label"] + ".json")).write_text(result.stdout, encoding="utf-8")
        prices.append({"kappa":point["kappa"], "classification":actual["classification"]})
    # Two rejection controls test reconstruction; a third tests actual row semantics.
    bad_patch = copy.deepcopy(patch)
    bad_patch["edits"][0]["before"].append(["invalid"])
    try:
        reconstruct(source, bad_patch)
    except ValueError:
        pass
    else:
        raise ValueError("preimage mutation was accepted")
    bad_source = copy.deepcopy(source)
    bad_source["program"][0] = ["invalid"]
    try:
        reconstruct(bad_source, patch)
    except ValueError:
        pass
    else:
        raise ValueError("source mutation was accepted")
    mutant = copy.deepcopy(word)
    index = next(i for i,e in enumerate(mutant["program"]) if e[0] == "ADD")
    from fractions import Fraction
    mutant["program"][index][3] = str(-Fraction(mutant["program"][index][3]))
    try:
        audit.audit_word(mutant, read(root / "data/CERTS.json"), 225 * 2**40, read(root / "data/HEADER.json"))
    except audit.AuditFailure as error:
        rejection = error.kind
    else:
        raise ValueError("semantic sign mutation was accepted")
    report = {"status":"PASS_SCOPED_EE251F60_REPLAY", "candidate":digest(word), "source":digest(source), "events":len(word["program"]), "finite_status":finite["status"], "inventory":inventory, "prices":prices, "rejection_controls":["wrong source", "wrong edit preimage", rejection], "scope":"Fresh exact reconstruction, all public rows/CLEAR, actual caller paid/target recount and original 256-bit price CLI. Recorded ordinary/precision/native-phase evidence is reused, not rerun; whole physical and analytic obligations remain open."}
    for entry in manifest["files"]:
        need(hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest() == entry["sha256"], "input changed during replay")
    (out / "RESULT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))

if __name__ == "__main__":
    main()
