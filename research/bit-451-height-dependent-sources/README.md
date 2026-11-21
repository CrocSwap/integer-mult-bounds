# Height-dependent source capacity for the 451-factor multiplier

The existing fixed-multitape algorithm returns the exact product of every pair of n-bit integers in time O(n (log n)^(1−κ)) with **conditional κ = 0.00387992804547**. This change improves the proof of its ordinary BIT cost. It preserves the finite supplier, caller, productive ownership and five inherited premises. [Proof](PROOF.md) · [Independent rational certificate](RESULT.json)

| Complete comparator | Previous κ | Exact increase | Percentage increase, rounded | Exact percentage |
|---|---:|---:|---:|---:|
| [Preceding #8026 power-19 proof](https://github.com/CrocSwap/integer-mult-bounds/blob/70c410a0b219d906a4162bd37e81fdb8ea0854b6/research/bit-451-carrier-cover/tensor/SIBLING.json) | 0.00387992804544 | 0.00000000000003 | 0.000000000773210215464% | (25/32332733712)% |
| [External #7863 supplier](https://github.com/CrocSwap/integer-mult-bounds/commit/b3e4412fe01f07dc58305616fabf96345f49a781) | 0.00387992804346 | 0.00000000000201 | 0.000000051805084462534% | (3350/64665467391)% |

At fixed p=18 and scale 1804, a rank band of unmodified paid siblings proves a factor of 5/2 for nonroot inputs. For root inputs the argument separates the two input-size ranges at x=K^(7/8), where K=16^451 and n=134^451 K^G x. The upper range bounds root weight relative to the total source mass by a decreasing geometric upper bound. The verifier checks 19 Newton coefficients in the first region, all 32 initial heights in the second region, and 19 translated coefficients for the tail from height 32. Dropping the improved denominator in the upper region fails at a finite height. The signed carrier loss falls from 747/H to 708/H. After all seven ordinary stages, the cap is 0.00387992804555917 and the complete application tests 0.00387992804554. The new claim exceeds the old relaxed ceiling by exactly 209/33400000000000000. [All-height inequalities](PROOF.md) · [Signed receipts](SIGNED.json)

## Reproduction

Run from the repository root on POSIX with CPython 3.12 and its standard library.

```sh
python3.12 -IB scripts/research_package.py --package research/bit-451-height-dependent-sources
```

This command authenticates and unpacks the original 202-entry #7863 source manifest, regenerates the native 36-call supplier and first reproduces the known-good power-19 complete application. It runs two independent arithmetic implementations of the height-dependent proof, checks all 70 rows, and cold-replays the 48-call rational consumer for the new cap, including both signed orientations, all 54 strict and four functional checks, precision, tape, and the low-cap and extra-paid-call controls. For both calls it checks all five generated scientific file hashes. The original archive and scientific controls come from the pinned companion package. The final marker is `PASS_COMPLETE_HEIGHT_DEPENDENT_SOURCE claim=0.00387992804547`. [Exact prior files](SOURCES.json) · [Registered verification](VERIFY.json)

The original Round 342 primary run stopped after confirming the full projected price, limiting guard and both nonroot guards. Its 45-second discovery alarm was delivered after an expensive conversion of a decimal neighbour of zero into a rational. The run finished in 65.275 seconds and did not verify a finite height or a Newton coefficient. Round 343 made log(1) exactly zero, kept the case and prior completed values pinned, and reproduced all 70 rows under a 45-second supervisor deadline. The independent rational evaluator and signed replay had already completed. This same frozen case contributes one gain. [Original capped receipt](CAPPED.json) · [Corrected screen](screen.py) · [Independent proof](audit.py)

The five premises cover native action on all columns, owned erasure, compiler closure, precision and tape, and analytic recovery. The physical seven-stage transfer still requires the original and nested stock to return at every stage. The selected record on main remains #7000. Clear1nsight supplied the #7863 schedule and #7973 consumer replay, Jacob Alan Sussman the finite Pascal compiler, DreamingOfClouds the ambient and cover argument, zxv the finite compiler and weighted induction, JoyboyBrian earlier paid rank and clipping bounds, and Ali Romman the paired caller and all-height framework. Earlier #8026 proofs supplied the paid variance, complete moments and source counts. OpenAI Codex materially assisted the proof, code and independent replay. [#7973](https://github.com/CrocSwap/integer-mult-bounds/pull/7973) · [#4359](https://github.com/CrocSwap/integer-mult-bounds/pull/4359) · [#4480](https://github.com/CrocSwap/integer-mult-bounds/pull/4480) · [#5042](https://github.com/CrocSwap/integer-mult-bounds/pull/5042) · [#5070](https://github.com/CrocSwap/integer-mult-bounds/pull/5070)

## Open next questions

Could power 17 at h=1804 satisfy a stronger height-dependent source bound on this same word? First price the full change and test the necessary limiting ratio and attainable root and nonroot source capacities for the proposed factor of four. A viable case still needs a positive result on every size and height under the existing carrier and an independent signed replay.

The public handoff includes the original capped attempt, independently checked signed receipts, a clean replay command, scope and restart point. [Reproduction handoff](https://github.com/ToikY/integer-mult-bounds/blob/f6eb39804cb9eaefd927f8ede928ae7b453674f5/ROUNDS-341-343.md) · [Timestamped discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19797952)
