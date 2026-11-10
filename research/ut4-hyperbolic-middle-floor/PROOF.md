# Sharp central-target tariffs from a paired middle quotient

This scoped written proof was produced by Nick Petalas. Apache-2.0.

## Statement and inherited model

Use ToikY's [PR1662](https://github.com/CrocSwap/integer-mult-bounds/pull/1662)
formal model. Let G=UT4(F2), with a=I+E12, b=I+E23, c=I+E34 and
z=I+E14. On any finite r>=w>=1 roles, every paid factor is

    I_r + ([g]+1) x y^T,   g in {a,b,c},   x,y nonzero in F2^r.

Both idempotent and nilpotent scalar couplings are allowed. The complete
endpoint is I_r+([z]+1)P, where P=diag(I_w,0), or any common scalar
conjugate of that projector. Every role has arbitrary input, every extra
role is restored, and all paid factors, including restoration, are counted.
Interleaved free scalar GL_r(F2) mixing normalizes into the couplings as in
PR1662. Augmentation forces the final free scalar map to be identity.
There are no other free address operations, COPY, ERASE or initialized roles.

Every such word satisfies the new bound

    n_b >= 2w + rank(X_b) + rank(Y_b) >= 4w.

Together with PR1662's n_a,n_c>=2w, and its direct word, this gives the
exact complete tariff for all nonnegative uniform per-letter prices:

    min cost = 2w alpha + 4w beta + 2w gamma.

In particular, the unit minimum is 8w for every finite dirty workspace.
The theorem excludes the (2,3) and (3,2) seven-b cases left open by Victor
Li's [PR3938](https://github.com/CrocSwap/integer-mult-bounds/pull/3938).
It also supplies a direct algebraic exclusion of every n_b<4w case.
No chronological search or predecessor census is a premise of this proof.

## Coefficient premises

We use PR1662's fixed degree-three algebra homomorphism

    F2[G] -> Q = F2<A,B,C>/(A^2,B^2,C^2,AC-CA, degree>=4),
    [a] -> 1+A, [b] -> 1+B, [c] -> 1+C,
    [z] -> 1+ABC+ACB+BAC+CBA.

Its fixed homomorphism lemma and the outer-letter span bound are credited
premises, not new audit deliverables. Q has the basis

    1,A,B,C,AB,AC,BA,BC,CB,ABA,ABC,ACB,BAB,BAC,BCB,CBA,CBC.

For a scalar-matrix word, write H_s for the coefficient of a basis
monomial s in its product over Q. Since ABA, ABC, CBA and CBC have no
alternative representative from AC=CA, each is the literal ordered
subsequence sum with those three labels. The endpoint therefore implies

    H_B=H_AB=H_CB=H_BA=H_BC=0,
    H_ABA=H_CBC=0,   H_ABC=H_CBA=P.                 (1)

All equations hold as full r-by-r matrices, including every dirty block.

## The new paired factorization

Number the n=n_b middle calls in product order. Write their couplings as
B_j=x_j y_j^T and put

    X = [x_1 ... x_n],             Y = [y_1^T; ...; y_n^T].

For each middle call j, let A_j^- and C_j^- be the sums of the a and c
couplings strictly before it. Let A_j^+ and C_j^+ be the corresponding
sums strictly after it. Define

    U_A = [A_j^- x_j]_j,          V_A = [y_j^T A_j^+]_j,
    U_C = [C_j^- x_j]_j,          V_C = [y_j^T C_j^+]_j,
    U = [U_A; U_C],               V = [V_A V_C].

Here X has shape r-by-n, Y has shape n-by-r, U has shape 2r-by-n,
and V has shape n-by-2r. Distributivity in the original chronological
order, without commuting scalar matrices, gives

    XY = H_B,
    UY = [H_AB; H_CB],
    XV = [H_BA H_BC],
    UV = [ H_ABA  H_ABC ] = [ 0 P ].
         [ H_CBA  H_CBC ]   [ P 0 ]              (2)

For example, every term in U_A V_C chooses one a call before middle call
j and one c call after it, so it contributes exactly once to H_ABC.
The same expansion gives the other three blocks. No assumption that an
a prefix equals its suffix is needed.

By (1), XY=UY=XV=0. Thus im(Y) is a subspace of ker(X), V takes values
in ker(X), and U vanishes on im(Y). The product UV factors through

    ker(X)/im(Y),   dimension n-rank(X)-rank(Y).

The matrix on the right of (2) has rank 2 rank(P)=2w: its two image
blocks are separate copies of im(P). Therefore

    2w <= n-rank(X)-rank(Y).                      (3)

This is the new step. Keeping only H_ABC uses a rank-w product and gives
the weaker middle quotient bound in PR1662. The zero ABA and CBC blocks
allow both cross coefficients to contribute their ranks simultaneously.

For completeness, PR1662's remaining middle span argument is short.
The H_BAC coefficient also includes the BCA subsequences because AC=CA.
Every summand starts with a b coupling. Its image is consequently in
im(X). Since H_BAC=P, rank(X)>=w. Similarly H_ACB includes CAB, every
summand ends with a b coupling, and its row space lies in row(Y).
Since H_ACB=P, rank(Y)>=w. Substitution in (3) proves n_b>=4w.

## Attainment and exact weighted optimum

PR1662's direct group word (abcb)^2=z has counts (2,4,2).
On one coordinate role the scalar coupling is the coordinate projector,
so the same word acts by z on that role and by identity on all others.
Use it separately on all w active roles. The resulting word has counts
(2w,4w,2w), implements the complete formal endpoint, and restores every
dirty role. A common free scalar conjugation gives any conjugate P.

The inherited outer bounds n_a,n_c>=2w and the new n_b>=4w hold
simultaneously for every word. The direct word attains them simultaneously,
so its tariff is minimal for any nonnegative alpha,beta,gamma. This
conclusion permits zero prices, but still concerns finite words only.
It does not price role-dependent calls or a physical implementation.

## Evidence and limitations

The universal statement is the written factorization and dimension argument.
The local verifier checks the new paired identity by two different finite
calculations: polynomial coefficient expansion and prefix/suffix arrays.
It checks attaining words against the full 64-element group algebra.
No predecessor program or stored census is imported or executed.

The result is a scoped proof in this formal operation alphabet. It is not
a native supplier, a rational-frame identity or a complete multiplication
theorem. Common-label compilation, physical realization, stock, precision,
tape, analytic recovery and all five selected framework assumptions remain
separate. No new kappa or selected-frontier change is claimed. Independent
human and formal proof-kernel review are unclaimed.
