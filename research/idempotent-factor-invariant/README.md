# A complete factor invariant for two idempotents

**Written linear algebra lemma with exact finite corroboration; no new kappa.**
Prepared by the authorized automated research workflow with substantial
OpenAI Codex GPT-6.1 Sol assistance. Apache-2.0. Human and formal proof-kernel
review are unclaimed.

This answers the sufficient higher-rank invariant question in
[codyw912's PR4735](https://github.com/CrocSwap/integer-mult-bounds/pull/4735)
at `4afbea22e79e19d1d65702eb4090d454ee39d967`.
Its rank-one proof already uses an extension lemma for an inclusion and an
observation map. Allowing their source to have dimension `r+s` gives a complete
invariant for **ordered idempotents of any ranks over any field**. This note
states that extension explicitly, supplies the precise realizability condition
and exact removable zero-space dimension, and checks the invariant against
direct matrix conjugation on complete small domains.

The result is an algebraic state descriptor. It supplies no header count,
physical implementation, selected-caller binding, supplier admission or exponent
improvement. It does not claim a polynomial time canonical-form algorithm.

## 1. Statement

Let P,Q be idempotents on an n-dimensional vector space V over a field F,
with ranks r,s. They need not commute. Choose rank factorizations

```text
P=XY, YX=I_r,       Q=ZW, WZ=I_s.
```

Here X,Z are injective and Y,W are surjective. On U=F^r direct-sum F^s put

```text
C=[X Z]: U -> V,       D=[Y;W]: V -> U,
K=ker C,               L=im D,
M=DC = [ I_r  YZ ].
       [ WX   I_s ]
```

K and L are **actual subspaces of U**, not just their dimensions. Let
g=diag(A,B), with A in GL_r(F), B in GL_s(F). Its action on the datum is

```text
(K,L,M) -> (g^-1 K, g^-1 L, g^-1 M g).                 (1)
```

**Complete invariant.** Two ordered pairs are simultaneously conjugate if
and only if their fields, n,r,s agree and their triples (K,L,M) have the same
orbit under (1). Rank-factorization bases do not affect that orbit.

**Realizability.** A triple of subspaces K,L of U and an endomorphism M of U
with diagonal blocks I_r,I_s is realizable in dimension n exactly when

```text
K subset ker M,       im M subset L,
n >= a+b-c,
a=(r+s)-dim K,        b=dim L,        c=rank M.          (2)
```

**Exact active dimension.** The pair is conjugate to a pair on a space of
dimension

```text
d_active = a+b-c                                     (3)
```

direct-summed with two zero operators on dimension n-d_active. No larger
simultaneous zero direct summand can be removed. In particular

```text
d_active <= r+s+min(r,s),                            (4)
```

and this bound is sharp over every field for every pair of nonnegative ranks.
For r=s it is the sharp bound 3r. Ambient n must still be retained in a
header-counting state: adding zero dimensions changes its header ensemble.

## 2. Proof of completeness

First consider arbitrary systems C:U->V, D:V->U and C':U->V', D':V'->U
with equal ambient dimensions and exactly equal data ker C=ker C',
im D=im D', and DC=D'C'=M. This is the extension argument of PR4735 with
no restriction on dim U.

Let A0=im C and B0=ker D, and use primes for the other system. The map

```text
f0(Cu)=C'u
```

is a well-defined isomorphism A0->A0', because the two C kernels agree.
It satisfies D'f0=D on A0. Consequently it maps A0 intersect B0
isomorphically onto A0' intersect B0'. Since the D images and ambient
dimensions agree, dim B0=dim B0'. Extend this restriction to an isomorphism
fB:B0->B0'. The maps f0,fB agree on the intersection, so they combine to
an isomorphism on A0+B0 that still satisfies D'f=D.

Choose a basis of a complement of im M in the common space L=im D. Choose
one lift of each basis vector in V and one in V'. These lifts complement
A0+B0 and A0'+B0', respectively, because D induces an isomorphism

```text
V/(A0+B0)  ->  L/im M.
```

Mapping corresponding lifts extends f to an isomorphism V->V' with
fC=C' and D'f=D. This proves sufficiency for the system datum. Necessity
follows immediately from these two intertwining equations.

Apply the system result to the displayed rank factorizations. If the data
agree, fX=X', fZ=Z', Y'f=Y, W'f=W; therefore

```text
fP=fXY=X'Y=X'Y'f=P'f,       fQ=Q'f.
```

Changing the image bases of P,Q gives C->Cg and D->g^-1D, exactly (1).
Conversely, conjugation of an ordered pair carries each image basis to an
image basis of the corresponding projector, giving such block changes of
basis. Thus equality of the orbit is both necessary and sufficient. No
commutation, orthogonality, invertibility of M or equal-rank assumption was
used. The proof also includes rank-zero factors with their empty spaces.

## 3. Proof of realizability and the active-space formula

For any system, K subset ker M and im M subset L are necessary. Moreover

```text
dim(im C intersect ker D) = a-c,
dim ker D = n-b.
```

The intersection lies in ker D, so n>=a+b-c. Conversely take C to be the
quotient map U->U/K, followed by inclusion into the first a dimensions of V.
On im C define D(Cu)=Mu; this is well-defined by K subset ker M and has
image im M. Add b-c new independent directions whose D images are a basis
of a complement of im M in L, and send the remaining directions to zero.
Condition (2) is precisely the space needed for this construction. It has
the prescribed K,L,M. Splitting C into columns X,Z and D into rows Y,W,
the identity diagonal blocks of M give YX=I_r and WZ=I_s. Hence XY,ZW
are idempotents of ranks r,s. This proves (2) constructively.

For an existing pair, let T be the sum of im C and the b-c lifts just
described. Then dim T=a+b-c and T intersect ker D=im C intersect ker D.
Choose Z0 complementary to that intersection in ker D. We obtain
V=T direct-sum Z0. Both projectors have image in im C subset T and kill
Z0, so this is the asserted simultaneous zero decomposition. Any zero
summand must lie in ker D and be disjoint from im C, so its dimension is at
most (n-b)-(a-c)=n-d_active. This also proves minimality in (3).

Since a,b<=r+s and M has identity diagonal blocks, c>=max(r,s). This proves
(4). To attain it, use direct sums of the following rank-one pair:

```text
P* = [1 1 0],      Q* = [0 0 0].
     [0 0 0]           [1 1 1]
     [0 0 0]           [0 0 0]
```

Over every field, a=b=2 and M is the 2-by-2 all-ones matrix of rank one;
therefore d_active=3. Take min(r,s) copies, and append |r-s| one-dimensional
blocks with (P,Q)=(1,0) or (0,1) to supply the excess rank. The dimension is
3 min(r,s)+|r-s|=r+s+min(r,s). Both-zero ranks give active dimension zero.

The active formula can also be computed directly from the pair, without
choosing its factors:

```text
a = rank [P Q],       b = rank [P;Q],
c = rank [P  PQ].
         [QP Q ]
```

For c, the displayed block matrix factors as diag(X,Z) M diag(Y,W), whose
outer maps are respectively injective and surjective, so its rank is rank M.
These formulas describe algebraic dimension; they assign no execution cost.

## 4. Verification and boundaries

The standard-library verifier imports no predecessor code or mathematical
inputs, writes no files, and uses explicit exceptions active under -O. Run

```sh
python -B scripts/research_package.py --package research/idempotent-factor-invariant
```

The registered commands run both ordinary and optimized Python 3.12. A
Git-free package export can instead run `python -I -W error -O -B verify.py`.
The scientific marker is `PASS_IDEMPOTENT_FACTOR_INVARIANT`.

Each census fixes P=diag(I_r,0), enumerates **every** second idempotent Q of
rank s, and compares two classifications. The direct matrix calculation
conjugates Q by GL_r x GL_(n-r), the full centralizer of P. The proposed
invariant acts on its factor data by GL_r x GL_s. Every direct class must have
one signature and every signature one direct class. This covers all ordered
pairs up to conjugacy because every first rank-r idempotent is conjugate to
that fixed P; it does not literally loop over every first P.

| Field order | n | (r,s) | Second projectors | Direct classes | Direct/factor group orders |
|---:|---:|---:|---:|---:|---:|
| 2 | 4 | (2,2) | 560 | 30 | 36 / 36 |
| 2 | 4 | (1,2) | 560 | 8 | 168 / 6 |
| 2 | 3 | (1,2) | 28 | 7 | 6 / 6 |
| 2 | 3 | (1,1) | 28 | 7 | 6 / 1 |
| 3 | 3 | (1,1) | 117 | 8 | 96 / 4 |
| 3 | 2 | (1,1) | 12 | 7 | 4 / 4 |
| 4 | 2 | (1,1) | 20 | 8 | 9 / 9 |
| 5 | 2 | (1,1) | 30 | 9 | 16 / 16 |

Every one of these 1,355 cases also reconstructs a pair from its abstract
datum, checks the factor identities, compares its orbit and independently
normalizes the reconstructed first projector to check direct conjugacy. The
coordinate-free block-rank formula for d_active is checked separately. Sixteen direct-sum
fixtures attain (4) at rank pairs (1,1),(2,2),(3,2),(2,3) over all four fields.
Eleven semantic controls distinguish dropping K, L, M or n, reject too-small
ambient dimensions, incompatible K/L/M, nonidempotence and invalid field
entries, and distinguish F4 from integer arithmetic modulo four. F4 is
F2[x]/(x^2+x+1). The universal statements rest on the written proofs, not these
finite samples.

Observed local verification used CPython 3.12.10 on Windows. Metadata and both
registered ordinary/optimized commands passed. The first wrapper attempt passed
its scientific command but hit a sandbox TEMP cleanup permission error; setting
TEMP and TMP to a writable run-local directory allowed the complete unchanged
wrapper to pass. This is an environment limitation, not a scientific failure
or a portability repair in this package.

The implementation enumerates small groups and bounded matrix domains. The
largest raw matrix domain is 2^16; it does not enumerate GL4 or GL5. It is
not an efficient general canonical form: enumeration remains exponential in
the ranks. No higher-rank transition probabilities, full-guard recurrence
values, header cover, physical reads, dirty restoration, precision/tape,
stock, dispatch or complete consumer bill is supplied. These obligations
remain unknown. No selected cold replay, Lean or Docker run is required by
this isolated algebraic package, and none is claimed.

## 5. Sources, scope and attribution

Canonical base is `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7,
selected conditional kappa 60403/20000000 (#4470). The task is a **changed**
formal-interface-lemma card, a written side result rather than a formal proof
or selected-caller binding. Current selected-baseline orientation was attempted
but stopped because the sparse checkout omits certificates/frontier4470/CLAIM.json;
no selected-baseline pass is claimed. The scientific verifier needs none of
the omitted inputs. The family decision is **narrow, then stop** after this
classification lemma and its corroboration. It justifies no construction
expansion from a positive count or an unpriced consumer.

- **codyw912, PR4735**, `4afbea22e79e19d1d65702eb4090d454ee39d967`: the
  sufficient binary rank-one invariant, inclusion/observation extension
  argument and explicit higher-rank question. This proof generalizes that
  argument; its mathematical idea retains this credit. Substantial GPT-6
  Astra assistance is disclosed in that predecessor.
- **Mihir Srivastava, PR4689**, `3a72fbad148294aa9ca7f900a48dbb10e64232be`:
  seven residual states and finite full-guard counts, with Codex assistance.
  Their numerical results are not reproduced or claimed here. The direct
  centralizer calibration follows the image/kernel block method explained
  in PR4735; the factor invariant does not depend on those seven states.
- **ssafwann, PR4678/PR4671**: one-block counts, sector criterion and the
  earlier residual-state handoff; **Nick Petalas, PR4597 and its lineage**:
  ordered Schur and header questions; **Ryanson Jonathan**: full-guard census;
  **lee-phys**: binary dimension work; **Cinna Davis, PR4100**, and source527,
  commdata2338, Jose Manuel: the earlier request/normalizer context.
- **Nick Petalas, PR4240**, `9f9c89ed75e9fdae6b6762925b080fb308824858`,
  already proves the all-finite-field rank-one joint header law. The seven
  binary terminal counts are not an uncovered counting theorem. That overlap
  was found before starting this higher-rank task and is not republished as
  a new result.

SOURCES.json pins only canonical-main historical provenance. Exact pending
heads and README byte hashes are citations in TASK.json, not executable or
Git-history dependencies. No frozen archive or predecessor package changes.
Repository tooling retains its authors' attribution. No global mathematical
novelty or independent human acceptance is asserted.

Submission overlap also found Nick Petalas's
[PR4746](https://github.com/CrocSwap/integer-mult-bounds/pull/4746), which
extends the initial commuting identity-pivot dimension theorem to arbitrary
fields. It studies a prescribed product compression and maximal Schur rank;
this note classifies arbitrary ordered, possibly noncommuting residual pairs.
No dimension-minimum or header-count number from that proposal is claimed here.

## Open next questions

1. Can this complete descriptor yield a useful higher-rank transition table
   for one actual residual ensemble? The invariant controls state identity,
   which is needed to avoid merging states with different continuations.
   First compute split transitions for one fixed (n,r,s) and aggregate by the
   descriptor, retaining multiplicities. Enumeration of the active group is
   still exponential, and no transition cost or paid caller is supplied here.
2. Can actual odd-field requests use a fully charged header cover? This is
   needed before any supplier consequence. First pin one producer and its
   field, then price selection, emission, reads, dirty return and stock.
   The algebraic descriptor supplies none of that implementation contract.
