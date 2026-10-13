# Local identity, complete prefix admission and cost

For a six-register block, each ADD is the invertible Boolean transvection
`x_d ^= x_s`, with distinct source and destination. The unchanged PR952
Gaussian nomination code provides candidate factorizations of the old Boolean
map. The new verifier does not import this synthesis code: it checks every
selected program on all 64 Boolean inputs using ordinary lists. Equality of
those tables proves equality of the local Boolean maps for arbitrary dirt.

Every replaced interval is a complete contiguous same-frame A block, using
exactly its original six z registers. No external operation occurs inside
the interval. The remaining instructions and every other payload field are
retained, except that C is regenerated as the literal reverse of z-destination
operations in A then B, all at the full frame. Consequently the complete
Boolean boundary map is unchanged. Source replay independently checks E8
geometry, all 661 input columns, original H1-H5 and the interface conclusions.
Native records establish equality of each register's ordered MOVE path and
rank labels, and of every COPY/ERASE instruction.

## Replacing the sufficient local guard

PR952 requires the replacement's positive integer transfer to be dominated
entrywise by the old transfer in both directions. This is a sufficient
compositional criterion for bounding every surrounding positive computation.
It is not required by the actual complete-word precision inequalities.

The current replacement set has 35 blocks with a growing forward entry,
40 with a growing reverse entry and 33 with both. Thus every one of the
42 substitutions fails the old criterion. The verifier computes this from
all six positive unit columns in both directions; Boolean equality is not
mistaken for equality of the positive integer lifts.

For each actual trial word, replace every ADD by nonnegative addition, start
all 661 logical register bounds at one, and start the fresh scatter temporary
at zero. COPY assigns its source bound, and ERASE resets the temporary. Let F
and B be the largest register bounds in forward and reverse execution, with
COPY and ERASE interchanged under reversal. The triangle inequality and
induction through the instructions give valid absolute-value bounds for
every prefix. By homogeneity they apply to arbitrary uniformly bounded
incoming data, under the same inherited realization assumptions as the
selected supplier.

The builder evaluates complete macros; its source sets exclude their
destination, and the monotonically increasing destination dominates internal
macro ADDs. Its scatter evaluation accounts for all center-to-target ADDs.
The independent pinned PR952 interpreter instead lowers literal instructions,
explicitly allocates and clears the temporary, and replays both orientations.
Both methods agree on every one of the 42 accumulated candidate words. The
literal interpreter simultaneously checks the full arbitrary-dirt Boolean
endpoint, including source/helper restoration and `y += x`.

A word is admitted only when the exact integer inequalities

```
64 * F^3 * B^2 < 2^104
2^18 * F^5 * B^4 < 2^192
```

hold. The first is the native local payload bill. The second substitutes
K = 4 into the pinned controller expression `2^nb * F^(K+1) * B^K`, with its
asserted `nb = 6*(K-1) = 18`. The verifier checks this expression in the source
AST. The inherited charge is 192 bits at this K. This is a source-bound
substitution, not execution of the full global hosted controller.

For the final word F = 35,655 and B = 692,438, giving exactly

```
64 * F^3 * B^2 = 1390922981997045430446432000
2^18 * F^5 * B^4 = 3472687462578695909779041695145939468368884531200000
```

These require 91 and 172 bits. Actual trial costs and bounds are retained in
CERTIFICATE.json and independently replayed into EXPECTED.json. Zero rejected
trials is a measured outcome, not evidence that arbitrary replacements fit.
The controls insert Boolean-identity transvection pairs and rebuild literal
C. One such word passes the local ceiling with 103 bits but fails the
nine-stage ceiling with 194 bits; another needs 111 local bits. Both complete
Boolean endpoints pass before the precision check rejects them.

## Full price and remaining class limitations

The 42 substitutions remove 120 A ADDs. Each has one paired cleanup operation,
so the net saving is exactly 240. The source and helper counts, frame paths,
copies, erasures and recursive children are unchanged. Literal and native
counts both give 24,305 / 23,673 / 23,433 for PR589 / PR952 / this candidate.
Native record counts are 27,234 / 26,602 / 26,362. The paid histogram remains
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`, rank mass 5,129, with nine
copies of rank seven. For 5/9/11 stages the original bridge ADD counts are
666 / 1,998 / 2,664 and fresh copy counts are 45 / 81 / 99. The incremental
ADD savings against PR952 are therefore 1,200 / 2,160 / 2,640 at those stages.

The strict comparison is exhausted only for the declared Gaussian menu on
the frozen PR952 input. The new search uses the same menu, a changed admission
condition and one seeded order of the blocks. It checks at most 32 nominees
per block and stops after the first admitted nominee. All first nominees
pass in the actual run. It does not search all GL(6,2) factorizations, minimize
complete cost under the precision ceilings, or exclude further passes with
other admission orders or nomination methods. The 12-ADD PR925 frame-267
factor remains shorter than our 13-ADD nominee. No individual-block or
whole-circuit optimality is claimed.

All claims here concern this finite word and retained conditional interface.
The full hosted compiler, invoice, outer assembly and underlying all-size
mathematical obligations are not discharged by these computations.
