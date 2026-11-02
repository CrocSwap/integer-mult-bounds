# Exact weighted price for two normal targets

This is a scoped written proof. It answers the two-target first experiment
in Open next question 1 of Krzysztof Wojt's PR5242. The earlier unit-price
semilinear theorem, scalar normalization and natural representation retain
their predecessor credit. The new contribution is the quotient-loop rigidity,
including repeated labels, and its weighted tariff consequence. Josie Elliston / PR6048
already excludes three calls for distinct pair targets in every group when
no paid label is a target. Its distinct-target floor is credited rather than
claimed as new here. The proof below does not need that predecessor as an
assumption; it also covers the repeated-label case excluded there.

## Contract

Let p be any odd prime, F = F_(2^p), and G = F* semidirect C_p, with

    (a,j)(b,k) = (a b^(2^j), j+k mod p).

Work in Mat_r(F2[G]) for any finite r >= 2. All roles start independently
arbitrary. A paid call is D_P(g) = I + P tensor ([g]+[1]), where g != 1
and P = u v^T is a binary rank-one idempotent, v^T u = 1. Free operations
are arbitrary GL_r(F2) scalar maps. The exact full formal endpoint is

    diag([h_1], [h_2], [1], ..., [1]),

where h_1 and h_2 are nonidentity normal elements, meaning (a,0), a != 1.
Repeated labels are allowed. Thus every other dirty role must be restored.
A normal call costs a > 0 and an outside call costs b > 0, uniformly within
each type. There are no other free address maps or higher-rank paid calls.

**Theorem.** The exact minimum price is 2 min(a, 2b).
In particular, the minimum number of outside-only calls is four.
The prices are arbitrary positive real numbers. They are formal complete
per-call prices within this contract, not a claimed physical supplier bill.

## A three-factor quotient lemma

Let K be any extension of F2. For i = 1,2,3 let P_i be binary rank-one
idempotents and let lambda_i be nonzero elements of K different from 1.
Set A_i = I + (lambda_i+1) P_i. Then

    A_3 A_2 A_1 = I  implies  P_1 = P_2 = P_3.

It also implies lambda_1 lambda_2 lambda_3 = 1.

Write P_i = u_i v_i^T with binary vectors and v_i^T u_i = 1.
Since A_3 is invertible,

    A_2 A_1 - I = (lambda_3^(-1)+1) P_3

has rank one. Put c_i = lambda_i+1 != 0. Direct multiplication gives

    A_2 A_1 - I = c_1 u_1 v_1^T + c_2 u_2 v_2^T
                    + c_1 c_2 (v_2^T u_1) u_2 v_1^T.

If both the two columns u_1,u_2 and the two rows v_1,v_2 are independent,
this expression factors as a full-column-rank matrix, an invertible 2 by 2
triangular matrix with diagonal c_1,c_2, and a full-row-rank matrix.
Its rank is two, a contradiction. Consequently either u_1=u_2 or v_1=v_2.
Nonzero binary vectors that are proportional over K are equal.

Suppose u_1=u_2=u. If v_1 != v_2, the product difference is

    u (lambda_2 c_1 v_1^T + c_2 v_2^T).

Both row coefficients are nonzero. Its column space is Ku, so the binary
column in P_3 must be u. Also

    span_K(v_1,v_2) intersect F2^r = span_F2(v_1,v_2).

For completeness, binary independent rows admit binary coordinate duals;
applying these to a binary vector in their K-span recovers binary
coefficients. The only possible nonzero v_3 are v_1, v_2 and v_1+v_2.
The first two are excluded because both displayed coefficients are nonzero.
The last satisfies (v_1+v_2)^T u = 0, contradicting idempotence of P_3.
Therefore v_1=v_2. The common-row case follows by transposing the two-factor
product and using the same argument in reversed order. Thus P_1=P_2.
Their product is I+(lambda_1 lambda_2+1)P_1. It cannot be I because
A_3 != I. Comparison with A_3^(-1) yields P_3=P_1 and the scalar identity.
This proves the lemma for every finite r, without a dimension census.

The binary restriction matters. Over F4, let w^2+w+1=0 and use common
column e_1 with rows (1,0), (1,1), (1,w). All three projectors are
idempotent and different. Taking lambda_i=w gives A_3 A_2 A_1=I.
The verifier checks this boundary exactly. It is outside the contract.

## Three outside calls cannot deliver the two normal targets

Move all free scalar maps to the right using

    S D_P(g) = D_(S P S^(-1))(g) S.

Augmentation [g] -> 1 sends every paid factor and the required target to I,
so the remaining free scalar product is I. Normalization preserves binary
rank-one idempotence, labels and prices. This is PR5242's normalization.

Choose a characteristic-two extension K containing a primitive p-th root
zeta. The quotient character chi(a,j)=zeta^j extends to the group algebra.
Every outside label has chi(g) != 1 and every normal target has character 1.
Thus a hypothetical three-outside-call word gives A_3 A_2 A_1=I in this
representation. The lemma forces all three normalized projectors to be P.
In the full formal algebra, their product then equals D_P(g_3 g_2 g_1).
This equality follows from P^2=P and (I-P)P=P(I-P)=0; no commutation of
the group labels is assumed.

A single such projector cannot equal the two-target endpoint. Define a
binary linear functional ell on F2[G] that sends [1] to zero and both
[h_1] and [h_2] to one. This is well-defined even when h_1=h_2, since the
normal targets are nonidentity basis labels. Apply ell entry by entry to
the difference from I. The target gives diag(1,1,0,...,0), of rank two.
D_P(g_3 g_2 g_1)-I gives a scalar multiple of P, of rank at most one.
This contradiction proves the new obstruction, including arbitrary
restored dirty workspace.

## Lower bound for arbitrary mixtures and prices

Use the natural representation rho(a,j)(z)=a z^(2^j) on F. PR5242 proves
its displacement rank is p on normal labels and p-1 on outside labels.
Rank telescoping therefore gives, for N normal and O outside calls,

    p N + (p-1) O >= 2p.

This cited premise is used without replaying the predecessor theorem.
If N >= 2, the price is at least 2a. If N=1, the inequality excludes O<=1,
so the price is at least a+2b. If N=0, it excludes O<=2, and the new
three-call obstruction excludes O=3. The price is then at least 4b.
Every legal word consequently costs at least

    min(2a, a+2b, 4b) = 2 min(a,2b).

This is a case split over all possible call counts, not a bounded search.

## Attainment

One coordinate normal call on each of the two target roles costs 2a.
Every nonidentity normal element h=(c,0) factors as

    h = (c,-1) (1,1).

Both factors are outside because p is odd. Applying the two corresponding
calls successively on the same coordinate projector gives D_(E_ii)(h).
Doing this on each target role costs 4b, restores every other role, and
attains the full formal endpoint. Replacing only one role gives the
intermediate price a+2b. Choosing the cheaper endpoint price proves the
theorem. The attaining words use no clean workspace.

## Limits and credit

The all-prime and all-workspace quantifiers rest on this written proof.
Finite checks corroborate the new quotient lemma and attaining words.
They are not independent human review or formal proof-kernel acceptance.
Three or more normal targets, mixed target lists, arbitrary per-label
prices, nonbinary free mixing and higher-rank paid calls remain outside
this theorem. No universal optimum for all semilinear target lists is claimed.

Native realization, physical movement, ownership, restoration implementation,
precision, stock/compiler, recursive and outer invoices remain unpriced.
No new kappa, supplier admission, complete multiplication theorem or
selected-frontier change follows.

This proof and its verifier were produced by Nick Petalas. Credit Krzysztof
Wojt / PR5242 for the question, quotient character, mixed unit-price theorem
and support-rigidity method; Nick Petalas / PR5202 for the normal-C7 rank
bound; Cinna Davis / PR2011 and PR3893 for the model and representation
precedent; eumemic / PR288 and the retained register-model lineage.
Josie Elliston / PR6048 supplies the distinct-label all-group short-word
obstruction, following Nick Petalas / PR6038. The source statements are
pinned as provenance in SOURCES.json.
Apache-2.0.
