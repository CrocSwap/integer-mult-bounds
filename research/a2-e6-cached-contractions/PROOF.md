# Exact contraction reuse in the PR2061 primary replay

This scoped implementation-equivalence proof was produced by Nick Petalas.
New work is Apache-2.0. Independent human and formal proof-kernel review are
unclaimed. Adam Gall's COPY69 theorem is a cited predecessor result, not a
new mathematical claim of this package.

## Contract and equality

The pinned primary verifier checks each requested ordered pair by computing

```text
sum_k rows[i][k] * (sum_s Q(E.LINES[j][s]) * frame.F[k][s]) / 4
    == 2 * E.G[i][j].
```

Its actual domain has 112 live indices, nine normals and eight coordinates.
All contractions use exact rational arithmetic. During an identity invocation
the indices, normals, roots and Gram matrix are fixed. No callback or mutation
occurs inside a contraction.

Define `C[j,k]` to be the parenthesized sum divided by four. Its inputs do not
depend on i. The adapter computes each C once, then uses
`sum_k rows[i][k] * C[j,k]` in the same i,j,k order. Each coefficient is exactly
the original coefficient, including rational conversion and division. Therefore
each entry comparison has exactly the same value. The first failing ordered
pair is unchanged, and success still requires every requested ordered pair.
Eagerly computing later coefficients adds no exceptional behavior on this
fixed finite rational domain.

The cache is local to one call. It is discarded before the next invocation,
so changing normals, input rows, roots or Gram data cannot reuse stale values.
The adapter authenticates all nine live files before importing predecessor
code. The predecessor retains its own source checks as well.

## Exact work reduction

The original `run()` invokes the identity routine twice. Its positive witness
compares 12,544 entries. Its existing deliberately changed coefficient fails
on comparison 4,817. Both invocations and both outcomes remain present.

For V visited pairs, the original executes 9V eight-coordinate contractions.
For each invocation the adapter executes 9*112=1,008 contractions. Hence

```text
original: 9*(12544+4817) = 156249 contractions
cached:   2*9*112       =   2016 contractions
removed:                  154233 contractions
removed rational products: 8*154233 = 1233864
```

These are counts of explicit `Q(a) * b` operations in the inner contraction.
No claim counts the saved additions, conversions or divisions as further
multiplications. The outer nine-term entry sums are unchanged. The verifier
enumerates the visited pairs and checks these exact counts.

## Complete workload and measurement

Both benchmark modes invoke the unchanged complete `run()`. It still performs
the geometry checks, every character-compatibility and triple-compatibility
check, support and rank calculations, attaining identity, all existing
rejection controls and both rational interval budget screens. Both compare
the entire freshly computed result with the pinned `RESULT.json` and print
the same complete-primary success line. Only `exact_identity` is replaced.

The complete primary CLI is the measurement boundary. Import, all source hash
checks, construction, scientific execution, certificate comparison and output
are inside the subprocess timer. It is not a whole four-command registered
workflow measurement. The independent checker and six-test driver remain
unchanged and are not claimed to be faster.

Five alternating original/cached fresh processes each passed, with identical
stdout and no stderr. Median elapsed time was 2.354848833 seconds original
and 1.698670834 seconds cached, a 27.8649733% reduction. Original range was
2.331363334 to 2.602431125 seconds; cached range was 1.675971083 to 1.886004875.
The ten integer nanosecond samples are reproduced in README.md.
These are local macOS measurements, not a portable timing guarantee.

A separate, untimed cProfile run attributed 2.769 of 4.770 profiled run-seconds
to the two original identity invocations. The measured saving is below that
profile share. Other exact rational work, especially the unchanged interval
budget calculation, limits the complete-CLI gain. Profiling overhead is not
included in the reported timings.

## Scope and stopping point

The proof applies to this fixed source-bound rational routine, not arbitrary
side-effecting or mutable input objects. The new finite controls compare the
original and cached routines on rational inputs, every single-entry mutation
of five bounded domains, changed normals and changed Gram data. Separate
source controls reject corruption of each live file and one missing file.

The first verified improvement ended optimization. This package does not
re-establish the predecessor's optimum, change its decoder, lower a native
invoice or prove a multiplication bound. Complete supplier, physical, stock,
precision/tape, compiler and outer obligations retain their prior status.
