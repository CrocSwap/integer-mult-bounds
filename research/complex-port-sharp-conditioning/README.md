# Sharp conditioning of the complete complex two-bank port

This scoped proof replaces the bound 16 in Dugongue's
[PR #4743](https://github.com/CrocSwap/integer-mult-bounds/pull/4743)
by the exact Euclidean condition number

\[
 \operatorname{cond}_2 {\cal U}_f=\operatorname{cond}_2 {\cal V}_f
 =\frac{11+3\sqrt{13}}2,\qquad f\geq1.
\]

Both the norm and inverse norm are exactly \((\sqrt{13}+3)/2\).
The result concerns the complete two- and three-call maps on two arbitrary
independent input banks. It does not improve their paid call count, admit a
supplier or change the selected multiplication exponent.

This contribution is produced by Nick Petalas. The shear singular-value
calculation is classical linear algebra; the new result is its sharp
application to these particular ports, with the exact spectrum and witness.
Independent human and formal proof-kernel review are unclaimed.

## The precise interface

Use the retained letters and schedules of #4743, not a tensor power of their
sum. Write \(G_f=G^{\otimes f}\) for each individual letter. Set

\[
 A_f=C_{0,f},\quad D_f=J_fW_fC_{0,f},\quad
 L_f=P_f+2Q_f.
\]

The two full-input ports are

\[
 {\cal U}_f=\begin{pmatrix}A_f&0\\A_fL_fA_f&A_f\end{pmatrix},\qquad
 {\cal V}_f=\begin{pmatrix}A_f&0\\D_fL_fA_f&D_f\end{pmatrix}.
\]

All of \(A_f,D_f,P_f,Q_f\) are unitary. Consequently each port is
unitarily equivalent on its left and right to

\[
 {\cal S}(L_f)=\begin{pmatrix}I&0\\L_f&I\end{pmatrix}.
\]

For example \({\cal U}_f=\operatorname{diag}(I,A_f){\cal S}(L_f)
\operatorname{diag}(A_f,I)\); replace the left \(A_f\) by \(D_f\) for
\({\cal V}_f\). This uses both independent inputs and both outputs.

## Proof of the sharp constant

For any square complex matrix \(L\), its singular-value decomposition reduces the
shear to an orthogonal sum of the two-dimensional shears

\[
 \begin{pmatrix}1&0\\s&1\end{pmatrix},
 \qquad s\text{ a singular value of }L.
\]

The Gram matrix is \(\left(\begin{smallmatrix}1+s^2&s\\s&1
\end{smallmatrix}\right)\). Its eigenvalues have product one and sum
\(2+s^2\), so the corresponding singular values are

\[
 \frac{\sqrt{s^2+4}+s}{2},\qquad
 \frac{\sqrt{s^2+4}-s}{2}.
\]

The first increases with \(s\), the second is its reciprocal. Thus both the
shear norm and inverse norm equal the first expression at \(s=\|L\|_2\).

Here \(P=SUS,\ Q=SVS\), where \(S e_x=i^{\operatorname{popcount}(x)}e_x\),
\(U\) is CNOT from bit 0 to bit 2, and \(V\) swaps bits 0 and 1. Therefore

\[
 R=P^*Q=S^*UVS,\qquad
 R_f=P_f^*Q_f=R^{\otimes f}.
\]

The permutation \(UV\) fixes the all-ones vector. Hence \(R_f\) fixes the
nonzero vector \(v_f=S_f^*{\bf1}\) at every width, and

\[
 L_fv_f=P_f(I+2R_f)v_f=3P_fv_f.
\]

The triangle inequality gives \(\|L_f\|_2\leq3\), and this vector gives
equality. Substituting \(s=3\) proves the asserted norms and condition number.
The invariant Gram sector spanned by \((v_f,0)\) and \((0,P_fv_f)\) is exactly

\[
 \begin{pmatrix}10&3\\3&1\end{pmatrix}.
\]

Its eigenvalues are the roots of \(t^2-11t+1\), proving attainment of both
extremes, rather than only an improved upper bound.

## Complete singular spectrum

For completeness, the relative permutation is
\((0)(4)(1\ 2\ 5\ 6)(3\ 7)\). Its power traces are \(8,2,4,2\).
Tensor traces raise these four values to the \(f\)-th power.
The four character projectors of this order-four unitary therefore give
multiplicities

\[
 m_+=\frac{8^f+4^f+2\,2^f}4,\quad
 m_-=\frac{8^f+4^f-2\,2^f}4,\quad
 m_i=m_{-i}=\frac{8^f-4^f}4.
\]

Since \(L_f^*L_f=5I+2(R_f+R_f^*)\), its squared singular values are
9, 1 and 5 with respective multiplicities \(m_+,m_-,2m_i\).
For each \(d\in\{1,5,9\}\), both port singular values are

\[
 \frac{\sqrt{d+4}+\sqrt d}{2},\qquad
 \frac{\sqrt{d+4}-\sqrt d}{2},
\]

each repeated by the corresponding coupling multiplicity. This is a
closed all-width formula, not an extrapolation of finite ranks.

## Evidence and reproduction

The standard-library verifier constructs the literal phase monomials
independently at widths 1, 2 and 3. For the resulting 16-, 128- and
1,024-row shear matrices it checks the new Gram annihilator

\[
 \prod_{d\in\{1,5,9\}}\bigl(G^2-(d+2)G+I\bigr)=0,
 \qquad G={\cal S}(L_f)^*{\cal S}(L_f),
\]

both inverse multiplication orders and the sharp two-dimensional sector.
Exact spectral-projector traces enumerate the squared-coupling multiplicities:
\( (2,2,4), (18,24,22), (140,224,148) \), ordered by \(d=1,5,9\).
Six controls reject a changed coupling coefficient, swapped multiplicities,
the wrong inverse sign, unsupported width, invalid branch and false cap ten.
It imports no predecessor verifier and does not replay any predecessor rank
or endpoint certificate.

From the repository root, using CPython 3.12:

    /Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/complex-port-sharp-conditioning/verify.py
    /Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/complex-port-sharp-conditioning/verify.py
    /Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/complex-port-sharp-conditioning
    /Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/complex-port-sharp-conditioning --check-source-history

The final status is PASS_COMPLEX_PORT_SHARP_CONDITIONING. Optional
--receipt /absolute/scratch/path.json writes a generated receipt binding all
five package files by SHA-256. No receipt is hand-written or committed.

## Scope, sources and research decision

The mathematical baseline is canonical main
624de9dc66858af0945e5f8a0942488d62280d43, priority revision 7.
SOURCES.json pins the originating card, selected record and predecessor
proof texts as provenance. The computation is self-contained and has no
external live input. This changes the card's rank-shape search to a small
precision-interface lemma. The card's historical first control was attempted
and fails with KeyError: 'complex_profile' under the changed selected schema.
The current source-binding control passed with
PASS_RESEARCH_BASELINE_BINDINGS_ONLY.

Credit Dugongue's #4743 for both full-input schedules and the previous
bound 16; Yiyang / Lyy-iiis's
[#4710](https://github.com/CrocSwap/integer-mult-bounds/pull/4710)
for the repaired phase letters; lee-phys's
[#4688](https://github.com/CrocSwap/integer-mult-bounds/pull/4688)
for the two-image prefix and order-four permutation; and Jacob Alan Sussman's
[#4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628)
for the small-unit model, with eumemic and Swapnil Jain's predecessor
certificate framework credited there. Their constructions and earlier
singular-value observations are cited inputs. No predecessor credit is changed.

Discovery stops at this sharper constant. The full producer/consumer bill
remains that of #4743: paid calls, restoration, native workspace and array
passes are inherited; numerical Gaussian implementations, compiler costs and
complete recursive stability are separate obligations. This result does not
price any unknown cost as zero or justify a further construction campaign.
The proof concerns exact Euclidean endpoint conditioning. It makes no claim
about coordinatewise rounding, internal Gaussian gate cuts, nonunitary
encodings, a complete five-input unit or integer multiplication.

Implementation inspection uses the Build the Lever and Prove It Works
principles: the independent rerunnable Gram check is the evidence artifact.
There is no recursion or dynamic code execution. Widths are fixed, matrices
have at most 1,024 rows, each row at most 1,024 entries, and all functions are
under 60 lines. Meaningful checks remain enabled under optimization.
Managed-runtime allocation is a deviation from Power of Ten rule 3:
Python integers, dictionaries and temporary matrices allocate during the
finite check; the fixed dimension bounds live storage and each matrix is
released after its width. Rule 9's indirect-call deviation is confined to
six fixed local rejection controls. Replacing Python storage or these
callbacks is warranted only if the verifier becomes a reusable service or
accepts larger domains. Warning-strict ordinary and optimized commands are
registered; no separate Python static analyzer is configured for this package.

## Open next questions

1. How does this sharp endpoint constant propagate through a complete
   recursively substituted word? Start with one explicit composition of the
   retained ports and account for the actual intervening nonunitary mixers.
   A complete word is needed; multiplying endpoint constants blindly may lose
   cancellation and does not establish stability.
2. What is the sharp coordinatewise rounding-error amplification for the
   actual native schedule? Begin with the stated monomial and paid-call error
   channels in #4743 and retain their order. A concrete rounded Gaussian
   implementation and its error contract remain required.

The structured versions are in TASK.json. New work is Apache-2.0.
