# Selected dependency-head metadata is unchecked by the fast selected-record checker

**Adversarial metadata audit and proposed opt-in guard; no new kappa.**
Task card `supplier-boundary-audit`, scope **refined** to the selected record's
dependency-head and related publication fields. Base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The selected frontier, cold replay
and `scripts/verify_selected_result.py` are **not** modified.

## Finding

`scripts/verify_selected_result.py` binds certificate bytes, exact κ, the
selected source inventory and every proof supplement. It does **not** read:

- `reviewed_dependency_heads`
- `audited_source_head`
- `source_prs`
- `previous_kappa`
- `status` / `scope` / `reproduce`

Mutating only those fields, while leaving the certificate digest, inventory and
supplements untouched, still yields acceptance. Among top-level Python files
under `scripts/` (`scripts/*.py`), none mention `reviewed_dependency_heads` or
`audited_source_head`. This package does not run `make frontier1094-verify` and
does not claim a repository-wide source scan.

**Severity: low.** This is a publication/attribution consistency gap, not a
counterfeit construction acceptance. κ, the finite assembly and inventoried
supplier packages remain hash-bound. Reviewers who treat the head table as
machine-checked provenance currently over-read the checker.

The published #1094 record is nevertheless internally consistent:

| Check | Result |
| --- | --- |
| `audited_source_head` equals head of `source_prs[0]` (#1094) | yes |
| `previous_kappa` equals `certificates/checkpoints/frontier1042.json` κ | yes |
| All 48 reviewed head keys appear in `source_prs` | yes |
| Shared heads with the previous checkpoint (35) | identical |
| Shared heads with batch1099 integration `reviewed_heads` (13) | identical |

Independent GitHub PR-head spot checks for #1094, #1087, #1042, #589, #858 and
#987 matched the published digests in the session that authored this package;
those network observations are **not** part of the offline replay.

## Reproduce

The audit and guard run with Python 3.10+ (standard library only). The
registered `scripts/research_package.py` runner for this package requires
**Python 3.12**. Prefer the copy/paste recipe below:

```sh
python3.12 -B research/selected-dependency-heads-audit/verify.py
python3.12 -B research/selected-dependency-heads-audit/guard.py
python3.12 -B scripts/research_package.py --package research/selected-dependency-heads-audit
```

Expected final verifier status: `PASS_SELECTED_DEPENDENCY_HEADS_AUDIT`.
The deterministic receipt must equal [EXPECTED.json](EXPECTED.json).
Normal verification writes no files. After an intentional code change, regenerate
with `python3.12 -B research/selected-dependency-heads-audit/verify.py --write`.

The verifier refuses `-O` (assertions must stay enabled). Positive control: the
live selected record passes `verify_selected_result.check`. Negative control: a
mutated `certificate_sha256` is still rejected. Four metadata mutants are
accepted by the live checker; three head/`previous_kappa`/`source_prs` mutants
are rejected by the proposed [guard.py](guard.py).

## Proposed guard (not applied)

[guard.py](guard.py) is an opt-in consistency check. It binds:

1. `audited_source_head` to the reviewed head of `source_prs[0]`;
2. every reviewed head key to membership in `source_prs` and 40-hex form;
3. `previous_kappa` to the kappa of `previous_record`;
4. shared heads with the previous checkpoint;
5. optionally, shared heads with
   `docs/research/community-batch1099-integration.json` `reviewed_heads`.

It does **not** authenticate GitHub, prove a head is the reviewed mathematical
source, or replace certificate/inventory checks. This package deliberately does
not patch `scripts/verify_selected_result.py`; wiring the guard is a maintainer
decision.

## Task card, overlap and scope

Chooser track `adversarial-audit`, nonce `1e43292e32b5524502e2a2fde0d33272`,
card `supplier-boundary-audit`. First working command
`research/owner-boundary-audit/verify.py` passed. Scope refined to one named
current condition: whether selected dependency-head metadata follows from the
actual source-bound selected-record checker.

Nearest predecessors (credit retained; this package adds a different object):

- [owner-boundary-audit](../owner-boundary-audit/README.md) — method pattern
  (timing-only omission vs full controller);
- [selected-proof-binding](../selected-proof-binding/README.md) — primary-proof
  coverage gap in the same checker family (repaired upstream);
- [ledger-decision-binding](../ledger-decision-binding/README.md) — considered
  selected dependency-head consistency at an earlier base, then audited a
  ledger failure mode instead;
- [frontier1094-ancestry-binding-seed69](../frontier1094-ancestry-binding-seed69/README.md)
  — reuse-mode ancestry binding; orthogonal to this metadata surface;
- Discussion/claim #1730 — certificate/invoice/outer binding to the cold replay;
  distinct fields and path.

Advisory claim text: [CLAIM.md](CLAIM.md).

## Open next questions

1. **Should `verify_selected_result.py` grow an optional or mandatory dependency-head
   consistency clause?** It matters because reviewers cite the head table as
   provenance. First step: decide whether previous-checkpoint agreement and
   `source_prs[0]` binding are enough, or whether integration `reviewed_heads`
   must also be named by the selected record. Blocked by: maintainer product
   choice; this package only supplies the mutation evidence and a draft guard.

2. **Should `status` / `scope` / `reproduce` gain digest pins or schema checks?**
   They are also unchecked, but have no local oracle in this package beyond
   non-emptiness. First step: inventory which publication fields are machine
   cited by downstream tooling. Blocked by: no current consumer identified among
   top-level `scripts/*.py` during this session.

## Credit and limits

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Not independent human peer review. Apache-2.0. Predecessor authors above retain
credit for their packages and reviews. Inherited all-size/compiler, hosting,
precision/tape, analytic and bit H1–H5 obligations are untouched. This is not a
formal multiplication theorem. Selected frontier left unchanged.
