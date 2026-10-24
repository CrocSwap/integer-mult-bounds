# Independent common-reference uniform-cap admission audit

Prepared for Brian (`JoyboyBrian`) with substantial OpenAI Codex assistance.
Apache-2.0.

This package audits one quantified implication of the retained raw Gaussian
construction: **one successful `Reference.for_cap` allocation supplies the
same reference accuracy required at every eligible capped raw block**, in
both narrow and broad directions. The proof independently derives cap-wide
gauge and conditioning domination, relative-weight entry accuracy, and an
explicit outward-tail margin. It does not construct another Gaussian compiler.

Canonical investigation:
[Discussion #4202](https://github.com/CrocSwap/integer-mult-bounds/discussions/4202#discussioncomment-19130764).
The source theorem and allocation belong to Jose Manuel's
[`RAW-GAUSSIAN-PROOF.md`](../rational-unitary-fft/RAW-GAUSSIAN-PROOF.md),
`gaussian_reference.py` and `raw_gaussian.py`, last changed at
`c9db4069d59bfad26a15fe000b91cc3a058684e5` and retained at the pinned base.
The following is an independent audit, not a claim that their implication was
previously absent.

## Domain and precise result

Let integers `0 < K < S`, `α >= 1`, a dyadic cap `B >= 1` with `2B <= S`,
a rational radius `R >= 1`, and target integer `t >= 1` be fixed. Set
`θ=K/S`, `ρ=1+θ`, `λ=1/ρ`, and `c*=1/(α²ρ)`. Use the source allocation

```
F* = 1 + α²θ(B²+B+1),        G* = α 2^ceil(8F*),
H* = 2 qbar(B,c*),           Q* = G*² H*,
e  = t + ceil(log2(8(R+1)Q*²)),   δ = 2^(-e),
w  = ceil(sqrt((e+5)/(3α²))),
A  = α²ρ²,
W  = max(ceil(A), ceil(sqrt(A(e+5)/3)), 2w+2),
b_e = e + 3 + ceil(log2(2 max(w,W)+1)).
```

The theorem is conditional on the **period-cut guards** `2w<S` and
`2W<S+K`. These are real admission conditions: increasing target precision
at fixed geometry may violate them. The reference is not promised to exist
for every otherwise valid input tuple.

For every original-period, original-constant-phase dyadic block of size
`n<=B`, the raw source's `Q_raw` satisfies `Q_raw<=Q*`, and its *same global*
reference satisfies

```
E_ref < (3/8) 2^(-e) <= 2^(-t) / (8(R+1)Q_raw²).
```

The stronger `3/8` slack is a convenient independent certificate for the
existing guard, not a new selected parameter or an optimized precision claim.
The reference object and its original global addresses remain fixed across
blocks; no window rerounding is permitted.

Two predecessor contracts are explicit. For all positive `c` and legal
half-shifts, the scalar conditioning certificate obeys

```
Qcap(n,c) = n exp(π/(4c)) <= qbar(n,c) <= (4/3) Qcap(n,c).
```

The interval producer encloses `exp(-π f)` for every rational `f>=0`, at
working precision `J>=16`, with width at most `512 J² 2^(-J)`. ToikY's
[independent scalar audit #4220](https://github.com/CrocSwap/integer-mult-bounds/pull/4220)
at `5cf23ba47a28b78a98eb0665177b5030e65c01b9` audits that distinct scalar
backend. The normalized matrix inverse estimate, its q-LDU proof, and the
complete raw circuit error budget remain predecessor dependencies. This
package proves the *uniform allocation implication*, not those whole theorems.

## 1. One cap dominates all original-cell gauges

In a legal block let `r=(n-1)/2`, and let `β` be the beta coordinate at its
center. Since the phase is constant and the center is between the endpoints,
`|β|<=1/2`. Every centered coordinate has magnitude at most `r<=B/2`.
With `d=β/ρ`, the narrow factors have absolute exponents at most
`α²θ r²`. The broad source factors have absolute exponents at most

```
1/(4α²ρ²) + (θ/α²)(r²+r),
(θ/α²)(r²+2r),
```

using `λ<=1` and `|d|<=1/2` directly in its two quadratic formulas. Each
quantity is at most `F*`, because `α>=1` and `r<=B/2`. Monotonicity of the
integer ceiling now gives `G_local<=G*`, including the exact broad `α^-1`
scale and its reciprocal through the source's factor `α` in `G_local`.

The narrow normalized parameter is `c=α²ρ`; the broad one is `c=c*`.
Both are at least `c*`; their shifts are `-β/ρ` and
`-(β/ρ)(1-θ)`, respectively, of magnitude at most `1/2`. Therefore

```
qbar(n,c) <= (4/3)n exp(π/(4c))
          <= (4/3)B exp(π/(4c*))
          <= (4/3)qbar(B,c*) < H*.
```

Also `qbar(n,c)>=n`, so `max(n,qbar(n,c))=qbar(n,c)`. Consequently
`Q_raw = G_local² max(n,qbar(n,c)) <= Q*`.
This comparison does **not** assume that rational interval upper certificates
are themselves monotone in their inputs. The factor two allows for the
stated `4/3` certificate inflation. An abstract certificate control checks
that silently dropping that allowance is not justified by this contract
alone; it is not a claimed counterexample to the actual Gaussian routine.

## 2. Positive shared weights and retained entry error

For `0<=f<=F`, let `L=ceil(8F)`, relative request `b>=1`,
`P=L+b+3`, and `J=2P+32`. Since `π<4` and Euler's number is less than four,
`exp(-πf)>=2^(-L)`. The interval width contract implies a width at most
`2^(-P)` (at `P>=4` the elementary inequality is immediate and decreases with
`P`). Flooring its lower endpoint to the `P` grid adds less than `2^(-P)`.
Thus the positive stored value has relative loss at most `2^(-b-2)` and is
strictly positive. The exact stored reciprocal has relative error at most
twice that loss. This is the source's one-sided relative producer; an
absolute coefficient approximation that can return zero is insufficient.

For reference weights, `F=α²/(4θ)` and `b=b_e+4`; write
`η=2^(-b_e-6)`. Both stored weights lie in `[(1-η)w_j,w_j]`, so their ratio
has relative error at most `η/(1-η)<=2η`. In one original phase cell, for
integer offset `h`, `β_j=β_i+θh`, and the exact normalized entry exponent is

```
(ρh+β_i)² - β_j² = (1+2θ)h²+2β_i h >= h²-|h| >= 0.
```

The ideal entry is therefore at most one. The weight ratio is at most
`exp(πα²|h|)<=2^Lratio`, where `Lratio=ceil(8α²w)` for retained `|h|<=w`.
The stored ratio is at most twice this. At kernel precision
`b_G=b_e+Lratio+4`, its amplified absolute error is at most `2^(-b_e)/8`.
Together the weight and kernel errors are bounded by

```
2η + 2^(Lratio+1-b_G) = (5/32)2^(-b_e) < 2^(-b_e).
```

Across an original cell or period cut, the retained source uses the absolute
producer instead; it does not borrow the within-cell ratio identity. Broad
entries use an absolute approximation divided by exact `α>=1`. Exact
unit diagonal and hole conventions contribute zero coefficient error.

## 3. Outward tails have a uniform strict margin

The source tail working precision is
`J=2(b_e+ceil(8A)+16)+32`. In particular `J>=2b_e+80` and `b_e>=8`.
Set `σ=512J²2^(-J)`. The function `J²2^(-J)` decreases here, and checking
`b_e=8`, then the ratio on incrementing `b_e`, proves

```
σ <= 2^(-b_e-23) <= δ 2^(-26).
```

For the narrow tail, its first exponent factor is `α²w(w+1)` and its
successive-step factor is `2α²(w+1)`. For the broad tail they are
`(W+1/2)²/A` and `2(W+1)/A`. The choices of `w,W` give, in both cases,
`3 first >= e+5` and `3 step >= 6`; both tail prefactors are at most two.
Since `π>3` and Euler's number exceeds two, the true numerator is at most
`δ/32` and the true ratio at most `1/64`. An interval upper endpoint is
at most its true value plus `σ`. Thus each **actual outward** tail is at most

```
2(δ/32+σ)/(1-1/64-σ)
<= δ · 2(1/32+2^(-26))/(63/64-2^(-26)) < δ/4.
```

This also proves the denominator checks positive, without an assumption
that the true denominator and the outward one coincide. Each retained row
or column has at most `2w+1` or `2W+1` rounded entries, whose total allowance
is at most `δ/8` by the choice of `b_e`. Hence both reported source errors
are strictly less than `3δ/8`.

For clarity about the comparison target, narrow row/column windings enumerate
integer offsets without repetition. Their discarded terms are bounded by
`exp(-πα²(h²-|h|))`; the geometric ratio gives the tail above, including
removed nonzero diagonal aliases. Broad selected lifts occupy distinct integer
target coordinates, with displacement lower bound `|d|-1/2`; this gives its
stated geometric tail in each induced norm. Period-cut admission guarantees
unique retained lifts. A nonwrapping block of length at most `S/2` has zero
retained lift whenever its entry is retained. The same tail argument bounds
omissions from its **unperiodized** raw matrix directly. A periodic global
comparison alone would not imply that local statement.

Combining the error bound with section 1 and the ceiling in `e` proves the
uniform caller inequality in the precise result. No finite list of blocks
is used in this quantified deduction.

## 4. Inverse consequence and remaining boundary

Assume the predecessor's ideal raw inverse bound `||A^-1||<=Q_raw` and
`||A_ref-A||<=E_ref` in a fixed submultiplicative induced norm. The admission
inequality implies `Q_raw E_ref<1/2`. Resolvent expansion therefore yields

```
||A_ref^-1-A^-1|| <= 2 Q_raw² E_ref.
```

This explains the squared inverse allowance in the actual caller. It is not
valid to charge only `E_ref` for the inverse. The remaining diagonal
coefficient, actual circuit, grid-rounding and physical delivery budgets are
outside this audit, as are core/halo carving, tensor callers, raw-H entrances,
selected κ and the complete multiplication theorem.

## Source-bound replay and limits

The checker executes the actual `Reference` implementation. It extracts the
unchanged conditioning prefix of `Gaussian.__init__` and the unchanged
`RawGaussian.__init__` prefix through the exact common-reference admission
check, stopping before compiler construction. Its independent arithmetic
reconstructs the allocation, proves the rational tail upper margins for the
fixtures, and compares the actual caller threshold. This extraction boundary
is explicit: **no raw circuit executes**.

Three geometries `(S,K,α,B,R,t)=(97,1,1,8,1,4)`, `(129,3,2,4,2,3)` and
`(257,2,1,8,3,5)` cover **160** legal narrow/broad block admissions through
size eight, including cell edges and middle positions. One actual shared
weight-ratio entry per geometry is independently compared with its directly
formed raw exponential enclosure. The interval producer is shared, not an
independent transcendental implementation; the inequalities above are the
independent audit. Five controls cover an underfunded reference, invalid
period cuts, underfunded positive-weight setup, abstract certificate inflation,
and scalar inverse sensitivity. The last two are explicit mathematical
controls rather than claimed source defects.

All live dependencies are pinned at base
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7. The complete
fresh overlap snapshot at 2026-10-22 18:50 UTC covered 506 open PRs, 3650
discussion records and 5860 local notes; the live #4202 scope was also checked.
The active tensor/raw-H work is excluded. ToikY/#4220's distinct normalized
scalar audit leaves this shared-reference raw implication for follow-up.
Coverage is not proof of novelty or independent scientific acceptance.

```
python3 scripts/research_package.py --package research/raw-gaussian-cap-audit --check-only
python3.12 scripts/research_package.py --package research/raw-gaussian-cap-audit
python3 -B scripts/check_research_commit.py --package research/raw-gaussian-cap-audit --check-source-history
```

The registered replay runs normal and optimized Python 3.12 using only the
standard library. Run the final preflight after committing. No full historical
suite, Lean, Docker or multiplication replay is claimed. Credit Jose Manuel's
allocation and raw compiler, Vlado's phase-cell/circuit lineage, Jeremy Kothe's
shifted identities, Mason Hale's intervals, and ToikY's scalar audit.

## Open next questions

Can the parent caller prove that its **original** reserved-strip/core/halo
carving passes a single `Reference.for_cap` description to every raw block,
with the same `(B,R,t)` and no rerounding? First bind actual carving records to
original phase cells and period cuts, then check cap/radius/target identity
before invoking this admission theorem. The open obligation is caller
composition and physical ownership, not more samples of the scalar allocator.
