# Sharp pairing cost for binary decoders on the 40 Eisenstein lines

We prove **C >= 40** for the scalar rectangle model in Jonathan Lam's
[PR #798](https://github.com/CrocSwap/integer-mult-bounds/pull/798), and use
his row-star construction to attain equality. We allow arbitrary supports,
asymmetric readers and sources, any finite number of terms, and XOR
cancellations. We do not require clean rectangles or a minimum-rank decoder.

We obtain the lower bound by reducing a normalized Hermitian Gram matrix
modulo 2 and applying rank subadditivity to a Hadamard product. DreamingOfClouds
used the same-field rank argument in Lemma B of
[PR #1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590).
We add the good-reduction certificate and pairing-rank comparison for this
Eisenstein geometry. With these steps, we close
the scalar cost interval left by the floor 22 in #798, the floor 23 in
[PR #1977](https://github.com/CrocSwap/integer-mult-bounds/pull/1977), and
the non-clean cost screen in
[PR #1794](https://github.com/CrocSwap/integer-mult-bounds/pull/1794).
We retain the selected multiplication exponent.

## Exact model

Use the 240 doubled E8 roots and the order-three orthogonal action J from
Joel Pulikkan / GamingPuzzled's PR #620, as reconstructed by Jonathan Lam
in `research/eisenstein-clique-copy-bound/geometry.py`. We pin that file in
`SOURCES.json`. Its six-root orbits under +/-J give 40 lines over
K = Q(omega), where omega^2 + omega + 1 = 0 and multiplication by omega
acts as J. Write r_i for a representative of line i.

For a set S of lines, write X_S for the rational span of r_i and Jr_i.
For any rational row bases V_R and V_A of X_R and X_A, define

    c(R,A) = rank_Q(V_R V_A^T)/2.

Choose any binary matrix B satisfying

    B_ii = 1;
    B_ij = 0 when i != j and lines i,j are nonorthogonal.

The entries at orthogonal pairs may differ in the two directions. Choose
any finite decomposition over F2,

    B = sum_j 1_Rj 1_Aj^T,
    C = sum_j c(R_j,A_j).

**Theorem.** For every such B and decomposition, C >= 40. For each fitting
B, a row-star decomposition has C = 40. Thus each fitting B has minimum
abstract cost 40, regardless of its binary rank.

We prove a finite algebraic statement. A researcher who interprets C as a
physical COPY charge must establish the corresponding implementation
premise. We do not establish the unreviewed physical premise that earlier
authors traced to PR #446.

## Proof

### 1. An integral Hermitian Gram matrix at the prime 2

For x,y in Q^8, put d0 = x dot y and d1 = x dot Jy. Define

    h(x,y) = (d0 - d1 - omega*(d0 + 2*d1))/12.

Using J^2+J+I = 0 and orthogonality of J, we obtain

    h(x,Jy) = omega*h(x,y),
    h(Jx,y) = conjugate(omega)*h(x,y),
    h(y,x) = conjugate(h(x,y)),
    x dot y = 4*Tr_(K/Q)(h(x,y)).

Thus we may regard h as a Hermitian form on the four-dimensional K-space.
For a root r, we have r dot r = 8 and r dot Jr = -4, hence h(r,r) = 1.
Two lines are orthogonal exactly when both d0 and d1 vanish, which is
equivalent to h(r_i,r_j) = 0.

Write H_ij = h(r_i,r_j). The doubled-root inner products d0 and d1 are
multiples of 4, including after J permutes the roots. Therefore

    H_ij in S = Z[omega,1/3].

We can reduce S modulo 2. Since t^2+t+1 is irreducible over F2, we obtain
S/(2) = F4. Write Hbar for the entrywise reduction. We retain the diagonal
ones and the zeros at orthogonal pairs. We do not need to assume that a
nonzero off-diagonal entry stays nonzero, although the finite replay also
checks that property for this geometry.

We reduce this fixed Gram matrix. We never reduce an arbitrary rational
row basis, whose denominators might include 2.

### 2. Pairing cost bounds the reduced submatrix rank

We first identify

    rank_K H[R,A] = c(R,A).

The representatives r_i span X_R and X_A over K. A vector x in X_R
annihilates the rational pairing with X_A exactly when h(x,y) = 0 for
all y in X_A. Indeed, rational annihilation gives both
Tr(h(x,y)) = 0 and Tr(omega*h(x,y)) = 0, because Jy also lies in X_A.
For z=a+b*omega these two traces are 2a-b and -a-b; over Q their joint
vanishing forces a=b=0. The converse follows from the trace formula.
We have therefore identified the two radicals. Their K-dimensions are
half their rational dimensions, proving the rank equality.

Next, if rank_K H[R,A] = c, every (c+1)-minor vanishes in K. Each minor
lies in S, a subring of K, so it vanishes in S and after reduction to F4.
Consequently

    rank_F4 Hbar[R,A] <= rank_K H[R,A] = c(R,A).       (1)

This proof covers arbitrary line subsets, including empty sets. We do not
need to enumerate flats or assume nonsingular restricted spans.

### 3. The fitting identity forces total rank 40

Embed B and its binary decomposition in F4. Denote the entrywise product
by "o". The fitting conditions and the Gram zeros give

    Hbar o B = I_40.

Distributing over the rectangle sum gives

    I_40 = sum_j diag(1_Rj) Hbar diag(1_Aj).

The j-th summand has rank rank_F4 Hbar[R_j,A_j]. Rank subadditivity and
(1) imply

    40 <= sum_j rank_F4 Hbar[R_j,A_j] <= C.

The equality before the rank estimate holds in characteristic two, so we
have included overlapping supports and XOR cancellations.

For the matching upper bound, decompose B by rows. In row i choose
R_i={i} and A_i={j:B_ij=1}. The set A_i contains i and otherwise contains
only lines orthogonal to i. Hence H[{i},A_i] has one nonzero entry and
rank one. The 40 rows give C=40. This construction and its cost already
appear in #798; our contribution is the matching lower bound.

### 4. Binary minrank and minimum-rank support rigidity

We also recover the known binary minrank 10 without a SAT premise. If B
has binary rank h, factor it into h binary rank-one matrices. Each support
pair costs at most four, since K has ambient dimension four. The theorem
gives 40 <= 4h, hence h >= 10. The known partition into ten orthogonal
four-frames attains h=10: put an all-ones block on each frame. We replay a
literal partition and verify its fitting conditions and rank.

If B has rank 10, every nonzero vector in its row space and every nonzero
vector in its column space has support spanning the full four-dimensional
K-space. For example, suppose a row-space vector had support of K-rank
at most three. Extend it to a binary row-space basis. The resulting
ten-term factorization would cost at most 3+9*4=39, a contradiction.
Use a column-space basis for the other assertion. Thus a researcher
cannot build a rank-10 decoder from even one hyperplane-supported basis
vector, regardless of the other nine basis vectors.

## Fixed-support block-linear corollary

Suppose port t holds an independent b_t-bit vector. Message j consists of
q_j fixed binary linear forms in the inputs at A_j, and each receiver in
R_j receives that message. Receiver t also knows the full inputs at ports
orthogonal to t. Assume exact recovery on every input and the additive
pricing premise

    C = sum_j q_j*c(R_j,A_j).

Then **C >= sum_t b_t**, with equality from direct messages. In particular,
block-linear coding at equal demand b costs at least 40b.

To prove this, choose a linear recovery map for each demanded bit. Such a
map exists even if the declared decoder was nonlinear: exact recovery of
a linear coordinate from linear observations means that the observation
kernel lies in the coordinate kernel. The coordinate therefore belongs
to the observation row space.

Stacking these maps gives a block matrix B=sum_j D_j E_j over F2, with
diagonal blocks I_(b_t) and zero blocks at distinct nonorthogonal ports.
Here D_j has q_j columns, E_j has q_j rows, and their nonzero port blocks
lie in R_j and A_j. Lift Hbar by replacing Hbar_st with the constant
b_s by b_t block of that value. Call the resulting matrix G. Then

    G o B = I_(sum_t b_t).

Expand D_j E_j into its q_j rank-one terms. Each term after entrywise
multiplication has rank at most rank_F4 Hbar[R_j,A_j]: repeating rows and
columns to form G does not increase rank, and diagonal weighting cannot
increase it. Sum these bounds and apply (1).

We have not extended this argument to nonlinear encoders. The earlier
Michael Fischler's `eisenstein-message-copy-bound` package treats a broader nonlinear message
model and proves a different lower bound. We leave its nonlinear claims
and their attribution unchanged. Adaptive supports and pricing shared
physical work below the declared additive charge also remain outside our
theorem.

## Consequences and limits

Under the specific accounting in Maximooch's #1794 screen, a supplier
that beats the selected construction would need C <= 31, or C <= 29 at
window h=10. Our lower bound excludes those costs for the stated scalar
model. We do not rerun that screen here; we pin its incorporated receipt
as provenance and state this consequence conditional on its accounting.
The proof C=40 does not depend on the screen or the selected exponent.

The ten-source proposal that motivated this check also fails. If each
source lies in one orthogonal 12-line hyperplane, each term costs at most
three. Ten such terms would cost at most 30, contradicting the theorem,
even with unrestricted asymmetric reader sets.

Researchers can still change the geometry, scalar field, support model,
message nonlinearity, or physical pricing premise. We have not proved a
barrier for arbitrary integer multiplication algorithms or for the native
paired-log constructions that motivated our separate investigation.

## Reproduction and evidence

Run from the repository root with Python 3.12 and its standard library:

```sh
python3.12 scripts/research_package.py --package research/eisenstein-reduction-copy-floor
```

For a direct replay under an optimized interpreter:

```sh
python3 -I -O -B research/eisenstein-reduction-copy-floor/verify.py
```

We reconstruct the pinned geometry, check all 1,600 Hermitian entries,
6,400 rational trace identities, the quotient-field arithmetic, and all
Gram-value reduction identities. We also compare rational, K and F4
ranks on 209 boundary or deterministic sample blocks, check 40 hyperplane
column ranks, and replay two cost-40 row-star witnesses plus a non-clean
cost-48 cancellation witness. We verify the rank-10 frame partition, a
two-bit sharp frame code and 16 mixed-bit block estimates. Seven corruption
controls exercise diagonal, orthogonality, fitting, demand, denominator
and per-bit pricing assumptions. Acceptance
checks use explicit exceptions and remain active under `-O`.

The sample rank comparisons corroborate the proof in Section 2. We use
the radical and minor arguments there to cover arbitrary supports; we do
not infer that universal statement from samples. We claim a written proof
with exact finite checks, without proof-assistant formalization.

## Open next questions

- Can nonlinear encoding lower cost below 40b under the fixed-support,
  per-bit pairing charge? A researcher can start with one orthogonal
  frame and one non-clean message, then test exact decoding and compare
  with the existing nonlinear floor. The Schur-rank proof requires linear
  encoders, so it leaves this question open.
- Can a native supplier share physical work across messages and escape
  the additive pairing charge? A researcher must specify a complete
  source/reader/frame contract and price one small instance. We do not
  have such a contract, and a cheaper abstract rectangle search within
  the present model cannot supply one.

## Attribution

Jose Manuel (@jmbarrancoml), with substantial OpenAI Codex assistance in
the proof, implementation and prose. A read-only mathematical agent
identified the reduction argument during a ten-source construction
search; the primary agent derived the trace/rank proof and implemented
the replay. We have not obtained independent human review.

Joel Pulikkan / GamingPuzzled (#620) supplied the Eisenstein geometry.
Jonathan Lam (#798) supplied the exact pairing-cost model, geometry code,
floor 22 and row-star upper bound. Josie Elliston (#1977) obtained floor
23 by principal-submatrix minrank, and Maximooch (#1794) derived the
cost screen and the clean-class floor. DreamingOfClouds (#1590, Lemma B)
gave the same-field Hadamard rank argument for another decoder model.
Michael Fischler (@shiftybitshiftr) treated fixed-support nonlinear messages
in `eisenstein-message-copy-bound`. We use standard specialization and
trace-pairing arguments with the Hadamard bound to obtain the sharp cost.
We preserve their packages and licenses. See `SOURCES.json` for exact pins.
