# The 972-bit R437 child does not pay the parent spectator blank-return

No new κ. The selected conditional exponent stays `60403/20000000`.

## What is taken as stated

These integers are the ones written in `research/r437-carrier-integration`,
pinned at the base commit. This note does not execute `physical.py` or
`Layout.child_extents`.

From NUMERICAL.md §5, the live-symbol constant is `269241600`, and a parent
split divides that constant by `W = 28416`:

```text
269241600 / 28416 = 9475.
```

The same section writes `K = lcm(28416, 28425) * N * H_lifts = 269241600 * N * H_lifts`,
so the lcm claim being checked is `lcm(28416, 28425) = 269241600`. The unused-row
multiplier on the child is `U = t * 9475 * K^{D(n)-1}`.

From PHYSICAL.md, the source rank-two plan has extents

```text
B = 2,
G = 3 * 3^124,
S = 2,
U_parent = 9475,
V_parent = U_parent * B * G * S * 3^4 = 9475 * 12 * 3^128.
```

The executed child uses one row and gap `3`, and `physical.py` allocates a
tape of `972` bits for extents `(2, 3, 2)`.

## Arithmetic

`gcd(28416, 28425) = 3`, because `28425 - 28416 = 9` and `28416 = 3 * 9472`
with `9472` not divisible by `3`. Therefore

```text
lcm(28416, 28425) = 9472 * 28425 = 269241600,
269241600 = 28416 * 9475.
```

The four-atom factor in the parent formula is `3^4 = 81`. The executed gap is
the parent gap with the `124` omitted atom coordinates removed:

```text
E = 2 * 3 * 2 * 3^4 = 972,
V = 9475 * 2 * (3 * 3^124) * 2 * 3^4 = 9475 * 12 * 3^128.
```

The second expression equals `4 * 3^129 * 9475`, and `4 * 3^129 = 12 * 3^128`.
Canceling `E` gives the exact ratio

```text
V / E = 9475 * 3^124.
```

Both factors are greater than `1`. Dropping the unused rows leaves `3^124`.
Dropping the `124` coordinates leaves `9475`. Neither witness is the parent
payload.

## Blank-return comparison

Comparison model, stated here and not claimed as a theorem of the predecessor:
a fixed-tape blank-return charges at least one visit per payload symbol, and
the executed child is charged at most once per bit of its `972`-bit packet.

Under that model the parent blank-return is at least `V` and the executed
packet's blank-return is at most `972`. Since `V = 972 * 9475 * 3^124`, the
executed packet does not pay the parent blank-return. The local action-lane
decreases inside the `972`-bit boundary, recorded in BILL.md, are not a
payment of this term.

NUMERICAL.md §5 already says that the live-symbol inequality does not discharge
physical blank-return. The new content is the exact factor separating the
executed packet from the parent payload those pages name.

## Scope

This does not price gather, routing, checkpointing, table setup, or the
reverse-row coefficient. It does not assign zero to any unpaid term of
BILL.md's C/D inequality. It does not admit the carrier and it does not change
the selected frontier.
