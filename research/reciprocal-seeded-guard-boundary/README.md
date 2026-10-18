# The seeded reciprocal needs three uniform residual guards

**Scoped mathematical result; no new kappa.** The actual seeded two-guard
reciprocal fails at target precision 15. This closes the explicitly open
reachable-state question in [PR1638](https://github.com/CrocSwap/integer-mult-bounds/pull/1638),
without refuting its three-guard theorem. Together with that credited upper
bound, the examples below prove that three is the least nonnegative uniform
integer guard allowance for this particular **residual contract**.

## Fixed interface and quantifiers

For every real input `1 <= c < 2` and positive integer target `p`, define
`R_t(z) = floor(2^t z)/2^t`. Start at `x=5/8`. Perform one warm-up step at
`t=6`, then set `m=1`. While `m<p`, replace `m` by `min(2m,p)` and use
`t=m+g`, where `g` is one fixed nonnegative integer. Each step is exactly

```
c_t = R_t(c)
u   = R_t(c_t*x)
x   = R_t(x*(2-u)).
```

Products are exact before their displayed rounding. Preserve the incoming
iterate even if the new `t` is smaller than its stored precision. The contract
is `|1-cx| < 2^(-p-1)`. The lower examples also violate the non-strict version.
The result concerns this fixed seed, warm-up, capped schedule, rounding rule,
and simultaneous prefix/product precision. It does not optimize arbitrary
reciprocal algorithms or an absolute-error-only contract.

## Exact reachable failure with two guards

Take `c=127379/65536`, `p=15`, and `g=2`. The actual execution is:

| Target m | Working t | Input prefix c_t | Incoming x | Rounded u | Outgoing x |
| --- | --- | --- | --- | --- | --- |
| 1 | 6 | 31/16 | 5/8 | 77/64 | 31/64 |
| 2 | 4 | 31/16 | 31/64 | 15/16 | 1/2 |
| 4 | 6 | 31/16 | 1/2 | 31/32 | 33/64 |
| 8 | 10 | 995/512 | 33/64 | 513/512 | 263/512 |
| 15 | 17 | 127379/65536 | 263/512 | 65431/65536 | 67435/131072 |

Each entry follows by multiplying exact rationals and checking its floor-grid
inequalities. The final calculation is

```
1 - (127379/65536)*(67435/131072)
  = 131727/8589934592
  = 1/65536 + 655/8589934592 > 2^-16.
```

The preceding residuals are `245555/4194304`, `3693/131072`,
`-9203/4194304`, and `53755/33554432`. Each satisfies its respective stage
bound. Thus the final failure starts from a genuinely reached, admitted state,
not an arbitrary state that merely satisfies an invariant.

This is also an interval counterexample. Every

```
127379/65536 <= c < 26214/13487
```

has exactly the same execution and strictly excessive residual. Indeed, the
interval lies in `[254758/131072,254759/131072)`, which fixes every prefix
read in the table. The stored output is therefore constant. Its positive
residual exceeds `2^-16` exactly when `c < 26214/13487`. At that last rational
endpoint the residual equals the bound, so even the strict contract still
fails there; the displayed half-open interval avoids relying on equality.

At the dyadic witness, the absolute reciprocal error is only
`131727/16695820288 < 2^-16`. We therefore do **not** infer optimality for an
absolute-error-only guarantee. The retained root caller specifically consumes
a residual guarantee for its normalized reciprocal.

## Lower allowances and the credited upper bound

Actual executions also exclude the other lower integer allowances:

| g | c | p | Actual outputs after warm-up and successive stages | Final residual | Bound |
| --- | --- | --- | --- | --- | --- |
| 0 | 9/8 | 2 | 51/64, 3/4 | 5/32 | 1/8 |
| 1 | 39/32 | 3 | 25/32, 7/8, 7/8 | -17/256 | 1/16 |
| 2 | 127379/65536 | 15 | 31/64, 1/2, 33/64, 263/512, 67435/131072 | 131727/8589934592 | 1/65536 |

For completeness, the upper argument is PR1638's directed-rounding proof,
restated here with its credit and an unchanged source copy in `vendor/`.
Let `e=1-cx`, `delta=2^-t`, `h=c-c_t`, `a=c_t*x-u`, and
`b=x*(2-u)-x_plus`. Each of `h,a,b` lies in `[0,delta)`, and exact expansion gives

```
e_plus = e^2 - c*h*x^2 - c*x*a + c*b.
```

If `|e|<=1/2`, then `x>0`, `cx<=3/2`, and `cx^2<=9/4`. Consequently
`e^2-(15/4)delta < e_plus < e^2+2delta`. The seed has `|e|<=3/8`;
the six-bit warm-up gives `-15/256 < e_plus < 11/64`, hence `|e_plus|<1/4`.

Assume `|e|<=2^(-m-1)` and put `m'=min(2m,p)`, `t=m'+3`. Then
`e_plus < 2^(-2m-2)+2^(-m'-2) <= 2^(-m'-1)`.
The lower bound is strictly greater than
`-(15/32)2^-m' > -2^(-m'-1)`. This proves the invariant for every stage.
The finite increasing schedule ends at `p`; `p=1` uses the warm-up alone.
Thus three guards suffice for every real normalized input and positive target.

Combining this upper proof with the three **actual seeded** failures proves
the stated minimum. PR1638 already proves the upper bound and the different
arbitrary-invariant-state lower bound. Our contribution is the reachable lower
bound; credit for those previous results remains with @ToikY and predecessors.

## Reproduction and independent checking

Run from any checkout with Python 3.12 or later and the standard library:

```sh
python3 -I -B research/reciprocal-seeded-guard-boundary/verify.py
```

Expected marker: `PASS_SEEDED_GUARD_BOUNDARY witnesses=3 controls=7; no new kappa`.
The opt-in `VERIFY.json` also registers both this command and the package tests
for the repository's pinned Python 3.12 runner. Local validation uses stable
CPython 3.15.0 through the research wrapper. The registered 3.12 execution and
hosted CI are not claimed. `VALIDATION.json` records the exact local checks.
The replay writes no files. `CERTIFICATE.json` contains the exact integer
trace and rational conclusions. A direct integer-significand evaluator checks
the listed inputs. A separate rational certificate checker does not execute
the recurrence or call the evaluator: it verifies the floor inequalities for
every supplied row, its connections, and a schedule derived from powers of two.
It also proves that every prefix is constant on the failure interval.

Seven controls reject an omitted stage, wrong prefix, wrong rounded product,
wrong output, wrong seed, a false failure endpoint, and a wrong target.
`test_package.py` adds read-only relocation and four on-disk corruption tests;
three rehash the altered receipt to test semantics beyond source digests.
Three- and five-guard positive controls satisfy all stage bounds at each
counterexample input. This includes the first precision decrease after warm-up.
The proof above, rather than search coverage or expected receipts, establishes
the quantified result. The two checking models share the input certificate,
but not recurrence traversal or rounding implementation. Both come from this
Codex-assisted session; no independent human or proof-kernel review is claimed.

`search.py` preserves the discovery method. It probes left endpoints and
midpoints for targets up to 16 and stops on its first failure per allowance.
It does not certify all real inputs in earlier cells or minimum failing
precision. The replay checks the displayed counterexamples without searching.
The upper theorem is a written real-arithmetic induction, not finite enumeration.

## Scope, sources, and credit

Section09 is a downstream arithmetic corollary, not a dependency of the selected
multiplication construction. No selected record, supplier, upstream file, or
existing executable changes. We claim no kappa gain, measured speedup, physical
tape or precision admission, integration into the root/recovery caller, or
complete multiplication theorem. This counterexample requires no proposed
implementation or favorable cost model; it excludes a numerical substitution.

`SOURCES.json` pins the manuscript, selected record, source proof, and source
README. The base is `1f7a934975e5eacaf83511c9ac870263bf095e05`.
The exact PR1638 head is `394b90ee7fdaedd1f666a78a442127be3da17810`.
Credit **@ToikY / PR1638**, **Hanson Sun (@bbMisk) / PR1528**, the retained
OpenAI manuscript and its classical Brent reduction, and the repository's
maintainers. The vendored predecessor files remain unchanged. Their author and
AI disclosures remain intact. New work is Apache-2.0, prepared for
**Charles Bethin (@cbethin) with substantial OpenAI Codex assistance** in
derivation, implementation, verification, and writing.

## Open next questions

Does a modified final capped stage permit a two-guard schedule with a separately
proved residual contract? This result excludes the unchanged schedule only.
A useful first step is to derive a reachable interval invariant and account for
any extra stage or extra precision. More sampled successful cells do not prove it.

Can the three-guard proof be formalized and connected to the complete root and
recovery caller? Preserve the true-input residual, exact incoming precision,
and complete tape and cost obligations when making that connection.
