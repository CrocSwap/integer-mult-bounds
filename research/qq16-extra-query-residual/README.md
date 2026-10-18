# QQ16 residual A-input dimension after one extra query

**Scoped obstruction; no new supplier or kappa.** Even granting the complete
read-only pre-F0 value `B2 X_U` free of charge, the fixed QQ16 F0/B1 controller
cannot restore every original selected input from its retained observations.
There are at least `ceil(32 |G| / 7)` independent missing A-input directions
on the finite regular cover G: at least four sevenths of its `8|G|`-dimensional
A-input space. This is information dimension, not a paid recursive rank or a
physical cost estimate.

The contribution is a **quantitative dimension bound and independent trace
method**. The final overlap refresh found Adam Gall's concurrent
[PR2093](https://github.com/CrocSwap/integer-mult-bounds/pull/2093), exact head
`8b21a900eb520e4f11ea177b310f66316f8e8983`, which already proves the qualitative
obstruction using an explicit three-port witness invisible to *all* nonzero
charts. We credit that result rather than claim priority for insufficiency.
Our bound measures the size of the missing A space for the B2-only repair;
it does not establish that bound for observing all eight nonzero-chart queries.

Both results address the arbitrary-input question left open by Cinna Davis's
[PR2079](https://github.com/CrocSwap/integer-mult-bounds/pull/2079). That
contribution correctly separates the eight previously exhibited directions.
The residual family lies in both `ker B1` and `ker B2`, with nonzero `B0 h`.

## Argument and exact scope

The [written proof](PROOF.md) uses the actual U96 query columns and the stage
0, 1 and 2 cover routes. For each of the three stage pairs, all 96 relative
routes are distinct. With `S=[B0;B1;B2]` and `K=S* S`, the exact regular traces
are

```text
tr K   = 1152 |G|,
tr K^2 = 64512 |G|,
rank S >= (tr K)^2 / tr K^2 = (144/7) |G|.
```

Since `[B1;B2]` has at most `16|G|` output coordinates,
`dim B0(ker B1 intersect ker B2) >= ceil(32|G|/7)`.
Choose a rational, then denominator-cleared integer, h in this joint kernel
with `B0 h != 0`. Initialize only pair 0 as

```text
X_U=h, Y_U=0,
X_A=-P_(0,A) B0 h, Y_A=-X_A,
X_T=Y_T=0.
```

The unchanged F0/B1 pair leaves only `Y_(0,U)=h`. The inherited ordinary tail
has zero selected outputs, zero completed-X descendants and all five F-query
histories zero. The added observation `B2 X_U` is also zero, although the
original A input is nonzero. Thus no decoder determined only by these records
can restore all original selected inputs.

The result retains the local pair, ordinary tail, regular cover action and
native endpoint interpretation. It permits homogeneous selected-only controls
after B1. It grants the complete extra observation with no source mutation and
free indefinite retention. Logical payload-constant inputs retain arbitrary
cover values and apply at every positive tensor size under the inherited
invertible endpoint frames. Fixed finite-precision implementation is not proved.

The full initial `R2 X` is a different observation; it need not vanish here.
Changing a first-pair map, adding another ordinary read, or changing the tail
requires a new argument. An initial `B0 X_U` observation detects the constructed
missing A values, but is not proved to repair the whole controller.

## Evidence and reproduction

Run from a Git checkout with the pinned source history and Python 3.12:

```sh
python3.12 -I -B scripts/research_package.py --package research/qq16-extra-query-residual
```

Expected: `PASS_QQ16_EXTRA_QUERY_RESIDUAL`, six passing behavioral groups, and
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=negative-result`. No network or
third-party Python packages are needed. Direct verification is
`python3.12 -I -O -B research/qq16-extra-query-residual/verify.py`.

- The primary checker reads the frozen R certificate and reconstructs binary
  routes by transvections. It computes collision-aware matrix coefficients,
  the exact trace bound and the inherited tail's formal h trajectory.
- The code-disjoint oracle reconstructs R by backward covectors through all
  712 independent source/helper positions, then projects the source columns.
  It constructs routes by orthonormal axis swaps. The full R and U96 route
  hashes, all three coefficient matrices and both trace moments agree.
- Fixed [RESULT.json](RESULT.json) and [ORACLE.json](ORACLE.json) are consumed,
  not regenerated during acceptance. A complete C3xC3 regular example supplies
  an explicit residual witness and exact matrix ranks 25 and 17. This small
  example illustrates the argument; it does not replace the actual source check.
- Controls detect changed coefficients, route collisions, reversed noncommuting
  route products, an omitted cancelling bridge, source drift, typed and
  trace-preserving receipt corruption, missing receipts and overwritten
  generation outputs. Actual removal of the oracle's distinctness and Gram
  guards makes its control suite fail. Port permutation and whole-column signs
  are accepted; normal and optimized relocated checks preserve the receipts.
- [REVIEW.json](REVIEW.json) records an independent agent's mathematical review
  and hashes of the proof, both checkers, source manifest and primary receipt.

This is a written all-parameter rank/existence argument with finite exact
source checks. It does not enumerate the cover, construct an explicit basis
for the dimension bound, reprove the inherited native tail, replay the complete supplier,
or establish precision, physical costs, supplier admission or a formal-kernel
multiplication theorem. The zero-cost favorable relaxation already fails the
restoration obligation, so no moment screen or native implementation is claimed.

## Provenance and overlap

Scientific base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
Selected-record SHA256 is
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
Exact Git and SHA256 pins are in [SOURCES.json](SOURCES.json). Original immutable
archive bytes are used directly; no source archive is copied or modified.
[TASK.json](TASK.json) records selection, scope refinement and overlap.

The selector's recursive-interface allocation was refined to revision 4's
central `joint-query-controller` handoff. Work continues in
[Discussion2074](https://github.com/CrocSwap/integer-mult-bounds/discussions/2074#discussioncomment-18932289).
Adam Gall's adjacent [PR2086](https://github.com/CrocSwap/integer-mult-bounds/pull/2086)
changes the first A logger without retaining an extra observation; it does not
require the simultaneous `B1 h=B2 h=0` used here. Neither result is a universal
barrier to changed QQ16 interfaces.

## Open next questions

1. Does one properly priced **full** initial `R2 X` read or an additional
   `B0 X_U` read remove all missing selected information? It would change the
   observation contract tested here. First compute the joint kernel of the
   entire retained record, checking both A and T restoration, before native
   synthesis. The full-controller kernel and legal final frame access remain
   unresolved; detecting this family alone is insufficient.
2. Can a changed T record, ordinary response or backward first call avoid
   losing these initial values without another transcript? First apply the
   erased-state test and a favorable complete cost bound to one precise map.
   Global ordinary scheduling, endpoint access, hosting and precision remain
   blockers. Repeating the same fixed-pair B2-only observation is unnecessary.

## Credit

Prepared for Ross Richardson with substantial OpenAI Codex assistance, including
the `math-recursive-interfaces` proof specialist and code-disjoint
`math-exact-circuit-verification` oracle/reviewer. No independent human review
is claimed. New material is Apache-2.0.

Ali Romman's [PR1969](https://github.com/CrocSwap/integer-mult-bounds/pull/1969)
and its credited centre-encoding contributors supply the QQ16 maps, native
contracts, original observation witness and retained tail. Cinna Davis's PR2079
poses the extra observation and establishes its eight-direction separation.
Adam Gall's PR2086 supplies adjacent first-forward logger analysis, and his
concurrent PR2093 supplies the explicit all-nonzero-chart witness for the
same qualitative obstruction. PR2093's pinned proof was inspected; its
executable was not imported or rerun by this package. The
[upstream notices](../joint-query/NOTICE.md) retain all geometry, gauge44/t16,
compiler and selected-supplier attribution and source licenses.
