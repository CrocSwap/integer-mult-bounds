# Audit argument and implementation boundary

## Claim being checked

At the exact PR3297 source head in EXPORT.json, fix T740 owner replica 0 and
port 0, the thirty hosted intervals, the complete chronological word and its
completed-call data-stream interpretation. Insert a nonzero multiplier `z_j`
at each of its twenty residual-child sites, including currently empty sites.
PR3297 claims that the normalized eight-stream operator determines every `z_j`
uniquely. This audit checks that source binding, the complete polynomial matrix,
and the published inverse. It does not discover or extend the theorem.

The eight raw inputs and their exact canonical blobs are in SOURCES.json.
`source.py` does not execute an earlier verifier. An unedited lifted row is

```text
(time, helper, owner, child, port, offset)
    -> (10*time+copy, helper, owner+74*copy, child, port, offset).
```

The journal replaces exactly 145 specified lifted rows and checks each preimage.
Owner zero in an unedited row requires base owner zero and copy zero. Edits into
or out of owner-zero/port-zero are handled separately. Exactly thirty rows remain.
Their provider widths and the source PLAN determine the hosted phase gates.
Orthonormality, nonoverlap and compact hosted prefixes are checked. The residual
axes are precisely the complementary suffixes. This is a direct projection,
not an independent allocation-feasibility or full expanded-fill-digest audit.

Local stage `s` uses the inherited data-stream formula. With
`Q(x)=parity(11 & x)` and `P_k(x)=sum_{i<k} x_i`, remove incoming phase
`(1-side)Q` at stage zero, or `P_(9+8(s-1))-side*Q` otherwise. Perform the signed
local shear and attach `P_(9+8s)-side*Q`. The actual source local pair and reverse
flag select its rows and sign. Idle children attach their residual-axis phase,
`2*parity(translation_after & x)`, and `z_j`. The remaining primitive operations
are source bridge shears, terminal Y translations and `(X,Y)->(Y,-X)`.
Finally subtract `sum_i x_i` from each stream. The audited raw word has 183
primitive gates. These formulas are inherited completed-call semantics; this
audit does not prove their native physical implementation.

## Why an uncancelled path expansion is exact

Start stream `j` with one path of origin `j`, coefficient one and no phase or
formal variable. A phase gate attaches its exponent and formal variable to
every path in that stream. A shear `dst += c*src` concatenates the destination
paths and copies of all source paths with their signs multiplied by `c`.
A signed terminal exchange swaps the path lists and negates the old X list.
These rules are distributivity and linearity, so induction on the chronological
gate list proves that the signed path sum is exactly the complete operator.
No paths merge and no cancellation occurs during this induction. Path objects
are immutable, so copying a source cannot mutate its earlier contribution.

Every site is inserted once in the actual primitive word. A path cannot contain
the same formal variable twice. `paths.py` checks both properties. The final
1,174 paths are collected by output stream, input stream, formal-variable mask
and complete character exponent. Their signed sum is exactly the 72 terms in
the byte-for-byte PR3297 export, checked on every matrix entry.

For a binary axis `a`, the exact Boolean phase polynomial is

```text
parity(a & x) = sum_i a_i*x_i + 2*sum_(i<j) a_i*a_j*x_i*x_j  (mod 4).
```

Expand `product_i(1-2*a_i*x_i)` to prove this identity. Terms of degree three
and above disappear modulo four after division by two. The sign of the
quadratic coefficient is immaterial modulo four. Phase addition and integer
scaling are coefficientwise modulo four. Thus the path identity is valid on
all `2^73` characters, not only coordinate characters. The small truth table
and high-bit mixed-character tests are controls for the implementation, not
the all-character proof.

After normalization, every surviving entry has character factor either one
or `g=i^(-parity(11 & x))`. The latter occurs only in odd-row/even-column
entries. The checker requires this factor pattern for all terms before
removing it in the inverse calculation. Since `g` is nonzero, this is valid.

## Inverse and denominator audit

The inverse formulas are the twenty-entry triangular inverse in PR3297's
PROOF.md. `inverse.py` reimplements their substitution using sparse integer
Laurent polynomials in the twenty original coordinates. It does not call a
predecessor implementation or accept random substitutions as proof.

Before every division, the substituted denominator must have exactly one
nonzero term and coefficient `+1` or `-1`. The retained receipt lists all
21 denominators as exponent vectors; all coefficients are `+1`. Hence they
are units in `Z[z0^+-1,...,z19^+-1]`. Each recovered expression is required
to equal its named coordinate as a full Laurent polynomial. Temporary
quantities such as `u` and `p` do not receive special trust; their complete
substituted polynomials must satisfy the same divisor check.

These identities prove that two nonzero parameter vectors with the same
matrix have the same recovered coordinates. The complete matrix at all
`z_j=1` is separately checked to be identity. Therefore the identity fiber is
exactly that point. Denominator nonvanishing is established on the map's image,
not on arbitrary eight-by-eight input matrices. A zero parameter is outside
the inverse domain; rejecting a zero divisor does not prove a zero parameter
has an admissible physical interpretation.

The rank corollary is PR3297's. For independent binary axes of rank `r`, a
uniform character gives independent fair parities and
`E f_A=((1+i)/2)^r`, so `|E f_A|^2=2^-r`. Separate all-character phase equality
therefore fixes each residual rank. Repeated/dependent replacement lists do
not meet this hypothesis. Equal phase does not assert literal basis equality.
The old nonzero residual ranks are one at sites 4, 6, 14, 15 and 48 at sites
8, 10, 12, 13, as independently reconstructed in the receipt.

## Verification controls and limits

The tests compare the complete matrix to a separate direct Gaussian-integer
primitive evaluator at five characters and three simultaneous nonzero phase
vectors. This checks arithmetic and global phase, but shares the raw-source
compiler and is not a third independent physical model. Source-semantic
controls remove a hosted phase, an empty-site insertion, a dirty translation
or a terminal exchange, and reverse a bridge sign. Each fails the retained
matrix certificate or its character-factor requirement. Wrong coefficients
and illegal divisors fail the inverse check. Source/export corruption and
journal errors fail before a scientific result is accepted.

This package does not test other owners/ports, change charts, rederive native
execution, reprice the full invoice or prove supplier admission. It does not
validate the helper-bank interpretation excluded by the data-stream projection.
The theorem remains conditional on that predecessor interface.

## Engineering bounds and deviations

The source JSON is authenticated before interpretation. Each raw/decoded input
is capped at 32,000,000 bytes. The fixed base fill has 271,728 rows; the journal
has 145 edits, the base order 666 entries, the lift ten copies, the schedule at
most 64 events, and there are twenty sites and 73 character bits. The compiler
caps the word at 512 gates. The path interpreter rejects growth beyond 4,096
uncancelled paths, versus 1,174 in this word. Character polynomials have at most
2,701 terms. Laurent intermediates have at most 256 terms, and each product has
at most 65,536 pair operations. No recursion, runtime code generation, dynamic
imports or indirect plugin dispatch is used. Every function is under sixty
physical lines. Failure controls exercise the gate/path caps and illegal gates.

Power of Ten rule 3 requires a managed-runtime deviation for Python object and
integer allocation. Source-sized collections, fixed gate/path/term bounds,
serial execution and process-scoped ownership bound this finite checker; it is
not a steady-state allocator. JSON-library object overhead is not preallocated
or measured. A native fixed-capacity port would be the follow-up if this checker
became a long-running service. Rule 9 also retains Python's ordinary data-class
and container references, rather than claiming C pointer-level compliance.
The objects have one local owner or are immutable. Diagnostics are run with
`-Werror` and the repository's Ruff configuration; no diagnostic is suppressed.
