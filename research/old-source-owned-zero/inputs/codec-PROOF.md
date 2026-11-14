# A literal paid bridge from the old coded field to the complete native packet

This is a source-specific implementation lemma for the `precision_tape`
obligation, at canonical main
`e54523517d0f03e58352e647c403a5af3e525a57`. It answers the payload bridge
left open in #7578, exact head
`e9b6d75397e3553af77bab81d5816e4b8708a501`. It proves no new kappa and does
not discharge any of the five selected assumptions at its full scope.

The semantic coordinate bijection and the incompatible old/new lengths
were already stated in #7578. The old coded positive leaf #6967 already
has a structured physical implementation. The new result is the explicit
input-independent literal controller for this particular codec and strided
layout boundary, including old header parsing, inverse transport, physical
retirement and a complete direct-service bill. Stable binary partition is a
classical algorithm; no novelty is claimed for that general idea.

## 1. Exact old and new interfaces

The source header schema is copied verbatim from the canonical current
provider and checked against it:

```
outer, rows, stock, row_bits, within_bits, record_bits, p, d,
K, G, H, q0, qF, qB, D, f, rho, active_start, back_start,
selected_axes, entry_start, remainder, cutoff.
```

A nonnegative value uses `1^ell 0` followed by its ell binary digits,
least significant first. Zero has one digit. Every nonzero value has
leading (last written) digit one. The old descriptor is exactly these
twenty-three codes followed by physical blank. Let E be its actual bit
length, including values irrelevant to this bridge. All twenty-three
values are scanned and checked for canonical coding; ignored fields are
not interpreted as arithmetic promises.

Write

```
a = within_bits,       u = active_start,
C_rows = outer*rows,   g = 9f,
N = C_rows*2^a,        L = 2rb.
```

The bridge needs `outer, rows, f, K, cutoff > 0`, `0 <= rho < K`,
`u+9fK <= a`, and the complete old row relation
`row_bits = 2^a record_bits`. Each address record has r positive complex
coefficients, each with b>=2 real bits followed by b imaginary bits,
least significant first, and virtual delimiter 2 after each component.
The literal physical codes are 000 for 0, 001 for 1, and 010 for delimiter
2, as in the retained CodedPort. Therefore

```
record_bits = 6r(b+1),
V_old = C_rows*2^a*6r(b+1),
V_packed = C_rows*2^a*2rb = N L.
```

The bridge's geometric premises are weaker than the complete historical
monomial producer geometry: it does not use G, H, the back reservation or
the hidden row supplier. A caller of the older provider still owes those
additional premises. No permission to reinterpret its source tokens or
owner namespace follows from this local lemma.

The old numeric width b and coefficient multiplicity r are **not** separate
members of the twenty-three-field header. The controller reads the first
component to its delimiter, counts b physically and returns the old head.
It then divides the encoded `record_bits` exactly by `6(b+1)`. A zero or
nonintegral quotient rejects. Every later component is checked to have
exactly that b and a delimiter, so inference from the first component is
not an unchecked uniformity assumption. The component quantum is external
to both ABIs and is unchanged.

The output is exactly the supplied ABI of #7429: six positive canonical
Gamma codes `(f,r,P,S,b,cutoff)`, where

```
P = C_rows*2^u,  S = 2^(a-u-9f),
DATA = [P] x [2^f]^9 x [S], with r Gaussian coefficients per address.
```

Its components are signed MSB-first b-bit words, with no delimiters or
three-bit code expansion. Gamma is `0^(ell-1)` followed by the MSB-first
binary value, exactly as in the literal leaf's checker. The literal graph
preserves cutoff in binary: a cutoff of enormous numerical value costs
its encoded length, not its value. The bridge does not itself execute
the provider's f<=cutoff test; the same supplied cutoff reaches it.

## 2. The actual literal controller

`compile_bridge()` takes no runtime argument and produces 6,003 locations
on 43 fixed tapes. Instructions are only a scanned-symbol branch, a write
of one fixed symbol, a one-cell move, a fixed jump, or a halt. The alphabet
is `{blank,0,1,LEFT}`. LEFT is the common finite-alphabet renaming of the
old physical left guard and the literal provider's local guard; numeric
delimiter 2 is still the three physical bits 010, never a physical guard.
For a joint hardware table the two fixed marker names are relabelled once
at compilation to that hardware's blank/LEFT symbols. This is a fixed
injective change of instruction labels, not a runtime rewriting of public
markers or a conversion of numerical codeword 010.
No address, width, stride, payload value, list length or Python integer
selects a runtime instruction. Python arrays and numerical positions
exist only in the checker hardware and independent fixtures.

The finite subroutine macros in Builder are expanded at compilation. There
is no runtime call stack or unbounded inventory of registers. Literal
branches check the relevant symbolic invariants. A missing branch is an
explicit rejection. This contribution exports the complete finite table
by deterministic compilation from its small source; its digest is recorded
in the verification receipt.

The two original public tapes are OLD and CONTEXT. PACK and GAMMA are a
new supplied service bank and its header. All remaining tapes are private
counter, staging and shuttle banks. They enter at their local origins with
LEFT immediately before each origin, and physically blank bodies through
the stated capacity. Genuinely disjoint physical segments and the supply
of these guards/windows are premises. Object-identity alias checks in the
reference binder reject an obvious alias; they do not prove disjointness
of arbitrary external wrappers.

The parser reads all old header codes. It retains the used scalar values
as unary guides and cutoff as a binary word. It checks positivity, the
selected-position bounds, the exact row size and the recovered r. It
constructs the six Gamma values, converts every old component into its
MSB-first word, and checks the exact old data frontier. Conversion uses
one component tape, reverses that tape physically, and erases it before
the next component. Both original heads return to their origins; OLD
has not been written. The complete unsigned bit pattern is preserved,
including the most-negative signed word. No arithmetic rounding occurs.

## 3. All 9f selected positions and the stable-partition invariant

Number within-row bits from the left, beginning at zero. The old selected
position at native slot i and column j is

```
p_(i,j) = u+(if+j)K+rho,   0<=i<9, 0<=j<f.
```

Set `k=if+j`; then `p_k=u+kK+rho` for `0<=k<g=9f`.
The bridge performs **9f** extractions, even for the rank-one positive C
provider, which numerically changes only the first slot. Its ABI includes
all nine slots; neither the Fourier rank nor coefficient multiplicity r
replaces this count.

After k extractions the first u bits are unchanged and the next k positions
are the original selected bits `p_0,...,p_(k-1)`. All not-yet-selected bits
remain in their original relative order. Every earlier extraction rotates
an interval whose right endpoint is smaller than `p_k`, so the current
position of the next selected bit is still exactly `p_k`. Its destination
is `u+k`, and the intervening number of bits is

```
m_k = p_k-(u+k) = rho+k(K-1).
```

Thus, within each fixed prefix of length u+k and each original external
row, the current address layout has the form

```
[2^m_k] x [2] x [2^(a-p_k-1)].
```

Stable separation by the middle binary coordinate transforms it into

```
[2] x [2^m_k] x [2^(a-p_k-1)].
```

This is the desired bit rotation. It keeps the relative order of all
spectator bits and every complete coefficient record. Applying it
**separately within each already fixed prefix** is necessary: one global
partition can mix earlier selected bits, original prefixes or rows.

The complete result is the address-bit order

```
first u original bits; p_0,...,p_(g-1);
all remaining original bits in their original order.
```

All a original coordinates occur once. The external `C_rows` coordinate,
coefficient order, real/imaginary order and complete spectator fibres are
preserved. The nine selected f-bit chunks are MSB-first. Relative to the
old column naming this reverses column labels uniformly in every slot,
as already identified in #7578. It commutes with a tensor of identical
native column factors, including its repeated absolute phase. Return
uses the inverse address map; it does not leave this relabeling in place.

## 4. Physical shuttles and runtime guide generation

At extraction k the four unary guides are

```
PREFIX_k = C_rows*2^(u+k),
HALF_k   = L*2^(a-u-k-1),
RUN_k    = L*2^(a-p_k-1),
CHUNKS_k = 2^m_k.
```

Their exact relation is `HALF_k = RUN_k CHUNKS_k` and
`2 PREFIX_k HALF_k = V_packed`. No physical stride is supplied by a host
integer or evaluated using random access.

For one prefix the input stream contains CHUNKS alternating pairs of RUN
bits. A monotone input scan sends successive RUN-bit runs to ZERO and ONE.
Those two banks are then rewound and copied to the next full bank, ZERO
followed by ONE, erasing them during the copy. The next prefix appends to
the same output bank. At the end of the pass the old full packed bank is
retired, the new full bank is copied back and erased, and all heads return.
Those full-bank copies, erasures and returns are included in the bill.

The initial guides are computed by physical unary copying, multiplication
and doubling. Between consecutive passes the controller executes

```
PREFIX <- 2 PREFIX,    HALF <- HALF/2,
RUN <- RUN/2^K,        CHUNKS <- CHUNKS*2^(K-1).
```

K-1 is a physically computed unary guide. The K or K-1 consecutive
halvings/doublings each act on a unary tape. Summing their geometric lengths
charges their total work to the initial/final guide length, plus O(K)
loop overhead. They do not cost K times the largest guide length.

Every halving is exact on legal geometry. Before a further forward pass,
`a-p_k-1 >= K`; `a-u-k-1 >= 1`; and the guides have the displayed powers
of two. No guide is updated after the last pass. The first actual native
service therefore sees the complete Gamma packet and DATA at their origins.
The bridge keeps its final guides while the service runs; the service may
not access them or reuse their owners.

For return, start with the last guide values. Within each prefix, copy
HALF consecutive bits to ZERO and then HALF to ONE; replay CHUNKS pairs
of RUN bits from those banks, interleaving them into the next full bank
and erasing the consumed buffers. This is exactly the inverse rotation.
The reverse updates are

```
PREFIX <- PREFIX/2,    HALF <- 2 HALF,
RUN <- RUN*2^K,        CHUNKS <- CHUNKS/2^(K-1).
```

They are applied only before another reverse pass. In reverse pass k>=1,
PREFIX is even and `m_k >= K-1`, so the divisions are exact. The original
order is restored by induction down to k=0. No reverse routing table or
input-size family of tapes is materialized.

## 5. Successful return, retirement and ownership

Suppose the packed service returns the same complete b-bit format and
length at the original PACK/GAMMA heads, preserves GAMMA and all bridge
private tapes, and restores its own distinct private owners. Its numerical
action may be any function on those packed words; codec correctness is a
bitwise statement and needs no independence of input coefficients.

After inverse routing, the controller creates the complete old-format
image on STAGE: it physically reverses each b-bit component, emits its
three-bit digit codes and restores the delimiter. It checks the complete
packed frontier. Only then does a linear successful commit replace OLD
with the same number of physical bits. CONTEXT is never written. Every
bridge-owned body is erased and every head returns to its initial relative
origin. The LEFT markers and exterior symbols remain unchanged.

OLD is a protected backup through the entire forward codec, service and
inverse preparation. PACK is a paid temporary representation, with no new
productive-target credit. Parent and child owners are distinct physical
segments; the theorem does not infer that equal values or equal frames
permit aliasing. This construction supplies a local transfer/return
service; it does not establish the enclosing compiler's ownership naming
or allocation contract.

On the explicitly exercised malformed entrances, rejection precedes any
OLD write. General malformed-input retirement, interrupted computation,
corrupt service returns and failure cleanup of #7429 remain outside this
successful-call theorem. In particular a numerical rejection by a child
whose failure contract does not restore its banks cannot be promoted to a
successful full owned return. The #7578 common-root numerical premise is
one separate way to guarantee that the actual positive child succeeds.

## 6. Complete uniform time and backing bounds

Count every R/W/M/J/H transition, including tests and jumps. The following
coarse constants are obtained directly by counting the emitted loop bodies:

| Macro | Sufficient charged form |
|---|---|
| Copy, erase or rewind an ell-cell word | `16(ell+1)` transitions |
| Unary doubling or halving with cleanup | `128(ell+1)` |
| Canonical binary-to-unary conversion of v | `1024(v+encoded_length+1)` |
| Unary x-by-y product, all head returns | `128(xy+x+y+1)` |
| Unary-to-binary and one Gamma output | `256(v+1)` |
| One complete routing pass, including copies, retirement and guide updates | `8192(V_packed+1)` |

Here ell includes the span actually crossed on a return from a formerly
occupied, now-erased word. Erasing a buffer does not make its head's
physical return distance zero.

For binary-to-unary conversion, strict binary prefixes sum to less than
the final positive value; the sole zero word is handled separately. For
unary-to-binary conversion, an increment changes its trailing ones and
the next bit, then physically returns. The total trailing-one count over
v increments is less than v, so this is linear rather than v log v.

All nine unary-expanded old shape values are at most V_old on legal input.
For example `row_bits <= V_old`, `record_bits <= V_old`,
`K,u,9f <= a <= 2^a`, and outer and rows are at most C_rows. Products
constructed during preparation are either at most a or at most V_old.
The gK product is bounded by a-u. The row-size product is checked against
the supplied row_bits. Prefix counts, N, all shuttles and every unary
run/half/chunk guide are bounded by V_old. The unused header fields and
cutoff are scanned/copied in their encoded lengths and never unary-expanded.

In each routing pass the total number of payload bits copied to the two
half buffers is V_packed. Buffer readback, full-bank retirement, full-bank
replacement and all rewinds are linear in the same volume. The numbers of
prefixes and runs are also bounded by V_packed because every run contains
at least one bit. The geometric update sums in section 4 and K<=a<=V_old
cover the runtime counter work. Preparation and the two codec sweeps cost
O(V_old+E), and there are exactly 2g routing passes.

A conservative explicit whole-bridge envelope, deliberately much larger
than the preceding macro totals, is

```
T_bridge <= 2^20 ((9f+1)V_old + E + 1),
K_after <= K_entry + 64(V_old + E + 1).
```

The order of this particular controller is also necessary. Each of its
2g routing passes erases all V_packed cells of PACK and writes all of them
back from OUT. These alone are 4g V_packed=36f V_packed writes. Since
`V_packed/V_old=b/(3(b+1))>=2/9` for b>=2, there are at least 8f V_old
PACK writes. The E old header reads are distinct additional transitions.
Thus `T_bridge>=8f V_old+E`, and this controller has
**Theta(f V_old+E)** complete time. This is a lower bound for this graph,
not for every possible packing algorithm.

The second line counts the union of newly visited cells of all 41 private
tapes; each body has at most V_old+E+1 cells. Erasure does not subtract any
earlier history. K_entry retains every previous extent, including public
owners, suspended ancestors and old private high-water regions. The supplied
relative windows must cover these new extents; supplying those windows is
an explicit allocation premise. No ancestor sweep or absolute-origin access
is hidden in a rewind, which stops at its own LEFT guard.

For the Gamma bank specifically, g>=9 implies N>=512,
P<=N/512 and S<=N/512. Since b>=2 and r>=1, V_old>=18N,
and b,r,f are also bounded by the corresponding positive payload factors.
Using `length(Gamma(v))<=2v` for the five non-cutoff fields gives a total
less than V_old; the cutoff Gamma is shorter than its own old header code.
Thus the claimed per-bank V_old+E+1 cap also covers Gamma, rather than
assuming every output header is only as long as the original header.

The bound is for legal promised shapes, not a guarantee that malicious
enormous inconsistent header values are rejected within the valid-data bill.
This distinction is immaterial to the successful selected-occurrence theorem
but relevant when interpreting rejection tests as more than fault detection.

## 7. Source-relative central-service corollary and remaining obligations

The six generated values and complete data word meet precisely the packed
entrance required by #7429. In the selected event 24472 application of
#7578, use `b=p+h+2n+3`, the same common quantum, complete spectators and
f<=cutoff. Its complete-root Clifford-prefix argument supplies every
numerical integrality/width premise of the literal positive child. Its
local bill remains

```
T_C <= 65536(f V_packed + E_Gamma + 1),
K_C_after <= K_C_entry + 64(V_packed + E_Gamma + 1).
```

Using PACK/GAMMA as its two public ports and 27 additional genuinely
distinct private owners gives a 70-tape direct central-service composition.
The honest combined successful invoice is `T_bridge + T_C`; both historical
backing allowances are retained. The old-to-new length ratio
`3(b+1)/b > 3` remains exactly the predecessor's calculation. The physical
codec now pays for it; no header-only substitution is asserted.

This supplies a literal **direct/leaf-order** upper tariff O(f V_old+E),
uniformly in the complete valid old format. It does not produce the faster
nonleaf recurrence used by the selected conditional theorem. It does not
execute the right or left monomial, connect a HOME packet wrapper, prove
enclosing cutoff/stock/owner admission, or validate analytic recovery.
The exact source token and full selected compiler still need an admitted
dispatcher. All five global assumptions remain, and the selected conditional
bound remains kappa=0.00363005817.

More sharply, the preceding lower bound excludes using this unchanged
graph as a uniform `O(V_old f^(1-kappa)+E)` nonleaf service for kappa>0
on valid unbounded-f families with negligible descriptor term. For example
the bridge domain permits `a=9f,u=rho=0,K=r=1,b=2,outer=rows=1,cutoff=f`,
where E=O(f) and V_old=18*2^(9f). This is a scoped obstruction to this
direct controller's rate, not a restriction on a different representation,
ordinary supplier, changed caller or the selected conditional theorem.
In particular the selected tariff also has logarithmic precision factors;
this pure-power comparison does not exclude that full tariff without a
separate cofinal relation between f and precision p. Bounded leaf f gives
no contradiction to an accelerated asymptotic caller.

## 8. What the finite checks establish

The primary checker executes the actual fixed table on four complete
nine-slot f=1 packets. It independently reconstructs the bit-index
permutation, six Gamma values, component reversal, same-owner return,
private retirement and relative head positions. One packet has the old
reservation-compatible geometry a=12,u=2,K=1; another infers r=2,b=3 and
retains a 201-bit cutoff; another uses b=22. Two tests replace the packed
words with a supplied same-width function to distinguish correct inverse
transport from merely undoing untouched data. That supplied function is a
codec fixture, not an executed native C service.

Five extracted shuffle subprogram tests exercise nontrivial K=2/3, rho>0,
multiple prefixes/rows and different record widths against direct indexing.
They execute the same literal macro on small general rotation geometries;
they are not complete nine-slot f>1 or K>1 packets. The universal statement
rests on sections 3-6. Such complete packets are exponentially larger and
are explicitly unrun. Wrong-position/global-prefix controls, exact-length
and source-code controls, and alias binding distinguish the main seams.
Separate review must assess the proof and physical program, rather than
calling the author's own replay an independent proof.

Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.
The retained source authors and originating PRs are credited in NOTICE.md.
No independent human review or formal proof-kernel acceptance is claimed.
