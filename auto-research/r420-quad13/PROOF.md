# Local substitution and complete native cost

Let `g(d,s)` replace register d by its XOR with register s. All six registers
of the replaced contiguous A slice operate at frame 315. No target is among
these registers. The old and new ordered gate lists are in `WITNESS.json`.

For a gate list L, let `F(L)` be its matrix over F2 and `P(L)` its nonnegative
integer transfer matrix, obtained by replacing each XOR update by addition.
The certificate exhibits exact integer matrices satisfying

```
P(new) = P(old),
P(reverse(new)) <= P(reverse(old)) entrywise.
```

The forward equality implies `F(new)=F(old)` by reduction modulo two. It is
an identity on all six inputs, including arbitrary incoming helper dirt, not
only on the clean-source projection. Each binary XOR is an involution, so
reversing either circuit realizes the inverse of this common F2 matrix.

Substituting the new circuit in A therefore leaves every register's value at
the end of the slice unchanged. No external read occurs inside this contiguous
slice. All subsequent A operations, the retained COPY/scatter, B and initial D
can be kept. C is regenerated as the full-frame literal reverse of every
z-destination gate of A then B, exactly as required by PR543 hypothesis H4.
This retains H1-H5 and restores all source/helper inputs. The complete symbolic
replay checks the resulting target action `y_t -> y_t XOR x_t` on 660 columns.

The replacement touches the same six registers, each at the same common frame,
and introduces no register or frame. A register's first touch inside this slice
may occur at a different instruction index, but it has not been changed by an
earlier operation in the slice before that first touch. Its incoming climb is
thus the same climb on the same input. Each register's ordered frame path, all
boundary frames, and all external operations coincide. The verifier compares
these paths for every register and checks nestedness using the exact E8 frames.

For any nonnegative incoming bound vector u, the local forward terminal bound
is the same, `P(new)u=P(old)u`. Each addition only increases a coordinate, so
every local positive prefix lies componentwise below that local terminal bound.
In the full-frame cleanup slice the new terminal bound is componentwise no
larger for every u. Outside these two slices the nonnegative operations are
identical and monotone. Thus the substitution does not require larger
scalar cancellation-free prefix bounds in either traversal of the word.
This is a local monotonicity argument; it is not a newly replayed global hosted
invoice or a signed-integer restoration claim. Restoration is over F2.

The complete cost difference is seven removed binary ADDs in A and seven in C.
Source accesses for the remaining gates are explicitly retained; no helper,
COPY, ERASE, frame move or recursive child is added. D and B are unchanged.
The official record exporter gives 26,902 ADDs instead of 26,916, with the same
2,940 MOVEs, nine COPYs and nine ERASEs. Counting each positive frame increment
and each retained COPY rank yields the unchanged histogram

```
H = {1:1320, 2:1440, 4:60, 5:120, 8:9},
sum_r r H[r] = 5112.
```

Accordingly the finite scalar circuit improves, while its paid recursive
moment `sum_r H[r] r^p` is unchanged for every p. No improved c or kappa follows
from this contribution. No previously established fixed-profile ceiling is
challenged. Acceptance into a supplier still needs the inherited all-size and
physical interfaces and the supplier's full downstream checks.

The exact circuit matrices, finite Boolean enumeration and native dirty-column
replay are checkable evidence for this finite substitution. They are not a
formalization of the all-size multiplication theorem.
