# The fixed P120 quadratic space cannot attain rank 15

This contribution was produced by Nick Petalas.

Claim type: finite certificate with a scoped algebraic proof. Over every field
of characteristic three, legal P120 patterns whose columns lie in #7087's fixed
36-dimensional quadratic space have rank at least 16. Sixteen uniquely forced
columns and a nonzero minor certify this. A new explicit rank-31 point belongs
to the same space, lowering its cited constructive ceiling from 32 to 31.
Thus the restricted minimum lies in [16,31]; its exact value remains open.

unpaidmoon's [#7014](https://github.com/CrocSwap/integer-mult-bounds/pull/7014)
already gives an unrestricted rank-15 clique construction. The new obstruction
shows that this particular quadratic space cannot attain that rank. The rank-31
point is not an improvement to the unrestricted window bound. There is no new
kappa, physical decoder or selected-frontier change.

[PROOF.md](PROOF.md) defines the space and proves the uniform field consequence.
[FACTOR.json](FACTOR.json) contains the obstruction and the complete rank-31
factors. The standalone checker runs no predecessor verifier.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error -X dev research/p120-char3-rank31-window/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error -X dev -O research/p120-char3-rank31-window/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p120-char3-rank31-window
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p120-char3-rank31-window --check-source-history
```

Another CPython 3.12 path may replace the local interpreter path. The scientific
marker is `PASS_P120_CHAR3_RANK31 no_new_kappa`. The verifier prints a generated
receipt bound to all eight package files and writes no files. The publication
check needs full Git history; the scientific checker needs neither Git nor
network access.

The exact checks cover all 14,400 product entries, 120 diagonal entries, 6,720
forced zeros, three rank-31 determinants, 3,720 fixed-space membership entries,
912 forced-column equations, 16 uniqueness determinants and a nonzero 16 by 16
minor. Eleven rejection controls cover malformed certificates and violations of
the mask, rank, fixed-space membership, forced columns and independence. Three
small determinant fixtures cover identity, row-swap and singular matrices.

## Scope and limitations

Card `complex-rank-shape-decoder`, priority revision 8, changes scope from a
complete signed-moment improvement to a fixed-space obstruction and finite
construction. The source-bound baseline command passed at the selected #7000
checkpoint. The older catalogue context is not the selected frontier.

The initial target was a new unrestricted rank-31 upper bound answering #7087.
A broader PR check exposed #7014's stronger prior construction. The
[scope correction](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19542514)
records this before publication. The main new result is the restriction forcing
rank at least 16, so the fixed space misses the known unrestricted rank 15.

No optimal restricted rank, characterization of all rigid columns, physical
native implementation or complete supplier invoice is claimed. The five selected
framework assumptions remain unchanged. No predecessor scientific suite,
selected scientific replay, Lean or Docker run was performed. Independent human
and formal proof-kernel review are unclaimed.

The verifier has fixed dimensions and bounded loops, with a 64 KiB certificate
limit. Python allocates bounded temporary lists during this one-shot check;
this managed-runtime deviation is limited to matrices at most 120 by 120 and
has no retained outputs. Indirect calls are restricted to the named determinant
and negative-control routines. Warning-strict normal and optimized runs check
the same artifact. Shared code and diagnostics configuration are unchanged.

## Open next questions

1. What is the exact minimum rank inside this fixed quadratic space? The new
   bounds are 16 and 31. A first step is a common hyperplane meeting every legal
   affine fiber inside the delivered rank-31 span. A failed search would not
   prove a lower bound for all subspaces.
2. Which enlargement or change of the quadratic space admits a rank-15 point?
   Start by representing the cited #7014 clique columns in a larger feature
   space. Their membership and the cost of a useful decoder remain open here.
3. Is any of this finite-field structure useful in characteristic zero? Start
   with a separate exact mask factorization and its complete paid invoice.
   Reduction modulo three alone does not supply that implementation.

## Credit and sources

unpaidmoon supplies the fixed quadratic space, rank-32 construction and open
questions in [#7087 at 043b334e](https://github.com/CrocSwap/integer-mult-bounds/blob/043b334e7249e8b79e437a0765773a7e2fc8b8e8/research/p120-char3-rank32-window/README.md),
the quadratic predecessor in [#6953](https://github.com/CrocSwap/integer-mult-bounds/pull/6953),
the stronger unrestricted clique construction in [#7014](https://github.com/CrocSwap/integer-mult-bounds/pull/7014),
and the earlier odd-characteristic bound in [#6946](https://github.com/CrocSwap/integer-mult-bounds/pull/6946).
DreamingOfClouds supplies the port-window definition and family in
[#6933](https://github.com/CrocSwap/integer-mult-bounds/pull/6933).
Bukh, Cox, Blasiak and Haemers retain the fractional Haemers framework credit.
Finite-field elimination, rank factorization and scalar extension are classical.
The new fixed-space obstruction, rank-31 factors and standalone checker were
produced by Nick Petalas. Apache-2.0; see [NOTICE](NOTICE).

Cited pending predecessors are not replay dependencies. Their bytes are not
needed to check this certificate. SOURCES.json pins catalogue and selected-record
provenance. The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19542430)
and the scope correction state the change in the research question.
