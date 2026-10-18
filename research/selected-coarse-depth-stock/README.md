# Selected coarse depth: exact thresholds and a conditional stock component

**Scoped proof / mathematical audit. No new κ or selected-supplier change.**

For the selected PR1094 complex profile, under its inherited child rule
`r*floor(n/73)` and terminal rule `n<73`, the worst coarse depth is exactly
`D(n)=1+D(48*floor(n/73))`. Its integer thresholds satisfy
`b_1=73, b_(d+1)=73*ceil(b_d/48)`. The [written proof](PROOF.md) establishes
the sharp asymptotic coefficient `1/log2(73/48)` and an exact **43/26**
logarithmic allowance. The existing two-level halving guard belongs to the
predecessor assembler; this package does not claim it as new.

The selected finite invoice's depth component uses a 2,642-bit stock allowance.
The new coefficient charges `ceil(43*2642/26)=4370` instead of 5,284. Keeping
the other ledger terms charged gives a **conditional** comparison
`16469 -> 15555` (914 less). This is not an adopted complete row bound.
The physical interpretation of the complex per-level divisor and remaining
ledger terms is unresolved. This package establishes no complete complex
reserve coefficient or ordinary-bootstrap cutoff fit. Under a fully completed
ordinary-leaf contract the external leaf factor can be one; that does not
measure its internal borrowing.

The seed-selected native bootstrap stage is stage 2 **for comparing the atom
parameter s only**. The conditional complex parent-reserve formula, including
the leaf factor and `w=ceil(e^s)`, is in PROOF.md. The ordinary BIT bootstrap
uses m=64 and maximum child 42, not this complex m=73 tree. Concurrent
[PR2084](https://github.com/CrocSwap/integer-mult-bounds/pull/2084) derives its
separate GL64 envelope; [PR2087](https://github.com/CrocSwap/integer-mult-bounds/pull/2087)
addresses its conditional time lifting. This contribution does not supply
that ordinary producer's stock coefficient.
No operation or paid child is removed; moments, the retained 20,161 row cap,
outer constraints and conditional κ = **0.001672660197076918** stay unchanged.

## Reproduce and coverage

From the repository root, using Python 3.12 and only its standard library:

```sh
python3.12 -I -B research/selected-coarse-depth-stock/verify.py
```

Expected:

```
PASS_SELECTED_COARSE_DEPTH_STOCK block=43/26 widths=103139 conditional_row=16469->15555 controls=12 no_new_kappa
```

The registered replay also runs eight focused tests normally and with `-O`:

```sh
python3.12 scripts/research_package.py --package research/selected-coarse-depth-stock
```

The verifier authenticates the selected certificate, exact reviewed archive
members, complete owner/profile link and frozen PR1087 assembler. It never
executes or changes the predecessor compiler. Three depth implementations
agree: forward recursion, inverse thresholds and an all-child dynamic program.
Finite coverage is every width 0..100,000 plus threshold and binary-power
neighbors through exponent 512. These are tests of the written proof, not
formal verification of an all-size supplier or multiplication theorem.

The rational-block search is complete only for `1<=p<=64, 1<=q<=p`:
2,080 exact decisions, 1,227 passing, smallest ratio 43/26. Seed 64 fixes this
domain and selects stage `1+64%7`; no reroll or unrestricted optimum is claimed.
Twelve controls reject omitted paid/physical work, detached provenance,
weakened guards, invalid rounding/terminal rules and invalid depth certificates.
They also reject identifying the complex and BIT producer parameters.
The floor-stock control rejects an insufficient certificate for the stated
rational envelope; it is not an impossibility proof for a smaller allowance
derived by another argument.

## Source, overlap and scope

Exact base: `564148b82ae9df72163f22106f15e73efca8aff2`, priority revision 4.
[SOURCES.json](SOURCES.json) pins every dependency and consumed archive member.
No pending PR is an implementation dependency. The final scope is a complex
side lemma, refined after PR2084 clarified the actual ordinary BIT producer.
[TASK.json](TASK.json) records
the three candidate tasks, assignment, stopping rule and overlap coverage;
[CLAIM.md](CLAIM.md) preserves the original scope and
[coordination post](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18932040).

The entry refresh covered 354 open PRs and 738 Discussion records with complete
pagination. Exact-depth terms returned predecessor stock/packing references
and this claim, rather than a duplicate threshold or rational-block result.
This searches metadata and local package prose, not every diff or unpublished
experiment. Final freshness and checks are recorded in VALIDATION.json.

All-size lowering, common-label/mutable-source realization, physical hosting,
precision/tape, row restoration, analytic transfer and the bit H1–H5 assumptions
remain inherited. Frozen evidence, upstream/ and the selected frontier are
unchanged. The source-bound stock count is finite evidence, not proof that
the same divisor suffices at every atom width.

## Open next questions

1. Bind the selected parent's actual uniform per-level divisor C(w), including
   temporary families, to an explicit A*w+B logarithm. First trace its producer
   and physical row splitting at one cut; a finite 2,642-bit stock count alone
   does not discharge this question.
2. If a proposed physical lowering uses a partially completed leaf, price its
   common external reserve before combining it with the depth factor. Fully
   completed leaves can use external factor one; internal borrowing remains
   charged in their contract. The historical 57,604 and 252 numbers do not
   identify that internal reserve.
3. If a physical row-ledger adoption is proposed, prove which of its remaining
   terms depend on coarse depth and replay its actual producer. The modeled
   914 reduction alone changes no accepted supplier or multiplication bound.

## Credit and license

Josie Elliston's PR1956/1965 and ToikY's PR1990 identify the selected stock-fit
handoff. Their fourteen headrooms and fit repairs are not re-presented as new.
Rohan Arun supplies PR1094/387; Jeremy Kothe supplies PR1087 and its preserved
assembler; Hao Yan supplies the T16 controller. The finite-cover and restored
row contracts retain the PR185/eumemic lineage and original notices. Existing
stock corroboration, including PR1407, is predecessor evidence. Adam Gall's
concurrent PR2084/2087 prompted the explicit BIT/complex producer distinction;
the original pinned PR589 record independently corroborates their parameters.

Prepared by Sricharan Vagvala (@theon199) with substantial OpenAI Codex
assistance in research, proof, implementation, checking and writing. No
subagents, independent human review or proof-assistant acceptance is claimed.
New work is Apache-2.0; predecessor files remain byte-identical.
