# A sharp denominator cutoff for short ternary decompositions

For nonzero vectors u,v in {-1,0,1}^3 and an integer j>=1, call
A=2^(-j)uv^T a frame. Repetitions and negative entries are allowed.
Every entry has absolute value at most 1/2. The exponent j is intrinsic,
since some entry of uv^T is odd.

## The theorem

1. If at most four frames sum to I3, every exponent is at most two.
2. If at most five frames sum to 2I3, every exponent is at most two.

Both denominator cutoffs and both term limits are sharp. The proof is
uniform in j and uses no finite frame census or register-word theorem.

## Four terms summing to I3

Suppose the largest exponent is J>=3, with multiplicity t. Clear
denominators by multiplying by 2^J and reduce entries modulo two.
The right side and all smaller-exponent frames vanish. A single deepest
numerator uv^T cannot vanish, since both vectors have nonzero binary
reduction. Thus t>=2.

If t>=3, even with four terms any diagonal entry is at most

    (4-t)/2 + t/8 <= 7/8 < 1.

This is impossible. Thus t=2. Fewer than four terms would give at most
1/2+2/8<1 on a diagonal. There are exactly two remaining terms.

If both have exponent one, their diagonal sums are multiples of 1/2,
at most one. The deepest pair contributes at most 1/4 in absolute value
at each entry. Each shallow diagonal sum must therefore equal one.
Each shallow frame has all three diagonal entries +1/2. Its numerator
is ww^T for a full sign vector w in {+1,-1}^3, because u_i v_i=1 forces
u_i=v_i=+1 or -1 at every coordinate.

Every off-diagonal entry of the sum of two such half frames is an integer
in {-1,0,1}. The deepest pair cannot cancel a nonzero integer. Hence the
shallow sum has zero off-diagonal entries and diagonal one, so it is I3.
Its rank is at most two, contradicting rank(I3)=3.

Otherwise the two shallow coefficients have sum at most 1/2+1/4. If
neither is a half, the full diagonal is at most 1/4+1/4+1/8+1/8<1.
The only remaining possibility saturates the diagonal bound exactly.
Its exponents are (1,2,3,3), and every numerator is a full sign square
ww^T. All frames are then positive semidefinite. For the vector w of
the half frame,

    w^T (sum A) w >= (1/2)(w^T w)^2 = 9/2,
    w^T I3 w = 3.

This contradiction proves the first statement for every exponent.

## Five terms summing to 2I3

Suppose one frame A has exponent J>=3, so its entries have absolute value
at most 1/8. On a diagonal the other at most four frames contribute at
most two. If one such contribution is not +1/2, it is at most +1/4 by
the dyadic alphabet. The full diagonal is then at most

    3/2 + 1/4 + 1/8 = 15/8 < 2.

There must therefore be four other frames, each with all diagonal entries
+1/2. They are full sign squares divided by two. Their diagonal sum is
exactly two, so A has zero diagonal. Their off-diagonal sums are integers,
because each is a sum of four numbers in {+1/2,-1/2}. A cannot cancel a
nonzero integer, so its off-diagonal entries vanish too. This gives A=0,
contradicting the nonzero outer-product definition.

## Sharpness

The four sign vectors (1,-1,-1), (1,-1,1), (1,1,-1), (1,1,1) have squares
summing to 4I3 by entrywise addition. Their quarter frames give I3 in
four terms. Their half frames give 2I3 in four terms; splitting one half
into two identical quarters gives a five-term decomposition. Both
denominator cutoffs require exponent two.

Splitting one quarter of the first decomposition into two eighths gives
I3 in five terms with exponent three. Splitting one quarter in the
five-term 2I3 decomposition gives 2I3 in six terms with exponent three.
Neither term limit can increase while retaining the claimed cutoff.
These sign-square identities are classical Walsh/Hadamard identities.
The new assertion is the uniform exclusion.

## Consequence for short-word screening

Consider at most eight frames with total sum 3I3 and a positional subset
S summing to I3. Rational rank gives |S|>=3. Its complement sums to 2I3
and has at least four terms, by a diagonal entry and the 1/2 entry bound.
Thus |S|<=4, and the complement has at most five terms. The two statements
show that every frame has exponent at most two.

These requirements are weaker than a correct formal register word. In
Maximooch's PR1679 model, the determinant gives total exponent 3I3. A
nonzero I3 coefficient in the expanded endpoint requires a positional
subset summing to I3. The new lemma therefore reduces these necessary
screens to the half/quarter alphabet without enumerating projectors or
bounding restored dirty roles.

Tuafo's PR1628 already proves the nine-call endpoint floor for unrestricted
rational frames. That floor is not a new result here. PR1679's finite
exclusion may alternatively be cited after this reduction; its census
is neither rerun nor independently certified by this package.
