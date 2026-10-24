# Boundary proof and complete BIT cost

## 1. Source and owned input code

Use the PR589 word retained at the source commit in SOURCES.json. It has
111 X fields, 111 Y fields, 439 helpers and one owned COPY centre. The
logical main map is `(X,Y) -> (X,Y+X)` over GF(2). Each helper has the
identity logical endpoint. The source forward and reverse words have
this same logical map.

Replay the source records in reverse order over the vector space with
661 independent input symbols. Each of its nine COPY entries is a
linear form in these symbols. Reduce these nine forms by helper columns.
The resulting pivot helpers are

```text
222, 223, 224, 225, 226, 228, 230, 231, 233.
```

Each reduced form contains its own pivot and no other pivot. Every field
in its support has the full entrance frame. The relation rows are saved
in RESULT.json and are derived again from the source during every run.

Own these nine helpers. Clear each at entry and XOR its other relation
terms into it. The nine forms are then zero. These operations use a
common frame and leave all 652 retained input fields unchanged. A
chronological replay of the original reverse word now proves that every
COPY value is zero. The copy centre stays zero. Nine rank-one moves are
also on zero values. Replace only these moves by zero frame changes.
Clear the nine owned helpers at exit, and return the centre to its empty
frame. This gives a map on arbitrary retained inputs with all owned exit
fields zero. The entry clears make the result independent of arbitrary
initial values in owned storage.

The exact new local paid profile is

```text
{1:1314, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:10}.
```

The productive helper profile is `{8:430}`. There are no new nonzero
native maps. The original rank-one and rank-seven jobs are removed in
nine pairs. Each pair loses one rank-eight target. The fixed field count
remains 662; no new physical field is required.

## 2. Why one reverse word serves both directions

The logical involution alone is insufficient. Check the physical address
maps as well. For a source port let P be its rank-one rational projector,
K=I-P, Q=D_P, S=D_K, and R=D_I. Here D denotes the source two-bank
interchange, with its fixed second-bank reversal included. These address
permutations commute, square to I, and satisfy QS=R.

In this paragraph Q, S and R denote their induced data-permutation
operators. Let M be the two-field XOR shear, with block rows `(I,0)`
and `(I,I)`. The source forward physical operator is

```text
diag(R,S) M diag(Q,I) = [[S,0],[R,S]].
```

Its reverse physical operator is

```text
diag(Q,I) M diag(R,S) = [[S,0],[R,S]].
```

Both products therefore give the same physical endpoint. This endpoint
is an involution over GF(2), since RS+SR=0. Each retained helper has
endpoint D_I, also an involution. Thus the new reverse implementation
replaces either direction of the original local call with the same
caller port and role assignments. No new query, route or native map is
needed for this replacement.

The verifier checks the source entrance line and exit complement for
every port. It checks the rational address identities `D_I D_P=D_K`
and `D_P^2=D_K^2=I`. These are identities of address matrices. The block
XOR calculation above is an identity of induced data operators; it does
not identify addition of address matrices with addition of data operators.

## 3. Native interfaces and all column multiplicities

All nonzero native transitions are retained source transitions. The
verifier rebuilds every source projector over the rationals and checks
both nesting products and the rank difference for each transition pair.
For each of the 111 ports it builds an exact complement basis and a
15-dimensional route. It checks that the route is an involution, fixes
the central line, and sends the local full projector to the required
line-plus-fresh-stage projector.

For column multiplicity f, tensor each head-space projector and route
with I_f. The same products, inclusions and involutions hold. The entry
code consists of pointwise XORs and clears in a common full frame. Its
relations hold on arbitrary data arrays. The complete finite program
therefore has the same native boundary for every f under the inherited
all-column and owned-erasure premises.

Apply the retained delayed-cover bridge only after the entire finite
program is compiled. Its one common external weight is the same for all
fresh roles. All pointwise XORs commute with that weight. The retained
whole-fibre routes preserve independent data. The new code adds no
right-route symbol, nonzero native map or denominator. This argument
retains the source compiler and native realization premises; the finite
rational tests alone do not prove them.

## 4. Complete controller invoice

Replay every physical event in the source p16/a7 BIT controller over the
GF(2) group ring. Verify its literal scalar boundaries and all 32
independent main inputs per port. There are eighteen full calls and
fifteen query shears. Replace every full call by the new word, using
Section 2. Leave each thin query and idle transform in place.

Let P_old, T_old and P_new, T_new be the full paid and target histograms.
The exact differences are

```text
P_new - P_old = -162 H1 -162 H7
T_new - T_old = -162 H8.
```

Here Hr denotes one rank-r job or target. The new total is 57,231 paid
jobs and 11,292 productive fields. The paid rank mass is 215,457 and the
target rank mass is 216,210. The surplus is 753, as before. The verifier
reconstructs both complete invoices from the literal event list; it does
not subtract a proposed saving from a stored total.

For every 0<t<1 the exact moment improvement is
`162*(1+7^t-8^t)>0`. An equivalent certificate for the signed paid-minus-
target difference is the hinge sum `sum(delta_r*min(r,k))`: its values
at k=1,7,8 are -162,-162,0. All tail values are zero. This charges every
lost target and proves a strict improvement for the concave rank power.

Two rational interval engines check the new moment. The raw moment has
a positive margin at 0.003472070044 and a negative margin at
0.003472070045. This is a certified crossing, not an optimum over other
words or controller classes.

## 5. Compiler, cover and ordinary conversion

The new tested saving is 0.0034678 and the uniform saving is 0.0034668.
Keep the source tensor power 1024, cutoff 17, floor 18, second-moment
parameter 1/5 and reserve 1/250000. The exact interval checks give the
charged first-moment ratio below `1-reserve`, the tail ratio below
31/32 and the rounding ratio below 19/20. Both decay bounds after 128
steps are below 1/16. The completion surplus is positive, `17^64<18^63`,
and every target rank is below 256. RESULT.json records the exact H0 and
strict H1 thresholds. The winning uniform word is not materialized.

Keep the source cover loss 0.000009. The saving after cover is 0.0034578.
Use an odd prime `q>2^26*N^5` that avoids all fixed denominators and rank
witnesses. Keep atom fraction 0.004 and old ordinary saving 0.0000384599.
The new ordinary saving is

```text
(1-0.004)*0.0034578 + 0.004*0.0000384599 = 0.0034441226396.
```

The strict admitted endpoint is 0.00344412. At the same compiler gaps,
cover loss and atom fraction, the old word gives 0.0034363538396. The
matched gain is exactly 0.0000077688. This comparison does not credit the
new relations for the old source's unused conservative headroom.

The new local word has 25,891 pointwise records. This is 1,568 more than
the source's 24,305 XORs and eighteen COPY entry/exit records. Add all
1,568 records to the inherited complete local allowance of 1,000,000.
The new local allowance is 1,001,568. With all eighteen calls, thin
queries, physical events and boundary operations, the complete raw
nonrecursive allowance is 19,170,192, below the retained 10^9 allowance.
The new code uses only unit XOR coefficients, adds no denominator and
no storage field, and retains the source tape and cover obligations.

## 6. Complete multiplication scope

Use the pinned PR5398 outer parameters and replace only their ordinary
BIT saving by 0.00344412. All 54 strict and four functional predicates
pass. The actual BIT stock exponent is positive and strictly below the
active group exponent, which is below one. The complete multiplication
endpoint remains 0.00302728823. The complex supplier still binds.

This is a complete conditional BIT component improvement. It is not a
new complete multiplication bound, a selected-frontier change, a formal
proof, or an independent replay of the consumed complex construction.
All five inherited premise classes remain explicit in RESULT.json.
