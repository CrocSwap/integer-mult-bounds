# Independent audit of the mutable-leaver all-K cells (PR1005) and the seven-slot word (PR1018)

**Status: adversarial audit / independent verification. No new kappa. No counterexample found; one
documentation discrepancy.** The selected result and `upstream/` are unchanged.

Track 60–74 (adversarial audit), OS-random assignment seed **65** (`secrets.randbelow(100)`).
Base `2921874911956718fcaaaf9396fe8267b3cfa9f0`. Audited heads: PR1005
`779e80aef469bc3a28b19f1adde199871a9a22e3` and PR1018 `eac7547cb191f875d5f5ea5f9bbb1d2b8c51c4ef`.
PR1022, PR1028, PR1031 and PR1042 pin the same seven-slot local word (`c2b29430…`), so the
local-word results below also apply to them. Their owner maps and global replays are not covered.

## Why this object

PR1004/1005 introduce "mutable-leaver" cells. A coded 21-gate circuit uses face-event operands that
have no later reads as mutable scratch, and the "inherited cleanup" restores them at FULL. The k8
cells are the local word for six open κ claims (PR1005, PR1018, PR1022, PR1028, PR1031, PR1042). Their
recorded reviews come from the authors' own reviewer agents. Checking the premise independently is
the cheapest way to support or block that whole lineage.

## Statements checked

The verifier is standard-library only and imports nothing from the audited packages. Their words are
read as data (inputs pinned in `SOURCES.json`).

1. **Exact local map (all three words).** Every one of the 224 data columns, replayed forward through
   precondition, A, cut, B, tail and cleanup, gives `x -> x` and `y_t -> y_t + x_t`. For each of the 480
   helper columns, the inverse of the post-precondition program returns the unit vector plus a residue
   supported on targets only. This is exactly the condition for the pre-main compensation `y -= a·h`
   to exist, and it is a different formulation from the authors' constructive one. The residue
   vanishes for every entering helper.
2. **Frames.** An independent replay of monotone climbs over A, the centre paths, B, the early-cleanup
   tail and the terminal ends reproduces each word's recorded paid profile. The FULL cleanup touches
   only registers that end at FULL.
3. **Leaver premise.** All 8 coded cells are found literally, each exactly once, contiguous and in the
   published gate order, by unifying the `scaled` gate lists of `CODED-CELLS-k8.json`. The target sets
   come from `TRI-LEAVER-k8.json`; the coded target index is the TRI read index + 8, checked for all
   cells. The 24 mutated leavers (12 data registers, 12 helpers) satisfy all of the following:
   * none is a centre, entering helper or low-ended helper;
   * none is touched again in A, cut, B or the early-cleanup tail after its cell;
   * each is written in the FULL cleanup;
   * each holds a value different from its input at the end of B, so the restoration is real FULL
     work.
4. **No new class of source mutation.** Each of the 12 data-register leavers receives exactly one
   B-section write in both the no-triangle base word (`3e99ba77…`) and the cell word, and their
   A-section writes are identical. The cells re-pair or re-scale these pre-existing face-event writes
   (8 of 12 differ) and remove the packet-copy helpers. They add no mutation event to any data
   register. The dependence on mutable sources is therefore the one the gauge44 lineage already
   inherits.
5. **Profile deltas.** The raw-stage paid profiles, recounted with the replay of item 2, are additive
   per cell:

   | word | R | raw paid profile |
   |---|---:|---|
   | no-triangle | 504 | `{1:1880, 2:832, 3:312, 4:168, 5:168, 6:56, 8:8}` |
   | k5 cells | 489 | `{1:1910, 2:772, 3:327, 4:168, 5:168, 6:41, 8:8}` |
   | k8 cells | 480 | `{1:1928, 2:736, 3:336, 4:168, 5:168, 6:32, 8:8}` |

   `k5 − notri = 5u` and `k8 − k5 = 3u`, where **u = +6H1 −12H2 +3H3 −3H6** (rank mass −27, three
   helpers removed per cell). The seven-slot word differs from the final k8 word by exactly
   `7×{3:+2, 4:−4, 5:+2}`, which matches PR987's per-slot claim.

## Finding: per-cell profile claim not reproduced

The PR1004/PR1005 descriptions state: "Each cell changes the raw paid profile by exactly
−30H1+6H2+6H3." That claim is rank-mass-neutral. Against the no-triangle comparator, the measured
per-cell change is `+6H1 −12H2 +3H3 −3H6`. No rebuilt stage (raw, regroup, hpe, cold44) shows the
stated vector. The packages do not state the claim's comparator, and no code asserts it.

**This does not affect κ.** κ is priced from the final word's full profile through the reviewed
global replay. It is a description that reviewers should not rely on. The authors should state the
comparator or correct the sentence.

## Negative controls

Each mutant must be rejected by the check it targets. All 14 are rejected (7 on the final k8 word, 7
on the seven-slot word):

| control | rejected by |
|---|---|
| N1 drop a leaver write | endpoint |
| N2 drop the FULL-cleanup restoration of a leaver | endpoint |
| N3 neutral `h += ½x; h −= ½x` on a leaver at FULL after its cell | **premise only** |
| N4 wrong cell coefficient | endpoint |
| N5 leaver write moved after its first dependent read | endpoint |
| N6 entering-helper dirt into a cell target | endpoint (entering response) |
| N7 leaver gate below its current frame | frames |

N3 passes both the exact endpoint and the frame replay with an unchanged paid profile. The stated
premise is therefore a design property that the exact map and frame checks do not enforce on their
own. This audit checks it separately.

## Reproduce

```sh
python3 -I -B research/leaver-cell-audit-seed65/verify.py
```

Expected (about 5 s), with the result byte-compared to `RESULT.json`:

```text
PASS_INDEPENDENT_MUTABLE_LEAVER_AUDIT cells=8 leavers=24 columns=704 controls=14 per_cell_raw={1: 6, 2: -12, 3: 3, 6: -3} claimed_match=False
```

To rebuild the inputs, follow the README clean-clone commands of PR1005 (`reproduce.py --until word`,
`reproduce_notri.py --word-only`, `reproduce_leaver.py --id k8|k5 --word-only`,
`reproduce_leaver_chain.py --id k8`) and PR1018's `verify_slots.py --baseline <chain>`. The PR635
supplier is pinned at `a6895a69…`. `SOURCES.json` names each output file and its content hash. Every
hash equals the pin the PRs publish. In this run all 21 PR1005 chain steps (`STEPS.json`) exited 0, and PR1018 printed
`PASS_SLOTS_ON_CHECKED_K8_BASELINE 0.00167166528321877`.

## Scope and open obligations

This audit checks the local scalar/frame words only. It does not check the owner maps (K8c8, the T16
packings), hosting, the finite invoice, the moment and outer pricing, or any κ value. Nor does it check
the inherited mutable-source/common-label realization, Lemma A/G content, all-size compilation,
precision/tape or the analytic interfaces. Item 4 shows that the cells require nothing beyond the
inherited interface; it does not prove that interface. Finite replays are not a formal proof.

## Credit and disclosure

The construction and the audited packages are Jeremy Kothe's PR1004/PR1005/PR1018 (LeaverSAT, the
reviewer agents and G44Pack3 as named there). They build on rohanarun's PR987 slot search, NewBArch's
PR869 triangle-hybrid delivery, icekylinx's PR645 gauge44 construction and its `audit_local.py`, and
chafreaky's PR685/741 lineage. Two input files (`CODED-CELLS-k8.json`, `TRI-LEAVER-k8.json`) are
copied unchanged from PR1005 under the repository's Apache-2.0 license. The other inputs are outputs
of the authors' drivers.

Prepared by Sagar Thakrar with substantial assistance from Anthropic Claude (Claude Code).
