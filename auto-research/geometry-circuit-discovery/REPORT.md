# Geometry–circuit discovery: support-weighted central factors

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
October 8, 2026. Bounded discovery; no stronger multiplication bound.

## Decision

**Neither candidate earns a complete construction attempt.** Stop this round
at the screening gate. Two families were examined; the second has two named
instances connected by an explicit algebraic construction. There was no
parameter sweep, third candidate, or new finite-network claim.

The useful addition is an exact diagnostic for the **rational support cost
of a binary factorization**, rather than just its binary rank. For a fixed
central matrix of rank r, it optimizes over every factorization with exactly
r centers. This matters because changing the basis of a low-rank scalar map
need not produce cheap intermediate frames.

| Proposed pair | Labels n | Rational dimension d | Binary rank r | Best central support cost ell | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| E8 root lines, minimum-rank parity producer | 120 | 8 | 9 | 72 | Negative rank deficit in the granted two-axis copied-center ledger |
| Four-letter Hamming, length 3, distance 2 | 64 | 10 | 8 | 66 | Negative rank deficit in the same ledger |
| Same Hamming family, length 7, distance 4 | 16,384 | 22 | 576 | Even grant zero | Fails the 2^-9 target with one independent producer role per label |

These are scoped rejections. Redundant central factors, different binary
matrices on these graphs, block labels, and a different transfer adapter
are not excluded. No failed search is treated as a general impossibility.

The published certificates, selected release, pinned PR82 checkpoint, and
all earlier research are preserved. The checkpoint and acceptance contracts
are those of the [mechanism brief](../mechanism-prep/REPORT.md), not a claim
about newer submissions.

## Why these two families

The first asks whether a very small rational geometry with a genuine
two-field rank advantage can become competitive through a better choice
of central forms. E8 is **not a newly discovered geometry here**: the test
identifies its 120 projective lines with the earlier t=3 odd-support
[quadratic-phase family](../../docs/research/quadratic-affine-vectors.md).
The specific reason for reopening it is new: exhaustively optimize the
support-weighted central factor under the modern copied-center ledger.
The historical test used a stopping rank lower bound and the old
three-stage threshold; it did not solve this optimization.

The second changes the binary-cube alphabet to four letters. This changes
the local binary module from a single nilpotent block to a block plus two
trivial summands, while using a rational simplex geometry. It tests whether
additional labels can outweigh the increased rational dimension. It does
not repeat the already-rejected binary-cube parameter sweep.

Primary-source context: [Winter and van Luijk](https://arxiv.org/html/1901.06945v2)
describe the E8 roots and their inner-product graphs. Our coordinates,
binary matrices, factors, and costs are independently generated below.
[Bukh and Cox](https://arxiv.org/html/1802.00476v2) provide characteristic-sensitive
and block fitting-matrix constructions; that framework motivates looking
beyond scalar rank, but does not supply our required circuit adapter.
[Peña and Sarria](https://arxiv.org/html/1903.11587) construct characteristic-dependent
rank inequalities and associated coding separations. Reading that source
did not supply a third complete geometry–producer proposal with a costed
copied-readout interface. We did not count its capacity gap as a finite
network, or reopen the parked balanced-Fano model.

## The exact optimization

Let q_i be the rational input labels and let C be the fixed binary central
map. A proposed gathered center has value

    z_j = sum_i V_ji x_i   over F2.

In the support-containing frame proposal, its retained frame must contain
the rational span of every q_i with V_ji=1. Thus its central cost is at least

    w(V_j) = dim_Q span{q_i : V_ji=1}.

This is a statement about this producer/frame schedule, not every possible
implementation of that scalar map. Degenerate spans or incompatible
intermediate gates may increase the cost or invalidate the proposal; they
cannot rescue a rejection that grants the ideal cost.

If C=UV and the inner dimension equals r=rank_F2(C), the rows of V form
a basis of rowspace(C). Conversely every basis supplies such a factorization.
Enumerate all 2^r-1 nonzero rowspace vectors, weight each by its rational
support rank, then choose a minimum-weight basis by vector-matroid greedy.
The exchange property proves optimality. The certificate stores the entire
catalog, its cumulative binary ranks by cost, the selected basis, and U.

This does **not** optimize factors with more than r centers. Their forms
can lie outside rowspace(C), with dependencies canceled by U. Splitting
a single form into several forms cannot by itself improve its support-rank
cost: the old support is contained in the union of the new supports, and
dimension is subadditive. A useful redundant factor would need shared
reorganization across forms, not independent splitting of each center.

## Candidate A: E8 root geometry

Take one representative of each antipodal root pair. For exact integer
arithmetic the stored labels are twice the roots:

* 56 vectors with first nonzero entry 2 and the other nonzero entry +/-2;
* 64 vectors in {+1,-1}^8 with first entry 1 and an even number of minus signs.

For stored labels q_i define G_ij=q_i.q_j/4 and

    C_ij = 1 + G_ij mod 2.

G has diagonal 2, rational rank 8, and off-diagonal entries -1,0,1.
Consequently C has diagonal 1 and its off-diagonal ones are precisely
rationally orthogonal pairs. Normalize F=G/2 to obtain rank-one idempotents.
The exact binary rank is 9. In particular n=120 exceeds rd=72: this is
a real two-field rank-product advantage, just not a sufficient circuit gain.

**Producer proposal.** Use a rank-nine binary factor C=UV for central
parities, and the orthogonality side map C+I. Their sum is I over F2.
An edge-explicit side producer has compatible source-to-target line
inclusions because the two lines are orthogonal. A shared-sum replacement
would have to retain this compatibility. Central gathers use nested spans
of their input lines. The Euclidean form makes these spans nondegenerate;
a terminal read-only center could then use the copied-readout schedule,
with its transform still paid. Full side-role compression and the modern
adapter are granted optimistically for rejection, not asserted constructed.

**Result.** Every one of the 511 nonzero rowspace vectors has support
spanning all eight rational dimensions. All rank-nine choices therefore
cost ell=9*8=72. This is an exhaustive basis-independent conclusion.
There is no cheap hyperplane center hiding behind a different minimal
factorization.

With two equal axes, lambda=ell/n=3/5, so

    (N-L)/N = 1-2lambda = -1/5.

Even rank positivity fails under the granted ledger, regardless of scratch
compression. At the 2^-9 target the joint budget with rho=1 would require
ell<=43 per axis, before any extra independent roles or fragmentation.
Seventy-two is not close enough to justify constructing this producer.

## Candidate B: four-letter Hamming/simplex geometry

Let x range over {0,1,2,3}^k, with k=2D-1 and D a power of two. Define

    G_xy = D - dist_H(x,y),       C = I + A_D over F2,

where A_D is the distance-D adjacency matrix. The diagonal of G is D;
the off-diagonal support of C is exactly its zero set.

Use rational coordinates (1, [x_i=1], [x_i=2], [x_i=3]) over all i.
The form has H_00=D, constant-to-symbol entries -1, and each local
3-by-3 symbol block I+J. Its Schur complement is D-3k/4, nonzero for both
named instances. Thus d=3k+1 exactly. Unlike E8, this form is indefinite;
intermediate support spans are not automatically nondegenerate. Granting
their dimension as the full frame cost makes the screen more favorable.

The binary rank has a small independent certificate. Each local off-diagonal
adjacency is I+N, where N=J_4, N^2=0, and rank(N)=1. Expanding the distance
operator gives I+A_D=e_D(N_1,...,N_k). The code checks the binomial coefficient
cancellations. Each four-dimensional local module splits into one
two-dimensional nilpotent block and two one-dimensional trivial blocks.
On l live blocks, compute multiplication by e_D in

    F2[z_1,...,z_l]/(z_1^2,...,z_l^2).

The total rank is the sum of these block ranks with multiplicities
binom(k,l)*2^(k-l). For k=7,D=4 the live ranks are 1,2,8,16 and the total
is 280+168+112+16=576. Here 16,384>22*576, again a genuine rank-product
advantage across fields. No 16,384-square matrix is needed.

**Producer proposal.** A prefix/suffix dynamic program for the elementary
symmetric operator provides the central map, with distance-D side
contributions canceling it to I. An edge-explicit orthogonal side producer
is the conservative fallback. A compact producer would need to associate
each partial sum with a nondegenerate containing span, leave designated
center outputs unchanged during scatter, and charge all copies and
restoration. Neither the dynamic program nor its scalar rank establishes
those intermediate-frame and tape obligations. We screen before attempting
that construction.

**Small instance.** At k=3,D=2, n=64,d=10,r=8. Of the 255 nonzero binary
rowspace forms, 18 have support rank 8, 54 have rank 9, and 183 have rank 10.
The forms of cost at most 8 and at most 9 each span only seven binary
dimensions. The minimum-weight basis costs 7*8+10=66. It again fails rank
positivity in the proposed two-axis schedule. The target budget would
require ell<=19, even granting rho=1.

**Next named instance.** At k=7,D=4, d=22. With zero central loss, rho=1
on each axis, and perfect batching, the necessary joint residual is already
negative (approximately -0.00008514716). Consequently we do not build the
large scalar map or search its central bases. This rejects this instance
under the stated adapter; it is not a theorem about every Hamming parameter
or an implementation that changes the independent-producer contract.

## Complete budget and complex obligations

For the rank-one, two-stage copied-center proposal, grant the ledger

    m=d_1*d_2, N=n_1*n_2,
    W=2N+n_2*R_1+n_1*R_2,
    L=n_2*ell_1+n_1*ell_2,
    s=Wm-N+L.

Write rho_i=R_i/n_i and lambda_i=ell_i/n_i. The exact target screen is
the mechanism brief's joint inequality, with all macros packed into their
whole rank and independent producer storage relaxed to rho_i=1.
Its residual intervals are approximately:

| Proposal | Available budget minus charged optimistic cost |
| --- | ---: |
| E8 minimal-rank producer | -0.00750517338 |
| Hamming length three minimal-rank producer | -0.01445166721 |
| Hamming length seven, zero central loss | -0.00008514716 |

These numbers are summaries of rational intervals checked by integer
powers. The certificate does not confuse these fractional optimistic
profiles with physical recursive calls. In particular no constructor has
been inferred merely from substituting a new d or r into the old formula.

Both families have an **algebraic candidate** for the complex dual: use the
dyadic scalar matrix F=G/D (D=2 for E8) and binary phase geometry given by
the nondegenerate quotient of F2^n by ker(C), with bilinear form C.
The labels [e_i] have norm 1; off-diagonal nonzero F entries have zero
binary pairing. The phase dimensions would be 9, 8, and 576 respectively.
The normalized scalar entries and the displayed small rational factors
are dyadic. This is a compatible endpoint core, not a complex network.

The precise missing complex lemma is a producer with nondegenerate
intermediate binary frame spans, an all-original-input transparent action,
retained read-only centers with paid copied transforms, and a complete
ordered residual profile. No complex saving follows from the reciprocal
core alone. Since the bit proposals fail the optimistic gate, we did not
spend a construction attempt on this missing lemma.

## What is missing and when to reopen

The missing ingredient is now more concrete than a smaller matrix rank:
**a scalar core whose shared central forms have sufficiently small rational
support spans, together with affordable independent storage.** Low rank
in a small rational dimension can still put nearly every parity on the
entire ambient frame.

For E8, reopening would require a specific different supported C, a jointly
shared redundant factor whose weighted cost can plausibly fall below 44,
or a different frame/readout mechanism. The exact rank-nine result rules
out another search over basis choices. Merely splitting those nine forms
cannot help. This is a clear missing ingredient, not an endorsement of a
large blind redundant-factor search.

For the larger Hamming instance, central improvements alone do not address
the demonstrated dimension/storage obstruction. It needs a different
adapter, block geometry with its own ledger, or a representation that lowers
the rational dimension. None is supplied here. The 2^-9 goal therefore has
no newly validated construction path from this round.

## Reproduction and validation

Run from the repository root:

```sh
python3 research/geometry-circuit-discovery/screen.py --output research/geometry-circuit-discovery/certificate.json
python3 -m unittest discover -s research/geometry-circuit-discovery -p 'test_*.py' -v
```

The standard-library-only replay regenerates both cores, all 766 nonzero
rowspace support ranks, complete minimum-rank factors, module ranks, and
target budget intervals. Tests independently lower-bound every support
rank by elimination modulo 101, compare greedy against exhaustive toy
bases, reconstruct every scalar factor entry, verify the earlier-family
identification, and check the Hamming rational form and module decomposition.
See `validation.json` for the completed run and preservation check.
