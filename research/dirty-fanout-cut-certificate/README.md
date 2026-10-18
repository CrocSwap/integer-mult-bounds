# Exact dirty-output circuits with small cut certificates

**Scoped proof simplification and synthesis tool.** A supplied complete directed
tariff matrix now produces a restored-XOR circuit and an independently checkable
optimality certificate. The checker uses a weighted sum of elementary dirty-data
cut inequalities; it does not import the optimizer or invoke the external
branching theorem used by PR3121. No physical supplier or new kappa is claimed.

## What changes

Ross Richardson's [PR3121](https://github.com/CrocSwap/integer-mult-bounds/pull/3121)
proved the exact stationary dirty-output fanout tariff. Its executable enumerates
small forests. This package supplies the classical Chu-Liu/Edmonds contraction
algorithm, emits the actual preparation/oracle/restoration word, and verifies a
matching lower bound for **all permitted interleaved words**, not only forests.

The reusable observation is simple. For any nonempty set S of output rows,
a successful word must either invoke the shared-value oracle inside S or pay
at least two incoming ADDs to deliver the value and restore arbitrary dirt:

```
oracle_calls(S) + incoming_ADDs(S)/2 >= 1.
```

Price several such cuts. If their combined load is at most mu_i on every oracle
and 2c_ij on every ADD edge, their total price lower-bounds every successful
word. When the emitted circuit costs exactly that total, optimality follows.
[PROOF.md](PROOF.md) gives the self-contained argument, credited subset lemma,
contraction invariant, complete word and scope. This is an explicit application
of classical graph optimization, not a new general optimization theorem.

A useful failure control is the cheap directed cycle: per-row cheapest choices
suggest cost 5 but cannot reach a root. The certificate adds the missing
joint-cut price 98, proving the correct optimum **103**. This catches the
structural error with inequalities, without enumerating competing circuits.

## Executed evidence

- All **530** tariff matrices through three rows with every positive price in
  `{1,5}` match unrestricted exact shortest paths on affine maps: **394** strict
  sharing wins and **240** mixed-root certificates.
- **48** seeded rational instances through six rows match a separate exhaustive
  parent-function implementation, checking **145,984** forests across those cases.
- Nested-cycle examples through **112 rows** compile and pass the separate checker.
  The 112-row fixture has **216 cut prices**, **12,544 capacity inequalities**,
  one oracle and 222 ADDs. Its declared optimum is **1,539**.
- Eleven semantic/certificate mutation controls, four invalid-price cases,
  source/receipt/cost corruption, duplicate input keys and optimized read-only
  Git-free replay pass. A valid certificate with crossing cuts is accepted even
  though the compiler only emits laminar cuts. The exported CLI checker runs
  after the compiler file is removed.

[RESULT.json](RESULT.json) records complete deterministic receipts.
[CERTIFICATES.json](CERTIFICATES.json) contains the exact named certificates in
compact JSON. The large matrices are **synthetic stationary tariffs**, defined
exactly by `hierarchical_prices` with seed 19; they are not prices of the selected
supplier. The finite searches corroborate the proof and implementation, rather
than prove a full physical multiplication theorem.

The implementation uses O(q^3) rational arithmetic operations, and its certificates
have at most 2q-1 cuts. Bit lengths and the complete input matrix are real costs;
no unit-cost physical-tape claim is made. On the same six-row instance, three
alternating CPython 3.12.14 runs gave median **49.75 ms** for exhaustive enumeration
and **0.684 ms** for compilation plus the full checker (about 73x). Both returned
exactly 49. [BENCHMARK.json](BENCHMARK.json) records every timing, input digest and
environment. This compares the new exhaustive reference with the new compiler,
not two versions of a production physical routine. Timing is descriptive, never
a mathematical acceptance threshold.

## Use and reproduce

Python 3.12 standard library, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/dirty-fanout-cut-certificate
```

Expected markers: `PASS_DIRTY_FANOUT_CUT_SYNTHESIS`,
`PASS_DIRTY_FANOUT_CUT_EXPORT_CONTROLS`, and `PASS_REGISTERED_RESEARCH_PACKAGE`.
Direct `verify.py --suite small`, `examples` or `controls` runs a bounded subset.
`verify.py --emit` prints a fresh receipt and writes the named certificates.
`benchmark.py` reruns the same-input timing comparison without a speed threshold.

For a user-supplied tariff matrix, `mu[i]` prices a complete P_i call and
`add[i][j]` prices ADD(i,j), directed **j -> i**. Diagonals must be null; all other
prices are positive integers or exact rational strings. No float prices:

```sh
python3.12 research/dirty-fanout-cut-certificate/synthesize.py \
  research/dirty-fanout-cut-certificate/examples/chain.json > /tmp/fanout-certificate.json
python3.12 research/dirty-fanout-cut-certificate/check.py \
  research/dirty-fanout-cut-certificate/examples/chain.json /tmp/fanout-certificate.json
```

Expected: `PASS_DIRTY_FANOUT_CUT_CERTIFICATE`, cost `5`, one oracle and four ADDs.
The checker can be distributed separately with the tariff and certificate files.
It contains no solver dependency. Direct execution requires no Git, network,
third-party libraries or predecessor executable.

Exact scientific base: **`997e6a9ca7b4f95d50e366f61412fd640d72a88a`**.
[SOURCES.json](SOURCES.json) pins live predecessor documents and records exact
PR3121 reference hashes/head. The subset argument is rederived in the local
proof; no pending predecessor code or graph theorem is imported at runtime.
[TASK.json](TASK.json) records the changed card scope, seed, candidate selection,
completed domains and stopping rule. [Coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/3061#discussioncomment-18989707).

## Open next questions

The model requires arbitrary independent dirty output rows, the same arbitrary
common value from disjoint preserved sources, stationary complete positive
prices and unobserved intermediate rows. There are no extra helpers or free
COPY/CLEAR/basis changes. A separately required inverse has the same bill and
must be paid again. Path-, state- or frame-dependent prices require a new model.

The next physical task remains to name one operand-compatible caller, prove its
target lifetimes, and price every oracle/ADD route including access, frame
adapters, precision, restoration, ownership and head return. Those obligations
block supplier admission; this tool does not remove them. Once that matrix is
available, synthesis and a directly inspectable optimum certificate are ready.

A separate optional formalization can encode the dirty-span lemma and weighted
inequality, then the finite checker. This would shrink the trusted software
boundary further; no proof-assistant or independent human verification is claimed.
The selected frontier, frozen packages and `upstream/` are unchanged.

## Credit

Prepared by **Tekalign**, with substantial **OpenAI Codex** assistance in
mathematics, coding, verification and writing; Apache-2.0. Credit Ross Richardson's
PR3121 at `eea0861aff47df568be4bb4a4db43c2da390d351` for the subset lemma, edge-price
optimum and chain example; PR3063 at `3f384b8b7daccb2c8e12013fd81a738202ce0f8d` for
the destination tradeoff; Cinna Davis/PR1944 for the original dirty echo; PR1968's
separate multiple-term accumulation; Anthony/PR774, Oscar Fennell/PR759 and the
retained forest-synthesis lineage. Their discoveries are not claimed anew.

Credit Chu and Liu (1965) and Edmonds (1967),
[Optimum branchings](https://doi.org/10.6028/jres.071B.032), for the classical
contraction/optimization method. The code is newly written without copying a
third-party implementation. The contribution is the explicit cut-certificate
application, compiler and separate checker for this dirty-output contract.
