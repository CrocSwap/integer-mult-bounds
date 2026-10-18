# One-clean-carry scalar composition

## Boundary and claim

Fix a width `23 <= W <= 256`. Two disjoint W-bit two's-complement banks
hold target T and auxiliary/source S; one additional bit initially holds zero.
Both banks are exclusively writable for the duration of a scalar macro.
The circuit returns S exactly and returns the carry bit to zero. It uses
no coefficient scratch word. For ADD, S is the actual source. For SCALE,
S can be arbitrary dirty data, but a disjoint writable bank must be supplied.
No native owner assignment for that SCALE bank is established here.

For a reduced dyadic ADD coefficient q, require that S be divisible by its
denominator. For exact signed interpretation, require T, S and the completed
endpoint to fit W signed bits. For SCALE, retain every inherited target-walk
prefix alignment and range guard. `replay.bind` re-establishes those guards
for the two literal PR3076 providers and both orientations at the PR3094
seven-fractional-bit, `P+20` capacity. Intermediate ADD and negation states
below are modular; they need no additional signed guard bits.

The result is a conditional physical scalar implementation. Exclusive mutable
access strengthens the borrowing premise relative to PR3094's gate-level
read-only source implementation. Unknown access, routing, clean-stock and
consumer costs are not zero.

## MAJ/UMA primitive and shifts

The adder is the credited Cuccaro–Draper–Kutin–Moulton MAJ/UMA construction,
already used for local dyadic ADDs in PR3081. See the original
[2004 paper](https://arxiv.org/abs/quant-ph/0410184). No new adder is claimed.
At position i, write a=S_i, b=T_i, c=the incoming carry wire. The MAJ gates
are `c ^= a; b ^= a; a ^= b & c`. They place
`majority(a_old,b_old,c_old)` in a. The outgoing carry is therefore available
as the next position's c. At the top bit, `b ^= a; b ^= c` supplies the
modular sum without retaining overflow. Descending positions apply
`a ^= b & c; c ^= a; b ^= c`, restoring a and c while leaving the sum in b.
This proves source and clean-carry return by descending induction.

For n active bits, n>=2, the literal count is `2n−2` Toffolis and `4n−2`
CNOTs; n=1 uses one CNOT. There are n−1 MAJ and n−1 UMA blocks plus two top
CNOTs. Each block has one Toffoli and two CNOTs. The implementation retains
the standard literal gates rather than claiming a gate minimum.

For exponent e>=0, add source bits `[0,W−e)` to target bits `[e,W)`.
Those wires represent `2^e S mod 2^W`; omitted low target bits stay fixed.
If e>=W the increment is zero. If W−e=1 use the one-CNOT case.
For a right shift k=−e, require k<W and the low k source bits zero.
Copy the sign into those k bits with k CNOTs; connect the distinct source
wires in order `S[k:W] + S[0:k]`; run the adder; undo the k copies.
These wires encode the arithmetic quotient S/2^k. The adder restores every
source wire before unfill, including the original sign. This costs
`2W−2` Toffolis and `4W−2+2k` CNOTs and uses one clean carry.

For q=sum sign_j*2^e_j, concatenate the shifted adders, reversing a term's
entire gate list when its sign is negative. Every term restores S and carry,
so terms compose. The inherited signed-power expansion has at most nine terms,
and every exponent is at least the negative reduced-denominator exponent.
Thus denominator divisibility supplies all required low zeros. The sum has
exact coefficient q; intermediate target wrap is harmless modulo 2^W.

## SCALE and arbitrary dirty auxiliary data

HALF and DOUBLE retain the inherited reversible rotation and sign-fill
circuits, each costing `3W−2` CNOTs. Their inherited alignment and redundant
sign-bit guards remain necessary.

For negation, use the same one-carry modular adder three times and then
swap the two banks with W three-CNOT swaps:

```text
(T,S) -> (T+S,S) -> (T+S,-T) -> (S,-T) -> (-T,S)  modulo 2^W
```

Every adder returns its own carry. S needs no clean bits or numerical bound
beyond being a W-bit word, and is restored after the swap. The exact cost is
`6W−6` Toffolis and `15W−6` CNOTs. This costs more gates than PR3094's
carry-bank negation but permits the whole scalar layer to reuse a single
clean bit. Signed SCALE interpretation follows from the unchanged endpoint
and prefix guards, not from interpreting the temporary shears as signed values.

## Complete source-bound invoice

Cold replay authenticates the complete 30-file predecessor dependency set,
rebuilds both native programs, replays the complete native/capacity checks,
and rebinds all 9,992 scalar macros per orientation. The actual histogram
has 9,438 ADD and 554 SCALE macros. For both real components, the signed-power
ADD counts by exponent are:

| Exponent | −3 | −2 | −1 | 0 | 1 |
|---|---:|---:|---:|---:|---:|
| Calls | 210 | 5,432 | 7,040 | 5,862 | 478 |

SCALE additionally uses 924 negations, 222 HALF and 300 DOUBLE operations.
These counts are identical for the two providers and both orientations.
The dispatch hashes bind the chronology; no macro, frame, child or cleanup
operation is removed from the source stream.

Summing the literal formulas gives, per provider/orientation and both real
components, for every supported W:

| Implementation | CNOTs | Toffolis |
|---|---:|---:|
| PR3094 direct caller | `82274W−104534` | `77936W−119740` |
| One-carry caller | `91514W−9476` | `43588W−44544` |
| Old minus new | `−9240W−95058` | `34348W−75196` |

The combined unweighted logical-gate saving is `25108W−170254`, strictly
positive throughout 23<=W<=256 (at W=23 it is 407,230).
At W=84, CNOTs increase by 871,218, Toffolis fall by 2,810,036, and the
combined saving is 1,938,818. Clean carry stock falls from 83 bits to one;
the two operand banks total 168 bits in both template layouts. The changed
SCALE borrowing obligation must still be implemented on actual native owners.
A weighted tariff or physical time need not track this unweighted sum.

## Evidence and limits

`RESULT.json` records fresh native dispatch bindings, circuit hashes and all
four invoices. The verifier exhausts all aligned signed sources and every
modular target for ADDs at W=4..7. For SCALE it exhausts every arbitrary
auxiliary bank and each target satisfying the inherited guards. Complete
output states and reversed gate lists are checked on 314,560 truth columns
across 124 circuits. A separate Boolean-list evaluator checks 1,550 larger-width
fixtures through W=256. The written argument supplies the width-uniform proof.
Meaningful malformed/sign/cleanup controls run separately under optimized Python.
The reused native engine is executed, not independently reimplemented.

No recursive paid profile, moment, kappa, selected frontier, full native caller,
multitape routing bound or unconditional multiplication theorem is changed.
