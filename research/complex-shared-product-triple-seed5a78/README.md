# Persistent rank-one helper across three call roles

**Outcome: partial local construction. No selected-source placement or new `kappa` is claimed.**

## Exact three-call construction

For three output roles, let

\[
F_i(x,y)=x_0y_0+x_i y_i,\qquad i=1,2,3.
\]

Evaluating the calls independently uses six rank-one products: the common
product \(x_0y_0\) three times and one private product for each output. As one
joint bilinear map, the three outputs have an exact rank-four decomposition:
compute \(x_0y_0\) once with output coefficient vector \((1,1,1)\), then compute
\(x_1y_1,x_2y_2,x_3y_3\) with their respective coordinate outputs. The
rank-four X-mode flattening proves rank at least four.

The reversible interface uses one **clean width-one helper** \(h\):

1. Apply the rank-one child \(h\leftarrow h+x_0y_0\).
2. Add \(h\) into each of the three arbitrary dirty output targets.
3. Apply the three private rank-one children \(p_i\leftarrow p_i+x_i y_i\).
4. Apply the inverse rank-one child \(h\leftarrow h-x_0y_0\), returning \(h\) to zero.

This costs five rank-one child invocations per forward three-call batch
(two common-product calls, including cleanup, plus three private calls), versus
six when each call computes its own common product. It adds three local ADD
fanouts per direction and needs one clean helper slot per batch, reused
sequentially. The template uses the same frame throughout, has no value copies,
and reads the common source pair twice rather than three times. The inverse
reverses the schedule and restores arbitrary dirty output targets, all inputs,
and the clean helper. A nonzero helper at entry violates this interface; the
verifier includes a negative control for that case.

These are exact local costs for the displayed common-frame template. They do
not prove that the selected provider contains three roles with an identical
operand pair or has a spare clean slot.

## Exact moment screen

The pinned selected per-call profile is
\((n_1,n_2,n_3,n_4,n_5,n_8)=(2412,418,432,142,82,8)\), with
\(m=73\), 896 families, 9 stages, centre charge 64, and selected ceiling
\(a_0=1690054109089/10^{15}\). For \(s\) common rank-one products shared
across each triple and \(e\) additional rank-one-equivalent interface charges
per triple, the average rank-one profile changes to

\[
n'_1=2412+(e-s)/3,\qquad 0\le s\le2412,\quad e\in\{0,1,2\}.
\]

The two common-product child calls (compute and inverse cleanup) are already
included in the 3-to-2 saving; \(e\) prices further interface work. The other
rank counts, centre charge, and coverage law are held fixed. Exact relaxation
brackets show the 5% target \(a=35491136290869/20000000000000000\) first passes
at \(s=764,765,766\) for \(e=0,1,2\), respectively. At each boundary the
preceding integer has a certified lower relaxation bound above one and the
passing integer has a certified upper bound below one. One shared slot already
strictly improves the local ceiling under the zero-extra-charge profile.

This is an optimistic local moment screen, not a selected profile: the exact
three-call overlap count, helper hosting, and source/output frame compatibility
are not established. The \(e\) parameter is not a physical copy or storage
invoice. No supplier admission, changed selected frontier, or \(\kappa\) result
follows.

The first candidate mechanism in this cycle was to split a rank-four helper
into two rank-two helpers. The exact zero-overhead screen rejected it: even one
such split lowers the ceiling below the selected profile. The shared-product
construction is the one evidence-driven pivot.

## Pinned-source limit

The source archive and selected-record lineage are pinned in `SOURCES.json`.
The archive's phase-A local stream has 4,730 events: 3,738 scalar gates
(3,252 ADDs and 486 scales) and 992 climb records. Those records carry register,
phase, and rank data, but no explicit bilinear operand pairs. Equal ranks or
event labels do not identify equal products. Therefore this stream does not
establish a selected-provider triple reuse; no broader source impossibility is
claimed.

The exact construction, its forward/inverse invoice, and this schema-limited
observation are in `CERTIFICATE.json`. The scope claim is [Discussion #1167 comment 18923890](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18923890); the result handoff is [comment 18923996](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18923996). The focused package PR is [#1872](https://github.com/CrocSwap/integer-mult-bounds/pull/1872).

## Reproduce

From the repository root:

```sh
python3 -I -B research/complex-shared-product-triple-seed5a78/verify.py
python3 scripts/research_package.py --package research/complex-shared-product-triple-seed5a78 --check-only
python3.12 scripts/research_package.py --package research/complex-shared-product-triple-seed5a78
```

The exact verifier checks the four-atom joint tensor and its rank lower bound,
the six-atom separate baseline, dirty-target forward and inverse fixtures,
helper-cleanliness controls, complete child/ADD/helper counts, exact profile
threshold boundaries, and pinned phase-A event schema. The generic package
runner expects Python 3.12; the local environment has Python 3.14.7.

## Open next questions

1. Can the pinned selected program expose at least 766 common rank-one operand
   pairs across three call roles, or is another source-bound representation
   needed to identify them?
2. For any such triple, how much storage, transfer, frame, and restoration work
   does the selected physical interface charge beyond the modeled two child
   calls and three fanout ADDs?

## Credit

Prepared by Cinna / commdata2338. New work is Apache-2.0. Substantial OpenAI
Codex assistance in scope selection, exact screening, construction, verifier,
and package writing is disclosed in `TASK.json`; no independent human review
is claimed.
