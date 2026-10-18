# Exact boundary proof and scoped cost statement

## Algebraic identity

Work over `F2`. The twelve input rows are

```
(A, B, C, X_1, X_2, X_3, Y_1, Y_2, Y_3, Z_1, Z_2, Z_3).
```

An operation `u ^= v` replaces row `u` by `u+v`; it is an invertible
elementary row operation for arbitrary row values. Apply, in order,

```
A ^= B
X_i ^= A                          (i = 1,2,3)
A ^= C
Y_i ^= A                          (i = 1,2,3)
A ^= B
Z_i ^= A                          (i = 1,2,3)
A ^= C
```

The successive values of `A` are `A+B`, `A+B+C`, `A+C`, and `A`. Therefore
the three target families receive exactly `A+B`, `A+B+C`, and `A+C`, while
`A`, `B`, and `C` return to their initial values. This proves the boundary
identity for arbitrary rows, not only for the finite replay inputs. Since
row ADDs act coordinatewise, the identity holds for every width `L`.

The reverse sequence restores the complete input. Every operation is
self-inverse, so this inverse uses the same 13 charged ADDs.

## Cost accounting

The independent per-target circuit uses `2+3+2 = 7` ADDs per three-target
class: two per `X_i`, three per `Y_i`, and two per `Z_i`. Its total is 21.
The borrowed-source circuit uses four anchor transitions and one write to
each of nine targets, for a total of 13. Each ADD reads one source row and
writes one destination row, so these operation, row-read, and row-write
counts all decrease from 21 to 13. At width `L`, each count of ADDs
corresponds to that many length-`L` XOR passes; the arithmetic bill is 21L
versus 13L bit XORs.

The mask-state path is a closed walk on the square `Q_2`. It starts at `00`,
visits `10`, `11`, and `01`, and returns to `00`. A closed walk visiting all
four vertices has at least four edges; the displayed Gray cycle has four.
Thus the anchor-transition count is optimal among one-anchor schedules that
visit each required mask state and perform one ADD per target. Combined
with the necessary nine target writes in that schedule class, the class
minimum is 13. No unrestricted CNOT lower bound is claimed.

## Exact certificate coverage

`verify.py` constructs the 12-by-12 transfer matrix over `F2` for both the
independent and borrowed schedules and requires exact equality with the
specified boundary matrix. It then checks all 4096 scalar input states,
including all source and target values, and checks that reversing the
borrowed schedule restores every state. The negative controls remove the
final restoration, one mask transition, one target write, or replace the
return transition with the wrong source. Each must fail the complete
boundary comparison.

This is a small exact construction certificate, not a supplier invoice.
Every listed operation is charged. The model contains no tape head, clean
allocation, copies, hosted execution, frame conversion, precision bound,
or recursive multiplication call, so those quantities are not inferred.
