# A rank-thirty correction on the actual 112 ports

This packet gives an exact unit response E on the actual 112 data ports.
It has rank(E-I)=30. The previous signed matching has correction rank
56. The new response keeps the useful selected eight-port principal
block L. Both E and E^-1 have selected block L. The ordinary principal
block is also a dyadic unit.

The packet also gives complete in-place scalar words for E, E^-1, E^T,
and E^-T. Each word costs 3210 real scalar primitives at a common
frame. It uses no owned or borrowed field. These are port-code and
matrix results. Native phase lowering, routed access, the physical
terminal, helper progress, and the complete supplier cost are separate.

## The 48-port reciprocal part

The signed pair code H comes from the pinned cyclic family. Its 24
two-field blocks satisfy H H^T=2I. The six coded fields at each of
eight vertices have their actual carrier labels in the payload.

Use the root's reciprocal six-mode matrix. Write a=(a0,a1,a2,a3),
s=sum(a), and define

```text
E6(a,b,c)    = (a-s*1+b*1, c, -2s+3b),
E6^-1(a,b,c) = (a-s*1+c*1, -2s+3c, b).
```

Both matrices are integer units with determinant one and zero
diagonal. Their correction rank is two. The root proof establishes
the general construction and the sharp rank-two lower bound.

At each vertex, put its two modes that meet the selected physical
ports in the first two a positions. Fill the other four positions in
the source order. Conjugate the block by the sign diagonal

```text
D_v = diag(1, alpha_v, 1, 1, 1, 1),
alpha_v = (-1)^v.
```

The two selected-mode off-diagonal entries of both D_v E6 D_v and
D_v E6^-1 D_v are -alpha_v. All their diagonal entries are zero.
Consequently the physical selected block is exactly the old L after
the pair code is removed. The full physical 48-port response is
H^-1 (direct_sum_v D_v E6 D_v) H. It has determinant one and
correction rank sixteen. Its inverse is explicitly given by the same
formula with E6^-1.

This assignment is significant for the existing selected interface:
L^2=I/2 and det(L)=1/16 remain valid. It is not an arbitrary rank-two
block that loses the selected principal unit.

The mode word uses E6=P R, where P exchanges b and c. The reflection
R is implemented without a scratch field. With d_i the four a signs,
execute

```text
b -= sum_i d_i a_i
a_i += d_i b                 for each i
b *= -1
b += sum_i d_i a_i
exchange b,c
```

The exchange is four priced scalar instructions: three unit ADDs and
one negative unit scale. Thus each six-mode word costs 124. The eight
words cost 992. The physical pair code and its inverse cost 940 on
one bank. This gives 1932 for the complete 48-port scalar code.

The reflection factor alone has nonzero diagonal. Its scalar code
does not prove that it can be used as a free native transfer.

## A fourteen-block cover of the other 64 ports

The exact orthogonality graph joins ports p,r when q_p dot q_r=0.
All 64 q labels have odd norm. Exhaustive maximal-clique enumeration
finds 896 maximal cliques of size four and 64 of size eight. In
particular, this fixed support has no nine-clique.

The payload gives a disjoint cover by eleven five-cliques and three
three-cliques. On a clique of size k use

```text
C_k = I-J_k,       C_k^-1 = I-J_k/(k-1).
```

Here J_k is the all-ones matrix. Each C_k is a dyadic unit, has zero
diagonal, and differs from identity by rank one. Thus the 64-port
part has correction rank fourteen and determinant 2^25.

Fourteen is optimal within disjoint dyadic rank-one clique blocks of
sizes two, three, and five. A cover with at most twelve blocks covers
at most sixty ports. Thirteen five-blocks cover sixty-five ports, and
replacing a size five by size three or two decreases this number by
two or three, never by one. The graph has no size nine block. This is
a lower bound for this stated clique model, not a lower bound for all
native constructions or terminal decoders.

An in-place word for C_k is

```text
a += sum(rest)
b -= a                       for each remaining field b
a *= -(k-1)
a -= sum(rest)
```

The word uses 3(k-1) unit ADDs and one dyadic scale. Its cost is 102
when k=5 and 52 when k=3. The complete small code costs
11*102+3*52=1278. Reverse the word and invert its instructions to
obtain the inverse. The inverse has nonzero diagonal and is not
claimed to belong to the direct native zero-diagonal family.

## Complete code and principal inverse

Combine the two disjoint responses. The resulting E has determinant
2^25 and correction rank thirty. The payload gives exact matrices U,V
with 30 columns and rows, respectively, such that E-I=UV. Both U and
V have rank thirty.

Let S be the old selected eight ports and U0 its complement. Partition
E^-1 as [[L,N],[P,Q]]. Then

```text
(E_U0,U0)^-1 = Q-P L^-1 N.
```

Both multiplication orders are checked on all 104 ordinary columns.
Every inverse coefficient is dyadic. The ordinary determinant is
2^21. The selected determinant is 1/16.

The combined scalar word costs 1932+1278=3210. Its reverse gives
E^-1. Reverse the instruction order and transpose each elementary
operation to give E^T; apply both operations to give E^-T. Every word
is checked on all 112 columns. The maximum prefix row one-norm is
44 for E and E^-1, and 14 for E^T and E^-T. These are bounds for the
top-level scalar word only.

The generic five-code controller can use a native forward response
E and raw backward response E^T, provided each common-frame code is
legally bound at its stated cut. Its residual is still the ordered
operator E2 E1^-T E0. The physical terminal sees
Q(E2 E1^-T E0)Q^-1. Rank thirty in one local chart does not provide
free access to those correction coordinates in a routed hole frame.

## Reproduction and credit

The checker requires a new output directory and preserves all source
packets. Run it once with ordinary Python and once with optimized
Python, with different output directories. The expected status is
PASS_LOW_DISPLACEMENT_RESPONSE. The two payloads and receipts must
be byte-identical.

The root supplied the reciprocal rank-two matrix and its proof. The
independent-review lane supplied the complete cyclic zero-diagonal
family. The controller and oblique-native lanes supplied the actual
signed pair coordinates and the selected matching interface. The
encoded-controller lane supplied the legal-cut general-unit
controller and the three-field I-J code. This packet binds the
selected principal units, gives the actual fourteen-clique cover,
and extends the scalar code to five fields. AI assistance was used.

No PR or publication is authorized. Before any future PR description,
read /Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
