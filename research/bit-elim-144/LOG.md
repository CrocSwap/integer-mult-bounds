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
