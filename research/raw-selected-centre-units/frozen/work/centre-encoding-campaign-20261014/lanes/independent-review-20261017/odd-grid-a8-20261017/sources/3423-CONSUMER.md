# Actual P104 downstream interface and frame-path closure

Prepared by Clear1nsight, with substantial OpenAI assistance.

## 1. Scope and frozen sources

This proof follows the actual arithmetic surrounding the first P104 collector
through **zero-based event 4516**. Its numerical state consists of the following
63 persistent Gaussian arrays, each with 512 entries:

- `Y22` through `Y32`, and `Y63` through `Y103`: 52 banks;
- `D27` through `D31`: five banks;
- `Q7`: one bank;
- `G27` through `G31`: five banks.

The owned private bank `C` exists only during events 2025–2039. Every write to a
named persistent bank depends only on these banks or `C`. The selected state
therefore has a closed chronological numerical evolution. All 675 ADDs which
read these banks and write other banks remain explicit outgoing ports, with
their event, target, coefficient, frame and initial-input row retained.

The resulting object is an **open interface program**, not a claim to have
numerically executed the entire 4,517-event prefix. Other writes and native
transports of external banks remain outside this proof. In particular, no
initial or terminal contract for the external `X` banks is inferred merely
from their appearances as recipients.

The source bytes are the PR2586 word and recipes retained by the rounded
collector archive on canonical commit
`6f100d4bb5083f8c35d96fd95a539811c62f245c`:

| Input | SHA256 |
|---|---|
| `research/p104-rounded-collector/inputs/WORD.json` | `cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50` |
| `research/p104-rounded-collector/inputs/NATIVE.json.gz` | `ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d` |

The literal chart is
`Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)`. Write

\[
 O=[256,136,64,40,16,4,2,1],\qquad Q=[364],\qquad
 F=[256,128,64,32,16,8,4,2,1].
\]

The selected 576 state events consist of 392 native transports with total rank
581, 182 ADDs, one private allocation and one erasure. They include the minimal
257-event producer and the 15-event collector. These pieces must not be added
to the 576-event bill a second time.

## 2. Admitted initial states and real quarter sites

Let \(\pi=1+i\) and retain PR3382's Newton module

\[
 \mathcal B_9=E\mathbb Z[i]^{512},\qquad
 E=\begin{pmatrix}1&0\\1&\pi\end{pmatrix}^{\otimes9}.
\]

The strengthened initial contract is

\[
 Y_j^0\in4\mathcal B_9\quad(j\in\mathcal Y),\qquad
 D_j^0,Q_7^0,G_j^0\in\mathcal B_9,
\]

where \(\mathcal Y=\{22,\ldots,32\}\cup\{63,\ldots,103\}\).
Every one of these 63 initial physical frames is the empty frame. The D, Q and
G arrays can be independently dirty within this contract.

PR3382 proves that the actual Gaussian butterfly, its inverse and the source's
affine address/quadratic phase wrapper alphabet are automorphisms of
\(\mathcal B_9\). Consequently they also preserve \(4\mathcal B_9\).
The executable here independently checks the actual wrapper schema and source
convention, and executes the signed-floor arithmetic without importing
PR3382's executable model.

Every Y bank is transport-only throughout this word: it is never an ADD
destination. Thus admission at a named later quarter site is tied to a real
initial bank. For example, `Y103` is transported at events

\[
 207,980,1088,1184,1315,1470,1645,1834
\]

before it reaches frame F. Its first relevant downstream quarter is

```
2162: D28 -= Y103 / 4    at F
```

and its first quarter into Q7 is

```
4174: Q7 -= Y103 / 4     at F.
```

For either site, the exact condition is

\[
 Y_{103}^{\rm current}\in4\mathcal B_9
 \quad\Longleftrightarrow\quad Y_{103}^{0}\in4\mathcal B_9.
\]

This equivalence uses the actual path's bijective restriction to
\(4\mathcal B_9\),
not a mere forward sufficient bound. When the target is already in
\(\mathcal B_9\), its quarter update remains in \(\mathcal B_9\) if and only
if this source condition holds. Componentwise divisibility by four alone is
weaker than this Newton-module condition.

The same 52 initial Y banks supply all 52 producer quarter reads, all 52 D
cleanup quarters and all 52 Q7 cleanup quarters. Every outgoing quarter port
also has an admitted Y source. Thus this stronger *real initial contract*
supports the later operations; no new preparation is silently inserted at
event 2162 or 4174.

## 3. Exact authentication of the actual frame paths

Cancellation across different frame paths cannot be inferred from equal frame
labels. The checker proves a finite operator certificate for all 392 native
occurrences in the selected state program.

Use Gaussian Pauli operators

\[
 P(u,v,k)|x\rangle=i^k(-1)^{v\cdot x}|x\mathbin\oplus u\rangle.
\]

For a source wrapper

\[
 W|x\rangle=i^{s(x)}|Ax+b\rangle,
 \quad
 s(x)=p+\sum_j\ell_jx_j+2\sum_{j<k}q_{jk}x_jx_k\pmod4,
\]

the address matrix is checked invertible over \(\mathbb F_2\). Only the strict
upper triangle \(j<k\) of `quadratic_rows` is used. Diagonal and lower-triangle
bits in the archive are not additional phase terms.

The conjugated Pauli has

\[
 u'=Au,\qquad
 \widetilde v=v+(\ell\bmod2)\odot u+Q_{\rm off}u,
 \qquad v'=A^{-T}\widetilde v,
\]

\[
 k'=k+s(u)-s(0)+2v'\cdot b\pmod4.
\]

For every Pauli encountered during the path proof, the implementation also
checks this formula directly at all 512 basis addresses using the wrapper's
captured permutation and phase values. This is a separate finite check of the
formula used in the certificate.

For the source butterfly C on bit j,

\[
 C X_j C^{-1}=X_j,\qquad C Z_j C^{-1}=-iX_jZ_j,
\]

so its action is \(u_j\leftarrow u_j+v_j\),
\(k\leftarrow k+3v_j\pmod4\), with v unchanged. The right wrapper,
coordinate butterflies and left wrapper are composed in the literal source
order.

The algorithm starts with the identity operator at the empty frame. When a
new frame is first encountered, its exact operator is represented by a path
of source native events. At every later occurrence of an already represented
frame, it checks both:

1. identical conjugation images of the 18 generators \(X_j,Z_j\);
2. identical images of the nonzero anchor vector \(|0\rangle\), evaluated
   with exact Gaussian numerators and powers-of-two denominators.

These two conditions prove equality of the full 512-dimensional operators.
Indeed, the ratio of two invertible operators with equal generator actions
commutes with all Z generators, so it is diagonal, and commutes with all X
generators, so all diagonal entries are equal. Equal nonzero anchor images
then fix that scalar to one. A global phase cannot be discarded.

The source certificate covers 163 distinct frames, 392 occurrences and 230
redundant path equalities. In particular it covers the actual U at 2031 and
the separately archived V at 2033, every producer path, and all later Y, D,
Q7 and G paths. A legal-shaped mutation multiplying the actual return
wrapper's global phase by i leaves all Pauli actions unchanged and is
rejected by the anchor comparison.

Let \(A_H\) be the resulting exact native path operator from the empty frame
to a frame H. The finite certificate establishes

\[
 T_{H\to K}=A_KA_H^{-1}
\]

for every selected occurrence. This defines and authenticates the frame
potentials used below. The source's broader geometric interpretation in terms
of \(\Delta_H\) remains inherited from its compiler lineage; this finite
certificate does not independently rebuild that compiler for arbitrary frames.

## 4. What the actual producer, collector and later consumer restore

The exact path certificate permits the induction
\(\text{physical state}=A_{\text{current frame}}\,\text{logical row}\).
A native event changes its frame potential and leaves the row unchanged; an
ADD at a shared frame performs the same scalar row addition; zero and erase
create and remove the literal zero row. Thus the following row calculations
describe the actual physical state for every admitted input, independently
of the dense numerical fixture.

Put

\[
 s=\frac14\sum_{j\in\mathcal Y}Y_j^0.
\]

Each selected Y source is read once into exactly one of the five D banks in
the producer. Write \(\mathcal Y_j\) for that source partition. Its sizes for
D31, D30, D29, D28 and D27 are respectively 3, 7, 7, 11 and 24.

The exact source frame paths and ADD rows give the collector entrance

\[
 D_j^{\rm entrance}=A_O\left(D_j^0+rac14\sum_{h\in\mathcal Y_j}Y_h^0\right),
 \qquad
 Q_7^{\rm entrance}=A_Q\left(Q_7^0-\sum_{j=27}^{31}D_j^0\right).
\]

Therefore the literal collector's endpoint is

\[
 Q_7^{\rm collected}=A_Q(Q_7^0+s),\qquad C=0,
\]

with its five sources unchanged during the collector. This statement uses the
actual archived U/V composition authenticated above.

The subsequent D cleanup quarters exactly reverse each D bank's producer
source list. Their last events are:

| Bank | Quarter count | Last cleanup event |
|---|---:|---:|
| D31 | 3 | 2213 |
| D30 | 7 | 2279 |
| D29 | 7 | 2308 |
| D28 | 11 | 2390 |
| D27 | 24 | 2480 |

At these endpoints, the corresponding physical bank is \(A_FD_j^0\).

The first subsequent reads of collected Q7 are the five real unit ADDs
3052–3056, into G27–G31 at frame Q. Each G bank has been transported from its
independently dirty initial empty-frame state at events 3020–3024. Just after
the reads it contains

\[
 G_j=A_Q(G_j^0+Q_7^0+s).
\]

The G arrays are subsequently read by actual X-target ports and transported
through their distinct source frame paths. Q7 is transported to F at 4164;
the five unit subtractions at 4165, 4167, 4169, 4171 and 4173 give

\[
 G_j^{\rm final}=A_FG_j^0.
\]

Finally Q7 subtracts each of the same 52 Y banks once at F, from event 4174
through 4516, so

\[
 Q_7^{\rm final}=A_FQ_7^0.
\]

All 63 actual final physical frames are explicitly checked to be F. Every
persistent bank consequently ends with its initial value transported by
\(A_F\). Gauge-coordinate rows return to their initial rows; physical arrays
are not claimed unchanged across different frames. The private C bank is
checked literally zero before erasure.

Changing the actual event 2162 from `-1/4` to `+1/4` preserves the stated
lattice admission but leaves D28 with residual
\(A_F(Y_{103}^0/2)\). The endpoint check rejects this source-shaped control.

## 5. Every outgoing side effect remains visible

The 675 chronological outgoing ADD ports comprise:

| Actual read | Port count |
|---|---:|
| Y to other D banks | 348 |
| Y to other Q banks | 171 |
| G27–G31 to X | 104 |
| Q7 to X before its producer changes | 52 |

The last row consists of events 492–543. Omitting it would discard the dirty
Q7 compensation and misstate the useful external map. There are no outgoing
D reads to external banks in the chosen range.

The verifier derives integer input rows using \(Y_j^0/4\) as Y symbols and
the initial D/Q/G arrays as other symbols. Since frame paths have already
been authenticated, every port at frame H has its exact physical increment

\[
 \delta_{e}=A_H\sum_b r_{e,b}z_b,
\]

where \(z_Y=Y_Y^0/4\), the other \(z_b\) are initial arrays, and
\(r_{e,b}\in\mathbb Z\) is retained in the receipt. Its literal source
coefficient and source array are also recorded. No unobserved callback or
recipient history is substituted for this interface.

For the X ports, summing these increments after applying their respective
\(A_H^{-1}\) yields, for each of 52 distinct targets,

\[
 \sum_{e\to X_t} A_{H_e}^{-1}\delta_e
 =\frac{\epsilon_t}{2}\sum_{j\in\mathcal Y}Y_j^0,
 \qquad\epsilon_t\in\{+1,-1\}.
\]

There are 39 positive and 13 negative target signs. All dirty D, Q and G
coefficients cancel. The **52-by-52 scalar bank matrix** has rank one; after
expanding every array into 512 Gaussian entries, the corresponding map has
rank 512 over \(\mathbb Q(i)\). The complete sign map is retained in the
receipt. An independently written Fraction-row interpreter agrees with all
2,704 coefficients, the 63 restored input rows and all 675 port indices.

This is the frame-normalised outgoing port operator. A terminal X-bank claim
would additionally require its actual omitted updates and transports to be
composed with these ports. The other 519 Y ports remain separately retained;
they are not removed from the interface or its bill.

Each admitted port increment belongs to \(\mathcal B_9\), and is a Gaussian
integer array. The ADD is therefore exact for an arbitrary Gaussian recipient.
It preserves the recipient's membership in \(\mathcal B_9\) when that
recipient is in \(\mathcal B_9\) at the read. Future native arithmetic on an
external recipient needs its own domain proof. No claim about a recipient's
initial state follows from this local conditional statement.

## 6. The actual coefficient-coordinate maps

If values are stored as encoded arrays \(Ec\), the actual logical map of a
native frame operator A is

\[
 \widehat A=E^{-1}AE.
\]

Every admitted state or port row above then has coefficient map
\(\widehat A_H\) applied to the corresponding initial coefficient row. Unit
ADDs between two fields already in the same representation are unchanged.
Quarter coefficients apply only after the required fourfold Newton
divisibility is supplied.

This map is explicit for an arbitrary captured wrapper. For a Boolean subset
S and \(x_T=A^{-1}(1_T\oplus b)\), its Newton-coordinate action is

\[
 (\widehat Wc)_S=
 \pi^{-|S|}\sum_{T\subseteq S}(-1)^{|S|-|T|}
 i^{s(x_T)}\sum_{R\subseteq\operatorname{supp}(x_T)}\pi^{|R|}c_R.
\]

The native coordinate butterfly becomes the integer coefficient map
\((a,b)\mapsto(a+b,ib)\). Composing these formulas in the captured right,
butterfly and left order gives every real readout/transport intertwiner.

For the actual empty-to-Q operator, the canonical path is event 972. Its
complete 512-column integer matrix has 12,288 nonzero entries and maximum
absolute real/imaginary component four. Its ordered JSON-column hash is
`f6a4c95e33941a42fe2460195b9daee2d071f5396c9a441556e2f28e0e2076b3`.

For the actual empty-to-F operator, path `[203,984,1233,1818]`, the independent
Pauli-plus-anchor test proves the more explicit identity

\[
 A_F=(C^{-1})^{\otimes9},\qquad
 E^{-1}A_FE=
 \begin{pmatrix}1&i\\0&-i\end{pmatrix}^{\otimes9}.
\]

Its 512-column matrix has \(3^9=19683\) nonzero Gaussian-unit entries, with
ordered JSON-column hash
`727b837e10103ebda8ce33f8284f5204c317b2518a27f39e5e77d7413dfc2cfd`.

The distinction between A and its conjugate is visible in the actual source
map. On coefficient input \(e_0\), \((E^{-1}A_QE e_0)_0=1\), whereas
\((A_Qe_0)_0=(1-i)/2\); 17 coordinates differ. Thus the representation is
retained with its proved intertwiner. A caller requesting the unconjugated
map on arbitrary coefficient inputs cannot identify the two.

No encode/decode pair is needed at the producer/collector/consumer cuts when
the fields already have this persistent representation. Supplying arbitrary
external data through a new codec still requires a priced implementation and
acceptance of the conjugated logical map. The narrower initial Y domain is
not free preparation.

## 7. Independent execution and remaining boundaries

The checker imports no producer, PR3382 model or predecessor arithmetic
module. Its executable derivations consist of:

- exact source authentication and full-prefix frame/lifetime syntax;
- the all-occurrence operator path certificate and phase-only rejection;
- complete 512-column conjugated maps for the actual Q and F operators;
- integer symbolic rows for every selected state event and outgoing port;
- one chronological dense signed fixture on all 63 initial banks, including
  every retained Y transport from its initial value;
- 148,736 literal signed-floor versus independent exact-pair comparisons,
  784 complete-wrapper domain checks, 581 complete-coordinate domain checks,
  182 internal ADDs, 675 exact outgoing increment arrays and literal C erasure.

The complete-coordinate checks occur after each coordinate's disjoint
butterflies; complete-wrapper checks occur after each wrapper. Individual
permutation-cycle intermediates need only be Gaussian integers, since no
division occurs inside the wrapper. They are not separately claimed to be
members of the global Newton module.

The dense fixture's largest observed internal real/imaginary component is
1122. This is an observation about that fixture, not a universal bit-width or
physical precision admission. The operator identities and symbolic row proof
quantify over all admitted initial arrays independently of this fixture.

This establishes a real downstream representation contract and exact restored
internal endpoint. It does not establish the complete P104 word, an external
recipient's future domain, a physical allocation/routing implementation, a
recursive caller or a favourable supplier moment. All 675 ports, storage,
precision, control and cleanup obligations remain available to the separate
whole-bill analysis.

The final package verifier authenticates the sources and combines this
consumer evidence with the producer, independent witness and bill checks:

```sh
python3 -I -B research/p104-newton-interfaces/verify.py
python3 -I -O -B research/p104-newton-interfaces/verify.py
```

For a focused consumer replay, `consumer.py` accepts `--repo` and otherwise
resolves the source root from its package location. Its optional `--output`
path is created exclusively, so an existing receipt is never overwritten.

Credit the ywz65/PR2586 native P104 word, Arham Tahir's retained rounded
collector archive, Tekalign/PR3025's signed-floor and wrapper conventions, and
the PR3382 Newton-module theorem and independent reconstruction. Classical
Clifford/coding provenance and repository license/notice obligations remain
as recorded in the frozen predecessor packages.
