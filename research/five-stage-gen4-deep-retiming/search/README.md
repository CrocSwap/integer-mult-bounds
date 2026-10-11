# Selection search (provenance only)

`verify.py` never runs these scripts; the frozen `descent-selection.json` is the mathematical input.

```sh
python3 -B harness.py                          # cache the parity-fused word (about 1 minute)
python3 -B search.py                           # single-gate neighbour moves -> reproduces PR279's 880
python3 -B bcd.py --start assign_ls.pkl --tag bcd0 --passes 8
python3 -B bcd.py --start assign_bcd0.pkl --tag seed2 --joins --passes 5 --seed 2
python3 -B make_selection.py assign_seed2.pkl descent-selection.json
```

`cascade.py` (raise/lower cascades) and `ceiling.py` (decoupled per-register bound) reproduce the
negative results in `NOTE.md`. Outputs are written next to the scripts; run from a scratch copy.
