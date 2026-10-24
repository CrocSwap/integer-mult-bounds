# Mixed-sign orthogonal phase spectrum

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Contract and theorem

Let V=F2^n for n>=1 with its ordinary dot product. All vector sums and matrix
operations below are binary unless a congruence or integer weight is written.
Fix a sign mask b in V and put

    q_b(x) = wt(x) + 2 b·x modulo 4.

The dot product b·x in this formula is either 0 or 1. Its polarization is

    q_b(x+y) = q_b(x)+q_b(y)-2 x·y modulo 4.

For S in O(n,2), define the row-convention phase defect d_b(S) by

    q_b(S^T x)-q_b(x) = 2 d_b(S)·x modulo 4.                 (1)

The difference has zero polarization, hence is additive; its values are even
because S preserves x·x. Thus there is a unique binary d_b(S).

**Theorem.** The exact attainable set is

    D_b = {e : q_b(e)=0}
        = {e : wt(b+e) == wt(b) modulo 4}.                  (2)

For every e in D_b, the symmetric orthogonal involution

    T_e = I + e e^T

has d_b(T_e)=e. Every S has a unique factorization

    S = T_e H,       e=d_b(S),       d_b(H)=0.              (3)

Each fiber has size |O(n,2)|/N_(n,r), where

    r = wt(b) modulo 4,
    N_(n,r) = sum_{0<=k<=n, k==r modulo 4} binomial(n,k).

These are exact algebraic counts and a written scoped proof. They do not
price a physical chart change or establish supplier admission.

The equal-sign case b=0, its transvection representative and orthogonal-group
order are Philipp / mightyOil's PR1300. Gareth Davidson's PR1255 supplies the
residual gate and row-defect conventions. The present addition is arbitrary
fixed mixed signs, their changed image and stabilizer, and the corresponding
literal signed-kernel contract. Classical quadratic-refinement and Gauss-sum
methods are not claimed as new mathematics independent of this application.

## Necessity from an exact Gaussian sum

The sum over all x of i^(q_b(x)) factors coordinatewise as

    G_b = (1+i)^(n-wt(b)) (1-i)^wt(b)
        = (1+i)^n (-i)^wt(b).

It is nonzero. Since S^T permutes V, equation (1) gives G_b=G_(b+e), for
e=d_b(S). Dividing their displayed nonzero expressions shows

    wt(b+e) == wt(b) modulo 4.

No floating-point phase comparison or assumption on the weight of e alone
is involved. Writing h for the integer number of common 1-bits of b and e,

    wt(b+e)-wt(b) = wt(e)-2h == q_b(e) modulo 4,

because 2h modulo 4 equals twice the binary dot product. This proves the
equality of the two descriptions in (2). In particular every admissible e
has even weight.

## A representative for each admissible defect

For even-weight e, e·e=0. Direct multiplication shows

    T_e^T=T_e,       T_e^2=I,       T_e^T T_e=I.

Set a=e·x in {0,1}. Polarization gives

    q_b(T_e x)-q_b(x) = a (q_b(e)-2) modulo 4.

If e is admissible, q_b(e)=0, so this difference is 2e·x. Equation (1)
therefore gives d_b(T_e)=e. This includes e=0 with T_0=I and proves
sufficiency for every n and every sign pattern. A nonzero admissible defect
is corrected by one algebraic rank-one transvection, and cannot be corrected
by zero such transvections. This counts algebraic factors only.

The transported sign term can also be read directly from PR1300's defect:

    d_b(S) = d_0(S) + b + S b.                             (4)

For even e it yields

    d_b(T_e) = (wt(e)/2 + 1 + b·e) e,

where the coefficient is reduced modulo two. Dropping b+Sb incorrectly
reuses the equal-sign criterion.

## Cocycle, normalization and exact fibers

Apply (1) first to B^T A^T x, then to A^T x. The result is the twisted cocycle

    d_b(AB) = d_b(A) + A d_b(B).

Let e=d_b(S). Since T_e e=e, the cocycle gives

    d_b(T_e S) = e + T_e e = 0.

Thus H=T_e S proves (3). The e in (3) is prescribed by S, so H is unique.
The zero-defect maps form a subgroup. Conversely every such H satisfies

    d_b(T_e H)=e.

Multiplication by T_e is therefore a bijection from this subgroup to the
e fiber. All fibers have equal size. Translation e -> b+e identifies the
image with all binary vectors of weight congruent to wt(b) modulo four,
which gives N_(n,r) and the claimed stabilizer count.

For concrete counts use PR1300's credited recurrence

    O_1=1,       O_n=(2^(n-1)-[n odd]) O_(n-1) for n>=2.

At n=6 with one negative axis, N_(6,1)=binomial(6,1)+binomial(6,5)=12.
There are 23040/12=1920 exact preservers. The equal-sign case instead has
N_(6,0)=16 and 1440 preservers. These are counts of bases, not a cost saving.

## Literal signed residual

For orthonormal independent active directions u_1,...,u_n, take the product
of the commuting gates

    C_u^(s) = ((1+s i) I + (1-s i) X_u)/2,
    X_u f(x)=f(x+u),       s_j=(-1)^b_j.

Independence makes every displacement Ux have one subset expansion. Hence
its exact convolution coefficient is

    K_(U,b)(Ux) = c_b (-i)^q_b(x),
    c_b = ((1+i)/2)^n (-i)^wt(b).

For V=US with S orthogonal, coordinates of Ux in V are S^T x. Equation (1)
then gives

    K_(US,b)(Ux) = (-1)^(d_b(S)·x) K_(U,b)(Ux).

The fixed sign mask indexes the chart's columns on both sides. Permuting
signs with the axes is a different comparison. The all-nonzero coefficient
formula proves exact equality iff d_b(S)=0. The convolution commutes because
binary translations commute, without a native implementation assumption.

At n=5, let b=e_1 and e=e_1+e_2. Then q_b(e)=0 and d_b(T_e)=e, although e
has weight two. The same transvection has d_0(T_e)=0. Thus the mixed-sign
boundary differs even for a coordinate swap. Conversely e=e_1+e_2+e_3+e_4
has weight four but d_b(T_e)=0, so it is not its own mixed-sign defect.

## Remaining obligations

This proof treats an orthonormal active chart and fixed signed C gates.
It neither generalizes to every nonorthogonal chart nor prices native maps,
physical routes, source acquisition, dirty restoration, precision, stock,
fixed tapes or a complete recursive consumer. No selected-frontier change,
new kappa or complete multiplication theorem follows. The finite verifier
corroborates (1)-(4); the written argument supplies their universal quantifiers.
