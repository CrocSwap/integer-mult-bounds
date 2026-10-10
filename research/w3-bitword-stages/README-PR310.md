# w3 bit word: source-bound completed-bank admission

**Conditional κ = 94111687450666858500293 / 125000000000000000000000000 = 0.000752893499605334868002344.**

This is **0.18551765% above PR309** (`0.000751499335697559705920828`), the leading public construction claim checked during preparation, and **3.96366336% above PR280**. These compare conditional asymptotic exponents, not measured multiplication speed. The frontier observation is separate from this offline certificate; no priority or global-optimality claim is made.

The candidate is the supplied `w3-bitword.zip`: a cube-layer redesign, twin condensation and SAT-derived line-pair module on the PR249/source527 word. Its exact supplied word is preserved, SHA256 `a9501525563d3ec656ebf01aea9f2c9839e033563ea4a022500d68b12756ae86`. This package completes the missing source binding, bank allocation, endpoint/connector charts, finite invoice and stronger-complex-supplier admission. The retained original README and builders in `supplied/` describe the design and its initial partial-verification state; the builders are provenance only and are not required to verify the frozen word.

## Reproduce

Python 3.11+, a C++17 compiler and Boost headers are required. On Ubuntu:

```sh
sudo apt-get install -y g++ libboost-dev
python3 -m pip install -r research/w3-bitword/requirements.txt
python3 -B research/w3-bitword/verify.py --output /tmp/w3-proof
```

Use a fresh output outside the package. The verifier is network-free. For a nonstandard Boost installation, add `--boost-include /path/to/boost/include`; select a compiler with `--cxx clang++` or `--cxx g++`. A small standard-header compatibility file supports the inherited `bits/stdc++.h` includes on macOS.

Every mandatory proof stage executes. The two prerequisite source verifiers run concurrently in separate output directories. No saved PASS receipt or authenticated reuse option replaces execution. `CERTIFICATE.json` contains the mathematical admission; `VERIFICATION.json` binds it to all package source hashes and the actual fresh stages. Assertions must remain enabled, and the immutable source manifest is checked before and after the replay.

## What is admitted

- The complete eight-stage PR249/source527 prerequisite is rerun. Its actual raw word and frame table are regenerated and compared with the supplied base snapshot; the only ignored comparison field is nondeterministic elapsed seconds. The final w3 state word hash is recomputed.
- All 23,627 original global F₂ columns pass. The 1,455 freed helpers are proved absent from every actual record and are then deleted with an explicit register map; all 22,172 compact physical columns pass independently. The active helper count is 15,132. Sources and arbitrary remaining helper dirt are restored, 120 five-stage copies close, and six omitted-bridge controls are nonzero.
- All 3,473 new frame bases and ordinary annihilators have full rank and exact orthogonality. Their rational Gram inverses and complementary projector charts are computed. All 20,844 changed connector/endpoint projector charts are also constructed and checked; the maximum factor count is 342. All charged chart pivots and coefficients are below the retained 2^80 prime guard.
- Every one of the 3,026,400 active helper/replica/stage occurrences is assigned to a concrete width-120 bank slot without collision or padding. There are 105,803 banks per stage, 810,615 literal stock families and 162,123 normalized stock families. Bank endpoint tests and omission/repetition controls each cover 3,360 columns.
- The conservative normalizer remains 787. The complete bit-side selector charge is 571,950,677,600; the counted finite primitive coefficient is 58,246,212,755,400,601; the signed payload bound is 94 bits. Recursive children remain explicit.
- PR256 freshly regenerates and reference-checks the PR233 complex supplier at saving 7547/10^7. The complex label, forward/backward scalar, scratch-lifecycle, splice, router, precision and row guards are rechecked on that actual certificate. Coefficients with numerator up to five are expanded into paid repeated signed additions, with no new odd divisor. Forty exact coefficient recipes are checked. The resulting local bill is 238,393,708,927,310 < 2^48 and the physical row coefficient is 16,171 < the retained 20,161 reserve.
- The exact fixed prime q = 2^127 − 1, full rare-branch fallback, two independent rational moment engines, eight positive-gap ordinary levels, all 47 strict assembly inequalities and rejection of the adjacent 10^-27 grid point are admitted.

## Scope

This is a finite construction under the inherited all-size compiler, common weighted charts, restored rows, selectors, routing, prime supply, complex dirty-lifting, precision/recovery and analytic transfer interfaces. The checks do not establish these all-size hypotheses, a new Lean proof, an unconditional integer-multiplication theorem or a practical runtime result.

The PR249 source package is pinned to `96495746c786d6d0339dbb38c7f553d4af3f88ed`; its manifest is `86e8bc5182079c00877077c8e4c7b2690ba2486bec385c0857f1794cd2e6bedb`. PR256 is pinned to `db3f75cdc5f03f3131d48fb220f6bf1958404ff3`. Original source, notices and licenses are retained. See `PROOF.md`, `SOURCE.json` and `NOTICE.md`.
