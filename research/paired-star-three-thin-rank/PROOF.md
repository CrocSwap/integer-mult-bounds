# Three F_2 thin maps meet total rank 6 on the three-leaf paired star

No new kappa. At block size 2 and three leaves, the paired-star contract
has an explicit word with three thin maps of ranks 2, 2 and 2. The
chronological floor of 6 is therefore attained once three maps are
allowed. The two-map lower bound of 8 stays in force. This does not
build a caller and it does not touch the selected frontier.

## 1. Contract

Keep the paired-star contract of
`research/coupled31-chronology/PROOF.md`. The space is a core plus g=3
leaves, each of dimension d=2, over a field of characteristic two. Stage
j acts on the core and leaf j. A full call is `(I + x_j P)(I + e R)` in
`F_2[e, D_0, D_1, D_2] / (e^2)`, where `x_j = D_j + 1`, `R = P T_j`, and
the two projectors of a stage are an orthogonal resolution of `E_j` and
commute with `T_j`. A thin call is `I + e Z` for a constant matrix Z with
entries in F_2. The target is

```text
(I + e) * product_j (I + x_j E_j),
```

with the product taken from stage 0 on the right through stage 2 on the
left. The local form is

```text
P = [[A + B, B], [B, A + B]],    R = [[A, A], [A, A]].
```

A and I+A are rank-1 idempotents over F_2. There are 12 unordered
resolutions. Of the 12*12 ordered pairs, 96 have noncommuting A factors.
Each stage uses exactly two full calls. Consecutive thin calls in one gap
add, so a word has one matrix in each of the seven gaps. Chronological
order means the first call is the rightmost factor.

The predecessor rank bound gives

```text
sum of thin ranks >= 2d + 2 ceil((g - 2) / L) = 6
```

with L=3. `COMMUTING.md` needs at least two thin maps when every full
projector commutes, and its sharp construction at g=3 uses ranks 4 and 4.
One thin map is impossible, and every two-map word has rank sum at least
8. A rank sum of 6, if it exists, needs at least three nonzero maps.

## 2. Statement

**Theorem.** In this contract there is a word with exactly three nonzero
thin maps, of ranks 2, 2 and 2, whose product equals the target. Deleting
any one of those maps misses the target. The chronological floor of 6 is
attained. The word uses a noncommuting pair of stage projectors, so it is
not the commuting construction.

The theorem is one explicit identity. It does not say that every three-map
word has rank 6, and it does not reopen the two-map bound.

## 3. The word

Stages 0 and 1 use the resolution with A-bits `0001` and B-bits `0010`.
Stage 2 uses A-bits `0011` and B-bits `0000`. These three pairs are among
the 12 enumerated resolutions. The A factor of stage 0 does not commute
with the A factor of stage 2.

Number calls by `stage * 2 + half`, where half 0 carries A and half 1
carries I+A. The chronological order, earliest call first, is

```text
4, 2, 3, 0, 1, 5.
```

That is stage 2's first half, both halves of stage 1, both halves of
stage 0, then stage 2's second half. Each stage occurs twice.

The thin maps sit in gaps 1, 3 and 5. Gaps 0, 2, 4 and 6 are zero. Rows
are bitmasks, low bit on the left of the integer:

```text
gap 1: d2 00 00 00 00 03 03 00    rank 2
gap 3: 00 2e 01 00 01 01 00 00    rank 2
gap 5: 86 86 00 02 00 00 02 02    rank 2
```

## 4. The identity

Multiply in `F_2[D_0, D_1, D_2, e] / (e^2)` from the right. Because
`P R = R` and `x = 1 + D` in characteristic two, a full call is
`I + x P + e D R`. A thin call is `I + e Z`. The product of
`(A_0 + e A_1)(B_0 + e B_1)` is `A_0 B_0 + e (A_0 B_1 + A_1 B_0)`.

Every factor `I + x P` has degree 1 in only one stage variable, and each
stage occurs twice, so the pure product and the e coefficient have
multi-degree at most `(2, 2, 2)`. The multiplier aborts if a product
would exceed that degree. The checked product has no such term. Its pure
part equals `product_j (I + x_j E_j)`, and its e coefficient equals that
same matrix, which is the e coefficient of `(I + e)` times the pure
target.

Replacing any one of the three thin maps by zero misses the endpoint.
Flipping the low bit of the first row of the gap-1 map also misses it.
The same multiplier accepts the commuting control: one diagonal
resolution on every stage, grouped halves, and the `COMMUTING.md` maps
of ranks 4 and 4 in gaps 2 and 6. Deleting the first of those maps
misses the endpoint. The rank-6 word and the rank-8 control are different
words.

## 5. What was not claimed

No native caller, Lean proof, Docker replay, `make frontier6030-verify`,
or selected-frontier replay was run. The selected record remains
`781451/250000000 = 0.003125804` from PR #6030.

This package does not re-prove the one-map or two-map obstructions. It
does not search entries outside F_2, stages with three or more full
calls, or the profiles g=13, q=8 and g=31, q=26. A failed search was not
used as a nonexistence claim. The positive statement is the one word
above.

## Credit

The contract, the rank floor, and the commuting construction are from
PR #5747 (Ali Romman), including the predecessor statements in PR #5673,
PR #5631, and PR #5617. The one-map obstruction is open PR #6922. The
two-map rank-8 bound is open PR #6940; its open question asked whether
three or more maps can meet rank 6 or 7. Prepared by unpaidmoon with
substantial Cursor Grok assistance. Independent human review and a
proof-assistant proof are unclaimed. Apache-2.0.
