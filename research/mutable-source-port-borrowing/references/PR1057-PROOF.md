# A fixed pool under an exact additive contract

## Contract and allocator

Let V be an abelian group and let A_0,...,A_(n-1) be exact additive
endomorphisms of V. A leaf on distinct rows s,t performs
`row[t] += q A_i(row[s])`, with q in {+1,-1}, restoring its source and its
separately supplied private workspace. There are no aliased row views,
mutable coefficient descriptors, hidden state, concurrent observers or
exceptions midway through a leaf. Coefficients and descriptors are read-only.
Represented arithmetic is exact, with sufficient headroom. This is stronger
than merely requiring a reversible shear with a deterministic nonlinear
increment. Factors need not commute.

Global row zero is the external input. Row one is the output. For ternary
and binary nodes, retain the fixed mutable pool `{1,2,3,4}` and choose k-1
connectors from it after excluding the current source and target. The fixed
priority `[2,3,1,4]` specifies the emitted addresses. Every child receives
this same global pool; ancestor ports may be selected when they are not that
child's immediate ports. Global row zero is never a connector or target.

At most two pool rows are excluded, leaving at least two connectors. Thus
three dirty rows suffice for every finite ordered binary/ternary tree.
For binary-only trees the pool `{1,2,3}` leaves at least one connector, so
two dirty rows suffice. These are upper bounds, not necessity claims.
Small trees can use fewer. No row copy, row initialization or row clear
occurs when a physical row is lent to another invocation.

The external input is read-only at every prefix. An internal invocation's
source is guaranteed restored **on return**; deeper descendants can modify
it temporarily. This weaker internal source interface is part of the change.
Leaf calls still have distinct immediate ports and preserve their immediate
source throughout that atomic leaf.

## Induction and the echo word

Induct on the supplied finite tree. A leaf satisfies the contract. At an
internal node, let B_i be the ordered product represented by child i. By
induction, every completed child changes exactly its target by `q B_i(source)`
and restores every other row, independently of the incoming dirty values.
Consequently the state at child boundaries is precisely the state of ideal
shears on the chain of ports `(x,z_1,...,z_(k-1),y)`. Borrowing other ancestor
ports inside a child does not change these boundary maps.

Write U_i for the shear from chain port i to port i+1. With execution order
left to right, let `C = U_0 ... U_(k-2)` and `D = U_1 ... U_(k-2)`.
Use the credited PR673/PR822 word

```
C; U_(k-1); inverse(C); D; inverse(U_(k-1)); inverse(D).
```

For k=2 the word is `U; V; U^-1; V^-1`. After U, the connector is
`z + B_0 x`. The two V calls add
`B_1(z+B_0 x) - B_1 z = B_1 B_0 x` to y, and the connector restores.

For k=3 the word is `U; V; W; V^-1; U^-1; V; W^-1; V^-1`.
The first W reads `z_2 + B_1 z_1 + B_1 B_0 x`; the second reads
`z_2 + B_1 z_1`. Their difference is `B_2 B_1 B_0 x`. The inverse
ladders restore both connectors. No commutation of B_i is used. All
non-chain rows restore by the induction hypothesis. This proves the
positive call; reversing all leaf records and negating each sign proves
the negative call. Deterministic address selection makes this inverse
literal, even when ancestor ports are reused.

The result holds for arbitrary initial output and dirty rows. Its essential
step is that a completed child is an additive shear independent of its
incoming private pool. PR822's nonlinear contract permits that increment
to depend on private dirt. Lending an ancestor target can then change the
increment that a later inverse call must subtract. The eight-factor
certificate exhibits this failure, rather than extending the theorem to
rounded or arbitrary nonlinear leaves.

The general constant-register algebraic phenomenon is classical; see
Michael Ben-Or and Richard Cleve, *Computing Algebraic Formulas Using a
Constant Number of Registers*, SIAM J. Comput. 21(1), 54–58 (1992),
[doi:10.1137/0221006](https://epubs.siam.org/doi/abs/10.1137/0221006).
The contribution here is the specific allocator/contract comparison,
literal noncommuting replay and explicit resource bill, not priority for
constant-register computation.

## Calls, planning and the comparison class

For per-factor prices c_i valid for both signs, every occurrence, the common
precision and all required private work, a leaf has bill c_i. Binary nodes
have bill `2 W_0 + 2 W_1`; ternary nodes have bill `2 W_0 + 4 W_1 + 2 W_2`.
These include both target updates and every inverse ladder. Address-dependent
leaf costs must instead be summed over the actual emitted `(s,t,i,q)` records;
they cannot be replaced by a uniform c_i without justification.

For unit prices, let F(1)=1. For n>1 take the minimum of

```
2 F(a) + 2 F(n-a),                         1 <= a < n,
2 F(a) + 4 F(b) + 2 F(n-a-b),             a,b >= 1, a+b < n.
```

Every admitted root has one listed partition, and joining minimizers attains
each candidate. Induction proves optimality within these fixed echo templates
over binary/ternary ordered trees. It says nothing about other algebraic
identities, higher arities or arbitrary programs. Ties are resolved by
`(bill, arity, split sizes)`, and leaves are labeled consecutively.

The planner through 64 examines exactly 43,680 candidates. Its DP has O(n)
entries and O(n^3) arithmetic/comparison steps on their actual integer bit
lengths. The public routine also materializes all plans through n, using
O(n^2) tree storage; a single selected tree has O(n) nodes. Planning, tree
construction, precision calculation, coefficient preparation and word
compilation are paid separately. No reuse of planning is assumed.

For the 56-factor chosen tree: `N = 1,568`, depth five, 91 tree nodes.
The pinned PR822 sibling allocator has S=5, while the reserved allocator
has S=9 for this same tree. PR822's exact optimizer at cap five also costs
1,568; cap four is infeasible. Its proved capacity recurrence gives
`M_4 = 29 < 56 <= M_5 = 70`. This does not contradict that theorem because
its excluded-ancestor contract has changed. A balanced binary 56-factor
tree has 3,328 calls and six reserved dirty rows; our binary allocator can
emit that different word with two dirty rows. It is a separate space/time
choice, not a claim that three arrays are minimal.

With a fixed pool the generator uses O(h) control frames for tree depth h,
besides the read-only tree. Its Python validation/list construction and
yield propagation have the conservative record-operation bound
`O((n+N)h)`. The verifier deliberately materializes words, polynomial states
and receipts; its memory usage is not the theorem's data-space bound.

## Exact integer headroom

For a normed linear realization choose an integer `K >= 1` bounding every factor's induced
infinity norm. Define

```
H(leaf) = 1 + K,
H(node) = (k+1) K^n max_i H(child_i),
```

where n counts leaves below that node. At a completed-child boundary of
either the positive or negative k=2 or k=3 ladder, each chain row is a sum
of at most k+1 signed products applied to entry rows. Each product has
degree at most n; cancellation is exact. All other rows retain their entry
values. Hence the joint maximum norm is at most `(k+1) K^n` times the
node's entry norm at every such boundary. During a child, its inductively
bounded prefix multiplies this estimate by at most H(child). This proves
the displayed majorant for all prefixes, including borrowed ancestor ports.

For a dense integer leaf, each product and each partial row sum is bounded
by K times its incoming source norm, and the final target by 1+K times the
joint incoming norm. Thus the same majorant bounds scalar work as well as
data. If initial joint norm is at most a nonnegative integer D, sufficient signed payload width is

```
P = bit_length(max(K, D H(root))) + 1.
```

The maximum includes immutable coefficient values. This uses exact integer
arithmetic; no numerical error estimate or rounded restoration follows.
The independent free-module interpreter also computes weighted coefficient
l1 norms (`K^degree` per monomial) at every leaf boundary and checks the
majorant. In the main fixture the bound gives P=119 for D=7, K=2.
Observed dense maxima are evidence for those fixtures, not a replacement
for the majorant. Intermediate products can have degree greater than n
under port borrowing (69 at n=56), so a simple `K^n` global-prefix claim
would be unjustified.

## A complete, conditional price

For any actual backend, the complete execution price is

```
planning + coefficient/descriptor preparation + word compilation
+ sum over emitted leaves of C_i(s,t,q,L,P)
+ dispatch/control + any routing/frame work outside C_i
+ private-work initialization/final restoration.
```

`C_i` must include source/coefficient accesses, the chosen leaf's arithmetic,
its private work and both signs at the required precision. If a supplier
requires copies, physical frame changes or additional recursive children,
they belong in C_i or an explicit additional term. Port borrowing makes no
such adapter free and does not change those supplier requirements.

To make the accounting concrete, the certificate executes dense integer
matrix-vector leaves with four **clean scalar** P-bit work registers:
accumulator, source/target value, coefficient and product. Each matrix row
zeros its accumulator, reads L source entries and L coefficients, multiplies
and sums them, reads and updates one target entry and writes it back. After
each leaf all four scalar registers are explicitly zeroed. These are paid
ordinary assignments; no reversible-gate implementation of clearing is claimed.
The external arrays are arbitrary dirty data, while this small private/control
workspace has its separately stated clean contract. The same workspace is
charged to every allocator in the comparison.

Per leaf this executes `L^2` multiplies, `L^2+L` add/subtracts, `L+4` scalar
zero assignments, `2L^2+L` reads and L writes: `4L^2+4L+4` commands.
Initialize the four scalar registers once as four more paid zero assignments.
No length-L copy or clear is hidden here. Distinct leaf source and target
make the row-by-row target writes safe.

Data has `(S+2)L` P-bit cells, and read-only coefficients follow in `nL^2`
P-bit cells. Addresses are `sL+j`, `tL+i`, and
`(S+2)L+(factor*L+i)L+j`. The specified itinerary alternates source and
coefficient reads, visits the target for its read/write, and returns the
data head to address zero after **every** leaf. Literal replay and a separate
invoice calculation agree on every intercell distance. At each access a
bit head can scan a full P-bit cell and return to its left edge, adding
`2(P-1)` within-cell moves. Thus the explicit head bill is
`P * intercell_steps + 2(P-1) * accesses`, in addition to `P * accesses`
read/write bit actions. Address calculation is also paid: the receipt gives
the number of address events E and the address width a. With a specified
address routine of cost R(a) per event, add `E R(a)`.

The read-only unrolled program has N records of
`b = max(1,ceil(log2 n)) + 2 max(1,ceil(log2(S+2))) + 1` bits.
Charge Nb bits of storage and reads and 2Nb bits of forward-and-rewind
traversal. With a specified dispatcher of cost Q(b,a,log L) per record,
add `N Q(b,a,log L)` and its control workspace. Neither the dispatcher nor
the address routine is a proven fixed-tape compiler here. They remain
explicit backend parameters, not omitted constant-time pointer operations.

Writing M(P), A(P), Z(P) for scalar multiply, add/subtract and zero-assignment
costs, the dense arithmetic term is exactly

```
N L^2 M(P) + N(L^2+L) A(P) + (N(L+4)+4) Z(P).
```

Add the stated bit accesses/head travel, program preparation/read/travel,
`E R(a)`, `N Q(b,a,log L)`, coefficients, scalar workspace and backend control
storage. This gives an instantiated, conditional bill with no silent free
source access, restoration, scalar clearing or metadata. It does not prove
that the array saving improves runtime on another machine model.

PR673/730/822's call obstruction for the direct all-role adapter survives:
for n>=2 these echo trees have `N >= 4n-4`, so its optimistic moment
`3N / (2 n^(1-b))` is already at least three at b=0. Our fixed-tree call
multiplicities are unchanged. Selected supplier assumptions, exact recovery,
all-size realization, physical hosting, fixed-tape and analytic transfer
obligations remain inherited or open. No selected certificate is edited.
