# Exact dense B3/C3 term tariffs

Scoped written proof with exact finite corroboration. No new kappa.

For full B3/C3 root codes over any coefficient field of characteristic other
than two, the binary rank cost of a nonzero factor pair is exactly

```text
3  when either coefficient vector uses one coordinate,
5  when both use at least two coordinates.
```

Consequently every finite factor list has exact invoice `3m+2h`, where m
counts its nonzero terms and h counts terms in the second case. An admissible
cost-nine decoder must have three nonzero terms and h=0. The existence and
optimality of cost nine are predecessor results. The new formula determines
the exact surcharge and the condition for attaining that existing optimum.

[PROOF.md](PROOF.md) collapses identical signed-edge pairing rows, then
computes a three-by-three Schur complement. No coefficient search is needed
for its quantifiers. The orthogonality pairing is fixed in the integer
geometry; its cost rank is over F2, separately from the coefficient field.
Invertible diagonal rescalings preserve the formula.

## Evidence and reproduction

From the worktree root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/dense-bc3-term-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/dense-bc3-term-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dense-bc3-term-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/dense-bc3-term-tariff --check-source-history
```

Substitute another CPython 3.12 executable when needed. The direct marker is
`PASS_DENSE_BC3_TERM_TARIFF`. Each direct command prints a generated receipt
bound to the six package files by SHA256. An optional `--output` writes a new
external receipt and refuses an existing path. Default replay writes no files.

The checker establishes the following finite corroboration:

- All 49 nonempty coordinate-support pairs. Exact binary elimination and a
  separate finite-span enumeration agree: 33 pairs cost three, 16 cost five.
- All 296,784 ordered literal coefficient-pair cases across B3 and C3. For
  each family these are all nonzero vectors in `{-2,-1,0,1,2}^3` over Q and
  all nonzero vectors over F3, F5 and F7. Pairing entries come from literal
  integer-root orthogonality, independently of the incidence reduction.
- Six invalid support arguments and two wrong-tariff controls. Four explicit
  escapes demonstrate why a changed pairing, puncture or characteristic-two
  coefficient field falls outside the theorem.

Equal literal support pairs reuse their computed rank within one invocation;
every listed coefficient pair is still compared with the formula and counted.
No predecessor executable, scientific census or native replay is imported.
The written proof supplies the arbitrary-field statement; the finite checker
does not replace it.

## Scope and limitations

This is a local algebraic side result under the changed
`complex-new-helper-inventory` card. It does not supply a new helper inventory
or establish the card's complete supplier-admission contract. The selected
PR6030 record, kappa and five framework assumptions are unchanged.

The full root set, fixed dense pairing, root-code factors and characteristic
other than two are essential. Admissibility of a factorization remains a
separate requirement. Physical native maps, source/helper access, restoration,
hosting, precision, stock, tape, recursive compiler and outer admission are
unproved here. No complete multiplication theorem, selected cold replay,
independent human review or formal proof-kernel review is claimed.

Source provenance is pinned at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a` in
[SOURCES.json](SOURCES.json). The checker has no external runtime input.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19375577)
records the exact first milestone and stop rule. Research stopped after that
formula passed the first independent literal-root check.

## Open next questions

1. Derive an exact coordinate-support tariff in dimension four. First build
   the unsigned incidence blocks for each pair of supports. The larger edge
   block requires a new argument; this package proves no higher-dimensional
   formula.
2. Classify the admissible three-term cost-nine factorizations. First solve
   their biorthogonal coefficient equations with h=0. The tariff condition
   alone supplies neither this classification nor a physical implementation.

These questions are not reserved. Fresh overlap checking is required before
taking them. [TASK.json](TASK.json) records first steps and blockers.

## Code verification limits

All loops have fixed finite domains. There are nine literal root lines,
at most 342 vectors per coefficient case and eight cases. The support oracle
enumerates at most 512 binary span values. Managed Python allocation is an
explicit Power of Ten deviation: temporary integers, tuples, lists and a
within-invocation support-rank dictionary allocate during the scan, with
their sizes bounded by those domains. There is no recursion, dynamic code,
subprocess, network or repository-code import. Every function is below
60 physical lines. Warning-strict normal and optimized replay are the
available runtime diagnostics.

## Credit

The new formula, proof and standalone checker were produced by Nick Petalas.
Apache-2.0. Independent human and formal proof-kernel review are unclaimed.

Credit ywz65's [PR2582](https://github.com/CrocSwap/integer-mult-bounds/pull/2582)
for the dense B/C model, all-size floor and cross-star theorem used as
premises. Aaron Wang retains credit for PR2272/PR2518's root generators and
finite screens. DreamingOfClouds retains PR2228/PR2277's root-code floor method
and the credited earlier lineage. Nick Petalas's older PR4863 concerns
intermediate-axis punctures in dimensions at least four and is separate
from this full dimension-three exact term formula. None of these predecessors
is audited or recertified here.
