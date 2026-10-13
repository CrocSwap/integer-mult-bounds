# Partial-swap batching checks

These check the partial-swap factorization lemma (`notes/partial-swap-batching.tex`) and the two-stage
frames at small h.

```sh
python3 test_factor.py   # exact Bruhat profiles of S_p on random, sparse and adversarial idempotents
python3 frames.py        # two-stage frames at h = 6, 7, 8: monotonicity, rank sums, selected edges, profiles
python3 moment.py        # certified batched saving at h = 32
```
