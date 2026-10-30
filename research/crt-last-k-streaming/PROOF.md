# A conditional sequential lowering for the CRT last-K branch

This isolates the elementary exception in Cinna Davis's PR4100
`research/unconditional-batched-crt/CRT.md`, Section 4, retained at
`337d04939571a637aeab54a0f58f54fde811663a`. Its original bit exchange,
transformed control and complete suffix amortization are predecessor work.
The contribution here is the explicit fixed-tape two-slice lowering and its
preparation, payload, workspace and return invoice. It is conditional on
the ordinary width-one callee and the numerical evaluator; it does not
certify either of those hypotheses or the complete CRT construction.

## 1. Contract and physical order

Let an address have `L>=1` bits in **physical MSB-first positions**
`0,...,L-1`. Every one of the `M=2^L` addresses has an arbitrary `R>=1`-bit
payload. Let `V=MR`. Let `0<=H<L`, and let `j<L-H` be a target position.
Assume the Boolean function `f` omits the target and the entire final
`H`-bit suffix, for **all binary addresses**. It may depend on every
other bit and is not assumed to factor, be local, or have constant controls.

The desired endpoint is the permutation

```
x -> x XOR ( f(x) * 2^(L-1-j) ).                         (1)
```

Omission of the target makes this an involution. Suffix omission is a
separate condition used for preparation reuse. There is no initialized
address coordinate and no valid-address-only premise.

Write `k=L-H-1` for the last position before the suffix. The ordinary
callee is assumed to exchange physical address positions `j,k`, with
all other address coordinates preserved, in time at most `T_X(V)` using
a fixed inventory of tapes and at most `S_X(V)` visited workspace cells.
Denote that coordinate involution by `Q`.
The callee preserves its input, returns an owned output stream, and
satisfies its declared workspace/head-return contract within this tariff.
If `j=k`, it is the identity and no call is needed. This is a paid
**width-one** exchange, not a reversal or a width-H exchange.

After this exchange write the address as `a|b|r`, where `a` has `k` bits,
`b` is at position `k`, and `r` has `H` bits. Define

```
g(a) = f( Q(a|0|0^H) ).                                (2)
```

For every `b,r`, `f(Q(a|b|r))=g(a)`: varying `b` varies the original
target, and varying `r` varies only the omitted suffix. All dependencies
of the transformed function now occur before `b`.

Assume `g(a)` can be prepared on a fixed inventory of sequential work
tapes in at most `E_*` steps per `a`, **including** descriptor decoding,
workspace clearing and head returns. Its scratch length is at most
`E_*`, as follows for a sequential computation starting with blank
work tapes. More generally use any separately proved scratch bound
`S_*`; none of the endpoint argument requires a unit-cost evaluator.
This must be one **uniform encoded evaluator**, including the cost of
reading supplied control/descriptor parameters. There is no family of
size-specific compiled advice strings or uncharged oracle in E_*.

The proposition is a sequential implementation of (1) with

```
F = 2^(L-H-1) = M / 2^(H+1) preparations,
T <= 2 T_X(V) + O(V + F(E_* + L + log(R+1))),             (3)
middle-stage extra scratch
        <= 2^(H+1) R + O(E_* + L + log(R+1)),             (4)
total visited space
        = O(V + S_X(V) + E_* + L + log(R+1)).            (5)
```

on a number of tapes independent of `L,H,R` and of the number of
targets. The usual coefficient in `O` is fixed once the component
machines and encodings are fixed. No observed Python timing supplies it.
Equation (4) excludes the input/output streams and the ordinary callee's
workspace; it is not the complete construction's scratch bound.

## 2. Literal sequential schedule

Use four payload tapes: input, output, and two reusable staging tapes
`Z,O`. Their left markers are fixed. All evaluator and counter tapes
come from fixed inventories; loops do not allocate new tapes.

Call `Q` first. Enumerate prefixes `a` in binary order. Each prefix
occurs on the payload tape as exactly two consecutive slices

```
[ a|0|r, r=0,...,2^H-1 ] [ a|1|r, r=0,...,2^H-1 ].
```

For each prefix:

1. Prepare and retain the single bit `g(a)`.
2. Read the first complete slice sequentially onto `Z` and return its
   head. Read the second complete slice onto `O` and return its head.
   Each slice has `S=2^H R` payload bits.
3. If `g(a)=0`, sequentially append `Z` and then `O` to output. If
   `g(a)=1`, append `O` and then `Z`. Preserve order **inside** each
   slice. Erase each staging cell as it is read and return both heads
   to their left markers. There is no seek to an individual record.
4. Clear the control workspace, return its heads, and advance the
   prefix counter. The two staging tapes are now reusable.

Finally return the input and output heads, and apply `Q` again to
the output. This needs at most two width-one ordinary exchanges in
total, regardless of the distance between the exchanged coordinates.

For j!=k, the first Q preserves the original source and owns an intermediate A.
The middle procedure preserves A while producing intermediate B. The
last Q preserves B and returns the final owned output. Then erase and
return the two private V-bit intermediate regions A,B by linear scans.
The original source and final owned output remain. These extra scans
cost O(V) in (3); they are outside the middle-stage 13V invoice below.
For j=k, skip both Q calls and run the middle procedure directly from
the preserved original source into the final owned output. There are
then no A/B intermediate regions to erase; in particular, neither the
original source nor the final output is cleared as an intermediate.

At a prefix with `g(a)=1`, the record originally at `a|b|r` appears at
`a|(b XOR 1)|r`, with exactly the same `a,r` and payload. At a prefix
with `g(a)=0`, it stays at the same address. Thus the middle procedure
is the transformed switch, and conjugation by `Q` gives (1).
This argument covers arbitrary dirty payloads and arbitrary dirty
suffix coordinate values; it does not assume zero padding. The inverse
uses the same procedure, since each switch is an involution.

## 3. Complete tariff and fixed workspace

For clarity, count read, write and one-cell head move separately on
the four payload tapes. For each input payload bit, staging uses a
read and right move on input, a write and right move on its staging
tape, and one left move during return: **5** actions. Draining uses
a read, erase and right move on staging, a write and right move on
output, and one left move during return: **6** actions. Returning
the full input and output adds **2** actions per bit. Therefore the
middle-stage payload-bit portion is exactly **13V** actions in this model.
Markers, finite-state branching and counters add `O(V+F(L+log(R+1)))`;
they are excluded from that exact coefficient. The Python tape model
checks the payload-bit invoice only.

There is no L-bit address test or evaluator call at each record.
To find slice ends, use the same H-bit suffix counter and R-bit-record
boundary encoding for all prefixes. A binary counter kept with its
least significant end at the return marker has total carry traversal
`O(2^H+H)` across a complete suffix enumeration: each position is
visited only when the lower positions carry. Repeating the bounded
number of staging/draining passes keeps this linear. An analogous
counter through each R-bit record costs `O(R+log(R+1))=O(R)` per
record. Initialization and prefix preparation cost at most the
additive per-prefix term in (3). Counter and evaluator tape heads
return to fixed markers; end markers need only constant extra cells
per staging tape.

There are exactly F preparations, not M preparations. Clearing and
head returns are included in E_*, so all preparation work costs
`F E_*`. Input/output each occupy V bits and are roles of the payload
stream. The middle stage's extra payload scratch is at most the two slices, `2S`.
The evaluator's scratch is reusable across all prefixes, and no tape
is allocated per prefix, per source axis or per exceptional target.
The union of the fixed ordinary-callee, evaluator and staging/counter
inventories remains fixed.

The input and owned output/intermediate streams occupy a constant
number of V-bit regions. They may be kept while the next Q callee
runs, so (5) also includes its visited workspace. A sequential callee
with blank work tapes visits at most O(T_X(V)) new cells; the actual
O(V)-time callee premise therefore gives S_X(V)=O(V).

This proves (3)--(5) without assuming a random-access payload
operation. The verifier's direct array implementation of `Q` is
**only an endpoint oracle for the assumed ordinary callee**. It is
not included in the sequential payload invoice.

## 4. Application to the placed CRT caller

PR4100 Section 3 and Hiroki KUMAZAKI's PR4174 give the reservoir
placement context. We use its support/coordinate conclusion as an
explicit hypothesis, rather than importing or rechecking its entire
allocator: after the paid placement `P`, every relevant control omits
the complete back H-bit field, and its target lies in the middle Y
field. Retain `f_P(z)=f_original(P^-1(z))`. If a logical source axis
was split by placement, reconstruct it from its coordinate descriptor;
reading one old contiguous slice is not a valid substitute.

The last bit of Y is physical position `L-H-1`, exactly k above. A
target specified as the numeric local bit `j_Y` of Y, with Y occupying
`[2H,L-H)`, is at physical position `L-H-1-j_Y`; there is no implicit
physical bit reversal. Equation (2) is then

```
g(a) = f_original(P^-1(Q(a|0|0^H))).
```

This lowering applies to **any** target in Y. We do not identify the
source's guard-defined exceptional set with the physical last K bits:
arithmetic carries run toward larger numeric bit indices. For the
following tariff it suffices that the independently chosen exceptional
set has at most K targets. Its guard geometry remains predecessor work.

Each inverse placement is a known fixed set of block swaps, and Q
is one known coordinate swap. A deliberately naive sequential
reconstruction scans the encoded address once per requested original
bit, using `O(L^2)` steps and `O(L)` scratch. Descriptor decoding can
be charged to the same bound. This is polynomial overhead inside
preparation, not an uncharged constant per input record.

Conditional on PR4100's stated numerical evaluator bound, enlarge
its fixed constant to cover this reconstruction and all preparation
returns/clearing. With `L=Theta(p)` the resulting E_* satisfies

```
E_* <= C 2^(4 ell) (p+2)^16,
G = 64(ell + ceil(log2(p+2))),  H >= G.
```

These are premises, not a new certification of the numerical
algorithm or a derivation from the finite fixture. Exact integer
arithmetic gives

```
E_* / 2^H <= C 2^(-60 ell) (p+2)^(-48).
```

Consequently `F E_* = M E_*/2^(H+1) = O(M) = O(V)`.
The FL term in (3) is absorbed in E_* after increasing its fixed
constant, using L=Theta(p). Separately, `F log2(R+1)<=MR=V` for all
integer R>=1, so no extra relation between R and p is needed for that
counter term. The assumed width-one ordinary callee costs
`T_X(V)=O(V)`, so each elementary target costs `O(V)`. At most K
such targets cost `O(VK)`, with the same suffix and fixed inventories
reused and with all coordinate values restored except intended
target flips. The actual caller's controls omit all active target
bits, so sequential treatment agrees with its commuting layer.

This complete-fiber reuse cannot be transferred to the sparse bad
holes: their occupancy need not supply complete suffix slices.
The compact word and its exceptional repair remain separate.

## 5. Finite corroboration and boundary

`verify.py` authenticates the three source inputs by SHA256 and Git
blob hash before loading the exact retained CRT control bytes. It
uses explicit checks active under optimized Python. `--write-result`
is an explicit receipt-generation option; normal verification compares
the reproduced result without rewriting it.

The universal proposition is the written conditional proof above.
The tests corroborate its endpoint, transformed-control convention,
dirty suffix coverage, exact preparation count and payload invoice.
They do not time or implement the assumed E evaluator or ordinary
callee, do not validate the asymptotic reservoir cutoff using a tiny
fixture, and do not certify the complete CRT or multiplication theorem.

The source-bound root-axis fixture is a **control projection**, using
L=12,H=3 and suffix-only transport of the unused axis-2 bits. It does
not instantiate the full three-reservoir placement or execute PR4174's
allocator. Its targets may lie outside the hypothetical three-field Y
range and are admitted by the general lemma's weaker `q<L-H` premise.
It is not a literal post-allocator production tail instance; Section 4's
full caller application remains conditional on that separate placement.

The predecessor supplies the original elementary tail mechanism. New
evidence is the sequential two-slice schedule, fixed workspace/return
invoice, independent all-function tape model, source-bound actual
caller execution and mutation controls. No new kappa is claimed.
