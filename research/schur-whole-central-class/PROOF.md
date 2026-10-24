# Reconstruct the whole central operator from the sharp image

## Contract and statement

Work over any field F. Let P,Q be commuting idempotents with a common leading
identity block I_d. Let S,T be their Schur complements on a residual space V
of dimension m. Put H=(PQ)_11, K=ST-TS, Z=(S-T)^2, and require rank K=2d.
This is the sharp-image hypothesis. It is not optional.

The complete similarity class of Z is determined by H, m and the one integer

    a_1 = dim(ker S intersect ker(T-I))
          + dim(ker(S-I) intersect ker T).

The result concerns the central operator Z. It does not classify the ordered
pair (S,T), count headers or give a probability law. It covers nonnilpotent H,
non-split primary components, repeated roots and characteristic two.

The credited block action in ssafwann's [PR #5256](https://github.com/CrocSwap/integer-mult-bounds/pull/5256)
identifies M=im K with F^(2d). Set J=H(I-H) and Theta=2H-H^2. In this basis,

    D = Z|M = diag(Theta,Theta),
    B = K|M = [ J   2(I-H); -J  -J ].                 (1)

The second equation follows by taking the commutator of the source's ordered
matrices U_H and V_H. Thus B and D commute and B^2=D(D-I). The unchanged
source proof and fixture construction are retained in vendor, with exact
original and retained-history pins. Their proof and attribution remain intact.

For lambda=0,1, let M_lambda=ker(D-lambda I)^(2d). Compute the nilpotent Jordan
block sizes j_(lambda,1),...,j_(lambda,c_lambda) of B on M_lambda. Set

    a_0 = m-2d-a_1.

Then the lambda-primary Jordan blocks of Z are:

- for each j_(lambda,i), one block of length ceil((j_(lambda,i)+1)/2)
  and one of length floor((j_(lambda,i)+1)/2);
- a_lambda-c_lambda additional blocks of length one.

The remaining primary part is exactly D restricted to
im((D(D-I))^(2d)). This is an invariant complement to M_0+M_1 and gives a
representative over F itself. No splitting field is needed for this part.
For an admitted source pair, both extra multiplicities are nonnegative.

## Proof

For any two idempotents S,T, direct expansion gives

    K^2=Z(Z-I),    ZS=SZ,    ZT=TZ,
    KS=(I-S)K,    KT=(I-T)K.                           (2)

These are credited projector identities from the retained Schur lineage.
In particular ker K is invariant under both S and T. Their restrictions
commute on ker K. The four joint eigensectors therefore split ker K over
every field, including characteristic two. On the equal sectors 00 and11,
Z is zero. On the opposite sectors 01 and10, Z is identity. Rank-nullity gives

    dim ker K = m-2d = a_0+a_1.                       (3)

Decompose V into its Z-primary spaces at0, at1, and away from these endpoints.
On the last part, Z(Z-I) is invertible. Equation (2) makes K invertible there,
so that entire part is contained in im K. Its Z action is therefore exactly
the non-endpoint restriction of D in (1).

On V_lambda, lambda=0 or1, K is nilpotent: its square is the product of a
nilpotent operator and a commuting invertible operator. Moreover
M intersect V_lambda is im(K|V_lambda). On ker K within V_lambda, equation
(2) forces Z=lambda I, so the kernel dimension of K|V_lambda is a_lambda.

A nilpotent Jordan block of K of length ell>=2 induces on its image a block
of length ell-1. A block of length one has zero image. Thus every block j of
B|M_lambda comes from exactly one block j+1 of K|V_lambda. The remaining
blocks of K have length one, and their number is a_lambda-c_lambda.

The factor of Z(Z-I) other than Z-lambda I is invertible on V_lambda and
commutes with K. Therefore, for every positive integer r,

    rank((Z-lambda I)^r | V_lambda)
       = rank(K^(2r) | V_lambda).                    (4)

These ranks determine the nilpotent Jordan partition. Squaring a nilpotent
block of length ell splits its chain into the odd and even positions, with
lengths ceil(ell/2) and floor(ell/2); omit a zero-length chain. Apply this to
the reconstructed K blocks. The formula in the statement follows.

This is a complete similarity classification of Z under the stated contract.
It does not require a choice of how complementary vectors attach to M.
The integer a_1 is also recoverable from the full class, since

    dim V_1 = dim M_1 + a_1.

It cannot in general be omitted. Append one scalar00 sector or one scalar01
sector to the same admitted pair. Both operations preserve H, sharpness and
the new residual dimension. The first appends a zero eigenvalue to Z; the
second appends an eigenvalue one. Their characteristic polynomials differ.
The verifier retains this same-H, same-dimension control.

## The open characteristic-two nilpotent case

Suppose char F=2 and H is nilpotent with block sizes k_1,...,k_a, where
sum k_i=d. Then Theta=H^2, and (1) becomes

    B = diag(H(I-H),H(I-H)) [I 0; I I].

The second factor is invertible and commutes with H. Since I-H is invertible,
rank B^r = 2 rank H^r for every r. Thus B has two copies of every nilpotent H
block. The complete central partition is consequently

    sum_i [2 J_ceil((k_i+1)/2)(0) + 2 J_floor((k_i+1)/2)(0)]
    + (m-2d-a_1-2a) J_1(0) + a_1 J_1(1).            (5)

This answers the explicitly open characteristic-two question in ssafwann's
[PR #5267](https://github.com/CrocSwap/integer-mult-bounds/pull/5267).
For its nilpotent profile

    (r00,r10,r01,r11)=(d+s00,d+s10,d+s01,d+a+s11),

that predecessor's all-field representative gives a_1=s10+s01 and
m=3d+a+s00+s10+s01+s11. The extra zero-block count in (5) is therefore
`d-a+s00+s11`, and the extra one-block count is `s10+s01`.
The predecessor already proves the whole ordered-pair rigidity, its odd-field
k/(k+1) law and the fixed-H weights. None is claimed again here.

For the padded H=J3 fixture, (5) gives `(2,2,2,2,1,1)`. Its whole central
minimal polynomial is t^2. In odd characteristic the credited partition is
`(4,3,1,1,1)`, with minimal polynomial t^4. Division by two would give the
wrong characteristic-two answer.

## Computation, evidence and trust

[central.py](central.py) computes the two primary subspaces in dimension2d,
the nilpotent B rank sequences, and an explicit non-endpoint restriction.
Its current scalar implementation supports F2,F3,F5,F7. The written theorem
applies to every field. The function requires the stated source contract;
H,m,a_1 alone are not a proof that a proposed original pair is admissible.

The verifier constructs full source pairs with the frozen credited helper,
then independently forms their Schur complements and checks the original
premises and sharp rank. It computes full characteristic polynomials through
integer-lift Faddeev-LeVerrier, factors them over the small prime field, and
checks all primary power-rank partitions using a separate column-elimination
routine. These full-matrix invariants are compared with the proposed complete
representative. Non-split repeated factors and mixed primary examples prevent
scalar-eigenvalue sampling from serving as the acceptance test.

The generic nilpotent-image and squared-Jordan arguments are classical linear
algebra, not claims of global novelty. The new result is their complete
application to the sharp block-Schur central contract and the explicit
characteristic-two partition. Written proof, exact scalar arithmetic, Python
and source transcription remain in the trust base. Finite corroboration is
not independent human or proof-kernel acceptance. Nonsharp pairs, full ordered-
pair classification for general H, header weights, native realization and
all physical consumer costs remain outside scope. No kappa or frontier change.

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.
