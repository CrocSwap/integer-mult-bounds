# Source-bound reconciliation of the historical (6,4) cell

Fix the declared P112 root-evaluation code C in K^112, for a field K of
characteristic zero. The binary weight of a vector is the rank of the
labels in its support. Suppose n independent pieces have sorted weight
bounds W, with 6 <= n <= 10 and code-intersection dimension at least six.
The support capacities used below are the inherited bounds

```text
weight       2  3  4   5   6   7
capacity     2  4  8  12  20  36
```

The original BK/BK7 necessary conditions retain exactly 69 of the 7,546
multisets of this length and weight range. This is a historical filter
count. The unchanged PR3154 filter and a separate implementation agree on
every multiset, including the strict excess inequality sum(w-2) < 36.

The new result is an exact composition certificate for six fixed published
contracts. Conditional on those contracts, 62 rows are excluded and seven
are not certified by this inventory. No earlier exclusion is counted as
new. The seven rows are not asserted to be unresolved by every public
result. In particular, the source inventory deliberately does not implement
all original FINITE alpha rules, all cover theorems or all later profiles.

## Deletion and restriction

Deleting d pieces gives a coordinate subspace T' of the original piece
span T with codimension d. Restrict the quotient map T -> T/T' to
D = T intersect C. Its kernel is D intersect T', hence

```text
dim(T' intersect C) >= dim(T intersect C) - d >= 6-d.
```

This uses independence of the original pieces and imposes no bound on
the deleted pieces. It does not preserve all six code dimensions.

For selected small pieces, S is their actual support union. Its size is
at most the sum of their individual capacity bounds. This is ONE common
set. Every nonzero codeword has support at least 53, an inherited premise,
so deleting S is injective on C whenever the certified cap is below 53.
After this restriction the small pieces vanish. The retained code
dimensions then lie in the span of the selected residual endpoints.
Deleting coordinates cannot increase a piece's binary support rank.

## The six admitted contracts

Each contract is a conditional mathematical input, retained byte for byte
in vendor/. SOURCES.json identifies the exact source head and original path.

1. PR3262 proves that three residual rank-at-most-six pieces outside a
   common cut of at most 29 meet the restricted code in dimension at most
   one. Delete four pieces, keep three endpoints and n-7 small pieces.
   Two code dimensions survive deletion and restriction, a contradiction.
2. PR3205 proves that any independent small pieces with common support
   at most 30 and six endpoints of support at most 20 have code
   intersection dimension at most four. Delete one piece. Five code
   dimensions survive. Weight-at-most-six endpoints have support at most
   20, so the retained span contradicts this contract directly.
3. PR3260 proves the three-endpoint statement for ranks at most 5,5,6
   through common support 37. Delete four pieces and apply the same
   injective restriction as in item 1. This is its published threshold 37,
   with no dependency on the simultaneous Batch 4 threshold work.
4. PR3186 excludes the independent ten-piece bounds 3,4,6^8 at code
   dimension six. Any sorted ten-piece list componentwise bounded by
   that list is an immediate instance. No deletion is charged here.
5. PR3192 similarly excludes the independent nine-piece bounds 5,6^8 at
   code dimension six. Again the application is componentwise monotonic
   with exactly the required number of independent pieces.
6. PR3253 permits at most two projective directions outside one fixed
   binary seven-space and ONE common cut of at most five, when each
   remaining support has binary rank at most seven. The following
   quotient argument binds that statement to a caller.

For item 6, choose n-7 small pieces and one anchor q_0 among the seven
others. Require their total support cap to be below 53. Their images in
T/(T intersect C) are independent. Otherwise a nonzero linear combination
would be a codeword below distance 53. The quotient has dimension at most
n-6, equal to their number, so these images form a basis. Each of the six
other pieces q_i therefore gives a relation

```text
c_i = q_i - lambda_i q_0 - a_i in C,
a_i in the span of the small pieces.
```

The six c_i are independent: their coefficients on the six distinct q_i
are unit vectors in the original piece basis. Injective root evaluation
gives six independent directions h_i, hence six distinct projective
directions over K. Let V be a binary seven-space extending the anchor's
label span. Outside Lambda(V) and S, c_i agrees with q_i, whose binary
support rank is at most seven. When |S| <= 5, all six directions meet
PR3253's one-common-cut predicate, contradicting its limit of two.
The proof does not turn the six-cut witness into a five-cut theorem.
The two resulting historical rows were already covered by retained
four-line/alpha work, as recorded in PR3230's public correction. They are
not new profile exclusions.

## Exhaustive contract application

For either shortening rule with m endpoints, the number of deleted pieces
is 7-m and the number of small pieces is n-7. The primary checker enumerates
every endpoint subset, then every disjoint small subset of that size.
It tests the sorted endpoint ranks against the exact contract and sums
the actual small-piece capacity bounds. Pieces with equal bounds remain
distinct indices. Counts refer to indexed role assignments, not distinct
physical realizations.

The separate checker selects small subsets first, then endpoints. It uses
excess coordinates for the historical filter and an independent capacity
table. It reconstructs all successful assignment counts, checks every
retained witness's disjoint partition and deletion dimension, and checks
the minimum support-cap sum over these assignments when the endpoint contract is imposed. A
null minimum means too few compatible endpoints. These exhaustive checks
cover this fixed inventory, including non-prefix assignments; they do not
enumerate arbitrary new theorems or actual coefficient realizations.

Primary attribution follows the rule order above. Its disjoint counts are
55,2,1,1,1,2. Other successful certificates for the same row are also kept.
RESULT.json contains all 69 rows and all six attempts per row.

The uncertified rows are

```text
2^3,7^7
2^2,3,6,7^6
2^2,4,5,7^6
2,3^2,5,7^6
2,3,4^2,7^6
2,5,6^8
4,5^3,6^6
```

For the last two rows the minimum rank-six three-endpoint common-support
caps are 34 and 32, above 29. The mixed 5,5,6 contract instead needs caps
60 and 40, above 37. Thus a stronger uniform rank-five-only threshold would
not by itself certify those literal callers. For the first five rows,
the seven-flat common-cut caps of the n-7 smallest pieces are 6,8,12,10,14,
all above five. This identifies specific failed contracts, not a lower
bound against different geometry, actual support overlap or other proofs.

## Review limits

The retained theorems, their global capacities, root-code distance,
classification, finite censuses and Weyl-chamber arguments are conditional
inputs. This package checks their exact statements and source binding and
the new composition. It does not rerun their historical suites, replace
human or proof-kernel review, or establish full C5, C(P112)>=64, a physical
decoder, supplier admission, an all-size multiplication theorem or kappa.
