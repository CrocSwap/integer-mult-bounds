# Stage-8 Type A QUERY carriers

The paired QUERY demotion at caller clocks 1580 and 1659 requires two
additional input aggregates and one additional output direction at stage 8.
Four existing productive-helper moves implement the central phase directly.
Each fails the first-contact dirty-input test, and no combination of
injections at those four moves preserves the full helper returns through the
retained native suffix.

There is a constructive caller retiming. Moving 14 existing idle calls before
the host and deleting 28 cancelling ADDs removes all stage-2 through stage-7
body dependence from the required host correction. The check uses all 36
arbitrary input columns and all four phases with formal body variables. The
retiming keeps the paid profile fixed. The paired QUERY demotion still needs
a changed physical provider.

The [timed-readout follow-up](TEMPORAL.md) also checks the full seven-chart
bank, two terminal restoration obstructions, and a coframed entrance
compensation. The compensation restores all original returns and is
equivalent to an ordinary Y-input ADD.

## Exact setting

Use port 0 in Rohan Arun's [#7113 signed caller][caller] with the
[#7334 native word][native]. Clock 1423 is the stage-8 J. The literal physical
binding sends caller roles `8, 0, 18, 26` to native fields
`0, 112, 772, 882`, respectively. Every other public native field is
bound to another main role or an independent productive helper. The two
QUERYs both add the `q^-1` response of role 1 into role 0. The proposed
demotion replaces each with an ordinary unit ADD.

Let `J` be the old host. Let `S` and `S'` be the suffixes from just after
clock 1423 through clock 1659 inclusive, respectively with the old and
demoted QUERYs. The unique required host is `J* = (S')^-1 S J`. The replay
computes all columns of this map over Gaussian Laurent polynomials. At
`q = -1`, row 8, column 1 of `J* - J` is
`2 B2 B3 B4 B5 B6 B7 B8`, where each `Bk` is the stage-k body. Flipping
only `B2` changes the value from 2 to -2 at unit values for the other
bodies. Thus a replacement with the same four input bindings cannot
implement `J*`. Even if given role 1, a host whose only body action is
`B8` and whose adapters are independent of the other bodies still fails
this witness.

## Exact paid-idle retiming

The 14 Type A idles at clocks 1448, 1451, …, 1487 act on roles 1–7 and
19–25. Before its idle, each such row sees exactly two ADDs from an
unchanged donor. They have coefficients +2 and -2. There is no intervening
contact on that destination and no intervening write to its donor. Cancel
those ADDs, then move the idle before clock 1423 across the remaining
disjoint operations. Keep each post-idle ADD in place. These idles act on
roles disjoint from the old J. The other Type A ports and the Type B word
can keep their original schedule. There is no cross-port exchange.

Write `D` for the diagonal formed by the 14 moved idles. The new stage-8
requirement is `D J* D^-1`. The replay verifies the old word equals the
retimed word with the original QUERYs, and that substituting this required
host and the demoted QUERYs gives the same complete interval map. Only
`B8` occurs in the remaining host correction. A control restores one
cancelled ADD and breaks exact equality on the role-0 input column.

Let `Delta = D J* D^-1 - J`. Outside the four bound roles, the extra input
columns are signed copies of column 1 for roles 1–7 and 9–17, and of
column 19 for roles 19–25 and 27–35. The signs alternate in each range
with the first coefficient of each aggregate equal to +1. The outside
output rows in the second group are identical, and the first group's
outside output rows are zero. Thus two fixed linear gathers and one fixed
scatter suffice for the *outside part of the normalized interface*. The
role-8/19 by input-1/19 submatrix is diagonal with entries 2 and 4 at
`q = -1`, even at unit bodies. It certifies two necessary outside input
directions. Row 19 certifies the additional write direction.

This also bounds arbitrary body-independent phase-even mixing around a
shared interface. Suppose the local map factors as `C + W K V`, where
the feedthrough `C` and the ingress and egress `V,W` are independent of
`B8` and even in q on the real phase pair. The `B8` difference at
`q=1` has rank four with row and column spaces supported exactly on the
old hosted roles. Therefore the four hosted input and output axes must lie in the row space
of `V` and column space of `W`. The `q=-1` minus `q=1` difference
at unit bodies also factors through them. Modulo those four role axes, it
contains the rank-two input minor and a nonzero output direction. This
requires at least six ingress and five egress dimensions in the stated
factorization. Retaining the ordinary host's four fields while changing
their basis alone cannot supply the correction in that model.

## Existing native carriers

The verifier scans all 6,279 literal native MOVE events. It tests the
rank-one quotient of their phase polynomials against the central axis 11,
allowing an ordinary translation correction. It finds eight matches,
all exact without that correction. Four belong to already-bound main
fields and four to productive helpers. The helpers all ascend from chart
3, with empty basis, to chart 0, with basis `[11]`.

| Helper | Native MOVE | First contact | Productive input that isolates the moved row at that cut |
| ---: | ---: | --- | --- |
| 988 | 32194 | 32195, ADD into 772 | 988, coefficient 3/4 |
| 225 | 32641 | 32642, ADD from 0 into 225 | 225, coefficient -1 |
| 224 | 32643 | 32644, ADD from 0 into 224 | 224, coefficient -2 |
| 989 | 35131 | 35132, ADD into 772 | 377, coefficient 1/2 |

The complete literal chart-0 bank immediately before each first contact
is recorded in [RESULT.json](RESULT.json). Varying the indicated arbitrary
productive input changes only the proposed carrier in that bank. An
added aggregate in the same carrier direction is indistinguishable from
such a dirty input. A readout using that bank which cancels arbitrary
dirty inputs consequently kills the proposed signal too.

For a separate test, grant injection just before each of these four
moves, leave the native suffix fixed and ask for unchanged productive
helper outputs. In normalized coordinates the four injection columns on
helper return rows `317, 929, 61, 1344` are

```text
[ 2     0     0    2 ]
[ 0    1/4    0    0 ]
[ 0     0   -5/8   0 ]
[ 0     0     0    2 ]
```

The determinant is -5/8. No nonzero combination leaves those four returns
unchanged. The same check follows both forward columns and reverse
covectors, including the retained COPY guard in the forward walk. The
988 and 989 injections vanish at all 400 main returns. Of the four
injections, only 225 reaches any port-0 main endpoint, native field 112,
with normalized coefficient 1. None changes the caller's other
unbound outputs through the retained port binding.

The two tests respectively hold the first-contact bank and the entire
remaining native suffix fixed. Additional coframes, paid snapshots,
changed suffix corrections and a genuinely enlarged binding have
different hypotheses. The gross budget for two deletions is two
rank-one children at one port, before any new routing or work. The exact
retiming adds no paid child and no productive target. There is no
verified QUERY deletion or change in κ.

## Verification

Run with CPython 3.12 and assertions enabled.

```sh
python3.12 -I -B research/p104-stage8-query-carrier/verify.py
python3.12 -B scripts/research_package.py --package research/p104-stage8-query-carrier
```

The first command is self-contained in the package. The upstream heads and
paths of the package-local snapshots are in SOURCES.json retained_inputs. It authenticates the
four retained files, recomputes the receipt from the actual source words,
rechecks the real phase difference against #7343's separate modular
evaluator, and validates the retiming control. The carrier bounds use
the literal chart-normalized word. They do not build a new physical
provider, adjoint, tape or precision compiler. No selected replay was
needed for these finite statements.

## Open next questions

Find one actual layout for the two aggregate reads and the additional
scatter. At its first protected reads, show that the exposed phase
responses survive cancellation of every independent dirty input. A
shared transport with two timely snapshots or a changed suffix that
restores the helper rows could change the obstruction. Price the
physical binding, storage, returns and compiler at the same target
before attempting replication. See [TASK.json](TASK.json).

## Credit

Rohan Arun's #7113 supplies the caller and binding. Clear1nsight's #7334
supplies the native comparator. ToikY's #7342 and #7343 supply the exact
Laurent and modular engines, #7344 supplies the fixed-host provider
limits, and #7399 gives the distinct fixed-clock idle projection
obstruction. Dillon's #5388 demonstrates already-paid query hoisting
on a different producer and leaves changed dirty returns as an open
obligation. Substantial OpenAI Codex assistance. ChatGPT Pro helped
formulate the causal and dirty-return tests.

[caller]: https://github.com/CrocSwap/integer-mult-bounds/tree/07a76c5e2738882c0cb322278e56f6cae3c9885d/research/signed-caller-8x9
[native]: https://github.com/CrocSwap/integer-mult-bounds/tree/aaeec8c0acf01e99a5f331ef363a698d9c084ace/research/p104-helper-319-fused-return
