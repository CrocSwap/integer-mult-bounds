# A forest echo can lose under two-epoch tariffs

## Contract

There are exactly three required rows, initially independent arbitrary
`a0,a1,a2` in `F2^w`, for any finite `w >= 1`. A fixed straight-line program
uses only `ADD(i,j): Ai ^= Aj`, with distinct `i,j` in `{0,1,2}`, and exactly
one complete call `P0: A0 ^= p`. The arbitrary value `p` comes from preserved
read-only sources disjoint from all three rows. The call separates the two
epochs. The endpoint must be `Ai = ai ^ p` for every row and every input.
There is no helper, free basis change, observation, COPY, CLEAR or adaptation.

The common call has declared complete price one. Fix a real `M >= 3`.
Before the call, ADD(1,0) and ADD(2,1) cost one. After the call, ADD(2,0)
and ADD(1,2) cost one. Every other ADD costs M in its respective epoch.
These are hypotheses about complete stationary prices within each epoch.
No actual physical tariff matrix is supplied.

A *same-tree echo* chooses an outward spanning tree rooted at row zero,
executes each tree ADD once in children-before-parents order before P0,
then executes the literal reverse after P0. This is the single-root
construction in Ross Richardson's PR3121 with its prices changed across
the call. The word, target and dirty-output contract retain their meanings.

## Theorem

For every finite `w >= 1` and real `M >= 3`, the unrestricted optimum is
exactly **7**, including P0. Every same-tree echo costs exactly **2M+3**.
At M=3 the sharp comparison is 7 versus 9. In this changed price contract,
the ratio of the best same-tree echo to the unrestricted optimum is
unbounded as M grows.

This is a scoped written proof. It is not a counterexample to PR3121,
whose prices are stationary across the entire word.

## Attainment

The chronological program is

```text
ADD(2,1), ADD(1,0), ADD(2,1),
P0,
ADD(1,2), ADD(2,0), ADD(1,2).
```

Preparation maps `(a0,a1,a2)` to `(a0,a1+a0,a2+a0)`.
After P0 the rows are `(a0+p,a1+a0,a2+a0)`. The last three ADDs give
`(a0+p,a1+p,a2+p)` exactly. All six ADDs have price one, so the total is
seven. The read-only sources are preserved by the complete P0 contract.
There is no hidden scratch or uncompute. The proof applies componentwise
at every positive row width.

Both three-ADD words realize the same involution

```text
S = [1 0 0]
    [1 1 0]
    [1 0 1].
```

They are different spellings of S. Using the literal reverse of the
preparation would also be algebraically correct, but its three post-call
ADDs would each cost M. The alternative spelling is what changes the bill.
The elementary three-ADD identity itself is classical and is not claimed
as new. The contribution is the complete two-epoch optimum and its exact
separation from the forest echo.

## Lower bound for all words

First, every successful word has at least four ADDs. Rows one and two
must each be an ADD destination, since P0 does not directly change them
and their final values depend on p. Neither row can be a destination
exactly once. Project the state onto the three original dirt symbols,
equivalently set p=0. Every prefix dirt matrix is invertible. Before the
unique destination occurrence on row i its dirt row is `e_i`. The source
dirt row at that occurrence is nonzero, so afterward row i differs from
`e_i`. No later gate changes it. It cannot end at `e_i`, a contradiction.
Thus each of rows one and two is an ADD destination at least twice.
This is the one-row dirt argument credited to PR3063 and PR3121.

If any ADD has price M, the ADD bill is at least `M+3 >= 6`, by that
four-ADD floor. This already gives a total of at least seven.

It remains to consider words using only the two cheap ADDs in each
epoch. Write A for the preparation dirt matrix and B for the post-call
dirt matrix. Cheap preparation has the form

```text
A = [1 0 0]
    [a 1 0]
    [c b 1],       a,b,c in F2.
```

Cheap post-call computation has the form

```text
B = [1 0 0]
    [v 1 u]
    [t 0 1],       u,v,t in F2.
```

The required dirt endpoint is `BA=I`. Comparing the third row gives
`b=0` and `t=c`. Comparing the second gives `u=0` and `v=a`.
The p coefficient is `B e0=(1,v,t)^T`. It must be `(1,1,1)^T`, so
`a=c=v=t=1`. Consequently `A=B=S`.

No word of at most two cheap preparation ADDs gives S. Repeating one
generator twice gives I. Using each once leaves a nonzero coefficient
of a1 in row two, while S has zero there. A single generator also
cannot give S. Interchanging rows one and two gives the same argument
for the post-call cheap alphabet. Each epoch therefore needs at least
three cheap ADDs. The total ADD bill is at least six, completing the
lower bound.

This proves the all-word and all-width statement without relying on
the finite shortest-path computations.

## Exact forest bill

There are exactly three outward spanning trees rooted at zero:

```text
{0->1, 0->2}, {0->1, 1->2}, {0->2, 2->1}.
```

Every edge appearing here has combined before-plus-after price `M+1`.
Each tree has two edges, so its ADD bill is `2M+2` and its complete bill
is `2M+3`. Dividing by seven proves the unbounded ratio.

For one required row the oracle alone is optimal. For two required
rows, ADD(1,0) must occur at least once before the oracle to make the
preparation send `(1,1)^T` to `e0`, and at least once after the oracle
to deliver p to row one. The usual one-edge echo attains the sum of
these two prices. Thus three rows are the smallest size for this
separation in the exactly-one-P0, two-epoch XOR contract.

## Finite independent evidence

The primary verifier enumerates GL(3,2), the 24 permissible cut maps,
and shortest paths in both epoch-specific Cayley graphs. It verifies
both attaining path costs and every Bellman inequality, so a faulty
distance search cannot silently publish a larger optimum. At M=3 the
minimum combined ADD distance is six. Values M=1,2,6,11 are controls and
corroboration, not extra theorem claims. All three trees are enumerated.
The literal word also runs on every input tuple at widths one through
three, including arbitrary independent dirt and common values.

The separate checker uses the complete 16-entry Boolean truth tables
for three dirt bits and one common bit. Its graph contains the before
and after epochs and the single paid P0 transition. It exhausts all
1,344 reachable states and 8,232 transitions, independently obtaining
total seven. It imports neither the primary verifier nor predecessor
executables. These are two implementations by the same contributor,
not independent human review or formal proof-kernel acceptance.

## Boundary of the conclusion

The stationary theorem and its cut lower bounds are retained. Their
conversion to a repeated cheapest tree cannot be made with the
naive combined edge prices in this changed model. A valid unrestricted
optimizer must allow different algebraic realizations of the same cut
matrix on the two sides. This example still has one fixed source value
and does not answer the separate changing-source scheduling problem.

Physical routing, source access, frames, precision, ownership, head
return and restoration must all be included before any actual ADD
can be assigned these complete prices. The example supplies no such
caller. No selected construction, recursive rank profile, supplier
admission, new kappa or multiplication theorem follows.
