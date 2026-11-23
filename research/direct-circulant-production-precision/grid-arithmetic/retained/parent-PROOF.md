# A source-bound production precision theorem for direct circulant Fourier words

**Status: author derivation, awaiting independent cross-review.** This is a local numerical interface theorem. It assumes the retained rational compiler's explicit operator, fragment and layer estimates and the exact represented-input native Hadamard contract. It does not prove the global tape tariff, ownership, compiler closure, or the multiplication theorem. There is no new kappa.

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Primary source: CrocSwap/integer-mult-bounds#7849, Ali Romman's head
`3615fd982f2f4dc7172bef6f0dc9a4f77d5ab6dd`, package `research/direct-circulant-fourier`.
The retained full compiler is Jose Manuel's `research/rational-unitary-fft` at the canonical base.

## 1. Quantified result

Let there be `d >= 1` true cyclic axes of orders `2 <= r_i <= t_i = 2^ell_i`, with every `ell_i >= 1`. Put `L = sum ell_i`, and let `p >= 1` be the desired public precision parameter. The two signs use the same precision. Define the following integers:

```
E = ceil(1257*L/2) + 2154*d
A = 104*L + 438*d
J = 20000*(d+1)*(max(ell_i)+2)^6
C = 4*J*(d+1)^2 + d+1
P = 4*p + A + 2*E + bit_length(C).
```

Use `P` in the source's external `Grid`, hence `P+8` as the argument `bits` of `fourier_axis`. Retain the source's certified phase routine, unchanged exact rational root compiler and sixteen-H gate lowering. On represented inputs of maximum complex modulus at most one half, the computed transform differs from the exact original-coordinate Fourier mean, with identity on each local padded block, by strictly less than `2^(-4p)` in each coordinate.

This includes both private coefficient synthesis and external coefficient/data rounding. The theorem concerns the actual full padded array. It does not infer the theorem from a small diagnostic replay.

The source's original selector is

```
P_old = 4*p + 32768*(L+6*d)
        + 4*bit_length(J*(d+1)) + 64.
```

Our sufficient selector has linear part
`4*p + 1361*L + 4746*d + (L mod 2)`.
This comparison concerns a sufficient fractional precision, not the minimum precision required by the numerical algorithm, a measured tape speedup, or an exponent improvement.

The original selector is sufficient as a corollary. Put `q = J*(d+1)` and
`m = bit_length(q)`. Since `q >= d+1`,
`C = (d+1)*(4*q+1) <= 5*q^2 < 2^(2*m+3)`, so
`bit_length(C) <= 2*m+3`. The old selector exceeds the proposed selector by
at least `31407*L + 191862*d + 2*m + 61 - (L mod 2) > 0`.
The argument below also applies to every larger `P`, because all conditioning
and layout envelopes are uniform for `P >= 1` and every charged defect decreases
with `2^(-P)`.

### Named source contracts

| Contract used here | Exact source binding | Scope retained |
| --- | --- | --- |
| Fourier/CRT identity and public-grid recovery | PR7849 head above, `PROOF.md` and `COMPOSITE-OUTER.md` | Arbitrary supported composite cyclic orders, correct character and no-wrap hypotheses |
| Root adapter and emitted layout | PR7849 head above, `spectral.py`, `root_gate_plan.py`, `tensor_word.py` | Actual coefficient guard, leading-section admission, pivoted sixteen-H words and odometer |
| Full rational compiler estimates | Canonical base above, `research/rational-unitary-fft/FULL-PROOF.md`, especially (6), (11), (14), (15), and `full.allocation` | Compiler applicability, source-ordered fragments, prefix/inverse-prefix and exact-word defect bounds remain assumptions of this application |
| Certified rational unit phases | Canonical base above, `research/rational-unitary-fft/engine.py`, `Phases.phase` | Every returned phase is unit and lies within its certified target error; the oracle's all-size correctness is inherited |
| Exact native H action | PR7849's inherited represented-input native service | Exactness on sufficiently widened private grids; tariff, storage and private instruction cuts are outside this lemma |

`ORIGINS.json` authenticates the executable fixtures; `SOURCES.json` pins
the canonical compiler proof and provenance. This proof instantiates the named
contracts rather than treating their implementation assertions as independent
proofs of those contracts.

## 2. The actual Fourier coefficient producer

Set `h = bit_length(2*r)` for one axis. In the pinned code, `cap = 1`, `gap_scale = 2*r` and the internal first-column grid is

```
b = P + 28 + 4*h,   u = 2^(-b).
```

The exact-unit rational phase routine receives `b+4` bits and certifies complex phase error at most `u/16`. The lower square root of radius one is exactly one. The rounded circulant column differs from its ideal root column by at most `4*u` per entry (a deliberately weaker version of the direct phase-plus-rounding bound). Thus its operator error is at most `4*r*u`. Since `2^h > 2*r`,

```
4*r*u < 2^(-P-30)/r^3 <= 2^(-P-8).
```

The ideal root has real part at least `1/(2*r)`. The same inequality gives `4*r*u < 1/(4*r)`, so the actual stored column satisfies strict accretivity at the adapter's declared margin `mu = 1/(4*r)`. The exact Hermitian admission therefore accepts, independently of rounding cancellation. Identity padding has no error.

Every leading principal section `A_k` of the padded stored root inherits
`Re(A_k) > mu*I`. For any vector `x`, Cauchy–Schwarz gives
`||A_k*x||*||x|| >= Re(x* A_k x) >= mu*||x||^2`.
Thus `||inverse(A_k)||_2 <= 1/mu`. Converting to maximum component
row/column sums costs at most `sqrt(2*k) <= 2*t`. This proves the exact
adapter's uniform leading-section allowance `Q = 2*t/mu = 8*t*r <= 8*t^2`;
it does not infer that allowance merely from invertibility of the full root.

Every returned phase is exactly unit. Let `delta = u/16`. The rounded entry chirp has error at most `delta+u < 2*u`. The averaged Gauss scalar has error at most `delta`; multiplying by the correction phase and then the chirp gives error at most `3*delta`, because both exact and approximate averaged Gauss scalars have modulus at most one. Its final component rounding adds less than `u`. Hence the exit diagonal also has error less than `2*u`.

The ideal entry has unit modulus. The ideal exit has modulus `1/sqrt(r)` on the true block and one on the holes. Since `2*u < 1/(2*r)`, every stored entry and exit diagonal and its inverse has norm at most `2*t`.

The retained full compiler at target `P+8` supplies an exact stored gate word with operator defect at most `2^(-P-8)` against the stored rational root. Its radius argument is `2*t`; no data rounding is included in this exact-word endpoint estimate. Combining with first-column error gives a root-word defect at most `2^(-P-7)` against the ideal unitary root.

Write the exact stored axis word as `Khat Rhat Rhat Ehat`, and its ideal target as `K R R E`. The ideal factors have norm at most one. The stored root and diagonal factors have norm at most two. The four-term product difference is therefore bounded by

```
9*entry_exit_error + 6*root_error
 <= (9/256 + 6/128)*2^(-P)
 = (21/256)*2^(-P) < 2^(-P).
```

Here the common upper bound `entry_exit_error <= 2^(-P-8)` follows immediately from `b = P+28+4*h`. This proves a dimension-independent local exact-word endpoint error; the source's `t^O(1)` envelope is more conservative.

## 3. Explicit source compiler envelopes

The source adapter's component bounds obey `lambda <= 4*t` and `Q <= 8*t^2`. For the first bound, the stored root has spectral norm at most `1+4*r*u < 2`, and a component row/column sum is at most `sqrt(2*t)` times that norm. The second is the adapter's literal `2*t/mu = 8*t*r`.

Consequently `chi = lambda*Q <= 32*t^3`. For `ell >= 1`, induction gives `2^ell >= 2*ell`, so the source displacement allowance satisfies

```
r_star = 2*ell+8 <= 5*t.
```

Substitute these bounds into the full compiler's equations (6), (11), (14) and (15), as implemented by `full.allocation`:

```
B = 256*t^3*chi^12 <= 2^68*t^39
alpha = 8*r_star*t^2*chi <= 1280*t^6
K_G = 2*t+64*t^2*chi <= 2050*t^5
H_star <= (4102*t^5)*(9230*t^6) < 2^26*t^11
U+1 = lambda+lambda^2*Q+1 <= 133*t^4
2*Q <= 16*t^2.
```

Thus the fragment bound `H = max(H_star,U+1,2*Q)` is at most `2^26*t^11`. Since `max(1,lambda,Q) <= 8*t^2`, the source physical-cut bound is

```
K = 2*max(1,lambda,Q)*B*H <= 2^98*t^52.
```

The inequality `4102*9230 = 37,861,460 < 2^26` is exact. All the other comparisons use nonnegative monomials and `t >= 2`; they are universal inequalities, not extrapolations of sampled dimensions.

This also independently validates the source's looser `(64t)^40`, `(64t)^16` and `(64t)^64` bounds for completed approximate prefixes, fragments and physical prefixes respectively.

## 4. Literal sixteen-H lowering and routing

An original two-coordinate gate is the ratio of adjacent source prefixes, so the gate and its inverse have norm at most

```
L_gate = K^2 <= 2^196*t^104.
```

The largest-modulus pivot choice makes both shear ratios have modulus at most one. The two parameters supplied to each three-H identity are `-3` and `3+z` with `|z| <= 1`. Their moduli therefore lie between two and four. Every non-pivot diagonal and its inverse is bounded by 64. A raw H or its inverse is also bounded by 64. The middle pivot and its inverse are bounded by `2*L_gate`.

Fully expanding both `upper_six` words before joining neighboring diagonals gives 23 diagonal factors and 16 H factors. Exactly one diagonal is the pivot. Therefore every partial product and its inverse, including cuts after a joined diagonal, is bounded by

```
64^40 * (2*L_gate).
```

This uses a conservative count of 40 ordinary factors; the fully expanded count is 38. Simultaneous pair words are a direct sum, so their norm is the maximum of the pair bounds, with no factor for the number of pairs.

Completed Beneš switch rows are permutations. A partial switch and its inverse have norm at most four; all earlier completed rows contribute norm one. At a routed matching cut, combine that factor, the current pair-word prefix, and a source compiler prefix. Each lowered root prefix and inverse prefix is bounded by

```
4*K*64^40*(2*K^2) <= 2^537*t^156.
```

Across two roots and both external diagonals, every exact one-axis prefix and inverse prefix is therefore bounded by

```
(2*t)^2 * (2^537*t^156)^2 = 2^1076*t^314.
```

The axis programs may finish at different times. Exact tensor factors on distinct axes commute, so any global external prefix is the tensor product of one prefix for each axis. Sequential width classes and complete packs do not multiply the number of prefixes for an axis. To retain a conservative allowance for a partially completed tensor-H pack, permit one additional factor `2^d` at each end of an interval. This concerns cuts in the external H schedule; the literal native service's private arithmetic remains governed by its inherited exact represented-input contract.

The two-norm of a global interval is at most

```
2^(2154*d + 628*L).
```

For a `T = 2^L` coordinate array, a matrix's infinity operator norm is at most `sqrt(T)` times its spectral norm. Hence every external exact-word interval is Lipschitz with constant `2^E`, where

```
E = ceil(1257*L/2) + 2154*d.
```

## 5. Coefficient odometers and local data errors

Every single exact scalar factor of an axis's joined diagonal is bounded by the partial-word estimate without the preceding source prefix:

```
b_i = 2^437*t_i^104 >= 1.
```

This also bounds the entry and exit scalars and all routing scalars. Put `F = product b_i = 2^(437*d+104*L)` and external grid step `v = 2^(-P)`.

Each individual rounded complex factor differs by at most `v` and has modulus at most `2*b_i`. The difference of products, together with at most `d-1` rounded suffix multiplications, bounds the error in any computed coefficient by `2*d*2^d*F*v`. This estimate permits zero factors and uses no division by a prior table entry.

The odometer does not accumulate this error over the length of a tensor scan. At every write, suffix `k` is the rounded product of the current factors with indices at least `k`; a carry changes indices `0,...,j`, recomputes suffixes `j,...,1`, and leaves every higher suffix with its unchanged arguments. Induction on carries proves that each retained suffix is built from at most `d` factors and at most `d-1` multiplications, irrespective of how many records were already visited.

The final multiplication by a represented data value adds at most `v` absolute complex error. Since `2*d+1 <= (d+1)^2`, its local defect is bounded by

```
epsilon*(1 + ||z||_infinity),
epsilon = (d+1)^2 * 2^(-P+A),
A = 104*L + 438*d.
```

A native H is exact on represented words under the inherited service contract. Any charged return conversion with one component rounding is also covered by this local envelope. Widening its private exact grid to cover the known integer radius is a separate retained service premise, not an uncharged assumption of this proof.

## 6. Source-specific stage count

At width `ell`, the full compiler has at most

```
D(ell) = 1 + 2*ell*(2*ell+8)*(8*ell^2+32*ell+18)
       = 32*ell^4+256*ell^3+584*ell^2+288*ell+1
```

matching layers. `local_schedule` emits 17 diagonal/H entries for a lowered matching plus two directions of `2*ell-1` switches, each with three entries: at most `12*ell+11` external entries per matching. Count each entry's diagonal and optional exact H as **separate mathematical steps**, so a pre-H rounding error is propagated by the interval bound. There are at most two steps per entry, two root passes, at most `d` nonempty packs, and one entry and one exit diagonal. Therefore

```
J_actual <= 2 + 4*d*D(ell_max)*(12*ell_max+11)
         <= 20000*(d+1)*(ell_max+2)^6 = J.
```

The last inequality follows by coefficient comparison of polynomials with nonnegative coefficients. This bound counts the literal schedule's diagonals and H calls separately, including the no-H diagonal entries. H steps have zero local defect under the retained native contract; charging them the same envelope only increases the budget. This is not the sharper polylogarithmic time count used by the outer complexity proof.

## 7. Endpoint bias and closing the bootstrap

Section 2 gives local exact-word endpoint error below `2^(-P)`. Every ideal local endpoint has spectral norm at most one and every stored endpoint norm at most two. The tensor product difference is bounded by `d*2^(d-1)*2^(-P)` in spectral norm. On a maximum-norm half-disk input, the coordinate error is at most that quantity times `sqrt(T)/2`. Thus the exact stored tensor word has endpoint synthesis bias at most

```
beta = (d+1)*2^(-P+E).
```

For external execution use the retained bootstrap theorem with `M = R = 2^E`, local defect `epsilon` from Section 5, and at most `J` stages. Its budget and total raw error are bounded by

```
J*M*epsilon = J*(d+1)^2*2^(-P+A+E),

J*M*epsilon*(2+2*R) + beta
 <= [4*J*(d+1)^2 + d+1]*2^(-P+A+2*E)
 = C*2^(-P+A+2*E).
```

For the proposed `P`, the last expression is strictly below `2^(-4p)` because `C < 2^bit_length(C)`. The bootstrap spend is strictly below `2^(-4p-E)/4 <= 1/4`, since `4*J*(d+1)^2 < C`. In particular it is below one half, so the bootstrap is valid without circularly assuming a bound on the computed state.

Conjugating the word and its input gives the opposite sign with identical norms and errors. No symmetry of the component tie-breaking rule is needed.

## 8. Exact product recovery and limits

If the remaining source hypotheses hold — pairwise coprime true sides, true volume `S <= B`, no cyclic wrap, radix digit scale `4B`, `p = 6*log2(B)`, `B >= 32`, correct CRT character, and the public toward-zero conversions — the proved raw bound is exactly the input to the source's public-grid recovery theorem. Its final integer error is at most `144/B^2 < 1/2`. This corollary uses the source recovery theorem and exact native contracts; it is not an independent complete multiplier proof.

All five canonical assumptions retain their selected status. This package provides a source-specific numerical lemma and a smaller sufficient fractional-grid selector. It does not change selected source files, admit pending suppliers, assert a practical crossover, or claim proof-kernel verification.

## Open next questions

1. Independently cross-review the literal source-to-constant bindings and the odometer induction. A wrong stage or omitted factor invalidates this application even if the scalar bootstrap arithmetic passes.
2. Join the improved selector to a source-specific all-size private-grid/owned-arena theorem. The external error bound alone is not the literal tape storage proof.
3. Tighten or formally certify the inherited full compiler's source physical-cut estimates. This contribution uses those exact estimates rather than re-proving the full compiler.

## Credit

Ali Romman supplied the direct circulant construction, its all-moduli Fourier/CRT and grid interfaces, coefficient generator and original precision selector. Jose Manuel (`jmbarrancoml`) supplied the rational unitary/full compiler and polynomial physical-cut estimates. Vlado Vojdanovski supplied the displacement and tensor matching compiler; Chafik Boukhalfa supplied the certified phase routine. Cinna Davis and the credited mixed-rank/native contributors supplied the inherited supplier and recovery chain. Prepared for Jerry Chen / `@CubeJerry` with substantial OpenAI assistance. Separate model-assisted review, when recorded, is not human or proof-kernel acceptance.
