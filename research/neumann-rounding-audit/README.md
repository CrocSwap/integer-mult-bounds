# Rounded Neumann evaluation: a sharp accumulation boundary and a stable replacement

**Adversarial mathematical audit / conditional precision refinement; no new κ.**
The retained inverse evaluation sums separately rounded powers. Its quadratic
error allowance cannot in general be replaced by a linear allowance under the
stated approximation contract. An exact two-coordinate family demonstrates
this even for a positive linear operator and an odd, zero-preserving oracle.
A fixed-source Horner evaluation instead has error **less than p grid units**,
keeps every intermediate in the disk grid, and uses the same **k−1** oracle
calls. This is a written all-size argument with finite exact corroboration;
it is not a defect in the existing quadratic bound.

No claim is made that the adversarial oracle is the actual Gaussian routine.
The replacement is implemented at its abstract oracle boundary. The Gaussian
analytic estimates, the rounded chirped-correlation implementation (including
PR371's separate rounding issue), and physical integration remain inherited
obligations. No selected supplier, source, precision charge or exponent changes.

## Exact object and source boundary

Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
The selected record at this base gives
`κ = 836330098538459/500000000000000000 = 0.001672660197076918`,
reviewed in `docs/research/community-batch1099-review.md`; its cold replay is
`make frontier1094-verify`. That review retains the precision/analytic
interfaces audited here. This package does not perform that cold replay.

The three live source inputs, pinned by Git blob and SHA256 in
[SOURCES.json](SOURCES.json), are:

- `upstream/build/sections/07-resampling.tex`: disk-grid format, possibly
  nonlinear approximation contract, and the rounded power-sum evaluator.
- `scripts/make_fast_gaussian_patch.py`: the retained replacement uses
  `||E|| < 0.42`, local error `< (p/3)2^-p`, `1 <= k <= p`, and
  `||E^k|| <= 2^-p`, preserving the old `3p²/4` inverse error bound.
- `notes/fast-gaussian-resampling.tex`: the exact correction-power estimate
  and the assumed rounded-E interface. No transcendental routine is imported.

The protected invariant is that every oracle call receives a valid disk-grid
input, every error and tail term is charged, and call counts refer to the
emitted evaluation. Agreement between two programs alone does not establish
this invariant; the proof, direct rational inverse and adverse fixtures check
separate parts of it.

## 1. Conditional Horner theorem

Let `p > 100` be an integer, `h = 2^-p`, and use the maximum complex-coordinate
norm. Let `E : C^s -> C^s` be linear with `||E|| <= q = 21/50`. Assume
`T : D_p^s -> D_p^s` satisfies `||T(z)-Ez|| < η = (p/3)h` for **every**
disk-grid input; T need not be linear, homogeneous, continuous or odd.
Choose an integer `1 <= k <= p` with `||E^k|| <= h`.

For input `u` in the disk grid, round both components of `u/2` toward zero
once, obtaining `v`. Keep this v unchanged and evaluate:

```text
y = v
repeat k-1 times:
    z = T(y)
    y = v - z                 # exact subtraction of grid numerators
return y
```

Then every `y` and `z` belongs to `D_p^s`, and

```text
||y - (I+E)^(-1)u/2||
    < ((p/3 + 3/2)/(1-q)) h
    = (50p/87 + 75/29) h
    < p h.
```

**Disk proof.** Componentwise inward halving gives `||v|| <= 1/2` and
`ρ = ||v-u/2|| <= h/sqrt(2) < h`. Given `||y|| <= 1`, the next state has
norm at most `1/2 + q + η < 1`. The last inequality holds for p=101 by
exact rational comparison, and `p 2^-p` decreases thereafter. Subtraction
is exact on the grid, so no further rounding or projection is needed.
This induction also establishes that each invocation is within T's domain.

**Error proof.** Define `x_0=u/2` and `x_{j+1}=u/2-E x_j`. Then
`x_{k-1} = (1/2) sum_{j=0}^{k-1} (-E)^j u`. If
`d_j=||y_j-x_j||`, then `d_0=ρ` and
`d_{j+1} <= ρ + q d_j + η`, with the oracle-error inequality strict.
Consequently

```text
d_(k-1) <= ρ sum_(j=0)^(k-1) q^j + η sum_(j=0)^(k-2) q^j
         < (h+η)/(1-q).
```

For k=1 the empty η sum is zero and the same strict upper bound holds.
The omitted exact tail is at most
`||E^k|| ||u|| / (2(1-q)) <= h/(2(1-q))`.
Adding these two terms proves the displayed bound. Its last inequality is
equivalent to `p > 225/37`, already implied by p>100. This proof requires
neither a relative error promise nor cancellation among rounding errors.

Conditionally composing this replacement with the retained contraction D'
(error `<4h`) and exact selector C gives B0 error `<(p+4)h`. The retained
S' allowance is `<16ph`, so both one-dimensional maps may use the common
allowance `<16ph`, and the linewise tensor composition `<16dph`. These are
conditional error allowances, not an implementation/adoption claim or a
change to the selected outer assembly.

## 2. The old evaluation genuinely permits quadratic accumulation

For every integer p>100 put `a=floor((p-1)/9)` and let

```text
E = (1/4) [[0,1],[1,0]].
```

For a complex grid component `h(n+i m)`, define

```text
R(h(n+i m)) = h(trunc(n/4) + 3a sign(n) + i trunc(m/4)),
T(z0,z1) = (R(z1), R(z0)),                  sign(0)=0.
```

Truncation is toward zero. E has nonnegative entries and norm 1/4;
T is deterministic, odd and zero-preserving. Its real component error is
at most `3ah`, and its imaginary component error is less than h. Therefore
its local error is less than `sqrt(9a²+1)h < (p/3)h`: use `p >= 9a+1`
and `a >= 1`. It maps the entire disk grid into itself since
`||T(z)|| < 1/4 + (p/3)h < 1`. It also satisfies the retained bound
`||T(z)|| < 0.42||z|| + (p/3)h`.

Take `u=h(8a,-8a)` and `v=u/2=h(4a,-4a)`. All coordinates are real here.
Since `T(v)=-v` and T is odd, the old rounded powers satisfy
`v_j=(-1)^j v`. Their alternating sum is **k v**, whereas the exact answer
is `(I+E)^(-1)u/2=(4/3)v`. Thus, for every
`ceil(p/2) <= k <= p`,

```text
||E^k|| = 4^-k <= h,
old error = 4a(k-4/3)h >= (2/15)p²h.
```

Indeed `a >= p/10` for p>=101 and `k-4/3 >= p/3`. The input, rounded
powers, partial sums and final output all remain in the disk: in particular
`4ak <= 4p²/9 < 2^p` for p>=101. The old error stays below its published
`3p²h/4` allowance. This is a counterexample to a **stronger hypothetical
linear allowance for the old evaluator**, not to the manuscript's bound.
It is also not an impossibility theorem for actual Gaussian rounding or for
other inverse algorithms. The fixed-source recurrence above is an escape.

At p=128, a=14 and k=64, both evaluators make exactly 63 calls:

| Quantity | Value in units of h |
|---|---:|
| First coordinate of u | 112 |
| Exact inverse output | 224/3 |
| Old power-sum output | 3584 |
| Old absolute error | 10528/3 |
| Horner output | 130 |
| Horner absolute error | 166/3 |
| Proved Horner allowance | 6625/87 < 128 |

## 3. The fixed contraction margin matters

The condition `q<1/2` alone does not justify the new disk induction at a
fixed precision. A control uses p=101, `q=1/2-h`, scalar `E=-q`, input
u=1 and, on real inputs,
`T(x)=trunc_grid(-q x)-3h sign(x)`. The complex extension truncates both
components and adds the real sign correction. Its error is less than
`sqrt(17)h < (p/3)h`, and it maps the disk grid to itself. Also `q^p<h`.
Nevertheless, the Horner state exits the unit disk at update 99, reaching
`1+h`. This is an exact witness to the weakened-premise failure. The
published fixed margin q=0.42 excludes it.

## 4. Complete wrapper accounting

Both evaluators use the same k terms and **k−1** complete E calls, with
all internal work of each E call inherited. Horner additionally pays for:

- 2s component halvings/inward truncations to prepare the permanent v;
- 2s(k−1) exact component subtractions, reading v and the returned E value
  and writing the next y on every iteration;
- all initial/final scans, head returns, consumed-buffer cleanup and loop
  control. These cost O(ksp) bit operations on a fixed number of tapes;
  subtraction has O(p)-bit operands, including one temporary sign/carry bit.

Retain v on one tape, current y on another and E's result/next y on a third,
reusing the caller's fixed stream buffers; E retains its own stated workspace.
Returning stream heads and clearing old buffers costs a constant number of
full scans per call, included above. No old sum is fed to the oracle, no
random access is assumed, and there is no new growing tape count. The audit
program deliberately retains traces for testing; those traces are not part
of this fixed-tape execution or its memory claim.

Writing `C_E` for one full E cost, the invoice is
`C_H(k) = (k−1) C_E + O(ksp+p+log k)` for k>=1, including preparation and
output. Under the retained `C_E=O((t+p)p^(1+δ))` and s<t, it is
`O(k(t+p)p^(1+δ))`, the existing asymptotic cost. This is not a benchmark
or a speedup claim. It removes an error-accumulation factor, not E calls.

## Reproduce and finite scope

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 scripts/research_package.py --package research/neumann-rounding-audit
```

Expected: `PASS_NEUMANN_ROUNDING_AUDIT fixtures=648 family=326 controls=6`,
passing focused tests, and `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`.
For a direct read-only replay on Python 3.12 or 3.14:

```sh
python3 -I -O -B research/neumann-rounding-audit/verify.py
```

[RESULT.json](RESULT.json) records the deterministic evidence. Nine rational
or Gaussian-rational matrices of dimensions 1–3, p in {101,128,257}, four
input families, k in {1,2,p}, and two oracle modes give 648 cases. Every
state is compared between integer arithmetic and a separate Fraction/real
block-matrix implementation. Dense rational elimination of `(I+E)y=u/2`
supplies an independent final-answer check. Exact squared-modulus tests
include both real and imaginary components; no floating-point acceptance
or imported mathematical verifier is used.

The adverse family covers every p=101..260 plus {511,512,1024}, each at
k=ceil(p/2) and k=p: 326 complete evaluations of each method. Controls
reject wrong sign, missing normalization, missing tail premise, overwriting
v, weakening the disk margin, and a linear claim for the original evaluator.
Package tests exercise source/receipt corruption, invalid inputs and read-only
relocation. Finite execution corroborates the written proofs; it is not a
formal proof or a search over all approximation routines.

## Scope selection and overlap

OS seed **68**, adversarial-audit track, with `68 mod 3 = 2` selecting the
third of three candidates: rounded-block packing (already PR1243), exact
correction-power endpoint potential (already PR902), and rounded Neumann
error placement. The `uniform-transfer-audit` card is refined to this precise
precision implication. The initial complete overlap snapshot covered 874
open PRs and 134 discussion records. A last-claims check preceded the
[claim in discussion 1409](https://github.com/CrocSwap/integer-mult-bounds/discussions/1409).
No pinned sprint issue existed. Search coverage and fresh submission checks
are recorded in [TASK.json](TASK.json); no search proves novelty.

The stopping rule is completion of the two written arguments, the specified
finite domain and semantic controls, within a 60-minute session with 15
minutes reserved for verification/handoff. This does not reopen PR902's
exact-decay analysis or PR1243's packing search.

## Open next questions

1. Can the fixed-source evaluator be wired to a source-bound implementation
   of the corrected Gaussian E routine? This would test the actual consumer
   and allow adoption of the linear error allowance. First resolve or adopt
   the block-rounding repair from PR371, then replay one complete line while
   auditing the ordered scans. The missing integrated Gaussian implementation
   and retained analytic guarantees are the blockers.
2. Does the actual Gaussian rounding routine satisfy an additional relative
   error property that rules out the oscillating family for the original
   power-sum evaluation? First derive its local error at small alternating
   inputs. Its full error structure, beyond the present absolute contract,
   is required; the counterexample does not settle that more restricted case.

## Credit and limitations

Credit eumemic's PR5 (`d3d370c34937503bd3fa63c83d505a05e8e50893`), icekylinx's
retained source/interface work, and the Harvey–van der Hoeven resampling
lineage. Artus Krohn-Grimberghe's PR371
(`988ef67986c313445936fc7103908b6163b9d47e`) identifies the distinct final-grid
rounding issue. Effy Elden's PR684
(`14dd937d9e2d3e51092c0c35a8c2c9cdf8ba81f4`) audits the generated domain/windows;
Alan Grillo's PR902 (`e17fd726b23ff009518c2fc7fa0c423e3c25a46d`) improves the
exact-power endpoint potential and distinguishes residual from inverse-tail
error. Hanson's PR1243 (`c8d2d7f685b9fded81212433970de29fe134f197`) audits
inner packing. None of these pending implementations is imported. Ordinary
Horner evaluation and contractive fixed-point error analysis are not claimed
as new mathematical methods.

Prepared by Hanson Sun (@bbMisk) with substantial OpenAI Codex assistance in
mathematics, code, verification and writing. Apache-2.0; predecessor sources
and notices are unchanged. No independent human review, Lean proof, complete
supplier replay, physical tape implementation, hosted-CI result or unconditional
multiplication theorem is claimed.
