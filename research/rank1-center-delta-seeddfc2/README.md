# Rank-one difference between dirty-output centers

**Result:** an exact local construction on two-bit sources. Two rank-two bilinear
centers whose difference has rank one admit a joint rank-three tensor. This saves
one rank-one child against separate evaluation while preserving arbitrary dirty
output panels and an untouched scratch panel. The claim is local to this map pair;
it does not identify a compatible pair in the selected supplier.

## Scope and evidence

This refines the `persistent-boundary` card to the explicit pair in
[TASK.json](TASK.json). The three products are `x0*y0`, `x1*y1`, and `x0*y1`,
with output coefficient vectors `(1,0,1,0)`, `(0,1,0,1)`, `(0,0,1,1)` in target
order `(p0,p1,q0,q1)`. The output-slice span has dimension three, so no two-atom
joint decomposition exists. Each center separately has rank two, making the
four-versus-three child comparison exact for this pair.

The same construction gives a general local lemma: if `F` and `F+H` both have
bilinear rank `r` in a common frame, and `H(x,y)=alpha(x) beta(y) c` is one
rank-one tensor, the paired dirty-target map has rank at most `r+1`, versus
`2r` for separate evaluation. It saves at least `r-1` bilinear children for
`r >= 2` in this rank model. The output coefficient vectors are part of each
tensor atom; frame changes, copying, precision, hosting and restoration remain
outside the lemma and must be priced at a concrete occurrence.

For the proof, write `F = sum_i alpha_i(x) beta_i(y) c_i`. Route each product
to the paired output vector `(c_i,c_i)`, then evaluate the single correction
product once with output vector `(0,c)`. This computes `(F,F+H)` with `r+1`
rank-one bilinear atoms. Applying the same atom updates to arbitrary dirty
target panels is legal because every update is XOR and therefore involutive.

The verifier exhausts all 1,024 states with `x,y,p,q,scratch` independently in
`F2^2`, compares the atom circuit to the direct bilinear map, checks the target
update is an involution, and preserves both source inputs and scratch. Negative
controls omit the correction or one of its two output coefficients. The exact
receipt is [CERTIFICATE.json](CERTIFICATE.json); pinned source hashes and Git
blobs are in [SOURCES.json](SOURCES.json).

The second result is only a favorable selected-profile screen. It assumes all 72
candidate pairs exist and every cost outside the rank-one correction is zero.
The exact fixed-word ceiling improves from the selected upper bound
`1690054109089/10^15` to the interval in the certificate, but remains below the
`1/99` saving target. No supplier occurrence, frame realization, new `kappa`, or
frontier change is established.

The focused package PR is [#1838](https://github.com/CrocSwap/integer-mult-bounds/pull/1838).
The claim and live coordination record are at
[Discussion #1166, comment 18922942](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18922942).
Related work includes identical-center sharing (#1708, #1748, #1791), idle-axis
hosting (#1516), and restoration batching (#1155). The tested distinction is
the explicitly charged rank-one tensor difference.

## Reproduce

From the repository root, with the pinned source tree available:

```sh
python3 -B research/rank1-center-delta-seeddfc2/verify.py
python3 scripts/research_package.py --package research/rank1-center-delta-seeddfc2 --check-only
python3.12 -B scripts/research_package.py --package research/rank1-center-delta-seeddfc2
```

The verifier uses exact `F2` operations and rational ceiling intervals. It is
read-only. Python 3.12 is the repository's registered replay target; a local
Python 3.14 replay may be used when 3.12 is unavailable, with that limitation
reported separately.

## Open next questions

1. Does a pinned selected-supplier pair of same-source center tensors have an
   exact rank-one difference? This determines whether the local child saving
   can affect a paid profile. First step: extract one candidate pair's center
   maps in a common source/output frame and compute the difference tensor.
   Blocker: no occurrence is named or routed by this bounded prototype.
2. What is the native frame, copy rank, precision, and restoration cost of the
   correction child at a real occurrence? These determine whether the abstract
   one-child correction retains its cost advantage. First step: instantiate one
   source-pinned occurrence and count every interface operation. Blocker: this
   package contains no selected E8 frame realization.

## Credit

Prepared by Cinna / commdata2338 with substantial OpenAI Codex assistance. No
independent human review is claimed. Identical-center sharing is attributed to
the related work linked above; this package supplies a rank-one-difference
construction and exact dirty-state receipt. The selected profile and fixed-word
ceiling inputs are attributed to their pinned repository packages in
`SOURCES.json`. New work is Apache-2.0.
