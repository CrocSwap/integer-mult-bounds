# Original cover contracts in the historical (6,4) cell

Fix the declared P112 root-evaluation code C over a characteristic-zero
field K. Assume its inherited minimum distance 53 and the support caps

```text
binary support rank   2  3  4   5   6   7
support cap           2  4  8  12  20  36
```

Let q_1,...,q_n be independent pieces, 6 <= n <= 10, with sorted binary
support-rank bounds W and dim(span(q_i) intersect C) >= 6. The historical
BK/BK7 filter retains 69 of the 7,546 bounded weight multisets. PR3282's
fixed six-contract inventory conditionally certifies 62 of these. Its
seven other rows were explicitly not claimed to be the public frontier.

This package supplies the omitted original cover applications. It
conditionally accounts for three of those seven rows, so the expanded
inventory certifies 65 of 69. These are recovered earlier exclusions,
not new geometric theorems or a claim that four rows remain unresolved
by every public result.

## The quotient-basis implication

Choose rho=n-6 pieces X whose total support cap is less than 53. Their
images in T/(T intersect C), T=span(q_i), are independent. Indeed, any
nonzero linear combination is nonzero by piece independence, and has
support below the code distance. It cannot be a codeword. The quotient
has dimension at most n-6=rho, so these images are a basis and the code
intersection has dimension exactly six.

For each of the six nonbasis pieces q_y there is a unique a_y in span(X)
with c_y=q_y-a_y in C. The six c_y are independent, by their coefficients
on the six distinct nonbasis pieces. Injective root evaluation therefore
gives six independent directions h_y. Their off-supports satisfy

```text
Off(h_y) subset support(q_y) union union_{x in X} support(q_x).
```

Partition X into three indexed groups A,B,P. A group's union of binary
label spans has rank at most the sum of the member ranks. Thus A and B
fit into fixed flats of the declared dimensions if their weight sums
fit. The union of the actual supports in P is ONE common set of size at
most the sum of its support caps. No assumption of disjoint supports is
made. After removing those two flats and that common set, h_y's support
has binary rank at most the rank bound on q_y.

## Exact inherited contracts

The following are mathematical inputs, not newly replayed geometric
claims. Every source payload is retained verbatim and authenticated by
its exact Git blob and SHA256. In each row the first two dimensions bound
fixed binary flats; deletion allowances may even vary with direction in
the inherited theorem, so one common deletion set is permitted.

| Rule | Flat dimensions | Deleted lines | Residual rank | Direction span bound |
|---|---:|---:|---:|---:|
| alpha74 | 7,4 | 0 | 7 | 4 |
| beta7p2 | 6,6 | 2 | 7 | 4 |
| beta6p4 | 6,6 | 4 | 6 | 1 |
| beta6p8 | 6,6 | 8 | 6 | 3 |

PR3154 FINITE gives alpha74 and beta7p2. Its later PROOF_MAP and final
labelled full_b log supersede the stale unfinished status in FINITE's
original notes. The log preserves the early join failures, the empty
representative numbering correction, and the final index-free agreement
of the two complete rank-seven, two-deletion runs. This is recorded
predecessor evidence, not a rerun here. PR3161 supplies the written
rank-six four/eight-deletion contracts and their scope.

The real span statements transfer to every characteristic-zero K.
For fixed binary flats and a root-zero pattern, the direction space is
the kernel of a rational matrix. The directions with exactly that
pattern are the complement of finitely many proper rational hyperplanes
in this kernel. If nonempty after extension to K, this complement is
nonempty and spans the rational kernel over Q. Its real vectors satisfy
the inherited real contract. The sum of all qualifying rational kernels
therefore has dimension at most that contract's bound. Scalar extension
preserves this dimension and contains every qualifying K-direction.
There are finitely many root-zero patterns, so this argument covers all
of them without ordering K or sampling a finite field.

For the rank-six rules, each nonbasis weight-seven piece contributes at
most one additional dimension. If s7 is their number, the six required
independent directions would have total span at most the stated bound
plus s7. A certificate requires this sum to be strictly below six.
The rank-seven rules need no exceptional endpoint allowance.

## Three recovered applications

All three use beta7p2. The displayed quotient basis always has four
pieces, since each original row has ten. Brackets show cover roles;
identical weight entries are still distinct piece indices in RESULT.json.

| Original weights | Six-flat A | Six-flat B | Common cut piece | Basis support cap |
|---|---|---|---|---:|
| 2,2,3,6,7^6 | [2,3] | [6] | [2] | 28 |
| 2,2,4,5,7^6 | [2,4] | [5] | [2] | 24 |
| 2,3,3,5,7^6 | [3,3] | [5] | [2] | 22 |

The flat weight sums are at most six. Each common cut has at most two
lines. Every support cap is below 53. The six remaining pieces have rank
bounds seven, so their six independent directions lie in a space of
dimension at most four, a contradiction.

The code enumerates every rho-piece quotient basis and all three-role
assignments, recording the number of successful indexed certificates
and one literal witness for each rule and each row. A separate checker
uses full-index basis masks, then cut subsets and complementary flat
subsets. It reproduces all 276 rule/row counts, including zero counts.

## Four inventory-uncertified rows and the precise boundary

```text
2^3,7^7
2,3,4^2,7^6
2,5,6^8
4,5^3,6^6
```

None fits any of the four new rules by these conservative rank-sum and
support-cap tests. This is not a nonexistence claim for actual support
unions or coefficients. In particular, 2,3,4^2,7^6 has quotient basis
[2,3,4,4]. Its roles [2,4], [4], [3] fit two six-flats but need four
common lines. The unproved uniform beta rank-seven p=4 contract would
suffice; the available p=2 contract does not. A control confirms that
relaxing only this budget creates a certificate, which is not admitted.
Alpha74, beta6p4 and beta6p8 certify no additional row beyond the inherited
six-contract inventory plus beta7p2.

## Limits

The distance, support capacities, geometric cover theorems and PR3282's
six-contract coverage remain inherited conditional inputs. Their heavy
censuses and full proof dependencies were not rerun. This package checks
the exact source bytes and the new algebraic caller composition. It does
not establish actual support-union minima, coefficient realizability,
full C5, C(P112)>=64, a decoder, physical execution, supplier admission,
a multiplication theorem or any new kappa. Human and proof-kernel review
are separate. Lean, Docker and selected cold replay are unrun.
