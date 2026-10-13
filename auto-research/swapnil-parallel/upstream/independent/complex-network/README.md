# Fully batched complex saving of the PR #7 network

An independent rebuild of the complex side used by the round-three witness:

- `side.py`: the PR #7 complex producer (pieces, pair stars, optional PR #4 retained totals).
- `labels.py`: exact binary label checks over F2^h for every edge of the producer.
- `roles.py`: role-level compile (addition, piece and retained-total slots).
- `fullbatch_hist.py`: the three-stage invocation schedule with h+1 centre wires; it records the rank of
  every nonzero residual edge and checks that the ranks sum to s exactly.
- `fullbatch_cert.py`: treats every residual edge as one whole-residual child (PR #15's full batching),
  certifies a_c by exact bisection on the moment equation with certified upper bounds on ln (`bc.py`),
  reports the path bound, and evaluates kappa with `scripts/certificate_round3.py`.

```sh
python3 fullbatch_hist.py 28 /tmp/fb28.json   # ~4 min; label check, ranks, sum_ok
python3 fullbatch_cert.py /tmp/fb28.json
```

At h=28 (m = 21952, R = 93867 with the centre wires, s = 45772350635112192) the labels check has 0 bad
edges, the rank sum equals s, and the certified saving is a_c = 1048009/(2.5*10^11) ~ 4.192e-6. With the
batched two-stage bit interchange (a_b = 22157/(5*10^9)) this gives kappa = 13086957581/(3.125*10^15)
~ 4.1878e-6 under both guards, with the simultaneous butterflies binding.
