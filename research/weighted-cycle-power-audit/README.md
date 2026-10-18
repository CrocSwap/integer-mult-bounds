# Weighted-cycle power audit

**A balanced cycle product is insufficient to preserve a unit-weight inverse
bound.** This scoped negative result audits the operator hypothesis in
[PR803](https://github.com/CrocSwap/integer-mult-bounds/pull/803), without
contradicting its correctly stated theorem or changing the selected bound.

The explicit 256-entry witness has every weight within 1/16 of one, exact
cycle product one, and spectrum on the unit circle. For `P(z)=z-33/32`,
the scalar circle gap is 1/32, but the matrix inverse norm lies strictly
between **1936 and 1937**. The inherited unit-weight degree-only estimate
would be **800** (or **160** using its zero interior-root count).

[PROOF.md](PROOF.md) establishes the all-length counterexample family,
the exact cumulative power factor K, its sharp worst case under local
magnitude tolerances, and a sufficient perturbation guard. For `P(z)=z-a`,
it identifies the local-error threshold: below the circle gap, a uniform
bound holds; at the gap, worst-case growth is linear in length; above it,
balanced cycles can grow exponentially. The corrected
transfer pays **K times** the inherited Wiener bound. None of these claims
improves a multiplication exponent or prices a rounded implementation.

The note also gives the **exact largest inverse norm** for a linear
polynomial over all balanced cycles of a specified length and local weight
tolerance, with rational attaining weights. At length 256 and tolerance
1/16, this maximum lies between **2164 and 2165**, above the simpler
two-block witness. The formula treats complex phases as well as real weights.

## Reproduce

From the repository root, with Python 3.10 or later and no third-party
dependencies or network access:

```sh
python -B research/weighted-cycle-power-audit/verify.py
```

Expected result: exit zero and `PASS: exact weighted-cycle power audit`,
with 1,377 generated matrix cases / 9,990 signed-power samples, 72 dense inverses /
504 independent basis solves (24 cases in each error/gap regime),
240 perturbation cases (155 admitted,
85 inconclusive), 48 sharp-cap witnesses / 2,600 direct path products,
96 dense sharp-inverse witnesses plus three length-256 affine checks,
108 dense complex-phase inverses,
18 named admission and failure controls, and primary inverse-norm floor 1936.

The read-only default recomputes and compares `EXPECTED.json`; it does not
silently regenerate a passing receipt. `--write-receipt` is an explicit
maintenance operation, not verification. Exact source blobs and SHA256 pins
are checked first. Paths resolve relative to the script, so it can also be
run from another working directory.

Proof-relevant mutation and package-integrity checks:

```sh
python -B -m unittest discover -s research/weighted-cycle-power-audit -p test_package.py -v
```

Expected result: 11 tests pass, including rejection of a corrupted source,
wrong blob pin, changed result/domain receipt, omitted norm factor, edge-only
factor, wrong weight order, optimistic perturbation guard, a missing cycle
denominator, irrational magnitude ratios outside the norm oracle's domain,
and lost failure detection under optimized Python.

## Scope and reproducibility

- Exact base: `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`.
- Audited PR803: `d213ac12d4a1ab8f717d942e844df318ceb395fb`.
- Preceding PR692 resolvent: `c5b53a5e80372a1fae9830d8dcf21aaabce3f729`.
- Seed 71 selected the operator-hypothesis audit and the primary eta.
  [CLAIM.md](CLAIM.md) records candidates, overlap review and timing.
- [DOMAIN.json](DOMAIN.json) specifies all finite coverage and stopping
  rules. The ten threshold cases cover eta from 1/2 down to 1/1024, with
  lengths up to 13,356. Large cases verify exact scalar inequalities, not
  dense matrices of those dimensions. There is no random finite search.
- [SOURCES.json](SOURCES.json) pins eight byte-exact predecessor/context
  files. [NOTICE.md](NOTICE.md) credits their authors and classical tools.
- [OVERLAP.json](OVERLAP.json) records the final PR/source refresh, including
  concurrent PR846 and the newly selected #799 frontier as context.
  [VALIDATION.json](VALIDATION.json) and `evidence/` record the isolated replay
  and proof-relevant package tests; no remote CI success is inferred.
- `exact.py` contains the cycle-prefix certificate and affine solver;
  `oracles.py` independently supplies dense matrix arithmetic;
  `verify.py` connects them and records exact evidence.

The universal statements rest on the written proof, not the finite replay.
PR803's analytic coefficient estimate remains an inherited premise.
Human mathematical review remains open. The preserved selected-result file
is base-commit context, not an endorsement of a new frontier. No change is
made to `upstream/`, global generators, selected certificates, or schedules.

Prepared for **William Lawyer**, with substantial **OpenAI Codex assistance**.
Apache-2.0. This package is a research note / scoped negative result and
independent exact verification.
