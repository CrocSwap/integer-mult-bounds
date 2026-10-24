# Exact complete-header counts for a sharp Schur block

**Written counting theorem with exact finite corroboration; no new kappa.**
Prepared for **ssafwann** with substantial **OpenAI Codex (gpt-6-astra)**
assistance, by one agent. Apache-2.0.

[PR4671](https://github.com/CrocSwap/integer-mult-bounds/pull/4671) determines
when an identity-pivot Schur commutator attains rank 2d, and asks how often
complete headers satisfy its six map conditions. This package supplies an
exact count for **every fixed commuting binary idempotent pair**, in terms of
its four joint-sector dimensions. It retains the dependence through the common
compressed product H; it does not multiply the six marginal probabilities.

Two scalar examples have **60,480** and **181,440** sharp complete headers in
GL_5(F2), with exact densities **3/496** and **9/496**. The four equal
2-dimensional sectors have sharp density **27/2,763,520** at block size d=2.

**The sample space is complete headers; the acceptance event is one block.**
The event requires both leading d-by-d blocks to be I_d and their Schur
commutator to have rank 2d. It does **not** require every later leading minor
to pass. Thus this is not a full-guard-chain law, a physical caller, or a
supplier admission. The distinction matters when comparing the predecessor
full-guard counts of Nick Petalas and Ryanson Jonathan.

## 1. Exact count

Fix commuting idempotents P0,Q0 on V=F2^n. Their four joint eigenspaces have
dimensions r=(r00,r10,r01,r11), in that order, with nonnegative entries summing
to n. Choose a complete ordered header M uniformly from GL_n(F2), and put
P=M^-1 P0 M and Q=M^-1 Q0 M. This is equivalent to the G P0 G^-1 convention
in prior header work by taking G=M^-1. Fix 1<=d<=n.

Let Z count headers with both leading blocks I_d. Let N count such headers
whose Schur-commutator rank is 2d. When d=n the Schur space is zero and N=0.
All probabilities below concern fixed requests, chosen before the header.

Define the injection count

\[
I(s,k)=\prod_{j=0}^{k-1}(2^s-2^j)
\]

for 0<=k<=s, and zero otherwise. An empty product is one, so
|GL_0(F2)|=I(0,0)=1. Put G(s)=I(s,s) and

\[
{m\brack k}_2=I(m,k)/G(k)
\]

for 0<=k<=m, and zero otherwise. For a fixed T in M_d(F2) of rank rho,
define two counts of factorizations X Y=T through F2^r:

\[
U(r,d,\rho)=\sum_{k=\rho}^{\min(d,r)}
 {d-\rho\brack d-k}_2\, I(r,k)\,2^{d(r-k)}, \tag{1}
\]
\[
A(r,d,\rho)=
\begin{cases}
 I(r,d)\,2^{\rho(r-d)} I(r-d,d-\rho),&r\ge d,\\
 0,&r<d.
\end{cases} \tag{2}
\]

U allows arbitrary maps; A requires Y injective and X surjective. These
formulas depend on T only through its rank. Zero-dimensional sectors are
included: U(0,d,0)=1, while A(0,d,rho)=0 for d>=1.

For H in M_d(F2), write h=rank H and w=rank(I+H). Then the exact counts are

\[
\boxed{\begin{aligned}
N&=G(n-d)\sum_{H\in M_d(\mathbb F_2)}
 U(r_{00},d,w)A(r_{10},d,w)A(r_{01},d,w)A(r_{11},d,h),\\
Z&=G(n-d)\sum_{H\in M_d(\mathbb F_2)}
 U(r_{00},d,w)U(r_{10},d,w)U(r_{01},d,w)U(r_{11},d,h).
\end{aligned}} \tag{3}
\]

Thus the unconditional sharp density is N/G(n), and its conditional density
among identity-pivot headers is N/Z when Z>0. When Z=0, no conditional
probability is asserted. The sum retains the actual joint distribution of
rank H and rank(I+H). They must not be sampled independently.

This is a finite formula for every d, not an efficient large-d algorithm.
The checker groups the 2^(d²) matrices by their rank pairs and evaluates d<=3.
There is no quotient by a sector centralizer: different ordered headers are
different elements of the stated sample space, even when they conjugate the
pair to the same matrices.

## 2. Proof of the factor counts

For (1), condition on k=rank Y. The equation X Y=T is solvable exactly when
ker Y is a (d-k)-dimensional subspace of ker T. There are
`[d-rho choose d-k]_2` choices for that kernel. For any chosen kernel, there
are I(r,k) embeddings of the quotient F2^d/ker Y into F2^r, hence that many
maps Y with precisely this kernel. X is then uniquely prescribed on im Y
by X(Yv)=Tv. On a complement of dimension r-k, it is an arbitrary map to
F2^d, giving 2^(d(r-k)) choices. Sum over k. The Gaussian coefficient itself
counts subspaces because each has G(d-k) ordered bases, whereas the ambient
kernel has I(d-rho,d-k) ordered independent tuples.

For (2), there are I(r,d) choices for the injective Y. In a basis starting
with its image, write X=(T L). For X to be onto, the image of L in the quotient
F2^d/im T, of dimension d-rho, must be onto. There are I(r-d,d-rho) such
surjections. Each has 2^(rho(r-d)) lifts L, proving (2). This argument also
explains the zero count when r<2d-rho; injectivity alone is insufficient.

## 3. From sector factors to complete headers

Let i be the first d columns of M, and pi the first d rows of M^-1. Then
pi i=I. Conversely, every split pair (i,pi) with pi i=I has exactly
**G(n-d)** header completions: append any ordered basis of ker pi to i.
These are all the completions, and each header gives one split pair. Replacing
the kernel basis N by NK conjugates both Schur complements by K^-1 on the
left and K on the right. Thus their commutator rank is unchanged throughout
a completion fibre. In particular the total number of split pairs is

\[
I(n,d)2^{d(n-d)}=G(n)/G(n-d). \tag{4}
\]

The factor 2^{d(n-d)} belongs to choosing pi for a fixed i. It is not an
additional multiplier after the complete split pair has already been counted.
This extends the equal-completion principle in Nick Petalas's earlier scalar
header proofs to a d-dimensional block, with the full multiplicity retained.

Choose fixed bases in the four joint sectors. Let Y_j:U->V_j be the component
of i and X_j:V_j->U the restriction of pi. The identity-pivot conditions are

\[
\begin{aligned}
X_{10}Y_{10}+X_{11}Y_{11}&=I,\\
X_{01}Y_{01}+X_{11}Y_{11}&=I,\\
\sum_j X_jY_j&=I.
\end{aligned}
\]

Putting H=X11 Y11 gives

\[
X_{00}Y_{00}=X_{10}Y_{10}=X_{01}Y_{01}=I+H,\qquad X_{11}Y_{11}=H. \tag{5}
\]

Conversely, (5) implies all three equations, so it already enforces pi i=I,
including injectivity of the assembled i and surjectivity of the assembled pi.
There is no additional global compatibility test. Once H is fixed, the four
factorization choices are independent **as choices of maps in fixed sectors**.
Every resulting split pair determines H uniquely; summing over H does not
count a pair twice.

The six-map criterion from #4671, restated with proof below, says that sharpness
requires exactly the X/Y maps in sectors 10,01,11 to be onto/one-to-one. Thus
use U for sector 00 and A for the other three to count sharp split pairs.
Use U in all four sectors to count all identity-pivot split pairs. Multiply
both counts by G(n-d) to obtain (3). The whole derivation applies to any fixed
pair with these sector dimensions by simultaneous change of basis, which
permutes the uniform complete-header sample space.

### Credited six-map criterion, with its algebraic justification

Write P=[[I,R],[C,D]], Q=[[I,L],[E,F]], S=D+CR and T=F+EL. The ordered
factorization from Nick Petalas's #4597, specialized in #4657/#4671, is

\[
[S,T]=(TC\ \ C+E)\begin{pmatrix}R+L\\RT\end{pmatrix}. \tag{6}
\]

To check it directly, set J=(PQ)21 and B=(PQ)12. Commutation gives
RE=LC=H+I, DE=J+C, FC=J+E, RF=B+L, LD=B+R and DF+FD=ER+CL.
Expansion yields `[S,T]=J(R+L)+(C+E)B+CHL+EHR`, while TC=J+EH and RT=B+HL,
which verifies (6).

In ambient coordinates define

\[
\mathcal A=(QPi+QiH\ \ (P+Q)i),\qquad
\mathcal B=\begin{pmatrix}\pi(P+Q)\\\pi PQ+H\pi Q\end{pmatrix}.
\]

We have pi A=0 and B i=0. Corestricting A to ker pi and restricting B to
ker pi gives the two factors in (6). In sector coordinates,

\[
\mathcal A(x,y)=(0,Y_{10}y,Y_{01}(Hx+y),Y_{11}(I+H)x),
\]
\[
\mathcal B(v)=(X_{10}v_{10}+X_{01}v_{01},\ HX_{01}v_{01}+(I+H)X_{11}v_{11}).
\]

Sharpness makes A injective. A nonzero z in ker Y10 forces Hz=z and makes
A(z,z)=0; a nonzero z in ker Y01 forces Hz=z and makes A(z,0)=0; a nonzero
z in ker Y11 forces Hz=0 and also makes A(z,0)=0. Therefore all three Y maps
are injective. Apply the same argument to P^T,Q^T to obtain surjectivity of
all three X maps: rank(E_j^T i)=rank(pi E_j)=rank X_j.

Conversely injectivity of the three Y maps makes A injective: its zero vector
equations give y=0, Hx=0 and (I+H)x=0. A row (u,v) annihilating B must satisfy
u X10=0, (u+vH)X01=0 and v(I+H)X11=0. Surjectivity of the X maps gives
u=0 and v=0, so B is onto. Since B kills iU, its restriction to ker pi is
onto too. The product in (6) has rank 2d. This establishes the precise cited
criterion without importing a predecessor executable or relying on an
unavailable pending source at replay time.

## 4. Exact examples and a dependence countercheck

The table reports both the complete-header count and the correct denominator.
A split pair includes a labeled d-dimensional inclusion and its projection.

| Sector dimensions (00,10,01,11) | d | Identity-pivot split pairs | Sharp split pairs | Sharp complete headers | N/G(n) | N/Z |
|---|---:|---:|---:|---:|---:|---:|
| (1,1,1,2) | 1 | 172 | 3 | 60,480 | 3/496 | 3/172 |
| (0,2,2,1) | 1 | 100 | 9 | 181,440 | 9/496 | 9/100 |
| (2,2,2,2) | 2 | 1,932,288 | 2,592 | 52,251,375,697,920 | 27/2,763,520 | 27/20,128 |

The first two pairs both have rank P0=rank Q0=3 in dimension five, yet
their sharp densities differ by a factor of three. Individual projector ranks
alone do not determine the count.

For the first two rows, G(4)=20,160 and G(5)=9,999,360. In the third row,
G(6)=20,158,709,760 and G(8)=5,348,063,769,211,699,200.
At (2,2,2,2), sharpness permits only the two H for which both H and I+H are
invertible; each contributes G(2)^4=1,296 split pairs.

There is a simple numerical check against the independence shortcut. Among
the 100 identity-pivot split pairs for (0,2,2,1), the six full-rank event counts
are **60,60,60,60,100,100**. Their joint fraction is **9/100**. Multiplying
marginals instead gives **81/625**, a different number. For (1,1,1,2), the
marginal counts are 64,64,64,64,168,168 among 172, and again their product
differs from the joint fraction 3/172. The sum over shared H in (3) retains
this dependence.

## 5. Verification and reproduction

```sh
python3.12 -B scripts/research_package.py --package research/schur-header-count
python3.12 -B scripts/check_research_commit.py --package research/schur-header-count --check-source-history
```

The standard-library verifier prints `PASS_SCHUR_HEADER_COUNT`. Registered
ordinary and optimized (`-O`) modes use explicit exceptions, not assertions.
A Git-free exported package can run `python3.12 -I -W error -O -B verify.py`.
No external mathematical input, compiler or predecessor executable is needed.

The checks deliberately use direct matrix calculations separately from the
counting formulas:

- All **270,759** pairs (X,Y) with d=1,2,3 and sector size r=0,1,2,3 are
  enumerated. Product matrices and both factor ranks give exact counts for
  every T, agreeing with (1) and (2), including zero-sized sectors.
- Complete literal header censuses cover GL3 at profile (0,1,1,1), d=1, and
  GL4 at profiles (1,1,1,1), d=1,2, and (0,1,1,2), d=1. There are
  **60,648 header/context cases**; identity-pivot counts are 54, 5,040, 36 and
  9,072 respectively, and all sharp counts are zero.
- For each of the two n=5 profiles, **all 496 scalar split pairs** are checked
  by constructing a header and directly computing the Schur rank for each
  identity-pivot pair. No six-map test is used to select the positive pairs.
- All G4 completions of the resulting 3 and 9 positive split pairs are
  explicitly formed, inverted and checked by literal conjugation and Schur
  multiplication: **241,920 positive complete-header cases**, distinct for each fixed pair. This is
  not a raw enumeration of every GL5 header; completeness of this positive
  census uses the proved equal-completion bijection and rank invariance under
  a change of basis in ker pi. Distinctness is checked within each fixed pair.
- Seven controls reject the wrong conditional denominator, independent
  marginals, a missing completion multiplier, forcing full rank in sector 00,
  omitting surjectivity, negative sector dimensions and zero block size.

The d=2,n=8 number is evaluated by the proved formula, supported by the complete
small factor census; the 5.3e18-element header space is **not** enumerated.
Universal claims rest on the written proof, with these finite checks as
corroboration. Human/formal-kernel acceptance is unclaimed. Lean, Docker and
the selected scientific cold replay were not run. Hosted CI is reported
separately in the PR, rather than inferred from local success.

## 6. Task, scope and attribution

Base: canonical main `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7,
selected conditional kappa 0.00302015. This takes the explicit #4671 handoff
and marks `formal-interface-lemma` **changed** to an algebraic counting side
result. The [canonical Discussion4653](https://github.com/CrocSwap/integer-mult-bounds/discussions/4653)
records overlap and the decision to keep the completed dimension question
closed and narrow this round to the specified header ensemble.

**Obligation ledger.** The criterion, factor counts and complete-header
multiplicity are proved above. Production header covers, header selection and
emission, physical reads, owned/borrowed state, dirty compensation/restoration,
stock, dispatch, later guards and the complete consumer bill remain unknown,
not zero. No physical saving or supplier implementation follows from a positive
count. No selected-frontier change is made.

Credit and exact primary sources:

- **ssafwann, #4671**, `8d2e3bc76aa7d43e5c629daaf1e72d4dd5a81ed9`:
  the six-map criterion, dimension theorem and explicit counting handoff;
  substantial OpenAI Codex assistance. The criterion is retained and proved
  above, not claimed as the new contribution.
- **ssafwann, #4657**, `b79f90bc8d839a4998a40b10bcb437e87baa8397`:
  preceding identity-pivot factorization and 4d construction.
- **Nick Petalas, #4597**, `dfeb8ca729a04aea4aa290438f2ed50a37a9c7cb`:
  ordered block-Schur factorization; #4278/#4259/#4246/#4228 retain the
  scalar Schur and equal-completion/full-header lineage. Their original
  attribution and assistance disclosures are preserved in those sources.
- **Ryanson Jonathan, #4609/#4617**, and **lee-phys, #4634**: preceding binary
  sharpness, minimum-dimension constructions and questions, with their
  disclosed Claude Code / OpenAI Codex assistance.
- **Cinna Davis, #4100**: earlier BIT request/header setting; source527,
  commdata2338 and Jose Manuel retain the earlier normalizer lineage credit.

Related inspected work #4598 (`c80f445e8c3c22d341d467254b89245fbddb9eb2`) and
#4599 (`19ca650c67ad2722790dc60c0bfd12989479b06a`) counts corank-one full guards,
not the one-block identity-pivot/Schur-rank event here. The merged
`full-guard-header-census` provides literal full-guard checks with Ryanson
Jonathan's attribution; it is context, not an imported verifier. This package
makes no numerical comparison between those different events. Exact source
paths, Git blobs and byte hashes are recorded as citations in TASK.json;
pending PRs are not runtime Git dependencies.

The new contribution is the exact header law (3), with the elementary factor
counts (1)–(2) derived explicitly, the exact examples and finite corroboration.
Repository tooling retains its contributors' attribution. Apache-2.0.

## Open next questions

Can this one-block count feed a state-aware full-guard recursion? The next
Schur pair generally does not commute, so applying (3) again is unjustified.
Start with one of the n=5 profiles and classify the residual pair up to
simultaneous conjugacy, retaining how many complete headers reach each state;
compare with the orbit question already identified in #4597. The blocker is
the residual-state distribution, not another seed or a product of marginals.
Any use by a real producer additionally needs its actual header cover and a
complete cost allowance. No claim is held on that follow-up.
