# Owner fill and width-aware ceiling for the PR2339 80-alias T74 words

**Negative result; no κ claim.** This package takes the 400-helper words of
[PR2339](https://github.com/CrocSwap/integer-mult-bounds/pull/2339) (PR2226 low anticipatory aliases on
the PR2269 T74 borrow words) and builds a legal whole-helper owner fill on the unchanged PR2269 T74
template. The fill is recounted and priced independently. Then it bounds every such fill:

| object | b |
|---|---|
| PR2339's own estimate (width-blind cap × PR2269's realized fraction) | ≈ 0.0017259 (**wrong**) |
| width-blind R = 48 packing cap (merged `complex-local-word-ceiling` model) | 0.0017479583719744 |
| **certified width-aware ceiling, any legal whole-helper fill** (`ceiling_lp.py`) | **< 0.0016867** |
| **realized legal fill OWNERS-80** (native, certified bracket, width 1e-40) | **0.0016865432362690642682…** |
| PR2269 claimed b (43 high aliases, same template) | 0.0016962471390584742… |

The realized fill reaches 99.994% of the width-aware LP ceiling, so the fill is not what loses the
mass saving. Both numbers sit 9.7e-6 (0.57%) **below** PR2269. The low aliases free 121 local rank
units per call. But they replace width-8 helpers, which pack exactly into the rank-8/16/32 bins, with
width-9 lenders, which do not. The fragmentation costs more than the freed mass.

This corrects PR2339's "≈ 0.0017259" estimate and its model prices F/C/C8 (0.0017255 / 0.0017127 /
0.0017141). None of them is attainable on this template with unsplit helpers. PR2339's local
construction and its width-blind cap are not affected: the cap is a valid but loose upper bound.

**Concurrent work.** [PR2360](https://github.com/CrocSwap/integer-mult-bounds/pull/2360) (Jeremy
Diviney, head `16d4ea6c`) appeared while this package was being prepared. It independently certifies
b < 0.0016870 for the same words with the same 1,163-pattern relaxation, using an all-extra envelope.
This package was written independently and adds:

1. the actual legal fill (the attainable side; PR2360 has only the ceiling);
2. a tighter ceiling, b < 0.0016867, from the real 249/417 dispatch;
3. the variant and control cases below;
4. an independent re-check of PR2360's `DUAL.json` (all 1,163 inequalities hold; lower bound of
   66304·mu = 66304.0043 under its envelope), with a tampered-dual rejection.

The pattern-dual relaxation itself comes from PR1129 (Ali Romman) and the R480 pattern-dual audit.

## Width-aware ceilings (`ceiling_lp.py`)

Fix the local words. Every role sits whole in one idle bin of rank R ∈ {8, 16, 32, 48}. The bin
counts are N_8 = 49728 and N_16 = N_32 = N_48 = 33152, recounted from the PR2269 plan. The moment is
linear in the child counts, so 66304·mu(a) is at least the local term plus the minimum over
fractional pattern counts. Any exact feasible LP dual bounds that minimum from below. Floating
simplex duals are converted to rationals. They are repaired to exact feasibility against 800-bit
lower enclosures of (r/73)^(1−a), and the bound is checked exactly.

| case | widths {4,5,7,8,9} per call | LP ceiling (float) | certified | realized |
|---|---|---|---|---|
| PR2269 words (43 high) | 36, 9, 36, 116, 240 | 0.0016964047495 | b < 0.0016965 | PR2269 claim: 99.991% |
| PR2322 words (positive control) | 33, 9, 38, 114, 240 | 0.0016971957580 | b < 0.0016973 | PR2322 claim: 99.992%; PR2374's 0.0016971949509: 99.99995% |
| +5 high only (PR2339 variant) | 36, 4, 36, 116, 240 | 0.0016964047495 | b < 0.0016965 | numerically identical to PR2269 at displayed precision |
| 32 low only (PR2339 variant) | 4, 9, 36, 84, 272 | 0.0016866447555 | b < 0.0016867 | — |
| **PR2339 80 aliases** | 4, 4, 36, 84, 272 | 0.0016866447555 | **b < 0.0016867** | **OWNERS-80: 99.994%** |

Why the low aliases lose. The LP optimum for PR2269 fills 2,294 rank-32 bins with [8,8,8,8] and
23,976 with [4,9,9,9], so few bins keep a remainder. For the 80-alias inventory, 36 width-4/5 helpers
per call become 8. Then 27,824 rank-32 bins host [9,9,9] and keep an idle rank-5 child, and 6,068
rank-16 bins host a lone [9] and keep a rank-7 child.

The +5 high aliases give no gain at the displayed numerical precision. Each one removes a local
rank-5 child, but the corresponding pattern replacement turns a [5,9,9,9] bin into [9,9,9] with an
idle rank-5 remainder. This explains the cancellation in that pattern; equality of the printed
floating-point LP optima is not itself an exact global-optimality certificate. The separately
certified upper bounds in the table remain valid.

The profiles of the two PR2339 variants are taken from PR2339's README table. Their width inventories
follow from the alias definitions: a high alias drops a width-5 helper, and a low alias drops a
width-8 helper and turns a width-4 lender into width 9. The PR2322 profile comes from its README
(head `002304ef`). PR2374's leftover idle ranks {1:21978, 3:8592, 5:2552, 32:1, 48:24560} match this
LP optimum up to rounding, which is consistent with its window-free optimality statement.

## The fill (OWNERS-80)

`build_fill.py` is deterministic and uses no randomness (about 230 s). It takes LP-optimal target
patterns, runs an earliest-deadline sweep over the PR2269 global template windows, and finishes with
a hill-climb. It covers 666 calls (249 gauge44 + 417 extra, PR2269 dispatch) × 400 helpers = 266,400
roles in 69,734 idle remainders.

The global profile is {1:1529770, 2:354318, 3:267386, 4:83250, 5:52489, 7:6114, 8:5328, 41:33,
48:22786}. It satisfies mass 4,816,512 = 73·66304 − 23680 and the halving guard 73² > 2·48².

`fill_check80.py` is standalone and adapted from our own iteration-3 checker, PR2315. It recounts the
fill from the pinned PR2339 words and the PR2269 template under these rules:

- **R-a** one role per (call, helper), with the right widths;
- **R-b** capacity, disjoint and prefix-filled slices;
- **R-c** idle recount and global profile;
- **R-d** every role strictly inside a window rebuilt from GLOBAL-TEMPLATE events;
- **R-e** families: owner·896 + (2·pair + side)·112 + port, never the caller's active pair, one
  helper per family per call;
- **R-f** PR2322 private namespace: physical 66714 = W + 400 + 8 + 2, with 44 zero buffers inside
  the reserve;
- **R-g** X2 pending-axis disjointness and 3,175 73-column charts.

It rejects 16 mutations and accepts PR2269's own fill as a positive control. `price80.py` brackets
the root of the recounted profile at width 1e-40:

- native: [0.0016865432362690642682667899981505185179, …180];
- conservative (+32·m·N·m^a/(10^16·W)): [0.0016865432334377487154646916218346533773, …774].

Its 12 controls reject this fill at PR2269's b and at PR2322's κ. `check_fill.py` is a second,
build-side legality check that reuses the vendored iteration-3 checker in `vendor/iter3/`.

## Reproduce

From the repository root (CPython ≥ 3.10, standard library only):

```sh
python3 -I -B research/t74-80alias-owner-fill/run_all.py --fetch   # ~25 s
python3 -I -B research/t74-80alias-owner-fill/ceiling_lp.py        # ~7 s
```

`--fetch` fetches `refs/pull/2269/head` (b479fc55) and `refs/pull/2322/head` (002304ef) from the
canonical repository if they are absent. The PR2339 words (commit bf1742ae) are read from git when
present. Otherwise they come from the byte-identical copies in `inputs/`, which are blob- and
sha256-pinned in `inputs/SOURCES.json` and in `fill_check80.py`.

Expected final lines:
`PASS_T74_80ALIAS_RUN_ALL roles=266400 physical=66714 buffers=44/400 native=[0.0016865432362690642682667899981505185179,…] … below_2269=1 below_2322=1 cap_fraction=9.6486464E-1`
and `PASS_T74_WIDTH_AWARE_CEILING`.

To rebuild the fill (optional, about 230 s): `python3 -I -B research/t74-80alias-owner-fill/build_fill.py --out-dir /tmp/o80`.
The receipts record the content sha256 `c45585b9…`.

Environment. All results were run on CPython 3.14.4 (Linux x86_64), with a 3.10 grammar check. The
registered replay pins Python 3.12, which was not available here. `scripts/research_package.py
--check-only` passes; the 3.12 replay itself was not run locally.

## Scope and limits

This is a finite fill plus a scoped ceiling. Neither is a κ claim, and the ceiling is not an
impossibility theorem for the low-alias idea. The ceiling covers the fixed PR2339 words, unsplit
helpers and the unchanged PR2269 bin stock and template. It drops time windows, families and ports,
so it is a relaxation and valid for every legal fill. It says nothing about:

- a different subset of aliases;
- a changed parent bin inventory;
- split helper reservations;
- a changed local contract.

The fill was checked only for owner/hosting legality and priced only by rank profile. The following
remain open, and would be needed only if the fill were to be used:

- native lowering, in both orientations, of the 64 anticipatory initial corrections and 37 new warps;
- lender lifetimes and X-field ownership in the whole-call map;
- physical lowering of the 44 buffers, prefix bits and invoice;
- the PLAN/SPEC refreeze for 400 helpers;
- the outer ledger.

Because the fill already loses to PR2269, closing them cannot help.

## Open next questions

- **Partial low subsets.** Can k of the 32 low lenders (0 < k < 32) keep their width-9 helpers in
  remainder-free [4,9,9,9] / [5,9,9,9] / [7,9] patterns while still saving local mass? First step:
  rebuild the k-low words with PR2339 `build_ext.py`, recount profiles, and screen each with
  `ceiling_lp.certify()`. Per-subset profiles are not determined by mass alone.
- **Changed bin stock.** Could a T74 variant whose child ranks absorb width 9 without remainders
  turn the mass saving into a gain? First step: parametrise `NB` in `ceiling_lp.py`. A real template
  change needs its own schedule and outer.
- **Split reservations.** Is splitting a width-9 lender across two bins legal under the hosting
  rules? It is the only packing-side escape for this inventory, and it needs a new lemma, not
  computation.

## Credits and licence

- PR2339 (Sagar Thakrar, this author): the 80-alias words.
- PR2269 (Jeremy Kothe): the T74 borrow43 template, dispatch and fill format.
- PR2322 (Vlado Vojdanovski): the private-namespace rule and the reference profile.
- PR2312 and PR2302 (jeremykothe2).
- PR2226 (Cinna Davis / 1337isnot1337): anticipatory dirty borrowing.
- PR1319 and PR1297: the T74 lineage (Rohan Arun et al.).
- The merged `complex-local-word-ceiling` cap model (Douglas Colkitt).
- PR2360 (Jeremy Diviney): concurrent independent ceiling; its `DUAL.json` is copied byte-for-byte
  into `inputs/PR2360-DUAL.json`.
- PR1129 (Ali Romman): the pattern-dual method.
- PR2374, PR2349 and PR2363 (jeremykothe2, mason-hale): the current owner-fill line on PR2322's words,
  cited only as reference points.

`vendor/iter3/` holds verbatim copies of our iteration-3 checkers (PR2315, commit 4a2f20ea). This
package was prepared with substantial AI assistance (Claude Code, Anthropic, Claude Opus 5.5). An AI
subagent reviewed the fill checker; no independent human review is claimed. Apache-2.0.
