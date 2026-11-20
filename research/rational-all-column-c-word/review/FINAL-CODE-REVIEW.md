# Final complementary code review: rational all-column C words

## Conclusion and disposition

No blocking execution or semantic-validator defect was found in word.py or
execute.py. Their exact matrix keys, signed coefficient code, complete
spectators, padding, row stock, staged Gaussian numerators, private zero
endpoints, and both root scale drops agree with the independent invariant.

One proof-text correction was identified and accepted by the author:
denominator fields share the total unary length budget. The statement that
D can attain L^L at unary code length L is false. This does not affect the
odd-debt lemma, binary guard, implementation, or effective-startup conclusion.
The same overstatement in the initial independent review has been explicitly
corrected in REVIEW.md Section 4. See Section 5 below for the exact argument.
The candidate proof's final correction is authenticated in DISPOSITION.json.
The tested code is unchanged, the corrected proof was reread, and this scoped
logical review is approved after that correction.

This remains a logical-code and mathematical review. The named scalar,
movement, XOR, placement, parking, and ownership contracts are retained.
No tested word is funded and no multiplication or kappa claim is made.

The candidate is research/rational-all-column-c-word.
FINAL-CODE-RESULT.json records the exact code/proof hashes at test time.
The prior derivation is REVIEW.md; the new checker is check_final_code.py.

## 1. Exact all-column semantics and signed code

The formal state keeps a key (original_owner,A) and a separate coefficient
in Q(i). SCALE changes only the coefficient. Column operations change A
by exact left multiplication. Fraction arithmetic gives canonical equality.

Absolute phase stays in A. In particular iA is not merged with A:
(iA)^(tensor f)=i^f A^(tensor f), whereas an exterior scalar i acts once.
The distinct-nonzero-matrix Vandermonde argument applies over Q(i).
All column generators are invertible, so a nonzero matrix key remains
nonzero. Zero scalar coefficients are explicitly removed.

Every productive output must equal the target on its own original owner;
every private endpoint must vanish. The latter is stronger than the
predecessor's productive-only check and matches the declared append-CLEAR
convention. No owned field supplies productive credit.

The signed unary encoding is bijective: a>=0 maps to 2a, and a<0 maps to
-2a-1. The inverse uses parity. Syntax checks cover positive q, integer types,
register indices, axis ranges, and distinct CNOT/CZ axes. Incomplete codes and
unknown tags are rejected.

Independent checks cover 1,683 signed triples and all 65,534 binary strings
of lengths 1..15. All 650 accepted short strings re-encode identically.
Funding remains separate from semantic acceptance.

## 2. Recursion, complete fields, and logical ownership

Repeated division by N computes d=floor(log_N h), so W^d is the required
productive stock. At least that many original rows implies padding to its
next multiple is less than twice the original row count. Cyclic splitting
batch[k::W] and zip/interleave undo one another exactly. The padded stock is
divisible by W at every nonleaf child; private registers receive the same
row count as one productive register.

Active axes are distinct and lie within a complete Boolean cube. Each base
coordinate selects one block of f axes. X/S/CZ/CNOT operate on the matching
coordinates across columns while retaining all spectator coordinates.
Residual C axes are processed before the word and commute with its disjoint
selected blocks. Arbitrary axis order is therefore supported.

Lifted input rows and private rows have distinct mutable row objects.
Cyclic slicing preserves that disjointness; shared coordinate tuples are
immutable. ADD/SUB build the entire new register before assignment, including
self-add and self-sub. Correlated values do not create a mutable owner alias.

Private endpoint checks precede dropping private registers. Padding is checked
after root completion and scale retirement. This uses the all-column identity
on each arbitrary productive owner: padding may be mixed with nonzero rows
inside a word, but must return to zero at its endpoint.

## 3. Odd debt, binary guard, and staged width

For each odd prime ell, a scalar division increases pole order by at most
v_ell(D); addition takes the maximum. Native monomial gates and completed
C endpoints add no odd debt. There are at most d unfinished contexts and
J instructions in each, so D^(Jd) clears every intermediate odd denominator.

The code creates that scale only once before visit. Descendants inherit
it; completed siblings do not retain their internal odd debt.

The computed m satisfies |a|+|b|<2^m and q<2^m, with m>=2. Signs and
unreduced fractions are conservatively included. HALF and ADD fit the
same allowance.

An explicit sufficient prefix bound is

    B(h) <= (N-1)d + J(m+2)d + Jh/(N-1) + N+2.

Its terms pay for unfinished-level tails, scalar prefixes and staged
numerators, completed children, and the terminal direct branch.
A completed rank-f C child adds at most f denominator bits and f bits
of real-component maximum-norm growth relative to its input.

For N>=2, m>=2, and d<=h, B(h) is strictly smaller than

    G(h) = 8 (N + J(m+2) + 1) (h+1).

The initial magnitude uses at most p+G+Jd log2(D) bits, and intermediate
growth needs less than G more. The capacity

    p + 2G + Jd bitlength(D) + 4

therefore covers signs, all stored values, and numerator staging.

SCALE retains both old limbs, computes (a*x-b*y,b*x+a*y), and only then
checks exact division by q. Each partial multiplication is bounded by
(|a|+|b|) times the incoming maximum, so the written width bound also covers
partial products when a final numerator cancels. The max_bits receipt samples
stored values and complete numerators; it is not a microscopic trace of
every multiplication scratch cell.

C similarly forms both full numerators before exact division by two.
The common root format is unchanged across recursive boundaries.

## 4. Root retirement and the physical boundary

The completed root contains

    2^G D^(Jd) C^(tensor h) x.

Its target denominator divides 2^h. Because G>=h, the exact fixed-D
divisions Jd times and the exact drop by 2^(G-h) are valid and return
2^h C^(tensor h)x. Both drops occur in the code.

The omitted-odd-retirement control returns exactly 729 times the required
answer for its chosen word. The root odd factor is not an alternative
normalization.

The extra root passes add no paid C calls. Under the named complete-scan
contract they cost O_word(V log(h+2)); local rational passes cost O_word(V).
These preserve the inherited positive-power layer tariff.

Logical zeroing and Python object removal are not tape erasure. Even a
numerically zero private field still needs its inherited backing retirement.
The counter private_retired_values counts CLEAR events in this model;
it is not a complete erasure invoice, and self-subtraction can zero a private
field without a CLEAR event. These finite counters must not be promoted to a
literal tape receipt.

Likewise, computing p with Python bit_length is finite-model instrumentation.
A physical realization uses the admitted input-format precision and scans
the full reserved capacity. It gains no free value-dependent allocation.

## 5. Corrected startup argument

At total unary code length L, each denominator q_i contributes q_i one
symbols, in addition to all delimiters and other fields. Thus

    sum_i q_i <= L,
    D <= product_i q_i <= 3^(L/3).

The last inequality follows from q<=3^(q/3) for every positive integer q.
The initial review incorrectly treated the loose individual-field bound
L^L as attainable despite the shared length budget. In particular, a
D-state table alone need not exceed the 2^O(L) validator budget.

Binary rational arithmetic and a binary divisor descriptor remain a clean
uniform implementation choice. Their validity does not depend on excluding
a D-state table by an asymptotic contradiction.

Coefficient heights, matrix sizes, and path counts still give an exact
2^O(L) poly(L) semantic test. Enumeration through a fixed multiple of
log(p+2) is polynomial in p. A qualifying funded word's existence remains
a separate premise.

## 6. Additional independent checks

The checker imports the candidate Word and execute as the objects being
reviewed. Its target oracle is the earlier independent Fraction C routine,
written before this candidate was inspected. It applies direct kernels in
reverse axis order, then multiplies by 2^h. It does not import the candidate
verifier or target oracle.

All six complete executions agree:

| Word | N,W,Z,J | Rank | Original/padded rows | Stress |
|---|---|---:|---:|---|
| Nested odd division | 2,2,0,14 | 8 | 9/16 | Three unfinished levels; spectator |
| Three-row mixing | 3,3,2,47 | 3 | 4/6 | Signed complex scalars; two private owners |
| Three-row mixing | 3,3,2,47 | 6 | 4/6 | Two columns; arbitrary spectators and axis order |
| Three-row mixing | 3,3,2,47 | 7 | 5/6 | Residual tail plus two columns |
| Binary-height sandwich | 2,2,0,6 | 2 | 3/4 | Denominator 2^1024 |
| Self-alias/cancellation | 2,2,1,10 | 4 | 5/8 | Self-add, HALF, self-sub, zero scalar |

The nested case performs 573,440 scalar component divisions, 131,072
C component divisions, and 84 paid calls. Its maximum measured magnitude
is 4,322 bits inside capacity 8,589.

The height sandwich has m=1025 and G=147,960. A coefficient-blind old guard
fails exact division; the corrected guard succeeds.

Additional controls establish:

- D^J fails at depth three: the first paid-child spine consumes 15 factors
  of 3 while J=14. D^(Jd) succeeds.
- A scalar/column phase substitution agrees at one column and fails at two.
  The semantic validator rejects it.
- Omitting odd retirement gives the exact incorrect factor 729.
- Every tested word is unfunded.

Run:

    python3 -I -B research/rational-all-column-c-word/review/check_final_code.py

FINAL-CODE-RESULT.json contains all domains, constants, capacities, counts,
controls, hashes, and output digests. The universal claim follows from the
induction and exact symbolic test, not these finite executions.

