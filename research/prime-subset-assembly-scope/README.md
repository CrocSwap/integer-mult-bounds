# The historical prime-subset ceiling depends on the assembly

**Research consolidation; no new kappa.** The archived common-subset
prime-power screen excludes `kappa >= 2^-26` using the historical conversion
`kappa < a/5`. That exclusion cannot be transferred unchanged to the later
balanced conversion `kappa < a/(1+a)`.

Keeping the same family, loss ledger and optimistic side-cost floor, this
package proves the transferred necessary ceiling

```text
kappa < A/(1+A) < 7829/200000000000 = 0.000000039145 < 2^-24.
```

Here `A` is the maximum of the historical optimistic bit-saving envelope,
not an achieved bit saving. The transferred envelope is above both `2^-25`
and `2^-26`; those targets are **not excluded by this envelope**. Other
constraints may still exclude them. There is no supplied circuit or paid
bridge, and no claim that either target is attainable.

The historical note is correctly scoped to its old assembly. This resolves
the difference between two assembly-dependent exclusions; it reports no
counterexample to that note or to the selected construction.

## Reproduce

From the repository root, with Python 3.11+ and the standard library:

```sh
python -I -S -B research/prime-subset-assembly-scope/verify.py
```

Expected final line:

```text
PASS_PRIME_SUBSET_ASSEMBLY_SCOPE_NO_NEW_KAPPA cases=626 controls=8
```

The command checks 12 source/input SHA-256 and Git-blob pins before doing
arithmetic, reconstructs every archived finite row, compares the exact
result with [RESULT.json](RESULT.json), and exercises eight rejection
controls. It imports no predecessor code, needs no Git executable or network
at runtime, writes nothing by default, and also works under `-O`.

`--output /path/to/new-receipt.json` writes the calculated receipt to a new
file only. Existing files are never overwritten. This explicit generation
mode does not compare against the committed receipt. Additional tests run
with `python -I -S -B research/prime-subset-assembly-scope/test_verify.py`.

## Fixed family and exact calculation

For a prime power `q >= 2`, set

```text
k = 2q-1, j = q-1, n = C(h,k), r = C(h,j), M = C(k,j).
W = 2n^3 + 2n^2(S+r), Delta = n^3 - 6n^2*r*h, m = h^3.
```

The inherited construction keeps the incidence center, rational indicator
lines, shared three-stage compiler, and every common-subset partial output
in a cancellation-free sum DAG. The source proof gives `S >= 2Mn` when
`Delta > 0`. In its `c+u` notation, `u=Mn` counts outputs and `c>=u` counts
addition nodes. The archived scope string's `c+q` means this same `c+u`
ledger; the field-size parameter is not the number of output roles.

Substituting that optimistic floor gives

```text
eta(q,h) = (n-6rh) / (2h^3(n+2Mn+r)),
a_actual <= -log(1-eta(q,h))/log(h^3)
          < A(q,h) = eta(q,h)/((1-eta(q,h))*log(h^3)).
```

Nonpositive deficits are discarded. No omitted frame, restoration or
recursive work is assumed free in a new construction: these are the
unchanged historical ledger and its optimistic relaxation, not an emitted
implementation.

The checker generates prime powers by sieving primes and taking powers. It
checks all **626** pairs with `2q-1 <= h < 65`, including **301** positive
deficits, against the archived exact rows. It reconstructs the archived
24-term logarithm rationals for comparison, then independently encloses
every `A(q,h)` using the positive series

```text
log(x) = sum(z^i/i, i=1..N) + remainder, z=1-1/x,
0 <= remainder <= z^(N+1)/((N+1)(1-z)), 1 <= x <= 2.
```

Binary range reduction and `N=96` give rational bounds with no floating-point
decisions. This differs from the historical atanh expansion. Exact intervals
separate the unique finite maximum `(q,h)=(3,29)` from every other case.
At this pair, `n=118755`, `r=406`, `S_floor=2375100` and
`eta=237/599335286`.

| Same optimistic family envelope | Approximate necessary upper bound |
| --- | ---: |
| Bit envelope `A` | `3.91449860718828694e-8` |
| Historical conversion `A/5` | `7.82899721437657388e-9` |
| Balanced conversion `A/(1+A)` | `3.91449845395529948e-8` |

The receipt contains exact outward rational enclosures. Its digest of all
301 per-case enclosures is a compact reproducibility aid; the checker
actually recomputes and compares every one of the 626 archived rows.

## The tail must also change

Simply removing `/5` from the old finite maximum leaves a proof gap. The
archived generic dimension bound at `h=65` is approximately `7.26919538e-8`,
which is itself above `2^-24` before the old conversion. The checker proves
this comparison with both sides of its logarithm enclosure.

The family-specific side floor supplies the missing tail. For all prime
powers `q>=2`, `M=C(2q-1,q-1)>=3`. Therefore

```text
0 < eta(q,h) < 1/(14h^3),
A(q,h) < 1/((14h^3-1)*log(h^3)).
```

Both positive factors in the denominator increase with `h`. At `h=65`
the bound is less than `2.076911615877643e-8`, strictly below the finite
winner's lower enclosure. All `h>=65` are excluded from maximizing `A`.
Every `q>=33` requires `h>=2q-1>=65`, so this includes the remaining prime
powers. This analytical tail plus the finite enumeration proves the all-size
envelope within the stated family; finite enumeration alone would not.

## What the balanced comparison establishes

The balanced interfaces require both `kappa < epsilon*a` (or a stricter
backed-off version) and `kappa < 1-epsilon`. Their maximum possible common
margin is `a/(1+a)`, obtained by balancing the two expressions. The function
is increasing, so **if** this family supplies an effective bit saving
`a <= A` to an admitted balanced assembly, `kappa < A/(1+A)` follows.

The current T37 lineage retains that balanced outer engine; its six-step
recipe and other supplier costs can only further restrict this necessary
comparison. We do not insert the archived construction into that engine.
In particular, `balanced_shared.py` requires a validated paid bridge and
an actual uniform supplier. This package provides neither.

A rational diagnostic demonstrates the limited non-exclusion claim. At
`(3,29)`, set `a=3/10^8`, backoff `h_backoff=10^-12`,
`q_eff=a*(1-2*h_backoff)`, and
`epsilon=(1-h_backoff)/(1+q_eff)`. The verifier proves that this `a` is
below the **exact ideal relaxed rate**, using a lower logarithm enclosure,
and that both balanced margins strictly exceed `kappa=2^-25`. The old
`a/5` margin does not. These are two reduced inequalities, not 47-constraint
assembly validation, physical admission, or a multiplication witness.

## Provenance, review and limits

Exact repository base: `407d52ff15b2217b6e22bce44728b4c3907b6515`.
[SOURCES.json](SOURCES.json) pins the historical certificate, its five
listed sources, and the cited family/assembly arguments and interfaces.
The source files are read as evidence and never executed. The selected
conditional result at this base is `1661960547713947/10^18` from T37/#942;
it is context only and is not replayed here. `upstream/`, the selected
frontier, and every existing repository file are unchanged.

The stopping rule is completion of those 626 cases, exact interval separation,
and the analytical tail. This is not a new search for circuits or a reopening
of a closed search with more computation. The changed hypothesis is solely
the conversion from bit saving to multiplication saving. Higher-rank frames,
different output representations, side circuits with cancellation, changed
stage geometry or ledgers, and different assembly recipes are outside the
negative result. All-size/compiler, realization, hosting, precision/tape,
analytic transfer and actual bridge-admission obligations remain inherited.
The written argument and exact finite checks are not a formal proof of the
full multiplication theorem.

Credit Douglas R. Colkitt and the contributors to the original prime-subset
and core-limit notes; the balanced lineage credits Zhihao Chen, RaD/hipotures,
icekylinx and eumemic in its retained source notices. Jonathan Capalbo's
T37 package supplies the current lineage pointer, not a dependency of a new
construction. Existing #927 historical ranking, #930 PR210 reconciliation,
and #970 bit-compression provenance work address different objects and are
not consumed by this verifier.

Contribution by **woklerx**, with substantial **OpenAI Codex assistance** in
the analysis, implementation and scoped second-agent review. See
[REVIEW.md](REVIEW.md), [CLAIM.md](CLAIM.md) and the repository Apache-2.0
license. The second-agent review is not independent human peer review.
