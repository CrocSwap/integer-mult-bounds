# Sprint claim: dyadic query runs

- Track: recursive interfaces. OS assignment seed **55**, drawn with
  `secrets.randbelow(100)` at 2026-10-13 13:51:49 UTC (2026-10-14 Melbourne).
- Exact base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`.
- Object: batches of PR840's centered native BIT shears on the **same** target
  and unchanged source, with exponents `+/-2^j` for a finite index set J.
- Hypothesis: keeping the target in its intermediate ADDRESS layout across
  adjacent powers eliminates repeated query boundaries. The candidate bill is
  `2|J| + runs(J)` ordinary children instead of `3|J|`, with no private row.
  Investigate exact optimality only in the target-query / source-XOR alphabet.
- Method/domain: written integer-walk argument, literal paid affine/child
  lowering, independent Laurent and modular VALUE replay. Complete all 63
  nonempty subsets of indices 0 through 5; seed 55 selects the gapped set
  `{0,1,2,4,5}`. No random search or new kappa claim.
- Deliverable: one standalone research construction with proof, complete
  typed cost recurrence, exact certificates, source pins and adverse controls.
- Budget: approximately 60 minutes, orientation at most 12 minutes;
  final 15 minutes reserved for verification and handoff. Expected finish
  2026-10-14 01:52 AEDT (2026-10-13 14:52 UTC).

Three candidates were considered: (1) extend the dyadic DATA-target query
pair across a finite exponent set, (2) move clean checkpoints among recursive
subtrees, (3) share a dirty connector among product-shear outputs. Candidate 1
was selected. PR714/788 already cover checkpoint placement; PR889/934/943 and
the newly visible PR944 cover the multi-source connector neighborhood. The
selected task extends PR840's single centered pair to a shared target batch;
it does not repeat its arbitrary-dirty-row three-query lower bound.

Initial overlap inventory: 714 open PRs through #943. Immediate claim refresh
included #944 (signed connectors) and #945 (complex Horner). No pinned issues
exist; the two open issues #650/#913 are not sprint coordination issues, so
this claim is local. The review ledger marks PR521 unreviewed and has no
exact-head acceptance for PR677/840. They are pinned pending predecessors,
not accepted frontier dependencies. Prior fixed-menu and supplier-profile
negative results are not reopened: the query interface changes and the
selected supplier is not modified.

At this base the selected conditional kappa is
`1661957774647029/1000000000000000000` (PR890). Its certificate, actual T21
construction and maintainer review were followed. The first checkout read
saw the older PR799 snapshot while the fetch was running; that snapshot is
not used as the accepted result here.

## Result update

Completed contribution: [PR953](https://github.com/CrocSwap/integer-mult-bounds/pull/953),
**recursive-interface research construction; no new kappa**. The written
argument proves the `2|J|+runs(J)` query optimum in the declared uniform
target-only dyadic alphabet, including arbitrary off-support excursions.
The seed-55 batch uses 12 children and 72 affine events instead of 15 and 90,
with ten XOR scans and no extra full private row in both programs. Actual
coefficient-dependent work and all inherited implementation obligations remain
explicit in [the proof and recurrence](PROOF.md).

All 63 literal cases, the separate 15-selection bounded walk census, 252 dirty
forward/inverse case pairs, 15 rejection controls and eight package faults
pass. The complete evidence agrees on Python 3.14.6 and 3.9.6; source Git
objects, relocation and regeneration pass. See [validation](VALIDATION.md)
for the exact domains and the incomplete root-suite boundary (missing SymPy).

The full overlap refresh reached #947 and the immediate pre-submission check
reached #950, again with no pinned coordination issue. PR840's consumed head
remains unchanged. Main advanced to `007664306fff84fbb1c9a1b4053b69f439764034`
without changing the selected record. The mathematical implementation and
certificate were committed at `282eff4d60bacfe1d0018bc08b22a2e1bf8d5928`;
this result update adds publication metadata only. Verification and packaging
occupied the final part of the session, after implementation was frozen.
