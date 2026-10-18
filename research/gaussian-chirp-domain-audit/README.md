# Audit: the generated Gaussian chirp domain closes PR #371's caveat

**Research note and independent mathematical audit; no new kappa.** The
generated Gaussian construction supplies `alpha^-2 <= theta <= 1/4` to
`lem:chirped-gaussian`. Its integer windows and stated working precisions
`P=3p` and `P=34p` satisfy the audited arithmetic obligations throughout
that domain. The broader header left in `upstream/` is not the header used
by this construction.

This resolves the specific domain caveat in the body of
[PR #371](https://github.com/CrocSwap/integer-mult-bounds/pull/371) at
`988ef67986c313445936fc7103908b6163b9d47e`. That PR's separate final-grid
rounding defect remains genuine and its correction is **not** incorporated
by this audit. Passing this package does not certify the containing lemma,
the selected construction or the full multiplication theorem.

## Exact source and statement

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Assignment seed: **64**, adversarial mathematical audit.
The accepted certificate at this base is #626 with #543,
`kappa=51110230636731/31250000000000000`; it is unchanged.

The audited statement is the use of the no-sort domain by
`lem:chirped-gaussian`, specifically its block windows, amplification
ceilings and sufficient precision inequality

```text
P >= p + Gamma + ceil(log2(F L_A)) + 11.
```

The [source pins](SOURCES.json) identify the exact direct inputs, generated
manuscript digests and PR #371's source hashes. The base commit pins the
transitive generator dependencies. The source check executes the actual
`patched_files()` composition in memory; it writes nothing to `upstream/`
or existing certificates. It checks these links:

1. [`make_fast_gaussian_patch.resampling`](../../scripts/make_fast_gaussian_patch.py#L23-L33)
   replaces the original hypothesis `theta > p/alpha^4` by
   `alpha^-2 <= theta <= 1/4`.
2. The same function [inserts the note](../../scripts/make_fast_gaussian_patch.py#L157-L161)
   verbatim. The chirp lemma inherits that new header, including integer
   `p>=101`, integer `2<=alpha<sqrt(p)`, and `sigma=1+theta`.
3. The [assembly replacement](../../scripts/make_fast_gaussian_patch.py#L251-L263)
   establishes the upper and lower theta bounds eventually. This audit
   does not re-prove its prime-existence or asymptotic setup arguments.

The generator and unmodified upstream resampling file at PR #371's exact
head are byte-identical to these files at the audit base. Thus the domain
finding applies there too, rather than merely to a later repair. No pending
PR is treated as an accepted stronger multiplication bound.

## Concrete control: what the old header alone would permit

Take `p=101`, `alpha=2`, `s=2`, `t=19`. These satisfy the old upstream
header, including coprimality and `theta=17/2 > p/alpha^4=101/16`.
For the **new chirp E algorithm**, however,

```text
m = ceil(sqrt(101)/(2*2)) = 3,
L_B = 2m+2 = 8,
q_0 = 0,
q_1 = floor(19/2 + 1/2) = 10.
```

The first block contains outputs `ell=0,1`, but evaluates only local
correlation coordinates `0,...,7`. It misses `q_1=10`. The actual generated
header rejects this tuple because `theta>1/4`.

This is a counterexample to applying the *new window recipe under only the
old hypotheses*. It is not a counterexample to the original slower
no-sort theorem, nor to the generated construction's restricted claim.
It shows why source composition is mathematically significant.

## Uniform arithmetic argument

The [separate review](INDEPENDENT-REVIEW.md) gives the window-containment
proofs and the uniform precision argument. A rational common enclosure is

```text
pi/ln(2) < (22/7)/(56/81) = 891/196.
```

For completeness, `ln(2)>56/81` follows from the first two positive terms
of `ln(2)=2*sum_(k>=0) (1/3)^(2k+1)/(2k+1)`.
Also `22/7-pi = integral_0^1 x^4(1-x)^4/(1+x^2) dx > 0`: polynomial
division gives the integrand
`x^6-4x^5+5x^4-4x^2+4-4/(1+x^2)`.
These elementary analytic identities explain the enclosure; the finite
checker evaluates only its exact rational consequences.

With `theta<=1/4`, `alpha^2<p` and `p>100`, those consequences are

| Obligation | Exact sufficient bound |
|---|---|
| Forward amplification | `(891/196)*(121/400) < 7/5`, so `Gamma=ceil(7p/5)` suffices |
| Correction amplification | `(891/196)*(25/4) < 29`, so `Gamma=29p` suffices |
| Correction input scale | `(891/196)/4 < 57/50`, so `B=ceil(57 alpha^2/50)` suffices |
| Forward precision | `(53/20)p+12 < 3p` for every `p>=101` |
| Correction precision | `(1607/50)p+11 < 34p` for every `p>=101` |

The precision rows use `L_A<4p` for S', `L_A<=p` for E, and exact integer
ceiling-log bounds. For E, use the sharper `B<=1.14p+1` when deriving the
printed `32.14p+11` bound, rather than only `F<=2^(1.15p)`.

## Reproduce

From the repository root, using Python and its standard library (tested
with Python 3.14.7):

```sh
python3 -B research/gaussian-chirp-domain-audit/verify.py
```

Expected output:

```text
PASS_SCOPED_GAUSSIAN_CHIRP_DOMAIN_AUDIT
Exact parameter pairs: 21773
Exact correction windows: 968049
All 7 negative controls rejected; receipt matches
```

The deterministic [receipt](RECEIPT.json) records exact coverage, generated
source digests, minimum precision slacks and control outcomes. The command
recomputes its contents and rejects any mismatch. `--write` is available
only for deliberate regeneration after reviewing a change.

This is exhaustive finite validation within the following domains, not a
search for a stronger construction:

- Every `101<=p<=1088` and integer `2<=alpha<sqrt(p)`: 21,773 pairs.
  The worst theta-dependent amplification envelope is checked at `theta=1/4`.
- Every coprime `2<=s<=128`, `s<t<=5s/4`, and `1<=m<=9`; every starting
  residue and every output offset. Correction residues include negative
  periodic representatives; all forward residues are also checked. These
  are generic integer-window cases, independent of the parameter-pair
  loop; actual S' block sizes in that loop exceed 9. The written window
  proof covers arbitrary positive integer `m`.
- Seed 64 selected the task, sets the finite cutoffs, and rotates the
  correction residue order. The stopping rule is completion of those
  enumerations. The written arguments, not enumeration, address all sizes.

Seven controls remove each source-domain bound, remove its assembly
justification, underfund each stated precision budget, use the old-header
counterexample above, and shorten an in-domain E output window. The two
precision controls reject violations of the *sufficient certified budget*;
they do not prove that those smaller precisions necessarily fail numerically.

The separate review also preserves a second implementation with a different
formula for the exact correction-window ceiling. Run
`python3 -B research/gaussian-chirp-domain-audit/independent_budget_check.py`;
it prints `PASS_INDEPENDENT_GAUSSIAN_BUDGETS pairs=168093 controls=5` and
a JSON summary. Its wider arithmetic domain is `101<=p<=4096`; it does not
repeat the source composition or residue-window enumeration.

## Scope, attribution and handoff

The new evidence is a source-bound resolution of the domain concern, a
concrete window counterexample to the wrong source composition, written
uniform arithmetic arguments, and independent exact finite implementations.
This does not reopen a closed search or assert a new exponent.

Inherited obligations include the one-block internal error enclosure,
Gaussian tail bounds, transcendental approximation routines, packed
integer multiplication, periodic tape movement, Neumann evaluation, and
the selected suppliers' all-size and analytic interfaces. The tests
neither implement the Gaussian maps nor establish those obligations.
PR #371 remains unreviewed in the base ledger; this submission is scoped
evidence for its review, not a request to mark the entire PR verified.

Contributor: **Effy Elden (ineffyble)**, with substantial OpenAI Codex
assistance, including a separate AI source/arithmetic reviewer. No human
peer review or formal verification is claimed. Credit eumemic's PR #5
construction, icekylinx's shifted error enclosure, Artus Krohn-Grimberghe
and PR #371's disclosed GPT-6 Pro/Codex final-grid work, and David Harvey
and Joris van der Hoeven's analytic algorithms. The new package is under
the repository's Apache-2.0 license; predecessor notices remain intact.

The [sprint claim](CLAIM.md) records candidate selection, overlap checks,
timing and the final handoff. No existing source, selected certificate or
review-ledger disposition is changed by this contribution.
