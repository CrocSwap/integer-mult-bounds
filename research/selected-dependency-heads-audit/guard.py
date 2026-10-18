#!/usr/bin/env python3
"""Proposed opt-in binding for selected-record dependency metadata.

This is a supplemental consistency check. It is not wired into
``scripts/verify_selected_result.py`` or the selected cold replay. It does not
authenticate GitHub, prove that a head is the reviewed mathematical source, or
replace certificate/inventory/supplement checks.

Wentao Li (@VictorLiwentao) with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import re
import sys

HEX40 = re.compile(r"^[0-9a-f]{40}$")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_record(record: dict, root: Path, *, integration: dict | None = None):
    """Reject obviously unbound or internally inconsistent dependency metadata.

    Checked:
    - ``audited_source_head`` is a 40-hex digest and equals the head for
      ``source_prs[0]`` in ``reviewed_dependency_heads``;
    - every reviewed dependency key is an integer PR present in ``source_prs``;
    - every reviewed head is a 40-hex digest;
    - ``previous_kappa`` equals the kappa of ``previous_record``;
    - shared keys with ``previous_record.reviewed_dependency_heads`` agree;
    - when ``integration`` is supplied, shared keys with its ``reviewed_heads``
      agree.

    Not checked: live GitHub state, full Git object presence, mathematical
    content of any supplier, or the selected certificate bytes (those remain
    the job of ``verify_selected_result``).
    """
    root = root.resolve()
    heads = record.get("reviewed_dependency_heads")
    require(isinstance(heads, dict) and heads, "Missing reviewed_dependency_heads")
    source_prs = record.get("source_prs")
    require(isinstance(source_prs, list) and source_prs, "Missing source_prs")
    require(all(isinstance(n, int) and n > 0 for n in source_prs), "source_prs must be positive ints")
    require(len(source_prs) == len(set(source_prs)), "source_prs must be unique")

    audited = record.get("audited_source_head")
    require(isinstance(audited, str) and HEX40.fullmatch(audited), "audited_source_head must be 40-hex")
    lead = source_prs[0]
    lead_key = str(lead)
    require(lead_key in heads, "audited PR missing from reviewed_dependency_heads: " + lead_key)
    require(heads[lead_key] == audited, "audited_source_head differs from reviewed head for source_prs[0]")

    for key, digest in heads.items():
        require(isinstance(key, str) and key.isdigit(), "reviewed_dependency_heads keys must be decimal strings")
        number = int(key)
        require(number in source_prs, "reviewed head PR not listed in source_prs: " + key)
        require(isinstance(digest, str) and HEX40.fullmatch(digest), "invalid reviewed head: " + key)

    previous_path = root / record["previous_record"]
    require(previous_path.is_file(), "previous_record missing: " + record["previous_record"])
    previous = load(previous_path)
    require(Fraction(record["previous_kappa"]) == Fraction(previous["kappa"]),
            "previous_kappa differs from previous_record kappa")

    previous_heads = previous.get("reviewed_dependency_heads") or {}
    for key, digest in previous_heads.items():
        if key in heads:
            require(heads[key] == digest, "selected head disagrees with previous_record: " + key)

    for key in ("status", "scope", "reproduce", "review", "validation"):
        require(isinstance(record.get(key), str) and record[key].strip(), "missing metadata field: " + key)

    if integration is not None:
        reviewed = integration.get("reviewed_heads") or {}
        for key, digest in reviewed.items():
            if key in heads:
                require(heads[key] == digest, "selected head disagrees with integration reviewed_heads: " + key)

    return {
        "lead_pr": lead,
        "audited_source_head": audited,
        "reviewed_dependency_heads": len(heads),
        "source_prs": len(source_prs),
        "previous_record": record["previous_record"],
        "previous_kappa": record["previous_kappa"],
        "shared_with_previous": sum(1 for k in previous_heads if k in heads),
        "shared_with_integration": (
            sum(1 for k in (integration.get("reviewed_heads") or {}) if k in heads)
            if integration is not None else None
        ),
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    root = Path(__file__).resolve().parents[2]
    record_path = root / "certificates/selected-result.json"
    integration_path = root / "docs/research/community-batch1099-integration.json"
    if "--root" in argv:
        i = argv.index("--root")
        root = Path(argv[i + 1]).resolve()
        record_path = root / "certificates/selected-result.json"
        integration_path = root / "docs/research/community-batch1099-integration.json"
    record = load(record_path)
    integration = load(integration_path) if integration_path.is_file() else None
    summary = check_record(record, root, integration=integration)
    print("PASS_SELECTED_DEPENDENCY_HEADS_GUARD " + json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
