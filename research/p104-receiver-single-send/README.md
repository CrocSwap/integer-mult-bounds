# Exact price of replacing P104 paid slot 88 with direct sends

On the submitted rational P104 word from #7786, remove the route through chart 288 at paid slots 95914 and 88. Allow any of the 1,103 original charts to send directly to receiver 127 while preserving all other transfers and permitting arbitrary receiver recoding. The least number of direct sends is **two**. For every nonnegative, nondecreasing concave grade tariff with zero cost at grade zero, the exact optimal paid cost is **one grade-eight send and one grade-one send**. [Proof and model](PROOF.md)

At the enrolled target κ = 0.00387981257853, the incumbent route pays grades two and five. Across the 48 rational calls, the best direct solution **increases** the paid bill by 94.666202960674077138503464–94.666202960674077138503465 signed units. The incumbent already needs 0.379442 additional units of saving. This is a sharp obstruction for direct replacement of a fixed cut. A physical implementation would also pay for local restocking and terminal arithmetic.

| What was checked | Result |
|---|---|
| Four exact sparse inputs on the complete word | All 901 surviving receiver deposits vanish. The required output is one. |
| Every donor with all-time stock | The first test is visible only at charts 11, 58 and 278. Each requires a different chart on another test. |
| Constructive replacement at the original times | Chart 11 sends public coordinate 674. Chart 138 sends an already available exact copy of coordinate 780. |
| Source and replacement operators | Two rewritten terminal forms agree on all 1,289 independent coordinates. The other 1,287 outputs have no changed dependency. |

Clear1nsight's #7795 asked for an additional live observation on a three-coordinate witness after six proposed paid-pair recodings failed. Here chart 11 supplies one, and combining it with chart 138's live atom actually reconstructs the required rows. The four-witness argument prices the optimum across every possible set of fixed direct donors. Changes to other paid rows and inter-donor routing remain open. Clear1nsight's concurrent #7804 tests 126 two-ingress choices at adjoint chart 3 and a changed exterior. Its source and receiver boundary differ from the direct primal chart-127 cut studied here. [Predecessor handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/7795) · [Parallel result #7804](https://github.com/CrocSwap/integer-mult-bounds/pull/7804) · [Coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19754778)

## Reproduce

From the repository root, run the registered package with CPython 3.12.

~~~sh
python3.12 -B scripts/research_package.py --package research/p104-receiver-single-send
~~~

The standalone checks are standard-library Python. The forward check propagates the four witnesses, verifies all chart ranks, and independently encloses the signed tariff. The second check constructs the legal two-send operator, validates all chronological sources, and verifies both changed outputs by reverse substitution. The immutable compressed word and its uncompressed payload are authenticated on each run. [Forward check](verify_cut.py) · [Adjoint check](verify_operator.py) · [Source pins](SOURCE-PINS.json)

## Open next questions

Can a change to an existing ingress at chart 278 combine the useful observations before the final direct leg at sufficiently low cost? Start by finding an ingress operator that carries the weight of coordinate 674 on test A and separates test D while preserving its original downstream readers. Price the altered ingress, the final send, and every required restoration against the incumbent 48-call invoice. Existing exclusions for six named pairs and the present fixed-stock optimum constrain different classes of changes.

## Credit

Clear1nsight supplied the #7786 rational word, the paid-slot-88 handoff and test D in #7795, building on Ali Romman's #7776 signed framework, the #7774 and #7781 lineages, and the contributors recorded in the retained notice. The other three sparse inputs, all-chart proof, exact attaining recoding and price comparison were prepared by apoursh with substantial OpenAI Codex assistance. New work is Apache-2.0. The project's selected conditional multiplication bound remains unchanged. [Incumbent source and contributor history](https://github.com/CrocSwap/integer-mult-bounds/tree/89a67c404226d51028e135de2b9169e9020d57af/research/p104-iterated-returns/continuation) · [Retained source notice](retained/PR7795-NOTICE) · [Original word notice](retained/PR7786-NOTICE) · [Source license](retained/LICENSE)
