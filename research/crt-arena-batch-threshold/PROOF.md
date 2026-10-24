# Full shared-arena batch threshold

This is a scoped counting theorem about the explicit bill in unpaidmoon's
[PR4650 proof](../crt-arena-root-axis/PROOF.md), at canonical main
`624de9dc66858af0945e5f8a0942488d62280d43`. Its tariffs and arena census are
premises here. The new result classifies the full batch without changing that
bill. No predecessor executable is replayed.

## Statement

Let `p >= 2` and `1 <= h <= ell <= p` be integers. Put

```
q = p+2, N = 2^h, w = 4q,
A = N^2 + 2Nh^2 + 24Nh + 3N,
J = N(h^2+3h+1),
T = A(26wJ+25w) + 30wJ + 3Nh + 6(2h-1)N + 3,
U = 65536q^3 + 1024q ell^3 + 1024q^2
    + 4[9(ell+2)^2 N + (1+8w^2)T],
B = 8q U, E = 2^(4ell) q^16.
```

Thus `B` repeats the complete one-axis charge, including its CRT work and
four networks, on the maximum `8q` axes. In particular every tape action
still pays the optional schoolbook product of two `w`-bit words.

Then `B < E` except at exactly `(p,ell,h) = (2,1,1)` and `(2,2,2)`.
The least real constant `C` satisfying `B <= C E` throughout this domain is

```
C* = 9702312163 / 8589934592.
```

It is attained at `(2,2,2)`. These are comparisons of the stated majorant.
An excess of that majorant is not a lower bound on an actual machine.

## Proof for p >= 3

First take `ell = h`, so `q >= max(5,h+2)`. PR4650's explicit-bill lemmas
give, for `h >= 2`,

```
U <= 17472q^4 + 36q^2 N + 6109440q^3 N^3 h^2.
```

Multiplication by the full batch size gives

```
B <= 139776q^5 + 288q^3 N + 48875520q^4 N^3 h^2.
```

Each summand is strictly below `E/3`. For the first this is equivalent to
`419328 < N^4 q^11`, which holds already at `N=4,q=5` and is preserved by
increasing either variable. For the second it is
`864 < N^3 q^13`, with the same smallest pair.

The third comparison is

```
146626560 h^2 < 2^h q^12.
```

At `h=2,3`, use `q >= 5` and the respective exact comparisons

```
586506240 < 976562500,
1319639040 < 1953125000.
```

At `h=4`, `q >= 6` gives `2346024960 < 34828517376`.
For `h >= 4`, set `r(h) = 2^h(h+2)^12/h^2`. Then

```
r(h+1)/r(h) = 2 ((h+3)/(h+2))^12 (h/(h+1))^2
             >= 2 (4/5)^2 = 32/25 > 1.
```

Consequently the `h=4` inequality propagates to every larger `h` using
`q >= h+2`. This proves `B < E` at `ell=h>=2`.

For `ell=h=1`, PR4650's height-one expansion gives

```
U <= 37169148q^3,
B <= 297353184q^4 < 16q^16 = E,
```

since `297353184 < 16*5^12` and `q >= 5`.

Now fix `q,h` and increase `ell`. The only `ell`-dependent terms in `U`
are `1024q ell^3` and `36N(ell+2)^2`. For integer `ell>=1`,

```
(ell+1)^3 - 16ell^3 = -15ell^3+3ell^2+3ell+1 <= -8ell^3 < 0,
(ell+3)^2 - 16(ell+2)^2 = -15ell^2-58ell-55 < 0.
```

The omitted part of `U` is positive and independent of `ell`, so
`U(ell+1)<16U(ell)`. Multiplication by the fixed `8q` preserves this strict
inequality, while `E(ell+1)=16E(ell)`. The result at `ell=h` therefore
extends to every `ell>=h`, in particular the required `ell<=p`.

## Exhaustion of p = 2 and sharp constant

There are exactly three admissible pairs `(ell,h)` when `p=2`.
Substitution into the displayed integers gives

```
(ell,h)    B                 E                 B/E
(1,1)      75548846976       68719476736       590225367/536870912
(2,1)      75549780608       1099511627776     590232661/8589934592
(2,2)      1241895956864     1099511627776     9702312163/8589934592
```

The middle ratio is below one. The first exceeds one, and its numerator
when written over `8589934592` is `9443605872 < 9702312163`. All `p>=3`
ratios are below one by the proof above. Hence the last row is the global
maximum and gives the stated least constant. This completes the proof.

## Consequence and limits

For every `p>=3`, changing the scalar inventory is unnecessary to fit the
entire batch under this particular allowance. Over the full domain `p>=2`,
the sharp majorant constant is `C*`, and the coarse integer constant two
also suffices. This closes the large-parameter part of PR4650's batch
question with its existing schedule; it does not supply the tighter
word-operation inventory requested there.

The arena tariff, CRT reconstruction premise and maximum batch size remain
inherited. Reservoir placement, actual arena execution, repair, native lifting,
all-size caller composition and the outer multiplication theorem are separate
obligations. The selected frontier is unchanged. The quantified conclusion is
proved by the inequalities above; finite checker output is corroboration.
