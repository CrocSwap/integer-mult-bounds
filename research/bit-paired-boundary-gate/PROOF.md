# A paired boundary contract and its pre-construction cost gate

This continues PR673 at `b3917936aafbd0d680a954a86e25c4ce7e28a9f9`.
**The requested construction remains unachieved.** This note verifies a
different composable endpoint, a concrete but unprofitable realization, and
an exact owner plan and cost target for a replacement local word. No new
supplier or kappa is admitted. The selected frontier is unchanged.

## 1. Change both incoming boundaries

Work in an eight-dimensional rational Euclidean address space. Choose
orthogonal projections P and Q with PQ=QP=0, rank(P)=1 and rank(Q)=k-1.
Put R=I-P-Q. For a projector U, D_U exchanges the head and tail address
components on U, fixes its complement, and is an involution. On orthogonal
subspaces, D_U D_V=D_(U+V). Here these are ADDRESS permutations; addition
of their actions on Boolean payloads is a different operation.

The proposed local scalar word still computes `(x,y,z) -> (x,y+x,z)` for
every incoming dirty helper vector z, but with different frame boundaries:

| Role | Incoming frame | Outgoing frame | Monotone climb |
|---|---|---|---:|
| source | P | I-Q | 8-k |
| target | Q | I-P | 8-k |
| each helper | 0 | I | 8 |

Conjugating the scalar shear by these frames gives the exact payload
operator

    M = [[D_R, 0], [D_I, D_R]].

Indeed the source diagonal is D_(I-Q)D_P=D_R, the target diagonal is
D_(I-P)D_Q=D_R, and the off-diagonal is D_(I-P)D_P=D_I.
The reflected reverse word, with data roles exchanged, has the matching
upper-triangular operator. Thus separate source and target entrances can
produce a common boundary of rank k. This does not establish a scalar word
with those frames, nor a new orthogonality representation of the E8 graph.

The checker constructs rational orthogonal coordinates at each of the 111
actual PR589 ports. A Householder map sends 2e_0 to its norm-four port q;
P is the first coordinate, Q the next k-1 coordinates, and R the remaining
8-k. All inner products and port images are checked exactly for k=2 and 3.
This supplies geometric candidates for Q, not compatible scalar gates.

## 2. The global endpoint composes exactly

Let a=8-k. Add eight exterior blocks E_1,...,E_8 of dimension a to the
initial eight-space. A rational involution rho exchanges R with E_s and
fixes P+Q. It sends the local diagonal D_R to D_Es and the local off-diagonal
D_I8 to D_(P+Q+E_s). Its incoming/outgoing frame identities are verified
in the exact orthogonal coordinates above.

Use the retained nine-stage B_4 bank schedule and its chronological idle
advances, with every old width 7 replaced by a. The full endpoint is D_full
on all eight banks in dimension

    m_core = k+9(8-k).

The verifier proves this identity in the group algebra F2[C2^10], retaining
formal sums of permutations. Its ten commuting involutions represent P+Q
and the nine residual blocks. The result is the single full-address exchange
on every output bank, with no off-diagonal contribution. The regular action
is faithful and covers all 8*1024 formal basis columns. Removing any of the
18 bridge shears changes the endpoint. This check does not replace the
missing local word by an assertion that such a word exists.

For comparison with the actual m=64, W=28416 invoice, pad the core with
64-m_core ordinary directions and apply one paid child on those directions
to each data family after the completed core. The two exchanges commute.
This retains the productive denominator and the desired D_64 endpoint.
Padding is charged; it is not extra productive volume or free helper space.

## 3. A concrete wrapper exists, but is too expensive

The old local word has operator `[[D_(I-P),0],[D_I,D_(I-P)]]`.
Apply D_Q to the target before it and D_Q to the source after it. This
exactly produces M. Each of these native children has rank k-1. They
are real frame descents: target Q -> 0 and source I -> I-Q. They cannot
be subtracted from the old invoice as if they were absorbed climbs.

For k=3 the wrapper adds 222 rank-two children per invocation. A simple
physical plan allocates 439 owned helper rows, initializes them to zero,
and reuses them after each completed local invocation. The inherited exact
local replay restores all helper scalars; applying their final ADDRESS
permutation to zero still gives zero. The nine existing center rows remain
typed. Stock is 28416+439+9=28864 full rows, with productive W still 28416.
No helper work in this plan advances an idle data owner.

The complete recursive histogram for this explicit owned-row plan includes:
the actual PR589 local profile 288 times; 288*222 rank-two wrappers; every
full idle advance of the new five-coordinate schedule; and 28416 rank-16
padding children. The retained fallback shape is charged per child. Its
rank mass is 3018720 and its moment at c=1/99+10^-9 exceeds **1.7015**.
It increases the paid mass by 4202 2/3 per invocation. It fails even if new
chart preparation and routing have zero recursive cost, so we do not build
its supplier/controller.

The scalar/source-access bill still includes 288*24305 aligned XOR scans,
18*111*32 bridge XOR scans, and 288*9 inherited center copy/clear episodes.
Owned helper initialization costs 439 full-row zero scans. Each added
wrapper retains its native child and the inherited source/route interface.
New descriptor, chart and tape head-return constants have not been emitted;
their omission favors a candidate that already fails. This is not a finite
compiler admission or a claim that the new cover's fallback proof is done.

## 4. A target that does not depend on perfect consolidation

The meaningful next target uses k=3 directly, without those wrappers:
source P -> I-Q, target Q -> I-P, both with rank-five monotone paths. Keep
v=111, nine stages, 32 replicas, and at most nine rank-seven COPY episodes.
Require no more than 296 width-eight helper paths, each with arbitrary
incoming dirt restored in scalar coordinates.

The per-replica idle widths are

    10,5,20,5,30,5,30,20,10.

Each has 222 physical copies and the same untouched-stage windows as the
pinned chronology. There are exactly

    222 * (1+0+2+0+3+0+3+2+1) = 2664 = 9*296

whole width-eight slots. An integral flow supplies all 296 helpers at every
stage. The checker expands it into 2664 reservations per replica, 85248
globally, including family, window, coordinate offset, stage and helper ID.
It checks disjoint absolute coordinates and chronological membership.
Each replica translates the family by 888. All unused coordinates are
returned at their original idle boundaries; their per-replica histogram is

    {2:444, 4:444, 5:666, 6:444}.

No new helper storage is needed for this plan; physical stock would be
W+9=28425. The rank-16 padding is performed after the core, separately on
every productive family. It supplies no unproved extra hosting slots.
297 whole width-eight helpers per stage cannot fit this particular plan:
the total slot capacity is already exhausted. Partial-width entrances,
new banking, or different chronological schedules are outside that fence.

If the missing local word had these properties, its data, helper and COPY
rank mass per invocation would be

    222*5 + 296*8 + 63 = 3541.

Charge **every one of these units as its own rank-one child**, including
all helper restoration. This dominates any partition into proper children
of the same rank mass at 0<c<1, including the per-child fallback. Retain the
literal owner remainder and padding. The complete conditional profile is

    {1:1019808, 2:14208, 4:14208, 5:21312, 6:14208, 16:28416}.

Two exact rational interval engines give the following strict results at
**c=1/99+10^-9**, which is strictly larger than the necessary rate:

| Conditional local bill | Net rank saving per invocation | Moment, approximately |
|---|---:|---:|
| one child per monotone role/copy | 197 1/3 | 0.9835051889234464 |
| every local unit at rank one | 197 1/3 | 0.9947928245644905 |
| above plus 31 rank-one repair children per invocation | 166 1/3 | 0.9999126541717095 |
| above plus 32 repair children per invocation | 165 1/3 | 1.0000778099654908 |

Thus this target pays consolidation pessimistically and leaves a precise
31-unit repair margin at the existing per-role child volume. Any actual
repair must also account for its source reads, storage, routing and companion
operations; this allowance does not provide those mechanisms. It clears
both the 100-net-unit gate and the bit-rate
gate **only under the missing local-word hypothesis**. It is not an achieved
improvement. Source access, all dirty columns, COPY rank, actual frame paths,
finite cover routing, stock constants and analytic interfaces of that word
must still be verified. The unchanged complex supplier also prevents a
claim of kappa=0.01 from this bit-only conditional table.

The boundary accounting explains the change. For general k with the charged
padding and complete hosted remainder,

    deficit = 32*(8*111*k - 9*C).

With C=63, moving from k=1 to k=2 would save only 98 2/3 units per invocation,
slightly below the requested 100. k=3 saves 197 1/3, before excess motions or
other repairs. Neither helper deletion nor increasing the denominator is
responsible for this conditional credit.

## 5. The old scalar order cannot simply be re-framed

Start every old source at its actual line and every other role at zero.
Ignore the supplied frame table. At each scalar gate assign the smallest
possible monotone frame: the rational span of every operand's current frame.
Grant each copied arrival frame zero, which only makes this test easier.
Any monotone assignment for the same ordered scalar word must contain these
spans. Nonzero target/helper entrances could only enlarge them.

On the actual PR589 word, after B the source ranks are `{4:3, 7:108}`.
After C, all **111** sources have forced rank eight. They cannot finish in
I-Q of dimension six (or seven for k=2) along a monotone path. Omitting C
changes the closure and provides a nontrivial control. This is a topology
obstruction for monotone re-framing of this word, not a lower bound for
other scalar words or carefully paid descents. The next construction must
change the source/read/restoration topology or pay for enough resets within
the cost gate; a frame optimizer on the unchanged stream cannot realize it.

## 6. Gaussian E8 is a distinct, conditionally closed shortcut

Gaussian E8 has 60 complex lines in complex dimension four, or rational
rank-two ports in dimension eight. PR770's weighted-clique certificate
reports a copy lower bound of **40 complex rank units** in its stated
whole-line scalar-copy model. That is 80 rational rank units, not 40.
The floor is an external premise here, not independently re-proved.

Under the B_K accounting and slot-domination hypotheses of the inherited
format analysis, put k=2, h=8 and C/v=80/60=4/3. Let s=2K+1. The deficit
per port is D=(4K-4)/3. The checker uses exact logarithm intervals to prove
D/Cost < 0.0078 for K=1,...,42. For K>=43, the pre-stretch idle slots alone
give

    Cost >= 24 sum_(p=1)^(K-1) p log(K/p)
         >= 24 sum p(1-p/K) = 4(K^2-1),
    D/Cost <= 1/(3(K+1)) <= 1/132 < 0.0078.

The inequality exp(t)-1>=t then bounds every saving in that format below
0.0078<1/99. Helpers, fallback and remaining costs cannot improve this
favorable bound. This excludes the shortcut only with the stated COPY
floor and format hypotheses; vector-valued interacting delivery or changed
geometry remains outside it. The two-sided boundary target above does not
assume that its paired planes retain the old E8 orthogonality graph.

## Attribution and scope

The native D_U calculus, compressed B_K recipe and existing scalar word are
inherited from the PR370/386/436/443/510/545/589 lineages, with their existing
icekylinx, Zhihao Chen, eumemic, chafreaky, DreamingOfClouds, OpenAI and Claude
notices. The owner windows build on DaysSky's hosting work, independently
checked in this contribution's prior gate. The format slot bounds are
DreamingOfClouds' PR595/717 work. Gaussian context comes from GamingPuzzled's
PR620 and chinmayarvind23's PR770 (which credits thakrarsagar's PR738 and
Mister-Meeseeks' PR703). No priority claim is made for the elementary
endpoint identities, flow allocation or rank/moment inequalities.

Prepared for @androolloyd with substantial OpenAI Codex assistance,
Apache-2.0. Finite algebra and exact prices are not a formal proof of the
multiplication theorem. The success goal remains active and unachieved.
