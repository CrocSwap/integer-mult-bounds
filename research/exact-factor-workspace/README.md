# Exact fixed-factor dirty workspace

For a fixed rank-one word, one spectator-only basis change needs exactly

    d = dim(U) + dim(V) - rank(V|U)

retained dirty roles. Here U is the span of dirty column components and V
the span of dirty row components. This is a scoped proof, with an exact finite
certificate. It preserves the original active coordinates and every paid
factor. It supplies no new κ or cheaper endpoint word.

The result replaces an upper bound by the exact answer for the single-basis
restriction used in [Brian's PR4783](https://github.com/CrocSwap/integer-mult-bounds/pull/4783).
That predecessor gives d≤m-L for normalized simple-label S4 words. Its proof
and executable are cited, not audited or replayed here. Our theorem works over
any field and any unital algebra with central scalar coefficients. The S4
inversion-slack inequality retains its predecessor's narrower hypotheses.

[PROOF.md](PROOF.md) classifies every optimal retained/discarded splitting.
Writing u=dim U, v=dim V, t=rank(V|U) and k=n-u-v+t, over a field of size q
there are exactly q^((u-t)k) optimal discarded subspaces and
q^(k(u+v-2t)) ordered optimal splittings. These count subspaces, not bases.

[Gareth Davidson's PR2323](https://github.com/CrocSwap/integer-mult-bounds/pull/2323)
already gives the smaller optimum t when one can replace the factors while
preserving their contractions. Our stricter preservation boundary keeps both
pairing radicals. The difference can be arbitrarily large even for words that
restore every dirty input. It is not a contradiction or an improvement of
that resynthesis theorem. No literature-priority claim is made for elementary
subspace and complement arguments.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/exact-factor-workspace
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/exact-factor-workspace/verify.py
```

`verify.py` enumerates all subspace pairs over F2 in dimensions 0 through 4,
F3 in dimensions 0 through 3 and F5 in dimensions 0 through 2. Its independent
minimum oracle enumerates every ordered direct-sum decomposition without
formula-based pruning. It checks the exact dimension and both optimal counts.
Seven restored S3 word fixtures check all formal factors and endpoints through
the faithful regular representation, including one-sided, paired, orthogonal
and dense dirty couplings. All 5,669 subspace pairs agree with the minimum
and both counts. Exact coverage and transcript hashes are generated
in [RESULT.json](RESULT.json). Every package source file is hash-bound.

Both registered commands are read-only. To regenerate the receipt, use
`verify.py --write-result /an/unoccupied/path.json` and compare the generated
file with RESULT.json. The direct verifier works from a Git-free package copy.
Receipt generation refuses an occupied output path. Verification remains
active when Python assertions are disabled.

## Scope and family decision

This changes the bit-new-register-model card to a formal workspace-interface
classification. It avoids an unbounded workspace search for a supplied word,
while retaining the exact coordinate-preservation boundary. It is a local
module, not a new native mechanism or complete supplier. Stop after this
classification. Physical scalar conversion, restricted gauges, native access,
ownership, precision/tape costs and admission remain unknown, not zero.

The current selected source-binding positive control passed. The card's older
`scripts/research_baseline.py` fails with `KeyError: 'bit_lower'` on the current
selected certificate. That unrelated script is unchanged. No historical
construction replay, C++, Lean or Docker check is needed for this theorem.

The verifier follows structured, nonrecursive control flow with fixed census
domains. Its largest universe has 27 vectors and its largest subspace family
has 67 members. Functions are below 60 lines. A managed-runtime allocation
deviation applies to Python tuples, sets and arbitrary-precision integers;
the fixed domains bound their live sizes. There is no steady service loop or
unbounded search. The warning-strict registered normal and optimized runs
check the complete declared domain. Reassess these bounds before widening it.

## Open next questions

- Can the exact coordinate restriction be computed efficiently for a large
  supplied word with additional support constraints? Start with one actual
  native layout and characterize the legal spectator basis changes. The full
  GL model here does not pay or preserve those physical restrictions.
- Which target needs less workspace after changing its factors? Specify an
  endpoint and paid budget, then use the existing contraction-preserving
  theorem where its alphabet is closed. This package gives no endpoint optimum.

## Sources and credit

This contribution is produced by Nick Petalas. Apache-2.0.

Credit Brian/JoyboyBrian PR4783 and PR4765 for the single-basis spectator
restriction and inversion-slack context; Gareth Davidson/bitplane PR2323 for
the exact contraction-preserving pairing compression; Cinna Davis/1337isnot1337
PR1541 for image-span restriction; ToikY PR1662/1680 for the UT4 span and
orientation reductions; and the register-model and cut predecessors credited
by those packages. None of their mathematics or counts is a new deliverable
here. [SOURCES.json](SOURCES.json) pins provenance, including the pending
PR4783 citation, without importing predecessor executables.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19133318)
records canonical main 624de9dc66858af0945e5f8a0942488d62280d43 and priority
revision 7. Entry overlap checked live open PRs, recent claims, merged searches
and distinctive all-main README/proof terms. The cache covered 365 open PRs
and 3,819 Discussion records. Sparse local notes, nested source differences
and unpublished work are incompletely covered. No novelty certificate,
independent human review or formal proof-kernel acceptance is claimed.
