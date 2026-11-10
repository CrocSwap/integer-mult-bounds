# A sharp four-axis map with the exact native square

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The native factorization, correction predicates and half-grid lower bound are
inherited from Nick Petalas's CrocSwap/integer-mult-bounds#6574. The phase-only
construction is CrocSwap/integer-mult-bounds#6758; the period lower bound is
CrocSwap/integer-mult-bounds#6761. The new result is a compatible invariant
period and correction cycles satisfying the exact square at the sharp radius.

## 1. Statement and notation

Coordinates are indexed by the four-bit strings, encoded as integers 0 through
15; write `wt` for Hamming weight and `j xor 15` for coordinate complement.
Let

\[
 W_{rs}=(-1)^{\operatorname{wt}(r\mathbin{\&}s)},\quad A=W/4,\quad
 S_{jj}=(-1)^{\operatorname{wt}(j)},\quad (Jz)_j=z_{j\mathbin{\mathrm{xor}}15},
 \quad K=SJ,\quad B=SA.
\]

Walsh orthogonality and character translation give

\[
 A^2=I,\qquad ASA=J,\qquad B^2=K,\qquad B^4=I.
\]

Both `A` and `B` are orthogonal; `S` and `J` commute. On complex vectors set
\(D_{jj}=(-i)^{\operatorname{wt}(j)}\) and \(U=-DAD\). Then \(D^2=S\),
\(DJD=J\), \(U^2=J\), and \(U\) is unitary. Here `U` is exactly the native
four-axis transform, not a numerical approximation or a different phase
convention.

The construction below gives a map \(R:\mathbb Z^{16}\to\mathbb Z^{16}\)
and its componentwise extension \(R_C(a+ib)=R(a)+iR(b)\), with
\(F=-D R_C D\). For every Gaussian integer vector `z`:

* `F` is a bijection, \(F^2=J\), \(F^4=I\), and \(F^{-1}=JF=FJ\).
* \(F(\zeta z)=\zeta F(z)\) for a **global** unit \(\zeta\in\{1,-1,i,-i\}\).
* \(\sum_jF(z)_j=\sum_jz_j\).
* \(\|F(z)-Uz\|_2\le\sqrt8\), and the same radius holds for the inverse
  relative to \(U^{-1}\). Both radii are attained.
* If `Uz` is Gaussian-integral, then \(F(z)=Uz\).

The real map is affine with slope `A` on a lattice of index 4096. This attains
the divisibility lower bound proved in #6761 for odd real rounders commuting
with `K`. No minimality claim is made for arbitrary coupled complex rounders.
At grid spacing `h`, multiply the displayed error bounds by `h`.

## 2. The invariant period

Let

\[
 L=\{z\in\mathbb Z^{16}:Az\in\mathbb Z^{16}\}.
\]

Write \(t=\sum_s z_s\) and \(b_j=\sum_{s:s_j=1}z_s\). Expanding Walsh signs
modulo four shows

\[
 z\in L\iff t\equiv0\pmod4\text{ and }b_j\equiv0\pmod2\ (0\le j<4).
\]

Indeed \((Wz)_r\equiv t-2\sum_{j:r_j=1}b_j\pmod4\); the rows `r=0` and
`r=2^j` establish necessity, and that expression establishes sufficiency.
Thus \([\mathbb Z^{16}:L]=64\). Use the following ordered integer basis:

\[
 u_0=4e_0,\qquad u_{j+1}=2(e_{2^j}-e_0)\quad(0\le j<4),
\]

followed, in increasing `s` of weight at least two, by

\[
 u_s'=e_s+(\operatorname{wt}(s)-1)e_0-\sum_{j:s_j=1}e_{2^j}.
\]

The basis coordinates of `z` in `L` are exactly

\[
 x(z)=(t/4,b_0/2,b_1/2,b_2/2,b_3/2,
 z_3,z_5,z_6,z_7,z_9,z_{10},z_{11},z_{12},z_{13},z_{14},z_{15}).
\]

The physical basis determinant has absolute value 64. Also `B` preserves `L`:
`Bz` is integral for `z` in `L`, and \(ABz=Jz\) is integral.

On these sixteen basis coordinates, take the binary row masks

```
0x0021  0x0906  0x6fde  0x0103  0xa8ec  0x029e
```

with the least significant bit referring to coordinate zero. Let `G` denote
the six-row matrix and define

\[
 \Gamma=\{z\in L:Gx(z)=0\pmod2\}.
\]

The binary row rank is six; its ascending pivot columns are `0,1,2,3,4,6`.
Consequently \([L:\Gamma]=64\) and \([\mathbb Z^{16}:\Gamma]=4096\).
If the rows are named \(g_0,\ldots,g_5\), direct exact multiplication in the
stated `L` basis gives the covector action

\[
 (g_0B,g_1B,g_2B,g_3B,g_4B,g_5B)
 =(g_0+g_1,g_1+g_2,g_2,g_3+g_4,g_4+g_5,g_5)
 \pmod2.
\]

Thus \(B\Gamma=\Gamma\); inclusion suffices because \(B^4=I\). In
particular `K` also preserves `Gamma`. This stronger `B` invariance is the
missing prerequisite beyond a period merely compatible with negation.

The restriction of `G` to the first five columns has rank five. Since those
columns span \((L\cap2\mathbb Z^{16})/2L\), this proves
\(\Gamma\cap2\mathbb Z^{16}\subseteq2L\), the necessary oddness condition.
Furthermore \(2L\subseteq\Gamma\), so \(8\mathbb Z^{16}\subseteq\Gamma\).
The residue classifier therefore only needs three low bits per input
coordinate. This observation does not make its physical evaluation free.

## 3. Exact quotient labels and representatives

For any `z`, encode the residue modulo `L` by

\[
 q=(t\bmod4)+4\sum_{j=0}^3(b_j\bmod2)2^j\in\{0,\ldots,63\}.
\]

Write `a=q mod 4`, `m=floor(q/4)`, and let `r(q)` have coordinate
\(r(q)_0=a-\operatorname{wt}(m)\), coordinates
\(r(q)_{2^j}=m_j\), and zero elsewhere. Then \(z-r(q)\in L\).
The complete class label is

\[
 s(z)=64q+\sum_{i=0}^5(g_i x(z-r(q))\bmod2)2^i.
\]

Two integer vectors have the same label exactly when their difference lies
in `Gamma`. Reduction of each input coordinate modulo eight leaves this label
unchanged. `kernel.py` uses this low-bit variant; the dense rational lattice
oracle in `verify.py` does not use that classifier.

The certificate fixes representatives as follows. Inspect the sixteen columns
of `G` in ascending order; retain a column if it is independent of the columns
already retained. Use the resulting six columns to lift each six-bit syndrome
by its unique binary linear combination of those columns. Replace each chosen
column by its corresponding physical `L` basis vector, obtaining `l(v)`.
The representative numbered \(s=64q+v\) is \(r_s=r(q)+l(v)\). This specifies
all 4096 representatives without a hidden search, arbitrary tie break or
external artifact.

## 4. The finite correction certificate

`CERTIFICATE.json` contains the period rows and 568 pairs `[s,c]`, where `s`
is a class label and `c` is a sixteen-entry integer vector. A row generates
four steps starting from \((z,c)=(r_s,c_s)\):

\[
 z\longleftarrow (SWz+c)/4=Bz+c/4,\qquad c\longleftarrow-Bc.
\]

At each step, assign correction `c` to the class of `z`, and correction `-c`
to the class of `-z`. All quarters are exact integers. Repeated assignments
agree, the cycles close, and the rows cover every class. There are 4 generated
class orbits of size 1, 18 of size 2, 78 of size 4 and 468 of size 8; their
sizes sum to 4096. The certificate is 26,889 bytes.

For the expanded correction table, put

\[
 T(z)=Bz+c_{s(z)}/4,\qquad R(z)=ST(z).
\]

The decisive finite predicates, checked on **every** representative, are:

1. \(SWr_s+c_s\equiv0\pmod4\).
2. \(\|c_s\|_2^2\le64\) and \((\Re d)^Tc_s=(\Im d)^Tc_s=0\), where
   \(d_j=(-i)^{\operatorname{wt}(j)}\).
3. \(c_{s(-r_s)}=-c_s\).
4. If \(p(s)=s(T(r_s))\), then \(c_{p(s)}=-Bc_s\).

The checker also verifies `K` covariance, quotient bijectivity, both literal
inverse compositions, maximal correction coordinate 5, and the value 64 for
the maximum squared correction norm. These are consequences or additional
bounds, not substitutes for predicate 4. In particular the rejection control
at class 128 changes an entire negation/`K` orbit: all local integrality,
sharp error, weighted sums, oddness and `K` covariance survive, but the exact
square predicate fails.

The discovery search fixed this period, enumerated representative real
corrections `e=S c` in `[-3,3]^16` with the stated residues, weighted sums and
energy bound, and paired the induced negation/`K` orbits. A forced partner
`-Bc` may have coordinates of magnitude 5. The 64 coarse classes have candidate
count histogram `{1:1, 848:32, 4900:1, 36:28, 70:2}`. The resulting graph has
1120 vertices and 63,018 compatible undirected edges including loops, with no
isolated vertex. After forcing the displayed basis cycle, the first greedy seed, zero, supplies
the complete certificate; the
stopping rule allowed seeds 0 through 99. The optional search is a discovery
procedure, not a completeness proof over periods, matchings or rounders.
The mathematical result rests on the complete finite certificate and the lift
below, not on a heuristic search succeeding.

## 5. Lift from the quotient to every integer input

For \(\gamma\in\Gamma\), class labels are unchanged, so

\[
 T(z+\gamma)=T(z)+B\gamma,\qquad
 R(z+\gamma)=R(z)+A\gamma.
\]

Since `B Gamma = Gamma`, the class of `T(z)` depends only on the class of `z`.
Integrality therefore extends from the representatives to all integer inputs,
and predicate 4 applies everywhere. Thus

\[
 T(T(z))
 =B^2z+\tfrac14 Bc_{s(z)}+\tfrac14c_{s(T(z))}
 =Kz.
\]

Predicate 3 likewise extends oddness to all inputs. The equation `T^2=K`
implies `T` commutes with `K` and is bijective, with inverse `KT`. Since `S`
commutes with `K`, `R=ST` is odd, bijective and commutes with `K`. Moreover

\[
 RSR=S T^2=SK=J.
\]

This is the exact identity needed by the native factorization. Merely having
an arbitrary fourth-order real permutation would not establish it.

The real error is \(R(z)-Az=S c_{s(z)}/4\), of norm at most 2. All 64
correction entries for classes in `L/Gamma` are zero. Hence `Rz=Az` on `L`;
conversely a zero error implies that `Az` is integral.

## 6. Native square, sum, sharp error and inverse

Oddness makes `R_C` commute with multiplication by a global `i`, and hence
with every global Gaussian unit. The fixed diagonal `D` also commutes with
those scalars, proving the stated global covariance of `F`. This does **not**
assert covariance under independently chosen coordinate phases.

Using oddness to move the inner minus sign, the exact composition is

\[
 F^2=-D R_C D(-D R_C D)=D(R_C S R_C)D=DJD=J.
\]

Associativity now gives \(F^4=I\), \(FJ=JF\) and \(F^{-1}=JF\).
For each real correction, \(d^TSc=\bar d^Tc=0\), because `DS=conj(D)`
and both its real and imaginary weighted sums vanish. Also
\(d^TA=-\bar d^T\), so \(\mathbf1^TU=\mathbf1^T\). Therefore `F`
preserves the complex coordinate sum exactly.

The two componentwise real errors are orthogonal real/imaginary lanes, and
`D` preserves norm. It follows that

\[
 \|F(z)-Uz\|_2^2
 =\frac{\|c_{s(\Re Dz)}\|_2^2+\|c_{s(\Im Dz)}\|_2^2}{16}\le8.
\]

For \(z=(2+2i)e_0\), all real and imaginary coordinates of `Uz` are half
integers. Every Gaussian-integer output therefore has squared distance at
least \(16(1/4+1/4)=8\). The bound is sharp. Since
\(F^{-1}=JF\), \(U^{-1}=JU\), and `J` is an isometry, the inverse has
exactly the same pointwise error and the same sharp witness. Finally, `D` is
an integral Gaussian-unit diagonal: `Uz` is Gaussian-integral exactly when
both real lanes of `A Dz` are integral. The exactness of `R` on `L` gives
`Fz=Uz` on all such inputs.

The native affine period
\(\Omega=D^{-1}(\Gamma+i\Gamma)\) has index \(4096^2\) in
\(\mathbb Z[i]^{16}\). It is `U` invariant because, in `D` coordinates, the
linear action is `-B` on each real lane. This is a componentwise construction;
no lower bound for a different coupled complex construction is inferred.

## 7. Period lower bound and the fixed-block word interface

CrocSwap/integer-mult-bounds#6761 proves: if an odd integer-valued real map has
full-rank affine period with slope `A` and commutes with `K`, then its period
index is divisible by 4096. Section 5 checks both hypotheses here. The present
index-4096 period therefore attains that earlier bound. The independent review
checks the predecessor's decisive finite ranks and hypothesis applicability;
the lower-bound theorem retains its predecessor attribution.

For every integer `m`, exact group consistency gives

\[
 F^{2m}=J^m=U^{2m},\qquad
 \|F^{2m+1}(z)-U^{2m+1}z\|_2\le\sqrt8.
\]

The second assertion follows by reducing the exponent modulo four: the two
odd possibilities are `F` and `JF`, and the two corresponding ideal maps are
`U` and `JU`. Thus repeated copies and inverses of this **same fixed block**
do not accumulate rounding error with word length. Global Gaussian scalars
can be moved through the word exactly. This closes the fixed-block native
square/fourth-power interface left open by #6758.

### Bounded-error attainment of the sharp tensor witness bound

The certificate also enforces the exact cycle

\[
 T:e_0\longmapsto e_3\longmapsto e_{15}\longmapsto e_{12}
       \longmapsto e_0.
\]

For each transition `z -> y`, its correction is `c=4y-SWz`. All four
corrections have squared norm 24, vanish under both weighted sums, and obey
`c_next=-Bc`. Their positive class labels are `64,849,3920,3136` and their
negative labels are `201,960,4049,3289`. These eight labels are distinct and
outside `L/Gamma`. The search fixes their matching edge before assigning the
remaining orbits. The complete certificate, not merely the local cycle, passes
all 4096-class obligations. Since `D_33=-1` and `S_33=1`, it follows that
`F(e0)=e3`.

This composes with the general
[tensor-obstruction theorem](https://github.com/CubeJerry/integer-mult-bounds/blob/408969010e33a5aacdeecc164a554111e09f8f36/research/gaussian-rounding-tensor-obstruction/PROOF.md).
Here is the complete specialization, so the new optimality claim is directly
reviewable in this package. Put `alpha=-4`, `lambda_j=i^wt(j)` and
`X0=lambda e0^T`. Every lambda entry is a Gaussian unit,
`U lambda=-4e0`, and `-4U` has Gaussian-unit entries. Applying the same `F`
independently to every row and column gives

\[
 F_{\rm row}F_{\rm col}(X_0)=e_0(-4Ue_0)^T,\qquad
 F_{\rm col}F_{\rm row}(X_0)=e_0(-4F(e_0))^T.
\]

The first order uses exactness on integral ideal images; the other uses global
unit covariance, followed by the same exactness. Their squared Frobenius
difference is therefore `16 ||Ue0-F(e0)||_2^2`.

For any admissible injective map, `w=F(e0)` is nonzero because `F(0)=0`.
Sum preservation also implies nonzero `w`. Each real or imaginary component
of `u=Ue0` has absolute value at most `1/4`. If
`L1(w)=sum_j(|Re w_j|+|Im w_j|)`, Gaussian integrality gives

\[
 \|u-w\|_2^2
 \ge 1+L_1(w)-\tfrac12L_1(w)
 \ge \tfrac32.
\]

Thus the squared discrepancy on this fixed tensor witness is at least 24.
The new certificate attains it: `w=e3` and `Re(u_3)=1/4`, so the error
squared is `2-2(1/4)=3/2`. More explicitly the first-row defect is
`D 1 + 4e3` and every other row vanishes. The `(0,3)` outputs are `-1` and
`-4`; all sixteen first-row entries differ, with squared norm `9+15=24`.
The independent checker evaluates all 256 entries in both orders.

This establishes sharpness at `n=4` while retaining bijectivity, exact sum,
global unit covariance, exactness on integral ideal images, the uniform
sharp error `sqrt(8) h`, and the native square `F^2=J`. The companion theorem's
unbounded-error sharpness example is not needed. The claim concerns the
specified witness `X0`: it is **not** a worst-case tensor-discrepancy optimum
and does not make the two row/column actions commute. Their ideal linear
counterparts commute, but this exact nonlinear difference is unavoidable
under the stated hypotheses.

No general native word compiler, separately rounded individual-axis
commutation, or all-size graph flatness follows. These distinctions matter
when substituting the block into a supplier.

## 8. Costs and complete-bound boundary

A direct fast reference evaluation applies one 16-point real Walsh transform
per lane: 64 additions/subtractions per lane, followed by 16 correction
additions and 16 exact quarter divisions. Thus the complex transform uses
160 full-word additions/subtractions and 32 quarter divisions, **in addition
to** signs, low-bit reads and classification, table addressing and retrieval,
ordinary reads/writes, scratch management and any reversible cleanup. The
inverse adds the coordinate-complement permutation, whose physical routing
also requires a bill. These are arithmetic counts, not a primitive-operation
or tape-cost certificate.

The expanded correction payload has 4096 entries of sixteen signed four-bit
values: 262,144 logical bits, or 32 KiB, shared between two real-lane lookups.
The 12-bit class label does not imply constant-time or free random access in
the repository's physical model. Certificate expansion and authentication are
offline reference setup; a physical implementation must specify initialization,
control, retained stock, table access, workspace and cleanup costs explicitly.
For component magnitudes at most `M`, a raw signed-Walsh-plus-correction
numerator is bounded by `16 M + 5`; this does not by itself establish the
surrounding caller's precision or word-width invariant.

The credible next connection is the retained four-axis dirty-port/precision
interface used by #6509 and #6758: the same sharp radius remains available,
while restoration and repeated fixed-block words now obey the exact native
square. Before any global improvement, one must bind this particular table
and classifier to the actual input cuts and helper state, charge its physical
access/cleanup/routing and precision work, and derive a changed complete paid
recursive profile. The present package supplies none of those prices and
changes no selected supplier or frontier. **No new κ.**
