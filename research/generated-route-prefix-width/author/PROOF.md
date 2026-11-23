# Structural prefix certificates for the generated two-output producer

## 1. Claim and source boundary

Fix the admitted source grammar in #8092 at
`6a3437d1cd94dc4e1792f4052511af6160120bf9`, over canonical
`e54523517d0f03e58352e647c403a5af3e525a57`. Its retained `factor_words.emit`
specifies the exact chronology for literals, inverses, products, direct sums,
tensors, identity extension, permutations, conjugations and carried guards.
The first two-output package supplies the independently reviewed elementary
producer for the actual 94 addition coefficients and 15 dyadic scales.
Exact source hashes are in ORIGINS.json.

We give a computable certificate (d,e) for **every prefix of both the forward
and inverse emitted word**, including prefixes ending inside an individual
copy. For each such right-action matrix M,

    2^d M has integer entries, and ||M||_1 <= 2^e,

where ||M||_1=max_j sum_i |M_ij| is the maximum column-sum norm and d,e are
nonnegative integers. Tensor and guard copy multiplicities do not multiply
these bounds. The certificate follows the compact recipe rather than its
expanded operation count.

For any supplied canonical low row x, odd q>=3 and emitted prefix, the exact
carry C=(xM-(xM mod q))/q then has a common denominator 2^d and numerator
absolute value below 2^(d+e+1). The two-output producer can use that **fixed
denominator from the start**, with at most d+e+9 signed work bits. It combines
the entire update numerator before dividing exactly by a small power of two.
No individual summand is assumed divisible.

This is a partial discharge of a temporary-width implication for the actual
generated grammar. It does not prove that arbitrary recipe certificates are
O(log N), establish a selected private-H grid, route a complete payload,
return native owners, or remove a canonical assumption. All five selected
assumptions and the selected conditional kappa remain unchanged.

## 2. Leaf certificates and structural rules

For each admitted literal word, evaluate its finitely many forward and inverse
prefixes in exact dyadic arithmetic. Let d be the largest power-of-two
denominator exponent of any entry. Choose e>=0 so every maximum column-sum
is at most 2^e. This finite seed computation has an explicit exact algorithm;
we do not claim an observed global maximum for the full seed inventory.
The source's fixed finite seed set makes these finite constants. A supplied
arbitrary literal is not thereby admitted as a new source seed.

Identity and permutation recipes have certificate (0,0), since every emitted
prefix is a permutation matrix. For pairs write addition and maximum
coordinatewise. The remaining rules are

| Source constructor | Certificate |
| --- | --- |
| inverse(A), extend(A) | cert(A) |
| direct_sum(A,B) | max(cert(A),cert(B)) |
| multiply(A,B), tensor(A,B) | cert(A)+cert(B) |
| conjugate(T,A) | 2 cert(T)+cert(A) |
| guarded(S,C,rank) | cert(S)+2 cert(C) |

Both denominator exponents and logarithmic norm bounds obey these rules.
They are sufficient upper bounds; cancellation is not required.

### Products and direct sums

Products of matrices with integer-scaled denominators 2^a and 2^b have
denominator dividing 2^(a+b). The column-sum norm is submultiplicative.
A product prefix is a child prefix, or a completed first child times a
prefix of the second. The inverse word visits the children in reverse order
and in inverse direction. Because the certificate covers both directions,
the same sum works.

A direct-sum prefix acts in one block while completed/untouched blocks act
independently. The common dyadic exponent is their maximum, and the norm of
a block diagonal matrix is the maximum block norm. This remains true when
the inverse emitter reverses the block order. Identity extension is the
same argument with an identity block.

### Tensor chronology, including partial copies

The actual emitter first runs A on each column fibre, then B on each row
fibre. In the first phase, completed copies of A, one prefix of A and untouched
identity copies act on disjoint coordinate sets. Up to a permutation of
coordinates, their matrix is block diagonal. Its certificate is cert(A),
independent of the number of fibres.

At the end of the first phase the matrix is A tensor I. A partial second
phase is a block diagonal collection of copies of B, one B-prefix and
identities. Its certificate is cert(B). Multiplying gives the sum rule.
The inverse emitter reverses phase order, copy order and child words. The
same two-phase argument applies with inverse children. This proves the
claim for every elementary prefix, not only phase endpoints.

### Conjugations and carried guards

The literal conjugation chronology is T, A (or A^-1), T^-1. Applying the
product argument to these three phases gives 2 cert(T)+cert(A), including
prefixes inside either boundary copy.

For a guard, H=I tensor C is emitted first. Its certificate is cert(C).
The middle phase applies S to `rank` coordinate fibres indexed by j; the
sets {i*C.n+j : i} are disjoint. A partial middle phase is therefore a direct
sum of completed S copies, one S-prefix and identities, with cert(S), even
when rank=0 or full rank. The final H^-1 gives cert(S)+2 cert(C). Inverse
emission reverses the middle fibre order and uses S^-1, while retaining H
and H^-1 as the boundary phases. The same rule covers it. No orthogonality
of the carried sector basis is assumed.

These cases exhaust the retained emitter. Permutations introduced by tagged
sum/tensor, splitting and placement are explicit swap recipes, so their
certificate remains (0,0); physical relabeling is not silently made free.

### Ordered additions and signed scale atoms

The same certificate also covers `expanded_ordered_ops`, the source's physical
lowering into ordered additions and signed dyadic scale atoms. An upper
addition A is emitted as P,L,P with a coordinate transposition P and
A=P L P. Starting from a prefix X, its two extra intermediate products are
X P and X P L=X A P. These are column permutations of the pre/post matrices,
so neither their common denominator nor their column-sum norm increases.

A signed dyadic scale is split into repeated factors of magnitude two or
one half, with the sign on the first atom; a scale of -1 is one atom.
The absolute entries in that column vary monotonically between their pre/post
magnitudes. Under repeated halving the denominator exponent is bounded by
the final exponent; under repeated doubling it is bounded by the initial
exponent. Signs do not affect either bound. Thus every added partial atom
is covered too. This is a connection to the actual lowered instruction
interface, not a proof that the complete payload route has been executed.

## 3. Carry denominators and widths

Let y be the canonical residue row xM mod q, and D=2^d. Since q is odd, D is
invertible modulo q. D xM and D y are integer rows congruent modulo q.
Consequently p=D(xM-y)/q is an integer row. The column-sum norm gives

    |(xM)_j| <= max_i(x_i) ||M||_1 < q 2^e,
    |C_j| < 2^e+1,
    |p_j| < 2^d(2^e+1) <= 2^(d+e+1).

The norm must be the maximum **column** sum because x is a row and its
infinity norm is used. Replacing it by maximum row sum would need an extra
dimension factor and would not establish this bound.

For an elementary addition with coefficient a/2^s, let c be the integer
carry numerator returned by the reviewed elementary low producer:

    2^s l_i + a l_k = 2^s l'_i + q c.

The fixed-denominator high register update is

    p'_i = (2^s p_i + a p_k + c 2^d) / 2^s.

For a scale it is

    p'_i = (a p_i + c 2^d) / 2^s.

Other numerator coordinates remain unchanged; a swap exchanges its two
numerators and low digits. Initial numerators are zero. Induction proves
these equations give D times the exact prefix carry. The next prefix has
denominator dividing D by Section 2, so the **combined** numerator is divisible
by 2^s. This remains valid when d<s or when individual terms are odd.
An implementation checks the s low bits before shifting the signed integer.

For the actual alphabet, 2^s+|a|<=55 for additions; scale |a|<=16 also fits
this bound. The elementary carry numerator satisfies |c|<=54. First combine
the old-register terms, whose joint magnitude is below
55*2^(d+e+1); then add c*2^d. The entire intermediate is below

    110*2^(d+e) +54*2^d <=164*2^(d+e) <2^(d+e+8).

Thus d+e+9 signed bits suffice for every arithmetic intermediate, while
stored numerators need at most d+e+2 signed bits. Division by 2^s and the
zero-bit divisibility test introduce no wider integer. The low producer's
separate finite state and B=bit_length(q) input/output channels are unchanged.

The update does not replace q-adic cocycle identities or prove them anew.
#5841 already gives the exact low/carry identities and a column-denominator
bound. The contribution here is the source-grammar certificate for **all
emitted prefixes**, especially partial tensor/guard copies, and its use in
a fixed-denominator integer producer rather than accumulated denominator
inflation proportional to the expanded number of gates.

## 4. Tensor family and limits

For a fixed admitted b-dimensional base recipe A, b>=2, with certificate
(d0,e0), the recursively formed r-fold tensor power has N=b^r and certificate
(r d0,r e0). Its signed work width is at most r(d0+e0)+9=O(log N).
If its word has m0 nonswap instructions, the emitted tensor word has
m_r=r b^(r-1) m0. Thus the prior 6m_r+5 bound can grow with an exponentially
expanded word while this certificate grows only linearly in r.

This statement is only for fixed-base tensor families and other recipes whose
certificate has separately been bounded. Arbitrary repeated products or
conjugations can have much larger d,e. A small endpoint matrix alone does
not bound its prefixes: a word can grow a coefficient enormously and then
cancel it. Certificate computation cannot use endpoint cancellation to omit
the intermediate bound.

## 5. Access bill, evidence and remaining work

Certificate arithmetic consists of finite exact seed-prefix evaluation plus
max/add operations over the compact recipe; these operations and the recipe
storage remain charged work. No table over all low matrices is produced.
For each supplied row, each nonswap uses the same two complete B-bit reads
of the relevant low channels and q, the same elementary comparator work,
and one bounded full-numerator update. An addition uses two shifts, one
multiplication by a fixed small integer, two additions, a divisibility check
and an exact signed shift; a scale uses one
small product, one shift, one addition and the same check/shift. A swap reads
and writes two low and two numerator fields. The reference validator also
scans the N stored numerators to check their bounds; that scan is included
in the conservative cost below. Nothing requires rescaling all other high
coordinates after a gate.

Replacing the predecessor's W by d+e+9 in its conservative sequential bound
gives O_source(N^2(ell+1)[B+d+e+log(2N)]^2) bit operations and materialized
row data bounded by O(N(B+d+e)), in addition to the charged recipe/word
description. This is a supplied-low-row/low-matrix evaluation bound. It
still does not construct the global payload permutation, low-type ordering,
native-owner return, service dispatch or a whole-multiplier tariff.

The exact checker authenticates its retained sources, computes the structural
certificate, independently evaluates every tested forward/inverse matrix
prefix in both native and ordered/atomized emission, and compares
fixed-denominator low/carry outputs with rational
arithmetic. It includes source constructors, nonorthogonal and empty/full
guards, inverse chronology, and fixed-base tensor families. Negative controls
challenge wrong norm direction, omitted conjugation/guard boundary factors,
endpoint-only certificates, too-small denominators, dividing terms separately,
and losing the elementary low carry. Finite checks support the structural
proof; they do not instantiate the selected enormous expression.

The next concrete task is to compute/bound these certificates for the actual
selected compact expression and join them to the remaining source-specific
private precision and physical route contracts. A logarithmic-width theorem
for that complete expression remains open here.
