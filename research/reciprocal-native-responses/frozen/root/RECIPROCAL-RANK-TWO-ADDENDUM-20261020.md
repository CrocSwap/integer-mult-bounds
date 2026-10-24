# Scope correction and a balanced response

This note supplements the frozen reciprocal rank-two proof. It does not
change that proof's matrix identities.

The statement that the two correction coordinates depend on five modes
needs a more precise form. The first row of V depends on the four a
modes and b. The second row depends on b and c. Their union contains
all six modes. Only the first row, which is the reflection query, has
the proposed rank-five capture to the common radical. The independent
review found this wording defect. No two-coordinate capture was priced
in the frozen proof.

For n=6, a diagonal conjugation reduces both matrix row norms. Set

```text
D=diag(1,1,1,1,-2,2),       E_balanced=D^-1 E D.
```

With s=sum(a), the exact maps are

```text
E_balanced(a,b,c)=(a-s*1-2*b*1, -c, -s-3*b),
E_balanced^-1(a,b,c)=(a-s*1+2*c*1, s-3*c, -b).
```

Both matrices have maximum absolute row sum seven. The unbalanced
pair has maximum absolute row sum eleven. The two diagonals remain
zero and both correction ranks remain two. The a-to-a entries remain
unchanged, so this conjugation preserves a selected minor supported
only on the a modes.

The coefficient changes exchange four unit ADD coefficients with four
coefficient-two ADD coefficients in each direction. They preserve the
sum of the inherited scalar ADD charges. This is a statement about
the matrix transfer coefficients. Pair codes, intermediate norm bounds,
native paths, and routed use still need their own verification.

The root checked the two matrices with exact rational arithmetic.
The native-construction lane has the formulas for a full replay.
Do not treat the row-norm bound as a complete finite-precision proof.
