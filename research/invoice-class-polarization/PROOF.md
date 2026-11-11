# The polarized invoice ceiling for the signed concave screen

## 1. The screen

Fix an integer ambient rank `m >= 2` and an invoice: a paid multiset

    P = (r_1, ..., r_Kp),   1 <= r_i <= m,

and a target multiset

    T = (s_1, ..., s_Kt),   1 <= s_j <= m,

with entry counts `Kp = |P|`, `Kt = |T|`, rank masses `Mp = sum r_i`,
`Mt = sum s_j`. For an exponent `x` the signed net is

    N_{P,T}(x) = sum_i r_i^x - sum_j s_j^x.

This is exactly the quantity of the documented comparator
`scripts/compare_recursive_invoices.py`, whose tariff is `r^(1-C)` with
saving `C`; write `x = 1 - C`, so the admitted range is `0 < x < 1`. The
comparator decides the order of two *given* invoices for every increasing
concave tariff, in particular for every power `r^x`, `0 < x < 1`.

The question here is different: over the whole class of invoices with the
same four summary numbers `(Kp, Mp, Kt, Mt)`, which one is the most
favourable for the screen, and is that extreme independent of `x`?

Throughout, `f(r) = r^x` with `0 < x < 1`. Then `f` is strictly concave and
strictly increasing on `[0, inf)`, so its increments `f(j+1) - f(j)` are
strictly decreasing in `j >= 0`.

## 2. The paid extreme: maximum spread

**Definition (greedy spread vector).** For integers `1 <= K <= M <= K m` put

    j  = min(K - 1, (M - K) // (m - 1)),
    r0 = M - K + 1 - j (m - 1),

and let `G(K, M, m)` be the multiset with `j` copies of `m`, one copy of
`r0`, and `K - j - 1` copies of `1`.

The constraints `1 <= r0 <= m` hold: `r0 >= 1` because
`j (m-1) <= M - K`; and `r0 <= m` because either `j = K - 1`, when
`r0 = M - (K-1)m <= m`, or `j < K - 1`, when maximality of `j` gives
`(j+1)(m-1) > M - K`, i.e. `r0 < m`.

**Lemma 1 (paid spread).** Let `1 <= a <= b` with `a >= 2` and `b <= m - 1`.
Then

    f(a - 1) + f(b + 1) < f(a) + f(b).

*Proof.* The increments of a strictly concave function are strictly
decreasing, and `a - 1 <= b`, so
`f(b+1) - f(b) < f(a) - f(a-1)`. Rearranging gives the claim. QED

Call a multiset `V` *spread-terminal* if no such pair of entries exists, i.e.
after sorting, every entry that is `>= 2` is followed only by entries equal to
`m`. A spread-terminal multiset therefore has the shape `1^a v m^b` with
`a, b >= 0`, at most one entry `v`, and `1 <= v <= m` (the cases `v = 1` and
`v = m` are the pure `1^a m^b` shapes).

**Lemma 2.** For `1 <= K <= M <= K m` the multiset `G(K, M, m)` is
spread-terminal, and it is the only spread-terminal multiset with `K` entries
and mass `M`.

*Proof.* Write `G = 1^a v m^b` with `v = r0`. If `v = m` then `j = K - 1` and
`G` is all `m`. Otherwise every entry strictly between `1` and `m` is the
single `v`, so `G` is spread-terminal.

For uniqueness, let `1^a v m^b` and `1^A w m^B` be two spread-terminal
multisets with the same count and mass, using the convention that `v` or `w`
may be absent. Equal counts give `a + b = A + B` when both are pure, and
`a + b + 1 = A + B + 1` when both have an interior entry. Equal masses then
force `a = A`, `b = B`, `v = w` by the two computations below.

*Both have an interior entry.* Equal counts give `b - B = A - a =: d`, and
equal masses give `(a - A) + (v - w) + d m = 0`, i.e.
`v - w = d (m - 1)`. Since `1 < v, w < m`, `|v - w| <= m - 3 < m - 1`, hence
`d = 0` and `v = w`.

*One has an interior entry.* Say `1^a v m^b` and `1^A m^B` have equal count
and mass. Equal counts give `a + b + 1 = A + B`, i.e. `A - a = b - B + 1`.
Equal masses give `(a - A) + v + (b - B) m = 0`. Substitute
`a - A = B - b - 1`:

    v = (b - B + 1) - (b - B) m = 1 + (b - B)(1 - m).

If `b - B >= 0` then `v >= 1` forces `b - B = 0`, so `v = 1`, contradicting
`1 < v`. If `b - B <= -1` then `v = 1 + (B - b)(m - 1) >= m`, contradicting
`v < m`. So this case cannot occur. QED

**Proposition 1 (paid minimum).** For every multiset `P` with `K` entries,
entries in `[1, m]` and mass `M`,

    sum_{r in P} f(r) >= sum_{r in G(K,M,m)} f(r),

with equality if and only if `P = G(K, M, m)`.

*Proof.* Sort `P`. If `P` is not spread-terminal there is a pair `a <= b` with
`a >= 2`, `b <= m - 1`; replacing `a` by `a - 1` and `b` by `b + 1` keeps the
count, the mass and the bound `[1, m]`, and by Lemma 1 strictly decreases the
sum. Iterating terminates because each step strictly decreases the sum and
the feasible set is finite. The terminal endpoint has the same count and mass,
so by Lemma 2 it is `G`. Hence every `P != G` admits a strictly decreasing
path to `G`, and since a global minimum cannot be non-terminal, `G` is the
unique minimiser. QED

## 3. The target extreme: balance

**Definition (balanced vector).** For `1 <= K <= N <= K m` write
`q = N // K`, `t = N - q K`, and let `B(K, N, m)` be the multiset with `t`
copies of `q + 1` and `K - t` copies of `q`.

**Lemma 3.** Let `1 <= b <= m - 2` and `b + 2 <= a <= m`. Then

    f(a - 1) + f(b + 1) > f(a) + f(b).

*Proof.* Here `b + 1 <= a - 1`, so strict monotonicity of the decreasing
increments gives `f(b+1) - f(b) > f(a) - f(a-1)`; rearrange. QED

**Proposition 2 (target maximum).** For every multiset `T` with `K` entries,
entries in `[1, m]` and mass `N`,

    sum_{s in T} f(s) <= sum_{s in B(K,N,m)} f(s),

with equality if and only if `T = B(K, N, m)`.

*Proof.* If two entries differ by at least two, Lemma 3 applied to the larger
`a` and the smaller `b` strictly increases the sum while preserving count,
mass and bounds. The only terminal multisets have all entries in `{q, q+1}`
for their common quotient, hence are balanced, and the balanced multiset is
unique for `(K, N)`. The same iteration argument gives the claim. QED

## 4. The class ceiling

**Theorem.** Let `P, T` be any invoice with entry counts `Kp, Kt`, rank masses
`Mp, Mt` and ranks in `[1, m]` (`m >= 2`). Then for every `x` with
`0 < x < 1`,

    N_{P,T}(x) >= N_{G(Kp,Mp,m), B(Kt,Mt,m)}(x),

and equality holds if and only if `P = G(Kp, Mp, m)` and
`T = B(Kt, Mt, m)`.

*Proof.* Apply Proposition 1 to the paid side and Proposition 2 to the target
side; the two sides are independent and the inequality subtracts the target
sum. Equality in the difference forces equality on both sides because each
side's deviation is nonnegative (paid) or nonpositive (target) with a sign
fixed by Propositions 1 and 2. QED

**Corollary 1 (sharpness).** Both `G` and `B` are valid rank multisets in
`[1, m]`, so the bound is attained inside the class: the canonical invoice
`(G, B)` is a schema-valid input to the comparator. The canonical invoice
depends on `(Kp, Mp, Kt, Mt, m)` only, not on `x`.

**Corollary 2 (uniformity).** The theorem holds simultaneously for every
exponent in `(0, 1)`: one canonical invoice is the pointwise-in-`x` extreme of
the whole class. The class ceiling is therefore a single function

    Lambda(x) = sum_{r in G} r^x - sum_{s in B} s^x,

a signed sum of at most four pure powers.

## 5. Consequences for the screen

**(a) O(1) necessary condition.** Let `I` be an incumbent invoice with net
`Psi(x)`. A candidate with summary numbers `(Kp, Mp, Kt, Mt)` can beat `I` at
some exponent `x` only if `Lambda(x) < Psi(x)`. In particular, using the
cruder mass-only bounds `sum r^x >= Mp m^{x-1}` and `sum s^x <= Mt`,

    Mt > Mp m^{x-1} - Psi(x)

is necessary. Neither test replays a construction.

**(b) O(1) sufficient certificate for `uniformly_worse`.** Let `Lambda_NEW` be
the canonical ceiling of the candidate class and let `U_OLD` be the
*antipodal* invoice of the incumbent class: paid balanced at
`B(Kp, Mp, m)` and targets spread at `G(Kt, Mt, m)`. Then
`N_NEW(x) >= Lambda_NEW(x)` and `N_OLD(x) <= U_OLD(x)` for all `0 < x < 1`, so

    Lambda_NEW(x) > U_OLD(x) for all x  ==>  N_NEW(x) > N_OLD(x) for all x.

Both sides are 2-rank invoices, so the existing hinge comparator verifies the
hypothesis exactly, in constant time, without enumerating either class. This
turns a per-invoice comparison into a per-class comparison.

**(c) Sharpness of the exponent range.** At `x = 1` the paid sum and the
target sum both equal the rank mass, so the theorem's inequality is an
equality for *every* pair of invoices with the same masses, canonical or not.
At `x = 0` both sides count entries. Hence `0 < x < 1` is exactly the range in
which the extreme is the polarized invoice; outside it the class has no unique
extreme. This is the sense in which the theorem is sharp and not an artefact
of the chosen extremal vectors.

**(d) Relation to the existing tool.** The comparator answers "is this given
invoice uniformly better than that given invoice" by a hinge criterion. The
theorem answers "what is the best possible invoice with these four numbers",
which the comparator does not compute, and it composes with the comparator in
both directions (a) and (b).

## 6. What is not claimed

1. No physical, native, compiler, precision, hosting, ownership or supplier
   admission. Ranks here are declared histogram entries, as in the comparator;
   the comparator's own assurance block makes the same restriction.
2. No claim about paid *call* counts, scalar instruction counts or additional
   charges outside the raw signed moment.
3. No `kappa` change. The result is a scoped arithmetic theorem about the
   documented screen, and it inherits the comparator's status as an arithmetic
   screen, not a construction.
4. Nothing here asserts that a canonical invoice is *realizable* by a word. It
   is a bound over declarations; Corollary 1 says only that the bound cannot be
   improved inside the declared class.
