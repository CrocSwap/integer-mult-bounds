# The fixed border needs two repair locations

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and predecessor

Take Ali Romman's five-call border in
[PR6398, BOUNDARY-MODULES.md, sections 2 and 3](https://github.com/aliromman/integer-mult-bounds/blob/dee2663ba0918be86993fd9d63c8d64b020f4c83/research/mixed-projector-root-headroom/BOUNDARY-MODULES.md).
Its five chronological factors, parameterized by a nonzero scalar `e`,
are fixed throughout this result. Three independent invertible commuting
stage variables are `A,B,C`; the central involution is `S`.
The target is `S diag(ABC,A,B,C)` on four arbitrary input fields.

**Theorem.** Over any field of characteristic other than two, no linear
repair confined to one of the six cuts can make this fixed word equal its
target as a formal identity in `S,A,B,C` modulo `S^2=1`. The repair may be an arbitrary
matrix depending on `S` and `e`, of any rank, but must be independent of
`A,B,C`. Consequently a product of arbitrarily many such operations at one
cut also cannot repair it. The minimum number of distinct repair cuts is two,
attained by the predecessor's two rank-one corrections.

The cut is fixed as part of the word, independently of the stage variables.
There are four fields and no additional workspace. The theorem does not
cover retuning the original factors, moving stage operations, using a stage
or its inverse inside a repair, nonlinear recovery or approximate recovery.
It is a scoped algebraic obstruction, not a supplier or kappa claim.

The predecessor supplies the border and its two-correction construction.
The new result is the exclusion of every single repair location, including
arbitrary-rank and arbitrarily long central-only blocks. It does not replay
the predecessor's native word, root search, counts or price exclusions.

## Normalize the nonzero border parameter

Write `Q_i(e)=I+(S-1)u_i(e)v_i(e)` for the five query matrices and `D_i`
for their left stage multipliers. In chronological order, these are

| i | u_i(e) | v_i(e) | D_i |
| --- | --- | --- | --- |
| 0 | (1,0,0,0) | (0,1/e,0,0) | diag(A,A,1,1) |
| 1 | (-1/e,1,0,0) | (0,1,-e^2,0) | I |
| 2 | (-e,0,1,0) | (-1/e,0,-1,0) | diag(B,1,B,1) |
| 3 | (-e,0,1,-1) | (-1/e,0,0,0) | I |
| 4 | (1,0,0,1/e) | (-1,0,0,e) | diag(C,1,1,C) |

Let `E=diag(e,1,e^2,e^2)`. Each outer product satisfies

`u_i(e)v_i(e) = E^-1 u_i(1)v_i(1) E`.

All `D_i` and the target commute with `E`. Therefore the entire word,
each prefix and suffix, and the unique required repair at any cut are
conjugates by `E` of their `e=1` counterparts. Since `E` is invertible
and independent of the stages, existence of a stage-independent repair
is equivalent at `e` and at one. This similarity is an algebraic proof
device, not a claim of free physical normalization.

## A two-point middle-stage witness at every cut

It suffices to specialize `S=-1`, `A=C=1`, and write `B=b`.
These scalar stages are a valid restriction of a formal identity.
In fact the two witnesses `b=1,-1` are already unitary scalar stages.
Set

`M_i = D_i (I-2u_i(1)v_i(1))`.

For the three full sites `v_i u_i=0`, so the inverse of their query
factor is `I+2u_i v_i`. At the other two sites `v_i u_i=1`, so their
query factors are their own inverses. Thus every factor is invertible
for `b!=0`. Define, for `0<=k<=5`,

`P_k=M_(k-1)...M_0`, `L_k=M_4...M_k`, and `T=-diag(b,1,b,1)`.

Empty products are identity matrices. Any inserted matrix `K` satisfying
`L_k K P_k=T` is uniquely forced to be

`K_k(b) = L_k^-1 T P_k^-1`.

Direct multiplication gives the following complete table. Coordinates are
zero-based and `E_ij` is a matrix unit. Each row lists `K_k(b)-I`.

| cut k | Required displacement |
| --- | --- |
| 0 | `-2/b E_03 + 2 E_12` |
| 1 | `-4 E_02 - 2/b E_03 + 2 E_12` |
| 2 | `-2/b E_03 - 2 E_12` |
| 3 | `2 E_03 + 4/b E_10 + 2/b E_12 - 4 E_23` |
| 4 | `4 E_00 - 2 E_03 + 2/b E_12 + 8 E_30 - 4 E_33` |
| 5 | `-2 E_03 + 2/b E_12` |

For cuts zero through two, entry `(0,3)` equals `-2/b`.
For cuts three through five, entry `(1,2)` equals `2/b`.
Each changes by a nonzero multiple of four between `b=1` and `b=-1`
in every characteristic other than two. The unique required matrices
therefore differ. No matrix independent of `b` works at either cut for
both inputs. This excludes all six cuts, without restricting the rank,
determinant, central dependence or internal factorization of `K`.

Conjugation by `E` proves the same exclusion for every nonzero `e`.
Any central-only linear block at a single cut has one aggregate matrix
independent of the stages, so the exclusion covers the whole block.

The specialization is sufficient for the negative result: no interpolation
in general stages or numeric approximation to the actual native operators
is assumed. The failure already appears on two scalar stage characters.

## Sharpness and the scope of the cost consequence

The predecessor's corrections are

`I+(S-1)e^2 E_12` at cut two, and
`I+(S-1)e E_03` at cut five.

Its exact identity proves that these two locations attain the target on
arbitrary inputs. Both displacements have rank one and square to zero.
Combining that cited upper bound with the new single-cut exclusion proves
the exact minimum of two repair locations in the stated model. The verifier
also executes the attaining word on its finite fixtures, solely as the
positive witness accompanying this new lower bound.

The predecessor already prices these two direct corrections and excludes
their complete invoice at its candidate saving. This contribution does
not recount or strengthen that price calculation. It establishes that
concentrating all stage-independent recovery at one cut cannot replace
them, even with a higher-rank central operation or unlimited local scalar
mixing. Different two-cut recoveries, stage-sensitive operations, changed
factors, additional fields and precision transfer remain open.

## Exact evidence

`verify.py` computes all required corrections by exact rational inversion,
independently of the displayed formulas. It checks every cut at both
middle-stage witnesses for each of six nonzero border parameters. It then
uses the correction required at `b=1` on the `b=-1` word and requires that
the purported endpoint fail at every cut. These are 36 explicit rejected
recovery attempts, not a sampled assertion that all possible matrices fail;
uniqueness supplies the quantifier over all matrices.

There are also 36 normalized table checks and 48 attaining two-correction
fixtures, plus five domain/singularity rejection controls. Each entry of
`b K_k(b)` has polynomial degree at most two: exactly one inverse stage
factor involves `b^-1`, and `T` has degree one. The displayed candidate
table has the same bound. The checks at `b=1,2,3`, included in the six
normalized values, therefore certify the table coefficients over the
rationals by interpolation. All coefficients are integers before adjoining
`b^-1`, so the identities transfer to every field. The two-point failure
uses only `1,-1`, so it remains valid in every characteristic other than two.

The all-parameter theorem rests on this written uniqueness, similarity
and two-point argument. The finite fixtures are exact corroboration and
a coefficient certificate, not formal proof-kernel acceptance.
