# P112 two-total correction at source union 44–47

**Research note / scoped negative result. No new κ or supplier.**

An arbitrary 44-port deletion can remove **five** rank units from the eight
P112 coordinate readers. An exact **two-column correction cannot realize
that pattern**: it would have to cancel a rank-three coordinate minor.
The retained loss is at most **four** through 47 source ports. Charging
both added totals gives COPY rank sum **at least 66** in the full-rank
on-column case. PR1197’s complementary reductions then extend the general
fixed-reader two-total no-saving range from 43 to **47**.

This resolves the next support interval left open by Josie Elliston’s
PR1787 and Philipp/mightyOil’s PR1827. The new step uses the rank-two
cancellation constraint as well as the deletion geometry. The full complex
parameter claim is the [written proof](PROOF.md), supported by exhaustive
finite premise checks; it is not an exhaustive enumeration of complex
matrices or a proof-assistant theorem.

## Evidence and scope

[RESULT.json](RESULT.json) records all eight local code inventories, all
reader-subset joins through five readers, the 42 four-reader cuts, 56
cross-reader obligations, 56 explicit nonzero integer cancellation minors,
all 672 minimal cancellation classes, sharp geometric witnesses at each
new size, and the complete integer
added-price screen. A second unpacked binary elimination checks critical
loss vectors and fixture costs. Source pins are in [SOURCES.json](SOURCES.json).

Two exact all-pairs fixtures distinguish the claims:

- Two independent, overlapping correction columns attain retained loss
  four at 44 ports, with total COPY bill **75**. Their sources leave
  `col(X)` (`rank[X Z]=10`). This does **not** attain the 66 lower bill.
- Three correction columns attain retained loss five on the same set,
  with total bill 81. This refutes an extension that drops the two-column
  restriction. It supplies no cheaper decoder.

The stronger 66 floor is restricted to two nonzero independent added
readers and sources on-column. The general 64 floor inherits PR1197’s
rank-one/off-column reductions. All sources may be complex; ordinary
transpose is used. Only separate-total pairing-rank sum is bounded, not
power sums or every supplier cost. All other helper, access, frame,
restoration, hosting and recursive work is optimistically free in this
screen. Union sizes **48 or larger**, changed readers, masked exactness,
physical implementation and all-size admission are unexamined. The selected
construction and `upstream/` are unchanged.

## Reproduce

From the repository root, CPython 3.12 and the standard library:

```sh
python3.12 scripts/research_package.py --package research/p112-joint-loss-boundary-seed49
```

This checks metadata/source pins, runs the exact checker normally and under
`-O`, and ends with
`PASS_REGISTERED_RESEARCH_PACKAGE research/p112-joint-loss-boundary-seed49 outcome=completed`.
Each mathematical run prints
`PASS_P112_JOINT_LOSS_BOUNDARY domain=44..47 geometric_max=5 rank_two_loss_bound=4 full_rank_copy_floor=66 no_new_kappa`.
No network, solver, external numerical library or predecessor checker is needed.
The direct read-only command is
`python3.12 -I -B research/p112-joint-loss-boundary-seed49/verify.py`.
A fresh receipt may be written with `--write /new/path.json`; overwriting is
refused. Source drift and corrupted-receipt controls must fail closed.

Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; priority revision 4;
OS-random assignment seed **49**, structural decoder research. The catalogue
card was narrowed to an algebraic side result; its 5% physical-construction
gate is not claimed. Candidate selection, overlap coverage, stopping rule,
exact predecessor heads and claim are in [TASK.json](TASK.json) and
[discussion 2369](https://github.com/CrocSwap/integer-mult-bounds/discussions/2369).

## Open next questions

- At **48 ports**, fourth losses, two simultaneous second losses and new
  multi-reader unions may enter. First enumerate these new minimal
  profiles, then test their **two-column cancellation minors** before
  treating a deletion witness as a feasible correction. The present
  completeness argument stops at 47; a larger computation without the
  realizability step would not settle the decoder question.
- Can a fully charged fixed-reader two-total construction beat COPY 64 at
  a larger union? Start with one realizable profile beyond 47 and charge
  both added totals, source preparation, frames and restoration. Neither
  this package’s geometric witnesses nor its bill-75 fixture supplies a
  favorable completed budget.

Structured relevance, first steps and blockers are in TASK.json.

## Credit

Josie Elliston PR1787 supplies the generalized-weight/support-screen
predecessor; Philipp/mightyOil PR1827 sharpens joint losses through 43 and
PR1197 supplies complementary two-total reductions. Credit also to Mihir
Srivastava PR845, woklerx PR998, commdata2338 PR1375, Hanson Sun/bbMisk
PR1432, adamgall’s Gram census, and the DreamingOfClouds / Joel
Pulikkan/GamingPuzzled E8/COPY lineage. Pending PR2338’s minimal-realisation
column-space floors do not cover arbitrary source columns used here and
are not dependencies.

Prepared by **Sricharan Vagvala (@theon199)** with substantial **OpenAI Codex**
assistance for mathematics, implementation, checks and writing. Parent-only
execution; author-checked, no independent human review. New work Apache-2.0;
predecessor files and attribution are retained.
