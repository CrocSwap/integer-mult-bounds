# Cubic and quintic response sectors cannot mix

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written proof with exact finite corroboration.
Independent human and formal proof-kernel review are unclaimed.

Let U be a unitary Clifford on M qubits with entries in Q(i). If the actual
whole-bank matrix satisfies `(Phi3 Phi5)(U)=0`, then exactly one of Phi3(U)
and Phi5(U) is zero. The operator has exact order three or five. By the cited
pure-factor theorem of [#6192](https://github.com/CrocSwap/integer-mult-bounds/pull/6192),
its Pauli symplectic defect has rank two or four, respectively, and its
native B rank is at most min(M,4). This product relation cannot create an
unbounded-native-rank response family. No new kappa is claimed.

The new step answers the explicit Phi3/Phi5 test in #6192's Open next
question 2. It does not recheck the primitive-factor theorem. The
[proof](PROOF.md) derives `2a+4b=2^M` and `Tr(U)=-a-b`. A nonzero integer
Clifford trace has magnitude a power of two. If both sectors occur,
`2^(M-2)<a+b<2^(M-1)`, a contradiction.

Ross Richardson's [#4081](https://github.com/CrocSwap/integer-mult-bounds/pull/4081)
supplies the earlier Clifford trace gate; #6192 supplies the field and
pure-factor background. Classical cyclotomic and Pauli-character facts retain
their classical status. No literature-wide priority claim is made.

## Reproduction and evidence

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/two-cyclotomic-no-mixing/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/two-cyclotomic-no-mixing/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/two-cyclotomic-no-mixing
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/two-cyclotomic-no-mixing --check-source-history
```

Any CPython 3.12 installation may replace the local interpreter path.
The direct marker is `PASS_TWO_CYCLOTOMIC_NO_MIXING`; the registered runner
also prints `PASS_REGISTERED_RESEARCH_PACKAGE`. Both registered commands
cover the same complete finite domain, with checks active under `-O`.
The verifier writes no files. `--emit` prints a computed receipt binding
all six package files by SHA256 and recording the interpreter version;
redirect it outside the checkout.

All 131,089 nonnegative spectral multiplicity pairs at widths 1 through 18
are enumerated. Exactly 35 pure endpoints pass the trace gate; all 131,054
mixed pairs fail. The written proof supplies the unbounded quantifiers.

Four complete Gaussian-rational matrix fixtures check unitarity, the two
polynomials and their product, exact order and every Pauli generator image.
The cubic and quintic matrices are positive fixtures. An eight-by-eight
unitary with both sectors satisfies the product but fails Cliffordness.
A Clifford of exact order fifteen fails the product relation. These controls
prevent replacing the hypotheses by unitarity or finite order alone.
Polynomial convolution, four integer trace tests, a non-qubit arithmetic
control and two capacity rejections supply additional checks. The receipt
records every matrix's outcomes. The quintic fixture is credited to #6192;
no predecessor executable is imported or run.

## Scope and provenance

The `joint-query-controller` card is explicitly changed to this algebraic
response-interface obstruction. A bounded-degree response is a proposed way
to avoid growing native cost; this result closes one named product-polynomial
escape. It supplies no completed producer/consumer or favorable paid invoice.
The selected frontier, kappa and five framework assumptions retain their status.

[SOURCES.json](SOURCES.json) pins the cited statements and assignment
provenance to main `e54523517d0f03e58352e647c403a5af3e525a57`, revision 8,
selected #7000. All predecessor pins are provenance, not executable inputs.
The selected metadata baseline passed after its sparse source closure was
materialized; that check was orientation, not a scientific replay.

Overlap checks covered live open PRs, this account's 38 PRs created within
seven days, recent handoffs and active Discussions, main README searches,
merged cyclotomic/Phi3/Phi5 searches and local reservations. The cached
helper reported 477 open PRs and 7,121 Discussion records with complete
pagination, but only 177 of 10,178 local note records. Both the general
mixed-factor form and the literal polynomial were searched. Arbitrary diffs
and unpublished work remain coverage limits.

The exact whole-bank relation and actual global phase are essential to the
statement. Other products, coefficient fields, restricted-input relations
and approximate identities are not classified. Physical caller realization,
dirty restoration, ownership, hosting, precision, stock, tape execution,
compiler closure and supplier admission remain outside this contribution.
No selected cold replay, native replay, Lean or Docker build was run.

## Verification implementation limits

The fixed-domain checker uses at most eight-by-eight matrices, three qubits
for matrix fixtures, 128 signed Paulis, polynomial degree at most fifteen,
and fifteen multiplications for an order test. The multiplicity loop has
eighteen widths and at most 65,537 pairs at one width. Functions fit within
sixty physical lines. Explicit invariant failures remain active under
optimization. There is no recursion, dynamic code loading, subprocess or
external dependency. Matrices and coefficients are fixed in the source.
The only file reads are the six package files for receipt hashes, each
capped at 100,000 bytes after reading.

Power of Ten rule 3 has a managed-runtime deviation: Python allocates rational
numbers and collections dynamically. Fixed matrices, finite Pauli tables,
a streamed multiplicity census and the six-file receipt bound live data.
Rule 9 uses built-in `len` as the sole `map` callback over at most four
blocks. Warning-strict normal/optimized runs and AST compilation provide the
available diagnostics; no external static analyzer is claimed.

## Open next questions

1. Can Phi3*Phi15 support genuinely mixed sectors in a whole-bank
   Gaussian-rational Clifford? Its primitive traces have opposite signs,
   so the present bracket does not apply. First solve multiplicity and
   power-trace constraints, then seek a full Pauli action. No construction
   or exclusion is supplied here.
2. Can three same-sign primitive sectors evade this two-sector argument?
   First enumerate dimension and trace constraints for Phi3*Phi5*Phi17.
   The present proof gives no general product classification or physical
   caller.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).
