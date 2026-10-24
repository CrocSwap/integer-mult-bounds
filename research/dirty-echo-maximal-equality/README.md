# The exact maximal equality band for dirty echoes

For the ordered reserved-parent-scratch echo grammar of Alexander
Schwartzman's [#784](https://github.com/CrocSwap/integer-mult-bounds/pull/784),
the affine lower bound is attained exactly when

```
ceil(2^(s+1)/3) <= n <= 2^s,
min N = 2^(s+1)n - 4^s.
```

This extends the preceding sufficient band `3*2^(s-2) <= n <= 2^s`.
[PROOF.md](PROOF.md) also characterizes every equality tree. Its exact slack
identity permits binary nodes with tight children and ternary nodes with
capacity-saturating endpoints; larger arities have positive slack.
At four scratch arrays the new theorem includes eleven factors and 96
complete calls. The predecessor's finite table already includes this
numerical optimum. The contribution is the all-size maximality theorem,
not a replay or recount of that table.

Claim type: scoped proof with exact finite corroboration. No new kappa,
physical supplier or complete multiplication theorem is claimed.
This contribution is produced by Nick Petalas. Independent human and
formal proof-kernel review are unclaimed.

## Reproduce

From the repository root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/research_package.py --package research/dirty-echo-maximal-equality
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/check_research_commit.py --package research/dirty-echo-maximal-equality --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/dirty-echo-maximal-equality/verify.py
```

The first command runs both registered checks. A portable reviewer can replace
the absolute interpreter path with their CPython 3.12 executable. The scientific
verifier also runs outside Git. It compares every field of the generated
[RESULT.json](RESULT.json), including source hashes, and prints
`PASS_DIRTY_ECHO_MAXIMAL_EQUALITY`. `--write /absolute/new/file.json` creates
an exclusive generated receipt and refuses an existing path.

[oracle.py](oracle.py) independently minimizes over every root arity and
positive child-size composition, without using the new equality threshold.
It checks all budgets 0..8 and factor counts 1..256. A separate whole-tree
enumerator checks the recursive characterization on every ordered tree through
eight leaves, including nonoptimal shapes and every fitting budget through
eight. The constructor supplies every equality size through budget eight.
Boundary and corruption controls run under optimized Python as well.
Finite checks support the written proof; they do not establish its universal
quantifiers by enumeration. Exact coverage is generated in RESULT.json.
No predecessor verifier, Lean build or supplier replay is run.

## Credit and source boundary

Alexander Schwartzman #784 supplies the lower bound and sufficient equality
family. Gareth Davidson #887 supplies its scoped Lean formalization, explicitly
without maximality. The original multiway echo and restoration semantics are
androolloyd's #673. Credit Koroffstrogov #758 for the all-arity optimizer,
Sagar Thakrar #730 for ordered binary/ternary optimization, Dillon Amburgey
#689 for the balanced ternary baseline, and the retained Chafik Boukhalfa
#628 leaf lineage. No predecessor implementation is copied or imported.
[SOURCES.json](SOURCES.json) pins the statements as historical provenance.
The model and the necessary definitions are stated completely in PROOF.md.
The source contexts are cited premises; their computations are not rechecked.

The entry cached scan covered 379 open PRs and 3,859 Discussion records,
with complete reported pagination. Its local corpus included only 102 of
6,319 tracked notes. Relevant predecessor notes were then materialized.
Live handoffs, relevant PR bodies, merged-term searches and all-main README
searches supplement the scan. They do not cover unpublished work or prove
literature novelty. The canonical claim is in
[handoffs #1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19133745).
New files are Apache-2.0.

## Limits and verification policy

The theorem keeps unit leaf prices, all inverse/restoration calls, ordered
factors, static trees and parent-reserved dirty arrays. It does not cover
connector reuse, clean checkpoints or arbitrary reversible programs. The full
supplier bill remains a separate, unfavorable predecessor interface; local
call optimality does not improve kappa. A formal-kernel extension, physical
caller and weighted analogue remain unrun or unresolved.

The new Python code has bounded inputs and iterative traversals. Functions
fit within 60 physical lines. Explicit exceptions remain active under `-O`.
Managed Python and itertools allocate at runtime, a Power of Ten deviation;
fixed domains of at most 256 leaves, budget eight and eight-leaf exhaustive
trees bound live data. Strict-warning normal/optimized runs and corruption
controls provide the applicable diagnostics. The local oracle import uses one explicit path and the receipt binds its
bytes. Rejection controls dispatch only to two named validation functions.
These bounded Python mechanisms are documented deviations from the strict
metaprogramming and indirect-call rules. No static type checker is configured
for this standalone integer verifier; syntax compilation and strict-warning
execution are the available language diagnostics.

## Open next questions

- Determine a closed form for the number of equality trees at each `(s,n)`.
  Start from the disjoint binary/ternary shape recurrence in PROOF.md.
  This would distinguish existence from schedule multiplicity; no physical
  caller is needed, but no such count is proved here.
- Find a useful analytic bound for unequal leaf prices under the same scratch
  contract. Start with one fixed ordered price vector and keep all restoration
  multipliers. The maximal unit-price equality band alone does not solve it.
