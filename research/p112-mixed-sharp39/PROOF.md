# A mixed 5,5,6 counterexample at common cut 40

Let P be the 112 nonframe E8 root lines in the pinned `geometry.py`, with its
leading-one nine-bit labels. For a characteristic-zero field K let
`C = {(r_t dot h)_t : h in K^8}`. Binary support rank means the F2 rank of
the labels at nonzero coordinates. Let pi delete one coordinate set S.

**Proposition.** There is a set S of 40 coordinates and three rational residual
vectors q1,q2,q3 of binary support ranks 5,5,6 for which

```
dim_K(pi(C) intersect span_K(q1,q2,q3)) >= 2.
```

All data are integers, so the same example works over every characteristic-zero
field. The sufficient allowance 39 proved in pinned PR3278 is therefore sharp,
conditional on that predecessor's theorem. Its proof and receipt are retained
verbatim; the present replay does not re-prove its sufficient direction.

## Literal construction

Use these orthogonal doubled-root directions:

```
a = (0,0,0,0,0,2,-2,0)
b = (0,0,0,2,-2,0,0,0)
```

Their codeword union U has 84 live coordinates. Its projective fibers have
sizes 31,31,11,11. Each large fiber has lost two frame roots, unlike the
four-root punctures of PR3278's minimum-union planes.

In the fixed sorted P112 order, take the following disjoint supports:

```
A = [37,38,49,50,53,54,65,66,69,70,81,82]
B = [17,18,21,22,27,28,31,32,103,104,107,108]
D = [5,6,11,12,25,26,33,34,43,47,56,60,75,79,88,92,101,102,109,110]
```

A and B lie in a's axis fiber, where c_b is zero. D lies in b's axis fiber,
where c_a is zero. Their exact binary label ranks are 5,5,6. Define

```
S = U minus (A union B union D)
q1(t) = c_a(t) on A, zero elsewhere
q2(t) = c_a(t) on B, zero elsewhere
q3(t) = c_b(t) on D, zero elsewhere.
```

Since the support union has size 44, S has size 84-44=40. At each of the
72 retained coordinates the actual integer data satisfy

```
q1 + q2 = pi(c_a),    q3 = pi(c_b).
```

The codewords have disjoint nonempty retained supports. Their evaluation minor
at coordinates 5 and 17 is nonzero, of absolute value 16. Thus they remain
independent over K and belong to the piece span, proving the proposition.
`WITNESS.json` records all 112 entries of each piece and every cut index.
The replay checks these equations and ranks directly; feasible cardinality
counts or abstract set covers alone would not prove the statement.

## Evidence and limits

The primary checker uses the source-authenticated geometry, exact integer
equations and nine-pivot binary elimination. The separate checker reconstructs
roots by coordinate type, recovers simple-root coefficients through an integral
recurrence, and checks span sizes 32,32,64. All matrices and sets are finite.
No optimization, float tolerance, full flat census or scientific Git dependency
is needed to check the counterexample.

PR3278 supplies the sufficient theorem at 39 and explicitly records inherited
capacity and Weyl/chamber dependencies. Hash authentication does not establish
those mathematical dependencies. The new obstruction at 40 stands separately.
PR3283's related uniform-rank-five witness at 48 uses different data and ranks;
its conclusion is not needed here. Concurrent A2 rank-six joint32 and D6
four-puncture capacity18 proofs are unused.

This is a shortening counterexample. It does not supply an actual caller,
a full C5 factorization, a complete decoder, a physical/native implementation,
restoration or consumer costs, a supplier or a new multiplication exponent.
No human or proof-kernel approval is claimed. Credit the pinned PR3278
predecessors, PR3283, DreamingOfClouds/PR3154 and the retained E8/P112 lineage.
