# Geometric multiplicity of eigenvalue 0 on the other three 216 joint sign spaces

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, the four joint sign spaces of the
`c=1` sign stabilizer and the involutions `g` and `t` share one characteristic
polynomial. PR #6964 pins the joint `(+1,+1)` matrix. PR #7018 records
geometric multiplicity 24 for eigenvalue 0 on that one matrix and leaves the
other three matrices unpinned. On each of those three matrices the rational
nullity of `B = 4 A_1` is 24. Eigenvalue 0 of `A_1` therefore has geometric
multiplicity 24, equal to its algebraic multiplicity and equal to the
multiplicity recorded for the `(+1,+1)` matrix.

No new kappa. The selected conditional kappa stays `781451/250000000`.

## Result

The proof is in [PROOF.md](PROOF.md). For each sign pair `(+1,-1)`, `(-1,+1)`,
and `(-1,-1)`:

- the rational rank of the pinned 216-by-216 integer matrix is 192, so `dim_Q ker(M) = 24`;
- a 192-by-192 minor is nonzero modulo `1000003` and modulo `1000033`;
- 24 integer kernel vectors satisfy `M v = 0` and are linearly independent over `Q`;
- `D M` is symmetric for the positive diagonal `D` of basis support sizes, and the `D`-Gram determinant of the kernel is nonzero, so the ascent of eigenvalue 0 is 1 and the algebraic multiplicity is 24.

The three matrices differ from the pinned `(+1,+1)` matrix and from each other.
The rank modulo either prime is a lower bound on the rational rank. Equality
uses the kernel. Sharing the characteristic polynomial is not the nullity
argument.

| sign | certificate | SHA256 |
|---|---|---|
| `(+1,-1)` | [evidence/g-plus-t-minus.json](evidence/g-plus-t-minus.json) | `f3077453f9009ee4dd6cc4879cbd7ce6fdb8858f6083ce43d0e8c586473a44a8` |
| `(-1,+1)` | [evidence/g-minus-t-plus.json](evidence/g-minus-t-plus.json) | `b9e60ba3fc977503ef489ddd9b377ff02f8b9f70b580c539422f49d88533301d` |
| `(-1,-1)` | [evidence/g-minus-t-minus.json](evidence/g-minus-t-minus.json) | `58a4b4c053e1496e8824938b574e7773aaa9ad9da6edf1a031d5ff3a0e0282ed` |

Evidence class: a proof for each of the three pinned matrices. The four joint
sign pairs of these two involutions are exactly `(±1, ±1)`, so these three
pairs are the complete complement of the `(+1,+1)` matrix.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal caller binding.
The live question is open question 2 of PR #7018, which is itself open
question 2 of the characteristic-polynomial package merged as PR #6964. That
package records algebraic multiplicity 24 on all four joint sign spaces and
pins only the `(+1,+1)` matrix. PR #7018 computes the rational nullity of that
one matrix.

Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/a1-joint-216-other-nullity/verify.py
python3 -B -O research/a1-joint-216-other-nullity/verify.py
python3 -B scripts/research_package.py --package research/a1-joint-216-other-nullity --check-only
```

The marker is `PASS_A1_JOINT_216_OTHER_NULLITY`. Acceptance uses explicit
checks, so `-O` does not skip a theorem or a rejection control. No Lean,
Docker, degree-881 replay, selected cold replay, or recomputation of the
degree-216 characteristic polynomial was run.

## Overlap

`scripts/find_overlap.py` was run on 2026-11-10 against upstream
`17469fff78c22941280f04d39dc5a1faee09c840`. Coverage: local notes 10178 of
10178 HEAD paths, complete, before this package was committed; 339 open PRs,
pagination complete, fetched 2026-11-10T10:35:00Z; 7013 discussion records,
pagination complete, fetched 2026-11-10T10:26:58Z. A later discussion refresh
hit the GitHub rate limit and kept that complete snapshot. The phrases
`joint sign`, `geometric multiplicity`, and `216-by-216` match open PR #7018,
which records nullity 24 for the pinned `(+1,+1)` matrix and states that
these three matrices are not pinned. They also match merged PR #6964, which
records the common characteristic polynomial and not these ranks. No open PR
pins these three matrices or computes their rational nullities. Discussion comment
[19514151](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19514151)
is the finding for the `(+1,+1)` nullity. Comment
[19507672](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19507672)
records a dimension split of the same four spaces and does not compute this
rank.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- Eigenvalue 2 of `A_1` has recorded algebraic multiplicity 12. Its geometric multiplicity on each of these three pinned matrices is the nullity of `M - 8 I`. The same question on the already pinned `(+1,+1)` matrix is a separate computation.

## Credit

JoyboyBrian's handoff recorded the open decomposition question, discussion
comment
[19144258](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144258).
The sign-stabilizer split supplied `g`, `t`, and dimension 216 without a
basis. PR #6964 pinned the `(+1,+1)` basis, that matrix, the common
characteristic polynomial, and algebraic multiplicity 24. PR #7018 computed
the rational nullity of that one matrix and left these three matrices
unpinned. Ali Romman's PR4958 and PR4720 retain the query and the Bell
action. Nick Petalas's PR5120 is the degree-410 lower bound. Krzysztof Wojt's
`research/exact-one-slot-gram` is the degree-881 annihilator. The doubled
representation comes from PR1719. New work is Apache-2.0.
