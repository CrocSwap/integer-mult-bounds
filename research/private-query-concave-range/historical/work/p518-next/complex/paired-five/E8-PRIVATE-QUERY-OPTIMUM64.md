# Private scalar query-frame optimum 64 on the retained E8 pattern

Independent review passed for this proof in the stated model. The separate
review, exact checks and clean-input replay are bound by the source receipt.

Keep the retained 112 E8 root lines. Let `G=R R^T/4`. For any finite
scalar factorization `G=sum_j u_j f_j`, require the binary source frame of
query f_j to contain every source label in its support. Let Q be the sum
of the dimensions of those private query frames. The optimum is Q=64,
over Q, R or C. Arbitrary redundant query rows are permitted.

## Reduce the rank profiles

Drop zero query rows. Drop dependent query rows and absorb their scalar
coefficients into the decoder columns. This operation cannot increase
the source frame sum. It leaves N independent rows whose span contains
the rank-eight Gram code W. Suppose their total frame sum is at most 63.

The analytic frame-capacity proof gives source capacities
`[0,1,2,4,8,12,20,36,64,112]` at ranks zero through nine. The generalized
support proof gives code-subspace support lower bounds
`[0,53,76,92,100,106,109,111,112]` at dimensions zero through eight.

Every subset of k independent query rows intersects W in dimension at
least k+8-N. Apply the corresponding support bound to its support union.
Every one of the 112 source columns is nonzero, and these correction
columns are pairwise nonproportional. Thus at most N source columns have
query-support incidence one. Total incidence is at least 224-N.

There is also an average-union bound. For m selected query rows with
total incidence at most I, distribute that incidence among 112 ports.
The coverage probability of a port in a random k-subset of these rows
is concave in its integer multiplicity. Its average union is therefore
at most the value from the most even multiplicities. Write `I=112*t+r`.
The maximum mean is

```text
112 - ((112-r)*choose(m-t,k)+r*choose(m-t-1,k))/choose(m,k).
```

If each such k-subset must cover more ports, the rank profile is impossible.
Use the summed capacities of the m smallest frames for I. The exact
profile checker enumerates all 1,735,600 nondecreasing profiles with sum
at most 63. A separate generating-function count checks coverage.

For N=9, a pair of queries has a nonzero intersection with W. A frame
pair of ranks at most six and seven has total source union at most 56.
Any such Gram query is a root direction, even over C. Their root-support
capacities sum to at most twenty plus 32, less than the minimum support
53. This excludes the corresponding profiles.

After these exact necessary conditions, only two profiles remain:

```text
[7,7,7,7,7,7,7,7,7]
[1,6,7,7,7,7,7,7,7,7].
```

The nine-rank-seven simplex proof excludes the first. The ten-query
singleton and self-port proof excludes the second. Thus Q cannot be
at most 63. The current eight coordinate gathers each have frame rank
eight and give a factorization of G. Their sum 64 attains the lower bound.

## Binary and scalar fitting changes

The rank-nine binary fitting theorem forces the current fitting matrix
for this fixed retained pattern, including nonsymmetric matrices. Every
minimal rank-nine binary factor coordinate system differs by an invertible
change. This preserves all source support-frame dimensions.

The characteristic-zero rank-eight scalar fitting theorem gives `F=L G D`
for nonsingular diagonal L and D, including nonsymmetric complex matrices.
Transform every factorization of F to one of G by
`G=sum_j (L^-1 u_j)(f_j D^-1)`. Nonzero input scalings preserve all query
supports. Hence the same optimum lower bound applies in those coordinates.

## Cost and scope

The dimension sum is a copy cost only if each private query transfer pays
at least its frame dimension. This model does not cover a physical shared
carrier with another chronological payment rule. It also does not cover
productive source ownership, larger binary or scalar fitting ranks, native
block operations, another zero pattern, or another controller.

This proves that redundant private scalar queries cannot reduce the current
64-rank gather bill in this fixed two-field rank pattern. It does not give
a new supplier, circuit, or exponent improvement.
