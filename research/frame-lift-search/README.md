# Frame-only search is exhausted on the selected complex providers

Rohan Guliani (@Rohansguliani). Prepared with substantial AI assistance (an AI coding agent wrote the search code
and ran the experiments under the author's direction). Apache-2.0.

## Current selected word (#741, eight B-frame coalescences after SW4)

The exact frame solver was given PR699's SW4 word (`d232183f…`, the input of #741's `FRAME-RECIPE.json`). Using the
admissible model (hpe cone caps from the audit's pre-check, tail frames fixed), it returned in 27 s with CP-SAT
`OPTIMAL` and the profile `{1:2556,2:334,3:430,4:194,5:56,8:8}`. That is **exactly #741's profile**: the search
rediscovers the merged improvement automatically and certifies that it is complete. `check_sw4.py` applies #741's
recipe, reproduces its pinned output hash `e7804702…` and solves the frame LP on both words:

| word | linear weight | LP optimum | exact-root weight (a* = #741 complex root) | LP optimum |
|---|---:|---:|---:|---:|
| PR699 SW4 input | 18162.854792 | 18155.950422 | 18226.598582 | 18219.665540 |
| #741 (selected) | 18155.950422050 | 18155.950422051 | 18219.665539989 | 18219.665539988 |

So **no frame-only change of the selected SW4 word can raise κ**. Six commuting-reorder restarts on the #741 word,
each re-solved by the LP, gave 18155.950422 (twice) or higher (up to +5.36); see [ORDER-SEARCH.json](ORDER-SEARCH.json). The frame slack left by PR699 (6.90 linear and
6.93 exact-root units) is exactly what #741's eight frames recovered. The receipt is [RESULT-SW4.json](RESULT-SW4.json).

## Earlier selected words (#626)

**Result (negative, scoped).** For the two complex provider words of the selected #626 construction
(`jp8` and `ck`, content hashes pinned in
[`complex-k492-owner-repair/data/SPEC.json`](../complex-k492-owner-repair/data/SPEC.json)), the paid local profile
is **exactly optimal over every frame assignment of the fixed gate sequence**, for the first-order recurrence
weight. No frame regroup, coalescence, promotion or demotion recipe of any size can improve κ on these words. The
same holds for the exact root-moment criterion at the selected complex root (see Limits). Two
independent solvers agree: a local-polytope LP (HiGHS) whose optimum equals the input weight to `1e-9`, and an
integer CP-SAT model reporting `OPTIMAL` with the same value. Annealing over commuting gate orders, followed by an
exact frame re-solve, did not beat the input either.

The search space is a relaxation of the native audit, so the negative result covers every audit-admissible frame
change of these two words. It does not cover changes to the scalar program, the helper count, gate scheduling
across non-commuting gates, or the bit supplier.

## Why frames, and what the model is

The complex side binds the selected κ (`complex_lower = 0.0016382067`, `bit_lower = 0.0016538270`). It is priced
by the root moment `Σ_r (r·n_r/(m·W))·(m/r)^a = 1` with `m = 73` and `W = 7168`. The 64 jp8 calls contribute
160,768 of the 181,659 rank-1 children. Rank-1 children are 34.9% of the rank mass, and they carry about half of
the moment's logarithmic weight. The children of a provider word are exactly the **frame climbs** of
`hpe_audit_and_transport.py::climb`. Every A/B/tail gate moves both of its registers to the gate frame, which must
contain their current frames. The scalar program never depends on the frames. The rank mass per word is fixed by
the widths, so only the partition of climbs into sizes can change. The figure of merit is
`Σ_climbs W(d)` with `W(d) = d·ln(48/d)`: the linearisation of the moment relative to rank-48 idle filler. That
filler is what freed rank mass becomes.

In `frame_lift.py`, every gate frame `X_g` is a variable (a subspace of F₂⁹, stored as a 512-bit membership mask).
The constraints are:

- `X_g ⊆ X_next` along every register's chain;
- start frames (ports, `start_extra`) as lower anchors;
- **equality** with the centre frame or target level at the cut (no climb is allowed there);
- terminal frames (`FULL`, `perp(port)`, `helper_final`) as upper anchors.

All constraints are of the form `X ⊆ Y` or `X ⊆ const`. Feasible assignments are therefore closed under
intersection and sum, and they lie between a least solution (forward spans, `least.py`) and a greatest solution
(backward intersections). Each gate's domain is the finite set of subspaces in `[least_g, greatest_g]`:

| word | gates | domain size 1 | 2 | 5 | 16 |
|---|---:|---:|---:|---:|---:|
| jp8 | 4471 | 3133 | 1132 | 178 | 28 |
| ck | 4507 | 3581 | 720 | 178 | 28 |

The model omits the hpe cone caps, the cold_end allowlist conditions and the fixed tail frames, so it relaxes the
audit. Its optimum is therefore a lower bound for every admissible frame-only change.

## Numbers

| word | input chain weight | LP optimum | CP-SAT | greatest lift (all frames raised) |
|---|---:|---:|---:|---|
| jp8 | 18475.029780700 | 18475.029780701 | OPTIMAL, same value | worse: 19175.44, profile `{1:2953,2:588,3:237,4:116,5:78,8:8}` |
| ck | 18568.580702034 | 18568.580702035 | OPTIMAL, same value | worse: 19088.29, profile `{1:2965,2:592,3:237,4:100,5:78,8:8}` |

The excluded centre-descent and target-level terms are fixed: 114.67 for both words. In the input words, most
gates already sit at their least feasible frame: the dataflow span of their operands. The prior coalescence
stages placed the remainder exactly at the optimum. The opposite policy, lifting every register as early as
possible, merges some climbs but splits more, and it costs +3.8% (jp8).

**Commuting reorders.** `order_search.py` anneals over moves of A/B gates inside their commutation windows. It
uses the commutation rule of `build_gate_moves.py`. Each order is priced by its least-frame lift, and the result
is then re-solved exactly for frames. The least-frame proxy reports gains of 7–45 weight units. Across 11
restarts on jp8 and ck ([ORDER-SEARCH.json](ORDER-SEARCH.json): seeds, temperatures 0–1.5, 6,000–8,000 steps),
the exact re-solve returned to the input optimum (jp8 18475.0298, ck 18568.5807) or landed above it (worst:
+10.04 for ck). The proxy's gains come from dropping deliberate coalescences, which the exact solver restores. On
the #571 prefix word, the same pipeline also returns exactly the input profile. Random reorders are only a sample,
so this is not a proof for all orders.

## What this says about κ > 0.01

By Jensen's inequality, with the current deficit (2560 of `m·W = 523264`, so `p = 0.99511`), the complex
exponent obeys `a ≤ −ln p / E_mass[ln(m/r)]`. The selected profile has `E_mass[ln(73/r)] = 2.992`: a mass-weighted
geometric-mean child rank of 3.66, and a cap of 0.0016391, which is essentially the achieved 0.0016382.
Reaching `a ≥ 0.01` at this deficit needs a geometric-mean child rank of **at least 44.7**. At the current child
ranks it needs a deficit of **at least 15,425** (6.0×). The bit side would also need a matching improvement.
Frame bookkeeping cannot supply either: the rank mass is fixed by the widths, and the analysis above shows the
partition into climbs is already optimal. Progress toward κ > 0.01 needs new scalar structure: fewer helper climbs
from a different decomposition, or a larger deficit. In jp8, unit climbs of helpers are the dominant term (about
1,700 of 2,512 rank-1 climbs, 726 of them in section A).

## Reproduce

```sh
# 1. Rebuild the provider words (or reuse the 'complex' directory of `make frontier626-verify`).
python3 -B research/complex-k492-owner-repair/verify.py --work /tmp/k492/complex --jobs 4 \
  $(for n in multicold structural_gain larger_gain joint_prefix frame_coalescing direct_delivery; do \
    echo --source $n=$PWD/research/complex-k492-owner-repair/vendor/$n; done)
# 2. Hash-pinned frame-only optimality check (numpy/scipy only).
python3 -B research/frame-lift-search/check.py --work /tmp/k492/complex --out /tmp/FRAME-LIFT.json
# Optional: CP-SAT cross-check (needs `pip install ortools`) and the order search.
python3 research/frame-lift-search/frame_exact.py /tmp/k492/complex/jp8-step6-cold_end/FULL-WORD.json.gz
# Current selected word: PR699 SW4 input (e.g. <work>/sw4/sw4/FULL-WORD.json.gz from complex-sw4-frame8/verify.sh)
python3 -B research/frame-lift-search/check_sw4.py --input SW4-FULL-WORD.json.gz --out /tmp/FRAME-LIFT-SW4.json
python3 research/frame-lift-search/frame_exact.py SW4-FULL-WORD.json.gz --caps --recipe /tmp/recipe.json
python3 research/frame-lift-search/order_search.py WORD.json.gz ORDER.json --steps 8000 --seed 1
python3 research/frame-lift-search/order_to_word.py WORD.json.gz ORDER.json REORDERED.json.gz
python3 research/frame-lift-search/eval_lp.py REORDERED.json.gz
```

`RESULT.json` is the receipt from running `check.py` on a fresh rebuild of the package (`verify.py`, Linux,
Python 3.13). It records the hashes, profiles, domain sizes, LP sizes, both objectives and the greatest-lift
profile.

## Limits

- Each word's rank mass is fixed by its widths. So at the selected complex root `a*`, a profile change raises the
  root iff it lowers `Σ_climbs d·(73/d)^a*`. `check.py` solves the LP for this exact-root weight as well as for
  the linearisation, and both are optimal at the input (jp8 18538.644391, ck 18633.088537 after the `1/a*`
  rescaling). The criterion holds hosting and idle remainders fixed. These are unchanged because the widths are
  unchanged.
- The LP is solved in floating point (HiGHS). It is a strong numerical cross-check, not an exact rational dual
  certificate. CP-SAT's `OPTIMAL` status is a solver claim without a proof log.
- The scope is a fixed gate sequence for the LP/CP-SAT result, and sampled commuting reorders for the annealing
  result. The scalar program, helper count, dispatch, hosting and bit supplier are out of scope.
- The check reuses the package's provider words. It does not add new admission, phase or global checks, because
  no word is changed.
