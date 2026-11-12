# A sharper rational for the section-6 one-step comparison

Selected κ stays `363005817/100000000000`. This note replaces one rational
constant in one comparison. It does not prove `precision_tape`, it does not
name a cutoff, and it does not change the exponent.

The predecessor note at
`8e0124415604b89a1cfc842cb6dc6da96ea87ac5` (fork branch
`cursor/threshold-ratio-persistence-1d8f`, not on this base) proved persistence
of the section-6 comparison and left, as its second open question, whether an
elementary argument can replace `8/5`. That constant is the pair
`3^5 = 243 < 256 = 2^8`, used with `(1+1/m)^m < 3`. The assigned first step
is a sharper integer pair, tested at `(d0, a, b) = (1, 2, 5)`. This note
answers that step. It does not redo the explicit witness `j*` from the
predecessor, and it does not use the monomial record count of open PR #7286.

## Statement

Let `p` and `q` be positive integers with `3^p < 2^q`. Let `d0`, `a` and `b`
be integers with `d0 ≥ 1`, `a ≥ 1` and `b ≥ 1`, and write `D = d0 b`. For an
integer `m ≥ 1`, the one-step comparison at `(d0, a, b)` is

```text
(m+1)^D < m^D 2^a.
```

**Theorem.** If `m ≥ ceil(q D / (p a))`, the one-step comparison holds.
In particular it holds for `(p, q) = (17, 27)`. Since `27/17 < 8/5`, every
integer `m` that meets `m ≥ ceil(8 D / (5 a))` also meets the new ceiling, and
the new ceiling is at most the old one.

**Test point.** For `(d0, a, b) = (1, 2, 5)` the new ceiling is `4`. The
one-step comparison fails at `m = 3` and holds for every integer `m ≥ 4`.
Thus `4` is the least integer `T` such that the comparison holds for every
integer `m ≥ T`, at this single triple. The rational `8/5` is not the least
admissible ratio of this shape, and no admissible pair lowers this ceiling
below `4`.

An admissible pair means positive integers `p, q` with `3^p < 2^q`. The
resulting rational is `q/p`.

## The integer pair

```text
3^2 = 9
3^4 = 81
3^8 = 6561
3^16 = 43046721
3^17 = 129140163
2^10 = 1024
2^20 = 1048576
2^27 = 134217728
```

So `3^17 < 2^27`. Also `2^26 = 67108864 < 3^17`, so `27` is the least such
exponent on the right. Cross-multiplication gives `27 · 5 = 135 < 136 = 17 · 8`,
hence `27/17 < 8/5`. The original pair remains admissible and is not strictly
sharper: `3^5 = 243 < 256 = 2^8` and `5 · 8 = 8 · 5`.

## The binomial bound

For every integer `m ≥ 1`,

```text
(m+1)^m < 3 m^m.
```

Expand `(1 + 1/m)^m`. The summand of index `k` is
`C(m,k) / m^k = (1/k!) ∏_{i=1}^{k-1} (1 - i/m) ≤ 1/k!`. For `k ≥ 1`,
`1/k! ≤ 1/2^{k-1}`: equality holds at `k = 1`, and if it holds at `k` then
`1/(k+1)! = 1/(k! (k+1)) ≤ 1/(2^{k-1} · 2)` because `k+1 ≥ 2`. Therefore

```text
(1 + 1/m)^m ≤ Σ_{k=0}^{m} 1/k! ≤ 1 + Σ_{j=0}^{m-1} 1/2^j
            = 1 + (2 - 2^{1-m}) = 3 - 2^{1-m} < 3.
```

The last step is strict for every finite `m`. Multiplying by the positive
integer `m^m` gives the displayed comparison.

## One-step lemma

Let `m ≥ ceil(q D / (p a))`. Then `p a m ≥ q D` as integers. From the binomial
bound, raising to the positive power `D` gives

```text
(m+1)^{m D} < 3^D m^{m D}.
```

Since `q D ≤ p a m` and `3^p < 2^q`,

```text
3^{q D} ≤ 3^{p a m} = (3^p)^{a m} < (2^q)^{a m} = 2^{q a m}.
```

The second comparison stays strict when `q D = p a m`, because `3^p < 2^q`.
For positive integers `X, Y` and a positive integer `k`, `X^k < Y^k` implies
`X < Y`: otherwise `X ≥ Y` would give `X^k ≥ Y^k`. Apply that with
`X = 3^D`, `Y = 2^{a m}` and `k = q`:

```text
3^D < 2^{a m}.
```

Hence `(m+1)^{m D} < 2^{a m} m^{m D} = (2^a m^D)^m`. The same root comparison
gives `(m+1)^D < 2^a m^D`.

The case `p a m = q D` occurs at `(d0, a, b, m) = (1, 27, 17, 1)` for the pair
`(17, 27)`. There the binomial step is `2^17 < 3^17`, and `3^17 < 2^27` supplies
the remaining strictness:
`131072 = 2^17 < 129140163 = 3^17 < 134217728 = 2^27`.

## The rational `27/17` replaces `8/5`

Apply the lemma at `p = 17` and `q = 27`. The hypothesis
`m ≥ ceil(8 D / (5 a))` may be replaced by `m ≥ ceil(27 D / (17 a))`.

The new threshold is at most the old one. Let
`x = 27 D / (17 a)` and `y = 8 D / (5 a)`. Then `x < y`, because
`27/17 < 8/5`. Let `n = ceil(y)`. The integer `n` satisfies `n ≥ y > x`, so
`n` is an integer greater than `x` and therefore at least `x`. The least
integer greater than or equal to `x` is then at most `n`, which is
`ceil(x) ≤ ceil(y)`.

Consequently any index that meets the old ceiling meets the new one. The
review's factor `4` is not recomputed here. Any sufficient condition that
already forces the successor past the `8/5` ceiling still forces it past the
`27/17` ceiling, because the new ceiling is smaller or equal. This note does
not claim a smaller factor.

If `C ≥ 1` is an integer and `P(j)` means

```text
C^b (j+1)^D ≤ 2^{a j},
```

and if `P(j)` holds with `j+1` at least the new ceiling, the one-step lemma
gives

```text
C^b (j+2)^D < C^b (j+1)^D 2^a ≤ 2^{a j} 2^a = 2^{a(j+1)}.
```

So `P(j+1)` holds, and induction gives `P(k)` for every integer `k ≥ j`.
The ceiling is essential. For `C = 1`, `(d0, a, b) = (1, 2, 5)` and `j = 0`,
`P(0)` is `1 ≤ 1`, but `P(1)` is `2^5 ≤ 2^2`, which is false, and
`j+1 = 1` is below the ceiling `4`.

## The test point `(1, 2, 5)`

Here `D = 5` and `a = 2`, so the new ceiling is `ceil(135/34)`.
Since `135 = 3 · 34 + 33`, one has `3 < 135/34 < 4`, and the ceiling is `4`.
The old ceiling is `ceil(8 · 5 / (5 · 2)) = ceil(4) = 4`.

At `m = 3`, `4^5 = 1024` and `3^5 · 2^2 = 243 · 4 = 972`, so `1024 > 972`.
At `m = 4`, `5^5 = 3125` and `4^5 · 4 = 1024 · 4 = 4096`, so `3125 < 4096`.
The lemma then gives the comparison for every integer `m ≥ 4`. Combined with
the failure at `m = 3`, the least integer `T` with the stated universal
property at this triple is exactly `4`.

## No admissible pair lowers that ceiling

**Floor lemma.** Let `u` and `v` be positive integers with `3^u > 2^v`.
Every admissible pair satisfies `u q ≥ v p + 1`, hence `q/p > v/u`.

If instead `u q ≤ v p`, then `2^{u q} ≤ 2^{v p}`. Raising `2^v < 3^u` to the
power `p` gives `2^{v p} < 3^{u p}`, so `2^{u q} < 3^{u p}` and `2^q < 3^p`,
contradicting admissibility.

Two applications use `3^5 = 243`:

- `243 > 64 = 2^6`. Every admissible pair has `5 q ≥ 6 p + 1`, so
  `5 q / (2 p) > 3`. At `(1, 2, 5)` the induced ceiling is
  `ceil(5 q / (2 p))`, which is therefore at least `4`.
- `243 > 128 = 2^7`. Every admissible pair has `5 q ≥ 7 p + 1`, so
  `5 q / p > 7`. At `(d0, a, b) = (1, 1, 5)` the induced ceiling is
  `ceil(5 q / p)`, which is therefore at least `8`.

If also `q/p ≤ 8/5`, then `5 q ≤ 8 p`, so `5 q / (2 p) ≤ 4`. Together with
the first application, the `(1, 2, 5)` ceiling is exactly `4`. A strictly
sharper pair has `5 q < 8 p`, so the quotient lies strictly between `3` and
`4` and the ceiling is still `4`. In particular `(17, 27)` does not lower it.

The direct failure at `m = 3` is stronger than this floor: no true statement
of the form "the one-step comparison holds for every integer `m ≥ 3`" is
available at this triple, whether or not the rational comes from a power pair.

## Where a sharper pair does and does not move a ceiling

At `(d0, a, b) = (1, 27, 17)` the old ceiling is
`ceil(8 · 17 / (5 · 27)) = ceil(136/135) = 2`, and the new ceiling is
`ceil(27 · 17 / (17 · 27)) = 1`. The comparison holds at `m = 1`, as recorded
above. The smaller rational is therefore strictly more permissive on some
triples. This witness is one triple, not a census of all triples where the
ceiling drops.

At `(d0, a, b) = (1, 1, 5)` both displayed ceilings equal `8`:
`ceil(8 · 5 / 5) = 8` and `ceil(135/17) = 8`, because
`135 = 7 · 17 + 16`. The floor lemma says every admissible pair has ceiling
at least `8` there. The integer comparison itself is ahead of that floor:

```text
6^5 = 7776,   7^5 = 16807,   8^5 = 32768
7^5 = 16807 > 15552 = 2 · 6^5
8^5 = 32768 < 33614 = 2 · 7^5
```

So the comparison fails at `m = 6` and holds at `m = 7`. No pair `3^p < 2^q`
has a hypothesis `m ≥ ceil(q · 5 / p)` that includes `7`, because that ceiling
is at least `8`. Replacing `256 > 243` by a sharper pair of the same shape
does not certify the `m = 7` step. A tighter bound than `(1+1/m)^m < 3` would
be a different argument. This note does not supply one.

## Least exponent not exceeding `17`

For each integer `p` with `1 ≤ p ≤ 17`, let `q_min(p)` be the least positive
integer `q` with `3^p < 2^q`. The set is nonempty because `4^p > 3^p`, so
`q = 2p` is always large enough, and the positive integers are well-ordered.
The values are:

```text
p    1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17
q    2  4  5  7  8 10 12 13 15 16 18 20 21 23 24 26 27
```

`verify.py` recomputes each entry by increasing `q` until `2^q > 3^p`, with
the same bound `q ≤ 2p`. That is the whole domain: one finite `p` interval,
and for each `p` one finite increasing search that stops by a proved bound.

For `1 ≤ p ≤ 16` the table satisfies `5 q_min(p) ≥ 8 p`. Any larger `q` has
a larger ratio. If `5 q_min(p) > 8 p`, every admissible `q` is strictly above
`8/5`. If `5 q_min(p) = 8 p`, the least `q` has ratio exactly `8/5` and every
larger `q` is strictly above `8/5`. Either way, no pair with `p ≤ 16` is
strictly sharper than `8/5`.

For `p = 17`, `q_min = 27` and `5 · 27 = 135 < 136 = 8 · 17`, so `(17, 27)`
is strictly sharper. If `q ≥ 28`, then `5 q ≥ 140 > 136`, so the ratio is
above `8/5`. If `q ≤ 26`, then `2^q ≤ 2^26 < 3^17`, so the pair is not
admissible. Thus `(17, 27)` is the only sharper pair with `p ≤ 17`.

This census does not say that `27/17` is the least admissible ratio. It says
only that no smaller exponent `p` produces a strictly smaller ratio than `8/5`.

## Further witnesses, not a minimum

Two further admissible pairs lie strictly below `27/17`. They are witnesses.
They are not an exhaustive search for the least ratio, and a later pair could
be smaller.

- `3^29 < 2^46`, and `46 · 17 = 782 < 783 = 29 · 27`, so `46/29 < 27/17`.
- `3^41 < 2^65`, and `65 · 29 = 1885 < 1886 = 41 · 46`, so `65/41 < 46/29`.

Both still induce ceiling `4` at `(1, 2, 5)`, by the floor lemma. The powers
are exact integer comparisons in `verify.py`. They are not the hand
multiplication used for `3^17` and `2^27`.

A ratio below `8/5` is not enough by itself. `19/12 < 8/5` because
`19 · 5 = 95 < 96 = 12 · 8`, but `3^12 > 2^19`, so `(12, 19)` is not
admissible and the lemma does not apply to it.

## Evidence classes

1. **Proof.** The binomial bound, the one-step lemma for every admissible
   pair, the comparison `3^17 < 2^27` by the multiplication chain above, the
   inequality `27/17 < 8/5`, ceiling monotonicity, persistence once the new
   ceiling is met, the exact threshold `4` at `(1, 2, 5)`, and the floor
   lemma that no admissible pair lowers that threshold or includes `m = 7` at
   `(1, 1, 5)`.
2. **Exhaustive finite census.** The seventeen values of `q_min(p)` for
   `1 ≤ p ≤ 17`, with the termination bound `4^p > 3^p` and the uniqueness
   argument in the previous section. The domain is finite and the search for
   each least `q` runs to completion.
3. **Witnesses, not a minimum and not a census.** The pairs `(29, 46)` and
   `(41, 65)`. A finite rectangle in `verify.py` checks the integer step on
   `1 ≤ d0 ≤ 5` and `1 ≤ a, b ≤ 8`. That rectangle is not the lemma. The
   binomial checks for `m = 1..48` are not the binomial proof.

## What is not proved

The five selected assumptions stay assumptions. The argument never reads a
selected outer predicate, a monomial recipe, or a tape alphabet. It does not
compute the least `j` for the constants in section 6. It does not say that
`27/17`, `46/29` or `65/41` is the greatest lower bound of admissible ratios.
It does not replace `(1+1/m)^m < 3` by a tighter estimate, and the `(1, 1, 5)`
gap shows why a sharper pair of this same shape cannot close that particular
step. It does not rerun the predecessor's construction of `j*`, and it does
not change selected κ. Open PR #7286 is not an input.
