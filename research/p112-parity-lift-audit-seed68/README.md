# Two-sided P112 parity lifts do not lower copy-rank cost

**Scoped negative result and adversarial audit; no new kappa.** For the
specified ten-term P112 family, all 512 binary character gates on each
side and all complex amplitudes have copy-rank sum at least **64**. Members
with columns outside the root code on both factors cost at least **76**.
The result covers the coordinate pair `(0,5)` and orthogonal directions
`e_0+e_5`, `e_0-e_5`; it does not cover arbitrary ten-term decoders.

The [proof](PROOF.md) reduces the two complex amplitudes to four support
classes each. The [certificate](CERTIFICATE.json) covers all 4,194,304
resulting gate-and-class records. Two rank implementations agree on every
one of the 325638 distinct support pairs used. The stronger quantification
comes from the written zero-set argument, not from sampling complex values.

This recovers our unpublished seed-32 experiment after its automation was
interrupted. Audit seed **68** selected the amplitude-reduction obligation.
The unfinished checker had an invalid negative-control precondition: its
alleged two-sided example was actually one-sided. The corrected control
also shows why both extra terms must be billed: removing their charges
would turn an actual cost 76 into a false cost 62. That was a test defect
in unpublished work, not a defect in the selected construction.

## Reproduce

Python **3.10 or later**, standard library only, from the repository root:

```sh
python3 -I -B research/p112-parity-lift-audit-seed68/verify.py
```

Expected:

```text
PASS_P112_PARITY_LIFT_AUDIT_S68 records=4194304 minimum=64 rank_cap=8 independent_pairs=325638
```

`--emit` prints the regenerated certificate. `--certificate PATH` checks
an alternative receipt. Normal verification is read-only and works from
any working directory when the script path is absolute. Explicit failures
remain active under Python `-O`; no third-party environment or predecessor
checker is imported. On macOS, choose a Python 3.10+ executable if the
system `python3` is older.

The exact base is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
[SOURCES.json](SOURCES.json) pins the geometry with SHA256 and Git blob ID,
and separately records source and review context. The only runtime input
outside this package is the unchanged PR845 geometry snapshot. The selected
record at the base points to PR1094 with conditional
`kappa=836330098538459/500000000000000000`. This package does not edit it.

## Evidence and limits

The finite run validates all 112 roots, eight deleted frame lines, frame
coordinates, 12544 scalar and binary pairings, and `X^T X=56 I`. Every
copy-rank query is checked both in the nine-bit label representation and
against the binary matrix derived directly from integer root products.
It records all 25 changed-term rank profiles and checks literal factor
identities on 27 representatives, including exact near-breakpoint fractions.

Eleven embedded controls cover the faulty old witness, unpaid extra
charges, rounding at amplitude breakpoints, omitted terms, wrong signs,
nonorthogonal directions, support cardinality, binary dependence,
dimension-only cache keys and label corruption. Package tests separately
check saved-receipt mutation, relocation and source-pin failures.

The finite rank census and written support reduction prove only the scoped
algebraic cost claim. Its physical interpretation inherits PR446's
separate-total gathering and copy-tree assumptions. Preparation, source
access, frame changes, other copies, restoration and recursive children
were assigned zero extra expense for the optimistic screen. The cost
component still cannot improve, so no physical supplier was implemented.
Improvements in rank distribution, helper work, scheduling or hosting at
unchanged copy-rank sum remain possible. No complete supplier recurrence,
new recursive moment, multiplication theorem or kappa is established.

The [claim](CLAIM.md) records the three candidates, seeds, scope selection
and overlap review. The stopping rule was complete finite coverage, with
no random search, time-truncated domain or speculative pivot. The two rank
algorithms share geometry and support masks; the second is independent
linear algebra, not a separate proof of the support formulas.

## Predecessors and attribution

- **Joel Pulikkan / GamingPuzzled, PR620**, and its construction lineage
  supply the baseline cost 64.
- **DreamingOfClouds, PR717**, supplies the P112 model and open mixed-rank
  question. **Mihir Srivastava, PR845**, supplies the unchanged geometry
  snapshot and fixed-reader single-lift theorem.
- **joaqcoo, PR1224**, proves the nine-term one-sided normal form and
  already gives a ten-term example with both factors outside the root code.
  This package adds the exact cost census for the stated parity-lift class.
- **mightyOil, PR1197**, studies two additional totals while retaining the
  eight coordinate readers. Our two changed factors are outside that
  fixed-reader scope. **Sagar Thakrar, PR1133**, supplies related rational
  descent for single lifts, not a premise of this proof.

Prepared for Sagar Thakrar (@thakrarsagar), with substantial OpenAI Codex
assistance in mathematics, implementation, verification and writing. The
checker recovers our interrupted seed-32 code and adds this audit's repairs
and controls. New material is Apache-2.0 under the repository license;
predecessor files and their notices remain unchanged. See SOURCES.json for
exact references and [VALIDATION.md](VALIDATION.md) for observed checks.

## Open next questions

The useful next change would alter the gate or lift class, not repeat this
finite census with another random seed. A quadratic Boolean gate or three
active update coordinates could change the support geometry. First derive
its exact compensation identity and a complete optimistic copy invoice;
the obstacle is preserving all-pairs equality while paying every added term.

Alternatively, a tied cost-64 member could have a useful rank distribution
or schedule. Compare its full recursive rank moment and required frame
transitions against a pinned physical supplier before claiming a benefit.
No such physical comparison or recurrence is supplied here.
