# Exact affine-lattice output hulls for rounded-linear programs

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written proof with exact finite corroboration.

For every finite rational rounded-linear program on integer parameters,
the complete output set is a computable finite union of translates of one
lattice. Its smallest containing affine lattice has an explicit finite
generating set. This gives a necessary and sufficient test for closure in
any proposed rational affine target lattice, including changing domains
and internally nested rounding nodes.

For `R(t)=floor(t+1/2)`, replace each rounding node by the identity and
propagate its argument's rational linear row. Let q clear every denominator
in these rows, M be the idealized output matrix and `C={0,...,q-1}^k`.
Then the new exact formulas are

```text
F(Z^k) = union_(c in C) (F(c) + q M Z^k)
hull_Z(F(Z^k)) = F(0) + span_Z({q M e_i}_i, {F(c)-F(0)}_c)
```

[PROOF.md](PROOF.md) proves translation equivariance by induction through
the actual rounded program and proves both equalities and minimality.
A larger permissible translation lattice may reduce the residue set.
The rectangular formula uses at most `q^k-1+k` generators; it makes no
polynomial-time or minimal-period claim.

The distinction between residues and drift matters. On the entrance
`x=3n, y=2m`, the shear `(x,y) -> (x,y+R(x/2))` has even second coordinates
on all four q=2 residue representatives. Nevertheless `F(2,0)=(6,3)`.
Its exact affine-lattice hull is `3Z x Z`, while the proposed target
`3Z x 2Z` fails. Ideal-image and residue-only closure tests both miss
information supplied by the formula. The output set itself is smaller
than its hull.

## Evidence and reproduction

From the repository root with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/rounded-program-affine-hull/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/rounded-program-affine-hull/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rounded-program-affine-hull
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rounded-program-affine-hull --check-source-history
```

Another CPython 3.12 path may substitute. The last command requires the
committed package. Direct verification is read-only and Git-free. It prints
a generated JSON receipt bound to all six package source hashes, followed
by `PASS_ROUNDED_PROGRAM_AFFINE_HULL`. Both direct modes are registered in
[VERIFY.json](VERIFY.json); the runner reports `PASS_REGISTERED_RESEARCH_PACKAGE`.

The finite census contains 80 one-parameter nested-rounding programs and
256 two-parameter rounded-shear programs with rational affine entrances.
Across these 336 programs it checks 3,904 residue outputs, 33,696 literal
outputs in signed parameter boxes and 6,336 affine target-closure comparisons.
The literal-output route generates its lattice without idealizing the
rounding nodes. All translation identities and hull comparisons agree.
These are enumerated fixtures, not a count of distinct functions.

An independent determinantal-minor check and rank-one content check cover
all 729 ordered triples of planar vectors with coordinates in `{-1,0,1}`.
Fourteen named semantic controls cover the drift counterexample, ideal
image, nested denominators, signed ties, a smaller nonrectangular period,
rank-zero and unrounded rational maps. Five malformed-program cases reject.
The universal statements rest on the written proof, rather than this census.

## Source, credit and scope

Credit woklerx [#1848](https://github.com/CrocSwap/integer-mult-bounds/pull/1848),
head `d975e19e7e931fc2b45792a4f7140ac13759a7da`, for the explicit question
about closure under intervening rounded updates and the affine-domain
mixed-precision interface. Its cancellation theorem is a cited result.
Retain Gareth Davidson, Chafik Boukhalfa and Ali Romman's precision and
dirty-restoration lineage credited there.

Adam Gall [#1908](https://github.com/CrocSwap/integer-mult-bounds/pull/1908)
already gives a source-specific internally rounded-leaf counterexample.
Nick Petalas [#6446](https://github.com/CrocSwap/integer-mult-bounds/pull/6446)
classifies a common invariant integer lattice for opposite planar rounded
shears. Those contracts are related context; neither result nor executable
is used as a step in this proof. Their numerical certificates are not
replayed. The new formula and general closure criterion above are the
contribution. The elementary translation, coset and integer-lattice
methods are classical, with no literature-wide priority claim.

[TASK.json](TASK.json) records a change from the caller-specific
`uniform-transfer-audit` card to this general precision-interface lemma.
The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19572796)
states the same mathematical scope. Canonical base is
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8 and selected
#7000. [SOURCES.json](SOURCES.json) binds the source question and related
packages as historical provenance. There are no external runtime inputs.

Live open PRs, this account's recent work, the latest handoff posts,
active discussions, local reservations, main-tree README terms and merged
PR searches were checked. The cached card scan covered 768 open PRs,
7,355 Discussion records and 10,178 local note records, with separately
reported freshness. A dedicated author/date scan of 768 open and 6,175
closed PRs found no recent account PR referencing #1848. Searches cover
titles, bodies and notes, not every code diff or unpublished result.

## Limits and verification design

The contract has fixed rational affine arithmetic and half-up rounding,
with finitely many nodes and unrestricted integer parameters. Variable
products, data-dependent branches, overflow and saturation are excluded.
The output lattice need not equal the actual reachable set. Replacing
a reachable set by its hull discards nonlattice information.

No actual selected caller, entrance contract or useful precision policy
is established. Complete native implementation, owners and restoration,
movement/storage/precision charges, recursive invoice and all five selected
framework assumptions remain open. No new kappa, supplier admission,
selected-frontier change or complete multiplication theorem is claimed.
Independent human and formal proof-kernel review are unclaimed. No
predecessor scientific replay, selected cold replay, Lean or Docker run
was performed.

The verifier has no recursion, subprocesses, external libraries or writes.
Its fixture contract limits inputs to two parameters, eight nodes and
period at most 12. Each literal parameter box therefore has at most 1,296
points; only one program's vectors are live. Package source reads are
capped at 128 KiB each. All checks remain active under optimized Python.
Functions fit within 60 physical lines. Python's dynamic allocation is
a managed-runtime deviation from fixed memory; these bounds constrain
live collections, while no allocation-free or static-analyzer claim is
made. Warning-strict normal and optimized execution provide the available
interpreter diagnostics.

## Open next questions

Apply the criterion to one literal selected rounded caller with an admitted
rational affine entrance. First extract its fixed rounded-linear fragment
and compute the residue outputs and drift vectors, then test the next
required source domain. The caller's exact entrance and reachability,
later inverse compatibility and complete precision, movement, storage and
restoration bill remain blockers. No continuation is part of this result;
the structured question is in [TASK.json](TASK.json).
