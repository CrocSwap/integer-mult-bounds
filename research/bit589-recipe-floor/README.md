# Nine-stage stage recipes cannot improve PR #589's idle hosting

**Status: scoped negative result (bit supplier). No new κ.**

The question is whether any nine-stage stage recipe can improve PR #589's idle hosting. The domain searched is every
recipe with four exchanged pairs, one rank-1 local per stage and at most one ±1 bridge per gap: 2,070,720 valid
recipes, 1,064 distinct idle-window structures. **None raises PR #589's bit c.** The template recipe attains the
maximum, tied by seven other structures that leave the identical remainder. The width-8 hosting wall `R ≤ 4v = 444`
holds for every recipe in the class.

The selected #1094 assembly is complex-bound: complex b is 0.0016755 and bit c is 0.0017334. No bit-side result
changes κ (0.001672660197076918).

## Question and predecessors

PR #589's nine-stage bit c is fixed by two inputs. The first is the word's local paid profile, which PR #886 and #933
showed is locally optimal. The second is the **idle remainder** `{2:435, 4:444, 6:444, 7:666, 42:9}` per replica that
PR #442 hosting leaves behind.

- **Fixed windows (bit589-width-packing).** The merged `research/bit589-width-packing` (Sagar Thakrar) proved that,
  with the template's idle windows held fixed, no width-8 re-hosting improves c. It identified helper width 7 as the
  lever.
- **Geometric audit (#1307).** Open #1307 (commdata2338) audits the geometric disjointness of the same hosting.
- **This note: vary the windows.** Here the windows themselves vary. They are produced by the *stage recipe*
  (`recipe(K)` in `global_k.py`, PR #463/#510 lineage). Per data-coordinate copy, the template advances idle pairs
  by Δ = {6,6,4,4,2,2,1,1,1} levels. A Δ-level advance is a rank-7Δ child, which can host ⌊7Δ/8⌋ width-8 residuals
  from the stages it spans.
- **What was open.** Could another valid recipe produce fewer or longer advances, and so more capacity and a
  cheaper remainder?

## Results

| question | answer |
|---|---|
| Fewer locals per exchanged pair? | **No: 2K+1 locals are necessary.** First proved uniformly by open #743 (Johnny Franks; archived report M). `PROOF.md` gives an equivalent formulation whose invariants drive the search's pruning. `floor_check.py` confirms K = 1, 2. At nine stages K ≤ 4, so the deficit `T(2Kv − L·cst)` cannot be raised by a recipe. |
| PR #589 from the recipe alone? | **Exact.** The template recipe, read unchanged from the vendored `global_k.py`, gives windows equal to the frozen official selection index by index. It gives the same remainder and c = `1733427039589844234749/10^24`. |
| Optimistic ceiling: any split of the 27 idle level-steps, pooled residuals, no recipe validity | c ≤ 0.001927 (+11.2%), but only with 4–5 segments such as Δ = 8+8+6+5. |
| The same ceiling with ≥ 9 segments | c ≤ 0.0017515 (+1.04%), which needs advances of 8 levels. |
| Exhaustive K = 4 class | **2,070,720** recipes form **1,064** window structures with 9 / 10 / 11 idle segments (75 / 513 / 476 structures). Σ Δ = 27 and max Δ ≤ 6 throughout. |
| Hosting (count/window programme, 0 banks, paid remainder ≤ 45) | Capacity is `27 − #segments ≤ 18` slots per copy set, at most **3,996** against 3,951 needed. 989 structures fail total capacity, 27 lack capacity at some stage, 2 fail the joint transport or remainder cap, and **46 are hostable**. |
| Best exact c | **PR #589's c exactly**, attained by 8 structures with the same remainder. The other hostable structures sit at four lower values, 0.044% to 0.213% lower. **None is higher.** |

### Why the remainder is pinned

- **Capacity equals Δ − 1.** For 1 ≤ Δ ≤ 8, `⌊7Δ/8⌋ = Δ − 1`. A fully hosted advance therefore leaves exactly
  `8 − Δ`, and capacity per copy set is `Σ(Δ_i − 1) = 27 − #segments`.
- **The template already has the fewest segments.** The smallest segment count in the class grows as 3(K−1): 3, 6
  and 9 for K = 2, 3, 4. The longest advance grows as 2(K−1): 2, 4 and 6. Hence, at K = 4:
  - capacity is at most 18 slots, so `R ≤ 18·2v/9 = 4v` for every recipe;
  - no advance reaches the 7–8 levels that the optimistic layouts need.
- **The same conclusion as with fixed windows.** With 9 segments and Σ Δ = 27, the remainders `8 − Δ` total 45 per
  copy set. The 45 spare slots are best left as whole rank-42 copies, as bit589-width-packing proved for the fixed
  windows.
- **Where a gain must come from instead.** Any further bit gain must come from outside this class:
  - wider gaps (open question 1);
  - other stage counts (eleven stages is already worse for this word: 0.0017110);
  - banks or split residuals (#448/#480, not established);
  - **helper width**, which is bit589-width-packing's lever.

## Method

1. **Scalar model.** The model is the template's own integer replay. A forward local is `side1_p += side0_p`, a
   reverse local is `side0_p −= side1_p`, and a bridge is `diag(A, A⁻ᵀ)`. A recipe is valid iff the product is block
   anti-diagonal, so that a final bridge sequence plus the exchange gives the identity.
   - A Levi before the first local, or after the last, cannot change validity, because it preserves L0 and L1.
   - So the search omits both and, by pair symmetry, puts the first local on pair 0.
2. **Search.** Depth-first search with exact integer ranks.
   - It prunes with `max(μ, K−μ') + max(K−ν, ν') ≤ remaining stages` from `PROOF.md`.
   - Completability of (stage, product) is memoised.
   - Entries are capped at |8|. At K = 3, a cap of 64 gives the identical 28,464 recipes.
3. **Idle children and windows.** Idle children are inserted exactly as `global_k` does: before a local, before a
   bridge, and finally in pair order. Windows follow PR #442 `hosting_core.windows`.
4. **Hosting.** Hosting is an exact integer programme with PR #442's objective.
   - Every residual is hosted (0 banks, as PR #589).
   - A residual of stage s is hosted only in a window spanning s.
   - Every paid remainder is ≤ 45, which keeps halving depth 2 and row 18,355 < 20,161.
   - The template and the best five structures are re-solved with the **vendored official** `hosting_k.solve`
     (`host_all=True, max_remainder=45`). It must give the same objective and the same c.
5. **Price.** The price is the pinned rational moment engine of the selected assembly (sha256 `81cbc864…`), with the
   inherited bad-branch surcharge. The global profile is `288 ×` local + `32 ×` remainder. The rank-mass identity
   `T(2Kv − L·cst) = 10,272` and halving depth 2 are asserted for every structure.

## Reproduce

```sh
python3.12 -m pip install numpy==2.5.4 scipy==1.18.1
python3.12 -B research/bit589-recipe-floor/verify.py --reuse --jobs 2    # registered generic replay, about 2 minutes
python3.12 -B research/bit589-recipe-floor/verify.py --jobs 12           # also reruns the K=4 search, about 25 minutes
python3.12 scripts/research_package.py --package research/bit589-recipe-floor
```

- **`--reuse`** re-prices the committed search `data/search-K4.json`, which is hash-pinned in `EXPECTED.json`.
- **Without `--reuse`**, the search is rerun and must equal the committed file in content.
- **Measured.** `--reuse --jobs 2` takes 24 s through `scripts/research_package.py` (Python 3.12.15). The full run
  takes 26 min 55 s with `--jobs 12` and 165 MB RSS. Both used numpy 2.5.4 and scipy 1.18.1 on Linux x86-64.

Expected last line:

```text
PASS_BIT589_RECIPE_FLOOR floor=2K+1 K3_recipes=28464 K4_recipes=2070720 K4_structures=1064 max_capacity=3996 hostable=46 best_c=1733427039589844234749/1000000000000000000000000 equal=8 above_pr589=0 no_new_kappa (…s)
```

## Controls

- **Positive.** The template recipe composes with the exchange to the identity. Its windows equal the frozen
  `selection9-p111.json` index by index. The own programme, the frozen selection and the official programme agree,
  and the price is PR #589's c exactly.
- **Negative (19).** These all fail as they should:
  - dropping any of the six internal bridges;
  - dropping any of the nine locals;
  - flipping one local's type;
  - removing stage 0 from every window (hosting becomes infeasible).

  The invariants are `(4,0,0,4)` at the identity and `(0,4,4,0)` at the template product.
- **Agreement between implementations.**
  - The numpy and pure-Python floor checks agree (K = 2: 180,092 states at length 5, 12 hits, none shorter).
  - A separate prototype search found the same 2,070,720 recipes and the same 1,064 structures at K = 4.
  - The prototype and package also agree on all 135 K = 3 structures.

## Scope

- **Searched class.** Nine-stage recipes with K = 4, one local per stage, at most one bridge (coefficient ±1) per
  gap, and entries |≤ 8|. Priced with PR #589's word under PR #442 width-8 whole-residual hosting, 32 replicas and
  0 banks.
- **Hosting relaxes geometry.** "Hostable" means admissible in PR #442's count/window programme. Open #1307 shows that
  this does not imply disjoint physical axes. The search is therefore a relaxation, and a stricter geometric check could
  only remove candidates. It cannot weaken the negative result.
- **Not searched.**
  - Gaps with two or more bridges: a K = 3 probe did not finish in 20 minutes.
  - Banks, and cross-copy or split residuals.
  - Other stage counts, words or replica schemes.
  - Locals that are not single-pair rank-1 shears.
  - Width-7 helpers.

  "No better structure" is a statement about this class only.
- **Proof status.** The 2K+1 floor has written proofs here and in #743. The K = 4 result is an exhaustive finite
  enumeration, not a formal proof. Hosting is optimal only within the stated integer programme.
- **κ and inherited assumptions.** κ is unchanged. All inherited bit assumptions remain: mutable-source realization,
  whole-call hosting, all-size compiler, precision and tape, and H1–H5.
- **Files.** Only this directory is added. The selected record, PR #589's package and `upstream/` are unchanged.

## Open next questions

The same three questions, with their fields, are in `TASK.json`.

1. **Wider gaps.**
   - *Question:* can a gap holding several bridges give a K = 4 recipe with fewer than 9 idle segments, or with an
     advance of 7–8 levels?
   - *Why it matters:* it is the only lever left inside this template.
   - *First step:* rerun `recipe_search.py 3 --bridges-per-gap 2` with stronger pruning.
   - *Blocked by:* search cost.
2. **A segment theorem.**
   - *Question:* is "at least 3(K−1) idle segments" a theorem for every bridge recipe?
   - *Why it matters:* it would make `R ≤ 4v` recipe-independent at width 8, at every K.
   - *First step:* generalise the observed 3/6/9 into entry, final and borrowing synchronisation counts.
   - *Blocked by:* a written proof; the rank invariants bound locals, not syncs.
3. **The width-7 interaction.**
   - *Question:* once width-7 helpers exist, which recipe is best?
   - *Why it matters:* 7 divides every 7Δ window, so capacity becomes 27 slots for every recipe.
   - *First step:* re-price `data/search-K4.json` at width 7 under bit589-width-packing's bracket.
   - *Blocked by:* no width-7 bit helper exists yet.

## Provenance

- **Base.** `410026dc5513b87db92ae98571d1d5984c69a983`. The work was started on `8bddbee3`; every pinned input is
  byte-identical on both bases.
- **Assignment and card.** OS-random assignment seed **18** (bit supplier track). Catalogue card `selected-packing`,
  with scope declared `refined` in `TASK.json`.
- **Pins.** All inputs are hash-pinned in `SOURCES.json` and `recipe_lib.py` and checked by `verify.py`:
  - the moment engine and PR #589's `EXPECTED.json`, which match the selected assembly's own input pins;
  - the vendored `global_k.py`, `hosting_k.py` and `hosting_core.py`;
  - the frozen selection.
- **Claim.** [Discussion #1427](https://github.com/CrocSwap/integer-mult-bounds/discussions/1427).
- **Overlap.** `scripts/find_overlap.py --refresh` was run on 2026-10-14 over 785 open PRs and 145 discussions,
  searching recipe, hosting, idle and stage terms. It found no recipe-variation search. The adjacent work is credited:
  bit589-width-packing, #1307, #743, #886 and #933.

## Credit

- **Template and recipe lineage.** Zhihao Chen and eumemic (PR #386/#436), chafreaky (#439/#443), and
  DreamingOfClouds (#463 generalisation, #510 nine-stage chain, #589).
- **Hosting.** DaysSky (PR #442 idle-axis hosting).
- **The word.** eumemic (#543/#555), DreamingOfClouds (#545/#589), and Jacob Sussman (the E8 unit and the borrowing
  chain).
- **The 2K+1 floor.** Archived report M and Johnny Franks (#743).
- **Fixed-window hosting bound.** Sagar Thakrar (bit589-width-packing).
- **Geometric audit.** commdata2338 (open #1307).
- **Paid-profile predecessors.** SethBurkart123 (#886) and #933.

Prepared by Ian Libânio with substantial AI assistance (Claude Opus 5.5, Anthropic, via Claude Code). Apache-2.0.
