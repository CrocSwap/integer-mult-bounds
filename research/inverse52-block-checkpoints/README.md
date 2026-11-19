# Exact finite-window sampling with block checkpoints

The same ordered label, first stopping depth and censoring result now needs
`559+51*ceil(2*sqrt(L))` clean work bits. The emitted gate count stays linear
in L. At L=64, clean work is 1,375 bits instead of 3,874; gates rise from
128,827 to 238,965. The L resident coin bits remain separate inputs.

Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/inverse52-block-checkpoints
```

Both modes print `PASS_INVERSE52_BLOCK_CHECKPOINTS 940486 whole-wire cases 524800 block choices`
and elapsed seconds. Read [the proof](PROOF.md), [certificate](RESULT.json),
[gate generator](block.py), [source pins](SOURCE-PINS.json) and [credits](CREDITS.md).
No new kappa or full physical supplier is claimed.

## Open next questions

Install this finite service in a caller that handles censoring and pays for
fresh coins, owner extraction, tape access and clean stock. Those costs and
all five inherited framework assumptions remain open.
