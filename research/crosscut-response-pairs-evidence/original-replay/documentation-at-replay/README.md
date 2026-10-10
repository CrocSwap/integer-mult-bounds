# Early-cut pairs and connected-block retiming

This additive package improves the conditional exponent saving to

```
kappa = 711457853376510082124745 / 10^27
      = 0.000711457853376510082124745
```

The exact gain over PR265 is `425611242438074456938 / 10^27`, approximately
0.05986% of its exponent saving. This is a finite construction under the same
inherited all-size hypotheses. It is not an unconditional multiplication
theorem or a measured practical speedup.

The package retains all 518 original entrances, adds 369 response pairs at the
earliest cut (372 additional entrance dimensions), preserves PR263's 25 gate
retimings, and jointly retimes 29 connected blocks containing 57 ADDs. The latter
changes the rank distribution without changing total calls or rank mass.
All changes are composed into one emitted word and priced together.

| Quantity | PR265 | This package |
|---|---:|---:|
| Pivot entrances | 518 | 887 |
| Entrance dimension | 1,344 | 1,716 |
| Normalized stock | 173,435 | 173,311 |
| Normalized child calls | 3,956,800 | 3,970,720 |
| Normalized rank mass | 20,777,000 | 20,762,120 |
| Deficit | 35,200 | 35,200 |
| Conditional kappa | 0.000711032242134072007667807 | 0.000711457853376510082124745 |

More calls are fully charged; the saving follows from the complete rank profile,
not from comparing call counts alone. There are 40 physical replicas and five
stages. Literal stock is 866,555, with 3,317,400 helper/replica/stage bank
assignments and 916 exact candidate charts.

## Reproduce

Use this package in the repository at PR265 commit
`fc00fcf07a554ff6847b2a8764ecc26f5a99542a`. Python 3.11+, SymPy 1.14.0,
a C++17 compiler and Boost headers are required. Run with assertions enabled
and a fresh output directory outside the checkout. Replay needs no network.

```sh
python3 -m pip install -r research/crosscut-response-pairs/requirements.txt
python3 -B research/crosscut-response-pairs/verify.py --output /tmp/crosscut-replay
```

The default compiler is `g++`. The local verification used Python 3.14,
Apple Clang with libc++, and Boost 1.87. For macOS, put the supplied `stdc++.h`
in `INCLUDE/bits/stdc++.h` and link `INCLUDE/boost` to the Boost header directory:

```sh
python3 -B research/crosscut-response-pairs/verify.py \
  --output /tmp/crosscut-replay --cxx clang++ --boost-include /path/to/INCLUDE
```

The wrapper first regenerates PR249 from retained source, recompiles all seven
native checkers, and completely reproduces PR265. It then constructs the new
word, binds both retiming stages through complete scalar-core alignment, checks
exact integer source spans and rational frame bases/annihilators, and reruns all
native legality, prefix, bank, global-column, pricing and finite-invoice checks.
Finally, two retained rational moment engines verify the finite bootstrap,
all 47 strict outer constraints, seven margins and adjacent-grid rejection.
No stored PASS receipt replaces a fresh execution.

The final word must have SHA-256
`8593fa0359aa13b26ede7490f500f239c97d238df2730496a9ac29bcafd7b4ae`.
Every fresh mathematical receipt must match `expected/`. Only timing and a
generated source-stream path are omitted from receipt comparison. Source
manifests are checked before and after execution. A successful run writes
`VERIFICATION.json` with `PASS_SOURCE_BOUND_CROSSCUT_RESPONSE_PAIRS`.

`PROOF.md` gives the simultaneous donor-sharing and retiming arguments;
`NOTICE.md` credits inherited and contemporaneous public work. `discovery/`
contains the search scripts, which nominate witnesses but are not acceptance
checks. The search uses NumPy in addition to SymPy; replay does not need NumPy.
No global optimum, upstream acceptance, CI success or new Lean proof is claimed.

## Contemporary comparison

At the October 10, 2026 queue check, PR266 reported
`0.000711403723709732`, PR267 reported
`0.000711074913688782665281379`, and PR268 reported
`0.000711191385398487`. This candidate exceeds those posted endpoints, including
PR266 by approximately 0.00761%. These comparisons use their public claims;
their independent packages were not replayed here. PR266's early-cut pairs and
PR267's chronological donor sharing overlap this run's search directions; no
priority claim is made for those ideas. The baseline replay and strict gain
assertion are against pinned PR265.
