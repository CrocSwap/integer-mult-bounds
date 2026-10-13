# bit-elim-144 log (fr-dag worker; Sol 00:23 steering)

Branch wk/bit144 from croc/pr144 (c8b22bc, icekylinx: paired-cube shared cores, kappa 4609169/10^10, BIT-LIMITED:
stopped bit 4613422943/10^13 vs complex 4856569/10^10).  Earlier lanes parked: wk/cover-dag d57cb18 (DAG lane on
#130), wk/bitreuse b5cd811 (bit reuse on #129), wk/fr-dag 867f9ba (logs).

## Step 1 GATE (passed)
* `python3 scripts/paired_cube_network.py --output research/fr-dag/gate-paired-cube-network.json` (PR144 unchanged):
  PASS, byte-identical to certificates/paired-cube-network.json.
* `python3 research/bit-elim-144/price144.py` (PR144's own functions; R check relaxed; COARSE and kappa as LARGEST
  points of PR144's 10^-10 grids, next points rejected): coarse 577207/1250000000 = 4617656/10^10, stopped
  4613422943/10^13, kappa 4609169/10^10 (next 4609170/10^10 rejected).  Exact reproduction.

## Step 2-3 terminal elimination on #144's bit word (PR97 round-7 word, 9,543 selected / 2,022 omitted)
* Candidates (deferred output slots that never source): 4,725, ALL among the 9,543 selected gauge slots (none omitted).
  Eliminating a selected slot deletes its gauge and its read; the remaining target chains are subsequences of
  #144's certified chains, and the only new frame facts are the new target-chain adjacencies (re-certified exactly).
* `elim144.py research/fr-dag/data/frames_cache.json.gz plan-all.json`: per target, max first-order gain subset with
  the merged target chain [0, remaining selected sigmas (positive Z support), redirected frames, h-1] nested exactly
  over Q (exact bases from the pinned witness via check_lifted's machinery, cached): 1,549 eliminations.
* `row144.py plan-all.json row-elim.json` (mirrors paired_cube_bit.reconstruct): R 27,317, W 30,859, rank 2,127,247,
  deficit 2,024 unchanged, selected gauges 7,994.
* `replay144.py plan-all.json`: Z replay (exact integer coefficients) and F2 replay (3 seeds) PASS; tamper controls
  (missing redirected update, sign-flipped redirected update) rejected.
* `price144.py row-elim.json` (#144's own functions): coarse 4655227/10^10, stopped 1162739093/2.5e12 = 4.6509563720e-4,
  kappa 4646633/10^10 = 4.646633e-4 (next 4646634/10^10 rejected), still bit-limited (complex 4856569/10^10).
KAPPA 4646633/10000000000 4.646633e-04 (PR144 + 1,549 bit terminal eliminations; +0.813%)
* Pending for the package: from-scratch exact check of the new adjacencies in verify.py (no cache), README/PROOF.
