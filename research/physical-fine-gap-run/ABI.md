# Physical fine-gap run page contract

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Registered scientific replay and its scope are given in VERIFY.json and README.md.

Sources: Dugongue's CrocSwap/integer-mult-bounds#5571 mathematical run inverse;
Jose Manuel's CrocSwap/integer-mult-bounds#3851 physical signed convolution;
CrocSwap/integer-mult-bounds#3787 actual word multiplier.

## Fixed ports

Canonical encoded Count ports n,L,W,P satisfy n>=1, 1<=L<=n and 0<=P<W.
Data and coefficient ports use the unchanged `ring_words` Signed encoding:
exactly W physical bits per record, interpreted on grid2^-P. They use
`records.Tape` in the authenticated predecessor cohort.

A fixed set of six borrowed coefficient streams:

1. Finv: F_i^-1 in increasing original run order, n records, reused twice.
2. F: F_i in increasing original run order, n records.
3. mu_minus: lower recurrence coefficients in forward order, n records.
4. mu_plus: upper recurrence coefficients in reverse order, n records.
5. residual_minus: lower residual block pages in forward traversal.
6. residual_plus: upper residual block pages in backward traversal.

The seven numerical streams and four canonical Count tapes are pairwise
disjoint and external to all owner and descendant roles, including inactive
FFT pools. Borrowed bytes and origin heads are preserved. The complete
returned vector stays protected until physically consumed and erased. Other
owned bodies are erased at return; retained backing remains charged.

## Residual blocks

At traversal index k, b=min(L,n-k), c=min(L,k), N=c+b. The input window is
[k-c,k+b), with N<=2L. Each block page has exactly:

    inverse input gauges: N Signed records;
    signed convolution kernel: N Signed records;
    output gauges: b Signed records.

Anchor u is the first actual output coordinate. For orientation sigma=+1
(lower) or -1 (upper), exact source values are

    d_i=exp(a theta(i-u)^2),
    k_r=(-1)^r exp(-a(3rho-2sigma beta_u)r)/F_r, 0<=r<=L,
    k_r=0 for r>L.

All participating |i-u|<=L. The page holds rounded d_j^-1, k_r and d_i.
Scale the input window, call the actual lower convolution on N records,
physically discard its first c records, and scale the remaining b records.
Every unused child return bit is consumed. No global similarity gauge is used.

## Complete schedule and rounding

    Finv; R_minus; C_minus; F; reverse;
    R_plus; C_plus; reverse; Finv.

Diagonal products and completed convolution coordinates truncate once toward
zero. A recurrence row computes trunc_P((rhs<<P)-mu*previous), using an exact
doubled-grid residual. Its first coefficient is0. Subsequent exact coefficients
are exp(-a(rho-sigma(beta_i+beta_(i-sigma)))), rounded downward.

COEFFICIENTS.md owns the source-generation, truncation, accumulated-rounding
and carrier-width proof. Arbitrarily changed pages do not inherit that theorem.
The run consumer treats one arbitrary signed real vector; a complex caller
must pay both componentwise applications and its physical conversion.

## Scope

This is the complete run inverse, not the periodic Schur correction or the
full Gaussian/CRT/multiplication caller. The q-identity, mathematical recurrence,
generic convolution and Reference hole/resolvent bridge are inherited. The new
target is their coefficient-bound physical execution and full local invoice.
No new kappa or globally removed selected assumption is claimed.
