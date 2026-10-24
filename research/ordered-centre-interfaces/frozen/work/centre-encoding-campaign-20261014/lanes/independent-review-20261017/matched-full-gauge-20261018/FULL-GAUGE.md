# The actual matched response as a common-FULL scalar map

The frozen full native response E is a symmetric dyadic involution.
This packet implements E=E^-1 on 112 arbitrary data fields in a common
FULL frame. The cost is 2396 real scalar primitives. It uses no native
child, owned field, or private field. The actual matched native X exits
all have this frame, so the map can be appended there.

On the 48-port component, write E=A^-1 M A. The matrix A is the direct
sum of the 24 actual signed two-field codes. The matrix M consists of
24 signed transpositions of their mode carriers. On the other 64 ports,
E is the actual 32 negative transpositions. The packet pins the full
native response, including this negative-permutation component.

For one pair code [[a,b],[c,d]], each entry is a signed unit and its rows
are orthogonal. Thus d=-abc. The following four operations apply it:

```text
x <- a x
x <- x + b y
y <- 2d y
y <- y + ca x.
```

The second output is ca(ax+by)+2dy=cx+dy. A scale by one is omitted.
Reverse these operations and invert their coefficients for the inverse
code. Across all pairs the code costs 470 real primitives, and the
inverse code costs 470.

A signed transposition (x,y)->(w y,w x), with w=+1 or -1, has the word

```text
x <- x+y
y <- y-x
x <- x+y.
```

These three additions give (y_old,-x_old). If w=+1, negate the second
field. If w=-1, negate the first. Each transposition costs 26 real
primitives. Thus the 24 mode transpositions cost 624 and the 32 physical
negative transpositions cost 832. The complete total is

```text
470 + 624 + 470 + 832 = 2396.
```

The payload gives every scalar event. A forward row replay and a reverse
column replay each equal the actual full E on all 112 inputs. Repeating
the same literal word gives identity in both replays. The check rejects
omission of the pair undo. Exact prefix row sums bound the array norm;
the resulting bound is in `CHECKS.json`. This is a top-level bound, not
a recursive precision certificate.

Every operation requires the same physical frame on its source and
target. In a common FULL frame, scalar port maps commute with the common
F_9 operation, so these operations have the stated logical response.
The proof does not permit the map on the unequal Y-hole frames. It also
does not identify E at different supplier stages. Such stage changes
must use their actual physical port view and pay its access cost.

This is a fixed scalar word, not a minimality claim. It supplies a
concrete endpoint gauge for the new response. A complete controller,
source-retirement proof, terminal phase map, host, and total recurrence
remain separate. No kappa result or publication is claimed.

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/matched-full-gauge-20261018/emit_full_gauge.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/matched-full-gauge-20261018/emit_full_gauge.py
```

The expected output is `PASS_MATCHED_COMMON_FULL_GAUGE`. The normal and
optimized payload and receipt bytes agree. This work uses the controller
lane's matched modes and the oblique-native and history lanes' full
native response. The scalar pair factor was derived in this lane's
cyclic-flag construction. The work was produced with AI assistance.
Independent review is separate.
