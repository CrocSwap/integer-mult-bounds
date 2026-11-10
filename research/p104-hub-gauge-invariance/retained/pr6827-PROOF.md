# Pure dual-pair retirement criterion: statements and proofs

No κ is claimed. Everything below is linear algebra over a ring of scalars and is
independent of any pricing model.

## 0. Setting and hypotheses

* **D** is the ring of ordinary scalars of the word: `Z[1/2]` (dyadic rationals).
  The proofs use only that D is a principal ideal domain in which every invertible
  matrix is a product of elementary matrices and a diagonal matrix of units (true for
  Euclidean domains, in particular `Z[1/2]` and `Z[i][1/2]`; for `Z[1/2]` section 3
  gives the factorisation explicitly).
* **Ordinary events** are ADD(dst,src,x) with x in D, SCALE by a unit of D, and SWAP. They act
  on the register vector. A set of registers is *combinable* if ordinary events may mix exactly
  those registers at the moment considered.
* **R** is a commutative ring containing D; all remaining events (queries, local gates,
  lambda, idle, chart moves) are invertible matrices over R. `R` may have zero divisors
  (for example `q^4 = 1`); only the invertibility of the elements named below is used.
* A word acts on registers `1..n`; input `j` initially sits in register `j`. For a cut:
  `P` is the prefix matrix (`P[i][j]` = coefficient of input j in register i), `S` the suffix
  matrix, `X = S P` the endpoint. All three are invertible over R.

Hypotheses of the criterion, each used where indicated.

* **(H1) Equal-target class.** `G` is a set of inputs and `tau` in `R` with `X e_g = tau e_g` and
  `e_g^T X = tau e_g^T` for all g in G (X is block diagonal on G with the scalar block `tau I`).
  Since X is invertible, `tau` is a unit of R. Used in the converse direction of 2.1 (e) and in
  the endpoint computation.
* **(H2) Frame.** `RF` is the set of registers that ordinary events can combine at the cut
  (caller word: all registers; native word: the registers resident in one chart F). The basis
  changes `E` (acting on `D^G`) are legal at the start and at the end of the word; `A` (acting on
  `D^RF`) is legal at the cut and at the start of the suffix.
* **(H3) Scalars.** As in the setting above.
* **(H4) Job.** `s` is a unit of R (a monomial, `lambda_sigma` times a monomial, or a chart).
  Whether the emitted jobs `s` and `tau/s` are accepted by a given host grammar is a separate
  legality condition and is not part of the algebra.

Notation: `D^G` is the module of column vectors with entries in D supported on G;
`s D^RF = { s v : v in D^RF }`.

## 1. Definition of retirement

Fix a cut, an input `p` in G, a register `r` in RF and a job `s`. (When the same index names the
input and the register, `p = r`.) A **retirement of p into r with job s** is a pair
`E in GL(D^G)`, `A in GL(D^RF)` (matrices that act as the identity off G, respectively RF) such that
the word

    w' = E ; prefix ; A ; [emit register r, load a fresh independent input z into r] ; A^{-1} ; suffix ; E^{-1}

computes, for all independent inputs `x` and `z`:

* the emitted value is `s x_p`;
* the final register vector is `X x - tau x_p e_p + (tau/s) z e_p`.

That is, the diagonal entry `tau` of X at p is replaced by two independent jobs, `s` (emitted at
the cut) and `tau/s` (the fresh input), and nothing else changes. Writing `Q = A P E` and
`R = E^{-1} S A^{-1}`, the final vector is `R(Qx + (z - (Qx)_r) e_r)`.

## 2. The criterion

Let `V_s = { c in D^G : P c in s D^RF }` (pure columns) and
`W_s = { d in D^G (rows) : exists a in D^RF with a P = s d }` (pure rows, `d = aP/s`).
With (H1) and invertibility, `W_s = { d in D^G : d S in (tau/s) D^RF }` (see (c)).

**Theorem 2.1.** Assume (H1)-(H4), p in G, r in RF. The following are equivalent.

* (a) There is a retirement of p into r with job s (section 1).
* (b) There are `E in GL(D^G)`, `A in GL(D^RF)` with `Q = APE` satisfying
  `Q e_p = s e_r` and `e_r^T Q = s e_p^T`.
* (c) There are `c in D^G`, `d in D^G`, `u, a in D^RF` with
  `P c = s u`, `a P = s d`, `a u = 1`. (Then `d c = 1` automatically.)
* (d) There are `c in V_s` and `d in W_s` with `d c = 1`.

Moreover, given (c), the following `E`, `A` realise (b): `E e_p = c`, `e_p^T E^{-1} = d`,
`A u = e_r`, `e_r^T A = a`; such E, A exist and are products of ordinary events (section 3).

*Proof.*

(a)<=>(b). Put `R = E^{-1} S A^{-1}`. Then `R Q = E^{-1} S P E = E^{-1} X E = X`, because E acts on G
only and X is block diagonal there with the scalar block `tau I` (H1: this is where both the
column and the row condition are used).
Suppose (a). The emitted value is `e_r^T Q x = s x_p` for all x, so `e_r^T Q = s e_p^T`. The coefficient
of z in the final vector is `R e_r`, so `R e_r = (tau/s) e_p`. Then `R (Q e_p) = X e_p = tau e_p
= s R e_r = R (s e_r)`; R is invertible, so `Q e_p = s e_r`. This is (b).
Suppose (b). Then `s R e_r = R Q e_p = X e_p = tau e_p`, so `R e_r = (tau/s) e_p` (s is a unit).
The final vector is `(RQ - R e_r e_r^T Q) x + R e_r z = (X - (tau/s) s e_p e_p^T) x + (tau/s) z e_p`,
and the emitted value is `e_r^T Q x = s x_p`. This is (a).
(If only the row condition held, the fresh slot would keep a dependence on the old inputs; if only
the column condition held, the emitted value would depend on other inputs. Both halves are used.)

(b)<=>(c). Given E, A, set `c = E e_p`, `d = e_p^T E^{-1}`, `u = A^{-1} e_r`, `a = e_r^T A`. Then
`Q e_p = A P c = s e_r` is `P c = s A^{-1} e_r = s u`, and `e_r^T Q = a P E = s e_p^T` is
`a P = s e_p^T E^{-1} = s d`. All four vectors have entries in D and lie in `D^G`, `D^RF` because E, A do.
`a u = e_r^T A A^{-1} e_r = 1`. Conversely given (c), the identity `a u = (1/s) a P c = d c` shows
`d c = a u = 1`. Then `D^G = c D (+) ker d` (as `d c = 1`), `ker d` is a direct summand of a free
module over a PID, hence free, and `E = [c | basis of ker d]` (c in column p) is invertible over D,
`e_p^T E^{-1} = d`. The same construction in `D^RF` (using `u`, `a` and the column r) gives `A^{-1}`.
Elementary realisation: section 3.

(c)<=>(d). If `a P = s d` with `a in D^RF` then `a = s d P^{-1} = s d X^{-1} S = (s/tau) d S`
(by H1 `d X = tau d` for d supported on G, so `d X^{-1} = tau^{-1} d`), hence `d S = (tau/s) a in (tau/s) D^RF`;
conversely if `d S in (tau/s) D^RF`, put `a = (s/tau) d S`, then `a P = (s/tau) d X = s d`. Thus
`W_s` is the set of `d` produced by (c), and `P c = s u` is the definition of `V_s`. QED

**What each hypothesis does.** (H1) is needed for the endpoint identity `E^{-1} X E = X` and for the
two-sided form of the criterion; without it conjugating by E changes the endpoint (control: pivot outside
the class, `verify.py`). (H2) enters through the supports of `a`, `u` (RF) and `c`, `d` (G); the pair can
exist for a larger RF and fail for a smaller one (control: the retimed role removed from the frame,
`verify.py`). (H3) is used for the elementary realisation. (H4) lets us divide by `s` and `tau`.
Nothing in (a)-(d) asks `p in RF`: the retired input and the emitting register may be different indices.

## 3. Completion and realisation over Z[1/2]

There is no Hermite or primitive-vector gap here. `d c = 1` already splits `D^G`; no separate
primitivity hypothesis on `c` is needed (and it would be insufficient: unimodularity of c alone does not give
a compatible row d).

Explicit elementary factorisation over `D = Z[1/2]`. Let `c` have `d c = 1`.
1. Scale each non-zero entry of `c` by a unit `2^k` to an odd integer (SCALE events).
2. The gcd of the odd integers is 1 (otherwise `c` would not generate the unit ideal). Euclid on the entries
   (ADD with integer coefficients, choosing the entry of least absolute value) reaches a vector with a single
   non-zero entry, `+-1`.
3. SWAP it to position p and SCALE by `+-1`. This is a list `M1` of ordinary events with `M1 c = e_p`.
4. `E1 = M1^{-1}`, `d'' = d E1` has `d''_p = d c = 1`. Put `T = prod_{j != p} ADD(p, j, -d''_j)`.
   Then `E = E1 T` has `E e_p = c` and `e_p^T E^{-1} = d`.
The same list, applied to the pair `(u,a)`, gives `A^{-1}` (and `A` is its inverse list). `verify.py` runs this
on 400 random dual pairs and on the literal words below. For `Z[i][1/2]` the same proof works with the Gaussian
Euclidean algorithm; it is not executed here.

**Rings that are not PIDs.** What is used is that a vector with `d c = 1` is the first column of a matrix of
the allowed event group. Over other rings this can fail (for example, over rings with non-free stably free
modules); we claim nothing there.

## 4. Ordinary events and the census

**Proposition 4.1.** Let `B` be an ordinary event (or a product of ordinary events) acting inside
one frame. Replacing `P` by `B P` (cut one event later) leaves `V_s` unchanged, maps the rows `a` to `a B^{-1}`,
and leaves the set `W_s` and the pairing `d c` unchanged. Hence the existence of a pure dual pair and its Gram
matrix are constant along a run of ordinary events; only the initial cut and the cuts after non-ordinary events
(query, local, lambda, idle, chart move) have to be examined.
*Proof.* If B acts inside RF it restricts to a bijection of `D^RF` and is the identity elsewhere, so `B P c in s D^RF`
iff `P c in s D^RF`, and `(a B^{-1})(B P) = a P`. If B acts inside another frame it fixes every vector supported
on RF and every vector supported off its frame, so both conditions are unchanged and `a B = a`. QED

## 5. Simultaneous retirements: unit divisors, not rank

For fixed `s` the map `pi: W_s x V_s -> D`, `pi(d,c) = d c`, is a bilinear pairing of
finitely generated free D-modules (submodules of free modules of finite rank over a PID;
`W_s` is the image of `{a in D^RF : aP in s D^G}` under the bijection `a -> aP/s`).

**Theorem 5.1.** The following are equivalent for `k >= 1`.
(i) There are columns `C = [c_1..c_k]`, rows `Dr`, `U`, `Ar` over D with `P C = s U`, `Ar P = s Dr`,
`Dr C = I_k`, distinct pivots `p_1..p_k` in G and distinct registers in RF (so that `k` retirements with the same
`s` can be done at once, `E e_{p_i} = c_i`, `A u_i = e_{r_i}`).
(ii) The Gram matrix of `pi` has at least k elementary divisors that are units of D.
In particular the number of simultaneous retirements at the cut is the number `u_s` of unit elementary
divisors of `pi`, and `u_s <= rank pi` (rank over the fraction field), with equality exactly when every non-zero
divisor is a unit.

*Proof.* (ii)=>(i): Smith normal form `U M Vm = diag(e_1,..)` of a Gram matrix `M`; with `e_1..e_k` units, rows
`U[i]` and columns `Vm[:,j]` give `d_i c_j = delta_ij` up to unit rescaling. Conversely (i): if `Dr = Zd [w]`,
`C = [v] Zc` in lattice bases, then `Zd M Zc = I_k`; every `k x k` minor of the left side is a D-combination of
`k x k` minors of M (Cauchy-Binet), so the gcd of the `k x k` minors of M divides 1, i.e. the product of the first
k elementary divisors is a unit. The existence of the pivots follows from section 3 applied to the block
version (complete `C` by a basis of `ker Dr`). QED

**Example (rank one, no retirement).** `D = Z[1/2]`, `R = D[t,t^{-1}]`, four registers,
`P = I + t N` with `N` the strictly upper triangular matrix with `N_12 = 3`, `N_13 = 1`, `N_24 = 1`
(`N^3 = 0`, so `P^{-1} = I - tN + t^2 N^2`, `X = I`, `tau = s = 1`, `G = RF = all`). Then
`V_1 = ker N` has basis `e_1`, `e_2 - 3 e_3`; the pure rows are `e_3^T` and `e_4^T`; the Gram matrix is
`[[0,-3],[0,0]]`. The pairing has rank 1 but its only divisor is 3, a non-unit of `Z[1/2]`: no value of
`d c` equals a unit, so by Theorem 2.1 there is no retirement, although the rank over `Q` is one.
(`verify.py` evaluates `d c` for all combinations of coefficients with absolute value at most 6.)
A counting statement stated for the rank over `Q` is therefore too strong; the statement above is the
correct one. In the literal words below every non-zero divisor is a unit.

**Example (both lattices non-zero, pairing zero).** The same construction with `N` the 3x3 Jordan block:
pure columns and pure rows both exist (dimension one each) and the Gram matrix is `[[0]]`. Then `a u = 0`, which
is incompatible with `a u = 1`.

## 6. Cuts inside native calls (levels)

Model (M). Registers split into `O` (caller registers outside the current call, untouched in it) and `Nat`
(the native registers of the current call: the pair, the helpers, owned fields). Inputs split into `K` (caller
inputs) and `Hh` (helper inputs of the current call). With `C = [C_o ; C_p]` the invertible caller prefix
(`C_p` = rows of the two registers entering the call) and `N_pre = [N_m | N_h]` the invertible native prefix up
to the cut, with entries in D (charts absorbed in the job),

    P = [[ C_o , 0 ],[ N_m C_p , N_h ]],    RF inside Nat   (no ordinary event mixes O with Nat).

The identification of the literal composite word with (M), the grading of native registers by chart and the
use of stage monomials in C, are modelling inputs of this section, not derived here. Classes are taken
within one level: `G inside K` or `G inside Hh` (a class mixing caller roles and helpers would be a
separate statement).

**Proposition 6.1 (helper classes).** If `G inside Hh`, then for every pair `(a,u)`: `u_O = 0`, `a_O = 0`
and `a N_m = 0`; pairs are the pairs of the native block alone. *Proof.* `c` has no K part, so the O rows of `P c`
are `C_o 0 = 0`; `a` lies in `D^RF inside Nat`, so `a_O = 0`; the K columns of `a P` are `a_v N_m C_p`, and `C_p`
has independent rows, hence `a_v N_m = 0`. QED

**Proposition 6.2 (caller classes).** If `G inside K` and `(c,d,u,a)` is a pair at an in-call cut (job `s`),
then `u_b = (0, C_p c / s)` and `a_b = (0, a_v N_m)` (zero on O, entries on the two pair registers) form,
together with the same `c`, `d` and `s`, a pair at the caller cut immediately before the call (prefix `C`,
`RF` = all caller registers).
*Proof.* The O rows of `P c` give `C_o c = 0`. On Nat, `N_m C_p c = s u_v` (the helper columns of `c` vanish).
`N_pre` is invertible over D, so `N_m` has a left inverse `L` over D (`L N_m = I`), hence
`C_p c = L N_m C_p c = s (L u_v)` and `C_p c / s = L u_v in D^2`; so `C c = s u_b` with `u_b` in D.
The helper columns of `a P = s d` give `a_v N_h = 0`, the K columns give `a_v N_m C_p = s d`, i.e.
`a_b C = s d` with `a_b in D^2`. Finally `a_b u_b = a_v N_m C_p c / s = d c = 1`. QED
Consequently in-call hits for caller classes exist only where a caller-boundary hit exists, and the caller
census (all cuts of the caller word, local gates atomic) covers them.

**Proposition 6.3 (consecutive calls).** Suppose calls are sequential with disjoint helper inputs, and at a
cut inside call j the helper registers of unstarted calls (identity rows) and of finished calls are not at the
frame F of RF. If `G inside Hh`, any pure column `c` is supported on the helpers of call j.
*Proof.* For an unstarted call j', the rows of `P c` at its helper registers equal `c_{j'}` and lie outside RF, so
`c_{j'} = 0`. For a finished call, `P c` restricted to the registers of that call is its full native block applied
to `(0, c_{j'})`; these registers lie outside RF, and the block is invertible, so `c_{j'} = 0`. The same support
statement holds for `a` (supported in RF inside the current call). QED
Together with 6.1: at every in-call cut the retirements of helper classes are those of the single current
native call, and no dual pair uses helpers of two calls. The condition fails if the helpers of two calls can be
co-resident in one frame at a cut (interleaved calls), which is outside this proposition.

## 7. Scope and open directions

* Retirements are of the conjugation type of section 1: a basis change `E` inside the class at the start and its
  inverse at the end, a basis change `A` inside the frame at the cut. By Theorem 2.1(a)<=>(b) the pure dual
  pair is also necessary within that type. Rewrites that change more than the pivot slot, scalars outside D, jobs
  that the host grammar does not accept, and cuts where the needed `A` would have to combine registers outside RF
  are not covered.
* The census in `verify.py` excludes jobs `s` that are scalar phases (no q or stage content) or equal to the
  class target up to a scalar phase, since those split off a rank-zero job; they are algebraically valid.
* Pricing, native phases, owned lifetimes and the framework assumptions of the cited words are not
  re-derived. The statements here do not change any κ.

## 8. Executable record

`verify.py` (Python 3.12, standard library, about 6 s) reproduces:

* the endpoint of each retained caller word is the declared diagonal (H1) and the native helpers' endpoint is the identity on helpers;
* #6716 (unretired caller): the census over all non-ordinary cuts, all classes, all jobs gives exactly one hit,
  cut 353, class {4,20,21}, `s = lambda_{-1} q`, Gram `[1]`; the retired word, with a completion computed from scratch,
  reproduces the predicted endpoint on all 35 columns;
* #6726 (unretired caller): hits exactly at cut 158 (class {6,7}, monomial job) and at cuts 383, 392
  (class {4,5}, lambda-type job; cut 394 of the published witness lies in the same ordinary run); each retired
  word is replayed;
* the #6726 final caller (also the caller of #6805): no cut carries a pair or a rank without a unit;
* #6805 native word with the retimed move: at cut 12372, frame 243, class of helper 368 (361 inputs, 15 resident
  registers), `V_s` has dimension 4, the pure rows have dimension 1 (they need role 80), the Gram matrix is `[4,4,4,4]`
  (a unit of `Z[1/2]`, not of `Z`), and the completed word reproduces the original endpoint on all 771 public
  inputs with helper 368 replaced by a fresh input. Without role 80 in the frame there is no pure row; in the
  word without the retiming there is none either;
* controls: pivot outside the class, non-pure row, non-pure column, zero pairing (`a u = 0` at the trivial job
  of #6716's cut), frame too small, rank-one pairing without a unit.
