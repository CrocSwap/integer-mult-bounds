# Joint coefficient rigidity for one paid contraction

Jerry Chen / @CubeJerry, with substantial OpenAI assistance. Apache-2.0.
This addendum extends the source-bound contact theorem. No new κ.

## 1. Source and precise claim

Use #6824 at 2a7ca44fbda3abaa4df355b183ed7d7478eef7c1, retained through
#6835 at 44316f3e6023a7f8c516360e22e9efd6f0fe48c5. Its canonical payload
SHA256 is d3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821.
The parent package authenticates the bytes, original legality and all 772
public endpoint rows.

Indices are **zero-based original event indices**. Event 10947 is
ADD(796,438,−1,245), the sole touch of helper 438 between MOVEs 10946 and
14152. Those MOVEs follow frames \(911\to245\to127\), of dimensions
\(7\to8\to9\). Deleting the contact would permit their contraction from two
rank-one requests to one rank-two request, with potential paid-moment saving
\(2-2^t>0\) for \(0<t<1\), while preserving helper endpoints.

**Theorem.** Delete event 10947 and retune the coefficients of at most two
distinct other existing ADD, COPY or SCALE events to arbitrary rationals,
with operands, order and frames fixed. Even allowing arbitrary invertible
rational replacement maps at the two original boundary hubs, the original
public endpoint cannot be recovered.

Zero changes and zero resulting coefficients, including zero SCALEs, are
admitted. COPY may overwrite a nonzero owned destination; INIT/CLEAR reset
owned coordinates. This relaxed linear model contains the legal candidates
and imposes no zero-before-CLEAR requirement. Contracting the two MOVEs
does not change the normalized scalar calculation used below.

## 2. Deleted baseline and necessary hub conditions

Let \(K\) be the initial zero-frame public coordinates and \(R\) the final
full-frame coordinates. Here \(|K|=556\), \(|R|=571\), and the source endpoint is
\(A=I+\sum_{r\in\mathrm{live}}E_{r+112,r}\), with inverse obtained by negating
that sum. A supported hub map acts invertibly on its declared coordinate
block, fixes its complement, and has no cross-block entries. Hence

\[
(G_9TG_0)[\bar R,\bar K]=T[\bar R,\bar K].
\]

Repair requires C1, \(T[\bar R,\bar K]=A[\bar R,\bar K]\), and invertibility
of the public map \(T\).

Set the deleted ADD's coefficient to zero as an index-preserving placeholder,
and call its public map \(T_0\). Exact replay establishes

\[
T_0=A+u_0v_0,\qquad 1+v_0A^{-1}u_0=1,\qquad \det T_0=1.
\]

The coefficient change is included in \(u_0\). The constructed inverse

\[
Q=T_0^{-1}=A^{-1}-
\frac{A^{-1}u_0v_0A^{-1}}{1+v_0A^{-1}u_0}
\]

is checked by both matrix products. Its C1 defect is the nonzero rank-one
matrix \(wz\), where \(w=e_{585}\) and
\(z=(T_0-A)[585,\bar K]\). This 51-entry row is recomputed from the source;
in particular \(z_2=-1\).

## 3. Exact two-variable response

In the **deleted word**, let \(u_a\) be the final public response to a unit
inserted into event \(a\)'s destination immediately after it, and \(v_a\)
its source row immediately before it. SCALE uses its destination as source.
For \(a<b\), let \(\tau_{ab}\) propagate that insertion after \(a\) to the
source immediately before \(b\). Coefficient changes \(x,y\) give

\[
T(x,y)=T_0+xu_av_a+yu_bv_b+xy\tau_{ab}u_bv_a.       \tag{1}
\]

This follows by expanding the two affine event-matrix perturbations. COPY's
reset part is coefficient-independent. Owned resets and rectangular
input/output maps require no intermediate inverse. Recomputing responses
after deletion includes all interactions with that fixed change.

Put \(p=u_a|_{\bar R}\), \(q=v_a|_{\bar K}\),
\(r=u_b|_{\bar R}\), \(s=v_b|_{\bar K}\), and \(\tau=\tau_{ab}\).
Then C1 is exactly

\[
wz+xpq+yrs+xy\tau rq=0.                              \tag{2}
\]

## 4. Complete pair screen

Suppose first \(xy\ne0\). The update in (2) factors as

\[
[p\ \ r]\begin{pmatrix}x&0\\xy\tau&y\end{pmatrix}
\begin{bmatrix}q\\s\end{bmatrix}.
\]

The middle matrix is invertible. If both outside factors had rank two,
the product would have rank two, contradicting the required value \(-wz\).
Therefore every possible pair satisfies at least one of:

* \(p,r\in\operatorname{span}(w)\), at least one nonzero, with
  \(z\in\operatorname{span}(q,s)\);
* \(q,s\in\operatorname{span}(z)\), at least one nonzero, with
  \(w\in\operatorname{span}(p,r)\).

A rank-one outside factor must have the target's column or row direction.
The opposite-side span condition is also necessary. Zero vectors are retained.

The span test is exact: relative to nonzero target \(t\), write a vector
as \(c\,t+\sigma h\), where the quotient has zero at the first nonzero
coordinate of \(t\), and \(h\)'s first nonzero entry is normalized to one.
For two nonzero quotients, the target belongs to their span precisely when
their normalized directions agree and
\(c_1\sigma_2-c_2\sigma_1\ne0\). If a quotient is zero, a nonzero pure
target vector suffices; a zero vector alone does not. These rules cover
all two-vector span cases over the rationals.

Among the 15,071 remaining scalar events, 15 have nonzero output direction
\(w\), 5,749 have zero restricted output, 13 have nonzero input direction
\(z\), and 6,311 have zero restricted input. Exhausting both classes leaves
**46,381 unordered pairs**: 23,101 common-column pairs and 23,280 additional
common-row pairs.

For each pair, the opposite-side vectors lie in the span of the target
and at most one common quotient direction. Resolving (2) in these independent
directions is therefore equivalent to every boundary entry. The resulting
one or two equations are reduced exactly in monomials \(x,y,Z\), with
\(Z=xy\) temporarily independent and the constant term retained. No
coefficient values are sampled by this screen or reduction.

## 5. Zero-change corners

If \(x=0\) or \(y=0\), a single compensator must cancel \(wz\). Both its
restricted vectors must be nonzero and proportional to \(w,z\). The verifier
freshly enumerates that intersection, obtaining exactly these C1 solutions:

| Compensator event | Coefficient change | \(\det T/\det T_0\) |
|---|---:|---:|
| 12280 | \(-1\) | \(0\) |
| 12282 | \(-1/2\) | \(0\) |
| 12287 | \(-1\) | \(0\) |
| 12288 | \(-1\) | \(0\) |

Each unique change is solved from C1, and its determinant is checked as
\(1+xv_aQu_a\). Thus zero changes cannot give an invertible repair,
including for pairs omitted by the nonzero-\(xy\) screen. With neither
compensator, the baseline's nonzero defect already excludes C1.

## 6. Determinant identity and finite closure

Define \(d_{ij}=v_iQu_j\). The rank-two determinant identity applied to
(1), with its cubic terms cancelled, gives

\[
\frac{\det T(x,y)}{\det T_0}
=1+d_{aa}x+d_{bb}y+
 (d_{aa}d_{bb}-d_{ab}d_{ba}+\tau d_{ab})xy.             \tag{3}
\]

No candidate endpoint is inverted. The transfer term is \(\tau d_{ab}\)
with this order of the indices.

The exact reconstruction closes all screened pairs:

| Outcome | Count |
|---|---:|
| Inconsistent affine system in \(x,y,Z\) | 99 |
| Determinant in the linear span of the C1 equations | 43,334 |
| Remaining C1 equation fixes \(x=x_0\) | 2,012 |
| Remaining C1 equation fixes \(y=y_0\) | 936 |
| **Total** | **46,381** |

The first class has no solution even in the relaxed monomial space.
In the second, the affine determinant polynomial is a linear combination
of C1 equations, so it vanishes throughout their solution set.

Every other system has one RREF row, no \(Z\) coefficient and exactly one
nonzero linear coefficient. Write (3) as
\(D_0+D_xx+D_yy+D_{xy}xy\). At fixed \(x=x_0\), the checker verifies

\[
D_0+D_xx_0=0,\qquad D_y+D_{xy}x_0=0;
\]

at fixed \(y=y_0\), it verifies

\[
D_0+D_yy_0=0,\qquad D_x+D_{xy}y_0=0.
\]

These identities cover every value of the remaining rational variable.
No division by a variable or unexamined exceptional component occurs.
Unexpected residual shapes cause failure; a general nonlinear solver is
unnecessary. Together with section 5, every coefficient choice satisfying
C1 yields a singular public endpoint.

## 7. Actual hub replacement

The original pre/middle/post factorization is justified by disjoint-register
commutation in #6835, PROOF section 3.4. Its post-hub private lifetimes are
self-contained. The square public factors multiply to invertible \(A\),
so the original hub maps are invertible. Not every frame-zero or full-frame
event is automatically in a replaceable hub.

The deletion is in the middle. If both compensators are also there, write
\(T=G_9M'G_0\). Arbitrary replacements give

\[
G'_9M'G'_0=(G'_9G_9^{-1})\,T\,(G_0^{-1}G'_0),
\]

so the C1 and invertibility requirements above apply. If a compensator lies
inside an actual replaceable hub, arbitrary replacement subsumes that edit.
Absorbing it leaves at most one middle compensator, excluded by section 5;
absorbing both leaves the baseline. This also handles a retuning that made
an old hub singular: no inverse of that edited hub is assumed.

## 8. Evidence, scope and review

verify_joint.py reconstructs the baseline, domain, transfers and exact
classification; JOINT-CERTIFICATE.json records the result. Fourteen literal
changed-word controls check the full 772-row expansion, C1 and independently
eliminated null vectors. Omitting a nonzero mixed term is rejected. A separate
two-register positive control admits joint repair with two retunings and
supported dyadic hubs. These controls corroborate the proof and exhaustive
finite reconstruction; they do not establish completeness by sampling.

The theorem covers **one fixed deletion**, two other existing scalar
coefficients and the stated hubs. Other deletions with two compensators,
changed operands, new gates, interior bases, new helpers or different routes
remain open. No replacement supplier, new invoice root, compiler validation
or multiplication exponent is claimed. All five framework assumptions and
the selected frontier remain unchanged.

The native construction and export retain DreamingOfClouds's #6824/#6835
credit, CubeJerry's #6805 route work, Ali Romman's event/helper lineage,
and the contributors named in the parent NOTICE. Rank-one updates,
Sherman–Morrison and determinant identities are classical. The new result
is the complete source-bound closure of this explicit joint edit.

A second OpenAI GPT-6 Astra Pro agent reviewed the rank screen, quotient
test, deleted-word expansion, inverse and determinant derivation. A separate
rational loop checked all 2,948 recorded residual rows: 2,012 fixed \(x\),
936 fixed \(y\), and zero failed determinant-coefficient tests. It separately
checked the four single-compensator corner values and inspected the source
events proving the sole contact and ranks \(1+1\). This is AI-assisted
mathematical review with targeted exact checks, not a separate implementation
of the entire 46,381-pair reconstruction or human acceptance. The companion
verification record states the full replays and independent reconstructions
actually executed.
