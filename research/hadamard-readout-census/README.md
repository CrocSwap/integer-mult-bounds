# Signed Hadamard readout census and weighted recursive price

**Research construction / finite scoped optimum. No new κ.**

This extends PR997's signed four-source/four-output batch by exhausting its
eight-source-call class and permitting arbitrary repeated readouts. The
complete census covers **40,320** source orders, yields **114** minimum
profiles and **22** Pareto profiles, and certifies a minimum of **22 queries**
in that class. Two independent integer algorithms agree on every frequency.

For positive complete A-query prices sorted as a<=b<=c<=d, the exact readout
price is `4a+4b+2c+2d+min(2c,4a)`. Add twice the sum of B-query prices.
The optimum uses a 24-query profile when `c>2a`, illustrating why fewer
queries need not mean less recursive work.

Using PR997's exact A=[2,3,4,5], B=[1,2,3,4] balanced children, an emitted
24-query word uses **222 primitive calls versus 238**, **66 echo nodes
versus 72**, and the same **four dirty scratch rows**. All 22 frontier words,
the comparison word, noncommuting factor order, arbitrary dirty inputs and
literal inverses are checked. The complete recurrence prices source and
coefficient operations, every child and inverse, helper rows, control,
adapters, storage, frame changes and head return. Two extra query dispatches
remain a real expense; the benefit requires the inequality in PROOF.md.

## Reproduce

Python 3.10+; standard library only, from the repository root (absolute
script paths also work from other directories):

```sh
python3 -I -O -B research/hadamard-readout-census/test_package.py
```

Expected final markers:

```
PASS_HADAMARD_READOUT_CENSUS signed_paths=40320 profiles=114 pareto=22 queries=22 leaf_calls=222_vs_238 controls=10 no_new_kappa
PASS_HADAMARD_READOUT_PACKAGE regeneration=PASS relocation=PASS controls=4
```

The package test reproduces the certificate, runs a relocated read-only
optimized-Python check, and tests deliberate corruption of a source pin,
coverage table and restoring word, plus occupied-output preservation.
The verifier includes 624 dense basis/dirty replays and exact free-operator
checks for each attaining profile. To regenerate separately, use a **new**
output path; existing output files are refused:

```sh
python3 -I -B research/hadamard-readout-census/census.py --output /tmp/hadamard-census-new.json
```

## Pins, scope and handoff

Exact base: `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`; OS-random assignment
seed **55**, recursive interfaces. Source and context pins are in SOURCES.json.
PR997 is pinned at `b3fda8d59436103b195069a6328cbf5d74f73bc0` and its word
is replayed through the same new backend as the candidate.

The domain fixes exactly one + and one - B call per source, an arbitrary
dirty connector and exact linear additive children.
Correctness for the optimum is the independent formal-operator coefficient
identity; special maps with additional algebraic relations are excluded.
Enumeration stops after
all 40,320 source paths; readout cardinality is completely covered by the
proved eight-call upper bound. Signed prices must agree and be independent
of placement/state. The envelope excludes varying frame/travel charges,
additional source calls, output borrowing and other query alphabets.

The base selected κ is `836330098538459/500000000000000000`, from PR1094.
This package does not alter the selection or supply a new hosted supplier,
recursive moment, physical tape implementation, measured speedup or full
multiplication theorem. All-size/compiler, realization, hosting, precision,
exact recovery and analytic obligations remain as documented upstream.

PR1088 concerns a different 3x3 weighted repair; PR1012 concerns hosted
restoration deferral; PR1135 concerns rounded borrowed child contracts. This
adds complete 4x4 coverage and an arbitrary-positive-price envelope to PR997's
sampled construction. Local sprint claim and overlap checks are included.

Prepared by **Cinna Davis (@1337isnot1337)** with substantial **OpenAI Codex
assistance** in reasoning, implementation, verification and writing.
Apache-2.0. See NOTICE.md and retained predecessor notices for credit.
