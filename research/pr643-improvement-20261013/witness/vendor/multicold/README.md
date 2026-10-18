# Eight cold helpers in every complete complex invocation

κ = 0.001596133352130093 (conditional).

The complex supplier has b = 0.00159868506668458107128. The unchanged cited PR543 bit cap is c = 0.001653826988146798944268, so complex binds. A separately verified conservative complex model yields κ = 0.001596133349380077. The gain over PR564 (κ = 0.001593134158181640) is 2.999e-6, or 0.188%.

PR564 made one helper per call cold: helper 270 enters at rank one, so its residual width drops from nine to eight. This package adds seven more cold helpers to every provider. Each one is killed by a *multi-cut* kernel: its donor gates `donor += -q·pivot @E` sit at different cuts rather than at one cut. The pivot holds only its initial dirt until its first original touch, so the gates cancel its complete dirty response if and only if an exact dyadic relation holds among the donor columns at their cuts.

- Helper-donor kernels: helpers 282, 294 and 306 (registers 506@[24], 518@[30], 530@[30]). Each uses four or five gates on helper donors, one of which is another B-first helper split at its first frame. Each changes the local profile by `{1:+1,2:+2,3:-2}`.
- Target-donor kernels: helpers 271, 283, 295 and 307 (registers 495@[24], 507@[24], 519@[30], 531@[30]). Each uses three B-part gates: two on output targets, like the post-centre gauge compensation, and one on a B-first partner. Each changes the local profile by `{1:+3,2:+1,3:-2}`.

Every B-first width-nine helper needs another B-first helper as its split donor, so this family has at most 16/2 = 8 cold helpers per word. All eight are used.

All 72 calls keep PR564's dispatch: 15 zero-pivot, two four-pivot and 55 eight-pivot words. All three now carry the eight cold helpers. With p promoted pivots:

- The width inventory is `{4:p, 5:56-p, 8:164, 9:284}`.
- The local paid profile is `e1·(2316+2p) + e2·(452-2p) + e3·(456-p) + e4·(184+p) + 56e5 + 56e6 + 8e8`.
- There are 220 entering helpers, and the entrance rank is 388+p.

A new literal owner assignment realizes the inventory. It was found with an aggregate CP-SAT model with per-call Hall conditions, adapted from the open allocator in `research/complex-delivery-map-open-allocator`, then a per-pattern Kőnig edge colouring. Its idle profile is `{1:93,2:93,3:2118,7:1,48:1713}`, against PR564's `{3:2364,7:172,48:1668}`.

The complete paid profile is `{1:167741,2:31741,3:34502,4:13696,5:4032,6:4032,7:1,8:576,48:1713}`. It is reconstructed from both actual reflected scalar event lists and the complete physical controller. All 36,288 helpers have one whole owner, with no auxiliary banks. The audit checks 3,209 orthogonal chart types, 27,679 cross-replica roles and 4,018 positive idle remainders. Live stock is 7168, physical stock 7682, rank mass 520704 and deficit 2560.

Run it with standard-library Python 3 and a fresh output directory outside this source package:

```sh
python3 -B verify.py --work /tmp/multicold-replay
```

Assertions must remain enabled. The verifier:

- Fully reconstructs frozen PR558 and the four-pivot source.
- Rebuilds PR564's three one-cold words with their six cold-kernel omission controls each.
- Applies the seven frozen multi-cut kernels to each word. It checks exact zero complete dirty response by forward replay, legal frame chains and the pinned profile delta, and runs 32 omission controls per provider (every new gate alone and every whole kernel, in both exact orientations).
- Re-runs, on each final word, the inherited 44-kernel and four/eight promotion omission audits.
- Checks all 728 scalar columns in both orientations, all 504 arbitrary dirty helpers restored, both reflected ledgers, all 2929 exact phase edges and 224 endpoint adapters per provider, and the normalized wrappers.
- Binds the three fresh native providers and checks the complete physical assignment with 16 controller mutants.
- Emits a fresh complete finite invoice and checks both exact recurrence/assembly models with 54 malformed-receipt controls.

The fresh invoice charges 11,598,720 scalar primitives, 5,743,456 coefficient-work primitives and 4,561,920 elementary wrapper factors. Prefix 225 is below 512; the physical row coefficient 16,467 is below 20,161. Full group/router, adapter, literal, mass, precision, tape, idle and all-size obligations remain charged. Two rational moment engines reject the adjacent supplier endpoint, and both models pass seven bootstrap levels and 47 strict outer constraints with next-grid and parameter controls.

The native complex moment credits rohanarun's PR559 exactly as in PR564. Only the generic complex bad-residue surcharge is omitted; the conservative witness is verified first, and the PR543 bit fallback remains.

This remains conditional on the inherited all-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, analytic transfer and PR543 H1–H5 assumptions. Finite exact replay is not an unconditional theorem, a full Lean proof or a practical speed claim. Source pins, notices, licenses and AI disclosures are preserved.
