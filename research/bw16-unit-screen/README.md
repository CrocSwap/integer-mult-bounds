# BW16 as a unit: main's window screen ranks it below E8

**No new κ is claimed.** This note screens the Barnes–Wall lattice BW16 (2160 minimal-vector lines in rank 16) as
a unit with the screen that main already applies to the ADE root systems, K12, Leech and the Niemeier lattices
(`research/e8-decoder-floors-and-cold14-notes/ade_screen.py`, #598, #606). BW16 has not been screened before.

The screen's result:

- 72 pairwise non-orthogonal lines force the window to c ≥ 72 (E8: c = 9).
- So the copy proxy is x ≥ 8/15.
- The certified ceiling is then at most 3.8923·10⁻³ at every stage count s = 3…39, which is 0.649× E8's bit
  ceiling (6.0005·10⁻³).
- BW16 already loses at c ≥ 63, so the conclusion does not depend on finding the largest clique.

```sh
python3 -B research/bw16-unit-screen/bw16_check.py
```

It uses the standard library only, runs in about 3 minutes and ends with `PASS_BW16_UNIT_SCREEN (21 checks)`.

## Setting

The checks use the conventions of main's unit screen (`ade_screen.py`, #620):

- v lines, lattice rank h, window c, copy proxy x = c·h/v;
- #595's certified ceiling `X(s, h, 1, x)`, imported unchanged from `research/format-limits/scripts/skel.py`.

The decoder pattern is that of `research/format-limits/README.md` §C.6 (#446 Theorem A): over F₂,
B_TS = 0 where G_TS ≠ 0 and B_TT = 1, with window = rank B. On a set K of pairwise non-orthogonal lines the pattern
forces B[K, K] = I, so c ≥ |K|.

## What is checked

| Step | Check | Result |
|---|---|---|
| Lattice | BW16 = RM(1,4) + 2·RM(3,4) + 4ℤ¹⁶ (Construction D) | codes rebuilt from their generators |
| Minimal vectors | the norm-8 vectors are exactly the shapes (±2²) and (±1⁸); both are enumerated in full | 480 + 3840 = 4320, no shorter vector |
| Lines | | 2160 |
| Inner products | \|⟨x, y⟩\| profile of every line | {0: 855, 2: 1024, 4: 280}, the same for all lines |
| E8 reference | 120 lines, exhaustive branch and bound | 63 orthogonal neighbours per line; largest non-orthogonal set 8 |
| Clique | `data/clique72.json`, 64 lines of shape (1⁸) and 8 of shape (2²), pairwise non-orthogonal | \|⟨x, y⟩\| ∈ {2, 4}; a deterministic greedy reproduces it exactly |
| Window | c ≥ 72 from the clique; the pattern's natural decoder B₀ = I + [orthogonal pairs] is checked against the pattern | 72 ≤ c_min ≤ rank_F₂ B₀ = 191 |
| Ceiling | X(s, 16, 1, 8/15) for s = 3, 5, …, 39 | max 3.8923·10⁻³ at s = 3 |
| Reference | E8 bit, X(5, 8, 1, 63/111) (#595 A.3); full E8, X(5, 8, 1, 3/5) | 6.0005·10⁻³; 5.1598·10⁻³ |
| Break-even | the smallest c at which BW16 is below E8's bit ceiling at every s (X is non-increasing in x, #595 A.2) | c = 63 (c = 62 still wins at some s) |

## Why BW16 loses

The loss is entirely the copy charge.

- With free copies (x = 0), BW16's ceiling X(3, 16, 1, 0) = 1.9614·10⁻² would be more than 3× E8's.
- But BW16's lines are too densely non-orthogonal. Each line is orthogonal to only 855 of the other 2159, so large
  pairwise non-orthogonal sets exist. The decoder pattern then pays one window unit per clique line.
- E8 escapes this. Its largest non-orthogonal set is exactly 8 lines among 120, also checked.
- At the natural decoder B₀ the window is 191. That gives x = 191·16/2160 > 1, the regime that main's ADE note
  records as giving no saving.

## Scope

- **This is a ranking screen, not a κ bound.**
  - The selected record, κ = 1.661634653669567·10⁻³ (#799), sits below BW16's screen ceiling, as it does below E8's.
  - The record realises 0.277 of E8's bit ceiling. Nothing here bounds what fraction BW16 could realise.
  - The statement is the same kind as main's ADE, Leech and Niemeier screens: BW16's ceiling is 35% below E8's.
- **Helper cost.** X* alone does not rank unit families (#620 §4). Helper cost grows with the number of orthogonal
  neighbours per line: 63 for E8, 855 for BW16. That points the same way as the screen but is not priced here.
- **Decoder pattern.** Only decoders on the §C.6 pattern are covered. Off-pattern decoders, for example lossy
  corrections with B_TS ≠ 0 on non-orthogonal pairs, are outside this note, as they are outside #620's.
- **Window.** c_min is not determined. Only the bracket [72, 191] is proved. The conclusion needs only c ≥ 63.
- **Clique.** 72 is not claimed to be the largest clique.
- **Parameters.** k = 1, as in `ade_screen.py`.

## Related work

- Main's screens: `ade_screen.py` and §4 of `research/e8-decoder-floors-and-cold14-notes/README.md` (#620: ADE,
  extension rings, K12), #598 (Leech, Turyn), #606 (Niemeier).
- The Gaussian E8 clique ceilings: #738, #770, #868.
- None of these screens BW16. That was checked against the titles and bodies of all hub PRs through #883 and
  against main at `f567884a`.

## Files

- `bw16_check.py`: the checks.
- `data/clique72.json`: the 72-line clique, also rebuilt by the checker.
- `NOTICE.md`, `LICENSE` (Apache-2.0).
- `.github/workflows/bw16-unit-screen.yml`: CI.

## Credits

- DreamingOfClouds, for #595's certified ceiling `skel.X` and the decoder-pattern results of `format-limits`.
- Joel Pulikkan (GamingPuzzled), for #620's unit screen.
- The authors of #446 (Theorem A), #598 and #606.
- BW16 and Construction D are classical: Barnes and Wall (1959); Conway and Sloane, *Sphere Packings, Lattices and
  Groups*, ch. 4 and 8.
- Prepared by DaysSky, with assistance from Claude.
