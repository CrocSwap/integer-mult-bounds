# The coefficient polygon and all root valuations

The object under audit is the “Integral polynomial and unit roots” section
of Ali Romman's PR621, source head
`520774462b19b29af41554b74def31f9d01e997e`. Keep its notation

    r = p^a, n = r-1,
    f(z) = r P(z) = sum_(j=0)^n a_j z^j,
    a_j = product_(s=j+1)^n (1-u^s),

where p is prime, a >= 1, and u is a primitive r-th root. We include r=2,
which PR621 treats separately. The leading coefficient is one and a_0=r.
We prove a more precise version of its nonunit statement. This is a written
proof, not a proof-assistant formalization.

## Valuation and coefficient identity

Work in the complete field K = Q_p(u). Let pi=1-u. The polynomial
Phi_(p^a)(1-X), up to its leading sign, is Eisenstein at p: its constant
coefficient is p, and modulo p it is a unit times X^e, where

    e = phi(r) = (p-1)p^(a-1).

Thus pi is a uniformizer and v(pi)=1 implies v(p)=e. Extend this valuation
to an algebraic closure without renormalizing it. This standard total
ramification fact is also recorded in Keith Conrad's
[Kummer's Lemma, p. 8](https://kconrad.math.uconn.edu/blurbs/gradnumthy/kummer.pdf).

For 1 <= s < r, write s=p^h t with p not dividing t. Then

    v(1-u^s) = p^h.

Here is a direct justification. For every b prime to p, the quotient
(1-u^b)/(1-u) is a unit: its residue is b modulo pi. For h<a, factor

    1-u^(p^h) = product_(xi^(p^h)=1) (1-xi u).

Each xi u is a primitive r-th root, since its exponent relative to u is
1 modulo p. Each factor therefore has valuation one. Replacing u^(p^h)
by its t-th power multiplies by a unit for the same residue reason.
This argument also proves invariance under every primitive root choice.

Put m=r-j. Since v_p(r-t)=v_p(t) for 0<t<r,

    v(a_j) = A(m),
    A(m) = sum_(t=1)^(m-1) p^(v_p(t)).                    (1)

The integer valuation v_p(t) in (1) has v_p(p)=1; the coefficient valuation
v has v(p)=e. Keeping those two normalizations distinct is essential.

## Lower hull, including its collinear points

Let H_0=0 and H_k=k(p-1)p^(k-1) for k>=1. Counting the integers divisible
by each power of p gives A(p^k)=H_k. More generally, for
p^(k-1) <= m <= p^k,

    A(m) = (m-1) + (p-1) sum_(h=1)^(k-1) p^(h-1) floor((m-1)/p^h).

Use floor((m-1)/p^h) >= m/p^h - 1 in every summand. Then

    A(m) >= lambda_k m - p^(k-1),
    lambda_k = 1 + (k-1)(p-1)/p.                          (2)

The line in (2) joins (p^(k-1),H_(k-1)) to (p^k,H_k). All weights in the
floor sum are positive. Equality holds exactly when p^(k-1) divides m;
for k=1 the empty sum makes every integer m in the interval an equality.

Consequently, in the ascending coefficient coordinates (j,v(a_j)), the
lower convex hull has exactly the vertices

    (r-p^k, H_k),  k=a,a-1,...,0.                         (3)

Its slopes, read left to right, are -lambda_a,...,-lambda_1, which strictly
increase. Equation (2) places every other coefficient on or above the
corresponding segment, so none can create a lower vertex. For odd p there
are additional collinear coefficient points: on segment k these have
r-j = t p^(k-1), with t=1,...,p. They are contacts, not additional vertices.

## Root multiset and the audited implication

The Newton polygon theorem now gives, for each k=1,...,a,

    root valuation lambda_k = 1 + (k-1)(p-1)/p,
    multiplicity p^k-p^(k-1) = (p-1)p^(k-1).             (4)

See J. S. Milne, [Algebraic Number Theory, Proposition 7.44](https://www.jmilne.org/math/CourseNotes/ANTc.pdf),
printed p. 125. Milne orders coefficients from leading to constant, whereas
(3) orders them from constant to leading; this reverses the slope sign.
Roots are counted with multiplicity. Two useful checks on (4) are

    sum_(k=1)^a (p-1)p^(k-1) = r-1,
    sum_(k=1)^a lambda_k (p-1)p^(k-1) = a phi(r) = v(a_0).

Every lambda_k is positive. Since f is monic with algebraic integer
coefficients, all its roots are algebraic integers. Each has positive
valuation at a prime above p, so its inverse is not integral there and
it is not an algebraic unit. This confirms PR621's nonunit lemma.

For global roots, choose a prime of a splitting field above p to assign
individual valuations. The multiset is unchanged; individual assignments
need not be canonical. Under the convention v_p(p)=1, (4) is divided by e.
For example r=8 has valuations 2 (four roots), 3/2 (two), and 1 (one)
in the pi convention; its conventional values are 1/2, 3/8, and 1/4.

PR621 further excludes complex unit-circle roots because a complex
algebraic integer of modulus one has an integral inverse (its complex
conjugate), hence is a unit. Our audit confirms that implication. Positive
p-adic valuation alone is not a claim about a root's complex modulus.
We do not improve PR621's quantitative complex-circle or operator bound.

## Independent coefficient reconstruction

The second arithmetic implementation constructs a_j in Z[u]/(u^r-1)
by sparse polynomial multiplication, reduces modulo Phi_r(u), and makes
the exact integer basis substitution u=1-pi. Its result is

    a_j = sum_(i=0)^(e-1) c_i pi^i,  c_i in Z.

The nonzero summands have valuations e v_p(c_i)+i, which have distinct
residues modulo e. Therefore their minimum is unique and

    v(a_j) = min_(c_i != 0) [e v_p(c_i)+i].                (5)

This method does not sum individual factor valuations or use (1) or (2).
It checks every coefficient of every primitive embedding in the finite
r<=68 domain against (1), and a convex-hull algorithm checks (3), (4), and
the full equality locus in (2). Exact Eisenstein and small dense-polynomial
checks test the independent engine's algebraic assumptions and reduction.
Finite replay tests these implementations; the preceding argument supplies
the uniform proof.

## Scope and attribution

This is a scoped strengthening and audit of an incorporated lemma, with no
counterexample to the accepted result. A modified constant a_0=r+1 is a
unit and produces the horizontal polygon: that negative control explains
why the original tail-product hypothesis cannot simply be omitted.

Credit Ali Romman for the kernel-conditioning and nonunit argument, OpenAI
and the classical q-Pochhammer/Newton sources for the kernel, and the
standard cyclotomic and Newton-polygon theorems cited above. No literature
priority claim is made. This supplies no paid inverse or supplier, improved
κ, common-label realization, all-size compiler, precision/tape schedule, or
complete multiplication theorem. See NOTICE.md for assistance disclosure.
