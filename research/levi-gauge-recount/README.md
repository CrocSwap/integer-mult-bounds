# Independent recount of #4518: Levi-adaptive gauges

**Claim type:** an independent recount by separately written code. **No new κ.** It covers Dugongue's
[#4518](https://github.com/CrocSwap/integer-mult-bounds/pull/4518) (head `9f0d81c8`). That PR changes the
target gauge between dyadic coefficient groups in the four native cleanup windows, and reports a scalar
allowance of 666 → 616 per orientation and a lower suffix error.

The PR is not merged, so its `NATIVE.json` is vendored here as `NATIVE-4518.json`. The bytes are
SHA256-pinned to the PR head and marked `-text`.

## Results (both orientations)

| | forward | backward |
| --- | ---: | ---: |
| scalar allowance: original → #4505 → #4518 | 158,120 → 158,020 → **157,970** | 158,168 → 158,068 → **158,018** |
| saving over #4505 / original | 50 / 150 | 50 / 150 |
| worst suffix ADD+SCALE weight (#4510 model) | 1,328 (unchanged) | **4,871** (from 4,879) |

1. **Logical correctness.** Every non-scalar event is unchanged. All changes lie in one scalar segment
   (4,208 → 4,212 scalars), whose exact rational linear effect on all 411 touched fields equals the
   original's. Borrowed fields are therefore restored and no field is dirtied. This uses the same code
   as my #4513.
2. **The tariff.** It is re-implemented independently and gives exactly the allowances above.
3. **The suffix bounds.** These use my independent reverse-response code from #4514, with an
   initial-input factor of 2.
4. **The interval theorem.** #4518's optimum within its family,
   `C + min_{L≤0≤H} [4(H−L) + 2 Σ dist(s_i, [L, H])]`, equals an **exhaustive Dijkstra search** over
   gauge walks (unit SCALE steps cost 2, start and end at gauge 0) and add orders (an ADD at gauge `g`
   costs `2|s_i − g|` above its odd-part price) on 400 random valuation multisets of size up to 6.

## Not covered

- #4518's physical frames, phases and prefix envelope (its own literal and prefix loops).
- The Levi dualization proof itself.
- Optimality beyond the stated family.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/levi-gauge-recount --check-only
python3.12 -B scripts/research_package.py --package research/levi-gauge-recount
```

The verifier prints `PASS_LEVI_GAUGE_RECOUNT` in a few seconds, using only the standard library.

## Open next questions

1. **Does letting the source gauge move too (not only the target) lower the 616 further?**
   - *First step:* extend the Dijkstra state to two gauges, and price source restoration.

## Credit

- The construction, the interval theorem and the Levi connection are Dugongue's (#4518), building on #4502,
  #4505 and MathProof's TI_SP proof.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
