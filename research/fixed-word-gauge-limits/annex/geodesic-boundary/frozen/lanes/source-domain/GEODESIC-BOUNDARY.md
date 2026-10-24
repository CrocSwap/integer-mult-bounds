# Common-boundary normalization cannot gain rank by frame fusion

The direct common-frame inverse for the one-shot mode controller cannot
give a positive supplier exponent by frame gauges or native-child fusion
alone. Its minimum native rank mass is the full productive rank. The
explicit rank-one boundary normalizations attain this lower bound. This
is a result for the retained wire paths and the common boundary encoding.
It is not a lower bound for the required computation with arbitrary
encodings or controllers.

The argument uses the frame-distance idea in the pinned
`research/format-limits-corrected/README.md`, Section C.2, Theorem N. That
source proves the canonical-subspace port-gauge bound. This note gives
the Lagrangian form for arbitrary Clifford gauges, checks the current
emitted mode words, and applies the bound to the one-shot common-frame
inverse. It does not claim the triangle argument as a new idea.

## The frame-path theorem

Fix a native dimension `n`. Put

    Z={(0,z): z in F_2^n}.

For a Clifford frame operator T, let S(T) be its binary symplectic action
on Pauli labels and define

    L(T)=S(T)^-1 Z.

This is an n-dimensional Lagrangian. For two such spaces set

    d(L,K)=n-dim(L intersect K).

The native Fourier rank of A is

    rho(A)=d(Z,S(A)^-1 Z).

Thus an exact native step from frame T to frame U has rank

    rho(U T^-1)=d(L(T),L(U)).                         (1)

The equality includes all monomial Clifford wrappers. A monomial M
preserves Z, so `L(M T)=L(T)`. Its global phase also does not change L.
The rank lower bound therefore does not discard a phase charge; it gives
a lower bound before the nonnegative cost of phase and address work.

For three Lagrangians, the two intersections with the middle space give

    dim(L intersect H) >= dim(L intersect K)
                         +dim(K intersect H)-n.

Indeed, the intersection of the two subspaces inside K lies in
`L intersect H`. Rearrangement gives the triangle inequality for d.
Apply it to the successive frames of one wire path and use (1):

    sum_native_steps rho(step) >= d(L(T_in),L(T_out)). (2)

The following hypotheses specify the circuit class.

1. Retain the persistent array-register paths of the scalar macro program.
   An explicit array permutation transports the paths and their frames.
   A native event belongs to exactly one such path and is counted once.
2. Each scalar ADD or COPY has a common frame on its live operands. A
   scalar SCALE does not change the frame. Retain the scalar accesses;
   do not replace them by native operator-valued coefficients for free.
3. A productive path is not cleared and assigned a new frame at no cost.
   Its arbitrary input lifetime is not moved into private zero workspace
   and replaced by another lifetime. Native work on other paths is
   nonnegative and is not credited twice.
4. Price every changed native step, including a step that used to have
   rank zero. Exact fusions of adjacent native steps are allowed. They
   still satisfy (2). Arbitrary Clifford frame gauges are allowed, subject
   to legal scalar access and the specified boundary frames.

Summing (2) gives a lower bound for the whole native job invoice. It does
not assume that the new frames are canonical subspace frames or that a
gauge comes from a fixed finite palette.

If N productive paths start in the chosen frame I and end in the full
native frame F_n, up to left monomial wrappers, then each endpoint distance
is n. Hence

    sum_native_steps rho(step) >= n N.               (3)

For tensor power lambda, use binary dimension `n*lambda`. A rank-r native
child has binary rank `r*lambda`. Divide (3) by lambda. The same bound
therefore holds at every allowed tensor power. Cover permutations only
permute the paths. Sum over the whole finite cover and then divide by its
order; no equality of the data in different cover classes is assumed.

For a common-boundary implementation whose scalar content endpoint is
the identity, the frame endpoint in (3) is the required full native map.
This is the contract used by the direct common-frame inverse below.

## The actual local mode words attain their path distances

The local source is commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The archive and member hashes
are checked by `verify_geodesic.py`. It also pins the emitted
`FULL-MODE-PROGRAMS.json.gz` and `ONE-SIDED-MODE-PROGRAMS.json.gz` from
the history-encoding lane.

In either orientation, each word has 704 persistent paths. Its 3,486
native climbs are all nested upward steps. The original frame before
each step is U, the frame after it is V, and

    U subset V,  rho(step)=dim(V)-dim(U).

Their total rank is 5,522. On every persistent path, this sum equals the
distance between that path's original endpoints. All 1,570 rank-zero
adapters remain in the event inventory.

These local frame labels refer to the relative chart. In the backward
coordinates `D_U=T_U F_9^-1`, the common right factor preserves every
Lagrangian distance. Thus the local I and F_9 labels below do not state
an additional physical boundary contract. The global common-I/common-F
contract is specified separately in the next section.

The full-mode macro word has 19,658 ADDs and 731 SCALEs. The one-sided
variant has 20,106 ADDs and 731 SCALEs. Neither emitted word has an array
COPY, an array CLEAR, or a reference to the private C bank. This statement
is about the full-array macro program. The lower real-arithmetic code can
still use private scratch COPY and CLEAR operations. Such scratch is not
a productive array path and is not a new native storage resource in this
gauge-only class. The theorem does not permit promotion of that scratch
or a new transfer of a productive lifetime into it.

For each of the 112 ports q, the old X path starts at C_q and ends at the
full local frame. Its endpoint distance is eight. The old Y path starts
at I and ends at `F_9 C_q^-1`, up to its exact monomial adapter. Its
distance is also eight. Changing the X input to I and the Y output to
F_9 makes both distances nine. This forces 224 additional rank units:

    local normalized rank >= 5522+224=5746.          (4)

This bound allows port-dependent Clifford gauges on all interior scalar
components. Ordinary restored helpers can have equal right gauges at
both boundaries: a common symplectic action preserves their endpoint
distance. The other prescribed data and mode endpoints remain fixed.

The literal first native event on each X path is a rank-zero
`old_to_new` adapter. The last event on each Y path is a rank-zero
`new_to_old` adapter. A line normalization fused there has rank one.
For every port, scalar accesses occur before the first paid X climb and
after the last paid Y climb. Thus those paid children are not adjacent
to the proposed correction. Moving a correction through the scalar
accesses requires changing all affected frames; (4) still applies.

Equation (4) is a local check. The global construction pays a boundary
normalization only at each complete data history, not at every call.

## Application to the one-shot common-frame inverse

The encoded-controller lane gives an exact joint content map on all old
data and the 72 fresh mode arrays per replica. Its direct common-frame
inverse has this order:

1. Apply Q on the four old X input banks, where `Q=diag(C_q)`.
2. Run the one-shot controller, its retained bridges, and its signed
   terminal exchange, with the exact mode histories and owner backfills.
3. Apply `Q^-1` to the old X output banks. These outputs come from the
   preterminal Y paths.
4. Invert the full joint content map in the common final full-F frame.

This is a different placement from separately conjugating the individual
Schur queries. All data and modes in step 4 have the same full boundary
frame. Its operator-valued coefficients have the monomial realization
specified in `encoded-controller/ONE-SHOT.md`; that realization is an
inherited construction premise, not re-emitted here.

With the initial Q operations included, every old productive path starts
at I. With the terminal Q corrections included, every such path ends at
F_73, following the terminal exchange as a path permutation. The new
stopped mode histories also start at I and end at F_73. The common-frame
inverse makes the joint scalar content endpoint the identity.

Thus (3) applies to any frame-gauge rewrite or fusion of this retained
common-boundary realization. It already grants the scalar inverse, its
monomial accesses, and its finite work. Extra hosting or workspace work
cannot reduce the lower bound.

Here is the exact invoice over all 16 replicas, per cover class. The
selected complete profile has rank mass 1,041,408 and 14,336 productive
old families. Removing its 1,152 rank-eight centre children leaves

    1,032,192 = 72*14,336.

The 1,152 fresh modes, their preparations, active uses, tails, and retained
old-owner backfills add exactly `73*1152=84,096` to this centre-free bill.
The pre-normalization one-shot mass is therefore 1,116,288. This equality
uses the inherited whole-owner invoice; it does not assign its costs
independently to a single replica.

There are now 15,488 productive families. The common-boundary lower bound
and the required increase are

    73*15,488 = 1,130,624,
    1,130,624-1,116,288 = 14,336.

The average increase per replica is 896. The explicit input and output
normalizers use `2*4*112=896` rank-one children per replica, so this rank
bound is sharp. Fusion can reduce the number of recorded operations, but
cannot reduce this complete rank mass.

The checked rank-48 mode plan splits the large preparation and tail
children. With the normalizers added, every child rank is at most 48,
and the native moment at exponent zero is exactly one. For any `b>0`,

    sum_r c_r r^(1-b)/(N*73^(1-b))
      =sum_r c_r r*(73/r)^b/(73*N) > 1.

For a different admitted fusion, all native child ranks are at most 73.
Equation (3) still gives a moment at least one for every `b>=0`. A
positive supplier exponent therefore cannot follow from this route by
frame fusion alone. No new kappa value or supplier admission is claimed.

## Limits and controls

An arbitrary physical input is not required to have formal frame I.
The old supplier uses virtual Q input frames, complementary output
frames, and a nontrivial logical bank exchange. It saves one rank unit
on each old data path. This is a counterexample to any attempt to impose
the common-boundary premise on every correct supplier.

A private array known to be zero can be given a different formal frame
without a native operation. It is not an arbitrary productive path in
(2). New lifetime transfers, new scalar interfaces, native operator-valued
ADDs, joint recursive children, and encodings that retain virtual Q at a
boundary need separate analysis. This result does not exclude them.

The checker rejects a changed native rank, a productive-array CLEAR, and
an unequal-frame scalar access. It checks the local paths in both
orientations and both emitted variants. Its global part verifies the
exact inherited profile and the stated conditional one-shot rank delta.
It does not emit the global word, validate a new owner allocation, or
price scalar/address work. Separate-agent proof review passed. The receipt
is `encoded-controller/review/GEODESIC-REVIEW.json`. That review rebuilt
all 1,004 source frame spaces by Gaussian nullspaces and checked the four
words with symplectic pairing ranks. It also checked the complete two-bit
symplectic group as a control for the matrix order and metric identities.
The producer output was reproduced byte for byte under `-I -O -B`, and
all three damaged-input controls were rejected.

Run from the workspace root:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/source-domain/verify_geodesic.py --repo worktrees/k5-centre-sharing --out work/centre-encoding-campaign-20261014/lanes/source-domain/GEODESIC-CHECKS.json
```

Expected status: `PASS_COMMON_BOUNDARY_GEODESIC_PREMISES_AND_INVOICE`.

Before any PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
This note was prepared with OpenAI Codex assistance. The mode construction,
its owner backfills, and its exact content decoder come from the named
campaign lanes; the canonical frame-distance premise is prior work as
credited above.
