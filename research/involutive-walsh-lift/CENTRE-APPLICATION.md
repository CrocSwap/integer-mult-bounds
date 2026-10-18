# Complementary centre queries after the lift

The lifted port phase resolves one specific obstruction to a reusable
centre encoder. It gives two nonzero complementary factors over the
Gaussian dyadic coefficient ring at every tensor size. The actual routed
centre maps then have an exact cross-stage annihilation law. This note
proves that law and a decoder for its joint linear map. It does not claim
that the decoder has a cheap native implementation.

## The coefficient obstruction and its removal

The one-copy Walsh source line H_q satisfies `H_q^2=iI`. The polynomial
`x^2-i` is irreducible over the Gaussian rationals: a root `a+bi`, with
rational a,b, would require `a^2=b^2` and `2ab=1`, hence `a^2=1/2`.
Thus its two-dimensional polynomial algebra over that field has no
nonzero zero divisors. In particular, a pair of nonzero linear factors
in H_q over that field cannot annihilate each other. This statement
concerns the polynomial interface; it is not a general lower bound for
all encoders or all native operations.

The doubled source is

    Q_q=i^-1(H_q tensor H_q),  Q_q^2=I.

Both eigenvalues occur. For example, each line Walsh factor has two
opposite eigenvalues, and their tensor product has both signs after
normalization. The two projections `(I+Q_q)/2` and `(I-Q_q)/2` are
therefore nonzero, with product zero. Their coefficients are Gaussian
dyadic. The formula tensors to every positive new tensor size, without
adjoining a square root or pairing replicas.

## The actual routed centre maps

Let R be the eight-row centre matrix of the pinned 112-port supplier,
and let `K=R^T/4`. To define R directly from the source word, stop at
the pre-centre cut. Express the eight centre-helper contents in the
original source, target, and helper columns. R is the coefficient block
on the 112 source columns.
Let Q be the diagonal port operator with entries Q_q. The actual route
at stage s fixes each port direction q and exchanges its eight local
perpendicular axes with the fresh block. Its doubled address route
fixes both copies of q. The cover-index route D_s consequently obeys

    D_s Q=Q D_s.

The global source replay verifies the actual routes and their exact
phases. It does not infer this relation from binary support alone.

For any invertible mode frame N_s define

    A_s=(I+Q) D_s^-1 K N_s,
    B_s=N_s^-1 R D_s (I-Q).

Then, for every pair of stages s,t,

    B_s A_t
      =N_s^-1 R D_s (I-Q)(I+Q)D_t^-1 K N_t
      =0.                                                   (1)

No relation between N_s and N_t is needed. A matrix which acts only on
the data-bank index can occur between the two factors in (1), since it
commutes with Q and the port routes. The centre matrix itself need not
commute with Q.

Equation (1) permits a mode injection through A_t to remain invisible
to every later query B_s. It is the exact property needed to prevent
earlier arbitrary mode contents from contaminating later centre
queries. It applies to all cover data and all borrowed mode values.

## A decoder with no extra query array

The following linear lemma states the resulting construction target.
Let W be an invertible ideal data-bank controller. Let T stack the
queries of its ideal prefixes. Let L collect the corresponding mode
injections after propagation through the ideal suffixes. Suppose

    T W^-1 L=0.                                             (2)

Equation (1) proves (2) when the intervening ideal bank operations have
the stated port-independent form. Let J select those cohorts whose
data error uses their updated mode value. The other cohorts use their
incoming mode value. Thus J is diagonal with entries zero or one.

If one use of each cohort gives the joint map

    d'=W d-L h-L J T d,
    h'=h+T d,                                              (3)

then the following three shears restore every incoming mode h:

1. `d' <- d'+L J h'`.
2. `h' <- h'-T W^-1 d'`.
3. `d' <- d'+L(I-J)h'`.

After step one, the data are `W d-L(I-J)h`. Equation (2) makes the
query in step two equal to T d, so the modes become h. Step three then
returns W d. Every step is reversible. There is no clean-mode
assumption and no extra array for the value T d. Each cohort injects
once, before or after the shared extraction according to its J entry.

This decoder is a general linear identity. The exact retargeted
supplier now permits its annihilation hypothesis at every stage. The
remaining physical obligations are the implementation of the local
birth map in (3), access to `T W^-1`, legal mode injections L, completed
mode histories, arbitrary-state restoration in their native frames,
and a complete changed-word invoice. The unchanged-word invoice in
this package does not pay for those operations.

Research and verification used substantial OpenAI Codex assistance.
