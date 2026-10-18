# An inverse P104 residue box from the forward basis

The inverse lifting map can reuse PR3035's certified **343-bit forward residue
box and the same reducer**. Reverse the active address bits and exchange the
real/imaginary components before and after the forward computation. This gives
the literal inverse, including signed floor effects. A second inverse HNF is
unnecessary: its basis is the forward basis with an explicit row permutation.

This closes the algebraic/basis part of PR3035 open question 3. It supplies
a local inverse interface and added permutation bill. Complete physical
consumption/restoration and any runtime improvement remain unresolved.
The 343-bit index is unchanged. No new supplier or kappa is claimed.

Base main `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
Source PR3035 `0cc430349a3f3dc200666bc22e997076e0a557ed`; its literal word is
Tekalign's PR3025/3033 reference, retained byte-identically by PR3035.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18982349).
Ross Richardson's [PR3043 modular reducer](https://github.com/CrocSwap/integer-mult-bounds/pull/3043),
head `b5cabfb02a3d8bc3121825144373b03a5648479d`, is complementary. It was
released during this session and leaves the inverse image lattice as a separate
obligation. This package implements no alternative modular reducer and does
not independently certify its gate invoice.
PR3037's maximality theorem is context, not a dependency of this proof.
The catalogue card and explicitly changed handoff scope are in [TASK.json](TASK.json).

## Exact all-rank identities

The retained pair P+ uses componentwise floors:

```
d = a-b; s = b+floor(d/2); d = i*d;
b' = s-floor(d/2); a' = b'+d.
```

Set `E(a,b)=(a-b,b+floor((a-b)/2))`. Its inverse is
`E^-1(d,s)=(s-floor(d/2)+d,s-floor(d/2))`, so
`P+=E^-1 diag(i,1) E`. The identical word with -i, called P-, is its inverse.

Define **S(p+iq)=q+ip**. Component exchange commutes with addition, subtraction
and componentwise floor at every signed integer, while `S i S=-i`. Thus
`P-=S P+ S`, applying S to both pair roles. Ordinary complex conjugation
does not commute with floor at negative odd integers and cannot replace S.

Let P_j apply P+ to address-bit-j pairs, and write
`L_r=P_(r-1)...P_0`, with the rightmost factor applied first. Let B_r reverse
exactly the r active address bits, and T_r=S B_r. Then
`B_r P_j B_r=P_(r-1-j)`. S and B commute and are involutions. Consequently

```
T_r L_r T_r = P_0^-1 ... P_(r-1)^-1 = L_r^-1.             (1)
```

Replacing floors by exact halves proves `T_r U_r T_r=U_r^-1` for the ideal
linear map as well. Rank zero is included: L_0=U_0=I and T_0=S. These proofs
have no rank or magnitude bound; the executable verification is finite.

## Image lattice and canonical inverse box

PR3035's Gamma_r requires even real and imaginary differences at every pair
of every ideal forward prefix. These conditions make all prefixes integral.
Let Gamma_r^- be the corresponding lattice for reverse-order ideal P- pairs.

For z in Gamma_r, trace its admissible ideal path. A pair's output difference
is i times its input difference, hence still even in both components. Its
reverse pair satisfies the reverse parity condition and retraces that integral
step exactly. This proves U_r Gamma_r is contained in Gamma_r^-.
Conversely, reversing any admissible backward path gives an admissible forward
path: the P- difference is -i times its input difference. This proves equality.
T exchanges stage order and pair sign while preserving even component
conditions, so it maps admissible forward paths bijectively to backward paths.
Therefore, without invoking maximality,

```
U_r Gamma_r = Gamma_r^- = T_r Gamma_r.                    (2)
```

Let H be PR3035's upper-triangular rank-seven basis. The row-permuted matrix
T H is a basis of U_7 Gamma_7, triangular in the permuted coordinate order.
It is not claimed to be an HNF in the original order. If c_H is the unchanged
descending forward reduction, define

```
c_-(y) = T c_H(T y).                                     (3)
```

Then y-c_-(y) belongs to U Gamma. Uniqueness and existence follow by applying
T to the forward canonical box. Its 36 one-, 125 two-, 70 four-, 22 eight-
and three sixteen-valued coordinate ranges are permuted, so the inverse box
has exactly 2^343 elements and every real residue remains below 16.
The predecessor's counterexample to using the *unpermuted* Gamma remains valid.

The exact inverse split is `L^-1(y)=U^-1(y-s)+L^-1(s)` for s=c_-(y).
More directly, for PR3035's executable forward split F, equation (1) gives
**`L^-1(y)=T F(T y)`**. The replay compares this with the literal inverse
and checks exact paired return for signed inputs.

All 256 source-basis columns are checked in both directions: U H reduces to
zero after T in H; the backward image of T H reduces to zero in H. Every
forward/reverse parity condition is checked by new code against the retained
integer-numerator ideal oracle. The predecessor's HNF/index replay is retained
source-bound coverage, not a newly independent index algorithm.

## Permutation bill and implementation boundary

T permutes **real components**; S is not complex linear. It must not silently
inherit the native Gaussian-monomial wrapper tariff. For d=2^(r+1) components,
T has d/2 two-cycles and no fixed component, because it exchanges Re/Im.

`turn_inplace` implements each cycle with three scalar swaps through one
borrowed arbitrary dirty scalar, restored exactly. Each logical scalar swap
reads and writes two cells. No data arithmetic is used.

| Boundary | Two-cycles | Scalar swaps | Real reads | Real writes |
|---|---:|---:|---:|---:|
| One T at r=7 | 128 | 384 | 768 | 768 |
| Two boundaries around one inverse split | 256 | 768 | 1,536 | 1,536 |
| Four blocks, N=512 inverse split | 1,024 | 3,072 | 6,144 | 6,144 |

These are constructive counts, not a minimality bound. Schedule generation,
loop work, storage/access and physical tape movement are additional. The
schedule can be computed by r-bit reversal or stored in d indices. Permutation
preserves widths; the scratch must accommodate the maximum working component
and its own dirty entrance value. No extra vector is needed by this subroutine.
The Python wrapper owns an input copy; F retains its original arrays. Exposing
c_- separately also needs its own two T boundaries.

The complete inverse cost in this implementation is **cost(F on T y)+2 cost(T)**.
All forward decomposition, extra narrow ideal work, lifting, buffers, precision
and cleanup remain in cost(F). Actual input/output wrappers are additional.
Fusing T with wrappers requires an explicit real-coordinate implementation
and bill. Dirty scratch restoration for T and Python array lifetime do not
establish physical restoration of F, hosting or an admitted exact wide backend.
No dependent circuit/supplier expansion is undertaken here.

## Reproduction and checks

Python 3.12 and the standard library suffice, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-inverse-residue-permutation
```

The verifier authenticates all three retained inputs before executing any
predecessor code. [PREDECESSOR.json](PREDECESSOR.json) records exact head,
paths, Git blobs and SHA256; [SOURCES.json](SOURCES.json) pins assignment
provenance. Verification reads, and never regenerates, [RESULT.json](RESULT.json).

Checks: 4,802 signed pair/direction cases; all 256 columns in both lattice
directions; 40 signed word fixtures, ranks 0..7; five inverse-split widths
through 4,090 bits; separate zero/4,096-bit boundary cases; and eight behavioral
test groups. Controls detect ordinary conjugation, omitted reversal/exchange,
unpermuted inverse-box reuse, a same-index invalid basis, nonperiods, invalid
input types, corruption before source execution and a wrong nested receipt
type. A relocated Git-free optimized replay checks standalone operation.
`IMB_RUN_ROOT` can select an existing temporary directory for export tests.
Code is bounded to ranks 0..7 and 8,192 component magnitude bits; the retained
forward split has its original 4,096-bit entrance limit. Hosted CI, independent
human/formal review and full selected cold replay are separate and unclaimed.

## Open next questions

Can the paired reducer and actual consumer fit a complete physical bill?
Compose the complementary modular reducer with (3), then charge both narrow
passes, wrappers, exact backend, buffers and restoration. That decides whether
the smaller domain pays for itself. PR3043 already reports no win for the frozen
scalar lifting invoice, so a new consumer must identify actual removed work.
Its physical/backend contracts remain unresolved. No new search is started here.

## Credit

Arham Tahir, with substantial OpenAI Codex assistance in proof, implementation,
checks and writing. Apache-2.0. Nick Petalas/PR3035 supplies the lattice, basis,
forward reducer and inverse-basis handoff; PR3037 addresses maximality.
Tekalign/PR3025/3033 supplies the lifting word, collector and scalar split.
Retain ywz65/PR2586/2555, Arham Tahir/PR2999 and the broader P104 geometry/native
lineage. The three vendored files are byte-exact and retain original notices.
Generic coordinate conjugacy, lattice transport and dirty-scratch swaps are
not claimed as new.
