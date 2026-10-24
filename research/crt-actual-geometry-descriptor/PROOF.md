# Exact scope and completeness argument

Fix only the `Layout` constructed by the pinned PR4174 `production_census`: `d=65536`, widths `w_i=24-(i mod 2)`, `ell=24`, `p=6 sum_i w_i`. Thus `L=1540096`, `G=3072`, `K=196608`, `r_max=5`, and `H=15360`. All following quantifiers range over this layout, not arbitrary admissible layouts.

## 1. Every split active axis is reached

The source allocator partitions each level into two regions. At nonroot level `l`, region `s` starts at `a=s d/2`, has length `d/2`, and emits the right half of each block of `w=2^l` axes. An eligible axis `i` has zero-based stream rank

```text
r = floor((i-a)/w) (w/2) + (i mod w) - w/2.
```

At root level 16, region `s` starts at `a=d/2+s d/4`, emits all `d/4` consecutive axes, and `r=i-a`. In both cases the unique batch containing `i` has index `floor(r/5)`. Its members are precisely the source stream positions `[5 floor(r/5), min(5 floor(r/5)+5,d/4))`. The verifier uses these rank formulas to select the batch and independently reads that bounded slice from the actual source `_regions` stream.

For fixed level and partition, `_make_plan` chooses its reservoir and three source blocks independently of active-axis membership and batch index. The destinations are always `[0,H)`, `[H,2H)`, `[L-H,L)`. All six intervals are disjoint. A split axis is exactly an original axis with a strict interior exchange endpoint. Endpoints at axis boundaries cause no split. Because every source block lies inside a reservoir consisting of complete axes, and every active axis lies outside that reservoir, no source-block endpoint splits an active axis. Thus only destination endpoints need possibly qualify; the verifier nonetheless enumerates every distinct endpoint of all six blocks.

The original axis intervals are disjoint and cover `[0,L)`. Write `P(n)=47 floor(n/2)+24(n mod 2)`. Axis `i` is `[L-P(i+1), L-P(i))`, independently checked against the owning `Layout.axis_interval` for every axis. Each nonboundary cut belongs to exactly one such axis. The verifier locates it with the source prefix index, checks strict containment using this independent formula, checks region eligibility, and obtains its unique batch by the preceding rank formula. Iterating all 16 levels, both partitions and all exchange endpoints therefore covers every active split-axis target possibility. There are exactly 26 eligible tuples, with axes `653`, `64228`, `64882`; no arbitrary batch sampling is used. The source allocation census of 104864 plans need not run.

## 2. The target-bit superset contains every actual synchronized layer

At any synchronized Beneš layer, an active axis contributes at most one of its own bits. Allowing *all* its local bits and pairing each with *all* local bits of every other axis in the same batch is a superset of every possible synchronized layer, including padded identity operations. Two targets on the same axis cannot belong to such a layer. Filtering to full guards or requiring exactly two members in a color can only shrink this superset.

The actual three exchanges preserve order inside each exchanged block. For each original axis interval, split at all interior endpoints and translate each piece by the exchange containing it. The verifier's independent implementation applies the exchanges sequentially; it agrees with both `Plan.map_interval` and every literal `Plan.map_position` on the bounded candidate axes. Six-block disjointness ensures a translated piece enters no later exchange.

If a moved target has front-origin physical position `v`, its arithmetic index in the current `y` field is `j=L-H-1-v`. Source omission of all reservoir fields places every active target in `[2H,L-H)`, as proved by PR4174. Therefore for two targets `j-j'=v'-v`, and CRT.md's equal-color rule `j mod K = j' mod K` is equivalent to `|v-v'|` being a positive multiple of `K`. The constant reversal and offset do not affect equality of colors. Distinct original axes remain disjoint under the exchange permutation, so distance zero is impossible.

## 3. Exact distance certificate

For half-open integer image intervals `A=[a,b)` and `C=[c,d)`, the signed difference set is exactly the inclusive integer interval `[a-d+1,b-c-1]`: its endpoints are attained, and all intermediate integers are attained. Intersect this interval and its negation with the positive integers to obtain every possible positive absolute difference. Take the union across all fragment pairs and all other same-batch active axes. Merge overlapping or adjacent intervals without filling any gap.

For each candidate, `RESULT.json` records the resulting exact union. An inclusive interval `[u,v]`, `u>=1`, contains a positive multiple of `K` if and only if `K ceil(u/K)<=v`. Every interval in all 26 rows fails this condition. This is exact integer arithmetic, not a rounding estimate, histogram or sample. A second calculation iterates the small pairs of source-axis bits through actual `Plan.map_position` and checks equality with the entire recorded union. Positive controls include a multiple at either interval endpoint and period 1; the detector would accept a pair if one existed.

It follows that no two bits in different same-batch axes, with at least one axis split by an exchange cut, share a color in this fixed layout. In particular, no real full-guard exactly-two-target color subbatch of the requested kind exists. Checking guard lengths is unnecessary for this rejection; omitting the guard filter enlarges the tested set and strengthens this particular negative conclusion.

## 4. Consequence and limit

A correct frontend cannot construct PR4990's two ordered same-color guards for the nonexistent requested caller. Stop before implementing descriptors or inventing target positions. This does not reject PR4990's valid supplied-unary interface, assert a flaw in PR4100's coloring algorithm, or prove an all-layout obstruction. Each target may legitimately be processed in a singleton color; other layouts or batches without a split axis are outside this certificate. A changed caller witness must precede further frontend implementation. Complete costs and the selected frontier remain unchanged.
