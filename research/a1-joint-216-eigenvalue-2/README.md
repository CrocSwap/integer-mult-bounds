# Geometric multiplicity of eigenvalue 2

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

On the integer matrix `M` of `B = 4 A_1` in the pinned joint `(+1,+1)` basis
of dimension 216, the rational nullity of `M - 8 I` is 12. Eigenvalue 2 of
`A_1` therefore has geometric multiplicity 12. The same eigenvalue has
algebraic multiplicity 12.

No new kappa. The selected conditional kappa stays `781451/250000000`.

## Result

The matrix of `A_1` is `M/4`, so eigenvalue 2 of `A_1` is eigenvalue 8 of
`M`. Exact elimination of `M - 8 I` over `Q` gives

```text
rank_Q(M - 8 I) = 204,
dim_Q ker(M - 8 I) = 12.
```

Twelve integer kernel vectors, with entries in `-120..120`, satisfy
`(M - 8 I) v = 0` and are linearly independent over `Q`: on the free columns
they form a diagonal matrix whose product is `2^20 * 17^2`. A 204-by-204
minor is nonzero. The rank modulo `1000003` and modulo `1000033` is 204.
Each modular rank is a lower bound on the rational rank. Equality uses the
integer kernel.

The weighted Gram determinant of these 12 vectors is nonzero, and `M - 8 I`
is self-adjoint for the positive definite diagonal form of basis support
sizes. The ascent of eigenvalue 8 is 1, so the algebraic multiplicity is 12.
That count matches the recorded factor `(x - 2)^12`.

The argument is written in [PROOF.md](PROOF.md). The kernel certificate is
[evidence/kernel.json](evidence/kernel.json), SHA256
`23262c04465589eef2ea32c116de7e8b1aac284373d6bf842ea36842aebc4e54`.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal caller binding.
The live question is open question 1 of the eigenvalue-0 package, pull
request
[#7018](https://github.com/CrocSwap/integer-mult-bounds/pull/7018),
which pins geometric multiplicity 24 for eigenvalue 0 and does not run the
shifted elimination. The characteristic polynomial and the matrix come from
merged pull request
[#6964](https://github.com/CrocSwap/integer-mult-bounds/pull/6964).
This package computes one nullity. It does not recompute that polynomial and
does not recompute the eigenvalue-0 kernel.

Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/a1-joint-216-eigenvalue-2/verify.py
python3 -B -O research/a1-joint-216-eigenvalue-2/verify.py
python3 -B scripts/research_package.py --package research/a1-joint-216-eigenvalue-2 --check-only
```

The marker is `PASS_A1_JOINT_216_EIGENVALUE_2`. Acceptance uses explicit
checks, so `-O` does not skip a theorem or a rejection control. No Lean,
Docker, degree-881 replay, degree-216 characteristic polynomial, or selected
cold replay was run.

## Overlap

`scripts/find_overlap.py` was run on 2026-11-10 against upstream
`17469fff78c22941280f04d39dc5a1faee09c840`. Coverage at
2026-11-10T10:33:41Z: local note search complete, 10178 HEAD paths plus this
package's own uncommitted notes; 339 open PRs, pagination complete, fetched
2026-11-10T10:32:34Z; 7013 discussion records, pagination complete, fetched
2026-11-10T10:33:40Z. The phrases `M - 8 I`, `shifted elimination`, and
`geometric multiplicity of eigenvalue 2` matched this package and open pull
request
[#7018](https://github.com/CrocSwap/integer-mult-bounds/pull/7018), whose
body lists this nullity as an open question and states that the shifted
elimination was not run. No open PR computes it.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- Eigenvalue `-2` of `A_1` on this same matrix is the nullity of `M + 8 I`.
  The recorded algebraic multiplicity is 12. The shifted elimination for
  `M + 8 I` was not run.
- Eigenvalue 2 on each of the other three joint sign spaces is a separate
  matrix. Those matrices are not pinned here. Eigenvalue 0 on those spaces
  is the other open question of
  [#7018](https://github.com/CrocSwap/integer-mult-bounds/pull/7018).

## Credit

JoyboyBrian's handoff is discussion comment
[19144258](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144258).
The sign-stabilizer split supplied `g`, `t`, and dimension 216. Pull request
[#6964](https://github.com/CrocSwap/integer-mult-bounds/pull/6964) pinned the
basis, the matrix, and algebraic multiplicity 12 for eigenvalue 2. Pull
request
[#7018](https://github.com/CrocSwap/integer-mult-bounds/pull/7018)
recorded geometric multiplicity 24 for eigenvalue 0 and left this shifted
elimination open; the finding is discussion comment
[19514151](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19514151).
Ali Romman's PR4958 and PR4720 retain the query and the Bell action. Nick
Petalas's PR5120 is the degree-410 lower bound. Krzysztof Wojt's
`research/exact-one-slot-gram` is the degree-881 annihilator. The doubled
representation comes from PR1719. New work is Apache-2.0.
