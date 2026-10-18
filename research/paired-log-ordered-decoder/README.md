# Ordered decoding of the nine-call paired-log controller

Jose Manuel (@jmbarrancoml), with substantial OpenAI Codex assistance.

I give an explicit inverse for the nine-call controller after replacing its
local calls by paired source/query swaps with independent dirty logs. The
decoder preserves operator order across different charts. It restores the
data and all nine initial log blocks without inverting an aggregate route
matrix.

I also identify the exact space of observations of the final Y banks that a
fixed linear decoder needs, given the final X banks and logs. Over a field,
its dimension is

$$
\sum_{j=0}^3\operatorname{rank}
  \begin{pmatrix}R_{2j}\\R_{2j+1}\end{pmatrix}
=4r+\sum_{j=0}^3\operatorname{rank}
  \left(R_{2j}|_{\ker R_{2j+1}}\right).
$$

This dimension lies between 4r and 8r, and both bounds occur. It counts
scalar information in the stated vector-space model. It does **not** count
native Fourier children or certify their price.

The result addresses the scalar closure missing from the
[paired local handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18927433).
A native implementation still needs the routed Y readers, the resulting
injections, owner placement and the complete precision/recurrence bill.
I claim no improved exponent or selected-frontier change.

## Source interface and controller

For stages s=0,...,8, let R_s:V→L and P_s,Z_s:L→V satisfy
R_s P_s=R_s Z_s=I. Operators at different stages need not commute.
The ordered identities below hold for maps of modules over a unital ring.
The later dimension statement assumes finite-dimensional vector spaces
over a field, with dim(V)=n and dim(L)=r.

Define

$$
T_s=\begin{pmatrix}I-Z_sR_s&P_s\\R_s&0\end{pmatrix},\qquad
T_s^{-1}=\begin{pmatrix}I-P_sR_s&Z_s\\R_s&0\end{pmatrix}.
$$

Multiplying the displayed blocks in either order gives the identity using
only the two stated right-inverse relations. In particular, the old log
input remains arbitrary; a source update stores its information in V.

A forward call at stage s and pair j replaces `(X_j,z_s)` by
`T_s(X_j,z_s)` and adds the new X_j to Y_j. A backward call subtracts the
old Y_j from X_j and replaces `(Y_j,z_s)` by `T_s^-1(Y_j,z_s)`.
Each stage uses its own independent incoming log z_s.

The bridge `(dst,src,c)` performs

```
X_dst += c X_src
Y_src -= c Y_dst.
```

Use the pinned nineteen-event recipe from the retained PR377 replay:
forward0 on pair0; for j=0,...,3, backward(2j+1), the positive bridge to
pair j+1 when it exists, forward(2j+2), and the negative bridge; then the
three descending tail bridges. The final signed exchange is separate.
All formulas below use the final banks **before** that exchange.

This package treats the local maps as exact hypotheses. It does not assert
that an arbitrary chosen chart operator has a legal native realization.
For the E8 local proposal, R=the eight-row query, P=the supported right
inverse, K satisfies RK=14I, and Z=K−13P. The proposed new log fields change
the source inventory relative to the predecessor constructions.

## Explicit decoder

Write X_j,Y_j for the observed final banks, ell_s for the final logs, and
eta_s for the initial logs to recover. The only observations of Y that the
decoder acquires are

$$
q_j^{\rm e}=R_{2j}Y_j,\qquad q_j^{\rm b}=R_{2j+1}Y_j.
$$

The decoder leaves Y in place and eventually adds a computed correction.
It may apply the stated operators to X, logs and acquired query values.
Calling those sources available is an algebraic convention; native access
and scalar/address costs remain separate obligations.

First set

$$
c_0=X_0,\quad c_j=X_j-c_{j-1}\ (j=1,2,3),\quad c_{-1}=0,
\quad\eta_8=R_8c_3,\quad d_4=c_3.
$$

For j=3,2,1,0 in that order, put b=2j+1 and f=2j+2 and compute

$$
\begin{aligned}
y_j^{\rm in}&=-c_{j-1}-c_j-Z_f\ell_f+P_f\eta_f,\\
\eta_b&=q_j^{\rm b}-R_b d_{j+1},\\
d_j&=-d_{j+1}+P_b\ell_b-Z_b\eta_b-y_j^{\rm in},\\
\eta_{2j}&=q_j^{\rm e}+R_{2j}d_j.
\end{aligned}
$$

Then recover the original X banks by

$$
x_j^{\rm in}=Y_j+d_j-c_{j-1}\quad(j=1,2,3),\qquad
x_0^{\rm in}=Y_0+d_0-P_0\eta_0+Z_0\ell_0.
$$

The complete output is `(x_in,y_in,eta)`. To retain the original terminal
exchange, first put `(-y_in,x_in)` into the two data banks; the signed
exchange then returns `(x_in,y_in)`.

### Proof of reconstruction

Undoing the tail bridges on X gives c_j. Let w_j denote X_j immediately
after forward(2j+2), before its negative bridge. For j<3,
`w_j=c_j+x_(j+1)^in`; for j=3, `w_3=c_3`. The query of that source output
is eta_(2j+2), because R_f times the first row of T_f equals its incoming
log. Hence eta8=R8c3 initializes the reverse recursion.

Before backward(2j+1), Y_j equals its original value plus the previous
forward contribution. The X input at that point differs from the same
previous contribution by c_(j−1), with c_−1=0. Thus the backward target
becomes `−y_j^in−c_(j−1)`. Including the positive bridge and then inverting
the forward source update proves the displayed formula for y_j^in. The
next pair's original X value cancels on both sides; no chart commutation
occurs.

Let d_(j+1) be the difference between the forward contribution w_j and
the final Y_(j+1), with d4=w3. The tail bridge gives
`Y_j_after_backward=Y_j−d_(j+1)`. Its R_b query is eta_b, which proves the
second decoder equation. Inverting the backward source update gives its
incoming Y value. Subtracting y_j^in recovers the preceding forward
contribution. By definition that contribution is `Y_j+d_j`; rearrangement
gives the third equation.

Its R_(2j) query equals eta_(2j), proving the fourth equation and the
induction invariant for the next iteration. For j>=1, the preceding
negative bridge implies `x_j^in=Y_j+d_j−c_(j−1)`. At j=0 the contribution
comes from forward0 itself, so its inverse source formula gives the last
displayed equation. These steps also recover each arbitrary initial log.

## Exact required Y-observation space

Fix final X and ell and vary final Y. This is legitimate because each
local call and bridge is invertible, hence the complete controller is
invertible. To compare linear spaces, set the fixed values to zero.

Process the reverse recursion in decreasing j. Modulo quantities already
determined by later Y blocks, the log reconstruction has the form

$$
\begin{pmatrix}\eta_{2j+1}\\\eta_{2j}\end{pmatrix}
=
\begin{pmatrix}I&0\\-R_{2j}Z_{2j+1}&I\end{pmatrix}
\begin{pmatrix}q_j^{\rm b}\\q_j^{\rm e}\end{pmatrix}
+\text{terms from later blocks}.
$$

Each diagonal block is invertible by changing the sign of its lower-left
entry. The full transformation from the eight query blocks to eta0,...,eta7
is block triangular and invertible; eta8 is fixed by the available outputs.
Thus the initial-log map and the stacked Y readers have exactly the same
kernel. Over a field they have the same row space. Any fixed linear
observation of Y that permits exact recovery of all initial logs must
contain that row space, and the displayed decoder attains it.

For one pair write Rb=R_(2j+1), Rf=R_(2j), Zb=Z_(2j+1). The residual

$$
E_j=R_f(I-Z_bR_b)
$$

is the restriction of Rf after projection onto ker(Rb). Row reduction of
the stacked reader replaces Rf by E_j. Its row space meets the row space
of Rb trivially: E_j Zb=0, whereas Rb Zb=I. Therefore

$$
\operatorname{rank}\begin{pmatrix}R_f\\R_b\end{pmatrix}
=r+\operatorname{rank}(E_j)
=r+\operatorname{rank}(R_f|_{\ker R_b}).
$$

Independent Y banks make the four ranks additive. Coherent reader spaces
give the lower bound 4r; transverse row spaces give 8r. The checker includes
both extremes and an intermediate case.

The four initial odd-stage logs already give a direct 4r obstruction to a
decoder that uses only final X and logs. A backward call injects its fresh
log through Z_b into Y_j. The following forward call reads X, not Y. The
two adjacent bridges send the difference between Y before and after that
forward call to the next pair, cancelling this fresh log's contribution.
It never reaches X or a later log output. The tail acts invertibly on Y,
so the four injective Z_b images remain hidden there.

## Scope, reproduction and checks

From repository root, using the standard library:

```sh
python3 scripts/research_package.py --package research/paired-log-ordered-decoder --check-only
python3.12 scripts/research_package.py --package research/paired-log-ordered-decoder
```

The verifier reads the pinned controller recipe. It restores 290 exact input
columns across five rational fixtures with dense readers and sparse P
injections. Three fixtures have noncommuting cross-chart compositions.
It checks equality of the hard-log and stacked-reader row spaces, not only
their dimensions. Five controls per fixture reject a missing Y query,
discarded logs, a missing bridge, the wrong source inverse and a failed
right-inverse hypothesis. Explicit exceptions retain these checks under `-O`.

These finite checks support the written universal argument; they are not
a formal proof or a replay of the E8 native word. A separate dense checker
also restored 58 columns in each of three varied-chart examples. Both
implementations involved Codex, so I claim no independent human review.

For a finite routed realization, interpret the chart operators as actual
linear maps and include the cover/address multiplicity in n and r. Do not
treat a cover group ring as a division ring or substitute r=8 into a scalar
rank theorem while omitting its multiplicity. The ordered inverse itself
does not need division or commuting charts.

Uniform0→FULL log endpoints can make X/log arithmetic available after the
paid completions and exact cover corrections. They do not make the Y-hole
queries available. A field rank of 32 or 64 in a particular finite model
does not certify 32 or 64 native children. Query acquisition, output
injections and log normalization must enter the complete native invoice.

## Open next questions

- Construct the four routed reader/update primitives with a complete native
  bill. First implement one adjacent pair of readers on actual hole-frame
  data, including owner and payload translations. No such priced primitive
  comes from this proof.
- Change the local controller or its log interface to reduce the required
  observation space. First identify an operation that changes the hidden
  odd-log subspace. Reusing logs requires new frame and endpoint accounting;
  it cannot inherit this independent-log theorem unchanged.

Structured scope and next steps appear in [TASK.json](TASK.json).

## Credit and overlap

Zhihao Chen (@jacklightChen), [PR377](https://github.com/CrocSwap/integer-mult-bounds/pull/377),
supplied the retained nine-stage implementation used by the pinned replay.
I retain its preceding controller, Clifford-frame and supplier lineage.

Ali Romman's [PR1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862)
supplied source preparation and dirty-helper correction. His
[PR1969](https://github.com/CrocSwap/integer-mult-bounds/pull/1969), pinned at
`a6e6ad3936f67b8f63b5b68c5e75d540610a65e7`, supplies query exchange, ordered
local inverses and the warning that a Y-hole query needs a paid read or
retained history. It studies a different sixteen-selected-port interface;
I do not claim that this theorem closes its controller.

Rohan Arun's [PR1931](https://github.com/CrocSwap/integer-mult-bounds/pull/1931),
at `d043a01b222365a951853904c001761921bb843b`, supplies the current local
source-reflection instances. The paired independent-log interface appears
in the linked handoff. PR1930's prefix-shear formula and PR1973's fixed-code
winding law have different hypotheses. These comparisons do not establish
exhaustive novelty.

I contribute the ordered global inverse and the exact observation-space
characterization for this interface. Elementary query swaps, triangular
elimination and linear row-space observability are standard linear algebra.
New work is Apache-2.0, with substantial OpenAI Codex assistance in proof,
implementation and prose. Read-only mathematical agents supplied a first
decoder derivation and separate finite checks. Frozen sources remain unchanged.
