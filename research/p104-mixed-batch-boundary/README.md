# A finite P104 batch with one fewer boundary

**Conditional κ ≥ 0.00382069832557.** The directed upper endpoint for Ali Romman’s #7756 caller is 0.00382063778177. The certified increase is **0.00000006054380** under the same five framework assumptions. The public multiplier estimate has the form `O(n (log n)^(1−κ))`.

The comparison uses 2,048 native invocations on both sides. Closing the caller after 1,024 invocations forces eight homogeneous B roots into the second copy. Keeping the batch open lets 64 more mixed roots use those ports. Ali Romman supplied the mixed word, parametric placement and the 1,024-call construction. This package qualifies the finite 2,048-call instance, proves how much the removable boundary costs, and bounds every grouping of the same three templates. [PR #7756](https://github.com/CrocSwap/integer-mult-bounds/pull/7756) · [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19721689)

| At 2,048 native calls | Two sealed batches | One continuous batch |
| --- | ---: | ---: |
| Homogeneous A roots | 5,232 | 5,176 |
| Homogeneous B roots | 16 | 8 |
| Mixed roots | 8,064 | 8,128 |
| Paid recursive jobs | 12,161,984 | 12,161,504 |
| Independent productive jobs | 2,185,728 | 2,185,472 |
| Ordinary map slots | 67,877,696 | 68,126,112 |
| Scalar services at the retained rate | 52,366,581,760 | 52,630,409,216 |

For the rank price `f(r) = r^(1−κ)`, the paid side loses 224 rank-one jobs, 224 rank-eight jobs and 32 rank-nine jobs. The productive side loses 256 rank-nine targets. The net credit is therefore `224 × (f(1) + f(8) − f(9))`. At the screening target 0.00382065 this covers the two-copy deficit of 0.539322686852 with 2.672422580135 price units of credit. The complete new invoice crosses in **[0.00382069832565, 0.00382069832566]**. [Directed prices and exact histograms](evidence/price.json)

The first call has eight B ports. A mixed root needs seven earlier A visits, so these ports require eight distinct homogeneous B roots in any fully occupied chronological batch using these three words. The placement attains that bound. Its limiting raw crossing lies in **[0.00382075887146, 0.00382075887147]**. The finite 2,048-call claim leaves less than 0.00000006054590 below that ceiling. [Proof and scope](PROOF.md)

## Physical application

The compact graph SHA-256 is `c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84`. Each invocation serves 400 main fields and 862 independent helpers. The certificate checks 819,200 main bindings and 1,765,376 helper owners. All 420,096 caller owners reach their prescribed signed terminal rows. Both the numerical permutation and phase translation are charged on entry and exit, totaling 3,276,800 ordinary view operations. The counted increase in ordinary work is included in the finite service budget. Compiler depth and the 54 strict and four functional outer predicates pass with ordinary BIT pin 0.00385248. [Application receipt](evidence/application.json)

Two implementations reproduce the same complete 35,717,248-instruction stream, SHA-256 `3b326189234984d7797566fa4732d4e2698db778f117cd09bb5654ea740c5563`. One reconstructs the schedule from the root words, port inventory and native layout. The other projects every emitted instruction back to its owner and template position. Symbolic template identities and disjoint root ownership establish the arbitrary-input caller action. Two finite character executions additionally test all final owners with opposite head parities modulo 65,537. [Independent schedule](evidence/seam.json) · [Full owner projection](evidence/expansion.json) · [Finite character executions](evidence/probe.json)

## Reproduce

From the repository root, run with CPython 3.12 and the standard library.

```sh
python3.12 -B scripts/research_package.py --package research/p104-mixed-batch-boundary
```

For a shorter review, `python3.12 -I -B research/p104-mixed-batch-boundary/verify.py price` reconstructs both complete invoices. Use `seam` for the independent schedule and stream checks. Each registered command compares its complete output to the deposited JSON. The manifest gives the scope and timeout of all five commands. [Registered replay](VERIFY.json)

The source subset under `pr7756/` comes from scientific commit `9e051455757d1cc86b822e52e42e1e1c98ead417` and PR head `6b0044123aad114cf71ca2bb0e98741e5a27c7b5`. Its original paths, Git blob IDs and SHA-256 hashes are recorded. The snapshot permits an offline replay while #7756 is pending upstream. Two arithmetic scripts come from canonical main `e54523517d0f03e58352e647c403a5af3e525a57`. [PR source manifest](PR7756-SOURCES.json) · [Base and arithmetic inputs](SOURCES.json)

## Assumptions

The result inherits native application at all positive column multiplicities, owned erasure, uniform mixed-target compilation, precision and tape accounting, and analytic recovery. The evidence covers a finite supplier application. General multiplier materialization, human or proof-kernel acceptance and frontier admission remain open. The canonical selected value at the pinned base is 0.00363005817. [Selected result and assumptions](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/certificates/selected-result.json)

## Open next questions

For admission, independently replay the two caller digests, verify the boundary price, and check the larger ordinary invoice against the finite application. To exceed the three-template ceiling with a different root, first specify its chronological port types and signed outputs, identify the exact replaced roots, and price both sides at equal native calls. [Task and open questions](TASK.json)

## Credit

Clear1nsight prepared this extension with substantial OpenAI Codex assistance, including separate source, price, schedule and application checks. Ali Romman supplied the grouped native graph, mixed root, scheduler and physical binding in #7756. Rohan Arun supplied the mirrored caller construction, SYLforge the homogeneous signed word, and DreamingOfClouds and Claude the nested flags, banked techniques and signed-curvature gate. Clear1nsight’s earlier work supplied causal splits and guarded physical accounting. Jerry Chen / CubeJerry, Douglas Colkitt and the credited community contributors supplied the selected framework and BIT application. Apache-2.0 and predecessor notices accompany the source. [Upstream credits](https://github.com/aliromman/integer-mult-bounds/blob/9e051455757d1cc86b822e52e42e1e1c98ead417/research/p104-parallel-bank-punctures/CREDITS.md) · [Retained notice](pr7756/NOTICE)
