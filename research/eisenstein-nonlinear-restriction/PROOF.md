# Coordinate faces bound the possible nonlinear saving

This contribution is produced by Nick Petalas. New work is Apache-2.0.

## Model and credited premise

Use Michael Fischler's [PR814 fixed-support nonlinear model](../eisenstein-message-copy-bound/PROOF.md).
There are forty Eisenstein E8 ports. Port t holds b_t independent binary
coordinates. Put N=sum_t b_t. Each fixed-width message Y_j=f_j(X_Aj) has
q_j bits, fixed source support A_j and fixed reader support R_j. Receiver t
recovers all its input bits on every input, using its received messages and
the inputs of ports orthogonal to t. Decoders need not be linear.

The abstract charge is C=sum_j q_j c(R_j,A_j), where c is half the rational
pairing rank of the two line-generated subspaces. Charges add per bit.
This is a model premise, not a proved physical implementation price.

We invoke Jose Manuel's [PR2017 fixed-support block-linear corollary](../eisenstein-reduction-copy-floor/README.md#fixed-support-block-linear-corollary).
If all messages are binary linear in the independent input coordinates,
then C is at least the total demand. This includes arbitrary unequal
demands, zero demands, arbitrary fixed supports, and nonlinear decoders.
An affine message has the same conclusion after its known constant is
subtracted at each reader. The good-reduction and Schur-rank proof are
credited premises; this package does not re-prove or replay them.

## The new restriction lemma

Fix a set S of h individual input coordinates to one specified assignment a.
Suppose that, on this coordinate face, every output bit of every message
is affine in the N-h unfixed coordinates. Then

    C >= N-h.                                                    (1)

Proof. The unfixed coordinates still range independently over their full
binary product. Each port now demands exactly its own unfixed coordinates.
Every old decoder remains correct on the face. Its fixed coordinates are
known constants; its unfixed side information still comes only from
orthogonal ports. Subtract the known affine constants of the messages.
This gives a fixed-support block-linear protocol for total demand N-h.
It may retain the original supports and widths. Apply the credited
PR2017 theorem directly to obtain (1). Alternatively, remove inactive
sources and readers. Restricting the bilinear pairing to smaller spans
cannot increase its rank, so that version has charge at most the original
C and gives the same inequality. This proves the lemma.

Let h_* be the minimum number of coordinates fixed on any such affine
face, allowing arbitrary specified zero or one values. A face always
exists, since fixing all N coordinates makes every message constant. Thus

    C >= N-h_*.                                                  (2)

The face is a restriction used to prove an exact-code lower bound.
It is not an input-dependent free routing header. No execution is given
extra information about a random input. Arbitrary affine subspaces that
couple different ports are excluded: they need not preserve the product
of independent per-port demands required by the credited theorem.

## An exact monomial hitting-set corollary

Represent each transmitted bit by its unique squarefree algebraic normal
form over F2, in all N individual input coordinates. Form a hypergraph E
whose edges are all monomial supports of degree at least two appearing
in at least one output bit. Let tau(E) be its minimum vertex-cover size.
Here a vertex cover meets every edge, and the empty hypergraph has tau=0.

Setting every variable in a cover S to zero removes every nonlinear
monomial. All surviving terms are affine. Conversely, after fixing S to
zero, every monomial disjoint from S survives unchanged, and distinct
surviving monomials cannot cancel. Hence zero fixing makes all messages
affine exactly when S meets every edge. The exact minimum zero-fixing
number is tau(E). In particular h_*<=tau(E), and

    C >= N-tau(E).                                               (3)

For quadratic messages, E is the ordinary interaction graph across all
output bits, so its vertex-cover number supplies the bound.
The minimum is not a claim about computing vertex cover in polynomial time.
The executable searches only the bounded domains stated in its README.

Nonzero faces can improve (3). For one output with ANF

    x0*x1 + x0*x2 + x1*x2 + x0*x1*x2,

the zero-face cover number is two, since all three edges of a triangle
occur. Fixing x2=1 instead leaves x0+x1, so h_*=1. The function is nonlinear
on the full cube, making this minimum exact. This distinguishes (2) from
the zero-face corollary.

## Meaning for a cheaper nonlinear proposal

Any proposed exact code with C<=N-d must satisfy h_*>=d and tau(E)>=d.
For equal b-bit demands, N=40b. A proposed C<=31b therefore needs both
parameters at least 9b. The number 31 is a conditional target, not an
attained charge. It is motivated by Maximooch's historical PR1794 format
screen, cited through PR2017; that screen is not replayed or assumed by
the restriction proof. The inherited unrestricted nonlinear floor of 22b remains
separate; combining it with (2) gives max(22b,40b-h_*).

These inequalities do not prove a nonlinear code with C<N, or sharpness
of (1) for any positive h. A nonlinear encoder can have no cost advantage.
The new fixture illustrates this: on an orthogonal four-frame, send each
of the first three input bits directly to its owner and send
x3+x0*x1*x2 to the fourth owner. The fourth owner knows the first three
inputs as permitted orthogonal side information. Each message has pairing
price one. Add the other thirty-six direct singleton messages. The full
code costs forty, has h_*=tau=1, and the new necessary floor is thirty-nine.
The verifier checks the sixteen frame inputs and the separate direct-bit
components; the written product decomposition covers all forty inputs.

## Limits and predecessor credit

The result requires deterministic zero-error decoding, independent product
inputs, fixed supports and widths, permitted orthogonal side information,
and additive per-bit pairing prices. It does not cover errors, correlated
demands, adaptive or interactive messages, a private free header, or shared
physical pricing. It supplies no native circuit, supplier admission, new
kappa, or complete multiplication theorem. The all-width statement is an
informal proof with finite corroboration; formal-kernel and independent
human review are unclaimed.

Credit Michael Fischler for the nonlinear model, Jose Manuel for the
linear floor, Jonathan Lam and Joel Pulikkan / GamingPuzzled for the
geometry and original pairing-cost model, and ywz65 for the distinct
adaptive-affine public-broadcast theorem in PR2607. That theorem requires
affine queries at every adaptive node; here the original fixed messages
may be genuinely nonlinear. The new step is the coordinate-face
restriction and the resulting quantified nonlinear-dependence obstruction.
