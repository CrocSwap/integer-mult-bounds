# Compact certificates for dirty circuits with actual inverse calls

A name such as `A_inverse` is an independent symbol unless the verifier
implements its relation to `A`. This package closes that specific gap in
[zxv's PR5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235), exact
head `48976daa4dce59b4867ef046da72a370e389925d`.

For two linear register programs with r independent input roles and q total
unary occurrences, **D=r+q states** suffice to certify equality of **every
returned role** under all invertible operator substitutions and all payload
dimensions. Forward and inverse occurrences share the same generator. A failed
identity yields explicit unipotent matrices and an input in dimension at most
D. No expansion of reduced words or infinite series is needed.

The [written proof](PROOF.md) constructs a finite feedback realization at
`G=I+Y`, proves the passage to arbitrary invertible matrices using a central
indeterminate, and gives sound/complete closure certificates. These are a new
repository interface and implementation of classical rational-series ideas,
not a new general weighted-automata or Magnus theorem. This is author-checked
scoped algebra, not supplier admission or a new kappa.

## Interface and use

Programs are JSON with `field: 0` for Q or a prime p <= 2^31-1 for F_p, an
ordered list of `roles`, named `operators`, and `left`/`right` instruction lists.
Every role starts as a separate arbitrary vector and every role is compared at
exit. Scalar coefficients are integers or exact fraction strings; denominators
must be invertible in the selected field. See the three [examples](examples).

| Instruction | Exact semantics |
|---|---|
| `linear`, `dst`, `terms: [[role,c], ...]` | Replace dst by the scalar sum, reading all old values. |
| `apply`, `dst`, `operator`, `direction: 1` or `-1` | Apply G or its actual inverse to dst. |
| `query`, `dst`, `src`, `operator`, `direction`, `coefficient` | Add c G^direction(src) to dst, reading the old source even when src=dst. |

The [dirty-sandwich example](examples/dirty-sandwich.json) compares two complete
programs with endpoint `(x,h,y+B A x)` and restores arbitrary dirty h. The
[wrong-order example](examples/wrong-order.json) produces a three-dimensional
counterexample; its [literal matrices and input](examples/wrong-order.witness.json)
make the noncommutation failure directly inspectable. The
[binary inverse-tail example](examples/binary-inverse-tail.json) needs a
degree-five coefficient and has a genuinely infinite formal tail.

Generate and check a certificate from the repository root:

```sh
python3.12 -B research/inverse-dirty-certificates/certify.py \
  research/inverse-dirty-certificates/examples/dirty-sandwich.json \
  --output /tmp/dirty-sandwich-certificate.json
python3.12 -B research/inverse-dirty-certificates/check_certificate.py \
  research/inverse-dirty-certificates/examples/dirty-sandwich.json \
  /tmp/dirty-sandwich-certificate.json
```

For a false identity, `certify.py` also accepts `--witness /tmp/witness.json`,
which writes the actual invertible matrices, all initial role vectors and the
endpoint discrepancy. A valid negative certificate is successfully checked
with verdict `different`; CLI exit success means valid evidence, not equality.

`check_certificate.py` imports neither `algebra.py` nor the producer. It
reconstructs the feedback equations separately and performs no elimination or
search. It shares only strict syntax and exact field arithmetic. The literal
free-group and matrix oracles are a separate implementation in `oracles.py`.
All were prepared in the same assisted research session; this is not an
independent scientific review claim.

## Evidence and scope

The deterministic replay checks:

- 504 signed-word cancellation/deletion cases over Q, F2 and F5;
- 160 scalar/apply/query differential programs against literal reduced words;
- 64 dirty-boundary, order, self-source and characteristic controls;
- 36 delayed/infinite-tail cases, including positive-characteristic witnesses;
- 324 literal invertible-matrix substitutions of the full dirty boundary;
- 16 malformed/false certificate rejections and 15 invalid-program rejections;
- three committed example certificates and two explicit matrix witnesses.

The `(A+B)^64` stress endpoint contains **2^64 distinct words** before
comparison. Its inverse-aware certificate uses **260 states and 64 invariant
rows**. It overwrites a helper identically on both sides; actual dirty-helper
restoration is checked separately. This is a compact-representation example,
not a claim about performance on every existing supplier.

The proof permits arbitrary fields. This executable supports Q and prime
fields only. Inverse calls are exact square linear operations. Extra operator
relations, rectangular types, nonlinear or rounded leaves, native realization,
phase conventions, precision, stock, hosting, tapes and the complete paid/outer
bill remain outside scope. A negative result for independently invertible
generators may disappear under additional relations. The checker does not
certify shortestness of a failure word or a minimum matrix dimension.

Normal and optimized registered replays, source/history checks and the
Git-free export are recorded in [VALIDATION.json](VALIDATION.json). Finite tests
corroborate the universal written proof; no Lean or independent human review is
claimed. No selected record or predecessor source is changed.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/inverse-dirty-certificates --check-only
python3.12 scripts/research_package.py --package research/inverse-dirty-certificates
python3.12 -W error -B research/inverse-dirty-certificates/verify.py
python3.12 -W error -O -B research/inverse-dirty-certificates/verify.py
```

One direct replay took about 16 seconds on the recorded host. Default replay
does not write package files. `--write-examples` is an explicit regeneration
mode; `--quick` is a development smoke test and is not the registered replay.
The direct verifier is standalone and works in a Git-free package export.
The registered runner additionally validates the pinned Git provenance.

## Open next questions

1. Bind one existing inverse-bearing native word to this grammar while
   preserving every input and returned helper. Compare against its existing
   reduced-word oracle at an exact source head. The remaining blocker is the
   adapter's source/type/phase contract; this package does not infer it.
2. Add one other explicitly named relation model, such as commuting pairs.
   Start with a normalization theorem and a noncommuting rejection fixture.
   Quotienting the present transition matrices without a new proof is unsound.
3. Reduce checker path recomputation on a larger real adapter. Compare identical
   closure equations and complete endpoints before changing representation;
   exact rational coefficient growth remains an unmeasured scaling constraint.

These are released questions, not claims on further work. Details and the scope
change from the generic formal-interface card are in [TASK.json](TASK.json).

## Credit

Prepared by **Krzysztof Wójt (@krzysztofwojt)** with substantial **OpenAI Codex
assistance**, including a separately delegated exact-oracle implementation.
Apache-2.0. Classical sources are cited in [PROOF.md](PROOF.md).

Credit **zxv's PR5235** for the compact independent-operator register bridge,
invariant certificates, unipotent witnesses and the explicit inverse-frontend
question. Its dirty-echo lineage (**androolloyd**, **Chafik Boukhalfa/chafreaky
#628**, **Ali Romman #621**), **Cinna Davis #4100/#4088**, **ToikY**'s free-word
tensor audit, **Sagar Thakrar #3687**, **roger-sato #3693**, and the dirty-phase
audit following **Charles Bethin #1278** retain their results and attribution.
No predecessor source code or archived artifact is copied or modified.

The fresh main base is `ff3cc58e370d0f678e529246f8c73e8094e18fcf`, priority
revision 7. [SOURCES.json](SOURCES.json) distinguishes ancestor provenance from
the contextual pending predecessor, which is not a replay dependency.
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5236#discussioncomment-19147346)
records live overlap and status. The checked corpus and targeted searches are
evidence of due diligence, not coverage of unpublished work or arbitrary
historical diffs.
