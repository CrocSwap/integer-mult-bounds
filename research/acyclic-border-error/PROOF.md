# Bounded acyclic selectors retain their rank rows

This is a scoped proof over the real or complex numbers. The rational program
corroborates finite instances. No predecessor scientific executable is run.

## 1. Sharp envelope

Fix n>=2 and L>=1. Define

    f(e) = e sum_{k=0}^{n-1} (1+L-e)^k.

There is a unique a=a_n(L) in (0,1/n) with f(a)=1. For every complex
n by n matrix A satisfying, in a single coordinate order,

    |A_ii - 1| <= e,
    |A_ij| <= L       if i<j,
    |A_ij| <= e       if i>j,

e<a implies rank A=n. The cutoff is sharp for this envelope. At e=a,
the real matrix with diagonal 1-a, every upper entry -L and every lower
entry -a has rank exactly n-1. For n=1 the cutoff is exactly one.

On [0,1/n], put q=1+L-e>=1. Each summand in the derivative

    f'(e) = sum_{k=0}^{n-1} q^k - e sum_{k=1}^{n-1} k q^{k-1}

is positive, since q-ek>0. Also f(0)=0 and f(1/n)>1. On (1/n,1],
f(e)>=ne>1. This proves existence and uniqueness in the stated interval.

Let B have entry L above the diagonal and e on or below it. Set
w_i=q^{n-1-i}, with indices starting at zero. Direct row subtraction gives

    (I-B)w = (1-f(e)) 1.

Thus w>0 and Bw<w when e<a. If Az=0 for nonzero z, choose i maximizing
|z_i|/w_i=t>0. The hypotheses give

    |z_i| = |((I-A)z)_i| <= t(Bw)_i < t w_i = |z_i|,

a contradiction. Absolute values make this valid for complex entries.

At e=a the displayed real matrix is I-B and has kernel vector w. Replace
row i by old row i minus old row i+1 for i=0,...,n-2, leaving the last row
unchanged. This determinant-one row transformation gives the independent
first n-1 equations z_i-q z_{i+1}=0. The last becomes
(1-f(e))z_{n-1}=0. Therefore det(I-B)=1-f(e), and its boundary rank
is exactly n-1. This proves sharpness over the full directed triangular
envelope. It does not assert that a symmetric P112 mask attains it.

## 2. Rational attainment and growth

For rational q>=2 and n>=2 set

    S=sum_{k=0}^{n-1} q^k,   e=1/S,   L=q-1+e.

All entries of I-B and its kernel vector are rational, L>=1, and f(e)=1.
For n=8,q=2 this gives e=1/255, L=256/255 and rank seven. These are
boundary fixtures, not P112 decoder constructions.

At the cutoff q=1+L-a>1, the geometric-sum identity gives

    a(1+L-a)^n=L,
    L/(1+L)^n < a <= L^{-(n-1)},
    a L^{n-1} -> 1 as L -> infinity, for fixed n.

The bounds follow from L<=q<1+L; the limit follows from q/L->1.
The exponent n-1 is therefore sharp. A simpler necessary condition for
a singular matrix is e>=a>1/(2^n L^{n-1}). If e<=2^-p and L<=2^b,
singularity requires p<n+(n-1)b. This is a magnitude constraint, not a
physical precision or tape-cost theorem. The asymptotic assertion fixes n.

## 3. Transfer to an approximate AGLB row

DreamingOfClouds's PR5559, PROOF.md section 5, uses an acyclic generalized
Lemma B, abbreviated AGLB. Retain its exact support, price and certificate
statements as predecessors. We extend one rank row; we do not re-establish
its enumerations, LP bounds or COPY64 claims.

Let B0 be a zero-one mask with unit diagonal. Let J be a zero-one selector
which is one on B0 and nonzero outside B0 only on directed acyclic arcs.
Let the subtotal to which the row is applied be

    M_paid=sum_{k=1}^m p_k q_k^T.

Assume |(M_paid)_ij-delta_ij|<=e on B0 and |(M_paid)_ij|<=L on the
extra selected arcs, with L>=1. A topological order puts those arcs above
the diagonal. C=J Hadamard M_paid satisfies section 1, since e<a<=1<=L.
Consequently, for e<a,

    n = rank C
      <= sum_k rank( diag(p_k) J diag(q_k) )
       = sum_k rank J[supp p_k, supp q_k].

These ranks are over the coefficient field, not F2. Exact supports justify
the final equality, including empty supports. The same reasoning applies
to each principal-subset row at its own dimension. A cost certificate using
only these rows and inequalities valid independently of the exact decoder
equations transfers when every rank row meets these hypotheses. Exact-only
off-diagonal cover and coefficient-ratio clauses do not automatically
transfer. This is a conditional rule, not a replay of any cost certificate.

If zero-price terms are omitted in the exact argument, M_paid MUST be the
subtotal after that omission. A final-total bound does not suffice. In the
n=2 rational family above, adding L E_01, a free term for the directed
diagonal-and-lower mask, cancels the large upper entry and leaves a bounded
invertible lower triangular total. The paid subtotal is still singular and
has magnitude L. This is a directed-mask example, not a P112 realization.

If m is fixed and every factor entry has magnitude at most H, subtotal
entries have magnitude at most m H^2. Take L=max(1,m H^2). A deficient
AGLB row at error tending to zero forces unbounded factor magnitude.
Once m H^2>=1 it requires

    H > [1/(2^n e m^{n-1})]^{1/(2(n-1))}.

No unrestricted border-cost floor, physical cost for these coefficients,
native realization or new kappa follows.

## 4. Prior mathematical methods

Absolute-value comparison and scaled diagonal dominance are classical
interval-matrix methods. See Jiri Rohn, *Forty necessary and sufficient
conditions for regularity of interval matrices: a survey*, Electronic
Journal of Linear Algebra 18 (2009), 500-512, especially Theorem 4.1(ii):
https://journals.uwyo.edu/index.php/ela/article/view/655 . That theory retains
credit. No general literature-priority claim is made for interval regularity.
The contribution is this explicit envelope, its rational attainment and
growth law, and the paid-subtotal transfer to decoder rank rows left outside
PR5559's exact-only argument.
