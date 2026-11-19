# Exactly four columns over fifteenth roots

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

Let zeta be a primitive fifteenth root of unity. The largest number of
pairwise orthogonal columns of length eight with entries among powers of zeta is
exactly four. This resolves the q=5,b=1 attainment question in
[PR #7768](https://github.com/CrocSwap/integer-mult-bounds/pull/7768),
whose general column-defect bound permits five columns.

This is a complete finite certificate with an attaining example. It is
not a failed search. Larger alphabets of order 3*5^b with b>1 remain
outside the finite domain. No physical supplier or new kappa follows.

## 1. Normalize any pair of columns

Row phases make the first column constant 1. The second column is now
a zero sum of eight fifteenth roots. The complete source census checks
all C(22,8)=319,770 multisets in the integral basis modulo

```text
Phi_15(X) = X^8-X^7+X^5-X^4+X^3-X+1.
```

It finds exactly fifteen zero multisets. Each is one rotated 3-cycle
and one rotated 5-cycle. This also follows from the classical cycle
theorem, but the finite census suffices here. See the
[pinned source proof](https://github.com/aliromman/integer-mult-bounds/blob/d33fe8562c86888307cbba4a2aa92490212c8d78/research/mixed-cycle-column-obstruction/PROOF.md)
and [unchanged source checker](https://github.com/aliromman/integer-mult-bounds/blob/d33fe8562c86888307cbba4a2aa92490212c8d78/research/mixed-cycle-column-obstruction/verify.py).

The fifteen multisets are exactly the scalar shifts of

```text
v = (0,5,10,0,3,6,9,12),
```

where an exponent e denotes zeta^e. The checker compares both sets
exactly. A phase on the second column and a row permutation therefore
put every orthogonal pair into the form (1,zeta^v). These operations
preserve the alphabet and all other orthogonality relations.

Each additional column can be scaled independently to make its first
entry 1. Its exponent vector then begins with zero. This does not
change the fixed pair. No row or column phase outside the original
alphabet is used.

## 2. Enumerate every possible extension

The new checker first examines all C(21,7)=116,280 nondecreasing
seven-term tails, with the first exponent fixed to zero. Polynomial
reduction finds exactly seven possible zero-sum supports. A recursive
multiset permutation gives all 20,160 normalized columns orthogonal
to the first column. A separate enumeration uses the fifteen rotated
cycle multisets and ordinary permutations. The two full sets agree.

Exactly 95 candidates are also orthogonal to zeta^v. Every decision
is checked in two exact integral bases: direct polynomial division
by Phi_15 and the tensor basis of Q(omega,zeta_5). The basis map uses

```text
zeta^e = omega^(2e) zeta_5^(2e).
```

The cycle-support membership check gives a third comparison for these
20,160 decisions. No floating-point tolerance is used.

Let G have these 95 candidates as its vertices, in lexicographic order.
An edge means that the corresponding columns are orthogonal. All
C(95,2)=4,465 pairs are tested in both exact bases. The graph has twelve
edges. Its only nontrivial connected components are the cycles

```text
0 -- 67 -- 2 -- 66 -- 1 -- 68 -- 0,
19 -- 51 -- 20 -- 52 -- 21 -- 53 -- 19.
```

The other 83 vertices are isolated. All vectors, edges and components
are in `RESULT.json`. Connected-component traversal checks these two
six-cycles. Separate checks examine every one of the 138,415 vertex
triples and every edge's bitset of common neighbors. Both find no
triangle.

Five mutually orthogonal columns would give three additional columns
after pair normalization. They would form a triangle in G, which is
impossible. Thus at most four columns exist. With the fixed normalized
pair, there are exactly twelve four-column sets and 83 maximal
three-column sets. These are labeled, normalized counts, not counts
up to every matrix equivalence.

## 3. An attaining matrix

Use the following exponent matrix; replace each entry e by zeta^e.

```text
0   0   0   0
0   5   0  10
0  10  10   5
0   0   5  10
0   3   6   4
0   6  12  13
0   9   3   7
0  12   9   1
```

The four columns are the constant column, v, vertex 0 and vertex 67.
The checker computes every Gram entry. Its diagonal is 8 and all
other entries are zero, in both exact bases. Therefore four columns
are attainable and the maximum is exactly four.

The checker rejects all 448 changes obtained by replacing one entry
with any of the other fourteen roots. It also checks each candidate's
self-norm and distinguishes the wrong bilinear pairing that omits
complex conjugation. These controls make the orthogonality convention
explicit.

## Evidence and limits

All nineteen retained files have exact SHA-256 and Git-blob pins.
The complete PR7762 checker and its nested PR7744 replay run unchanged.
The new enumeration and full graph are checked in normal and optimized
Python modes. The saved certificate is compared with a full recomputation.
The statement is finite and exhaustive within the specified alphabet,
row count and exact orthogonality condition.

The source general bound remains valid for every b>=1, but this sharp
capacity proof fixes b=1. It does not classify all matrices under full
row and column equivalence. Other row counts, larger alphabets,
approximate orthogonality, physical preparation and complete caller
pricing remain open. All five framework assumptions and the selected
frontier remain unchanged. No selected cold replay, Lean, Docker,
independent human acceptance or formal proof kernel was used.
No global literature priority is claimed.
