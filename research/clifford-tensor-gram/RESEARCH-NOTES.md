# Continuation research record

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

## Starting point

The first result is commit 0db0609042d3bee25028ef6515fcee40a33e958d in
[PR #5376](https://github.com/CrocSwap/integer-mult-bounds/pull/5376).
It proves the 8n+4 positive-width cutoff and a 14/15 separation bound.
Both local modes, the export, mutation checks and hosted CI passed.
The continuation refresh found main at
1ec1119972c9aefe42525172d07b332fcff81cb4. Priority revision 7 and both
consumed kernels are unchanged. The selected kappa is not part of this work.

## Questions and acceptance tests

1. Can a degree-eight invariant reduce the number of widths to eight?
   Prove invariance under a complete native generating set. Prove the
   resulting kernel inclusion, with all width and coefficient quantifiers.
2. Can the filter bound improve from 14/15 to 75/76?
   Prove the coefficient signs and control their total absolute value for
   every n. Numerical samples do not establish the uniform bound.
3. What is the sharp one-axis positive-width cutoff?
   Combine an exact full-rank Gram certificate with an explicit lower-bound
   example. Do not generalize a one-axis result to other axis counts.
4. Can exact traces and entries avoid a dense 2^n base matrix?
   Derive a phase-exact quadratic-sum algorithm. Compare it with the frozen
   source and independent dense cases, including inverses and zero traces.
   Preserve possible exponential growth in expanded circuit support.

## Initial observations, not yet new accepted results

For n=1,...,12, exact filter coefficient sums give reciprocal positive mass
at least 75/76. The n=1 value is exactly 75/76. The later values increase
toward approximately 0.9887179563. These samples suggest a monotonicity
proof; they do not prove it.

The extended binary Hamming code of length eight is self-dual and doubly
even. Its row-code tensor is a candidate invariant for every axis count.
The classical code-invariant construction is prior work of Runge and
Nebe, Rains and Sloane, not a new invariant discovered here.

The original direct witness search examines all D^2 coordinate pairs at
each tensor factor. Even a compact trace routine alone does not remove
that search. A complete scalable extractor needs a separate argument.

## Results of the continuation

The proofs and algorithms are saved in [ADVANCES.md](ADVANCES.md),
[quadratic.py](quadratic.py) and [compact.py](compact.py).

1. The length-eight code invariant gives kernel inclusion from f+8 to f.
   Eight selected widths now suffice. For nine axes these are 69 through 76.
2. The coefficient sign pattern ++-- gives a monotonicity proof for the
   filter norm. Its maximum is 77/75 at n=1. Positive mass is at most 76/75,
   so the stable separation improves from 14/15 to 75/76.
3. The one-axis Gram sum at widths 5,6,7,8 has rank 96. A saved inverse
   over F_65537 proves this rank in characteristic zero. The previous
   Reynolds example proves that the maximum cutoff eight is sharp.
   Central scalar characters also prove that four widths are necessary.
4. Exact quadratic path sums retain the native global phase. Conditional
   sums with coordinate prefixes give a bitwise witness extractor. This
   removes both the dense base matrix and the D^2 coordinate scan.

The first modular experiment gave cumulative ranks modulo 65537 of
4,14,34,57,77,91,95,96 at widths 1 through 8. These are modular ranks;
the lower-width values alone are not characteristic-zero rank certificates.
The final proof uses the rank-96 inverse and the separate Reynolds obstruction.

The replay includes 640 exhaustive small quadratic sums, every one-axis
native group word, entangling two- and three-axis words, complete register
programs and exact positive relations. The large cases certify an explicit
64-axis entry and the phase relation on 65 axes. Full counts and literal
certificates are saved with the package.

## Performance correction

The initial filter routine repeatedly reduced rational coefficients. The
continuation instead multiplies integer numerator factors and keeps one
denominator. A direct comparison with the function from commit
0db0609042d3bee25028ef6515fcee40a33e958d gave identical coefficient lists
at n=0,1,2,9,16,32. One local CPython 3.14.7 measurement at n=32 took
0.283 seconds before and 0.0149 seconds after. This is one measurement of
the filter builder, not a full-verifier or provider speed claim.
The registered validation uses CPython 3.12.13 and checks the original
receipts as well as the new results.

The first read-only continuation replay found a receipt-comparison defect:
native gate tuples serialize as JSON arrays. Comparing the loaded arrays
with in-memory tuples fails even when the serialized bytes agree. The
receipt check now compares canonical serialized bytes. This fixes the
serialization boundary without changing mathematical values or certificates.

## Limits and routes not established

The eight-width embedding does not preserve the dimension-free stability
constant. The 75/76 bound still uses all widths from 1 through 8n+4. A
trace routine alone would not remove the coordinate search; the conditional
two-path sum is needed for that step. The general maximum cutoff is not
proved sharp, and the one-axis result cannot be extrapolated to n>=2.

The code invariant and binary quadratic-form method are classical. No
literature priority claim is made for those methods. The native phase
derivation, program binding, width refinements and reproducible certificates
are the contribution here. Symbolic word support can still be exponential.
No complete current provider, physical invoice or kappa improvement follows.
The written proofs remain author-checked with substantial AI assistance.

The final upstream refresh kept main at
1ec1119972c9aefe42525172d07b332fcff81cb4. The selected result and source
pins did not change. The canonical Discussion claim remains the coordination
point. This continuation updates the same focused PR.

## Local verification closeout

The registered runner passed all four commands on CPython 3.12.13:
the original replay and the continuation replay, each in normal and
optimized mode. One complete local run took 88.42 seconds. The original
receipts remain unchanged after the integer filter optimization.

Both mutation audits passed. Each of eight defects was rejected in both
Python modes, for 16 negative runs. The new defects change a native phase,
an inverse sign, a coordinate constraint and a dirty return. The metadata
and pinned-source check also passed. Exact commands are in README.md.

The final advisory overlap refresh at 2026-10-23 21:12 UTC covered 337
open PRs and 4,676 Discussion records, with complete remote pagination.
The new-term matches were this contribution and an unrelated occurrence
of 75/76 in a prior pencil-selection note. The sparse local checkout covers
only 16 of 7,269 note paths. Relevant predecessor proofs were read
separately. Historical diffs and unpublished work remain outside coverage.
The concurrent monomial PR remains at its previously reviewed head and
has not been changed by this work.
