# Exact extremizers of the third binary character mode

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped mathematical proof with an exhaustive finite equality
lemma. For every k >= 3, the zero-diagonal binary character matrices with
at least two entries attaining Z(c)=19*3^(k-3) are exactly two arrows
with a common head or tail, plus isolated vertices. Their exact labelled
count is k(k-1)(k-2). Every one has positive sign in the unnormalized
signed full-guard character sum, so this is its exact third-mode
coefficient. The Fourier and finite-GL normalization factors are separate.

This answers Open next question 2 of
[PR5146](https://github.com/CrocSwap/integer-mult-bounds/pull/5146).
That predecessor proves the sharp bound and supplies one attaining
family. The new result is the complete equality classification and exact
multiplicity. Its published bound is a cited premise. No predecessor
program, census or spectrum table is imported or audited.

[PROOF.md](PROOF.md) gives the universal argument. A three-vertex equality
lemma forces every outside-induced unary field and constant to vanish.
One-vertex and two-vertex outside assignments then rule out every extra
arrow. Labelled stars give the matching construction and count. No new
kappa or selected-frontier change is claimed.

## Reproduce

From the repository root, using the Python 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/binary-character-extremizers/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/binary-character-extremizers/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/binary-character-extremizers
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/binary-character-extremizers --check-source-history
```

Any CPython 3.12 interpreter can replace the displayed local path. The
direct commands write nothing and emit `PASS_BINARY_CHARACTER_EXTREMIZERS`
inside a newly generated JSON receipt binding all six package files by
SHA256. Neither a receipt nor mathematical output is hand-written.
Each registered command has a 120-second timeout. The standalone checker
requires neither Git nor predecessor files.

## Evidence

The checker enumerates every three-vertex graph with at least two arrows
and every unary field. Its literal ternary-state sum establishes the new
local equality lemma. A separate positive-subset sum checks global
classification at small dimensions and every extension of a fixed
attaining core by two outside vertices. It also constructs all labelled
stars for k=3 through 8 and checks their distinctness, values and count.
The generated receipt records exact executed counts and the six complete
local equality rows. Invalid domains and false equality rules reject,
including a directed path, reciprocal arrows, a three-arrow star,
nonzero unary fields and an outside edge with a changing constant sign.

Executed coverage is 3648 local graph/field cases, 4140 character matrices
at k=3,4, all 16384 two-outside-vertex extensions of one fixed core, and
756 distinct labelled attaining examples at k=3..8. The local sums and
the positive-subset oracle agree on all 57 eligible k=3 characters.
There are eight invalid-domain rejections, six semantic checks and 63
nonzero-field rejections. The local equality table has exactly six rows.
Three actual code mutations, omitting fields, changing star incidence and
ignoring outside edges, reject in both normal and optimized local runs.

The finite checks establish the local finite lemma and corroborate the
universal argument. They are not a census at every dimension. Normal and
optimized modes run the same explicit checks. Source pins are historical
provenance only, with no external executable inputs. The current baseline
orientation reports `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` for selected
PR6030; that is metadata orientation rather than a scientific replay.

## Scope and limits

The independent-moment card is explicitly changed to this original
spectral side question. Binary arithmetic, zero diagonal and the uniform
three-state weights are essential. The result does not give a fourth
spectral mode, a complete all-k probability inequality, negative
association, an odd-field or weighted analogue, a request producer,
sampling/emission procedure, native realization, dirty restoration or
complete physical invoice. All five selected framework assumptions remain.
No complete multiplication theorem is claimed. Selected cold replay,
Lean, Docker and native builds were not run. Independent human and formal
proof-kernel review are unclaimed.

All verifier loops have explicit finite input bounds, with no recursion,
subprocesses or dynamic execution. Matrices have at most twelve rows;
literal sums allow at most six, and executed local sums use three.
The extension loop has exactly 16384 cases and handles one matrix at a
time. Each function fits within sixty physical lines. Explicit exceptions
retain contracts under optimization; registered commands treat warnings
as errors. Python and standard-library runtime dispatch and allocation
are managed-runtime deviations from fixed allocation and static calls.
The declared dimension/file bounds and one-at-a-time enumeration bound
live work. No real-time or fixed-memory runtime guarantee is claimed.
A larger census must revise and verify the capacities first. Syntax and
function-length inspection pass. External Python analyzers were unavailable;
warning-strict execution is the recurring registered diagnostic.

## Open next questions

1. What is the sharp fourth character value and its complete equality
   family? Begin with the next local conditioned extrema and outside-field
   rigidity. This proof supplies neither that value nor a fourth-mode gap.
   The answer could sharpen full-guard moment remainders.
2. Can an actual request producer exploit a shared header at a favorable
   complete price? Start with one source-bound producer/consumer and
   account for sampling, selection, emission, native alignment and dirty
   restoration. Those physical costs are unknown here.

[TASK.json](TASK.json) records structured relevance, first steps and blockers.
Research stops at this first verified improvement; no follow-on is reserved.

## Credit and coordination

Nick Petalas / PR5146 supplies the sharp remainder bound and explicit
equality question, and PR4275 supplies the signed character law. Ryanson
Jonathan / pinterbanget PR4607 supplies the five-event predecessor and
structural-spectrum motivation. Nick Petalas / PR4599 supplies the
four-event antecedent. Cinna Davis, source527, commdata2338 and Jose Manuel
retain the request and normalizer lineage credited by those sources.
Conditioning, finite character sums and the triangle inequality are
classical. The scoped classification and its checker are the new work.
Frozen sources and predecessor attribution are unchanged.

Base: canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8, selected PR6030. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362336)
records the target. Live claims, local reservations, current main README
searches, merged/open PR searches and recent account work were checked.
The cached overlap snapshot has 387 open PRs and 6319 Discussion records
with complete remote pagination, but searches only 114 of 8917 local
notes. Separate Git searches cover main README terms. Unpublished work,
sparse notes and arbitrary historical diffs remain coverage limits.
PR5860's five-indicator probability comparisons and PR6415's literal
header-census optimization are separate quantities and are not extended.
