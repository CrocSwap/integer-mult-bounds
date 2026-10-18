#!/usr/bin/env python3
"""Audit: selected dependency-head metadata is unchecked by verify_selected_result.

Finding (scoped; no new kappa):
``scripts/verify_selected_result.py`` binds certificate bytes, exact kappa,
source inventory and proof supplements. It does **not** read
``reviewed_dependency_heads``, ``audited_source_head``, ``source_prs``,
``previous_kappa``, ``status``, ``scope`` or ``reproduce``. Mutating only those
fields leaves the checker accepting the record. Among top-level Python files
under ``scripts/`` (``scripts/*.py``), none mention the head fields. The
published #1094 record remains internally consistent with its previous
checkpoint and with the batch1099 integration ``reviewed_heads`` on their
shared keys.

This package does not change the selected frontier or selected scripts, and
does not run a cold frontier replay. ``guard.py`` is a proposed opt-in check
only.

Wentao Li (@VictorLiwentao) with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import copy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import re
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
EXPECTED_PATH = PACKAGE / "EXPECTED.json"

RECORD_REL = "certificates/selected-result.json"
PREV_REL = "certificates/checkpoints/frontier1042.json"
INTEGRATION_REL = "docs/research/community-batch1099-integration.json"
CHECKER_REL = "scripts/verify_selected_result.py"

UNCHECKED_FIELDS = (
    "reviewed_dependency_heads",
    "audited_source_head",
    "source_prs",
    "previous_kappa",
    "status",
    "scope",
    "reproduce",
)


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def sha(data: bytes) -> str:
    return sha256(data).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def pin_sources():
    sources = load(PACKAGE / "SOURCES.json")
    require(sources["base_commit"], "SOURCES.json missing base_commit")
    for entry in sources["files"]:
        path = ROOT / entry["path"]
        require(path.is_file(), "missing pinned source: " + entry["path"])
        digest = sha(path.read_bytes())
        require(digest == entry["sha256"], "pinned source bytes changed: " + entry["path"])
    return sources


def load_checker():
    path = ROOT / CHECKER_REL
    spec = importlib.util.spec_from_file_location("verify_selected_result_audit", path)
    require(spec is not None and spec.loader is not None, "cannot load verify_selected_result")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def accept(module, record, root, label):
    try:
        kappa = module.check(record, root=root)
        return {"accepted": True, "kappa": str(kappa), "error": None, "label": label}
    except Exception as exc:  # noqa: BLE001 - record exact rejection text
        return {"accepted": False, "kappa": None, "error": f"{type(exc).__name__}: {exc}", "label": label}


def reject(module, record, root, label):
    outcome = accept(module, record, root, label)
    require(not outcome["accepted"], "expected rejection for " + label)
    return outcome


def mutate_heads(record):
    mutant = copy.deepcopy(record)
    mutant["audited_source_head"] = "0" * 40
    mutant["reviewed_dependency_heads"] = {k: "deadbeef" * 5 for k in mutant["reviewed_dependency_heads"]}
    mutant["reviewed_dependency_heads"][str(mutant["source_prs"][0])] = "1" * 40
    return mutant


def mutate_previous_kappa(record):
    mutant = copy.deepcopy(record)
    mutant["previous_kappa"] = "1/2"
    return mutant


def mutate_source_prs(record):
    mutant = copy.deepcopy(record)
    mutant["source_prs"] = [999999] + list(mutant["source_prs"][1:])
    return mutant


def mutate_publication(record):
    mutant = copy.deepcopy(record)
    mutant["status"] = "FAKE_STATUS"
    mutant["scope"] = "FAKE_SCOPE"
    mutant["reproduce"] = "make nonexistent-target"
    return mutant


def mutate_certificate_digest(record):
    """Negative control: the live checker must still reject certificate drift."""
    mutant = copy.deepcopy(record)
    mutant["certificate_sha256"] = "0" * 64
    return mutant


def static_script_scan():
    """Require that acceptance code does not *read* the metadata fields.

    A docstring may mention the word ``reproduce`` ("reproduce command") without
    binding ``record['reproduce']``. Look for subscription / ``.get`` access.
    """
    text = (ROOT / CHECKER_REL).read_text(encoding="utf-8")
    access_hits = {}
    for name in UNCHECKED_FIELDS:
        patterns = (
            f"record['{name}']",
            f'record["{name}"]',
            f"record.get('{name}'",
            f'record.get("{name}"',
            f"['{name}']",
            f'["{name}"]',
        )
        # Narrow ``['name']`` / ``["name"]`` to lines that also mention record.
        line_hits = []
        for i, line in enumerate(text.splitlines(), 1):
            if name not in line:
                continue
            if any(p in line for p in patterns[:4]) or (
                ("record" in line) and (f"['{name}']" in line or f'["{name}"]' in line)
            ):
                line_hits.append(i)
        access_hits[name] = line_hits
    script_hits = []
    for path in sorted((ROOT / "scripts").glob("*.py")):
        body = path.read_text(encoding="utf-8", errors="replace")
        if "reviewed_dependency_heads" in body or "audited_source_head" in body:
            script_hits.append(path.name)
    return {
        "verify_selected_result_record_access_lines": access_hits,
        "top_level_scripts_py_mentioning_head_fields": script_hits,
        "static_scan_scope": "top-level scripts/*.py only; not a recursive repository scan",
    }


def published_consistency(record, previous, integration):
    heads = {str(k): v for k, v in record["reviewed_dependency_heads"].items()}
    prev_heads = {str(k): v for k, v in previous.get("reviewed_dependency_heads", {}).items()}
    integ_heads = {str(k): v for k, v in integration.get("reviewed_heads", {}).items()}
    shared_prev = sorted(set(heads) & set(prev_heads), key=int)
    shared_integ = sorted(set(heads) & set(integ_heads), key=int)
    return {
        "audited_equals_lead_head": record["audited_source_head"] == heads[str(record["source_prs"][0])],
        "lead_pr": record["source_prs"][0],
        "previous_kappa_matches_checkpoint": record["previous_kappa"] == previous["kappa"],
        "heads_subset_of_source_prs": sorted(
            {int(k) for k in heads} - set(record["source_prs"])
        )
        == [],
        "shared_with_previous_count": len(shared_prev),
        "shared_with_previous_diffs": [k for k in shared_prev if heads[k] != prev_heads[k]],
        "shared_with_integration_count": len(shared_integ),
        "shared_with_integration_diffs": [k for k in shared_integ if heads[k] != integ_heads[k]],
        "new_heads_since_previous": sorted(set(heads) - set(prev_heads), key=int),
        "n_reviewed_dependency_heads": len(heads),
        "n_source_prs": len(record["source_prs"]),
        "hex40_heads": all(re.fullmatch(r"[0-9a-f]{40}", h) for h in heads.values()),
    }


def proposed_guard_outcomes(record, root, integration):
    sys.path.insert(0, str(PACKAGE))
    import guard  # noqa: WPS433 - package-local proposed check

    live = {"accepted": True, "error": None}
    try:
        guard.check_record(record, root, integration=integration)
    except Exception as exc:  # noqa: BLE001
        live = {"accepted": False, "error": f"{type(exc).__name__}: {exc}"}

    outcomes = {"live": live, "mutations": {}}
    # Publication prose fields (status/scope/reproduce) have no local digest oracle
    # in this package; the gap is documented via the live checker mutants only.
    for label, builder in (
        ("false_heads", mutate_heads),
        ("false_previous_kappa", mutate_previous_kappa),
        ("false_source_prs", mutate_source_prs),
    ):
        try:
            guard.check_record(builder(record), root, integration=integration)
            outcomes["mutations"][label] = {"accepted": True, "error": None}
        except Exception as exc:  # noqa: BLE001
            outcomes["mutations"][label] = {
                "accepted": False,
                "error": f"{type(exc).__name__}: {exc}",
            }
    return outcomes


def build_receipt(write=False):
    sources = pin_sources()
    record = load(ROOT / RECORD_REL)
    previous = load(ROOT / PREV_REL)
    integration = load(ROOT / INTEGRATION_REL)
    module = load_checker()

    require(not sys.flags.optimize, "Assertions must remain enabled")

    live = accept(module, record, ROOT, "live_selected_record")
    require(live["accepted"], "live selected record must pass verify_selected_result")

    mutants = {
        "false_heads": accept(module, mutate_heads(record), ROOT, "false_heads"),
        "false_previous_kappa": accept(module, mutate_previous_kappa(record), ROOT, "false_previous_kappa"),
        "false_source_prs": accept(module, mutate_source_prs(record), ROOT, "false_source_prs"),
        "false_publication": accept(module, mutate_publication(record), ROOT, "false_publication"),
    }
    for label, outcome in mutants.items():
        require(outcome["accepted"], "current checker unexpectedly rejects " + label)

    digest_control = reject(module, mutate_certificate_digest(record), ROOT, "false_certificate_sha256")

    scan = static_script_scan()
    require(all(not v for v in scan["verify_selected_result_record_access_lines"].values()),
            "verify_selected_result unexpectedly reads an unchecked metadata field")
    require(scan["top_level_scripts_py_mentioning_head_fields"] == [],
            "top-level scripts/*.py unexpectedly references dependency head fields")

    consistency = published_consistency(record, previous, integration)
    require(consistency["audited_equals_lead_head"], "published audited head mismatch")
    require(consistency["previous_kappa_matches_checkpoint"], "published previous_kappa mismatch")
    require(consistency["heads_subset_of_source_prs"], "published head not in source_prs")
    require(consistency["shared_with_previous_diffs"] == [], "published head disagrees with previous_record")
    require(consistency["shared_with_integration_diffs"] == [], "published head disagrees with integration")
    require(consistency["hex40_heads"], "published head is not 40-hex")

    guard_outcomes = proposed_guard_outcomes(record, ROOT, integration)
    require(guard_outcomes["live"]["accepted"], "proposed guard must accept live record")
    for label, outcome in guard_outcomes["mutations"].items():
        require(not outcome["accepted"], "proposed guard must reject " + label)

    receipt = {
        "status": "PASS_SELECTED_DEPENDENCY_HEADS_AUDIT",
        "base_commit": sources["base_commit"],
        "selected_kappa": record["kappa"],
        "selected_record_sha256": sha((ROOT / RECORD_REL).read_bytes()),
        "checker_sha256": sha((ROOT / CHECKER_REL).read_bytes()),
        "live_checker_accepts_selected": live,
        "live_checker_accepts_metadata_mutants": mutants,
        "live_checker_rejects_certificate_digest_mutant": {
            "accepted": digest_control["accepted"],
            "error_prefix": (digest_control["error"] or "")[:80],
        },
        "static_scan": scan,
        "published_consistency": consistency,
        "proposed_guard": {
            "accepts_live": guard_outcomes["live"]["accepted"],
            "rejects_mutations": {
                label: (not outcome["accepted"]) for label, outcome in guard_outcomes["mutations"].items()
            },
            "mutation_errors": {
                label: outcome["error"] for label, outcome in guard_outcomes["mutations"].items()
            },
        },
        "severity": "low",
        "severity_rationale": (
            "Publication/attribution metadata only; certificate, inventory and "
            "supplements remain hash-bound. No kappa change and no counterfeit "
            "construction acceptance was demonstrated."
        ),
        "scope": (
            "Finite metadata audit of the selected #1094 record and "
            "verify_selected_result.py acceptance surface, plus a static scan "
            "of top-level scripts/*.py only. Not a full cold replay, Lean "
            "proof, repository-wide source scan, or GitHub authenticity theorem."
        ),
    }

    if write:
        EXPECTED_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def reject_duplicate_json_keys() -> None:
    """Fail if any package JSON object repeats a key (stdlib json keeps the last)."""

    def check_obj(raw: str, label: str) -> None:
        def pairs_hook(pairs):
            seen = set()
            out = {}
            for k, v in pairs:
                require(k not in seen, f"duplicate JSON key {k!r} in {label}")
                seen.add(k)
                out[k] = v
            return out

        json.loads(raw, object_pairs_hook=pairs_hook)

    for path in sorted(PACKAGE.glob("*.json")):
        check_obj(path.read_text(encoding="utf-8"), path.name)


def main():
    write = "--write" in sys.argv
    reject_duplicate_json_keys()
    before = EXPECTED_PATH.read_bytes() if EXPECTED_PATH.is_file() else None
    receipt = build_receipt(write=write)
    expected = load(EXPECTED_PATH)
    # Compare without depending on exact exception wording for the digest control
    # beyond a stable prefix already stored.
    require(receipt == expected, "receipt differs from EXPECTED.json; pass --write after intentional change")
    if not write:
        after = EXPECTED_PATH.read_bytes()
        require(before == after, "read-only verify mutated EXPECTED.json")
        forged = dict(expected)
        forged = json.loads(json.dumps(forged))
        forged["severity"] = "critical"
        require(receipt != forged, "corruption control: severity forge must differ from recomputed receipt")
    print(receipt["status"])
    print(
        "live_checker_accepts_metadata_mutants="
        + ",".join(sorted(receipt["live_checker_accepts_metadata_mutants"]))
    )
    print(
        "proposed_guard_rejects="
        + ",".join(
            k for k, ok in sorted(receipt["proposed_guard"]["rejects_mutations"].items()) if ok
        )
    )
    print(
        "published_heads={n_heads}; shared_prev={sp}; shared_integ={si}".format(
            n_heads=receipt["published_consistency"]["n_reviewed_dependency_heads"],
            sp=receipt["published_consistency"]["shared_with_previous_count"],
            si=receipt["published_consistency"]["shared_with_integration_count"],
        )
    )


if __name__ == "__main__":
    main()
