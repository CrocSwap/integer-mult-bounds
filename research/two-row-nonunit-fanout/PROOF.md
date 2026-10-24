# Exact two-row dirty-fanout tariff with comparable demands

Krzysztof Wójt, with substantial OpenAI Codex assistance. Apache-2.0.

This is a written algebraic proof. The executable corroborates finite cases;
neither finite testing nor this package supplies a physical supplier or new κ.

## Contract and notation

Keep the contract of Nick Petalas's #4916, restricted to **two** rows, but
allow nonunit and zero target coefficients. Let R be any ring with 1 ≠ 0,
not necessarily finite or commutative. The arbitrary independent inputs are
`a_0,a_1,p ∈ R^w`, with w ≥ 1. The disjoint common source p is preserved.
The required endpoint is

    A_0 = a_0 + λ_0 p,       A_1 = a_1 + λ_1 p.

A finite, fixed straight-line word may use only

    P_i(β): A_i ← A_i + β p,              price μ_i > 0,
    E_i(α): A_i ← A_i + α A_(1-i),        price c_i > 0.

Thus c_i prices the ADD **into** i. Coefficients multiply on the left.
Prices are stationary, finite, complete, and independent of coefficients;
they may be arbitrary positive real numbers. Every call is charged, including
coefficient preparation and inverse application as stipulated by that model.
There are no other rows, free row transformations, clearing, intermediate
observations, input-dependent choices or separately erased original dirt.
An inverse word, when requested, must be paid separately.

Write `x ≼ y` when `x ∈ Ry`, equivalently x = r y for some r ∈ R.
Assume the two principal **left** ideals are comparable:

    λ_0 ≼ λ_1  or  λ_1 ≼ λ_0.

This is a condition on the two demands, not on every ideal of R. It includes
every pair in Z/p^k (p prime, k ≥ 1), every pair in a left chain ring, and
some pairs in noncommutative rings. Incomparable demand pairs are excluded.

## The tariff

For i ∈ {0,1} put j = 1-i. Define the direct price

    D = [λ_0 ≠ 0] μ_0 + [λ_1 ≠ 0] μ_1,

the single-insertion price

              { μ_i                         if λ_j = 0,
    S_i =     { μ_i + 2 c_j                 if λ_j ≠ 0 and λ_j ≼ λ_i,
              { μ_i + 2(c_i+c_j)            otherwise,

and the repeated-insertion price

    T_i = 2 μ_i + 2 c_j.

**Theorem.** Over all words in this contract, the exact minimum is

    OPT = min(D, S_0, S_1, T_0, T_1).

This includes the zero-demand boundary: OPT = 0 if both demands vanish.
The formula solves every two-row nonunit instance over Z/p^k for every
positive price vector, rather than only a fixed modulus or price matrix.

For two nonzero demands with λ_j not in Rλ_i, comparability gives λ_i ∈ Rλ_j.
The only extra options beyond direct insertion and the valid forest rooted
at j are

    2 μ_i + 2 c_j       and       μ_i + 2(c_i+c_j).

They respectively pay a second source insertion or reversible mixing in
both directions. Their difference is μ_i - 2 c_i: the cheaper method
changes at μ_i = 2 c_i. A forest whose parent demand cannot generate its
child demand is not an attaining construction.

## Lower bound for arbitrary interleavings

Zero-coefficient calls can be deleted, since prices are positive. Work with
a word containing no such calls. Set p = 0 and project onto the two original
dirt symbols. Its matrix starts and ends at I_2. Every E_i is an elementary
invertible matrix with inverse E_i(-α); P_i does not change this matrix.
The all-input contract implies matrix equality by testing a single input
coordinate equal to 1 and the other inputs equal to zero. No rank-over-a-field
assumption is used.

**Directional return lemma.** Each ADD direction occurs either zero times
or at least twice. For example, if the upper direction occurred exactly
once with nonzero coefficient α, every other dirt operation would be lower
triangular. Combining adjacent lower elementary matrices would give

    L(x) U(α) L(y).

Its upper-right entry is α over any ring, so it cannot be I_2. Interchanging
the two rows gives the other direction. Source calls can be ignored for
this argument, because they do not change dirt coefficients.

If the target is nonzero, some P_i occurs. Classify by the rows receiving
source insertions:

1. **Both rows receive an insertion.** The bill is at least μ_0+μ_1 ≥ D.

2. **Only row i receives insertions, at least twice.** If λ_j ≠ 0, some
   E_j must occur: otherwise row j never acquires any p coefficient.
   The directional return lemma requires at least two E_j, so the bill is
   at least T_i. If λ_j = 0, the bill is at least μ_i = S_i.

3. **There is exactly one insertion, at row i.** If λ_j = 0 its price alone
   gives S_i. Otherwise there are at least two E_j. If λ_j ≼ λ_i, this
   already gives the required S_i lower bound. If λ_j is not in Rλ_i,
   there must also be an E_i: without that direction, the sole insertion
   coefficient must equal λ_i, and row j's final source coefficient is a
   sum of left multiples of λ_i, hence belongs to Rλ_i. The contradiction
   and the return lemma force at least two E_i, giving μ_i+2(c_i+c_j)=S_i.

Every possible word therefore costs at least the minimum of the five
displayed numbers. This argument allows arbitrarily many calls, arbitrary
coefficients (including zero divisors), cancellations and interleavings.
It does not require Edmonds' branching theorem.

## Attaining words

All words below are in chronological execution order. They preserve the
common source and return the full dirt matrix to I_2.

**Direct:** insert λ_i p at each row whose demand is nonzero. Cost D.

**Single insertion, divisible direction:** if λ_j = r λ_i, execute

    E_j(-r), P_i(λ_i), E_j(r).

The endpoint at j is `(a_j-r a_i)+r(a_i+λ_i p) = a_j+λ_j p`.
If λ_j = 0, a lone P_i(λ_i) suffices. Zero-coefficient calls may be omitted.
This attains S_i in its first two cases (or a smaller, already-covered
direct price when both demands vanish).

**Two insertions at i:** for any pair of demands, execute

    E_j(-1), P_i(λ_j), E_j(1), P_i(λ_i-λ_j).

The middle pair transports λ_j p after cancelling a_i; the final insertion
sets row i's demand to λ_i. Its price is T_i. This construction uses no
division. If a source coefficient is zero, it can be omitted; the lower
bound still applies to the resulting word.

**Single insertion, reverse divisibility:** in the remaining case λ_j ≠ 0
and λ_j not in Rλ_i, comparability supplies b with λ_i = b λ_j. Execute

    E_i(1-b), E_j(-1), P_i(λ_j), E_j(1), E_i(b-1).

The first two ADDs are the inverse of the last two ADDs. Immediately after
the insertion the source coefficient column is λ_j e_i. The last two ADDs
send e_i to b e_i + e_j, giving exactly `(λ_i,λ_j)` in row order (i,j).
Hence arbitrary dirt is restored and the price is S_i. No commutation of
b with λ_j has been used. In this remaining case b ≠ 1, so all four ADDs
are nonzero. Literal inversion reverses any word and negates every gate
coefficient, with the same tariff.

For each expression in the lower envelope there is thus a legal word of
at most that price. Together with the lower bound, this proves equality.

## Consequences and discriminators

- For unit demands both divisibility directions hold. The T_i options and
  unnecessary reverse-mixing options are dominated, recovering exactly
  the two-row specialization of #4916's rooted-forest law.
- The credited #4916 boundary over Z/4 with `(λ_0,λ_1)=(2,1)`, μ=(1,9)
  and c=(1,1) has D=10, S_0=5, S_1=11, T_0=4, T_1=20: OPT=4.
- With the same demands, μ=(100,1000) and c=(1,1), OPT=104 is instead
  attained with one source insertion and four ADDs. Paying two source
  insertions costs 202. A rule allowing only valid forests and repeated
  source insertions therefore misses a real optimal regime.
- If λ_0=0, λ_1≠0, direct cost is μ_1; using row 0 as a temporary dirty
  source recipient may still be cheaper. Its original dirt must return.
- In a noncommutative ring the test is left divisibility. Replacing it by
  right divisibility can incorrectly enable the three-call word. The
  executable includes an explicit 2×2 binary-matrix counterexample.

The universal result rests on this proof. Finite exact shortest paths check
the implementation and its bounded instances; they are not its universal
premise. More rows, incomparable demand ideals and actual physical tariff
matrices require separate results.
