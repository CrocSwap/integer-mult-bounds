# Independent exact arithmetic and fixed-profile ceiling — PR5383

The independently reconstructed complete invoice passes the fixed source compiler and outer arithmetic at **κ = .00302666**, tested saving **.00302667**, exact head `4bd6efa51a495a7c7b7754915cf0244e7e60969e`. The final static receipt v3 binds the separate physical and fresh expanded precision/stock gates and has status **FUNDED_CONDITIONAL_INDEPENDENT_STATIC_ADMISSION**, with `endpoint_funded=true`. Registered normal/optimized replay and publication remain separate gates. No selected record or external state changes are made here.

`receipt-v1.json` SHA256 is `fd195f406b6e8e11e29cad1a8d7c4ecf264ea5b968d19472a1ff4a2db0f4b112`. Its independent invoice SHA256 is `7c6dfe167dd83cc48b32743e6bcfa76e3420ccd5be997c935b02a99e3636f44e`; capsule manifest SHA256 is `ae6a1b933c386feabc9bab3300163df41e94bd3ddeeff973955695d33d5b11c8`. The evaluator uses the census histograms, not the author's RESULT or arithmetic engine. An earlier `optimistic-screen-v1.json` is retained as explicitly model-only provenance and cannot be used as admission evidence.

| Obligation | Independent exact result |
| --- | --- |
| Complete paid / productive count | 64,148 / 10,800 |
| Paid / productive rank mass | 237,982 / 238,734; surplus 752 |
| Strict raw root bracket | `(.00302667476807,.00302667476808)`, width `10^-14` |
| Fixed-profile monotonicity | derivative upper ≤ -195473.450610684 on `[0,.05]` |
| Remaining domain | moment upper ≤ -6820.155255095 on `[.05,1]` |
| Paid ratio α | approximately .9999999950169633876 |
| Reserve | `10^-9`, with strict α reserve slack > `3.9830366124*10^-9` |
| Original tail γ / completion tail δ | approximately .95696856409606 / .95165247326188, each strictly below .97 |
| Charged completion/rounding slack | `2145530521/2097154147483648`, approximately .00000102306762885 |
| Fixed compiler tuple | product1024; cutoff20; floor21; moment offset1/5; θ63/64; logarithmic power1000 |
| Uniform gap / saving | `1/700000000`; `.003026668571428571...` |
| Finite compiler height | `j=44836`, `H=31385200000000`, `N=2^H`; successful integer test and preceding grid rejection |
| Outer inventory | every one of 54 strict and four functional slacks positive; minimum strict `1/7000000000` |
| Ordinary BIT reuse | atom1/250; covered saving69/20000; converted saving8590884599/2500000000000; admitted17/5000 |
| Independently billed ordinary allowances | local scalar158744; conservative routes4834000; sum4992744<10^7; complete raw181098496<10^9 |
| Gain over selected #4610 | `.0000048842` |
| Gain over independently admitted #5377 | `.00000431` |

## Arithmetic method and domains

`exact_engine.py` imports only the Python standard library. Its rational enclosure code derives from our separately implemented prior #5377 audit: atanh logarithms with 60 terms and geometric remainder, positive 32-term exponential with explicit remainder and dyadic range reduction, and outward rounding to a `10^55` rational grid. All acceptance comparisons use exact fractions or integers. Floating-point arithmetic is used only for elapsed wall time; report decimals are explanatory renderings of certified rational bounds.

The root enclosure is tested directly, with strictly positive lower-bound moment at the lower endpoint and strictly negative upper-bound moment at the upper endpoint. For the signed profile `a[r]=T[r]-P[r]`, the derivative is `-sum a[r]*log(r)*r^(1-c)`. Sixteen directed interval subdivisions prove it is negative on `[0,1/20]`; 128 further subdivisions prove the moment negative on `[1/20,1]`. Thus this **particular complete P/T profile** has one admissible crossing in `0<c<1`. This is a necessary profile ceiling; it is neither a ceiling over constructions nor a global optimum over compiler parameters. No additional root digits or broad parameter search were pursued.

The current source tuple is fixed. The evaluator rejects changed model IDs or a different tuple as `OUTSIDE_PROVED_DOMAIN`, and requires ambient rank145. Only the separately justified source formula is evaluated:

`alpha=P(t)/T(t)`, `gamma=P(t+1/5)/(20^(1/5)*T(t))`, `delta=10800*21/(20^tested*T(t))`, `t=1-tested`.

The full original and completion tails are charged. The proof checks `.97^128<1/16`, `4*.97^1024<4/2^32`, the rounded normalized paid upper bound, `20^64<21^63`, shifted exits, complement η capacity, initial logarithmic-majorant range and finite height domain. Uniform saving is strictly below the tested saving, by exactly one gap.

The finite compiler grid uses `step=700000000` and `H=step*j`. It checks `(H+1)^1000<2^j` and failure at `j-1`. For real `x>0`, `1000 log(step*x+1)-x log2` is strictly concave, equals zero at zero, has positive derivative there (`1000*step>log2`) and tends to minus infinity. It therefore has one positive crossing; the adjacent exact tests establish the minimum success on this specific sufficient grid. They do not establish optimality among compilers.

## Source and transfer coverage

`bind_and_check.py` rechecks all 36 capsule rows against SHA256, byte length and raw Git-blob digest, and both raw commit object IDs. It binds the exact independent invoice SHA, literal word/controller/source hashes, source-tested constants extracted from the AST without execution, and the capsule producer's authenticated raw ancestry report. It independently verifies that the current controller, endpoint ledger and ordinary-BIT source record have exactly the previously independently reviewed source hashes. Complete Git-tree/history provenance remains the capsule producer's responsibility.

The 54 strict transfer values are independently transcribed and evaluated in `exact_engine.py`. `check_source_inventory.py` statically checks the exact current endpoint source inventory: 45 direct strict names plus nine margin-derived names; three inherited functional names plus the explicit stronger-BIT stock predicate, giving four. This is the current source interface's actual inventory, rather than treating “58” as universal.

The stronger ordinary BIT record is reused at its authenticated source hash. This arithmetic check verifies the actual conversion formula and strict domain `atom > ordinary > admitted > tested` and `atom < 1-ordinary`. It separately evaluates the inherited generic row-stock predicate `beta*(997/1000)` and actual stronger-BIT stock predicate `beta*(249/250)`. The former does not replace the latter. Fresh expanded complex/BIT product-stock and fixed-tape applicability remain role03's separate gate.

## Negative controls

The exact ledger rejects old BIT saving .0027, a closed uniform gap, charging the tested saving as final κ, epsilon=1, missing layout and full-dimensional groups. Charged reserve controls reject an excessive `10^-8` reserve at this tested point, insufficient `10^-13` reserve for the completion/rounding envelope, and the power128 envelope. The adjacent preceding compiler grid and raw upper root endpoint are rejected.

The source-binding layer rejects an altered source byte stream, an unsupported model, an unsupported cutoff tuple and an invoice with 128 unearned rank-nine productive outputs, because it no longer matches the frozen independent census SHA. This productive-credit control authenticates the census boundary; physical correctness of excluding those helpers is separately established by role01's actual word controls.

## Scope and attribution

The five conditional source assumptions remain `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`. This worker runs no author module, native evaluator, Lean, full cold replay, or materialized enormous compiler word. The exact invoice, physical all-column word, expanded finite-template proof and registered replay are distinct evidence streams. Receipt v1 retains `endpoint_funded=false` as the earlier arithmetic-only evidence. Final receiptv3 binds physical receiptc8221d..., precision closure0a171a... (leaf-inclusive error addendum), the same invoice/capsule and all four canonical generic proof references. It checks no new candidate-specific assumptions, correct fresh N/C1 and stronger-BIT stock product, then sets `endpoint_funded=true`; it still makes no registered-cold or publication claim.

Ali Romman owns #5383's eight-relation construction. Preserve Cao Yifan's #4610 word; Cinna Davis's controller/helper lineage; zxv's native/compiler/precision contributions; Jacob Alan Sussman's mixed-target recursion; Chris R/Clear1nsight's independent #5241/#5384 admission, and all source notices. This review used substantial OpenAI Codex assistance.

Read-only reproduction: `timeout 60s python3 -B outputs/price-plane-swarm-20261024/04-exact-funding/reproduce.py`. This completed successfully in19.830 seconds, reauthenticated the capsule/invoice and compared every exact arithmetic result to the immutable receipt. It writes no source or receipt. `bind_and_check.py` is the historical producer; its output immutability guard intentionally rejects a second write to receiptv1.

Final static closure: `receipt-v3.json` SHA256 `a5f48459f8500909a243462c2cd205c57f064fc76ef7082ba41c516fbd5a5794`. `close_5383_v3.py` performs hash and applicability-contract checks only; it preserves the exact numeric receiptv1 and its separately re-executed arithmetic.
