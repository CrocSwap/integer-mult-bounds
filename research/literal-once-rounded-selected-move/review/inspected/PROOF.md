# A literal arbitrary-input, once-rounded selected MOVE

## 1. Exact source and quantified boundary

Canonical main is e54523517d0f03e58352e647c403a5af3e525a57. The source is
the actual selected #7000 event at zero-based index 24472,
`["MOVE",415,3,99,false]`, with source frames [] and [239]. Its exact
factorization is the frozen core's `U=L (C^(tensor f)) R`, including the
right absolute phase i^f, actual G maps, right translation and left phase.
Source binding and all 512 Gaussian kernel columns are reproduced by the
retained bind_source.py. ROUNDED-SOURCES.json pins the immutable small helper
files to CubeJerry dffe132bbe16d830e2aa7367ed40a540f5c7fd64, and the credited
#7211 allocation proof to 2b882fd2834303655f82d084e25dc551f67e9784. No parent
endpoint/core or retained predecessor source is changed.

**Theorem.** Let f,r,P,S,cutoff be positive, w>=2 and f<=cutoff. Supply the
complete packed array `[P] x [2^f]^9 x [S]` with r Gaussian coefficients
per address, w signed MSB-first bits for each real then imaginary component,
and the public six-Gamma header f,r,P,S,w,cutoff. Let the payload numerators
be arbitrary signed w-bit integers, including the most-negative value,
on an arbitrary unchanged common grid Delta. Let every physical private
window be blank, the owners genuinely distinct and all entry heads at
their respective origins, with the complete opaque/exterior contract of
the frozen core. Put

`k=ceil(f/2)`, `W=w+2k+1`, `n=W-k=w+k+1`,

`N=PSr2^(9f)`, `V=2Nw`, `V_W=2NW`.

One fixed 84,935-location, 54-tape four-symbol local program returns

`Delta * floor(U(x/Delta)+1/2)`

componentwise on the original DATA owner, whenever every such rounded
component fits signed w bits. It rejects a true final signed-w overflow
before any public DATA write, even after earlier outputs were staged.
On the legal physical/format/cutoff domain, that true final rounded overflow
is its only numerical rejection. No integral final-output or C-prefix
promise on the original grid is required. All successful heads, private
bodies/guards and opaque exteriors are restored. Failure retirement/retry
and interruption rollback are outside this contract.

The complete direct bounds are

`T<=2^26(fV_W+E+1)`, `K_final<=K_entry+4096(V_W+E+1)`,

with E the actual original six-code length. Erasure never subtracts any
previous history. These are source-specific direct/leaf bounds, not a
recursive selected-rate tariff, Count/Tape provider substitution or complete
selected caller. The native rank is fixed at one, so the number of Gaussian
axes is f. The header's r is **coefficient multiplicity**, not native rank;
it never replaces f in the scale. All nine f-bit native blocks remain.

## 2. Numerical preflight on the concrete frozen core

The allocation is credited #7211, not a new width-optimality theorem. Its
prior denominator and component-row-norm facts are from #2772/#3089/#3091
and the cited Gaussian lineage: entries of a j-axis C tensor have real and
imaginary denominator dividing `2^ceil(j/2)`, and its induced real/imaginary
component maximum norm is `2^ceil(j/2)`. The component norm, not a smaller
entrance fibre's Euclidean norm, is used here.

Write M=2^(w-1), so arbitrary original signed inputs have component magnitude
<=M, including -M. Literal ingress multiplies every numerator by 2^k. The
source monomial R consists solely of permutations and Gaussian units, hence
preserves both the component bound 2^k M and divisibility by 2^k. After j
of the actual f central axes, every stored numerator is integral because
`ceil(j/2)<=k`. Its component magnitude is at most

`2^ceil(j/2) * 2^k M <=2^(2k)M=2^(W-2)`.

The same bound covers entrance and exit monomials, which are outside the
bare C-axis sequence and have no larger component norm. Thus every phase
negation fits strictly inside signed W bits and never negates the widened
most-negative word. Every completed C axis is integral and fits W bits.
One does not incorrectly require a reserved zero to survive each division.
Integrality of the complete next prefix proves the parity of its next
actual four-term numerator.

This is precisely the **concrete** numerical predicate of the frozen
#7429/core graph. That graph allocates W+2 numerator bits, runs its exact
carry rows, checks parity and signed quotient fit, and stores W-bit axis
outputs. These actual temporary rows are charged by the core at V_W. No
uninstantiated #6030 Provider or fused primitive is imported. The core
therefore completes with the exact integer widened return

`z=2^k U(x/Delta)`.

The original Delta remains the implicit grid during this temporary semantic
scaling; final division/rounding returns to Delta. Absolute source phases
are retained by the unchanged core. No numerical rejection can occur
inside its monomial or central-axis operations on this admitted W boundary.

## 3. Literal scale, header and all complete addresses

Public ports are HEADER=0 and DATA=1. Wrapper-private ports 2,...,24 contain
WH, WD, OUTPUT, two traces and fixed metadata/binary work roles. The core's
31 ports map injectively to `(WH,WD,25,...,53)`. All 29 core-private owners
are disjoint from every wrapper role and public owner. Its complete 82,813
instructions are copied with only fixed PC/tape relocation; its halt becomes
one unit-cost goto. No runtime call or numeric callback implements it.

Actual Gamma decoding copies the first four original codes into WH and
decodes f,r,P,S to unary. It decodes w without copying it, and physically
checks w>=2. Every public header advance records HTRACE. A two-state loop
over actual F marks starts in state one, appending a K mark on every 1->0
transition. This generates k=ceil(f/2). Unary copying and one actual appended
mark generate MARGIN=k+1, WIDE=w+2k+1 and HIGH=w+k+1. These are physical
guides, not supplied integers.

The frozen helper's repeated floor-halving encoder converts a copy of WIDE
to canonical binary W, in linear time: alternating unary quotients consume
at most 2W marks in total and push parity digits, which are popped MSB-first.
The exact helper cost is `19W-12popcount(W)+19ell(W)+7`. The actual binary
length guide then emits Gamma(W). The cutoff code is copied by encoded
prefix/tail length only; its represented value is never expanded to unary.
HTRACE returns public HEADER and WH rewinds. WH contains precisely
Gamma(f,r,P,S,W,cutoff), with the original public codes and opaque tail
unchanged. Even a huge cutoff costs only its encoded contribution to E.

COUNT is actually generated as `2PSr2^(9f)` using unary products, nine
doublings per actual F mark and one final doubling. It counts real/imaginary
components. The number of native coordinate bits is still 9f, not k or n.
There is no supplied collapsed volume, stride or host multiplication.

For each COUNT component, ingress emits k+1 copies of its original sign,
all w original bits and k zeroes. This is the exact signed W-bit encoding
of 2^k times the original integer, including its most-negative value. K,
MARGIN and WIDTH heads return after each component. DATA advances are traced;
after precisely V bits, the following blank is checked and the public head
returns by consuming TRACE. WD rewinds with all V_W widened bits.

Only component format changes. Real/imaginary order, coefficient index,
S spectator, all nine native axes and P outer row remain complete and in
their actual order. WD is a fully materialized packed field, not a selected
axis view, sampled prefix or free strided placement. WH/WD and the distinct
blank core banks now meet the actual frozen core boundary proved above.

## 4. Literal once-rounding and post-round fit

After complete exact core return, WH and WD are at origin, all 29 core
private owners are blank, and the wrapper's metadata remains live at origin.
The complete WD field contains integer z=2^k U(x/Delta). For each component,
rounded_egress copies its high n=W-k bits into the guarded TMP buffer, using
HIGH as an actual loop clock. This is the signed n-bit integer

`a=floor(z/2^k)`.

Its low k bits encode the Euclidean remainder r, `0<=r<2^k`, even when z is
negative. The first discarded bit b is therefore one exactly when
`r>=2^(k-1)`. The graph remembers b in finite control, reads and advances
over all k discarded bits using K, and returns K. Lower discarded values
are irrelevant to the result but their reads and head movements are paid.

If b=1, the graph seeks TMP's end and performs a literal right-to-left
binary increment with a one-bit carry. It stops at the first zero or the
guard. Every traversed one becomes zero; the first zero becomes one. It
returns TMP to origin. The all-one representation of -1 becomes zero;
that carry out is deliberately accepted. By the positional-value carry
invariant the complete n-bit result is a+1 modulo 2^n. If b=0 TMP is
unchanged. On actual core outputs, `|z|<=2^(W-2)`, so

`-2^(n-2)<=a<=2^(n-2)`, and `-2^(n-2)<=a+b<=2^(n-2)+1`.

Here n=w+k+1>=4, so a+b fits signed n bits. Thus modulo addition is the
actual integer q, without true temporary overflow. This proves

`q=a+b=floor(z/2^k+1/2)`.

In particular, z=-1,k=1 gives q=0 and z=1,k=1 gives q=1. Exact negative
half ties go toward positive infinity, not away from zero or to even.

**Only now** does the graph test signed-w fit. It remembers TMP's sign,
checks all k+1 leading bits equal that sign, and checks the first retained
middle bit equals it. These are exactly the redundant sign-extension
conditions for an n-bit signed integer to fit w bits. The remaining w
bits are copied into OUTPUT. TMP is then returned and fully erased;
WIDTH, MARGIN and HIGH return on every completed component.

Pre-round clipping is invalid: w=2,k=1,z=-5 has a=-3, outside [-2,1], but
q=-2 fits. This is not merely an arbitrary bad-width word: bare C on
`a=-2+i,b=-2` has real scaled output -5. The literal unit graph accepts
this word in 260 instructions. The previous partial-prefix integer is
never subjected to the final w-bit fit condition.

Every WD advance, including high-prefix copy and all discarded bits, writes
TRACE. After COUNT components, the next WD blank is checked; TRACE returns
WD and OUTPUT rewinds to its guard. Exactly V_W wide input bits have been
read and exactly V original-width output bits staged. The same actual
component order and all tensor/spectator addresses are retained. Only true
post-round signed-w overflow can take a numerical rejecting branch on this
legal core-produced field. The wide field remains owned until explicit
cleanup; neither TMP nor OUTPUT aliases it.

## 5. Public atomicity, normal retirement and history

All header acquisition, ingress, core and rounded egress take place without
a write to public HEADER or DATA. The core's public ports are private WH/WD.
Every numerical fit check precedes the sole final public commit. A true
overflow can leave TMP and earlier OUTPUT components live, but the original
public values remain exact. The checker reaches such overflow after 128
narrow body bits were already staged, with zero public DATA writes.

On full success, OUTPUT is copied to the same original public DATA owner,
while OUTPUT is erased and TRACE records each advance. The public head
returns by consuming TRACE; blank OUTPUT rewinds. All 23 wrapper-private
roles are explicitly cleared, guards erased and heads returned. The mapped
core banks were already returned blank. No owner object, origin or backing
interval is replaced, and no owned field earns productive credit.

Every successful call restores all private windows, so the same owners can
be reused for a later smaller packet at fixed origins. It scans only that
packet's current bodies and metadata. Old blank tails remain allocated and
charged without a retrospective scan. Cumulative history keeps each owner's
absolute visited union, rather than releasing erased cells. If origins move,
their absolute old/new unions and paid transport corridors must be retained.
Creating a fresh wrapper object cannot erase that history. Fixture-supplied
public packet replacement is not free caller acquisition.

Rejecting-call cleanup, restored failure heads and same-bank retry are not
claimed. Interruption during commit is not a rollback mechanism. Invalid
physical blankness, malformed headers/cardinality, width/cutoff failure and
caller allocation are separate from the numerical theorem's admitted domain.

## 6. Complete direct cost, including widened core and scratch

Let E_W be the private widened six-code length. Only Gamma(w) changes to
Gamma(W), so `E_W<=E+2W<=E+2V_W`. The unchanged core costs

`2^24(fV_W+E_W+1)`

including its internal transaction, both monomials, complete all-f child,
all signed services, W+2 numerator rows, head returns and retirement. Its
halt becomes a single unit-cost goto, not a free call or external callback.

The entire additional wrapper admits these deliberately loose allowances:

| Additional operation | Complete instruction allowance |
|---|---|
| guards, header/scale/margin/high-width production and return | `2^14(V_W+E+1)` |
| COUNT products, actual 9f doublings and one final doubling | `2^14(V_W+1)` |
| complete signed ingress and source/wide-bank returns | `256(V_W+1)` |
| all rounding, carries, post-round fit, staging and returns | `1024(V_W+1)` |
| public commit, complete wrapper clearing/guards and halt | `8192(V_W+E+1)` |

Each decoded Gamma value costs <256(n+1), including copied bits; strict
binary prefix values sum to less than n. The five decoded values are <=V_W.
Scale/margin/high guides use constantly many scans of f,k,w,W. The copied
floor-halving encoder costs `19W-12popcount(W)+19ell(W)+7`; Gamma emission
is linear in its actual bit length, and cutoff work is linear in its encoded
length E. These justify the first row with ample slack.

COUNT's two unary product results are <=N. The sum of old lengths of all
`9f+1` doublings is <COUNT; a doubling uses `47n+18` literal instructions
with the copied helper pattern. All f-loop resets and guide retirement are
included. No f scans of the final count are hidden.

One component ingress uses at most `12w+16k+24<=24W` steps before whole-field
returns. Rounding copies n high bits, reads k discarded bits, optionally
seeks/increments/returns the complete n-bit prefix, checks k+1 sign bits,
copies w bits and clears TMP. Every such scan is bounded by W; a conservative
count is <256W per component. Trace return costs `5l+3` and ordinary rewind
`3l+3`, including their end tests. Thus the two component-loop rows include
all component clocks, traces and full head returns. There is no per-bit scan
of an entire address or encoded cutoff. The bit carry never calls an integer
addition service.

The final public commit plus returns costs `16V+7`. Each of the 23 wrapper
roles has current cap <=2V_W+E; clear costs `7l+4`, followed by three guard
retirement instructions. This is below the last allowance. Summing all
five additional rows is <`2^20(V_W+E+1)`. Consequently

`T<=2^24(fV_W+E_W+1)+2^20(V_W+E+1)`

` <=2^24(3fV_W+E+1)+2^20(V_W+E+1)`

` <=2^26(fV_W+E+1)`.

All complete array copies, descriptors, scale and rounding loops, history,
source access, return and private work are paid at the actual enlarged W.
This bound also covers time up to true final-overflow rejection on the legal
domain, since it is a prefix of the same bounded loops. It is O(fV_W+E).
At a fixed leaf cutoff f is bounded; no recursive f^sigma tariff follows.

For backing, WH has E_W cells, WD has V_W, OUTPUT has V<=V_W, TRACE at most
V_W, HTRACE E, COUNT/DOUBLE/AUX at most V_W, and every unary/binary metadata
or TMP role at most max(V_W,E). TMP is reused serially but its old maximum
still counts. Guards/endpoints give an additional wrapper/private total
<=46V_W+23E+46; public head intervals add <=V_W+E+2. This is
<64(V_W+E+1). The complete core adds
`1024(V_W+E_W+1)<=3072(V_W+E+1)` on all its 31 mapped owners. Adding these
actual historical increases without subtracting overlaps or erasures gives
<3136(V_W+E+1), below the declared 4096 allowance. Earlier public/opaque and
private backing remains in K_entry throughout, including suspended caller
work. A finite final-overflow rejection touches no larger windows.

## 7. Executed evidence, attribution and remaining obligations

check_rounded.py uses an explicit dense local-instruction CPU and integer
rounding oracle. It imports no independent preflight checker. Its 10,080
complete signed-W scalar cases cover w=2..5,k=1..3, including words beyond
the actual core-produced radius, and compare both q and final acceptance.
They include 840 positive and 840 negative half ties, all-one-prefix carry,
every lower discarded-bit pattern, the accepted -5->-2 boundary, and semantic
controls against pre-round clipping, ties-even and floor-only return. There
are 23 actual header producers and 23 signed ingress runs through f=129,
k=65, with a 512-bit cutoff value copied only in encoded form. Those are
honest converter/header-boundary tests, not full native f>=2 runs.

Every one of the 82,813 embedded core instructions is compared with a
separate absolute-PC relocation formula. Static checks reject any early
public write. Complete actual m=9,f=1 array execution is compared with an
explicit forward sparse Gaussian source-kernel formula, denominator two,
followed by a single independent integer nearest-UP operation per output.
It uses no executable C butterfly or local carry algorithm to obtain the
expected values. The complete source-kernel binding is separate.

The nonintegral packet also supplies an original most-negative imaginary
component at an address whose right phase would negate it without the
widening. At original w=3 the actual complete graph takes 21,899,137 steps,
commits exactly 3072 bits and restores all 54 heads/private/exteriors. Four
exact output components are nonintegral before final rounding. A smaller
w=2 packet reuses the same owners and takes 18,364,903 steps, retaining
cumulative visited history 118,239, including the new long encoded cutoff.
A true final-overflow packet on source pair 32/462 takes 18,055,922 steps;
128 narrow body bits have been staged when the next rounded component
fails fit. Both original publics remain intact and no DATA write occurred.
Failure head/private restoration is not asserted.

Separate root review uses a fresh sparse local CPU at distinct signed
origins, its own mathematical converter/domain checks, all core relocations,
late overflow controls and fresh source kernel inputs. The mathematical
preflight independently checks the allocation and nearest-UP/post-fit
argument under the credited Gaussian facts; its generic fused-update caveat
is concretely supplied here by the actual #7429 W+2 temporary rows. Review
targets and finite coverage are recorded separately; AI review is not
independent human or formal proof-kernel acceptance.

No complete f=2 native tape execution is claimed. The universal all-f result
rests on the exact numerical proof, immutable core lemmas and literal
header/converter/lifecycle invariants. Finite converter cases or a reduced
native dimension are not substituted for a complete mandatory geometry.

Credit Nick Petalas #7211 for this sufficient smaller arbitrary-input
allocation, #6996 for its distinct old coded/provider whole-MOVE interface,
the #2772/#3089/#3091 Gaussian denominator/norm lineage, CubeJerry's source
#7426/#7428/#7429/#7430 and the frozen literal core/endpoint helper work.
All retained notices and exact source pins remain. This is a new scoped
source-specific physical mechanism, not a new width-optimality theorem or
an implementation of #7211's old Count/Tape substitution.

Still open are the actual selected caller's old-codec/strided packed entry,
source occurrence/owner transport, global grid/precision/error and cutoff
admission, stock/owned reset, faster nonleaf work and recursive invoice,
compiler and analytic recovery applications. The complete original source
error-fibre assumptions are not inferred from this local rounding map.
All five selected framework assumptions and conditional kappa remain.
No catalogue/cold selected replay, Count/Tape placement, hosted CI, human
review, formal proof-kernel acceptance or complete multiplier is claimed.
