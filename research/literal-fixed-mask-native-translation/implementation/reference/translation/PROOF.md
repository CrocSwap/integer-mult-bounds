# A literal descriptor join for one selected native translation

**Scoped enabling lemma; no new kappa.** Prepared for Jerry Chen / @CubeJerry
with substantial OpenAI assistance. Canonical base:
`e54523517d0f03e58352e647c403a5af3e525a57`.

## 1. Actual source factor and exact boundary

The selected native word is
`research/shared-wire-split-composition/data/final.json.gz`, compressed SHA256
`2b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883`.
Its zero-based event 24472 is `["MOVE",415,3,99,false]`. The exact lowering of
the frame-3 to frame-99 operator has rank 1. Its right monomial has affine
offset **1**, with matrix rows
`(239,129,130,132,136,16,160,192,256)`.

The retained Clifford constructor produces `diag; perm(G); xgate(offset);
global_phase`. Rows of G are indexed by output bits: the image integer is
`sum_i parity(G_i & x)*2^i`, then XOR offset. Therefore offset 1 flips
**output coordinate 0 after G**. It does not identify bit zero with the
fastest packed coordinate. The complete authenticated recipe is retained in
`RECIPE.json`; `bind_source.py` recomputes it and checks the post-matrix
translation with the separate retained signed-Pauli/Gaussian evaluator.

The supplied entry ABI is exactly the five-Gamma/raw packed ABI of
[literal-native-quadratic-phase](https://github.com/CubeJerry/integer-mult-bounds/tree/172f4535ce8dcff79f626410af845f757c1563be/research/literal-native-quadratic-phase).
Its coordinate tuple is `a=(a_0,...,a_8)` with a_0 the slow coordinate, a_8
the fast coordinate, and each `a_i` an f-bit nonnegative integer. For each
tensor column j, native coordinate bit i is `(a_i >> j)&1`.

Consequently the source's lifted X_1 acts by

`(a_0,a_1,...,a_8) -> (a_0 XOR (2^f-1),a_1,...,a_8)`.

This package implements that translation alone at the stated post-matrix
boundary. It does not implement G, the source quadratic phase, the central
rank-one child, or the whole MOVE. In particular the existing phase pass
cannot simply be followed by this translation while omitting G.

## 2. The joined literal theorem

Supply positive integers `f,r,P,S,w` as five consecutive canonical Elias
Gamma codes on HEADER. Gamma(n) consists of `ell(n)-1` zeroes followed by
the ell(n) ordinary binary digits of n. Let E be their total bit length.
DATA is the complete lexicographic array

`[P] x [2^f]^9 x [S]`,

with r Gaussian coefficients per array entry and 2w raw bits per coefficient,
real component then imaginary component, each MSB first. The word contains
exactly

`V = 2*P*2^(9f)*S*r*w`

bits and then a physical blank. The payload may be arbitrary; no arithmetic
or signed headroom is needed for this permutation. HEADER can have opaque
data immediately after its fifth code. DATA can have opaque data after the
blank endpoint. All such exteriors remain unchanged.

The fixed ports are HEADER=0, DATA=1, three private binary descriptors at
2,3,4, the nine retained reversal work roles at 5,...,13, and eleven producer
roles at 14,...,24. Thus there are **25 tapes**, of which 23 are private.
Each head begins at its own arbitrary origin, possibly negative. On private
roles, the guard at origin minus one and the active windows in Section 7 are
blank. This is an explicit allocation/blankness premise, not something two
local probes certify. Opaque cells outside those windows are preserved.

**Theorem.** `compile_translation()` emits one fixed 1,878-location graph,
alphabet `{blank,0,1,|}`, using only scanned-symbol branches, one-cell writes,
unit moves, fixed jumps and halt. It has no runtime shape, integer, coordinate
array, source callback, multiplication service or graph-generation argument.
On every legal packet it applies the source translation above, commits to
the same DATA owner and exact original field, restores HEADER and every head,
and erases all private bodies and guards.

For every successful call its complete local instruction count obeys

`T <= 4096*(V+E+1)`,

and its private historical backing obeys

`K_final <= K0 + 32*(V+E+1)`.

K0 is actual previous private backing, including currently blank retained
cells. No erasure reduces it. Both bounds are O(V) on this complete ABI.

Missing DATA bits, an extra immediate DATA bit, or a malformed finite header
encountered by the literal parser cause rejection before any DATA write.
General malformed-input termination, failure cleanup, interrupted-call
recovery and later reuse after failure are not claimed. The normal runtime
graph contains no verifier step budget.

## 3. Producing the correct collapsed lengths

Collapse the complete packet as `[P'] x [R] x [B]`, taking

`P'=P`, `R=2^f`, `B=2*S*r*w*2^(8f)`.

The remaining eight coordinates, all spectator copies, r coefficients and
both complete w-bit components are in the B-bit suffix record. This includes
every real/imaginary bit; reversing B-bit records must preserve their internal
order. The identity `P' R B = V` is exact.

The producer obtains these encodings from the actual HEADER as follows.

1. The retained Gamma pattern creates unary guides of lengths f,r,P,S,w.
   LENGTH counts prefix zeroes. Each tail digit b changes an existing unary
   prefix v to `2v+b` using DOUBLE and physical scans. HTRACE records every
   HEADER step and returns HEADER to its entry origin with erasure.
2. RDESC receives one `1`, then exactly f zeroes while scanning the F guide.
   This is the canonical MSB-first encoding of `2^f`; it does not construct
   an uncharged host power or require a supplied binary R.
3. Three literal nested scans over S, r and w append two unary marks per
   innermost visit. PRODUCT therefore has exactly `B0=2Srw` marks.
4. For every mark of F, the fixed program executes eight unary doublings of
   PRODUCT. Induction on the scanned F prefix gives the final length
   `B=B0*2^(8f)`. Each doubling physically copies, clears, restores and
   erases its scratch. Eight is a fixed property of this source geometry;
   the number of iterations over f is discovered by local scans.
5. The routine in Section 4 consumes OUTER=P and PRODUCT=B and emits their
   canonical binary words on PDESC and BDESC. RDESC is already canonical.

At the reversal join all 25 heads are at their original origins. DATA has
not been written or moved. The three generated descriptor words are
canonical, positive, terminated by physical blanks, and on distinct owners.
The reversal's nine private windows are untouched and blank. Producer guards
at descriptor origin minus one are opaque exterior symbols to the reversal;
that routine neither reads nor changes them.

## 4. A charged unary-to-binary bridge

The descriptor routine `unary_binary` takes one positive unary run of length
n, a blank quotient role HALF, a blank DIGITS stack, and a blank destination.
Their roles and guards are distinct. Two fixed control copies alternate
which of the source/HALF roles holds the current positive quotient. This
does not allocate a changing family of tapes.

While scanning the current run, a parity control bit toggles on every mark.
Every second mark appends one mark to the other role; all current marks are
erased. Thus at the scan end the other role has floor(n/2) marks and the
parity is n mod 2. The routine restores both unary heads and appends the
parity as one bit to DIGITS. A local read of the quotient distinguishes a
positive next iteration from termination. At termination both unary roles
are blank and restored.

The resulting DIGITS word contains the remainders of repeated exact division
by two, least significant first. Its last bit is 1 because the last positive
quotient is 1. Popping DIGITS backward into the destination therefore writes
the canonical MSB-first binary representation, with no leading zero and no
external length. The pop erases DIGITS; guarded rewind restores destination
and all scratch heads.

This is the classical division-by-two conversion with an explicit local
implementation and complete charge, not a claimed new numeral algorithm.
Here its linear cost matters: materializing unary B is affordable because
B is a complete suffix volume, and binary production must not add a hidden
quadratic rescan.

For an iteration with current value n_i and quotient q_i=floor(n_i/2), the
literal instruction count is `7n_i+5q_i+10`. This includes the parity scan,
all writes, both rewinds, digit append and next-iteration test. If
`ell=ell(n)` and `s=popcount(n)`, then

`sum_i n_i=2n-s`, `sum_i q_i=n-s`.

The initial jump and final digit reversal/rewind add `9ell+7`. Hence the
routine's exact cost, excluding its caller's guard installation/removal, is

`19n - 12s + 19ell + 7 <= 38n+7`.

The current unary run never exceeds n, HALF never exceeds floor(n/2), and
DIGITS/destination never exceed ell(n). These are all-size loop invariants.
The finite encoder tests independently check the exact census; they are not
used as a universal interpolation argument.

## 5. Actual reversal invocation and successful retirement

The invoked graph is the exact
[literal-row-reversal](https://github.com/CubeJerry/integer-mult-bounds/tree/7662d01d827c95d90032579c168cae78aa531f2f/research/literal-row-reversal)
program, source SHA256
`4b516d85baf3303db809bc1174394009b1fc71a8f7d17fb6c729ec8bb6aba245`.
Its 524 instructions are included in the joined graph with a fixed tape and
label relabeling. The single successful halt becomes a fixed jump to the
descriptor-retirement epilogue, of the same one-instruction cost. No runtime
call, decoded size, computed target or interpreter callback is inserted.
The verifier checks every instruction of this embedded subgraph against the
retained graph, including its rejection branch.

The predecessor theorem maps each `[P] x [R] x [B]` packet to
`A'(p,a,b)=A(p,R-1-a,b)`, preserving the internal order of each complete
B-bit suffix record. For R=2^f, `R-1-a=a XOR (R-1)`. Combined with Section 3,
this is exactly the source tensor X_1 and preserves all other coordinates,
Gaussian coefficients and individual component bits.

The predecessor stages its entire output, checks exact DATA cardinality,
then installs only on the same DATA owner. It restores descriptor heads and
its nine private roles before jumping to the epilogue. The epilogue erases
all generated descriptor bodies and remaining unary parameter bodies, then
all fourteen producer guards. Each clearing scan stops at its current blank
frontier and rewinds to its local guard. At halt every private body and guard
is blank and all heads have returned to their entry origins.

If the header parser or the reversal rejects, the producer has made no DATA
write and the reversal has not started commit. Public values are therefore
preserved, but private work and heads can remain dirty. The proof requires
successful cleanup before a subsequent clean call.

## 6. Exact complete instruction bill and linear envelope

Each local instruction, including a read, write, unit move, jump or halt,
costs one. Let `s(n)=popcount(n)`, `ell(n)=floor(log2(n))+1`, and set

`E'=ell(P)+ell(R)+ell(B)`.

Define two exact helper counts:

`g(n)=47n-30s(n)+33ell(n)-42`,

`h(n)=19n-12s(n)+19ell(n)+7`.

The first is Gamma decoding before the shared HEADER return and guards;
the second is Section 4's complete unary-to-binary conversion. To verify
the first directly, each leading zero uses seven instructions. A binary
prefix update from v by b uses `47v+17b+18` instructions in its three unary
copy/clear helpers, plus eight in the Gamma wrapper. The strict prefix sum
is `n-s(n)`. Counting the leading one and terminal LENGTH read gives g(n).
The proof uses finite control states and local scans throughout.

The exact predecessor reversal count is

`C(P,R,B)=53V+23PR+71P+54R+54B+28E'`

`          -30(s(P)+s(R)+s(B))-8`.

The entire joined program has the following additive census:

| Executed region | Exact instruction count |
|---|---|
| Install fourteen producer guards | `42` |
| Decode the five Gamma values | `g(f)+g(r)+g(P)+g(S)+g(w)` |
| Return HEADER and erase its trace | `5E+3` |
| Produce RDESC and restore F/RDESC | `11f+12` |
| Produce B0 by complete nested scans | `16Srw+10Sr+10S+7` |
| Execute eight doublings per F mark | `47(B-B0)+150f+4` |
| Produce PDESC and BDESC | `h(P)+h(B)` |
| Complete retained reversal | `C(P,R,B)` |
| Erase producer bodies/guards and halt | `7(E'+f+r+S+w)+99` |

For the doubling row, a zero-bit update costs `47v+18`; there are 8f such
updates and their previous values sum to B-B0. Scanning and returning F
adds `6f+4`. For the last row, OUTER and PRODUCT have been consumed and all
temporary guides are blank; the only remaining body lengths are the three
descriptors and f,r,S,w. Clearing a body of length n costs `7n+4`, including
its return. Fourteen guard removals and the final halt give the constant 99.

This census includes source acquisition, every unary expansion, record load,
copy, two-stack reversal, full output stage, DATA returns, complete commit,
descriptor returns, setup and erasure. It is independent of payload bits and
absolute origins. The graph is built once at a fixed finite setup cost before
the numerical inputs vary; the displayed bill is for each execution of that
fixed graph. No input-dependent compilation is hidden.

For a convenient envelope, put `Sigma=f+r+P+S+w`. Gamma acquisition plus
HEADER return is at most `256(E+Sigma+1)`. RDESC costs at most `32(f+1)`;
the nested product at most `18B0+7`; the doubling stage at most
`47B+286f+4`; the two encoders at most `38(P+B)+14`; and the reversal at
most `256(V+E'+1)`. The exact epilogue is as above. Since every parameter,
B and B0 is at most V, Sigma<=5V. Moreover `E'<=log2(V)+3<=V`, as V>=1024.
These bounds sum to less than `4096(V+E+1)`.

Finally `E<=2log2(frPSw)+5<=2log2(V)+5`, so E is O(log V) and the complete
execution is O(V). A unary parameter unrelated to the packet volume would
not justify this argument. Here the exact complete-array product pays every
expanded guide, including the large suffix B.

## 7. Private backing, exteriors and repeated calls

Every private role has a guard at relative position -1. The table below
gives its largest possible body/end position; hence its visited interval is
contained in `[-1,cap]`. Define `M=max(P,B)` and `L=ell(M)`.

| Producer role | Cap |
|---|---|
| PDESC, RDESC, BDESC | `ell(P)`, `f+1`, `ell(B)` respectively |
| HTRACE, LENGTH | `E` each |
| DOUBLE | `M` |
| F, COEFF, OUTER, SPECTATOR, WIDTH | `f,r,P,S,w` respectively |
| PRODUCT | `B` |
| HALF | `floor(M/2)` |
| DIGITS | `L` |

B dominates f,r,S,w because `B=2Srw*2^(8f)` and all parameters are positive.
Thus DOUBLE never needs more than max(P,B), whether during Gamma acquisition
or suffix doubling. The encoder alternates source/HALF, and its quotient
can never exceed half its initial source length. Its digit stack is bounded
by L. These caps include all intermediate formats, not just final contents.

The predecessor's nine reversal roles retain their proved windows: OUTPUT
and DTRACE cap V; prefix and row guides cap P and R; suffix guide and record
scratch cap B; doubling scratch caps max(P,R,B); descriptor trace caps the
largest descriptor length; and group scratch caps RB. Its private history
increment is at most `8V+E'+18`.

Adding the fourteen producer intervals gives the explicit union bound

`K_final <= K0 + 8V + 2E' + 2E + M + Sigma + B + floor(M/2) + L + 46`.

This is below `K0+32(V+E+1)`. Public heads visit exactly HEADER's consumed
interval `[0,E]` and DATA's complete interval `[0,V]`; their input backing
and endpoints are separately part of the supplied public field storage.
All opaque exteriors are preserved by the guard/frontier invariants.

Erasure leaves previous backing allocated. After successful reuse at fixed
origins, retain the per-role maximum cap reached and combine it with actual
initial history; do not replace that sum by equality with a maximum of
per-call sums. A coarse valid sequence bound is
`K_initial+32(V_max+E_max+1)`. A shorter call scans only its current bodies,
so its exact current-shape instruction bill is unaffected by old blank
capacity. If caller origins change, keep the per-role absolute unions and
pay caller transport corridors; there is no bound on arbitrary relocated
histories by current V alone.

## 8. Evidence, novelty and remaining obligations

The complete author receipt contains nine successful runs, totaling 702,464
payload bits and 57,517,967 local transitions. This includes a full selected
nine-coordinate f=2 packet: 262,144 Gaussian coefficients and 524,288 bits.
It is complete coverage of that fixture, not a higher-width prefix. All
104 standalone encoder cases, through n=1024, satisfy the exact encoder
census. Whole-packet expected outputs use a separate source-coordinate XOR
formula at coefficient addresses, not the reversal algorithm.

The checker inspects the actual three produced descriptor words before the
retained subgraph starts, verifies every embedded predecessor instruction,
and checks exact HEADER/DATA read, write and movement counts, all origins,
private retirement and opaque exteriors. The same physical Tape objects are
kept across a longer/shorter/regrowing chain. The shorter call has the exact
same instruction count as its fresh counterpart, with old history retained.

Controls omit the real/imaginary factor, interchange collapsed prefix/suffix
descriptors while preserving total volume, and omit descriptor retirement.
The wrong-axis control runs past the descriptor check and fails the source
coordinate output oracle. Separate malformed-header, short-DATA and extra-DATA
cases reject with unchanged public contents. Source binding changes offset 1
to bit 8 and requires the independent full-kernel comparison to reject it.
Independent review and its exact receipt are recorded separately when ready.

The predecessor row-reversal theorem already proves the complete-record map,
its translation corollary and cost. Its caller supplied collapsed binary
lengths. The serial monomial predecessor already provides literal descriptor
iteration for a different view ABI, while its numerical service remains
structured control. This contribution is the actual runtime descriptor
producer and fixed-graph composition on the current supplied five-Gamma ABI,
with source-specific axis/order binding and complete costs. It does not
claim a new reversal, tensor identity, numeral-conversion method or faster
monomial tariff.

The five-Gamma/raw entry packet is still supplied. Production of this ABI
from the selected caller, its actual physical owner selector, conversion from
other component encodings, the source matrix G, remaining monomial factors,
recursive children, global stock and analytic recovery remain separate.
In particular the source owner number 415 binds which native operation
contains the factor; it does not identify the physical DATA tape of a full
selected compiler invocation. The theorem's same-owner statement begins at
its explicit DATA entry owner.

All five selected assumptions remain retained: `native_all_columns`,
`owned_erasure`, `compiler`, `precision_tape`, and `analytic_recovery`.
The complete selected kappa remains 0.00363005817. This is one removed local
descriptor-production premise, not an unconditional multiplication theorem.

Credit the selected #7000 source and its retained Clifford/native contributors;
the exact source-binding and packed ABI in the published B3 package; the
published C3 literal-row-reversal program and its classical two-stack lineage;
the prior literal phase's Gamma/unary helpers; and #7349's literal machine.
The retained references preserve their notices. Independent AI review does
not constitute human or proof-kernel acceptance.
