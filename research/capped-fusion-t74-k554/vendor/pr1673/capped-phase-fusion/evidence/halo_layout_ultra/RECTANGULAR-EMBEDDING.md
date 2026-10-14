# One-pass near-one rectangular embedding and crop

This supplies the dyadic-container qualification for the halo theorem. It
does not require one full payload scan per axis.

Let input axes have arbitrary lengths `s_1,...,s_D` and let dyadic target
lengths `t_i>=s_i` be given, with total address width
`A=sum_i log2 t_i=O(p)`. The input and output use lexicographic axis-major
order, the last coordinate changing fastest. Every payload record has at
least `c p` bits, as in the retained coefficient representation. Assume
`T=product t_i <= C product s_i = C S`; C is the separately proved
near-one capacity bound, not a product of per-axis dyadic roundings.

Enumerate the complete target rectangle in lexicographic order with its
ordinary A-bit binary counter. For each target address x, output the next
source record if `x_i<s_i` for every i; otherwise output one zero record.
The restriction of target lexicographic order to the valid subrectangle
is exactly source lexicographic order. Hence no source address lookup,
permutation or random seek occurs, and every source record is consumed
once. Its coordinate tuple is embedded unchanged.

Store the A address bits and the A-bit padded representations of s_i on
two work tapes with common axis delimiters. A synchronized scan compares
each coordinate with its bound and ORs the invalid flags. Resetting these
heads costs O(A). Incrementing and resetting the address counter also
costs O(A) in a deliberately conservative implementation. The input/output
heads move monotonically, and each target step costs O(A+B)=O(B) for a
B-bit record. Thus total time and space are O(TB)=O(SB), on a fixed number
of tapes. The bound counts descriptor reads **once per complete B-bit
record**, not once per payload bit. No delicate amortized flag structure
is needed when B=Omega(p).

Cropping the padded tensor is the inverse ordered scan: enumerate target
addresses with the same predicate and copy only valid records. It costs
O(TB) and returns precisely the original axis-major source order.

This does not supply a favorable T/S bound for arbitrary lengths. In the
intended outer construction that bound is the already retained near-one
prime/dyadic capacity inequality. It also does not make zero-extended
dyadic convolution equal to convolution cyclic modulo s_i. The halo theorem
can use the padded representation as storage while every sparse boundary
key is reduced modulo the **true** source period s_i. The following
additional geometry qualification is then required.

## True-period ragged strips

The exact extension to arbitrary true periods, its sparse-volume proof,
source-driven enumerator and finite controls are in `RAGGED-PERIODS.md`.
Only complete valid tile interiors use the flat cyclic convolution; all
regular face and ragged-core lookups use the true period s_i. Invalid storage
zeros never serve as claimed true-period convolution inputs.
