# Nested and crossed pure products at g=31, q=26

**Status: proof of the pure-product step, plus one pure-product witness. No new kappa. The endpoint stays open.**

Selected frontier, unchanged:
`781451/250000000 = 0.003125804`
in `certificates/selected-result.json` at base
`17469fff78c22941280f04d39dc5a1faee09c840`.

## Scope and evidence

The assigned question is whether nested or crossing stage intervals, with
projectors that need not commute, can meet the paired-star endpoint at
`g=31`, `q=26` with five rank-26 thin maps. Open PR #7005 settled only the
consecutive-halves schedule and asked for the pure product of one crossed
pair and one nested pair before any `q=26` search. This package stops at
that product.

[PROOF.md](PROOF.md) proves three statements in the projector algebra.

- A nested pair equals the pure target if and only if the outer off-diagonal
  block `B` is zero. The inner block and commutation are free. If the outer
  `B` is nonzero, the coefficient of `x y` on the core-to-leaf block is that
  matrix. Thin maps do not appear in the pure part, so they cannot repair it.
  The same failure survives any number of adjacent stages placed entirely
  outside the nest. At `g=31` that is a scoped obstruction for this schedule,
  including five rank-26 maps.
- With both off-diagonal blocks zero, a crossed pair equals the pure target
  if and only if the two idempotents commute. Commuting full projectors remain
  the separate `ceil(g/2) = 16` map-count in `research/coupled31-chronology/COMMUTING.md`.
- There is an explicit equal-half witness, a direct sum of thirteen `F_2^4`
  seeds, with core dimension `52` and half-rank `26`, whose projectors do not
  commute and whose crossed pure product equals the target. Concatenating a
  noncommuting nest with outer `B = 0` and this cross also matches the pure
  target, as does one adjacent stage on either side. This is a pure-product
  witness only. The coefficient of `e` was not computed, so it is not an
  endpoint witness and not a construction of the profile.

The argument is an identity in the projector algebra, checked by a sound
expansion of the defining relations, plus finite matrix multiplication for the
witness and the `q=26` direct sums. It is not a census of call orders or
projectors, and it is not a heuristic search. Unrestricted nonexistence of
the `g=31`, `q=26` profile is not a result. The `g=13`, `q=8` profile is not
reported.

No new kappa. Five rank-26 maps have total rank `130`. That number is not a
new lower bound.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 scripts/research_package.py --package research/g31-q26-nested-crossed-pure --check-only
python3.12 scripts/research_package.py --package research/g31-q26-nested-crossed-pure
```

Direct replay:

```sh
python3 -B research/g31-q26-nested-crossed-pure/verify.py
```

The passing marker is `PASS_G31_Q26_NESTED_CROSSED_PURE` with `endpoint=open`
and `kappa=781451/250000000`. The checker drops `AB+BA = B` and requires the
one-stage factor to fail. It compares the nested and crossed word expansions
with the closed forms, then multiplies the explicit `q=26` matrices.

Source pins are in [SOURCES.json](SOURCES.json). The catalogue card and the
selected record are provenance. The coupled-star proof and commuting note
are pinned at the same base commit. Full Git history is required to resolve
those blobs.

## Open next questions

1. For a nest with outer `B = 0`, or for the crossed witness above, with every
   other stage adjacent and outside that block, can thin maps of total rank
   `130` cancel the coefficient of `e` at `g=31`, `q=26`?
   The pure product already matches, so this is the remaining endpoint
   question for these schedules. A useful first step is the core-to-leaf
   coefficient of `e` after dividing by the pure scalar product, in one of
   the two families. No such coefficient is computed here. A later incomplete
   search would not be a proof.

2. Which crossed pairs with a nonzero off-diagonal block have pure product
   equal to the target, beyond the direct-sum witness?
   The `B = 0` case is settled by the commutator. A useful first step is the
   core-core coefficient of `x y` for general `B`, as the commutator of
   `A+B`, and the higher coefficients that remain when that commutator
   vanishes. The witness shows that the set is nonempty and can be
   noncommuting. It does not list the set.

## Credit

The paired-star contract and the commuting map-count are from PR #5747
(Ali Romman), including PR #5673, PR #5631, and PR #5617. Cinna Davis supplied
the controller/simplex lineage those packages retain. Open PR #7005 asked this
pure-product question and proved the separate consecutive-halves rank bound.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
