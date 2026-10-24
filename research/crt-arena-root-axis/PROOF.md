# One root axis on a shared Beneš arena

This is a counting proof for the shared-arena schedule left open by
`research/crt-uniform-evaluator`. It does not accept PR #4100, it does not
change κ, and it does not replace that package's per-table bound for a whole
batch of axes.

## Proposition

For all integers `p >= 2` and `1 <= h <= ell <= p`, write `q = p + 2`,
`N = 2^h` and `w = 4q`. One root axis, reconstructed by the pinned evaluator's
one-axis CRT bill and then compiled as four shared-arena networks, uses at
most

```text
E(p, ell) = 2^{4 ell} q^{16}
```

bit-steps. The four networks are the forward rotation, the inverse rotation,
and the same pair for the inverse macro. Each network is the PR #4192 arena
on `N` wires, followed by one protected bit query. Beside every tape action
in that arena invoice, the scalar control may perform one `w`-bit by `w`-bit
schoolbook product.

The same explicit charge, repeated for all `8q` axes, exceeds `E` at
`p = 2`, `ell = 2`, `h = 2`. The per-table evaluator already fits that batch
by a different scan. This note does not transfer its constant to the batch
under the arena charge.

## Predecessor sentences

The one-axis reconstruction bill is the evaluator's substitution
`m <= 8q`, `W <= 8q`:

```text
65536 q^3 + 1024 q ell^3 + 1024 q^2.
```

Across `A <= 8q` axes that file multiplies the bill by `8q` and obtains
`524288 q^4 + 8192 q^2 ell^3 + 8192 q^3`. Writing one rotation table costs at
most `9(ell + 2)^2` bit-steps per wire. A schoolbook product of an `a`-bit
integer by a `b`-bit integer costs at most `8ab` bit-steps.

PR #4192, at commit `519d811cc48693ad9969d6d7994bef3940167005`, fixes the
arena geometry. The unmodified proof is
`vendor/pr4192-crt-benes-scan-PROOF.md` (SHA256
`c3eb4e14dc5ee0102cbf77c4a0e61db9989c2b8a0eaf7f0659a6e39373197474`).
It sets every record field to `w = 4p + 8` bits, hence `w = 4q`, and

```text
J = N(h^2 + 3h + 1),    B = 5 w J.
```

One logical access performs exactly `26 w J + 25 w` tape actions.
Initialization and erasure add `6B = 30 w J`. The protected input costs
`3 N h`. Owned output costs `3(2h - 1)N`, and one query costs
`3(2h - 1)N + 3`. The access census satisfies

```text
A <= N^2 + 2 N h^2 + 24 N h + 3 N.
```

That file's uniform bound is `O((A + J + 1) B (p + 2)^2)` after charging
each scalar instruction `O(w^2)`. The leading piece of the charge below is
exactly that shape with coefficient `3328/5`:

```text
8 w^2 * A * (26 w J) = (3328/5) A B q^2.
```

## The explicit bill

For one network let

```text
T_tape = A (26 w J + 25 w) + 30 w J + 3 N h + 6(2h - 1) N + 3,
T_scalar = 8 w^2 T_tape,
T_rot = 9 (ell + 2)^2 N.
```

`8 w^2` is the schoolbook cap at equal lengths. The touch formula in the
pinned evaluator is `3ab + 3a + b`; at `a = b = w >= 1` this is
`3w^2 + 4w <= 8w^2`, because `4 <= 5w`. The `w = 0` comparison `4 <= 0` is
false, so the cap is stated only for a positive width.

One axis with four networks is

```text
U = T_crt + 4 (T_rot + T_tape + T_scalar),
T_crt = 65536 q^3 + 1024 q ell^3 + 1024 q^2.
```

## Lemmas used for every admissible pair

Write `N = 2^h` and `poly(h) = 2h^2 + 24h + 3`, so `A = N^2 + N poly(h)`.

1. `poly(h+1) = poly(h) + 4h + 26`, because
   `2(h+1)^2 - 2h^2 = 4h + 2` and `24(h+1) - 24h = 24`.
   Directly, `poly(1) <= 30`, `poly(2) <= 60` and `poly(3) <= 120`.
   For `h >= 3`, `4h + 26 <= 15 * 2^h`: the `h = 3` value is `38 <= 120`,
   and `4(h+1) + 26 = 4h + 30 <= 15 * 2^h + 4 <= 30 * 2^h` once
   `4 <= 15 * 2^h`. Thus `poly(h) <= 15 * 2^h` and `A <= 16 N^2` for every
   integer `h >= 1`.

2. `h^2 + 3h + 1 <= 5 h^2` because `(h - 1)(4h + 1) = 4h^2 - 3h - 1 >= 0`
   for every integer `h >= 1`. Hence `J <= 5 N h^2`. At `h = 1`, `J = 10`
   and `A >= 4`.

3. The displayed exact census `(37 N h - 35 N) / 2` is at most the
   convenient linear term `24 N h + 3 N`, because `11h + 41 > 0`.

4. `15 h <= 16 * 4^h` for `h >= 1`. The base is `15 <= 64`. The step uses
   `15 <= 48 * 4^h`, so `15(h+1) <= 16 * 4^h + 15 <= 64 * 4^h`.

5. The tail `3 N h + 6(2h - 1)N + 3 = 15 N h - 6 N + 3` is at most
   `15 N h` for `N >= 1`. Combined with `A >= N^2`, `J >= N` and `w >= 16`,
   `15 N h <= A J w`. Also `J >= 10` gives `25 A <= (5/2) A J`, and
   `A >= 4` gives `30 J <= (15/2) A J`, so

```text
26 A J + 25 A + 30 J <= 36 A J,
T_tape <= 37 A J w.
```

6. `1 + 8 w^2 = 1 + 128 q^2 <= 129 q^2`. For `h + 2 <= q`,
   `T_rot <= 9 q^2 N` at `ell = h`. Therefore one network is at most
   `9 q^2 N + 19092 q^3 A J`, four networks are at most
   `36 q^2 N + 76368 q^3 A J`, and `A J <= 80 N^3 h^2` gives

```text
4 (T_rot + T_tape + T_scalar) <= 36 q^2 N + 6109440 q^3 N^3 h^2.
```

7. For `0 <= ell <= q - 2` and `q >= 4`,
   `65536 q^3 <= 16384 q^4` and `1024 q^2 <= 64 q^4`, while
   `1024 q ell^3 <= 1024 q^4`. Hence `T_crt <= 17472 q^4`.

At `ell = h >= 2` and `q >= h + 2` (so `q >= 4`),

```text
U <= 17472 q^4 + 36 q^2 N + 6109440 q^3 N^3 h^2.
```

Each of those three terms is at most one third of `2^{4h} q^{16}`. The first
two are smallest at `N = 4`, `q = 4`, where `52416 <= 2^{32}` and
`108 <= 2^{34}`, and both right-hand sides grow with `N` and `q`. The third
is `18328320 h^2 <= 2^h (h + 2)^{13}`. This holds at `h = 2` and `h = 3` by
direct powers. At `h = 4` it is `18328320 <= 6^{13}`. For `h >= 4` the
function `r(h) = 2^h (h+2)^{13} / h^2` is strictly increasing, because

```text
r(h+1) / r(h) >= 2 (h / (h+1))^2 >= 32/25 > 1.
```

The middle comparison is `h >= 4`. Thus the majorant is at most the allowance
for every integer `h >= 2` and `q >= h + 2`.

## The height-one line, and a longer modulus

At `h = 1` the same polynomials give

```text
U = 36868096 q^3 + 11776 q^2 + 288544 q + 732
  <= 37169148 q^3
```

when `ell = 1`. For `q >= 4`, `37169148 <= 16 q^{13}`, so
`U <= 16 q^{16} = 2^{4} q^{16}`.

For a longer modulus, fix `h` and `q` and raise `ell`. The parts of `U` that
depend on `ell` are `1024 q ell^3` and `36 N (ell + 2)^2`. For `ell >= 1`,

```text
(ell+1)^3 - 16 ell^3 <= -8 ell^3 < 0,
(ell+3)^2 - 16 (ell+2)^2 = -15 ell^2 - 58 ell - 55 < 0,
```

and the `ell`-independent part `S` satisfies `-15 S < 0`. Therefore
`U(ell+1) < 16 U(ell)`. The allowance multiplies by exactly 16. Starting from
`ell = h`, every larger admissible `ell` stays inside the allowance.

Every triple `p >= 2`, `1 <= h <= ell <= p` has `q = p + 2 >= 4` and
`q >= ell + 2 >= h + 2`. The height-one cubic or the `h >= 2` majorant covers
`ell = h`, and the step covers `ell > h`.

## Two evaluated witnesses

At `p = 2`, `ell = 2`, `h = 2` (`q = 4`, `N = 4`):

```text
U = 38809248652,
E = 2^{40} = 1099511627776,
28 U <= E < 29 U.
```

On the box `h = 1..8`, `ell = h`, and the four values of `q` beginning at
`max(4, h+2)`, this pair has the largest ratio `U / E`. That box is a check.
The proof is the induction above.

The same formulas with `32 = 8q` axes give

```text
U_batch = 1241895956864 > E.
```

So this per-action schoolbook majorant fits one axis and does not fit the
whole displayed batch. The factor `8q` on the CRT term alone reproduces the
evaluator's six-term CRT display; the excess comes from repeating the arena,
not from the reconstruction.

## What this does not prove

Reservoir placement, the ordinary interchange callee, sparse repair, native
execution, and the outer multiplication theorem stay out of scope. The arena
is charged from the predecessor's census and tape formulas; this package does
not execute PR #4192's simulator or the retained Beneš compiler. The scalar
term is an explicit majorant large enough to cover one schoolbook product per
tape action. A tighter word-operation inventory could change the batch
comparison. No new κ is selected. The selected conditional value remains
`60403/20000000 = 0.00302015`.
