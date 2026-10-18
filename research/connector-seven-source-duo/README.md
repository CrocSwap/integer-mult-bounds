# Seven-source universal connector word in the singleton+DUO alphabet

**Recursive-interface construction with full priced batch bill; no new kappa.**
In the prefix-walk model of
[`research/universal-connector-boundary`](../universal-connector-boundary/README.md)
(Ross Richardson, CrocSwap/integer-mult-bounds#943 / CrocSwap/integer-mult-bounds#934
lineage) extended by exactly the charged pair-source DUO family of
[`research/duo-toggle-connector`](../duo-toggle-connector/README.md)
(`DUO_{j,k}: z += B_j x_j + B_k x_k`, one dispatch, two source adds, sources
read-only, everything else unchanged), the **seven-source universal source word
has length k = 22 calls at W = 24 toggle-adds**:

```text
steps  64 32 8 20 64 32 1 16 64 2 4 64 1 4 34 8 16 1 4 32 1 16
       (weight-2 steps: 20 = B_2 + B_4 and 34 = B_1 + B_5; all others singleton)
k = 22, d = 2, W = 22 + 2 = 24
```

The closed walk restores `z` (every label count is even: 4, 2, 4, 2, 4, 4, 4),
its prefix set covers all 128 masks of `F2^7` as pairwise prefix XORs, and an
independent dual test (`m` covered iff some prefix `p` has `p xor m` a prefix)
agrees. This is a strict Pareto improvement on the merged singleton upper bound
`f(7) <= 24` in [`research/universal-connector-six-source`](../universal-connector-six-source/README.md)
(a 24-call Gray word at 24 adds): the all-127-row batch runs **276 root queries
at 278 toggle-adds instead of 278 at 278**. In the price model
`c_B = o + p`, `c_DUO = o + 2p`, `c_A = o + p` the batch totals are `276o + 278p`
against `278o + 278p`: **strictly better for every `o > 0`, with total adds
unchanged** (saving exactly `2o`). Nothing is free: the two DUO calls pay two
source adds and one dispatch each, exactly as in `research/duo-toggle-connector`.

```sh
python3 -I -B research/connector-seven-source-duo/verify.py
```

Expected: `PASS_SEVEN_SOURCE_DUO k=22 W=24 queries=276 adds=278 universal=128/128 controls=945+gray+side+mutations`.
Python 3.10+ and the standard library suffice. [CERTIFICATE.json](CERTIFICATE.json)
holds both literal words, the label counts, the batch bill and the control
records. [search.py](search.py) and [walk_search.py](walk_search.py) are the
seeded search tools that produced the words (seed 20261015; the headline word
was the first hit of the `(k, d) = (22, 2)` target).

## Model and reduction (unchanged from the predecessors)

The frozen interface allows only complete calls `B_j: z += B_j x_j` and
`A_i: y_i += A_i z` and their charged DUO combination on arbitrary dirty
length-L F2 arrays; no copies, extra connectors, frame changes or combined
A-calls. Project a word onto its source calls and let `q_t` be the XOR of the
first `t` steps (`q_0 = 0`). Restoration forces `q_k = 0` and every label count
even. Two `A_i` readouts at boundaries `s, t` realize exactly the row
`q_s xor q_t`, so the word is universal iff `D(w) = {q_s xor q_t} = F2^7`. A
weight-2 step is one charged DUO call, so `W = k + d` for `d` weight-2 steps.

## Bill, and what is and is not claimed

For the frozen all-127-row batch every row needs two paired readouts, so the
schedule costs `k + 254` root queries and `W + 254` toggle-adds:

| Schedule | Root queries | Toggle-adds | Source calls | Readouts |
|---|---:|---:|---:|---:|
| Singleton Gray word (`research/universal-connector-six-source`) | 278 | 278 | 24 | 254 |
| This package, DUO word | **276** | **278** | 22 | 254 |

A second word of 21 calls at 26 adds (`k = 21, d = 5`) is recorded in
CERTIFICATE.json as search evidence. It is incomparable with `(22,24)`: it
trades two extra adds for one fewer query, and is cheaper when `o > 2p`. Neither
word is proved Pareto-optimal over all legal words. The search's best coverages at `(20,2) = 122/128`,
`(20,4) = 124/128`, `(20,6) = 126/128`, `(21,3) = 127/128` are bounded search
failures, not exclusions: no word of length 20 or 21 with `W <= 24` is ruled out.

**Not checked / not claimed:** no physical supplier instance of the connector
interface exists (the predecessors' limitation, unchanged); no compiler/tape
integration, frames, owner admission, precision or outer analytic obligations;
no proof assistant; no claim that `k = 22` or `W = 24` is minimal at `n = 7`;
no claim about the singleton `f(7)` (the gap `18 <= f(7) <= 24` is untouched by
this two-call alphabet change); no kappa, certificate or selected-frontier
change. The DUO saving is `2o`; with `o = 0` there is no gain over the Gray word.

## Verification, controls and failure modes

`verify.py` is a deterministic replay (it does not rerun the search):

1. the five-source DUO witness of `research/duo-toggle-connector` replays closed
   and universal with its recorded prefixes (smallest falsifying-instance control);
2. the 945 canonical five-source singleton words are re-enumerated and the
   complete `|D(w)|` histogram `{16:42, 19:120, 21:180, 22:56, 23:45, 24:220,
   26:110, 28:150, 31:22}` reproduces the merged 945-pairing table exactly, and
   the merged example word covers 31 of 32 masks;
3. the Gray construction covers `F2^n` for `n = 4..7`, and the merged six-source
   Gray literal covers all 64 masks of `F2^6`;
4. both words replay exactly: closure, per-label parity, step weights in `{1,2}`,
   all 128 pairwise masks, and the dual coverage test;
5. the complete batch bill and its `o + p` tariff comparison are asserted;
6. three mutation controls (deleted call, DUO shrunk to a singleton, retargeted
   call) must each be detected;
7. a SHA-256 digest pins the two words inside the certificate.

## Scope status

**Changed**, recorded per the card's own scope-change trigger: the card asked for
one added operation family, and DUO is already added and priced by
`research/duo-toggle-connector` and open PRs
https://github.com/CrocSwap/integer-mult-bounds/pull/2128 and
https://github.com/CrocSwap/integer-mult-bounds/pull/2156 (six sources entirely
closed). This package keeps the alphabet and raises the source count to seven,
the first boundary where the universal word is superlinear and the only one
where the merged baseline (`f(7) <= 24`) was heuristic beyond 22 calls. The
card's acceptance question — does the one added operation family offer a
favorable *completed* budget — is therefore answered at its next unsaturated
boundary: yes, `2o` on the full all-127-row batch.

Task card: [notes/agent-52-seven-source-duo-task-card.md](../../notes/agent-52-seven-source-duo-task-card.md);
chooser OS seed `4e177efb421addcdb3ba4ff20efdaefd`, track `recursive-interfaces`,
base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Overlap: find_overlap terms
'seven-source DUO', 'seven source', 'f(7)', 'additive basis', 'difference cover'
on a fresh complete remote snapshot (2026-10-15T06:47Z, 577 open PRs / 1103
discussion records) found no seven-source full-coverage (128-mask) claim in any
alphabet. Discussion https://github.com/CrocSwap/integer-mult-bounds/discussions/2221
and PR https://github.com/CrocSwap/integer-mult-bounds/pull/2236 treat a
different object: the 63 weight-1/2/3 masks at seven sources with 14/18 singleton
events. No matches is not a novelty certificate.

## Open next questions

- **Is `(22, 24)` the Pareto profile at `n = 7` in the combined alphabet?** It
  matters because the DUO call count would then settle the first superlinear
  boundary. First step: a complete `(k, d) = (20, 4)` and `(21, 3)` census or a
  counting lower bound on `(k, W)` pairs. Blocked by: the word space is
  `~20^22` before symmetry, and no exclusion technique beyond the parity bound
  `d = k mod 2` is known here.
- **Does a real supplier boundary admit the DUO call at `o > 0`?** Inherited
  unchanged from `research/duo-toggle-connector`: the whole saving is `2o`.
  First step: instantiate one DUO call in the predecessor's dense-bit-matrix
  leaf and price its entry/exit frame against two singleton calls. Blocked by:
  no physical instance of the connector interface exists in the selected
  supplier.
- **Does the singleton `f(7)` itself drop below 24?** The merged gap is
  `18 <= f(7) <= 24`. This package's words are not singleton words. First step:
  target the `(22, 0)` or `(21, 1)`... (`d = 0` singleton) coverage hill-climb
  with the retained tools. Blocked by: the same search-failure ceiling the
  merged package recorded (126/128 at length 22).

## Credit

Contributor: **Aaron Wang**, with help from opencode (substantial AI assistance).
Model, reduction and the five-source boundary: Ross Richardson
(CrocSwap/integer-mult-bounds#943, #934). Six-source singleton value `f(6) = 16`
and the `n = 7` bounds: Douglas Colkitt (CrocSwap/integer-mult-bounds#1185) with
Hanson Sun's independent verification (CrocSwap/integer-mult-bounds#1215),
merged in `research/universal-connector-six-source`. DUO alphabet, its five-source
Pareto profile and pricing: `research/duo-toggle-connector`
(CrocSwap/integer-mult-bounds#1403 lineage). Six-source DUO word `(14, 16)` and
batch: Aaron Wang/Navinor with opencode,
https://github.com/CrocSwap/integer-mult-bounds/pull/2128. Six-source DUO batch
optimality certificate and the basis value `r[(C2)^6] = 14` (Volodymyr Gavrylkiv,
JIS 20 (2017), Table 3): https://github.com/CrocSwap/integer-mult-bounds/pull/2156.
New work in this package is Apache-2.0; no third-party code is vendored.
