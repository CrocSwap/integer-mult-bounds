# The finite boundary cost of the three P104 caller templates

On the native graph of PR #7756 at
`6b0044123aad114cf71ca2bb0e98741e5a27c7b5`, one contiguous 2,048-call schedule
exchanges 56 homogeneous A and eight homogeneous B roots for 64 mixed
roots relative to two sealed 1,024-call batches. Its signed target-minus-paid
margin increases by $224(f(1)+f(8)-f(9))$, where $f(r)=r^{1-\kappa}$.
The exchange is the optimum at this length among fully occupied,
chronological placements of the three literal templates. [PR #7756](https://github.com/CrocSwap/integer-mult-bounds/pull/7756)

## The endpoint bound and its realization

The physical native call has 96 A ports and eight B ports. At call $t$,
the body color is $t\bmod 16$. Each independent root visits exactly one
port on each of sixteen strictly increasing calls and sees each color once.
The literal visit words are $A^{16}$, $B^{16}$ and $A^7B^2A^7$.
Full port occupancy requires equal numbers of calls of each color, since
each color has 104 ports per appearance and consumes one visit per root.
Thus a nonempty batch length $K$ must be a positive multiple of sixteen.

At call zero all eight B ports must belong to distinct homogeneous B
roots. A mixed root needs seven earlier visits before its first B visit.
Let $A,B,M$ count homogeneous A, homogeneous B and mixed roots. Counting
visits gives

```math
14M+16A=96K,\qquad 2M+16B=8K,\qquad B\geq8.
```

Consequently $M=4K-8B$ and $A=5K/2+7B$. The two count bounds are
simultaneously attained exactly when $B=8$.

For each even start $s=2,4,\ldots,K-16$, place a cohort of eight mixed
roots at $s,\ldots,s+15$. At each call there are at most eight potential
cohorts, one per local slot of the matching parity. There are seven A
slots of either parity, so the mixed roots use at most 56 of the 96
A ports. Their B visits exhaust eight ports at each call in the single
interval from 9 through $K-8$, with one cohort at each such call.
This interval has $K-16$ calls, leaving eight B ports of each color.
For each parity-compatible A slot and color, exactly $(K-16)/16$
cohorts use that slot at that color. The seven A slots per parity
therefore leave $96K/16-8\cdot7(K-16)/16=5K/2+56$ A ports of each color.
For either type, take the entries at the same index in the sixteen
remaining color queues and sort them by call to obtain one homogeneous
root. The colors are distinct, so their calls are distinct. The same
construction has empty mixed cohorts at $K=16$ and gives 96 A roots
and eight B roots.

Two sealed 1,024-call copies have $(A,B,M)=(5232,16,8064)$. The 2,048-call
schedule has $(5176,8,8128)$. The eight additional start times are 1010
through 1024 in strides of two, accounting for the 64 mixed roots. Their
B visits fill calls 1017 through 1032 inclusive.

## Signed rank exchange at fixed length

The independently read literal profiles have the following histograms.
The common paid rows are four at each of ranks 8, 16, 24, 32, 40, 48
and 56. The common productive rows are two at rank 129 and four at each
of ranks 17, 25, 33, 41, 49, 57 and 65.

| Root | Paid rows beyond the common rows | Productive rows beyond the common rows |
| --- | --- | --- |
| A | Four at rank 1 | Four at rank 9 |
| B | 28 at rank 8 and four at rank 9 | Four at rank 9 |
| Mixed | None | None |

Reducing $B$ by one eliminates seven A and one B root and adds eight
mixed roots at fixed $K$. It removes 28, 28 and four paid rows of ranks
1, 8 and 9, respectively, and removes 32 productive rows of rank 9.
The signed margin increases by $28(f(1)+f(8)-f(9))$.
For $0<\kappa<1$, strict concavity and $f(0)=0$ give
$f(1)>f(9)/9$ and $f(8)>8f(9)/9$. The native contributions depend
only on the number of calls of each color. Therefore the feasible
endpoint $B=8$ strictly maximizes the complete signed margin at each
feasible finite length throughout that exponent interval.

## Arbitrary inputs, charts and cleanup

Give each root its own independent input field for every local register.
The verifier binds each local contact to the compact native address list
for its physical port. Every call has 400 distinct caller owners at 400
distinct main addresses. All 862 helpers have fresh owners
$(t,\text{source label})$ and retain their original charts. The protected
source labels 325 and 1087 map to compact roles 313 and 971. Both retain
their rank-four route from chart 3 to chart 237 and return to their own
owners at every call. The pinned native arbitrary-input identity provides
the direct sum of the port operators and the independent helper returns.

Each main field is converted immediately before its native call and
restored immediately afterward, with both views acting on exactly the
native main-owner table. In the central nine coordinates, use the
orthogonal map $P$ with columns given by the port head $q$ and its
eight pinned basis vectors. Extend it by the identity on the 128 body
axes. If $F$ is the sum of the nine coordinate phases, the entry
translation $\tau$ obeys

```math
F(k)-(PF)(k)=2\langle\tau,k\rangle\pmod4.
```

The verifier checks the two directions on every central character and
checks that the affine exit map is the exact inverse of entry. It maps
the canonical head to $q$ with its phase. The Y frame differs by the
inverse head, so the same translations correct the X and Y frames.
The four signed native endpoint operators at each body color include
the original rank-zero compact entrance and exit adapters. Their conjugates use the same canonical
head $Q$ and the current body product $D_{t\bmod16}$. Before that body
product, an A port sends $(x,y,u,v)$ to $(x,y+Q^{-1}x,u-Qv,v)$ and a
B port sends $(x,y)$ to $(x-Qy,(Q^{-1}x+y)/2)$. Each body is a
disjoint eight-axis block. Renaming the sixteen formal body variables by
each root's actual color permutation therefore preserves the pinned
local signed Gaussian identity, every paid mask rank and every terminal
rank for arbitrary inputs. A negative odd terminal head is corrected by
the ordinary translation $Q^2$.

The verifier projects the contact table and the intervening operations
onto each root. The local block before its next contact runs after its
previous exit view. Its operations name only that root's registers and
execute in literal order. Each final block runs after that root's last
exit. This preserves the source and destination observations at their
original positions in the local word. The pinned native execution holds
its public inputs through terminal installation and clears its private
homes. Caller services run in serial between calls. A normalizer retains
two source components, two translated components, eight products and
four sums, accumulates both summands before output installation, and
clears its 16 temporary component arrays. Complex literals need at most
the same stock. Paid query and idle services return before the next
local instruction. Their source, retired temporaries and persistent
terminal fields retain their distinct roles.

## Verification scope and reproduction

The proof applies to nonempty batches on the fixed native graph with
the three literal templates, independent owners, full occupancy and
strict chronology. Changed templates, extra contacts per root per call,
shared owners, incomplete color coverage, partial occupancy, and other
native graphs fall outside the proposition. The exact local Gaussian
identities and the native arbitrary-input and physical cleanup results
are pinned inputs here. Compiled physical and outer admissibility require
the separate finite application and retain the five framework assumptions
for native all-column application, owned erasure, the compiler, precision
and tape accounting, and analytic recovery.

The full stream of emitted caller macros reconstructed by the standalone verifier
has 35,717,248 records and SHA-256
`3b326189234984d7797566fa4732d4e2698db778f117cd09bb5654ea740c5563`.
The same code reproduces the pinned 17,777,792-record 1,024-call stream.
It checks all 819,200 main bindings and both views on each binding in the
2,048-call stream. The guarded native installation and CLEAR operations
are replayed separately against the pinned graph. The two finite character probes in the application
test numerical behavior on their specified inputs. They supplement the
full structural reconstruction and the arbitrary-input composition.

At equal call count each side uses 1,638,400 view permutations and
1,638,400 view translations, with 22-bit scalar coefficients and a
$2^{30}$ scalar step rate. The contiguous caller uses 126,976 more
nonreal literals and 2,176 fewer terminal head corrections. These
occurrence changes contribute 248,416 more ordinary map slots,
8,083,456 more Gaussian component slots before the factor of 32,
and 512 fewer odd conversions. The signed invoice delta removes 224,
224 and 32 paid rows at ranks 1, 8 and 9 and 256 productive rows at
rank 9. The application prices both complete invoices.

```sh
python3 -I -B verify_seam.py --source pr7756 --output seam-receipt.replay.json
```

The source directory contains the pinned `p104-parallel-bank-punctures`
package. The source construction runs in a separate Python process to
supply the native graph and layout. Alternatively, pass its graph and
layout exports with `--native-graph` and `--native-layout`. The verifier
reconstructs the caller using only the input data. The receipt records
rejection of simultaneous visits, a wrong port type, repeated color,
port collision, a missing exit view, an omitted phase translation, and
partial scratch clearing. [Pinned native and caller work](https://github.com/CrocSwap/integer-mult-bounds/tree/6b0044123aad114cf71ca2bb0e98741e5a27c7b5/research/p104-parallel-bank-punctures)
