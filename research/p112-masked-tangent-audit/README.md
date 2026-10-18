# Exact P112 masked decoders: the coordinate connected component

**Scoped structural result; no new κ or physical supplier.** Every continuous
path of exact eight-term masked decoders starting at the standard P112 decoder
remains a reciprocal row scaling and a factor-basis change of an all-pairs
decoder. Consequently that entire path retains the inherited copy-cost floor
of **64**, even though both factors may leave the root-coordinate column space
and the odd-pair entries may change.

This closes one concrete way of approaching the masked-decoder opening left by
PR968/1077: continuous exact deformation from the coordinate construction.
It does not exclude a disconnected masked component, a discrete or approximate
search that reaches one, or a decoder with nine or more terms. A merely local
cost floor already follows from persistence of nonzero entries; the useful
result here is the **whole connected-component classification**.

## Precise result

For the explicit 112 live E8 root lines, use the eight deleted frame roots as
coordinate normals. The resulting integer matrix `Y` satisfies `YᵀY=56I`;
`K=YYᵀ` is twice the true-root Gram matrix. Constrain `DTᵀ=K` only on the
6,720 ordered diagonal and orthogonal-pair entries. Both factors have eight
columns, with arbitrary complex coefficients and ordinary transpose.

The connected component containing `(Y,Y)` is exactly

```
D = S Y A,       T = S⁻¹ Y A⁻ᵀ,
```

where `S` is invertible diagonal and `A` is an invertible 8×8 matrix. The result
also confines every real continuous path from `(Y,Y)` to the corresponding
real orbit. Limits cannot escape via deficient-rank factors.

[PROOF.md](PROOF.md) gives the argument: an exact tangent certificate makes the
orbit open, and the connected graph of nonzero unconstrained entries makes it
closed. The primary checker computes rank **1,617** for the **6,720 × 1,792**
integer Jacobian; 175 independent integer null vectors prove the matching
upper bound. A separate implementation splits the equations and obtains
ranks **868 + 749** using different finite-field arithmetic.

## Reproduce

From the repository root, Python 3.10+ and the standard library:

```sh
python3 -I -B research/p112-masked-tangent-audit/verify.py
python3 -I -B research/p112-masked-tangent-audit/independent.py
python3 -I -B research/p112-masked-tangent-audit/test_package.py
```

The path-scoped [GitHub Actions workflow](../../.github/workflows/p112-masked-tangent-audit.yml)
runs these checks, the inherited complex-floor replay and selected-record
regressions on Ubuntu 24.04 with Python 3.10 and 3.14. It also requires tracked
sources and certificates to remain unchanged. Hosted run status is linked from
the pull request; successful local execution alone does not imply hosted success.

The primary success marker is:

```
PASS_P112_MASKED_COMPONENT rank=1617 nullity=175 mask=6720 odd_edges=2912 controls=9
```

The primary replay is a few seconds on the recorded machine; the
independent replay is under one second. `verify.py --write` regenerates
[CERTIFICATE.json](CERTIFICATE.json); default verification is read-only and
compares the complete recomputation with the saved certificate. Optimization
(`-O`) is supported. [VALIDATION.md](VALIDATION.md) records actual runs and scope.

The primary implementation uses sparse Gaussian elimination over F101 and
explicitly rechecks its selected square minor. The independent implementation
constructs symmetric/antisymmetric equations and uses bitset elimination over
F3. Both pair modular rank lower bounds with integer null-vector identities,
so the stated rank is exact over Q, R and C, not a finite-field guess.

Controls include a valid masked example outside both root codes, incorrect
reciprocal scaling, a missing diagonal constraint, a wrong transpose sign,
a basis change that alters supports, an exact complex phase distinguishing
transpose from conjugate transpose, and a rank-nine completion outside the
claimed orbit. Package tests reject changed/missing source proofs and a
corrupted rank receipt, and run both checkers in an isolated relocated tree.

## Sources, overlap and limits

The task selector chose `complex-masked-decoder`; [TASK.md](TASK.md) records the
nonce, base `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`, bounded investigation
and live overlap process. [SOURCES.json](SOURCES.json) pins the two inherited
proof files, predecessor heads, and inspected concurrent work.

- **PR968** (`themilkman216`) supplies the eight-term all-pairs cost floor and
  frame-pair model; **PR1077** (`woklerx`) extends the floor to complex coefficients.
  Their hyperplane-flat classification premise remains inherited in the cost
  corollary. The component classification itself does not use that premise.
- **PR1191** (Philipp / `mightyOil`) proves masked-to-all-pairs rigidity when at
  least one factor is root-linear, for arbitrary term count. This package allows
  both factors outside that space, fixes eight terms, and classifies the component
  reached from the coordinate decoder. Its proof was read; no code is imported.
- **PR1180** (`woklerx`) studies overcomplete all-pairs root-linear factors. It
  does not classify the two-sided masked component. Its PR description was read;
  its theorem is not used here.
- **DreamingOfClouds** (PR717/595), **Joel Pulikkan / GamingPuzzled** (PR620),
  **icekylinx** (P112), and the retained complex and bit supplier lineages retain
  their geometry, decoder, cost-model and construction credit.

No selected record, frozen input, or predecessor code is changed. No new word,
restoration/hosting schedule, supplier invoice, native admission, all-size
compiler proof, or multiplication theorem is supplied. All inherited
precision/tape, common-label/mutable-source, analytic-transfer and bit H1–H5
obligations remain. The written topological proof is not checked in Lean.

Prepared with substantial **OpenAI Codex** assistance in mathematics,
implementation, documentation and separate AI review. Neither the separate
implementation nor the review is independent human peer review. New material
is Apache-2.0, under the repository license.
