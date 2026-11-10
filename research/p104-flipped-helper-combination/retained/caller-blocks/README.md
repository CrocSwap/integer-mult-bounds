# Exact constant-block simplification of the shared-native caller

**No new κ.** This source-bound rewrite reduces the pinned caller from 2,492 events to 1,194 and its inherited conservative ordinary-work allowance by **172,789,760**. Every native contact, thin query, whole-idle job and LAMBDA event remains unchanged and in the same order. No runtime benchmark or stronger multiplication theorem is claimed.

## Result and provenance

The source is CrocSwap/integer-mult-bounds#6902 at `e4d42607f24d7a049b0fca329dc4c34882405c25`, on canonical base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Its caller repeatedly restores a constant basis and enters another basis. Composing and resynthesizing each maximal contiguous ADD/SCALE/SWAP block removes redundant work without moving a nonconstant event.

The algorithm uses exact integer row elimination, reverses the elimination operations with their inverses, and splits large ADD coefficients before accepting a shorter block. It changes 38 blocks. The accepted word has only ADD coefficients `+/-1,+/-2`, SCALE coefficient `-1`, and SWAPs; its coefficient alphabet is no larger than the source's. All 40 role labels and all other caller metadata remain identical.

| Event | Before | After |
|---|---:|---:|
| ADD | 1,380 | 516 |
| SWAP | 786 | 418 |
| SCALE | 146 | 80 |
| LAMBDA | 124 | 124 |
| HOST2 | 18 | 18 |
| IDLE_ONE | 32 | 32 |
| QUERY | 6 | 6 |
| Total | 2,492 | 1,194 |

The frozen files are retained in `data/`. SHA256 of the source caller is `c403bb58f732de8356ed7fef3717649b209ba9d37eb4b8000eec9d876dc7142f`; SHA256 of the replacement is `e83221e5de1cd75b92bbbc40057f07e406af9551bd511bae659fa7173d6d5332`. No native artifact is duplicated or changed.

## Exact identity and boundary preservation

There are 180 nonconstant anchors and 181 intervening constant-block positions, of which 80 source blocks are nonempty. For each changed block, the verifier compares every entry of its exact `40 x 40` integer matrix with the source. The generator uses forward row matrices; the check independently propagates all 40 output functionals backwards through each old/new block. This checks 60,800 exact scalar entries across the 38 changed blocks. Unchanged blocks are identical as event lists.

Induction over the unchanged anchors now proves equality of the complete exact caller for every input and every substitution for the anchor operations. In particular each native boundary sees exactly the same state and role map, and the final diagonal target is unchanged. The native work, paid recursive jobs, main targets, query jobs, whole-idle jobs and adapter inventory are therefore unchanged. This argument does not depend on evaluating a finite set of central characters.

Exact circuit equality does not mean rounded intermediate states are identical. The new word has its own coefficient, height and denominator bounds below; inherited error and supplier-admission obligations remain in force.

## Complete ordinary accounting

For the pinned grammar the caller envelope is `32 * 40 * 104 * events`. Its reduction is exactly

\[
32\cdot40\cdot104\cdot(2492-1194)=172789760.
\]

The checker independently rebuilds every other caller-side term from the frozen metadata and event lists:

| Caller-side term | Before | After |
|---|---:|---:|
| Caller envelope | 331,735,040 | 158,945,280 |
| Thin-call allowance | 9,984 | 9,984 |
| Output rows | 108,160 | 108,160 |
| Main adapters | 248,768,000 | 248,768,000 |
| Whole-idle adapters | 200,928,000 | 200,928,000 |
| Query adapters | 1,872,000 | 1,872,000 |
| Total excluding the 18 unchanged natives | 783,421,184 | 610,631,424 |

Consequently, for **any fixed per-native allowance c**, the complete ordinary bill is reduced by the same amount: `18*c + 610631424` replaces `18*c + 783421184`. This comparison does not assume that the displayed `10^7` allowance is a valid upper bound for the source native.

Substituting the three source-specific native allowances, separately recounted by the pinned predecessor's `ordinary.py` during this investigation, gives:

| Native allowance convention | Before | After |
|---|---:|---:|
| Displayed `10^7` per call | 963,421,184 | 790,631,424 |
| Source actual allowance `10114988` | 965,490,968 | 792,701,208 |
| Source reviewed scalar upper `10425008` | 971,071,328 | 798,281,568 |

Any unchanged additional debit adds equally to both columns. For example, an additional `1000*104*124 = 12,896,000` charge for the unchanged LAMBDA events gives reviewed totals 983,967,328 and 811,177,568. This arithmetic does not itself prove that the chosen debit implements LAMBDA; its implementation is a separate obligation.

### Literal scalar operations and fresh growth

There is an explicit small-coefficient implementation of every constant gate. Per complex stream coordinate, perform `|a|` complex additions/subtractions for `y += a*x`, two real negations for SCALE(-1), and six real copies for SWAP. This gives 9,576 scalar operations before and 4,108 after. These are conservative operation counts for the constant portions, not measured timings or a replacement for the full caller/native ledger.

For formal caller heights, use the sum of absolute real and imaginary coefficients, summed over monomials in `Q(i)[q,D_1,...,D_18]/(q^4-1)`, and the maximum row sum over inputs. This norm is submultiplicative. ADD(a) has operator norm at most `1+|a|`; SCALE(-1), SWAP and an IDLE monomial have norm one. QUERY and the two disjoint HOST2 shears have norm at most two, as does each LAMBDA polynomial. Thus every prefix and every suffix is bounded by

\[
2^{\#\mathrm{LAMBDA}+\#\mathrm{HOST2}+\#\mathrm{QUERY}}
\prod_{\mathrm{ADD}}(1+|a|).
\]

The exact integer products give bounds **less than `2^2057` before and less than `2^784` after**. All constant coefficients are integers; only the 124 formal LAMBDA factors introduce denominators, so all formal caller coefficients have denominator dividing `2^124`. Within a constant block, starting from its identity map, the largest observed exact prefix row sum drops from 60 to 39 and the largest absolute entry from 5 to 4. These fresh bounds include every new constant prefix. They are bounds on the caller macros; native internal growth and an expanded implementation of LAMBDA require their separate, unchanged accounting.

## Reproduction and executed checks

From the repository root with Python 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/p104-caller-constant-blocks
```

Expected: `PASS_CALLER_CONSTANT_BLOCKS`, `PASS_INDEPENDENT_FORMAL_CALLER` and `PASS_REGISTERED_RESEARCH_PACKAGE`.

The separate lead oracle and mathematical review are described in
[INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md). It independently replays both
whole callers over the exact Gaussian polynomial ring, with free stage variables
and an explicit exponent-packing bound; it imports no producer scientific code.

The command regenerates the replacement, checks source pins, independent block identities, metadata and anchor equality, the complete caller-side ordinary invoice, literal scalar counts, fresh growth and denominator bounds. Negative controls reject a wrong ADD sign, a deleted constant gate, a wrong scaling, a changed native boundary role, and an endpoint-preserving pair of ADD(4)/ADD(-4) gates outside the certified alphabet. It also runs under optimized Python; no proof check relies on assertions.

The pinned predecessor's physical caller check and ordinary recount were also executed on the replacement. The physical check covers 7,488 absolute native boundary contacts, the 1,872 reverse cross terms, all main targets and whole-idle axes, injective allocation, the complete unchanged recursive invoice, controls and adapter inventory. Source hashes and the actually executed receipts are recorded in `SOURCES.json` and `CHECKS.json`. These external checks are supplementary; the standalone reproduction needs no unmerged Git object or external package.

## Limitations

This is an ordinary-work reduction for one frozen caller. The paid/productive profile, its raw crossing and κ are unchanged. It does not admit A6 owned ascent, LAMBDA pricing, BIT supply, the new shared-native interface, or the five inherited framework assumptions. A new native can use the freed allowance only after its own identity, complete costs and growth bounds pass.

## Open next questions

1. Use the fixed replacement with a separately verified native improvement and rebuild its complete raw and recursive bills. The block identity transfers, but native admission does not.
2. Investigate exact simplification across a nonconstant anchor only after proving the required commutation relation and preserving its native/idle boundary. This package deliberately does not move such anchors.
3. Compare rounded-error constants after expanding every LAMBDA. The macro height bound here is fresh and exact, but is not an all-width implementation proof.

## Credit

Contributed by @CubeJerry with substantial OpenAI GPT-6 Astra assistance for exact rewriting, proof, checks and prose. Credit to DreamingOfClouds and the contributors of CrocSwap/integer-mult-bounds#6902 for the source caller, to CrocSwap/integer-mult-bounds#6833 for chain geometry, and to zxv (CrocSwap/integer-mult-bounds#6726) and thu-nmrc (CrocSwap/integer-mult-bounds#6716) for the caller lineage. Apache-2.0; retained source credit is preserved in `NOTICE`.
