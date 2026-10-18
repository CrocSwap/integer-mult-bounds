"""Binding-coverage trace of the selected acceptance, with real-check fixtures.

Question (adversarial-audit / supplier-boundary-audit, refined): does the
selected supplier obligation "the audited sources are the consumed sources"
follow from the actual source-bound checks?  This checker

1. enumerates the repository inputs consumed by the selected fast acceptance
   (scripts/verify_selected_result.py) and by the documented reproduce driver
   (scripts/verify_frontier1094.py, including its --baseline1042 reuse mode and
   the frozen research/complex-t16-rare-pattern-exchanges chain),
2. classifies every consumed path by the check that binds its bytes:
   manifest-roots inventory, record proof_supplements, record certificate hash,
   package-internal MANIFEST pins, checkpoint self-binding, or NONE,
3. exercises the real check() acceptance function from
   scripts/verify_selected_result.py on synthetic fixtures: bound-file
   mutations must be rejected, unbound-file mutations must be accepted,
4. compares the deterministic receipt to EXPECTED.json.

Read-only on the working tree; fixtures live in a temporary directory.
Python 3.10+, standard library only.  Aaron Wang, with help from opencode.
"""
import json
import hashlib
import re
import shutil
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_selected_result as vsr  # noqa: E402  (real acceptance function)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


# Consumed repository inputs of the selected acceptance paths.  Derived from
# the pinned scripts' literal path reads and subprocess calls; the scan_lits()
# control below re-derives every literal path those scripts mention.
CONSUMED = {
    "fast-path": [
        "certificates/selected-result.json",
        "research/community-frontier1094-audit/ASSEMBLY.json",
        "research/community-frontier1094-audit/SELECTED-SOURCE.json",
        "docs/research/community-batch1099-review.md",
        "docs/research/community-batch1099-integration.json",
    ],
    "reproduce-driver": [
        "scripts/verify_selected_result.py",
        "scripts/verify_frontier1094.py",
        "scripts/verify_frontier1042.py",
        "scripts/verify_replay_coverage.py",
        "certificates/checkpoints/frontier1042.json",
        "research/community-frontier1042-audit/RESULT.json",
        "research/community-batch1099-audit/check_frontier1094.py",
    ],
    "frozen-complex-chain": [
        "research/complex-t16-rare-pattern-exchanges/verify.py",
        "research/complex-t16-rare-pattern-exchanges/MANIFEST.json",
        "research/complex-t16-rare-pattern-exchanges/SOURCE.json",
        "research/complex-t16-rare-pattern-exchanges/CANDIDATE.json",
        "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz",
        "research/complex-t16-rare-pattern-exchanges/data/OWNERS.json.gz",
        "research/complex-t16-rare-pattern-exchanges/data/PLAN.json",
        "research/complex-t16-rare-pattern-exchanges/data/SPEC.json",
    ],
}


def scan_lits(paths):
    """Every '...' literal in the pinned scripts that resolves to a repo file."""
    out = set()
    for name in paths:
        text = (ROOT / name).read_text(encoding="utf-8", errors="replace")
        for lit in re.findall(r"['\"]([A-Za-z0-9_./+-]+\.[A-Za-z0-9]{2,6})['\"]", text):
            if (ROOT / lit).is_file():
                out.add(lit)
    return out


def classify(record, manifest):
    roots = manifest.get("package_roots", [])
    manifest_files = set(manifest["files"])
    supplements = set(record["proof_supplements"])
    rows = []
    for cls, names in CONSUMED.items():
        for name in names:
            path = ROOT / name
            if name == "certificates/selected-result.json":
                bound = "record-root-of-trust"
            elif name == "research/community-frontier1094-audit/SELECTED-SOURCE.json":
                bound = "NONE"
            elif name in manifest_files:
                bound = "manifest-roots-inventory"
            elif name in supplements:
                bound = "record-proof-supplement"
            elif name == record["certificate"]:
                bound = "record-certificate-sha256"
            elif any(name.startswith(r + "/") for r in roots) and name.endswith(
                ("MANIFEST.json", "SOURCE.json")
            ):
                bound = "package-internal-pin-root"
            elif any(name.startswith(r + "/") for r in roots):
                bound = "package-manifest-self-pin"
            elif name.startswith("certificates/checkpoints/"):
                bound = "checkpoint-self-binding"
            elif name.startswith("scripts/") and name in supplements:
                bound = "record-proof-supplement"
            else:
                bound = "NONE"
            rows.append(dict(cls=cls, path=name, binding=bound, exists=path.is_file(),
                             sha256=sha(path) if path.is_file() else None))
    return rows


def expect_error(fn, fragment):
    try:
        fn()
    except ValueError as error:
        assert fragment in str(error), f"wrong rejection {error!r} for {fragment!r}"
        return str(error)
    raise AssertionError("fixture was accepted but must be rejected: " + fragment)


def fixtures():
    """Synthetic fixtures through the real vsr.check acceptance function."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        pkg = root / "research/toy-audit"
        pkg.mkdir(parents=True)
        (root / "research/toy-side").mkdir()
        cert = {"kappa": "3/2000"}
        (pkg / "CERTIFICATE.json").write_text(json.dumps(cert))
        (pkg / "inventory-file.txt").write_text("pinned payload\n")
        (pkg / "SELECTED-SOURCE.json").write_text(json.dumps({
            "files": {
                "CERTIFICATE.json": sha(pkg / "CERTIFICATE.json"),
                "inventory-file.txt": sha(pkg / "inventory-file.txt"),
            }}))
        proof = root / "research/toy-side/PROOF.md"
        proof.write_text("proof bytes\n")
        review = root / "research/toy-side/REVIEW.md"
        review.write_text("existence-only pointer\n")
        record = {
            "kappa": "3/2000", "decimal": "3/2000",
            "certificate": "research/toy-audit/CERTIFICATE.json",
            "certificate_sha256": sha(pkg / "CERTIFICATE.json"),
            "source_manifest": "research/toy-audit/SELECTED-SOURCE.json",
            "proof": "research/toy-side/PROOF.md",
            "proof_supplements": {"research/toy-side/PROOF.md": sha(proof)},
            "review": "research/toy-side/REVIEW.md",
            "validation": "research/toy-side/REVIEW.md",
        }
        outcomes = {}
        vsr.check(record, root)
        outcomes["healthy_accepted"] = True
        # 1. bound inventory mutation is rejected
        (pkg / "inventory-file.txt").write_text("corrupted payload\n")
        outcomes["inventory_mutation"] = expect_error(
            lambda: vsr.check(record, root), "Selected package inventory or bytes changed")
        (pkg / "inventory-file.txt").write_text("pinned payload\n")
        # 2. proof-supplement mutation is rejected
        proof.write_text("corrupted proof\n")
        outcomes["supplement_mutation"] = expect_error(
            lambda: vsr.check(record, root), "Selected proof supplement changed")
        proof.write_text("proof bytes\n")
        # 3. proof without a covering digest is rejected
        record2 = dict(record, proof_supplements={"research/toy-side/REVIEW.md": sha(review)})
        outcomes["uncovered_proof"] = expect_error(
            lambda: vsr.check(record2, root), "Selected primary proof is not covered")
        # 4. existence-only pointer mutation is accepted
        review.write_text("semantically wrong review text\n")
        vsr.check(record, root)
        outcomes["existence_only_mutation_accepted"] = True
        review.write_text("existence-only pointer\n")
        # 5. decimal/kappa disagreement is rejected
        record3 = dict(record, decimal="3/1000")
        outcomes["decimal_mutation"] = expect_error(
            lambda: vsr.check(record3, root), "Selected decimal differs")
        # 6. unbound sidecar consumed by nothing in check() is accepted
        side = root / "research/toy-side/UNBOUND-RECEIPT.json"
        side.write_text("{}")
        vsr.check(record, root)
        side.write_text('{"forged": true}')
        vsr.check(record, root)
        outcomes["unbound_sidecar_accepted"] = True
        # 7. the manifest anchor is unbound: consistent forgery of an
        #    inventory file and the manifest's own digest list is accepted
        (pkg / "inventory-file.txt").write_text("forged payload\n")
        (pkg / "SELECTED-SOURCE.json").write_text(json.dumps({
            "files": {
                "CERTIFICATE.json": sha(pkg / "CERTIFICATE.json"),
                "inventory-file.txt": sha(pkg / "inventory-file.txt"),
            }}))
        vsr.check(record, root)
        outcomes["consistent_manifest_forgery_accepted"] = True
        return outcomes


def main():
    assert __debug__, "assertions required"
    record = load("certificates/selected-result.json")
    manifest = load("research/community-frontier1094-audit/SELECTED-SOURCE.json")
    rows = classify(record, manifest)
    assert all(r["exists"] for r in rows), "missing consumed input"
    lits = scan_lits(["scripts/verify_frontier1094.py", "scripts/verify_selected_result.py"])
    enumerated = {r["path"] for r in rows} | set(record["proof_supplements"])
    unenumerated = sorted(lits for lits in lits if lits not in enumerated)
    counts = {}
    for r in rows:
        counts[r["binding"]] = counts.get(r["binding"], 0) + 1
    unbound = sorted(r["path"] for r in rows if r["binding"] == "NONE")
    fx = fixtures()
    receipt = {
        "status": "PASS_SELECTED_BINDING_COVERAGE_AUDIT",
        "selected_record_sha256": sha(ROOT / "certificates/selected-result.json"),
        "selected_source_sha256": sha(ROOT / "research/community-frontier1094-audit/SELECTED-SOURCE.json"),
        "consumed": rows,
        "binding_counts": counts,
        "unbound_consumed": unbound,
        "script_literals_outside_enumeration": unenumerated,
        "fixtures": fx,
    }
    if "--emit" in sys.argv:
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return
    expected = json.loads((ROOT / "research/selected-binding-coverage-seeda342/EXPECTED.json").read_text())
    assert receipt == expected, "receipt differs from EXPECTED.json"
    print(json.dumps(receipt, indent=2, sort_keys=True))
    print("PASS_SELECTED_BINDING_COVERAGE_AUDIT unbound=%d fixtures=7" % len(unbound))


if __name__ == "__main__":
    main()
