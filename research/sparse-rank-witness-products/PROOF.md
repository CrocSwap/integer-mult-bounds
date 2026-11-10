# Exact product preservation

Let a_i be row i of A and b_j column j of B, with compatible explicit
dimensions m×k and k×n. The existing helper computes positive common
denominators d_i and e_j, and integer arrays u_i=d_i a_i and v_j=e_j b_j.
If either common denominator exceeds the existing 16,384-bit threshold,
the new routines use the previous exact Fraction predicates/expressions.
The threshold is not a truncation or a numerical approximation.

For a successfully scaled pair,

    (AB)_ij = sum_t u_it v_jt / (d_i e_j).

The producer therefore obtains precisely the old Fraction sum by one integer
dot product and one final `Fraction(numerator, d_i*e_j)`. A Fraction constructor
reduces to the same unique canonical rational. Neither order of exact additions
nor normalization of intermediate rationals changes that result. For k=0 the
empty sum is zero, preserving the rank-zero certificate; explicit dimensions
also preserve zero-row and zero-column products.

For checking, choose S as either the nonzero positions of u_i or the nonzero
positions of v_j. Each term outside S has at least one exactly zero factor, so

    sum_{t in S} u_it v_jt = sum_{t=0}^{k-1} u_it v_jt.

The code selects the smaller support, and checks against target z with the
unchanged cross-multiplication predicate

    numerator * z.denominator == z.numerator * d_i * e_j.

There is no floating arithmetic, tolerance, sampling, dropped witness, assumption
that a submitted basis is sparse, or reuse of the generator's answer as a check.
Dense or malicious submitted witnesses simply have larger exact supports. All
four source checks still run: minor inverse, full factorization, right kernel,
and left kernel. Free-coordinate identity requirements, shapes, rank and pivot
indices, rational grammar, byte limits and certificate budgets are unchanged.

Only coefficient products in certificate generation change. Gaussian elimination
and minor inversion use the same code and encounter the same values, choosing the
same rows and columns. The rational coefficient products above are identical;
therefore both canonical kernel bases and all serialized certificate values are
identical. The producer still invokes the complete checker on its result.

This is a classical implementation-preservation argument. Finite conformance
tests test the code; they do not replace the argument or prove a multiplication
theorem. Runtime measurements concern only the declared fixture and environment.
