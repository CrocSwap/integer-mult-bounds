This is an exact continuous packing upper bound for every positive replica count
with PR2833's fixed local profile, helper widths, per-replica bins and live-stock
normalization. It enumerates all 1,163 integer bin patterns, verifies the exact
nine-column rational primal, and checks all dual inequalities using directed
rational moment bounds. It performs no allocation or optimization search.

With this directory installed as `packing/` beside `independent/`, run:

```sh
python -I -S -B packing/verify.py --owner evidence/INDEPENDENT-OWNERS.json --moment evidence/INDEPENDENT-MOMENT.json --out /tmp/packing-cap.json
```

Use `--bundle PATH` to select the exact independent source bundle elsewhere.
The output must be fresh and outside the source package and bundles. Inputs are authenticated
before execution and checked again before output. The replay writes no cache or
source artifacts. Python 3's standard library is sufficient.

`inputs/moment.py` is the exact PR2827 independent rational engine. The symbolic
dual and active basis come from the prior authorized packing analysis; their
copied bytes and SHA256 values are bound in `DERIVATION.json` and the replay.
All function ASTs are unchanged from the audited PR2833 cap calculation.

The bound does not establish integer or chronological attainment. Its reported
gain fraction compares the actual T124 finite-moment target with the available
continuous gain above PR2833's full exact headline. Full changed native/global/
outer admission remains separate.
