# Ternary global-gauge screen for one coordinate-root P112 decoder

**Scoped exact negative result; no new κ.** On one pinned E8 P112 puncture and one merged nine-normal frame, the full ternary box of correlated coefficient shifts contains no active nine-term decoder below copied-information cost 72. The two cost-64 assignments each remove one term. This does not bound other frames, punctures, independent per-root gauges, or shifts outside the box.

The research seed is `655425ccd826280b13917975e2854d16`, selected on the `complex-mechanisms` track at catalogue priority revision 3. The exact base is `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; the selected-record SHA256 is `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. That base retains selected conditional finite construction κ `836330098538459/500000000000000000` (about `0.001672660197076918`). The review, source manifest, assembly certificate, selector and task catalogue are pinned in [SOURCES.json](SOURCES.json).

## Construction family

The eight deleted E8 lines are the exact coordinate frame with indices `[0, 13, 90, 99, 108, 113, 118, 119]`. Add the first extra root with four nonzero inner products against that frame (index `1`) to make a nine-normal frame. Its unique coefficient dependency is

```text
z = (-1, -1, -1, -1, 0, 0, 0, 0, 2),   sum_k z_k b_k = 0.
```

For each live root line `i`, let `c_i` be the exact base row satisfying `sum_k c_ik b_k = 2 r_i`. For one shared integer vector `w ∈ {-1,0,1}^8`, set

```text
D_ik(w) = c_ik + <r_i,w> z_k.
```

The identity remains exact for every `w` because the added row term is a scalar multiple of the frame dependency. The verifier enumerates all `3^8 = 6,561` choices. For each of the nine product terms it forms the row support `X_k` and normal support `Y_k`, then charges the exact `F2` pairing rank `rank_F2(X_k,Y_k)`. This is the full copied-information invoice for this decoder family; it does not include a physical frame or recursive restoration circuit, so no κ conversion is justified.

## Exact result

| Total copied-information cost | Assignments | Nine terms active |
|---:|---:|---:|
| 64 | 2 | 0 |
| 72 | 3 | 3 |
| 73 | 6,556 | 6,556 |

The two cost-64 gauges are `w=(0,-1,0,0,0,0,0,0)` and `w=0`; each has one empty row support, so it is an eight-term decoder. The three active cost-72 gauges are

```text
(-1,-1,0,0,0,0,0,0)
(-1, 0,0,0,0,0,0,0)
( 1, 1,0,0,0,0,0,0)
```

Each has nine term ranks `(8,8,8,8,8,8,8,8,8)`. The verifier checks all `112^2 = 12,544` live root pairs for each of these five low-cost exact identities. A one-coefficient mutation is rejected. The predecessor package records `64/112` as its shipped P112 comparator, so this active family supplies no copy-cost saving to carry into a fully charged profile.

## Scope and overlap

The scope is a correlated, one-vector gauge family on one puncture. The exact support alphabet is the ternary coordinate box; this is not a search over arbitrary real or integer `w`.

The selected nine-normal frame comes from merged [PR #1224](https://github.com/CrocSwap/integer-mult-bounds/pull/1224), whose `research/nine-term-decoder-normal-form-seed42/` package scans per-root ratio-class choices in several frames and punctures. This search instead binds all per-root gauge parameters to the same eight-coordinate vector. Direct nearby work was also checked before claiming: PR #1923 / Discussion #1622 treats a symmetric ten-term Householder family; PR #1614 treats A8 simplex punctures; PRs #1779 and #1817 concern rank-16 diagonal batches and their interleaving. None matches this object and parameter family. The live claim is in [Discussion #1167](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18926689).

The result is a finite census for this family. It is not a universal lower bound for nine-term decoders, a circuit implementation, a supplier-compatible local word, or a new conditional multiplication exponent. The selected record is unchanged.

## Reproduce

```sh
python3 -I -B research/coord-root-p112-global-gauge-seed655425/verify.py
python3 scripts/research_package.py --package research/coord-root-p112-global-gauge-seed655425 --check-only
```

The first command performs the exact census and writes `RESULT.json`. The registered replay uses Python 3.12 and reruns the same check. `verify.py` refuses to run if the two source modules from merged PR #1224 have drifted from their pinned SHA256 values.

## Open next questions

- Does a larger bounded global-shift box contain an active decoder with a lower copy invoice on this puncture? Before expanding the search, derive the optimistic target invoice and claim a new explicit box.
- Can independently chosen per-root gauges be constrained by a meaningful correlation model that is not already covered by the predecessor's ratio-class census?
