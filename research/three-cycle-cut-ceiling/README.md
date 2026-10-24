# A uniform ceiling for three-cycle permutation-cut certificates

**Computer-assisted proof-method obstruction; no new kappa.** In the formal
coordinate-CNOT model of #4939/#4950/#4968, let `t` target registers carry
coordinate three-cycles, on arbitrary triples and in either orientation.
All other registers are dirty and restored; scalar register mixing is free.
For every finite address dimension `n >= 3` and register count `R >= t`,
every nonnegative combination of register-independent permutation cuts has
normalized target value at most

\[
\beta t,\qquad \beta=\frac{27+9\sqrt2}{7}=5.675417\ldots<\frac{23}{4}<6.
\]

This includes **every subset of the regular representation**, every finite
permutation action, and mixtures of different actions. Consequently that
linear cut relaxation, followed by rounding up its final value, cannot prove
the direct `6t` tariff when `t >= 4`: its rounded value is at most `6t-1`.
This does **not** construct a word shorter than `6t` or exclude stronger uses
of integer call-count constraints.

The constant is **sharp for the real quadratic domination used below**.
The optimum over Boolean cuts can be smaller and is **not determined here**.
In particular, this is not an exact certification of #4968's exploratory
approximately 3.51 cut value.

## Delta and model

James Reed's [#4968](https://github.com/CrocSwap/integer-mult-bounds/pull/4968)
proves mixed-transposition cut bounds and reports restricted order-pattern
optima, leaving arbitrary permutation cuts open. JoyboyBrian's
[#4974](https://github.com/CrocSwap/integer-mult-bounds/pull/4974) proves the
single-three-cycle word floor by formal support. James Reed's
[#5005](https://github.com/CrocSwap/integer-mult-bounds/pull/5005) proves two
three-cycles cost twelve at `n=3,R=2` by an exact word search. Those word
minima are not recomputed. The new result is a certified ceiling on the
**whole linear cut cone**, with a uniform lift beyond the 168-element group.

Work in `M_R(F2[GL_n(F2)])`. A paid factor is
`D_N(g)=I+([g]+[e])N`, where `g=I+E_ij`, `i!=j`, and
`N=u v^T`, `v^T u=1`. Every such rank-one factor costs one. Scalar
`GL_R(F2)` maps are free. The endpoint is diagonal, with one coordinate
three-cycle in each of `t` roles and identity in all other roles. Equality
is formal, on arbitrary dirty inputs; no clean workspace or free address
map is introduced.

For a finite permutation action on a set `Omega` and `A subset Omega`, write
`out_A(g)=|{x in A: gx not in A}|`. The cut in the register representation
is `A tensor F2^R`; the **same** `A` is used for every register. Its binary
cross-block rank `q_A` satisfies

\[
q_A(UV)\le q_A(U)+q_A(V),\quad q_A(\text{free scalar})=0,
\quad q_A(D_N(g))=\operatorname{out}_A(g),
\quad q_A(T)=\sum_{r=1}^t\operatorname{out}_A(c_r).
\]

The product inequality follows by expanding its off-diagonal block. The
paid block is a partial permutation matrix tensored with a rank-one matrix;
the target blocks are separate direct summands. These are the credited
#4950/#4968 cut formulas. Subsequent real quadratic forms concern these
**integer crossing counts**; they do not lift formal binary endpoint
equalities to characteristic zero.

## 1. The finite integer certificate

In the integral group algebra of `H=GL3(F2)`, let `S` be its six coordinate
CNOTs, let `c:(x0,x1,x2)->(x1,x2,x0)`, and put

\[
\ell=6e-\sum_{s\in S}s,\qquad b=2e-c-c^2.
\]

The exact coefficient identity is `p(ell)b=0`, where

\[
\begin{split}
p(X)={}&(X^2-6X+7)(X^2-14X+42)\\
 &\cdot(X-5)(X-6)(X-7)(X-9).
\end{split}
\]

For an auditable expanded form, its coefficients from constant to leading
term are

```text
555660, -1006362, 741006, -295897, 70871, -10494, 942, -47, 1.
```

[verify.py](verify.py) enumerates the 168 invertible three-row binary
matrices and evaluates this expression by exact integer convolution. Every
one of the 168 coefficients is zero. This is the finite computer-assisted
premise. Independently, [independent.py](independent.py) generates the group
as permutations of the seven nonzero vectors and checks the operator on
**all 168 basis columns**, with no imports from the primary implementation.
The regular representation is faithful, so the coefficient identity is an
identity in `Z[H]`, not only a numerical spectral observation.

## 2. Quadratic domination, and its sharpness

Apply any finite-dimensional real orthogonal representation of `H` to the
certificate and call the images `L` and `B`. Every CNOT is an involution,
so `L=sum_s(I-U_s)` is self-adjoint and positive semidefinite. Also
`B=2I-U_c-U_c^2` is self-adjoint, `B^2=3B`, and `LB=BL`: conjugation by `c`
permutes the six CNOTs. Thus `B/3` is an orthogonal projection.

On `im B`, `p(L)=0`. The roots of `p` are

```text
3-sqrt(2), 3+sqrt(2), 7-sqrt(7), 7+sqrt(7), 5, 6, 7, 9.
```

The smallest is `alpha=3-sqrt(2)>0`. Decompose `f=f0+f1`, with
`f0 in ker B` and `f1 in im B`. The spectral theorem and commutation give

\[
\langle f,Lf\rangle\ge\alpha\|f_1\|^2,\qquad
\langle f,(B/2)f\rangle=\tfrac32\|f_1\|^2.
\]

Consequently

\[
6\langle f,(B/2)f\rangle\le
\frac9{3-\sqrt2}\langle f,Lf\rangle
=\beta\langle f,Lf\rangle.\tag{1}
\]

Here is an exact witness that this **real quadratic** constant is optimal.
Let `q=p/(X^2-6X+7)` and, in the regular representation, set
`v=q(L)B delta_e`, `w=(L-3I)v`. Both verifiers check

```text
(L-3I)w = 2v,    Bv = 3v,
||v||^2 = 117151272,    ||w||^2 = 234302544,
<v,w> = -165676896,    v,w each have 165 nonzero entries.
```

Then `a=v-w/sqrt(2)` is a nonzero vector with `La=alpha*a`, `Ba=3a`.
It is nonzero because nonzero rational vectors `v,w` cannot satisfy
`w=sqrt(2)*v`. It attains equality in (1). This real vector is not claimed
to be a Boolean cut; spectral sharpness does not settle the cut optimum.

## 3. All cuts, all address dimensions, and all register counts

For any permutation action, substitute `f=1_A` in (1). Permutations have
equally many entries into and exits from a subset, so

\[
\langle1_A,(I-U_s)1_A\rangle=\operatorname{out}_A(s),\qquad
\langle1_A,(B/2)1_A\rangle=\operatorname{out}_A(c).
\]

The latter also uses `out_A(c)=out_A(c^-1)`. Hence every subset satisfies

\[
6\operatorname{out}_A(c)\le
\beta\sum_{s\in S}\operatorname{out}_A(s).\tag{2}
\]

For `n>=3`, restrict any permutation action of `GL_n(F2)` to the embedded
`GL3(F2)` on a target's three coordinates. It is still an orthogonal
representation of that subgroup, so (2) holds for its six internal CNOTs.
All other coordinates are untouched by those six operators. No projection
from `GL_n` to `GL3`, clean-ancilla specialization, or bound on spectator
writes is needed. In the regular action this can equivalently be seen by
partitioning into orbits `H x` and summing the same inequality on each.
Coordinate relabelling and `c <-> c^-1` cover every target triple/orientation.

Now choose arbitrary nonnegative cut weights, possibly on different finite
permutation actions. Let `C_g` be the resulting paid cost for a coordinate
CNOT `g`, and `D_r` the resulting crossing value of target `c_r`. Set
`M=max_g C_g`, taking the maximum over **all** paid address labels. Summing
(2) with the weights, for the six-label set `S_r` of target `r`, gives

\[
D_r\le\frac\beta6\sum_{g\in S_r}C_g\le\beta M,
\qquad Q(T)=\sum_rD_r\le\beta t M.\tag{3}
\]

If `M=0`, the target value is zero and this combination supplies no bound.
Otherwise its ordinary subadditivity certificate is `calls >= Q(T)/M`,
and (3) bounds that certificate by `beta*t`. Weights can depend on `n,R,t`;
the argument does not. Extra dirty registers and dense scalar mixing do not
change the paid cross-block rank-one calculation.

Finally `beta<23/4` follows from `36sqrt(2)<53`, or `2592<2809`. For `t>=4`,

\[
\beta t<6t-t/4\le6t-1,
\quad\text{so}\quad \lceil Q(T)/M\rceil\le6t-1.
\]

This statement concerns nonnegative linear combinations and their final
rounding. It does not bound an integer program retaining every individual
label count, nonlinear combinations, non-coordinate subspace cuts, or the
actual word length. Direct concatenation still supplies the familiar `6t`
upper bound; whether calls can be shared remains a separate question.

## Evidence and reproduction

Python 3.12, standard library only; no numerical solver in verification:

```sh
python3.12 -B scripts/research_package.py --package research/three-cycle-cut-ceiling
python3.12 -I -W error -B research/three-cycle-cut-ceiling/verify.py
python3.12 -I -O -W error -B research/three-cycle-cut-ceiling/independent.py
```

The registered replay runs both implementations normally and with `-O`.
The primary recomputes the group-algebra identity and sharpness vectors,
checks 144 literal binary paid cross-block ranks and four dirty endpoints,
and exhausts all 32,768 cuts of the natural 15-point `GL4` action with a
spectator coordinate. Those finite model checks corroborate (not replace)
the written lift. Altering the polynomial, omitting a CNOT, using an
order-two/identity target, assuming a rank-two paid factor has rank-one cost,
omitting a dirty-role restoration, and claiming a six-to-one crossing ratio
are distinct controls. The independent engine checks all 168 columns and
requires all corrupted operators to fail; its acceptance logic is also
tested on deliberately corrupted reports.
Actual CLI mutation tests reject twelve corrupted runs across normal and
optimized interpreters; reversing the cycle is accepted in both modes.
The complete registered replay passed locally on macOS arm64 / Python 3.12.12.

Numerical exploration suggested the polynomial. A 45-second MILP probe did
not certify a Boolean-cut optimum; neither it nor floating eigensolutions
are acceptance evidence. Exact polynomial evaluation and the written
spectral argument are the evidence retained here. No predecessor word
census, full selected cold replay, Lean, Docker, or physical supplier run
is required or claimed. The selected-source metadata baseline passed;
that check is not scientific admission.

## Scope and stopping decision

This is a side result on a lower-bound proof method, with a changed
`bit-new-register-model` scope. It prevents an unrestricted permutation-cut
LP campaign from certifying `6t` by the stated linear mechanism for `t>=4`.
It establishes no supplier, compiler/stock/precision bill, actual sharing,
complete multiplication theorem, or new kappa. Selected `60403/20000000`
is unchanged. Stop at this certificate rather than enlarge the word search.

## Open next questions

1. **What is the Boolean-cut optimum at n=3?** It is at most `beta`, and can
   be smaller. Start from an explicit cut/weight witness and a separately
   certified global upper bound. The 2^168 cut domain and missing exact
   optimization certificate remain the obstacle. More floating digits of
   a feasible cut are not a solution.
2. **Can a different invariant prove multi-cycle additivity?** Target one
   new obstruction, such as register interactions or constrained integer
   label counts, beyond these nonnegative permutation-cut combinations.
   Begin with a precise statement for four targets; neither this ceiling
   nor the single-target support lemma supplies the needed additive bound.

## Coordination and credit

Canonical [claim and status](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-19140523).
Fresh clone: `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`; before claiming,
refreshed to the scientific base `4c0a359d88f22f05189d51f48387750b801a45d4`.
Priority revision 7 and governing guidance were unchanged. Entry overlap
covered complete pagination of 303 open PRs and 4,153 Discussion records,
plus 6,710 local notes, followed by live topic checks. This is bounded
overlap evidence, not a novelty guarantee. The claim began at fixed GL3;
the written representation restriction proves the all-dimension extension.
Exact predecessor bytes, selected record and task card are provenance pins
in [SOURCES.json](SOURCES.json), not live runtime dependencies.

Credit James Reed / jwr404 (#4950, #4968, #5005) for the cut model and open
question; Mihir Srivastava (#4939) for the spectator model; JoyboyBrian
(#4974) for the formal-support theorem; Ross Richardson (#1989 and GL2
corollary), commdata2338 (#1414/#1495), Gareth Davidson (#1333), #1541, and
their retained predecessor attribution. Their packages remain unchanged.

Prepared by Krzysztof Wojt / krzysztofwojt with substantial OpenAI Codex
assistance. A Luna supporting agent supplied the independently represented
matrix checker; the primary agent reviewed it and owns the proof and
integration. These are same-session AI-assisted checks, not independent
human review or formal-kernel acceptance. Apache-2.0.
