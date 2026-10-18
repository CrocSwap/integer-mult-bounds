# Exact obstruction for a query added after U8 section A

## 1. Statement and class

Use the raw U8 word with decompressed SHA-256
`090fd574747fbf9628e70cb9beb792732914cfa52e1df147579fe4dbccc68c5a`.
The code reconstructs it from the pinned X4 archive and U8 recipe.
There are 112 source roles, 112 target roles, and 504 helper roles.

Choose any source index beta. Set its source value to zero and omit its target
output. The changed query in the P111 frame-pair decoder is

```text
q_beta(X) = sum_(i != beta) (r_beta dot r_i)/2 * X_i.
```

The `r_i` here are the integer vectors in the raw U8 word. Each has squared
norm four. The query has 52 nonzero coefficients. They are +1 or -1. Let
`H_beta = {x : x dot port_beta = 0}` in `F2^9`. The source labels in the query
span this eight-dimensional hyperplane.

The integration class has the following restrictions.

1. The old A section has finished. Its clean source rows stay fixed. Inserted
   operations can read these rows. They cannot change or combine them.
2. The old COPY, B, cleanup, and final-frame contracts stay fixed. An old row
   can advance only to a frame from which every later required frame remains
   reachable by inclusion. It cannot descend.
3. Each new carrier has a monotone frame path inside `H_beta` until its query
   delivery. It can read any old rows at a common frame. New carriers cannot
   combine with each other before `H_beta`. They can combine without charge
   at `H_beta`. A new accumulator is a carrier under this definition if it
   reads an old row before it reaches `H_beta`.
4. The nine-call owner geometry has 888 live wires per P111 replica. Per
   replica it has 666 capacity-8 bins and 444 bins of each capacity 16, 32,
   and 48. The old helper widths stay fixed. New monotone carriers consume
   their end dimension minus their entrance dimension.
5. All old child charges remain, except for the favorable credits in section
   5. Additional work has nonnegative cost. No other supplier or outer
   assembly rule is changed.

**Theorem.** No member of this class has a native moment at most one at
`b0 = 0.001664727258740678855772`, for any positive integer replica count.
The conclusion still holds if each call chooses a different beta.

This is a theorem about this finite word and this explicit class. It is not a
claim about every P111 construction. In particular, it does not constrain a
new gather built during a changed A section.

## 2. Exact rows and future-frame restrictions

Give source i the formal clean value `X_i`. Give every target and helper zero
clean value. The precondition uses only target and helper roles, so it does
not change these clean values. Dirty-value compensation also has no clean
source response. Replay each add and scale in A over the rationals. This
gives a row `a_r` and current frame `U_r` for each register r at the cut.

The checker independently replays every monotone frame climb through A, B,
early cleanup, and final endpoints. It counts COPY descents separately. It
checks the local profile and helper widths against the retained word. It
also checks each clean row's source labels against its current frame.

Let `I_r` be the intersection of all later required frames for r. These
include its retained centre frame or target COPY level, all B uses, each
early-cleanup use at its actual early frame, and its final endpoint. A
permitted old-row read at frame V must satisfy

```text
U_r subset V subset I_r intersect H_beta.
```

Drop coordinate beta from each clean row. Among nonzero rows with
`U_r subset H_beta`, rational elimination gives the following complete census.

| Punctures | Eligible rows | Rank of eligible rows | Required rows | Required current dimensions |
| ---: | ---: | ---: | ---: | --- |
| 64 | 22 | 22 | 16 | ten at 3, six at 2 |
| 32 | 28 | 28 | 18 | eight at 3, ten at 2 |
| 16 | 52 | 52 | 26 | twenty-six at 2 |

In each case the query is in the eligible row span. The eligible rows are
independent. Therefore its expression in these rows is unique. The
certificate gives every nonzero rational coefficient. Direct substitution
checks each expression against the root-defined query.

For every required row, the finite subspace check gives the exact set equality

```text
I_r intersect H_beta = U_r.
```

Thus the old tail does not permit that row to advance within the query
hyperplane. The required `U_r` form an antichain: no two of them contain one
another. The code checks all pairs, including pairs with different dimensions.
It also checks that no old role has
`U_r subset H_beta subset I_r`. Hence an old role cannot itself become the
query accumulator under these contracts. The omitted data roles are not
needed for this conclusion.

These statements follow from complete finite enumeration of the pinned word.
They are exact rational and binary-subspace checks, not a random search.

## 3. Each required row needs its own monotone transport

Every query delivery is a linear combination of eligible old rows. Their
independence forces every required row to have its stated nonzero total
coefficient. That row must therefore be read by at least one carrier that
contributes to the query.

A carrier cannot read two required rows. It would have to visit their two
fixed frames. A monotone path cannot visit two incomparable subspaces.
Arbitrary scalar coefficients, extra zero rows, and cancellations do not
remove this obstruction. They do not change the unique expression in the
independent eligible rows.

A carrier that reads at `U_r` must subsequently reach `H_beta`. The required
transport rank is at least `8 - dim(U_r)`. If the path splits this rank into
positive increments `d_1,...,d_k`, its cost is at least the cost of a direct
rank-d child. In fact, for `0 < b < 1`,

```text
f_b(d) = d*(73/d)^b = 73^b*d^(1-b),
sum_j f_b(d_j) >= f_b(sum_j d_j).
```

We grant the carrier its entire read frame as a free entrance and let it end
at `H_beta`. The minimum transport profiles in the census are therefore

```text
64 punctures: 10 H5 +  6 H6, width mass  86;
32 punctures:  8 H5 + 10 H6, width mass 100;
16 punctures:          26 H6, width mass 156.
```

A carrier that acts as the accumulator can supply one of these transports.
It still pays that transport. There is no separate centre charge in this
bound. A carrier cannot be reused for a second incomparable read after it
has reached `H_beta` without a forbidden descent.

## 4. The owner-volume relaxation

The old local paid profile is

```text
L = {1:2548, 2:338, 3:446, 4:162, 5:72, 8:8}.
```

The helper width inventory is
`{4:80, 5:32, 7:54, 8:122, 9:216}`, with mass 3778 per call.
P111 has owner capacity

```text
111*(6*8 + 4*(16+32+48)) = 47952
```

per replica. After nine old helper sets, the residual mass is
`47952 - 9*3778 = 13950`. If the new transport mass per call is w, it is
`13950 - 9*w`.

For every residual rank `0 < r <= 48` and every positive b,

```text
f_b(r)/r = (73/r)^b >= (73/48)^b.
```

Thus residual mass R costs at least `R*f_b(48)/48`. This grants fractional
rank-48 children, with no fragmentation, owner labels, windows, or bin-count
restriction. It is a lower bound for every actual owner packing.

The same inequality makes extra monotone transport nonnegative after its
owner-space credit. Splitting a required transport cannot reduce its cost,
and extra path increments contribute `f_b(r) - r*f_b(48)/48 >= 0`.
Thus larger entrances, narrower endpoints, and better packing cannot improve
on the free-entrance and pooled-volume lower bound within this class.

## 5. Full favorable invoice

Let `D_beta` be the sum of all paid climbs on source beta and target beta in
the original U8 word. The checker derives it from the events for each beta.
Every such profile has rank mass 16. It does not use the modal path from an
older favorable-budget calculation.

Give the integration all of the following credits:

- Delete `D_beta`, even if a frozen old gate still needs that data role.
- Replace one rank-8 COPY child by a rank-7 child.
- Charge only the required new transports `C_beta` from section 3.
- Grant all new dirty compensation, restoration, source access, scalar work,
  native adapters, temporary-stream work, and target-interface changes free.
- Retain only the residual-volume lower bound from section 4.

These credits need not be jointly realizable. They only lower the cost. In
particular, this is not a proposed supplier or an unimplemented kappa claim.
The resulting moment is

```text
M_beta(b) = [9*sum_r (L-D_beta-H8+H7+C_beta)[r]*f_b(r)
             + (13950-9*w_beta)*f_b(48)/48] / (73*888).
```

All 112 exact rational lower bounds exceed one at b0. The minimum occurs at
raw root indices `1, 9, 65, 73`. For these indices,

```text
D_beta = 9 H1 + 2 H2 + H3,
C_beta = 10 H5 + 6 H6,
L-D_beta-H8+H7+C_beta =
    {1:2539, 2:336, 3:445, 4:162, 5:82, 6:6, 7:1, 8:7},
residual mass = 13176.
```

The minimum moment is enclosed by

```text
1.00000864736369386816835926810620863001514
1.00000864736369386816835926935824150131476
```

The certificate stores rational endpoints, not these display decimals.
With the transport charge omitted, every beta passes with a moment below
one. This checks that the transport obstruction is decisive.

For T replicas, all local costs and the owner volume scale by T. The division
by `73*888*T` cancels T. If the beta values vary between calls, the total
relaxed numerator is the sum of their separate numerators, with the same
linear idle-space credit. Each exceeds its share of the denominator. This
proves the theorem for every positive T and for mixtures of punctures.

Every coefficient in each final relaxed profile is nonnegative, and every
child rank is less than 73. Its moment is strictly increasing in b. Failure
at b0 therefore implies failure at every larger b, including the numerical
b selected by the later PR1042 frontier. The word in PR1042 is outside the
class of this theorem.

## 6. Rational interval check

For `0 <= z <= 1/3`, use

```text
log((1+z)/(1-z)) = 2*sum_(j>=0) z^(2*j+1)/(2*j+1).
```

After 24 terms, the omitted positive tail is at most
`2*z^49/(49*(1-z^2))`. Reduce `73/r` into `[1,2)` by powers of two and bound
`log(2)` with z = 1/3. Multiply both endpoints by the exact rational b0.

The resulting exponent x is in `[0,1)`. After degree 12 in the exponential
series, the tail is at most

```text
(x^12/12!)*(x/13)/(1-x/14).
```

All operations are rational. Rounding is outward to a denominator of
`2^160`. The retained independent interval engine uses 80 logarithm terms,
16 exponential terms, and a denominator of `2^200`. Its interval for every
used rank lies inside the new interval. No floating-point value decides an
inequality.

## 7. What remains open

The proof leaves the following mechanisms open: change the A rows or the B
contracts; allow new carriers to combine before the final hyperplane; pay
for nonmonotone paths or copies; change the owner geometry; or use another
local word. Each such construction needs its complete physical interface and
cost. The unchanged bit supplier does not repair a failed complex moment.

This package does not replay the complete native phases, the global owner
map, fixed-precision arithmetic, or a tape compiler. It supplies a necessary
cost bound in the stated native-frame model. All inherited all-size,
common-label, physical-hosting, precision/tape, analytic-transfer, and bit
H1-H5 assumptions remain outside this finite result.
