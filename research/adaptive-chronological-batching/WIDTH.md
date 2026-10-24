# Uniform width bounds for the adaptive chronological compiler

This is a **conditional all-rank width theorem**, not an extrapolation from a
finite scan. It uses this package's arbitrary-height cut inventory and the
least-LCM batching policy of Mihir Srivastava's
[PR #4507](https://github.com/CrocSwap/integer-mult-bounds/pull/4507).
The flow and adaptive height are zxv's
[PR #4483](https://github.com/CrocSwap/integer-mult-bounds/pull/4483), extending
Jacob Alan Sussman's integer compiler. Native semantics and the actual order
of individual paid positions remain premises.

For fixed height parameters `M >= 2`, `g >= 1`, put

```text
k0 = min(target ranks),   m = max(target ranks),
z = max(0, 1 - g log_M(k0)).
```

The least widths satisfy

\[
\boxed{\log B_N=O\!\left(N^z(\log N)^{d'+1}\right)},
\]

where `d'` counts distinct primes dividing any target rank, paid rank **or M**.
When `k0^g >= M` this is quasipolynomial. Otherwise `0 < z < 1`, so it is
subexponential. The constants depend on the fixed native rule, `M` and `g`.
This is an upper bound, not a tight growth rate, optimal batching theorem,
leaf-cost improvement, physical cost bound or new κ.

This theorem and the
[default-height proof](../chronological-width-bound/README.md) are two
scoped parts of one contribution. The default proof sharpens
[#4586](https://github.com/CrocSwap/integer-mult-bounds/pull/4586)
(`aadb7bc59390683450b1969e4632f546929dc569`) from logarithmic degree
`d+2` to `d+1` via bounded per-plateau visits; it does not originate the
quasipolynomial classification. Independent finite default checks in
[#4588](https://github.com/CrocSwap/integer-mult-bounds/pull/4588)
(`2f6578907b7f8718a13921552cc3069d3908e936`) are complementary.
[#4591](https://github.com/CrocSwap/integer-mult-bounds/pull/4591)
(`84c0fb3a39bcb1e4b8c48892bfdd8a6e7ae58a50`) checks arbitrary-height
aggregate identities, not actual chronological cut divisibility. That
cut-level transfer is proved in this package's README; the new width
bound here applies to its resulting recurrence.

## 1. Hypotheses and exact recurrence

Let `W_k` and `P_r` be positive integer multiplicities, with

```text
2 <= k0 <= k <= m,       1 <= r <= rmax < m.
```

Assume a paid rank-one position. This sufficient hypothesis makes every
height-G forest nonempty: the all-rank-one paid path reaches a degree-zero
leaf unit. Every finite forest with a unit has at least one fresh source.
More general rules require their own nonemptiness proof; an empty flow must
not be silently substituted by a productive supplier.
The default companion has a separate root-nonemptiness proof and needs
no paid rank-one position. Thus the theorem as stated here does not
subsume its entire hypothesis domain.

Let `W = sum W_k`, `P = sum P_r`. Widths are one below any fixed ordinary
cutoff `n0 >= m`. For `n >= n0`, define exactly

```text
C_n = floor(n/m),
ell(n) = floor(log_M C_n),
G_n = g ell(n).
```

**Default specialization versus executable interface.** Formally setting
`M=k0,g=1` gives the default height, `d'=d` (the primes of `k0` already
occur among target ranks), `z=0` and logarithmic degree `d+1`. This is a
symbolic specialization, with the nonemptiness qualification above. The
named `('adaptive', M, a, b)` interface in `batching.py` requires positive
integers `a,b`, so `g=a+b>=2`; no claim is made that this route ran `g=1`.
`width_bound.py` also takes `g` directly for its finite witnesses, including
a `g=1` toy case; that is not an all-rank default specialization replay.

Instantiate **all** chronological classes of the height-G_n forest, including
later components beneath empty parent classes. Let `S_n > 0` be the source
count and let `(j,q)` range over every upfront complement and separate exit
cut in the policy proved in README.md. Then

\[
a_n=\operatorname{lcm}_{(j,q)}\frac{B_j}{\gcd(B_j,q)},
\qquad B_n=S_na_n.                                            \tag{1}
\]

Repeated occurrences of a cut do not multiply `q`. The proof below needs only
that every `j` is an actual complement or exit, and that (1) is the policy.
For every prime `p`, without any restriction to the rank-prime alphabet,

\[
v_p(B_n)\le v_p(S_n)+\max_{j\text{ invoked at }n}v_p(B_j).       \tag{2}
\]

Strong induction bounds this valuation by a sum of source valuations along
one decreasing recursive rank chain. Different primes can use different
chains; no common maximizing chain is asserted.

## 2. Every recursive edge has an integer decrement

All unit columns are at most `C_n`. A paid exit has
`j <= rmax C_n`, hence `n-j >= C_n`. A nonroot source has rank greater than
`n/m`, so its complement decreases the ambient rank by at least `C_n+1`.
A root source, if present, contains `G_n+1` target letters, so its rank is
at least `k0^(G_n+1)`. Thus every recursive child satisfies

\[
n-j\ge\delta(n):=\min(C_n,k_0^{G_n+1})\ge1.                  \tag{3}
\]

An empty root class imposes no root-source obligation. This is why the
argument remains valid when the default-height fixed-factor contraction
fails. In particular, it does not assume every source exceeds `n/m`.

For `N >= n0`, put `Lambda = floor(log_M floor(N/m))`. At level `ell`, set

```text
lo_ell = max(n0, m M^ell),
hi_ell = min(N, m M^(ell+1)-1),
delta_ell = min(M^ell, k0^(g ell+1)),
t_ell = 0                                      if hi_ell < lo_ell,
        1 + floor((hi_ell-lo_ell)/delta_ell)     otherwise.
```

Along a descending chain, the nodes at one level are contiguous. Consecutive
nodes of that run drop by at least `delta_ell`; therefore there are at most
`t_ell` nodes at that level. These bounds require integer arithmetic only.

## 3. Source counts are constant on multiplicative-semigroup plateaus

Let `Gamma'` be the semigroup generated by the target ranks, the paid ranks
and `M`, including 1. Every eligibility comparison has the form
`rho*c <= C_n`, where `rho*c` is in this semigroup. Height changes occur at
`C_n = M^ell`, also in `Gamma'`. All finite source and cut data are therefore
constant between successive elements of `Gamma'`. Complement ranks `n-s`
are **not** constant, and are not used in this plateau claim.

Write `S(gamma)` for the source count at plateau start `gamma`. The number
of starts through `C` satisfies

\[
J(C)\le\prod_{p\mid M\prod k\prod r}
          (1+\lfloor\log_p C\rfloor)=O((\log C)^{d'}).        \tag{4}
\]

This box can contain unattainable products; it is only an upper bound.
The prime factors of `S(gamma)` need not belong to this alphabet.

At height `G`, the number of units is bounded by

\[
U\le\sum_{h=0}^G W^hP^{G-h}\le(W+P)^G.
\]

The second inequality follows by comparing binomial coefficients; it also
holds at `G=0`. Each unit has `W` target demand slots. Fresh sources are a
subset, so

\[
1\le S(\gamma)\le W(W+P)^{g\ell}.                            \tag{5}
\]

## 4. Exact divisor and bit envelope

For each level, let `L_ell` be the LCM of all `S(gamma)` with
`M^ell <= gamma < M^(ell+1)` and `gamma <= floor(N/m)`; an empty LCM is 1.
The levels with `t_ell=0` contribute nothing. Equations (2) and (3), applied
to each prime's chain, prove

\[
\boxed{B_n\mid Q_N:=\prod_{\ell=0}^{\Lambda}L_\ell^{t_\ell}
       \quad(0\le n\le N).}                                \tag{6}
\]

Let `J_ell` count the starts included in `L_ell`. The following is an entirely
integer bit envelope:

\[
b_N=\sum_\ell t_\ell J_\ell
 \left(\lceil\log_2 W\rceil+g\ell\lceil\log_2(W+P)\rceil\right).
\]

Then `B_n <= Q_N <= 2^b_N` for every `n <= N`. Computing enormous `Q_N` is
not necessary to use the symbolic theorem. The finite verifier uses exact
integer divisibility on bounded fixtures, rather than sampling a few primes.
The default companion instead uses a product of individual plateau source
counts raised to its constant plateau-visit bound. That divisor and (6)
are different certificates; equal asymptotic order at `M=k0,g=1` does not
establish universal finite numerical dominance of either one.

## 5. Growth in the two regimes

If `k0^g >= M`, then `delta_ell=M^ell` and
`t_ell <= m(M-1)`. Equations (4) and (5) immediately give
`log B_N = O((log N)^(d'+1))`.

Otherwise put `rho=M/k0^g > 1` and `z=log_M rho`. The level lengths obey

\[
t_\ell\le 1+m(M-1)+\frac{m(M-1)}{k_0}\rho^\ell.
\]

Summing the geometric progression gives
`sum t_ell = O(rho^Lambda) = O(N^z)`. Combining this with (4) and (5)
proves the stated subexponential bound. Here `0 < z < 1` because
`k0 >= 2` and `g >= 1`.

There is no unconditional comparison with an exponential **lower** bound
for adaptive nested widths: that would require an additional eventual
source-count lower bound of two. Finite least-versus-nested comparisons in
RESULT.json remain separate evidence.

## 6. Source-bound applications and verification scope

The pinned `rank-convergence/BENCHMARKS.json` fixes `g=witness.a+witness.b=2`:

| Profile | m | k0 | M | Proven exponent z |
| --- | ---: | ---: | ---: | --- |
| p7 | 121 | 5 | 256 | `1-log_256(25)` |
| native4453 | 153 | 4 | 1024 | `3/5` |
| p16 | 145 | 4 | 1024 | `3/5` |

All three have paid rank one. The theorem is about these exact raw profiles,
not materialized strictifications. The later
[PR #4533](https://github.com/CrocSwap/integer-mult-bounds/pull/4533) retunes
`M`; its different geometry is not certified by these application receipts.
The theorem allows any *fixed* `M,g`, not parameters depending on `n`.

`width_bound.py` checks integer decrements, source bounds, semigroup plateaus,
per-level chain-visit bounds and the all-prime divisor on finite toy
compilations. It separately binds the three real geometries and exercises
height boundaries through `M^2`, without materializing their all-rank
compilers. Finite checks exercise the proof's hypotheses and implementations;
they are not a proof of the asymptotic statement.

The historical base and immutable input pins are unchanged. At the
consolidation comparison main `fbc9ea0249746acca4f504d4fda2b84e0e36cf0d`,
the selected conditional κ is `.00302015` from #4470; #4483/#4507 remain
non-selected research inputs, not an admitted replacement frontier.

## 7. Remaining obligations and credit

Correctness of arbitrary-height chronological cuts is established separately
in README.md and the package's literal oracle checks. The full native word,
owned restoration, storage, routing, precision, stock, fixed-tape execution,
analytic transfer and exact recovery are not admitted here. No normalized
leaf exponent, κ, practical threshold or selected result changes.

A sharper width bound might use actual gcd savings or narrower semigroup
counts. Neither is needed for this result. A concrete next question is
whether these bounds can replace one declared finite-resource envelope at
its actual multiplication caller, with all physical costs still charged.

Prepared for codyw912 with substantial OpenAI assistance. An independent
Anthropic-model mathematical challenge checked the root/decrement argument
and supplied the sharper integer level-run form and the two growth regimes.
This is AI review, not independent human or proof-kernel verification.
Predecessor attribution above and in README.md remains intact. Apache-2.0.
