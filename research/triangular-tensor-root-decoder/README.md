# A sparse tensor-root decoder with COPY mass 31

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped constructive proof with exact finite corroboration. For every s>=1,
n=2^s, the exact tensor-root identity

```text
2 [[2,1],[1,2]]^(tensor s) = sum_z p_z q_z^t
```

has an explicit dyadic factorization with COPY profile `(n-1)H1 + Hn`
under the predecessor's pairing B=J+P, where P complements binary words.
Its COPY rank mass is **2n-1**, giving **31 at n=16**, compared with the
displayed dense mass 256 in Cinna Davis's
[PR3895](https://github.com/CrocSwap/integer-mult-bounds/pull/3895).
The bound is constructive; no optimum is claimed.

The new step uses the supports of a triangular Kronecker factorization.
Every column except the first fixes a nonempty set of binary coordinates,
so its support block of B is a nonempty all-ones matrix of rank one.
The first column costs n. [PROOF.md](PROOF.md) gives both the tensor proof
and a separate entrywise subset-sum identity. The full scalar identity holds
for arbitrary complex inputs with ordinary transpose. Nothing is masked away.
For every real t>0 the rank-power bill drops from n*n^t to n^t+n-1.

## Evidence and reproduction

From the repository root, using the standard-library CPython 3.12 interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/triangular-tensor-root-decoder/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/triangular-tensor-root-decoder/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/triangular-tensor-root-decoder
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/triangular-tensor-root-decoder --check-source-history
```

Another CPython 3.12 path may replace the displayed interpreter. The direct
verifier is Git-free, read-only and prints a generated receipt bound to all
six package files. It imports no predecessor code and has no external runtime
inputs. Its marker is `PASS_TRIANGULAR_TENSOR_ROOT_DECODER`.

Exact checks cover all six levels s=1,...,6, with 5,460 full Gram identity
entries, 10,920 entries of the two-sided frame inverses, all 126 actual support
charges, and 84 literal product-root Gram entries at s=1,...,3. A closed
subset formula and a separate literal Kronecker construction agree on the
frames. Thirteen controls cover six invalid exponents, altered/omitted weights,
wrong columns, antipodal versus proper-subcube supports, and two false tariffs.
The all-s and all-real-t statements rest on the written proof.

## Connection and limits

This changes the local factorization in PR3895's growing tensor alphabet.
It is a side result on `complex-rank-shape-decoder`, with scope explicitly
changed in [TASK.json](TASK.json). The current selected source-binding baseline
passed; no selected scientific suite or predecessor verifier was replayed.

The unweighted frame F and its inverse are dyadic, while the weighted factor
need not have a dyadic inverse. The proof keeps weights in scalar accumulation
and does not claim that inverse. Native delivery and physical coefficient costs
remain open. In particular B still has rank 16 at s=4, and ToikY's
[PR3928](https://github.com/CrocSwap/integer-mult-bounds/pull/3928)
literal nine-bit embedding obstruction remains applicable.

No native word, arbitrary-dirty ambient restoration, ownership/hosting plan,
precision/tape/stock bound, complete paid/productive invoice, compiler or
outer admission is supplied. No new kappa, selected-frontier change or complete
multiplication theorem is claimed. All five selected framework assumptions
remain. Independent human and formal proof-kernel review are unclaimed.
No Lean, Docker or historical supplier suite was run.

## Sources and overlap

The question source and main predecessor is Cinna Davis / 1337isnot1337,
PR3895, head `2e969106d82a7e53ee3a22580653521b4876cc6b`. Its exact identity,
pairing and dense comparator are cited, not audited. The new construction is
self-contained and does not require that pending commit at runtime.
ToikY's PR3928 is read at `2b2daaecac95e1048923d22fda51ccd01780565f`.
DreamingOfClouds / PR717, themilkman216 / PR968 and woklerx / PR1077 retain
the preceding decoder conventions and E8/native/Clifford credit.
LDL factorization, Kronecker products and binary rank are classical.

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
[SOURCES.json](SOURCES.json) binds the card and selected record as historical
provenance. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19376720)
reserves this factorization. The complete cached overlap refresh covered 598
open PRs and 6,675 Discussion records. Sparse local coverage was 125 of 8,917
notes before this package. Main README searches and live merged searches for
the tensor object, formula and triangular/LDL forms supplement that coverage.
Recent account work and concurrent claims were screened. Arbitrary diffs,
unpublished work and worldwide literature coverage remain outside this search.

## Verifier bounds

The executable accepts only s=1,...,6, so matrices have at most 64 rows and
columns. Literal root vectors are limited to 512 entries. No recursion,
subprocesses, dynamic code or external services occur. Every function is below
60 lines. Explicit failure checks survive optimized Python; warnings are errors.
No separate static analyzer is installed. Python's managed allocation and
bounded control callbacks are deviations from Power of Ten rules 3 and 9;
the fixed domains bound their live state and possible targets. The verifier
prints hashes of six named files, each limited to 256 KiB. It writes nothing.

## Open next questions

- Can a named consumer use these sparse terms without the full n-dimensional
  tensor-label embedding? Start with one exact changed source/reader map and
  check every constrained scalar coefficient. The existing nine-bit obstruction
  rules out silently reusing the full pairing, and no consumer is supplied here.
- Can the sparse scalar frames and weights be realized within a favorable
  complete physical invoice? Start at n=4 with explicit entry, delivery and
  restoration words. Native legality, arbitrary dirty inputs, coefficient and
  precision costs remain blockers. A favorable local COPY bill alone is
  insufficient to expand the construction.
