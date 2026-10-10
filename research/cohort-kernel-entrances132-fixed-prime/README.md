# Fixed-prime refinement on PR254's 132-pair cohort word

This extension preserves PR254's physical word and changes only the exact conditional arithmetic used to price its bit supplier. It applies the fixed prime and rare-class density `2m^3/q` to the actual `m = 120`, `W = 173839` profile, keeps the complete fallback charged, extends the finite ordinary recurrence to eight levels, and tightens the outer backoff to `eta = 10^-24`.

The resulting exact value is

```text
kappa = 710465204542247142217249 / 10^27
```

This is above PR254's `71046520063283/10^17` by exactly `3909417142217249/10^27`. The physical construction does not change, and the bit supplier remains binding.

## Reproduction

From the repository root, using Python 3.11+, SymPy 1.14.0, GNU g++ with C++17, and Boost headers:

```sh
python3 -m pip install -r research/cohort-kernel-entrances132-fixed-prime/requirements.txt
python3 -B research/cohort-kernel-entrances132-fixed-prime/verify.py --output /tmp/cohort-pr254-fixed-prime
```

Choose a new output directory outside the checkout. This wrapper runs PR254's complete source regeneration and all seven native checkers, then recomputes the fixed-prime certificate. It does not accept stored PASS receipts as proof. The GitHub workflow runs that full command and separately kernel-checks `Prime.lean`.

## Inputs and scope

The parent verifier checks 20,107 local F2 columns in both directions, 232,320 pair/target response equalities, all 23,627 global five-stage columns, actual frame legality and dirty restoration, all 3,317,400 role/replica/stage assignments, the full finite invoice, the exact parent price, and its negative controls. The arithmetic extension uses the regenerated profile and checks both independent rational moment engines, all eight finite cutoff levels, all 47 strict outer inequalities, all seven margins, and rejection of the adjacent `10^-27` kappa point.

The rare-class fallback remains `32m^2` for every rare child. The counted finite coefficient remains `62447396383377201 < 2^80 < q`; selectors, charts, routes, replicas, and restoration remain charged. The fixed prime is `q = 2^127 - 1`, with exact density `3456000/q < 10^-16` for `m = 120`.

This remains conditional on PR249/PR254's all-size weighted compiler, common weighted chart, restored-row bound, routing, prime supply, precision/recovery, complex symbolic correctness, and analytic reduction. Finite checks establish the physical witness and arithmetic under those inherited interfaces; they do not prove the unconditional multiplication theorem or practical runtime. The Lean file proves prime and density facts only.
