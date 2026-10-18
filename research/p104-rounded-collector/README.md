# A deterministic rounded P104 collector fails strict-zero erasure

The first collector in ywz65's [PR2586 physical dual](https://github.com/CrocSwap/integer-mult-bounds/pull/2586),
head `7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`, has an explicit
fixed-point counterexample. Round each completed rank-seven child output to
the same componentwise nearest-even grid. For **every** `b >= 4`, put
`h = 2^-b` and choose the physical dirty value `D31 = (1+h) delta_0`
at the collector's entry cut. Set the other four gather sources to zero.
The private collector reaches erasure with **`C = -h delta_0`**, although
its two child calls satisfy the local completed-output relative-error
inequality with `u = h`. Exact arithmetic restores zero.

This instantiates [Nick Petalas's PR2549](https://github.com/CrocSwap/integer-mult-bounds/pull/2549)
precision/lifecycle handoff using actual physical native recipes and a
deterministic quantizer. PR2549 already established abstract allowed-defect
counterexamples and norm bounds; those results are credited, not claimed new.
This package does not repair disposal or contradict PR2586's exact theorem.

## Contract and exact witness

Use zero-based events **2025–2039** of the pinned 5,398-event word.
All five `D` fields start in the common physical dimension-eight chart.
They are arbitrary dirty inputs at this cut and are never written locally.
The initial `Q7` can be zero; its initial dirty value does not affect cleanup.
The literal instructions are:

1. Allocate exact-zero `C`; add `D31,D30,D29,D28,D27` into it.
2. Apply the native transport `U` at event **2031** (dimension eight to one).
3. Add `C` to `Q7`, without feedback from `Q7`.
4. Apply the inverse native transport `V` at event **2033** (one to eight).
5. Subtract `D27,D28,D29,D30,D31`; require zero to erase at event **2039**.

The complete arrays have 512 complex addresses. Each transport recipe is a
Gaussian monomial, seven binary `C` factors, and a Gaussian monomial.
The primitive is `C_e = ((1+i)I + (1-i)X_e)/2`, with the precise permutations,
quadratic phases and global phases from PR2586. No compiler or predecessor
executable is imported. The receipt binds both native occurrences to the
literal frames and rank. All 512 columns satisfy `VU = I`.

Let `z = U delta_0`. Its 128 nonzero coordinates are
`(±1 ± i)/16`, and `||z||_2 = 1`. The verifier checks this flat-column
property at **every** input address, using butterfly evaluation and a separate
tensor-product column formula. These implementations share the monomial
parser; they are not independent human or formal verification.

For `b >= 4`, every component of `z` lies on the `h` grid. The exact outbound
result is `(1+h)z`. Each real and imaginary rounding displacement is `h/16`,
strictly below the half-grid threshold, so there are no tie cases:

```
round_h(U ((1+h) delta_0)) = z
round_h(V z)              = delta_0
C immediately before erase = delta_0 - (1+h) delta_0 = -h delta_0.
```

The outbound completed-output defect is `-h z`, with Hilbert norm `h`.
The input norm is `1+h`; hence `h <= u(1+h)` for `u=h`. The return defect is
zero. Both calls meet that local relative-error test on this execution. This
is **not** a claim that fixed-point rounding satisfies it for all inputs.
Since a Gaussian monomial only permutes coordinates and multiplies by powers
of `i`, nearest-even quantization commutes with the output monomial. Rounding
after the entire transport is therefore identical to rounding at its rank-seven
child output before the exact final monomial.

For example, `b=4` uses the grid-valued input `17/16 delta_0` and leaves
`-1/16 delta_0` in `C`. Refining the child output grid by four fractional bits
makes this particular example exact. Rechoosing the input for the refined
**common** grid gives the same family again. This excludes neither mixed
precision nor a different cleanup algorithm.

## Evidence and reproduction

Standard-library Python 3.12; default replay is read-only and Git/network-free:

```sh
python3.12 -I -O -B research/p104-rounded-collector/verify.py
python3.12 -I -O -B research/p104-rounded-collector/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-rounded-collector
```

The checker executes the fifteen literal instructions on full Gaussian-dyadic
arrays and confirms unchanged dirty sources, the query result, each local
defect and the erase residual. It cross-checks all 512 native round-trip
columns and tests `b=4,5,8,17,64,256`; the argument above establishes all
`b >= 4`. It uses integers throughout. `RESULT.json` is compared in full.
`--out NEW_PATH` writes a separate receipt and refuses overwrite.

Controls include exact and finer-grid successful cleanup, strict rounded erase
rejection, a wrong cleanup sign, a wrong native global phase, the excluded
coarse-grid case, signed nearest-even ties, source drift, receipt drift and
Git-free CLI replay. `PREDECESSORS.json` authenticates the byte-identical
committed word and compressed native archive by SHA256 and Git blob ID.
Compression is authenticated as an immutable source, not regenerated output.

## Limits and family decision

This is a **local rounded-child/erase interface counterexample**, not a full
rounded execution of the 5,398-event caller. The local source fields are on
the stated grid; no claim is made that they arise from a uniformly rounded
prefix on the same entrance grid. The ideal prefix before this first collector
contains only invertible transports, distinct-register ADDs and signs, so the
cut values are reachable from arbitrary ideal persistent inputs under the
inherited exact prefix semantics.

The result excludes using this same-grid, memoryless nearest-even child pair
as a universally zero-restoring collector on arbitrary cut inputs. A child
may satisfy its relative-error requirement on an execution while its caller's
strict-zero storage requirement fails. Increasing a finite common precision
shrinks the residual but does not make it exactly zero on all cut inputs.

No actual recursive rounded child implementation, reversible cleanup,
residual-tolerant disposal, owner/hosting invoice, global precision/tape,
remaining 102 corrections, full selected replay, all-size supplier or new
kappa is supplied. The native chart semantics are inherited from PR2586;
only the two named recipes and local instruction boundary are checked here.
**Decision: narrow and finish this test.** Further construction needs an
explicit cleanup/consumer contract and its complete bill, not another norm
estimate for the same failing erase.

## Open next questions

- **Can a rounded collector restore exactly without retaining erased history?**
  This decides strict-zero admission. Start with the two pinned rank-seven
  calls and keep the actual approximation residue, then exhibit reversible
  cleanup or state the required extra storage. The blocker is a constructive
  lifecycle and its cost; the present counterexample alone does not forbid it.
- **Can mixed precision or a residual-tolerant lifecycle fit the full caller?**
  State the allowed dirty entrance domain and precision at every read, then
  price retained residuals, disposal and restoration. Four extra bits repair
  this single witness, but do not prove a universal full-caller contract.

Structured questions, selection/freshness and the bounded scope are in
`TASK.json`. The selected record is unchanged.

## Credit and provenance

Base canonical main `b4560d9e7216f72b73c5aa940ac099c05e33ccf9`, priority
revision 5. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18953699).
PR2586 supplies the exact physical dual and recipes; PR2497
`7f2cf129d42030d3eb3975b7d1b07392c6d32a1b` supplies the clean logical word.
Nick Petalas's PR2549 `bd3bea4b4e09ead04355a477a7c28559427d1ef6`
supplies the precision/erasure question, and PR2550 the complementary-chart
idea. PR2551 supplies the physical boundary distinction. Adam Gall's PR2096
supplies the earlier Hilbert-defect method.

Retain the P104 lineage: Ross Richardson/PR2445, commdata2338/PR2393,
Hiroki Kumazaki/PR2353, Philippe Van Velzen, Chafik Boukhalfa/PR1991,
Rohan Arun/PR1972, Adam Gall/PR1940, Josie Elliston/PR1071,
Ali Romman/PR1125/1862 and icekylinx/PR531. Native monomial and `C` semantics
follow the credited retained `p104-native-channel/vendor/native_verify.py`;
its predecessor notices remain unchanged under `p104-native-channel/notices/`.
Source-specific credit and licenses remain with the pinned predecessors.

New derivation, checker and writing prepared for Arham Tahir with substantial
OpenAI Codex assistance. Apache-2.0. Author-checked evidence; no subagents,
independent human review, proof assistant, maintainer admission or hosted-CI
success is claimed.
