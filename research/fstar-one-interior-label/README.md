# F-star: one exceptional label is necessary and sufficient at v = 11

For **each of the twelve eleven-line restrictions of `tied_min`**, the exact
Form-R maximum is **10**. A certificate keeping all eleven lines needs at least
one pair outside Form-R. Exactly one additional pair of the form
`(a,b) = (111,e_c)` suffices, with `c` in that line's column support. All other
pairs in the new witnesses are ordinary repairs or matched pivots.

This answers the constructive part of [Aaron Wang's PR2963 open question 2][2963]
and settles [PR2914's open Form-R question][2914] on the full twelve-line fixture.
Its Form-R maximum is also exactly 10: any eleven-line certificate would occur
in one of the twelve excluded restrictions, while a ten-line witness exists.
No recorded CP-SAT optimum or predecessor executable is needed for either result.
The [retained review][review] explicitly leaves the Form-R question open and
records objective bugs in the older completion routines. This package imports
none of those routines and does not endorse their other claims.

This is an author-checked finite result. It is not a proof or refutation of
F-star, a physical decoder construction, supplier admission or a new kappa.
The selected frontier and all predecessor packages are unchanged.

## Definitions and exact scope

The source is DreamingOfClouds' `tied_min` fixture from PR2111, retained in
Aaron Wang's PR2869 package on main. Its SHA256 is
`670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93`.
It is byte-identical to the fixture vendored by PR2963 at
`ee755e682b3b30d493e764d3be50003b13b69b4a`. The receipt reconstructs every
zero entry from the integer factors `M = P Q^T`, not a stored zero graph.

An L8 certificate consists of supported three-bit labels `a(t),b(t)` and an
order of kept lines. It requires `a(t) dot b(t) = 1` over F2 and
`a(t) dot b(s) = 0` whenever `t` precedes `s` and `M[t,s] = 0`.
DreamingOfClouds' PR1590 proves the inherited bound `cost >= cert(M)`.
That bound is context, not newly proved here.

Every entry of P is odd; Q has exactly two odd nonzero entries per line.
The canonical anchors are therefore `a0(t)=111` and `b0(t)=supp Q(t)`.
All eleven-line restrictions retain these anchors, and `a0 dot b0 = 0`.
The self-certifying Form-R pairs of PR2914 are precisely:

- repairs `(a,b0(t))` with `a dot b0(t)=1`;
- matched pivots `(e_c,e_c)` with `c` in `supp Q(t)`.

There are six distinct pairs per line. The anchor itself cannot certify a
kept line and may be discarded. All labels allowed by L8 already lie in the
sub-anchor box on this fixture, because the anchors equal the full supports.
Consequently the minimum number of non-Form-R pairs is also the minimum number
of BOX-INTERIOR pairs under the predecessor's classification.

The sufficient extension adds only the two pairs `(111,e_c)` per line, with
an occurrence budget of one across the whole certificate. Here `a=a0`, not a
proper subset. The class name BOX-INTERIOR means "inside the box but outside
Form-R"; it does not require both anchor inclusions to be proper.

## Exact finite exclusion

The primary checker places the next line from left to right. Its state stores,
for each unplaced line s, the currently allowed b labels. A state value of zero
marks a line already placed. When placing t with pair `(a,b)`, every unplaced
zero-arc successor s loses b labels with `a dot b(s)=1`. An empty remaining
domain rejects the branch.

The state has all information needed for a completion. Earlier constraints
restrict only future b labels. Future constraints never inspect an earlier b.
For a fixed current a, choose the least-cost available b; that choice cannot
change any later domain. When paths reach the same state, retaining only their
least cost is therefore exact. Induction on the number of unplaced lines proves
that the finite recurrence preserves every possible certificate and introduces
none. The empty state at depth eleven is reachable if and only if an allowed
full certificate exists.

For budget zero the complete reachable-layer counts, identical on all twelve
restrictions, are:

```text
1, 44, 338, 652, 652, 434, 210, 87, 30, 7, 0, 0
```

Thus all 2,455 reachable states exhaust without an eleven-line Form-R witness.
The separate reverse-order implementation chooses the *last* line and stores
allowed a labels instead. It uses explicit sets of labels rather than the
primary bitmask domains, and imports no primary or predecessor code. Its
complete layer counts are:

```text
1, 22, 76, 146, 231, 244, 128, 34, 6, 0, 0, 0
```

These 888 states independently exclude the same twelve full certificates.
Both recurrences reject a capacity overrun rather than interpreting it as an
exclusion. No heuristic search, floating-point arithmetic or solver status is
used for acceptance.

## Constructive witnesses and minimality

[RESULT.json](RESULT.json) contains all twelve one-exception eleven-line
witnesses, all twelve ten-line Form-R witnesses, and complete primary frontier
counts and digests. Default replay recomputes the complete receipt. Both
implementations check the supported labels, diagonal parities and every
chronological zero-arc condition of each witness.

For example, omit original line 0 and index the remaining lines locally as
0 through 10, corresponding to original lines 1 through 11. One full witness
lists `(line,a,b)` in certificate order, with labels encoded as integers:

```text
(0,1,1), (1,1,1), (2,5,6), (3,5,3), (6,1,5), (4,4,4),
(8,7,2), (5,2,6), (7,2,2), (9,4,4), (10,2,2)
```

Only `(8,7,2)` is outside Form-R. Since zero exceptions are impossible and
one succeeds, the minimum is exactly one. This is minimality in the *number
of exceptional kept-line pairs*, not a universal minimality claim about proof
families or physical decoder designs.

PR2963 reports `named=9` on these restrictions. Taking that separately pinned
claim as context, the gap splits as `named 9 < Form-R 10 < one-exception 11`.
The new result does not recheck the predecessor's named-family optimization.
In particular, unrestricted ordering alone does not close the second point.

## Reproduce and checks

Python 3.12 or later, standard library only, from the repository root:

```sh
python3.12 -I -O -Werror -B research/fstar-one-interior-label/verify.py
python3.12 -I -O -Werror -B research/fstar-one-interior-label/independent.py
python3.12 -I -O -Werror -B research/fstar-one-interior-label/test_verify.py
python3.12 -B scripts/research_package.py --package research/fstar-one-interior-label
```

The primary marker is
`PASS_FSTAR_ONE_INTERIOR records=12 form_r=10 minimum_interior=1 full_form_r=10`.
`verify.py --emit` prints the recomputed receipt without writing files.
`--write-result NEW_PATH` creates a new file exclusively. Direct replay needs
only this package and the declared fixture, not Git or network access.

Seven behavioral test groups include a literal pair-times-order oracle on
all 220 three-line restrictions and four four-line controls, both exception
budgets, reversed witnesses, broken support/diagonal/order, actual weakened
implementations, capacity exhaustion, source corruption before parsing,
duplicate JSON keys, typed receipt drift and optimized Git-free replay.
Ignoring zero-arc restrictions or misclassifying the new pairs as Form-R makes
the actual weakened checker falsely admit eleven, so the controls distinguish
these faults. Local environments and commands are recorded in TASK.json.
Hosted CI is separate; no independent human or formal-kernel review is claimed.

## Open next questions

Can a general proof family permit a small number of `(a0,e_c)` exceptions
while preserving an explicit L8 order? This matters because the named families
miss an entire point that one such exception supplies here. A feasible first
step is to inspect the twelve stored orders for one common sufficient rule
and test it against both PR2111 fixtures. The blocker is a proved general
ordering rule, not finding more seeds. This finite result gives no guarantee
for other decoders, anchor normalizations or an arbitrary number of lines.

Family decision: finish this finite label/ordering question and stop. No
physical construction or dependent search expansion follows from the result.
Native realization, copied information, restoration, physical hosting, full
recursive cost, precision and all-size lifting are unrun and remain separate
obligations before any supplier or kappa claim.

## Sources and credit

Scientific base is canonical main `916ecdd9d6e666fcad9b25369d055311f6ce8204`,
priority revision 5. [SOURCES.json](SOURCES.json) records exact live input and
historical assignment pins; [TASK.json](TASK.json) records the changed scope
from complex rank-shape mechanisms to this fresh proof-level handoff.
[Discussion2967][claim] is the canonical investigation thread.

Credit Aaron Wang for PR2963's explicit handoff, PR2914's Form-R/box ladder,
PR2936's family census, and PR2869's retained fixture/anchor normalization.
Retain his PR2717/2747/2774/2890/2901 certificate, repair, pivot and graph
lineage. Credit DreamingOfClouds for PR2111's fixture and PR1590's L8 definition
and cost bound. No earlier fixture, label family, named optimum or physical
construction is claimed as new. The new content is the two exact Form-R
exclusions, the sharp one-exception result and its twelve constructive orders.

Nick Petalas. Apache-2.0. Automated assistance was used for computation and
checking. No independent human review is claimed.

Build the Lever led to the rerunnable finite checker. Prove It Works led to
the reverse-order exclusion and literal witness replay. Test Behavior, Not
Implementation led to the real CLI controls and actual weakened implementations.
Boundary Discipline kept source/receipt validation outside the recurrence.

Power of Ten rule 3 deviation: Python allocates managed objects. Inputs are
capped at 4 KB, receipts at 2 MB, factors at twelve three-total lines, and each
search at 100,000 cumulative states with at most twelve transitions in depth.
Both frontiers are also capacity-checked while constructed. A deployed checker
for larger or untrusted domains would need a fixed-capacity representation.
Test-only source loading and unittest dispatch are rule 8/9 deviations with
three fixed local modules, bounded child processes, 60-second timeouts and
scoped temporary cleanup. No scientific replay dynamically loads predecessor
code. All changed functions are below 60 lines, contain no recursion and retain
explicit checks under `-O`. Diagnostics run with warnings as errors and Ruff
`E,F,I,UP,B`; shared repository configuration is unchanged.

[2963]: https://github.com/CrocSwap/integer-mult-bounds/blob/ee755e682b3b30d493e764d3be50003b13b69b4a/research/fstar-gap2-v11-seed42ff0611/README.md
[2914]: https://github.com/CrocSwap/integer-mult-bounds/blob/3f7781efccdf10fa61a1e0a6f11c191579b21280/research/fstar-family-gap-seed1c25f56f/README.md
[claim]: https://github.com/CrocSwap/integer-mult-bounds/discussions/2967
[review]: https://github.com/CrocSwap/integer-mult-bounds/blob/a23bdc1b07be96bea0101d44ae27d14de67a79ed/research/community-efficient1900-audit/README.md#remaining-review
