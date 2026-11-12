# Geometric multiplicity of eigenvalue 0 on one 48-dimensional eigenspace of s

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, the eigenvalue-`+1` space of
`s = (0 4 3 7)(5 6)` on the moved character `eps[1] * eps[2]` carries the
integer matrix of `B = 4 A_1` pinned by open PR #7036. The rational nullity
of that 48-by-48 matrix is 10. Eigenvalue 0 of `A_1` therefore has geometric
multiplicity 10, equal to its algebraic multiplicity.

No new kappa. The selected conditional kappa stays `781451/250000000`.

## Result

The proof is in [PROOF.md](PROOF.md). On the pinned 48-by-48 matrix `M`:

- the rational rank is 38, so `dim_Q ker(M) = 10`;
- a 38-by-38 minor is nonzero modulo `1000003` and modulo `1000033`;
- 10 integer kernel vectors, with entries at most 2 in absolute value, satisfy `M v = 0` and are linearly independent over `Q`;
- `D M` is symmetric for the positive diagonal `D` of basis support sizes, and the `D`-Gram determinant of the kernel is nonzero, so the ascent of eigenvalue 0 is 1 and the algebraic multiplicity is 10.

The rank modulo either prime is a lower bound on the rational rank. Equality
uses the kernel. The kernel certificate is
[evidence/kernel.json](evidence/kernel.json), SHA256
`ef25ff41864e6e918681cf7ecec31217a92704b735378d1f75f0e9acec9dbf3a`.

The matrix and basis are byte copies of the predecessor blobs, because
commit `0a670e4db89c79e6536dd4f448da0664d3f73890` is not on main:

```text
matrix  32b45cef4c1461f81b7b04b07ad388058cd872159a3f29107c6fe47ada6c4eae
basis   c18744f28d41c76a9b4299539a8c56e197a16850dd7ccc32aa7d227a48ef6764
```

Evidence class: a proof for this one pinned matrix.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal caller binding.
The live question is open question 2 of the characteristic-polynomial
package, PR #7036: the geometric multiplicity of eigenvalue 0 on this
matrix. The predecessor records algebraic multiplicity 10 and states that a
modular rank is only a lower bound.

Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/c1-moved-48-nullity/verify.py
python3 -B -O research/c1-moved-48-nullity/verify.py
python3 -B scripts/research_package.py --package research/c1-moved-48-nullity --check-only
```

The marker is `PASS_C1_MOVED_48_NULLITY`. Acceptance uses explicit checks,
so `-O` does not skip a theorem or a rejection control. No Lean, Docker,
degree-881 replay, selected cold replay, or recomputation of the degree-48
characteristic polynomial was run. When the predecessor commit is in the
clone, the verifier also checks that the vendored bytes and the recorded
factor `(10, (0, 1))` are that commit's objects.

## Overlap

Checked on 2026-11-10 against upstream
`17469fff78c22941280f04d39dc5a1faee09c840`.
`scripts/find_overlap.py "geometric multiplicity" "48-by-48" "pinned 48" --offline`
covered 10178 of 10178 HEAD notes and found no computation of this nullity.
The offline cache had no usable open-PR or discussion snapshot. A GitHub
search of open pull requests for `geometric multiplicity` returns PR #7036,
which asks this question, and PR #7018, which records geometric multiplicity
24 on the different 216-by-216 matrix. Fork PR 209 cuts one 48-dimensional
eigenspace by a 12-dimensional invariant subspace and does not compute the
nullity of this pinned matrix.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- Eigenvalue 2 of `A_1` has recorded algebraic multiplicity 6. Its geometric multiplicity is the nullity of `M - 8 I` on this same pinned matrix.
- Eigenvalue `-2` of `A_1` has recorded algebraic multiplicity 6. Its geometric multiplicity is the nullity of `M + 8 I` on this same pinned matrix.
- The eigenvalue `-1` space of `s` on the same character has the same recorded characteristic polynomial. Its matrix is not pinned here.

## Credit

JoyboyBrian's handoff recorded the open decomposition question, discussion
comment
[19144258](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144258).
PR #7036 pinned this basis, this matrix, and algebraic multiplicity 10.
PR #7009 recorded `s` and the multiplicity pattern `48^4` without a basis.
The sign-stabilizer split supplied `g` and `t`. The rank method follows
`research/a1-joint-216-nullity/` on a different matrix. Ali Romman's PR4958
and PR4720 retain the query and the Bell action. Nick Petalas's PR5120 is
the degree-410 lower bound. Krzysztof Wojt's `research/exact-one-slot-gram`
is the degree-881 annihilator. The doubled representation comes from PR1719.
New work is Apache-2.0.
