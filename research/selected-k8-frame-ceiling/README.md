# Complete frame-reassignment bound for the selected k8 word

**Scoped obstruction, no new kappa.** Even changing all 5,413 A/B/tail
gate frames simultaneously cannot raise the selected word's favorable
packing ceiling beyond

    a < 0.001690054109089,
    kappa < 1690054109089/1001690054109089 ≈ 0.001687202646.

This excludes the revision-3 target of a 5% improvement in that ceiling.
It fixes the scalar operations and chronology, helper endpoints, cut
and tail membership, while allowing every legal monotone F2^9 gate frame
and every idle packing under the existing coverage law and rank guard.
The given frame assignment attains the exact LP lower bound at the two
test exponents. The favorable relaxation optimum is bracketed to 10^-15;
fractional ideal idle packing is not a physical construction.

## What this adds

PR1240's `complex-local-word-ceiling` fixes a paid local profile. Here
that profile is allowed to vary over **all** frame assignments of the
actual selected k8 scalar word. A complete exact certificate shows that
this freedom still cannot lift the established ceiling. The bound also
allows different legal assignments in different invocations.

Navinor's retained `complex-x4-frame-bound` gives the method and an
earlier X4 result. Its original model is retained unchanged and credited;
this package supplies the new word binding and all new dual certificates.
PR557, PR776 and PR815 cover preceding frame models/words. Arham Tahir's
[PR1605](https://github.com/CrocSwap/integer-mult-bounds/pull/1605) prices
abstract rank-one reblocking; this tests the full actual gate chronology.

The exact word hash is
`c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8`:
480 helpers, 3,451 A gates, 1,846 B gates and 116 early-cleanup gates.
SLOT-PINS-k8 and the retained word-lineage reconciliation bind it to the
selected construction. The similarly named R492 evidence file is an
older predecessor and is excluded.

## Evidence

The [proof](PROOF.md) explains complete interval enumeration, LP weak
duality, fixed rank mass and the full idle-packing screen.

- **1,741 free gates**, with 2, 5 or 16 frame choices; the other 3,672
  gates are forced. All subspaces in each interval are included.
- **135 components**, **17,507 LP rows**, **23,004 columns**. The given
  assignment matches every dual objective as an exact coefficient identity.
- **16,564** reduced-cost vectors vanish identically; **6,440** are
  rigorously positive at the baseline ceiling upper endpoint and the
  5% target. No solver status or floating-point tolerance is accepted as
  evidence of those signs.
- The primary checker uses retained exact-log/exp arithmetic. A separate
  implementation reconstructs the event graph, all frame intervals and
  101 cone ceilings using bitsets and inverse row covectors, then checks
  all dual inequalities using integer-root intervals. It imports neither
  the predecessor mathematics nor the primary checker. All graph/domain
  hashes, coverage and ceiling signs agree.
- The unchanged native auditor checks the baseline and a nontrivial
  all-upper-frame assignment on **704 columns in both orientations**,
  including arbitrary helper dirt, paid profiles and low-end cones.
- **14 control groups** cover those native examples, omitted frame/edge/
  centre work, an invalid arithmetic oracle, optimized read-only relocation
  of both checkers, and eight external certificate/source/JSON corruptions.

A simpler per-register dimension relaxation already rejects the 5% target
with normalized bill greater than 1.000125724118. The coupled exact duals
give the stronger ceiling result. The complete local profile includes all
climbs and eight centre descents, mass 5,586; the coverage law leaves
1,646 idle rank units per call. No extra work is credited as a saving.

Separate code and finite certificates do not constitute independent human
review or proof-assistant verification.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py \
  --package research/selected-k8-frame-ceiling
```

This runs `verify.py`, `independent.py` and `test_package.py`. All package
guards remain active under `-O`; the primary loads unchanged legacy code
with its assertion guards explicitly enabled. Normal replay is read-only.
`verify.py --write-expected` explicitly regenerates only the receipt.
Retained source hashes and Git blobs are checked before use. The dual
certificate's canonical parsed payload, rather than its gzip container,
is the mathematical identity used across environments.

`nominate.py` is optional discovery code, adapted from the credited X4
generator. It used highspy 1.15.1, NumPy 2.5.4 and SciPy 1.18.1 in an
isolated environment. `DISCOVERY.json` records nomination diagnostics;
its floating-point numbers are not used by either acceptance checker.
Final verification requires no solver dependency.

Validation completed with the full registered Python 3.12 replay, including
all 14 control groups. Both mathematical checkers also passed under
Python 3.14.4 with `-I -O -B` in a relocated read-only package, with every
file unchanged. The canonical primary receipt is
`a65d7a10aed29d7d112bb12aff0a1b0466b632cd38be068f7860bf15e5f3d265`.

## Scope and coordination

Single random nonce `600a2fb184f55021a1cd62892ce3a7aa`, revision-3
`complex-mechanisms / complex-rank-shape-decoder`, no reroll. Base main
`a73173f77596b0a1a115b9fed82b65183e20f7ad`. The prescribed ceiling replay,
lever table and selected-source binding control passed before the bounded
investigation. [Discussion1659](https://github.com/CrocSwap/integer-mult-bounds/discussions/1659)
records the claim and finding; TASK.json records scope and overlap.

Published as [PR1671](https://github.com/CrocSwap/integer-mult-bounds/pull/1671).
The mathematical commit is
`11fbeaf34609147c124323c2f5e74fc450dad931`; the follow-up publication
metadata changes no runtime code, source, proof or certificate.

The final overlap refresh covered 499 open PRs and 318 discussion records
with complete pagination and no warnings, at 05:59–06:00 UTC on 2026-10-14.
Relevant PR815 and PR1605 heads were rechecked. Main advanced to
`5cff33057a2b35adb90dddd5084d748ec66201eb`; the selected record, task
catalogue, instructions, replay hook and all nine retained inputs were
unchanged, and this package path was absent. Aaron Wang / navinor's
[complementary climb-pair census](https://github.com/CrocSwap/integer-mult-bounds/discussions/1659#discussioncomment-18916048)
was read before publication and is credited as nearby work, not a proof
input. Its question about intervening operations is covered here when
their scalar chronology and the stated frame contract are fixed.

This is the card's fixed-word block-climb obstruction, not a successful
construction passing its 5% gate. No global optimality over scalar words,
changed endpoints, reordered gates, new helpers, shared centre work or
changed coverage laws is asserted. The result does not prove frame
optimality at every exponent. The current selected saving lies below
the ceiling, and remaining packing headroom is not claimed eliminated.
No full selected cold replay, new native/global admission, all-size
compiler, precision/tape or analytic-transfer theorem is supplied.

## Open next questions

1. **Change one scalar dependency or gate order.** This can alter the
   complete frame intervals and escape the fixed-word bound. Start with
   one declared legal rewrite that changes an active dual constraint,
   recompute the exact ceiling, and retain it only if the full profile
   has enough headroom. Dirty-state correctness and low-end cones are
   the first admission obligations.
2. **Change helper start/end frames.** Endpoints fix the telescoping rank
   mass here. Pin one helper with a proposed wider residual contract and
   derive its full conversion, restoration and hosting invoice before
   synthesis. The present fixed-width coverage decomposition may cease
   to apply; it cannot be reused without checking its hypotheses.
3. **Extract useful structure from the active dual constraints.** The
   certificate proves a numerical bound but does not classify all
   optimal assignments. Start by analyzing the zero reduced-cost support
   in the 665-node component. LP support alone does not guarantee a
   realizable common-frame assignment or a valid changed scalar word.

## Credit

Prepared by Gareth Davidson (@bitplane), with substantial OpenAI Codex
assistance. Credit navinor's frame method and source code, the
chafreaky/ntedvs/Rohan Guliani lineage, Douglas Colkitt's ceiling,
Sagar Thakrar's coverage law, Arham Tahir's reblocking screen, and the
Jeremy Kothe/Rohan Arun/Hao Yan/icekylinx selected construction and
woklerx word reconciliation. See NOTICE.md and retained source credits.
Apache-2.0; no independent human review is asserted.
