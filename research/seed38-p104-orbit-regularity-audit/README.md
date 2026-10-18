# Audit of the P104 local-orbit inference

**Status: second independent proof-step audit; no new κ, decoder, or supplier.**
Following the completed claim #1275 and PR #1292, this package checks the local
algebraic-geometric implication used by Navinor's
[PR #1292](https://github.com/CrocSwap/integer-mult-bounds/pull/1292), at its
exact head `7a8325f6c8e5a6830ce919965a2959ac459e010a`.

PR #1292 proves by an exact finite-field certificate that, at `K0 = 2G`, the
tangent space of the masked rank-eight variety on each P104 frame-pair class
is the tangent space of the diagonal-torus orbit. Its README then concludes
that the variety and orbit agree locally. This note spells out that implication
and checks the dimension hypotheses against the pinned certificate.

## Finding

The inference is valid under the stated certificate. For each of the three
P104 representatives, `v = 104`; the reduced M-system has 832 unknowns and
rank 665, so its kernel has dimension 167. The 64 GL(8) parameterization
directions map to zero, leaving a tangent image of dimension 103, exactly
`v - 1`, the dimension of the torus orbit. The same equalities hold for P120
and P112 with dimensions 119 and 111.

The wrapper also checks every one of the 168 stated gauge and torus generators
against every reduced M-system row modulo `2^31 - 1` for all three P104
representatives. This is an exhaustive finite-field consistency check alongside
the source script's two random-combination checks; the rational kernel
inclusion follows from the displayed gauge and torus formulas.

The orbit is a smooth subvariety of the affine algebraic set defined by
`rank(K) <= 8`, `K_ii = 4`, and `K_ij = 0` on orthogonal live pairs. Its
dimension gives a lower bound on the local dimension of that set. The exact
tangent dimension gives the matching upper bound. Thus the local ring is
regular at `2G`, and the equal-dimensional orbit inclusion is locally open.
The germs agree. The full argument and scope are in [PROOF.md](PROOF.md).

This verifies the local conclusion only. It does not exclude disconnected
off-orbit solution components on P104, rank-nine costly parts, other masks, or
any improvement to the selected moment. The selected κ remains
`836330098538459/500000000000000000`; the complex supplier remains binding.

## Reproduce

From the repository root, with Python 3.12+ and the standard library:

```sh
python3 -I -B research/seed38-p104-orbit-regularity-audit/verify.py
```

Expected final marker:

```text
PASS_P104_LOCAL_ORBIT_REGULARITY: tangent_dim=103 orbit_dim=103 classes=3 local_only no_new_kappa
```

The verifier checks all pinned source hashes, runs the unchanged PR #1292 exact
certificate, exhaustively checks the stated P104 kernel generators modulo the
pinned prime, and checks the dimension arithmetic used in this audit. Its
certificate output is finite evidence for the tangent-space premises; the
regularity argument is stated separately in `PROOF.md`.

## Open next questions

- **Global P104 rank-eight rigidity:** an off-orbit component far from `2G`
  remains possible. A useful next step is the exact bilinear system on one
  representative from each of the three relative-position classes. The blocker
  is a complete classification of those components.
- **Rank-nine masked parts:** the rank-eight tangent result does not constrain
  a ninth costly term. A useful first step is one explicitly pinned ninth
  support on one P104 class, with its complete copied-information cost. The
  blocker is choosing a support whose full bill could improve the current
  complex moment.

## Attribution

This audit is distinct from PR #1292's tangent-system construction: it checks
the geometric implication from that exact tangent certificate to a local orbit
statement. Credit Navinor (with opencode assistance) for PR #1292; DreamingOfClouds
for the PR #717 mask model; themilkman216 for PR #968's frame-pair decoder and
7/13 floor; and burntout76 for PR #1212's P112/P120 rigidity result. This
package was prepared with substantial OpenAI Codex assistance; no independent
human review is claimed.
