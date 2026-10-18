# Concurrent T37 construction: equal exponent, distinct owners

Jonathan Capalbo (@jon314159) published [PR942](https://github.com/CrocSwap/integer-mult-bounds/pull/942)
at `1960cfa919a0945d0ca4cb14ea96237000037903` during this contribution's
verification. It reaches the same conditional κ = 0.001661960547713947 and
has since been selected on main. No unique record, priority, or gain over
PR942 is claimed here. Its code is not imported into this package.

Both constructions combine the PR890 T21 and PR870 T16 owner sources,
preserve the U8 word and PR589 bit supplier, use 37 replicas, pay complex
payload1024 and obtain idle profile `{48:11086,1:6}`. Both certify the same
complex endpoint and κ. The finite row charge is 17495 in both.

The actual physical witnesses differ:

| Obligation | PR942 | This seed39 construction |
| --- | --- | --- |
| Merge keys, T21 / T16 | `144*i` / `189*j` | `16*i` / `21*j-528` |
| Ties | T21 first | T21 first |
| Changed owner records | 8 | 10, including 6 relocations |
| Additional mathematical claim | all-T upper bound for its unchanged U8 family | no all-T or optimality claim |

This package reconstructs its alternative owners from the same pinned
predecessors and independently expands source events, whole-role windows and
73-axis charts. Its strict 20-stage replay rechecks all 333 invocations,
167832 helper roles, the emitted controller, the complete cost invoice and
all 47 outer inequalities. Much of that replay deliberately uses shared
inherited code, including the two exact moment engines. It is not an entirely
code-disjoint audit of PR942 and does not independently validate PR942's
all-T proof.

The extra boundary evidence includes 47 package rejection controls, two
positive recompression controls, byte-for-byte reconstruction of runtime
source adapters, and five payload mutants required to reach their named
assertions. All 30 predecessor/current omitted owner edits and both omitted
interleaving delays are also checked. Exact receipts and source hashes are
retained beside this note; the default command rebuilds the full ancestry.

The final overlap check also found Joel Pulikkan (@GamingPuzzled)'s
[PR962](https://github.com/CrocSwap/integer-mult-bounds/pull/962), head
`50c6ae8151493af21d284afe34fb35f68f6d4934`. Its PR description reports another
independent eight-edit construction, with merge keys `(i+1)/189` and
`(j+1)/144`, the same κ and a cold ancestry replay. We inspected that
description and changed-file inventory, but did not execute its package.
Its work is credited as additional concurrent corroboration. This submission
adds the shifted ten-edit witness and the specific runtime-byte, receipt
binding, recompression and assertion-targeted payload evidence above; it is
not offered as a new packing mechanism relative to these concurrent results.

One explicit accounting difference is resolved by
`check_bootstrap_reserve.py`: our runtime retains the predecessor's literal
512 in the bootstrap linear cutoff term, whereas the concurrent packages
raise it to 1024. For every one of our fourteen recorded gaps,
`gap <= 9/514`, hence `36/gap^2 >= 2*(4+1024)/gap`. The quadratic term
therefore selects exactly the same integer cutoff under either allowance.
The source-bound standalone check verifies both reserves and this equality,
with four negative controls. No smaller cutoff is claimed or needed here.

Source readings used for comparison: PR942's `PROOF.md`, `CLAIM.json`,
`evidence/README.md` and `ALL-T-PROOF.md` at the head above. Its reported
checks are credited as its evidence, not passed off as our execution.
The finite certificates retain the all-size/compiler, realization, hosting,
precision/tape, analytic-transfer and bit H1–H5 assumptions. They do not
constitute a formal proof of the full multiplication theorem.

Prepared by Tekalign (@tekuuu) with substantial OpenAI Codex assistance.
