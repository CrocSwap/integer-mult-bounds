# Independent census of dirty fanout star queries

**Independent verification and a scoped equality-count result; no new κ.**

[PR889](https://github.com/CrocSwap/integer-mult-bounds/pull/889) proves a
`2k+2` query minimum for its one-connector, `k`-output dirty fanout model.
This package independently reconstructs its exact integer state, exhausts the
shortest-word domain through five outputs, and characterizes **all** minimizers:

| Outputs `k` | Minimum queries | Number of minimum-length labelled words |
|---:|---:|---:|
| 1 | 4 | 4 |
| 2 | 6 | 24 |
| 3 | 8 | 288 |
| 4 | 10 | 5,760 |
| 5 | 12 | 172,800 |

The [written proof](PROOF.md) gives `2(k+1)(k!)²` for every `k>=1` in this
alphabet. Each output has one query between the connector's two updates and
one outside, with signs fixed by the connector excursion. The finite census
checks that count independently; it does not use the classification
to generate words or decide state transitions. This is not a formal proof in
a proof assistant or a lower bound for unrestricted circuits.

## Reproduce

Python 3.10+ and the standard library suffice, offline and outside a Git checkout:

```sh
python3 -I -B research/dirty-fanout-star-census/verify.py
```

Expected:

```text
PASS_STAR_CENSUS k=1..5 minima=4,6,8,10,12 counts=4,24,288,5760,172800 emitter_cases=60 star_cases=5 controls=6 no_new_kappa
```

The default command compares every byte of the deterministic recomputed
[certificate](CERTIFICATE.json), including its source-manifest digest, and
does not write files. `--write` explicitly regenerates that certificate.
`python3 -I -O -B research/dirty-fanout-star-census/test_package.py` runs ten
additional failure-sensitivity and relocation tests. See [validation](VALIDATION.md).

## What is checked independently

Only signed `z += Bx` and `y_i += A_i z` queries are allowed. The source,
connector and outputs are distinct; each query preserves its source and
restores private scratch. Correctness is universal over exact additive linear
maps and arbitrary dirt. The state records the connector coefficient `t` and,
for each output, its coefficients `(a_i,b_i)` on `A_i z_initial` and `A_i Bx`.
Acceptance requires `t=0` and every pair equal to `(0,1)`.

For each `k=1..5`, the horizon is exactly `0..2k+2`, with all `2(k+1)` signed
letters admitted at every step. The checker quotients states by output-label
permutations but retains **labelled-word multiplicities** as arbitrary-precision
integers. It prunes only with a proved lower bound on the number of remaining
queries; it does not assume the optimum or equality classification to prune.
An unquotiented, unpruned implementation agrees at every length for `k=1,2`.
This is complete compressed enumeration of the stated finite domain, not a
random sample or a replay of only the predecessor's chosen words.

The only executed predecessor routine is its literal instruction **emitter**.
A new sparse free-associative-algebra interpreter checks all initial source,
target and scratch columns simultaneously, retaining factor order over the
integers. It checks 60 complete recursive words (fanouts 1..5, common lengths
1..4, asymmetric branch lengths 1..3, and all three predecessor schedules)
and their literal inverses. Five one-factor batches separately pass strict
star-alphabet, one-connector, endpoint and minimum-length admission.
No predecessor interpreter, census, invoice, leaf-count function or receipt is
imported. These checks do not audit PR889's physical invoice or rounded maps.

Six built-in controls expose missing connector restoration, a wrong output
sign, a changed common factor on return, omitted dirty cancellation, aliased
ports, and an incorrectly commuted factor product. The package tests also
detect lost quotient multiplicities and an endpoint-preserving extension that
uses forbidden ports. A signal-only or commuting scalar fixture would miss
some of these failures.

## Pins, attribution and scope

Original base: `91a2094f2e022930069e8cfdc810a3ea1b81cd09`.
Refreshed submission base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`.
Subject: PR889 at `e2021d1c9e06948528cbc0a8fd7079b671da981d`.
[SOURCES.json](SOURCES.json) pins all three verbatim source/reference files by
SHA256 and Git blob identity; their original paths and notice are retained.
The subject may be reviewed without merging PR889 first. The source snapshot
is a reference/emitter dependency, not an assertion that the entire PR is
approved. [CLAIM.json](CLAIM.json) records OS seed **79**, task selection,
overlap review and the stopping rule.

Credit **CubeJerry / PR889** for the batched interface and sharp query minimum,
and **Chafik Boukhalfa / PR628** for its dirty-commutator lineage. The new
contribution is the independently checked complete minimizer census and bounded
literal-emitter correspondence. PR896's nonlinear binary evaluator proof and
PR934's binary multi-source query model have different scope. PR934 extends
PR889's one-source construction; it does not count all shortest labelled words
in this one-source model, which is the additional evidence supplied here.
Prepared for **Ross Richardson (@RossRichardson)** with substantial OpenAI Codex
assistance, including a separate delegated proof derivation and code review.
No independent human review is claimed. See [NOTICE.md](NOTICE.md) and [LICENSE](LICENSE).

The original base selected conditional κ=`1661634653669567/10^18`. During
verification, upstream selected PR890 at `1661957774647029/10^18`; refreshed
main was incorporated and its selected-record checks passed. This package
changes no selected certificate or upstream source. The abstract query contract,
all-size address/compiler correspondence, native source access and hosting,
precision/tape realization and analytic transfer remain separate obligations.
There is no new supplier, cost saving, unrestricted optimum, or multiplication
theorem claim. The finite emitter checks do not establish all-size compiler
correctness, and the census does not apply to rounded nonlinear leaves.
