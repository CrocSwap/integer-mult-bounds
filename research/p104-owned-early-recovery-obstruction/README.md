# Exclude early coframed recovery of owned helper 1533

**NO VERIFIED GAIN.** On exact #7481, replace the zero INIT of owned helper 1533 by one independent input \(z\). Keep the old word up to the cut on chart 1031 immediately before MOVE42500. A correction using all 18 live coframed rows cannot restore the old rows, preserve the old outward ADD result and return \(z\), even when allowed arbitrary rational linear combinations. Exact forward and reverse coefficient replays certify the inconsistency.

The separating input gives old coordinates 34, 129 and 1336 value −1 and \(z=1\), with every other old input zero. All 18 modified rows vanish. The old rows 1336 and 1563 evaluate to −1 and +1, respectively, and the required output \(z\) evaluates to +1. The retained ADD42502 source term alone is expressible. This exclusion extends the later chart-591 cut audit in #7482.

From a clean POSIX checkout with CPython 3.12:

```sh
python3.12 -I -B research/p104-owned-early-recovery-obstruction/replay.py
```

## Open next questions

This is one lifetime at one cut. Changing the earlier scalar prefix or allowing other-chart storage changes the available rows and requires fresh pricing and replay. Other lifetimes and cuts remain open. For another route to improve the signed complex moment, choose one paid operation outside overlapping public claims and first bound the full tariff change, including any restoration and boundary work.

[Proof](PROOF.md) · [Verification](VERIFICATION.md) · [Source and credit](PROVENANCE.json) · [Relative dependency pins](PINS.json)
