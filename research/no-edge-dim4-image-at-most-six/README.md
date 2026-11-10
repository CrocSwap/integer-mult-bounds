# No-edge pattern dimension 4 has total image at most 6

**Result.** A complete no-edge pool of binary rank-one idempotents whose
off-diagonal pattern space has dimension 4 has joint image of dimension at
most 6. Dimension 6 is attained, and every such pool is reducible there. The
largest irreducible joint image therefore has dimension at most 5. The pool
in #7094 attains 5, and this package rechecks that witness. **No new κ.**
The selected value remains `781451/250000000`.

The three dimension-6 geometries are a pair of disjoint normal-form triples,
a pair of column triples on different columns, and one column triple beside
one normal-form triple. Each is reducible: the normal-form pair has an
invariant 3-dimensional block, and the other two have a nontrivial common
kernel.

## Scope and evidence

Catalogue card: `bit-new-register-model`, priority revision 8, base commit
`f16923d466a6aba912299882e0545564d2ba7bb2`. Scope status: **changed**. The
card asks for a new register alphabet. This package answers the open question
of #7094, which asks whether irreducible joint image 6 is possible after
#7094 attained 5. The reason is recorded in [TASK.json](TASK.json). The
original native acceptance gate is unmet, and the selected frontier is
unchanged. Question 1 of #6921, paid-rank accounting after a relation split,
is not this result.

[PROOF.md](PROOF.md) is the argument. Any six independent images have
patterns in one of four combinatorial types, and the verifier enumerates all
5005 six-point subsets of F2^4. A meet-1 type is impossible by Lemma 3 of
#6838. A cap or a one-triple type contains a diagonal quadruple, and that
quadruple forces total dimension at most 5. The only remaining type is two
disjoint triples. Each triple is a column triple or a normal-form triple by
the #6921 classification; the verifier repeats the 168-element GL(3,2)
census. Those three geometries have dimension exactly 6 and are reducible.

[verify.py](verify.py) repeats the two finite censuses, rebuilds the three
dimension-6 pools (including one spare coordinate), and rechecks the #7094
dimension-5 pool at widths 5 through 8, including its subspace lattice.
Deleting the last dimension-5 projector leaves an invariant subspace, and
one normal-form block alone is reducible, so the lattice scan is not
hard-wired to one answer. These checks certify the witnesses and the
censuses. They do not enumerate all four-dimensional pattern spaces. The
case split in the proof is what covers every pool and every width.

Source pins are in [SOURCES.json](SOURCES.json). The catalogue is provenance
at the base commit, and the selected record is an input because the verifier
reads it. Full Git history is needed to resolve the pins. Nothing here reruns
the selected baseline as a scientific replay.

Overlap was rechecked on 2026-11-10 against 406 open and 6175 closed upstream
PR records and 7014 discussion records, with a complete local note inventory
at base `f16923d466a6aba912299882e0545564d2ba7bb2`. The search terms were
"irreducible joint image", "pattern dimension 4", "joint-image dimension",
and "no-edge pool". The matches are the predecessor chain: #5921 (fiber
lemma), #6782 (edge quotient), #6785 (one-edge exclusion), #6838 (total image
at most 4 for pattern dimension at most 3), #6921 (irreducible bound 3),
#6962 (irreducible dimension 4), and #7094 (irreducible dimension 5, leaving
dimension 6 open). No match is not a novelty certificate. Open upstream PRs
through #7105 do not take this question.

## Reproduce

From the repository root, with Python 3.12 and the standard library only:

```sh
python3 -B research/no-edge-dim4-image-at-most-six/verify.py
python3 -I -O -B research/no-edge-dim4-image-at-most-six/verify.py
python3 -B scripts/research_package.py --package research/no-edge-dim4-image-at-most-six --check-only
python3 -B scripts/research_package.py --package research/no-edge-dim4-image-at-most-six
```

The verifier prints `PASS_NO_EDGE_DIM4_IMAGE_AT_MOST_SIX`.

## Open next questions

1. **Pattern dimension 5.** Does a complete no-edge pool of pattern dimension
   5 still have total joint image at most 6, and can its irreducible image
   exceed 5? The parity construction one dimension higher has total image 6,
   while the edge-quotient bound only gives 31. The four-dimensional census
   does not carry over.

2. **Coordinate classification at dimension 6.** Is every dimension-6 pool a
   coordinate permutation of one of the three witnesses? The dimension bound
   does not need that list.

3. **Paid rank.** After a valid relation split, does irreducible dimension at
   most 5 change a three-relation paid-rank obstruction? This remains
   question 1 of #6921. The split hypotheses are not proved here.

## Credit

The fiber lemma is Nick Petalas, #5921. The total-image bound and Lemma 3
are CubeJerry, #6838. The triple classification and the irreducible bound 3
are #6921. The dimension-4 irreducible 4-cycle is #6962. The dimension-5
irreducible witness rechecked here is #7094. Prepared by unpaidmoon with
substantial Cursor Grok assistance. New work is Apache-2.0.
