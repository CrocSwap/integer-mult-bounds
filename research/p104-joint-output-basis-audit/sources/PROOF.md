# Nine joint native output contractions

The claim is conditional `kappa = 0.00315057`. The exact source is PR6349.
The consumer is the fixed PR6348 binary query tree. PR6350 already publishes
their composition at `0.00314980`. The contribution here is a new supplier
word with nine smaller helper outputs. All inherited assumptions remain.

## 1. Source and native transpose

The source has 770 independent public inputs, 29 owned labels and 32 owned
lifetimes. The main interface has 104 pairs. Each of the 562 other public
inputs supplies an independent helper target. Four source helper inputs
already start in nonzero frames; those PR6349 input lifts remain unchanged.

Use `Z` for frame 3 and `Omega` for frame 127. Their dimensions are zero and
nine. The construction first takes the native transpose of the complete
source. Replace each frame by its orthogonal complement over `F_2^9`, reverse
the event order, reverse each MOVE and swap each ADD's source and destination.
Exchange INIT with CLEAR. Exchange the two main roles in each live pair.
An original COPY into a zero owned field becomes an ADD in the transpose.

This is the retained source/destination duality. It is a construction rule,
not a substitute for verification. The final forward word is checked by the
unchanged endpoint and native-phase engines. In particular, the argument
does not infer native equality from a scalar matrix alone.

In the transposed word, let `A` be the public scalar preparation at `Z`.
Every public field leaves `Z` at most once and cannot return. Every scalar
operation at `Z` uses only public fields. Thus these scalar operations can
move to the front, in their original order. A later operation at `Z` cannot
use a field that has already left `Z`.

Let `C` be block diagonal on the first-departure groups. A block uses only
fields with the same first destination. It can therefore be applied at `Z`
and reversed at that destination. This permits a useful departure functional
to become one physical row. `BASIS.json` gives all three blocks of `C`.

## 2. Joint input and departure bases

Choose the nine anchor roles

```text
P = (703, 393, 707, 484, 297, 485, 226, 361, 451).
```

All nine are full independent helper channels in the transposed source.
Let `B0` be the explicit invertible helper basis in `BASIS.json`. It uses
only ADD, SWAP and nonzero dyadic SCALE operations. It acts only among
independent `Z -> Omega` helpers. The columns `B0 e_a`, for `a in P`, are

| Anchor | Input direction |
|---|---|
| 703 | `e703 - e704` |
| 393 | `4e395` |
| 707 | `e707` |
| 484 | `e484 + 4e707` |
| 297 | `-e288 - e292 + e296 + 2e299 - e302 + 2e303` |
| 485 | `e485` |
| 226 | `-e449 + 4e707` |
| 361 | `-e352 - e356 - e366 + e367` |
| 451 | `e451` |

Write `b_a` for anchor row `a` of `C A`. Exact rational calculation gives

```text
b_a B0 = e_a^T + d_a,
support(d_a) is disjoint from P.
```

Each `d_a` uses only full helper coordinates. Define

```text
B2 = I - sum_a e_a d_a.
```

The off-anchor condition gives `d_a e_b = 0` for all anchors `a,b`. It follows
that `B2` is invertible, with inverse `I + sum_a e_a d_a`, and

```text
b_a B0 B2 = e_a^T.
```

The constructor checks every coefficient of this identity. It also executes
`B2`, `B0`, `A` and `C` on independent symbolic rows with the nine anchor
inputs set to zero. Every resulting anchor row is exactly zero. These are
checks on full sparse rational rows, not sampled vectors or modular ranks.

Use nine zero owned fields in place of the anchors during this preparation.
They can be cleared at the end because their rows are zero. The actual nine
public inputs have not been set to zero. They remain arbitrary in their new
native entrance frames and are inserted next. The zero specialization is
only a linear decomposition of the preparation. The other input responses
have all been computed.

The complete input basis is `B0 B2`, since the emitted word applies `B2`
first. It acts only on full helpers. All full helper maps have the same native
operator, so this basis commutes with their common endpoint map. The final
inverse basis restores the independent helper endpoint.

## 3. Legal response insertion

The missing anchor columns are `C A B0 e_a`, because `B2 e_a = e_a`.
`BASIS.json` lists every nonzero response coefficient. Give anchor 703 the
four-dimensional entrance

```text
F4 = span(dual frame 712) intersect span(dual frame 714).
```

Give anchors 393, 707, 484, 297, 485 and 226 the one-dimensional frame
`span([51])`, which is dual frame 246. Give anchors 361 and 451 the
one-dimensional frame `span([30])`, which is dual frame 245.

Each nonprimary response group has one entrance frame `F` and one original
first destination `G`. The emitted MOVE checks require `F` to be a subspace
of `G`. The primary response groups contain only their unit anchor rows.

If `F = G`, move a recipient to `G` and add its missing input response there.
If `F` is smaller than `G`, the group's response matrix has rank one.
Choose a carrier with response `s`. Each other recipient has response
`lambda*s`. Let their arbitrary prepared old values be `u_c` and `u_r`.
The legal sequence is

```text
at Z:    recipient <- u_r - lambda*u_c
         move recipient Z -> G
         move carrier Z -> F
at F:    carrier <- u_c + s
         move carrier F -> G
at G:    recipient <- recipient + lambda*carrier.
```

The recipient now equals `u_r + lambda*s`. The carrier equals `u_c + s`.
All arbitrary old values are preserved. Both carrier transports are paid.
No copy of an input direction or old carrier value is assumed to be free.
All ratios and response proportionalities are exact dyadic equalities.

Keep each primary input at its entrance until all responses that need it
have been delivered. Then move it to its original first destination. Move
the remaining members of each `C` block there and apply `C^-1`.
Delete exactly these original first-departure MOVEs. Keep the remaining
nonzero-frame source events in their original order. Finish with `B0^-1`
and then `B2^-1` at `Omega`.

After `C^-1`, every field has the same value and frame as the source with
input basis `B0 B2`. The source suffix is therefore legal. The inverse output
basis gives the original independent endpoint with the nine new input
frames. This proves the scalar construction for arbitrary public inputs.
The native frame rule lifts the same argument to each positive tensor width;
the exact map and absolute-phase checker verifies each required local map.

## 4. Return to the forward interface

Transpose the construction again. Restore the original coordinate bases of
all 1,094 source frames. The new frame is the orthogonal complement of `F4`.
Its exact basis is `[7,9,35,66,400]`. The final native replay checks these
coordinate choices and their absolute phases.

All original input frames remain unchanged. Exactly nine output frames change:

| Helpers | Final frame | New target rank | Old target rank |
|---|---|---:|---:|
| 703 | 1094, basis `[7,9,35,66,400]` | 5 | 9 |
| 393, 707, 484, 297, 485, 226 | 246 | 8 | 9 |
| 361, 451 | 245 | 8 | 9 |

No main boundary changes. Frames 1091 and 1092 retain their exact source
bytes. The original R22 and retained-operand constructions remain part of
the source. Double transposition changes original COPY instructions into
equivalent ADDs into zero owned fields. The original scalar opcode list is
therefore not claimed to remain byte-identical.

The final word has 17,657 events and 1,095 frames. It uses 29 owned labels,
41 owned lifetimes and peak storage 13. The nine new lifetimes use labels
770 through 778 in a separate interval. They receive no productive credit.
The unchanged checker validates every INIT, MOVE, COPY/ADD and CLEAR.
The constructor separately proves that the nine dual temporary rows are
zero at their CLEARs; that property is not inferred from owned-erasure
permission.

## 5. Complete invoice and price

Relative to PR6349, the exact local paid change is

```text
14H1 - 4H2 - 3H3 + 4H4 - 5H5.
```

The exact productive change is `H5 + 8H8 - 9H9`. Paid rank mass falls from
5,946 to 5,934. Helper rank mass falls from 4,226 to 4,214. The helper count
stays 562. Local paid calls increase from 3,450 to 3,456. Both parts of the
signed invoice are needed; a paid-rank decrease alone does not prove a gain.

The PR6348 caller is fixed. It has 19 native calls, 16 thin queries and
16 paired whole idles. Every call receives a fresh set of 562 independent
helper inputs. The main caller has `34*104` independent fields. Thus its
productive field count remains `19*562 + 34*104 = 14214`.

With `P_local` and `T_local` the new local profiles, its complete profiles are

```text
P = 19 P_local + 1664H1
    + 208(9H16 + H24 + 4H32 + H56 + H64)
T = 19 T_local + 208H153
    + 208(9H17 + H25 + 4H33 + H57 + H65).
```

The emitted caller count and the separate tree formula agree. There are
70,656 paid jobs and rank-mass surplus 808. The complete paid and target
changes are nineteen times the two local changes. Every additional carrier
transport and every reduced helper target occurs nineteen times.

The exact raw crossing lies in
`(0.00315058201488, 0.00315058201489)`. A rational derivative bound makes it
unique below the retained BIT cap `.0034`. Two separate rational engines
check the strict moment inequality at the tested saving `.003150575`.
The old supplier with this same caller has its crossing in
`(0.00314981300605, 0.00314981300606)` and fails at the new claim `.00315057`.
This reproduces the released PR6350 control without importing its pending
code. The new mechanism's gain is not combined with the earlier composition
gain in the headline comparison.

Completion uses power 1024, cutoff 12, floor 13, tail offset `1/7`, reserve
`10^-12` and decay `31/32`. The compiler uses theta `63/64`, logarithm power
1100 and gap `1/1400000000`. The sufficient threshold is
`N = 2^70855400000000`. The adjacent rejected threshold point is checked.
These are sufficient symbolic bounds; the huge word is not materialized.

The new local scalar allowance is 128,694. The retained native and route
allowance is 5,368,000. Their sum is below the allocated `10^7` per call.
It includes the 41 owned lifetimes. The complete ordinary-work upper bound
is 194,902,768, below `10^9`. All 54 strict and four functional outer
predicates pass with the retained admitted BIT saving `.0034`.

The signed change is not better for every power `0<t<1`. At `t=0`, the extra
six paid calls give a loss. The complete exact check at the stated saving is
the applicable price evidence. No universal concave-tariff claim is made.

## 6. Checks and limits

The verifier authenticates all thirteen live source files before it imports
their code. It regenerates the basis witness and every word payload byte.
It checks the source and changed scalar words, then uses a separate dense
reverse replay for all 799 columns and 638,401 coefficients. The unchanged
native engine checks 2,932 distinct maps, 208 main adapters, 1,124 helper
normalizers and absolute phases. The fixed physical caller check covers all
7,904 contacts and 53,248 central-square columns.

Controls omit an input-basis correction, a dirty-carrier subtraction, a
departure inverse and an output inverse. Other controls change an output
frame, a temporary frame, a native charge or a productive debit. All reject.
The retained caller controls reject a missing thin query, translation or
idle, and a wrong central orientation. Source corruption is rejected.
All explicit guards remain active with Python assertions disabled.

The five assumptions `native_all_columns`, `owned_erasure`, `compiler`,
`precision_tape` and `analytic_recovery` remain. Finite checks do not prove
their full quantified statements. Author replay and hosted replay do not
establish independent scientific acceptance. The selected frontier is not
changed. The gain is small and does not meet the donor's breakthrough target.

## Open next questions

An independent review should first check the joint anchor identity and the
paid response insertion, then trace each of the nine target debits through
the fixed caller. A larger gain needs a new exact source construction or a
new caller contract. An exploratory local-only contraction screen found no
accepted extension. Its search log is not included here, and no obstruction
or optimality claim depends on it. See TASK.json for the first steps, the
required live overlap check and the remaining obligations.
