# Two-source toggle DUO for the five-source universal connector

**Recursive-interface construction and exact finite exclusion; no new kappa.**
Add exactly one new complete call type to the frozen connector alphabet of
[`research/universal-connector-boundary`](../universal-connector-boundary/README.md)
(Ross Richardson, CrocSwap/integer-mult-bounds#943 / CrocSwap/integer-mult-bounds#934 lineage):

    DUO_{j,k}: z += B_j x_j + B_k x_k     (j != k; one dispatch, sources read-only)

The only changed premise is that package's "no combined queries" rule; every
other hypothesis (complete calls, arbitrary dirty rows, restoration of `z` and
all scratch, paired `A_i` readouts, generic admissible operators) is unchanged,
and the DUO call is charged in full. In the extended alphabet the five-source
universal source word has **unique Pareto profile (k, W) = (10 calls, 12
toggle-adds)**, where `k` counts complete source calls and `W` counts source
adds (each `B_j` add one, each DUO add two). The frozen singleton alphabet
needs (12, 12). For the frozen all-31-row batch this gives **72 root queries at
74 toggle-adds instead of 74 at 74**: the support bound 72, unattainable in the
singleton alphabet, is attained exactly here. In the price model
`c_B = o + p`, `c_DUO = o + 2p`, `c_A = o + p` (per-call overhead `o`, per-add
marginal `p`) the completed batch costs `72o + 74p` against the frozen
`74o + 74p`: **strictly better for every `o > 0`, with total adds unchanged.**

```sh
python3 -B research/duo-toggle-connector/verify.py
```

Expected (Python 3.10+, standard library only, ~6 minutes):

```text
PASS_DUO_TOGGLE_INDEPENDENT s9_sets=7888725 full=0 batch_calls=72
PRICING saving=2 root queries, 0 toggle-adds (2 per-call overheads o)
PASS_DUO_TOGGLE_CONNECTOR queries=72->74 adds=74 pareto=(10,12)
```

[CERTIFICATE.json](CERTIFICATE.json) contains the census counts, histograms,
sorted-record SHA256, explicit witness words, the full 72-call batch word and
the pricing records. `generate.py` regenerates it deterministically
(`--check` compares), `independent.py` re-checks everything by code-disjoint
enumerations.

## Prefix reduction carries over

The predecessor's reduction needs no change. Project a word onto its source
calls and let `q_t` be the source parity vector after `t` calls (`q_0 = 0`). A
DUO call adds one weight-2 vector to `q_t`; a singleton call adds a weight-1
vector. Thus a generic schedule is a **closed walk with steps of weight 1 or
2** (restoration forces `q_k = 0`), `W` is the sum of step weights (= total
source touches), and two `A_i` readouts at boundaries `s, t` realize exactly
the row `q_s XOR q_t`. The available rows are `D(w) = {q_s XOR q_t}`, and `D(w)`
is full coverage exactly when the XOR-closure of the prefix set `P` is `F2^n`.
Necessity is the predecessor's specialization `L = 1`, `A_i = B_j = identity`
with independent dirty bits; sufficiency is placing each output's two readouts
at boundaries achieving its mask. This is why the finite census below decides
the question completely for the searched domain.

## Exact finite result

Counts here are root calls `k` and toggle-adds `W`; `s` = number of distinct
prefixes of a closed walk (`k >= s`).

| Sources | Frozen alphabet (2n lower bound) | DUO alphabet | Witness |
|---|---|---|---|
| 3 (tiny falsifier) | (6, 6) | **(5, 6)**, unique Pareto | steps `1,2,1,4,6`; prefixes `0,1,3,2,6,0` |
| 4 (side row) | (8, 8) | **(6, 8)**, unique Pareto | steps `1,4,9,6,8,2`; prefixes `0,1,5,12,10,2,0` |
| 5 (frozen instance) | (12, 12) | **(10, 12)**, unique Pareto | steps `1,2,8,18,12,16,1,2,4,2`; prefixes `0,1,3,11,25,21,5,4,6,2,0` |

Lower bounds for `n = 5` (both complete, not heuristic):

1. **`k >= 10`.** Full coverage needs `C(s,2) >= 31`, so `s >= 9`, and
   `k >= s`. The complete census of all `s = 9` sets (prune is a monotone
   pair-sum collision count; independently re-scanned by brute-force
   `itertools.combinations`, 7,888,725 sets, zero full covers) shows no
   9-point difference cover of `F2^5` exists. Hence `s >= 10` and `k >= 10`.
2. **`W >= 12`.** Each source is touched an even number of times, so `W` is
   even and `W >= 2n = 10`. `W = 10` leaves only the all-unit `k = 10` words
   (the frozen 945 pairings of the predecessor, reproduced here with maximum
   coverage 31 of 32) or words with `k <= 9`, which need `s <= 9` covers that
   do not exist. So `W >= 12`.

The witness attains (10, 12), so it is the unique Pareto profile: any better
call count or add count contradicts (1) or (2). The five-source census also
finds 99,200 ten-point difference covers (`C(10,2) = 45` pairs, at most 14
collisions), of which 86,400 carry a covering walk with `k <= 10`; the
lexicographic min-walk histogram is (10,12): 8,500, (10,14): 47,600,
(10,16): 26,600, (10,18): 3,700 (sorted-record SHA256 in the certificate).
For `n = 3` the same argument gives `k >= 5`, `W >= 6`; the census is a
complete walk enumeration.

## Priced whole construction

The batch object is the predecessor's frozen instance: five sources, one output
for each of the 31 nonzero masks. Both schedules use 62 paired readouts
(`31 x 2`), so the comparison is exactly the source word.

| Schedule | Root queries | Toggle-adds | Source calls | Readouts |
|---|---:|---:|---:|---:|
| Frozen 12-call word (`research/universal-connector-boundary`) | 74 | 74 | 12 | 62 |
| DUO witness | **72** | **74** | 10 | 62 |

With per-call overhead `o` (dispatch, entry/exit frame, head return,
instruction record) and per-add marginal `p` (coefficient/source access,
arithmetic, target update), the batch totals are `74o + 74p` and `72o + 74p`.
The saving is **exactly `2o`**; it never increases the add count, because the
DUO witness keeps `W = 12`. The DUO call's own complete price is
`c_DUO = o + 2p`: two accumulations in one dispatch, one entry/exit frame, one
head return. In the predecessor's concrete dense-bit-matrix implementation the
same statement reads `c_DUO <= 2 c_B - delta`, where `delta` is one saved
return-to-origin traversal, one instruction-record access and one scalar
initialization, so the batch saves `2 delta` against `62 c_A + 12 c_B`.
Nothing is declared free: the two adds inside a DUO call pay the full
traversal (`4 L^2` coefficient reads, `4 L^2` source reads, `4 L^2` ANDs,
`4 L^2 + L` XORs per target entry, head travel at most `S (8 L^2 + 2 L + 1)`).

Mechanism comparison, credited and distinct: https://github.com/CrocSwap/integer-mult-bounds/pull/1340 and https://github.com/CrocSwap/integer-mult-bounds/pull/1370 (discussion 1352, Arham Tahir) reach ten queries by making source rows **temporarily writable** (four source XORs, mutable-source shear path) and price that mechanism; this package keeps every source read-only and changes the operation instead. https://github.com/CrocSwap/integer-mult-bounds/pull/1185 (f(6) = 16) stays in the unchanged alphabet.

## Verification, controls and not-checked obligations

`verify.py` runs three stages: deterministic regeneration of the certificate,
code-disjoint independent checks, and the pricing assertions. The independent
stage re-derives the `s = 9` exclusion by a brute-force combinations scan (no
pruning), the `n = 3` frontier by a recursive walk DFS, and the 945 control by
restricted-growth words; it replays the emitted 72-call batch word
symbolically and densely at `L = 1, 2, 3` with seeded random noncommuting
matrices and arbitrary dirty connector/output rows (forward and reverse
order), checking connector restoration and all 31 output rows. Four mutation
controls (deleted call, shrunk DUO, misplaced readout, tampered record) must
each be detected. Twelve dense executions are run in total.

**Not checked:** no physical supplier instance of this interface exists (the
predecessor's own limitation, unchanged here); no compiler/tape integration,
frames, owner admission, precision or outer analytic obligations; no proof
assistant; no weighted global optimum beyond this unit/parameter price model;
walks with `k >= 11` are outside the census (they cannot beat (10, 12), which
is already Pareto-minimal); the 99,200-cover histogram is generate.py's claim
with a recorded hash, re-derivable by re-running it, while the headline
witness and both lower bounds are independently re-checked.

## Scope status

Refined, not changed: the card asked for "one additional operation and a small
source count for its first counterexample"; the operation is fixed to the
two-source combined toggle and the domains to 3 sources (tiny falsifier) and
5 sources (the frozen priced instance), with 4 sources recorded as a side row.
The task card is [notes/agent-18-duo-toggle-task-card.md](../../notes/agent-18-duo-toggle-task-card.md);
selector nonce `bf263697e6c72cee43b6ded62be24c62`, track `recursive-interfaces`.
Base commit `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Overlap helper queries
for 'two-source toggle', 'combined query', 'pair toggle', 'difference cover',
'additive basis' and related terms returned zero matches on a fresh complete
remote snapshot (2026-10-14T00:11Z); no matches is not proof of novelty.

## Open next questions

- **Does a real supplier boundary admit the DUO call at `o > 0`?** It matters
  because the whole saving is `2o`: with no per-call overhead there is no
  gain. First step: instantiate the predecessor's leaf implementation for one
  DUO call and measure its entry/exit frame cost against two singleton calls
  in `make frontier1094-verify`'s pricing vocabulary. Blocked by: no physical
  instance of the connector interface exists in the selected supplier.
- **What is the exact Pareto profile at `n = 6`?** It matters because
  https://github.com/CrocSwap/integer-mult-bounds/pull/1185 fixes `f(6) = 16`
  in the singleton alphabet and `C(12,2) = 66 >= 63` allows `s = 12` in
  principle. First step: enumerate `s = 11` and `s = 12` difference covers of
  `F2^6` with the collision prune and search their wt<=2 walkability.
  Blocked by: `C(63,11)` needs the prune to bite before the search is cheap.
- **Can a three-source call or a deferred readout lower `W` below 12 at
  `k = 10`?** It matters because `W = 12` is the frozen add count; lowering it
  would save adds as well as calls. First step: redo this census with steps of
  weight <= 3 and a charged three-source call. Blocked by: none; a bounded
  follow-up.

## Credit and provenance

Predecessor: `research/universal-connector-boundary` (merged
https://github.com/CrocSwap/integer-mult-bounds/pull/943, Ross Richardson),
whose interface, prefix reduction, 945-pairing control and cost
recurrence this package builds on and reproduces as a control. Comparison
credit: Arham Tahir's mutable-source shear mechanism
(https://github.com/CrocSwap/integer-mult-bounds/pull/1340,
https://github.com/CrocSwap/integer-mult-bounds/pull/1370, discussion 1352).
See `SOURCES.json` for exact pins. Prepared by **Navinor** with help from
opencode. Apache-2.0; no frozen source, upstream file or selected record is
changed by this package.
