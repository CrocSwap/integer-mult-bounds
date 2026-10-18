# Exact optimum over all dependency ideals

## Statement and scope

Take the PR1062 word pinned in SOURCES.json. Number its 111 target rows from 0 through 110.
Number the 306 elementary gates in its literal target-basis undo from 0 through 305.
These are local target indices; physical target register r is 111+r.

Let E be the target-basis preparation and S the 111-by-9 binary scatter matrix.
The undo is the literal reverse of E. Every undo gate has the form d ^= s.
All target-basis gates use frame zero.

For every subset I of the 306 undo gates, impose this condition:
if i belongs to I and an earlier gate j does not commute with i, then j belongs to I.
Such subsets are precisely the dependency ideals used in PR2115, section 5.
There is no restriction on the size of I.
Let G_I apply its selected gates in their original order.

**Theorem.** The minimum of nnz(G_I E S), over all these ideals I, is exactly 94.
The ideal {31,51,52} attains the minimum.

Here nnz counts ones over F2. Each scatter entry costs one ADD.
All 306 undo gates remain present, either before or after the scatter.
This result does not optimize a different basis circuit, interleaving within the scatter, frame paths, or extra workspace.
It does not assert supplier admission or a new exponent.

## Constant increments from a complete circuit

Write P=ES. Execute the complete undo on P once.
For gate i=(d_i,s_i), let a_i be its source row immediately before that gate in this complete execution.
For an ideal I, the resulting row d is

```text
P_d XOR XOR_{i in I, d_i=d} a_i.                       (1)
```

**Proof.** Proceed in the order of selected gates.
Every earlier gate that writes s_i does not commute with gate i, so the ideal contains it.
By induction, each such earlier selected gate adds the same source row as in the complete execution.
Thus s_i has its complete-execution value when gate i runs.
This proves the claim about its increment, and summing the increments gives (1).

The empty prefix supplies the induction base.

For completeness, two elementary transvections (d,s) and (e,t) commute exactly when d is not t and e is not s.
The source binding contains 850 earlier noncommuting pairs.
The independent checker reconstructs these pairs by multiplying their small coefficient matrices.

Equation (1) is a consequence of the ideal condition.
An arbitrary nonideal subset does not establish a valid circuit through this equation.
In particular, {31,47,51,52} has relaxed cost 93 but omits necessary predecessors of gate 47.
The verifier rejects that subset.

## A certificate using row weights

Represent each nine-bit row by its integer mask, with scatter column 0 as the least significant bit.
Let w_d be the Hamming weight of row d after applying (1).
For each row, temporarily allow every subset of the gates that write that row, ignoring dependencies.
This only enlarges the feasible set, so a row lower bound remains valid for every ideal.

There are 1,386 such row subsets in total.
The most populated row has eight writer gates, so its table has 256 cases.
CERTIFICATE.json lists each row's initial mask, writer indices, case count, and minimum.
The initial total is 97.
Every row except 24,28,47,68,93 has minimum equal to its initial weight.
The five exceptional minima are respectively 4,0,1,1,1, with initial weights 5,2,2,2,2.

The following seven exact row expressions contain every nonzero coefficient needed for the stronger bound.
Here z_i is 1 when gate i belongs to I, and multiplication by z_i selects a mask or zero.
All displayed additions are bitwise XOR, not integer addition.
Zero increments do not appear.

| Row d | Row mask after selected increments |
|---:|---|
| 6 | 3 z_36 XOR 25 z_288 |
| 24 | 171 XOR 128 z_31 XOR 372 z_186 |
| 28 | 3 XOR z_51 XOR 2 z_52 XOR 67 z_53 XOR 256 z_54 XOR 104 z_196 |
| 47 | 96 XOR 32 z_47 XOR 124 z_266 XOR 425 z_298 |
| 68 | 257 XOR 3 z_62 XOR 256 z_93 XOR 67 z_119 XOR 488 z_289 |
| 93 | 3 XOR 257 z_37 XOR 2 z_39 XOR 96 z_159 |
| 96 | 272 XOR 96 z_6 XOR 4 z_7 |

Their complete truth tables give these implications:

1. w_47 < 2 implies z_47=1; z_6=1 implies w_96 >= 4.
2. w_68 < 2 implies z_93=1.
3. w_93 < 2 implies z_39=1; z_36=1 implies w_6 >= 2.

These are small explicit finite statements, not numerical approximations.
Both checkers exhaust their truth tables, including choices that violate the ideal condition.
The relevant ideal implications are

```text
z_47 <= z_6,
z_93 <= z_37 <= z_36,
z_39 <= z_36.                                          (2)
```

Each implication in (2) is a direct noncommuting dependency, not a guessed relation.

First group rows 47 and 96. If w_47 >= 2, their sum is at least 2+2=4.
Otherwise (2) forces z_6=1, and their sum is at least 1+4=5.
Thus w_47+w_96 >= 4 in either case.

Next group rows 68,93,6. If neither of the first two weights drops, their sum is at least 2+2+0=4.
If either drops, (2) forces z_36=1, giving a sum of at least 1+1+2=4.
Thus this second group always costs at least 4.

The other 104 rows exclude these five grouped rows and rows 24,28.
Their individual minima sum to 82.
Rows 24 and 28 cost at least 4 and 0.
Adding the disjoint groups proves

```text
nnz(G_I E S) >= 82 + 4 + 0 + 4 + 4 = 94.               (3)
```

No search over a bounded ideal size enters (3).
The certificate covers every ideal, through the row relaxation and its four necessary dependencies.

## Attainment and complete word boundary

Gates 31,51,52 have no earlier noncommuting predecessor, so their set is an ideal.
Their literal execution changes only row 24 from 171 to 43 and row 28 from 3 to 0.
The total weight falls from 97 to 94.
This is the same attaining split already reported by Sagar Thakrar in PR2115.
The new contribution is its optimality over every ideal.

To connect the optimization with the stated circuit class, write the complete undo as U.
Any omitted gate that precedes a selected gate commutes with it, by the ideal condition.
Repeatedly exchanging these pairs puts selected gates first without changing the product.
Thus U equals the remaining undo after G_I, in execution order.

Keep G_I in D, use listing G_I E S, and put the remaining undo before the original B.
A never reads or writes a target, so the target basis commutes past A.
The copied totals depend only on sources and helpers and remain unchanged.
The modified scatter contributes G_I E S c to the targets for arbitrary copied values c.
The remaining undo cancels G_I E and restores the original S c contribution.
After this undo, the entire state agrees with the original word before B.

The unchanged B and C therefore give the same boundary.

This argument is a binary coefficient identity on arbitrary source, target, and helper inputs.
It extends to any F2-module through the same coefficients.
The verifier also executes the literal COPY/ERASE stream on all 661 input columns, in both directions.
It obtains (x,y,h) -> (x,y+x,h), including restoration of every arbitrary helper.

The 306 undo ADDs move but remain charged. The scatter decreases from 527 to 94.
The complete local ADD count is therefore 11,500-527+94=11,067.
Nine COPY/ERASE pairs, preparation, helpers, A, C, and the original B remain present.

All moved gates use frame zero and preserve the target paths and recursive profile under the inherited realization.
PR2115 supplies the chronological argument and its reported guards for this exact attaining split.
This package does not repeat its native, hosting, precision, or supplier-admission obligations.

## Independent validation and limits

The primary checker follows forward row states to derive P and all 306 increments.
It enumerates row subsets and checks (2), (3), and the complete attaining word.

The separate checker imports no primary or predecessor implementation.
It derives every coefficient through backward propagation of a row functional through the original circuit.
It evaluates all row choices as Boolean truth-table bit planes.
It reconstructs the dependency relation by literal multiplication of transvection matrices.
It also checks the attaining reorder as a complete 111-by-111 coefficient map.
These checks validate the crucial coefficients and lower-bound premises through different traversals and models.

They do not constitute independent human review or proof-assistant verification.

Z3 4.15.3 first found that the exact full-ideal model has no solution of cost at most 93.
That exploratory answer is not a premise of the proof or a runtime dependency.
The small certificate above replaces solver trust and large ideal enumeration.
The finite source facts remain tied to the pinned word and the stated gate ordering.
