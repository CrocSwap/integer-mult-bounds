# Normal45 terminal A-retiming boundary (no new κ)

Moving any one of PR2942's four terminal normal45 source additions backward,
within the single-accumulator family specified below, **cannot lower its paid
frame cost**. This closes a concrete part of PR2942's open retiming question;
it does not close general retiming, change the selected result or invalidate
PR2942. No new construction or κ is claimed.

Scientific base: `95ff4e2dd396c505932a43ff7c1cdfdd94b8c867`.
Both source words are byte-exact from [PR2942](https://github.com/CrocSwap/integer-mult-bounds/pull/2942)
head `a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf`. The selected maintainer-reviewed
record at the base still gives κ = 0.001672660197076918. PR2942's larger
conditional claim is the experiment's source, not a newly selected frontier.

## Result and scope

All indices below are **zero-based positions before an A gate in the pinned
word**. The selected original addition is removed; its exact transported row
is inserted at the cut. We investigate one addition at a time, preserving the
remaining scalar order, prelude, B, restore, entrances, endpoints and inventory.
All non-prelude A frames are free to change. Every order of the nonzero source
additions is covered. No extra registers or intermediate factoring are used in
this single-accumulator family.

| Addition | Original index | Complete cut domain | Earliest legal cut | Rejected cuts | Surviving cuts |
|---|---:|---:|---:|---:|---:|
| `57 += 94` | 3866 | 1852…3866 | 2164 | 312 | 1703 |
| `57 += 62` | 3865 | 1852…3865 | 2010 | 158 | 1856 |
| `92 += 63` | 3859 | 1857…3859 | 2010 | 153 | 1850 |
| `92 += 61` | 3860 | 1857…3860 | 2164 | 307 | 1697 |

These are the maximal intervals after the accumulator's last read or scale.
For **each provider**, 8,036 cuts give 930 order-independent frame rejections
and 7,106 surviving cuts. Commuting across gates on disjoint registers reduces
the survivors to ten distinct dependency orders; their source permutations
give twelve frame-optimization problems. Both providers therefore cover
**16,072 cuts and 24 exact frame optima**.

Every optimum has exactly the source's local profile:

```text
{1:2434, 2:632, 3:286, 4:104, 5:26, 8:8}
```

This is an exhaustive finite cost result for the stated domain, not “no
candidate found” in a heuristic search. The cost comparisons hold uniformly
for `b ∈ [0.001722816319863214327995, 0.001722816319863214327998]`, using the
inherited price `H_r(b) = r(73/r)^b`. This interval contains the source's
reported complex endpoint and headline; its full admission is not replayed
here. The helper inventory, 86 private cleanup buffers and inherited owner
schedule stay fixed. Consequently there is no local frame-cost gain to pass
to that assembly from this family.

A bounded extension also transports the full rank-one operator across earlier
accumulator readers. For each provider, a directed information-path test rejects
7,078 of the 7,082 earlier cuts, even for **alternative scalar factorizations
with auxiliary registers**. The four unrejected cuts—1851 for each `57` addition,
1856 for each `92` addition—remain **unresolved by that necessary test**. They
are not claimed feasible or cheap. New warps, changed surrounding scalar words,
changed centre frames and simultaneous retiming of several selected additions
are outside this result. See [PROOF.md](PROOF.md).

## Reproduce

Standard library only, no Git or network needed by the verifier. The registered
CPython 3.12.14 run passes, as does a Git-free read-only export under CPython
3.14.7 with `-I -B -O` (78.13 seconds, peak RSS 396 MiB). Both reproduce the same
committed result. See [VALIDATION.json](VALIDATION.json):

```sh
python3.12 -B research/normal45-a-retiming-boundary/verify.py
```

Expected final line:

```text
PASS_NORMAL45_SINGLE_SHEAR_RETIMING_BOUNDARY controls 34
```

The registered command is:

```sh
python3.12 scripts/research_package.py --package research/normal45-a-retiming-boundary
```

The verifier authenticates the five retained input/code files, recomputes the
entire census and deterministic `RESULT.json`, exhaustively optimizes complete
A-frame domains, and replays each representative word in both orientations on
all 632 independent inputs using the retained auditor. Cleanup is regenerated
and all 86 private zero buffers are checked. A separate explicit-subset
implementation recounts the full frame invoice and inventory. Negative controls
cover corrupted inputs, wrong scalar signs, stale cleanup, a missing recursive
charge, and both source orders at forbidden early cuts. Positive controls check
the subspace enumeration and deliberately relaxed centre ceilings.

No native Clifford/Gaussian replay, physical owner admission, precision/tape
analysis, outer release or all-size compiler theorem is claimed. Those inherited
obligations remain separate; finite free-operator replay is not a formal proof
of the full multiplication theorem. There is no claim of a new independent
human audit.

## Method and completed coverage

OS seed **30**, complex-supplier track, chose the source order 94, 62, 63, 61
after the initial inspection of 2/94 (register 2 has no corresponding terminal
A addition). The three initial candidates and the bounded stopping rule are in
[TASK.json](TASK.json). The direct retiming screen was followed by one bounded
multi-target extension. Coverage stopped at the stated finite domains; no
random search, unbounded solver or larger-κ search is hidden in the result.

The public claim is [Discussion2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18974656).
The relevant predecessor is PR2942's fixed-order result. PR2943 addresses the
different fixed-inventory packing problem of PR2930. This package changes
scalar gate order and proves a new scoped boundary; it does not repeat either
allocation audit.

## Open next questions

1. At the four unresolved earlier cuts, can a paid scalar factorization or
   relay avoid the direct source-sharing obstruction? First derive its full
   local profile, including relay initialization, source access and cleanup.
   The directed test passing is only a necessary condition.
2. Can a simultaneous multi-shear or changed centre-basis construction evade
   the single-shear premise? Start with one explicit combined operator and
   require exact endpoint, frame and complete-cost checks. More computation
   within the closed single-shear domain will not help.
3. New warps or changed B/restore/entrance contracts require a separate scope,
   a favorable complete budget, and the missing native/owner/outer admission.

## Credit and license

Prepared by **Tekalign**, with substantial **OpenAI Codex** assistance in
investigation, code, proof drafting and verification. Apache-2.0; the repository
license applies. [CREDITS.md](CREDITS.md) credits the retained construction,
frame-model, exact arithmetic and auditor authors; their files are unmodified.

## Submission freshness

Main was refreshed to `389fa10d714f5b40afe624908e487eb5e424498d` on
2026-10-16. Priority revision 5 and the selected record were unchanged. The new
AGENTS/CONTRIBUTING archive-intake guidance was read: a merged research package
may still be partially reviewed; archival merge is not mathematical endorsement.
PR2942 and PR2943 had merged. The concurrently opened
[PR2948](https://github.com/CrocSwap/integer-mult-bounds/pull/2948), Jeremy Kothe,
head `34e1080739e5e8a4349f8582c31dca798c308d4a`, claims a larger conditional κ
from nine rewrites on PR2917/PR2930, including other A, B, restore and carrier
operations. Its body was inspected for overlap. This package neither audits nor
limits that changed word: its result is the exact boundary of the pinned PR2942
single-shear family. The scientific source pins are intentionally retained.
