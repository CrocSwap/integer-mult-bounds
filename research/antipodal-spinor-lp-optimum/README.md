# The antipodal D16 spinor relaxation has a unique exact optimum

**Scoped proof with an exact finite linear-program certificate. No new kappa.**
The full real-valued antipodal two-point Delsarte relaxation for binary
length-sixteen codes with nonzero distances in `{2,6,8,10,14,16}` has exact
optimum

```text
max sum_i A_i = 18432/29,
(A_2,A_6,A_8) = (750,2002,12870)/29, uniquely.
```

Consequently, imposing all antipodal equalities cannot improve the existing
317-spinor-line cap by this relaxation and even-cardinality rounding alone.
A stronger bound needs constraints outside this real two-point program.
This certifies optimality of a relaxation; it does not construct a code or
prove that 317 spinor lines can occur.

This contribution was produced by Nick Petalas. Apache-2.0.

## New step and predecessor

DreamingOfClouds's [PR #2244](https://github.com/CrocSwap/integer-mult-bounds/pull/2244),
section 8.2 of `research/line-system-saturation/README.md`, supplies the
D16+ spinor distance model and the upper certificate `18432/29`, rounded to
634 words or 317 antipodal lines. That certificate is a cited predecessor,
not a result recounted or independently audited here. Its #2228, #2125,
#968 and lattice/decoder lineage retain their credit.

The new result is a matching feasible primal distribution for the full
antipodal program, together with uniqueness. The three-constraint gap identity
below gives a short self-contained optimality proof. The continuous optimum
and its optimizer distinguish this result from the predecessor's code upper
bound. The originally proposed improvement of that bound did not occur;
the delivered result closes the proposed antipodality-only strengthening.

## Program and proof

For a nonempty binary code C, let `A_i` be its average number of words at
distance i from a word of C. Thus `A_0=1` and `sum A_i=|C|`.
Antipodality gives `A_16=1` and `A_i=A_(16-i)`. Define

```text
K_k(i) = sum_j (-1)^j binom(i,j) binom(16-i,k-j),
L_k(A) = sum_(i=0)^16 A_i K_k(i).
```

The character identity gives

```text
L_k(A) = (1/|C|) sum_(wt u=k) (sum_(c in C) (-1)^(u.c))^2 >= 0.
```

The program imposes these seventeen inequalities, nonnegative real A_i,
the antipodal equalities, and zero A_i at forbidden distances. It imposes
no integrality or three-point conditions. Write
`x=A_2=A_14`, `y=A_6=A_10`, `z=A_8`; its objective is `N=2+2x+2y+z`.
Three of its inequalities are

```text
L_2 =   240 +  128x         -  8z >= 0,
L_6 = 16016         + 128y  - 56z >= 0,
L_8 = 25740 - 1716x - 180y  + 70z >= 0.
```

The exact affine identity

```text
18432/29 - N = (25 L_2 + L_6 + 2 L_8)/116
```

proves the upper bound. At `(x,y,z)=(750,2002,12870)/29`, all distance
coordinates are nonnegative. Its entire transform vector has only four
nonzero entries:

```text
L_0 = L_16 = 18432/29,
L_4 = L_12 = 931840/29.
```

All other L_k vanish. This proves feasibility and attains the bound.
All three multipliers in the gap identity are positive. Equality therefore
forces `L_2=L_6=L_8=0`. The coefficient matrix of these equations has
determinant `-1900544`, so their displayed solution is unique.

The predecessor's cap remains 317: an antipodal code has even cardinality,
so `|C| <= 2 floor((18432/29)/2) = 634`. In the stated roots-plus-spinors
family, adding the predecessor's 240 root lines still gives at most 557.
Neither cap is improved or claimed as newly proved code geometry here.
In particular, the primal optimizer is a feasible real distribution, not
an actual code's distribution: its total is not an integer.

## Verification and reproduction

The verifier uses only the Python 3.12 standard library and imports no
predecessor code. It checks the primal vector and all seventeen transforms,
the affine dual identity coefficient by coefficient, the positive dual
weights and the nonsingular active system. An independent coefficient
recurrence checks all 289 Krawtchouk entries against the binomial formula.
It enumerates all sixteen ordered pairs of a four-word antipodal code as
a normalization control. Five altered distributions must be rejected:
broken symmetry, a negative transform, missing antipode, forbidden distance
and a negative distance count. All guards remain active under optimization.

From the worktree root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/antipodal-spinor-lp-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/antipodal-spinor-lp-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/antipodal-spinor-lp-optimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/antipodal-spinor-lp-optimum --check-source-history
```

Any CPython 3.12 installation can replace this local path. Both registered
commands have a sixty-second timeout. Each run prints a generated receipt
bound to all five package files and ends with

```text
PASS_ANTIPODAL_SPINOR_LP_OPTIMUM optimum=18432/29 unique=1 transforms=17 controls=5 no_new_kappa
```

No receipt is hand-written or stored. `SOURCES.json` pins the predecessor
README and the historical task/selected context to the starting main commit.
The README is a declared input; the verifier itself is self-contained.

The originating card's historical `complex-local-word-ceiling/verify.py`
orientation command fails with `KeyError: 'complex_profile'` against the
changed selected schema. The current `scripts/research_selected_baseline.py`
passes its source-bound metadata checks at selected `60403/20000000`.
Neither orientation command is part of the new mathematical certificate.

## Limits and implementation bounds

The claim is the exact optimum of the explicitly stated finite real linear
program. It is not a maximum code-size theorem, a nonexistence proof for
317 spinor lines, or an obstruction to stronger integrality or higher-point
bounds. The complex-rank-shape-decoder card is changed to this geometric
side result. Native coefficient preparation, compensation, routing, frames,
restoration, precision and stock costs remain unknown. No supplier, selected
frontier or complete multiplication theorem changes. Independent human and
formal proof-kernel review are unclaimed. No Lean, Docker, native replay or
selected construction replay is run.

The code has no recursion, subprocesses, network, variable search bounds or
solver dependency. Vectors have seventeen entries; coefficient loops have
at most sixteen rounds; the determinant has six terms; receipt reads cover
five named files of at most 1 MiB each. Every function is below sixty lines.
Power of Ten rule 3 has a managed-runtime deviation: Python allocates exact
integers, fractions and lists during checking. The stated fixed domains bound
live state, and each receipt buffer is released before the next read. A
fixed-buffer implementation is the follow-up if this checker is ported to
a runtime forbidding allocation. Normal and optimized warning-strict commands
provide the Python diagnostics; repository-wide settings are unchanged.

## Open next questions

Can a three-point or integrality strengthening lower the 317-spinor-line cap?
First add one named triple-distance consistency constraint and test whether
it excludes the unique optimizer above. This targets information missing
from every inequality in the present program. No triple distribution or
integral code realization is supplied, and a larger search is not started.

## Overlap and source scope

Before the claim, live PRs, this account's recent work, current handoffs,
active Discussions and local reservations were checked. Distinctive main-tree
and merged-PR searches found the #2244 bound and #606's different full-shell
spinor circuits. The overlap helper reports its cached coverage separately;
sparse notes and unpublished work limit that search. No predecessor scientific
replay is used as the deliverable. The new primal/uniqueness proof is the
entire contribution.

The advance [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19145587)
records the original bound-improvement question and its bounded negative exit.
