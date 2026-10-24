# Finite, stable tensor tests for the full dyadic Clifford group

**A uniform algebraic interface theorem and an exact verifier; no new kappa.**
For fixed scalar register programs on n binary axes, with unitary dyadic
Clifford operators and every dirty input/return retained, equality at the
**eight widths 8n-3 through 8n+4 implies equality at every positive width**
for n>=2. For one axis, **widths 5,6,7,8 suffice**, and both the maximum
cutoff eight and the number of tests four are sharp. For zero axes use
widths 1,2,3,4. This
covers Gaussian and Hadamard gates as well as phase-monomial maps. The cutoff
does not depend on program length or expanded support.

The [original proof](PROOF.md) and [extensions](ADVANCES.md) give a stable test.
Let M be the squared coefficient
norm after equal exact native operators are combined. Some tested width has
normalized squared Hilbert-Schmidt residual at least **(75/76)M** among all
widths 1 through 8n+4. An explicit
rational polynomial recovers M from the finite norm sequence. Base-space pair
traces suffice. The compact implementation uses exact quadratic sums and
bitwise conditional norms. It builds **neither a dense base matrix nor a
tensor matrix**, and it removes the original D^2 coordinate scan.

For the source's nine binary axes, **eight tests at widths 69 through 76** suffice.
This is an algebraic bound, not a full supplier replay or a minimal cutoff.
The complete kappa calculation and selected frontier are unchanged.

The [complete-provider application](PROVIDER.md) now passes both directions
of the selected PR4610 local provider: all 633 inputs and returns, 7,000
oriented native recipe classes, and the full physical programs. It also
excludes **30,328 early/late pair fusions at every positive tensor width**.
The domain contains every pair of paid climbs on one persistent role, at
all ranks and without an adjacency condition. The [result](provider/RESULT.json),
[full-program witnesses](provider/WITNESSES.json), and
[research notes](provider/RESEARCH-NOTES.md) preserve the evidence and limits.
No paid job is removed and kappa does not increase.

## A concrete small-width trap

The [Reynolds example](examples/reynolds.json) adds the average of the 96
one-axis native group operators to a dirty target. It preserves the source.
Its complete endpoint is the identity at widths **1 through 7**, but fails at
width **8**, with a literal entry **5/24**. The
[certificate](examples/reynolds.certificate.json) gives the roles and coordinates.
This example uses the full group, not a numerical sample.

## Use

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/clifford-tensor-gram
```

The registered commands print `PASS_CLIFFORD_TENSOR_GRAM_NO_NEW_KAPPA` and
`PASS_CLIFFORD_ADVANCES_NO_NEW_KAPPA` in normal and optimized Python.
The provider commands also print
`PASS_COMPLETE_PR4610_PROVIDER_AND_30328_FUSION_OBSTRUCTIONS`.
Direct commands also work in a Git-free export:

```sh
python3.12 -I -W error -B research/clifford-tensor-gram/verify.py
python3.12 -I -O -W error -B research/clifford-tensor-gram/verify.py
python3.12 -I -W error -B research/clifford-tensor-gram/verify_advances.py
python3.12 -I -O -W error -B research/clifford-tensor-gram/verify_advances.py
python3.12 -I -W error -B research/clifford-tensor-gram/verify_provider.py
python3.12 -I -O -W error -B research/clifford-tensor-gram/verify_provider.py
python3.12 -I -B research/clifford-tensor-gram/compact.py \
  research/clifford-tensor-gram/examples/native-64.json
python3.12 -I -B research/clifford-tensor-gram/certify.py \
  research/clifford-tensor-gram/examples/native-relation.json
python3.12 -I -B research/clifford-tensor-gram/check_witness.py \
  research/clifford-tensor-gram/examples/reynolds.json \
  research/clifford-tensor-gram/examples/reynolds.certificate.json
python3.12 -I -B research/clifford-tensor-gram/audit_mutations.py
python3.12 -I -B research/clifford-tensor-gram/audit_advances.py
```

The producer prints JSON. Read `equivalent_at_all_positive_widths`; a successful
process means the decision completed, and a counterexample is a valid result.
The independent witness checker prints `PASS_LITERAL_TENSOR_WITNESS 5/24`.
Relative to the original dense producer, it uses a separate signed-word
interpreter and literal matrix entries, with
no producer import, trace calculation or interpolation argument. Only the
frozen scalar arithmetic is shared.
It checks the literal nonzero entry, not the claimed norms or the universal
cutoff theorem.

The compact producer reuses that signed-word expansion. Its differential
checks use the original dense compiler, frozen source matrices and literal
entries. It is not an independent checker of itself. The research record is
saved in [RESEARCH-NOTES.md](RESEARCH-NOTES.md).

## Input contract

`compact.py` uses the same roles and instructions below, but each value in
`operators` is a literal native circuit. See the
[64-axis example](examples/native-64.json) and
[65-axis phase relation](examples/native-65.json). The native gate forms are
`["P", rows]`, `["X", offset]`, `["D", rows, alpha]`, `["C", mask, sign]`
and `["phase", exponent]`. Binary matrix rows are integer masks. Diagonal
alpha values belong to 0,1,2,3 and have the diagonal row parity. C signs
are +1 or -1. The parser checks the native gate conditions.

The compact certificate records the reduced decision widths. For a negative
result it still computes all 8n+4 norm values to use the stronger stability
bound and select its witness. The eight-width theorem alone does not give
that dimension-free bound on the selected eight norms.

The [native relation example](examples/native-relation.json) gives the format.
`axes` is n; `roles` counts arbitrary independent inputs and returns.
`operators` contains exact 2^n-by-2^n matrices, with integer entries or
Gaussian-rational strings such as `1/2-1/2i`. Floats are rejected. The frontend
checks dyadic entries, unitarity and normalization of all Pauli generators.
`program` and `reference` are complete instruction lists. An empty reference
is identity on every role.

| Instruction | Required fields | Action |
| --- | --- | --- |
| `add` | `src`, `dst` | Add a scalar multiple of a role |
| `query` | `src`, `dst`, `symbol` | Add an operator image of a role |
| `apply` | `dst`, `symbol` | Apply an operator to a role |
| `scale` | `dst`, `coefficient` | Scale a role |
| `swap` | `src`, `dst` | Exchange roles |

`add` and `query` accept an optional `coefficient`, default one. `query` and
`apply` accept Boolean `inverse`, default false. Self queries read the previous
value. Global phase stays inside the tensor power; scalar coefficients stay
outside. The source convention has H^2=iI. Replacing that operator with scalar
scaling by i passes width one and fails width two, as the
[phase example](examples/phase-trap.json) shows. Scalar coefficients need not
be dyadic.

## Evidence and limits

[ADVANCES-RESULT.json](ADVANCES-RESULT.json) records the continuation:
256 code Fourier values, exact filter bounds for n=0,...,64, a rank-96
modular inverse certificate, 640 exhaustive small quadratic sums, 3,328
native entries, 128 native traces, 304 partial inner products, 48 complete
program comparisons and literal witnesses, nine exact native relations,
a scalar-phase trap and eight rejection controls. The large cases use
64 and 65 axes. Their base dimensions are 2^64 and 2^65; no dense base
array is allocated. The 64-axis witness is the exact entry 1/4294967296.
The 65-axis relation retains H^2=iI as a native operator identity.

[RESULT.json](RESULT.json) records 96 group elements, 689 exact trace-filter
values, 2,124 source columns, 48 entangling trace cases, 60 explicit tensor
norms, 72 complete endpoint comparisons, 24 full tensor program comparisons,
16 random literal witnesses, two zero-axis boundary cases and 20 controls.
The source columns include both
orientations of an actual nine-axis Gaussian gate. Controls reject nonunitary
inputs, non-dyadic phases, Toffoli, malformed instructions, wrong tensor phases,
missing helper returns and false witnesses. Source hashes are checked before
the replay imports the frozen files.

[MUTATIONS.json](MUTATIONS.json) records four private-copy defects rejected in
both Python modes: a missing trace factor, an ignored inverse, an omitted
dirty return and a missing Gram normalization. The audit prints
`PASS_CLIFFORD_GRAM_MUTATIONS`. The local runs used CPython 3.12.13 on macOS
with no third-party packages.

[ADVANCES-MUTATIONS.json](ADVANCES-MUTATIONS.json) records four additional
defects rejected in both modes: a wrong native C phase, an ignored native
inverse sign, a missing prefix constraint and an omitted dirty return.
The audit prints `PASS_CLIFFORD_ADVANCE_MUTATIONS`.

The written proof supplies the universal quantifiers. Finite tests corroborate
it. This is author-checked with substantial AI assistance, not independent
human or proof-kernel acceptance. Compilation can expand exponentially many
terms. The compact path and witness algorithms use polynomial work in the
axis count, literal word length, tensor width and expanded support. The
original dense frontend still uses base dimension 2^n. No polynomial-time claim in instruction
length or practical full-supplier speedup follows. The provider application
checks the complete selected local word and its native recipes. A selected
controller/compiler cold replay, new admission, Lean and Docker are not run.
Physical storage, tapes, stock, precision and outer recovery remain separate.
Programs that change with f, non-Clifford gates, continuous phases, nonunitary
native operators, rounded leaves and restricted clean-input contracts are excluded.

## Sources and credit

Base: canonical main `7c472563474e60185e6ca101a17622133d047e56`, priority 7.
[SOURCES.json](SOURCES.json) binds exact sources. No predecessor is modified.
The provider application has the separate current-main pin
`1ec1119972c9aefe42525172d07b332fcff81cb4`; its source copies and full credit
are in [provider/SOURCES.json](provider/SOURCES.json) and
[provider/NOTICE.md](provider/NOTICE.md).
Rohan Arun supplies the retained native compiler, following Jeremy Kothe and
the native lineage. Tekalign's retention and Cinna Davis's borrowing work keep
their credit. The complete [notice](vendor/NATIVE-LINEAGE-NOTICE) accompanies
the byte-identical kernel.

zxv's [PR #5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235)
supplies the independent-symbol interface and frozen Gaussian arithmetic.
Krzysztof Wojt's [PR #5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262)
supplies the inverse-aware interface and native-relation handoff. lm1909's
[projection-recursion check](https://github.com/CrocSwap/integer-mult-bounds/blob/7c472563474e60185e6ca101a17622133d047e56/research/projection-recursion-check/README.md)
already uses positive-width group separation, following Jacob Alan Sussman's
engine model. Cinna Davis, ToikY, Sagar Thakrar, roger-sato and the retained
free-word/tensor audits keep their earlier results and attribution.

Chris R's [PR #4928](https://github.com/CrocSwap/integer-mult-bounds/pull/4928)
and [PR #4978](https://github.com/CrocSwap/integer-mult-bounds/pull/4978)
already use finite Clifford alphabets and tensor Gram separation. Their
[general separation proof](https://github.com/CrocSwap/integer-mult-bounds/blob/7c472563474e60185e6ca101a17622133d047e56/research/two-full-retained-helper-ceiling/science/PROOF.md)
and [passive-query clarification](https://github.com/CrocSwap/integer-mult-bounds/blob/7c472563474e60185e6ca101a17622133d047e56/research/passive-saved-query-ceiling/evidence/frozen/pr4948-saved-query-macro-gate/UNIFORM-ALPHABET-ADDENDUM.md)
retain that credit. This package adds an explicit linear cutoff and constant
stability bound for fixed scalar coefficients in the full dyadic class.

Concurrent [PR #5369](https://github.com/CrocSwap/integer-mult-bounds/pull/5369)
proves a four-width criterion for affine-quadratic monomial maps.
Its scope excludes Hadamard gates. The
[coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5236#discussioncomment-19153620)
records this package's larger class, Gram test and stability claim. Public
PR/Discussion bodies and relevant main notes were checked. Historical diffs
and unpublished work remain outside coverage.

Classical ingredients are credited in [PROOF.md](PROOF.md). No new general
Burnside-Brauer theorem, general circuit identity algorithm or global priority
is claimed. The contribution is the explicit native trace filter, stable
cutoff, program frontend, compact witness and source-bound validation.
The code invariant follows Runge and Nebe, Rains and Sloane. The binary
quadratic-form method follows Dehaene and De Moor. [ADVANCES.md](ADVANCES.md)
links those sources and derives the native phase conventions used here.

## Open next questions

1. Find the sharp maximum cutoff for n>=2. The one-axis maximum eight is
   now sharp. The general eight-width test still reaches 8n+4.
2. Prove a useful stability constant on the eight selected widths. The
   present 75/76 bound uses the full range 1,...,8n+4.
3. Bind a complete current provider and measure support growth. Retain every
   input/return and native phase. Physical admission and a full bill remain open.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
