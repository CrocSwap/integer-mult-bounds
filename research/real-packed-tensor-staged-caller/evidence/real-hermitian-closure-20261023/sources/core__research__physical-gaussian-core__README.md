# Physical normalized Gaussian compression cores

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
Apache-2.0 for this implementation; I retain the source-specific notices
and the RaD CC0 license with the analytic inputs.

I implement one complete Gaussian principal-window compression core on
the retained fixed tapes. I generate the global coefficients, prepare
exact old-H Schur pages, execute both interior passes around the boundary
solve, and normalize the complex core back to the target grid. I give
the quantified production argument in [PROOF.md](PROOF.md), conditioned
on the pinned Gaussian and word-multiplication premises.

For a source window of m rows, I charge the online consumer at

    O((m+m*w²/d+w²)*p*log²(p+2)) time,
    O((m+m*w²/d+w²)*p) space.

I also charge polynomial(t,p) exact setup time and scratch. An isolated
window cannot absorb that workspace into its payload. The retained
complete bulk tensor supplies the separate asymptotic amortization.
The enclosing catalogue, halo/router, expansion and CRT/integer caller
remain open here. I leave the selected frontier unchanged.

I preserve one global rounded H, including its exact rational within-cell
similarity, directed cross-cell entries, diagonal1 and physical period
cuts. I cancel similarity weights only inside exact Schur setup, invert
the original truncated Toeplitz blocks, and restore the weights in the
correction. For online local applications I use Chafik Boukhalfa's
[PR489](https://github.com/CrocSwap/integer-mult-bounds/pull/489)
two-convolution factorization. Its dense local q-model never replaces
the old matrix in Schur setup.

## Interfaces and evidence

`Preparation.run_production` derives P=32768p and the source bandwidth,
checks the retained domain and sufficient locality margins, then emits
a protected structured page. `Core.run(page, halo)` consumes borrowed
page/input tapes and returns the normalized core. Both owners restore
their scratch and borrowed origin heads. The caller must consume each
protected output before reusing its producer.
I state approximation and cost guarantees for pages from the matching
production preparation; framing checks alone do not certify arbitrary
factor advice.

`run_explicit` exposes the same preparation at declared finite parameters.
I use it for bounded execution checks; smaller grids do not inherit the
production approximation guarantee. The production metadata check uses
p=16384 and derives P=536870912 without materializing that enormous grid.

I execute three complete finite joins: an interior window, a window
crossing the physical period, and clipped boundary pieces with a gap in
C selection. I compare the pages with independently computed old-H
Schur factors and the nonzero outputs with staged and dense exact models.
I also check a closed public preparation/consumer lifecycle,15 fault and
ownership controls, reuse, signed convolutions and coefficient intervals.
[EVIDENCE.md](EVIDENCE.md) separates those checks and the unrun production
sizes.

The new owners call the actual [PR3787](https://github.com/CrocSwap/integer-mult-bounds/pull/3787)
word API with a fixed crossover4096. The finite Gaussian packets use its
Karatsuba branch. PR3787's retained checks exercised its FFT branch above
its default16 cutoff. I retain that distinction and the acyclic ring
dependency; I use no host arithmetic callback in the physical core.

## Reproduction

Use Python3.12 and the standard library from the repository root:

```sh
python3.12 scripts/research_package.py --package research/physical-gaussian-core --check-only
python3.12 scripts/research_package.py --package research/physical-gaussian-core
python3.12 scripts/check_research_commit.py --package research/physical-gaussian-core --check-source-history
```

I group 12 checks into eight commands in [VERIFY.json](VERIFY.json), with
a 540-second largest command allowance and a 1200-second sum of timeouts. The verifiers use
explicit exceptions under isolated, optimized Python. I authenticate the
whole word export, the complete PR489 reference package and the analytic
inputs before importing one shared physical cohort. The official export
supports replay outside Git. The public receipt records the final commit,
export hashes and hosted result.

## Sources and coordination

I started from canonical main20ecf2891d80b5acf18d980b2164fb44ea7faa90,
priority revision6, and recorded the five-point gate before implementation
in [Discussion3664](https://github.com/CrocSwap/integer-mult-bounds/discussions/3664).
[TASK.json](TASK.json) retains the original card, scope and overlap coverage.

I pin PR3787 at9b5474f47b0ea9a3c76bb5b1b577fb36704815e0, including
corrected PR3709, and Chafik Boukhalfa's PR489 at
8922e3b3f0fd7772b0fb42028eb2532984c3ab42. I credit his PR481 boundary
and PR486 halo predecessors, the RaD project (hipotures) Gaussian/bulk
reports, Mason Hale's interval reference, Dugongue's scalar ABI precedent,
the classical FFT/Karatsuba/q-calculus identities and the inherited
Harvey–van der Hoeven, OpenAI manuscript and Douglas Colkitt framework.
I retain the nested notices and substantial AI-assistance disclosures.
These are author checks and a conditional algorithmic argument; I claim
no independent human or formal-kernel review.

## Open next questions

- Can the physical expansion and complete tensor caller use these pages
  with their full paid schedule? First implement one source-normalized
  real-Gaussian expansion block and connect the two endpoints through
  PR3763's chirp middle map. Establish its .6 input norm and count the
  actual D resampled axes in gamma=sum_i(2u_i+j_i+1); the bulk report
  uses D=d-1. Coefficient pages, spectator reuse, halos, source/core
  reshaping and final layout still need a joined caller.
- Can the mixed-radix CRT entrance and return preserve the valid interval
  through that caller? First implement an actual field conversion and
  check both interval endpoints and both S factors in final recovery.
  A coordinate-slot router alone does not discharge that obligation.
- Can a reviewer validate the complete precision and source correspondence?
  First inspect the exact old-H Schur control, production hypotheses and
  guarded word/interval proofs. The inherited numerical and analytic
  premises still need their separate review.
