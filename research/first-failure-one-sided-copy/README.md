# A fixed-frame COPY saving at the one-sided first-failure boundary

Two finite exact constructions on the 93-line unit of
[ToikY's PR1609](https://github.com/CrocSwap/integer-mult-bounds/pull/1609):

| Construction | Separate-term binary pairing ranks | Total |
|---|---|---:|
| All-pairs identity in the exhibited non-coordinate frame | 9,9,9,9,9,9,9,9 | 72 |
| One-sided mask-only completion in that same frame | 8,9,9,9,9,9,9,9 | 71 |
| Another all-pairs identity on the same live lines | 7,8,7,8,8,8,8,9 | 63 |

The new step is an explicit non-coordinate frame in which one-sided masked
freedom saves one COPY unit. The COPY63 construction shows why this does not
establish a saving against an appropriate all-pairs comparator. Neither
construction is asserted optimal. This is a finite certificate and a written
linear-algebra derivation, with no new kappa or physical supplier.

## Model and fixed input

Use doubled E8 roots `q`, of squared norm eight, with first nonzero coordinate
positive. Their lexicographically sorted list has 120 lines. Write `r=q/2`
and `G_ij = r_i dot r_j`. The required mask consists of equal or orthogonal
root lines. The binary pairing table is

```text
N_ij = 1  if G_ij is even, and 0 otherwise.
```

A term with actual top support `S` and bottom support `T` costs
`rank_F2 N[S,T]`. We sum the ranks of all eight terms separately.

The fixed predecessor instance has

```text
q_t = (2,2,0,0,0,0,0,0),   n = (1,-1,2,0,0,0,0,0).
```

Delete exactly the orthogonal lines `q_i` with `q_i dot n != 0`. There are
27 deleted and 93 live lines. The target neighbourhood consists of the
target and 36 live orthogonal lines, all annihilated by `n`. PR1609 supplies
this instance and its first-failure interpretation. Its sharp threshold
and flat census are cited, not re-proved here. The verifier binds the
predecessor certificate hash and checks the exact deleted-index list.

## The non-coordinate construction

Let the bottom directions be the rows

```text
w_0 = 13 q_t + 7 n = (33,19,14,0,0,0,0,0),
w_1 = e_1, ..., w_7 = e_7.
```

Let `u_0,...,u_7` be their dual basis, so `u_k dot w_l = delta_kl`.
Explicitly, `u_0=e_0/33`, `u_1=e_1-19e_0/33`,
`u_2=e_2-14e_0/33`, and `u_k=e_k` for `k>=3`.
For a scalar `c`, put `s_j=q_j` except `s_t=q_t+c n`, and set

```text
D_ik = q_i dot u_k,       T_jk = (s_j dot w_k)/2.
```

Biorthogonality gives the identity

```text
(D T^T - 2G)_ij = 0                         if j != t,
(D T^T - 2G)_it = (c/2) (q_i dot n).
```

Thus every `c` preserves all masked entries. The top factor is root-linear.
At `c=0` the product equals `2G` on every pair. Choose

```text
c = -(w_0 dot q_t)/(w_0 dot n) = -104/42 = -52/21.
```

This removes the target from the first bottom support. That support was
exactly the 56 lines odd to the target together with the target itself;
it becomes those 56 lines. The verifier enumerates these sets and checks
that their full pairing-row spans have ranks nine and eight, respectively.
The first top support spans the full rank-nine pairing-row space.
Direct elimination of the actual rectangular pairing submatrices gives
first-term rank nine before the change and eight after it. Every other
term has rank nine in both cases.

The verifier checks all 8,649 entries of each product. At `c=-52/21`,
exactly 56 entries differ from `2G`, all unmasked and in the target column.
This proves the finite COPY72 to COPY71 comparison in this frame.
For every positive power `p`, the same comparison is strict:
`8^p + 7*9^p < 8*9^p`.

## The all-pairs comparator

Choose these eight independent top directions, all doubled root vectors:

```text
(0,0,2,0,0,0,0,2)
(0,0,2,0,0,0,-2,0)
(1,-1,1,-1,-1,-1,-1,-1)
(1,-1,1,-1,1,-1,-1,1)
(1,-1,1,1,1,1,-1,1)
(1,-1,1,-1,1,1,-1,-1)
(1,-1,1,-1,-1,1,-1,1)
(1,1,1,1,-1,1,-1,1)
```

Use their duals as bottom directions and set every `s_j=q_j`. The same
biorthogonality identity gives `D T^T=2G` on every pair. The computed
ranks are `7,8,7,8,8,8,8,9`, summing to 63. Seven top directions are
among the deleted lines; factor directions need not themselves be live
ports. The full rational duals are generated in [RESULT.json](RESULT.json).

After sorting, this comparator's ranks are coordinatewise no larger than
those of the COPY71 mask-only construction, with seven strict inequalities.
It therefore has a smaller COPY power sum for every positive power `p`.
This compares the two exhibited profiles and supplies no optimum or lower
bound for either decoder class.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/first-failure-one-sided-copy
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/first-failure-one-sided-copy/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/first-failure-one-sided-copy/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/first-failure-one-sided-copy --check-source-history
```

Another CPython 3.12 installation can replace the interpreter path.
Both registered commands have 120-second limits and print
`PASS_FIRST_FAILURE_ONE_SIDED_COPY one_sided=71 same_frame=72 all_pairs=63 no_new_kappa`.
Default replay writes no files. To generate a fresh receipt, pass
`--write /absolute/path/to/new-result.json`; existing destinations are rejected.
The receipt binds the verifier and predecessor certificate SHA256 hashes.

Each actual support pairing rank is cross-checked by bitset elimination and
separate dense F2 elimination. Rejection controls plant a masked coefficient
error, expose a nonzero masked error upon each of the 27 possible one-line
restorations, and test a frame whose first pairing rank is eight.
No predecessor executable is imported or run.

The verifier has no recursion, subprocesses or network calls. Functions fit
within 60 physical lines. Loops are bounded by 120 lines, eight dimensions,
eight terms, 27 restorations or the fixed root generator's 256 sign patterns.
Binary elimination has an explicit 120-step inner bound. Checks remain active
under Python optimization; both registered runs treat warnings as errors.

Power of Ten rule 3 deviation: CPython allocates managed objects during exact
arithmetic. Live matrices have at most 120 rows and 120 columns; rational
frames are 8 by 8, and residual maps have at most 93 squared entries. The
fixed input certificate is capped at 1 MiB. A fixed-allocation rewrite would
require another runtime. Reassess these bounds before parameterizing the
geometry. No additional static analyzer or repository-wide configuration
change is introduced.

## Scope, overlap and remaining obligations

The result covers this fixed unit, the displayed frames and separate-term
binary pairing-rank charges. Gathering, native endpoints, arbitrary-dirty
restoration, frame changes, hosting, precision/tape, all-size/compiler
realization and analytic transfer remain unpriced and unproved here.
No selected cold replay, Lean or Docker run was performed. Independent human
and formal proof-kernel review are unclaimed.

The original [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19530146)
planned a coordinate census as well. That census is omitted from this delivery
because the [earlier coordinate-perturbation claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19530120)
covers it. This package claims only the explicit non-coordinate construction
and displayed comparator, and does not claim the best root-frame comparator.
The P112 results of merged #2816 concern another live set and their stated
one-sided classes. Merged #5232 concerns fixed A7+A1 normals and another
puncture. Neither supplies the finite constructions given here.
[TASK.json](TASK.json) records the changed scope and overlap coverage;
[SOURCES.json](SOURCES.json) binds historical provenance and the live input.

## Open next questions

Can an eight-term one-sided mask-only completion on this fixed unit beat the
exhibited all-pairs profile `7,7,7,8,8,8,8,9`? A first step is to parameterize
root-linear top frames and the one-dimensional target-row freedom, then
compare actual support pairing ranks. This matters because a fixed-frame
saving does not settle the comparison over frames. No global optimization
or lower bound is supplied; physical realization would remain an additional
obligation. The structured question is in TASK.json.

## Credit

This contribution was produced by Nick Petalas. New work is Apache-2.0.
ToikY's #1609 supplies the 27-deletion boundary, exact instance and open COPY
question. Philipp / mightyOil's #1191 supplies the one-sided local-spanning
mechanism. DreamingOfClouds's #717 and #2338 supply the separate-term COPY
model and accounting context. Joaqcoo's #1224 and Adam Gall's #2062 develop
the row-shift normal form; Nick Petalas's #5232 applies row shifts to the
different A7+A1 puncture. The E7 geometry retains the predecessor credit of
DreamingOfClouds #595 and DaysSky #897. The displayed frame, its COPY71
completion and the explicit COPY63 comparison are the contribution here.
