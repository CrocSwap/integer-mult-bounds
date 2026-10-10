# Target-prefix compression composed with the gen4 retiming, early restorations and dirty entrances

**Conditional κ = 725113717934416422443945/10^27 = 7.25113717934416e-4**, +9.25 × 10⁻⁷ (+0.128 %) over PR280's 7.24189082265949e-4, +2.24 × 10⁻⁶ over PR276.

This package is utcorvusvolat's `gen4-retiming-entrances` (PR280: the 880 common-frame retimings, 440 early helper restorations and 60 transported dirty entrances on the gen4 word, with its exact emitters, native chart/column checkers, fixed-prime pricer and completed-bank admission) with one added stage, `code/target_prefix.py` (frozen `data/target-selection.json`), run after `05-entrances` and before the column, chart, price and admission checks: eumemic's PR268 exact F₂ target-prefix compression, as the native stage of PR273/PR279. On PR280's final word, 280 disjoint target groups (220 squares of four targets with three retained, and 60 pairs created by the transported entrances) have a dependent target whose frame-20 prefix response is the F₂ sum of its retained group-mates'. The dependent's 1,190 frame-20 reads are omitted; it receives `t −= p_j` at the zero frame at the cut and `t += p_j` at the group's common nondegenerate 21-dimensional frame at the close, where all members are moved (1,440 setup/restore additions; 626,610 weighted ADDs). Local paid histogram delta {1: −220, 2: −54, 3: −36, 18: −66, 19: −24, 20: −190, 21: +280} at unchanged rank mass; normalized calls 5,808,240 → 5,789,640, stock 255,841 and deficit 52,800 unchanged. The stage recomputes every member's literal prefix response from the actual word and requires the dependency before emitting anything, rebuilds every MOVE from the actual needs, checks nested chains, fixed endpoints and COPY lifetimes, nondegenerate endpoint bases and both all-column replays with an omitted-setup negative control; PR280's five-stage column checker, chart audit (4,004 projectors), fixed-prime pricer (47 strict constraints, adjacent grid rejected) and completed-bank admission then re-examine the composed word. `code/price.py` pins the new call count and κ; `verify.py` pins the composed word's SHA-256.

Prepared by Rohan Arun with Anthropic Claude assistance; Apache-2.0. Everything below is PR280's own description of the inherited construction.

---

# Gen4 retiming, early restoration and dirty entrances

This package constructs the conditional finite bound

**κ = 724189082265949363570532 / 10^27 = 0.000724189082265949363570532.**

It composes 880 source-pair frame retimings, 440 early helper restorations and 60 transported dirty entrances on the PR276 gen4 word. The signed scalar maps are preserved by the checked commutation identities; all changed geometry, completed banks and finite charges are recomputed on the resulting word.

At the latest comparison during preparation, this is **0.08533948% above PR279** (κ = 0.000723571590007464), and **0.18250242% above PR276** (κ = 0.000722869827347495). PR279 independently posted the same 880 retimings while this package was being prepared. The extra improvement here is the composition with shortened helper endpoints and new dirty entrances. No priority or global optimality is claimed. These are changes to a conditional asymptotic bound, not measured multiplication speedups.

## Reproduce

Python 3.11+, SymPy 1.14.0, a C++17 compiler and Boost headers are required. On Ubuntu:

```sh
sudo apt-get install g++ libboost-dev
python3 -m pip install -r research/gen4-retiming-entrances/requirements.txt
python3 -B research/gen4-retiming-entrances/verify.py --output /tmp/gen4-composed-replay
```

Use a fresh output directory outside this package. The verifier runs without network access. It freshly verifies the unmodified, vendored PR276 package, regenerates its raw word, applies the three exact recipes, checks every global formal column, generates the changed projector charts, enumerates the bank assignments, reproduces the price and admits the complete finite invoice. Saved PASS files are not inputs to this recipe. Its immutable manifest is checked before and after execution. Assertions are mandatory.

PR276 is pinned to commit `d428ab0462b9dfd3131ab4e89999f0adcd6173dd`, with its original manifest SHA256 `6381aa8d881a4a89cf6c40db5bcd705b928a27599540a270bf3cd15f604c705d`. The complete 110-file prerequisite package and original licenses/notices are retained in `vendor/pr276`. Later edits to that PR do not alter this dependency.

## Concrete checks and result

- The final word SHA256 is `71dd08f325566160a01b1c3d8b38450eeb48f478c8f7588065e234d58bddef48`.
- All 23,450 global formal columns pass the five-stage construction, with 120 fresh copies, original-source immutability and six nonzero omitted-bridge controls. The signed changes are separately justified over the integers; the F₂ replay is not used as a substitute for that argument.
- All 3,784 changed connector/endpoint projector charts, including 500 changed helper endpoints, are recomputed exactly. The largest chart has 208 elementary factors; numerator and denominator maxima are 764 and 351.
- All 4,923,000 role/replica/stage assignments are enumerated. The inventory has 171,361 banks per stage, 1,279,205 literal stock families and 255,841 normalized stock families. There are 2,400 endpoint columns and 2,400 nonzero omission/repetition control columns.
- Normalizer 447 = 208 + 119 + 120; selector charge 528,906,962,400; finite primitive coefficient 92,488,203,535,344,001; recomputed signed payload bound 91 bits.
- Exact fixed-prime proof for q = 2^127 − 1, the full fallback, two rational moment engines, eight ordinary levels, all 47 strict outer inequalities and adjacent-grid rejection.

The normalized paid histogram has 5,808,240 calls, rank mass 30,648,120 and deficit 52,800. The largest child remains 50. Recursive children are charged explicitly and are not included in the finite coefficient.

## Scope

This is a conditional finite construction under the inherited all-size compiler, common weighted chart, restored rows, selectors, routing, prime supply, precision/recovery, complex symbolic correctness and analytic reduction interfaces. It does not establish those assumptions, an unconditional multiplication theorem, a new Lean proof or a practical runtime result. The offline verifier proves this pinned construction; the public-frontier comparison is a separate dated observation.

See `PROOF.md`, `docs/cleanup-proof.md`, code-level exact checks, and `NOTICE.md` for the construction and attribution.
