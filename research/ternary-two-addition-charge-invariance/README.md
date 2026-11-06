# Ternary guard costs through two additions are charge-only

Scoped written proof with exact finite corroboration, produced by Nick Petalas.
No new kappa is claimed.

For every full affine ternary guard family, the multiset of scalar/vector
charges determines the optimal monomial-header price truncated at three:

```text
charge pairs (u_i b_i, u_i W_:i)
    determine min(number of paid row additions, 3)
```

The theorem holds in every dimension, including multiple slope rows. Hidden
dual entries at zero image coordinates cannot change whether the price is
zero, one or two. Therefore any equal-charge pair with different optimal
prices must have smaller price at least three. The full charge-sufficiency
question remains open.

This answers a bounded part of Open next question 1 in SHIN09-git's
[PR #6712](https://github.com/CrocSwap/integer-mult-bounds/pull/6712), exact head
`03caa7f6cb5bd21c834024e9d81f6b43eb325b91`. That package supplies the header
model, separation criterion, component-charge invariant and already-separated
scalar price. [PROOF.md](PROOF.md) restates these facts and proves the new
two-addition reduction. Its key case is a three-vertex component containing
two opposite slope charges and an initially zero-charge coordinate. The
nonzero slope restriction survives invertible operations, forcing one final
image coordinate to vanish. The remaining two scalar charges differ from a
canonical merge by at most one scalar settlement unit.

## Evidence and reproduction

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/ternary-two-addition-charge-invariance/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/ternary-two-addition-charge-invariance/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/ternary-two-addition-charge-invariance
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/ternary-two-addition-charge-invariance --check-source-history
```

Other hosts can substitute their CPython 3.12 executable. Only the standard
library is used. Direct replay prints
`PASS_TERNARY_TWO_ADDITION_CHARGE_INVARIANCE`, with zero failed checks and
SHA256 hashes of the proof and verifier. Receipts are generated on stdout;
no hand-written receipt is committed.

The finite corroboration covers 1,256 monomial-orbit representatives and 221
dimension-tagged charge fibers at dimensions two through five. It includes
constant families as well as nonzero pencils. Breadth-first expansion stops
after exactly two paid levels; reported cost three means only at least three.
The new result is the all-dimension proof, rather than a recount of the
predecessor's full cost census. No predecessor executable or receipt is run.
Additional checks enumerate 46 local scalar cases, 2,916 dense header actions,
and 19 literal two-coordinate families using actual principal determinants.
Three controls reject a fabricated split within a charge fiber, omission of
the negative scalar endpoint, and the wrong sign in an inverse dual update.

The verifier has no recursion, runtime code generation, network access or
variable-size external input. Functions have fewer than 60 lines. The largest
candidate enumeration has binomial(18,5)=8,568 entries; its retained valid-state
set has 933 entries. Neighbor sets have at most 40 entries and the search has
two levels. Managed Python allocation is a Power-of-Ten deviation, bounded
by these fixed domains. Warning-as-error normal and optimized execution use
explicit exceptions for every scientific gate. Additional static analyzer
coverage is not claimed.

## Limitations

This is the free-permutation, free-nonzero-scaling, unit-row-addition metric
over F3, for a full affine family on a fixed number of coordinates. No extra
workspace is added. The universal statement is a written proof; the finite
engine tests only one slope row. Independent human and proof-kernel review
are unclaimed. Higher prices, partial families, other fields, physical
delivery/restoration, complete recursive invoices and supplier admission
remain outside scope. All five selected framework assumptions remain.

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
The selected record remains unchanged at kappa `0.003125804`. This is a side
lemma for header accounting, explicitly recorded as changed scope from
`bit-helper-contract` in [TASK.json](TASK.json). Sources in [SOURCES.json](SOURCES.json)
are historical task/selected-record provenance; there are no external live
replay inputs or pending Git-history dependencies.

## Open next questions

Does the charge multiset determine prices at least three? Begin with a
three-addition component containing two opposite slope charges and two
initially zero-charge coordinates. A four-vertex component can retain three
nonzero scalar charges, so the present one-settlement replacement argument
does not apply. Resolving this would decide whether hidden packet data can
be discarded in a full cost optimizer. This is a proposed next step, not a
counterexample or a claimed obstruction at three additions.

## Credit

The new two-addition theorem and verifier were produced by Nick Petalas.
SHIN09-git / PR6712 retains credit for the full-family settlement model,
component invariant, scalar-price theorem and original open question.
SHIN09-git / PR6710 supplies the common-image guard setup; ToikY and Nick
Petalas retain earlier full-header work, and the classical debt-partition
lineage retains its predecessor credit. No predecessor credit is changed.
Apache-2.0.
