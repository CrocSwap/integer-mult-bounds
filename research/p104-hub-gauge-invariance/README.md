# Fixed-word hub-gauge invariance for PURE helper pairs

**No new κ.** This package answers the interior-pair open question in
[#6835](https://github.com/CrocSwap/integer-mult-bounds/pull/6835) under a
precise fixed-word, complete-helper-class contract.

If one pair of zero/full hub maps satisfies `G9 T G0 = A`, with
`A=I+E` and `supp E ⊆ (K\R)×(R\K)`, then **every** solution is

```math
G'_0=G_0B,\qquad G'_9=B^{-1}G_9,\qquad B\in GL_{K\cap R}(\mathbb Z[1/2]).
```

At any matched cut in the unchanged middle word, `P'=PB`. A PURE pair
transports by `c'=B^-1 c`, `d'=d B`, with its physical read and write
vectors unchanged. Therefore the full dyadic pairing, every Smith factor
and its simultaneous PURE retirement capacity are invariant. This is
stronger than a comparison of rational ranks.

The conclusion applies to **complete equal-boundary helper classes** in
the retained native fixture: every member of `H=K∩R` is an eligible
helper, and all other such classes are disjoint from H. More generally B must preserve the helper block, both
columns and dual rows. A restricted label set or constrained boundary
basis alphabet need not meet that condition.

## What is new, and what is inherited

DreamingOfClouds's #6835 proves the normal-form existence conditions but
leaves this cut question open. DreamingOfClouds's #6827 supplies the PURE
criterion and the unit-divisor capacity theorem. Ali Romman's #5599
supplies the earlier physical independent-input helper split, the
prefix/suffix sufficient conditions and dyadic completion mechanism.

The new results here are the complete endpoint-gauge stabilizer, its
isomorphism of the PURE pairing, and its transport of the earlier
prefix/suffix sufficient split witnesses when private resets make the
state rectangular. We audit the predecessor's dyadic existence proof
without replacing its completion theorem or claiming a new completion
algorithm.

## Exact examples and native application

The checker contains a three-coordinate family with Gram matrix `[m]`.
For `m=4` it has a dyadic unit pair; for `m=3` it has rank one and no unit
pair; for `m=0` both modules are nonzero but pair to zero. A nontrivial
dyadic hub gauge preserves these Gram matrices exactly. A simultaneous
example has Gram `diag(4,3)`, rational rank two and capacity one.

A second control has **the same total middle matrix `T=I2` and the same
seven MOVEs** in two legal words. Four intermediate ADDs mix two registers,
separate them into different frames, and later undo the mixing. At the
matched cut the complete helper class has capacity one in the baseline
and zero in the changed word. Exact Laurent-polynomial replay verifies
the same full formal chart endpoint. Thus fixed total T alone does not
fix cut capacity: the unchanged event word and matched physical bank are
essential premises.

For the retained #6824 word, the original and #6835 reconstructed gauges
are related by a nontrivial dyadic B supported exactly within the
359-dimensional common helper block. The program checks its inverse,
all 77 complete helper boundary classes, and prefix transport on every
public and private state row at three interior cuts. It also checks each
middle pre-CLEAR row. This is an applicability check of the actual
source, not a symbolic productive-pair census.

The retained scalar model resets nonzero private rows at 32 middle
CLEARs. Accordingly, the proof distinguishes PURE sufficiency from the
claim of PURE necessity in an invertible-state model. The broader
prefix/suffix sufficient contract is also invariant; its capacity is not
silently identified with the PURE Smith count.

## Reproduce

Standard library only, Python 3.12 used for the recorded run:

```sh
python3 -I -B research/p104-hub-gauge-invariance/verify.py
python3 -I -O -B research/p104-hub-gauge-invariance/verify.py
```

For the quick mathematical examples without the native fixture replay:

```sh
python3 -I -B research/p104-hub-gauge-invariance/verify.py --small-only
```

`--output PATH` writes the certificate. `RESULTS.json` records a full run;
timing is diagnostic and is not a mathematical equality target. All
failures use explicit exceptions, including under `-O`. No network,
third-party numerical package, probabilistic rank, or external checkout
is needed. Retained Python source is hash-checked and compiled directly,
so stale `.pyc` files cannot override it.

The manifest registers normal and optimized runs. `PROOF.md` contains the
general proof and complete contracts; `VERIFY.md` explains the evidence
and unrun obligations. Source pins and contributor notices are retained.

## Limits

This rules out an exhaustive **gauge-only** search as a route to more
intrinsic PURE capacity in the same middle word. It does not rule out
changed middle operations, routes, intermediate gauges followed by
separation, different helper boundaries, changed read rules, or a more
efficient implementation of boundary bases. Any resulting candidate
still needs its complete legality and productive/paid invoice.

## Open next questions

Can an intermediate basis change improve the complete invoice on the retained P104 word?
A useful next experiment would specify one actual intermediate frame,
change the middle word there, and prove the full independent-input
identity and restoration bill. The two-register control establishes
possibility in principle, not an improvement in the retained P104 word.
The selected `0.003125804` result from #6030 and its five framework
assumptions remain unchanged.
