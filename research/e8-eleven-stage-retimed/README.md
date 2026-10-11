# e8-eleven-stage-retimed

Conditional kappa `8441130528457 / 6250000000000000 = 0.001350580884553120`, 0.2105 percent above PR 450.

PR 450's mixed R740 word with 113 phase-B deliveries moved to coarser frames, every scalar addition unchanged, priced by
PR 450's pipeline run unchanged. See `PROOF.md`. Replay:

```
python3 -B research/e8-eleven-stage-retimed/verify.py /absolute/new/output --quick
```

Needs what PR 450's verify.py needs (Python 3.11+, numpy, mpmath, sympy, a C++17 compiler via `CXX`, Boost headers via `BOOST_INCLUDE`).
Apache-2.0.
