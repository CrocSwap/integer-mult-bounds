# An order-three constraint for three-qubit Clifford conditioning

## 1. Claim, premises, and attribution

This note adds an order-three character constraint to the transvection
relaxation of [PR6794](https://github.com/CrocSwap/integer-mult-bounds/pull/6794).
Together with the retained exact thirty-row certificate it proves, for the
source's normalized character-power Gram matrices and every $f\geq10$,
\[
 \frac{405}{16384}I\preceq H_f
       \preceq\frac{1334151}{131072}I,\qquad
 \operatorname{cond}(H_f)\leq\frac{16471}{40}=411.775<807.
\]
This is a sufficient bound, improving the credited 807 certificate. It is
not the actual Gram spectrum or exact condition number. The width threshold
remains ten, and no multiplication-frontier change is asserted.

Use the finite Gaussian-dyadic Clifford group and notation of
[PR6714, proof at its pinned head](https://github.com/alephnan/integer-mult-bounds/blob/f7f32a18dde54e67624a9ed9cc7e1b266d9585c0/research/clifford-three-qubit-threshold/PROOF.md):

* $V=\mathbb C^8$ is the natural representation, $z=iI_8$, and
  $P\triangleleft G$ is the three-qubit Pauli group.
* $G/P=S=\operatorname{Sp}(6,2)$, while the projective alphabet has size
  $M=|G/\langle z\rangle|=92897280$.
* Every relevant irreducible $\mu$ with $\mu(z)=-I$ restricts to one
  quadratic-form orbit of $P$, of size $N=36$ or $28$, each character
  occurring with the same multiplicity $a\geq1$. Thus $d_\mu=Na$.
  The orbit sizes correspond respectively to Arf invariant zero and one.
* The odd-central-sector irreducibles are the honest representations
  $V\otimes\sigma$, for the thirty irreducibles $\sigma$ of $S$.
  Write $d_\sigma=\dim\sigma$, and let $m_\sigma$ be their multiplicities
  in $V^{\otimes9}$. For nonnegative integers $n_\sigma$,
  \[
  \overline V\otimes\mu
    =\bigoplus_\sigma n_\sigma(V\otimes\sigma),\qquad
  d_\mu=\sum_\sigma n_\sigma d_\sigma,\qquad
  m_{\mu,10}=\sum_\sigma n_\sigma m_\sigma.                 \tag{1}
  \]
* For a transvection $t\in S$, with $t_\sigma=\chi_\sigma(t)$, the
  inherited bound from PR6794 is
  \[
     \left|\sum_\sigma n_\sigma t_\sigma\right|\leq16a.   \tag{2}
  \]

These representation and width-nine multiplicity statements, the published
table identification, and the later-width Gram propagation are inherited
premises. They are not re-established by reading their retained numerical
data. The source byte pins identify the exact versions used.

Credit for the three-qubit threshold, quadratic-form description, and
width-nine decomposition belongs to alephnan's PR6714, using the published
Clifford character table of Chin-Yen Lee, Wei-Hsuan Yu, Yung-Ning Peng, and
Ching-Jui Lai. Credit for the transvection relaxation and its certified
807 bound belongs to Nick Petalas's PR6794 at head
`c6252da020819a08ef2b2ff14280146c43ad374c`. Classical finite-group character
theory supplies the reciprocity and trace principles used below. Our earlier
PR6718 reviewed parts of PR6714's argument; it is not a fresh table
identification or multiplicity computation.

The new written lemma is that for the order-three quotient element $s$
specified below, and $c_\sigma=\chi_\sigma(s)$,
\[
 \frac{\operatorname{Re}\sum_\sigma n_\sigma c_\sigma}{d_\mu}
 \in
 \begin{cases}
 [-3/36,\;6/36],&N=36,\\
 [-5/28,\;10/28],&N=28.
 \end{cases}                                             \tag{3}
\]
The selected quotient column is real, so the real-part notation can be
omitted after that inherited table binding has been made. We do not assume
that each individual fixed multiplicity-space trace is real.

## 2. A lift with exact phase

On one qubit set
\[
 h=\frac{1+i}{2}\begin{pmatrix}1&1\\1&-1\end{pmatrix},
 \qquad S_0=\begin{pmatrix}1&0\\0&i\end{pmatrix},
 \qquad A=hS_0,
 \qquad g=A\otimes I_4.                                   \tag{4}
\]
The entries lie in $\mathbb Z[i,1/2]$. Since
$\left|(1+i)/2\right|^2=1/2$, the two real Hadamard rows have squared
norm two, and $S_0$ is unitary, both $A$ and $g$ are unitary.

Put $b=(1+i)/2$. Then
\[
 A=b\begin{pmatrix}1&i\\1&-i\end{pmatrix},\qquad
 \operatorname{tr}A=b(1-i)=1,\qquad
 \det A=b^2(-2i)=1.
\]
Its characteristic equation gives
\[
 A^2-A+I_2=0,\qquad A^3=-I_2.
\]
Consequently
\[
        \operatorname{tr}_V g=4,\qquad g^3=-I_8=z^2.      \tag{5}
\]
This is an equality of actual Gaussian-dyadic operators; no projective phase
has been discarded.

For the usual Hermitian Pauli matrices $X,Y,Z$, direct conjugation gives
\[
 AXA^*=-Y,\qquad AYA^*=-Z,\qquad AZA^*=X.                \tag{6}
\]
For example $S_0XS_0^*=Y$, $hYh^*=-Y$, and the other two identities
follow in the same way. Thus $g$ normalizes the Pauli group and belongs to
the source group $G$. On Pauli labels in its first symplectic plane its
quotient action is
\[
       (x_1,y_1)\longmapsto(x_1+y_1,x_1),                 \tag{7}
\]
and it is the identity on the other four label coordinates. This quotient
element $s\in S$ has order exactly three: it cycles the three nonzero
vectors of that plane. Its fixed space has dimension four.

As a hand check of the class size, there are
$63\cdot32/6=336$ nondegenerate symplectic two-planes in a six-dimensional
space over $\mathbb F_2$. Indeed, choose a nonzero first basis vector in
63 ways and its symplectic partner in 32 ways, and divide by the six ordered
symplectic bases of a two-plane. On each such plane there are two order-three
elements, acting as the identity on its orthogonal complement. They are
conjugate under the symplectic group, including interchange of the two
orientations inside the plane. The plane is recovered as
$\operatorname{im}(s-I)$, so there is no overcount. The class size is
therefore $336\cdot2=672$.

To associate this class with an actual character column, use PR6714's
inherited *complete* thirty-class quotient catalogue and its published-table
identification. Its retained thirty-entry quotient-class-size list contains
**672 exactly once**, at quotient fibre **5**. Since the hand calculation
above proves that our $s$ has class size 672, completeness and uniqueness in
that catalogue identify its class with fibre 5. This is an inference from
both the computed class size and the inherited complete catalogue; class
size alone, without that uniqueness premise, would not suffice. Fibre 5
comprises published projective classes **9 and 10**, and its retained fixed
dimension **4** also agrees with (7). Both projective classes give the same
inflated quotient-character column. Use that column for every $c_\sigma$
below. The completeness, size list, source-class association, and thirty-row
ordering remain cited source data rather than a rebuilt character table.

## 3. Exactly six or ten fixed Pauli characters

For $\mu(z)=-I$, one has $\mu(-I)=\mu(z^2)=I$. The restriction to $P$
therefore factors through its abelianization. In the source convention its
one-dimensional characters are indexed by quadratic forms
\[
 Q_{\alpha,\beta}(x,y)=x\cdot y+\alpha\cdot x+\beta\cdot y,
 \qquad \alpha,\beta\in\mathbb F_2^3,                    \tag{8}
\]
with Arf invariant $\alpha\cdot\beta$. For the Hermitian Pauli representative
$W_{x,y}=i^{x\cdot y}X^xZ^y$, the character is
$\lambda_Q(W_{x,y})=(-1)^{Q(x,y)}$. Its value on the central generator
is separately fixed as $\lambda_Q(z)=-1$.

Conjugation by $g$ sends each $W_v$ to $\pm W_{sv}$. The sign is
invisible to these characters because their value on $-I$ is one. Thus
the action on $Q$ is ordinary quadratic pullback. Whether one writes the
pullback by $s$ or by $s^{-1}$ does not change its fixed forms.

Apply (7) to the first summand of (8). Its transformed expression is
\[
 x_1y_1+(1+\alpha_1+\beta_1)x_1+\alpha_1y_1.
\]
Equality with
$x_1y_1+\alpha_1x_1+\beta_1y_1$ for every $x_1,y_1$ is equivalent to
\[
                    \alpha_1=\beta_1=1.                 \tag{9}
\]
The other four parameters are free. The total Arf invariant is now
\[
         1+\alpha_2\beta_2+\alpha_3\beta_3.
\]
Among pairs $(\alpha',\beta')\in\mathbb F_2^2\times\mathbb F_2^2$,
ten have dot product zero and six have dot product one: if $\alpha'=0$
there are four zero-dot-product choices; for each of the other three
$\alpha'$, exactly two of the four $\beta'$ have each dot product.
Therefore the fixed-form counts in the two source orbits are
\[
             f_{36}=6,\qquad f_{28}=10.                  \tag{10}
\]
This calculation uses all sixteen fixed forms, with the source's actual
Arf-orbit convention; it does not replace either orbit by its size alone.

## 4. An order-three trace bound on each fixed space

By the inherited restriction statement,
\[
       V_\mu=\bigoplus_{Q\in\mathcal O_N} E_Q,
       \qquad \dim E_Q=a.
\]
The operator $\mu(g)$ permutes these summands. A nonfixed summand contributes
zero to the trace, because its diagonal block in this decomposition is zero.
If $Q$ is fixed, $\mu(g)|_{E_Q}$ has cube $I$, by (5) and
$\mu(-I)=I$. A finite-group representation can be unitarized, or simply
one can use that $X^3-1$ has distinct roots over $\mathbb C$. Its
eigenvalues belong to $\{1,\omega,\omega^2\}$, where
$\omega=e^{2\pi i/3}$. Each eigenvalue has real part either one or
minus one half. Hence
\[
 -\frac a2\leq
   \operatorname{Re}\operatorname{tr}(\mu(g)|_{E_Q})
   \leq a.
\]
Summing the fixed summands proves
\[
       -\frac{f_Na}{2}\leq
          \operatorname{Re}\chi_\mu(g)\leq f_Na.         \tag{11}
\]
There is no assertion that the extreme multiplicity-space eigenvalue
patterns occur in actual irreducibles. Equation (11) is a necessary bound,
not an actual-spectrum endpoint statement.

## 5. Exact cancellation in the character identity

Evaluate (1) at the actual lift $g$. The left side is
$\overline{\operatorname{tr}_V g}\,\chi_\mu(g)$. On the right, every
inflated $\sigma$ has character $\chi_\sigma(s)$, so
\[
 \overline{\operatorname{tr}_V g}\,\chi_\mu(g)
   =\operatorname{tr}_V g
      \sum_\sigma n_\sigma\chi_\sigma(s).
\]
By (5), both natural-character factors are the same real nonzero number
four. Thus the cancellation has phase exactly one:
\[
             T_3:=\sum_\sigma n_\sigma c_\sigma
                   =\chi_\mu(g).                        \tag{12}
\]
In particular, no unit-modulus phase needs to be bounded or chosen. Combining
(10)--(12) and dividing by $d_\mu=Na$ proves (3). The retained quotient
column consists of real integers, so $T_3$ is real in this application.

## 6. The two-trace relaxation and exact certificate

For an actual $\mu$ define
\[
 x_\sigma=\frac{n_\sigma d_\sigma}{d_\mu},\quad
 r_\sigma=\frac{m_\sigma}{d_\sigma},\quad
 u_\sigma=\frac{t_\sigma}{d_\sigma},\quad
 v_\sigma=\frac{c_\sigma}{d_\sigma}.
\]
Then $x_\sigma\geq0$, $\sum x_\sigma=1$, and (1) gives
\[
       \frac{m_{\mu,10}}{d_\mu}=\sum_\sigma x_\sigma r_\sigma.
\]
For each $N\in\{28,36\}$, actual irreducibles therefore give feasible
points of the rational polytope
\[
 \begin{split}
 x_\sigma&\geq0,\qquad\sum x_\sigma=1,\\
 -16/N&\leq\sum x_\sigma u_\sigma\leq16/N,\\
 -f_N/(2N)&\leq\sum x_\sigma v_\sigma\leq f_N/N.
 \end{split}                                             \tag{13}
\]
This remains a relaxation: integrality of the $n_\sigma$, actual branching
rules, and all other irreducible character constraints have been discarded.
The bounds need not be attained by actual $\mu$.

A checked rowwise affine bound
\[
 m_\sigma\geq A d_\sigma+B t_\sigma+C c_\sigma
 \quad\hbox{for every one of the thirty rows}
\]
gives
$m_{\mu,10}/d_\mu\geq A+B\tau+C\gamma$, where
$\tau=\sum x_\sigma u_\sigma$ and
$\gamma=\sum x_\sigma v_\sigma$. Minimizing this affine expression over
the rectangle in (13) is an exact rational lower certificate. Reversing the
rowwise inequality and maximizing gives an upper certificate. Feasible
mixtures with matching objectives additionally certify sharpness of the
*relaxation*. Those are sufficient certificate obligations; numerical
optimization output without the row and feasibility checks is insufficient.

The retained exact certificate checks nonnegative residuals on all thirty
source rows for each of these three integer inequalities:
\[
 \begin{split}
  21m_\sigma-16d_\sigma+28c_\sigma&\geq0,\\
   5m_\sigma-19d_\sigma+84c_\sigma&\geq0,\\
 1007d_\sigma+7063c_\sigma-30m_\sigma&\geq0.
 \end{split}                                             \tag{14}
\]
The verifier stores all thirty exact rational residuals for each displayed
supporting plane; multiplication by its positive denominator yields the
corresponding integer inequality above. These are finite checks of the
inherited character/multiplicity input, not a new reconstruction of it.

For $N=28$, the first inequality gives
\[
 \frac{m_{\mu,10}}{d_\mu}
    \geq\frac{16}{21}-\frac43\gamma
    \geq\frac{16}{21}-\frac43\frac5{14}=\frac27.
\]
For $N=36$, the second gives
\[
 \frac{m_{\mu,10}}{d_\mu}
    \geq\frac{19}{5}-\frac{84}{5}\gamma
    \geq\frac{19}{5}-\frac{84}{5}\frac16=1.
\]
The third supplies the upper bound
$1007/30+(7063/30)\gamma$. Its coefficient of $\gamma$ is positive,
so the upper endpoint of the order-three slab applies. The resulting
per-orbit intervals are
\[
 \frac{m_{\mu,10}}{d_\mu}\in
 \begin{cases}
  [\,2/7,\;2353/20\,],&N=28,\\
  [\,1,\;2621/36\,],&N=36.
 \end{cases}                                             \tag{15}
\]
Both lower supporting planes have negative $\gamma$ coefficient and
likewise use that same upper slab endpoint. All four displayed dual
certificates have transvection coefficient zero.

Here are feasible matching primal mixtures from the retained packet.
Row numbers refer to the **published table's original row indices**, as
in the source's thirty-row list, not a newly numbered list. Weights are
the normalized simplex variables $x_\sigma$, not the integers
$n_\sigma$ of an asserted actual irreducible.

| $N$ | Extremum | Nonzero row weights | $\tau$ | $\gamma$ | Objective |
| --- | --- | --- | --- | --- | --- |
| 28 | Minimum | row 2: $3/7$; row 9: $4/7$ | $-27/49$ | $5/14$ | $2/7$ |
| 28 | Maximum | row 1: $2/5$; row 13: $3/5$ | $3/7$ | $5/14$ | $2353/20$ |
| 36 | Minimum | row 9: $8/9$; row 12: $1/9$ | $-25/63$ | $1/6$ | $1$ |
| 36 | Maximum | row 1: $2/9$; row 13: $7/9$ | $7/27$ | $1/6$ | $2621/36$ |

Each mixture has nonnegative weights summing to one, satisfies both
moment slabs, and meets its supporting plane with equality. In
particular, its transvection moment is strictly inside the transvection
slab. The bounds are therefore exact optima of (13). In fact the
order-three *upper* trace constraint, together with the simplex and source
row data, already yields these same extrema: the duals need no
transvection term and the matching primals remain feasible. This does not
make them actual irreducible or spectral endpoints.

For completeness, the generic finite vertex check covers support sizes
one, two, and three. A vertex with $s$ positive weights needs $s-1$
independent active moment equations after normalization; only two moment
coordinates are available, so $s\leq3$. Support-two vertices are obtained
by intersecting pairs with each slab boundary. Support-three vertices
require one boundary from each coordinate and a nonsingular three-column
system; degenerate supports reduce to smaller ones. All candidates are
then checked against both slabs and positivity. The retained run records
84 distinct vertices for $N=28$ (28 single-support and 56 two-support),
and 168 for $N=36$ (24 single-support and 144 two-support), with no
positive three-support vertices. These are finite fixed-input outputs,
not a claim about all possible character polytopes. The rowwise duals
and matching primals above independently suffice to certify (15).

Taking the union of the two possible orbit types gives
\[
       \frac27\leq \frac{m_{\mu,10}}{d_\mu}\leq\frac{2353}{20}.
\]
The inherited Gram-eigenvalue scale is
$M/8^{10}=2835/32768$. Hence
\[
       \frac{405}{16384}I\preceq H_{10}
             \preceq\frac{1334151}{131072}I.              \tag{16}
\]
The inherited Schur-product relation
$H_{j+1}=H_j\circ H_1$, with $H_1\succeq0$ and diagonal one,
preserves (16) for every $j\geq10$: multiply each PSD difference
entrywise by $H_1$, and use $I\circ H_1=I$. Finally, the ratio of the
upper and lower bounds is
\[
          \frac{2353/20}{\,2/7\,}
                    =\frac{16471}{40}=411.775<807.       \tag{17}
\]
This improves a sufficient uniform conditioning bound. It does not
assert equality for the condition number, change the already proved
width threshold, or remove any inherited representation or Gram premise.

## 7. Evidence and limits

The derivation above is written, source-aware mathematics. The proposed lift
and target bounds were supplied in the coordinator's preclaim recipe, and
the author had prior exposure to PR6714, PR6794, and PR6718. It is not a blind
derivation, a human review, or a formal-kernel certificate. No original
source checker, tensor constructor, table reconstruction, numerical LP,
matrix experiment, or spectral computation was executed by this proof role.
Any separately reported program evidence must retain its own exact scope.

The numerical completion of section 6 was made only after the coordinator
preserved and ran the sealed new verifier once in its explicit generation
mode, and retained its complete successful packet. This proof role read
that existing packet without rerunning any engine. The packet's source
authentication, actual Gaussian lift/Pauli/form calculations, rational
primal/dual residuals, and six discriminating controls are finite evidence
with their own receipts. Normal/optimized replays, export/cold checks,
public CI, and independent human or formal acceptance require their own
evidence and are not inferred from that first run.

The source finite group, its published-table association, the width-nine
multiplicities, tensor reciprocity premises, and Gram interpretation remain
explicit dependencies. The hand lift, fixed-form count, fixed-space trace
inequality, and exact phase cancellation are the new proof obligations
resolved here. No physical native implementation, all-input caller,
precision/overflow envelope, supplier, asymptotic multiplication exponent,
or selected-frontier change follows from this conditioning lemma.
