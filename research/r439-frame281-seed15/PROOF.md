# Fixed-transfer factorization and the reverse guard

Use the ordered existing registers `[263,275,310,374,410,491]`. A gate `(d,s)`
means `register[d] += register[s]`; its Boolean action uses XOR, while its
positive integer action is used for the cancellation-free precision envelope.
The PR952 frame281 transfer is

```text
3 2 1 1 1 1
2 3 1 1 1 1
1 1 1 0 1 0
1 1 0 1 0 1
3 3 1 1 2 1
1 1 1 0 1 1
```

The emitted 12-ADD circuit is

```text
(5,1) (4,0) (3,5) (2,4) (5,2) (3,0)
(2,1) (1,3) (1,2) (4,1) (0,3) (0,2)
```

Its exact forward integer matrix equals the original 13-ADD circuit's matrix.
Independent column evaluation and all 64 Boolean inputs verify the identity.

## Complete finite minimum recurrence

Let `E_ds = I + e_ds` for `d != s`. Starting from identity, any positive
ADD-only program stays entrywise at least identity. Removing its last gate
subtracts row s from row d. Retain precisely those predecessor matrices P
still entrywise at least I. Every valid program has one such predecessor;
conversely each retained edge reverses to a legal positive ADD. The source
row has diagonal at least one, so every subtraction strictly lowers entry sum.
The graph is finite, and for this matrix the maximum path length is at most
`42 - 6 = 36`.

Set `D(I)=0`; otherwise `D(M)=1+min D(P)` over retained predecessors, with
infinity when none reaches identity. The exhaustive row-subtraction recurrence
in `search.py` gives **D(M)=12**, with 41,235 vertices, 209,118 edges and 88
dead ends. Its sentinel 999 exceeds every possible finite distance; a resource
cap is reported as incomplete, never as an impossibility result.

`independent.py` instead removes the **first** ADD: right multiplication by
`E_ds^-1` subtracts column d from column s. A breadth-first traversal checks
every layer below 12 before accepting the first identity. It visits 41,203
states and examines 208,824 edges from completed layers. It imports no discovery
code. Different closure counts are expected: one method finishes the entire
last-gate graph; the other stops at the first identity layer in the first-gate
graph.

## An exact stricter-class minimum

Let B be the positive matrix obtained by executing PR952's original 13 gates
in reverse order, without negating them. The new circuit exceeds B in four
entries: `(2,1):0->2`, `(5,1):0->2`, `(5,2):1->3`, `(5,3):0->2`.
Thus it fails an entrywise reverse-domination guard.

Discovery traverses only shortest-distance edges `D(P)=D(M)-1`, accumulating
the positive reverse-prefix matrix of each peeled last gate. It prunes a branch
as soon as that matrix exceeds B; all entries can only increase. Exhausting
116 paired states and 283 surviving edges gives no guarded 12-gate witness.
All shorter words were already excluded by D(M)=12. The original 13-gate word
satisfies the guard with equality, proving guarded minimum **13**.

The independent proof uses first-gate paired-column BFS and accumulates the
reverse product by column addition. It explores every retained paired state
through depth 12 and first reaches identity at 13, visiting 735 states. Positive
prefix monotonicity justifies its separate guard pruning. This independently
establishes the same minimum without using the discovery distances. Both
proofs concern a final **positive matrix** bound; no claim is made about every
possible arithmetic circuit or other norm-based guard.

## Whole-word substitution and complete cost

Only `A[825:838]` of the pinned PR952 candidate changes, at the same frame281.
All six registers occur in the replacement. Phase C is regenerated as the
literal reverse of the z-destination gates of A then B at the full frame,
exactly as required by the retained H4. D, scatter, B, frame geometry, retained
totals, start/final frames and other A gates are unchanged. Frame paths are
compared for all 661 registers, and all COPY/ERASE and MOVE costs are rechecked
in the actual emitted instructions.

One forward ADD plus one mandatory cleanup ADD is saved. The complete count
is 23,673 -> 23,671; no new helper, copy, source access, frame conversion,
restoration call or recursive child is hidden. All 661 arbitrary-input columns
and original H1-H5 conditions hold. The paid rank histogram remains
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`, with rank mass 5,129 and nine
rank-seven COPYs (decoder constant 63).

The local reverse guard is sufficient but unnecessarily strong here. Direct
positive replay of the whole word gives F=41,287 before and after, and
B=833,084 -> 832,712. The exact local expression `64*F^3*B^2` remains below
`2^104` (92 bits). The inherited nine-stage expression `2^18*F^5*B^4` is
AST-bound to the pinned `global_k.py`; it changes from

```text
15148224495959132732497298498295876067945200524197888
```

to

```text
15121185848152904741114841695242575582734804360101888
```

and remains 174 bits under the 192-bit allowance. This exact expression check
does not constitute a native 5/9/11-stage replay or a hosted global invoice.
Those execution/adoption obligations remain open. The rank moment is unchanged
and the selected result is complex-bound, so no kappa improvement follows.

These are finite algebraic arguments supported by exhaustive exact programs,
not a Lean proof of the multiplication theorem. Assumptions and attribution
remain as stated in README and NOTICE.
