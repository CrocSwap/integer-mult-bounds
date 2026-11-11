# Matrix elements of the F9 operators off |0>

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Contract

Use the backward word `F9-SOURCE-DAG-ALL8-WORD.json.gz` inside the unchanged
packet `research/filtered-native-kappa004/inputs/original-packet.tar.gz`.
Its SHA256 is

```text
934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775
```

The 72 canonical warp classes and the four signed variants of `K_G` are those
of the merged fixed-vector audit. Amplitudes are the exact states of
`research/active-mode-delivery-frontier/source/quadratic.py`, SHA256

```text
d406584aed1479b75c387bc964b9e797b2f4f75e5f8c6bbea00df07f7d590a91
```

The domain is finite: 72 classes, the four signed variants, and all 512
computational basis states of width 9. The checker evaluates every triple.
This is an exhaustive census of that domain. It is not a statement about an
arbitrary invertible matrix, a full-frame transport, or a different word.

## Evaluation formula

For a class with column list `G_columns`, let `G` be the matrix produced by
`diagonal_data` in the checker: the transpose of those columns. Let `Q` be
its quadratic rows and `α` its linear signs, each `α_i` in `{0,1}`. The
forward circuit is the permutation `P_G`, `x -> Gx`, followed by the diagonal
gate `D(α)`. On a computational basis state the permutation contributes no
phase, and the diagonal gate sees the image address. With no support columns
its constant `i`-power is

```text
e_α(y) = Σ_i α_i y_i + 2 Σ_{i<j, Q_ij=1} y_i y_j    (mod 4).
```

The summand `2` is the empty-support product of two constant-one Boolean
forms, which is the rule in the pinned engine. Thus

```text
K_G |x> = i^{e_α(Gx)} |Gx>.
```

The state is one basis vector, the denominator is 0, and the phase is a unit
in `{1, i, -1, -i}`. The computational matrix element `<x|K_G|x>` is that
phase when `Gx = x`, and is 0 otherwise. It equals `+1` exactly when
`Gx = x` and `e_α(x) ≡ 0 (mod 4)`.

The backward variant uses linear signs `-α`. Each adjoint runs the diagonal
gate before the inverse permutation, so its phase is read at the input
address and its output address is `G^{-1}x`. The pinned engine agrees with
these four predictions at every class and every address.

## The phase-+1 set is a subspace

Write `S(G)` for the addresses with matrix element `+1`. Address `0` is in
every `S(G)`: the predecessor lemma `K|0> = |0>` is recomputed here for all
288 variants.

On `ker(G+I)`, the census finds `e_α(x) ∈ {0,2}`. Negating the exponent does
not change either value modulo 4, and `G^{-1}x = x` on that kernel. Therefore
the four signed variants have the same matrix element at every address: `+1`,
`-1`, or `0`.

The same census checks that `e_α` on the kernel equals the linear extension of
its values on one basis. A `{0,2}`-valued function with that property is a
character `x -> (-1)^{λ(x)}`. Hence `S(G) = ker(G+I) ∩ ker(λ)` is an
`F_2`-subspace. The recorded basis in `RESULT.json` spans exactly the
addresses the formula marks `+1`. Both checks run over every vector of every
kernel, not over a sample.

There are 114 pairs `(class, address)` where the address is fixed and the
matrix element is `-1`. One of them is exhibited: operator 6 sends `|328>` to
itself with phase `-1` in every signed variant. The scalar observer, which
leaves a coefficient unchanged, disagrees with `K_G` at that address.

## No nonzero address is common to every class

Operator 26 has `S = {0,1}`. Its recorded basis is the single vector `1`, and
the checker rejects any other phase-+1 address.

Operator 30 sends `|1>` to `|2>` with phase `+1`. The matrix element at
address 1 is 0, so `1` is not in its phase-+1 set. Operators 30 and 66 are
the only classes with that failure at address 1; the other 70 classes have
matrix element `+1` there. All four variants agree on both exceptions.

Every common phase-+1 address would have to lie in `S` for operator 26 and
in `S` for operator 30. The only such address is `0`. The direct intersection
of all 72 sets is checked separately and is also `{0}`.

## What this does not say

The formula prices `K_G`, the operator named by the scalar observer at `|0>`.
It does not price the full-frame transport `F† K_G F`. The predecessor audit
already separated those operators on `|0>`.

No caller, transport invoice, compiler, precision tape, or outer admission is
claimed. The selected conditional value stays
`363005817/100000000000`. The five framework assumptions stay in force.
