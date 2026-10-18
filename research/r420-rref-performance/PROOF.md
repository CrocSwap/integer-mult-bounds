# Exact interface preservation

The domain here is a finite rectangular matrix over the rationals. The shipped
R420 caller supplies integer coordinates; the supplemental suite also exercises
rationals. Malformed/ragged matrices are outside this equivalence claim.

PR367's `_integer_rows` clears denominators of each row by a positive common
multiple, then divides by its nonnegative gcd when greater than one. Both are
nonzero rational row scalings for a nonzero row; zero rows stay zero. Thus the
rational row space is preserved.

At a nonzero pivot column, the kernel swaps one nonzero pivot into the next
rank position. To eliminate entry `b` below or above a pivot `a`, it computes

`(a / gcd(a,b)) * row - (b / gcd(a,b)) * pivot_row`

and divides the resulting row by its content when that content exceeds one.
The coefficient of the replaced row is nonzero, so this elementary replacement
is invertible over Q. The pivot row is left unchanged during that elimination
step. This is exact integer arithmetic, not division with discarded remainder.

Induct on pivot columns. Unused rows vanish in earlier pivot columns; the new
pivot row therefore also vanishes there. Eliminating above the new pivot may
scale an older pivot but cannot fill any earlier cleared off-pivot entry. The
older nonzero pivot remains nonzero. At termination, the nonzero rows have
strictly increasing pivot positions and zeros in all other pivot positions.
Their first nonzero entries are the recorded pivots. All remaining rows vanish.

Dividing each nonzero row by its own pivot gives its unique rational RREF.
PR543's original algorithm computes that same unique RREF, in increasing pivot
order, with zero rows removed. Consequently both returned objects agree exactly:
the list of rows of `Fraction` objects, and the list of pivot indices. PR367's
`key_of` exposes a tuple representation; this adapter instead uses its pinned
`_eliminate(..., reduced=True)` and supplies PR543's list-and-pivots interface.

PR543's unchanged `nullspace_int` chooses increasing free columns, places a one
in each chosen free column, fills pivot coordinates from the negated RREF
entries, and clears denominators by their least common multiple. Equal RREF and
pivots imply equal integer annihilator vectors, including signs, scales and
ordering, not merely equal spans. `Word.__init__` calls the replacement twice
per nonempty frame exactly as before. Nothing is cached across those calls.

All subsequent functions retain the original code and consume identical
dimensions and annihilator vectors. Within this domain, the original geometry,
frame, scalar and interface decisions therefore have the same inputs. The
complete-check, original-mutation and altered-geometry differential runs check
this interface in the actual word. They are finite corroboration of this written
argument, not formal proof of the whole supplier or multiplication theorem.

This argument describes Aman's existing PR367 elimination and the new R420
return-value adapter. It asserts no novelty for fraction-free elimination.
