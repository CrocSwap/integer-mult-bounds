# Selected-interface families and local words

This annex adopts five previously reviewed families from the campaign.
They give complete-minor geometry, a signed-pivot construction, and exact
local words on two historical providers. The family proofs extend the
single selected examples in the parent package. They do not give a routed
caller or a complete kappa improvement. The accepted parent files and
the separate spectral annex remain unchanged.

| Family | Adopted result | Frozen proof or review |
| --- | --- | --- |
| B05 | All 64 complete-minor unions, all 20 balanced splits, serial gauges, and a 42-parameter positive-metric obstruction | [Structured review](frozen/lanes/bridge-review-20261017/structured-centres-review-20261018/REVIEW.md) |
| B06 | Signed principal-unit theorem, six-step ordinary factor, and 960 algebraic pivot selections | [Signed-pivot theorem](frozen/lanes/bridge-review-20261017/signed-centres-review-20261018/SIGNED-PIVOT.md) |
| N06 | Five raw selected-exchange variants on each provider | [Raw-word review](frozen/lanes/independent-review-20261017/NEW-RAW-REVIEW.md) |
| N08 | Five signed or oblique map forms on each provider | [Signed-word review](frozen/lanes/independent-review-20261017/NEW-SIGNED-REVIEW.md) |
| N10 | Four complete forward words with a direct live-field eight-line suffix | [Live-field review](frozen/lanes/new-native-recipes-20261017/forward-eight-review-20261018/REVIEW.md) |

[SOURCES.json](SOURCES.json) binds the exact source files. The original
proofs, reviews, programs, and freeze records remain byte-exact. The
[fresh replay](evidence/REPLAY.json) is separate from the original review
dates and from publication approval.

## Structured response and complete minors

The partial response has a closed 64-port Hadamard block with square
`4I`. The structured response keeps that block and uses
`E_48 = -I + K^T K/2` on the other 48 ports, where `K K^T=12I_8`.
Six complete eight-port minors partition this block. Each has Gram
`2I_8`. All 64 unions satisfy the stated selected and ordinary Gram
identities. All 20 unions of three minors give dyadic 24/24 interfaces.

The [complete-minor theorem](frozen/lanes/bridge-review-20261017/structured-centres-review-20261018/COMPLETE-MINOR-INTERFACES.md)
has a more general form. Let `K` consist of `d >= 4` square minors,
each with Gram `lambda I`, where lambda is a positive power of two.
Select `k` complete minors. For the response `J=I-K^T K/lambda`, the
ordinary and data maps have dyadic inverses at an interior split
`2 <= k <= d-2` exactly when both `k-1` and `d-1-k` are powers of two.
The query-preserving balanced case has `k=d/2`; it is dyadic exactly
when `d/2-1` is a power of two. This theorem concerns unions of the
specified complete minors. It does not classify irregular port sets.

At one selected minor in the actual six-minor family, the data map has
rank 40 and an explicit eight-dimensional kernel. The source blocks
satisfy `BD=5I_8`. A dyadic observation `M` with dyadic-unit `MD` must
give stacked observation rank 16 for `[B;M]`; the proof reduces modulo
five. The rational choice `M=B/5` has rank eight instead. At five
selected minors the ordinary eight-port map is zero. These endpoint
facts do not bound the number or rank of native children.

The actual native forward words give `Y += E X`; the backward words
give `X -= E^T Y`. The backward word is not an inverse-response word.
The partial and structured words cost 86,664 and 87,360 real scalar
primitives, respectively, in both orientations and on both providers.
Each has 3,507 native children with rank mass 5,073.

The structured response has determinant `2^64 * 5^8`. Its full rational
inverse requires division by five. Its common-frame interface gauges
avoid that division within the stated selected split. The original
data gauges `A,A^-1` cost 2,688 each; the ordinary gauges `H,H^-1` cost
1,236 and 1,332. Version two gives the same maps at 2,368 each for
`A,A^-1` and 1,172 each for `H,H^-1`. Each word uses one serial owned
field `C0`, which starts and ends at zero. It is zero after every query.
A separate entry CLEAR, if required, costs two real primitives. These
common-frame gauges do not supply mixed-frame access or the separate
64-port gauge.

## Positive diagonal metrics in the stated family

The retained proof concerns the specified 42-dimensional real symmetric
response family `E=sum_i w_i S_i`. Its exact zero-diagonal witness
expands `tr(Y E D E)` for every positive diagonal `D`. All 112 coefficient
polynomials are checked. Strict positivity forces the ten coefficients
`w_32,...,w_41` to vanish. The remaining response has rank at most 64,
and the Hadamard block attains that rank.

Thus no invertible real diagonal input and output gauges make a full
112-port orthogonal response within this family. The theorem does not
cover nonsymmetric reciprocal pairs, a larger response family, changed
native words, or a different representation. Its 42-dimensional scope
comes from the exact retained directions, not from a claim that a finite
search found all possible responses.

## Signed pivots and data-carried centre values

For the actual component-sign response, write
`J=G-K^T Lambda K/lambda`, where `G` is a symmetric signed permutation.
Choose selected ports `S` whose partners `T=G(S)` are disjoint from S.
If the selected and partner centre minors are dyadic units, the selected
and ordinary principal blocks `L` and `H` are dyadic units. Under
`G K^T=K^T Lambda`, a unit selected minor also gives a unit partner minor.
The [six-step factor](frozen/lanes/bridge-review-20261017/signed-centres-review-20261018/SIGNED-PIVOT.md)
uses the arbitrary data in the partner fields as centre coordinates.
It restores their required ordinary output and needs no zero work field.

For the displayed selection `S=[0,7,15,36,42,46,79,89]`,
`det(L)=det(H)=1/16`. The general two-principal-unit data interface and
its inverse are dyadic even though the full response has an odd
determinant. Literal common-frame `H,H^-1` each cost 1,648 primitives;
`A,A^-1` each cost 4,720. All four use existing data fields, with no
COPY, CLEAR, owned field, or native child. Both native response
orientations cost 87,360 primitives at mass 5,073 and 3,507 children.

For the fixed sign pattern, the graph has six eight-cycle covers and
three covers made from two four-cycles. Its nonsingular port choices
number `6*2^7 + 3*2^6 = 960`. The checker covers all nine cycle covers
and all 256 choices per cover. This is exhaustive only for this fixed
sign pattern and cycle-cover construction. Only the displayed selection
has emitted and priced gauge words. The other 959 selections have the
algebraic guarantee.

The component-sign family also has a sharp lower bound of eight selected
ports for a dyadic ordinary principal inverse. Jacobi's identity and
the inverse denominator give fifth-adic valuation at least `8-s` for
selection size `s<8`. The displayed sets attain eight. This bounds
selection size; it is not a native capture-rank bound.

## Raw selected exchanges on the retained clean core

This family uses `S=[0,7,20,27,36,46,57,111]` and the original raw
response `J=[[0,-B],[-D,I-DB]]`, with `BD=13I`. It is different from
the component-sign response in the preceding section. Physical input
is `(Qx,y)` and physical output is `(F x', F Q^-1 y')`. The formulas
retain each port operator in order.

B0 carries the original selected X input into productive selected Y
without a new native child. F8 carries the dense ordinary query into
completed selected X and adds eight rank-one calls. B8 and B16 add one
or two eight-line corrections; F0 omits the forward input code. The
[proof](frozen/lanes/new-core-transfer-20261017/RAW-SELECTED-TRANSFER.md)
and review give every complete map and both orders of the B0 and F8
content inverses. An inverse formula is not a priced native decoder.

| Word | Real scalar primitives | Native rank mass | Children | Added rank-one calls |
| --- | ---: | ---: | ---: | ---: |
| B0 | 168,896 | 5,073 | 3,507 | 0 |
| B8 | 173,104 | 5,081 | 3,515 | 8 |
| B16 | 177,312 | 5,089 | 3,523 | 16 |
| F0 | 164,944 | 5,073 | 3,507 | 0 |
| F8 | 169,152 | 5,081 | 3,515 | 8 |

Each row applies to both providers and includes the full retained
164,514-primitive clean core. Each added line has two explicit monomial
wrappers. The seven final CLEARs of C1 through C7 cost 14 primitives and
are included. All eight owned outputs are zero. Productive information
return does not supply a free code conversion between calls.

## Signed-unit and oblique words on that core

This separate signed family has `S=I-KR-Pi`, `K=R^T/4`, and the same
selected coordinates as the raw family. It is not the component-sign
matrix used for the 960 pivots. The actual identities are `RK=14I`,
`R Pi K=I`, and `P S^-1=-Pi` for `P=Pi K R`. The full S and its inverse
are dyadic. The five local forms on each provider are

```text
F_S(x,y)          = (x, y+Sx)
B_S(x,y)          = (x-Sy, y)
coded F_S(x,y)    = (x, S(x+y))
coded B_S(x,y)    = (S^-1 x-y, y)
oblique B_S(x,y)  = ((S^-1+Pi)x-y, y-Pi x).
```

| Map | Real scalar primitives | Native rank mass | Children |
| --- | ---: | ---: | ---: |
| Plain signed forward or backward | 164,626 | 5,081 | 3,515 |
| Coded signed forward or backward | 171,938 | 5,081 | 3,515 |
| Oblique backward | 172,050 | 5,089 | 3,523 |

Each bill includes the retained clean core and literal boundary work.
A signed boundary has eight new rank-one calls and sixteen wrappers;
the oblique word has two such boundaries. C0 returns to zero, while
unused C1 through C7 retain their arbitrary inputs. This differs from
the raw words' explicit eight-zero-output contract. A coded target can
leave holes; it is not automatically a mixed retiring target.

## Direct phase on eight current live fields

This suffix uses the changed signed response and the selection
`[0,7,15,36,42,46,79,89]`. It acts directly on the eight current selected
X fields after the forward word. First apply positive Q, then subtract
`L Y_S + B X_U` from selected X at the completed view. The actual source
values are `Y_S=q d` and `X_U=k`; d is arbitrary. The complete output is

```text
physical X = (Qh,k),        physical Y_S = q d,
logical Y_U = H(v+k)+D q d  (balanced),
logical Y_U = v+Hk+D q d    (raw).
```

The exact identity `Q_v=P_G Q_e0 P_G^-1` gives each new live-field call.
All translations commute, so `Q_v F=F Q_v` with the full global phase.
The fresh independent check covers all 4,096 recipe columns and all
4,096 FULL-commutation columns. It also checks arbitrary current d in
each of the four complete words. No Q is moved through L, B, D, or H.

The final scaled subtraction costs 1,312 real primitives, compared with
1,600 for the direct form. Complete raw and balanced words cost 89,088
and 92,784, respectively. Each has 3,515 children and rank mass 5,081,
with profile `2441H1+724H2+228H3+102H4+20H5`. Relative to its preceding
word, the suffix adds eight H1 calls and sixteen pure-permutation
wrappers. It uses no new owned or private field. The wrappers remain
explicit and are not included in the scalar subtotal. Their global
descriptor and access costs remain open.

## Replay and evidence limits

Use Python 3.11 or later and the standard library. Run one process and
keep at least 3 GiB free disk space. Use a new output directory outside
the annex:

```sh
python3 -I -B replay.py --out /tmp/selected-interface-families-annex
```

The final line must be:

```text
PASS_SELECTED_INTERFACE_FAMILIES_ANNEX
```

The runner copies the 133 pinned files to a new scratch tree with the
original relative layout. It runs six original independent checks in
normal and optimized Python. Every new receipt must match its frozen
bytes. Compressed source containers and their decompressed payloads are
both checked. No source or import adaptation is used.

The checks cover 36 complete local words per mode, each with all 640
arbitrary live and owned input columns, including 408 borrowed helpers.
They also check the 91 private zero-buffer lifetimes, stated owned
outputs, exact scalar frames and costs, both interface inverse orders,
the finite geometry families, and the new signed-line kernels. Negative
controls reject omitted exchanges, wrong line signs, wrong oblique
returns, borrowed-helper clears, and missing live-field subtraction.

The [retained core-phase review](frozen/lanes/independent-review-20261017/NEW-CORE-NATIVE-REVIEW.md)
supplies the unchanged core's orientation-specific phase records and
helper wrappers. This annex replays the complete ordered words and new
line kernels. It does not rerun that core-phase suite, the parent suite,
or the original emitters and their source-generation toolchain. The
formal warp replay and retained phase proof have separate roles.

## Open next questions

Literal gauges and native access for the other 959 algebraic signed
selections remain open. A complete caller must also supply routed
transitions, physical source access, paired exterior phases, endpoint
decoding, helper-owner histories, recursive child hosting, wrapper
costs, storage, and precision. The local bills cannot be inserted into
a supplier recurrence without those proofs. Applicability to the
current selected supplier is not established.

[ANNEX-MANIFEST.json](ANNEX-MANIFEST.json) binds this annex separately.
[NOTICE.md](NOTICE.md) retains the source credit and license. Frozen
pending-review and publication-authority sentences record their original
historical stage. No new research or complete kappa claim is added here.
