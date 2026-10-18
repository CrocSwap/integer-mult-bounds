# Canonical source packets and common-view refinement

We prove a source-interface lemma for the retained BIT residual implementation.
We construct its raw directory from the physical prefix domain, route complete
owner packets, and bind the resulting common fields to the coefficient program.
We retain PR2501's below-64 child restriction. We do not construct the complete
selected global driver or a larger recursive child in this package.

## Quantified input contract

Fix an odd prime q, a dimension m at most 64, a finite request catalogue, and
fixed rational charts whose denominators and determinants are units modulo q.
For the selected application take m=64. Let

    M=q^w, Q=M/q, H=Q^(m²),
    N=|GL_m(F_q)|=product_(k=0)^(m-1) (q^m-q^k), w>=1.

Use the canonical residue-word extent L=bitlength(M)+1, including its high-zero
margin. Store arbitrary cardinalities on separate canonical binary tapes.
Keep the same q, M and compiled code width for older and current fields.

Take C>=1 old physical prefix positions, in their actual order. At each position
retain h frozen raw-field records. Allow repeated tuples: older spectator
coordinates can distinguish positions with identical coefficient fields. Supply
one old directory containing these C tuples in order. Within each family use

    [old physical position] × [GL low class] × [high matrix] × [complete fibre].

Order low matrices lexicographically by row-major entries. Order each high
matrix G in [Q]^(m²) the same way. Each fibre has R Boolean bits, including
unused stock, the complete body and suffix spectators in their declared order.
Older spectator coordinates may lie between frozen fields; represent their
positions in C instead of deduplicating tuples or moving them to a trailing
factor. This lemma assumes this physical family layout at entry. The global
caller still has to obtain that layout from its admitted stock and hosting map.

For the improved cost bound require R>=M^(2n), n>=1, and retain the root coupling

    w=ceil(e^(17/10000)),  2^(h+1)<=8e².

The correctness statements below do not need this coupling. Bare-header tests
use the direct cost bound, not its body-volume simplification.

## Finite low codes without a GL64 lookup table

We rank independent rows in order. After k independent rows, choose the next
row from F_q^m outside their span, a set of size q^m-q^k. Rank these choices
lexicographically and combine their ranks in those mixed radices.

To count excluded vectors with a prescribed coordinate prefix, solve the
corresponding linear equations for the k span coefficients. If the equations
have rank r and remain consistent, count q^(k-r) solutions. A new independent
equation leaves q^(k-r-1) solutions for each next digit. A dependent equation
allows one digit or makes the prefix inconsistent. Subtract that count from
q^(m-j-1), the number of all vectors with the next coordinate fixed. This gives
the exact lexicographic branch sizes. Induction on j proves vector rank/unrank;
induction on k proves a bijection with [N]. `low_codes.py` implements these
equations with fixed-q arithmetic during source compilation.

For R0 compiled requests, encode

    code = (2*request + common_view_flag)*N + low_rank,
    code_bits = ceil(log2(2*R0*N)).

This is an injective code for the request, view and complete low class. The
selected two-request test vocabulary needs 6,494 bits at q=3; the retained
28,278-request count would need 6,507. We instantiate two selected labels here,
with request 0 for MOVE18085 and request 1 for COPY511. We leave full request
enumeration to the global caller. Compile its complete vocabulary before execution:
changing its width after freezing older fields would violate their format.
We cannot encode these source classes with the 16-bit fixture default.

## Directory production and physical selection

`directory.produce` scans each old tuple once into a serialized local buffer.
It checks old codes and high digits one word at a time. It retains at most one
decoded old numerical word, rather than h decoded matrices.

For each old position, start an m²-word odometer at zero. Emit the old tuple,
the new code and the current high words. Increment the last row-major word,
carrying at Q; continue through the preceding words. On a full carry, clear
the odometer and advance to the next old tuple. The usual positional invariant
shows that we emit exactly the H high matrices, in order, once per old position.
At Q=1 we emit one all-zero matrix. At h=0 we still emit H records for each of
the C distinct empty-prefix positions.

We compute CH by 4096(w-1) fixed-q multiplications for m=64, or m²(w-1) in the
generic implementation. We count emitted tuples on a separate unbounded tape
and compare the two canonical encodings. We retain zero and dead fields and
their original global slots. Every high word has the full residue-word extent,
including leading zeros. We emit raw G, before any numerical basis preparation.

`selection.gather` scans one family in its declared physical order and copies
the chosen low block at each old position. It returns [old position]×[G]×[fibre].
`scatter` copies untouched blocks and substitutes the returned packet at those
same positions. Binary counters control both scans. We compile the chosen
low ordinal from the fixed vocabulary; we never decode a runtime high index
or spectator cardinality. Thus the produced directory and gathered payload
have the same prefix order and multiplicity.

## Complete owner/common route

For an owner chart sigma and fixed source low g0, compile

    d0 = g0 sigma mod q.

For each enumerated G, compute in the canonical M-ring

    d=(g0+qG)sigma mod M,
    K_ij=(d_ij-d0_ij)/q.

Use the representative d_ij in[0,M). Its residue modulo q is d0_ij, so the
subtraction is nonnegative, the division is exact, and 0<=K_ij<Q. Multiplication
by sigma is invertible modulo M and maps the g0 coset onto the d0 coset.
Consequently G↦K is a bijection of the entire high cube. This calculation
includes carries from g0 and from rational chart coefficients. Multiplying G
alone by the chart modulo Q generally gives a different key.

For one old position, decorate each complete fibre with its computed m²-word
destination key. Apply stable binary radix passes, starting with the last
matrix coordinate and its least significant bit. Within a pass, append each
key/fibre record to bucket 0 or 1, then concatenate the buckets. A one-hot word
cursor selects the bit. We use unit head movement, two sequential buckets,
binary counts and opaque bit copies; we perform no destination seek or
numerical word decoding.

Induction over passes orders the records by the processed key suffix. After
the last pass, the records have lexicographic K order. Strip the keys while
comparing them to a fresh canonical odometer. Bijectivity gives exactly one
record at each target G. Thus we send the complete fibre at g to g sigma,
preserving its body and spectator addresses. Process older positions in order
and erase local work between them. Older frozen fields never enter the sort.

For the inverse, repeat with sigma^-1 and source low d0. Matrix composition
and canonical output order restore the original packet. At w=1 the sole high
key is zero; the payload order stays fixed while the low-class label changes.
Keep Q in the M-word arena only for unsigned division, comparison and counting.
We never construct a residue ring from that padded quotient.

## Common-view coefficient binding

Write a compiled local projector as P0=B0 E_r B0^-1. In native owner coordinates
the source specification prepares

    P=g sigma P0 sigma^-1 g^-1.

After routing, the current physical header is d=g sigma. The corresponding
specification must use chart I and preparation B0:

    P=d P0 d^-1.

We retain the owner chart as provenance and for the inverse route. We keep
older frozen codes unchanged and tag the current field with the new common
request/low code. `binding.owner_common` checks the original split-basis
preparation before compiling this common specification.

We obtain a counterexample from the actual MOVE18085, role 222/family 444.
Use its base E00 and its chart that exchanges 0 and 8.
Choose native g=sigma, so common d=I. The correct projector is E00; a second
chart application gives E88. At f=1 and unit incoming weights, the correct
residual sends address e_H0 to e_D63, physical coordinate 127. With the wrong
specification, we leave it at coordinate 0 and change its first pivot from 1 to 0.

`residual.SelectedResidual` supplies the concrete consumer. It checks the
common code and chart, compares the encoded parent size/depth with the shared
geometry, then calls PR2501's packet interpreter. For each coefficient it wraps
the produced raw prefix in the original Fields interface and invokes the actual
selected coefficient/serialized-child callback. Each child retains one entry
and return across the complete high packet. The inherited child-width guard
still applies. We test this selected junction at coefficient sites and test
complete Boolean execution in the two-dimensional model.

`SelectedCopy511` compiles the authenticated interval, its inverse owner-low
selection and the common request specification, then passes that concrete
consumer to the physical driver. It checks the parent field depth and rejects
a conflicting frozen-code interpretation. We probe both wrapper junctions in
the selected source test; we do not count those probes as full payload execution.

## Transported COPY511 lifetime

We authenticate forward events 21881 through 21937, source role 473/family 527,
private role 661 and 55 target roles. The source chart exchanges 0…7 with 17…24;
the target charts are stage-zero identities. The interval has compact JSON hash
`e622fdcb880ed9e39962929f64272937cc4ccdd6bafd7def1dc1d7a68512b35e`.
We use family 28416 for the COPY request's private work and family 527 for its source.

Independently, write

    u=(0,1,-1,0,-1,0,0,-1),
    P0=E_[0,8) - u_hat u_hat^T/4.

Use zero on the other 56 coordinates. This projector has the authenticated
COPY511 base label. For common header d put P=dP0d^-1. With incoming unit
diagonal A and tail reversal C0, define

    v=P(C0 D-A^-1 H),
    T_d(H,D)=(H+A v, D-C0 v).

We obtain T_d²=I from P²=P. This is the direct weighted residual formula used
for the independent address check.

Gather the source at low d0 sigma^-1 and route it to common coordinates.
Gather each target at d0. Copy the common source into fresh private work and
execute the complete residual once. We then have

    Z(d,z)=S(d sigma^-1,T_d z).

Execute the 55 literal XORs and clear private work. For arbitrary dirty,
correlated live functions, the endpoint is

    S'=S,
    Y_t'(d,z)=Y_t(d,z) XOR S(d sigma^-1,T_d z),
    Z'=0.

The authenticated interval writes neither the source nor Z after the
completed transport. This supplies the transported ERASE guard. Comparing
Z with the untransported source would reject valid inputs. Our complete small
test includes such an input. We keep the original source family protected,
scatter changed targets into their original low blocks, and erase staging.
The targets have identity charts; a general local word still needs its own
inverse-route/scatter driver.

We verify all 128 address columns of the actual COPY511 residual over Z/9.
At identity low header we execute the fallback branch, with 16,517 child calls.
For the complete 56-family Boolean test, we use a two-dimensional rank-one
analogue with the same 55-XOR lifetime pattern. We leave the selected
64-dimensional Boolean family execution open.

## Tape charges and directory parking

Let J=m²L+O_q(1) be the key length and V=CHR the logical packet volume.
Let D denote the serialized frozen/current directory volume. We have

    D=O_q(CH(h+1)(w+1)).

The producer needs O_q(D) movement plus polynomial cardinality setup. It keeps
one serialized old tuple, one fixed-dimensional high odometer, and separate
binary counts. Computing CH costs O_q(w log(C+1)+w²); ripple counting costs
O(CH+log(CH+1)). These counts do not share the residue arena's width.

For the route, include the decoration and key movement:

    T_route=O_q(JV + CH(poly(w)+J²)).

The J² term matters for short fibres. Under R>=q^(2nw), n>=1, exponential
body volume absorbs the fixed polynomial in w, giving O_q(wV). Extra unused
or suffix stock only increases R. Gather/scatter across all N low classes
adds a fixed-q factor. We keep numerical labels, source compilation and the
finite selected route count inside C_q; we claim no practical small constant.

For directory absorption, the retained coupling gives

    h+1 <= 3+(20000/17)log2(w) <= (20051/17)w,
    D <= a_q(40102/17) CH w².

Since w<=2^(w-1)<=q^(w-1), we obtain D/V<=a_q(40102/17)/q².
Thus D=O_q(V). Each cardinality's own multiplicity absorbs its bit length;
in particular log2(C+1)<=C. The same argument charges source scanning,
rewinding, copying and erasure. Before absorption, retain the displayed
polynomial terms for arbitrary unbounded h and small fibres.

Per-prefix sorting needs O_q(V+Hw+poly(w)) local work, plus the output and
separate count tapes. A live parent directory adds D to physical occupied
volume while a child runs. We charge O(D) for a parked copy and its return.
We must add directory terms to the older literal occupancy V+4v and parking
5V+19v expressions; adding an inactive directory adds 5D plus its fixed role
markers to that parking formula. We do not reuse those numerical constants
unchanged. We preserve the asymptotic C_q V(n+w) toll under the retained
coupling and leave numerical reserve admission to the complete caller.

The source lemma creates no extra logical row stock and changes no recursive
denominator. Full request production, selected global execution, larger
children, recursive parking integration and formal machine verification remain
open. We claim neither a new selected exponent nor a full multiplication theorem.
