# A uniform repair tariff over the selected complex recursion

This is a conditional cost-composition lemma. The input is the explicit
exceptional-record repair tariff in Jose Manuel's PR2250, section 3, and the
width/volume recursion proposed in PR2287, sections 3, 5 and 7. We do not
reprove either endpoint construction or its tape implementation. In particular,
the tariff below is a nonnegative expression bounding a named part of the
runtime, not a lower bound on every implementation of the same permutation.

## Quantified statement

Fix integers p>=2 and d>=1 at the root. Put beta=1/1000,
sigma=99833/100000 and g=15999/10^9. Let the root width e0<=d and volume V0
be positive. Let Gamma be any positive integer. At an internal node of width
e, the selected source specifies, for each r in

    H={1:349604,2:60192,3:62585,4:20448,
       5:11808,7:7,8:1152,48:4866},

H[r]*Gamma children of width r floor(e/73), each of logical volume
V/(14336 Gamma). Stop when e<73 or e^1000<d. A child with no remaining
internal node contributes no repair tariff. Dimensions, multiplicities and
volumes are mathematical quantities; no enumeration of Gamma is required.

At each internal node allow at most J repair calls, where J is one fixed
bound independent of p, d, depth and node. A call may consist of any number
of outer rows; apply its tariff to each row and sum. Its rows together have
volume at most that node's V. For every row, let M be its number of records,
R its unchanged record length in bits, A its key/control bound, and delta an
upper bound on its bad-record fraction. Assume one common A_* and R obey

    1<=A<=A_*, R>=A_*^3,
    0<=delta<=5/(128p^3),
    [5/(128p^3)] A_* (1+A_*/R)<=1.             (Admission)

The bound R is the actual complete coefficient record supplied to repair,
not a long field merely located elsewhere in the address. The compact
fields on which the source guard is counted must have complete ranges in
each row. These structural conditions justify using the displayed delta.

For one row define the PR2250 repair tariff exactly as

    Q(M,R,A,delta)=MR + M A^3 + delta M A(R+A).

Then the sum of these tariffs over all internal nodes, all calls and all
rows is at most

    (3J/g) V0 e0^sigma / max(73,d^beta)^sigma
        <= (3J/g) V0 d^[sigma(1-beta)].       (1)

The conclusion holds at arbitrary recursion depth with one constant:

    3/g = 1000000000/5333,
    sigma(1-beta)=99733167/100000000,
    599/600 - sigma(1-beta)=300499/300000000 > 0.

If the implementation uses time at most c Q for each repair, multiply (1)
by its uniform primitive constant c. J and c are explicit hypotheses. We
do not certify a numerical J for every operation of the entire supplier;
ordinary interchanges, other control preparation, scalar kernels, leaves,
parking and analytic transfer are outside this repair-only invoice.

## Proof of (1)

Admission gives A^3/R<=1 and delta A(1+A/R)<=1. Thus Q<=3MR,
including control preparation, keys, all radix passes and cleanup already
present in the source tariff. Summing rows gives at most 3V per call and
3JV per internal node. There is no factor for the number of outer rows:
each term was charged to that row's complete volume.

Define the potential of a node as V e^sigma. Since 0<sigma<1, floors only
decrease the child width. The sum of child potentials is at most

    V e^sigma mu,
    mu=sum_r [H[r]/14336] (r/73)^sigma < 1-g.  (2)

Gamma cancels exactly: it is in the number of children and in each child's
volume. Both independent interval engines certify (2) from the source's
eight integer histogram entries; no unproved decimal approximation is used.
All children are strictly smaller because r<=48<73, so the tree is finite.
Induction over levels bounds the potential at level k by V0 e0^sigma mu^k.

Every internal node has e>=a=max(73,d^beta). Its volume is therefore at
most its potential divided by a^sigma. Sum the geometric series and then
use the per-node tariff:

    sum_internal V <= V0(e0/a)^sigma/(1-mu)
                   <= V0(e0/a)^sigma/g.

This proves the first bound, including an empty tree. Since e0<=d and
a>=d^beta, it also proves the second. There is no omitted depth factor.
The exact strict gap to 599/600 is positive; this repair term fits that
layer exponent without invoking an epsilon-dependent logarithm argument.
It does not establish the other terms in that exponent's proof.

## Why the proposed source packet rules supply uniform admission

This paragraph is a source-level implication, conditional on implementing
the specified packet rules. It is not evidence that a complete physical
selected caller has already been emitted or executed.

PR2287 keeps p,d,K,G,H and one guarded component width w global. Its owner
packet has the full remaining row range, full compact fields, complete
binary spectators and r Gaussian coefficients of 2w bits each. Thus
R=2wr does not change on an owner selection or a recursive complex call.
Common-frame monomial maps permute the address and multiply coefficients
by unit phases; they do not expose the coefficient index as an address
field of a new repair call. Ordinary callees preserve their complete
payload. The coefficientwise C and scalar kernels are separately charged
linear scans, not new invocations of the compact repair tariff.

Let L=14336 Gamma and D0(e)=0 below 73, otherwise
D0(e)=1+D0(48 floor(e/73)). The source reserves a row count divisible by
L^D0(d), padding by less than two once at the root. Its selector decodes
[14336] x [Gamma] x [U] wholly within that row coordinate. For a child e',
D0(e')<=D0(e)-1, so L^D0(e') divides U. This operation restricts neither a
compact guard field nor the coefficient suffix. A non-power-of-two U only
changes the number of full outer rows. Applying the adapter successively to
those rows and reassembling before one complex child preserves all these
properties by induction. It creates no child per outer row.

All descendant row/address extents are at most the padded root extents;
fixed work/copy factors can be included in A_*. With total address length
O(p), r=2^Theta(p/d) and w=O(p), one fixed c_A has A_*<=c_A p. The enormous
fixed grid and cover constants change c_A, not its dependence on depth.

PR2250's original guard, n<=p, G=4 ceil(log2 p)+6 and
K>=G+4 ceil(log2 p)+10 give

    delta<=n(2*2^-G+8*2^(G-K))<=5/(128p^3).

Because every row keeps complete compact ranges, this is the same bound at
every node, including arbitrary dirty values and correlations in the payload.
It is a count of addresses, not a probabilistic assumption on data values.

For each fixed epsilon in (0,1), d<=p^epsilon and
r>=2^(a0 p/d) for some fixed a0>0 imply R>=A_*^3 eventually.
Indeed, a0 p^(1-epsilon)/log2 p tends to infinity. Once R>=A_*^3,
A_*/R<=1, and the last Admission inequality follows from
p^2>=5c_A/64. These thresholds depend on the fixed root family, a0 and c_A,
not on the descendant. K/log p tending to infinity supplies the guard
threshold. This applies to the original epsilon=997/1000 and the proposed
epsilon=1/40 caller without changing the proof. It is not a new dimension
extension or a claim that this covers every callee assumption. PR2365's
finite scalar cutoff is not asserted to satisfy every unspecified c_A/a0
threshold simultaneously.

## Two countermodels to stronger size-only inferences

**Long data somewhere in the packet is insufficient.** Take p=s^2,
d=s, r=2^s, w=p, and M=3*2^p. A=ceil(log2(2MR)) is Theta(p), where
R=2wr. Exposing the coefficient index as an outer address changes the
record count to Mr and the record length to 2w. Total bits, data and even
the identity endpoint are unchanged. Nevertheless the normalized cubic
preparation term changes from A^3/(2wr)=o(1) to A^3/(2w)=Theta(p^2).
Thus the displayed source tariff alone no longer implies a uniform linear
cost. A legal identity implementation which performs exactly A^3 counter
steps per record realizes this distinction. The executable model performs
those nested steps on a small stream and checks compressed larger shapes.
This does not prove a lower bound for PR2250's actual preparation code.

**A global bad density is not a per-slice density.** In the actual original
guard, the compact digit t=B-1 is bad for every choice of the other fields.
Restrict to that fibre, and also set source control z=0 and target parity
a=0. The source four-step raw word leaves this fibre fixed: S=T=I. An
endpoint-correct keyed repair can therefore process this stream, but all
its records are bad. A key of k address bits forces this literal stable
radix routine to move each record through k passes. Its traffic is kV,
even with arbitrarily long R. Reusing the global delta=O(p^-3) for this
restricted call is false. The executor checks the identity raw word and
sorts actual correlated payloads while counting all complete-record moves.

Both models pass endpoint or total-volume checks that ignore the changed
structure; neither satisfies the full original complete-record/complete-
field contract. They are not counterexamples to PR2250 or PR2287. If an
implementation partitions all compact fibres, an aggregate density bound
could still pay the total repair. That is a different proof obligation.

## Evidence boundary

The universal result is the written potential argument and exact interval
certificate for its fixed moment. The executable tariff cases, row-stock
graphs and smaller cost models check arithmetic and failure modes; they
do not convert a finite replay into a universal tape theorem. No native
Gaussian supplier, complete cover payload, all-size transition table,
physical clock time, formal proof kernel or new multiplication bound is
certified here.
