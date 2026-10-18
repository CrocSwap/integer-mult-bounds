# Which P104 side-correction result applies?

Use this map before starting another `p104-side-correction` attempt. It records which premise each
result fixes, what it excludes, and which premise changes are still untested. It is a navigation
aid, not a review: entries marked *open PR* are author-checked and unreviewed, and discussion
findings are provisional. Recheck the heads below and [live overlap](../../autoresearch.md#1-orient-briefly-then-choose-a-distinct-task)
before relying on an entry. Snapshot: 2026-10-14, 20:25 UTC, canonical main `0fdd7d82`,
priority revision 4.

## Shared object

[PR1972](https://github.com/CrocSwap/integer-mult-bounds/pull/1972) (Rohan Arun, draft, head
`fd82d172`) supplies a 4,058-event P104 channel `Y <- Y + (G/2)X` on 104 root ports. It has
72 arbitrary dirty helpers, which are restored, eight query registers `Q_k`, and eight owned
private-copy lifetimes. [PR1991](https://github.com/CrocSwap/integer-mult-bounds/pull/1991)
(Chafik Boukhalfa, merged, head `6e222517`) is its native Clifford realization in
[research/p104-native-channel](../../research/p104-native-channel/README.md). The local paid
profile is `{1:1074, 2:58, 3:86, 4:104, 5:48, 6:24, 7:8, 8:8}`, rank mass `2368 = 2312`
boundary coverage plus COPY56.

Identity transfer needs the missing `S = I - G/2`. Here `G² = 26G`, so `S` is invertible with
`S⁻¹ = I - G/24` and has rank 104. Every diagonal entry of `S` is zero and every row has 48
off-diagonal entries `±1/2`, 4,992 in total.

## The budget every route must meet

[PR2082](https://github.com/CrocSwap/integer-mult-bounds/pull/2082) and [PR2083](https://github.com/CrocSwap/integer-mult-bounds/pull/2083) price completions under the same explicitly conditional coverage contract:
the paired-chain template with `p = 4, v = 104`, so `s = N = 9`, `m = 73`, `W = 832`, with one
unpaid coordinate per live family and unchanged idle requirements. Capacity is `73 · 832 = 60,736`
and idle coverage is `72 · 832 - 9 · 2312 = 39,096`. If a correction adds `k` paid rank units per
call and earns no new creditable progress, the zero-saving moment is

```text
M(0) = (9 · (2368 + k) + 39096) / 60736
```

The uncorrected channel gives `7551/7592 < 1`. **`M(0) ≤ 1` exactly when `k ≤ 328/9 ≈ 36.4`.**
Since `(r/m)^(1-a) ≥ r/m` for `0 ≤ a < 1`, a correction above that line has no positive saving.
The recorded values are `k = 96: 7659/7592`, `k = 104: 1917/1898` and `k = 208: 7785/7592`, all
above one. [PR2082](https://github.com/CrocSwap/integer-mult-bounds/pull/2082) states the same
328/9 slack. These values are reproduced exactly by the snippet at the end of this note.

Each route covered below is either infeasible (no completion at all) or needs at least 96 added
positive-rank transports per call. Under these premises the side correction is therefore closed,
whatever its scalar cost. A successful route must change at least one premise:
which transports or frame paths exist, or whether added transports earn creditable progress (a
changed coverage interface).

## Results by premise

| Result and status | Premise fixed | Conclusion | Explicitly outside |
| --- | --- | --- | --- |
| [PR2090](https://github.com/CrocSwap/integer-mult-bounds/pull/2090), Adam Gall, open PR, head `dff116ef` | Frozen itinerary; original transports and private lifetimes kept; arbitrary added or replacement **common-frame** linear mixing at all 4,059 cuts | Source-to-target rank at most 8 arrays. At cut 2429 the queries `Q0..Q7` separate every `X` from every `Y`. The original channel attains 8; identity needs 104. | Terminal `+208` correction, new or retimed transports, new storage, non-common-chart operations. The 96 missing directions are not a 96-child native bound. |
| [PR2082](https://github.com/CrocSwap/integer-mult-bounds/pull/2082), David Arias, open PR, head `60f4e337` | Same sharp 8-register cut. Corollary: corrections inserted between original events that restore every frame before the next event, keep the transports and add no storage | At least 96 added positive-rank transports per call; `M(0) ≥ 7659/7592` under the contract above | Persistent changed-frame buffers, retiming, replacement or fusion of transports, new storage, changed coverage |
| [PR2113](https://github.com/CrocSwap/integer-mult-bounds/pull/2113), Jeremy Diviney, open PR, head `fa1a45f9` | **Arbitrary interleaving** of the existing per-register frame paths; all 2,624 original ADDs and 8 COPYs discarded (free scalar resynthesis) | Still rank at most 8 arrays: removing the eight private descents disconnects sources from targets | New frame paths, replacement or fusion of transports, additional storage |
| [PR2127](https://github.com/CrocSwap/integer-mult-bounds/pull/2127), Ross Richardson, open PR, head `befebf0f` | Original transport occurrences kept; **arbitrary source-independent workspace lifetimes** and valid retiming | At least 96 added outward whole-array transports. The 444 frames split 222/222 after removing the eight descents. | Replacement or fusion of original transports, free cross-chart operations, changed coverage. Its README notes that added transports may carry creditable progress, so the `M(0)` comparison is conditional. |
| [PR2083](https://github.com/CrocSwap/integer-mult-bounds/pull/2083), Adam Gall, open PR, head `7231ab97` | **Terminal cut** after the whole channel including query cleanup; canonical common-chart, nested-transport model; arbitrary scalar mixing and full-frame dirty workspace | At least 104 added paid ranks with free owned allocate/copy/discard, 208 without; even 104 gives `M(0) ≥ 1917/1898` | Earlier interleaving, other chart alphabets, changed coverage |
| [PR2089](https://github.com/CrocSwap/integer-mult-bounds/pull/2089), 1337isnot1337, open PR, head `54d4c6f5` ([finding 2092](https://github.com/CrocSwap/integer-mult-bounds/discussions/2092) cites pre-rebase `267d3d05`) | **Construction** at the terminal cut: promote each target to the full frame, add its 48 entries, return | Exact over all 280 input columns; 4,992 ADDs and 208 rank-one transports, profile `{1:1282, ...}`, mass 2,576. Attains [PR2083](https://github.com/CrocSwap/integer-mult-bounds/pull/2083)'s 208 no-allocation floor; its relaxed moment at `a = 1/99` is above one. | Global owner and hosting schedule, source-read delivery, integration with the [PR1940](https://github.com/CrocSwap/integer-mult-bounds/pull/1940) schedule |
| [Discussion 2080](https://github.com/CrocSwap/integer-mult-bounds/discussions/2080), 1337isnot1337, released, fork commit `ea2f3fc4` | Same terminal construction, released as a duplicate of the [PR2089](https://github.com/CrocSwap/integer-mult-bounds/pull/2089) claim | Same 208-transport construction with a terminal path floor; no PR | As [PR2089](https://github.com/CrocSwap/integer-mult-bounds/pull/2089) |
| [Discussion 2107](https://github.com/CrocSwap/integer-mult-bounds/discussions/2107), 1337isnot1337, finding, no public artifact at snapshot | **Pre-query-cleanup cut** (before event 3642): each `Q_k` is its initial dirty value plus a 52-source `X` row | Exact candidate identity: replace the 416-term initial compensation block by `Y_t += α_t Q_live` at the late cut, plus `Y_t += X_t`. The dirty baseline cancels and the scalar change is +104 events instead of 4,992. Still 208 rank-one target transitions, so the budget line above still fails. | Full modified-word and native replay were pending at the snapshot |
| [Discussion 2121](https://github.com/CrocSwap/integer-mult-bounds/discussions/2121), Jose Manuel, active claim to 21:15 UTC, local only | **Changed producer:** 112 source labels `P104 ∪ {a_k}` with pseudo-inputs `z_k = -Q_k/2`; the ordinary E8 side matrix gives `(I - G/2)x + DQ/4` | Exact scalar identity claimed; no frame chronology or invoice yet | Outside all retained-occurrence theorems ([PR2127](https://github.com/CrocSwap/integer-mult-bounds/pull/2127) says so explicitly) |
| [Discussion 2131](https://github.com/CrocSwap/integer-mult-bounds/discussions/2131), active claim to 22:17 UTC, local only | **Original transport occurrences not retained:** up to 104 added arbitrary-dirty width-nine carriers, each with one delivery room and one gather/deliver/cleanup epoch; intermediate frame paths and transports may be replaced and rescheduled | No construction or cost established yet | Outside the retained-occurrence and frozen-path theorems by design |
| [PR2096](https://github.com/CrocSwap/integer-mult-bounds/pull/2096), Adam Gall, open PR, head `f22626f3` | Precision of the **uncorrected** native channel | All-cut coefficients 106 (input-to-prefix), 450 and 668; `u ≤ 2^(-b-17)` suffices | Any corrected word: its combined prefix and defect maps must be recomputed |

## What the negative results share

The four cut results ([PR2082](https://github.com/CrocSwap/integer-mult-bounds/pull/2082), [PR2090](https://github.com/CrocSwap/integer-mult-bounds/pull/2090), [PR2113](https://github.com/CrocSwap/integer-mult-bounds/pull/2113), [PR2127](https://github.com/CrocSwap/integer-mult-bounds/pull/2127)) keep the original eight private descents,
as fixed transport occurrences or fixed frame paths. They then widen what may happen around them,
step by step:

- common-frame mixing ([PR2090](https://github.com/CrocSwap/integer-mult-bounds/pull/2090));
- free scalar resynthesis and interleaving ([PR2113](https://github.com/CrocSwap/integer-mult-bounds/pull/2113));
- added storage and retiming ([PR2127](https://github.com/CrocSwap/integer-mult-bounds/pull/2127)).

None of them replaces or fuses an original transport, adds a new frame path for an existing role,
or uses a cross-chart operation that is not a counted transport. [PR2090](https://github.com/CrocSwap/integer-mult-bounds/pull/2090) and [PR2113](https://github.com/CrocSwap/integer-mult-bounds/pull/2113) prove rank
bounds only. Where a recursive-cost conclusion is drawn ([PR2082](https://github.com/CrocSwap/integer-mult-bounds/pull/2082), [PR2083](https://github.com/CrocSwap/integer-mult-bounds/pull/2083) and [PR2127](https://github.com/CrocSwap/integer-mult-bounds/pull/2127)'s explicitly
conditional comparison), it keeps the retained coverage contract with no credit for added
transports.

The constructions and candidates ([PR2089](https://github.com/CrocSwap/integer-mult-bounds/pull/2089), discussions [2080](https://github.com/CrocSwap/integer-mult-bounds/discussions/2080) and [2107](https://github.com/CrocSwap/integer-mult-bounds/discussions/2107)) all pay 208 rank-one target
transitions, far above the 36-unit line. They differ only in scalar cost and cut.

## Premise changes not yet covered at the snapshot

1. **Replace or fuse original transports**, or give a role a new frame path. [PR2113](https://github.com/CrocSwap/integer-mult-bounds/pull/2113)'s open question
   proposes changing one helper's intermediate frame and then exhibiting a cut bypass with dirty
   restoration. The live attempts in this class are discussion [2121](https://github.com/CrocSwap/integer-mult-bounds/discussions/2121)'s
   changed producer and discussion [2131](https://github.com/CrocSwap/integer-mult-bounds/discussions/2131)'s replaced carriers. Under the
   retained contract, either must still add at most about 36 rank units per call unless it also
   earns creditable progress (item 2).
2. **Creditable progress for added transports.** This means a changed coverage interface in which
   new transports advance endpoints that the idle bill would otherwise pay for. [PR2127](https://github.com/CrocSwap/integer-mult-bounds/pull/2127) shows one
   monotone helper path with productive progress, but no coverage law that credits it. [PR2083](https://github.com/CrocSwap/integer-mult-bounds/pull/2083)'s next
   question names this route.

With the original transports kept, the proved floor is 96 added transports ([PR2082](https://github.com/CrocSwap/integer-mult-bounds/pull/2082), [PR2127](https://github.com/CrocSwap/integer-mult-bounds/pull/2127)) and
the cheapest construction pays 208 ([PR2089](https://github.com/CrocSwap/integer-mult-bounds/pull/2089)). Closing that gap does not matter under the retained
contract, because 96 already exceeds the 36-unit line. Under a changed coverage interface it could
matter again.

Precision ([PR2096](https://github.com/CrocSwap/integer-mult-bounds/pull/2096)), chronological hosting and all-size admission stay open for every route. A
corrected word needs its own combined precision map.

## Reproduce the budget line

From any directory, Python 3.10+:

```python
from fractions import Fraction as F
idle, cap = 72 * 832 - 9 * 2312, 73 * 832          # 39096, 60736
M0 = lambda k: F(9 * (2368 + k) + idle, cap)
assert (M0(96), M0(104), M0(208)) == (F(7659, 7592), F(1917, 1898), F(7785, 7592))
assert M0(0) == F(7551, 7592) and M0(36) <= 1 < M0(37)
print(F(cap - idle - 9 * 2368, 9))                  # 328/9
```

The constants come from the cited PRs, not from a fresh replay of their packages. The contract
itself is conditional; see [PR2082](https://github.com/CrocSwap/integer-mult-bounds/pull/2082) and [PR2083](https://github.com/CrocSwap/integer-mult-bounds/pull/2083) for its sources (Dominik Scholz's paired-chain model,
Sagar Thakrar's [PR1012](https://github.com/CrocSwap/integer-mult-bounds/pull/1012) coverage identity and Douglas Colkitt's [PR1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240) ceiling).

## Credit

Prepared by Aaron Wang / navinor, with help from Claude Code, from the PR bodies and discussion
posts linked above. All results belong to their authors: Rohan Arun, Chafik Boukhalfa, Adam Gall,
David Arias, Jeremy Diviney, Ross Richardson, 1337isnot1337, Jose Manuel and their credited
predecessors. Corrections from the authors are welcome. Apache-2.0.
