# sparse-rank-witness-products

**Verification tooling; no new κ.** Extend the current shared rational-rank
certificate tool's exact product implementation. Kernel witnesses have large
free-coordinate identity blocks, so most dot-product entries are zero. Evaluate
each checking dot product using the smaller exact support. In the producer,
clear denominators once and reduce each output rational once, rather than at
every multiply/add. Pivot selection, minor inversion, all four product checks,
complete kernel bases, input limits and certificate formatting stay in place.

## Scope and evidence

Original card: `replay-runtime`, refined to the user-assigned shared-tool
optimization. Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Source commits, Git blobs and SHA256 pins are in [SOURCES.json](SOURCES.json).
`baseline.py` is the byte-exact current predecessor, including PR6272's existing
integer checker. `fixtures.py` retains Nick Petalas's PR6272 fixture verbatim.
This measures an improvement over that already optimized baseline.

On that 48×64 rank-eight fixture the unchanged four product predicates require
320,000 dense integer multiplications; the smaller supports require 69,280.
The certificate producer additionally replaces 6,656 Fraction multiply/add
pairs with integer accumulation and 832 final rational reductions. The
elimination and inverse are deliberately untouched. [PROOF.md](PROOF.md)
gives the exact equivalence argument; the finite differential checks corroborate
the implementation.

On Windows 10 / CPython 3.12.2, seven alternating fresh-process pairs give
median **3.5729 → 3.1467 seconds (11.93% less wall time)**. The earlier valid
seven-pair run gives **3.9845 → 3.4193 seconds (14.18% less)**. Both complete
reports are retained as `BENCHMARK.json` and `BENCHMARK-INITIAL.json`; all 56
producer/checker commands succeed and every certificate has byte hash
`3de7ffd6fb2a33528c61a3527122e181165e556f0f98facbb3d66d27b10ff6f6`.
Ranges overlap and one pair in each run regresses, so these are noisy local
medians, not an every-run guarantee. The initial run overlapped other local
verification/setup activity; the repeat began after those checks finished.
Fresh temporary bytecode-prefix directories prevent project bytecode reuse and
also include standard-library source-import cost in both arms. Input generation
and source authentication are excluded. No speed is inferred from a profiler.

The fixture is a **synthetic rational interface**, not an observed supplier
matrix. No universal speedup or complete selected-supplier replay improvement
is claimed. Worst-case dense matrices have less sparsity; large coprime
denominators use the retained 16,384-bit fallback. Python object allocation is
still a managed-runtime implementation, not a fixed-capacity backend proof.

## Reproduce

Python 3.12 standard library only, from repository root:

```sh
python3.12 -B scripts/research_package.py --package research/sparse-rank-witness-products
python3.12 -B -m unittest discover -s tests -p test_research_rational_rank.py -v
python3.12 -B research/sparse-rank-witness-products/benchmark.py --pairs 7 --output /tmp/fresh-rank-benchmark.json
```

The benchmark refuses an existing output path. Each timed arm starts a fresh
producer, saves the complete certificate and starts a fresh certificate checker.
Startup, file access, parsing, elimination, all verification predicates and output
serialization are included. The order alternates; fixture construction, profiling
and source authentication happen before timing. The source hashes must stay
unchanged during a run. Each arm must succeed and all certificate bytes must
match. Wall time is evidence, never a CI pass threshold.

The verifier compares **596 complete certificates**, including all 512 binary
3×3 matrices, seeded rectangular rational matrices, zero rank, nonleading pivots
and full rank 64. Both engines cross-check every certificate. It also compares
70 sparse/empty product shapes with plain Fraction arithmetic; tests actual
denominator growth beyond the scale cap and forced fallback; rejects corrupt
inverse, factorization and both kernels; and confirms that a faulty producer
product still fails the unchanged certificate predicates. Normal and optimized
registered commands use explicit checks. The seven existing relevant unit tests
remain separate coverage. No source checks or mathematical predicates are
replaced by a cached success result.

## Open next questions

- Does the improvement hold for a named constructor's actual interface matrix?
  Export a source-bound matrix within the tool's 64×64 input limit and run the
  same paired complete CLI harness. Access to that specific matrix and its
  current constructor contract is needed; this synthetic fixture cannot answer it.
- Do these product changes compose efficiently with the pending integer-pivot
  implementation in PR6705? First bind that exact head and run complete-certificate
  comparisons and fresh paired timings of the combination. Intermediate growth
  and dense cases still need measurement; this contribution does not replace
  elimination or incorporate that pending implementation.

## Credit

Ali Romman / PR5789 supplies the shared rank certificate, parser, pivot choices
and complete kernel checks. Nick Petalas / PR6272 supplies denominator-cleared
product checking and the retained fixture, benchmark precedent and source
notices. Related PR5954 uses primitive integer rows for a different rank-only
consumer, and PR6270 optimizes rational-box solves; neither is this complete
rank-certificate product path. Sparse dot products and denominator clearing
are classical, with no new algorithmic or mathematical priority claim.
The separately proposed [PR6705](https://github.com/CrocSwap/integer-mult-bounds/pull/6705)
at `e56d08c60910a4a635b708f26acbcc3326639dd5` changes pivot discovery with
primitive integer rows. This change leaves that stage unchanged and targets
coefficient production and all four verification products. Combined performance
has not been measured.

Prepared by Joseph Anglada with substantial OpenAI Codex assistance,
Apache-2.0. No independent human or formal-kernel review is claimed. Native,
physical, precision, compiler, outer theorem, Lean and selected cold replay
obligations are outside this tooling change. Live title/body overlap checks are
bounded evidence, not a novelty proof.
