# The Type A stage-8 singleton interval

The fixed endpoints are 1466 and 1487. There are 22 events
including both endpoints and 20 strict interior events.
The interior consists of ADD 7←0 with coefficient +2, six
complete ADD/idle/ADD triplets on roles 19–24, and ADD 25←18
with coefficient −2. The six intervening idles also include
B8. All six remain in both the old and erased intervals.

Set q=1 and all body characters except B8 to 1. Write b=B8,
t=b−1 and let e_r be coordinate r. The triplet on row r
is conjugation of I + t e_r e_r^T by the shear
S_r = I − 2 e_r e_18^T. Its transported projector is

```text
P_r = e_r (e_r^T − 2 e_18^T), r = 19,...,24.
```

Every product of distinct such projectors is zero. The
edge shears commute with the six projectors and with each
other. Thus the exact intervening operator is

```text
W(b) = W_0 (I + t sum_{r=19}^{24} P_r)
W_0  = I + 2 e_7 e_0^T − 2 e_25 e_18^T.
```

Use the cut basis just before clock 1466. The first endpoint
projector is P_7 = e_7 e_7^T. Conjugating the last endpoint
projector by W_0 inverse yields Q_25 = e_25(e_25^T − 2 e_18^T).
Both annihilate every middle projector and each other,
in both multiplication orders. Let E_old(b) be the old
inclusive interval and W(b) the interval after erasing the
two endpoints. The normalized exact difference is

```text
W_0 inverse · (E_old(b) − W(b)) = t (P_7 + Q_25).
```

The derivative at b=1 is supported on rows 7 and 25 and
has identity minor on rows and columns 7 and 25. Its exact
rank is two. At b=−1, the same minor has determinant 4.
The stage-8 body axes are independent of the central and
other stage axes. Two active body bits yield B8=−1 with
the other characters fixed at 1. This is a B8-only identity
and physical specialization.

A single projected replacement with local wrappers fixed in
b and unit-body identity differs from identity by at most
one rank on each fixed body fibre. Placing it at either old
clock multiplies the difference by the unchanged W(b) and
cannot increase its rank. This necessary gate therefore fails
for any paid rank that still returns through one projected
role. The proof fixes the intervening word and its derivative
contributions. Changes to those contributions, additional
projected returns and other pairs require separate tests.

## Directed quote

The fully rank-additive quote replaces 192 paid rank-eight
positions by 96 paid rank-sixteen positions across the
96 Type A ports. The one-edit raw gross upper is
3.848300498820991, with a positive complete directed probe.
The two disjoint singleton pairs together have gross upper
7.696600997641981 and fixed-moonshot complete upper
−131.3160419215735. These are upward-rounded bounds.
The optimistic rank-eight quote grants an unproved physical
square. Its one-edit raw gross upper is 762.1982813488973.
It does not relax the single-projected-return obstruction.
The exact tested scope has zero realized saving.
