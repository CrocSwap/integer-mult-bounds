# Port count and puncture depth, priced with the exact packing ceiling

**Planning bound under a favorable relaxation. No new κ; no word, decoder realization or supplier. The selected record is unchanged.**

This answers the second open question of [#1240's packing ceiling](../complex-local-word-ceiling/README.md):
*how does the target budget scale with the port count V, relative to a word's excess spend?* It answers for
the 120-line E8 alphabet, where V = 120 − p and the decoder constant (cst) cannot be chosen freely: the
[frame-pair floor](../complex-frame-pair-decoders/README.md) gives cst ≥ max(72 − p, 56) for exact eight-term
decoders with p ≤ 24, and that floor is attained at every p.

## Model

All premises are explicit in `verify.py`:

- **Ceiling.** #1240's `ceiling.py`, unchanged. Coverage law: mass = 72W + cst·N. There are 8V live families
  per nine-stage replica, and idle children have rank at most 51.
- **Local word.** The selected #1094 word, re-derived from the pinned assembly and idle histogram:
  `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`, whose eight rank-8 children are the centre.
- **Per-port knob.** This is PR717's P1 model, as transported by `complex-frame-pair-decoders` (section G).
  Each port contributes one source climb (1,1,1,5) and one target climb (1,1,4,1,1) per call. Here the
  knob is applied linearly in V; above V = 112 this is an extrapolation.
- **Centre.** Eight terms with balanced costs: cst = 8q + s gives s children of rank q+1 and 8−s of rank q.
  This reproduces every attained split on the frame-pair chain.
- **Sensitivity model.** The non-centre word scales proportionally with V instead, with no fixed part.

## Results

All values are certified exact-rational brackets at a 10⁻¹² grid. "×" is relative to the selected word's
ceiling (a < 0.001690054109089).

| p | V | cst (floor) | cst/V | Ceiling a (knob) | × (knob) | κ cap | × (proportional) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 120 | 72 | 3/5 | 0.0016032 | 0.9486 | 0.0016006 | 0.9103 |
| 4 | 116 | 68 | 17/29 | 0.0016460 | 0.9740 | 0.0016433 | 0.9536 |
| 8 | 112 | 64 | 4/7 | 0.0016901 | 1 | 0.0016872 | 1 |
| 12 | 108 | 60 | 5/9 | 0.0017354 | 1.0268 | 0.0017324 | 1.0498 |
| **16** | **104** | **56** | **7/13** | **0.0017820** | **1.0544** | **0.0017788** | **1.1035** |
| 18 | 102 | 56 | 28/51 | 0.0017074 | 1.0102 | 0.0017045 | 1.0702 |
| 20 | 100 | 56 | 14/25 | 0.0016317 | 0.9655 | 0.0016290 | 1.0356 |
| 22 | 98 | 56 | 4/7 | 0.0015549 | 0.9200 | 0.0015525 | 0.9996 |
| 24 | 96 | 56 | 7/12 | 0.0014769 | 0.8739 | 0.0014748 | 0.9621 |

`RESULT.json` has all 25 rows.

1. **On the attained floor, P104 maximizes the ceiling in both models.** Under the knob model its ceiling is
   ×1.054 (κ < 0.0017788). That exceeds the bit primitive (0.0017334), so the lever can at most *unbind* the
   complex side. A floor decoder beats the selected word's ceiling only for p = 9..18 (V = 102..111).
2. **The two lever components are large but nearly cancel.**
   - Ports alone, at cst 64: V = 120 gives ×1.167 and V = 104 gives ×0.823 (about +2.0% per port).
   - The decoder constant alone, at V = 112: cst 56 gives ×1.225 (about +2.6% per unit).
   - For p ≤ 16 the floor trades one port for one cst unit, so each puncture nets only about +0.66%. Beyond
     p = 16 the floor stays at 56, and each further puncture costs about 2.1–2.6%.
3. **A port pays for itself, but V is bounded.** This answers #1240's open question.
   - At both the selected ceiling and a = 1/99, a port's excess spend is below its budget increment:
     0.00115 < 0.01165 at the ceiling, and 0.00696 < 0.00899 at 1/99.
   - So wider words help at fixed cst. Extrapolating the knob at cst 64, unbinding needs V ≥ 114, but
     a = 1/99 needs **V ≥ 1,328**, and E8 has only 120 lines.
   - **No (V, cst ≥ 0) with V ≤ 120 reaches 1/99**, even with no centre at all.
4. **The copy ratio cst/V is not a monotone proxy for the moment under the knob model.** P112 (cst 64) and
   P98 (cst 56) both have ratio 4/7, but P98's ceiling is certified 8% lower. The reason is that the word has
   a large V-independent part: about 1,628 rank-1 children per call remain at V = 0. Under proportional
   scaling the ratio ordering is nearly restored (P98 ×0.9996). So decoder searches that rank results by
   cst/v (for example #1187/#1455) should rank by the break-even table below instead.

### Break-even decoder constants (screening table for decoder work)

The table gives the largest integer cst at each V whose ceiling still reaches each target (knob model). It is
sharp: cst + 1 fails. Pass/fail is monotone in cst, because +1 cst moves one unit of mass from a rank-q centre
child to rank q+1 and leaves the idle mass unchanged.

| V | 82 | 96 | 100 | 104 | 108 | 111 | 112 | 114 | 116 | 120 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Beat the selected word's ceiling | 41 | 51 | 54 | 57 | 60 | 63 | 64 | 65 | 67 | 70 |
| Reach the bit primitive (unbind) | 40 | 50 | 53 | 56 | 60 | 62 | 63 | 64 | 66 | 69 |
| Same as row 1, proportional model | 46 | 54 | 57 | 59 | 61 | 63 | 64 | 65 | 66 | 68 |
| Reach a = 1/99 | none | none | none | none | none | none | none | none | none | none |

The #1187/#1455 82-port witnesses (cst 55 and 54) price at ×0.562 and ×0.594. An 82-port decoder would need
cst ≤ 41 to match the selected word.

## Scope and limits

- **Favorable relaxation only.** The bound allows fractional idle counts at rank 51. It omits whatever
  realizing a punctured word costs, including the asymmetric-centre reads, frame legality, restoration and
  the unpaired-centre parity costs (≥ 78) that PR717 recorded. The admissible primitive saving in this model is at most its ceiling.
- **The per-port knob is PR717's local marginal model, not a derived word.** A real P104 or P120 word may
  have a different profile. The proportional row brackets one alternative, and the qualitative conclusions
  (P104 is the argmax, 1/99 is unreachable, the lever only unbinds) hold in both models. Rows with V > 112
  extrapolate the knob.
- **The centre split is balanced.** For a fixed cst, a more unequal split of term costs would lower the cost
  slightly (child cost per unit mass falls with rank). The floor is proved only for exact eight-term decoders
  with p ≤ 24; nine-term, masked or E-graph-only decoders, and other alphabets, are outside it (see
  frame-pair-decoders' scope).
- **Planning conversion.** κ < a/(1+a) is the retained balanced conversion and assumes the complex side binds.
  The bit primitive comes from the selected assembly (PR589).
- **Predecessor check note.** At this base, `complex-frame-pair-decoders/verify.py` fails only its
  `G.selected-record` gate, because the selected record moved from PR942 to PR1094 after that package was
  frozen. Its decoder census and chain (sections A–F, H) pass, and this package uses only the chain values.

## Reproduce

```sh
python3 -I -B research/complex-puncture-depth-ceiling/verify.py           # ~80 s, PASS_COMPLEX_PUNCTURE_DEPTH_CEILING
python3 -I -B research/complex-puncture-depth-ceiling/verify.py --write   # regenerate RESULT.json
python3 scripts/research_package.py --package research/complex-puncture-depth-ceiling
```

The verifier runs 22 checks. Besides the positive control (#1240's ceiling reproduced exactly) and
re-deriving the word from the pinned assembly, it has these controls:

- V = 77 is rejected by the coverage law.
- The floor is refused beyond p = 24.
- Pass/fail is monotone in cst at V = 104.
- Keeping the 56 removed rank-1 children at P104 lowers its ceiling.
- RESULT.json must match the recomputation byte for byte.

## Open next questions

- **What is the real per-port profile of a P104 word?** The knob is a marginal model, and the break-even table
  needs the actual local word.
  - *Why it matters:* the P104 headroom (×1.054 knob, ×1.10 proportional) is the largest on the attained
    floor, and it decides whether this lever can unbind the complex side.
  - *First step:* build the P104 analogue of the #1094 local word and screen its profile with
    `ceiling.ceiling(local, 73, 832, 9, 56)`.
  - *Blocker:* asymmetric-centre realization (PR717's parity and pair-split conflicts).
- **Do the larger-alphabet unit screens survive re-pricing with this ceiling?**
  - *Why it matters:* per-port excess is below the per-port budget even at 1/99, so V is the one lever here
    that does not saturate. E8 caps it at 120 lines (1/99 would need V ≥ 1,328 at cst 64). The existing
    ADE/Leech/Niemeier screen (#620, `ade_screen.py`) and the BW16 screen (#895, 2160 lines, copy window
    c ≥ 72) rank units by the ratio-type proxy x = c·h/v, and finding 4 shows such a ratio can misorder
    words with a fixed V-independent part.
  - *First step:* write one larger unit's coverage law, centre floor and per-port knob, then price it with
    this verifier's `word()` and `max_cst()`.
  - *Blocker:* a per-port knob and an attained centre floor for that unit.

## Credit

- **Douglas Colkitt:** the packing-ceiling calculator and its open question (#1240).
- **DreamingOfClouds:** the B14 model and P1 per-port knob (PR717).
- **The `complex-frame-pair-decoders` authors:** the attained floor chain and the knob transport.
- **Navinor:** coverage-law thresholds at a fixed word (#1348), a complementary lever in which F changes
  but the word does not.
- **Cinna Davis and woklerx:** the 82-port witnesses (#1187, #1455).
- **Joel Pulikkan and DaysSky:** the unit screens cited in the open questions (#620, #895).
- **The authors of the selected #1094 construction:** credited in its review.

Prepared by Jack Galler with substantial Claude Opus 5.5 (Anthropic, Claude Code) assistance: model choice,
code and text. Apache-2.0.
