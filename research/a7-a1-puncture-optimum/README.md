# Sharp COPY71 for the coordinate-frame A7+A1 puncture

For the fixed A7 weights plus A1 normal family, remove the eight E8 lines
`e0 +/- e1, e2 +/- e3, e4 +/- e5, e6 +/- e7`. The exact separate-term COPY
minimum on the remaining 112 lines is **71**, allowing arbitrary independent
complex row shifts and allowing zero terms. The rational witness has ranks
`(0,8,9,9,9,9,9,9,9)`.

This is a scoped written proof with exhaustive finite binary lemmas. It
answers the specified-puncture question in Adam Gall's
[PR2062](https://github.com/CrocSwap/integer-mult-bounds/pull/2062), whose
P120 optimum is cited, not replayed. The COPY71 floor excludes beating the
ordinary P112 COPY64 comparator with these normals and this puncture.
No supplier, full recursive moment, new kappa or selected-frontier change
is claimed.

## Proof and evidence

[PROOF.md](PROOF.md) gives the complete complex-parameter argument. The
puncture creates a two-dimensional partner space in 254 binary-plane cases,
so the old dimension-one argument cannot be transferred. New finite lemmas
bound the total row-support deficiency by ten, giving `81-10=71`.

The standalone standard-library verifier constructs the roots and puncture
directly. It imports no predecessor code and runs no predecessor verifier.
Its complete finite evidence includes:

- All 43,435 planes in the nine-dimensional binary character space, with
  304,045 comparisons of compatibility-mask and direct-annihilator calculations.
- All 511 nonzero characters for each of seven conflict sets, including
  the six independent exceptional root labels used by the proof.
- The puncture-preserving symmetries needed to cover all eight anchor columns.
- All 12,544 equations for each of three successful endpoint fixtures,
  including a genuinely nonreal shift. The attaining invoice is computed
  directly from the actual binary support-pair submatrices.
- Rejection of a deleted A1 term and a single corrupted coefficient, and
  a discriminator showing that the old dimension-one premise fails here.

The universal complex-shift statement uses the written deficiency proof;
it is not inferred from a sample of scalar parameters. No receipt is
handwritten or committed. Each run emits its computed evidence and SHA256
hashes of the package's regular files to stdout.

## Reproduce

From the worktree root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/a7-a1-puncture-optimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/a7-a1-puncture-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/a7-a1-puncture-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/a7-a1-puncture-optimum --check-source-history
```

Another CPython 3.12 installation can replace the absolute interpreter path.
Expected scientific marker:

```text
PASS_A7_A1_P112_COPY71 planes=43435 annihilator_checks=304045 cost=71
```

Both registered commands have 120-second limits. Default replay writes no
files. [VALIDATION.md](VALIDATION.md) records actual local results and limits.

## Scope and implementation constraints

The theorem fixes the normals, puncture, all-pairs identity and additive
separate-term pairing-rank charge. The all-nine-active optimum, other
punctures, shared copies and masked identities are outside scope. Native
acquisition, delivery, restoration, frames, hosting, precision and compiler
costs remain unpriced. No selected cold replay, Lean or Docker build was run.
Independent human and formal proof-kernel review are unclaimed.

The verifier has no recursion, dynamic imports, subprocesses or network
calls. All functions fit within 60 physical lines. Loops are bounded by 120
root lines, 512 characters, seven conflict sets, 43,435 planes, nine matrix
columns or eight symmetry steps. Binary elimination accepts at most 120
rows and 120 columns. The plane search visits at most `512^2` candidate
character pairs. Checks use explicit exceptions and remain active
under optimization.

Power of Ten rule 3 deviation: CPython allocates managed objects during the
finite calculation. The largest retained compatibility table contains
`7*512` integers of at most 512 bits; live root and matrix collections have
at most 120 entries per axis. Temporary forbidden-label tuples have at most
112 entries and are discarded after each calculation. A fixed-allocation
rewrite would require a different runtime. Review these bounds before
allowing variable geometries. Warning-strict normal and optimized runs
provide the available Python diagnostics; no additional static analyzer
or repository-wide configuration change is introduced.

## Open next questions

- Can a frame puncture in a different orbit relative to these A7+A1 normals
  lower COPY below 71? Start by deriving its reader ranks and conflict-space
  dimensions. This result covers only the coordinate-pair frame; changed
  partner dimensions block reusing the proof without new lemmas.
- What is the optimum for this puncture if all nine terms must be active?
  Start with equality in the deficiency-ten bound and price an exact active
  witness. The present attainer has one zero term, so no active optimum is
  supplied. Its physical relevance still needs a fully paid consumer.

## Sources and credit

This contribution was produced by Nick Petalas. New work is Apache-2.0.
Credit joaqcoo [#1224](https://github.com/CrocSwap/integer-mult-bounds/pull/1224)
for the family and complete row-shift normal form; Adam Gall
[#2062](https://github.com/CrocSwap/integer-mult-bounds/pull/2062), head
`8344a5fc1eb643aca6a21bc745d824a38f449e39`, for the canonical model,
unpunctured theorem and explicit puncture question; Philipp / mightyOil
[#1248](https://github.com/CrocSwap/integer-mult-bounds/pull/1248) for the
deficiency-space method; DreamingOfClouds #446/#595/#717 for the decoder
and separate COPY model; and the retained E8 geometry lineage.

Canonical base is `ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`, priority
revision 7. [SOURCES.json](SOURCES.json) pins predecessor/context prose;
none is executable input. [TASK.json](TASK.json) records the changed card
scope and overlap coverage. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19146127)
preceded the new finite computation. Frozen predecessor packages are unchanged.
