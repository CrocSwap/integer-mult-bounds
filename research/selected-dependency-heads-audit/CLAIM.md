# CLAIM (advisory)

**CLAIM** (supplier-boundary-audit, scope refined)

Question: do `certificates/selected-result.json` fields
`reviewed_dependency_heads`, `audited_source_head`, `source_prs`,
`previous_kappa`, `status`, `scope` and `reproduce` follow from any
source-bound acceptance check on the selected reproduce path, or can a
well-formed record with false dependency heads still pass
`scripts/verify_selected_result.py` while leaving
certificate/kappa/inventory/supplements unchanged?

Base / predecessors: main `0b1cccf8`; `research/owner-boundary-audit`
(method pattern); `research/selected-proof-binding` (primary-proof coverage
gap, repaired); `research/ledger-decision-binding` (considered selected
dependency-head consistency but chose a ledger failure mode at an earlier
base); `research/frontier1094-ancestry-binding-seed69` (reuse-mode ancestry
binding; orthogonal). Distinct from discussion #1730
(certificate/invoice/outer field binding to cold replay).

Method and domain: (1) mutate only the named metadata fields and re-run
`verify_selected_result.check` against the live checkout; (2) confirm that no
top-level Python file under `scripts/` (`scripts/*.py`) mentions the head
fields; (3) independently recheck the published heads for internal consistency
with `previous_record` and batch1099 integration `reviewed_heads`; (4) ship a
scoped package with positive/negative fixtures and a proposed opt-in guard
(not applied to selected scripts).

Expected artifact: `research/selected-dependency-heads-audit/`; no κ claim;
selected frontier untouched.

Claim expires: 2026-10-14T10:11Z UTC.
