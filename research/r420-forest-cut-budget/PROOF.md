# Rooted-forest compensation: correctness and restricted optimality

This construction changes R420's frame-zero dirt compensation. It preserves
arbitrary target and helper inputs, introduces no register, and changes no
paid frame path. The claim is a finite circuit simplification, not a new
bit exponent or multiplication theorem. Prepared by Anthony Lei with
substantial OpenAI Codex assistance; Apache-2.0.

Postorder row-CNOT synthesis using spanning arborescences is established
work: see Vandaele, Martiel and Goubault de Brugière,
[*Phase polynomials synthesis algorithms for NISQ architectures and beyond*,
arXiv:2104.00934v1, §3.1](https://arxiv.org/pdf/2104.00934v1).
Our contribution is the scoped R420 application, its compensation cost
model and certificates, and complete coefficient accounting. We do not
claim the first tree-based XOR synthesis method. The R420 supplier belongs
to eumemic (#543); restored target-pair compensation precedes this work
in #713/#716. Larger forest components extend that restricted pair class.
Concurrent #759 (Oscar Fennell) independently published the forest class
and the same unconstrained floor during final validation. We credit that
result without a priority claim; the additional result here is the exact
fixed-tree cut budget and its separately compiled generic Lean proof.

## 1. Circuit class and dirty-input correctness

Let targets have arbitrary initial values \(y\in\mathbb F_2^n\), helpers
have arbitrary values \(s\in\mathbb F_2^m\), and sources be \(x\).
Fix the binary compensation matrix \(K\), with row supports \(K_i\).
The required map is

\[
D_K:(x,s,y)\longmapsto(x,s,y+Ks).
\]

Sources are neither read nor written. Helpers are read but never written.
Every binary XOR costs one; directly injecting a row costs its Hamming
weight. All targets and helpers remain at frame zero. No input is
assumed clean and no scratch register is available.

Choose a rooted forest on the fixed targets, with parent \(p(i)\) for
each nonroot. Its circuit has exactly these three parts:

1. Prepare `y_i ^= y_p(i)` once per nonroot, children before parents.
2. Inject \(K_i\) at each root and \(K_i\mathbin\triangle K_{p(i)}\)
   at each nonroot, directly from helpers.
3. Reverse the preparation gate list, giving parents-before-children
   unpreparation.

**Theorem 1.** Every such circuit implements \(D_K\).

**Proof.** Put \(T_{i,p(i)}=1\), with other entries zero. During
preparation each child reads its parent's original value, because the
parent has not yet been modified. Thus preparation is exactly
\(A=I+T\). If the maximum forest depth is \(d\), then
\(T^{d+1}=0\), and over \(\mathbb F_2\),

\[
A^{-1}=I+T+\cdots+T^d.
\]

The injection matrix is \(AK\): its rows are precisely the stated root
rows and child-parent differences. Reversed XOR gates implement
\(A^{-1}\), since each gate is an involution. Therefore

\[
y\longmapsto Ay\longmapsto Ay+AKs
 \longmapsto A^{-1}(Ay+AKs)=y+Ks.
\]

Sources and helpers are unchanged throughout. No restriction was placed
on their values or on \(y\). ∎

The order is essential: parent-first preparation generally accumulates
additional ancestors and would need different injection rows.

## 2. Substitution into R420's scalar interface

R420's original H2 requires D to read only helpers. The new target-target
preparation gates violate that syntactic condition. We explicitly replace
it by the exact semantic condition:

> **H2′.** D runs before any climb, is legal at frame zero, fixes all
> sources and helpers, and has map \((x,s,y)\mapsto(x,s,y+Ns)\).

Theorem 1 proves H2′ with \(N=K\). Keep R420's other hypotheses. With
\(z=(x,s)\), its raw A/scatter/B stream has map
\((z,y)\mapsto(Uz,y+Jx+Ks)\); no z-destination gate reads a target,
and the raw target-to-target block is identity. Its unchanged cleanup
applies \(U^{-1}\) to z. Consequently the complete circuit with H2′ is

\[
(x,s,y)\longmapsto(x,s,y+Jx+(K+N)s).
\]

The original identities \(J=I\), \(N=K\) give the required addition
of x into y. A, scatter, B, C, and literal z-cleanup are unchanged.
An audit must check D's complete matrix, including the target identity
block and zero source block; the individual new injection rows need not
equal the original rows.

The block calculation alone does not justify reordering the framed stream.
Apply the chronological substitution bridge of woklerx's
[#1194](../r439-semantic-d-contract-seed10/PROOF.md), also used by Arham Tahir's
[#1311](../r439-abc-semantic-bridge/README.md): replace the candidate's D with
the original D to obtain a proof-only virtual word. Here that word is literally
the original R420 word, so the unchanged checker passes all original H1–H5
and U/J/K/C conditions, including the separately checked J=I. The actual D
and original D are legal source-free prefixes at the common zero frame,
with equal complete binary operators and equal exit frames. Their matrix
equality holds over every compatible F2 module, including streams. The same
chronological continuation therefore receives identical values and frames;
no later operation is moved or treated as a frame-free stream operator.

`test_semantic_bridge.py` checks this splice, all 660 boundary columns, frames
and complete paid paths with the pinned original checker. It records exactly
the original syntactic H2 and K_equals_D failures on the actual word, and
rejects missing restoration, scalar-neutral frame changes and forbidden target
feedback. Only the actual D is executed and priced; the virtual D is a proof
device. This is a concrete application of the credited conditional bridge,
not a new all-size realization theorem.

All new operands start at frame zero, so every new XOR is legal there
without a climb. The replacement preserves helpers, retained totals,
stage count, hosting demand, and paid-rank profile. The inherited
physical/compiler and all-size assumptions remain assumptions.

## 3. Exact minimum within the forest class

For a forest F with r roots, both preparation and unpreparation cost
\(n-r\). Its complete cost is

\[
C(F)=\sum_{i\text{ root}}|K_i|
 +\sum_{i\text{ nonroot}}\bigl(2+|K_i\triangle K_{p(i)}|\bigr).
\tag{1}
\]

Empty injection rows cost zero. This count includes all restoration XORs.
The original cost is \(C_0=\sum_i|K_i|\).

Add one abstract sentinel vertex * to the n targets. On the complete
undirected graph assign integer edge weights

\[
w(*,i)=|K_i|,\qquad w(i,j)=2+|K_i\triangle K_j|.
\]

**Theorem 2.** Minimum spanning-tree weight equals the minimum of (1)
over all rooted forests in §1, without a coefficient or depth constraint.

**Proof.** Given a rooted forest, attach every root to *. The result is
connected and has n edges on \(n+1\) vertices, hence is a tree. Its
weight is (1). Conversely, remove * from any spanning tree. Each
remaining component contains exactly one former neighbor of *: at least
one by connectedness, and at most one because two would create a cycle.
Root each component at that neighbor. These constructions are inverse
and preserve weight. ∎

For an independently checkable optimality certificate, a proposed tree Q
must satisfy, for every non-tree edge \(e=(u,v)\),

\[
w(e)\ge\max_{f\in P_Q(u,v)}w(f), \tag{2}
\]

where \(P_Q(u,v)\) is its unique tree path. Necessity follows by
replacing a heavier path edge with e. For sufficiency, remove an edge f
of Q. Every other edge e crossing its resulting cut has
\(w(e)\ge w(f)\), because its Q-path contains f. Compare Q with any
spanning tree S. Choose \(f\in Q\setminus S\). The S-path joining
f's endpoints crosses this cut in some edge e outside Q. Replacing e
by f preserves the tree, does not increase weight, and increases its
overlap with Q. Repeating at most n times gives Q. Thus Q is minimum,
including when weights tie.

The independent checker recomputes row supports, graph weights, tree
cost and every inequality (2). The theorem concerns only this forest
class. It does not optimize general target basis changes, helper basis
changes, or the physical coefficient invoice. In particular, a selected
forest obtained by cutting edges is not claimed globally optimal among
forests satisfying an invoice limit.

**A concrete limit.** Partition nine helpers into disjoint size-three
sets A, B, C. Take \(K_1=A\cup B\), \(K_2=B\cup C\),
\(K_3=A\cup C\). Every root costs 6 and every target edge costs 8.
A forest with k target edges costs \(6(3-k)+8k=18+2k\), so its
optimum is 18. A general target basis does better: prepare
`y3 ^= y1; y3 ^= y2`, inject \(K_1\) into y1 and \(K_2\) into y2,
and reverse preparation. Since \(K_3=K_1+K_2\), it implements the
same dirty-input map with \(2+6+6+2=16\) XORs. Thus forest optimality
must not be described as unrestricted circuit optimality.

## 4. Unsigned coefficients and controlled cuts

Exact binary cancellation is not a valid integer norm estimate. Regard
T now as a nonnegative integer matrix, and let H be the zero-one
incidence matrix of the injection supports. Preparation has unsigned
transfer \(I+T\); unpreparation has
\(U_+=I+T+\cdots+T^d\). The unsigned D transfer is

\[
y\longmapsto
 \left(I+2\sum_{j=1}^dT^j\right)y+U_+Hs. \tag{3}
\]

The factor two on every proper ancestor is real in this calculation.
With unit initial magnitudes, the row bound at target i is exactly

\[
q_i=1+2\operatorname{depth}(i)
       +\sum_{v\in\text{root-to-}i}|H_v|.
\tag{4}
\]

Equivalently, a root has \(q_i=1+|K_i|\), and a nonroot has
\(q_i=q_{p(i)}+2+|K_i\triangle K_{p(i)}|\). Every unsigned operation
is an addition, so intermediate bounds are at most the final bound.
The reversed D word has the same unsigned transfer: it again has the
same preparation and unpreparation, while the reversed helper injections
commute. The complete compiled forward and backward invoices must still
be recomputed; scalar equivalence alone supplies no such invoice.

**Cut lemma.** Delete an edge from child i to its parent p and make i
a root. The new forest is correct by Theorem 1, and its cost changes by

\[
\Delta C=|K_i|-|K_i\triangle K_p|-2. \tag{5}
\]

Only i's injection and its two edge gates change, proving (5). For
every descendant of i, the new unsigned helper path replaces the whole
old root-to-i prefix by \(K_i\). The XOR of those old injection rows
is \(K_i\), so its zero-one incidence is entrywise at most their
integer incidence sum. Proper ancestors above i also disappear from
(3). Hence cutting weakly decreases the unsigned D transfer entrywise
in both directions; other components are unchanged. In (4), every
descendant's depth decreases by the old depth of i. Multiple cuts
preserve these conclusions by iteration. A cut is therefore a precise
way to trade additional XORs for smaller coefficients, but passing a
particular global bound still requires its actual invoice.

## 5. Exact budget optimization over cuts of one fixed tree

Freeze the oriented seed-6 minimum forest, including its tie-breaking.
Only its 116 target edges may be cut; the remaining edges cannot be
reoriented or replaced. The following optimum concerns all \(2^{116}\)
cut subsets of this fixed forest, not all forests.

The invoice is the integer quantity \(64F^3B^2<2^{104}\), where F
and B are complete forward and backward unsigned maxima. In this word,
unchanged source/helper rows attain \(F_*=144651\), also the uncut
forward maximum. No gate in the unchanged tail reads a target. Cutting
decreases D's unsigned outputs, while these work rows remain unchanged;
therefore every cut subset has exactly \(F=F_*\). Its reverse cap is

\[
B_{\rm cap}=\left\lfloor\sqrt{
 \left\lfloor\frac{2^{104}-1}{64F_*^3}\right\rfloor}\right\rfloor.
\]

Replay the unchanged reverse tail before D once. Let its maximum be
\(B_0\), target endpoint magnitudes be \(a_i\), helper magnitudes be
\(h_j\), and \(w_h(S)=\sum_{j\in S}h_j\). First require
\(B_0\le B_{\rm cap}\). If r is the retained root above i, the exact
backward D endpoint satisfies

\[
b_r(r)=a_r+w_h(K_r),\qquad
b_i(r)=b_{p(i)}(r)+a_i+a_{p(i)}
                      +w_h(K_i\triangle K_{p(i)}).
\]

This is (3) with nonuniform incoming magnitudes. Nonnegative additions
make endpoint bounds sufficient for every intermediate D prefix.

Define \(c_i(r)=|K_i|\) when \(i=r\), and otherwise
\(c_i(r)=2+|K_i\triangle K_{p(i)}|\). For each vertex i and ancestor
r, let \(D(i,r)\) be the minimum feasible subtree cost when i remains
connected to root r. Set it to infinity if \(b_i(r)>B_{\rm cap}\).
Otherwise,

\[
D(i,r)=c_i(r)+\sum_{j\text{ child of }i}
                  \min\{D(j,r),D(j,j)\}. \tag{6}
\]

**Proof of exactness.** Each child edge has precisely two possibilities:
retain it, preserving root r, or cut it, making j a new root. Once this
choice is made, child subtrees share no gates, costs or constraints;
their only inherited quantity is their root. Induction from leaves
therefore proves (6). Summing \(D(r,r)\) over the original roots
enumerates every cut subset implicitly and returns its exact minimum
feasible cost. There are at most \(n^2\) ancestor states. Full literal
replay independently checks the selected reconstruction's invoice. ∎

The verifier can also use the unchanged work-row value merely as a
necessary forward lower bound: a feasible reconstructed word attaining
the resulting DP lower bound still proves cut-class optimality. Neither
argument establishes an optimum among other minimum trees, different
orientations, or arbitrary forests under the payload constraint.

## 6. Calibration, selected witness, and formalization boundary

On the pinned R420 word, the unconstrained forest minimum is 14,921
XORs, compared with the original 19,922: a calibration saving of 5,001.
The particular seed-6 minimum tree is **not an admissible selected witness** under the fixed
104-bit payload limit. Its finite bill has forward norm 144,651,
backward norm 20,395,400, and payload 106 bits. This failure is retained
as evidence that minimizing XOR count does not minimize the invoice.

The selected cuts are the child indices **5, 34, 39, 57, 78**. The
independently reproduced 724-state recurrence gives D cost **15,025**,
saving **4,897** against the original, with **22,019** whole-word ADDs.
Literal replay gives F = 144,651 and B = 9,800,790, hence
`64 F^3 B^2 = 18606576056688220135806852422400 < 2^104`.
The exact B cap is 10,232,638. This is the optimum in the fixed oriented
tree's cut class, not a global optimum under the payload constraint.

That distinction has a concrete R420 witness: changing only the selected
parent of vertex 32 from 37 to 34 yields D cost **15,023**, complete cost
**22,017**, and the same F, B and strict payload pass. The independent
scope-control test replays all 660 columns and the unchanged frame paths,
then correctly rejects its certificate as outside the frozen cut family.
This nearby word has not received a separate native or hosted replay.
It demonstrates why the 15,025 certificate must not be described as the
best admissible target forest or best known R420 XOR count.

`Forest.lean` proves generic Boolean XOR linearity, reversal, the
children-before-parent action, and compensation with arbitrary helpers
and targets. It does not prove the minimum-spanning-tree theorem,
the concrete numerical optimum, unsigned invoices, physical frame
transport, or multiplication. Forest optimality rests on the written
proof and independent exact finite certificate; circuit admission also
requires full-column replay and the complete coefficient bill.

The paid profile is unchanged, so a scalar-operation saving establishes
no new bit exponent or κ. The result retains the original supplier's
compiler, common-label, hosting, precision, tape, and analytic assumptions.
