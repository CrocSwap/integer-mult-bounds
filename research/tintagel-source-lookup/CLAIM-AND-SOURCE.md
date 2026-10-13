# Claim and source ledger

Checked 12 October 2026. This is a bounded overlap assessment for the
lookup note, not a priority claim or a review of every open submission.

| Item | Evidence | Scope |
| --- | --- | --- |
| Source form and neighboring triples | `upstream/build/sections/03-motifs.tex`, current main `db0e57bc7f36b5ac0fc844ad7ce1396165ee6647`, lines 210–230 | Original OpenAI manuscript bit label geometry, preserved in the repository maintained by Douglas Colkitt, including `G=I-J/9` and intersection-one orthogonality. |
| Correct projection coefficient | Direct calculation from that form; local Tintagel v9 corrected proof | `V_L(j)=(3*1_{j in L}-1)/6`, not an independent new geometry result. |
| Lookup contraction | `README.md`, adjacent-exterior proof | Paper induction over complete pivot blocks and all retained rows, using a column-a invariant rather than a unit-row claim. This is the scoped claim offered here. |
| Finite normal forms | `replay.py` | 1,936 exact rational cases, 20/17 alphabet, 65,416 word records, 11,584 pivots. This computation does not prove the contraction lemma. |
| Corroboration | `replay.py --stress`; unpublished local v9 review | 6,090 h=7–9 compressed cases are publicly replayable here. The local review reports another 6,984 operation-level deletions in 6,510 h=3–9 matrices; that separate check is not reproduced in this patch. |
| Rank and reference termination | `README.md` projector calculation and ordered reference | `rank A=h-r`; exactly `h-r` pivots in `h` row iterations. No physical execution claim. |
| Physical provider | Local v9 independent re-review | **Not linked** above Q=11 at the recursive pivot branch; full h=5/h=100 source graphs had structural validation only. |

The frozen local Tintagel v9 archive has SHA256
`1978c40c7b5f23a818096df10f713e23d95b7f27a1e97550093d2ce3e02cbb09`.
Its unpublished independent re-review on 12 October 2026 accepted the corrected
coefficient, all-row contraction, and finite replay while explicitly
rejecting any inference of a full provider or Lean proof. The earlier
v1/v2 prose contained incorrect coefficient and zero-row claims; this
note uses the corrected v3 proof only. The review is local provenance,
not a public theorem certification.

A separate bounded Claude Opus review on 12 October 2026 requested the
explicit Gram/projection derivation, pivot-row and rank reasoning, and
the computer-assisted label now in `README.md`. It also suggested the
false stronger statement \(\text{row }b=-e_a\), which an independent
exact-commit publication review refuted at \(h=5,S=\{0,1,2\}\).
The exported proof now keeps only the weaker column-\(a\) invariant;
`replay.py` checks the counterexample as a regression. Opus
**did not run** `replay.py` or verify
the 65,416 records, digest, or 20/17 alphabet; those facts rely on the
local replay and remain independently executable from this patch. The
exact-commit reviewer separately replayed the 1,936-case checker and
confirmed the finite counts, but the all-height step remains the
paper induction. These reviews support scrutiny, not formal certification.

## Overlap checked

The existing clean source mirror's receipt 224 observed CrocSwap main at
`db0e57bc7f36b5ac0fc844ad7ce1396165ee6647`. An exact text search
of that tree found no `Tintagel`, `gap skeleton`, or all-retained-row
lookup proof. Current GitHub PR title/body searches for `Tintagel`,
`lookup`, `gap skeleton`, and source-complement language found no matching
submission. [PR #390](https://github.com/CrocSwap/integer-mult-bounds/pull/390)
is the related heterogeneous-bank proposal;
[PR #430](https://github.com/CrocSwap/integer-mult-bounds/pull/430)
audits its physical interface and B3 composition. Neither supplied the
adjacent-exterior lookup proof in its reviewed description. An exact
source and proof comparison of every open PR was not performed, so this
supports a narrow contribution claim, not exclusivity or priority.

Receipt 224 also records [PR #576](https://github.com/CrocSwap/integer-mult-bounds/pull/576)
advancing to `f4e9f7e85e9211cf6ba6c5789da2aa0902d9121e`. Its
one-commit old-to-new comparison lists only an owner assignment archive,
plan, witness specification, and manifest. The visible diff has no
lookup contraction, source-factor table, or one-cell interface code.
The compressed owner archive's contents were not inspected. This is
limited negative overlap evidence; this note does not depend on those
assignments.

The current repository README still advertises a **conditional**
integer-multiplication record and lists all-size compiler and physical
interfaces as assumptions. This note must not be read as resolving
those assumptions. The local v9 source graph stops at
`branch_number(builder, 'Q', {11: base_edge})` for a Q>11 rank-one
pivot. Its successful h=100 graph compilation is structural, not a
successful full source-bank run. The fixed-source-\(W\) grouping scope,
S0-transformed-input premise, and exceptional terms remain intact.

## Replay and review rule

Run `python3 -I -B research/tintagel-source-lookup/replay.py --stress`.
Check the paper induction separately. Treat certificate success,
conditional mathematical arguments, structural graph compilation,
finite physical runs, and formal proofs as different evidence classes.
The public patch contains only the lookup note and a standard-library
exact checker. It imports no confidential transcripts or downstream
machine code and changes no selected bound or source pin.
