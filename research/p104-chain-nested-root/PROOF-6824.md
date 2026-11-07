# Shared-carrier input lift: arbitrary-input identity and local saving

This note covers only the new step. The chain that produces its starting word
(the #6702 native word, the paid retiming and helper-368 split of
[#6805](https://github.com/CrocSwap/integer-mult-bounds/pull/6805)) is argued in
`PROOF-6805.md`, unchanged, and is rebuilt here by `retimed_construct.py` and
pinned by `base_native_payload_sha256` in `EXPECTED.json`. Event indices below are
zero-based in that #6805 word (18,622 events); `LIFT.json` lists every edit.

## The edit

Frame 105 has dimension 1 (basis `{51}`) and lies inside frames 430, 755, 1051,
127 and 246, whose bases all contain 51. Roles 556 (exit frame 246, class of
`MOVE(556,3,755)`) and 664 (exit frame 127) are independent helpers born at
frame 3 in the source. After the edit both are born at frame 105. Role 665,
the partner of 664 in the same Z-prep rows, stays born at frame 3. Frame 3
is the zero-dimensional frame.

Deleted source events (all at frame 3): `768 ADD(138,664,-1/2)`,
`770 ADD(120,556,1/2)`, `771 ADD(120,664,-1/2)`, `862 ADD(178,664,3/2)`,
`967 ADD(192,664,-1/2)`, `1991 ADD(179,664,-1/2)`, `9342 MOVE(665,3,1051)`,
`9349 MOVE(664,3,1051)`, `9620 MOVE(120,3,430)`; and `10157 MOVE(556,3,755)` is
replaced by `MOVE(556,105,755)`. Inserted events: before 9340,
`MOVE(120,3,105)`, `ADD(120,556,1/2,105)`, `ADD(120,664,-1,105)`,
`MOVE(120,105,430)`; between 9340 and 9341 (179 is at frame 105),
`ADD(179,664,-1,105)`, `MOVE(664,105,1051)`, `MOVE(665,3,1051)`,
`ADD(665,664,1,1051)`; and at the very end `ADD(665,664,-1,127)`. Roles 120, 556,
664 and 665 have no other event in the affected intervals (checked by the
bound-event assertions of `lift.py`).

## Why the endpoint is unchanged, for arbitrary inputs

Write `y` for the public inputs of the new word and `x` for those of the
#6805 word. Let `sigma` be the invertible substitution
`x664 = y664`, `x665 = y665 + y664`, identity elsewhere. For a register,
its linear form in `x` evaluated at `sigma(y)` is its "old form"; the defect
of the new word is `new form - old form`. Everything is a linear form over
all 772 inputs; no input is presumed zero.

1. *Z-prep rows.* In the source, rows `r` receive `a_r x664 + b_r x665` at
   frame 3 by an adjacent pair of events. Under `sigma` this equals
   `(a_r+b_r) y664 + b_r y665`. The new word keeps only the `665` event, so
   its defect is `-(a_r+b_r) y664`. The pairs are
   138: (-1/2, 1/2), 192: (-1/2, 1/2), 120: (-1/2, -1/2), 178: (3/2, 1/2),
   179: (-1/2, -1/2), giving sums 0, 0, -1, 2, -1. Row 120 also lost
   `1/2 x556` (556 is born at 105, not read at frame 3).
2. *Defects cancel before delivery, except at three registers.* Row 178 has
   defect `-2 y664`. The retained source events `5734 ADD(178,138,1)` and
   `5735 ADD(178,179,2)` add `0` and `2` times the defects of rows 138 and
   179, the latter being `+y664`, so row 178's defect is exactly cancelled.
   Role 665 holds `y665` where the old form is `y665 + y664`. At event 9340
   the defects are therefore exactly
   `D120 = y664 - (1/2) y556`, `D179 = y664`, `D665 = -y664`, and zero at
   every other register. The independent replay in `independent/check_native.py`
   computes this vector from the events and compares it literally.
3. *Delivery.* The four events before 9340 move the carrier 120 to frame 105,
   where roles 556 and 664 live, and add `(1/2) y556 - y664` to it, which
   cancels `D120`. The event `ADD(179,664,-1,105)` is executed while 179 is at
   frame 105 (it moved there at 9340) and cancels `D179`. Role 664 moves
   from 105 to 1051 and 665 from 3 to 1051, where `ADD(665,664,1,1051)` adds
   the untouched `y664` and cancels `D665`. After these events every register in
   the new word equals its old form at `sigma(y)` (verified for all roles by
   exact rational replay; also at all 47 owned `CLEAR` events, so the erased
   values, and hence the zero pattern, are unchanged).
4. *Suffix.* Every later source event occurs unchanged in the new word,
   except that the moves of 120, 664 and 556 start from their new frames.
   A `MOVE` does not change a linear form, so the relation "new form = old form
   at `sigma(y)`" persists to the end. The source endpoint is the identity
   on public inputs (plus the main interface), and no main role is 664 or 665,
   so the new final forms equal the identity at every role except 665,
   whose new form is `y665 + y664`. The final event
   `ADD(665,664,-1,127)` subtracts role 664's form `y664`, leaving `y665`.
   The endpoint is the identity for arbitrary `y`.

The same conclusion is reached without the substitution by the full adjoint
audit of the new word, which checks all 801 x 801 endpoint coefficients, both
in `verify.py` (`native.replay`) and in `independent/check_native.py`.

## Local saving

Native helper exits: role 664 changes from rank 9 (frame 3 to 127) to rank 8
(105 to 127); role 556 from rank 8 (3 to 246) to rank 7 (105 to 246). Paid
requests: 120 pays `1+1` instead of `2` (3 to 430), 556 pays `2` instead of `3`,
664 pays `4` instead of `5`. With `H_r = r^t`, `t = 1 - kappa`, the
literal per-native-call changes are

    Delta T = H7 - H9 (productive helpers: 9:360->359, 7:9->10),
    Delta P = 2 H1 - H3 + H4 - H5 (paid: 1:+2, 3:-1, 4:+1, 5:-1),

so

    Delta(T-P) = g(t) = H7 + H3 + H5 - H9 - H4 - 2 H1.

Rank masses agree (7+3+5 = 9+4+2), but the multiset `(7,5,3,0)` is not
majorized by `(9,4,1,1)`, so strict concavity of `r^t` does not give the sign
for all `t`; indeed `g<0` for small `t`. The sign at the exponents used
is proved as follows. `g(1)=0` and `g'(1) = 7 ln7 + 3 ln3 + 5 ln5 - 9 ln9 -
4 ln4 = -0.3558...`. For `s <= 1`, `|g''(s)| <= M = 7 ln^2 7 + 3 ln^2 3 + 5
ln^2 5 + 9 ln^2 9 + 4 ln^2 4 = 94.22...`, so `g'(s) <= g'(1) + (1-s) M < 0`
for `1-s <= 0.0034`, and for `t = 1 - kappa` with `0 < kappa <= 0.0034`,
`g(t) = -int_t^1 g' >= kappa*0.3558 - kappa^2*M/2 > 0`. At `kappa = 0.00330823`
this lower bound is 6.6e-4; the exact value is 1.1331e-3. `pricing.py` proves the
same two facts with the retained exact interval engines (`g'(1)` upper bound,
the majorant `M`, and the positive enclosure of `g` at both the claimed and
tested exponents); the numbers are in `RESULT.json` under `local_lift_gain`.

Rank mass is unchanged (surplus 760); paid mass falls by 36 over the eighteen
calls to 178,044; paid requests rise by 18 to 66,888. The eighteen-call signed
improvement over #6805 is exactly 18 `g(t)`, `+8.94e-8` in the raw crossing
(from 0.0033081451891 to 0.00330823456614).

## What this does and does not establish

This is an exact identity for the pinned word, checked by exact rational
replay and an independently written adjoint; it is not a proof for any other
word or helper pair. Frame legality (nesting of 105 inside each exit frame,
every used native chart pair, all Gaussian columns of the new pairs) is
checked by `verify.py`. The five framework assumptions of the retained chain
remain (`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`,
`analytic_recovery`), and the selected κ is unchanged. The gain, about
+9e-8 (0.0027%), is small.
