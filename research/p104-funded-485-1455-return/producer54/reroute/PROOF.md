# A funded role 485 bypass through the paid role 1455 stream

This construction changes the exact PR7480 word at head `58a9d052143f5d85295ed2d0163591c47f89a331`. The source canonical SHA-256 is `5044adee019f073f286789ccb688ffca76d42b60518242bb4daea818d33d337a`. The emitted candidate canonical SHA-256 is `64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8`.

The construction bypasses role 485's visit to frame 721 and uses role 1455's already paid stream to supply role 824's required read. Role 1455 then visits frame 724 so both independent streams can be decoded before their original consumers. The complete native paid delta is `{1: +1, 3: -1, 4: -1, 6: +1}`, with no productive debit. This document proves the exact normalised arbitrary-input identity and its native price identity. The physical compiler, common grid, complete signed invoice, precision, tape, and outer predicates are checked separately. It does not declare a kappa.

All source event indices are zero based.

## Arbitrary-input identity

At the cut immediately before original event 33163, let \(S, D, N, T, A,\) and \(X\) denote the current rows of roles 485, 1455, 976, 54, 824, and 212, respectively. These rows are arbitrary. In particular, neither role 485 nor role 1455 is assumed clean, and their independent initial values are retained.

The original local instructions produce \(212 = X + D\). Writing \(F = D + N\), they also require the following rows.

- Role 485 has \(S + T\) at its first use in frame 724.
- Role 1455 has \(F + T/2\) on reaching frame 904, before the original subtraction of \(N\).
- Role 824 has \(A - S - T + F/2\).

First perform the original \(212 \mathrel{+}= 1455\) read at frame 3, and then the original \(1455 \mathrel{+}= 976\) addition. Encode roles 485 and 1455 with two shears at frame 3. Their stored values become

\[
x = S - 2F,
\qquad
y = F + \frac{2}{3}x = \frac{2S - F}{3}.
\]

The encoding matrix on the independent pair \((S,F)\) is

\[
\begin{pmatrix}
1 & -2 \\
2/3 & -1/3
\end{pmatrix},
\]

whose determinant is one.

Move only role 1455 to frame 721. The two operations \(824 \mathrel{-}= (3/2)y\) and \(824 \mathrel{-}= T\) give

\[
824 = A - \frac{3}{2}\frac{2S-F}{3} - T
    = A - S - T + \frac{F}{2},
\]

which is exactly the complete original row of role 824. Then perform \(1455 \mathrel{+}= T/2\). Move role 1455 from frame 721 to frame 724, and move role 485 directly from frame 3 to frame 724. At this common frame, the two inverse shears give

\[
\begin{aligned}
1455 &= \left(y + \frac{T}{2}\right) - \frac{2}{3}x
      = F + \frac{T}{2}, \\
485 &= x + 2\left(F + \frac{T}{2}\right)
     = S + T.
\end{aligned}
\]

Thus both original streams are restored, with both independent dirty returns. Move role 1455 from frame 724 to frame 904. The original \(1455 \mathrel{-}= 976\) instruction is retained, so its subsequent value is \(D + T/2\), exactly as before.

The entire existing PR7480 block in frame 724 and all its corrections in frame 904 are retained literally. Roles 449, 1206, 1477, and the owned coordinate 1501 therefore receive the same values as in the source. No part of the previous rejected two-direction bypass or its unpaid return is used.

## Literal splice and chronology

Insert the following 13 events immediately before original event 33163. They occupy candidate indices 33163 through 33175.

```json
[
  ["ADD",212,1455,"1",3],
  ["ADD",1455,976,"1",3],
  ["ADD",485,1455,"-2",3],
  ["ADD",1455,485,"2/3",3],
  ["MOVE",1455,3,721,false],
  ["ADD",824,1455,"-3/2",721],
  ["ADD",824,54,"-1",721],
  ["ADD",1455,54,"1/2",721],
  ["MOVE",1455,721,724,false],
  ["MOVE",485,3,724,false],
  ["ADD",1455,485,"-2/3",724],
  ["ADD",485,1455,"2",724],
  ["MOVE",1455,724,904,false]
]
```

Remove exactly the original events 33163, 33164, 33165, 33172, 33186, 33191, 33200, 33201, 33203, and 33205. Every other original event remains unchanged and retains its relative order.

The retimed read into role 212 has no intervening contact with role 212 or role 1455. The retimed read from role 976 has no intervening contact with role 976. Role 54 has no write between its original source uses at events 33164 and 33203. Role 485 is restored before its first retained arithmetic in frame 724, at original event 33173. Role 1455 is restored before its next retained arithmetic, at original event 33206. Role 824's complete row is restored before its next unrelated contact. These claims are verified against the literal source contact inventory.

The changed routes use the strict binary subspace chain

\[
3 \subsetneq 721 \subsetneq 724 \subsetneq 904,
\]

with ranks 0, 4, 6, and 7. All operands of each ADD have the exact current coframe. There is no new scratch, no new lifetime, and no public erasure.

## Complete native price

The two relevant transport changes are

| Role | Original route and ranks | Candidate route and ranks |
|---|---|---|
| 485 | 3 → 721 → 724, ranks 4 + 2 | 3 → 724, rank 6 |
| 1455 | 3 → 721 → 904, ranks 4 + 3 | 3 → 721 → 724 → 904, ranks 4 + 2 + 1 |

The rank 2 terms cancel. Hence the paid change is

\[
\Delta P = H_1 + H_6 - H_3 - H_4.
\]

Both the paid call count and rank mass are unchanged. The public initial and final charts, the complete literal public outputs, and the productive profile are unchanged. The same fixed caller with 17 native occurrences therefore multiplies this native profile delta by 17, subject to the separate complete application verification.

For \(H(r) = r^{1-C}\) and \(0 < C < 1\), define \(h(x) = x^{1-C}\). Its derivative is strictly decreasing. Therefore

\[
H_3 - H_1 = \int_1^3 h'(x)\,dx
> \int_4^6 h'(x)\,dx = H_6 - H_4.
\]

Consequently \(g(C) = H_3 + H_4 - H_6 - H_1\) is strictly positive. This is an exact strict price identity, with the added rank 1 transport fully charged. A complete signed claim still requires all ordinary, resource, precision, compiler, and outer obligations.

## Executed checks and scope

The independent emitter in `independent_check.py` does not import `build.py`. It reconstructs the same candidate bytes and checks all 1569 formal current rows across the half-open original interval \([33163, 33219)\) and candidate interval \([33163, 33222)\). Every row agrees. It also checks that the retained INIT 1501 and CLEAR 1501 events have identical protected rows. There is no COPY inside the changed interval, and all outside events are retained literally, so their clean-destination obligations are preserved by composition.

Complete-word coframe and ownership checks pass. There are 76475 events, exactly three additional ADDs, with no additional SCALE or MOVE instruction. The 74 owned lifetimes, 68 declared owned labels, and peak of 50 are unchanged. The retained complete native checker also reports no bad input columns. The physical and complete signed application checks are separate receipts.

The 13-event splice is the concise construction found here. No minimality or global optimality claim is made. The five retained framework assumptions remain `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, and `analytic_recovery`. No selected frontier record is changed.
