# Contracting the silent role-379 stay

Let A, B and D be the ordered frames of charts 748, 1065 and 1072. Their
binary spans are strictly nested and have dimensions 3, 5 and 6. In each
source word role 379 is a public nonmain role. It travels through A → B → D,
with no tape instruction mentioning it between the two MOVEs. The edit
holds role 379 in A until the second MOVE and then sends it directly to D.

| Source | Old MOVE at first clock | Old MOVE at second clock | New MOVE |
| --- | --- | --- | --- |
| [#7636](https://github.com/CrocSwap/integer-mult-bounds/pull/7636) | 131142, MOVE 379 748 1065 false | 131294, MOVE 379 1065 1072 false | MOVE 379 748 1072 false |
| [#7658](https://github.com/CrocSwap/integer-mult-bounds/pull/7658) | 98054, MOVE 379 748 1065 false | 98204, MOVE 379 1065 1072 false | MOVE 379 748 1072 false |

Clocks are zero-based on each original word. Delete the old MOVE at the
first clock, and replace the old MOVE at the second clock. Every retained
event keeps its order and operands. The new MOVE has index one less than
the second original clock. Input and endpoint frames are unchanged.

## Scalar and owned boundary

In normalized frame coordinates a MOVE changes only the active chart.
The tapes have identical ordered INIT, ADD, COPY, SCALE and CLEAR
operations with their full coefficients and chart annotations. Induction
on this sequence gives identical normalized rows after each operation for
arbitrary public input rows. The one chart discrepancy lies on role 379
while no instruction touches that role. The entire chronology is checked
for nesting, ownership, operands and chart co-residency on both tapes,
including the first role-379 observation after the direct MOVE.

The same induction gives equality at the ordered CLEAR observations.
The replay checks each original live-donor certificate against the
actual rational rows at both words' CLEARs. Retained CLEAR indices after
the first deletion shift by one, with identical certificate coefficients.
The independent replay also compares the incoming and outgoing values
of retained COPYs and operations with an owned operand. It checks the
whole public row map and the terminal state of every owned field.
The open interval contains two #7658 CLEARs at source clocks 98059 and
98073. Their certificates name other live providers, and the replay
checks that both omit role 379. The corresponding #7636 interval has
no CLEARs. A valid intervening scalar observation violates the silence
check. A sign
mutation with the same recursive histogram tests whether the replay
detects a change in the row map at equal invoice.

## Physical transition

Use the sources' ordered signed frame convention. If \(F_X\) is the
unitary frame of chart \(X\), the canonical operator from \(X\) to \(Y\)
is \(F_Y F_X^\dagger\). On the held field,

\[
(F_D F_B^\dagger)(F_B F_A^\dagger) = F_D F_A^\dagger.
\]

Intervening operations act on other fields and commute with the removed
first transition in the fieldwise operator model. This permits the
composed action to occur at the original second clock. The finite
checks compare the lowerings for both old pairs and the direct pair
against their respective canonical operators. They compare the
composition of the two old lowerings against the direct lowering.
Each comparison checks signed Pauli action and 512 exact Gaussian
columns in each direction. Multiplying the direct lowering by a
quarter-turn global phase preserves its signed Pauli tableau and changes
the basis columns in both directions. The wrong-phase control rejects
via the actual column comparison.

## Paid invoice

Each native call replaces paid ranks \((2,1)\) with \((3)\). It retains
the total rank mass and every productive target. For \(p=1-C\) with
\(0<p<1\), the strict decrease in the paid moment is \(2^p+1-3^p>0\).
Applying the change at all 17 native invocations reduces the rank-1 and
rank-2 paid counts by 17 each and increases the rank-3 count by 17. The
replay derives the signed caller residual by subtracting the 17 native
invoices from the declared parent invoice and checks the same complete
new invoice with two directed pricing methods.

The numerical brackets rely on the retained caller residual and on the
applicable native, erasure, compiler, precision/tape and analytic
recovery premises. Applying the result to the full signed caller also
requires its actual boundary, conversion and resource checks.

## Predecessor credit

DreamingOfClouds' [#7630](https://github.com/CrocSwap/integer-mult-bounds/pull/7630)
E6 removed the scalar use of role 379 at 1065 on the path inherited by
#7636. DreamingOfClouds' #7658 E2 removed main 176's pickup from role 379
on its #7641 lineage. The tested edit contracts the role-379 MOVEs after
those contact changes. The parent notices retain earlier construction,
caller and source attribution.
