# Materialized scalar lowerings for the rank-seven words

This package answers the arithmetic part of [PR3060's instruction-lowering
handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/3060).
Two binary-digit lowerings each save **9,760 real arithmetic instructions per
provider word and orientation** against an explicit scratch-based lowering.
They trade different intermediate-width requirements. This is not a runtime,
physical supplier or κ improvement.

The source is PR3042's six-skip word, retained byte-for-byte through PR3056 and
PR3060. Both providers are tested in the parent, three-ADD and tariff-optimal
forms, with their literal inverse cleanup. All three forms have the same
expanded instruction count under each policy:

| Word | Conservative bound, forward / backward | Scratch lowering | Either digit walk |
|---|---:|---:|---:|
| PR3042 | 158148 / 158196 | 93190 | 83430 |
| PR3056 | 158136 / 158184 | 93190 | 83430 |
| PR3060 | 158124 / 158172 | 93190 | 83430 |

These are counts for the scalar subsequence, including both real components.
The scratch baseline is implemented here, not claimed as an existing upstream
instruction implementation or an optimal read-only-source compiler.

## Arithmetic model and construction

Each of the following costs one unit on one real component:

- `t += s`, `t -= s`, with distinct registers;
- negate, double or halve one register;
- destructive copy or clear.

Arithmetic is exact over dyadic rationals. There is one owned, initially-zero
scratch register per component. It returns to zero after every macro. This is
not restoration of arbitrary borrowed scratch. Non-scalar events, including
frames, climbs, wrappers, warps, centres and the 91 private buffers, are retained
literally and are not assigned zero physical cost.

For `q = sign*n/2^k`, the scratch policy builds `n*s` by binary Horner operations,
halves the scratch `k` times, adds it to `t`, then clears it. Small integer
coefficients use repeated signed ADDs when cheaper. SCALE is expanded into unit
shifts and a possible negation. Every operation, including clearing, is counted.

Write `n = p*2^k + r`. A digit walk costs

```text
p + popcount(r) + 2*k
```

and is selected only when strictly cheaper than the scratch recipe.
First add `sign*p*s`. Then process the `k` fractional bits, most significant
first, using either of these equal-cost rules:

```text
source_walk                    target_walk
halve s                        double t
if the bit is 1: t += sign*s    if the bit is 1: t += sign*s

finally double s k times       finally halve t k times
```

The source walk restores the source exactly. Its target partial sums lie
between the original macro's two real endpoints. Its source magnitude never
exceeds its entry magnitude. The target walk never writes the source. After
normalizing the target by its accumulated doubling factor, its partial sums
obey the same endpoint property. At the end both rules implement `t += q*s`.
These statements hold for arbitrary dirty target/source values, not merely
zero inputs or independent numerical samples.

For example, half addition has two three-instruction implementations:

```text
halve s; add t,s; double s

double t; add t,s; halve t
```

Thus writable sources are an option, not a necessary condition for the saving.

## Width and access obligations

The exact 38 macro-type certificates in `evidence/RESULT.json` check every
recipe prefix. For the actual streams:

| Policy | Additional ADD target amplification | Temporary source fractional bits |
|---|---:|---:|
| Scratch | 1 | 0 |
| Source walk | 1 | at most 3 |
| Target walk | at most 8 | 0 |

The target walk therefore needs at most three additional integer guard bits
relative to the macro endpoint envelope. The source walk needs at most three
additional fractional bits at the temporarily written source. No claim is made
that existing physical formats already provide either allowance.

All policies' fallback scratch recipes require at most `8*abs(s)` magnitude
and three extra fractional bits. The complete receipt lists the actual source
or target registers needing the corresponding guard. There are 521 source
registers in the forward stream and 484 in the backward stream. The target-walk
integer-guard lists have 484 and 521 registers respectively. These lists are
not a physical memory allocation.

Exactly 4,858 scalar macros change, saving 9,760 real instructions after both
components and all inverse shifts are counted. The receipt separates the
coefficient contributions. The complete non-scalar stream is unchanged.

## The restore block still ties, and four is optimal

Set `x=X22`, `y=X230`. The parent, three-ADD and tariff-optimal blocks all
implement `(-y,x-y)`. Their expanded length is four per real component.
In particular, PR3056's coefficient-two ADD becomes two unit ADDs. PR3060's
lower conservative tariff does not produce an additional instruction saving
under these policies. This does not contradict its tariff-optimality theorem.

There are exactly 30 instructions in the stated three-register unit alphabet:
12 signed ADDs, six copies, and 12 unary operations. Starting from rows
`(1,0), (0,1), (0,0)`, exhaustive exact closure through three steps has cumulative
sizes `1,19,208,1769`. Neither the block, its inverse, nor their inverse-transpose
orientations occurs. An independent denominator-eight integer implementation
agrees. State merging is sound because these instructions depend only on the
current rows. The four-instruction witnesses prove the exact minimum, including
with the one zero scratch and destructive copy/clear available. More scratch,
fused operations and cross-component instructions are outside this theorem.

## Evidence and reproduction

Six fresh inherited native compiler runs validate both orientations, all 632
native dirty-input columns, frame chains, the unchanged local paid profile
`{1:2433,2:712,3:232,4:108,5:18,8:8}`, and the private-buffer endpoints.
Thirty-six complete scalar expansions are written and read back. A second
column interpreter checks the serialized registers, frames, signs, target map,
source restoration and scratch erasure at every macro. The compiler itself is
reused, not claimed as an independent implementation.

With `RUN` an existing session-owned directory outside the checkout:

```sh
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" python3.12 -W error -B \
  research/rank7-primitive-lowering/verify.py \
  --work "$RUN/expanded" > "$RUN/result.json"
cmp "$RUN/result.json" research/rank7-primitive-lowering/evidence/RESULT.json
TMPDIR="$RUN/tmp" python3.12 -W error -B \
  research/rank7-primitive-lowering/test_verify.py
TMPDIR="$RUN/tmp" python3.12 -B scripts/research_package.py \
  --package research/rank7-primitive-lowering
```

`--work` refuses existing paths and preserves diagnostics. Without it, outputs
are disposable under `TMPDIR`. Committed hashes describe decompressed canonical
programs, not gzip containers. No network or numerical dependencies are needed.
The tests cover all 6,643 bounded ADD coefficients under all policies, SCALEs,
an independent short-word census, and semantic/source/ownership/lifecycle
failure controls. Normal and optimized checks retain executable contracts.
`evidence/CHECKS.json` records commands and environment.

## Scope

This is a handoff-first **changed scope** of `independent-moment`, on canonical
main `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
The result is author-checked. No independent human or formal-kernel review is
claimed. The selected frontier and frozen predecessors are unchanged.

The arithmetic counts and width/access ledger are proved by the finite replay.
Fixed-width rounding, physical shift/copy/clear cost, storage/backing and
movement are **unknown** here. The inherited warp/wrapper implementation,
owner allocation, prefix/precision/tape, all-size/compiler, admission and outer
release are not rerun. The recursive profile does not improve, so no κ gain is
claimed. Stop at this boundary rather than expanding a dependent search.

## Open next questions

Can an actual fixed-width caller pay one of the two listed guard contracts
without losing the scalar saving? Start with the
half-ADD cases and the receipt's exact register lists, then price the widths,
source access, scratch, shifts and cleanup in that caller. The blocker is a
physical representation and ownership contract, not another coefficient
identity. Also independently replay the literal materialized streams before
using their counts in a new invoice.

## Credit

The arithmetic identities are elementary; no priority is claimed for generic
dyadic lowering or source gauges. Eumemic's [PR411](https://github.com/CrocSwap/integer-mult-bounds/pull/411)
already explicitly pays copy/halving/accumulation/clear recipes in another word.
The contribution here is the complete rank-seven stream comparison and its
concrete guard/access ledger.

Nick Petalas contributed these lowerings and the source-bound comparison.
PR3060 supplied the instruction-lowering handoff and its tariff-optimal word;
PR3056 supplied the three-ADD contraction. Credit dcharb78 for PR3042,
Jeremy Kothe for PR3015, Marius-Paul Dumitrean for PR2979, Cinna Davis for
PR2226, icekylinx and the PR433/514 emitter lineage, Tekalign and the retained
geometry/native/owner contributors. `vendor/CREDITS.md` and `vendor/NOTICE`
preserve predecessor attribution. Native compiler sources are pinned live
inputs, not modified copies. Apache-2.0. Development used substantial automated
assistance.
