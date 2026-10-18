# T185 dirty-entry and frame-refit screens (negative result)

**No new κ is claimed.** This package bounds the most direct native-word lever left after
[#2863](https://github.com/CrocSwap/integer-mult-bounds/pull/2863) proved the fixed-inventory packing optimum:
letting more helpers enter dirty **while every existing gate stays fixed**. It screens the PR2857 shared-kernel
words of #2863 and the newer preload-move words of
[#2894](https://github.com/CrocSwap/integer-mult-bounds/pull/2894) (Jeremy Kothe, 07:49 UTC, κ ≈ 0.0017201845).
Within the screened class there is **no frame-feasible candidate** on any of the four words. The same screen
reproduces exactly the 16 quartet helpers found by #2853's census on the older PR2833 words.

With every frame constraint removed, all 184 eligible helpers of the PR2857 words become algebraically
cancellable: the obstruction is frame placement, not linear algebra. #2894 is consistent with this. Its two new
quartets (456,457,466,467) and (458,459,464,465) all have a zero-frame first gate in the PR2857 words, outside
the fixed-gate class, and #2894 reaches them by re-synthesising the preload. This agent's ledger independently
reproduces #2894's local profile {1:2404, 2:642, 3:262, 4:128, 5:26, 8:8} and its inventory {8:86, 9:232}.

## Why this lever

On #2863's fixed packing model (dual prices from its `review/PROOF.md`), the float screen in
`tools/dual_screen.py` gives these first-order values per helper changed in all nine calls of a replica:

| Change | κ change, first-order |
|---|---:|
| Any single packing move (the #2863 gap) | about 4e-9 |
| One more PR2857-type staged rewrite, width 9→8, local 3H1−2H2 | +3.6e-7 |
| Enter dirty at a dimension-1 first frame (−H1, width 9→8), before receiver costs | +5.9e-7 |
| Width 9→8 with no native saving | −4.8e-5 |

The break-even extra climb cost for a dimension-1 entry is 0.0122 per call. These are screening estimates that
assume an unchanged LP basis, not certificates.

## What was screened

A compensated helper q0 can start at a nonzero frame only if its whole target-dirt response is cancelled inside
the program. `tools/entry_screen.py` tests whether that response lies in the exact rational span of responses
reachable by inserted gates `r += u*q0`:

- **Responses.** `tools/wordlib.py` computes an exact backward (adjoint) pass giving every register's
  target-dirt response just before every program item. It reproduces the stored compensation, after the
  precondition map, for 402 of 408 live helpers on all four words. The six exceptions are the warp-tainted
  initial-correction sources, which are excluded.
- **Insertion times.** Any program position outside the prelude and cut, up to q0's purity horizon. Before q0's
  first use, q0 = z0. Afterwards every read partner must be unchanged, with cancellation gates
  `r += -u c s` at the same frame.
- **Receivers.** Every live non-target register except q0, entering helpers and correction sources. Mode
  `direct` also excludes q0's own partners. Mode `pre-only` allows only insertions before q0's first use.
- **Frames.** One gate frame U with join(current frames) ⊆ U ⊆ meet(next requirements) for the receiver, q0 and
  every cancelled partner. Requirements come from the full program timeline: A, A/B target and centre pins,
  warps, B, restore and end frames.
- **One-hop relays (`--chains`).** Inject into an intermediate helper m, then `r += k*m` later, with m's partner
  cancellation. A relay gate moves m's whole content, so a plan is valid only with a nonzero injection
  coefficient. The test is: target ∈ span(V + R_m), and either R_m ∈ span(V) or target ∉ span(V).
- **Cost.** A pruned greedy upper bound on the extra climb cost, with H_r = r^p at the #2863 root.

`tools/refit_screens.py` is a **side check**: single-gate frame moves and forward/backward frame cascades
inside the fixed scalar word. The task card treats that class as covered by #1995/#2013 for older words.

## Results

| Word | Screen | Result |
|---|---|---|
| PR2833 base/extra (control) | direct, pre-only | exactly {460,461,468,469}, {462,463,470,471}, {478,479,490,491}, {480,481,492,493} |
| PR2857 base/extra (#2863 words) | direct, pre-only | **0** of 184 eligible (86 have a zero-frame first gate) |
| PR2857 base/extra | one-hop relays | 8 apparent (409, 411, 413, 415, 425, 427, 429, 431), **0 valid** |
| PR2857 base/extra | refits | single-gate 345 candidates, forward 2797 (53 feasible), backward 3009 (96 feasible): **0 improving** |
| PR2894 base/extra (preload-move words) | direct, pre-only | **0** of 182 eligible (84 zero-frame first) |
| PR2894 base/extra | one-hop relays | 8 apparent (same helpers), **0 valid** |
| PR2894 base/extra | refits | single-gate 345 candidates, forward 2803 (56 feasible), backward 3015 (96 feasible): **0 improving** |
| PR2857 base/extra | frames relaxed (control) | 184/184 in span, including 86/86 zero-frame-first helpers |

Failure controls in `verify.py`:

- A corrupted compensation coefficient is detected.
- A broken frame chain is rejected by the ledger.
- A de-optimised word (one climb split by lowering a gate frame) is repaired by the refit screen.
- The relay-validity test accepts six known relays for quartet helper 478 on the PR2833 word.

The survey agent independently re-ran #2853's own census tool (`dirt3.py --climb`) on the PR2857 words and
found 0 of 185 passes. That corroboration is local-only and not packaged.

**Bugs fixed during the session.** Each produced false positives before publication, and each was caught by
building a literal word or by the control:

1. Responses were recorded after an event instead of before it.
2. Next-frame requirements ignored B, restore and pin events.
3. A pre-insertion into q0's own partner was combined with a post-insertion that assumed the partner unchanged.
4. Relay vectors were treated as independent of the injection into the intermediate.

The published tools implement the corrected rules.

## Independent reproduction of #2863

`evidence/T185-REPLAY.json` records the reproduction.

- **Fast replay:** all five stages pass under Python 3.14.
  - The published head omits two `.gitattributes` files (`* -text`) that its manifest lists; restoring them
    from #2857 matches the pinned hash.
  - The regenerated `FILL.json.gz` differs only in its gzip container.
- **Complete cold replay:** passes in 1507 s (CPython 3.13.16, NumPy 2.5.4, SciPy 1.18.1, SymPy 1.14.0,
  mpmath 1.4.1) with κ = 0.001720100805416885927944 − 10⁻⁴⁶ − 10⁻⁷⁰ exactly.
  - The release receipt differs from the published one only in a wall-clock `seconds` field and the manifest
    hashes it cascades into. Substituting the published values reproduces the published receipt exactly.

## Reproduce

From the repository root (standard library only):

```sh
python3 scripts/research_package.py --package research/t185-dirty-entry-frame-screens --check-only
python3.12 scripts/research_package.py --package research/t185-dirty-entry-frame-screens
# individual screens
python3 -B research/t185-dirty-entry-frame-screens/tools/entry_screen.py \
  --word research/t185-dirty-entry-frame-screens/vendor/pr2857/WORD-base.json.gz --chains
python3 -B research/t185-dirty-entry-frame-screens/tools/refit_screens.py \
  --word research/t185-dirty-entry-frame-screens/vendor/pr2857/WORD-base.json.gz
# frame-relaxed census (about 12 minutes per word; not registered)
python3 -B research/t185-dirty-entry-frame-screens/tools/entry_screen.py \
  --word research/t185-dirty-entry-frame-screens/vendor/pr2857/WORD-base.json.gz --relax-frames
```

The registered `core` part takes about 110 s, and each `chains2857` / `chains2894` part about 250 s locally.
`evidence/VERIFY-RECEIPT-local.json` stores the local outputs.

## Scope and limits

This is a bounded screen of single-helper dirty entry and fixed-word frame refits. It is not an impossibility
theorem for native words. It does not cover:

- changed gate schedules or mixing blocks;
- simultaneous multi-helper entry;
- relays longer than one hop;
- operator-word corrections for warp-tainted helpers;
- receivers excluded above.

A positive screen would still need a literal word, the inherited exact endpoint audit, a new allocation, complete
admission and the outer release. All inherited all-size, compiler, hosting, precision/tape and analytic
assumptions of the frontier remain. No selected record is changed.

## Open next questions

The structured list is in [TASK.json](TASK.json):

1. **Re-route the phase-A mixing block.** Can it be changed so zero-frame-first helpers start at nonzero frames?
   The algebra already admits all of them. #2894's preload re-synthesis realises two quartets, leaving 84
   zero-frame-first helpers on its words. The first step is one remaining helper's pinning gates and an exact
   endpoint audit.
2. **Joint plans.** Do joint multi-helper plans or relations with two or more outside helpers (e.g. 479 via
   502/503/490) admit frame-feasible plans? This overlaps the advisory investigation in
   [Discussion #2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612) and #2875's unsearched
   lane.
3. **Warp-tainted helpers.** Can operator-word corrections make them cancellable?

## Credit

- **Source words:** Yiyang/Lyy-iiis (PR2857 shared-kernel words) and Jeremy Kothe (PR2833 dirt-entry words and
  auditor conventions), both vendored byte-for-byte with their notices in `vendor/`.
- **Census definitions and the control set:** Philippe Van Velzen (#2853).
- **Packing optimum and dual prices:** Dugongue (#2863).
- **Preload-move words:** Jeremy Kothe (#2894), vendored in `vendor/pr2894/` with that package's NOTICE and
  CREDITS.
- **Related predecessor screens:** #2875 (digitalis-p).
- **Retained lineage:** all contributors credited in those notices.

Prepared by digitalis-p with substantial Claude (Anthropic) assistance. Apache-2.0.
