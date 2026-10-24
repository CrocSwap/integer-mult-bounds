# A fixed bilinear certificate gives a precision-safe native boundary tariff

Prepared for Dugongue with substantial OpenAI Codex assistance. Informal sufficient theorem; no Lean build and no new numerical multiplication κ are claimed by this leaf.

## Explicit hypothesis and constructive lowering

Fix integers r ≥ 2 and m < r³. Supply three finite coefficient arrays α, β and γ proving an r × r matrix multiplication algorithm:

    (AB)_{ij} = Σ_{u=1}^m γ_{iju}
        (Σ_{a,b=1}^r α_{uab} A_{ab})
        (Σ_{c,d=1}^r β_{ucd} B_{cd})

for every pair A,B. The coefficients are fixed rational or fixed algebraic numbers with explicit defining and isolating data and a polynomial-time certified approximation procedure, independent of the growing input. Their defining data, exact identity, approximation procedure and denominator conditions are part of the supplied certificate. Set ω₀ = log_r m < 3. An exponent infimum or an existence theorem with no selected finite algorithm is not this explicit input.

For every complex W × W matrix product, recursive blocking with this certificate gives O(W^ω₀) arithmetic operations. Pad W to the least power of r above it; the constant-factor padding changes neither exponent nor precision order. Leaf products multiply only fixed-precision scalar words. No general integer-multiplication oracle, tensor-unit instruction, or Turing-machine simulation is used.

**Precision theorem.** Let every original real and imaginary component have magnitude at most 2^H. To return each component within absolute error 2^−P, this fixed recursive algorithm can be evaluated with O(P + H + log(W+2)) bits before and after the binary point, with constants depending only on its fixed certificate. Thus H,P = O(p) and W = p^O(1) give O(p)-bit intermediates and O(1) ordinary Word RAM instructions per scalar operation on words of C p bits, for a sufficiently large fixed C.

**Proof.** Let C ≥ 2 dominate the absolute values of all fixed coefficients, the sums of absolute coefficients in every one-factor linear form and output recombination, and the number of primitive operations in a fixed one-factor evaluation. At recursive depth h = ⌈log_r W⌉, the norms of every recursively formed input are at most C^h times the original maximum norm, with an extra fixed factor for representing complex numbers by real pairs. Each leaf product has magnitude at most C^(2h) 2^(2H). Output recombination has at most another C^h amplification. Every exact intermediate is consequently at most C^(3h+O(1)) 2^(2H), a polynomial in W times 2^(2H).

The circuit is bilinear: along a dependency path, an input-linear quantity is multiplied with an input-linear quantity once, after which recombination is linear. Its real arithmetic depth is O(h), with a constant depending on the fixed certificate. The sum of absolute derivative weights from perturbations to any output, including coefficient perturbations, is therefore bounded by C'^(h+1) 2^(2H+O(1)) for another fixed C'. Rounded quantities are controlled by the same bound after enlarging C', provided their initial absolute perturbations are at most 1. Expanding (x+e)(y+f)−xy = xf+ye+ef bounds the only nonlinear local perturbation. Thus rounding each operation and coefficient to error at most 2^−L gives output error at most C'^(h+1) 2^(2H+O(1)) 2^−L. Taking L = P + 2H + O(h+1) suffices. The magnitude estimate gives the same order of required integer bits. Fixed coefficients can be prepared once at that precision in poly(p) word operations by their supplied approximation procedure; this is n^o(1) when p = Θ(log n). This proves the tariff with actual finite arithmetic.

The theorem concerns multiplication. It does not remove any conditioning, pivot, inverse or periodic-closure proof needed by a boundary solve that uses multiplication. Those caller hypotheses remain explicit.

## Binding to the actual native boundary row

PR #4630 `NATIVE-ASSEMBLY.md`, section 5, pays the complete boundary algebra, both couplings and periodic closure by

    O(T (d/B) W_band^(ω₀−1) polylog(p)),
    d = Θ(p^ε),   B = Θ(p^ξ),
    W_band = O(p^(1/2) polylog(p)),   T p = Θ(n).

Substitution gives

    O(T p^(ε−ξ+(ω₀−1)/2) polylog(p))
      = O(T p^(1−[c₀+ξ−ε]) polylog(p)),
    c₀ = (3−ω₀)/2.

This is a direct charged substitution into the retained actual boundary algorithm. Any rational c with 0 < c < min(c₀,1/2) may conservatively replace c₀; its strict margin absorbs all retained polylog(p) factors. The precision theorem above ensures that using this fixed recursion does not multiply the scalar tariff by an omitted precision-dependent factor.

With Strassen’s explicit r = 2, m = 7 recursion, c₀ = (3−log₂7)/2. The conservative rational c = 12/125 is available because the exact integer inequality 7^125 < 2^351 proves ω₀ < 351/125 and hence c₀ > 12/125. The earlier c = 3/32 is smaller. Neither ceiling matters for the currently much smaller admitted supplier saving.

If the user’s matrix-multiplication development supplies a fixed exact stable certificate with ω₀ arbitrarily close above 9/4, this interface admits any c < 3/8. A theorem stating only ω ≤ 9/4 does not by itself identify the required certificate or establish its concrete coefficient-generation/precision contract. This document does not claim that such an explicit certificate was extracted or audited here.

## Universal native assembly for the replacement tariff

Retain every actual supplier, analytic, all-column, stock, conditioning, coefficient-generation and recovery hypothesis in PR #4635 `NATIVE-LIFT.md`. Let its fixed provider saving be q_C > 0, and choose rational

    0 < κ < Q := min(q_C,c),
    q = (κ+Q)/2,
    stop = (q_C−q)/(2q_C),
    δ = min(1/100, (q−κ)/(4(q+1)), (c−q)/16, (1/2−c)/4),
    ε = 1−δ,  β = 1−3δ,
    r_group = δ/10,  layout = δ/100,
    ξ = ε(1+q)−c+layout.

The symbol r_group is the source grouping parameter, not the matrix block side r. All parameters are fixed before n grows. Then the same actual native caller multiplies packed n-bit integers in O(n / (log n)^κ) word operations.

**Proof of every changed guard.** We have δ > 0, δ ≤ 1/100, β ≥ 97/100, 0 < q < c < 1/2, and q_C(1−stop)−q = (q_C−q)/2 > 0. The complete address-key size remains O(p^(β+1−ε) + p^β log p) = o(p), since β+1−ε = 1−2δ < 1. Thus its explicitly enumerated table costs n^o(1). The retained membership guard is 1−β−2(1−ε) = δ > 0, and 1−ε−r_group = 9δ/10 > 0.

Since δ ≤ (1/2−c)/4,

    ξ > 1−δ−c > 1/2.

Moreover

    ε−ξ = c−εq−layout ≥ c−q−δ/100 > 0.

The exact chirp/conditioning slack remains

    1−(β+2ξ−2+r_group)
      = 2(c−q) + δ(122/25+2q) > 0.

Therefore the full source analytic grouping/guard-bit arguments remain applicable.

The nine actual native rows now have savings

    εq,
    1,
    1−ε+qβ = q+δ(1−3q),
    1,
    1−ε+β = 1−2δ,
    c+ξ−ε = εq+layout,
    1/2+ξ−ε = (1/2−c)+εq+layout,
    ε,
    79−ε−β.

The first exceeds κ because δq < (q−κ)/4. For the fused row, q ≤ 1/3 gives saving at least q; if q > 1/3, its loss δ(3q−1) is less than 2δ(q+1) ≤ (q−κ)/2, so it still exceeds κ. The boundary row exceeds the main row by layout; the indexed sparse-axis row exceeds the boundary row by 1/2−c > 0. The remaining rows have savings at least 97/100 or 1, and κ < 1/2. Every row therefore has a fixed positive margin over κ. The complete coefficient and field representations have O(p) bits by the retained native bounds and the fixed-recursion precision theorem. Setup and table work are n^o(1), and source recovery remains exact. This proves the sufficient assembly.

## Scope and attribution

This extends a positive source-bound interface, rather than asserting a necessary condition or a barrier. It reuses the actual native algorithms and all their frozen proof obligations from Dugongue’s PR #4630 and #4635, the finite supplier/controller lineage, the Gaussian/Poisson and recovery foundations of Harvey and van der Hoeven, and Strassen’s explicit recursion. The new material is an explicit fixed-certificate precision boundary and a single universal parameter proof that permits c up to 1/2, with a correction to the fused-row comparison when q exceeds 1/3.

There is **no current κ improvement from this boundary replacement alone**: the main simultaneous-transform row remains limited by q_C. A numerical improvement must come from a stronger actually admitted provider, or a different complete native caller whose dominant row changes. No selected-frontier update or independent audit of the inherited full multiplication theorem is claimed.
