# The optimal refined-recovery fiber at every depth t ≥ 27

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

## Setting

Objects are those of Nick Petalas's
[PR6660](https://github.com/CrocSwap/integer-mult-bounds/pull/6660)
(head `b6de532e`), built on CubeJerry's PR6327 and the matrix M of #5444.
Frames U_j ∈ G = {U ∈ GL_112(ℤ) : MᵀU = Mᵀ}. Let W_j = (U_(j−1)⋯U_1)^(−1),
let φ_j : Q = F2^8/C → F2^112 be the map induced by W_j M mod 2, and let
ρ = dim(N_1+⋯+N_t) be the rank of the frame sequence. By PR6660 (c), ρ ≤ 104.

Write OPT(t) = min_U max_y |fiber(y)|. PR6660 proves OPT(t) = F^t for t ≤ 26.

## Theorem

For every t ≥ 27,

    13^(8t) / 2^104  ≤  OPT(t)  ≤  (1 + θ) · 13^(8t) / 2^104,
    θ = 5.4537·10⁻⁶ (the exact rational is computed by verify.py).

Consequently, the minimum packed tag at depth t is

    ⌈log₂ OPT(t)⌉ = ⌈8t·log₂13⌉ − 104

for every t ≥ 27 except possibly a sparse set of depths. At those depths
{8t·log₂13} lies within log₂(1+θ) < 7.9·10⁻⁶ of 1. The first such depth is
t = 584,977. The values are 696, 725, 755, 785, … bits. For 27 ≤ t ≤ 400 this
is exactly 100 bits below the identity-frame tag ⌈log₂ A_t⌉ of PR6327.

In words: past depth 26, mode-preserving frames save exactly the 104 parity bits
of the dimension cap against the trivial count 13^(8t). Up to a 5.5·10⁻⁶ relative
factor, they save nothing more.

## 1. Lower bound: the main Fourier term (all frames)

PR6660 §5 gives the zero fiber as Σ over (u_j) with Σ_j W_j M u_j ≡ 0 of
Π_j w(u_j), where w(u) = 7^(8−wt u) 6^(wt u). Write each φ_j through
χ ∈ F2^r on an ambient F2^r containing all images. For each χ, χ∘φ_j is the
character u ↦ (−1)^(h_j(χ)·u), with h_j(χ) ∈ C^⊥ = C. Poisson summation gives

    |fiber(0)| = 2^(−r) Σ_{χ ∈ F2^r} Π_j ŵ(h_j(χ)),   ŵ(h) = Σ_u w(u)(−1)^(h·u) = 13^(8 − wt h).

Every term is positive. The χ with all h_j(χ) = 0 are those orthogonal to the
span N_1+⋯+N_t, and there are 2^(r−ρ) of them, each contributing 13^(8t). Hence

    |fiber(0)| = 2^(−ρ) 13^(8t) (1 + ε₀),
    ε₀ = 2^(ρ−r) Σ_{χ: some h_j(χ) ≠ 0} Π_j 13^(−wt h_j(χ)) ≥ 0.

Since
ρ ≤ 104, every frame sequence has max_y |fiber(y)| ≥ |fiber(0)| ≥ 13^(8t)/2^104.

This is the statement that the zero target gets at least the average share of
all 13^(8t) chains among the 2^ρ parity targets. The positivity of ŵ is what
makes that true.

verify.py checks the identity, the bound and the next paragraph's monotonicity
exactly on twelve random small instances (t ∈ {2,3}, r ≤ 9).

**Monotonicity.** Suppose the new stage's image lies in the existing span, so ρ
is unchanged. Appending the stage multiplies each χ-term by 13^(−wt h_(t+1)(χ)),
which is at most 1. So ε₀ cannot increase.

## 2. Upper bound: FRAMES27, then repeat the last frame

[#6828](https://github.com/CrocSwap/integer-mult-bounds/pull/6828) gives explicit
frames FRAMES27 with ρ = 104 (dim D = 4). Their zero fiber is
(1+12ρ₂^25+3ρ₂^26) F^27, so

    θ := ε₀(FRAMES27) = (1+12ρ₂^25+3ρ₂^26) F^27 · 2^104 / 13^216 − 1 = 5.4537·10⁻⁶.

For t > 27 append U_j = I. The identity is in G, so W_j = W_27 for j > 27, ρ
stays 104, and by monotonicity ε₀(t) ≤ θ.

[#6848](https://github.com/CrocSwap/integer-mult-bounds/pull/6848) proves that
any frame sequence with ε₀ ≤ ε* = (1/13)/((23/12)^8 − 1) ≈ 4.25·10⁻⁴ has
max_y |fiber(y)| = |fiber(0)|. Since θ < ε*/75,

    OPT(t) ≤ |fiber(0)| = 2^(−104) 13^(8t) (1 + ε₀(t)) ≤ (1+θ) 13^(8t)/2^104.   ∎

## 3. Tag bits

⌈log₂ OPT(t)⌉ is determined whenever [log₂ lo, log₂ lo + log₂(1+θ)] contains no
integer, where lo = 13^(8t)/2^104. verify.py checks this exactly with big
integers for 27 ≤ t ≤ 400, together with the comparison against ⌈log₂ A_t⌉. It
then scans {8t·log₂13} at 60-digit precision for t < 600,000. The first depth
whose window could straddle a power of two is t = 584,977, with
1 − {8t·log₂13} ≈ 7.83·10⁻⁶.

## Relation to #6828's floor

The main term 13^(8t)/2^104 is below #6828's exact depth-27 value; it falls short
by the factor 1+θ. For t ≥ 28 it is above #6828's AM–GM floor. For example, at
t = 28 it is 252.51124·F^28 against 252.51122·F^28. #6828's balanced E-valued
patterns would fall *below* the main term at t ≥ 28, so they are not realizable
there.

## Scope

Exact for the PR6660 interface:

* fixed known frames in G;
* one relative precision bit before the first call;
* unbounded exact integers;
* complete output access.

The premises are cited and not replayed here:

* PR6660's chain bijection and dimension cap;
* #6828's FRAMES27 value and rank;
* #6848's max-fiber theorem.

All three are open and unmerged. The package supplies no codec, physical tag,
caller or restoration cost. κ, the selected frontier and its five assumptions are
unchanged. No independent human or proof-kernel review is claimed.
