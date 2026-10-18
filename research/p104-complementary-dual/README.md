# Complementary native frames for the corrected P104 dual

A finite native-frame realization submitted for review. No maintainer acceptance or new kappa is claimed.

[PR2497](https://github.com/CrocSwap/integer-mult-bounds/pull/2497), head
`7f2cf129d42030d3eb3975b7d1b07392c6d32a1b`, constructs a complete logical
inverse-transpose of the two-target corrected P104 word. Its reversed persistent
frame paths descend. Its second open question asks for complementary monotone
frames without increasing the invoice.

This package realizes that finite frame interface. It orthogonally complements
**every** literal frame in physical binary coordinates, retains all scalar
instructions, and independently checks new native recipes for all resulting
transports and intrinsic endpoints.

| Checked quantity | Result |
| --- | ---: |
| Literal events | 4,982 |
| Monotone persistent paths | 358 |
| Arbitrary boundary coefficients | 128,164 |
| Zero-restored private collectors | 8 |
| Native directed transport types / occurrences | 909 / 1,654 |
| Monomial intrinsic endpoint adapters | 208 |
| Positive transport rank mass | 3,126 |

The exact profile is unchanged from PR2497's zero-restored word:

```text
1216 H1 + 74 H2 + 86 H3 + 104 H4 + 48 H5 + 42 H6 + 76 H7 + 8 H8.
```

The 3,104 ADDs, 208 source signs and eight private allocations/erasures are
retained. There is no additional positive child from the 208 endpoint adapters.
This is a local invoice, not a recursive excess or complete hosted bill.

## Exact operator and proof

Write the forward logical map as

```text
S = [ I  0  0 ]
    [ C  I  0 ]
    [ 0  0  I ].
```

Here `C[t,s]=delta[t,s]` for `t=0,1`; otherwise
`C[t,s]=<p_t,p_s>/2`, with the retained P104 roots. The new word implements

```text
X_s <- X_s - sum_t C[t,s] Y_t,
```

and restores every Y and all 150 arbitrary dirty helper logical values. The
remaining 102 forward target rows are still G/2 rows, not identity rows.
The full asymmetric C-transpose is checked, including its zero entries.

The frozen source frames use compressed labels. First use PR1991's authenticated
Gram isometry to obtain physical labels with ordinary binary dot product. The
checker reconstructs all 120 E8 root lines, checks the compressed inverse Gram
matrix and all 14,400 physical pairings. Only then replace each physical subspace
`W` by `W-perp`. Taking the ordinary dot-product complement of the compressed
coordinates would not establish this result.

For every scalar instruction the old operands have the same frame, so their
complements also agree. Scalar rows therefore remain unchanged. For a transport
`A -> B`, complementation reverses inclusion and preserves the dimension gap:

```text
dim(A-perp) = 9-dim(A),
abs(dim(A-perp)-dim(B-perp)) = abs(dim(A)-dim(B)).
```

All persistent PR2497 paths descend; every complemented persistent path ascends.
The exact framed induction establishes physical value
`Gamma_(W-perp) * logical_row` at every cut. The new recipes establish each
literal change of canonical chart, including global phase. No cancellation of
unverified chart operators is assumed.

The persistent endpoint frames are:

- each Y source starts at its physical root line and ends at FULL;
- each X target starts at ZERO and ends at its physical root hyperplane;
- all 150 dirty helpers start at ZERO and end at FULL.

ZERO here names the zero-dimensional frame, not a zero logical value. All 358
persistent inputs remain arbitrary. Source intrinsic chart `C_q` and target
intrinsic chart `F9 C_q^-1` have exact rank-zero adapters to these endpoints.
Their global phases are checked separately for all 208 data endpoints.

Each private collector instead starts at a dimension-eight frame, descends by
rank seven to a line, returns by rank seven, and erases at exact logical zero.
There are sixteen such H7 uses, already included in the profile above. Those
private paths are deliberately **not** asserted monotone. Their admitted
physical storage contract remains open.

Let `A` and `B` be the block-diagonal canonical charts at the new entry and exit.
The proved physical operator is `B S^-T A^-1`. This is a **new realization** of
the same logical map. It is not a free conversion of the old physical arrays,
not equality to PR2497's old physical operator, and not a proof of physical
`F^-T` for the forward physical F. Any caller needing that different operator
must state and verify its chart binding.

## Reproduce

Standard-library Python. The generic registered environment is Python 3.12.
From repository root:

```sh
python3.12 -I -O -B research/p104-complementary-dual/verify.py
python3.12 -I -O -B research/p104-complementary-dual/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-complementary-dual
```

Default verification is read-only. It authenticates all external source bytes
before importing the credited native interpreter. It imports neither the
predecessor's producer nor the Clifford compiler. Signed Pauli actions and one
exact Gaussian state column determine each complete Clifford including phase.

`build.py --out NEW_FILE` regenerates all recipes using the retained compiler.
The tests compare the full decompressed JSON payload, not gzip container bytes.
The checked receipt binds the entire complemented word and native payload by
canonical SHA256. `verify.py --out NEW_FILE` writes a receipt exclusively to a
new file, never over an existing file.

Six semantic controls reject an actual persistent descent, omitted source sign,
nonzero collector erasure, wrong native global phase, wrong positive-child rank
and incorrect endpoint normal. A separate implementation uses binary Gaussian
nullspaces for all 7,352 literal frame occurrences and dense dyadic rows for all
128,164 boundary coefficients. Equivalent source bases produce the identical
complemented word. Source-before-import, missing evidence, exclusive output and
optimized Git-free read-only export tests cover the CLI evidence boundary.

## Scope and source binding

Scientific base and refreshed canonical main are
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4. Selected kappa
and all predecessor files remain unchanged. Source hashes and the exact PR2497
Git blob are in [SOURCES.json](SOURCES.json); the source word is retained
byte-for-byte in `inputs/CLEAN-DUAL.json`.

This closes only the finite complementary persistent-frame/native-price part
of PR2497's handoff. Physical initialization, scalar/address routing, recursive
precision, chronological ownership, idle/residual bills, private storage
admission, the remaining 102 target corrections and all-size/caller obligations
are not checked. There is no full supplier, favorable completed moment or new
kappa. No selected cold replay, proof-assistant or hosted CI run is claimed.

## Open next questions

1. Admit one literal rank8-to-rank1-to-rank8 collector with a complete physical
   allocation, routing, zero-return and erasure bill. Its exact logical zero and
   native rank invoice do not by themselves provide this storage contract.
2. Produce a complete 104-target corrected word and repeat the complementary
   frame/native checks on its actual bytes. The retained two-target map cannot
   establish a full identity supplier, even with correct opposite orientation.
3. Bind the required paired caller's intrinsic operators explicitly. If it needs
   physical F^-T rather than logical S^-T between the proved charts, a separate
   implication is required; this package does not silently identify them.

Structured questions and blockers are in [TASK.json](TASK.json).

## Credit

The complete logical word, zero-restoring collector mechanism and 56-rank return
charge belong to ywz65 / PR2497. PR2458 supplies its forward native predecessor;
Ross Richardson / PR2445 supplies the two-target correction. Retain credit for
commdata2338 / PR2393, Hiroki Kumazaki / PR2353, Philippe Van Velzen, Rohan Arun /
PR1972, Chafik Boukhalfa / PR1991, Adam Gall / PR1940, Josie Elliston / PR1071,
Ali Romman / PR1125 and the PR1862 interpreter, icekylinx / PR531 and the retained
Clifford/E8 lineage. Existing notices remain unchanged under
`research/p104-native-channel/notices/`. New material and the retained source
word are Apache-2.0.

This result is author-checked computation. No independent human or formal-kernel
review is claimed.
