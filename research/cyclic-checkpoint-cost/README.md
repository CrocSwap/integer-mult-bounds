# Exact canonical-checkpoint costs for cyclic output frames

This scoped proof answers the second **Open next question** in Ross
Richardson's [PR1287](https://github.com/CrocSwap/integer-mult-bounds/pull/1287).
It gives a closed form and an attaining schedule for any prescribed canonical
cuts in that fixed-child batch, and the sharp price of one extra cut.
No new kappa is claimed.

For workspace/output rotation prices `A=3, B=1`, five children cost 8 boundary
units. A canonical cut after child 2 still costs 8; a cut after child 1 costs 9.
Eager restoration costs 15. Thus an internal canonical cut can retain the full
boundary saving. These costs exclude the common child bodies. With the inherited
six-ADD rotation backend, the two boundary passes in a complete echo save
respectively 84 and 72 ADDs against eager restoration. No new rotation circuit
is asserted.

## Contract and exact formula

Use the predecessor's fixed indivisible children

```
C_i(D,W) = (D + R_i W, P W),   R_i P = Q R_i,   P^3 = Q^3 = I.
```

`P,Q` rotate every workspace/output triple. Inputs and private child workspace
are arbitrary dirty values. The parent applies only whole-register powers of
`P,Q` between ordered complete children. Either nonidentity power costs `A>0`
on workspace and `B>0` on output. The word must work uniformly over all admitted
readers and arbitrary incoming output. Before each child the two phases must
therefore agree. A canonical cut requires both phases zero. Cuts are read-only
frame requirements, without mutation or adaptive changes to later children.

Let `b(k)` be the minimum boundary cost for `k>=1` children, canonical at both
ends, without internal cuts. For all positive real prices:

```
if A <= B: b(k) = k A
if A >  B: b(k) = k B + f(k mod 3)

f(0) = 0
f(1) = A-B
f(2) = min(2(A-B), A)
```

For prescribed cuts partitioning the children into positive segment lengths
`k_1,...,k_s`, the exact optimum is `sum_j b(k_j)`.

The extra cost of splitting one segment into lengths `u,v>=1` is
`b(u)+b(v)-b(u+v)`. It is zero when `A<=B`. When `A>B`, its sharp maximum is

```
(A-B) + min(2(A-B), A).
```

Residues 1 and 2 in either order attain the maximum. Optimality concerns this
macro alphabet and uniform reader class. Opening child bodies changes the model.

## Proof

The predecessor gives the aligned transition. If the phase before a child is
`t` and the next aligned phase is `s`, put `d=s-t mod 3`. The child changes
`(t,t)` to `(t+1,t)`, so its post-child powers and transition prices are

```
workspace: d-1 mod 3,   output: d,
c(0)=A,  c(1)=B,  c(2)=A+B.
```

A nonzero entrance phase `(t,t)` costs `A+B`. Replace that entrance and its
first post-child gap by a first transition from phase zero to the same next
aligned phase `s`. That transition costs at most `A+B`, so is no dearer. The
next state is identical and all children remain aligned. The uniform canonical
map is preserved. Thus an optimum has zero entrance phase, including when the
first child is followed by a canonical cut.

Let `n_d` count the transitions of difference `d`. Order does not affect cost
or the final phase. The constraints are

```
n_0+n_1+n_2 = k,   n_1+2n_2 = 0 mod 3,
cost = n_0 A+n_1 B+n_2(A+B).
```

If `A<=B`, each transition costs at least `A`; all-zero differences attain
`k A`. Suppose `A>B`. Replace two differences 2 by differences 0 and 1.
Their sum modulo three is unchanged and cost falls by `A+B`. Replace a pair
0 and 2 by two differences 1: the sum is unchanged and cost falls by
`2A-B>0`. Hence an optimum has either no 2, or exactly one 2 and no 0.

With no 2 the congruence requires `n_0=k mod 3`, modulo multiples of three.
Cost increases with `n_0`, so the best such word has `r=k mod 3` zero
differences and all others 1. Its cost is `k B+r(A-B)`. The other possibility
has one difference 2 and all others 1. It is legal precisely when `r=2` and
costs `A+k B`. Taking the smaller proves the formula and explicitly constructs
an attaining word. Use the zero differences first, followed by the 1s; in the
second case use the 2 first, followed by the 1s.

Each prescribed cut has the canonical state. Restricting a legal word to each
segment gives the lower bound `b(k_j)`. Concatenating the attaining segment
words gives the upper bound, proving additivity.

For the one-cut bound put `a=A-B>0`, `c=min(2a,A)`. The residue correction is
`(0,a,c)`, where `a<=c<=2a`. A pair with a zero residue adds zero. The other
pairs add `2a-c`, `a+c`, or `2c-a`. All lie between zero and `a+c`; residues
1 and 2 attain `a+c`. This proves the bound and sharpness.

## Evidence and reproduction

The written proof establishes the quantified statement. The generated
[RESULT.json](RESULT.json) supplies finite corroboration of the new formula:

- All 16,320 cut-mask/price cases through eight children and integer prices
  `1<=A,B<=8`, compared with a separately written nine-state optimizer that
  permits every entrance and gap power.
- All 9,216 pairs `1<=u,v<=12` at those prices, checking the one-cut bound and
  its attained maximum; 72 exact rational-price cases.
- All 756 cut-mask/dimension fixtures through six children, with `1<=m<=4`
  workspace triples and `1<=n<=3` output triples. Periodic integer circulant
  readers execute each schedule on every dirty input/output basis vector and
  one signed rational probe. The 10,962 probes check the restored source and
  canonical partial batch output at every prescribed cut.
- Fourteen invalid-input/noncanonical-word rejections and three controls
  distinguishing the residue-two alternatives and an ignored checkpoint.

No predecessor code is imported or replayed. The receipt binds all five package
source files by SHA-256. Ordinary verification recomputes it and writes nothing.
From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/cyclic-checkpoint-cost/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/cyclic-checkpoint-cost/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cyclic-checkpoint-cost
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/cyclic-checkpoint-cost --check-source-history
```

Expected marker: `PASS_CYCLIC_CHECKPOINT_COST`. Elsewhere substitute the local
Python 3.12 path. `--write-result ABSENT_PATH` generates a new receipt and
refuses to overwrite; it is not the ordinary verification command.

## Limits and implementation bounds

A canonical batch cut exposes `D_initial + sum R_i W_initial`. Inside the
first batch of a source-only dirty echo this is not the completed partial
update from the external source. That stronger observation can need extra
copies, storage or a changed graph and is outside the theorem. Observation
execution costs are outside the boundary bill.

No selected supplier exposing these indivisible children is identified.
Physical routing, coefficient access, preparation, precision, native hosting
and all-size multiplication obligations remain open. The inherited child
contract, alignment rule and six-ADD upper bound are cited premises. The proof
is not checked by a formal proof kernel. The selected frontier is unchanged.

The formula implementation accepts up to 4,096 children and positive exact
integer/Fraction prices at most 4,096, with denominator at most 4,096. Schedule
emission accepts up to 64 segments and 256 total children, using linear output
space and emission work. These are implementation limits, not theorem limits.
No runtime speedup is claimed. Every function is below 60 lines. There is no
recursion, dynamic code or subprocess execution. Loops have explicit caps or
fixed fixture dimensions. Managed Python allocations are a Power-of-Ten rule-3
deviation, bounded by these caps. A fixed-storage implementation would be needed
to remove that runtime deviation. Warning-strict normal and optimized runs
exercise interpreter diagnostics; no separate static analyzer is configured.

## Open next questions

1. Can a literal consumer use a canonical partial batch record without requiring
   the completed external-source partial echo? Identify the record and its
   read-only use first. That missing consumer blocks an application of the
   zero-surcharge cuts.
2. What is the exact minimum when completed partial echoes are required at cuts?
   Start with three children and one observation, charging every source
   injection and restoration. Specify the stronger observed-output contract
   before applying the present formula.

## Scope, overlap and credit

Base main is `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
The `formal-interface-lemma` card is changed to a written exact interface proof
with finite corroboration. The card's historical baseline fails with
`KeyError: bit_lower`; the current selected-baseline source-binding command
passes. Neither is scientific evidence for this theorem.

Overlap checked live open PRs, this account's preceding-day PRs, the last 100
handoff posts, active discussions, distinctive main README and merged-PR
searches. The cached scan covered 379 open PRs and 3,852 Discussion records;
local notes were sparse. No matching canonical-cut formula was found within
that coverage. Unpublished work and arbitrary diffs remain outside it.
The [public claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19133719)
records the target and stopping rule.

This contribution was produced by Nick Petalas. Ross Richardson #1287 supplies
the order-three contract, alignment implication, sharp recurrence and explicit
checkpoint handoff. The new step is the closed form, arbitrary-cut optimum and
sharp surcharge, with independently written finite checks. Credit Sagar Thakrar
#1227 for paid output-sign frames, mightyOil/Philipp #1203 for compatible-reader
boundaries, and Ross Richardson #1145 for the six-ADD rotation upper bound.
Hanson Sun #1488 treats faithful S3 transport and cut policies; Cinna Davis #1391
treats order-four transport. Their work and the retained restoration/echo
lineage keep predecessor credit. No predecessor files or credits are changed.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.
