# Exact symmetric-phase rigidity of the PR4610 round-three word

**Scoped exact linear certificate; no new kappa.** The unchanged-paid-rank
mechanism in [Dugongue's #4654 phase-form grammar](https://github.com/CrocSwap/integer-mult-bounds/pull/4654)
has only the zero solution on Cao Yifan's frozen round-three native word under
the boundary conditions below. All **310,640** free binary symmetric-form
coordinates are forced zero by **559,016** exact homogeneous equations. Both
boundaries of all 408 independent helpers are allowed to vary.

This answers the concrete next question of whether that new grammar supplies
more productive helper rank at unchanged paid ranks on the strongest local
word checked in this session. It does not. It does not rule out phases that
increase some paid ranks, changed subspaces/maps, changed scalar order, relaxed
adapter/owned interfaces, or a new controller. No global phase obstruction or
optimal kappa is claimed.

## Frozen object and exact scope

The input is `research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz` at PR4610
head `1eb8da6cfb35512c0cc2533413e5ca42f48e13c6`. Its exact bytes are vendored
with original commit/path/blob provenance and an exact Git pin for the retained
copy in [SOURCES.json](SOURCES.json). Its local
paid profile is `{1:2201,2:412,3:510,4:127,5:40,8:8}` and its productive helper
profile is the retained `{4:28,7:7,8:47,9:326}`. This package neither changes
that word nor claims its proposed integer-multiplication exponent as reviewed.

At every scalar contact or chart boundary with subspace U, assign an arbitrary
symmetric bilinear form b on U, with dim(U)(dim(U)+1)/2 coordinates. This is the
full local symmetric-form space, not a search of 511 ambient rank-one forms.
The actual fixed conditions are:

* Keep all original subspaces, scalar chronological operations and shared G maps.
* Freeze both main endpoints, every explicit adapter boundary, and every scalar
  contact involving the owned C field to the original zero form.
* Preserve every paid Gaussian rank and every monomial native warp rank.
* Use one common form for every operand at each scalar contact. Both helper
  entrance and exit forms may vary, with their actual difference tested.

In particular the result does not cover a redesigned owned-center protocol.
The construction represents 19,199 nodes, including two inert sentinels, with
957 frozen nodes. Zero-dimensional contacts carry no form coordinates.

## Why the equations are sufficient and complete for this model

For a nested paid edge U subset W, the phase-form grammar gives

    new_rank = dim(W)-dim(U) + rank((b_U+b_W)|U).

Its old rank is unchanged exactly when the restricted forms agree. For each
pair of source basis vectors x,y, emit b_U(x,y)+b_W(x,y)=0. On a fixed logical
warp G:U->W, rank zero is preserved exactly when

    b_U(x,y) = b_W(Gx,Gy).

The verifier checks that the actual shared G maps the source chart onto the
target chart before emitting its equations, using G inverse on negative
occurrences. Scalar contacts share one node. Frozen node coordinates are zero.
These are the original conventions of #4654; no F2 reinterpretation of the
rational BIT geometry is involved. Only the complex nine-bit frame word is used.

In coordinates x=B a, y=B c, the coefficient of S_ii is a_i c_i, and the
coefficient of S_ij for i<j is a_i c_j+a_j c_i. The verifier computes these
coordinates by exact binary elimination. It emits 554,922 nonzero paid-edge
equations and 4,094 nonzero warp equations, rather than trusting a solver or
merely checking a saved numerical rank.

An elementary substitution certificate suffices. Each one-variable equation
sets that coordinate to zero; each two-variable equation identifies their
classes. Longer equations are revisited after substitution. The closure merges
all 310,640 coordinates into the zero class and discharges every equation.
There is no residual system requiring numerical elimination or a rank estimate.
Since each substitution follows an original homogeneous equation, every
solution of the original system must be zero. Conversely zero satisfies every
equation. This proves uniqueness.

For each helper, the verifier also evaluates all symmetric coefficient
functionals of (b_start+b_end) on its entrance space. All 80 nontrivial queries
are forced zero, so the productive rank cannot increase. This latter statement
would still be useful if some irrelevant form coordinates survived; here the
stronger all-coordinate rigidity is certified.

## Reproduce and verification limits

Standard-library CPython 3.12, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/symmetric-phase-rigidity
python3.12 -I -O -B research/symmetric-phase-rigidity/verify.py
```

The replay authenticates the source, reconstructs the graph and all equations,
discharges them exactly, and compares [RESULT.json](RESULT.json). Replacing
every frame basis by an independently changed basis gives the identical result.
Three small exact controls distinguish a surviving free direction, a forced
zero direction and a higher-arity equation that becomes decisive after other
substitutions. The discovery calculation was also performed with a separate
C++ equality/elimination implementation; the registered proof uses Python only.
Both implementations were prepared by the same assisted author, not independent
human reviewers.

This checks the frozen word's geometric phase constraints. It does not rerun
its arbitrary-column native endpoint proof, absolute Clifford phases, the
uniform compiler, BIT admission, precision, fixed-tape/Word RAM transfer or the
outer theorem. Those are unnecessary to the stated no-solution certificate and
are not claimed as verified here. The selected conditional kappa remains
0.00302015 at canonical base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`.

## Open next questions

A useful phase construction must escape at least one of the stated constraints.
The next bounded experiment is to allow explicitly costed rank increases at
paid or warp edges and compare the complete helper reward with that added bill.
Alternatively a changed chronological graph or a separately realized owned
center gauge can escape this certificate. A larger unchanged-rank nullspace
search on these exact bytes cannot. See [TASK.json](TASK.json).

## Credit

Prepared by Cinna Davis with substantial OpenAI Codex assistance, Apache-2.0.
Credit Dugongue for the source-convention-aware symmetric-form grammar and
phase-flow construction in #4654; Cao Yifan for PR4610's round-three word and
native G/helper interface design; Cinna Davis's #4440/#4441/#4447/#4470 supplier
and controller lineage; zxv, Jacob Alan Sussman and the retained scalar, E8,
Clifford, native, precision and compiler contributors. Classical bilinear-form
coordinates and exact equality substitution are not claimed as new mathematics.
