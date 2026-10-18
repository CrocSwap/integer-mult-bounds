## Result

This adds an exact six-call minimum for one mixed target in the formal group
algebra `F2[S4]`:

```text
diag([(13)(24)], [(12)(34)], [e])
```

There are three arbitrary dirty roles. Paid calls are
`I + ([s] + [e])N` for an adjacent transposition `s` in
`{(12),(23),(34)}` and every rank-one idempotent `N` in `M3(F2)`. Each call
costs one. Free interleaved scalar `GL3(F2)` changes are included through the
standard augmentation normalization.

The direct word costs six: four calls for `(13)(24)=(23)(12)(34)(23)` and
two for `(12)(34)=(12)(34)`. A complete exact two-plus-two meet over all 84
factors excludes every four-call word: all 7,056 ordered pair words were
indexed, covering 49,787,136 four-call words, with 4,698 distinct pair
products. The pair-state SHA-256 and deterministic receipt are in
`RESULT.json`. The sign quotient forces even word length, and the target
coefficient `(13)(24)` has adjacent-transposition length four. Together the
four-call exclusion proves the exact minimum is six.

Positive controls include the six-call mixed word and a found/replayed
four-call word for `diag([(12)(34)],[(12)(34)],[e])`. The repeated
`(13)(24)` target is a negative control. The Python verifier rebuilds the
formal algebra independently and cross-checks a separate C++ implementation.

Reproduce with:

```sh
python3 -I -B research/s4-mixed-v4-double-transposition-seed0cdbb4/verify.py
python3 scripts/research_package.py --package research/s4-mixed-v4-double-transposition-seed0cdbb4 --check-only
```

## Relation to prior work

PR #1734 uses the same group, label alphabet and role count for the repeated
target `diag([(13)(24)],[(13)(24)],[e])`, with exact minimum eight. This
submission changes the second active target to the distinct commuting
double transposition `(12)(34)` and gives direct bill six; it does not claim
priority for the common pair-state method or the general rank floor.

The selected conditional bound remains complex-bound. No rational-frame
supplier mapping, paid-moment change or new `kappa` is claimed.

Research seed `0cdbb418f7a976685134143f77494c2c`; task
`bit-new-register-model`; priority revision 3; exact base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA-256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
Prepared with substantial OpenAI Codex assistance; no independent human
review is claimed.
