# Geometric multiplicity of eigenvalue 0 on one 216-dimensional joint eigenspace

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, the joint `(+1,+1)` eigenspace of
the `c=1` sign stabilizer and the two involutions `g` and `t` carries the
integer matrix of `B = 4 A_1` pinned by
[research/a1-joint-216-charpoly](../a1-joint-216-charpoly/). The rational
nullity of that matrix is 24. Eigenvalue 0 of `A_1` therefore has geometric
multiplicity 24, equal to its algebraic multiplicity.

No new kappa. The selected conditional kappa stays `781451/250000000`.

## Result

The proof is in [PROOF.md](PROOF.md). On the pinned 216-by-216 matrix `M`:

- the rational rank is 192, so `dim_Q ker(M) = 24`;
- a 192-by-192 minor is nonzero modulo `1000003` and modulo `1000033`;
- 24 integer kernel vectors, with entries at most 10 in absolute value, satisfy `M v = 0` and are linearly independent over `Q`;
- `D M` is symmetric for the positive diagonal `D` of basis support sizes, and the `D`-Gram determinant of the kernel is nonzero, so the ascent of eigenvalue 0 is 1 and the algebraic multiplicity is 24.

The rank modulo either prime is a lower bound on the rational rank. Equality uses the kernel. The kernel certificate is
[evidence/kernel.json](evidence/kernel.json), SHA256
`4eefc84f2750988bfe22056387b427fd9de1c09093c6e4be480ffe209b207714`.

Evidence class: a proof for this one pinned matrix.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal caller binding.
The live question is open question 2 of the characteristic-polynomial package,
merged as PR #6964: the geometric multiplicity of eigenvalue 0 on this
matrix. The predecessor records algebraic multiplicity 24 and states that a
modular rank is only a lower bound.

Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/a1-joint-216-nullity/verify.py
python3 -B -O research/a1-joint-216-nullity/verify.py
python3 -B scripts/research_package.py --package research/a1-joint-216-nullity --check-only
```

The marker is `PASS_A1_JOINT_216_NULLITY`. Acceptance uses explicit checks,
so `-O` does not skip a theorem or a rejection control. No Lean, Docker,
degree-881 replay, selected cold replay, or recomputation of the degree-216
characteristic polynomial was run.

## Overlap

Checked on 2026-11-10 against upstream
`17469fff78c22941280f04d39dc5a1faee09c840`. GitHub pull-request search for
`geometric multiplicity` returns only merged PR #6964, whose package leaves
this rank uncomputed. Open PR #7008 records normalizer isotypic dimensions
8, 80, and 128 on this same space and does not compute a characteristic
polynomial or this nullity. Open PR #7009 splits the sign characters moved
by `g` and `t`; those characters have dimensions 432, 192, and 80. This
package does not intersect the 24-dimensional kernel with the isotypics of
#7008.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- Eigenvalue 2 of `A_1` has recorded algebraic multiplicity 12. Its geometric multiplicity is the nullity of `M - 8 I` on this same pinned matrix.
- The other three joint sign spaces have the same characteristic polynomial. Their matrices are not pinned here, so the same rank question is open for each of them.

## Credit

JoyboyBrian's handoff recorded the open decomposition question, discussion
comment
[19144258](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144258).
The sign-stabilizer split supplied `g`, `t`, and dimension 216 without a
basis. PR #6964 pinned this basis, this matrix, and algebraic multiplicity
24. Ali Romman's PR4958 and PR4720 retain the query and the Bell action.
Nick Petalas's PR5120 is the degree-410 lower bound. Krzysztof Wojt's
`research/exact-one-slot-gram` is the degree-881 annihilator. The doubled
representation comes from PR1719. New work is Apache-2.0.
