# Independent full-matrix audit of the HPE energy radix

**PR1906's three literal HPE pairs are independently corroborated.** A separate
closed parser and direct integer realification reconstruct all six matrices,
including global phase. All 3,072 complex rows have the claimed common energy
and reproduce the predecessor's three whole-matrix row digests. No discrepancy,
new radix bound, Lean proof, supplier or multiplication exponent is claimed.

Audited predecessor: Arham Tahir's
[PR1906](https://github.com/CrocSwap/integer-mult-bounds/pull/1906), exact head
`788848032c16bbe0a543c1186c6691c66131c090`. Base main is
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA256 is
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
The selection remains the conditional finite frontier1094 result. This audit
does not run its cold replay or change any selected source.

## What this audit adds

PR1906 obtains rows by conjugating columns of an adjoint interpreter. It checks
all those rows, but its forward/adjoint correspondence check samples the 4 by 4
entries at indices `{0,1,255,511}` per circuit. Its second forward interpreter
shares parsing and phase helpers. Those are disclosed limitations, not evidence
that its formulas are wrong.

This audit imports **no predecessor code**. It independently parses the six
`lhsLit1..3` / `rhsLit1..3` definitions in the pinned `Exact.lean`, then propagates
the identity matrix through every gate in chronological order. The representation
is an integer matrix on 1,024 interleaved real/imaginary coordinates. Permutations
use explicit binary dot products and inverse pullback; C gates use integer
four-row combinations. No packed evaluation or adjoint is used for acceptance.
Extraction is specific to these authenticated definitions; this is not a general
Lean parser for arbitrary comments, layout or continued expressions.

For every complex coefficient, all four entries of its real 2-by-2 block are
checked against `[[Re,-Im],[Im,Re]]`. Each LHS/RHS comparison covers every
normalized matrix entry, including implicit sparse zeros. The six matrices
cover **6,291,456 real entries**. Their six row-digest calculations agree in
three pairs with the pinned precursor receipt; digests corroborate that receipt
and do not substitute for the direct matrix equality.

| Literal pair | LHS C count | RHS C count | Common row energy | Safe radix bits |
|---|---:|---:|---:|---:|
| 1 | 9 | 7 | 262,144 | 10 |
| 2 | 9 | 7 | 262,144 | 10 |
| 3 | 9 | 7 | 262,144 | 10 |

Each raw realification has 262,144 nonzero integer entries. Every row and column
has its correct squared energy, with common normalization applied to the rows.
The unchanged safe radix is `2^10`; the largest 512-coordinate packed input
would have 5,111 bits. No performance measurement or optimal radix for these
particular matrices follows.

## Independent mathematical review

A separately delegated exact-circuit specialist reviewed the written argument,
source gate semantics, normalization and this oracle. The parent also checked
the argument. This is independent AI review, not human review or a kernel proof.

The decisive argument is sound. For positive integer B and a nonzero finite
Gaussian vector d with `sum d_j B^j=0`, its first nonzero digit is a nonzero
Gaussian multiple of B. At least one later digit is nonzero, so
`E(d)>=B^2+1`. If `E(u),E(v)<=R^2`, the parallelogram identity gives
`E(u-v)<=4R^2`. Thus `B>=2R` excludes every nonzero kernel difference, including
the equality boundary. For integer `R>=1`, all smaller positive integer radices
have the two-coordinate collision
`u=(ceil(B/2),0)`, `v=(-floor(B/2),1)`. This establishes sharpness for the whole
ball in dimensions at least two, not for equal-energy unitary rows. Length zero
is vacuous and length one is injective at every positive radix.

The extra gate premise is essential. Mutual-inverse finite permutation maps and
involutive XOR maps make P and X unitary. With `P_+=(I+X)/2`, `P_-=(I-X)/2`,
the normalized C gate is `P_+ + s*i*P_-`; diagonal/global i-powers are also
unitary. Hence a normalized circuit U is unitary, and dropping k halves gives
`Z=2^k U` with both row and column energy `4^k`. Scaling each side to
`K=max(k_left,k_right)` supplies the row premise with `R=2^K`. A column-energy
bound alone is insufficient. Numeric energy checks do not independently prove
orthogonality; the gate-level argument supplies unitarity.

The retained generic Lean equality theorem accepts arbitrary literal lists.
The stricter valid-gate premise cannot be silently omitted when using the
improved energy bound. For a concrete failure, take an invalid permutation
pullback mapping every address to zero, then phase `i^x0`, then `C(1,+)`.
Its unnormalized output row zero is `(2+2i)e_0`, energy eight, while one C gate
would predict four. The new and predecessor validators both reject that
permutation. The test intentionally disables validation to expose this exact
mathematical failure.

## Reproduction and controls

Python 3.12, standard library only:

```sh
python3.12 -I -B scripts/research_package.py --package research/hpe-energy-independent-audit
```

Normal replay is read-only and requires the fixed `RESULT.json`. Explicit
regeneration is separate:

```sh
python3.12 -I -B research/hpe-energy-independent-audit/verify.py --write /tmp/hpe-energy-audit.json
```

The registered replay checks complete matrices and three semantic faults per
pair: global phase, input character and omitted common normalization. A C gate
followed by its inverse is accepted even though its raw integer scale changes.
Seven test groups additionally cover:

- All 585 words of lengths zero through three over eight two-qubit gates,
  against independently specified dense Gaussian-rational matrices. The
  alphabet includes noncommuting gates, a non-self-inverse permutation,
  both C signs, zero-mask C, quadratic phase, XOR and global phase.
- Wrong permutation direction, reversed noncommuting order, valid phase
  periodicity, the nonunitary energy witness, and complete realification.
- Closed literal inventory, malformed tokens, missing/duplicate definitions
  and a harmless whitespace presentation change.
- Seven scientific predecessor-receipt corruptions with checksum guards
  bypassed; actual detector removal makes the rejection harness fail.
- Missing/duplicate/corrupted evidence, source drift, explicit byte-identical
  regeneration, and an optimized read-only export without Git.

Detector-removal controls disable the named whole predicates to test the rejection
harness. They do not establish sensitivity to every possible implementation fault.

The primary PR1906 direct verifier was also replayed from its exact Git head
in isolated scratch and passed. That is a reproduction, distinct from the new
oracle. The written all-dimension proof is not inferred from finite tests.
No Lean toolchain was available locally. No Lean build, supplier cold replay,
new canonical-frame derivation, physical hosting/restoration proof, precision
or tape-cost admission, or all-size multiplication proof was performed.

## Sources and credit

`SOURCES.json` pins both live Lean inputs and the original task provenance.
`PR1906-RESULT.json` is the unmodified precursor receipt, reproduced under its
Apache-2.0 license with exact source head and SHA256. Its row digests are used
only as comparison evidence. No predecessor implementation is copied.

Credit Arham Tahir / PR1906 for the sharp energy-ball result; woklerx / PR1859
for the earlier unitary-premise radix; Jeremy Kothe / PR593 for the retained
Lean semantics, proof and literal circuits; commdata2338 for the earlier
semantic-binding work and parser (not reused here); Sagar Thakrar / PR1781 for
the distinct selected-recipe census; and the inherited Lemma A/G and Clifford
work by DreamingOfClouds, icekylinx, Chafik Boukhalfa and Zhihao Chen. Their
source notices remain unchanged. The added value is deliberate independent
verification, not priority for their construction or proof.

Prepared for Ross with substantial OpenAI Codex assistance in implementation,
mathematics, testing and prose. One exact-circuit specialist supplied separate
proof and code review. Apache-2.0. Task draw and refined scope are in `TASK.json`;
coordination is in [Discussion1896](https://github.com/CrocSwap/integer-mult-bounds/discussions/1896).

## Open next questions

Formalize the least-nonzero-digit energy bound and valid-gate row norms in Lean,
then connect them to the retained packed comparator. This is the remaining
formal adoption step, already identified by PR1906. The concrete first step is
the Gaussian kernel-energy lemma plus the parallelogram implication; the
blocker is the missing kernel proof. Kernel timing and compiler resource bounds
are separate. Repeating this six-matrix census is unnecessary unless its sources
or arithmetic change. Structured details are in `TASK.json`.
