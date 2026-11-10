# Sharp three-axis reversible grid rounding

Let F = C tensor C tensor C on L = Z[i]^8, with the same C as PR6534.
The grid spacing is h. Code uses h = 1. This is an indexed word algorithm.
It does not provide a Boolean or tape tariff, native admission, or a kappa gain.

## A finite quotient gives an all-input inverse

Put M = 4F. For coordinates j,k in {0,...,7}, its complex entry is
`(-1+i) (-i)^popcount(j xor k)`. The checker constructs the equivalent
16 by 16 real integer matrix. It checks M* M = 16 I, M^2 = 16 P and both
complex sum rows, where P exchanges all three coordinate bits. These exact
finite matrix identities prove the corresponding operator identities.

Let K = L intersect F^-1 L. Its class key is Mx modulo 4. The checker builds
64 distinct keys and proves closure under every integer basis generator.
The zero key is present. Thus these are exactly all keys, not just sampled
keys. As F^2 = P preserves L, F(K) = K. The inverse has the same K.

For each class t, choose one centre c_t in that class. Define

```
G_s(x) = F^s (x-c_t) + c_t,       s in {-1,1}.
```

Since F(K) = K, G_s(x) is integral and remains in class t. The opposite sign
therefore selects the same centre and returns x exactly. Also G_s^4 = I.
The complex sum is unchanged because F fixes that sum. The error is constant
on a class: `(I-F^s)c_t`. Both signs have the same squared error by unitarity.
The centre values and the offsets for both signs are in the exact receipt.

## Complete centre optimization and its precise scope

This family fixes each coset and uses one centre per coset. It does not include
coset permutations, nonaffine rules, state-dependent centres or extra history.
For this family the sharp minimum possible uniform squared error is 5 h^2.
Here is a complete, finite proof of the centre search radius.

The Walsh basis gives eigenvalues 1,i,-1,-i for F, with multiplicities 1,3,3,1.
The eigenspace at 1 consists of constant complex vectors. Hence, if mu is the
mean of the eight complex entries,

```
||(I-F)c||^2 >= 2 ||c-mu||^2.
```

Subtract a constant Gaussian integer from c so each component of the new mean
lies in [-1/2,1/2]. This changes neither its coset nor its error. The resulting
integer vector satisfies

```
||c'||^2 = ||c-mu||^2 + 8 |mu-rounded(mu)|^2
         <= ||(I-F)c||^2 / 2 + 4.
```

The table supplies error at most 5 in every class. Any centre that can improve
or attain this bound therefore has an equivalent representative with squared
integer norm at most 6.5, hence at most 6. Enumerating all such real integer
16-vectors is exhaustive for every class minimum. No larger coordinate than
2 can occur in that ball.

`optimize.py` enumerates all 700,833 vectors in that ball. A separate generating
function, the sum of coefficients through degree 6 in `(1+2t+2t^4)^16`, checks
the census size. The minima, in squared-error units, are:

| Classes | Minimum |
| --- | --- |
| 1 | 0 |
| 32 | 5/2 |
| 15 | 4 |
| 16 | 5 |

The checker regenerates every centre and runtime byte. The sphere argument
and exhaustive enumeration prove the scoped optimum. They do not claim a
global lower bound for every reversible grid algorithm. The search uses no
optional solver and has no heuristic stop or omitted branches.

## Permuting cosets reaches the global uniform grid optimum

The fixed-coset restriction leaves useful slack. Keep the certified centres,
but match input classes t to output classes sigma(t). An edge is allowed when
the two centres have equal complex sums and
`||c_sigma(t) - F c_t||^2 <= 4`. Require zero to match only zero. The checker
uses a complete augmenting-path matching and obtains a permutation of all
64 classes. It checks every edge, the sum condition and bijectivity directly.
The resulting permutation also satisfies sigma^4 = I; this is verified, not
assumed for an arbitrary matching.

Define the forward map by `G(x) = F(x-c_t) + c_sigma(t)`. The output class is
sigma(t). For an input of class s, its inverse is
`F^-1(x-c_s) + c_sigma^-1(s)`. These formulas prove an exact inverse and exact
complex sum for every input. Four forward steps telescope to F^4(x-c_t)+c_t,
so this particular G also has fourth power one. Zero is fixed. The inverse
error equals the forward error on the matched edge, by unitarity. Both signs
therefore have uniform error at most 2h.

This bound is globally sharp among all integer-output maps for this ideal
operator, even without an inverse or sum requirement. Take the real vector
`c = (-1,-1,-1,-1,0,0,0,0)`. Every one of the sixteen real components of Fc
is a half-integer. Every integer output therefore has squared error at least
16/4 = 4. The constructed map attains that uniform lower bound. This is a
minimax statement; it does not say that each individual output is nearest.
The distinction matters at e0, as the next section shows.

## Why nearest-only fusion cannot continue

For x = e0, every real component of Fx is plus or minus 1/4. Its unique nearest
Gaussian integer vector is zero. Zero also has unique nearest output zero.
Thus every pointwise nearest rule for this three-axis map fails injectivity.
This exact two-input obstruction explains the changed approximation contract.
The present map is reversible and sum-preserving, but is not pointwise nearest.
No global phase-covariance or ideal-square rewrite is promised.

## Literal work and range

The runtime forms Mx once by input phases, a three-stage Walsh transform,
output phases and multiplication by -1 plus or minus i. It takes the sixteen
residues modulo four, finds their class in the sorted table, adds that class's
signed offset, and performs sixteen exact quarter shifts. For the inverse,
P reverses the eight complex pairs in the residue key, since F^-1 = PF. Its
offset uses the inverse coset permutation; it does not reuse a forward centre.
No search for a centre occurs during a data call.

One block uses 80 real additions or subtractions, 28 real negations, eight
component exchanges, sixteen quarter shifts and 144 checked values. It reads
sixteen residues and sixteen signed offset bytes, and checks sixteen exact
divisibilities. The packed runtime has 64 rows of sixteen key bytes and
32 offset bytes: 3,072 bytes for both signs. Binary search needs at most seven
key comparisons plus its equality check; each can inspect sixteen bytes.
Index work, data movement, format checks, Python objects and table access are
additional. The payload-byte figure is not a Python memory measurement or a
physical storage bound.

With input components bounded by A, the Walsh intermediates are bounded by 8A
and Mx by 16A. Each stored offset has absolute value at most 8, since its
squared norm is at most 64 and its integral components are checked in the table.
Thus a signed word range strictly above 16A+8 suffices. Actual values are
checked. Overflow is rejected, never saturated or wrapped.

For comparison, three retained single-axis stages use 120 additions on eight
entries; a PR6534 pair plus one stage uses 80. The new block also uses 80, and
changes 24 one-bit shifts into sixteen two-bit shifts, but adds the class table.
There is no overall runtime or physical-cost speedup claim.

## Minimum group error and complete ports

On a field of N entries, each group of one, two or three axes has error at
most E0 = h sqrt(N/2). Unitarity gives the sum of these group bounds for the
whole call. Each group preserves every spectator-fibre sum. Its inverse
reverses the literal group order and signs. The resulting bound is

```
||rounded_call(x) - ideal_call(x)||_2 <= ceil(f/3) h sqrt(N/2).
```

The previous two-axis grouping gives ceil(f/2) times the same factor. Neither
statement asserts that a long call attains the sum of its local bounds.
For f=3, the new eight-point bound is 2h, and the old pair-plus-singleton
certificate is 4h. The new local uniform value was proved optimal above.

Among partitions into groups of sizes one, two and three, at least ceil(f/3)
groups are needed. The chosen plan attains this. Among these minimum-group
plans it also minimizes data additions. A singleton or pair costs 5N additions;
a triple costs 10N. With g groups, the triple count is f-2g plus the singleton
count. For f>=2 our plan has no singletons, so it minimizes that count. Use
triples, except a remainder one becomes two pairs and a remainder two becomes
one pair. The case f=1 uses one singleton. The checker compares every partition
through f=128. This optimizes the error certificate first and data additions
second, not physical time, shifts or table traffic.

The retained two-call and three-call ports use exact monomials and the mix
P+2Q, whose norm is at most three. If E is the completed-call bound, the same
literal-order argument as PR6534 bounds either output bank by 5E. Reversing
the full port cancels every bijective call, monomial and mix, and returns both
dirty banks. The checker tests every paid actual-input cut, full ports through
f=3 and calls through f=4 against the retained independent matrix oracle.
This does not establish a full selected caller or a physical cleanup protocol.
