# A paid Gamma-header prefix for the selected complex stopping cutoff

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
This is a written all-input machine proof with finite corroboration, not a
formal-kernel proof. No new kappa or full framework-assumption discharge.

## 1. Actual source parameters and the remaining input edge

Scientific base: `e54523517d0f03e58352e647c403a5af3e525a57`.
The exact selected `research/shared-wire-split-composition/FULL-RESULT.json`
records claim 363005817/100000000000, tested 363005817007/100000000000000,
and gap g=(tested-claim)/7=1/100000000000000. Its `interval_gate.py` uses

    epsilon = 1-g; stop = g;
    internal = tau+(1-stop)*max(sig-tau,0);
    leaf = sig+stop*(1-sig).

These last two formulas identify the stopping exponent in
`notes/batched-complex-rows.tex`. The different variable `be=1-3g` is an
outer exponent and must not be substituted for the stopping exponent. Put

    Q=100000000000000, beta_stop=1/Q, epsilon=1-1/Q.

The retained formal layer input in `upstream/build/sections/05-layers.tex`
has the descriptor

    E=Gamma(p)Gamma(d)Gamma(r)Gamma(D_total)Gamma(P)Gamma(S)
      Gamma(K)Gamma(rho+1)Gamma(w).

The code, from `02-streams.tex`, is

    b_v=floor(log_2 v)+1,
    Gamma(v)=0^(b_v-1) bin_(b_v)(v), |Gamma(v)|=2b_v-1.

The promises include |E|<=C_desc*p, d<=b_d*p^epsilon, 1<=D_total<=d,
w>=p+2, and a nonempty complete array of volume V=2Mrw. The selected
application review section 5 retains this root boundary. Its reserved-axis
step either processes the layer individually or leaves active width
e=D_total-Q0, with 1<=e<=d. This prefix receives that already produced
marked unary WIDTH. It does not construct Q0, row grants or the full root
payload. The header validity and WIDTH/root correspondence remain premises.

The predecessor [published selected controller](https://github.com/CubeJerry/integer-mult-bounds/tree/9dfe6747b8553fd11b408f2b045c5954ef1e6eaa/research/selected-rank-control)
receives a supplied unary cutoff L. The present result implements its
missing cutoff-production edge from the actual header. The predecessor
sources are copied unchanged and authenticated. Neither main's selected
record nor the predecessor package is modified.

## 2. Exact theorem and machine domain

For every fixed N>=2, paid-site count P>=1 and root denominator Q>=2, the
literal program takes valid positive Gamma(p)Gamma(d) followed by any untouched
suffix, positive unary WIDTH e with e<=d, and the predecessor's marked
empty CHILD and suspended STACK inputs. It produces

    C=min(ceil(d^(1/Q)), e+1),

executes the unchanged selected controller with cutoff C, then retires C.
Every initial input cell and head is restored. For actual selected source
use, Q is the fixed value above and the complete retained header obeys all
its source promises. Smaller Q and syntactically encoded headers in tests are
functional analogues, not changed selected parameters or complete source-family
admission claims.

Tapes 0..3 are WIDTH, CHILD, STACK, CUTOFF. Tape 4 is borrowed HEADER.
Six private tapes are TRACE, LENGTH, D, ACC, FACTOR and PRODUCT. The HEADER
head initially addresses the first symbol of Gamma(p). Each new private bank
(including CUTOFF) has a blank owned guard cell one step left of its entry
head and a blank suffix. Arbitrary preserved ancestors may begin below that
guard cell. The program physically writes each guard delimiter before use,
and physically erases it before returning. These constant marker operations
are included, rather than assumed free. WIDTH/CHILD/STACK retain their
published entry markers and arbitrary permitted suspended prefixes.

K0 includes all retained entry backing, including warm blank capacity. New
backing below is additional historical capacity; erasure never subtracts it.
The valid-input theorem need not roll back malformed input.

Only local-symbol read, symbol write, unit head move, goto, emit and halt
instructions execute. Compile-time loops unroll fixed Q and fixed ports.
There is no runtime host integer, decoded descriptor, stack callback, dynamic
tape selection or input-dependent alphabet. Emit labels are stationary
finite-control edges; Python transcripts are verifier observations.

Let R_Q=bit_length(Q)+popcount(Q). The prefix has exactly 273+84R_Q
instruction locations. The retirement segment has 14. The unchanged selected
controller has 30N+42+P(69+3N), giving total

    329+84R_Q+30N+P(69+3N).

There are eleven tapes and P+4 symbols. For selected Q, R_Q=64. The prefix
alone has 5649 locations; the N=3,P=2 joined example has 5951 locations and
six symbols. This example does not materialize the enormous actual final
selected N,P or their owner manifest.

## 3. Header decoder and local restoration

While skipping Gamma(p), every leading zero appends one unary LENGTH token.
The first one ends that phase. For each saved token the machine consumes
exactly one following header bit, erases the token, and moves LENGTH left.
It stops on its own marker and restores that head. Thus the next header
symbol is precisely the start of Gamma(d), without knowing p at runtime.

The same leading-zero phase for Gamma(d) records b_d-1 remaining bits and
initializes unary D to one. For a following bit delta, the machine emits two
PRODUCT symbols per D symbol, then delta additional symbols; it clears old
D and moves PRODUCT back into D. Hence the updated unary value is 2v+delta.
Induction on the binary prefix proves D=d after all tail bits are consumed.
The LENGTH tokens control this loop symbolically; no host counter is read.

Every right move of HEADER appends exactly one TRACE token. At the end, TRACE
has h=|Gamma(p)Gamma(d)| symbols. A backward scan erases each token and moves
HEADER left once, then returns TRACE to its start. HEADER is never written,
never moves left of its original entry, and never reads later header fields.
Its final cells and head are exact. The trace and length guide are empty.
Each unary doubling has linear cost in its old/new values. Earlier binary
prefix values sum to less than d, so their total work is O(d), not O(d log d).

## 4. Saturated product and exact fixed power

The primitive starts with positive unary a,b,d, a,b<=d, and empty PRODUCT.
Its outer head scans ACC, its inner head scans FACTOR. Every pair emits one
PRODUCT symbol and advances the D head once. The D head reaching its first
blank stops production immediately, including partway through an inner scan.
Otherwise an inner completion rewinds FACTOR and advances ACC. Thus exactly
z=min(ab,d) symbols are emitted. Every input and output head rewinds locally.
ACC, FACTOR and D are preserved. No prior ancestor is scanned.

Because 1<=a,b<=d, z>=max(a,b). Consequently complete rewinds of input
streams also cost O(z). Saturation does not leave an uncharged long operand.
This is why positivity and the operand bound are part of the primitive's
contract.

A power step copies one source into FACTOR, computes the saturated product,
clears old ACC and FACTOR, and moves PRODUCT into ACC. For squaring the source
is ACC; for multiplication by the current trial t it is CUTOFF. Distinct tapes
hold the two multiplicands, including when squaring.

For positive integers, saturation satisfies

    min(min(a,d)*min(b,d),d)=min(ab,d).

Start ACC at one and process the compile-time binary digits of Q: square at
each digit, and multiply by t at each one digit. After the digits representing
nu, the invariant is ACC=min(t^nu,d). After R_Q power steps it is therefore
min(t^Q,d). Exact equality of the ACC and D unary lengths is equivalent to
t^Q>=d, including perfect-power equality. All operands stay positive and at
most d. FACTOR and PRODUCT are empty at each step boundary.

## 5. Trial cap, exact stopping law and source composition

CUTOFF first contains t=1. Before a power test, the machine compares CUTOFF
and WIDTH in lockstep, reading CUTOFF first. Exhausting CUTOFF means t<=e,
including equality. Exhausting WIDTH first means t=e+1, the sentinel. Both
heads rewind over only the inspected prefixes. WIDTH is never written.

At a nonsentinel trial, t<=e<=d, so the saturated-power operand contract holds.
If t^Q<d, ACC is cleared and one symbol is appended to CUTOFF. If t^Q>=d,
ACC is cleared and the cutoff is accepted. A sentinel is accepted without
performing its power. Thus the first accepted value is exactly
C=min(ceil(d^(1/Q)),e+1). D is then cleared, the six private arithmetic/guide
markers are erased, and READY is emitted. All tapes except the newly created
marked CUTOFF already have their original cells and heads.

Put L=ceil(d^(1/Q)). Every descendant width x of the published controller
satisfies x<=e. If L<=e+1, C=L. If L>e+1, both x<L and x<C hold. Hence

    x<max(N,L) if and only if x<max(N,C)

for every visited node. The complete call tree, paid-site order and remainder
hooks are unchanged. C is retained unchanged throughout selected execution.

`compile_joined` inserts the published selected instruction table at a fixed
offset, adds that offset to all its jump destinations, and replaces its
unique halt by one jump to retirement. No other instruction changes. The
prefix's unique halt is similarly linked to the selected entry. Relocation
is verified structurally; it is compilation, not a runtime callback. The
selected code touches only tapes 0..3, so HEADER and the six restored private
tapes remain stationary. Its completed-call theorem restores WIDTH, CHILD,
STACK and generated CUTOFF. Retirement clears CUTOFF and its owned guard,
emits RETIRED and halts. All eleven original tape states and heads are exact.

This composition implements the control interface. The READY edge supplies
no row grants or payload values; the selected E/L/D_i/U_i/A_r/B_r/X edges
still require their existing separately paid payload consumers.

## 6. Complete time and historical backing

For a unary input of length n, literal helper-loop counts are:

| Helper | Complete transitions, including terminal reads and head returns |
| --- | ---: |
| Erase and rewind | 7n+4 |
| Copy unchanged, target initially empty | 11n+7 |
| Move and erase source | 12n+7 |
| Emit two per source symbol and delta extra, delta in {0,1} | 16n+5delta+7 |
| Saturated multiplication, z=min(ab,d) | at most 40z+40 |

A rewind from an n-position prefix costs 3n+3. In multiplication, z emissions
cost 7z; completed inner resets cost at most 3z+7z, outer probes at most z+1,
and all four terminal rewinds cost at most 12z+12. The displayed 40z+40 is
conservative. A complete power step, including operand copying, product,
old-input erasures and result transfer, costs at most 77z+62<=160d.

The unary update v -> 2v+delta costs at most 47v+35. Summing earlier prefixes
gives at most 82d for these updates. The remaining decode, length-guide,
access-trace and header-return work fits 200(d+h+1), h=|Gamma(p)Gamma(d)|.
Each cap comparison and its two rewinds cost at most 11t+9. A failed trial's
increment costs at most 6t+10. Final power comparison, its two rewinds and ACC
clear cost O(d), with the direct loops bounded by 30d+20.

There are at most C power trials and C cap comparisons. Since the positive
integer d itself satisfies d^Q>=d, C<=ceil(d^(1/Q))<=d and C^2<=dC.
Include all initial marker writes, retirement marker erasures,
D cleanup, both linking jumps and final halt. The resulting conservative
all-input additional bill is

    T_prefix+T_retirement <= 1000(R_Q+1)(h+dC+1).

With e_v the selected tree widths, complete control time is therefore

    T_total <= 200(P+1) sum_v e_v + 1000(R_Q+1)(h+dC+1).

Neither erased arithmetic nor head returns are omitted. The failed trials,
not just the successful power, are charged. No sparse table access is used.

WIDTH and CHILD visit at most e+2 cells each. CUTOFF visits at most C+2.
The published stack occupies at most e/(1-1/N)+depth+2, with depth<=e-1.
HEADER visits h+1 cells, TRACE at most h+2, and LENGTH at most h+2.
Each of D, ACC, FACTOR and PRODUCT visits at most d+2. Adding these intervals
and the preexisting history K0 gives, in particular,

    S <= K0+(5+N/(N-1))*e+5d+4h+40.

This deliberately loose bound counts all eleven tapes and all retired unary d
storage. It is not the predecessor's root-width-only descriptor bound: when
d is much larger than e, an O(d) history term remains and must be paid.
Repeated multiplication stages, trials and completed outer calls reuse the
same fixed origins; their erased capacity is counted by the largest visited
prefix, not reset to zero.

## 7. Why the actual selected source pays this implementation

The ordinary rational-root arithmetic is not a novelty claim: retained
`08-assembly.tex` already describes exact power comparisons. The explicit
prefix above instead admits a particularly simple unary lowering because
the actual selected exponents satisfy a useful full-budget inequality.

Since C<=d^(1/Q)+1 and d<=b_d*p^epsilon,

    dC <= d^(1+1/Q)+d
        = O(p^(epsilon*(1+1/Q)))
        = O(p^(1-1/Q^2)) = O(p).

Also h<=|E|=O(p), e<=d=O(p), and R_Q is fixed. Thus the prefix and complete
retirement cost O_Q(p), with additional historical backing O(d+log p)=O(p).
The actual retained array has V=2Mrw>=2(p+2). A single nonempty record already
pays this O_Q(V) root fee. No new BIT supplier, logarithmic improvement,
superpolynomial-fiber allowance or uncharged arithmetic model is needed.

The time implication is source-specific. The functional machine works for
other fixed Q and valid integer inputs, but O(p) would not follow merely from
epsilon<1 if epsilon*(1+1/Q)>1. This proof uses the selected coupled values,
not an unstated inequality for arbitrary beta. Q's immense constant and all
existing eventual source thresholds remain finite; no practicality claim is
made.

## 8. Novelty, predecessors and remaining obligations

The immediate predecessor supplied the literal rank-one controller but
explicitly left its cutoff production open. This package adds the actual
Gamma-header reader, cutoff producer, retained cutoff and cleanup, and an
exact fixed-table link. Its source-specific unary budget avoids presenting
a standard integer-root algorithm as novel.

[#5158](https://github.com/CrocSwap/integer-mult-bounds/pull/5158) already proves
dyadic fixed-bank recursion.
[#6719](https://github.com/CrocSwap/integer-mult-bounds/pull/6719) and
[#6739](https://github.com/CrocSwap/integer-mult-bounds/pull/6739) construct/review
richer delayed-cover natural-root grants from supplied binary T/R_body/w and
unary depth. Their root/payload work is not re-proved.
[#5515](https://github.com/CrocSwap/integer-mult-bounds/pull/5515) studies a
different historical QQ16 global-root cutoff and its parking/divisibility
law. [#2310](https://github.com/CrocSwap/integer-mult-bounds/pull/2310) and
[#2386](https://github.com/CrocSwap/integer-mult-bounds/pull/2386) retain credit
for earlier charged control preparation and polynomial-absorption work.

The actual selected N,P/owner manifest, WIDTH from Q0/root reservation, header
validity, grants, full payload/remainder consumers, native semantics and
analytic/numerical endpoints remain obligations. This is a literal closure
of the cutoff input edge under that admitted root interface. All five
foundational assumptions remain retained; kappa stays 0.00363005817.
Classical unary arithmetic, binary exponentiation and depth-first techniques
retain their ordinary credit. No independent human or formal-kernel review
is claimed by the author.
