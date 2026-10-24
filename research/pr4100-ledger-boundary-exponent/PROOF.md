# Which boundary exponent the printed #4100 ledger uses

**Scoped sentence proof. No new κ.** #4100 is not accepted. The selected
conditional result stays `0.00302015`.

## Proposition

Let the union and boundary savings at a common `(eps, xi)` be the rows in
`research/unconditional-batched-crt/vendor/UNION-SCHEDULE.md` §4:

```text
S_u     = xi + 1/2 - eps
S_b(c)  = c + xi - eps
c       = (3 - tau) / 2
```

Then `S_b(c) - S_u = c - 1/2`. This identity does not use `q`, `r`, `zeta`,
or the slack.

The only numeric balance those notes print for this schedule is the point

```text
eps  = 0.99999437577296
xi   = 0.50167412128176
beta = 0.99664613320944
```

in `vendor/GAUGEFREE-INTERIORS.md` §6, together with its 7-decimal rounding
in UNION-SCHEDULE §5b. On that point the boundary row is the
`tau_eff = 2 + 10^{-64}` row. It is not the `tau = 45/16` row.

## One printed point

GAUGEFREE §6 item 5 prints the 14-digit triple above and sets
`c = (3 - tau_eff) / 2`. UNION-SCHEDULE §5b prints

```text
epsilon = 0.9999944, xi = 0.5016741, beta = 0.9966461
```

at `tau_eff = 2 + 1e-64`. Rounding each 14-digit coordinate half-up to seven
decimal places reproduces that triple, and no other 7-digit triple. The two
notes are the same balance.

From the 14-digit `(eps, xi)`,

```text
S_u = 1049840943 / 625000000000 = 0.0016797455088.
```

GAUGEFREE's displayed kappa begins `0.001679745508802299`, so `S_u` agrees
with that prefix through `0.00167974550880`. The leftover digits are the
rounding already present in the displayed `(eps, xi)`.

## The two exponents on that point

`tau_eff = 2 + 10^{-64}` gives `c - 1/2 = -5 · 10^{-65}`. The boundary row
and the union row therefore differ by `5 · 10^{-65}`. That is the gap inside
the same paragraph's joint margin "~ `1e-64`", and it is why §5b can say
that the union and boundary rows have the same exponent `eps + 1/2 - xi` and
both bind.

`tau = 45/16` gives `c = 3/32` and

```text
S_b - S_u = -13/32.
```

The boundary saving is then

```text
0.0016797455088 - 13/32 = -0.4045702544912,
```

which is not a margin of size about `10^{-64}` above the displayed kappa.
The joint-binding sentence is false at `45/16` for this printed point.

## Where `45/16` is printed

`GAUSSIAN.md`'s seven-product paragraph, and `vendor/FINE-PRIME.md` §6, assign
`tau = 45/16` to the dense cost

```text
O(V d W^(tau-1) / B polylog(p))
```

and say that this cost needs no structured inverse. FINE-PRIME's saving
`c + xi - epsilon` at `c = 3/32` is that Strassen row. It is a different row
from the §5b balance. `research/pr4100-row-field-ledger` already compared the
short-field movement with this Strassen row and stopped before choosing an
exponent. The comparison is not redone here.

## Where the layout lemma is copied

In `GAUSSIAN.md` the sentence "Temporary padding of the one exposed polynomial
row field is removed before the next axis" sits in the union-cost paragraph,
after the Strassen paragraph. UNION-SCHEDULE §6 assumes "the retained
polynomial-width row-field movement for batched boundary arithmetic" and says
that the document does not change the boundary matrix exponent. The ledger
that receives the layout lemma is therefore the §4–§5b ledger, and the
boundary exponent of that ledger is `tau_eff`.

## What is not claimed

`outer/check_ledger.py` is cited by §5b and is not a file of
`research/unconditional-batched-crt`. This note does not run it. It does not
prove the structured-boundary hypothesis, the Strassen inequality `7^16 < 2^45`,
or any all-size transfer. A later generator could still print a different
point; that is a separate obligation.
