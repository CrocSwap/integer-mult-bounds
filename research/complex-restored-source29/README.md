# Exact two-register frontier for the historical CK coefficients

**Scoped negative result and finite scalar construction; no new kappa.**
For all 103 coefficient magnitudes in the pinned [PR626](https://github.com/CrocSwap/integer-mult-bounds/pull/626) CK programs, allowing
temporary source and target mutation with exact restoration cannot beat the
stated scratch-circuit comparators, except at magnitudes 2 and 3. Those two
exceptions are attained by ordinary repeated unit additions; they do not
require source mutation. No novelty is claimed for those elementary identities.
The contribution is the complete source-bound exclusion and its checked finite
application.

This package adds only `research/complex-restored-source29/`. The selected
T37 result remains conditional kappa 0.001661960547713947. The historical CK
supplier, selected frontier, and `upstream/` are unchanged.

## Reproduce

Use Python 3.11+ and the standard library, offline, from the repository root:

```sh
python3 -I -B research/complex-restored-source29/verify.py
python3 -I -B research/complex-restored-source29/independent.py
python3 -I -B research/complex-restored-source29/test_package.py
```

The first command ends with:

```text
PASS_RESTORED_SOURCE_CK coefficients=103 exact_minima=77 improvements=2,3 saved_real=3124,3124 no_new_kappa
```

The second reports `PASS_RESTORED_SOURCE_INDEPENDENT`. Normal verification
compares the complete deterministic receipt with `EXPECTED.json` and writes
nothing. `--write NEW_PATH` explicitly produces a fresh receipt and refuses
overwrite. `SOURCES.json` pins exact input bytes and decompressed gzip payloads.

## Cost model and exhaustive scope

The task is to produce the scalar boundary `(T,S,W) -> (T+q*S,S,0)` for arbitrary inputs.
The two-register word may change both T and S, but must restore S exactly.
It may use `T += S`, `T -= S`, `S += T`, `S -= T`, and NEGATE, DOUBLE or HALF
on either register. Each instruction costs one primitive per real component.
No coefficient scratch, extra register, free swap or nonunit addition is
available. The incoming private W is arbitrary: its final clear costs one
additional primitive, even when the word never uses it.

No restrictions are put on intermediate magnitudes or denominator depths. Copying
or clearing T or S cannot help within this class: either makes their map
singular, and subsequent two-register linear operations cannot recover rank.
Adding reads, frame work or physical restrictions would only make the
optimistic exclusion stronger. Three-register circuits and cross-macro
sharing remain outside the claim.

Comparators include Sagar Thakrar's [PR696](https://github.com/CrocSwap/integer-mult-bounds/pull/696) copy/unit lowering, Gareth Davidson's
four [PR837](https://github.com/CrocSwap/integer-mult-bounds/pull/837) Horner variants, Philipp/mightyOil's [PR882](https://github.com/CrocSwap/integer-mult-bounds/pull/882) bounded scratch graph
method transferred explicitly to eligible CK coefficients, and Seb/ZK-Snarky's
[PR999](https://github.com/CrocSwap/integer-mult-bounds/pull/999) target-accumulation circuits. The [PR882](https://github.com/CrocSwap/integer-mult-bounds/pull/882) transfer is recomputed for CK;
its original 49-coefficient JP8 certificate is not treated as CK evidence.
Every comparator word receives a separate exact three-register endpoint check.
Comparison uses exact scalar costs, without asserting that all comparator
precision or production interfaces are jointly admitted.

The complete radius-six group ball has layer sizes
`1, 10, 69, 370, 1646, 6312, 22168`: 30,576 distinct matrices. Its digest
includes every exact matrix and shortest distance. Searching two halves covers
every word through length twelve, with no coefficient pruning. The calculation
finds exact minima for 77 magnitudes; for the other 26, the two-register cost
is at least 13, or at least 14 after the private clear.

This suffices to exclude *every strict cost improvement* in the stated class,
not merely the twelve-operation trials. Every coefficient has a checked
comparator costing at most 14. A strictly cheaper implementation must cost
at most 13, including its mandatory clear, hence contain at most twelve
two-register instructions. That entire domain was checked. Negative
coefficients have the same distances: conjugation by `diag(1,-1)` relabels
the addition signs without adding instructions. Both signs of every attained
witness are also replayed literally.

Any word of length at most twelve can be split chronologically into two words
of length at most six. Their matrices A and B
belong to the enumerated ball, and the endpoint is `B*A`. The main checker
looks up `B = G(q)*inverse(A)`. Breadth-first deduplication loses no continuation
because the current exact matrix determines every subsequent state. This is
an elementary finite certificate argument, not a Lean proof of multiplication.

## The two elementary exceptions

For the small positive integers q = 2 and 3, perform q unit additions into T
and clear W. Negative
q uses subtractions. Complete costs are 3 and 4, compared with the best stated
comparator costs 4 and 5. Exact shortest distances are respectively 2 and 3
before the clear. The original target, source and frame remain the boundary;
every additional source read is charged. Source and work magnitudes do not
grow, and target partial sums lie between its initial and final source
coefficients. Thus the shortcut preserves the original per-register envelope
and cannot introduce fractional precision requirements.

Applying only these two substitutions to the [PR696](https://github.com/CrocSwap/integer-mult-bounds/pull/696) CK programs gives:

| Complete scalar projection | [PR696](https://github.com/CrocSwap/integer-mult-bounds/pull/696) | Replacement | Saved real primitives |
|---|---:|---:|---:|
| Forward | 169,618 | 166,494 | 3,124 |
| Inverse transpose | 169,634 | 166,510 | 3,124 |

Each orientation replaces 1,562 macros. Literal replay covers all 725 input
columns: 716 native, eight private centers, and arbitrary coefficient-work
dirt. It checks the expected CK shear, all 492 helper restorations, private
clearing and the unchanged paid profile. Exact prefix row-L1 maxima remain
5,120 forward and 4,847 backward; denominator depths remain 3 and 8. The
cancellation-free envelope is also unchanged. These are scalar counts and
prefix calculations, not measured runtime or a new recursive saving.

A separate checker imports no code from the project. It reconstructs the group ball
with Fraction matrices and column operations, then uses the different quotient
`A = inverse(B)*G(q)` to check all 103 distances. It agrees on every matrix
distance, all 77 minima and both signs of each witness. Both implementations
are AI-written; this is algorithmic crosschecking, not independent human review.
Adverse controls cover lost source restoration, dirty work, target dirt, wrong
signs, missing reads, false distances, unpaid clearing and incomplete coverage.
Package tests cover isolated optimized relocation, equivalent recompression,
source and receipt corruption, and output preservation.

## Provenance and limits

Exact base: `2921874911956718fcaaaf9396fe8267b3cfa9f0`. OS assignment seed 29
selects the complex track, CK provider and gate tie order. `CLAIM.json` records
the rejected alternatives, fixed stopping rule and local coordination fallback;
no pinned sprint issue existed. The complete fixed domain was finished without
a timeout or larger search restart.

Credit Philipp/mightyOil's [PR883](https://github.com/CrocSwap/integer-mult-bounds/pull/883) for the two-register alphabet and precondition
minimum precedent; [PR882](https://github.com/CrocSwap/integer-mult-bounds/pull/882) for bounded scratch synthesis; Sagar Thakrar's [PR696](https://github.com/CrocSwap/integer-mult-bounds/pull/696)
and [PR723](https://github.com/CrocSwap/integer-mult-bounds/pull/723), Chris Pagolu's [PR734](https://github.com/CrocSwap/integer-mult-bounds/pull/734), Gareth Davidson's [PR837](https://github.com/CrocSwap/integer-mult-bounds/pull/837)/866, and Seb's [PR999](https://github.com/CrocSwap/integer-mult-bounds/pull/999)
for the coefficient comparison lineage. The verbatim [PR999](https://github.com/CrocSwap/integer-mult-bounds/pull/999) module retains its
author notice and is pinned to `fd38a824adb3a5c60c101a86c950a6d590454adf`.
The CK source is Chafik Boukhalfa's [PR626](https://github.com/CrocSwap/integer-mult-bounds/pull/626) at
`660de893d27bb7abd1d5b01b1640207528a5c851`, on Jeremy Kothe's [PR622](https://github.com/CrocSwap/integer-mult-bounds/pull/622) at
`f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`, with icekylinx's primitive/emitter
lineage and the retained predecessor notices. No priority is claimed for the
alphabet, meet-in-the-middle search, or repeated unit additions.

Full native phase/frame execution, cold provider rebuilding, global invoice
admission, selected T37 transport, Linux CI and Lean are not supplied. The
unaltered event inventory and recursive profile are counted, not physically
executed by these scalar projections. All-size/compiler, mutable-source
realization, whole-call hosting, precision/tape and analytic assumptions remain
inherited. Other registers, alphabets, coefficient inventories and shared
clearing boundaries are outside the exclusion.

Prepared for Hanson Sun (@bbMisk) with substantial OpenAI Codex assistance in
research, implementation, verification and writing. Apache-2.0.
