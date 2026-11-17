# An exact two-coordinate reduction for A7+A1 side information

This is a scoped written proof with finite exact geometric premises. It does
not determine the unrestricted row-shift optimum or supply a physical caller.

## Inherited model

Use the 120 unoriented E8 root lines, represented by doubled vectors v_i in
Z^8. They are the vectors with two entries in {2,-2}, or eight entries in
{1,-1} with even minus parity, up to sign. Orient the first nonzero entry
positively. The nine reader supports are

```text
Y_k = {i : 8 v_ik != sum_j v_ij},  k = 0,...,7,
Y_8 = {i : sum_j v_ij != 0}.
```

The complete decoder row family has first eight coefficients v_ik+t_i and
last coefficient sum_j v_ij/4. Its row supports are X_k. These definitions
and their binding to joaqcoo's #1224 frame are inherited from adamgall's
`a7-a1-decoder-floor`; that source binding is a cited premise.

Each input u_i is an independent d-bit vector, d>=1. Set B_ii=1 and, for
i!=j, B_ij=1 exactly when v_i and v_j are orthogonal. A term k sends a
deterministic zero-error message depending only on u restricted to X_k.
Every reader j in Y_k must recover sum_(i in X_k) B_ij u_i. The reader
knows all inputs on lines orthogonal to its own. Costs are log2 of message
range size, added separately over terms. These are exactly Matarener
#5299's support and side-information conventions, not a physical COPY bill.

For an undirected graph G, write beta_d(G) for the minimum log2 range size
of an index code on independent d-bit vertex inputs, with neighbors as
side information and each vertex demanding its own input. This uses no
ceiling on the logarithm. The finite optimum exists, since messages induce
a coloring of a finite confusion graph.

Matarener's induced-demand reduction identifies a term with the graph on
S_k=X_k intersect Y_k, with orthogonality edges. To see the upper direction
explicitly, encode only the inputs in S_k. Reader j in S_k recovers u_j and
already knows every other contributing input. Reader j in Y_k outside X_k
already knows its entire term value. For a lower bound fix inputs outside
the induced demand graph to zero.

## The theorem

Fix distinct coordinates a,b in {0,...,7}. Allow every row independently
to choose t_i in {-v_ia,-v_ib}. Let C_d(a,b) be the minimum complete
nine-term message cost over all these choices and all admissible codes.
Then, for every positive d,

```text
C_d(a,b) = 64d + beta_d(H44),
7d <= beta_d(H44) <= 8d,
71d <= C_d(a,b) <= 72d.
```

No equality to either numerical endpoint is asserted. All 28 coordinate
pairs give the same graph H44. It has the following standalone definition.
There are vertices A_j,B_j for j=0,...,5, and one vertex S for every odd
subset S of {0,...,5}. Edges are exactly

- A_j B_k for j!=k;
- A_j S for j in S, and B_j S for j not in S;
- S T for |S symmetric-difference T|=4.

There are no A-A or B-B edges. The verifier checks this description against
all 946 unordered pairs of the 44 root vertices.

## Seven protected terms

By coordinate symmetry take a=0,b=1. For k=2,...,7 define

```text
F_k = {i in Y_k : v_ik differs from both v_i0 and v_i1}.
F_8 = Y_8.
```

Every F_k is contained in S_k for every permitted row choice. Each mutable
F_k has 29 vertices, while F_8 has 57. Each contains an induced Petersen
graph and four further vertices isolated from that Petersen graph and
from one another. `CERTIFICATE.json` supplies seven explicit witnesses;
the verifier checks every induced edge and nonedge and both local row
choices. These are new protected cores, rather than the predecessor's
two complete shifted witnesses.

The Petersen graph has broadcast rate 5, by Blasiak, Kleinberg and
Lubetzky, [*Index Coding via Linear Programming*, Fact 5.6(1)](https://www.cs.cornell.edu/~ablasiak/papers/bkl-beta.pdf).
Consequently every d-bit code has log2 range at least 5d. Otherwise
repeating that finite code would give an asymptotic rate below 5.

Adding an isolated vertex adds exactly d to beta_d. For the lower bound,
its 2^d possible values require disjoint message sets, since its receiver
has no side information about the other inputs. Within each such fiber,
the messages still code the remaining graph, with the isolated value
fixed. Each fiber therefore has at least 2^beta_d(G) messages. Sending
the isolated input separately attains the matching upper bound.

Thus each protected term costs at least 9d, for a total of 63d. This uses
the classical Petersen rate and isolated-vertex argument already used in
#5299, applied to the newly certified cores.

## Combining the two remaining messages

Define the common graph Q by its vertex set

```text
V(Q) = {i : v_i0 != v_i1} intersect Y_0 intersect Y_1.
```

It has 45 vertices. Each of its vertices lies in exactly one of S_0,S_1:
one of v_i0+t_i and v_i1+t_i vanishes, and the other does not. Restrict all
inputs outside V(Q) to zero. The two term messages now depend only on
their respective parts of this partition. Concatenate them. Every vertex
of Q can use its corresponding decoder and its orthogonal side information,
so this is a valid code for Q. Its range size is at most the product of
the two individual range sizes. Therefore their summed cost is at least
beta_d(Q), giving

```text
C_d(0,1) >= 63d + beta_d(Q).
```

No claim of additivity over a partition of a general graph is used here.
The inequality follows from the actual concatenated code.

## A row choice attaining the reduction

Choose t_i by the following rule:

```text
if v_i0 = v_i1 or i is outside Y_1, choose -v_i0;
otherwise choose -v_i1.
```

Then S_0=V(Q) and S_1 is empty. For the only nontrivial case, i in Y_1
with unequal coordinates, column 1 vanishes and column 0 is nonzero;
it is a demand precisely when i also lies in Y_0. Inputs outside a demand
set cause no additional message cost because of the inherited side
information contract. Thus an optimal code for Q implements term zero,
and term one needs no message.

The other seven demand graphs each have an explicit binary fitting code
of rank nine. The verifier constructs each matrix M with diagonal one,
one on orthogonality edges and zero elsewhere, performs exact binary
elimination, and checks literal decoding on every source basis column.
Sending a row basis of M costs 9d. Since the protected cores also force
9d, all seven terms are exact at this row choice. Hence

```text
C_d(0,1) = 63d + beta_d(Q).
```

## Removing the isolated vertex

In doubled root coordinates Q consists exactly of

```text
z = (2,-2,0,0,0,0,0,0),
A_j = 2e_0 + 2e_(j+2),   B_j = 2e_1 + 2e_(j+2),
(1,-1,s_0,...,s_5), with an odd number of negative s_j.
```

The vertex z is isolated. Under the correspondence S={j:s_j=-1}, the
remaining orthogonality graph is exactly H44 as defined above. Therefore
beta_d(Q)=d+beta_d(H44), proving the exact reduction.

The certificate contains eight pairwise nonorthogonal vertices of Q,
including z. Deleting z gives an independent seven-set in H44, so
beta_d(H44)>=7d. Its displayed binary fitting matrix has rank eight,
and the verifier supplies an actual encoder/decoder, so beta_d(H44)<=8d.
Neither assertion says that rank eight is the optimal linear code.

Permuting the eight coordinates preserves dot products, the reader
supports and the two-coordinate family. Reorienting a moved root merely
multiplies its coefficients and cancellation shift by the same sign.
The result therefore holds for every pair a,b. The finite checker
additionally transports the seven protected certificates to all 28 pairs.

## What remains open

The exact nonlinear value beta_d(H44) is unresolved. In particular this
proof neither establishes the 72d floor for this whole subfamily nor
constructs a code below it. Allowing three cancellation coordinates,
generic shifts, changed normals, joint billing, or physical routing is
outside the theorem. Universal d-coverage comes from the written coding
argument, not extrapolation from finite payload tests. Independent human
and formal proof-kernel review are unclaimed.
