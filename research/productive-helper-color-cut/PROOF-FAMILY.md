# The whole three-output basis family fixing the protected value

This extends the color-cut obstruction in [PROOF.md](PROOF.md) to an infinite
family of direct targets. It uses the same 24 input registers, four colors,
ascending canonical scalar model and nine required monochrome output caps.
It makes no claim about arbitrary native operations, changed output caps or a
paid nonascending circuit.

Write `u = H output416 = input13 + input416`. For rational parameters
`lambda, mu`, change the other two output rows by

```text
output419 += lambda*u,
output421 += mu*u.
```

All other output rows remain those of `H = P T M`. In particular, the nine
monochrome output roles and their caps remain unchanged. Even if a parameter
choice fails an additional physical support condition, granting it here only
enlarges the class to be obstructed.

## Exact uniform rank certificate

Let `G` be the 15-by-8 dirty-output/hot-input block reconstructed from `H`,
in the row and column orders in `PROOF.md`. The changed block is

```text
G(lambda,mu) = G + (lambda*e419 + mu*e421)*e13^T.
```

The seven columns other than column13 are unchanged and have exact rank7.
For every rational parameter pair, an exact right-kernel vector, in hot order
`13,16,43,44,51,78,99,104`, is

```text
n(lambda,mu) =
 (2, mu, -1-lambda-mu, mu, -2*lambda,
  lambda-1, lambda-1, 1+lambda-mu).
```

Its first coordinate is always2, so it is never zero. Thus the rank of
`G(lambda,mu)` is exactly7 for all parameters, and its rowspace is precisely
the hyperplane perpendicular to `n(lambda,mu)`.

`check_family.py` checks this as a polynomial identity, without selecting a
grid of parameters. Writing `n=n0+lambda*nL+mu*nM`, it verifies the constant,
both linear and all three quadratic coefficients of `G(lambda,mu)*n` on
every row. In particular, `nL[13]=nM[13]=0` makes the quadratic coefficients
vanish. It independently checks the rank7 unaffected-column minor and the
rank5 block obtained by deleting both changed rows.

## The single-color directions never span the rowspace

A hyperplane in eight coordinates intersects a two-coordinate color plane
in dimension2 if both corresponding normal coordinates vanish, and otherwise
in dimension1. Applying this to the four disjoint color pairs gives:

| Color pair | Restriction of the normal | Intersection dimension |
|---|---|---|
| 13,51 | `(2,-2*lambda)` | 1 |
| 78,99 | `(lambda-1,lambda-1)` | `1 + [lambda=1]` |
| 16,44 | `(mu,mu)` | `1 + [mu=0]` |
| 43,104 | `(-1-lambda-mu,1+lambda-mu)` | `1 + [lambda=-1 and mu=0]` |

The final row follows by adding the two equations to get `mu=0`, then
substituting to get `lambda=-1`. Since the color pairs have disjoint support,
their intersection subspaces form a direct sum. Their total dimension is

```text
4 + [lambda=1] + [mu=0] + [lambda=-1 and mu=0] <= 6 < 7.
```

For `mu != 0` the sum is at most5. For `mu=0`, the conditions `lambda=1`
and `lambda=-1` are disjoint over the rationals, so the sum is at most6.
The necessary color-cut condition therefore fails for every parameter pair.
There is no ascending realization of any target in this family under the
stated model and boundary caps.

## Coverage of arbitrary invertible mixing that fixes u

Consider any rational invertible basis change on the three output values
`(u, output419, output421)` that fixes the value `u` exactly. Its matrix has
the block form

```text
F = [[1, 0],
     [v, A]],        A in GL(2,Q),  v in Q^2.
```

It factors exactly as

```text
F = diag(1,A) * [[1, 0],
                [A^-1*v, I2]].
```

The right factor is the two-shear family above. The left factor mixes only
dirty output rows419 and421 by an invertible matrix. It preserves the
rowspace of the complete dirty-output/hot-input block. Hence it cannot repair
the failure of the color-cut condition. This proves the same obstruction for
every invertible rational basis change on these three outputs that fixes `u`.

If these three channels pass through the same native map, this is the natural
entire commuting three-channel basis family fixing the protected value.
The obstruction itself does not require native-map equality: it applies to
the direct scalar targets irrespective of their later native feasibility.
It does not cover mixing another output into the family, changing `u`, or
letting one of the nine monochrome output caps become multicolor.
