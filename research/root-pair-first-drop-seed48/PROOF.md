# Exact odd-root-pair threshold: 26 punctures

## Model and statement

Use the 120 unoriented E8 root lines. For reproducible coordinates, the
verifier forms doubled roots from the vectors with two entries `+/-2`
and six zeros, together with the vectors having eight entries `+/-1`
and an even number of minus signs. In each pair `{r,-r}` retain its
lexicographically larger element, then sort. The true root is `r/2`.

Let `N[i,j] = (r_i dot r_j / 4 + 1) mod 2`. This is the exact pairing
matrix from PR717's B14 model, as used by PR968. The verifier checks that
its F2 rank is nine. Define `S_a = {i : r_i dot r_a != 0}`. For a common
puncture set P, the cost of the root-normal term `(a,b)` is

```text
c(a,b,P) = rank_F2 N[S_a \ P, S_b \ P].
```

The theorem concerns distinct nonorthogonal root lines, equivalently
`abs(r_a dot r_b) = 4`. Parallel pairs and general non-root normals are
outside its scope. Nonzero rescaling of either normal does not change
its support. Then:

1. For every such pair and every `|P| <= 25`, `c(a,b,P) >= 7`.
2. For every such pair there exists a set of 26 punctures with cost six.

Hence 26 is the exact first threshold for cost at most six in this class.
Neither statement classifies every set of 26 punctures or minimizes a
sum of eight term costs.

## Why the 25-puncture enumeration is complete

A symmetric rank-nine matrix N induces a nondegenerate bilinear form on
the nine-dimensional quotient by its radical. The root labels span this
space. Let U and V be the spans of the surviving labels in the two
supports. Nondegeneracy gives

```text
rank B|_(U x V) >= dim(U) + dim(V) - 9.
```

Indeed, the kernel of `U -> V*` is `U intersect V-perp`, whose dimension
is at most `9-dim(V)`. Consequently, if the pairing rank is at most six,
at least one of U,V has dimension at most seven.

The replay chooses nine independent pairing rows and uses their columns
to give nine-bit coordinates to all labels. It verifies coordinate rank
nine and 511 distinct nonzero functional evaluation masks. Thus it
enumerates the entire dual space, not a sampled family. Over F2 any two
distinct nonzero functionals are independent, so the 130,305 unordered
pairs exhaust all possible pairs that could lie in the annihilator of
a support span of dimension at most seven.

For a functional lambda, write `V_lambda` for the set of labels on which
it evaluates to one. To make both lambda and mu vanish on a surviving
support S, the puncture must include

```text
M = S intersect (V_lambda union V_mu).
```

For each support of the fixed pair, the full enumeration finds minimum
`|M| = 25`. Exactly 189 functional pairs attain this minimum, producing
63 distinct masks per side. The two families are disjoint, leaving
126 masks. There is no mask of size below 25. If `|P| <= 25` permits a
support dimension at most seven, `M subset P` therefore forces `P=M`.
Every potentially cost-six set with at most 25 punctures is consequently
one of these 126 masks. This does not assert that arbitrary 25-puncture
sets have rank seven; other sets need not lower a support dimension.

For each of the 126 masks the actual rectangular pairing matrix has
rank seven, computed by two separate elimination implementations:
bitset row reduction and dense literal binary elimination. This excludes
cost at most six at every puncture size through 25.

## A 26-puncture witness

The seed 48 selects line a=48 and its first odd partner b=0 in the
canonical order above. Their doubled root vectors are

```text
a = (1,-1,-1,-1,1,1,-1,1)
b = (0,0,0,0,0,0,2,-2).
```

One attaining puncture is

```text
0,23,24,25,26,34,35,36,37,48,60,61,62,63,66,67,
72,73,76,77,78,79,82,83,88,89.
```

Removing line 48 from this list gives the recorded parent with support
dimensions `(9,7)` and pairing rank seven. Puncturing line 48 as well
gives dimensions `(8,7)` and rank six. Every one of the 26 one-line
restorations is also replayed and has cost at least seven. The certificate
stores the complete mask census and both dimension calculations.

## Transport to every odd pair

The verifier constructs eight explicit E8 root reflections in doubled
coordinates, `r -> r - (r dot s / 4) s`. For each it checks closure and
bijectivity on the 120 root lines, then checks every ordered pair of
lines for preservation of orthogonality and the N entry. These are
115,200 paired support/pairing comparisons. The action therefore
preserves both the term supports and their exact cost for any transported
puncture set.

A breadth-first orbit from `(48,0)` is compared as a set against all
ordered pairs satisfying `abs(r_a dot r_b)=4`. The sets coincide and
contain 6,720 elements. This finite equality certifies the required
transitivity directly. The lower bound and attaining puncture transport
to all of them; no abstract Weyl-group classification is assumed.

## Exact rational completion and full accounting

Let alpha and beta be the true roots of the fixed pair. Choose an
invertible rational matrix A whose first column is alpha and whose
other seven columns form a basis of `beta-perp`. Such a matrix is
invertible because `alpha dot beta != 0`; the implementation uses an
explicit pivot-coordinate basis and exact rational inversion. Set
`B = 2 A^(-transpose)`. The first column of B is proportional to beta,
because it pairs to zero with the other columns of A and to two with
alpha. Thus the first term has precisely the desired support pair.

For the matrix R of the 94 retained true roots, set `D=R A`, `T=R B`.
Then `D T^transpose = 2 R R^transpose = 2G`. The verifier checks all
8,836 entries in exact rational arithmetic, not just required E-edges,
and independently ranks each of the eight support pairing matrices.
Their costs are `(6,9,9,9,9,9,9,9)`, summing to 69 copies on 94 ports.
This completion only establishes that the term witness occurs in a
full exact eight-term rational decoder. It does not improve the known
copy-per-port ratio and is not asserted to be an optimal completion.

## Scope and credit

PR968 already proves its all-normal eight-term inequalities for `p<=24`.
This note identifies the first subsequent cost-six threshold in the
narrow odd-root-pair class, including its dimension-seven mechanism.
PR998 concerns one added total with fixed coordinate readers and does
not supply this threshold. No claim is made for parallel pairs, arbitrary
normals, nine or more terms, masked identities, physical gate counts,
multi-stage shared copies, precision admission or the selected bound.

The model and decoder accounting come from DreamingOfClouds's PR717
and themilkman216's PR968. This new enumeration, witness and verification
were prepared for @woklerx with substantial OpenAI Codex assistance.
See NOTICE.md and the exact predecessor file pins in SOURCES.json.
