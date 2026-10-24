# Strict rank bounds for the complete five-bit odd-type mask

Scoped mathematical proof with exact finite corroboration. Over every
field of characteristic two, the complete five-bit odd-type mask has
fitting rank at least **22 on its 105 regular types**, and at least
**53 on all 136 admissible types**. These are lower bounds, not exact minima.
No new kappa is claimed.

Write `j=11111` and let a type be `(q,w)` with both binary labels odd and
`w dot q=1`. A regular type has `q != j` and `w != j`. Each type occurs
once. A fitting matrix has arbitrary nonzero diagonal and must have
`N[s,t]=0` whenever `s != t` and `w_s dot q_t=1`. It may be asymmetric
and may have arbitrary entries in the full coefficient field.

The elementary Hadamard rank bound gives 21 on the regular types.
The new step excludes equality. After diagonal normalization, equality
would make the two square tensor factors inverses. Taking block traces
forces `sum(q w^T)=21 I_5=I_5`. The actual type sum is `J_5`, the all-ones
matrix. Its off-diagonal entries contradict this requirement. The 31
all-ones-source/sink types add rank individually, improving the associated
full-mask lower bound from 52 to 53. [PROOF.md](PROOF.md) gives the argument.

## Predecessors and scope change

Jose Manuel / jmbarrancoml's [PR3512](https://github.com/CrocSwap/integer-mult-bounds/pull/3512)
and [PR3544](https://github.com/CrocSwap/integer-mult-bounds/pull/3544) supply
the odd-type fitting model and leave optimal fitting rank open. PR3544,
head `6cfa4333a2e593ea092fe4bda686bb172b5b6d22`, proves the stronger
all-field regular coefficient `17/105` in dimension five. That theorem
is cited, not audited or replayed. The new result concerns the different,
characteristic-two boundary; it does not improve the rational bound.
[SOURCES.json](SOURCES.json) pins the main-retained predecessor documents
as provenance. The verifier imports no predecessor code or data.

Canonical base is `ff3cc58e370d0f678e529246f8c73e8094e18fcf`, priority
revision 7. The complex-rank-shape-decoder card is explicitly changed to
this algebraic side question. It closes a finite-field equality case
before a changed fitting model is used as a small-unit surrogate. This
is not a decoder construction or evidence of a better paid supplier bill.
The card's historical first command fails on the selected schema with
`KeyError: 'complex_profile'`; the current schema-aware
`scripts/research_selected_baseline.py` orientation passes. Neither is
part of the new proof.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19147080)
proposed exact values 21 and 52. The
[scope update](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19147122)
records their impossibility and the delivered strict lower bounds.
Targeted main-tree and merged-PR searches, live open PR bodies and
Discussion claims, recent same-account work and local reservations were
checked. The broad scan covers 311 open PRs and 4,484 Discussion records;
sparse local notes and unpublished work remain incomplete coverage.

## Reproduce

From the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/odd-five-char2-minrank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/odd-five-char2-minrank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/odd-five-char2-minrank
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/odd-five-char2-minrank --check-source-history
```

Any CPython 3.12 installation can replace the local interpreter path.
The expected marker is:

```text
PASS_ODD_FIVE_CHAR2_MINRANK regular_types=105 regular_lower=22 full_types=136 full_lower=53 tensor_fixtures=18 controls=7
```

The replay enumerates the complete 136-type domain, its 105 regular
positions, fifteen seven-element fibers and all 25 moment entries.
Eighteen tight tensor fixtures over F2/F4/F8 check both inverse products,
block traces and diagonal normalization, including nonbinary field
coefficients and repeated types. Two full-mask fixtures check exact
rank addition `132=31+101`. Seven rejection controls cover the impossible
rank-21 moment, wrong cardinality, a forbidden entry, zero diagonal,
missing normalization, corrupted tensor and zero inversion.

The verifier writes nothing and emits a fresh receipt bound to all six
package files and the executed results. Checks remain active with `-O`.
The written proof supplies the arbitrary-field quantifier; the replay
neither enumerates all fitting matrices nor certifies a formal proof kernel.

## Limitations and engineering notes

Characteristic zero and odd characteristic, nonuniform type multiplicities,
sharpness at ranks 22/53, physical factors, frames, ownership, routing,
restoration, precision, stock, compiler and complete supplier costs remain
outside this result. No selected-frontier update or complete multiplication
theorem is claimed. Independent human and formal proof-kernel review are
unclaimed. Lean, Docker and the selected supplier cold replay are unrun.

The verifier has no recursion, dynamic code, subprocess or network calls.
Its functions are below 60 lines. It bounds matrices by 136 rows and
columns, tensor matrices by ten rows and columns, fields by eight elements, package reads
by six files of at most one MiB, and all loops by these fixed domains.
Managed Python allocation is a deviation from static allocation; the
finite domains bound live matrix storage. Seven fixed rejection callbacks
are a bounded deviation from avoiding indirect calls. Warning-strict normal
and optimized replay and in-memory compilation supply diagnostics.

## Open next questions

1. Is the regular characteristic-two minimum 22? First seek a cover of the
   105 types by 22 compatible classes, or an explicit rank-22 factorization.
   Attainment is the missing obligation; a lower bound alone cannot supply it.
2. Can the full regular mask admit rank below 22 in characteristic zero?
   Start with a rational factorization respecting the same zeros, using
   PR3544's all-field lower bound as a cited premise. The five-column
   factorization of the binary parity mask does not survive that field change.

Structured questions are in [TASK.json](TASK.json).

## Credit

This contribution was produced by Nick Petalas. Jose Manuel / jmbarrancoml
supplies the odd-type model, all-field triangular/flag bounds and explicit
open fitting-rank question in PR3512/3544. Philippe Van Velzen supplies the
small-unit setting and prior acyclic/Hadamard method; DreamingOfClouds
supplies the related symmetric-mask Lagrangian and pairing-rank lineage.
The rank inequality, tensor factorization and cyclic trace are classical.
The new contribution is the strict characteristic-two bound for these
complete type sets and its stated proof and exact corroboration.
Predecessor files and credit are unchanged. Apache-2.0.
