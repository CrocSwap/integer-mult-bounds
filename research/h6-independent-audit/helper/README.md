# Helper admission audit for H6

This is an independent audit of the H6 package attributed to
DreamingOfClouds, pinned by the parent audit to
`b496aed769dd724cd1ff6b921cade626562be27b`, and of Dominik Scholz's
merged PR606 `research/niemeier-lattices` accounting and frame interfaces.
No new kappa, admissible supplier, or universal Walsh obstruction is claimed.
Prepared with OpenAI Codex assistance; Apache-2.0, preserving predecessor
attribution. Frozen predecessor files are read only.

## Result

The missing step is an **emitted dirty-restored, common-frame compensation
word with a priced schedule**. A scalar Walsh identity alone supplies neither
that word nor a conversion from Walsh terms, gates, rank or vector-space
dimension to the number of banked ordinary restored helpers.

The existing H6 budget is an optimistic necessary screen. It omits the K
encoder beyond its base terms, compensation chronology and extra private
descents. Two PR606 encoder proposals can be fully charged in the same rank
invoice, shrinking the remaining ordinary compensation helper allowance.
Their frame and scalar legality remains conditional, so passing the invoice
does not establish an algorithm.

At `L=5`, the exact strict ordinary helper capacity for path `[1,7,8,1]` is:

| Proposed baseline | Encoder helper roles already charged | Selected frontier1094 | Discussion PR1424 title |
| --- | ---: | ---: | ---: |
| H6 paper: both data paths `[16]`, center bill 12,752 | 0 | 88,765 | 88,409 |
| PR606 conservative encoder: both data paths `[1,15]`, center bill 12,752 | 44,976 | 41,810 | 41,454 |
| PR606 full-center fallback: source `[16]`, target `[1,7,8]`, center bill 13,872 | 816 | 66,313 | 65,990 |

These are **additional** compensation helpers. They use selected kappa
`836330098538459/500000000000000000` and comparison decimal
`0.001676855229071321886206381217337893` respectively. The latter is a
discussion/title comparison, not a statement that PR1424 is selected or
reviewed. The final two proposals and path choices are inherited from
PR606, not fresh constructions. All listed helper paths, pads, replication
stock, center descents and strict child caps are charged. Any extra private
descent, altered data chronology or other unlisted stage is additional work.

## The exact lemma still needed

For the actual 30,960 ports and their 17-bit addresses `p_s`, an emitted local
word must show all of the following together:

1. Sources begin at `span(p_s)`, dimension 1, and end at FULL. Targets begin
   at zero and end at `p_t^perp`, dimension 16. Ordinary helper registers
   begin at zero and end at FULL; nonzero entrances require their own
   inherited wrapper, spectator and one-owner justification.
2. Each scalar addition and copy has operands at the **same current frame**.
   Non-private frame changes are ascending nested climbs. Thus a source
   cannot be loaded into a frame-zero Walsh accumulator merely because
   scalar coefficients are known, and a FULL accumulator cannot add
   directly to a target capped at `p_t^perp`.
3. The *whole* scalar word implements the required source-to-target shear
   and restores every independent arbitrary helper dirt column. In the
   complete K plus compensation word the source-to-target block is I,
   the helper-to-target block is zero, and the non-target scalar block
   is restored. The same exact accounting and chronology must work for
   the inverse-transpose orientation. The rank-30,960 matrix `I-K` is
   not the dirt-response rank of a chosen circuit.
4. Dirt precompensation occurs before target climbs, or has an explicitly
   admitted nonzero-frame target chain. Cleanup and any sequential lane
   reuse must be actual emitted operations at legal frames. A linear
   dependency between scalar channels does not by itself permit virtual
   entrances, cheaper paths or reuse after a helper reaches FULL.
5. Every private copy is charged at its actual transition ranks and obeys
   its admitted lifetime/erasure interface; all other helper paths,
   spectator/pad banks, repeats, wrappers, and data splitting enter the
   controller invoice. In particular, a hypothetical copy-and-clear from
   FULL to a target cap is not asserted admitted here.

The relevant inherited statement is PR606
`workbench/paid-controller/PAID-CONTROLLER.txt`, together with the common-label
and complete-invocation rules of
`research/e8-complex-gauge-kernel/PROOF.md`, sections 2.1--2.4. A small
explicit program proving these clauses is a useful next contribution even
if its first fully charged invoice fails.

## A decisive scoped frame experiment

`frame_support.py` uses the actual port/address construction. For every one
of the 16 real coordinate columns c, the support `P[i,c] != 0` spans all
17 address dimensions; each result has a 17-port exact binary witness.
Repeating one witness drops the rank to 16, a negative control.

For an isolated character decoder column
`D_c(i) (-1)^(l_i M a)`, the character sign is never zero, so the support is
exactly `P[i,c] != 0`. The intersection of all supported target caps has
dimension `17 - 17 = 0`. The corresponding encoder support spans FULL.
Consequently, a **private character-column factorization** has a FULL
gathering frame and zero common scatter frame, so that architecture needs
a rank-17 private descent per such aggregate. This is an exact scoped frame
obstruction; it is not an arithmetic-circuit lower bound.

A final FWHT output cell has different support: it decodes only to its
address-label bucket. The positive control verifies that one such bucket
has address span 1 and common target cap dimension 16. This distinction
prevents extending the character-column result to all FWHT circuits.
Cross-channel cancellation, bucket routing, intermediate low frames and
shared arithmetic DAGs remain open.

## A conditional no-stock private-copy screen

There is a separate, elementary exclusion for a precisely stated model.
Suppose all fresh source-to-target flow factors through clean transient
scalar private-copy channels; each channel contributes a rank-one matrix
`a b^T`; every channel pays at least one rank of descent; and those descents
have **no additional bank stock and remove no previously charged work**.
Then an identity shear of rank N requires at least N channels and total
descent bill C at least N. Under PR606's stock convention,

`D = (L-1)N - LC <= -N < 0`.

The compensation-only variant is stronger in the same restricted model:
PR606 proves `rank(I-K)=N`, so its added no-stock descent bill alone is at
least N, before the existing K center bill. Positive pressure cannot repair
the negative deficit. This rules out that clean private-copy-only invoice.

**The no-stock premise is essential.** An ordinary restored-wire helper
adds stock `LR/q` and its path plus pad has mass `LmR/q`; hence its deficit
effect is zero. Counting such a helper as a new unpaid center would be
wrong. A stock-bearing alternative needs an explicit arbitrary-dirt
interface and complete path/pad invoice; the private-copy exclusion does
not rule it out. H6's allowance of roughly 80,000--90,000 ordinary helpers
already exceeds N, so matrix rank alone does not reject that allowance.

## Reproduction and evidence

From the repository root, use:

```sh
python3 -B research/h6-independent-audit/helper/charged_screen.py
python3 -B research/h6-independent-audit/helper/frame_support.py
```

The second script requires NumPy. The first needs only Python's standard
library and PR606's pinned cost engine. Both write only their adjacent JSON
receipts. Checks remain active under `-O`.

`CHARGED-SCREEN.json` records outward-rational pressure intervals, the exact
integer capacities, all path groups and input hashes.
`FRAME-SUPPORT.json` records all coordinate support witnesses and the
restricted-label control. These scripts verify scoped arithmetic and
geometric statements; they do not emit a supplier or replay the selected
frontier's full theorem interface.

## Open next questions

- Emit one compensation subword for a small orthogonal incidence set with
  independent source and helper dirt columns. Begin with direct legal
  source-frame to target-cap additions, then compare a tiny Walsh route.
  The required deliverable is exact scalar restoration plus monotone
  common-frame chronology and a recounted paid profile.
- Test whether multiple coordinate channels can share decoder routing
  before FULL, or whether address-bucket outputs can use an admitted
  stock-bearing restored interface. The blocker is dirt cancellation and
  target chronology, not the numerical matrix identity.
- Once a word exists, rerun its **actual** source, target and helper paths
  through the bank invoice, including every extra private descent. The
  budgets in this directory are conditional construction targets.
