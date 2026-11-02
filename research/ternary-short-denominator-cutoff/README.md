# Sharp denominator cutoffs for short ternary decompositions

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped written proof with exact finite corroboration.** Each frame is
`uv^T/2^j`, for nonzero `u,v in {-1,0,1}^3` and integer `j>=1`.
Negative entries, arbitrary exponents and repetitions are allowed.

- If at most four frames sum to `I3`, every exponent is at most two.
- If at most five frames sum to `2I3`, every exponent is at most two.

Both denominator cutoffs and both term limits are sharp. Quarter sign-square
frames attain the first bound. Splitting one half sign-square frame gives
a five-term attainer for the second. Splitting a quarter into two eighths
disproves the respective five- and six-term extensions.

The [proof](PROOF.md) uses deepest-numerator parity, diagonal and integer
off-diagonal gaps, and positivity only in a forced full-sign-square case.
It imposes no positivity assumption on the alphabet. The result is uniform
in the exponent; a finite cutoff search is not its proof.

## What this adds

Any list of at most eight frames with total `3I3` and a positional subset
summing to `I3` already lies in the half/quarter alphabet. These are the
determinant and subset-support screens preceding scalar projector synthesis
in Maximooch's [PR1679](https://github.com/CrocSwap/integer-mult-bounds/pull/1679).
The cutoff explains why deeper dyadic denominators add no candidates to
those necessary screens. Matrix decompositions need not realize an endpoint.

PR1679 asks for denominator-independent elimination. Its finite-alphabet
theorem and Tuafo's [PR1604](https://github.com/CrocSwap/integer-mult-bounds/pull/1604)
are credited predecessors. Tuafo's [PR1628](https://github.com/CrocSwap/integer-mult-bounds/pull/1628)
already proves the nine-call endpoint floor for unrestricted rational
frames with arbitrary restored dirty workspace. **That floor is not new
here.** No predecessor census, verifier, count or scientific receipt is
replayed. The new contribution is the geometric cutoff and its screening
consequence, with no new kappa or selected-frontier change.

## Reproduce

From the repository root, with the standard library and CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/ternary-short-denominator-cutoff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/ternary-short-denominator-cutoff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/ternary-short-denominator-cutoff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/ternary-short-denominator-cutoff --check-source-history
```

Another CPython 3.12 path can replace the displayed interpreter. Direct replay
prints `PASS_TERNARY_SHORT_DENOMINATOR_CUTOFF` in a generated JSON receipt
bound to all six package files by SHA256. It writes no files. The optional
`--receipt /absolute/external/new-file.json` exclusively creates a receipt
outside the package. No receipt is hand-authored or silently regenerated.

The new checker covers eight exact gap inequalities, all 1,819 sorted
exponent profiles of lengths one through four with exponents at most twelve,
all 676 ordered nonzero ternary numerator pairs, 4,064 half-pair gap cases,
256 forced positive-square cases and 15,872 five-term gap cases. The latter
exercises 24 zero remainders requiring the nonzero-frame hypothesis.
Another 192 literal attaining and term-limit counterexample decompositions
cover all signed coordinate permutations of four fixtures. Twelve rejection
controls exercise malformed frames, false sums and false denominator bounds.
Both normal and optimized modes retain every mathematical check. These finite
counts describe only this checker, not an enumeration of unbounded exponents.

## Scope, provenance and limits

The `bit-new-register-model` card is changed to a geometric screening theorem.
The current baseline command `scripts/research_selected_baseline.py` passes
source-binding orientation at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8. It is not a
scientific replay. The connection to BIT exploration is the explicit infinite
to finite denominator reduction before word synthesis. This side result
supplies no changed native mechanism or better recursive moment. The first
verified improvement is packaged without another construction round.

Dimension three, ternary numerators, reciprocal powers of two, nonzero frames
and the term limits are hypotheses. General rational weights, other targets,
more terms and other dimensions are not covered. No native realization,
physical caller, precision/tape, stock, compiler, outer transfer or complete
multiplication theorem is established. No selected cold replay, predecessor
scientific suite, Lean or Docker run was performed. Independent human and
formal proof-kernel review are unclaimed.

Source READMEs, catalogue and selected record are pinned historical provenance
in [SOURCES.json](SOURCES.json). Direct replay has no external runtime inputs.
Live PRs, recent claims, local reservations, distinctive main-tree searches
and merged searches were checked. Cached overlap reports incomplete sparse
local coverage; unsearched diffs and unpublished work remain limits.

## Verifier constraints

There is no recursion, subprocess, network, dynamic code execution or import
of predecessor code. Functions are below 60 physical lines. Matrices have
nine rational entries, sums have at most eight terms, the profile domain ends
at twelve, and tested exponents end at 256. Each package file is bounded at
128 KiB. Explicit exceptions preserve invariants under optimization.
Warning-strict normal and optimized replay provide Python diagnostics.

Power-of-ten rule 3 deviation: CPython allocates managed integers, Fractions
and collections during this bounded one-shot check. The fixed domains above
bound live mathematical data; no fixed-allocation or real-time claim is made.
A fixed-allocation port would need a separate representation. Rule 9 deviation:
the rejection helper calls exactly four local functions, `frame`, `check_sum`,
`check_ceiling` and `matrix_sum`. Its twelve bounded controls exercise these
targets and propagate unexpected exceptions.

## Open next questions

- What is the sharp exponent cutoff for five frames summing to `I3` or six
  summing to `2I3`? Eighth-frame fixtures disprove the current cutoff.
  Start with deepest-exponent multiplicities and remaining diagonal capacity;
  additional cancellation patterns are unresolved.
- Which unequal invertible ternary-dyadic target triples have a finite short
  screening domain? Start with one named triple and its actual determinant
  and subset equations. No entry-gap theorem for arbitrary targets is supplied.

Structured first steps and blockers are in [TASK.json](TASK.json).

## Credit

Maximooch supplies PR1679's alphabet and denominator-elimination question.
Tuafo supplies PR1604 and the stronger endpoint theorem PR1628. Ali Romman,
woklerx, Cinna Davis, eumemic and huxint retain the register, rank and character
lineage credited in those sources. Their files and credit lines are unchanged.
Walsh/Hadamard identities, binary reduction, rank subadditivity and positive
semidefinite comparison are classical; no literature-wide priority is claimed
for those tools. The sharp denominator cutoffs are the new contribution.
