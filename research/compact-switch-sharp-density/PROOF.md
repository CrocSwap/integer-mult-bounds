# Sharp-window density against the printed CRT repair room

Scoped proof. No new κ. The selected conditional exponent is unchanged.
This does not accept PR #4100, and it does not extend the simultaneous
carry argument from the published `2B` margin to the sharp window.

## Parameters

CRT.md §3, for integers `ell ≥ 1` and `p ≥ 2`, sets

```text
G = 64 (ell + ceil(log2(p+2))),    B = 2^G,    K = 64 G.
```

A batch has `r` targets with `r ≤ floor(L / (100 G))`. The absorption
hypothesis used below is the same one as PR #4328: `L ≤ p`. It is not
proved here that every address layout satisfies `L ≤ p`. On this domain
`G ≥ 192`.

## Two window predicates

A `K`-bit guard stores the target in its least bit and the window `W` in
the other `m = K − 1` bits, so `W` is an integer in `0, …, 2^m − 1`.
This is the layout in `check_batched_crt.py`: the published predicate is

```text
2B ≤ W < 2^m − 2B.
```

Whenever `4B ≤ 2^m`, exactly `4B` windows fail, and the fraction is

```text
4B / 2^m = 8B / 2^K.
```

That is the window summand in CRT.md §4.

The isolated post-increment step, with digit `τ ≤ B − 2`, is the map

```text
y1 = y + 2 z τ,    τ' = τ + (y1 mod 2),    y2 = y1 + z (1 − 2 τ').
```

For `z = 1`, `τ = B − 2` and a zero target bit, direct expansion shows
that `y1` first leaves the `m`-bit window at

```text
W = 2^m − (B − 2) = 2^m − B + 2.
```

Every smaller window, `0 ≤ W ≤ 2^m − B + 1`, returns `y2 = y + z(1−2b)`
with the window restored and with no bit at position `m+1` or above.
Thus the sharp bad set has size exactly `B − 2` (and size `0` when
`B = 2`). Its fraction is

```text
β = (B − 2) / 2^m = 2(B − 2) / 2^K.
```

For `B > 2` and `4B ≤ 2^m`,

```text
β = ((B − 2) / (4B)) · (8B / 2^K) < (1/4) · (8B / 2^K).
```

Every published-good window is sharp-good: `2B ≤ W ≤ 2^m − 2B − 1`
implies `W ≤ 2^m − B + 1` because `B ≥ 2`. The inclusion is proper
whenever a window below `2B` exists.

## What the substitution does not prove

CRT.md uses the `2B` margin to keep simultaneous carries inside disjoint
guards. The count above is for one isolated target. Replacing `8B/2^K`
by `β` in the density line is valid for that isolated predicate. It does
not by itself certify the simultaneous macro on the extra windows
`W < 2B` or `2^m − 2B ≤ W ≤ 2^m − B + 1`.

## Union bound

Charge a target as bad when either control digit equals `B − 1` or its
window is sharp-bad. The two digit failures contribute `2/B = 2^{1−G}`.
For `r` targets,

```text
δ ≤ r (2/B + β) = r (2^{1−G} + 2(2^G − 2) 2^{−64G}).
```

Factor `2^{−G}`:

```text
2/B + β = 2^{−G} (2 + 2(1 − 2^{1−G}) 2^{−62G})
        < 2^{−G} (2 + 2^{1−62G}).
```

The published window summand `8B/2^K` produces the same identity with
`2^{1−62G}` replaced by `2^{3−62G}`. Either window term is smaller than
`2^{−60}` times the digit term `2/B` once `G ≥ 1`.

## The printed room does not contain the window term

CRT.md §2 allows `E(p, ell) ≤ C_E 2^{4 ell} (p+2)^{16}`. With the §3
formula for `G`,

```text
2^{−G} 2^{4 ell} (p+2)^{16}
    = 2^{−60 ell} (p+2)^{16} / 2^{64 ceil(log2(p+2))}
    ≤ 2^{−60 ell} (p+2)^{−48},
```

because `2^{ceil(log2(p+2))} ≥ p+2`. The factor `8B/2^K` does not occur.
Substituting `β` leaves this line unchanged, including the constant
`C_E` in front of `E`.

## Absorption

Assume `L ≤ p` and `r ≤ floor(L/(100G))`. Then `r ≤ p/(100G) ≤ p/19200`,
and

```text
r (2/B + β) < r (2 + 2^{1−62G}) 2^{−G} ≤ p 2^{−G} / 6400.
```

The same bound holds with `8B/2^K` in place of `β`, because that only
increases the tiny summand from `2^{1−62G}` to `2^{3−62G}`, and
`2 + 2^{3−62G} < 3` still gives a factor below `1/6400`. Therefore both

```text
r (2/B + β) ≤ C p 2^{−G},    r (2/B + 8B/2^K) ≤ C p 2^{−G}
```

hold for every `C ≥ 1/6400`, and in particular for every `C ≥ 1`.
Multiplying by the room line,

```text
r (2/B + β) E ≤ (C_E p / 6400) 2^{−60 ell} (p+2)^{−48}.
```

The scalar prefactor that CRT.md compares with `2^{−G}` gets smaller
when `8B/2^K` is replaced by `β`, and the displayed `2^{−G} E` factor
is unchanged. The `O(V)` comparison does not lose room.

This is a comparison of those two displayed scalars. It is not a
fixed-tape replay of bad-key evaluation, sorting, or reinsertion.
