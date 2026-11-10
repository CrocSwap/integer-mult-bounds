# Characteristic polynomial of one 8-dimensional c=1 joint eigenspace

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, the unique 32-dimensional character
of the `c=1` sign stabilizer is the product of the signs on coordinates
`1, 2, 5` and `6`. Inside that character, the joint `(+1,+1)` eigenspace of
the involutions `g` and `t` is an 8-dimensional `A_1`-invariant subspace
supported on query coordinate 0. Its monic characteristic polynomial over `Q`
is

```text
x^4 (x-2)^2 (x+2)^2 = x^8 - 8 x^6 + 16 x^4.
```

No new kappa. The selected conditional kappa stays `781451/250000000`.

## Result

The sign stabilizer `H` is the order-16 group of sign patterns supported on
coordinates `{1,2,5,6}`. The trace formula gives character dimensions
`{864: 1, 432: 4, 192: 6, 80: 4, 32: 1}`. Exactly one character has dimension
32, and it is `chi(eps) = eps[1] eps[2] eps[5] eps[6]`. Both `g` and `t`
preserve it. The four joint sign spaces each have dimension 8.

On the pinned `(+1,+1)` space, write `B = 4 A_1`. The matrix of `B` is the
8-by-8 block matrix in [PROOF.md](PROOF.md), with entries in `{-4,0,4}`. Then
`chi_{A_1}(x) = 4^{-8} chi_B(4x)`, and

```text
chi_B(x) = x^4 (x-8)^2 (x+8)^2 = x^8 - 128 x^6 + 4096 x^4.
```

Ascending-coefficient SHA256 values are

```text
chi_A  4078d16db1834dcd427c4f1094b96838a2c425c116c7cd1b60d46aa1f472f632
chi_B  04375398447c3b08683582cc785814e9955ed62fcaa6725dc3467484c8a41457
```

The same polynomial is the characteristic polynomial on each of the four
joint spaces. Those spaces direct-sum to the 32-dimensional character space,
so the characteristic polynomial there is `x^{16} (x-2)^8 (x+2)^8`.

On each of the four joint matrices, `M(M^2 - 64 I) = 0`, and the exact
rational nullities of `M`, `M-8I` and `M+8I` are `4`, `2` and `2`. Thus
`A_1` is diagonalizable on each of them with minimal polynomial
`x(x-2)(x+2)`. Explicit eigenvectors for the pinned `(+1,+1)` basis are in
[evidence/kernels.json](evidence/kernels.json). The basis and the character
values are in [evidence/basis.json](evidence/basis.json) and
[evidence/character.json](evidence/character.json).

Each of `x`, `x-8` and `x+8` divides every published `c=1` sector minimal
polynomial in `research/exact-one-slot-gram/CERTIFICATE.json`. That
comparison evaluates coefficients. It does not replay the degree-881
certificate.

This space lies in a nontrivial character, so it meets the 216-dimensional
trivial-character joint space only at zero. It is not the 8-dimensional
isotypic summand of the signed normalizer of that 216-space.

## Evidence class

Proof of one finite identity. `H` is enumerated from all 128 sign patterns
with positive sign on coordinate 0, and all 16 of its characters are
evaluated. The joint space is the full solution space of the eigenvalue
equations, with dimension matching the trace formula. The polynomial is the
exact determinant of an explicit 8-by-8 integer matrix. This is not a
heuristic or incomplete search, and it is not an unrestricted nonexistence
claim.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal caller binding.
The live question is the characteristic polynomial left open by
[PR #6964](https://github.com/CrocSwap/integer-mult-bounds/pull/6964),
recorded in `research/a1-joint-216-charpoly/TASK.json` and in discussion
comment
[19507309](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19507309).
The sign-stabilizer split supplied the dimension 8 without the character's
signs or a basis. This package names the character and computes one
polynomial.

Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`. The priorities note on this commit still quotes
an older decimal; the selected record is the frontier value used here.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/a1-joint-8-charpoly/verify.py
python3 -B -O research/a1-joint-8-charpoly/verify.py
python3 -B scripts/research_package.py --package research/a1-joint-8-charpoly --check-only
```

The marker is `PASS_A1_JOINT_8_CHARPOLY`. Acceptance uses explicit checks,
so `-O` does not skip a theorem or a rejection control. No Lean, Docker,
degree-881 replay, or selected cold replay was run. The rational nullities
above are for this 8-by-8 matrix only.

## Overlap

`scripts/find_overlap.py` was run on 2026-11-10 against upstream
`17469fff78c22941280f04d39dc5a1faee09c840`. Coverage: local notes 10178 of
10178 HEAD paths, complete; 317 open PRs, pagination complete, fetched
2026-11-10T08:45:16Z; 6971 discussion records, pagination complete, fetched
2026-11-10T08:46:12Z. The phrase `8-dimensional joint` matched only discussion
comment 19507309, which asks for this polynomial and records the degree-216
polynomial instead. The phrase `unique 32-dimensional` matched that comment
and the sign-stabilizer finding
[19492873](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19492873),
which records dimensions and no polynomial. No open-PR body contained either
phrase.

[PR #6964](https://github.com/CrocSwap/integer-mult-bounds/pull/6964) is the
216-dimensional characteristic polynomial. Open
[PR #7008](https://github.com/CrocSwap/integer-mult-bounds/pull/7008) splits
the trivial-character 216-space under its signed normalizer and states that
it does not compute a characteristic polynomial. Its 8-dimensional summand is
the one in that trivial character. Open
[PR #7009](https://github.com/CrocSwap/integer-mult-bounds/pull/7009) splits
the characters that `g` and `t` move and states that it does not compute a
characteristic polynomial. Neither computes this polynomial. The geometric
multiplicity of eigenvalue 0 on the 216-by-216 matrix remains the question
left beside this one; it is not answered here.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- The four joint spaces are isospectral. This package does not exhibit a
  signed permutation, outside the group generated by `H`, `g` and `t`, that
  carries the pinned `(+1,+1)` basis onto one of the other three. The
  polynomial already splits each space, so that element is not needed for
  reducibility. This is not the question of a non-scalar action on the
  216-dimensional trivial-character summand.

## Credit

The sign-stabilizer split, PR #6944, recorded the unique 32-dimensional
character and the joint dimensions 8 without listing signs or a basis. PR
#6964 computed the characteristic polynomial of one 216-dimensional
trivial-character joint space and left this polynomial open. JoyboyBrian's
handoff, discussion comment 19144258, recorded the original decomposition
question. Ali Romman's PR4958 and PR4720 retain the query and the Bell
action. Krzysztof Wojt's exact one-slot package is the degree-881 annihilator
and the sector coefficient list used for the divisibility comparison. The
doubled representation comes from PR1719. New work is Apache-2.0.
