# Exact budgets for the cold-host lead

This is a conditional cost certificate for ten specified inventories and paid profiles. It does not construct a restored host, prove a literal owner allocation, or claim a new κ. The baseline is PR2802 at `17b2ee6ef3cf1468e78a6267f0ecbc9a0e6f60dd`; the J-hosting source is `dfbc5ba121d5d23381393f178be8d4ba25ebfa4d`. Copied inputs and the arithmetic engine are authenticated before execution.

Run from any directory with Python 3.12 and no third-party packages:

```sh
python3.12 -B -S /path/to/pricing/verify_budget_certificates.py
```

The default replay writes only to stdout. `run()` returns the same report for the package hook. It checks 20 exact duals, all 1,163 inequalities for each, ten integer pattern invoices and their rational root brackets, source bindings, rank mass, stock, and seven rejecting controls. Floating optimization supplied discovery proposals; neither an optimizer nor its optimality status participates in acceptance.

## What is priced

The baseline has 408 helpers, 72 private buffers, 666 calls, 271,728 owner roles, and physical stock 66,794. Both pinned providers have local profile `{1:2382,2:648,3:268,4:128,5:26,8:8}` and inventory `{4:26,5:2,7:62,8:78,9:240}`. The complete rank mass is 4,816,512. The bin inventory is the retained J-model: `{8:49728,16:33152,32:33152,48:33152}`. This finite pattern model drops chronological, family and window constraints; these are not assumed discharged.

Each nonbaseline case applies one of the following changes `k` times, for `k = 1, 2, 4`:

| Merged width | Inventory change | Local change per hosting | Private buffers |
|---|---|---|---|
| 9 | `(4,8) → 9` | `−H3` | `72−k` (host loses its cold end) |
| 8 | `(4,8) → 8` | `−H3−H2+H1` | 72 |
| 7 | `(4,8) → 7` | `−H3−H2` | 72 |

The width-9 row prices the optimistic `−H3` hosting ledger from J’s relaxation, conditional on that declared profile; the copied inputs do not establish a literal word realizing it. Widths 7 and 8 are ideal restored-host invoices; their algebra and frame feasibility are separate obligations. Physical stock is `66304 + helpers + 8 + buffers + 2`. A full-frame *restored* host would retain 72 buffers instead of the width-9 row's 71; this distinction does not improve its moment.

Every declared change obeys

`sum(rank * local_delta) = sum(width * inventory_delta)`.

Consequently the local and leftover-bin rank changes cancel globally. Appending `H1` while keeping the same inventory would violate this invariant and is rejected. An undo's cost must instead be its **net moment change**, including any compensating jumps, source/frame changes and ownership effects. Two scalar undo gates do not automatically cost two rank-one children.

## Certificate argument

For a tested rational endpoint `b`, set `h_r(b) = (r/73)^(1-b)`, with `h_0=0`. A pattern `(R,p)` places helper widths `p` inside a rank-`R` bin and leaves cost `h_(R−sum(p))`. The certificate gives one free dual coefficient for each bin type and each helper width. Replay checks, exactly, that their sum for every pattern is at most an outward rational **lower bound** on its idle cost. Multiplying by the fixed bin/role counts therefore lower-bounds the cost of every feasible fractional pattern allocation, hence every integer allocation and every literal allocation represented by this model.

The local paid cost is added with outward lower bounds. If this total is greater than 66,304, the endpoint is excluded. All child ranks are below 73, so the moment strictly increases with `b`; an excluded point is an upper bound on the root. The checked upper caps are:

| Case | Exact upper cap on its relaxed complex moment root |
|---|---:|
| Baseline | 0.001717795985 |
| Width 7, one hosting | 0.001718667310 |
| Width 7, two hostings | 0.001719538520 |
| Width 7, four hostings | 0.001720889596 |
| Width 8, one hosting | 0.001718075881 |
| Width 8, two hostings | 0.001718355869 |
| Width 8, four hostings | 0.001718916120 |
| Width 9, one hosting | 0.001717601028 |
| Width 9, two hostings | 0.001717406351 |
| Width 9, four hostings | 0.001716621842 |

The three width-9 caps are below PR2802's exact conditional κ. Thus **batching one, two or four copies of the stated `−H3` profile cannot win**; this does not exclude a simultaneous construction with additional frame savings or a different inventory.

Each sparse integer pattern invoice is independently reconstructed and its moment root enclosed in an interval of width `10^-24`. These pattern invoices need not satisfy owner timing and family rules. In particular, their positive width-7/8 values are optimistic room, not lower bounds on an achievable physical result.

At PR2802's exact κ, dividing remaining moment room by `666*h_1(b)` proves these strict necessary budgets for all additional **net** costs:

- One ideal width-7 hosting: less than **0.017959 H1-equivalent per call**.
- One ideal width-8 hosting: less than **0.005786 H1-equivalent per call**.

These are necessary optimistic budgets. They neither permit an unbalanced extra-child invoice nor establish a realizable restoration. Positive omitted costs only reduce the available room.

## Arithmetic and attribution

`vendor/base_two_moment.py` is copied byte-for-byte from the frozen `research/frame-domain-ceiling/engines/base_two_moment.py`; its retained source map identifies PR551's exact Git blob. The engine uses rational logarithm series and exponential tail bounds, with outward rounding. Its original docstring, the frame-domain package's notice and source map, and the Apache-2.0 license are retained. `SOURCE-PINS.json` records every copied path, commit, Git blob and SHA-256. The retained engine source blob is checked as well as its SHA-256.

PR2802 and the J exploration are Marius-Paul Dumitrean's work with the assistance disclosed in those sources. The underlying construction retains Tekalign/PR2751, DavidAriasC/PR2766, Philippe Van Velzen/PR2679 and PR2559, Jeremy Kothe's owner/native lineage, Mason Hale/PR2696, Cinna Davis/PR2226, and the earlier credited sources. The frame-domain package was prepared for chafreaky with OpenAI Codex assistance. This separate exact-dual pricing and replay was prepared for Marius-Paul Dumitrean with substantial OpenAI Codex assistance; it does not change the frozen predecessor files.
