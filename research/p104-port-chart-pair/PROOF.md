# Port-dependent charts in the C_u family match a data line only when they are equal

No new κ. The selected conditional exponent stays `60403/20000000`.

## Changed premise

PR #4136 shows that a uniform chart `C_u` preserves its own encoding, and that
an exit `C_u` (`u ≠ 0`) does not match the single next entrance `C_0 = I`.
The open data-line question is the changed premise: the next entrance may be
any chart in the same family, not only `I`.

The address space is `F_2^4`, with the character basis of size 16. For
`u` in that space, `X_u` is diagonal,

```text
X_u |z⟩ = (-1)^{u·z} |z⟩,
```

and the published chart is

```text
C_u = ((1+i) I + (1-i) X_u) / 2.
```

Thus `C_u |z⟩ = |z⟩` when `u·z = 0`, and `C_u |z⟩ = i |z⟩` when `u·z = 1`.
In particular `C_0 = I`, and `C_u^{-1}` multiplies the odd set of `u` by `-i`.

An adjacent data line whose exit chart is `C_a` and whose next entrance chart
is `C_b` matches every data character when `C_b C_a^{-1}` acts by `1` on every
character.

## Classification

On a character `z`, the multiplier of `C_b C_a^{-1}` is:

| `a·z` | `b·z` | multiplier |
|---|---|---|
| 0 | 0 | 1 |
| 1 | 1 | 1 |
| 0 | 1 | `i` |
| 1 | 0 | `-i` |

The two dot products agree for every `z` if and only if `a` and `b` are the
same linear form, hence the same vector. Therefore

```text
C_b C_a^{-1} = I  ⟺  a = b.
```

If `a ≠ b`, write `g = a + b ≠ 0`. The characters where the forms disagree are
exactly `{z : g·z = 1}`, a set of size 8. Every one of those characters is
multiplied by `i` or by `-i`, so the pair fails on exactly half of the data
line. The other eight characters, where the forms agree, are fixed.

There are 16 charts and 256 ordered pairs. The 16 pairs with `a = b` match
every character. The other 240 pairs fail on exactly eight characters. The
15 pairs checked in #4136 are the column `b = 0`, `a ≠ 0` of this table.

## What the phase is doing

If the odd eigenvalue `i` is replaced by `1`, every `C_u` becomes `I` and every
ordered pair matches. The obstruction is the relative phase, not the support
of `X_u` alone. Forgetting that phase is a false witness; the verifier rejects
it by counting 16 matches rather than 256.

## Scope

This is the data-line half of the changed chart premise. Helper roles are not
in the model, and this note does not supply an intertwiner, a dirty
restoration, a hosting bill, or a supplier. A different chart family could
still match. The uniform pairs `a = b` do match; they are not port-dependent.
