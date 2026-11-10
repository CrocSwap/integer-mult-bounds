# The full one-query width threshold

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract

Let M be positive, let K be nonnegative, and let Q,N be invertible M by M
matrices over a field. Both carrier inputs and all K helper coordinates are
arbitrary and independent. The required complete endpoint is

    C = [[Q-I, N], [Q, 0]],       T = C direct-sum I_K.

The helper endpoint is the identity on its actual input. There is no promise
that helpers start at zero. C is invertible: given outputs (a,b), first recover
x=Q^-1 b and then y=N^-1(a-(Q-I)x).

A single coordinate query J_W(U) acts by an arbitrary w by w matrix U on a
chosen coordinate subset W of size w and by the identity on its coordinate
complement. It has no cross blocks. W may meet several original banks. This
grants at least as much freedom as a query restricted to one physical bank.
The candidate factorization is

    T G = F J_W(U),                                             (1)

where F,G are invertible endpoints on all 2M+K coordinates. U is unrestricted;
equation (1) would itself force it to be invertible.

Fix positive support limits s,t. In each of the two carrier row blocks, every
physical column of G has at most s nonzero entries, and every physical column
of F has at most t. There is no sparsity restriction on helper row blocks.
Assume the following separation property for each A in {Q,N}:

    v != 0 and |supp(v)| <= s imply |supp(A v)| > t.             (2)

## Theorem

Under this contract every factorization (1) has

    w >= 2M.                                                   (3)

In particular no width M<w<2M is sufficient. The theorem holds for any finite
K, any positions of queried coordinates, and any invertible endpoint helper
blocks. It does not assume monomial endpoints or full-bank query alignment.

### Proof

For each j outside W, the query leaves the basis column e_j unchanged. Write
the carrier components of G e_j as (g_0,g_1). Equation (1) says

    (Q-I)g_0 + N g_1 = (F e_j)_0,
               Q g_0 = (F e_j)_1.

The support bounds and (2) first give g_0=0 from the bottom equation. The top
equation then gives g_1=0. Thus G sends every unqueried coordinate basis
vector into the helper coordinate subspace.

Those 2M+K-w vectors are linearly independent because G is invertible. The
helper subspace has dimension K. Consequently 2M+K-w<=K, proving (3).
This is the complete new dimension step. In particular it does not use the
older sufficient restriction w<=M. No endpoint or native tariff is inferred.

## Complex unitary specialization

For a unitary A with maximum entry modulus mu, the classical support
uncertainty inequality is

    |supp(v)| |supp(A v)| >= mu^-2       for v != 0.

Indeed each output coordinate is bounded by mu sqrt(|supp(v)|) ||v||_2;
summing over its support and using unitarity proves the inequality. Therefore
(2) holds whenever

    s t < min(mu_Q^-2, mu_N^-2).                                (4)

This is a strict inequality. The theorem proves the combined necessary
condition

    w >= 2M   or   s t >= min(mu_Q^-2, mu_N^-2).                 (5)

Ross Richardson's PR4057 supplies the native setting in which Q_f,N_f are
unitary with mu_Q_f=mu_N_f=2^-f. Its native amplitudes and operator recipes are
cited premises, not results checked again here. In that setting (5) becomes

    w_f >= 2M_f   or   s_f t_f >= 4^f.                          (6)

Thus the predecessor's support obstruction extends from queried widths at
most M_f to every width below 2M_f. Under its support-doubling ADD contract,
s_f<=2^a_G and t_f<=2^a_F, equation (6) also implies

    w_f < 2M_f implies a_G+a_F >= 2f.

The constant 2f is inherited. The new part is the complete width range on
which that necessary condition applies.

If the carrier endpoint blocks have fixed column-support bounds h_G,h_F,
every f with 4^f>h_G h_F requires w_f>=2M_f. In particular a sum of at most
h_G or h_F physical monomial terms in each such block has these bounds.
This includes the predecessor's fixed finite uniform-tensor dictionaries
whenever the stated carrier-block representation applies. Arbitrary growing
helper dimensions do not change the dimension argument. Rectangular helper
interfaces must still satisfy the explicit per-column bounds; a square-block
dictionary is not automatically a representation theorem for those interfaces.

## Exact boundaries

The width threshold is sharp in the relaxed coordinate-query model. With
F=G=I, take W to be all 2M carrier coordinates and U=C. Helpers remain exactly
unchanged. For a nonmonomial unitary with mu<1 the support bounds s=t=1
satisfy (4), so the lower threshold and this algebraic attainer coexist.
This arbitrary 2M-dimensional query is not a native implementation, paid word
or physical merger of two banks.

The strictness of (4) is necessary. Let Q=N=H_4/2, where H_4 is the four by four
Walsh sign matrix. Then mu^-2=4. Choose G=I, F=C and an empty query. Every
carrier block column of F has support at most four; G's have support at most
one. Equation (1) holds at s t=4 with w=0. Replacing < by <= would be false.

Separation is necessary too. If Q=N=I, then C is the swap of the carriers.
It is monomial. F=C, G=I and an empty query work with s=t=1. The finite checker
executes these boundary examples exactly, including the rational unitary.

## Attribution and limits

The triangular carrier, untouched-column equations, support-uncertainty
method, native four-flatness, and earlier w<=M statement are Ross Richardson's
PR4057 at bf793d8739ad26f2aaba023de6bebca50fc67356. This contribution extends
its width domain and states the sharp threshold in a relaxed coordinate-query
contract. Rank-nullity and the uncertainty inequality are classical.

There is no claim about a query on an arbitrary dense linear subspace,
interleaved multiple queries, a changed carrier map, discarded helpers, free
dense endpoint maps, or a rounded approximate endpoint. All such changes need
their own proof. No native realization, stock, tape, precision, ownership,
uniform compiler, supplier admission, new kappa, or complete multiplication
theorem is supplied. The universal statement rests on this written proof;
finite examples corroborate it and are not a formal proof-kernel check.
