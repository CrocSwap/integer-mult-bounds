# Exact parity deletion for two column planes

The criterion, its application to the open deletion question, and the finite
ordered-core census were produced by Nick Petalas. Apache-2.0.

The binary coordinate model and the question come from unpaidmoon's
[PR #7282](https://github.com/CrocSwap/integer-mult-bounds/pull/7282), Open
next question 1. Its exact README and proof are retained in `source/` with
their credit unchanged. Its five-orbit result and examples are not reproved
or used to establish the new count. Parity reduction, generator-matrix
column types, binary rank, the simplex code and Burnside's lemma are standard.
No priority is claimed for those general methods.

## 1. Model and deletion operation

All vector spaces are over F2. A column plane is `(c,T)`, where `c` is a
coordinate, `T` has dimension two, every vector of `T` vanishes at `c`, and
every nonzero vector of `T` has Hamming weight at least two. An ordered
column-column pair consists of `(c,T),(d,S)` with distinct columns and

```text
(<e_c> + T) intersect (<e_d> + S) = {0}.
```

The order is fixed throughout. A coordinate permutation sends the first
column to the first column and the second to the second; exchanging the
two planes is an additional equivalence and is not imposed here. Unused
coordinates are discarded, so width always means used support size.

Choose ordered bases `(a,b)` of `T` and `(u,v)` of `S`. For every coordinate
`j` other than `c,d`, define its joint type

```text
t_j = (a_j,b_j,u_j,v_j) in F2^4.
```

Ignore type zero, which is unused. Let `n_t` be the multiplicity of each
of the fifteen nonzero types. Define the cross vectors

```text
p = (a_d,b_d),    q = (u_c,v_c).
```

A permitted pair deletion removes two external coordinates of the same
joint type. It never removes `c` or `d`. Equality of types does not depend
on either chosen plane basis: a basis change acts invertibly on the types.

Delete such pairs until every type occurs at most once. Write

```text
O = { t != 0 : n_t is odd }.
```

The resulting object, before checking whether its planes survived, is the
parity core `(O,p,q)`.

## 2. Necessary and sufficient criterion

For `z in F2^4`, put

```text
w_O(z) = #{ t in O : z dot t = 1 }.
```

**Theorem 1.** Complete pair deletion preserves both planes with dimension
two and minimum nonzero weight at least two exactly when, for every
nonzero `h in F2^2`,

```text
w_O((h,0)) + h dot p >= 2,
w_O((0,h)) + h dot q >= 2.                         (D)
```

Here a dot product on the right is interpreted as the integer zero or one.
The resulting two three-dimensional image spaces are also disjoint exactly
when, in addition,

```text
w_O(z) >= 1 for every nonzero z in F2^4.            (R)
```

**Proof.** The three nonzero coefficient choices `h` give precisely the
three linear combinations of each pair of generator rows. Their external
weights are the two `w_O` terms. The only possible extra coordinate in a
`T` word is `d`, with bit `h dot p`; the only possible extra coordinate in
an `S` word is `c`, with bit `h dot q`. Thus (D) gives exactly their six
weights. It also ensures that none is zero, so both two-row maps are
injective and both planes have dimension two. Conversely each surviving
plane has those three weights, so all six inequalities are necessary.

Project away `c,d`. The four generator rows have rank four exactly when
no nonzero coefficient vector annihilates every column type in `O`, which
is precisely (R). Equivalently, adjoining `e_c,e_d` gives a six-row matrix
of rank six: pivoting on the two unit rows removes all cross entries, and
leaves this external four-row matrix. Under (D), each individual image
space has dimension three. Their sum has dimension six exactly when
their intersection is zero. This proves the second assertion. QED.

The two tests have different purposes. Taking `O={1,2,4,8}` in binary
integer notation gives projected rank four. With `p=q=0` it fails (D),
while `p=q=3` satisfies (D). Taking `O={5,10,15}` and `p=q=0` gives two
planes all of whose nonzero words have weight two, but their projected
images coincide and (R) fails.

**Corollary 2.** Every deletion order has the same final core up to a
coordinate permutation. If that core passes (D), every intermediate
deletion preserves both planes and their minimum distance. If it also
passes (R), every intermediate deletion preserves disjoint image spaces.

**Proof.** Each deletion subtracts two from one multiplicity. Termination
leaves exactly `n_t mod 2` copies, independently of order. At any
intermediate step, the eventual core is a coordinate restriction. Adding
coordinates cannot decrease any word's weight or the generator matrix's
row rank. Apply Theorem 1. QED.

Thus the tests decide both the final property and whether complete
deletion can be carried out while preserving the property at every step.
They do not require a greedy choice among duplicate types.

## 3. Sharp finite reduction and full orbit description

**Theorem 3.** Every parity core uses at most seventeen coordinates, and
this bound is sharp even among cores passing both tests. Surviving
original pairs, at arbitrary width, are exactly the multiplicity data
`((n_t)_{t!=0},p,q)` whose parity support passes (D) and (R), modulo the
action of `GL(2,2) x GL(2,2)` described below.

**Proof.** There is at most one retained coordinate of each of fifteen
external types, plus `c,d`. Take all fifteen nonzero types once and set
`p=q=0`. Every nonzero four-bit linear functional has value one on exactly
eight types. Hence (D) and (R) hold. This is the ordinary four-dimensional
binary simplex generator, partitioned into two ordered pairs of rows,
with two additional column-unit positions. No duplicate type remains,
so its seventeen used coordinates cannot be reduced by this operation.

The data reconstruct the four generator rows by repeating each joint
column type `n_t` times and inserting `p,q` at the two distinguished
columns. Pair deletion gives their parity core. If that core is valid,
the reconstructed original is valid by the same monotonicity argument
as Corollary 2. The converse for survival is Theorem 1.

Changing the generator bases by `L,M in GL(2,2)` acts by

```text
(x,y) -> (Lx,My),    p -> Lp,    q -> Mq.
```

It permutes the fifteen multiplicities accordingly. These changes leave
the planes unchanged. A coordinate permutation preserving the ordered
columns can only match coordinates with equal joint type once bases
have been aligned. Conversely, matching multiplicities after a pair of
basis changes supplies such a coordinate permutation. Therefore these
data modulo this group give exactly the asserted coordinate orbits. QED.

Each valid parity core is itself a valid original, and every even
increase of any of its type multiplicities preserves survival. The
theorem is an exact normal form for deciding survival, not a claim that
all original pairs admit complete deletion. For example, two copies of
each of the four types `1,2,4,8`, with `p=q=0`, give a valid original on
ten coordinates. Its parity core is empty and invalid.

## 4. Exact finite census

**Finite certificate.** There are exactly **15,710 ordered valid parity
cores up to coordinate permutation**. The complete type-labeled domain
has `2^15 * 4 * 4 = 524,288` states. Exactly **467,945** pass (D) and (R).
These are type-labeled states, not counts of arbitrary labeled ambient
coordinate pairs.

| Used width | Valid type-labeled states | Ordered coordinate orbits |
| ---: | ---: | ---: |
| 6 | 5,289 | 188 |
| 7 | 30,528 | 1,032 |
| 8 | 70,336 | 2,312 |
| 9 | 100,032 | 3,254 |
| 10 | 102,576 | 3,355 |
| 11 | 80,080 | 2,667 |
| 12 | 48,048 | 1,663 |
| 13 | 21,840 | 813 |
| 14 | 7,280 | 310 |
| 15 | 1,680 | 91 |
| 16 | 240 | 21 |
| 17 | 16 | 4 |

The exhaustive verifier checks every state against the criterion. It
also constructs the literal binary generator matrix for every support,
checks its rank by Gaussian elimination, and derives all sixteen cross
choices from the generator rows. This independently checks the labeled
count and both parts of the criterion on the finite domain.

Each `GL(2,2)` has the six permutations obtained by choosing the two
distinct nonzero images of a basis. The direct orbit enumeration uses
all 36 product actions and marks every member of each orbit. An ordered
integer scan selects exactly one minimum representative. It checks
invariance, disjoint orbit coverage and orbit-stabilizer divisibility.

An independent Burnside enumeration constructs the permutation cycles
on the fifteen types without the direct census's subset lookup tables.
Its fixed supports are all unions of those cycles, and its fixed cross
vectors are checked directly. Literal six-row matrices decide validity.
The average fixed-state count agrees with the orbit table at every width.

For a compact deterministic fingerprint, encode

```text
state = 16 * sum(2^(t-1) for t in O) + 4*p + q.
```

Concatenate the ascending minimum representatives as four-byte unsigned
little-endian integers. Their SHA256 is
`c8f462928008a6e39d5c3fecf3cf418ef1a77c380bde67bbf36a77d456254fef`.
This fingerprint is computed by the verifier; it is not a receipt of a
separate run or a substitute for the exhaustive check.

## 5. Limits

Theorems 1--3 are scoped written proofs for all finite multiplicities.
The orbit numbers are exact finite computational evidence, with the
complete reduction and group action proved above. No proof assistant,
independent human review, physical query word, native implementation,
supplier admission, improved kappa or complete multiplication theorem is
claimed. No selected-frontier file is changed. Deleting the distinguished
columns, deleting unequal types, or identifying the two ordered planes
requires a different operation or equivalence.
