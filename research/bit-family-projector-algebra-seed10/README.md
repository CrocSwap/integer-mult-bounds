# PR589 physical-family projector algebra audit

**Independent verification; no new kappa.** This package audits the exact
address-operator identity for family `(pair=1, copy=0)` in the selected PR589
bit supplier. It uses exact rational projector algebra and the block identity
below, not PR #1351's 128-column operator replay. The audit is conditional on
the frozen role map and interval axes recorded by PR #1351.

## Finding

The q-perp projector has rank seven. In child 0, its rank-seven block and
coordinate axis 8 make the rank-eight host; axes 9 through 14 are the rank-six
remainder. Their projectors are orthogonal and sum to the rank-fourteen source
projector. In child 7, the three rank-eight coordinate hosts on axes 36 through
59 and the rank-four remainder on axes 60 through 63 are mutually orthogonal
and sum to the rank-twenty-eight source projector.

For orthogonal projectors P and Q, the exact identity

    D(P) D(Q) = D(P + Q),   D(P) = [[I-P, P], [P, I-P]]

proves the full 128-dimensional address-map equality for each interval. The
verifier checks the exact 64-by-64 projectors, their ranks, idempotence,
orthogonality and sums with fractions. It also rejects an omitted helper, a
same-rank wrong-axis helper, and a duplicated helper.

This adds a symbolic proof route for the two frozen interval maps. It does not
rebuild the selected slot allocator or independently prove PR #1351's family
selection, chronology, or helper lowering. It does not change the paid profile,
the selected kappa, or supplier admission.

## Assignment and overlap

- Track: Bit supplier; OS assignment seed 10; exact base
  `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- The selected certificate is `research/community-frontier1094-audit/ASSEMBLY.json`,
  reviewed in `docs/research/community-batch1099-review.md`. Its selected value
  is kappa `836330098538459/500000000000000000`; its bit side inherits PR589
  commit `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.
- Candidate #1345 exhausts its stated fixed-word single and pair gate-order
  transport scope; #1334 prices its stated revision-3 lever relaxations at
  `a=1/99`; #1351 checks the same family by a different method. This package is
  deliberately an independent second audit of #1351's algebraic identity.
- PR #1307's all-family geometric census supplies useful predecessor context,
  including the warning that weaker slot/count conditions do not imply the
  physical projector map. Its production pipeline found no acceptance bug.
- No pinned sprint coordination issue was found. The local claim is in
  `CLAIM.md`; assignment screening and the fresh overlap snapshot are in
  `../seed10-bit-supplier/ASSIGNMENT.json`.

The exact PR #1351 head, result blob, and all consumed base files are pinned in
`SOURCES.json`. The predecessor result is retained as `PR1351-RESULT.json` so
the audit can be reproduced even if that PR changes or closes.

## Reproduce

From the repository root:

```sh
python3 -I -O -B research/bit-family-projector-algebra-seed10/verify.py
```

Expected output:

```text
PASS_BIT_FAMILY_PROJECTOR_ALGEBRA children=0,7 factors=2+4 q_rank=7 controls=3 no_new_kappa
```

## Open next questions

No new next question is claimed here. PR #1351 already lists the wider check of
all 444 mixed-child families and a full caller replay as follow-up work.

## Credit and disclosure

Credit 1337isnot1337 for PR #1351's frozen target certificate, commdata2338 for
PR #1307's geometric census, and DreamingOfClouds and eumemic for the selected
PR589/PR555 supplier lineage. Prepared by Cinna Davis with substantial OpenAI
Codex assistance for research, implementation, verification and writing. No
subagents or independent human review are claimed. The package carries the
repository Apache-2.0 license.
