# Hub gauges preserve the intrinsic PURE pairing

Jerry Chen / @CubeJerry, with substantial OpenAI ChatGPT assistance. Apache-2.0.

**Claim type: a scoped algebraic theorem, with exact small examples and a source-bound application check. No new κ.**

## 1. Question, predecessors and the two meanings of “fixed middle”

DreamingOfClouds's pending [#6835](https://github.com/CrocSwap/integer-mult-bounds/pull/6835),
at `44316f3e6023a7f8c516360e22e9efd6f0fe48c5`, proves a normal form for
zero/full hub maps and asks whether replacing those hubs can change PURE
DUAL PAIR retirements at interior cuts. The present result answers that
question for a **fixed middle word and a matched cut**. Its total public
matrix alone is insufficient to specify a cut; section 7 gives two legal
words with the same total middle matrix and different cut capacities.

The PURE criterion and its unit-elementary-divisor capacity are due to
DreamingOfClouds, [#6827](https://github.com/CrocSwap/integer-mult-bounds/pull/6827),
at `f0fbfd64ea8e7396a6e324d9103350b67215d890`, PROOF §§2–5. Ali Romman's
[#5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599),
`research/p104-helper-subspace-splits/PROOF.md` §1, supplies the earlier
physical independent-input helper split, its prefix/suffix conditions,
dyadic completions and the need to charge the complete boundary. We reuse
and credit these results. The new step is the **complete stabilizer of the
endpoint hub action**, followed by its contragredient action on the two
pairing modules. Section 5 also transports Ali Romman's sufficient
prefix/suffix witnesses when a private reset makes the state rectangular.

The native fixture is #6824 at
`2a7ca44fbda3abaa4df355b183ed7d7478eef7c1`, as exported by #6835. All retained
sources and hashes are identified in SOURCES.json and retained/SHA256.json.
No pending result is treated as an accepted change to the selected frontier.

## 2. The exact gauge freedom

Let the public coordinates be a finite set V. Let K be the coordinates
whose initial frame is zero and R those whose final frame is full. Set

\[
J=K\setminus R,\quad I=R\setminus K,\quad H=K\cap R,
\quad M=V\setminus(K\cup R).
\]

A matrix *supported on K* is an arbitrary invertible block on K, the
identity on its complement, with no cross-block entries. In particular it
both fixes complement columns and has complement unit rows. Use the same
definition for R and H. Write

\[
A=I_V+E,\qquad \operatorname{supp}E\subseteq J\times I.
\]

Thus E²=0 and A⁻¹=I−E. The scalar ring below is either Q or
D=Z[1/2]. A matrix is in GL(D) only when **both it and its inverse** have
dyadic entries; a nonzero determinant over Q is not enough.

### Theorem 1. Stabilizer and all solutions

Fix an invertible public middle matrix T and one solution

\[
G_9TG_0=A,
\]

where G₀ is supported on K and G₉ on R. Every other solution over the
same ring is uniquely

\[
\boxed{G'_0=G_0B,\qquad G'_9=B^{-1}G_9,
\quad B\in\mathrm{GL}(H).}
\]

Conversely every such B gives a solution. This is a torsor for GL(H),
meaning that after one solution is fixed there is exactly one common-hub
parameter B for every other solution. There is no independent freedom on
K and R. If H is empty, the solution is unique.

**Proof.** Set C₀=G₀⁻¹G′₀ and C₉=G′₉G₉⁻¹. They are supported on K and R,
and C₉AC₀=A. Since J lies outside R, the J rows of this equality give

\[
C_0[J,J]=I_J,\qquad C_0[J,H]=0.
\]

Here the E term contributes nothing on K columns, because E is supported
on J×I and C₀ fixes I. In the order (J,H) the K block of C₀ therefore has
shape

\[
\begin{pmatrix}I_J&0\\D_0&C\end{pmatrix},\qquad C\in\mathrm{GL}(H).
\]

For j∈J, AC₀eⱼ=eⱼ+vⱼ with vⱼ∈D^H, because E kills J and H columns.
The j column of C₉AC₀=A says eⱼ+C₉vⱼ=eⱼ. Invertibility of C₉ forces
vⱼ=0, hence D₀=0. Thus C₀ is supported on H. Call it B.
Any such B commutes with A: it changes neither the J rows nor I columns
of E, and EB=BE=E. Consequently C₉=AB⁻¹A⁻¹=B⁻¹.
This proves necessity, uniqueness and, by substitution, sufficiency. Every
step holds over D as well as Q. ∎

This classification does not require running #6835's construction or
assuming the matrix arose from a feed-forward special case. It uses only
the stated endpoint and support conditions. It concerns public hub maps;
two scalar event realizations of the same hub map can differ in length or
private scratch use.

### Audit of the dyadic existence proof

Theorem 1 classifies solutions **if one exists**. For existence we checked
#6835 PROOF Theorems 3.1–3.2 rather than inferring dyadic feasibility from
rational rank. Their hypotheses are

\[
\begin{aligned}
T[\bar R,\bar K]&=A[\bar R,\bar K],&
T[R,M]&=0,\\
T[M,K]&=0,&\operatorname{rank}_{\mathbb Q}T[R,K]&=|H|,
\end{aligned}
\]

and T∈GL(D). The rational factorization yields
T⁻¹[\bar K,J]=0. Put D₁=T[J,K] and N=T⁻¹[K,J]. Then

\[
D_1N=I_J,\qquad T[R,K]N=0.
\]

The first identity is a split surjection, giving the actual D-module
splitting

\[
D^K=ND^J\oplus\ker D_1.
\]

Since D is a PID, the kernel is free of rank |H|. If M₁ is any D-basis of
that kernel, Γ=[N | M₁] lies in GL(D); the J rows of Γ⁻¹ equal D₁.
Writing L₂=T[R,K]M₁ then gives the required block factorization
T=L A Γ⁻¹, with L supported on R. All matrices have entries in D, and

\[
\det L=\det T\det\Gamma
\]

is a dyadic unit. Thus L⁻¹ also has entries in D. This supplies G₀=Γ and
G₉=L⁻¹ over D. There is no overlooked odd-index lattice obstruction.
Changing the kernel basis changes Γ by precisely the GL(H) freedom of
Theorem 1.

The existence proof does **not** make the retained greedy constructor
complete. For K={0,1}, R={1}, A=I₂, take

\[
\Gamma=\begin{pmatrix}3&1\\5&2\end{pmatrix},\qquad
T=\Gamma^{-1}=\begin{pmatrix}2&-1\\-5&3\end{pmatrix}.
\]

Both matrices are integral and unimodular. Here N=(3,5)ᵀ and D₁=(2,−1),
so D₁N=1, but neither existing entry of N is a dyadic unit. The retained
#6835 greedy rule rejects this example, while G₀=Γ, G₉=I is a valid
solution. An elementary row subtraction can expose a unit entry; we claim
no new universal completion algorithm here. The negative control identifies
the limitation of the implemented rule, not a flaw in the existence theorem.

## 3. The fixed-word cut and helper contract

Fix a middle **event word**, including its order, operands, private
lifetimes and frame paths. Replace only its two boundary hub maps. A cut is
matched by the same position in that middle word; physical register names
and current frames are unchanged. The hub maps act on the public state;
any temporary scratch used to realize them meets the same discharged
boundary contract before or after this fixed middle word. The canonical
pre/middle/post factorization of #6835 is one such choice. We do not identify arbitrary
cuts of differently interleaved schedules.

Let Σ be a commutative coefficient ring containing D. It can include formal
invertible chart or query jobs. A prefix P maps **all independent original
inputs** to **all current state coordinates**. A suffix S maps that state
to the public outputs, and X=SP is the required operator endpoint. P can
be rectangular when private registers are present. Private INIT is a zero
initialization and CLEAR, when admitted, is a linear reset. No private row
may be omitted merely because it is absent from the public endpoint.

Changing G₀ to G₀B gives, by composition or induction over linear events,

\[
\boxed{P'=PB,\qquad S'=B^{-1}S.}                 \tag{3}
\]

These are exact identities, including private rows. B acts on the original
input coordinates, not on the physical state coordinates at the cut.
In the normalized scalar replay X=A. For a formal native operator
interpretation, the endpoint additionally has to commute with B. This is
satisfied on the full zero-to-full helper class, where every helper has
the same scalar target τ. The source-bound scalar check alone is not a
replay of all formal chart semantics.

Here is the precise retirement contract used below.

1. **Equal boundary and target.** G is an eligible helper class whose
   members share their initial and final frame. X has scalar block τI on
   G and no cross entries to or from G. Arbitrary GL(D^G) boundary basis
   changes and their inverses are allowed at those two frames.
2. **Invariant helper block.** B commutes with the coordinate projector
   onto G: it preserves both D^G and its coordinate complement. Equivalently
   B is block diagonal across G and its complement. In the retained native
   fixture all of H consists of eligible helpers. Consequently each
   complete class with fixed endpoint frames is either G=H or disjoint
   from H (section 8), so this condition holds. An arbitrary application
   must verify that helper eligibility has not selected a proper subset
   of H; a labelled subset need not be invariant.
3. **Fixed physical cut.** RF is the full declared bank that ordinary
   operations can combine at that cut. The same bank, read rules and
   writable coordinates are used in the two words. The necessary
   GL(D^RF) completions and their inverses must be legal. Fixed smaller
   read and write submodules can also be imposed; the argument preserves
   the actual read/write vectors.
4. **Fixed job.** s is a unit of Σ. The host must separately accept the
   jobs s and τ/s, the chosen physical output/input roles, and any strict
   intermediate-frame requirement. These grammar and lifetime contracts
   are held fixed when comparing the two gauges.

The statement is about intrinsic algebraic availability with unrestricted
legal boundary bases. A finite search over sparse vectors, a bound on
coefficient size or the number of basis-change events is an additional
constraint and need not be preserved.

## 4. Pairing invariance, including dyadic capacity

Following #6827, define the D-modules

\[
\begin{aligned}
\mathcal V_s(P)&=\{c\in D^G:Pc=s u\text{ for some }u\in D^{RF}\},\\
\mathcal W_s(P)&=\{d\in(D^G)^*:aP=s d\text{ for some }a\in(D^{RF})^*\}.
\end{aligned}
\]

A PURE dual pair consists of c,d,u,a as above with dc=au=1. The equality
au=dc follows from aPc=sau=sdc and invertibility of s. These modules are
finitely generated and free because they are submodules of finite free
D-modules. The proof does not require the map a↦aP to be injective.

### Theorem 2. Exact isomorphism of pairings

Under the contract in section 3, the maps

\[
c\longmapsto c'=B^{-1}c,\qquad
 d\longmapsto d'=dB                                     \tag{4}
\]

give D-module isomorphisms from \(\mathcal V_s(P)\) and
\(\mathcal W_s(P)\) to their counterparts for P′. They preserve the
pairing dc. The physical witnesses u and a are **unchanged**.

**Proof.** Both transformed vectors still have support in G because B and B⁻¹
preserve its column module and its row module. Equation (3) gives

\[
P'c'=PB B^{-1}c=Pc=su,\qquad
 aP'=aPB=sdB=sd'.
\]

The same calculation with B⁻¹ proves surjectivity and gives the inverse
map. Finally d′c′=dBB⁻¹c=dc. ∎

If vⱼ,wᵢ are bases of the two modules, the transported bases B⁻¹vⱼ,wᵢB
have **the identical Gram matrix**, not just equal rational rank.
Consequently every Smith invariant factor, the pairing ideals and the
number of unit elementary divisors over D agree.

### Corollary 2.1. Intrinsic PURE capacity is unchanged

For every fixed s and matched cut, the maximum number k of simultaneous
PURE pairs satisfying

\[
PC=sU,\quad A_rP=sD_r,\quad D_rC=A_rU=I_k
\]

is unchanged. As in #6827 Theorem 5.1, this number is the number of dyadic
unit elementary divisors of the pairing. It can be strictly less than the
rank over Q. The bijection is C′=B⁻¹C, D′ᵣ=DᵣB with U,Aᵣ fixed.

For completeness, a unit k-block splits D^G into C Dᵏ⊕ker Dᵣ and
D^RF into U Dᵏ⊕ker Aᵣ. Freeness of the complements over the PID supplies
the two legal basis completions. Conversely, a k-block identity is a
D-linear combination of k-minors of a Gram matrix by Cauchy–Binet; their
gcd must be a unit. Smith normal form yields the stated equivalence.
This repeats the relevant reasoning of #6827 to specify the exact
capacity being transported; it is not claimed as a new capacity theorem.

In particular, searching different zero/full gauges of the same middle
word cannot create an intrinsic PURE opportunity for a complete helper
class or change its pure-pair capacity. It may reveal a witness to a
search procedure that missed it in another basis.

### Rectangular states and necessity

PURE sufficiency still holds when P is rectangular. From SP=X and
Pc=su one gets Su=(τ/s)c. Therefore replacing the cut state by

\[
Px+u(z-aPx)
\]

has endpoint

\[
Xx+(\tau/s)c(z-sdx).
\]

Completing (c,d) at the helper boundary and (u,a) in the physical frame
turns this into one independent emitted job and one independent fresh
input job exactly as in the predecessors. This computation uses neither
P⁻¹ nor injectivity of S.

Necessity of PURE for **every** endpoint split requires more. In #6827's
Theorem 2.1, the implication from a correct retirement to Pc=su uses an
invertible suffix. If S has a kernel, one can instead have
Pc−su∈ker S. We therefore do not import that necessity into arbitrary
COPY/CLEAR words. Theorem 2 concerns the defined PURE pairing and its
capacity, and remains valid without necessity for a larger rewrite class.

## 5. The earlier two-sided sufficient contract is also preserved

Ali Romman's #5599 sufficient contract is naturally expressed with both
P and S. In this note's row/column conventions it asks for

\[
aP=s d,\qquad Su=(\tau/s)c,\qquad au=dc=1,             \tag{5}
\]

with c,d supported on G and u,a at the physical cut. The helper and cut
basis completions give a valid independent split by the same endpoint
calculation. These equations are a **sufficient contract** under its
stated native boundary and erasure assumptions; we make no new necessity
claim for all physical implementations.

Under (3), transport c,d as in (4) and keep u,a. Then

\[
aP'=s dB=s d',\qquad
S'u=B^{-1}Su=(\tau/s)B^{-1}c=(\tau/s)c',
\]

and both unit pairings are unchanged. This is a bijection, also for
simultaneous witnesses with both pairing matrices Iₖ. Thus changing only
the endpoint hubs cannot create a witness even for this broader
prefix/suffix sufficient split contract. We do **not** identify its
capacity with the PURE Smith count when S is noninjective.

A small distinction control has

\[
P=\begin{pmatrix}1&0\\0&1\\1&0\end{pmatrix},\qquad
S=\begin{pmatrix}1&0&0\\0&1&0\end{pmatrix},\quad SP=I_2.
\]

The third row is a live private copy of the first input. At RF={0},
a=(1,0,0), u=(1,0,0)ᵀ and c=dᵀ=(1,0)ᵀ satisfy (5), but Pc≠u. A
suffix that discards the copy implements the endpoint split under an
owned-reset contract. Requiring that private copy to be included in PURE
makes the alleged column impure; it must not be silently dropped. The
checker accepts and transports the two-sided witness, and rejects it as
a PURE witness. If a model requires zero-before-CLEAR, that broader split
example is outside its erasure contract; no conclusion for that model is
inferred from the reset example.

## 6. Constructive dyadic pairing example and arithmetic controls

Let G={0,1}, RF={0,1}, and over Σ=D[t,t⁻¹] set

\[
P=tP_m,\quad S=t^{-1}P_m^{-1},\quad X=I_3,\quad s=t,
\qquad
P_m=\begin{pmatrix}m&1&0\\1&0&1\\0&1&-(m+1)\end{pmatrix}.
\]

For every integer m, det Pₘ=1. Writing c=(c₀,c₁,0)ᵀ, the off-frame
component of Pₘc is c₁. Thus \(\mathcal V_s=D e_0\).
Writing a=(a₀,a₁,0), the forbidden input coefficient in aPₘ is a₁;
therefore \(\mathcal W_s=D(m,1,0)\). These are complete module bases,
with Gram matrix [m].

For m=4 there is one PURE pair:

\[
c=e_0,\quad d=(1,1/4,0),\quad
u=(4,1,0)^T,\quad a=(1/4,0,0).
\]

For m=3 the pairing has rational rank one but image 3D; no dyadic unit
pair exists. A putative row a=(1/3,0,0) solves the rational equations and
is rejected because 1/3∉D. For m=0 both pure modules are nonzero but the
pairing is zero. A direct sum of the m=4 and m=3 examples has Gram matrix
diag(4,3), rational rank two and simultaneous PURE capacity one.

Take the nontrivial dyadic gauge

\[
B=\begin{pmatrix}2&1/2&0\\0&1/2&0\\0&0&1\end{pmatrix},\qquad
B^{-1}=\begin{pmatrix}1/2&-1/2&0\\0&2&0\\0&0&1\end{pmatrix}.
\]

The transported module bases are (1/2,0,0)ᵀ and
(2m,(m+1)/2,0), with Gram matrix still [m]. In the m=4 pair, u and a
stay exactly as displayed. This is a small exact example of the theorem
with a nonconstant formal job. It is not a priced native supplier.

For the small Gram checks, the program computes the gcds of all k-minors,
removing powers of two. The ideal is the unit ideal exactly when that gcd
is one. It also checks the Gram row [3,5]: neither entry is a unit, but
its generated ideal is the unit ideal. A checker that looked only for an
existing unit entry would miss this capacity.

## 7. Necessary scope controls and genuine escape routes

### 7.1 A labelled subset can change its inventory

Let every input be a zero-to-full helper: H={0,1}. At a cut with RF={0}
use P=I₂. The gauge B that swaps the two helpers gives P′=B. For the
complete class H, both prefixes have capacity one; the transformed pair
uses c′=d′ᵀ=e₁ while physical u=aᵀ=e₀ stays fixed.

If the eligible set is artificially restricted to G={0}, its capacity is
one before the swap and zero afterwards. B does not preserve that G.
This is a change of the label-restricted question, not an intrinsic gain
for the complete equal-boundary class. Preserving only the column submodule
is also insufficient: the shear B=((1,1),(0,1)) preserves D e₀, but sends
the resident row e₀ᵀ to (1,1). With G={0} and RF={0}, its pure-column
module survives while its pure-row module becomes zero. The contract must
preserve the helper **block**, including the dual rows. Similarly, a declared boundary
subgroup or coefficient bound must be checked for invariance separately.

### 7.2 Same total middle matrix, different intermediate word

This is a concrete negative control against replacing “fixed word and
matched cut” by “fixed total matrix.” Work in F₂⁹ with frames

\[
F_0=\langle e_1\rangle,\quad
F_1=\langle e_1,e_2\rangle,\quad
F_2=\langle e_1,e_3\rangle,\quad
F_3=\langle e_1,e_2,e_3\rangle,
\]

and full frame F₉. Public helper h begins at zero, and public nonhelper m
begins at F₀. Both end at F₉, so G=H={h}, K={h}, R={h,m}. The baseline
moves h from zero to F₀; next h moves to F₁ and m to F₂; then both move
to F₃ and finally F₉. The matched cut is after the moves to F₁,F₂.
There are seven strict ascending MOVEs.

The second word inserts at F₀

\[
h\leftarrow h+m,\qquad m\leftarrow m+h,
\]

whose scalar matrix is U=\(\begin{pmatrix}1&1\\1&2\end{pmatrix}\).
At F₃ it inserts the inverse operations

\[
m\leftarrow m-h,\qquad h\leftarrow h-m.
\]

The co-rest and strict-MOVE rules hold, the MOVE lists are identical, and
all added ADDs lie strictly between the two hubs. The two total scalar
middle maps are both T=I₂ and both endpoints are A=I₂. At the matched
cut their scalar prefixes are I₂ and U. In the second word, for c=cₕeₕ,
the m component of Uc is cₕ; hence the pure-column module at RF={h} is
zero. The complete helper class has capacity one in the baseline and zero
in the changed word.

This is not merely a trivial scalar-job phenomenon. Give the five nonzero
frames independent invertible central variables z_F, with MOVE(F→G)
acting by z_G/z_F and z_zero=1. At the cut the helper column is
(z_F1,0)ᵀ before mixing and (z_F1,z_F2)ᵀ after mixing. The baseline has
job s=z_F1; the changed word still has no nonzero pure helper column.
Both complete operator endpoints are exactly

\[
\operatorname{diag}(z_{F9},z_{F9}/z_{F0}).
\]

The checker multiplies these Laurent polynomials exactly, not at sampled
numeric values. This formal typed-word example establishes the scope
boundary. It does not provide a P104 price improvement or identify a
helpful intermediate gauge for the 772-register source.

### 7.3 What the invariance does and does not exclude

A legal ordinary basis change confined to the same fixed cut frame is
already harmless by #6827 Proposition 4.1: it changes physical witnesses
by inverse transport. The escape in §7.2 mixes earlier and then separates
the registers into different physical frames before the cut.

Changes outside Theorems 1–2 include a changed middle word or prefix,
changed operand/frame routes, new registers or lifetimes, heterogeneous
helper boundary declarations that change legal boundary bases, an eligible
module not preserved by B, changed read/write rules, or a different
coefficient ring. Each can change the problem; none is asserted to improve
the native invoice. A differently scheduled word can present different
co-resident cut banks, even if its endpoint and invoice before splitting
are unchanged. We do not claim retirement-capacity invariance across those
new cut inventories.

Our conclusion also does not compare the ordinary work or coefficient
growth needed to realize two gauges or their boundary completions. Those
implementation costs are not the intrinsic pairing capacity.

## 8. Native applicability and exact certificate

The source export has 772 public coordinates, 29 private slots and 18,622
events. Its canonical pre/middle/post counts are 5,766 / 7,356 / 5,500.
The endpoint classes have |K|=556, |R|=571, |H|=359 and |M|=4. All 359
members of H are helpers with the same zero/full boundary pair. The
remaining complete helper boundary classes are disjoint from H. There
are 77 such complete helper classes in total.

The checker reconstructs the original hub maps, the middle T and a
second solution obtained by #6835's retained gauge constructor. It then
**independently** multiplies sparse matrices to compute

\[
B=G_0^{-1}G'_0,\qquad B^{-1}=(G'_0)^{-1}G_0.
\]

It checks both inverse identities, dyadic entries, support only on H,
G′₀=G₀B and G′₉=B⁻¹G₉. The nontrivial matrices have respectively 2,022
and 1,712 nonzero entries, counting their complement identities.
This is an actual equivalence of the two source gauges, not merely a
synthetic B appended to an unchanged matrix.

A second scalar replay keeps every public and private state row. At
middle cuts 1,839, 5,517 and 6,671, it checks P′=PB and P=P′B⁻¹ on all
801 slots. These cuts have respectively 1, 11 and 1 active private
registers. The last cut is selected as the first cut with the largest
proper-frame residency while any private register is live (19 residents).
The other two are quarter and three-quarter cuts. The general theorem
covers every matched cut; these finite checks exercise the real data and
rectangular-state convention.

The checker also verifies covariance of each pre-CLEAR private row and
its zero/nonzero status in the middle word. Under the retained scalar
semantics, 32 such rows are nonzero and one is zero. `check_legal` checks
frame/lifetime legality, not a zero-value requirement before erasure.
This is why the discussion of noninjective suffixes is material. We
preserve the inherited owned-erasure contract; we do not certify it anew.
If an application imposes a zero-before-CLEAR gate, the unchanged status
under B shows that a different endpoint gauge cannot repair a failed gate.

No source-bound census of symbolic productive jobs or dyadic Smith bases
at these native cuts is claimed. The check establishes the class/support
hypotheses and the exact scalar transport; Theorem 2 supplies the
all-gauges, all-matched-cuts algebraic conclusion under the declared
formal read and boundary contracts.

## 9. Scope of acceptance

The selected κ remains 0.003125804 from #6030 at the recorded base. The
five framework assumptions remain: native implementation at all widths,
owned erasure, uniform compiler closure, precision/tape cost, and analytic
integer recovery. We have not replayed the complete selected supplier,
#6833 caller, compiler or outer theorem. The new contribution is a
structural equivalence and precise controls on its use. The executable
checks are exact rational/dyadic and finite Laurent-polynomial
calculations; they are not proof-kernel verification or independent human
acceptance.
