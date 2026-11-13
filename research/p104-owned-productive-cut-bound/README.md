# Bound fixed-cut restoration of owned helper 1533

**NO VERIFIED GAIN.** On exact [#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481), make owned role 1533 an independently dirty productive helper at its old INIT 38139. Keep the scalar tape and both paid ascents unchanged through the cut just before CLEAR 42503, then allow any reversible scalar basis on its chart-591 bank. The new input has coefficient zero on every bank row and coefficients +1 and −1 on two live chart-1031 rows. No such basis can return the new input while restoring the old live state.

The independent complete comparison is κ `0.003647081039689`, with the exact [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) signed caller. The putative paid delta is zero and the productive delta is T7 +17. The directed gross upper is `118.1584595438061` raw before correction. The 19-lifetime relaxed whole-stock upper is `947.4502523754607` raw before compatibility and repairs. Realized saving in the tested scope is zero.

## Open next questions

One exact case was exhausted. Eighteen other increasing lifetimes, changed pre-CLEAR operations and earlier multi-chart restoration remain open. The next concrete test would permit one paid-neutral basis on chart 1031 just before MOVE42500, require the old chart-1031 live rows and the new dirty coordinate to be recovered exactly, and then verify its effect through the last MOVE and original chart-591 outward ADD.

From a clean checkout with POSIX CPython 3.12 and assertions enabled:

```sh
python3.12 -I -B research/p104-owned-productive-cut-bound/replay.py
```

[Proof](PROOF.md) · [Verification](VERIFICATION.md) · [Source and credit](PROVENANCE.json) · [Relative dependency pins](PINS.json)
