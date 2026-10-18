# PR1736 mixed-width slots preserve the whole q-perp block

**Scoped geometric proof and finite audit; no new supplier or kappa.** Every
one of the 75 retained PR1736 placements (`k=0,...,74`) admits PR1307's
completion-free pending-projector argument. No hosted slice or remainder
splits the local seven-dimensional `q-perp` block. Mixed widths alone do
not require choosing a local orthonormal completion.

This answers the geometric part of [PR1736](https://github.com/CrocSwap/integer-mult-bounds/pull/1736)'s
[Open next question 3](../bit589-width7-windows-seed72/README.md#open-next-questions),
and the concrete-candidate test in this account's
[PR1307](../selected-bit-hosting-audit/README.md#open-next-questions).
The claim is in [discussion #1289](https://github.com/CrocSwap/integer-mult-bounds/discussions/1289#discussioncomment-18953091).
PR1736's physical width-seven provider and supplier-admission obligations remain open.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

## Result and connection to the bit bound

The selected PR589 bit primitive has saving
`1733427039589844234749/10^24 = 0.001733427039589844234749`.
Its fixed nine-stage profile is
`{1:381024, 2:400416, 3:22752, 4:26880, 5:29376, 6:17376, 7:26784, 42:288}`,
with rank mass 1,808,352, width 64, 28,416 roles and deficit 10,272.
That conditional moment includes the inherited bad-residue surcharge; it
is not a lower bound on possible bit primitives. PR1736 prices hypothetical
width-seven conversions subject to the source windows and leaves their
projector compatibility open. This package resolves that one geometric
sub-obligation without constructing the conversions or changing a price.

| Checked domain | Result |
| --- | ---: |
| Retained placements, k=0 through 74 | 75 |
| Representative helper slots, across the 75 scenarios | 296,325 |
| Child/copy partitions, including zero remainders | 166,500 |
| Slots or remainders splitting q-perp | 0 |
| Rational live-port projectors | 111 |
| Typed data families in the 32-replica product | 28,416 |
| Helper occurrences after that product, summed across scenarios | 9,482,400 |
| Negative controls in the main verifier | 9 |

Each scenario has 3,951 helper slots per replica, `9k` of width seven and
`9(439-k)` of width eight. This includes 126,432 occurrences after the
32-replica product; the large total above sums alternative scenarios, not
one construction. The product lift is proved using an injective family
index and checked once, not by independently replaying all replicas.

For `k=1`, the nonzero idle histogram per replica remains
`{2:434, 4:442, 5:2, 6:442, 7:663, 42:10}`. Child 0, copy 0 begins with two
width-seven factors: the whole local `q-perp`, then seven exterior axes.
This is a concrete mixed-width example inside a capacity-14 child, already
within the completion-free argument. All 75 nonzero idle histograms match
PR1736's committed `RESULT.json` exactly.

## Why the geometric implication holds

An entrance child's ordered pending axes begin with all seven local axes;
other children contain only exterior axes. PR1736 packs a contiguous prefix
starting at offset zero, and every slot has width seven or eight. The first
slot therefore contains all local axes, or an empty prefix leaves them all
in the remainder. Every subsequent slot and the nonempty-prefix remainder
is exterior. This argument applies to any such prefix packing, not only
the 75 computed plans.

For each port, `K_q=I-qq^T/4` represents the complete local block. Every
slot projector is `0` or `K_q`, plus its exterior coordinate projector.
Disjoint supports are orthogonal, and the inherited identity
`D(P)D(Q)=D(P+Q)` for orthogonal projectors identifies the product of hosted
factors and remainder with the original idle operator on arbitrary head
and tail vectors. [PROOF.md](PROOF.md) states the assumptions, general
prefix lemma, exact basis-independence criterion and replica lift.

The distinction is testable. Swapping one local and one exterior axis
between k=1's two width-seven factors preserves ranks, windows and their
whole-child partition, but makes each individual factor depend on a local
completion. Explicit rational completions distinguish the factors at all
111 ports. The aggregate child still agrees. Thus a split is a need for
extra basis data, not by itself an impossibility or an erroneous child.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/bit-mixed-width-projectors
```

The registered replay runs the source-bound audit and the six direct
test groups. Direct commands:

```sh
python3 -I -B research/bit-mixed-width-projectors/verify.py
python3 -I -B research/bit-mixed-width-projectors/test_verify.py
```

Expected audit line:

```text
PASS_BIT_MIXED_WIDTH_PROJECTORS k=0..74 slots=296325 split=0 ports=111 controls=9 no_new_kappa
```

Verification reads and compares [RESULT.json](RESULT.json); it does not
rewrite evidence. `verify.py --write NEW_FILE` explicitly writes to a new
file and refuses overwrite. Both scripts support optimized Python.

Author-checked on CPython 3.12.3, Linux x86_64: the registered replay,
metadata/source-pin check and both scripts in optimized mode pass. A
Git-free relocated export also passes. Corrupting an exported source file
is rejected before execution; replacing the receipt's integer zero by
Boolean false is rejected by the typed canonical comparison.

The predecessor DP and builder are reused only to regenerate the precise
candidate placements at PR1736's original `a=1/570` construction point.
The new audit reconstructs source-level axes and direct-touch windows,
checks every role/width/prefix, exact factor partition, cross-child
disjointness, remainder and port projector. It does not re-prove the DP
optimum or re-price the moment. All transitive source imports are pinned
and declared in the replay manifest before they execute.

The main controls reject omitted/duplicate helpers, a wrong width, a
window violation, replica aliasing, a rank-preserving local split, a
rank-preserving wrong exterior axis, a missing factor and overlapping
factors. Valid changes of factor/record order pass. The separate tests
apply the rational 128-coordinate address operators to all basis columns
for 27 representative port/child/scenario fixtures (3,456 columns), cover
all 86 width-seven/eight prefix words fitting the four source capacities,
and test gapped/overlapping placements and changed local completions.

## Sources, scope and credit

Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
PR1736 is incorporated at head
`b4fd72163234c164d9a05f2f7dac9c57dcd7fb66`; PR1307 at
`4cb255ef445e2abc3ff8845fa01210b974e2cf6c`; selected PR589 at
`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`. Exact consumed main bytes
and their Git blobs are in [SOURCES.json](SOURCES.json). There is no pending
PR code dependency. The scope change from `bit-helper-contract` is recorded
in [TASK.json](TASK.json): this is a hosting-interface sublemma, not a
replacement H2/K scalar word.

Credit Sagar Thakrar for PR1736's placements, chronology, costs and open
question, and PR1023's width-packing model; commdata2338 for PR1307's
projector argument and source-level interpretation; mightyOil/Philipp for
PR1281's mixed-width relaxation; DreamingOfClouds for PR589/510/463;
eumemic for PR555 and the carrier skeleton; DaysSky for PR442; Zhihao Chen
for PR386; chafreaky and the retained geometry, audit and moment-engine
contributors. This retains their results and does not claim a new packing
optimum. The concurrent PR2423 geometry investigation concerns its
width-eight R438 placement, a distinct source object.

Not checked: a physical width-seven provider, helper-to-host intertwiners,
owner inactivity beyond the recorded source windows, correlated dirty-state
realization of a complete call, native or selected cold replay, H1-H5 or a
replacement interface, all-size compilation, precision/tape, analytic
transfer, or a multiplication theorem. No formal-kernel proof, independent
human review, new endpoint or frontier adoption is claimed. New material
is Apache-2.0, prepared and checked with substantial OpenAI Codex assistance.

## Open next questions

1. Bind an actual width-seven provider to one of these slots. Start with
   k=1 child0/copy0, whose host projector is exactly `K_q`, and specify the
   provider's entrance/exit maps and any helper-to-host intertwiner. This
   is needed before the geometric factorization can contribute to a
   supplier; native conversion and the provider's replacement interface
   remain blockers.
2. If a future allocation deliberately splits q-perp, provide one shared
   completion and its exact individual slot projectors. The two-completion
   witness here is a first regression fixture. Basis specification alone
   does not price its implementation or establish correlated-helper hosting.
