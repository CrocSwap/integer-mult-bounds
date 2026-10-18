# Arbitrary support masks with at most three totals

This is a finite algebraic theorem and an explicitly conditional cost
obstruction. It is not a physical supplier or a new multiplication bound.
All ranks below are over Q unless the field F2 is specified.

## Object and changed hypothesis

Use the 32 orientations `x in F2^5` of PR958's smallest five-port cube.
Its symmetric Gram and full binary decoder are

```
j(x,y) = 5 - HammingDistance(x,y)
G[x,y] = 2 (j(x,y)-1) (j(x,y)-3)
B[x,y] = 1 + parity(x) + parity(y)             (in F2).
```

Let E and O be the even and odd orientation sets; both have size 16.
We also use E, O and F=E+O for their indicator functions. Thus
`B = E E^t + O O^t` and its F2 row and column spaces are
`U = span{E,O}`, of dimension two.

A total is a nonzero binary outer product `f g^t`, with reader set
R=supp(f), source set S=supp(g), and objective `rank G[R,S]`.
Require the sum of the outer products to equal B on **all 1,024 entries**.
The functions f and g may be arbitrary functions of the port index. They
need not be affine. Messages are still XOR sums of the indicated input
coordinates: this does not introduce nonlinear functions of input data.

PR1046 proves an affine-support floor for arbitrary numbers of terms.
Here the number of nonzero terms is at most three, but the affine-support
restriction is removed. No claim is made about four or more arbitrary
support terms, a larger cube, masked identities, or a different Gram.

**Theorem.** Every such factorization costs at least 32. Two terms attain
32. Exactly three nonzero terms also attain 32, and every cost-32
three-term factorization has largest term rank 16. In contrast, with
three nonzero affine-support terms the exact minimum is 35. The last
comparison is independently checked by a complete reduced enumeration
justified below; it agrees with PR1046's reported reduced search.

## The finite geometric certificate

Order E before O and write `M = G[E,O]/2`. Directly from the displayed
integer pairing,

```
G/2 = [ 8I   M  ]       M M^t = 64 I,
      [ M^t  8I ]       M_ij is either -1 or 3.
```

The 256 integer entries of M and all 256 entries of `M M^t` are reproduced
in the certificate. A second implementation builds G by literal signed
coordinate-set intersections and checks this identity separately. These
are exact finite identities, not numerical eigenvalue estimates.
Putting Q=M/8 gives an orthogonal rational matrix and the factorization

```
G = 16 [ I ; Q^t ] [ I , Q ].
```

Thus G has rank 16. Each parity class is an orthogonal basis of the same
16-dimensional label space. Every cross pairing is nonzero. In
particular, a restricted Gram with both its indices among any of E, O,
and the full set F has rank 16.

## All factorizations with up to three terms

Write `B = A D^t` over F2, where the n columns of A,D are the reader and
source functions. Since B has rank two, both A and D have rank at least
two. Sylvester's inequality gives

```
rank(A) + rank(D) <= n + 2.
```

For n=1 this is impossible. For n=2 both ranks are two. For n=3 at
least one rank is two. Its span equals U, since it contains the
corresponding row or column space of B. Symmetry of G allows transposing
all terms, so assume the reader functions belong to `{E,O,F}`.
This reduction includes arbitrary non-affine masks on the other side.

For two terms the two readers must be distinct. Solving their binary
identity forces both sources to belong to `{E,O,F}` as well. Each term
costs 16. This proves the exact cost 32 for every two-term factorization.

If three terms repeat a reader f, merge their sources by XOR. The support
of that XOR lies in the union of the two original source supports, so

```
rank G[R, S1 symmetric_difference S2]
  <= rank G[R,S1] + rank G[R,S2].
```

All three readers cannot coincide because B has rank two. After the
merge there are exactly two nonzero independent terms. Hence the original
cost is at least 32. The unmerged single term in this two-term solution
already has rank 16. Therefore equality has largest term rank 16.

It remains to consider three distinct readers. Permuting the terms fixes
them as E, O, F. The entire family is then parameterized by **one arbitrary
32-bit mask** H:

```
B = E (E+H)^t + O (O+H)^t + F H^t.           (F2)
```

Exclude `H=0,E,O`, since these produce a zero source factor. Write
`A=H intersect E`, `C=H intersect O`, with sizes a,b, and let

```
r = rank M[A,C],       t = rank M[E\A,C].
```

The source columns in the E basis are identity columns for A and Q
columns for C. Quotienting by the relevant identity columns gives the
**exact**, individually priced three ranks

```
c_E = 16-a+r,
c_O = 16-b+r,
c_F = a+t,
C_total = 32-b+2r+t.
```

The second formula follows by transposing the same cross submatrix.
All b columns of M indexed by C are independent because M is invertible.
Splitting their rows into A and its complement gives `b <= r+t`. Thus

```
C_total >= 32+r >= 32.
```

If both A and C are nonempty, the dense cross block has `r>=1`, so the
cost is at least 33. If H lies wholly in one parity class, r=0 and the
cost is exactly 32. Nonzero-factor admissibility excludes the empty and
complete parity masks. Consequently, for the canonical distinct readers,
there are exactly

```
2 (2^16 - 2) = 131,068
```

equality masks, the nonempty proper subsets of either parity class.
Their price multiset is `{|H|,16-|H|,16}`. In particular their peak is 16.
Together with the repeated-reader case, this proves the theorem for
arbitrary supports. The finite slice experiment is not the reason the
statement covers all 2^32 masks; the preceding rank argument is.

## A three-total witness outside the affine class

The seed chooses coordinate i=`46 mod 5=1`. Let
`H = {x : parity(x)=0 and x_i=0}`. Then |H|=8. The three reader/source
pairs are

```
(E, E\H),  (O, O union H),  (F, H).
```

Their costs are `8,16,8`. The full decoder identity holds, including
all off-diagonal entries. A nonzero nonconstant affine function on F2^5
has support 16, while the constant one has support 32. The size-eight
mask H is therefore not affine. The source sizes are 8,24,8. This is
an algebraic decoder witness, not an emitted gather/COPY/frame program.

For the affine comparison, the same Sylvester reduction applies. If all
readers are distinct, H must be one of the 64 affine functions; excluding
0,E,O leaves 61 cases. If a reader repeats, choose the repeated reader
and the independent singleton reader (six choices). The merged source
and singleton source are fixed by B. Choose either repeated source from
the 64 affine functions, excluding zero and the merged source: 62 choices.
The other source is determined. These `6*62=372` repeated-reader templates
and the 61 distinct-reader templates exhaust the three-term affine class,
up to transposition and term permutation. Exact rank computation gives
minimum 35. No sampled or heuristic factorization search is involved.

## Cost boundary and unresolved work

Assume the same additive per-total copy-rank lower pricing and stage
ledger as PR958/1046, `D <= (s-1)v-s*C_total`, with v=32 and integer s>=3.
Then the complete optimistic budget is

```
D <= (s-1)32 - s*32 = -32.
```

This grants all source accesses, gathers, decoder arithmetic, scratch,
frame changes, restoration, idle work, recursive overhead, hosting,
precision and tape expenses zero additional cost. Adding nonnegative
expenses cannot rescue a positive deficit in this model. There is no
reason to implement this three-total mechanism as a new supplier under
these premises. The algebraic improvement 35 to 32 is not a saving in
an implemented supplier and does not improve kappa.

The smallest peak 16 statement is conditional on attaining total 32 with
three terms. It does **not** claim a global minimum peak for triples with
larger total cost. PR1046's four affine terms attain total 32 with peak
eight, which this note preserves and does not improve.

Four or more arbitrary-support terms, nonlinear/interactive data
messages, changed Gram pairings, masked identities and a different
stage/copy ledger remain outside scope. Physical realization, common
labels/mutable sources, whole-call hosting, precision/tape, bit H1-H5,
all-size compilation and analytic transfer remain inherited obligations.
This written finite proof is not proof-assistant or independent human
verification of the full multiplication theorem.
