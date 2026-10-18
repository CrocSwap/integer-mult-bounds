# Selected k8 frames: uniform power-cost optimum and optimal-profile rigidity

**Scoped audit and proof extension; no new kappa.** The selected k8 word's
paid profile

```text
{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}
```

minimizes its frame-reassignment LP for **every `0 <= a <= 1/32`**, under
the power price `r^(1-a)`. For **`0 < a <= 1/32`, every optimum has exactly
this paid histogram**, even though its frames need not be unique. The range
includes the `1/99` planning target.

Gareth Davidson / bitplane's [PR1671](https://github.com/CrocSwap/integer-mult-bounds/pull/1671)
already establishes the fixed-word packing ceiling by checking two exponents.
This package audits its unchanged symbolic duals and proves their uniform
validity and the equality-case result. It does not improve the existing ceiling.
See [PROOF.md](PROOF.md) for the quantified argument.

## Evidence

The exact predecessor head is `ce130d291f5ab6dd801544886a16f62d42d86118`.
The source-bound word, graph, cone caps and complete frame domains match it.
Both column assemblies reconstruct **all 23,004 columns, 17,507 rows and
135 component objectives**, including register-edge multiplicities and fixed
centre children. The local rank mass remains 5,586.

The 239 distinct rational reduced-cost vectors have these proofs:

| Columns | Distinct vectors | Uniform sign proof |
|---:|---:|---|
| 16,564 | 1 | Identically zero |
| 10 | 1 | Exact square `4(1-2^(-a))^2`, positive for a>0 |
| 6,430 | 237 | Degree-eight Bernstein polynomials with rational positive coefficients |

The polynomial proof uses independent logarithm bounds and alternating
exponential series; no floating-point value, solver or sampled exponent
establishes the interval claim. The smallest nonsquare slope bound exceeds
0.0179. Strict positivity on all nonzero residual vectors forces every
optimal LP point to use only identically-zero columns. The component objective
identities then force the entire paid histogram, including rank one by mass
conservation. At a=0 only optimality, not histogram uniqueness, is claimed.

[RESULT.json](RESULT.json) contains every distinct vector and its multiplicity,
its rational sign certificate, the complete column-stream digest and fixtures.
Changing gate G616 from the zero frame to span(148) gives a distinct feasible
model assignment with the same histogram. Separate native admission of that
alteration is not claimed.

Two exact boundaries prevent broader conclusions: a column of the same dual
is negative for the concave price `min(r,2)`, and another is negative for the
power exponent `a=1/20`. These invalidate extensions of **this dual**, not
baseline optimality outside the certified range. Neither supplies a cheaper
feasible assignment or contradicts PR1671.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/selected-k8-uniform-frame-audit
```

The registered replay checks source/provenance pins, runs the mathematical
checker and eight test groups. The direct read-only mathematical replay is:

```sh
python3.12 -I -O -B research/selected-k8-uniform-frame-audit/verify.py
```

It prints `PASS_SELECTED_K8_UNIFORM_FRAME_AUDIT ... interval=0..1/32 optimal_profile_unique no_new_kappa`.
Only an explicit `--write` regenerates RESULT.json. The tests include a separate
integer-root arithmetic calibration at a=1/32, 1/64 and 1/128, exact Bernstein
change-of-basis identities, rejected objective/column/domain mutations, source
and receipt corruption, and optimized read-only relocation.

## Scope, accounting and overlap

The domain fixes the scalar word/order, coefficients, endpoints, centre cut,
target pins and cleanup/cone contract. It uses PR1671's relaxed monotone
frame-assignment model. Both column assemblies share Aaron Wang/navinor's
pinned event/domain implementation; the second reconstructs column costs
directly from the graph. This is an independent arithmetic audit, **not** an
independent implementation or new proof of the physical interface.

The original 1,646 idle rank units per call, 64-per-call centre charge,
896/9 live families, width 73 and rank-51 idle cap remain. PR1671/PR1240's
full packing bound is inherited rather than recomputed here. No physical
decoder, new profile or kappa, selected cold replay, native execution, hosting,
all-size compiler, common-label/mutable-source realization, precision/tape,
analytic transfer, bit H1-H5, Lean or human review is established. Hosted CI
status is separate from local validation.

The revision-3 chooser selected `complex-rank-shape-decoder`, nonce
`4071338634dbc7c5d72c8e5f2a5a4633`. [TASK.json](TASK.json) declares the **changed**
scope from decoder synthesis to this audit/extension after fresh overlap found
PR1671. PR1605 concerns abstract reblocking and overhead, and the retained X4
package concerns an older word. The original physical-construction acceptance
gate is not claimed satisfied. The claim is in
[Discussion1659](https://github.com/CrocSwap/integer-mult-bounds/discussions/1659#discussioncomment-18916847).
Exact source pins and overlap coverage are in TASK.json and SOURCES.json.

## Open next questions

- **A changed scalar dependency or gate order.** This could evade the fixed-word
  obstruction. First name one explicit rewrite, prove its dirty-state and
  endpoint contract, and screen its complete local plus idle profile. The old
  event/domain certificate cannot certify the changed word.
- **Optimality beyond a=1/32.** At one specified exponent, produce a new exact
  dual or a feasible improving assignment. The present dual's negative column
  is insufficient. This is lower priority for the current supplier, whose
  full packing bill already fails at a much smaller exponent.

The questions and blockers are also structured in TASK.json.

## Credit

Gareth Davidson / bitplane supplies PR1671's unchanged duals and selected-word
frame theorem. Aaron Wang / navinor supplies the retained model and method.
Credit the Jeremy Kothe, Rohan Arun, Hao Yan, icekylinx, DreamingOfClouds,
eumemic and earlier frame/coverage lineage detailed in [NOTICE.md](NOTICE.md).

Prepared for Ross Richardson with substantial OpenAI Codex assistance in the
mathematics, implementation, testing and writing. No subagents or independent
human review. Apache-2.0; predecessor files and selected evidence are unchanged.
