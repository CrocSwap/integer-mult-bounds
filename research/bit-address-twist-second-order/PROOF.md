# A second-order obstruction for the seven-call address-twist pattern

This answers the bounded second-order task in PR4953, Open next question 1.
It does not prove a lower bound for arbitrary words with two-sided twists.

## 1. Exact pattern and statement

Let `O = Z_(2)` be the rationals with odd denominator, let
`Gamma = M_m(O)` with `m >= 2`, and let `R = F_2[Gamma]`.
Its basis elements satisfy `[A][B] = [A+B]`. There are exactly three
registers with arbitrary independent contents in `R`. Write `u=(1,1,1)^T`
and let `e_s` be the three coordinate vectors. A paid call is

`D_N(A) = I + ([A]-1) N`,

where `A` has rational rank one. The **fixed pattern** consists of:

* one `J` call with `N = u u^T`;
* one `P_s` call with `N = u e_s^T`, for each `s=0,1,2`;
* one `D_s` call with `N = e_s e_s^T`, for each `s=0,1,2`.

These seven binary projectors are rank-one idempotents. Each call has its own
arbitrary rank-one frame in `Gamma`. Before and after each call, allow a
conjugation by an arbitrary diagonal tuple of register twists:

`F_j = T_j D_{N_j}(A_j) T_j^{-1}`,

where `T_j = diag(tau_j0,tau_j1,tau_j2)` and
`tau_jr(B) = L_jr B R_jr` with `L_jr,R_jr in GL_m(O)`.
The twists can differ by call and register. All call orders are allowed.
There are no extra interleaved mixing operations, extra calls or extra roles.
Conjugations are a favorable free operation; this theorem assigns them no
native cost.

**Theorem.** If a word in this pattern agrees, modulo the cube of the
augmentation ideal, with the register operator
`diag([C_0],[C_1],[C_2])`, for `C_s in Gamma`, then

`rank_F2(C_s mod 2) <= 1` for every `s`.

Consequently the pattern cannot realize three identity-matrix targets for
`m=3`. In particular no assignment of per-call, per-register `S3 x S3`
axis-permutation twists repairs PR4953's seven-call witness, in any order.
The theorem also allows arbitrary odd-denominator rank-one frames and `PBQ`
twists in this same pattern. It does not normalize arbitrary words to it.

For the permutation-only case, arbitrary interleaved rolewise twists with
these same seven paid projectors are also covered. Moving all free twists
to one endpoint conjugates the paid calls as above and leaves one diagonal
tuple of twists. The paid calls and the target act identically on `I/I^2`,
so the remaining twist must act identically there. The `S3 x S3` action on
the nine matrix units is faithful, hence that twist is identity. This does
not normalize additional scalar mixing or a changed projector pattern.

## 2. The degree-two quotient keeps squares

Let `I` be the augmentation ideal of `R`. Put `d=m^2` and choose the matrix
units `E_i`. The ring `R/I^3` is

`Q = F_2[t_1,...,t_d] / (monomials of total degree >= 3)`,

under `[E_i] -> 1+t_i`. In particular `t_i^2` is nonzero.
Here is an elementary justification avoiding the divisible ambient group
`M_m(Q)`. For any `A in Gamma`, `[4A]-1 = ([A]-1)^4` lies in `I^3`.
Thus passage to `Gamma/4Gamma = (Z/4)^d` does not change `R/I^3`.
The latter finite group algebra is
`F_2[t_1,...,t_d]/(t_i^4 : 1<=i<=d)`; quotienting its augmentation ideal
by its cube gives exactly `Q`. An entry `a/b in O` reduces modulo four
using the inverse of the odd residue `b`.

Let `V = I/I^2 = M_m(F_2)`. The degree-two part is `Sym^2(V)` with its
ordinary polynomial squares, not the exterior algebra. For nonzero `a in V`,

`mu_a : V -> Sym^2(V), z -> a z`

is injective: the polynomial ring over `F_2` is an integral domain, and
the quotient removes no homogeneous degree-two polynomial. One must not use
the whole truncated ring as an integral domain.

Every allowed twist preserves `I` and its powers. Its induced action on `V`
is the invertible linear map `B -> (L mod 2) B (R mod 2)`. Its action on
`Q` can include degree-two terms in images of the generators; these will not
contribute to the degree-one-to-degree-two calculation below.

## 3. Two necessary coefficient identities

For a call `j`, define

`a_jr = tau_jr(A_j) mod 2 in V`,

and let `U_jrs` be the induced action on `V` of
`tau_jr tau_js^{-1}`. In particular

`a_jr = U_jrs a_js`.                                               (1)

The `(r,s)` entry of the call's increment is, when `x_jr y_js = 1`,

`h -> ([tau_jr(A_j)]-1) (tau_jr tau_js^{-1})(h)`,

and is zero otherwise. Write the entire increment as `B_j=F_j-I`.
It raises augmentation degree by at least one. Therefore:

* On a constant input in register `s`, the degree-one output in register `r`
  is `sum_j x_jr y_js a_jr`.
* On an arbitrary input of degree one `z in V` in register `s`, the
  degree-two **increment** in register `r` is
  `sum_j x_jr y_js a_jr (U_jrs z)`.

Both formulas are independent of order. All terms containing at least two
increments have degree at least two on constants and at least three on
degree-one inputs. Only the latter terms are discarded in the second
formula. Thus we do not omit the constant-input second-order cross terms;
we do not need them.

Any operator identity on arbitrary dirty inputs must satisfy both formulas.
The diagonal target has zero off-diagonal output, and has degree-one
constant-input increment `c_s=C_s mod 2` on its `s` diagonal.

Fix `s`, and choose any `r != s`. Exactly two calls have a nonzero
`(r,s)` increment: `J` and `P_s`. Their necessary identities are

`a_Jr = a_Ps,r =: a`,                                             (2)

`a (U_Jrs z + U_Ps,rs z) = 0` for every `z in V`.                  (3)

If `a=0`, invertibility and (1) give `a_Js=a_Ps,s=0`.
If `a!=0`, injectivity of `mu_a` makes (3) imply
`U_Jrs=U_Ps,rs`. Equations (1) and (2), with this common invertible map,
then give `a_Js=a_Ps,s` as well. In either case,

`a_Js + a_Ps,s = 0`.                                             (4)

On the diagonal `(s,s)`, the only calls are `J`, `P_s` and `D_s`.
Their constant-input degree-one identity and (4) imply

`c_s = a_Js + a_Ps,s + a_Ds,s = a_Ds,s`.                           (5)

Every 2-by-2 minor of a rational rank-one matrix over `O` is zero,
so its reduction modulo two has rank at most one. Left/right invertible
twists preserve that property. Hence (5) proves the theorem. This argument
applies to each `s` and uses no finite enumeration. It also handles frames
whose reduction modulo two is zero.

## 4. A concrete dirty input for the predecessor

PR4953 uses `A_J=E00`, `A_Ps=E11`, `A_Ds=E22`. For `P_s`, the other two
roles are twisted by `sigma(B)=SBS^T`, where `S` exchanges axes 0 and 1;
role `s` is untwisted. All other twists are identity.

In block `(r,s)=(1,0)`, equations (2)-(3) become

`a=t00`, `U_J10=id`, `U_P0,10=sigma`.

Take the legitimate dirty input `f_0=[E00]+[0]`, `f_1=f_2=0`.
Its image in `Q` is `t00` in role zero. The role-one output is

`t00 * (t00 + t11) = t00^2 + t00*t11 != 0`.                        (6)

The target role-one output is zero. Equation (6) is the same for all
`7!` call orders. It is a uniform algebraic obstruction, not a rerun of
the predecessor's exact order census.

The screen concerns the **action on filtered register contents**. We do
not identify a crossed-product algebra with its possibly nonfaithful action
on `Q`; twist labels cannot in general be discarded inside that algebra.
The predecessor's aggregate degree-one action screen passes its witness.
Testing dirty degree-one inputs one layer later supplies the missing condition.

## 5. Evidence and boundaries

The proof is the quantified result. `verify.py` independently implements
the degree-two polynomial quotient and a finite group-ring oracle over
`(Z/4)^9`; no predecessor code is imported. Their agreement tests the
actual actions, including the nonlinear degree-two part of a twist.
The concrete witness is checked, as are the direct nine-call positive
control, all 36 permutation twists, the reduced local cancellation domain,
and semantic rejection controls. These finite checks corroborate the proof.

The theorem leaves arbitrary seven/eight-call patterns, arbitrary interleaved
mixing, additional clean or dirty roles, even-denominator frames, and a native
price for twists open. It proves no nine-call lower bound for the full
two-sided model, no supplier, no new kappa and no complete multiplication
theorem. Source pins and predecessor credit are in `SOURCES.json` and README.

Prepared by Krzysztof Wójt / krzysztofwojt with substantial OpenAI Codex
assistance. Apache-2.0. The pattern and first-order witness are JoyboyBrian's
PR4953; the odd-denominator method follows Cinna Davis / 1337isnot1337's
PR2110 and the retained Ali Romman/eumemic/huxint lineage.
