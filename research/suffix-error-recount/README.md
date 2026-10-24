# Independent recomputation of #4510: suffix-weighted logical error bounds

**Claim type:** an independent recomputation by separately written code. **No new κ.** It covers Dugongue's
[#4510](https://github.com/CrocSwap/integer-mult-bounds/pull/4510) (head `97e0830a`), which bounds every
persistent output error of the complete THREE-base native word under an additive logical defect model.

## The model (#4510's)

- An additive defect of norm at most the class budget may enter the target field after every scalar, warp,
  climb and center event.
- Warps are isometric free-group symbols: an operator and its negation cancel when adjacent.
- Everything else is exact.

A reverse sweep keeps each field's exact response as `{(output, reduced warp word): rational}`. At each event
the ℓ₁ norm of the target field's response is added to each output's weight for that event class.

## Results (original and #4505-rewritten words)

| | forward | backward |
| --- | ---: | ---: |
| worst output ADD+SCALE weight | **1,328** (both words) | **4,879** (both words) |
| extra logical-defect bits | 11 | 13 |
| output rows changed by the rewrite | 33 | 90 |
| largest row increase / decrease | 2 / 109/4 | 12 / 4 |
| ADD-only worst weight | 2,355/2 | 4,308 → 4,300 |

The initial-input amplification factor is 2 in all four cases. Everything #4510 states reproduces. The largest
row decreases are new information.

## Not covered

- #4510's physical and recursive defect contracts and its feedback theorem. Those are its open questions.
- Whether this logical norm model matches a physical rounding implementation.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/suffix-error-recount --check-only
python3.12 -B scripts/research_package.py --package research/suffix-error-recount
```

The verifier prints `PASS_SUFFIX_ERROR_RECOUNT` in about 3 seconds, using only the standard library.

## Open next questions

1. **Bind a physical P-bit rounding of entire-field ADD/SCALE to #4510's logical δ.**
   - *Why it matters:* it turns the 11/13-bit statements into implementable precision.
   - *First step:* bound a field's norm growth along the word with the same reverse sweep.

## Credit

- The model, the certificate and the question are Dugongue's (#4510, #4505).

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
