# A linear error floor for rounded inverse oracles

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written proof with exact finite corroboration.

## Interface and theorem

Use the maximum complex-coordinate norm. Write D_p for the closed complex
unit disk intersected with 2^-p Z[i]. The numerical contract is Hanson Sun's
PR1430: p>100, h=2^-p, eta=ph/3, a linear E with norm at most 21/50,
and a deterministic T:D_p^s -> D_p^s satisfying

```text
||T(z)-Ez|| < eta  for every z in D_p^s.
```

An integer 1<=k<=p must satisfy ||E^k||<=h. The task is to approximate
`(I+E)^(-1)u/2` for u in D_p^s. In the oracle model here, E is hidden.
The algorithm receives p,k,u, the norm/error promises and access to T.
It receives no other E-dependent information. It may make any number of
valid adaptive queries, or even inspect the entire common function T.

For every integer p>100, there are two admissible entrywise nonnegative
two-coordinate operators E_- and E_+, with k=p and the same odd,
zero-preserving oracle T, for which every deterministic algorithm has error
greater than `(4/9)ph` on at least one instance. The same lower bound holds
for worst-case expected error of randomized algorithms. No randomized
algorithm can have success probability greater than 1/2 on both instances
at any error radius less than the two-instance radius R_p below.

Combined with PR1430's cited `<ph` Horner upper bound, the optimal worst-case
error order from this contract alone is Theta(ph). The exact minimax constant
for the entire contract class is not asserted.

## One common rounded oracle

Let S swap the two coordinates and put

```text
alpha = 2/5,  delta = (p/3-1)h,
E_- = (alpha-delta)S,  E_+ = (alpha+delta)S.
```

For z=h(n+im), let Q(z) be h times the nearest Gaussian integer to
`(2n/5)+i(2m/5)`. There are no ties, since the denominators are odd.
Define T(z_0,z_1)=(Q(z_1),Q(z_0)).

Each real rounding residual is at most 2h/5 in absolute value. Hence

```text
|Q(z)-alpha*z| <= (sqrt(8)/5)h < h.
```

Q, and therefore T, is odd and zero-preserving. For every disk input,
`|Q(z)| <= alpha+sqrt(8)h/5 < 1`, so T maps the entire required grid into
itself. For either hidden operator and every input in D_p^2,

```text
||T(z)-E_+ z|| < h+delta = eta,
||T(z)-E_- z|| < h+delta = eta.
```

This establishes the full-domain promise, rather than a sampled-query
promise. It also implies the retained bound
`||T(z)|| < (21/50)||z||+eta`.

For p>=101, `0<delta<1/50`. Indeed `(p/3-1)2^-p` decreases for p>4,
and its value at p=101 is less than 1/50. Thus

```text
0 < alpha-delta < alpha+delta < 21/50 < 1/2.
```

Both operators are entrywise nonnegative, and have norm alpha-delta and
alpha+delta respectively. They preserve coordinatewise positivity; no
positive-semidefinite hypothesis is used. Since S is an isometry,
`||E_+^p||=(alpha+delta)^p<h`, and the same holds for E_-.
Choosing k=p therefore supplies the required tail premise for both.

## Separated exact inverse answers

Choose the common input u=(1,-1), which belongs to D_p^2 and satisfies
Su=-u. Put a=1-alpha=3/5. The exact answers are

```text
y_- = u/[2(a+delta)],  y_+ = u/[2(a-delta)].
||y_+-y_-|| = delta/(a^2-delta^2) = 2R_p,
R_p = delta/[2(9/25-delta^2)].
```

All denominators are positive. In particular,

```text
R_p > (25/18)delta
    = (25p/54-25/18)h
    > (4p/9)h.
```

The last strict inequality is equivalent to p>75. This proves the stated
constant for every p>100. The two-instance radius also satisfies
`R_p/(ph) -> 25/54`; this is a property of these two instances, not a global
optimality claim.

## Indistinguishability

Every query has exactly the same response in the two instances. By induction,
an adaptive deterministic algorithm has the same transcript and the same
output v. The triangle inequality gives

```text
2R_p = ||y_+-y_-|| <= ||y_+-v||+||v-y_-||.
```

At least one error is at least R_p, hence strictly greater than `(4/9)ph`.
The midpoint of y_- and y_+ attains R_p on this two-instance decision problem.
The lower bound survives arbitrary query budgets because the whole function
T is identical, not just a selected finite transcript.

A randomized algorithm has the same output distribution on both instances.
Taking expectations in the triangle inequality proves the expected-error
statement, including infinite expectation. For any radius r<R_p, the two
closed success balls are disjoint. Their probabilities under that common
distribution sum to at most one, so at least one success probability is at
most 1/2. This does not assert which hidden instance is worse for a given
algorithm or random seed.

## What would evade this obstruction

The exact operator is not supplied separately. An algorithm that can inspect
an exact Gaussian formula, use E-dependent auxiliary data, refine the oracle
precision, or invoke a stronger relative-error law is outside this theorem.
The pair is not asserted to be an actual Gaussian resampling operator.
The result concerns the absolute numerical interface, not physical running
time, native calls, dirty restoration or a complete multiplication theorem.
No selected assumption or frontier value is changed. The universal statements
rest on this written proof. Finite checks do not enumerate all algorithms,
all grid points at p>100, or all precisions.
