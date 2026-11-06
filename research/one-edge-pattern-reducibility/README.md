# One-edge five-dimensional binary pools are reducible

This scoped proof and its standalone verifier were produced by Nick Petalas.
Apache-2.0. Independent human and formal proof-kernel review are unclaimed.

For a three-dimensional binary off-diagonal pattern space containing exactly
one matrix-unit edge E_ab, the complete noncoordinate rank-one-idempotent pool
cannot act irreducibly on a five-dimensional joint image. If that image has
dimension five, every pool member preserves span(e_a,e_b). Thus an irreducible
restricted pool has active dimension at most four. Attainment at four is not
claimed. A separate reducible example attains joint-image dimension five.

This answers the one-edge irreducible classification question in
[CubeJerry's PR6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782),
README open question 2. The [proof](PROOF.md) builds on that contribution's
edge-quotient lemma. The new step studies equality in its bound; the lemma
and its prior bound are credited premises, not reverified deliverables.
There is no new kappa or supplier admission.

## Evidence

The claim type is a scoped written proof with finite exact corroboration.
The universal argument holds at every ambient width under the credited
edge-quotient premise. The verifier imports no predecessor code and reads
no external scientific input.

At widths five and six it enumerates every fixed-edge pattern space capable
of attaining the bound. Equality requires all three nonzero quotient cosets
to be realized. The complete pools of these spaces are reconstructed from
all binary rank-one idempotents, and every dimension-five edge action is
checked exactly.

| Ambient width | One-edge spaces with all three quotient cosets realized | Dimension-five spaces | Those preserving the edge space |
| --- | ---: | ---: | ---: |
| 5 | 1030 | 30 | 30 |
| 6 | 6576 | 328 | 328 |

These are spaces with edge fixed to E01, not conjugacy classes or counts of
all pattern spaces. [PROOF.md](PROOF.md) explains the complete enumeration
of the relevant domain. The five-projector equality fixture is reconstructed
by a separate direct space check. Seven controls exercise dependent generators,
multiple edges, missing members, an extra coordinate projector, an unsupported
width and two explicit edge-space leakage cases.

Every direct run prints `PASS_ONE_EDGE_PATTERN_REDUCIBILITY` and a generated
JSON receipt with recomputed counts and SHA256 hashes of package files. No
handwritten scientific receipt is supplied.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/one-edge-pattern-reducibility/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/one-edge-pattern-reducibility/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/one-edge-pattern-reducibility
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/one-edge-pattern-reducibility --check-source-history
```

Any CPython 3.12 executable can replace the installation path. The last command
requires the package to be committed. The standalone verifier also runs without
Git, network or the rest of the repository.

Local CPython 3.12.15 runs passed normally and optimized, as did both registered
commands and the package metadata check. Individual direct runs took 0.097 and
0.101 seconds; these single-run measurements check the replay budget, not a
performance improvement. Syntax compilation and indentation diagnostics passed.

[SOURCES.json](SOURCES.json) pins the merged catalogue, selected record and
PR5921 proof context as historical Git provenance. [ORIGINS.json](ORIGINS.json)
separately pins the pending PR6782 proof by public URL, exact head and SHA256.
That cited mathematical premise is not imported by the finite verifier or
included in the Git-history preflight. No claim of independent verification
of PR6782 is made. The public proof must be consulted to assess the imported
lemma.

## Scope and limitations

The card `bit-helper-contract` is changed to an algebraic side question from
another contributor. The required selected-baseline command passed with
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; it authenticates metadata, not operators.
The selected record remains at `781451/250000000` under its five assumptions.
The direct construction, three-relation word problem and complete BIT moment
requested by the card remain unproved here.

The field is F2 and the pool is complete. Coordinate projectors are excluded.
Interleaving extra coordinate calls or other patterns can destroy the invariant
edge space. The result supplies neither a free physical basis transformation
nor a word-rank saving. Rational frames, arbitrary dirty-state restoration,
native realization, full cost/precision/tape/ownership accounting, compiler and
outer admission remain separate. No selected operator replay, Lean or Docker
run is supplied. The finite census does not establish unbounded quantifiers.

The verifier uses explicit checks that stay active under optimized Python.
All loops have fixed finite domains, with at most 2010 noncoordinate projector
records and at most 2010 quotient keys. Each pair loop has at most 2,019,045
iterations. There is no recursion. Python allocates managed objects during
enumeration; this is a bounded-domain deviation from fixed-allocation practice.
The negative-control callbacks have five fixed targets and no shared mutable
state. No dedicated linter is installed; warning-as-error execution, syntax and
indentation diagnostics are used for this isolated Python file.

## Related open work

- [#6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782) supplies the
  edge-quotient bound, a distinct two-edge five-dimensional irreducible example,
  its word obstruction and the explicit one-edge question. This package closes
  that one-edge five-dimensional irreducible case without replaying its results.
- [#6777](https://github.com/CrocSwap/integer-mult-bounds/pull/6777) proves a
  two-relation word-rank bound at arbitrary scalar width. The present result
  concerns three-dimensional pattern pools and proves no word-rank inequality.

Merged PR5921 supplies the fiber/cardinality context and PR1456/1846 the earlier
pattern-space framework. They retain their original credit. CubeJerry's new
edge-quotient theorem is the direct predecessor. The broader register-model
lineage credits David Govea, Ali Romman, woklerx and eumemic.

## Open next questions

- Can a one-edge core of dimension at most four yield a three-relation diagonal
  word with target rank exceeding paid rank? First specify one remaining scalar
  alphabet and its relation lattice. Chronological synthesis and rational frames
  are absent here, so the pool result alone cannot answer this.
- What is the sharp irreducible joint-image bound for zero-edge three-dimensional
  pattern spaces? Start with one explicit configuration from PR6782 question 2.
  This proof depends on a nonzero edge space and gives no zero-edge classification.

Structured first steps and blockers are in [TASK.json](TASK.json).
