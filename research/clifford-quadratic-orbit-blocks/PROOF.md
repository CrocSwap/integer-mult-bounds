# Two actual quadratic-orbit blocks of the width-ten Clifford Gram matrix

## 1. Statement and exact source group

Use the group of PR6714: $G$ consists of the unitary three-qubit Clifford
matrices with entries in $D=\mathbb Z[i,1/2]$. Its natural representation
$V$ has dimension eight. Write $z=iI$, let $P$ be the Pauli subgroup, and
put $S=G/P=\operatorname{Sp}(6,2)$. The scalar subgroup is $\mu_4$.
No ordinary Hadamard with an unavailable scalar phase, eighth root of
unity, or enlarged Clifford group is substituted for this source group.

The retained source proofs are
[PR6714 at f7f32a18](https://github.com/alephnan/integer-mult-bounds/blob/f7f32a18dde54e67624a9ed9cc7e1b266d9585c0/research/clifford-three-qubit-threshold/PROOF.md)
and
[PR6794 at c6252da0](https://github.com/petalas/integer-mult-bounds/blob/c6252da020819a08ef2b2ff14280146c43ad374c/research/clifford-transvection-conditioning/PROOF.md).
The package source pins bind their exact bytes and the retained table
and width-nine inputs.

Subject to the retained PR6714 quotient-table identification, width-nine
decomposition, and normalized Gram-block formula, the following are two
actual irreducibles and their width-ten data:

| Irreducible $\mu$ | Dimension | Multiplicity in $V^{\otimes10}$ | Gram eigenvalue at width ten | Regular block dimension |
| --- | --- | --- | --- | --- |
| $\operatorname{Sym}^2V$ | 36 | 2244 | $176715/32768$ | 1296 |
| $\Lambda^2V$ | 28 | 2159 | $874395/131072$ | 784 |

These are actual block eigenvalues, not the endpoints of a trace
relaxation. They are not claimed to be the smallest or largest eigenvalue
of the entire Gram matrix. The final column is the dimension of each
specified regular block; if another irreducible has the same eigenvalue,
the global spectral multiplicity is larger.

PR6794 asks for actual quadratic-form stabilizer decompositions as a
first step toward actual spectral endpoints. This note resolves just the
two multiplicity-one Pauli-orbit modules below. It does not determine
all even-sector irreducibles or their decompositions.

## 2. Bell matrices give the two irreducible modules

Let $F=\mathbb F_2^3\oplus\mathbb F_2^3$, write $v=(a,b)$, and define

\[
 q_0(v)=a\cdot b,\qquad
 \omega((a,b),(c,d))=a\cdot d+b\cdot c.
\]

The dots in these expressions are binary. Use the source's Hermitian
Pauli representatives

\[
 W_v=i^{\,q_0(v)}X^aZ^b.
\]

They are Hermitian unitary matrices, satisfy $W_v^2=I$, and obey

\[
 W_v^T=(-1)^{q_0(v)}W_v,\qquad
 W_vW_w=(-1)^{\omega(v,w)}W_wW_v.                    \tag{1}
\]

With the source binary-dot convention a tensor product of single-qubit
$Y$ matrices may differ from $W_v$ by a real sign. This causes no change
in (1) or the argument. We keep the source representatives throughout.

Identify $V\otimes V$ with $8$-by-$8$ matrices by
$e_j\otimes e_k\mapsto E_{jk}$. Its actual $G$ action is congruence

\[
                    B\longmapsto gBg^T.                \tag{2}
\]

The 64 matrices $B_w=W_w$ form a basis, for example by Pauli trace
orthogonality. From (1) their symmetric and skew-symmetric spans have
dimensions 36 and 28, respectively, and are precisely
$\operatorname{Sym}^2 V$ and $\Lambda^2V$ under this identification.
For the count, $a=0$ allows eight $b$ with $a\cdot b=0$; each of the
other seven $a$ allows four of each parity. Thus the two counts are
$8+7\cdot4=36$ and $7\cdot4=28$.

Under a Pauli representative, (2) acts on a basis line by

\[
 W_vB_wW_v^T
       =(-1)^{q_0(v)+\omega(v,w)}B_w.
\]

Set $Q_w(v)=q_0(v)+\omega(v,w)$. The central generator $z$ acts by
$i^2=-1$ in (2), so these are the source's one-dimensional Pauli
characters with central value $-1$. The $Q_w$ are all distinct. If
$w=(c,d)$, their linear parameters are $\alpha=d,\ \beta=c$, and

\[
                  \operatorname{Arf}(Q_w)=c\cdot d=q_0(w).
                                                               \tag{3}
\]

The source quotient $S$ acts transitively on each of the two Arf orbits
of quadratic forms. Pauli conjugation signs are invisible in these
characters because $-I=z^2$ acts as one. Consequently (2) permutes the
36, respectively 28, one-dimensional weight spaces transitively.

This proves irreducibility of each actual $G$ module. Indeed, any
nonzero invariant subspace splits into its Pauli character components
over $\mathbb C$, by the character projectors for this finite abelian
quotient of $P$. Since every weight space is one-dimensional, it contains
a whole such line. Transitivity under $G$ then gives every line in the
orbit. Denote these irreducibles by $\mu_{36}$ and $\mu_{28}$.
Their central value is $\mu_N(z)=-I$.

## 3. A phase-exact all-element intertwiner

Let $\mathcal O_N$ be the corresponding set of quadratic forms, and
let $\Pi_N=\mathbb C[\mathcal O_N]$ be its ordinary permutation
representation, inflated from $S$. For any actual $g\in G$, the
one-dimensional weight-space argument gives

\[
            gB_Qg^T=\theta_Q(g)B_{Q'},\qquad
            |\theta_Q(g)|=1,                            \tag{4}
\]

where $Q'$ is the permuted label. The modulus follows also by preserving
the Hilbert-Schmidt norm. There is no assumption that $\theta_Q$ is one,
or that (2) itself is the unphased permutation representation.

Define a linear map

\[
 \Phi:V\otimes\Pi_N\longrightarrow\overline V\otimes\mu_N,
 \qquad
 \Phi(v\otimes e_Q)=B_Q^\dagger v\otimes B_Q.             \tag{5}
\]

Each $B_Q$ is invertible, so (5) is an isomorphism: on each labelled
summand it is simply the invertible map $B_Q^\dagger$ on an
eight-dimensional vector.

Taking the adjoint of (4), and using unitarity of $g$, gives

\[
 \overline g\,B_Q^\dagger g^\dagger
       =\overline{\theta_Q(g)}B_{Q'}^\dagger,\qquad
 \theta_Q(g)\,\overline g\,B_Q^\dagger
       =B_{Q'}^\dagger g.                               \tag{6}
\]

Thus the action on the right of (5) is

\[
 (\overline g\otimes\mu_N(g))\Phi(v\otimes e_Q)
 =\theta_Q(g)\overline gB_Q^\dagger v\otimes B_{Q'}
 =\Phi(gv\otimes e_{Q'}).
\]

It follows that the honest $G$ representations satisfy

\[
                  \overline V\otimes\mu_N
                      \cong V\otimes\Pi_N.              \tag{7}
\]

This is an all-element intertwiner, including every Pauli element and
every scalar in $\mu_4$. In particular it is not a character-division
argument at elements with nonzero natural trace, nor an equality only
up to a central phase. The conjugate natural representation in (5)--(7)
is essential.

## 4. The two permutation modules are rank two

For completeness, the quadratic-form permutation action is two-transitive.
Fix a form $Q$. Every other form with the same polar form is uniquely
$Q+\omega(-,w)$. The standard Arf identity is

\[
 \operatorname{Arf}(Q+\omega(-,w))
                =\operatorname{Arf}(Q)+Q(w).             \tag{8}
\]

In the present coordinates this follows by writing
$Q(a,b)=a\cdot b+\alpha\cdot a+\beta\cdot b$ and
$w=(c,d)$: the new linear parameters are $\alpha+d,\beta+c$;
the difference of the two Arf values is
$\alpha\cdot c+\beta\cdot d+c\cdot d=Q(w)$.
Thus the other forms in the same orbit are parameterized by the
nonzero singular vectors $w$, those with $Q(w)=0$.

Here is an elementary proof that $O(Q)$ is transitive on those vectors.
For any $a$ with $Q(a)=1$, the symplectic transvection
$\tau_a(x)=x+\omega(x,a)a$ preserves $Q$.
If distinct nonzero singular $u,v$ satisfy $\omega(u,v)=1$,
then $Q(u+v)=1$ and $\tau_{u+v}$ sends $u$ to $v$.
If instead $\omega(u,v)=0$, the two independent linear conditions
$\omega(u,c)=\omega(v,c)=1$ have a solution, by nondegeneracy of
$\omega$. Replacing $c$ by $c+u$ preserves both conditions and toggles
$Q(c)$, so choose $c$ singular. The transvections with directions
$u+c$ and $v+c$ preserve $Q$ and send $u$ first to $c$, then to $v$.
This proves the desired transitivity without a finite orbit enumeration.

The point stabilizer in $S$ is $O(Q)$, so it is transitive on all other
points of the quadratic-form orbit. Hence $\Pi_N$ is two-transitive.
Over $\mathbb C$ its commuting algebra has dimension two, since its
matrix entries are constant on the two orbits of ordered point pairs.
The constants are a single trivial constituent. Semisimplicity then
implies that the augmentation summand is one irreducible, of dimension
$N-1$. Therefore

\[
                   \Pi_{36}=1\oplus\sigma_{35},\qquad
                   \Pi_{28}=1\oplus\sigma_{27}.           \tag{9}
\]

These steps are classical permutation-representation and orthogonal-space
arguments; no new general representation-theoretic principle is claimed.

## 5. Bind the quotient constituents to the retained source rows

The following values are read from the source's complete thirty-row
quotient identification and its width-nine multiplicities. Row numbers
are the published table's original row indices.

| Published row | Degree | Transvection character | Width-nine multiplicity |
| --- | --- | --- | --- |
| 1 | 1 | 1 | 269 |
| 6 | 27 | 15 | 1890 |
| 7 | 35 | 15 | 1975 |
| 8 | 35 | -5 | 175 |

There is just one degree-27 irreducible among those quotient rows, so
the constituent $\sigma_{27}$ in (9) is row 6. There are two degree-35
possibilities, rows 7 and 8; the dimension alone does not distinguish them.

A transvection fixes sixteen forms in each Arf orbit, as in PR6714.
One can see the count by taking its direction to be the first
coordinate vector: the fixed-form condition is $\alpha_1=1$, and each
choice of the other four parameters determines $\beta_1$ uniquely for
either chosen Arf value. Thus
$\chi_{\Pi_N}(t)=16$ and the augmentation character is 15.
This selects row 7, not row 8, for $\sigma_{35}$.

Combining (7) and (9) therefore gives the actual decompositions

\[
 \begin{split}
 \overline V\otimes\mu_{36}
       &\cong (V\otimes1)\oplus(V\otimes\sigma_{\mathrm{row}\,7}),\\
 \overline V\otimes\mu_{28}
       &\cong (V\otimes1)\oplus(V\otimes\sigma_{\mathrm{row}\,6}).
 \end{split}                                             \tag{10}
\]

The source proves that the $V\otimes\sigma$ are the distinct irreducibles
in the relevant odd central sector. Their honest quotient identification
and numerical multiplicities are inherited data, not reconstructed by
this argument. The Bell construction and (7) determine which of those
source rows actually occur here.

## 6. Width-ten multiplicities and regular-block eigenvalues

For any irreducible $\mu$ in this central sector, tensor reciprocity gives

\[
 \dim\operatorname{Hom}_G(\mu,V^{\otimes10})
   =\dim\operatorname{Hom}_G(\overline V\otimes\mu,V^{\otimes9}).
                                                               \tag{11}
\]

Using (10), the retained width-nine decomposition and the two rows in
each direct sum show

\[
                 m_{\mu_{36}}(10)=269+1975=2244,\qquad
                 m_{\mu_{28}}(10)=269+1890=2159.          \tag{12}
\]

There is no extra degree factor in (12): each summand in (10) occurs
once, and (11) is a dimension of a Hom space between irreducibles.
Both $\mu_N$ have central value $-1$, which is the width-ten sector.

Let $M=|G/\langle z\rangle|=92897280$ and let $H_{10}$ be the source
normalized character-power Gram matrix. Its inherited block formula is

\[
             \lambda_\mu(10)=\frac{M}{8^{10}}
                                    \frac{m_\mu(10)}{\dim\mu},
             \qquad \frac{M}{8^{10}}=\frac{2835}{32768}.
\]

Substituting (12) gives

\[
 \lambda_{\mu_{36}}(10)
       =\frac{2835}{32768}\frac{2244}{36}
       =\frac{176715}{32768},\qquad
 \lambda_{\mu_{28}}(10)
       =\frac{2835}{32768}\frac{2159}{28}
       =\frac{874395}{131072}.                            \tag{13}
\]

The central-character regular ideal has a matrix block of dimension
$(\dim\mu)^2$ for each irreducible. Thus the two contributions have
dimensions $36^2=1296$ and $28^2=784$. These do not have an additional
factor four from the scalar lifts. Other blocks can share an eigenvalue;
(13) does not assert its total multiplicity in the whole Gram matrix.
The formulas are at width ten, not unchanged eigenvalue formulas for
every larger tensor width.

## 7. Evidence, credits, and remaining obligations

This is a source-aware written calculation. The coordinator supplied
the proposed Bell/intertwiner recipe before this draft, and this author
had prior source exposure to PR6714, PR6794, PR6718 and the later
order-three conditioning work. The recipe was critically checked rather
than treated as accepted. It is not blind discovery, independent human
review, or formal-kernel acceptance. This proof role executed no source
or new scientific program, table reconstruction, orbit enumeration,
constructor, tensor calculation, LP, or eigenvalue experiment.

Alephnan6714 supplies the actual Gaussian-dyadic group, its full
symplectic quotient, the quadratic-form orbit framework, width-nine
decomposition and normalized Gram-block formula. The table identification
uses the published work of Chin-Yen Lee, Wei-Hsuan Yu, Yung-Ning Peng
and Ching-Jui Lai. Nick Petalas6794 supplies the conditioning context
and the explicit actual-stabilizer-decomposition handoff.
The source-aware PR6718 proof review and the later conditioning result
are predecessor context, not fresh evidence or a decomposition replay.
Bell/Pauli identifications, multiplicity-free weight-space arguments,
tensor reciprocity, rank-two permutation modules and (8) are classical.
The contribution is their explicit phase-correct application to these
two source-bound actual blocks.

The source group/table identification, all other irreducible
decompositions, and all uncomputed spectral blocks remain distinct.
Nothing here proves global spectral endpoints, an exact condition
number, a new tensor threshold, or a selected-frontier improvement.
Native realization, a complete physical caller and its invoice,
precision/overflow, the supplier hypotheses and all five selected
framework assumptions remain outside this calculation.
