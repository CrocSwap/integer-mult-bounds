# P111 bit decoder: an algebraic pairing-cost floor of 63

**Scoped negative result; no new kappa.** For the actual 111-port bit geometry
shipped in #545, every scalar label-factorization of its fixed decoder has
total rational pairing rank at least **63**, with arbitrarily many totals.
Nine rank-seven star totals attain the bound.

The [proof](PROOF.md) supplies a solver-free counterpart to #620's reported
SAT exclusion: a counting argument for nine terms and two small matrix
obstructions for ten terms.
Fewer terms fail by rank; eleven or more already cost at least 66. The verifier
uses only exact integer and rational arithmetic, with no SAT solver or imported
predecessor code.

The source binding matters: the same nine numerical puncture indices select
different roots in two repository utilities. The shipped geometry has **36**
ordered discounted pairs; the sorted-tetrad utility gives **44**. This package
compares all 111 live coordinates to the shipped word before using the bound.
See [the numbering check](PROOF.md#source-numbering).

From the repository root, using Python 3.10 or newer:

```sh
python3 -B research/e8-p111-pairing-floor/verify.py
```

Expected:

```text
PASS_P111_PAIRING_FLOOR: cost 63; 511 exact supports; 261121 support pairs; 12 negative controls
```

The command verifies source hashes, regenerates the deterministic receipt and
compares it with [RESULTS.json](RESULTS.json). All controls run by default.
`--write /tmp/p111-result.json` writes a fresh receipt for comparison.

An optional [independent check](independent_check.py) reads the parent's stored
coordinates directly and uses SymPy (tested with 1.14.0):

```sh
python3 -B research/e8-p111-pairing-floor/independent_check.py
```

It checks all 511 rational support ranks and 81 pairing ranks, plus all 672
dimension-three basis factorizations in its explicitly bounded calibration
domain. It does not import the main checker or its root generator.

Coverage includes all 511 nonzero label functionals, exact Q-ranks of their
reader supports, all 81 hyperplane pairings, the classification of all 261,121
ordered functional pairs, all 29 candidate count budgets of cost at most 62,
and an attaining cost-63 factorization. The 128 seeded basis changes are
calibration tests, not an exhaustive search or a proof of the nine-term lemma.

The theorem fixes the decoder matrix and requires every individual source and
reader functional to lie in its nine-dimensional label space. It does not
exclude other fitting matrices, factorizations outside that space, vector
totals, other punctures or helper improvements. Translating pairing rank to
physical copy charges additionally inherits the separately stated tree and
additive accounting premises from #446. No physical supplier, full repository
replay, new asymptotic bound or formal multiplication theorem is claimed.

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The accepted conditional
kappa at that base remains `51110230636731/31250000000000000` (#626 with #543).
Source pins and related work are in [SOURCES.json](SOURCES.json); attribution
and substantial AI assistance are disclosed in [NOTICE.md](NOTICE.md).
Local execution details and limits are in [VALIDATION.md](VALIDATION.md).
