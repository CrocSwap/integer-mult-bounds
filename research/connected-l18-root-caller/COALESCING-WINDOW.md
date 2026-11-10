# The fixed repair fails throughout the improvement window

The coordinate-role compression proof in `IDLE-COALESCING.md` selects the same
degree vector for every `0 < kappa < 1`: union/intersection compression uses
only concavity, and the two final bridge choices are decided by
`f(1)+f(3) < 2 f(2)`. Thus a single pair of complete histograms bounds the best
possible moment in that precisely stated relaxation throughout this range.

Let `M(k) = sum_r (T_r-P_r) r^(1-k)`. `COALESCING-WINDOW.json` records both
complete histograms. They include 104 copies of the root target profile,
18 entire F-native paid and helper profiles, 18*104 extra paid rank-one
adapters, 3*104 thin jobs, and 104 copies of the optimally coalesced idle
profile. Their rank surplus at zero is 760. All ordinary implementation,
coalescing and outer overhead is optimistically free.

For `a = .00362701882` and `b = .01`, exact outward-rounded intervals give:

- `M(a) < -38.95196340866319`;
- `M'(k) < -198383.7893856592` for every `a <= k <= b`.

To obtain the second bound, put `c_r=T_r-P_r`. Each derivative term is
`-c_r log(r) r^(1-k)`. For positive c_r its upper bound occurs at b; for
negative c_r it occurs at a. Summing those independently valid upper bounds
gives the displayed uniform negative bound. Therefore `M(k)<0` on the whole
closed interval. This includes the newly proposed .00363005817 candidate and
the aspirational .01 endpoint; it says nothing about other constructions.

The independent checker reconstructs stage eligibility and the two compressed
bridge cases from the pinned root; it authenticates the actual caller and
retained F invoice and recomputes every target and paid multiplicity. Its
integer fixed-grid logarithm/exponential engine is the independently authored
engine published at `93effe2a135bf57b9e484cb630d8dd057159aec9`,
`research/shared-wire-split-composition/interval_gate.py`, unchanged here as
`review/interval_engine.py`. Exact byte pins are in `INPUT-PINS.json`.
This is attributed reuse of that arithmetic engine with a new profile and
uniform derivative proof, not another independent arithmetic implementation.

The seventh registered command recomputes and compares the complete receipt.
Omitting the paid adapter causes its endpoint test to fail; a reversed
interval is also rejected. Optimized Python is explicitly rejected. The
checker reads its inputs and receipt without rewriting them.

This result is restricted to the fixed 38 coordinate roles, fixed stage
masks, two coordinate hosts per stage, and arbitrary free merging of all
same-role idle occurrences. Noncoordinate idle directions, changed root
geometry, a cheaper native, helper mixing, or a larger coupled construction
are outside it. The F+H1 word itself remains unbuilt. **No new κ.**

Prepared for @CubeJerry with substantial OpenAI Codex assistance. The root,
native, compression and interval predecessors retain the credit stated in
`README.md`, `NOTICE` and `NATIVE.md`.
