# Exact audit of the last rational bypass

This is an independent scalar-operator and paid-delta audit of
[PR #7786](https://github.com/CrocSwap/integer-mult-bounds/pull/7786),
head `ff6f1d8ab3fafb71ea12ccd943013d058c0f5847`. It resolves the
source's chart-237 omission handoff. It also proves that the new value
cannot be synthesized from the retained receiving-bank inventory.
The construction and selected multiplication exponent do not change.

## Complete source and operator binding

The final graph has canonical SHA-256
`23b092d7e25b7e05caf76918e5956169113d6ea978d0939c95ce00f96595a67f`.
Reversing its exact published delta recovers the preceding graph
`1f1abdbd0601ad764ac254164e55dca39b6b83ac4ab0feb9904043639f291b28`.
Applying the delta again returns every final byte in the canonical
representation. The delta changes 24 forms and three paid-move entries.
All frames, public labels, input/output charts and 1,284 owners stay fixed.

The checker derives the desired operator from the literal layout. It
checks all 400 main fields and all 884 independent helper returns.
It expands every row of both graphs over exact rational numbers. Each
complete matrix has 1,648,656 coefficients. Both equal the desired
operator. A separately transposed final graph also expands to the full
adjoint. These three complete expansions use 47,736,551 integer
coefficient products. No random input test substitutes for these checks.

The source data are the
[frozen final graph](https://github.com/Clear1nsight/integer-mult-bounds/blob/ff6f1d8ab3fafb71ea12ccd943013d058c0f5847/research/p104-iterated-returns/complex/WORD.json.gz),
[layout](https://github.com/Clear1nsight/integer-mult-bounds/blob/ff6f1d8ab3fafb71ea12ccd943013d058c0f5847/research/p104-iterated-returns/complex/LAYOUT.json.gz)
and [reversible delta](https://github.com/Clear1nsight/integer-mult-bounds/blob/ff6f1d8ab3fafb71ea12ccd943013d058c0f5847/research/p104-iterated-returns/complex/POST-BIRTH-CHAIN-1.json.gz).
Their hashes are checked before any mutation control.

## The complete error law

Let u be the expanded input covector sent in new slot 80. In the final
graph its local expression is value(77)-value(76). Its complete support
has 17 independent inputs; RESULT.json records every coefficient.
In particular u_22=1 and u_1282=0. The exact scalar expansion gives

```text
new value(34002) - old value(34002) = u/2,
new value(11)    - old value(11)    = u/2.
```

Let h be the full output response to a unit pulse at paid node 34002,
and z the response to a unit pulse at new slot 80. Their supports have
20 and 16 outputs. The exact source-bound minor is

```text
             h      z
output 1282  2      0
output  488 -1     -1/2

determinant = -1.
```

Consider the two-parameter family that changes the row-34002 recoding
from u/2 to lambda*u and scales slot 80's payload to rho*u, leaving
all other final forms and contacts fixed. The donors 76 and 77 precede
node 34002, so u is unaffected by either change. Slot 80 has terminal
readers only. Linearity therefore gives the full matrix error

```text
E(lambda,rho) = [(lambda-1/2) h + (rho-1) z] u.
```

Here the bracket is a column and u is a row. This identity holds for
all rational lambda,rho, not only the six tested pairs. Since u_22=1,
the displayed minor proves E=0 if and only if lambda=1/2 and rho=1.
The newly independent output 1282 forces the recoding coefficient;
checking only selected old outputs would miss that obligation.

In particular, omitting slot 80 while retaining the correct recoding
gives E=-z*u. This has rank one and exactly 16*17=272 nonzero entries.
Its entry (488,22) is +1/2, as stated in the source handoff. The adjoint
has the transposed error and the same +1/2 witness. The checker tests
each parameter pair on a complete input column and a separately
transposed complete output covector. RESULT.json records the two-axis
errors and the full vectors h,z,u.

## No free reconstruction from the receiving banks

New slot 80 arrives at chart 127. Exclude that slot, then include every
other paid arrival at chart 127 and every public input initially at
that chart. This gives 901 banks. No paid sender depends on slot 80;
its readers are terminals only. Thus all retained bank values remain
available as the same symbolic forms when slot 80 is omitted.

The checker expands all 901 bank forms over the same 1,284 independent
inputs. They have rank 901. Exact elimination supplies a sparse vector
w with 16 nonzero entries such that

```text
bank_j(w) = 0 for every one of the 901 retained banks,
u(w) = -2.
```

All these equations are checked directly. Therefore u is outside the
span of the complete retained receiving-bank inventory. Even an
arbitrary rational linear combination with no timing restrictions
cannot reconstruct it. A terminal-only repair using those banks cannot
replace the missing slot-80 contribution while the other upstream
forms remain fixed. This is stronger than a failure to find a sparse
expression. It does not exclude a changed upstream word, a new paid
delivery, a new chart or a different consumer interface.

## The entire paid change

Both full schedules pass causal same-chart donor checks and strict
binary-subspace containment checks for every paid move. The only paid
changes are

| Action | Slot | Route | Grade |
|---|---:|---|---:|
| retire | 12 | 477 to 127 | 1 |
| retire | 95829 | 237 to 477 | 4 |
| insert | 80 | 237 to 127 | 5 |

The full native paid count drops from 5,712 to 5,711. All independent
target ranks remain unchanged. The new native target histogram is

```text
rank:   1   2   3    4   5   7   8    9
count: 19   7   9  239  28  15  32  535
```

Thus for any tariff H the native signed improvement is H1+H4-H5.
Under the source's unchanged 48-call caller it is 48(H1+H4-H5).
For H_r=r^t and 0<t<1 this is strictly positive, because
1^t+4^t>5^t. At t=1 it is zero. This proves the entire delta over the
exponent interval; it does not recompute a complete crossing or the
source's ordinary/outer admissions.

## Evidence, limits and open next questions

All ten retained files are authenticated. The checker uses only generic
exact arithmetic from Ali Romman's
[PR #7777 checker](https://github.com/aliromman/integer-mult-bounds/blob/0288431ab2ad0cccfbede0b57cd3edfb2679e0f6/research/p104-first-relay-repair/verify.py).
Its source-specific suite is not invoked. No PR #7786 verifier is
imported. Five incorrect parameter pairs change the full operator;
the correct pair passes. Controls also reject a false journal pin,
wrong bypass source chart and altered separator.

The preceding birth/quotient history, physical all-column charts,
held-state erasure, complete caller, ordinary compiler, precision,
finite stock and outer services are not replayed. Their source claims
remain separate. No new kappa, Lean, Docker, selected cold replay or
independent human/formal acceptance is claimed. All five assumptions
and the selected frontier remain unchanged.

A further paid improvement must change the available bank span or
upstream recoding, rather than discard slot 80 under this fixed word.
Name and price that changed interface before extending the search.
