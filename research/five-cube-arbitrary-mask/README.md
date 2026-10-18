# Every Boolean one-mask five-cube code retains the copy floor 32

**Research note / scoped structural negative result. No new kappa.**

For the five-cube Gram `G[x,y]=2(4-d(x,y))(2-d(x,y))` and the binary decoder
`B[x,y]=1+p(x)+p(y)`, every exact factorization with both factors in the common
code `span_F2{1,p,h}` has total rational pairing rank at least **32**, for
**any Boolean mask h and any finite number of terms**. The known two parity
totals attain 32. This removes the degree-at-most-two restriction of PR1222;
it also covers more than the three terms allowed by PR1177.

The [proof](PROOF.md) reduces the two parity orthogonal bases, partitioned by h,
to one- and two-dimensional components. Each pays twice its dimension. It
also gives an exact term-rank formula and five small binary-rank potentials
that certify the cost for arbitrary component multiplicities. It does not
enumerate all Boolean masks or infer a universal result from sampling.

Under the inherited additive stage/copy ledger, even granting every other
required expense zero leaves `D <= (s-1)*32-s*32 = -32` for all `s>=3`.
This closes one decoder mechanism in that model. It does not change the
selected supplier, establish a physical realization, or improve kappa.

## Reproduce

From the repository root, Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/five-cube-arbitrary-mask
```

Expected final marker:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/five-cube-arbitrary-mask outcome=negative-result
```

The hook runs both implementations and the package failure tests. Standalone
commands also work with Python 3.10 or later:

```sh
python3 -I -B research/five-cube-arbitrary-mask/verify.py
python3 -I -B research/five-cube-arbitrary-mask/independent.py
python3 -I -B research/five-cube-arbitrary-mask/test_package.py
```

The primary marker includes `masks=324 ranks=15876 edges=125440 controls=9`.
The second includes `degenerate_lifts=128`. The primary uses integer elimination;
the second reconstructs the Gram from Walsh characters and uses exact Fraction
elimination, importing no primary or predecessor code. Both implementations
were written by the same AI-assisted author; this is implementation diversity,
not separate authorship or independent human review.

The [certificate](CERTIFICATE.json) records every fixture rank, component
multiplicity and potential. Fixtures cover all 256 Boolean functions on the
seed-selected coordinates `(0,1,4)`, all squarefree monomials, both parity masks
and 42 seeded truth tables, with duplicates removed. They cover degrees through
five, but are not an exhaustive mask search. All 125,440 component-graph edges
and all 128 lifts of the four rank-two code cases are checked. The universal
statement comes from the written two-projection proof.

Controls address omitted/wrong factors, nonorthogonal Grams, wrong-field rank,
forged potentials, a singleton outside the common code, endpoint angles and
masked-only identities. A changed all-ones Gram retains the binary decoder at
cost two, showing why the geometric hypothesis matters. External tests corrupt
receipts and sources and check optimized execution in a read-only relocated copy.
`--write-certificate PATH` creates an exclusively new receipt.

## Scope, provenance and overlap

Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. OS-random assignment **42**,
structural decoder track. [TASK.json](TASK.json) records the three candidate
tasks, diversification, stopping rule and the change from the catalogue's
complex E8 example to a structural five-cube question. No pinned coordination
issue existed; the donor's local-claim fallback was used.

The accepted result at that base is conditional **0.001672660197076918**,
PR1094 with PR589 on PR555. The reviewed source/certificate bindings were
checked by `scripts/research_baseline.py`; the complete selected-supplier cold
replay was not run for this separate theorem. Existing files, `upstream/`,
the selected result and predecessor packages are unchanged.

[SOURCES.json](SOURCES.json) pins the incorporated predecessor proof, README
and attribution notice by Git blob and SHA256. The selected record and task
catalogue are historical provenance. No pending implementation or theorem is
imported. Pending scope comparisons were read at these exact heads:

| Work | Head | Distinction |
|---|---|---|
| [PR1177](https://github.com/CrocSwap/integer-mult-bounds/pull/1177), Ross Richardson | `e878ef36109bc6d7e21e62d03c22d8ec36f6f936` | Arbitrary masks, at most three terms |
| [PR1222](https://github.com/CrocSwap/integer-mult-bounds/pull/1222), Hanson Sun | `c6fe323581d3803a080b000b263a07edf2b00b54` | One common quadratic mask; includes a separate rank-cap theorem |
| [PR1482](https://github.com/CrocSwap/integer-mult-bounds/pull/1482), Hanson Sun | `4faed28a0e6c8a0aa5faa87b281b9373fb5d8403` | Two signed coordinate-product masks and a constrained-cost improvement |

Overlap coverage and limits are recorded in [OVERLAP.json](OVERLAP.json).
No novelty claim is based solely on a title search or a different seed.

Excluded: different reader/source codes, multiple extra masks, arbitrary
functions of the two cell bits, masked-only identities, nonlinear or interactive
data messages, changed Grams without the proved parity-basis property, and
changed copy/stage accounting. The general two-basis lemma is conditional on
its stated real orthogonal-basis hypotheses. Source access, helpers, frame
changes, restoration, recursion, physical hosting, precision/tape, all-size
compilation, bit H1-H5 and analytic transfer are not discharged.

## Open next questions

Two independent extra masks create finer partitions for which the
two-projection reduction need not preserve every support. The useful first
step is an exact small example where the third partition crosses a generic
two-dimensional component; compare its complete pairing bill before attempting
a supplier. PR1482 supplies finite two-mask examples, but no general floor for
arbitrary mask pairs. This requires a changed argument, not more one-mask trials.

Different reader and source mask codes are also outside the proof: a basis
change preserving one side's cells may not preserve the other side's supports.
A bounded first step is to fix two cubic masks and certify the resulting
512-state coefficient graph. A cheap algebraic witness would still require
source-access, frame/restoration and complete recursive pricing. Structured
versions of these questions and blockers are in TASK.json.

## Credit

Credit **Martin Rv / @martinxxx9, PR1046**, for the affine five-cube theorem and
its attaining totals; **Ross Richardson, PR958/1177**, for the quadratic port
geometry, stage accounting and arbitrary three-term analysis;
**Joel Pulikkan / @GamingPuzzled, PR231**, **icekylinx** and **eumemic** for the
paired-port lineage; and **DreamingOfClouds**, **Jacob Sussman** and
**Zhihao Chen** for the retained copy/frame/accounting interfaces. The pinned
predecessor NOTICE retains their original details. PR1222 and PR1482 are credited
above; neither is silently treated as accepted frontier work.

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in the mathematics, proof, both implementations, checks and writing. Apache-2.0.
No subagents, independent human review, proof-assistant verification, hosted-CI
success or full multiplication theorem are claimed.
