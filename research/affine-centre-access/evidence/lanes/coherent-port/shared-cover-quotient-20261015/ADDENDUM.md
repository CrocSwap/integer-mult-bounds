# Scope clarifications after independent review

This addendum applies to `QUOTIENT.md` with SHA256
`0e16a12d172ba215041c1096627772262863beca0c2296c8d773bdbac2d6c3d0`.
The original proof, checker, and receipt remain unchanged.

The independent review is
`residual-syndrome/physical-algebra/correlated-sector-review/REVIEW.json`,
SHA256 `3fcd2ffd0fd91289ae1841a3b1543239e4cd891521a55879dad1403c2e6cff50`.
It accepts the phase sector, the exact density formula, and the stated
finite checks. It identifies the two qualifications below.

## Order of the projected mode action

In Section 5, let E=P_H Pi_d and H=I+(H0-I)E. The inverse formula
holds for every E, including E=0. If H0 has finite order, the order of
H divides the order of H0. Equality of these orders requires a
nonzero range of E. On that range H acts as H0 on each mode vector;
on the kernel of E it acts as the identity.

A fixed-d sector can be empty at a short tensor width. For example,
d=3 is absent at width one. For d represented by 0,1,2,3, a tuple of
d copies of omega and otherwise zero columns proves nonzero range
whenever lambda>=d. The normalized cover average retains a nonzero
constant-cover vector on this payload sector. This qualification does
not change the all-width formula for the union S_n, its limit, or the
inverse formula.

## Cover-orbit terminology

The operator S_h f(g)=f(gh) uses the right action of H. Its orbits are
the sets gH, usually called left cosets. In the original note, read
the phrase "right subgroup coset" as "right-action orbit gH".
All matrix products and all formulas already use this displayed
right action. No route order or calculation changes.

No native projector, access cost, supplier theorem, or kappa gain is
added by this addendum. Publication remains on hold.
