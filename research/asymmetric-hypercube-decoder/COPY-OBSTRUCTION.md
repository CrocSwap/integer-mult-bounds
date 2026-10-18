# A weighted COPY obstruction from an integral separating pairing

The scalar decoder can be enlarged to permit arbitrary copied linear
observations, arbitrary target-dependent readable corrections, and exact
nonlinear decoding. For the even-size paired-port geometry, this enlargement
still requires total COPY frame rank at least the number of live targets.
The same bound survives chronological reuse of previous copies in a specified
monotone, copy-to-zero protocol. Under the inherited odd-stage rank ledger,
this already prevents a positive saving, before any scalar or restoration
costs are added.

This is a conditional obstruction for an explicitly stated physical model.
It does not exclude the selected E8 supplier, whose primitive integral labels
have even self-pairing. The source values below are independent scalar inputs;
geometric dependencies among their address labels do not identify those values.

## 1. Fixed observations and a general pairing

Let \(P\) be a finite set of \(v\) source/target indices. The source vector
\(x\in\mathbb F_2^P\) is arbitrary. Give source \(S\) a rational label
\(u_S\) in a common rational vector space \(U\). For each target \(T\), fix
a rational linear functional \(\ell_T:U\to\mathbb Q\) and a set \(R_T\)
of individually readable sources. Suppose

\[
 M_{TS}=\ell_T(u_S)\in\mathbb Z,\qquad
 M_{TT}\text{ is odd},\qquad
 M_{TS}=0\quad(S\in R_T).                         \tag{1}
\]

Let \(H_1,\ldots,H_b\in\mathbb F_2^P\) be any fixed linear observations.
Every target receives all \(H_i x\) and all individual \(x_S\) with
\(S\in R_T\). Observation \(i\) has support \(A_i\), is sourced from a
frame \(F_i\subseteq U\) containing every \(u_S\), \(S\in A_i\), and is
charged \(r_i=\dim_{\mathbb Q}F_i\). The observations may be repeated,
dependent, nonsymmetric, globally shared, or obtained by arbitrary recoding.

**Theorem 1.** If every target recovers its own \(x_T\) exactly on every input,
even using nonlinear postprocessing, then

\[
                         \sum_{i=1}^b r_i\ge v.       \tag{2}
\]

**Proof.** A linear coordinate recoverable from fixed linear observations
must lie in their row span. Indeed, two inputs with the same observations
differ by a vector in their common kernel. Exact recovery says that the
desired coordinate vanishes on this kernel, and the kernel's annihilator is
the observation row space. Apply this separately at each target, including
its readable individual coordinates. There are binary matrices \(A,B\) with

\[
                  I_v=AH+B,\qquad
                  B_{TS}=0\quad(S\notin R_T),          \tag{3}
\]

where the rows of \(H\) are the observations. Write \(\overline M\) for the
reduction of the integer matrix \(M\) modulo two. Its diagonal is one and
\(B\circ\overline M=0\), where \(\circ\) is entrywise multiplication.
Taking the entrywise product of (3) with \(\overline M\) gives

\[
 I_v=\sum_{i=1}^b
       \operatorname{diag}(A_{:i})\,\overline M\,
       \operatorname{diag}(H_{i:}).                    \tag{4}
\]

For each summand, deleting its zero columns and then bounding its rank gives

\[
\begin{aligned}
 \operatorname{rank}_{\mathbb F_2}
   (\operatorname{diag}(A_{:i})\overline M
      \operatorname{diag}(H_{i:}))
 &\le \operatorname{rank}_{\mathbb F_2}\overline M_{:,A_i}\\
 &\le \operatorname{rank}_{\mathbb Q}M_{:,A_i}\\
 &\le \dim_{\mathbb Q}\operatorname{span}\{u_S:S\in A_i\}
 \le r_i.
\end{aligned}                                                    \tag{5}
\]

The second inequality holds because a nonzero integer minor modulo two is
nonzero over \(\mathbb Q\). The third follows by factoring the matrix through
the source labels and the linear map \(u\mapsto(\ell_T(u))_T\). Rank
subadditivity in (4) proves (2). \(\square\)

Symmetry, positivity, and a common Gram form are unnecessary. An integral
Gram matrix with odd diagonal is a sufficient special case. A common
injective rational change of source coordinates, with the corresponding
change of functionals, preserves the hypotheses and frame dimensions.
Unrelated per-source relabellings are not such a change. Arbitrary rational
matrix entries cannot simply be reduced modulo two: the integral matrix and
odd diagonal in (1) are substantive requirements.

The bound is sharp at this observation/frame level. Copying each source
separately from its line has total rank \(v\). This says nothing about the
additional cost of completing that implementation as a supplier.

## 2. Sequential reuse through copy-to-zero innovations

Direct support containment need not hold for a later copied row: some of its
data may already have descended through an earlier COPY. The following
separate protocol theorem accounts for that reuse.

Use the labels and readable relation in (1). Consider a fixed binary linear
protocol with these rules:

1. Source \(x_S\) begins at frame \(\operatorname{span}(u_S)\). The source
   coefficient rows of helpers and targets are initially zero at frame zero.
2. Ordinary operations are binary ADDs at a common frame and climbs through
   nested frames. A climb never shrinks the frame.
3. COPY episode \(i\) reads a row \(w_i\) at frame \(F_i\) into a fresh
   frame-zero readable register and costs \(\dim F_i\). All earlier copied
   values may be reused and shared without further charge in this lower bound.
4. The final source coefficient row at target \(T\) is \(e_T\), at a frame
   contained in \(\ker\ell_T\). Any native source label in that frame is
   individually readable; enlarging \(R_T\) to all such labels is allowed.

Arbitrary initial helper dirt and target values are projected away when
tracking source coefficients. A valid arbitrary-input supplier must still
satisfy this necessary source-column condition. We also retain erased copies
as free observations, thereby giving the protocol additional power.

**Theorem 2.** Every protocol with these rules satisfies
\(\sum_i\dim F_i\ge v\).

**Proof.** Let \(W_i\) be the binary span of source coefficient rows copied
through episode \(i\). Maintain the invariant that every register at frame
\(F\), modulo \(W_i\), has a representative supported on labels contained
in \(F\). Initially this is immediate. A common-frame ADD sums two such
representatives, and a climb preserves containment.

Just before copy \(i\), choose such a representative \(h_i\) for \(w_i\).
Then

\[
 w_i=h_i+\sum_{j<i}c_{ij}w_j,\qquad
 \{u_S:S\in\operatorname{supp}h_i\}\subseteq F_i.     \tag{6}
\]

Adding \(w_i\) to the copied span preserves the invariant for every old
register. The fresh frame-zero copy represents zero modulo the new span, so
it also satisfies the invariant. The triangular change in (6) implies
\(\operatorname{span}(h_1,\ldots,h_i)=W_i\).

At completion the invariant at target \(T\) expresses \(e_T\) as a
combination of the innovations \(h_i\), plus a row supported on labels in
\(\ker\ell_T\). Thus (3) holds for these innovations. Each has supporting
label span of dimension at most \(\dim F_i\), and Theorem 1 applies.
\(\square\)

This class permits arbitrary linear reuse, global sharing and even
target-to-helper feedback. It contains the selected D/A/scatter/B/C word
shape when instantiated in a geometry satisfying (1), despite allowing more
feedback and more free access than that word's actual interface.

It does not cover a primitive charged only for a partial drop to a nonzero
destination frame, input-dependent nonlinear copy contents or routing, free
nonmonotone frame changes, or promised dependencies among source values.
The theorem does not assert that every physical supplier belongs to its
copy-to-zero class.

## 3. Even paired ports and arbitrary readable corrections

Take any live subset \(P\) of the signed \(k\)-ports on \(p\) coordinate
pairs. A port chooses \(k\) distinct pairs and one coordinate from each.
Its label is the incidence vector \(\chi_S\in\mathbb Q^{2p}\). Grant
target \(T\) every individual source with \(|S\cap T|=1\). Define

\[
 \ell_T(u)=\chi_T\cdot u-\frac1k\sum_j u_j,
 \qquad M_{TS}=|S\cap T|-1.                          \tag{7}
\]

For **every positive even \(k\)**, the diagonal \(k-1\) is odd. Therefore
Theorems 1 and 2 imply total COPY rank at least \(v=|P|\), including after
arbitrary punctures. This covers arbitrary recoded proper-star observations,
all other star degrees including the empty star, and observations not arising
from stars at all. Corrections may vary independently with both source and
target. The result is substantially wider than a uniform overlap-class
decoder restriction.

Indeed, individually readable corrections remove that earlier scalar
obstruction. For every \(k\ge2\), fix \(a\in T\) and write
\(z_b(S)=\mathbf1[b\in S]\). Over \(\mathbb F_2\),

\[
 f_T(z)=\prod_{b\in T}z_b+
        z_a\prod_{b\in T\setminus\{a\}}(1+z_b)
       =z_a\sum_{L\subsetneq T\setminus\{a\}}\prod_{b\in L}z_b
       =\mathbf1[S=T]+\mathbf1[S\cap T=\{a\}].       \tag{8}
\]

The top terms cancel, leaving only nonempty stars of degrees at most
\(k-1\). Equation (8) supplies an unpunctured scalar decoder with the
granted corrections. For even \(k\), it cannot make the requisite physical
COPY rank smaller than \(v\).

The rational symmetric form \(I-J/k^2\) realizes (7) as pairing with
\(\chi_T\). When \(2p=k^2\) that form is singular; no admissible frame
construction is claimed there or elsewhere merely from the formula. The
obstruction only needs the linear functionals and remains valid in this
favorable algebraic model. More generally, readability at intersection
\(a\) gives \(M_{TS}=|S\cap T|-a\), so the same obstruction applies when
\(k-a\) is odd.

For odd \(k\) with readability at intersection one, (7) has even diagonal
and this certificate is unavailable. That is consistent with the inherited
paired-triple construction and the selected E8 norm-two labels. It is an
escape from this obstruction, not a positive-cost certificate. In particular,
the known odd-\(k\) binomial decoder identities do not supply their own
source-branching, restoration or hosting invoice.

## 4. Comparison with the actual selected supplier ledger

This source trace is pinned to main commit
`91a2094f2e022930069e8cfdc810a3ea1b81cd09`. Its selected certificate names
Jeremy Kothe's PR #799 complex word, Chafik Boukhalfa's PR #741 frames, and
DreamingOfClouds' PR #589 bit tuning of eumemic's PR #555 construction. The
conditional selected value at that campaign-start checkpoint was
\(1661634653669567/10^{18}\).

A read-only refresh at main commit
`007664306fff84fbb1c9a1b4053b69f439764034` finds the selected PR #890
composition at \(1661957774647029/10^{18}\). Its
[pinned integration review](https://github.com/CrocSwap/integer-mult-bounds/blob/007664306fff84fbb1c9a1b4053b69f439764034/docs/research/community-frontier890-review.md)
retains the same PR #589 / PR #555 bit supplier. The bit ledger traced below
therefore remains applicable. This refresh is a source inspection, not a new
cold replay of the selected assembly; nothing here changes that selection.

The selected bit word has ambient dimension \(h=8\), \(v=111\) sources
and targets, \(R=439\) dirty helpers, and nine COPY ranks equal to seven:
\(C=63\). Its independent checker initializes all \(2v+R=661\) scalar
columns independently and checks restored sources/helpers and final target
\(y_T+x_T\). The rational labels describe address geometry; they are not
linear dependency promises on these input values.

The local word compensates dirty helpers in D at frame zero; A acts on
sources/helpers; scatter uses retained copied totals; B may interleave target
reads with more source/helper operations; C literally reverses the
source/helper-destination gates at full frame. Its H1--H5 conditions also
exclude target feedback into sources/helpers and require exact target-to-target
identity. All common-frame operations, COPY/ERASE episodes, dirt compensation,
cleanup and restoration belong to the actual supplier invoice.

The selected local rank profile obeys

\[
 \sum_r rH_{\rm local}(r)=hR+C+2v(h-1)=5129.         \tag{9}
\]

With \(L=9=2K+1\), \(K=4\), \(T=32\) replicas, address dimension
\(m=64\), and \(W=28416\) live data families, its whole-call hosting ledger
gives

\[
 D=mW-\sum_r rH_{\rm global}(r)
   =T(2Kv-LC)=10272.                               \tag{10}
\]

The bit endpoint is already nonbinding in this selected assembly. An
isolated bit saving would still require the complex and outer inequalities
to be reassembled before any claim about the selected exponent.

For a proposed paired-port replacement, **conditionally retain this same
odd-stage endpoint and whole-call rank accounting**, with general
\(L=2K+1\), \(m=1+(h-1)L\). Its favorable deficit is

\[
                  D=T[(L-1)v-LC].                   \tag{11}
\]

Theorem 2 gives \(C\ge v\) for even paired \(k\), hence
\(D\le-Tv<0\). Thus the rank mass alone is at least \(mW\). In the
corresponding normalized rank moment, with recursive child ranks \(0<r<m\),

\[
 \frac{\sum_r H(r)r^{1-c}}{Wm^{1-c}}
 =\sum_r\frac{rH(r)}{Wm}(m/r)^c\ge1\qquad(c\ge0).  \tag{12}
\]

Any inherited bad-branch allowance or other nonnegative charge worsens this
bound. Consequently this class cannot yield a positive exponent saving under
(11), even if all preparation, scalar gates, source access, restoration,
helpers, hosting and finite compilation costs are optimistically granted for
free. These charges are not actually free: granting them zero is what makes
the rejection favorable to the proposed construction.

Equation (11) is a stated template hypothesis, not an assertion that every
new label system has a legal selected-style hosting/compiler implementation.
The actual selected E8 model does not satisfy the odd-diagonal hypothesis,
so its \(C=63<111\) is consistent with the theorem.

## 5. Predecessors, verification scope and immutable sources

The underlying same-field entrywise-product rank obstruction is already in
[`rank-product-core.md`, section 3](../../docs/research/rank-product-core.md).
It gives the unweighted rank-product inequality and explains why the rational
and binary fields cannot be silently identified. The result here is its
**support-sensitive weighted refinement** \(\sum_i r_i\ge v\), using an
integral rational-to-binary reduction, individually readable corrections,
nonlinear postprocessing of fixed linear observations, and the chronological
innovation argument. There is no claim that the entrywise-product rank
inequality itself is new.

The general binomial incidence expansion is already in
[`single-intersection.md`](../../docs/research/single-intersection.md).
The paired-cube geometry is credited to icekylinx and eumemic. The selected
interface also inherits Zhihao Chen's source-mutability work (PR #425), DaysSky's
whole-call hosting (PR #442) and later chafreaky compositions, Dylan Crow's
independent-column checks (PR #370), and DreamingOfClouds' recursive moment
work (PR #315). Those underlying construction and validation contributions
are retained, not re-proved by this obstruction.

The all-parameter claims in sections 1--3 are the proofs above. The selected
numerical comparison is a read-only source trace, not a fresh end-to-end
supplier replay. Run the independent finite checker from the repository root:

```sh
python3 -I -O -B research/asymmetric-hypercube-decoder/copy_obstruction_verify.py --self-test
```

It checks all ports in eight cases: `k=2,p=3..6` and `k=4,p=4..7`. For one
anchored decoder per target it evaluates the actual star observations,
readable corrections, each entrywise-product summand, binary/rational ranks
and the reconstructed identity. Individual source copies check sharpness.
Four negative controls test the odd-k diagonal, intersection-zero and
intersection-two corrections, and a missing observation. A twelve-copy prefix
fragment checks triangular innovation replacement where raw copied supports
exceed their charged native-frame ranks. That fragment is not a restored
supplier schedule. The self-test checks isolated optimized relocation,
corrupt-receipt rejection and output preservation on failure. The expected
result is `PASS copy_obstruction_verify.py`, with the exact finite receipt in
[`COPY-OBSTRUCTION-RESULTS.json`](COPY-OBSTRUCTION-RESULTS.json).

These finite checks supplement the proofs; they do not establish the
all-parameter statements or certify an unimplemented physical supplier.

All files in the following table are read at the pinned main commit above;
the Git blob makes each individual source immutable.

| Source | Git blob |
| --- | --- |
| `certificates/selected-result.json` | `1f107b55a2f045fa66d9c35d658b3b79549f5ba6` |
| `docs/research/rank-product-core.md` | `9b683864233d79b4d9d982a48bdefd1a1bc875d0` |
| `docs/research/single-intersection.md` | `7cdf4555e9f9e043debbfe1e3a49fa201234d710` |
| `research/paired-cube-bit-fast/paired_cube_bit_word.py` | `fc7fb270d7598ea65722ae700676b0b67086a624` |
| `research/e8-bit-p111-tuned/README.md` | `40dff2216e65ebba0be490ad962e869876a45286` |
| `research/e8-bit-p111-tuned/tune/README.md` | `5b1554369682c8344d4f0767111d9b2b35eecbec` |
| `research/e8-bit-p111-tuned/code/xcheck_p.py` | `184f5dcf94a486cc7db91ca4db5865916bf26009` |
| `research/e8-bit-p111-tuned/code/adapt9p.py` | `96bbc2ba9bb11984736e34db8b65c1a91e8f842e` |
| `research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/code/assemble9.py` | `238226c568742dd5723b03eabae564a2eaa2bda9` |
| `research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py` | `3df12bd632f1fdba825ced57110a1fee82eb2857` |
