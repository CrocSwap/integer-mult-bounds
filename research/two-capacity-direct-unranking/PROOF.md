# Direct unranking for two capacities without a prescribed injection

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and premises

Let V and W have dimension n over F_q. Fix arbitrary subspaces A,B of V
and C,D of W. Define

`G = {g:V->W invertible : g(A) contained in C, g(B) contained in D}`.

There is a deterministic bijection from the integers 0 through |G|-1 to G
using O(1+n^5) field operations and O(1+n^4) exact integer arithmetic
operations on O(1+n^2 log q)-bit integers. Live working storage is O(1+n^2)
field elements and O(1+n^3 log q) bits. Fixed input and output matrices have
the same field-element bound. An empty G is detected before decoding.

This is the U=0 specialization of Ali Romman's PR6539 contract. Its count
and quotient/lift decomposition are cited premises. The new result makes
that decomposition an explicit direct unranking algorithm, with polynomial
resource bounds. The predecessor count, ToikY's PR6535 feasibility theorem,
and classical Gaussian, graph-map and basis-extension formulas are not new
claims. Nick Petalas's PR6607 already gives a general prescribed-injection
sampler through exponentially many candidate images. That self-reduction is
not used here. This proof leaves nonzero prescribed U open.

The field-operation bound assumes an exact finite-field arithmetic interface
and a fixed ordering of its elements. Bit cost of a chosen field representation
is additional. The executable supports prime orders at most 31 and F4, with
n at most 12. The proof has no such fixed dimension or field-order limit.

## Fixed decompositions and cardinality

All complements below are deterministic once the inputs are fixed. Extend
an ordered independent list by scanning a fixed basis of its containing
space, retaining exactly those vectors which increase rank.

Write J=A intersect B and T=C intersect D, of dimensions j and tau. Fix

`V = J direct-sum A0 direct-sum B0 direct-sum R`,
`C = T direct-sum C0`, `D = T direct-sum D0`,

where A=J direct-sum A0 and B=J direct-sum B0. Put
alpha=dim A0, beta=dim B0, c=dim C, d=dim D and s=j+alpha+beta.
The complement R concerns the whole domain V, not A+B alone.

Write Inj(m,k)=product_{r=0}^{k-1}(q^m-q^r), zero outside 0<=k<=m,
and use Gaussian coefficients with their usual zero convention. If j>tau
then G is empty. Otherwise set H=tau-j and

```text
w_i = [H choose i]_q [c-tau choose alpha-i]_q
      q^((H-i)(alpha-i)) Inj(alpha,alpha)
      Inj(d-j-i,beta) q^(i beta),

max(0,alpha-c+tau) <= i <= min(alpha,H),
S = sum_i w_i,
N = Inj(tau,j) S q^(j(alpha+beta))
    product_{r=s}^{n-1}(q^n-q^r).
```

PR6539 supplies N=|G| in this specialization. Zero weights are omitted.
An empty sum means N=0. No negative-dimensional injection is decoded.

## Polynomial elementary decoders

An ordered injection from F_q^k into F_q^m is decoded one image at a time.
After r images, extend their ordered basis to a full deterministic basis.
Every vector outside their span has unique coordinates (a,b), where
a is arbitrary in F_q^r and b is nonzero in F_q^(m-r). Index a in base q
and b by the nonzero integers 1,...,q^(m-r)-1. This is a bijection of
q^m-q^r indices with the possible next images. Mixed radices decode the
complete injection. No ambient vector list or rejection trial is needed.

A k-subspace of F_q^m has a unique reduced row-echelon basis. Divide its
first-column cases into a zero column and a pivot column. The first has
[m-1 choose k]_q possibilities. In the second, the remaining rows form a
(k-1)-subspace of F_q^(m-1), and the first row has m-k free coordinates
in the nonpivot columns. Its count is q^(m-k)[m-1 choose k-1]_q.
This gives a weighted first-column decoder. Iterating at most m times records
the pivots and their free coordinates, and then fills their unique RREF.
The executable uses iteration rather than recursion.

Both decoders have explicit inverse descriptions. Read the unique coordinates
or RREF, recover each mixed-radix digit, and reverse the branch decomposition.

## Decode a completion

1. Decode an arbitrary injection J->T, with Inj(tau,j) possibilities. Call
   its ordered image L. Choose the deterministic complement H0 of L in T.
   Thus H0 represents T/L and has dimension H.
2. Select i by its interval of length w_i within S. A subsequent local
   index ranges over exactly w_i choices. Choose an i-subspace I of H0,
   and an (alpha-i)-subspace K of C0, with the two Grassmann decoders.
   Choose every entry of a graph map K->H0/I in base q. The complement of
   I in H0 supplies fixed quotient representatives. The resulting subspace
   P of H0+C0 has dimension alpha and satisfies P intersect H0=I.
3. Decode an arbitrary ordered alpha-basis of P, by an element of GL_alpha.
   These are the images of the fixed basis of A0, modulo L.
4. In D/L=H0+D0, quotient by I. Decode an injection of the beta-dimensional
   B0 into the fixed representative space of dimension d-j-i. Lift each
   image through I by i arbitrary field entries. Its image Q is disjoint
   from P: the intersection of P with D/L is exactly I, and Q projects
   injectively modulo I. This accounts for Inj(d-j-i,beta)q^(i beta).
5. Independently lift every A0 and B0 basis image through L. These
   j(alpha+beta) free entries give the displayed global q-power.
6. Extend the resulting ordered s-dimensional image basis to an image of
   the fixed remaining domain basis R. Decode each next image outside the
   previous span with the elementary decoder. Finally change from the
   adapted domain basis back to the standard basis.

Steps 2 through 4 consume precisely the factors in w_i. Steps 1, 5 and 6
consume the other global factors of N. Integer division with remainder
therefore splits each index in [0,N) into one such sequence of choices.

## Bijection and uniformity

Every decoded image list is independent. The first j images lie in T.
The next alpha lie in C and the next beta in D; their quotient images
have zero intersection by step 4. Lifting through L preserves quotient
independence. The last images are independent by construction. The map
is thus in G, including all arbitrary input vectors by linearity.

Conversely, fix g in G. Its values on the fixed J basis determine the
injection and L. Project its A0 images modulo L. Their span is the unique P
in step 2, hence determines i, I, K and the graph. The ordered values
determine the GL_alpha choice in step 3. Projecting the B0 values modulo
L and then I determines the injection and lifts in step 4. The L-components
determine step 5. The values on R determine the outside-span digits in
step 6. All fixed complements are functions of earlier recovered choices.
Thus this inverse is unique, so the decoder is bijective.

A uniform integer index gives exactly the uniform distribution on G.
Put b=ceil(log2 N), with b=0 at N=1. Independent uniform b-bit integers,
accepted exactly when below N, give a uniform index at the first success.
With R attempts the exact exhaustion probability is
`(1-N/2^b)^R`; conditional on success, every map has probability 1/N.
The executable accepts at most 64 pre-supplied entropy blocks, validates
them all, and charges Rb provisioned bits. It returns the acceptance position
in bits separately. It has no hidden random source and no unbounded loop.
The abstract online version, generating blocks only until acceptance,
uses expected b*2^b/N<2b bits for N>1. This latter expectation is not a
measured cost of the pre-supplied-list API. At N=1 zero bits suffice.

## Resource bound

Row reduction of O(n) rows of length O(n) costs O(1+n^3) field operations.
A deterministic complement scans at most n vectors and performs at most n
such reductions, costing O(1+n^4). The injection and final extension
decoders make O(1+n) complement calls in total. All other operations are
linear combinations, a fixed number of complements, or the final n
coordinate solves. This proves O(1+n^5) field operations.

Gaussian products use O(1+n) factors each. The weighted branch sum and
the first-column decoders use polynomially many such products; including
integer powers by repeated squaring, O(1+n^4) arithmetic operations is a
conservative bound. All intermediate integers have O(1+n^2 log q) bits.
Rank comparisons and index arithmetic are included; no q^n candidate loop
is hidden. Space is bounded by a fixed number of O(n)-vector bases, O(n)
stored branch weights of O(1+n^2 log q) bits, and integer counters.
Zero-dimensional spaces use empty bases
and empty products, with one empty invertible map.

## Limits and next obligations

This supplies unrestricted linear completions. A nonzero prescribed
injection introduces the compatible quotient discrepancy of PR6539 and
is deliberately outside this proof. An actual native shared contact still
requires its signed or symplectic constraints, physical basis changes,
randomness generation, causal access, dirty restoration, precision, stock,
tapes, compiler and complete outer costs. No selected assumption is
discharged and no kappa is changed. The proof is written mathematics with
finite executable corroboration; independent human and proof-kernel
acceptance are unclaimed.
