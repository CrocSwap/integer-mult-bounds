# Two-call P112 batch floor under changed cross-call label charts

Scope: k = 2 independent P112 all-pairs demands (C = I_2), root-code factors,
separate-total union price, exactly as in merged PR1714
(`research/p112-batch-centre-floor`, alephnan). The **only** change is the
cross-call label chart. This is a written proof with exact finite premises
rechecked by `verify.py`. It is not a Lean proof and has not had independent
human review.

## 0. Inherited model and premises

X is the 112 x 8 live P112 root matrix (norm four, frame-adapted Hamming
coordinates), with `X^T X = 56 I_8`. Labels ell_i live in the nine-dimensional
binary space V with nondegenerate symmetric pairing b, where
`b(ell_i, ell_j) = 1 + x_i.x_j/2 mod 2` (PR1714 section 1).

A factorization is `D T^T = I_2 (x) X X^T` with `D = (I_2 (x) X) A` and
`T = (I_2 (x) X) Cf`. A and Cf are complex 16 x m matrices, and the transpose
is ordinary. Since `I_2 (x) X` has the left inverse `(1/56)(I_2 (x) X^T)`,
this is equivalent to

    A Cf^T = I_16.                                                    (0)

Term j has the reader column `a_j = (a_j^0, a_j^1)` and the source column
`c_j = (c_j^0, c_j^1)`, with one 8-block per call. Terms with a zero column
are discarded.

**Inherited finite premises** (PR845 Mihir Srivastava; PR1098 Adam Gall;
PR1714 alephnan; rechecked here by an independent stdlib construction):

* (S) *Support lemma.* For nonzero complex `a in C^8`, the label span of
  `supp(Xa)` is V or one of eight hyperplanes `H_k = span ell(E_k)`, where
  `E_k = supp(X e_k)`. Rechecked: 503 of 511 binary functionals have
  complement rank 8 and eight have rank 7 with coordinate-line kernels.
* (P) *Pair lemma.* `rank b|(U x W) >= 8` for any two such spans U, W.
  Rechecked: all 64 ordered pairs `(E_i, E_j)` have F2 rank 8. The cases
  involving V (`V x H_k`, rank 8; `V x V`, rank 9) follow from
  nondegeneracy of b (Gram rank 9, checked).
* Consequently every root-code support span has dimension >= 8. Taking
  U = W in (P) gives `rank <= dim U`.

## 1. Changed chart

Call 1 keeps the chart ell. Call 2's row i carries the label `phi(ell_i)`
for a linear bijection phi of V. A term's union reader-label set is

    L(S_j) = ell(supp X a_j^0)  union  phi ell(supp X a_j^1),

and similarly for the source set L(T_j). Its price is the F2 rank of the
pairing matrix `[b(s,t)]` for s in L(S_j) and t in L(T_j). A general pair of
charts (phi_1, phi_2) reduces to `phi = phi_1^{-1} phi_2` only when phi_1
is an isometry. This package treats call 1 fixed.

**Isometric charts.** Take phi in O(V,b), so `b(phi x, phi y) = b(x, y)`.
Then call 2's own pairing, and hence its standalone P112 demand price, is
unchanged; only the cross-call pairing `b(x, phi y)` changes. Conversions
between charts are granted **free**. This favourable grant only
strengthens the negative conclusion below.

Equivalent V (+) V description: put the union pairing
`Gamma = [[G, G phi], [phi^T G, G]]` on V (+) V, with call-s labels in
summand s. The price of a term is the rank of Gamma on the two union
spans. `verify.py` checks that the single-V and V (+) V computations
agree on its fixtures.

## 2. PR1714's per-term step does not extend to changed charts

PR1714 section 3 shows that every active term costs at least eight "even
when the chosen blocks have different call indices". That uses the
common chart. Under phi, consider a **pure cross term**, with reader
column only in call 1 and source column only in call 2:
`a = (a^0, 0)` and `c = (0, c^1)`. Its price is `rank b|(U x phi W)`, where
U and W are root-code spans. Hence

    price = dim U - dim(U cap (phi W)^perp) >= dim U + dim W - 9 >= 7.   (1)

Equality needs `U = H_i`, `W = H_j` and `phi v_j in H_i`, where `H_k = v_k^perp`.
Thus the price is 7 exactly when `b(v_i, phi v_j) = 0`. Under the common chart,
`b(v_i, v_j) = 1` for all i and j, which is PR1714's 64-pair check.

Let w0 be the characteristic vector, with `b(x,x) = b(x,w0)`. For any
isotropic u, meaning `b(u,u) = 0`, the transvection `t_u(x) = x + b(x,u) u`
lies in O(V,b). Then

    b(v_i, t_u v_j) = 1 + b(v_i,u) b(v_j,u),

so t_u makes exactly `s^2` ordered pairs rank 7, where
`s = #{k : b(v_k,u) = 1}`. The verifier checks this formula on all 255
isotropic transvections. Its finite census has s^2 = 0 for 15 vectors,
16 for 224 vectors, and 64 for 16 vectors. Thus **some isometric charts
make all 64 exceptional cross pairs rank 7**.

The fixed-seed sample has 162 charts, including the identity and the
targeted chart. Its observed counts are 0, 16, 24, 28, 32, 36, 40 and 64.
Direct 56 x 56 F2 ranks agree with the formula on 1,600 chart/pair
instances. So the per-term step **does not extend** to changed charts.
This is not an error in PR1714, which asserts the step only under its
common chart.

## 3. Theorem A (isometric charts): the minimum is still 128

**Theorem A.** For every phi in O(V,b) and every exact root-code
factorization of `I_2 (x) X X^T`, the total union price is at least 128.
The standard decoder `u_s (x) X e_k` on both sides attains 128. Equality
requires that the factorization have no pure cross term.

*Proof.* Classify each active term:

* N, **non-pure**: some call s has both `a^s != 0` and `c^s != 0`.
* P01: `a = (a^0, 0)` and `c = (0, c^1)`.
* P10: `a = (0, a^1)` and `c = (c^0, 0)`.

These cases exhaust all active terms because there are only two calls.

*Prices.* A non-pure term contains the within-call block for call s as
a submatrix of its union pairing matrix. For s = 2, isometry gives
`b(phi x, phi y) = b(x,y)`. Monotonicity and (P) therefore give price >= 8.
By (1), a pure cross term has price >= 7.

*Counting.* A P01 term's outer product `a c^T` lies only in the (0,1)
block. A P10 term's lies only in the (1,0) block. Write
`R01 = sum_{P01} a^0 (c^1)^T` with `r01 = rank R01 <= |P01|`, and define
R10 and r10 likewise. By (0),

    Q_N := sum_{N} a_j c_j^T = [[I, -R01], [-R10, I]].

The Schur complement over C gives
`rank Q_N = 8 + rank(I - R10 R01) >= 16 - min(r01, r10)`. A sum of |N|
rank-one matrices has rank at most |N|, so

    |N| >= 16 - min(r01, r10).                                          (2)

*Total.* Let mu = min(r01, r10). Then

    total >= 8|N| + 7(|P01| + |P10|)
          >= 8(16 - mu) + 7(r01 + r10)
          >= 128 + 6 mu + 7(r01 + r10 - 2 mu) >= 128.                   (3)

If a pure term exists, then `|P01| + |P10| >= 1`. If mu = 0, the excess
`7(|P01| + |P10|) >= 7` is strict. If mu >= 1, then 6mu > 0. Hence
equality forces `P01 = P10 = {}`. The standard decoder has 16 terms; each
pairs `H_k` with itself inside one call, so it costs 128 under every
phi. QED.

*Rank-7 cross terms therefore never help.* Every pure cross term adds
at least 7 units. It can remove at most `8 min(r01, r10)` units from the
non-pure count, and only when both directions are present.

**Exact fixtures** (targeted transvection chart, with full 224 x 224
all-pairs replay):

* One-cross decoder: 16 non-pure terms plus one rank-7 P01 term. Its
  cost is 135, matching the lower bound in (3). The same decoder costs 136
  under the common chart.
* Two-cross decoder: 15 non-pure terms and two rank-7 pure terms. Its cost
  is 135, against the bound 134.
* Schur-pattern decoder with `R01 = R10 = I`: 8 non-pure terms and 16 pure
  terms. Its cost is 188, against the bound 176.

## 4. Proposition B (general cross forms; sufficient condition only)

Secondary model: on V (+) V, keep b as both within-call blocks. Allow
arbitrary cross forms beta01 (call-1 reader, call-2 source) and beta10.
Let c01 and c10 be the minimum ranks of beta01 and beta10 on pairs of
root-code spans. By monotonicity, these minima are taken over the 64
hyperplane pairs.

**Proposition B.** If `c01 + c10 >= 8`, every exact k = 2 root-code
factorization costs at least 128.

*Proof.* Non-pure terms still cost at least 8 by the within-call
submatrix and (P). Count (2) does not depend on prices. Thus

    total >= 8(16 - mu) + c01 r01 + c10 r10
          >= 128 + (c01 + c10 - 8) mu + c01 (r01 - mu) + c10 (r10 - mu)
          >= 128.  QED

**Corollary B' (invertible charts in the V (+) V reading).** Let phi be
any linear bijection of V, isometric or not. Keep b as each call's own
pairing and take the cross forms `beta01(x,y) = b(x, phi y)` and
`beta10(x,y) = b(phi x, y)`. For hyperplanes U, W,
`rank b|(U x phi W) >= dim U + dim W - 9 = 7`, so `c01, c10 >= 7` and
Proposition B gives the floor 128. More generally, any cross forms with
`rank beta01 + rank beta10 >= 12` qualify: restricting a form to a pair of
hyperplanes lowers its rank by at most 2, so `c01 + c10 >= 12 - 4 = 8`.
Only the single-V reading of a non-isometric chart, where call 2's own
pairing changes, is left open by this route.

This is **only a sufficient condition**. The zero form beta = 0 has
`c01 = c10 = 0` but still obeys the floor:

**Proposition C (beta = 0).** If both cross forms vanish, every exact
factorization costs at least 128.

*Proof.* The union pairing matrix is block diagonal. A term's price is
the sum, over calls s with `a^s != 0 != c^s`, of its within-call ranks,
each at least 8. Diagonal block s of (0) is `I_8`, the sum of
`a^s (c^s)^T` over terms with both parts nonzero. So at least eight such
(term, s) incidences exist for each s. The total is at least
`8 * 16 = 128`. QED

This is the "beta = 0 pitfall": the cheap-looking Schur pattern
`Q_N = [[I,-I],[-I,I]]` (rank 8) plus 16 pure cross terms of price 0
costs exactly `8 * 16 + 0 = 128`, because each both-call term costs 16.
The verifier replays it exactly.

**Proposition D (any cross forms; necessary conditions for going below
128).** Call a non-pure term *double* if `a^0, c^0, a^1, c^1` are all
nonzero. For such a term, let rho01_j be the rank of beta01 from the
call-1 reader span to the call-2 source span. Let rho10_j be the rank of
beta10 from the call-2 reader span to the call-1 source span. Then every
exact k = 2 root-code factorization satisfies

    total >= 128 - sum_{double j} min(8, rho01_j + rho10_j) + sum_{pure j} price_j.   (4)

*Proof.* Let n_s count the terms with `a^s != 0 != c^s`. Diagonal block s
of (0) is `I_8`, so `n_s >= 8`. Every non-pure term counts in n_0 or n_1,
and the d double terms count in both. Hence the non-double non-pure terms
number at least `16 - 2d`, and each costs at least 8 by (P).

A double term's union matrix is `[[G00, B01], [B10, G11]]`. Here G00 and
G11 are within-call blocks of rank at least 8 each. B01 and B10 are its
cross blocks, of ranks rho01_j and rho10_j. Subadditivity of rank gives a
price of at least `max(8, 16 - rho01_j - rho10_j)`. Summing,

    total >= 8(16 - 2d) + sum_double max(8, 16 - rho01_j - rho10_j) + sum_pure,

which is (4). QED

Corollaries:

* Proposition C is the case beta = 0, where every rho is 0.
* A sub-128 decoder in any cross-form model needs two things. First,
  `mu = min(r01, r10) >= 1`; otherwise (2) gives `|N| >= 16` and the
  total is at least 128. Second, it needs double terms whose cross-form
  ranks strictly exceed what the pure terms pay. In the verifier,
  inequality (4) is checked on four exact families, 50 forms each. Its
  minimum value is 128 there.

**Remark (coordinate families, every cross form).** In the two-cross and
Schur-pattern families, each both-call term pairs `H_p (+) H_q` with
itself. G restricted to `H_p x H_p` is invertible by (P). The Schur
complement then gives price

    8 + rank(G_q - beta10 G_p^{-1} beta01) >= 16 - min(rank beta01, rank beta10),

with all forms restricted to the relevant hyperplanes. The two pure terms
on the same pair cost `rank beta01 + rank beta10`. Each such group
therefore costs at least 16, and both families cost >= 128 for every
cross form. In the one-cross family, mu = 0. Its cost is
`128 + rank beta01|(H_p x H_q)`.

The verifier checks these families, plus a non-coordinate Schur pattern
`[I;-I] M M^{-1} [I,-I]` with M upper-triangular all-ones, on three kinds
of cross form:

* beta = 0;
* the targeted chart;
* 48 seeded random cross-form pairs.

All but beta = 0 meet the sufficient condition of Proposition B. That
makes this a weak finite search; it does **not** show that every cross
form, or every decoder, obeys the floor.

## 5. What is not proved

* An exact minimum for arbitrary cross forms, which may be below 128 for
  some form and some non-coordinate decoder. No such decoder was
  constructed. None of the cross forms here is a legal or priced
  interface.
* General k, C != I_2, outside-code overcomplete factors, masked
  identities and temporal relations. Non-isometric charts in the single-V
  model change call 2's own demand price, so they are out of scope here
  (their V (+) V reading is covered by Corollary B').
* Any physical meaning. Chart conversions are granted free. A real
  interface would have to pay for them, and that would only raise costs.
  The floor is internal to PR1714's algebraic separate-total objective;
  it is not a lower bound for arbitrary interacting circuits.

Prepared by thakrarsagar with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5). Apache-2.0.
