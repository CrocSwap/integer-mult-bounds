# Coupled returns at two actual thin-query contacts

New scoped work by zxv with substantial OpenAI Codex assistance. Apache-2.0.
No subagents. This proof assumes the pinned PR5402 native endpoint. Its native
word, compiler, all-width physical implementation and source admission are not
proved again here. The new finite physical calculation uses an independent
literal monomial evaluator, including absolute phases.

## 1. Source contract and the compressed exit observation

Use Dillon's PR5402 at `3348fccea855082786d5f0fc5558b73d4974e745`:

\[
 X=Dx-Ry+RW h,\quad Y=Dy,\quad H=D(h-Zy),\quad R=DQ.
\]

The eight mode inputs h are arbitrary and independent of all main and other
helper inputs. The other 400 autonomous helpers and all nine zero owned returns
are retained. W and Z are ordinary scalar/monomial maps,

\[
 W=K_p^{-1} M K_m/2,\qquad Z=K_m^{-1}M^T K_p/2,
 \qquad ZW=14I.
\]

All K maps are unitary monomials, so Z=W*. The appropriate full Gaussians
intertwine W and Z: R_main W=W R_mode and R_mode Z=Z R_main. Separate
commutation with Q or D is not used.

Suppose the caller supplies the **versioned eight-field observation**

\[
 b=ZQY=ZRy.
\]

At the native return, apply Q to H and perform

\[
 H_o=QH+b=Rh,\qquad X_o=X-WH_o=Dx-Ry,\qquad Y_o=Y.
\]

These are ordered identities. They restore all original mode directions as
ordinary rank-nine jobs; they do not allocate independent credit to b. They
hold at every positive fiber width under the source contract, with the scalar
owner coefficients applied once outside the address tensor product.

The observation may be borrowed: every operation on it below is undone, and
it is returned unchanged. Source Y is unchanged. There is no erasure of a
persistent input. The provider's nine owned fields already return zero.

### Exact local operation bill

M has 448 nonzero entries. Once b is supplied, the exit uses:

1. Eight positive rank-one calls on H, then eight ADDs H+=b.
2. Apply K_m to eight H fields and K_p to 112 X fields.
3. The 448 ADDs X_i-=M_ik H_k/2.
4. Undo both monomial banks.

This costs **8 H1, 456 ADDs, 240 monomial field maps**, no new owned fields,
and no new target credit except restoration of the original eight H9 jobs.
The generator emits the literal field programs for these three contracts and the checker replays every adapter input, borrowed observation and dirty owned entry, checks every owned zero return, and recounts all instructions. Each ADD coefficient is an exterior dyadic scalar. A monomial field map is
charged ordinary work, not a zero-cost operation or a single tape step.

If a preserved full V=QY is supplied instead, fuse the common K_m pass:
apply K_m to QH and K_p to V, perform 448 ADDs into H, restore V, apply
K_p to X, perform another 448 ADDs, restore X and H. This costs **8 H1,
896 ADDs, 464 monomial maps**, with V unchanged and no extra owned fields.

If no observation is supplied, an explicit upper bound creates V by clearing
112 owned fields, copying Y, applying 112 positive H1 calls, and clearing the
observation bank after use. The resulting bill is **120 H1, 896 ADDs,
464 monomial maps, 112 COPYs, 224 CLEARs and 112 additional owned fields**.
All original helpers and targets are preserved. This is a constructive local
upper bound, not a minimum decoder tariff.

### Accuracy boundary

Let the returned provider errors be e_X,e_Y,e_H. If V=Q(Y+e_Y)+e_V and
the additional mode calls return Q(H+e_H)+e_J, then, writing e_A,e_B for
aggregate ordinary-operation residuals in the two updates,

\[
 E_H=Qe_H+e_J+ZQe_Y+Ze_V+e_A,\qquad E_X=e_X-WE_H+e_B.
\]

Since ||W||=||Z||=sqrt(14),

\[
 ||E_H||\le ||e_H||+||e_J||+\sqrt{14}(||e_Y||+||e_V||)+||e_A||,
 \quad ||E_X||\le ||e_X||+\sqrt{14}||E_H||+||e_B||.
\]

No independent-error assumption is needed for these triangle bounds. Actual
precision, coordinate rounding, source version retention, tape movement,
storage, compiler and outer funding remain obligations. These bounds do not
supply them for free. If b arrives after consumers have changed X or Y, the
consumer's propagated defect must also be repaired; the native-return identity
is not a late decoder for an already executed thin query.

## 2. Literal first and second consumer

The authenticated selected p16 controller begins with the following relevant
physical events (indices in its physical_events array):

| Event | Source instruction |
|---|---|
| 1 | backward FULL stage 1 on pair 0 |
| 2 | paid IDLE on pair 1, stages 0 and 1 |
| 3,4 | X0+=X1; Y1-=Y0 |
| 5 | lower thin shear Y0+=Q^-1 X0 |
| 6,7 | X0-=X1; Y1+=Y0 |
| 8 | backward FULL stage 3 on pair 1 |
| 9 | paid IDLE on pair 2, stages 0,1,3 |
| 10,11 | X1+=X2; Y2-=Y1 |
| 12 | lower thin shear Y1+=Q^-1 X1 |
| 13,14 | X1-=X2; Y2+=Y1 |

These fourteen instructions are also exactly the PR5398 successor caller's events 5 through 18, checked against its pinned literal controller. The two wrapped endpoint calls do not alter this clip. We leave those other FULLs completed; no claim is made for additional coupled substitutions at the wrapped endpoints.

Stage 0, the RIGHT boundary and all original inputs preceding this clip are
unchanged. Compare main outputs with the ordinary uncoupled main interfaces,
and let independent h1,h3 be the two new coupled mode input banks. Fresh D1,D3
commute with Q; W1 and W3 need not commute with Q or their own D.

After event 7, the main defects are

\[
 (\delta X_0,\delta Y_0,\delta X_1,\delta Y_1)
 =(R_1W_1h_1,D_1W_1h_1,0,D_1W_1h_1).
\]

The actual paid observation at event 5 has additional response D1 W1 h1.
It reads the version X0+X1, **not** Y0. A response cannot be relabelled Z1 QY0
without an additional embedding/identity. No impossibility claim about all
possible uses of that response is made here.

After event 14 the six main-bank defects are

\[
\begin{split}
 \delta X_0&=R_1W_1h_1,&\delta Y_0&=D_1W_1h_1,\\
 \delta X_1&=-R_3D_1W_1h_1+R_3W_3h_3,
 &\delta Y_1&=D_3W_3h_3,\\
 \delta X_2&=0,&\delta Y_2&=-D_3D_1W_1h_1+D_3W_3h_3.
\end{split}
\]

The second helper return additionally contains -D3 Z3 D1 W1 h1. Thus the
first defect disappears from Y1 but survives in X1, Y2 and the helper bank.
This is real two-generation transport, not loss of a dependency in the ledger.
The checker executes all fourteen source events over exact noncommutative
polynomial rows; reversing the query direction is rejected. The two FULLs,
224 thin H1 calls, 224 H16 IDLE jobs and 224 H24 IDLE jobs remain paid. No
coupled helper target credit is assigned by this experiment.

## 3. An eight-mode-only feed into the next FULL fails

Consider the specific proposed family that absorbs the incoming first-stage
innovation by updating the next helper input h3 to h3+T h1, leaves the main
inputs otherwise unchanged, and introduces no additional observations. To
cancel the inherited h1 term in X1 at stage 3, it necessarily requires

\[
 W_3 T=D_1W_1. \tag{*}
\]

This condition already allows **arbitrary linear address operators T**, a
larger class than ordinary scalar/monomial programs. It is not asserted as a
necessary condition for other joint encoders, changed main feeds, extra retained
observations, additional helper banks or arbitrary controllers.

At fiber width one embed the two stages on 17 physical bits: shared central
axis 0, first private axes 1..8, second private axes 9..16. The source literal
K_p and K_m words specify W1 and W3 on these planes with their exact phases.
Since Z3 W3=14I and Z3=W3*, the orthogonal projector onto im(W3) is
P3=W3 Z3/14. Therefore (*) implies (I-P3)D1 W1=0.

For each mode k, take the mode input with the shared central bit 1 and all
sixteen private bits zero. Denote its image under D1 W1 by v_k. The exact
calculation gives <v_i,v_j>=14 delta_ij. It evaluates Z3 v_k by sparse
Gaussian-integer arithmetic with common denominators 512 and 1024, and forms

\[
 G_{ij}=14\delta_{ij}-\langle Z_3v_i,Z_3v_j\rangle/14.
\]

This is the residual Gram matrix. In particular G00=173/14 and

\[
 \det G=1389039784345493055/26985857024>0.
\]

All eight exact elimination pivots are positive. Consequently all eight
sampled innovations survive outside im(W3); no T in the stated enlarged class
can satisfy (*). A width-one counterexample suffices to reject an all-width
contract. It is not a theorem that eight whole-field Gaussian jobs are needed:
these are eight independent complex directions, not a paid volume lower bound.

An instructive positive control uses central bit 0 instead. Its entire
residual Gram matrix is zero. Testing only the all-zero address would accept
the wrong handoff. A phase-only mismatch at one stage, preserving all address
permutations, is also rejected by the physical controls.

## 4. Complete recursive screen for the explicit purchased-observation exit

The selected native profile is rederived as PR5402's paid profile plus eight
H1 and eight H8 calls. Its helper profile is the 400 autonomous helpers plus
the original eight H9 jobs. Replaying controller event counts and target words
reproduces the selected ARITHMETIC.json inventories, not the obsolete invoice
embedded in the historical CONTROLLER.json.

There are **16 backward FULLs**, not 18 applicable calls. At each, buying the
missing observation and using the local exit changes the selected profile by
+112 H1 -8 H8, with original targets unchanged. The whole controller therefore
changes by +1792 H1 -128 H8, retains all fifteen thin query blocks, and changes
rank surplus 752 to **-16**. At saving a=1/250, a separate directed calculation
of sum(target r^(249/250))-sum(paid r^(249/250)) is strictly negative.
Each root enclosure is certified by exact 250th powers, with denominator 2^80.
Ordinary costs would be additional. This rejects the explicitly purchased
observation construction at the tested saving.

If b were already supplied at the correct version and boundary, restoring the
eight missing H1 calls would instead delete only the centers at these sixteen
FULLs, giving rank surplus 1776 and a positive moment screen at .004. The
observation's production, retention and consumer corrections are **unknown**,
not zero; this is a conditional allowance rather than a supplier or new κ.
The checker also reconstructs PR5413's declared economically neutral comparison profile: provider plus eight paid H8 and eight H8 mode targets at each of eighteen FULLs. Its 64,260 paid calls, 10,928 targets and masses 238,990/239,742 match the declared comparison. Replacing only the sixteen unwrapped calls with the purchased-response exit still gives surplus -16 and a strictly negative .004 signed moment. This is a conditional price comparison, not a replay or admission of PR5413's native completion, source application or compiler. No additional saving is claimed from its neutrality.

## Open next questions

1. Implement b=ZQY from already paid native observations on the correct version,
   with all displaced helper targets, ownership and restoration charged. Test
   one eight-field coefficient map before another full controller search.
2. If using more retained modes, name the enlarged input/output type and carry
   the full nonzero Gram residual through the next consumer. Its channel/volume
   and ordinary exit cost need explicit bounds. Merely increasing a search seed
   inside (*) does not change the rejection.
3. An actual delayed exit must correct the already executed query responses as
   well as the native return. The two-generation trace gives their exact maps.
   Price those maps before treating the native-return exit as a late repair.
