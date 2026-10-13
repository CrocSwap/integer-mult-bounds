# Saturation of the X54 mixed-T37 construction (#1193/#1218)

**No new κ.** This is a scoped negative result plus a screening tool for the highest open claim,
κ = 0.001675809683500501 (#1193, #1218, #1239). It asks whether that construction can still be improved by
(a) more width-neutral local moves on its two final words, or (b) a better packing of the same helpers.
Within the families and relaxations below, the answer is no. It also gives exact prices for helper-width changes,
so later inventory proposals can be screened before anyone builds them.

## Inputs

These are vendored byte-for-byte from open PRs and pinned in `verify.py`:

| File | Source |
|---|---|
| `inputs/D3-WORD.json.gz` | #1193 `vendor/pr1207/BASE-X54-WORD.json.gz`: #1148 joint entrances + #1195 fusions + X54 (125 calls) |
| `inputs/D4-WORD.json.gz` | #1193 `data/FOUR-WORD.json.gz`: D3 + entrance group 627 (208 calls) |
| `inputs/FLOW.json.gz`, `inputs/MIX.json` | #1193's frozen integer pattern flow and call dispatch |

The #1193 head is `4e392e90`; #1218 at `0aa14797` reuses the same words, flow and dispatch. The T37 bin
capacities are recomputed from files already on main: the retained #1042 replay archive and PR858/PR870's
unchanged `actual_windows`.

## Results

### 1. No local gain is left in the toolkit's move families

I used the #1186 toolkit at head `9254a3cc`, unchanged, with exact frame pricing. Both final words were swept.
#1195 had swept only the pre-slot and seven-slot words, before X54 and the joint entrances.

| Family | Candidates per word | Feasible | Gains (D3 / D4) |
|---|---:|---:|---:|
| Read fusion + single/pair swap repairs + full exchange (`repair.py`) | 2,238 | 969 | 0 / 0 |
| Read-set exchange, every subset of swappable reads, 14 copy pairs | 50 | 0 | 0 / 0 |
| Joint triangle-hybrid, ≤3 fused reads, partial swaps, both restore modes | 161 | 24 | 0 / 0 |

The baseline frames are also exactly optimal: the frame-solver optimum equals the published profile. The
per-candidate results are in `evidence/sweeps/`.

### 2. The incumbent idle profile is optimal for its mix (exact)

`packing.py` uses standard-library integer arithmetic. It recounts every helper width from the two words and
checks that the flow hosts all 159,840 helpers exactly once. The bins hold `{8:24864, 16:16576, 32:16576, 48:16576}`
and the idle remainders are `{1:2, 48:11374}`, with mass 545,954.

**Width-class invariant.** Let φ(4) = φ(8) = 0, φ(5) = 3, φ(7) = 1 and φ(9) = −1. Enumerating every multiset
of widths gives these bounds:
- a bin filled exactly to capacity 8, 16 or 32 has Φ ≥ 0;
- a bin filled exactly to capacity 48 has Φ ≥ −4.

Φ is additive, so its total is fixed by the helper inventory: −20,814 for 125 D3 + 208 D4.

**Consequence.** The only cheaper idle histogram of the same mass is `{2:1, 48:11374}`. A histogram with fewer
rank-48 parts is dearer by Karamata; this is checked for every j up to 11,374 at #1193's root endpoint.
Realizing `{2:1, 48:11374}` would need exactly 5,202 occupied capacity-48 bins, one remainder-two bin and every
other bin full. Then Φ ≥ −20,810 > −20,814, a contradiction.

The incumbent is tight. Every occupied capacity-48 bin attains −4, and the two `4+9+9+9` bins give −3 each.
**So the two leftover rank-one idle units cannot be merged into one rank-two child.** That would have been the
only remaining packing gain, about +3.3·10⁻¹⁰ in κ, for this mix. This holds even with time windows, ports and
family rules ignored.

### 3. The mix is optimal among demotion counts (numerical screening)

`aggregate.py` (SciPy/HiGHS, floating point) lets every call use k ∈ [−3, 3] extra four-helper entrance groups.
Each group is taken to change the profile by `−8H1+8H2+4H3−4H4` and four widths by 4→5. Only k = 0, 1 are
admitted words; the others are a linear extrapolation. The model ranges over all 1,163 bin patterns and relaxes
time windows. Its integer optimum equals the incumbent objective exactly: 208 groups in total. The fractional LP
gains only half a group, which is not integral, worth ≈2.5·10⁻¹⁰ in κ.

The LP duals have an exact two-parameter structure, π_w = −λ·w − μ·φ(w), with λ = 11.731 per unit of helper
width and μ = 25.041 per unit of Φ. The units are 10⁶ × moment × W, at the #1193 root.

### Screening rule for a proposed local change

Take a per-call change with paid-profile delta Δn, total helper-width delta ΔWid and Φ delta ΔΦ. Its marginal
score is

```
score = Σ_r Δn_r · 1e6·((r/73)^(1-a) − r/73)  −  11.731·ΔWid  −  25.041·ΔΦ
```

summed over the calls that adopt it, with a = 0.0016786227. A negative score is a candidate gain.
Δκ ≈ −1.028·10⁻¹¹ × score. The prices are marginal LP duals. An integral packing must still exist, and there is
almost no slack (2 units), so rerun the ILP with the new variant and then admit it natively.

Examples:
- An extra entrance group scores ≈ −1, which is break-even. That is why #1193 stops where it does.
- Shrinking one 9-wide helper to 8 earns 13.3. Turning a 9 into a 7 earns 26.6.
- Turning a 4 into a 5 earns 86.9, but growing 7→8 costs 13.3.

## Reproduce

```sh
python3 -B research/x54-mixed-t37-saturation/verify.py                        # ~2 s, stdlib
python3 -B research/x54-mixed-t37-saturation/aggregate.py --out /tmp/agg.json  # ~25 s, SciPy
python3 -B research/x54-mixed-t37-saturation/sweep.py --toolkit PR1186/research/exact-frame-toolkit \
    --word D3 --out /tmp/sweeps --workers 6                                    # ~10 min per word
```

`verify.py` does the following:
- checks the input pins;
- replays the exact packing statement against `evidence/PACKING.json`;
- rejects five controls: a changed call mix, a changed helper width, a non-conserving pattern, a dropped bin
  and non-invariant φ weights;
- recounts the stored sweep tallies.

It does not rerun the sweeps or the ILP.

## Scope and limitations

- The sweeps cover the #1186 move families as implemented, with their default limits: `repair.py` tries at most
  40 repairs per fusion. They do not cover other delivery rewrites, entrance or end changes, or different
  helper interfaces. A failed finite search is not an impossibility theorem.
- The packing statements relax time windows, ports and per-call family rules, so they are upper bounds on what
  any packing could achieve. They assume the retained T37 bin geometry (capacities ≤ 48) and the {4,5,7,8,9}
  width alphabet.
- All inherited conditions of the incumbent remain conditions here: all-size compiler, common-label and
  mutable-source realization, whole-call hosting, precision and tape, exact recovery, analytic transfer, and
  bit H1–H5.

## Open next questions

1. **Can a helper-width change pass the screening rule?** For example, a 9→8 end at local cost below 13.3 units,
   or a 4→5 entrance change below 86.9 per helper. *Why:* the packing is saturated, so only a changed inventory
   or local word can move κ. *First step:* price candidate single-helper entrance and end changes with the
   #1186 `harness.Pricer`, then score them with the rule above. *Blocked by:* there is no generator for
   single-helper interface changes; #1176 found that entrance demotions need whole four-helper groups.
2. **Can the bin geometry change?** *Why:* 11,374 idle rank-48 children sit three ranks below the halving-guard
   cap of 51 (#1240), and Φ only constrains occupied bins. *First step:* compute λ, μ and the idle cost for a
   hypothetical capacity-51 window family with `aggregate.py`'s model. *Blocked by:* the capacities come from
   the PR942 five-bank T37 lift; any change needs a new parent geometry and invoice.

## Credit

The #1193 global allocation is Jeremy Diviney's; #1218 is Rohan Arun's composition. The words come from
Thomas DiFiore's #1148, Marius-Paul Dumitrean's #1195 fusions, Jeremy Kothe's #1130 X54 and #1196/#1207's
composition. The search toolkit is #1186, by Marius-Paul Dumitrean. The windows are from Hao Yan's PR858/PR870
geometry. The demotion-group lead is #1111/#1176. #1240's packing-ceiling note motivated the idle-rank
question. Prepared by Wronskode with substantial AI assistance (Anthropic Claude, via Claude Code). Apache-2.0.
