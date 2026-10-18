# Frame-incidence saturation: a structural zero-exclusion criterion

**Scope:** Discussion [#1502](https://github.com/CrocSwap/integer-mult-bounds/discussions/1502),
CrocSwap/integer-mult-bounds. Research base
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`; priorities revision 2.
Characteristic zero throughout. No supplier, cost, multiplication-exponent, or frontier claim.

## 1. Result and its boundary

This note proves a reusable sufficient criterion for the missing zero-exclusion step.
The criterion uses **eight small ranks of 0–1 frame-incidence matrices, 28 connected
frame-intersection graphs, and a covering by blocks with a complete four-line class
plus one live line of the other class**. It does not use a Boolean solver or a
previous zero-exclusion certificate.

Under the criterion, every solution in the question satisfies the stronger identity

\[
                 a_{ik}b_{ik}=4 \qquad(i\in L\setminus F,\ k\in T_i).                 \tag{1}
\]

In particular, both factors are nonzero. This is a universal algebraic theorem,
not a numerical experiment or the assertion that a Boolean relaxation has one model.

The following P107 instance satisfies all the finite premises:

```
FRAME0 = (0, 1, 6, 11, 20, 29, 106, 119)
F      = (2, 5, 8, 9, 30, 41, 108, 117)
X      = (32, 45, 73, 78, 88)
L      = P112 minus X.
```

IDs are the lexicographically sorted canonical doubled roots specified in the
question. Here `G[32,73] = -1`, so X is not contained in any frame. Thus this is
outside the frame-contained deletion family excluded from the assignment.
It is not claimed to be outside every conceivable prior result.

There are **877 live frames**, **12 qualifying 4+1 blocks**, and **7 fully live
blocks** for this instance. The latter seven alone fail to cover three pivot
pairs. Thus the 4+1 strengthening is actually used, not just stated.

A short consequence of the same projector calculation gives gauge rigidity on
this instance as well, because all 14 blocks are nonempty; see Section 6.
The new contribution is the structural zero-exclusion argument, not a new audit
of the predecessor's Lemmas 5–6.

**Unresolved:** this package does not prove that every five-set admits a pivot
satisfying the criterion. No all-five-set or orbit census was performed. An exact
P107 control below fails the coverage condition at this particular pivot while
passing the other two conditions. That failure is not an algebraic counterexample.

## 2. Setting and a useful change of variables

Let the 120 roots be exactly those in the question: doubled vectors of squared
length 8, with first nonzero coordinate positive, sorted lexicographically.
Write `G_ij = (v_i dot v_j)/4`. Let L be a live set containing a frame F of eight
mutually orthogonal lines. The theorem below is not restricted to |L| = 107.

Suppose K, over a characteristic-zero field E, has rank at most eight and obeys
`K_ii = 4`, with zero entries on all ordered distinct orthogonal pairs. Since
`K[F,F] = 4I`, it has rank eight and

\[
 K=\tfrac14 K[:,F]K[F,:].
\]

Set `a_i = K[i,F]` and `b_i = K[F,i]^T`. Regard these as row vectors when taking
the outer products below. They obey the support restrictions and all E0/E2/E4
in the question. In particular,

\[
 a_i b_i^T=16,\qquad a_i b_j^T=0\quad(i\ne j,\ G_{ij}=0).
\]

Introduce the **possibly nonsymmetric** rank-one matrices

\[
                \Pi_i=\frac{a_i^T b_i}{16}\in\operatorname{Mat}_8(E).                \tag{2}
\]

They satisfy

\[
 \Pi_i^2=\Pi_i,\quad \operatorname{tr}\Pi_i=1,\quad
 \Pi_f=E_{ff}\ (f\in F),\quad
 \operatorname{supp}\Pi_i\subseteq T_i\times T_i\ (i\notin F).                      \tag{3}
\]

No symmetry, positivity, conjugation, ordering of E, or assumption of nonzero
entries is being imposed.

### Complete-frame identity

For **every** live frame S, not only the pivot,

\[
                            \sum_{i\in S}\Pi_i=I.                                  \tag{4}
\]

Indeed, the matrices with rows `a_i` and `b_i`, i in S, satisfy `A_S B_S^T = 16I`
by the ordered orthogonality equations. They are square and invertible. Hence
`B_S = 16 A_S^{-T}`, so `A_S^T B_S = 16I`, proving (4).

Similarly, if C is a complete class on a four-point support T,

\[
                            \sum_{i\in C}\Pi_i=E_T,                                \tag{5}
\]

where E_T is the diagonal coordinate projector onto T. One may either use the
four-by-four inverse identity or complete C to the live frame `C union (F minus T)`.
This is an algebraic consequence of the original equations, not an added equation
on odd pairs.

The canonical projectors are

\[
                  \Pi_i^0=\tfrac14 (G_{ik})_{k\in F}^{T}(G_{ik})_{k\in F}.
\]

The usual expansion in an orthogonal frame gives, for every live frame S,

\[
                  \sum_{i\in S}G_{ik}G_{i\ell}=4\delta_{k\ell}.                    \tag{6}
\]

The checker regenerates these identities from the integer root vectors.

## 3. Explicit finite hypotheses

Choose any finite family ScripS of live frames; taking all live frames is permitted
and is what the fixture does. For `J subset L minus F`, let M[J] be the 0–1 matrix
with rows indexed by S in ScripS, columns indexed by J, and entry `1` exactly when
i belongs to S. Repeated rows can be discarded without changing its rank.

For k, ell in F, k different from ell, put

\[
 I_k=\{i\in L\setminus F:G_{ik}\ne0\},\quad
 I_{k\ell}=I_k\cap I_\ell,\quad
 h_{k\ell}(i)=G_{ik}G_{i\ell}.
\]

### (D) Diagonal incidence saturation

For every k, the seven column vectors `h_kl restricted to I_k`, ell in F minus k,
are independent, and

\[
                        \operatorname{rank}_{\mathbb Q}M[I_k]=|I_k|-7.               \tag{D}
\]

Their containment in the kernel follows from (6), so this is equivalent to saying
that these seven **explicitly known** vectors are the entire kernel. It is a
rank condition on a finite integer incidence matrix, not on unknown a or b.

### (G) Two-point frame-intersection connectivity

For every unordered pivot pair {k,ell}, form a graph with nonempty vertex set
I_kl. Join i and j when some S in ScripS satisfies

\[
                          S\cap I_{k\ell}=\{i,j\}.
\]

Require this graph to be connected. Equation (6) gives
`h_kl(i) + h_kl(j) = 0` on each edge.

**This is not the E2 witness graph from the Boolean relaxation or from PR1399.**
Its edges encode an entry of the full-frame **projector sum** (4). The subsequent
proof also uses (D) and idempotence. No assertion is made that ordinary
pair-connectivity plus Z0 excludes zeros.

A slightly more general alternative to (G) is
`ker M[I_kl] = span(h_kl)`. Connectivity is a particularly simple sufficient
combinatorial certificate for that equality.

### (W) Complete-class-plus-one pair cover

Call a four-point block T **witnessed** when one of its two parity classes C is
complete and live, and the other class contains at least one live line j.
Require every pair of pivot coordinates to lie in at least one witnessed block.

This is weaker than requiring eight live lines in the witnessing block. It does
not require every block to have a complete class. The additional nonempty-block
premise used only in Section 6 will be stated separately.

### Theorem 1 — Structural zero exclusion

If (D), (G), and (W) hold, every characteristic-zero solution of the stated rank-eight
problem satisfies (1), for **all live nonpivot lines**, including partial classes.

The hypotheses are independently testable from the live root incidences. Their
selection is motivated by the identities (4) and (3): (D) and (G) linearize the
projector entries, and (W) eliminates the only exceptional local diagonal pattern.
Thus the criterion does not assume the desired nonvanishing, either explicitly
or by selecting already-gauged witnesses.

## 4. Proof of Theorem 1

### 4.1 Off-diagonal projector entries

Fix k different from ell. Write `p_i = (Pi_i)_{k ell}`. This is zero outside I_kl,
including all pivots. By (4), its restriction to I_kl lies in `ker M[I_kl]`.
On a graph edge, `p_i + p_j = 0`; also `h_kl(i) + h_kl(j) = 0`, with both h values
in {1,-1}. Consequently `p_i/h_kl(i) = p_j/h_kl(j)`. Connectivity gives a scalar
t_kell in E such that

\[
                   (\Pi_i)_{k\ell}=t_{k\ell}G_{ik}G_{i\ell}
                         \quad (i\in I_{k\ell}).                                 \tag{7}
\]

The scalar t_kell is allowed to be zero. No division by an unknown entry has occurred.
The two orientations have separate scalars t_kell and t_ellk.

### 4.2 Diagonal projector entries

Fix k. The difference between `(Pi_i)_{kk}` and `(Pi_i^0)_{kk}` vanishes at every
pivot and at every nonpivot outside I_k. By (4) and (6), its restriction to I_k
lies in `ker M[I_k]`. Hypothesis (D), which remains valid after extension from
Q to any characteristic-zero field, therefore gives scalars c_kell such that

\[
 (\Pi_i)_{kk}=\tfrac14+
          \sum_{\ell\in F\setminus\{k\}}c_{k\ell}G_{ik}G_{i\ell}
                              \quad(i\in I_k).                                   \tag{8}
\]

This is the useful information supplied by the incidence ranks. It is not
inferred merely from connected E2 equations.

### 4.3 The local 4+1 obstruction

This step uses the shared projector formulas already obtained from (D) and (G)
for every live row, including the fifth line. It does not assert that a complete
class and one opposite-class line, considered without those global hypotheses,
force nonzero support entries.

Fix a witnessed block T, a coordinate k in T, a complete class C on T, and a live
line j in the other class. For i on T define

\[
 s_i=(\varepsilon_{ik}\varepsilon_{i\ell})_{\ell\in T\setminus\{k\}},\qquad
 w_i=(\Pi_i)_{kk}.
\]

The four rows `(1,s_i)`, i in C, form a four-by-four Hadamard matrix: multiply
each row of the class sign matrix by its k-th entry, and put column k first.
In particular they are independent and the three nonconstant columns sum to zero.
Equation (8) becomes

\[
                            w_i=\tfrac14+\sum_{\ell\in T\setminus\{k\}}
                                           c_{k\ell}s_{i\ell}.                    \tag{9}
\]

Idempotence of Pi_i, combined with (7), gives

\[
                 w_i^2-w_i+
                  \sum_{\ell\in T\setminus\{k\}}t_{k\ell}t_{\ell k}=0.             \tag{10}
\]

Thus all these diagonal entries, including w_j, are roots of **one common monic
quadratic** `x^2-x+q_Tk`. Also (5) gives `sum_{i in C} w_i = 1`.

Here is the elementary characteristic-zero dichotomy. Choose one of the four
values x. Every value is either x or 1-x. If m of the four equal x, then

\[
                       mx+(4-m)(1-x)=1.
\]

With x chosen from the values, m is 1, 2, 3, or 4. The case m=2 is impossible.
For m=4 all four equal 1/4. For m=1 or m=3 the values are a permutation of
`(1,0,0,0)`. The coincident-root case x=1/2 is also impossible, since its sum
would be 2. This reasoning uses no order or positivity.

If all four values are 1/4, the invertibility of `(1,s_i)` immediately gives

\[
                             c_{k\ell}=0\quad(\ell\in T\setminus\{k\}).            \tag{11}
\]

Suppose instead that the exceptional value 1 occurs at i0 in C. By the same
Hadamard inverse, the unique coefficients in (9) are

\[
                          c_{k\ell}=\tfrac14s_{i0,\ell}.                          \tag{12}
\]

Since j has the opposite parity, the three signs
`s_{i0,ell} s_{j,ell}` have product -1. Their sum is either 1 or -3. Substitution
in (9) gives

\[
                                      w_j\in\{\tfrac12,-\tfrac12\}.              \tag{13}
\]

But the exceptional class values 0 and 1 in (10) force q_Tk=0. Equation (10)
then requires w_j to be 0 or 1, contrary to (13). Both contradictions are valid
over any characteristic-zero field. Hence the exceptional branch is impossible,
and (11) holds.

Notice the role of the fifth line: with only the complete class, the delta branch
is an actual possibility. It is not excluded by invertibility alone. Section 7
includes an explicit restricted algebraic example, not just a Boolean pattern.

### 4.4 All support entries

For each ordered pair k,ell, (W) supplies a witnessed block containing both.
Apply (11) with distinguished coordinate k to conclude c_kell=0. Hence all the
coefficients in (8) vanish and

\[
                          (\Pi_i)_{kk}=\tfrac14\quad(k\in T_i).
\]

By (2), `a_ik b_ik/16 = 1/4`, proving (1). A field has no zero divisors, so both
entries are nonzero. This conclusion includes all partial-class rows and any
live witnesses subsequently needed in an inherited rigidity argument. There is
no seed-only loophole. **End of proof.**

## 5. The exact P107 application

The five deleted doubled roots are:

| ID | Doubled root |
|---:|---|
| 32 | `(0,2,0,0,-2,0,0,0)` |
| 45 | `(1,-1,-1,-1,-1,1,1,1)` |
| 73 | `(1,-1,1,1,1,1,1,-1)` |
| 78 | `(1,1,-1,-1,1,-1,-1,1)` |
| 88 | `(1,1,-1,1,1,1,-1,1)` |

They lie in five distinct support blocks relative to F. The 14 blocks have live
class-size profile

```
7 blocks: (4,4)
5 blocks: (3,4)
2 blocks: (0,4).
```

Thus there are 21 complete classes, but no argument here assumes that the other
15 live nonpivot rows have nonzero entries in advance.

For (D), the independently regenerated rank table is:

| k | number of columns | incidence rank | canonical-kernel rank | distinct incidence rows |
|---:|---:|---:|---:|---:|
| 2   | 51 | 44 | 7 | 435 |
| 5   | 49 | 42 | 7 | 379 |
| 8   | 49 | 42 | 7 | 377 |
| 9   | 49 | 42 | 7 | 378 |
| 30  | 48 | 41 | 7 | 347 |
| 41  | 50 | 43 | 7 | 407 |
| 108 | 50 | 43 | 7 | 407 |
| 117 | 50 | 43 | 7 | 411 |

The arithmetic certificate is exact despite using a small prime. The checker
verifies the seven kernel vectors over the integers, verifies their independence
modulo the prime 1,000,003, and computes the displayed incidence ranks modulo
that prime. A nonzero modular minor is a nonzero integer minor, so the modular
calculation is a **lower bound** on characteristic-zero rank. The seven exact
independent kernel vectors give the matching upper bound. Their independence
also lifts to characteristic zero. The primality of the modulus is checked by
trial division. There are no floating-point ranks or probabilistic rank estimates.

For (G), all 28 graphs are connected. Their vertex counts range from 18 to 24;
edge counts range from 69 to 120. The complete per-pair table is in
`certificate.json`. Connectivity is checked directly, not inferred from a count.

For (W), all twelve blocks other than
`(2,5,8,9)` and `(30,41,108,117)` qualify. Those two exceptional blocks are
complementary, so they cannot both contain a given pair. Since each pair belongs
to three blocks, the twelve qualifying blocks cover every pair. The checker
also verifies coverage directly and records one complete class and one opposite
live witness for each qualifying block.

In contrast, the seven blocks with all eight lines live leave precisely these
pairs uncovered:

```
(5,8), (9,30), (30,117).
```

This proves a nonvacuous P107 application of Theorem 1. The general implication
is a written theorem; the finite fixture premises are reproducible exact
computations. The Python implementation is not a proof-assistant formalization.

## 6. Short gauge corollary of the same calculation

This section records a consequence rather than importing or re-auditing
PR1212 Lemmas 5–6 or PR1399 Lemma 9.

**Corollary 2.** In addition to (D), (G), and (W), suppose every one of the 14
support blocks has at least one live nonpivot line. Then
`K = D (2G_L) D^{-1}` for an invertible diagonal D. In particular this holds
for the displayed P107 fixture.

**Proof.** Theorem 1 gives `(Pi_i)_{kk}=1/4` on T_i. A two-by-two principal minor
of the rank-one matrix Pi_i gives

\[
                   t_{k\ell}t_{\ell k}=1/16
\]

whenever k,ell belong to T_i. By (W), every pair has such a row, so all these
scalars are nonzero. For distinct k,ell,m in the support of any live row,
rank one also gives

\[
                  t_{k\ell}t_{\ell m}=\tfrac14t_{km}.
\]

Every triple lies in one of the 14 blocks. Nonemptiness of all those blocks makes
the last equality available for every distinct triple. Set `u_kell=4t_kell` and
`u_kk=1`. Then `u_kell u_ellm=u_km`, including the degenerate cases supplied by
the inverse identities. Fix o in F and set `g_k=u_ko`; it follows that
`u_kell=g_k/g_ell`.

Combining this with (7) and the diagonal identity gives, on every live support,

\[
           a_{ik}b_{i\ell}=4\varepsilon_{ik}\varepsilon_{i\ell}g_k/g_\ell.
\]

Choose one support coordinate ell and use its already-proved nonzero b entry.
There is a nonzero scalar delta_i with

\[
 a_{ik}=\delta_i\varepsilon_{ik}g_k,\qquad
 b_{ik}=4\delta_i^{-1}\varepsilon_{ik}/g_k.
\]

Put `d_i=delta_i/2` for nonpivots and `d_f=1/g_f` for pivots. The pivot entries
have the required form, and for two nonpivots the identity
`sum_k G_ik G_jk = 2G_ij` gives

\[
                       K_{ij}=\tfrac14a_i b_j^T=2G_{ij}d_i/d_j.
\]

This proves the corollary. The nonempty-block premise is checked for the fixture.
It is not silently added to Theorem 1. **End of proof.**

The predecessor work already establishes the importance of these gauge forms
and the gluing/assembly strategy. The independent step here is the frame-incidence
route to the projector formulas and zero exclusion. No symmetry or copy-cost
consequence is claimed or rechecked.

## 7. Controls, experiments, and reproducibility limits

### Tests actually executed

The original `verify.py` was locally replayed in ordinary and optimized modes with CPython
3.12.14 on macOS 26.5.1 arm64, in isolated copies. Default runs passed in 0.583
and 0.622 seconds. The supplied research-session run log is separate evidence
and is not used as the local environment record. [REPLAY.json](REPLAY.json)
records eleven local expected outcomes, including both byte-identical certificate
regenerations and rejection of a tampered incidence rank. The checker uses only
the standard library and explicit exceptions, with no required `assert`. Required
finite checks are recomputed rather than accepted from the JSON file. The latter
is a compact regression record plus explicit fixture/witness data, not an opaque
solver proof.

The later 13-line boundary-control update was separately replayed under the same
local runtime in fourteen expected outcomes. Default normal/optimized runs took
0.545 and 0.631 seconds; both regenerated certificates match the supplied
replacement byte for byte. A saved-prediction tamper is rejected, and changing
the extra line's assigned pivot from label 2 to label 5 fails the shared-diagonal
guard under `-O`, also with `--write-certificate`, before any certificate write.
The original receipts are retained and the update receipt is appended in
[REPLAY.json](REPLAY.json).

The checker regenerates all roots and enumerates all frames by increasing-ID
orthogonality-clique recursion. At each recursive step, the candidate mask
contains exactly the larger IDs orthogonal to every selected line. Consequently
every eight-clique is visited exactly once. It obtains 2,025 frames and then
selects the 877 wholly contained in L.

An exact rational gauge example checks all original factor equations and all
11,449 entries of the reconstructed K against `D(2G)D^{-1}`. It does not establish
the universal theorem by sampling; that theorem is the argument in Section 4.

Four built-in rejection controls are checked:

* Zeroing a required entry in the rational positive factor example violates an
  original equation and is rejected.
* Using only the pivot as the frame family fails (D).
* The same deficient family has a disconnected two-point graph and is rejected
  by the independent (G) check.
* The actual P107 deletion `X_bad=(3,13,14,22,23)` passes (D) and (G), but fails
  (W) precisely at `(2,5)` for this pivot. It is rejected only at that stage.

The last control says **the sufficient criterion does not certify that instance
at that pivot**. It does not give an actual nongauge K and does not imply that
another pivot fails. It also does not prove (W) necessary for zero exclusion.

### Actual restricted algebraic counterexample to a weaker local step

Take only F and a single complete class C, for a 12-line live set. Bijectionally
assign its four lines to their four support coordinates. For the class line i
assigned to k, put `a_i=b_i=4e_k`; keep `a_f=b_f=4e_f` at pivots.
All original equations on this restricted live set hold: class lines are mutually
orthogonal, their assigned coordinates differ, and every prescribed pivot zero
is respected. The reconstructed K has rank eight by its pivot block. It is
**actually nongauge**, since some odd pivot entries are zero. The class A-matrix has
12 zero support entries.

This is not a P107 solution and not a counterexample to Theorem 1. It shows that
one complete class alone does not eliminate the delta branch of Section 4.3.
The checker also verifies all four choices of the exceptional class row and the
resulting fifth-row values +1/2 or -1/2, which fail scalar idempotence.

**A complete class plus one line is still insufficient without the global
hypotheses.** Take
`F=(2,5,8,9,30,41,108,117)`, `T=(2,5,30,41)`, the complete parity-minus class
`C=(22,27,34,37)`, and the opposite-class line `j=23`. Assign the four class
rows, in that order, to the four coordinates of T, in that order, with
`a_i=b_i=4e_assigned`. Keep `a_f=b_f=4e_f` at pivots and set
`a_23=b_23=4e_2`, where 2 is the global pivot label, the first coordinate of F.
On `F union C union {23}`, these are actual rational factors, not Boolean
supports. The checker verifies all 13 diagonal equations, all 108 ordered
distinct orthogonal-zero equations, and the pivot and support conditions.
The factorization gives rank at most eight and the pivot block gives rank
eight; the checker also verifies an exact modular rank-eight lower bound for
the integer matrix `4K=AB^T`. Each factor has 15 missing nonpivot support
coordinates, so this matrix is nongauge.

At pivot label 2, the class projector diagonals are `(1,0,0,0)`. In the
coordinate order `(5,30,41)`, the Hadamard inversion gives coefficients
`(1/4,1/4,-1/4)` in the shared diagonal formula, with constant term `1/4`.
The sign-product triple for line 23 is `(-1,-1,1)`, so that formula predicts
`Pi_23(2,2)=1/4-1/4-1/4-1/4=-1/2`, whereas its actual value is `1`.
All off-diagonal projector entries are zero, so the off-diagonal formula
itself admits all `t=0`. The failure is the shared diagonal formula from
(D), not the original equations or actual projector idempotence. Thus five
local lines do not justify replacing the global (D),(G) hypotheses. This
restricted 13-line solution is neither a P107 matrix nor a counterexample
to Theorem 1 or its gauge corollary.

No Boolean satisfying pattern is presented as an algebraic solution anywhere in
this package.

### Exploration domain and termination

Exploration used the exact stated 120-root model, complete-frame enumeration,
and one fixed pivot F as displayed above. Before the final fixture, the explicit
five-set `(3,4,7,10,12)` was tested and passed the stronger all-eight-live-block
version of the criterion. The final, more dispersed fixture was the first
five-element sample of `sorted(P112 minus F)` from Python's `Random(1502)`; it
met the requested five-distinct-support and 4+1-versus-full-block distinction,
so that selection stopped after one draw. Its literal IDs, not the random-number
implementation, define the delivered certificate. Baseline P112 and these two
positive P107 instances were explored; no all-five-set search was performed.
The deliberately constructed coverage-failure control is a separate test.

The smallest useful next question is whether every five-set admits **some** live
pivot for which (D), (G), and (W) hold, or whether (D)/(W) can be replaced by a
more deletion-robust structural condition. In particular, the fixed-pivot
coverage failure above prevents treating this package as a uniform proof.

## 8. Prior work, source status, and attribution

The exact model and finite geometry agree with the supplied handoff. This note
credits **Brett Halligan / burntout76 and Ninefold** for PR1212, **Josie Elliston**
for PR1399, PR1419, and PR1474, **DreamingOfClouds** for PR717, and
**themilkman216** for PR968. The predecessor's P108 coverage, DRUP work, local
rigidity lemmas, propagation lemma, and extension lemma are not new claims here.
In particular, this is not the already-known restriction-to-a-rigid-core extension
argument; it works with full-frame identities on the actual punctured set.

Pinned source references:

* [PR1212 proof](https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/57099cb5684f38877f31d149d598801671a633db/research/complex-rank8-decoder-rigidity/PROOF.md),
  head `57099cb5684f38877f31d149d598801671a633db`.
* [PR1399 proof](https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/4e1ba3a1ded94772cce5f8c0ad667a92afd6c493/research/complex-rank8-rigidity-p104-admissible/PROOF.md),
  head `4e1ba3a1ded94772cce5f8c0ad667a92afd6c493`.
* [PR1419 proof](https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/81b8997b4818fe914502866e5874e809c44dd852/research/complex-rank8-rigidity-extension/PROOF.md),
  head `81b8997b4818fe914502866e5874e809c44dd852`.
* [PR1474 proof](https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/311dd4e1eacef2b1301c68baf0276a9c51b32422/research/complex-rank8-rigidity-p108/PROOF.md),
  head `311dd4e1eacef2b1301c68baf0276a9c51b32422`.

The Pro research session reported rendered access to the four pinned proofs,
but could not authenticate their source bytes because direct downloads failed.
During local packaging, all four proof files were authenticated against their
exact fetched Git commits; the three SHA-256 values supplied in the brief matched.
[SOURCES.json](SOURCES.json) records those informational external pins separately
from main catalogue/selected-record provenance. This source check is not a proof
review or predecessor replay. The delivered checker has no external source or
DRUP dependency: it constructs the specified model from scratch. The scope and
overlap record are in [TASK.json](TASK.json); no comprehensive novelty claim is made.

Prepared by Andrey Mas with substantial **GPT-6 Pro assistance through ChatGPT**
for mathematical research and checker authorship. Codex coordinated sources,
audited execution implications, separately replayed the checker and mechanically
packaged the result. No independent human review or proof-assistant certification
is claimed. Released under **Apache-2.0**; see the repository [LICENSE](../../LICENSE).
The original theorem and its shared-formula clarification were retained. The
later restricted 13-line control and its prose were supplied by GPT-6 Pro; Codex
applied the supplied update and replayed it. Attribution and local
runtime/provenance paragraphs were normalized during packaging.
