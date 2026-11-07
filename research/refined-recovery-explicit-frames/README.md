# Explicit near-optimal refined-recovery frames at depths 28–30

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

**Exact finite certificate; no κ.** This answers the "explicit frames" open
question of [#6851](https://github.com/CrocSwap/integer-mult-bounds/pull/6851)
for t = 28, 29 and 30. Three explicit integer frame sequences come within a
tiny relative amount S_t of the universal lower bound 13^(8t)/2^104
([#6849](https://github.com/CrocSwap/integer-mult-bounds/pull/6849)):

| t | OPT(t)·2^104/13^(8t) − 1 ≤ S_t | previous | factor |
|---|---:|---:|---:|
| 28 | 2.72·10⁻⁷ | 5.45·10⁻⁶ (#6850, explicit) | 20× |
| 29 | 5.01·10⁻⁹ | 2.48·10⁻⁴ (#6851, existential) | 4.9·10⁴× |
| 30 | 5.05·10⁻¹² | 1.55·10⁻⁵ (#6851, existential) | 3.1·10⁶× |

Each S_t is exact. verify.py rebuilds the integer frames W_j = I + V_jE from
[FRAMES28.json](FRAMES28.json), [FRAMES29.json](FRAMES29.json) and
[FRAMES30.json](FRAMES30.json). It then reads off the binary images of W_j M and
checks rank 104. Finally it enumerates the whole dependency space D (up to 2^16
elements) and evaluates the zero fiber in exact rationals, through two
independent formulas. All S_t lie far below
[#6848](https://github.com/CrocSwap/integer-mult-bounds/pull/6848)'s threshold,
so for these frames the max fiber equals the zero fiber.

The frames were found by greedy local search over the ψ_j, starting from #6851's
random ensemble; see [PROOF.md](PROOF.md). verify.py does not trust the search;
it certifies the stated properties from the integers alone.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3.12 -I -W error -B research/refined-recovery-explicit-frames/verify.py
python3.12 -I -O -W error -B research/refined-recovery-explicit-frames/verify.py
python3.12 -B scripts/research_package.py --package research/refined-recovery-explicit-frames
```

Each run prints `PASS_REFINED_RECOVERY_EXPLICIT_FRAMES` in under a second.

## Limitations

These are upper bounds, and the exact OPT(t) at t ≥ 28 remains open. The result
cites PR6660's frame family, #6848's max-fiber theorem and #6849's lower bound,
all unmerged, and replays none of them.

The search code is not part of the package; the frames are certified directly.
Depths t ≥ 31 would need either D-enumeration beyond 2^16 or the χ-side sum.

The package supplies no codec, physical tag, caller or restoration cost. κ, the
selected frontier and its five assumptions are unchanged. No independent human or
proof-kernel review is claimed.

## Open next questions

1. **Exact minimum S at t = 28.** D has only 2^8 elements, so a classification
   in the style of #6828 might be feasible. It would give the exact OPT(28).
2. **Structured constructions.** Is there an algebraic family, for example from
   codes over GF(16), whose S_t matches the 14.8-bits-per-stage rate of #6852
   explicitly?

## Credit

Nick Petalas's PR6660 (frame family, dimension cap); CubeJerry's PR6327; zxv's
#5444; #6828, #6848, #6849, #6850 and #6851.
