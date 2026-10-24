# An invertible two-call prefix attaining eight block-3 hook bounds

**Result.** Two calls on one input can each gain the full 80 in eight
width-five coordinate certificates, using one zero scratch register and a
sum of two free address permutations between the calls. The scratch can be
cleared, and the resulting operator is invertible at **every** positive digit
width. Each of the two summands used alone gives a second gain of only 72.

This is a scoped mathematical construction and an exact computational proof
of its ranks. It makes the single-free-image obstruction in Jacob Sussman's
[#4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628) sharp with
respect to allowing two images, in this explicit example. It does **not**
construct five transforms in fourteen calls, improve the call lower bound,
or supply a new multiplication exponent. No Lean or human review is claimed.

## 1. Was the proposed small-unit problem already solved?

At the research checkpoint of 22 October 2026, canonical main was
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`. PR #4628 remained open at
`ee4fd87f064017c23e5a86fc1dcfe0a5237caed3`; its source repository still had
head `86e575e28ed94890872dcff1bb2621d7ff559cbd`. Both list block 3,
five arrays in fourteen calls, as open in the engine game. The subsequent
[#4643](https://github.com/CrocSwap/integer-mult-bounds/pull/4643) audits the
projection bound at blocks at least 4; it does not settle this case.

The overlap helper refreshed all pages of 445 open PR bodies and 3,589
discussion records (snapshot times 15:29 and 15:31 UTC). Targeted PR search
also included closed results. No resolution or competing claim for this
prefix question was found. The sparse checkout searched only 36 of 5,860
tracked package-note paths; neither this search nor the predecessor's open
label proves global novelty. Exact source links are in section 6.

## 2. Model and explicit program

Addresses are triples $x=(x_0,x_1,x_2)\in\mathbb F_2^3$, encoded as
$x_0+2x_1+4x_2$. Let $\mathcal V=\mathbb C^8$. A paid call is

$$
C=C_{e_0}=aI+bX_{e_0},\qquad
a=(1+i)/2,\quad b=(1-i)/2,
$$

where $X_v e_x=e_{x+v}$. At digit width $f$, write
$C_f=C^{\otimes f}$. The engine permits free invertible binary address
maps on an array, applied identically in each column, and rational linear
mixing of registers, including copies and erasures.

Use just these two address permutations:

$$
Ue_{(x_0,x_1,x_2)}=e_{(x_0,x_1,x_2+x_0)},\qquad
Ve_{(x_0,x_1,x_2)}=e_{(x_1,x_0,x_2)}.
$$

In address order $0,\ldots,7$, their images are respectively
`[0,5,2,7,4,1,6,3]` and `[0,2,1,3,4,6,5,7]`.
Write $U_f=U^{\otimes f}$, $V_f=V^{\otimes f}$.
The prefix returns

$$
F_{2,f}y=C_f(U_f+2V_f)C_fy. \tag{1}
$$

An actual two-register implementation, starting from $(r_0,r_1)=(y,0)$, is:

1. $r_0\leftarrow C_f r_0$. **One paid call.**
2. $r_1\leftarrow r_0$; $r_1\leftarrow U_f r_1$.
3. $r_0\leftarrow V_f r_0$; $r_1\leftarrow r_1+2r_0$.
4. $r_0\leftarrow V_f r_0$, restoring $u=C_fy$, since $V^2=I$.
5. $r_1\leftarrow C_f r_1$. **One paid call.** The state is $(u,F_{2,f}y)$.
6. Apply the free mixing matrix $\left(\begin{smallmatrix}0&1\\0&0\end{smallmatrix}\right)$,
   returning $(F_{2,f}y,0)$.

This uses two rank-one calls, one initially zero scratch register, integer
mixing coefficients, and no phase letters. No input copy outside these two
registers is assumed. In particular, the sum in (1) is implemented by mixing;
it is **not** $(U+2V)^{\otimes f}$.

## 3. Invertibility at every width

Both $U$ and $V$ are involutions. Put $R=U^{-1}V=UV$.
As an address permutation,

$$
R=(0)(4)(1\ 2\ 5\ 6)(3\ 7),\qquad R^4=I.
$$

Consequently $R_f=R^{\otimes f}$ also satisfies $R_f^4=I$, and

$$
(I+2R_f)(I-2R_f+4R_f^2-8R_f^3)=-15I.
$$

Since $U_f+2V_f=U_f(I+2R_f)$, this supplies an explicit inverse using
fixed rational coefficients, for every $f$. The two factors $C_f$ are
invertible as well. Thus (1) is invertible at every width, and clearing
$u$ in step 6 loses no input information. This is an analytic all-width
proof; it does not infer uniform correctness from the width-five experiment.

## 4. Exact simultaneous equality in eight cuts

At width five restrict to the invariant subspace
$H=\mathcal V\otimes\Lambda^4\mathcal V$, of dimension $8\binom84=560$.
For a single-column matrix $g$, its action is
$\rho(g)=g\otimes\Lambda^4g$, with entries

$$
\rho(g)_{(y,S),(x,T)}=g_{yx}\det(g_{S,T}). \tag{2}
$$

Split the coordinate basis $e_x\otimes e_T$ into four classes:

| Class | Condition | Size |
|---|---|---:|
| $O_0$ | $x\in T$, $\bigoplus_{t\in T}t=0$ | 56 |
| $O_1$ | $x\in T$, $\bigoplus_{t\in T}t\ne0$ | 224 |
| $O_2$ | $x\notin T$, $\bigoplus_{t\in T}t=0$ | 56 |
| $O_3$ | $x\notin T$, $\bigoplus_{t\in T}t\ne0$ | 224 |

The zero-XOR four-subsets are affine planes. For a mask $b$, let $N_b$
span the classes selected by its four binary digits. Every affine address
map preserves membership and zero XOR (four copies of a translation cancel).
Every diagonal phase preserves each coordinate line. Hence every $N_b$
below is kept by the engine's free letters. In particular $N_3$ is the
usual hook, and $N_8$ is the published single-term certificate $O_c$.

Let $q_b:H\to H/N_b$. For a state with one input and output maps
$A_1,\ldots,A_r$, its potential is

$$
\Phi_b(A_1,\ldots,A_r)
=\operatorname{rank}\begin{bmatrix}
q_bA_1|_{N_b}\\ \vdots\\ q_bA_r|_{N_b}
\end{bmatrix}.
$$

Put $D=\rho(C)$, $A=D\rho(U)D$, $B=D\rho(V)D$, and
$K=\rho(C_{e_2}C_{e_1}C_{e_0})$. Here $A+2B$ is the restriction
of the actual output family (1) to $H$; no tensor lift of a sum is taken.
The complete exact calculation is:

| Mask $b$ | $\dim N_b$ | $\Phi_b(D)$ | $\Phi_b(D,A)$ | $\Phi_b(D,B)$ | $\Phi_b(D,A+2B)$ | $\Phi_b(A+2B)$ | $\Phi_b(K)$ |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 224 | 80 | 152 | 152 | 160 | 160 | 224 |
| 3 | 280 | 80 | 152 | 152 | 160 | 160 | 224 |
| 6 | 280 | 80 | 152 | 152 | 160 | 160 | 224 |
| 7 | 336 | 80 | 152 | 152 | 160 | 160 | 224 |
| 8 | 224 | 80 | 152 | 152 | 160 | 160 | 224 |
| 9 | 280 | 80 | 152 | 152 | 160 | 160 | 224 |
| 12 | 280 | 80 | 152 | 152 | 160 | 160 | 224 |
| 13 | 336 | 80 | 152 | 152 | 160 | 160 | 224 |

The rank 80 is the cap for **every** direction: a binary invertible address
map sends $e_0$ to any nonzero direction and preserves $N_b$.
The kept-subspace argument of #4628 therefore bounds the increase from one
call by 80, even with scratch and singular mixing. These caps and demands
reproduce the known bound $80s\ge224W$, or $s\ge14W/5$.
They are calibration results, not new lower bounds.

For our prefix the first increase is 80 and the second is
$160-80=80$, simultaneously for every listed cut. The free steps in
between retain $u$ up to an invertible free image and hence preserve its
potential. The joint-state and final-state columns show that the erasure also
preserves all eight potentials. With either branch alone the second
increase is only $152-80=72$.

**What is new.** A second call can be fully productive on all these cuts
without receiving a fresh independent input: two free images of the same
earlier output suffice, and the combined map can remain uniformly invertible.
Thus the published obstruction for a *single* free image cannot be used as
a pruning rule for arbitrary free linear combinations of that output.
This does not dispute the predecessor's deliberately narrower statement.

## 5. A singular control that the eight cuts do not distinguish

Replacing coefficient 2 by 1 gives $F_{1,f}=C_f(U_f+V_f)C_f$.
The checker also obtains $\Phi_b(F_{1,5}|_H)=160$ for every listed cut.
Nevertheless this family is singular. Indeed its nullity is the multiplicity
of eigenvalue $-1$ in $R_f$. The projection onto that eigenspace is
$(I-R_f+R_f^2-R_f^3)/4$. Since the numbers of fixed addresses of
$R^0,R^1,R^2,R^3$ are $8,2,4,2$, tensor traces give exactly

$$
\dim\ker F_{1,f}=\frac{8^f+4^f-2\cdot2^f}{4}>0\quad(f\ge1).
$$

It is 2 at width one and 8,432 at width five. Erasing the retained first
output in this variant therefore destroys information while preserving all
eight potentials. This is a concrete check that equality in these
certificates does not itself certify injectivity or completion. Coefficient
2 avoids this defect by the explicit inverse in section 3.

## 6. Reproduction, status, and credit

```sh
python3.12 -B research/complex-two-image-hook-prefix/verify.py
python3.12 -O -B research/complex-two-image-hook-prefix/verify.py
python3.12 -B scripts/research_package.py --package research/complex-two-image-hook-prefix
```

The verifier uses the standard library and computes ranks exactly over
$\mathbb Q(i)$, with Gaussian-integer elimination and exact common-divisor
removal. The ranks over $\mathbb C$ are the same. It replaces $C$ by
$I-iX_{e_0}$, removing a nonzero scalar: each affected block of a rank
matrix is rescaled uniformly, so no rank changes. It expands exterior
products directly, checks all 313,600 entries of the first call against the
independent minor formula (2), and checks its square against
$\rho(I-iX)^2=-32i\rho(X)$.

Seven controls cover deletion of either summand, duplication of a summand,
replacement of the second permutation by the identity, an incorrect cap of
79, the wrong tensor lift of a sum, and the singular coefficient-1 variant.
Independent cycle enumeration at widths 1, 2, 3 checks the nullity formula.
Exploration used NumPy/modular ranks; **none of those exploratory calculations
or external libraries is an input to the registered proof computation**.
No Lean build, all-history replay, or full integer-multiplication verification
is claimed or needed for this scope.

`SOURCES.json` pins the originating catalogue and selected record in this
branch's base history. The pending predecessor's exact URLs and document
hashes are bibliographic references in this note and `TASK.json`; replay
does not require fetching an unrelated PR's Git objects.

Predecessor credit:

- Jacob Sussman, [#4628 README](https://github.com/jacobalansussman/integer-mult-bounds/blob/ee4fd87f064017c23e5a86fc1dcfe0a5237caed3/research/complex-small-m-lower-bounds/README.md)
  and [PROOF.md](https://github.com/jacobalansussman/integer-mult-bounds/blob/ee4fd87f064017c23e5a86fc1dcfe0a5237caed3/research/complex-small-m-lower-bounds/PROOF.md):
  model, kept-subspace argument, 14/5 bound, and open shapes.
- Sussman's [single-term gain package](https://github.com/jacobalansussman/wht-power-saving-lean/tree/86e575e28ed94890872dcff1bb2621d7ff559cbd/research/block-bounds-and-new-rules/programs/five-in-fourteen-block3)
  and [block-bounds README, section 3.5](https://github.com/jacobalansussman/wht-power-saving-lean/blob/86e575e28ed94890872dcff1bb2621d7ff559cbd/research/block-bounds-and-new-rules/README.md):
  the single-image cap 72, eight tight-certificate context, and the warning
  that a width-five candidate can fail at width six. This package independently
  derives and checks its explicit example; it does not import those programs
  or recheck the predecessor's classification of every single-image class.
- eumemic's [#288](https://github.com/CrocSwap/integer-mult-bounds/pull/288)
  for the underlying certificate method; Swapnil Jain's P1/P2 as credited by
  #4628; OpenAI for the engine's call and free-operation model.

Prepared for lee-phys with substantial OpenAI Codex assistance in the
derivation, search, code, and writing. No independent human review.
Apache-2.0. No predecessor package or selected-result record is modified.

## Open next questions

1. **Can a full 5-in-14 program use this prefix?** It may start with two
   saturated calls on one input, but the remaining schedule must deliver all
   five independent targets at every width. First test the prefix's allowed
   continuations against the per-array end conditions at width six; do not
   accept a candidate from this rank table alone. No continuation is supplied.
2. **Which additional invariant distinguishes the singular and invertible
   variants while retaining useful call bounds?** Their eight potentials
   agree despite different kernels. Start from the explicit order-four
   eigenspace in section 5 and track where that information resides under
   shared-register mixing. A global lower bound requires a new argument.

The structured questions and the explicit change from the task card's
selected-supplier scope are recorded in `TASK.json`.
