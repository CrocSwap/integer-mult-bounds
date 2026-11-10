# One thin map misses the three-leaf paired star over F_2

No new kappa. At block size 2 and three leaves, the paired-star endpoint
cannot be met by one thin map when every block entry lies in F_2. The
two-map commuting construction still meets it, with ranks 4 and 4. This
does not construct or exclude the open g=13, q=8 or g=31, q=26 profiles.

## 1. Contract

Keep the paired-star contract of
`research/coupled31-chronology/PROOF.md`. The space is a core plus g=3
leaves, each of dimension d=2, over a field of characteristic two. Stage
j acts on the core and leaf j. On those two blocks,

```text
E_j = diag(I, I),    T_j = [[I, I], [I, I]],    T_j^2 = 0.
```

A full call is `(I + x_j P)(I + e R)` in `F[e, D_0, D_1, D_2] / (e^2)`,
where `x_j = D_j + 1`, `R = P T_j`, and the two projectors of a stage are
an orthogonal resolution of `E_j` and commute with `T_j`. A thin call is
`I + e Z` for a constant matrix Z. The target is

```text
(I + e) * product_j (I + x_j E_j).
```

The local form is

```text
P = [[A + B, B], [B, A + B]],    R = [[A, A], [A, A]].
```

For two halves, A and I+A are rank-1 idempotents. Both block matrices are
idempotent and annihilate each other. Entries of A and B are in F_2.
Call order is arbitrary. Exactly one thin map is allowed, in any gap,
including before the first call and after the last.

## 2. Statement

**Theorem.** No such word exists. The same endpoint is met by two thin
maps of ranks 4 and 4, using one diagonal resolution on every stage.

The chronological rank floor from the predecessor proof is

```text
sum of thin ranks >= 2d + 2 ceil((g - 2) / L) = 6
```

with `L = floor(d / r) + 1 = 3`. One matrix may have rank 6, 7, or 8, so
the floor does not already forbid one thin map. The commuting-projector
theorem in `COMMUTING.md` needs at least `ceil(g / 2) = 2` thin maps, but
only when every full projector commutes. The census below drops that
hypothesis.

## 3. The gate in characteristic two

Let `P R = R`. Then

```text
(I + x P)(I + e R) = I + x P + e (I + x P) R
                    = I + x P + e (1 + x) R.
```

In characteristic two, `1 + x = 1 + (D + 1) = D`, so the e coefficient of
a full call is `D R` and the pure part is `I + (D + 1) P`. The registered
checker tests `P R = R` and `R P = R` for every legal call. A thin call
contributes Z and does not change the pure product.

List order is chronological. The first call is applied first, so it is
the rightmost factor. For a thin map in the gap after the first k calls,

```text
e coefficient = L_k * Z * R_k + (sum of the full-call contributions),
```

where `R_k` is the pure product of the earlier calls and `L_k` is the
pure product of the later calls. The target's e coefficient equals its
pure product Q. Whenever `L_k` and `R_k` are invertible,

```text
Z = L_k^{-1} * (Q + full-call sum) * R_k^{-1}
```

is the only candidate in that gap. Each factor `I + (D + 1) P` is
singular exactly when D = 0, because P is a projector. Every
specialization used below has nonzero stage values, so every prefix is
invertible and no gap is skipped.

## 4. Why the screen is exhaustive over F_2

There are 16 matrices A in `M_2(F_2)`. The rank-1 idempotents, together
with every B, were filtered by the two block-matrix conditions. The
checker finds 12 unordered resolutions, 3 of them with B = 0. Of the
12 * 12 ordered pairs, 96 have noncommuting A factors, so the search is
not the commuting subcase.

Each stage chooses one of the 12 resolutions. The six full calls may
stand in any of 6! = 720 orders. That is 12^3 * 720 = 1,244,160 words.
A legal Z is constant and has entries in F_2. Any such Z remains the
same matrix after specialization. The checker specializes at

```text
(D_0, D_1, D_2) = (2, 3, 5) and (6, 7, 11)
```

in GF(256), with the AES polynomial `x^8 + x^4 + x^3 + x + 1`. If the
two specializations do not return the same constant 0-1 matrix in the
same gap, that gap has no legal Z. If they do, the candidate is
multiplied out in `F_2[D_0, D_1, D_2, e] / (e^2)` and compared with the
target. A specialization accident cannot pass that replay.

The registered run screens 1,244,160 orders. The pure product matches
the endpoint for 159,984 of them. No gap at the first point agrees with
the same constant 0-1 matrix at the second point, so `exact_checks` is
0 and the polynomial replay rejects nothing further: every word already
failed over GF(256). Ninety-six ordered pairs of resolutions have
noncommuting A factors.

The same arithmetic is locked against the polynomial word. For one
nonzero-B resolution and one swapped order, every gap's predicted pure
product and e coefficient, with a fixed probe Z, equal the specialized
polynomial word. Separately, the two-map control's second thin map is
recovered by the gap formula after the first map is kept.

## 5. Positive control

Use the same diagonal rank-1 idempotent on every stage, with B = 0.
Run both halves of stage 0, then stage 1, then stage 2. After each
even index (the odd 1-based stages in `COMMUTING.md`), insert the thin
map described there: both directions between the core and the named
leaves, with 2-by-2 identity blocks. The first map touches leaves 0 and
1. The last touches only leaf 2. Both have rank 4. The polynomial word
equals the target. Deleting the first thin map misses it. One thin map
on those six calls also misses it, which the census already covers.

An unsplit schedule, one full call equal to E_j on each stage, likewise
has no one-thin word. That is a separate negative check, not part of the
paired two-half census.

## 6. What this does not say

- It does not raise kappa and does not price a caller.
- It does not show that the rank floor 6 is sharp. The control has total
  thin rank 8.
- It does not treat projectors with entries outside F_2. A larger
  characteristic-two field has more rank-1 idempotents.
- It does not treat three or more full calls in one stage.
- It does not lift to g=13, q=8 or g=31, q=26. Those profiles remain
  unconstructed, and they remain impossible when the full projectors
  commute.
- There is no native lift, restoration, tape, or compiler claim.
