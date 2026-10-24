# A Fibonacci paid-scan floor for two dense dirty outputs

For any finite number of arbitrary dirty banks, S inter-bank monomial ADD
scans and unary gates of total row-support exponent R can produce two
output banks of row support D only if

```
2^R F_(S+1) >= D,      F_0=0, F_1=F_2=1.
```

This scoped proof strengthens the earlier single-maximum support bound by
tracking the two largest bank support sizes. Arbitrary per-bank monomial
address/phase maps and permutations of whole banks are granted free. Every
ADD has distinct source and destination banks. [PROOF.md](PROOF.md) states
the full alphabet, induction and its same-bank boundary.

For the two full L-bit chirps in Ross Richardson's #4023, D=2^L. With no
native gates the necessary scan count is the least s with F_(s+1)>=2^L.
For L=3 this gives five ADDs instead of the inherited support-doubling floor
of three. This is a lower bound; no matching optimal word is claimed.
The selected kappa is unchanged.

## Evidence and reproduction

From the repository root, use CPython 3.12 and the standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/fibonacci-scan-floor
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/fibonacci-scan-floor --check-source-history
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/fibonacci-scan-floor/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/fibonacci-scan-floor/verify.py
```

Expected markers are `PASS_FIBONACCI_SCAN_FLOOR` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. The generated [RESULT.json](RESULT.json)
contains all finite counts and SHA256 hashes of the proof, verifier and
metadata. Default replay compares the complete receipt, including JSON
types, and writes nothing. The verifier works in a Git-free package copy.

The finite evidence includes every distinct sorted support-size relaxation
profile through seven gates for two through five banks, with unary exponents
one and two and total exponent at most four. Distinct-bank shears include
every ordered bank choice. Independent dense F5 executions test actual
cancellation, address permutations and unary operations. Tensor entries
corroborate chirp density through seven internal bits. One-fewer-scan,
invalid-input and same-bank-alphabet controls must reject.

The all-parameter conclusion rests on the written induction. No predecessor
verifier, native recipe, complete supplier, selected cold replay or proof
assistant is run. General free bank GL, buffered same-bank ADDs counted as
ordinary scans, multi-bank native gates, variable bank volumes and fused
traversals require separate models. Physical routing, precision, restoration
cost and actual runtime remain separate obligations.

## Scope and sources

Canonical base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
The connector-alphabet-change card changes scope to its cost-aware controller
boundary. Its old connector pairing fixture is not relevant to this alphabet
and is not replayed. The first new fixture is L=3 with two output banks.
The family decision is narrow: retain this quantitative obstruction and stop;
no further construction campaign or frontier change follows from it.

Ross Richardson's [#4023](https://github.com/CrocSwap/integer-mult-bounds/pull/4023)
supplies the paid two-chirp escape and its explicitly open constant-scan
question. His [#4082](https://github.com/CrocSwap/integer-mult-bounds/pull/4082)
and [#4057](https://github.com/CrocSwap/integer-mult-bounds/pull/4057) supply
the earlier support-doubling and paid-endpoint bounds in their respective
models. The standard union-of-support argument and Fibonacci recurrence
are not claimed as new methods. The new step is the two-bank order-statistic
invariant and the resulting paid-scan/native-support tradeoff.
[SOURCES.json](SOURCES.json) pins predecessor documentation as historical
provenance; no executable predecessor dependency is imported.

The live overlap scan covered 411 open PRs and 3,920 Discussion records at
2026-10-22 23:04 UTC. Sparse local notes were incomplete. Separate all-main
README and merged-PR searches covered the distinctive object and Fibonacci
terms. This coverage is not a novelty certificate. The canonical
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19134252)
records the question and scope.

## Open next questions

1. Find the exact ADD optimum between this lower bound and #4023's cited
   six-per-bit construction. Start at L=1 with two banks and explicit
   monomial shears. Exact feasibility may depend on available coefficients;
   no matching construction is supplied here.
2. Derive a weighted support bound for partial-volume or fused traversals.
   Start with a declared row-update and movement tariff. The present count
   charges full-bank serial shears, so supplies no runtime price in that model.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0. Credit Ross
Richardson for the predecessor constructions, support arguments and open
question, with their retained native and compiler lineage. Independent human
and formal proof-kernel review are unclaimed.

The verifier uses managed Python allocations. Its fixed finite domains and
explicit profile-capacity check bound live data; no constant-allocation
claim is made. All loops have finite domain bounds and no recursion is used.
Warning-strict normal and optimized replay check the committed artifact.
