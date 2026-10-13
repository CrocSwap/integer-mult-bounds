# Literal width-seven packing and exact admission

The admitted candidate in `width7/RESULT.json` has
**κ = 0.001600067494703216**, compared with PR564's
0.001593134158181640. It uses 63 width-seven providers and nine plain
four-cold providers. Every call keeps all 504 helper roles; the global
physical stock stays 7,682 families and the live stock stays 7,168.

The new width-seven provider promotes 32 existing entrance frames. Its
scalar operations and coefficients equal the corresponding four-cold word.
The additional frame cost is explicitly charged: relative to that word,
its local profile changes by `32 H1 + 160 H2 - 128 H3`. Shortening those
32 helper residuals from width eight to seven allows width-nine and
width-seven residuals to share rank-sixteen pending blocks. The nominated
map also moves the smaller width-four and width-five residuals.

`nominate_width7.py` used SciPy only to propose integer window flows and
bin patterns. A first aggregate solution failed the exact owner expansion;
the retained solution adds subset-of-width owner constraints. Every flow
in the final solution was expanded to literal owners and checked with
integers. The independently implemented physical audit then reconstructed
chronology including bridge touches, spectator axes and all pending
windows. No optimizer result is accepted as an admission proof.

The retained global profile is
`{1:169056, 2:41184, 3:25968, 4:13824, 5:4032, 6:4032, 7:48, 8:576, 48:1808}`.
The explicit idle remainders are `{3:1200, 7:48, 48:1808}`. The full finite
invoice includes all scalar primitives, coefficient work, wrappers,
controller moves and compiler charges. Both rational moment engines,
seven bootstrap levels and all 47 strict outer conditions pass for each
of the native and conservative complex models. The conservative value is
κ = 0.001600067491919801. The bit surcharge is retained.

## Reproduce

From the repository root, using only the Python standard library:

```sh
python3 -B research/larger-gain/global/reproduce.py \
  --source research/complex-allcold \
  --work /tmp/width7-reproduction
```

This rebuilds the pinned PR564 baseline, constructs and verifies all six
local provider variants, then binds the two selected providers, emits the
frozen owners, runs the independent physical audit and complete invoice,
and checks the exact assembly and mutation controls. The source manifest
is pinned to PR564 head `c18417b02b80594b2ca1c8c21185d28befafc935`.
No optimization library or repository network access is needed.

Complete existing replays can be reused:

```sh
python3 -B research/larger-gain/global/reproduce.py \
  --source research/complex-allcold \
  --baseline /path/to/complete-pr564-replay \
  --provider-work /path/to/complete-six-provider-replay \
  --work /tmp/width7-global-reproduction
```

Reuse checks the exact stage inventory, successful exits, log hashes,
source manifest, artifact inventory and provider bindings. Output includes
`RESULT.json`, `RECEIPT.json`, `STAGES.json`, logs and the full emitted global
artifacts. Timing-only phase receipt changes are accepted; substantive
phase changes are rejected.

`width7/ADAPTATION.patch` records the precise changes from the immutable
PR564 verifier. The adapted guards pin the new provider words, dispatch,
actual geometry, profile and rate; they preserve all inherited finite
admission checks. The final witness rejects 16 physical owner mutations
and 89 assembly mutations, including a width permutation at every one of
the 32 promoted helper entrances. Independent geometry and adapter reviews
are under `../geometry/`.

The earlier, smaller admitted fallback is retained in `fourcold/` with
κ = 0.001593675235313849. It is superseded by the width-seven witness.
The packing search has not proved global optimality.

## Scope

This is a conditional native exact-complex witness, composed with the cited
unchanged PR543 bit supplier. The inherited all-size compiler,
common-label and mutable-source realization, whole-call hosting,
precision/tape bounds and analytic-transfer assumptions remain. It is not
an unconditional multiplication theorem or a proof of worst-case O(1)
indexing. Faster indexing alone does not establish this κ change: the
admitted improvement comes from the explicit frame and owner repacking.
