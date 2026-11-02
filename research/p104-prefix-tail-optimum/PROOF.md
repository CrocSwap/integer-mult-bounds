# Exact optimum with the prefix paths fixed

## 1. Contract and theorem

Use Adam Gall's PR1940 supplied-copy boundary and its exact
`SCHEDULE.json`. A parent edge `[S,k]` requires a centre-k read at the
frame spanned by survivor labels in the eight-bit mask S. All survivor
labels are independent, so inclusion of these frames is inclusion of
masks and their dimensions are popcounts. These geometric and decoder
facts are inherited premises, not newly audited here.

Let D_k be the distinct masks assigned to centre k by the parent edges.
A cover partitions each D_k into nonempty chains under strict inclusion.
It has 32 chains in total. Each chain carries that one centre's exact
value, enters at the singleton `{k}`, visits its chain masks, and exits at
the full frame V of dimension 9. A frame increment of rank r costs f(r),
and f(0)=0. No centre mixing, redrop, changed target order or changed
entry/exit contract is allowed. All direct strict inclusion links are
permitted, not just consecutive links in the published cover.

**Theorem.** For every concave f on integer ranks 0,...,8, the minimum
delivery-tail cost over these covers is

```text
85 f(1) + 17 f(2) + 19 f(3) + 20 f(4).
```

The minimum is attained by PR1940's published cover. Concavity here means
that f(r)-f(r-1) is nonincreasing. Nondecreasing tariffs are included, but
that additional restriction is unnecessary for the proof.

The attaining construction and its 32-path count are credited to PR1940
and Ali Romman's PR1125 respectively. The new assertion is optimality
over the complete fixed-path chain-assignment class.

## 2. Chain cardinalities and chronology

The per-centre numbers of rank-four masks are

```text
centre             0  1  2  3  4  5  6  7
rank-four masks    5  3  4  4  4  3  4  5
```

The checker enumerates these masks and stores them as antichain witnesses.
A chain can contain at most one of them. Their counts sum to 32 and the
published cover attains every count. Therefore every cover with 32 chains
must have exactly the displayed number c_k at each centre. This is the
fixed-prefix specialization of the credited rank-four antichain argument.

Each target's successive prefix masks strictly increase in dimension.
Every strict link in a carrier chain does too. Process equal-frame reads
together and otherwise order by increasing dimension, breaking ties by
mask. That respects both target and carrier dependencies. Thus changing
the chain assignment within this class introduces no chronological cycle.
The target moves and scalar reads are unchanged by the assignment.

Every chain starts in dimension 1 and ends in dimension 9, hence its
increment ranks sum to 8. Every cover therefore has rank mass
32*8=256. This equality is essential for the linear term in section 5.

## 3. A matching formulation with every legal link

Fix a centre, put n=|D_k| and make a left and right vertex for every mask
u in D_k. Include an edge u_L to v_R exactly when u is a proper subset of
v. A matching of cardinality n-c_k is precisely a partition into c_k
chains: a matched edge declares an immediate successor. Each mask has
at most one predecessor and successor. Strict inclusion forbids cycles.
Conversely, consecutive pairs in any cover give such a matching.

Write a=|u| and b=|v|. Starting with each node on a separate chain gives
the constant cost

```text
B_f = sum_(u in D_k) [f(|u|-1) + f(9-|u|)].
```

Joining u to v replaces u's exit and v's entry by one direct increment.
Give the matching edge cost

```text
w_f(u,v) = f(b-a) - f(9-a) - f(b-1).
```

Then a cover's price equals B_f plus the sum of its matching-edge costs.
This includes every entry and exit increment, including zero increments
at singleton read frames. There is no charge omission at chain endpoints.

Add a source with unit-capacity zero-cost arcs to all left vertices and
unit-capacity zero-cost arcs from all right vertices to a sink. A matching
is an integral source/sink flow of the prescribed value n-c_k.

## 4. Exact optimality potentials

For j=1,...,7 use the hinge tariff h_j(r)=min(r,j). Form the residual
network at the published matching. An unused arc remains forward with
its original cost; a used arc is reversed and its cost negated. This
applies to the source/left and right/sink arcs too, not only links.

For every centre and hinge the certificate gives one integer potential
pi on all 2n+2 vertices. The checker enumerates every residual arc a to b
and verifies

```text
cost(a,b) + pi(a) - pi(b) >= 0.
```

Every residual circulation then has nonnegative cost, since potentials
telescope. The difference from the published flow to any other feasible
flow of the same value is a sum of residual circulations. Thus no other
matching, and hence no other c_k-chain cover, has a lower hinge price.
This argument requires no trust in an optimization status or numerical
tolerance. The optional certificate generator only finds the integer
potentials; acceptance is the direct inequality check.

There are 56 witnesses and 3,752 inequalities. The published cover's
total hinge minima, including all centres, are

```text
j               1    2    3    4    5    6    7    8
minimum       141  197  236  256  256  256  256  256
```

The j=8 column is the common linear rank mass. The source cover's
histogram gives those values exactly. No global enumeration of chain
covers is asserted; the dual inequalities cover every matching through
the circulation argument.

## 5. All concave tariffs

Put Delta_r=f(r)-f(r-1) and d_j=Delta_j-Delta_(j+1). Discrete concavity
is exactly d_j>=0 for j=1,...,7. Directly comparing first differences
gives the identity, for r=0,...,8,

```text
f(r) = Delta_8*r + sum_(j=1)^7 d_j*min(r,j).
```

The linear rank sum is the same for every cover. The published cover
minimizes every hinge separately by section 4. Taking their nonnegative
linear combination proves the theorem. In particular, the restriction
of r^s to these integer ranks is concave for every 0<s<1, so the exact
minimum throughout that entire power interval is

```text
85 + 17*2^s + 19*3^s + 20*4^s.
```

No root search, sampled exponent, transcendental approximation or
unproved extrapolation between tariffs enters this conclusion.

## 6. Consequence and limits

Within PR1940's fixed target prefix paths and 32-chain supplied-copy
contract, there is no delivery-tail saving from chain reassignment.
The same conclusion holds after adding the unchanged target-tail and
scalar-read charges. This closes that bounded optimization route.

Changing the prefix paths, chain count, term basis, copying/restoration
contract or entry/exit frames changes the optimization problem. Such
changes require a new complete bill. In particular, exact formation of
the 24 extra supplied centre copies remains unresolved here, and no
arbitrary-dirty restoration, native all-column realization, side-correction
compatibility, physical compiler, precision/tape or analytic recovery
obligation is discharged. The result is a scoped proof with a finite
certificate, not a new supplier or complete multiplication theorem.
