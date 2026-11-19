# Eight changed binary senders

## Result and scope

Every subset of the eight sender replacements in the pinned PR #7776 binary
word preserves its surviving public operator. The new packet rows have a
causal order and use only same-chart donors. With all eight helpers removed,
the eight stated sender corrections are the unique choice in the binary
include-or-omit family that preserves the output. Their errors cannot cancel.

This is an independent algebraic audit of an existing construction. It gives
no new kappa and no full physical or ordinary-service admission. The binary
service limits the source's conditional bound. The selected frontier and all
five framework assumptions stay unchanged.

## Simultaneous contraction rule

Consider an acyclic linear packet network over F2. A packet row specifies
the XOR of available labels at its sender. A terminal row gives a public
output. Let `v_j` be the output column caused by a unit perturbation in label
`j`. Reverse accumulation computes these columns. Suppose one helper `r`
and three distinct packets `z,a,d` satisfy

```text
v_z = e_r,       v_a + v_d = e_r.
```

Suppose `a,d` have the same sender chart. Remove helper input and output
`r`, delete packets `z,a`, add the old row of `a` to the row of `d`, and remove
the labels `r,z,a` from every retained row. Require a causal schedule for
the resulting network. These conditions suffice for the restricted public
operator.

To prove this, project the old output columns onto all retained output
coordinates. The projected column of `z` is zero; those of `a,d` are equal.
In the reverse equations, deleting row `z` removes a zero contribution.
Deleting row `a` removes its coefficients times its projected column.
Adding the same coefficients to row `d` restores exactly that contribution.
Deleted input coordinates need no reverse equation. Every retained column
therefore solves the new reverse equations. A causal network has a unique
solution to these equations. Its public operator is the required restriction.

The proof also applies to several disjoint triples and helper coordinates
at once. Project away all surrendered outputs. Each zero-column and equal-
column identity still holds. Add every retired sender row to its named
donor, then remove every retired label. If the new graph is causal, the same
reverse-potential proof applies. This proof does not assume that the old
delivery deadlines survive.

## Source-specific certificate

The checker reads all 34,137 instructions of the selected source word. It
tracks sets of labels, current chart tags and owned lifetimes. It handles
ADD, MOVE, INIT, CLEAR and whole-field SWAP separately. It checks every
chart use, the public final charts and the retirement of all owned fields.
This extraction is separate from the submitted integer-bitset extractor.

The source has 659 public fields and 2,871 paid packets. Packets below are
zero-based MOVE ordinals. The checker confirms both transpose identities,
the common sender and all original clocks for each row.

| Helper | z | a | d | Main output affected if its sender correction is omitted |
| --- | --- | --- | --- | --- |
| 633 | 2323 | 2657 | 1599 | 114 |
| 638 | 2342 | 2669 | 1617 | 120 |
| 646 | 2381 | 2695 | 1634 | 133 |
| 640 | 2453 | 2743 | 1621 | 157 |
| 649 | 2496 | 2771 | 1646 | 171 |
| 636 | 2497 | 2773 | 1609 | 172 |
| 651 | 2513 | 2783 | 1662 | 177 |
| 635 | 2532 | 2795 | 1608 | 183 |

For all 256 subsets, the checker constructs the simultaneous edited network
from the original rows. A separate topological sort checks causality. Every
XOR donor has the required sender chart. Forward bit-vector propagation
checks each complete output row. Reverse propagation checks the transpose
and the old projected-column invariant at every retained label.

The main map is `X_i -> X_i`, `Y_i -> Y_i+X_i` for 111 pairs. Every surviving
helper has its own identity row. The 256 matrices contain 109,830,912 scalar
entries in each orientation. Bit vectors represent their zero entries as
well as their one entries; this count is matrix coverage, not a gate count.
The full edited public map has rank 651.

All eight omitted-correction controls have rank-one error and affect only
the distinct main output in the last column. The certificate records each
entire error row and a one-input witness. A separate pass checks all 256
include-or-omit correction patterns after all eight restrictions. Their
residual matrices are exactly the sums of the listed disjoint error rows.
Only the pattern with all eight corrections has zero error. Thus the
eight-dimensional parameter-to-error map is injective in this fixed family.

The independent final packet graph agrees with the submitted implementation.
The original emitter then binds that graph to the published physical-word
digest. That binding does not replay the physical word or its rational
projector identities.

## Target debit and complete signed margin

Each restriction removes one rank-one and one rank-three paid packet and
surrenders one rank-four independent helper. No paid route is added. The
full edited native has paid counts `1378,1253,54,47,9,104,10` at ranks 1
through 7. It has 651 public fields and 2,855 paid packets.

The eight lost input coordinates are independent. The retained operator has
rank 651. It cannot give 659 independent public directions from those 651
inputs. The eight surrendered helpers therefore cannot retain productive
credit merely because an owned zero field could replace their input.

With the same 36-call caller, the complete target-minus-paid moment gains
`288*(1+3^(1-C)-4^(1-C))`. This is strictly positive for `0<C<1` by strict
subadditivity of `x^t` for `0<t<1`. The gain is zero at `C=0` and 288 at
`C=1`. This audit checks the local ranks and debit. It inherits the caller
multiplicity and does not recalculate the finite compiler or ordinary saving.

## Limits and open next questions

All eight donor packets occur before their retired partner in the old forward
word. The equivalent reverse alias is therefore late at its old deadline.
The changed sender row and new causal schedule are part of the construction.
The result does not contradict a theorem that fixes the old delivered forms
and receiver deadlines. It also gives no global optimum over other sender
rows or helper relations.

No rational projector, all-width native, full physical word, caller traversal,
owned-erasure implementation, tape layout, ordinary stock, interval gate or
finite compiler replay ran here. No selected cold replay, Lean, Docker,
independent human or formal-kernel acceptance is claimed.

Can another changed sender improve the complete binary invoice? A further
construction must state its causal delivery and charge all lost independent
helpers before it can use the full caller and ordinary compiler.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
