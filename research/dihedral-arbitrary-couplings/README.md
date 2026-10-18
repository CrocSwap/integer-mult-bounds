# dihedral-arbitrary-couplings
# Arbitrary binary couplings do not reduce the dihedral rank tariff

**Scoped written theorem; no new kappa.** Adam Gall's [PR1911](https://github.com/CrocSwap/integer-mult-bounds/pull/1911)
already proves the sharp infinite-dihedral tariff for rank-one **idempotent**
couplings. This package extends the gate alphabet to **every binary matrix N**,
including nilpotents and nonprojectors of higher rank, charging each gate
**rank(N)**. The same separate label tariffs remain exact for every finite
number of registers. The new implication is the minor-degree bound without
diagonalizability; the representations, endpoint valuation and attaining words
are credited to PR1911.

This is a rank bill, not an invocation lower bound. A single gate with N=I
acts on all R roles and is charged R. It is not evidence that an arbitrary
rank-R gate costs R native supplier children.

## Alphabet and theorem

Let G be the infinite dihedral group with presentation
G = <r,s | r^2=s^2=1>. Work in M_R(F2[G]), R>=W. Allow arbitrary scalar
GL_R(F2) changes at zero cost, and paid gates

    D_N(g) = I + ([g]+1) N,    g in {r,s}, N any binary R by R matrix.

The price is rank(N), separately for each label. A zero coupling is the identity
and costs zero. Group coefficients commute with scalar entries. Since
([g]+1)^2=0 in characteristic two, **D_N(g)^2=I for every N**; neither
N^2=N nor rank one is required.

All target and spectator inputs are arbitrary dirty data. The endpoint is exactly

    diag([(rs)^k_1 r^e_1], ..., [(rs)^k_W r^e_W], 1, ..., 1),

where k_i are integers and e_i in {0,1}. No erasure, COPY, clean state, direct
rotation or other address primitive is free. Every restoration is part of the
word. Then every program satisfies

    sum over r gates rank(N) >= A = sum_i |k_i+e_i|,
    sum over s gates rank(N) >= B = sum_i |k_i|.

The two bounds are attained simultaneously. Positive per-rank prices alpha,
beta therefore have exact minimum alpha*A + beta*B, even with arbitrarily many
restored dirty spectators and free scalar mixing.

## Proof: replace the projector-similarity step

Use PR1911's two Laurent representations over L=F2[t,t^-1]:

    C = [[0,1],[1,0]], V = [[0,t],[t^-1,0]],
    rho(r)=C, rho(s)=V; sigma(r)=V, sigma(s)=C.

They are representations because C^2=V^2=I. Formal equality implies represented
equality; the converse is never used. Let delta(M) be the largest degree among
all nonzero square minors, including the empty minor 1. Cauchy--Binet gives
delta(MP)<=delta(M)+delta(P). Every constant invertible matrix, including
represented free scalar changes, has delta zero.

**Rank-leading-coefficient lemma.** If M=tB+A+t^-1 C0 over a field and
rank(B)=q, every square minor has degree at most q. Expand a minor by
multilinearity in its columns. A term choosing more than q columns from B has
linearly dependent chosen columns, even after restricting to the minor's rows,
so its determinant vanishes. Every other term has degree equal to the number
of B columns minus the number of C0 columns, at most q. This argument includes
all minor sizes, arbitrary A and C0, and possible cancellation.

In fact delta(M)=q: if q>0 choose a nonzero q by q minor of B. The coefficient
of degree q in the same minor of M is precisely that determinant. For q=0
the upper bound and empty minor give equality. This equality concerns the
maximum over **all** minors, not the full determinant.

For a represented V gate,

    rho(D_N(s)) = I + N tensor (I+V)
               = t (N tensor E01) + (I+N tensor I) + t^-1 (N tensor E10).

The positive coefficient has rank rank(N), so
delta(rho(D_N(s)))=rank(N). A represented C gate is constant,
invertible, and has delta zero. Interchanging r and s gives

    delta(rho(D_N(r)))=0,        delta(rho(D_N(s)))=rank(N),
    delta(sigma(D_N(r)))=rank(N), delta(sigma(D_N(s)))=0.

No similarity or projector assumption appears here. In particular a nonzero
square-zero N is covered, although it cannot be similar to a nonzero projector.

As in PR1911, each target block is a monomial permutation matrix. Its exponents
under rho are -k_i,k_i, and under sigma are k_i+e_i,-(k_i+e_i).
Selecting all positive entries gives endpoint deltas B and A; no minor can
exceed their sum. Spectator identity blocks add zero. Subadditivity through
every paid and free gate proves both lower bounds directly, without needing
to normalize away the scalar changes.

For attainment, use coordinate projectors and the freely reduced literal word
(rs)^k_i r^e_i on each target. It contains |k_i+e_i| r labels and |k_i| s
labels. Different target coordinates commute. The formal group-algebra
identity establishes the endpoint and restores all spectators uniformly.
With left matrix actions execute the displayed word from right to left.
No basis changes or spectator roles are needed for this attaining word.
This matching construction and its tariff are inherited from PR1911.

## Exact factorization and a dirty-state implementation invoice

Binary rank factorization gives N=UV=sum_{j=1}^q u_j v_j^T with exactly
q=rank(N) nonzero rank-one terms. For a fixed reflection g and Q=[g]+1,

    product_j (I+Q u_j v_j^T) = I + Q sum_j u_j v_j^T = D_N(g),

because every cross term contains Q^2=0. The binary matrices need not commute.
This is an identity in the full group algebra, and decomposes the arbitrary
gate at exactly the same formal rank tariff into rank-one gates of the
**enlarged** alphabet. It does not pretend that every term is a projector.

For a rank-one term uv^T, put theta=v^T u. If theta=1, choose a binary basis
S with first column u and remaining columns a basis of ker(v^T). Then
S^-1 uv^T S=E00 and the canonical operation is one g on role 0.
If theta=0, choose w with v^T w=1 and extend u to a basis of ker(v^T);
the ordered columns [u,w,remaining kernel basis] give E01. Its canonical
operation, in chronological order, is

    a ^= b;  b <- g(b);  a ^= b;  b <- g(b).

It leaves a+(I+g)b in a and restores arbitrary dirty b. All other roles are
untouched. These identities hold for every involutory linear address action
g, not just the finite fixture in the checker.

Apply S^-1 before the canonical operation and S after it. Gaussian row
elimination implements these with scalar whole-register XOR additions,
including a three-XOR swap when needed. If c(S) is the emitted number of row
additions for S^-1, its reverse emits S and

    c(S) <= R(R-1)+3(R-1).

A rank-one projector therefore uses one address call and 2c(S) scalar XORs.
A nilpotent uses **two** address calls and 2c(S)+2 scalar XORs. For a chosen
rank decomposition with z nilpotent factors, the arbitrary gate uses exactly
q+z<=2q address calls and 2 sum_j c(S_j)+2z scalar XORs. All R roles can
start dirty; no extra data array or clean bit is assumed. An explicit schedule
has O(q R^2) operation descriptors. A scalar whole-array XOR costs L bit XORs
for arrays of length L; the address permutation has its own swap/address cost.

This is a uniform algebraic implementation and word-level invoice. It is not
a native C++ engine admission, an optimized finite-array algorithm, or an
all-size tape/compiler theorem. The lower-bound relaxation optimistically
prices every rank-one coupling at one, including the nilpotent case whose
supplied physical word uses two address calls. Charging more cannot invalidate
the lower bound, but does not identify these tariffs with recursive child rank.

## Reproduction and evidence

    python3.12 -I -O -B research/dihedral-arbitrary-couplings/verify.py
    python3.12 scripts/research_package.py --package research/dihedral-arbitrary-couplings

Default verification is read-only. Explicit --write regenerates RESULT.json.
The source README is authenticated by SHA-256 and Git blob hash before
mathematical checks; Git-free exports must include that declared input at its
repository-relative path. The generic runner additionally audits historical
task and selected-record provenance.

The independent finite checks cover all **530 binary matrices** for R=1,2,3:
**473,690 nonempty Laurent minors**, exact rank factorization, full F2[C2]
coefficient convolution, involutions, and compiled dirty-input endpoints.
They also cover all **284 nonzero rank-one matrices** for R=1,2,3,4,
including **129 nilpotents**, with **4,264 symbolic input columns**; every
output row is compared, not just clean inputs or source-only columns.
Thirty-four signed target words have independently reduced literal and
integer normal-form endpoints and matching separate tariffs.

Five controls expose the invalid projector premise, underpricing rank as
invocations, missing source restoration, missing identity summand, and reversed
basis orientation. Git-free CLI tests check read-only success, source
corruption, Boolean/float receipt substitutions, and actual implementation
mutations. Checks remain active with Python -O. The universal theorem is the
written proof above; finite checks are corroboration, not a Lean proof or
exhaustive search over unbounded words.

## Sources, overlap, and limits

Scientific and task base: 6bd33bc0b87a01e9c9d8b1c01576f3ddbcaee850, priority 5.
The prescribed baseline passed before selection. SOURCES.json pins the retained
PR1911 README, selected record and task catalogue. Exact predecessor head:
712593f82739203639d0a169b88c6bcac6f0590c, Adam Gall. Its all-register projector
theorem, representations, target computation, direct witnesses and predecessor
attribution remain credited. An initial projector-only proposal was retired
as duplicate before this package was written.

Related work was checked before choosing this cut:

- [PR1941](https://github.com/CrocSwap/integer-mult-bounds/pull/1941) already
  includes arbitrary-rank **idempotent** prices in a finite even-dihedral
  model. No novelty is claimed for merely replacing a projector by higher rank.
- [PR1589](https://github.com/CrocSwap/integer-mult-bounds/pull/1589),
  Arham Tahir, head 010ec8c01c0edbbb08b541be236ab78d096f2ca1, removes the
  projector premise for UT3 central targets using a mixed-coefficient rank
  argument. It motivates the premise audit; it is not an infinite-dihedral
  arbitrary-target theorem.
- [PR2290](https://github.com/CrocSwap/integer-mult-bounds/pull/2290),
  Cinna Davis, head 8839972a3cc939ebc17562473082189ea166d7de, adds nilpotents
  in a shallow two-role census. That finite search does not supply this
  all-length, all-register rank tariff.

Overlap included open PR bodies, retained closed/merged notes and ledger, and
targeted REST searches. Cached Discussions cover 1,239 records at 15:22Z on
2026-10-15; later claims may be missing. TASK.json records snapshot freshness.
No no-match search proves novelty; arbitrary code diffs were not exhaustively
searched. Coordination is on PR1911, comment 6198753145.

Finite cyclic actions identify group words and may have cheaper implementations.
The Laurent representation does not factor through those quotients, so this
lower bound is **not** transferred to finite-address permutations. No selected
cold replay, hosted CI, independent human review, supplier hosting/precision,
outer analytic transfer or new multiplication exponent is claimed.
Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.

## Open next questions

1. Find a torsion-aware analogue for finite dihedral targets; first test it on
   the quotient relation. The Laurent invariant cannot survive that relation.
2. Bind these primitives to an actual supplier invoice before using rank tariffs
   in adoption decisions. Begin with one reflection and every basis XOR; native
   hosting, scratch, child rank and recursive transfer remain unproved.
