# Fixed-prime refinement on PR259's 518-entrance multicut word

This arithmetic extension keeps PR259's complete physical transcript, 518 pivot entrances, multi-cut frame geometry, bank assignments, routes, replicas, and finite invoice. It changes only the rare-class density and the finite ordinary recurrence used to price the bit supplier.

The exact endpoint is

```text
kappa = 711029389987426878345881 / 10^27
```

This improves PR259's `142205877210807/200000000000000000` by exactly `3933391878345881/10^27`. It adds no physical DAG saving.

## Method and certificate

For `m = 120`, fix `q = 2^127 - 1` and use `rho = 2m^3/q = 3456000/q`, while retaining the complete `32m^2` fallback for every rare child. The verifier consumes PR259's newly regenerated exact profile and invoice. It checks two independent rational moment interval engines, eight ordinary finite cutoff levels, all 47 strict outer constraints and seven margins, and rejection of the adjacent `10^-27` endpoint.

The fresh invoice coefficient is `62639910650427201 < 2^80 < q`. The 200-factor maximum chart, 787 normalizer bound, selector calls, signed-prefix bill, and all other invoice entries remain charged and are checked. `Prime.lean` certifies the prime and density facts only; it does not prove the multiplication theorem.

## Reproduction

From the repository root, using Python 3.11+, SymPy 1.14.0, GNU g++ with C++17, and Boost headers:

```sh
python3 -m pip install -r research/multicut-kernel-condensation/requirements.txt
python3 -B research/multicut-kernel-condensation-fixed-prime/verify.py --output /tmp/multicut-fixed-prime
```

Choose a new output directory outside the checkout. The wrapper runs PR259's source regeneration and all seven native checkers, then recomputes the fixed-prime certificate from the fresh exact-price and finite-invoice receipts. It does not accept stored PASS receipts as proof.

The added Actions workflow runs that command and kernel-checks `Prime.lean`. The repository verification workflow covers every `make verify` group under Python 3.11, 3.13, and 3.14, the ranked-pair finite replay, and the historical, Gaussian, and matrix formal jobs.

## Physical profile and scope

The verified normalized profile has `m = 120`, stock `173435`, `3,956,840` children, rank mass `20,777,000`, deficit `35,200`, and maximum child rank `50`. The literal invoice retains 40 replicas, stock `867175`, `19,784,200` children, and rank mass `103,885,000`; selector, chart, routing, boundary, bridge, and restoration costs remain charged.

The result inherits PR249 and PR259's conditional all-size compiler, common weighted chart, restored-row bound, routing, prime supply, precision/recovery, complex symbolic correctness, and analytic reduction. The physical word and arithmetic are finitely replayed, but this is not an unconditional integer-multiplication theorem or a practical-runtime claim.
