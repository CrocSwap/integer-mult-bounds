# Three prescribed two-port targets: exact deletion cost

**Research note / scoped negative result. No new kappa or physical supplier.**

For the binary **nonempty** proper-star observations on signed two-ports,
the selectable three-target bound does not give the answer for every
prescribed triple. This package closes that specific distinction:

| Three distinct prescribed targets, `p>=3` original coordinate pairs | Minimum deleted nontarget inputs |
| --- | ---: |
| A triangle | Impossible at every budget |
| A three-edge path on exactly two complete original pairs | `6p-11` |
| Every other triple | `6p-12` |

At `p=2`, all four possible triples are the exceptional path and need one
deletion. Here deletion means restricting a source coordinate to zero,
equivalently removing it from the arbitrary input family. Every other
surviving input is unrestricted. It does not mean reading that coordinate
for free and subtracting it from an observation.

For example, take `p=5` and matched pairs `{0,1}`, `{2,3}`, ..., `{8,9}`.
The target path `{0,2}, {2,1}, {1,3}` needs **19** deletions, while the
ordinary path `{0,2}, {2,4}, {4,6}` needs **18**. Targets
`{0,2}, {2,4}, {0,4}` cannot all be recovered even after deleting every
nontarget coordinate. Their cycle can be toggled without changing any
vertex-star observation.

[PROOF.md](PROOF.md) gives a self-contained proof for all `p>=3`, including
the equality cases and explicit decoder construction. Its key criterion
is that each target must be a bridge of the retained graph. This criterion
also excludes arbitrary nonlinear postprocessing of the same observations.
It makes no claim about nonlinear or additional observations.

## Reproduce

From the repository root, offline, using Python 3.10+ and its standard library:

```sh
python -B research/prescribed-three-port-decoders/reproduce.py
```

Expected final marker:

```text
PASS_PRESCRIBED_TRIPLE_PACKAGE partition_triples=46348 independent_triples=12128 no_new_kappa
```

The command recomputes and checks both committed certificates without
changing them, then compares the two independently computed cost histograms.
It runs in approximately 12 seconds in the recorded Windows/Python 3.14.5
environment; this is a convenience measurement, not a performance claim.

* [verify.py](verify.py) enumerates all four-block partitions for `p=2,...,6`:
  **647,373 partitions**, **46,348 labelled target triples**, and **63 orbit
  cases**. It verifies every source coefficient of each displayed decoder
  on every surviving input. [CERTIFICATE.json](CERTIFICATE.json) records
  the minima, deletions, partitions and decoder vertex sets.
* [independent_check.py](independent_check.py) independently enumerates every
  three-dimensional binary cut subspace for `p=2,...,5`, using reduced row
  echelon form rather than graph partitions. Its orbit traversal uses group
  generators rather than first-occurrence canonicalization. It checks
  **800,002 subspaces** and **12,128 labelled triples**. The raw surviving
  vertex-incidence row span separately validates its decoder witnesses.
  [independent-results.json](independent-results.json) records its results.
* Controls cover missing, duplicated and forbidden deletions, corrupted
  decoders, a collapsed partition, the exceptional extra deletion, and the
  model-changing empty star. The independent checker also restores each
  single deleted input and requires recovery to fail. Optimization mode is
  refused by the independent checker, whose internal checks use assertions.

The largest main census, `p=6`, realizes all **19** matched-pair symmetry
types of three target edges: six endpoints cannot meet more than six
original pairs. Exhausting those shapes does not replace the proof that
the ambient-parameter formula holds for all p.

The finite census gives:

| p | Ordinary triples | Exceptional paths | Impossible triangles |
| ---: | ---: | ---: | ---: |
| 2 | 0 | 4 | 0 |
| 3 | 200 | 12 | 8 |
| 4 | 1,968 | 24 | 32 |
| 5 | 9,760 | 40 | 80 |
| 6 | 34,000 | 60 | 160 |

In general the last two counts are `4*binom(p,2)` and `8*binom(p,3)`;
the remaining triples are ordinary. The stopping rule is the end of the
listed exact finite domains, with no randomized sampling, time limit or
solver tolerance. Assignment seed **41** selected this structural-decoder
boundary; it is not used to claim distinctness for a duplicate experiment.

## What this adds and what it does not price

Sam Sung's [PR #669](https://github.com/CrocSwap/integer-mult-bounds/pull/669),
at head `7d526020fc368ce4157cd436995c2f4fcf683318`, gives the complete
selectable-target hierarchy for k=2 and, for q>=3, a criterion for prescribed
triples to attain the minimum `6q`, where `q=p-2`. It explicitly leaves
larger prescribed-triple budgets open. This result resolves **all prescribed
triples in the nonempty k=2 code**, including impossibility, the exact
one-deletion penalty, and the `p=3,4` boundary. It does not extend the
higher-k hierarchy or re-prove its full theorem. The proof here derives the
needed lower bound directly from graph components and does not import
PR #669's code or assume that unmerged result as a theorem dependency.

An attaining decoder uses three singleton-star observations, then an
invertible three-by-three binary basis change. If their selected vertex
set is A, deleting all nontarget edges incident to A leaves only target
contributions in those three observations. This is an exact information
statement. It grants the observations as inputs and **does not price their
physical production**. Puncturing changes the source family; it is not a
free implementation improvement to the selected supplier.

Source access, producing each star total, helper storage, frame changes,
copying, restoration, recursive children and whole-call hosting would all
need explicit costs before using this in a supplier. No favorable complete
invoice or global assembly is asserted. In particular, the complex supplier
is binding in the selected assembly, so an unpriced bit observation result
does not establish a larger kappa. The inherited all-size/compiler,
common-label/mutable-source, hosting, precision/tape, bit H1-H5 and analytic
obligations remain. Empty-star observations, more general k, alternative
geometry and additional nonlinear observations are outside this theorem.

## Provenance and validation

Base commit: `007664306fff84fbb1c9a1b4053b69f439764034`.
The selected certificate at that base is the maintainer-reviewed conditional
PR890 construction with `kappa=1661957774647029/10^18`. Its record, actual
T21 construction and maintainer review were inspected. Neither the selected
record nor `upstream/` is changed. Exact source hashes and dependency scope
are in [SOURCE-PINS.json](SOURCE-PINS.json); the bounded assignment and
overlap checks are in [CLAIM.json](CLAIM.json).

The reproduction command and the repository's selected-record check
(`python -B scripts/verify_selected_result.py`) pass. The unrelated full
supplier replay and repository-wide generator suite were not run: no
supplier, generator or assembly artifact is modified. Finite computation
supports the written proof; it is not formal verification of the full
multiplication theorem.

Credit to **Sam Sung / the-missionary-company** for PR #669's higher-target
hierarchy and its precise open boundary; **Joel Pulikkan / GamingPuzzled**
for PR #231's original star-family parity obstruction; and **icekylinx and
eumemic** for the paired-cube decoder lineage. The cut-code interpretation
and established graph-code literature are acknowledged in PR #669; no
literature-wide priority is claimed for that bridge.

Prepared for **woklerx** with substantial **OpenAI Codex assistance** in
mathematics, implementation, verification and writing. Separate Codex
workers supplied the independent implementation and mathematical audit;
this is not independent human review. Apache-2.0, under the repository's
[license](../../LICENSE).
