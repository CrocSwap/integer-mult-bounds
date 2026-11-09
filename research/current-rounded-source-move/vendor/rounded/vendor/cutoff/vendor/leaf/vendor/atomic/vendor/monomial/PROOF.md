# Current coded Gaussian monomial with complete coefficient fibres

Prepared for **@CubeJerry**, with substantial OpenAI assistance in source
analysis, implementation, mathematical argument, and adversarial verification.
Apache-2.0; predecessor notices and exact computational sources are retained.

## 1. Claim and non-overlap

This package supplies the missing format and context join between the physical
Gaussian monomial of [#3087](https://github.com/CrocSwap/integer-mult-bounds/pull/3087)
and the current three-bit `CodedPort` numeric field and twenty-three-field
descriptor. It produces the old layout and signed coefficients through counted
physical operations, executes the unchanged monomial, and returns the complete
current format in place. It preserves the descriptor and all caller ancestors,
and erases every owned current segment, including encoded logical blanks.

The theorem below is a **structured finite-control, fixed-inventory source
refinement**, relative to the stated completed ordinary supplier and current
port contracts. It is not an emitted flat transition table for the lifecycle
controller. It does not close a universal selected assumption or change kappa.

The inherited phase formula, affine compiler, signed-pair theorem, Compact
algorithm, and their cost are not new results. Jose Manuel (`jmbarrancoml`), with
OpenAI assistance, already implemented those in #3087, building on #2250,
#2378, #2422, and #3055. [#6293](https://github.com/CrocSwap/integer-mult-bounds/pull/6293)
already treats the all-width phase convention, including the repeated constant.
[#6930](https://github.com/CrocSwap/integer-mult-bounds/pull/6930), pinned at
`c726399fbdb6d80dd13bed760b56572fb4ea1022`, already audits the primary phase
integer of the selected MOVE used here. We inherit those results.

Chris R (`Clear1nsight`), with OpenAI assistance, supplied the older prepared
QQ16 common-grid conversion and signed packet join in
[#4129](https://github.com/CrocSwap/integer-mult-bounds/pull/4129). Its raw/tagged
packet and caller contracts differ from this current descriptor, current
`CodedPort`, selected source token, and suffix layout. We neither repeat its
quantum conversion nor identify its old component ABI with the current one.

The separately credited [current Compact binding](https://github.com/CubeJerry/integer-mult-bounds/tree/5629e7772d1720d6727465e328a45694f8620538/research/compiled-compact-native-binding) supplies the
shared current symbol codec, exact header parser, guarded old-tape refinement,
and complete current-segment retirement. We reuse those exact bytes. Its opaque
record permutation by itself does not establish arithmetic on the three-bit
encoding: the new delimiter stripping, signed-field grouping, and exact return
in this package are necessary for that step.

## 2. Quantified current interface

Compile a literal invertible binary monomial of fixed rank `1<=m<=73`, with
matrix `L`, offset `v`, constant `c` modulo four, linear coefficients `l_i`
modulo four, and strict-upper quadratic coefficients `q_ik` in `{0,1}`.
Compile its direction and one completed ordinary supplier before numerical
input. The supplier has the unchanged native interface and the contract used
by #3087; its fixture elementary branch is not an admission of its faster rate.

`Provider(literal,native_factory,inverse=False).bind(work)` fixes a finite set of
physical work ports. `run(field,context)` receives a current `CodedPort` field
and a read-only `BinaryContextPort` descriptor, both at their local origins.
The caller supplies genuinely disjoint physical segments for field, context,
and all work roles. The object-identity guards reject obvious aliasing but do
not prove disjointness of distinct wrappers over the same physical segment.
All current work segments are initially physically blank. Caller ancestors
precede protected local origin markers and are outside the writable segments.

The exact descriptor order is

```
outer, rows, stock, row_bits, within_bits, record_bits, p, d, K, G, H,
q0, qF, qB, D, f, rho, active_start, back_start, selected_axes,
entry_start, remainder, cutoff.
```

Each nonnegative integer is represented by a positive unary digit length,
a zero separator, and that many canonical least-significant-first binary
digits. The exact physical frontier follows field 23. All fields are scanned
and returned unchanged; unused large metadata is not free. In particular,
the address reservation `H` is not the signed component width below.

Write `a=within_bits`, `b=record_bits`, `u=active_start`, `z=back_start`,
`C=outer*rows`, and let `h>=2` be the uniform signed component width. Each
original numeric record contains `r>=1` complex coefficient fields. Each field
has `h` real bits then a component delimiter, and `h` imaginary bits then a
component delimiter. The bits are little-endian two's-complement integers on
one fixed common grid supplied by the caller. Each virtual bit or delimiter
is encoded by the current three-bit code, so

```
b=6*r*(h+1),  row_bits=2^a*b,  V=C*2^a*b.
```

The delimiter is virtual symbol 2, physically `010`. A numeric zero component
therefore retains its delimiter; it is not an unformatted run of physical zeros.
Virtual blank 4 is the stream frontier, while physical blank is symbol 6.
No internal physical blank is admitted inside a canonical complete field.

The required geometry is

```
outer,rows,f,K,G,H > 0,    0<=rho<K,
n=f-1,  t=n*G<=H,
2H<=u,  u+m*f*K<=z,  z+H<=a,
selected_axes=m*f+remainder<=d,  0<=remainder<m.
```

All positions are already within-row coordinates measured from the left.
This service does not subtract a global prefix again, and does not change
within-row geometry when `rows` or `stock` changes. Row counts may be arbitrary
positive integers. The remaining current producer premises, such as `H=dG`,
the correct occurrence placement and the global common-grid choice, are
retained when this service is used by that producer.

For each original address `x`, let `x_j` be the rank-m column at positions
`u+(i*f+j)*K+rho`, `0<=i<m`, `0<=j<f`. The endpoint is exactly the inherited
monomial

```
P(x)=f*c+sum_j(sum_i l_i*x_(j,i)
                  +2*sum_(i<k) q_(i,k)*x_(j,i)*x_(j,k))  (mod 4).
```

It applies `x_j -> L*x_j+v` in each column, and applies `i^P(x)` to every one
of the `r` original complex coefficients. All other address coordinates,
outer-row labels, coefficient ordering, common quantum, and descriptor values
are preserved. The inverse recovers the original address first and applies
`i^-P(x)` there. No precision conversion or rounding occurs.

## 3. Encoded geometry and the suffix-fibre identity

Set `s=a-z-t>=0`. The last `s` unselected address bits are a complete consecutive
suffix fibre. Interpret its `2^s` original records as additional coefficient
fields of a single old-format record:

```
r'=2^s*r,  R=2*h*r',  a'=a-s=z+t,
M0=2^a',  M=C*M0,  v0=M0*R,  Vraw=C*v0=C*2^a*2*h*r.
```

For `h>=2`, `Vraw/V=h/(3(h+1))` lies between `2/9` and `1/3`, so raw
and current physical payload volumes differ by a bounded constant factor.

The old field schema is fixed at construction:

| Field | Width | Current interval |
|---|---:|---|
| `u` | `t` | first front prefix |
| `u_rest` | `H-t` | remainder of first front field |
| `t` | `t` | second front prefix |
| `t_rest` | `H-t` | remainder of second front field |
| `before` | `u-2H` | all positions before the vector blocks |
| `v_i`, each `0<=i<m` | `fK` | current vector block i |
| `after` | `z-u-mfK` | all positions before the back field |
| `b` | `t` | back prefix |

The field widths sum to `a'`. Every displayed width is nonnegative by the
interface. The two front prefixes precede all vectors, and the back prefix
follows them. All residual helper fields may contain arbitrary dirty address
bits. No helper is initialized to zero or discarded.

This is an equality of consecutive physical stream intervals after delimiter
stripping, not an uncharged permutation. The old record traverses first the
suffix address and then the original coefficient index, exactly their current
stream order. Since no selected bit is in that suffix, every coefficient in
the fibre has the same `P` and affine destination. The unchanged #3087 scan
processes all `r'` coefficients. Thus grouping the suffix preserves each
original coefficient's endpoint. Leaving the suffix among enumerated address
bits would also be algebraically possible, but would lose the long-record
accounting used below; the implementation performs this explicit grouping.

Old native selected positions are counted from the least-significant end of
each vector field. Set

```
rho_native=K-1-rho.
```

The old selected position `rho_native+jK` equals the current position with
column ordinal `f-1-j`. The same reversal occurs in every vector block. Since
the identical affine map acts independently on each column and the phase is
the sum over all columns, this reversal changes neither endpoint. Merely
passing current `rho` to the old API would generally select other bits.

`prepare` constructs these integers with encoded Counts. It reads `h` by
counting the first component's format symbols; it does not decode a signed
value. It divides `b` by `6(h+1)` and checks positive quotient and zero
remainder. It checks the exact complete row length and all intervals above.
Its varying row counts, widths, shifts, and coefficient count remain on tapes.

## 4. Signed conversion and the complete return

`import_field` visits the current stream in order. For each complex pair it
copies exactly `h` bits, checks and skips delimiter 2, then repeats for the
imaginary component. It uses an encoded ripple counter for those widths and
a lockstep guide for the current symbols. It checks each later component has
the same width and delimiter. It preserves the complete `h`-bit representation,
including leading zeros and redundant sign bits; components are never
normalized as unsigned Counts. The old input has precisely the complete raw
format of #3087. The inherited engine verifies its total extent against
`C*2^a'*R`, so a whole-pair-aligned but incorrectly sized field is not silently
accepted. The guide restores the current public head without decoding a
payload length or consulting its allocated array length.

The monomial runs on that separate borrowed raw copy while the parent scope
is suspended. Its protected result is consumed before engine reuse. Only after
the entire monomial has returned does `export_field` modify the public field.
It copies every returned signed bit and reinserts each component delimiter at
its existing position. It requires exact agreement of raw output, current
field and guide frontiers. It restores the public origin and clears the
protected return, marker, bridge and guide. Consequently the returned current
body has exactly `V` physical bits in the same canonical format and on the
same numerical grid.

The only numerical admission is inherited signed representability. For phase
0 no component is negated; phase 1 requires the imaginary component to exceed
`-2^(h-1)`; phase 2 requires both; phase 3 requires the real component. These
conditions are required separately for every coefficient in every folded
fibre. The unchanged #3087 implementation checks both components before
emitting that pair, and raises `SignedHeadroomError` when needed.

On this named error for otherwise admitted shape and format, the inherited
engine erases partial output, closes its counters and current packet, and
returns to a reusable closed state. The wrapper has not written the public
field, closes its setup Counts, and retires all coded work. Thus field and
context remain unchanged and a subsequent valid input may use the same
inventory. This statement does not promise rollback for arbitrary malformed
streams, internal errors or interrupted execution.

## 5. Physical refinement, ownership, and retained backing

The source bootstrap loads the authenticated computational bodies of #3087
unchanged. Its archive-discovery module is replaced only by a shim selecting
the already authenticated shared Compact, Count, Tape and ordinary modules
from `compiled-compact-native-binding`. Runtime identity checks require one
actual Count/Tape vocabulary. `DEPENDENCIES.json` records Git blob and SHA256
for all copied source files, together with original repository, commit or
archive/member provenance. No numerical computation is delegated to a fixture
callback or to a host array.

That binding represents each old symbol by four current virtual bits, hence
twelve physical bits. Logical blanks are coded nonblank physical strings.
The old runtime `read`, `write`, `step`, origin guards and parking-table steps
are refined by local physical operations. Runtime indexing of old `cells`
is blocked; host head positions are not exposed to the algorithm. Fixed
template data, fixed role identities, alphabet symbols and finite phase states
may be in control. Varying coordinates and shapes use the encoded primitives.

Construction, including the literal affine word and native inventory, occurs
before input and has a positive fixed cost `F_template`. The wrapper adds
192 setup scratch roles and four persistent buffers to the inherited finite
engine inventory. The wrapper has 23 borrowed-header copies and a fixed
number of setup temporaries: 24 `prepare` results and the component-width Count,
with fewer than 32 additional arithmetic/counter roles at any source site.
Thus fewer than 80 wrapper roles are simultaneously live. Its parent scope is suspended across the child,
so these roles are not silently shared with active child leases. There is no
physical tape allocation per row, coefficient, column, gate, or recursion depth.

On completion, raw current retirement scans through coded logical blank tails
to the first fresh physical blank and restores the local origin. It does not
stop at an internal old logical blank. Therefore every owned current extent
is physically blank, and ancestor prefixes are untouched. The normal and
optimized executions below inspect all historical backing cells to test this
claim; the mathematical invariant is the contiguous coded frontier and local
origin, not the inspected array representation.

Previously allocated backing remains allocated. For role i let `o_i(k)` be
its current physical origin and `z_i(k)` its reached old-symbol extent in call
k, including coded blank extension. An honest retained envelope includes

```
sum_i max_(k<=current) [o_i(k)+12*z_i(k)+O(1)],
```

as well as borrowed field/context backing and the caller's continuation bank.
Smaller calls do not shrink this envelope. They also do not rescan a prior
larger extent: a successful preceding retirement leaves it physically blank,
and a new contiguous call stops at its own frontier.

## 6. Complete cost and the favorable domain

Let `E` be the physical header length, `Q` the fixed work-port count, and
`A=2+a'+ceil(log2(R+1))`. Let `g_E` be the literal word's early XOR/toggle
count, `g_L` its late XOR count, `g=g_E+g_L`, and `S=4g_E+12g_L`.
For `f>1` set

```
delta=min(1,(f-1)*(2*2^(-G)+8*2^(G-K))).
```

The completed binary ordinary bill `T_B(v,beta)` includes real padding and
restriction, its native work, borrowed preservation, return consumption and
cleanup. #3087 and #3055 give the unchanged old-symbol invoice

```
T_old <= S*sum_(j=1)^C T_B(v0,(f-1)G)
         + O_(m)((g+1)*(Vraw+M*A^6)
                  +g*delta*M*A*(R+A)).                         (1)
```

There are actually `S*C` ordinary calls. At `f=1` there are no ordinary calls
or exceptional term; retain `O_m((g+1)*Vraw+M*A^6)`. The phase-only recipe has
`g=0` and still pays its complete coefficient scan and setup. No fixture timing
is used to derive (1).

The new wrapper incurs no per-payload-bit long length scan. Ripple counter
initialization and decrements for an h-bit component cost `O(h)` in aggregate,
and each current symbol is visited a bounded number of times by the bridge
and guide. Hence signed format conversion costs `O(V)`. The first component
width scan costs `O(h)` and is included in this bound. Since a valid header's
`row_bits` value has at least `a+log2(b)` digits, and `h<=b`, all one-time
geometry arithmetic has operand lengths `O_m(E+1)`. Repeated doublings build
`2^a` and `2^s` in polynomial time in E. A conservative envelope for the fixed
number of products, divisions, comparisons and such loops is `O_m((E+1)^4)`.

Let `Z=sum_i z_i` denote **this call's** sum of reached old-symbol extents over
all work, setup, bridge and parking roles. A complete current-physical bill is

```
T_current <= F_template + C_codec*T_old
             + C_m*(V+(E+1)^4+Q) + 64*(Z+Q).                  (2)
```

The fixed `C_codec` covers the whole guarded source-control refinement,
including local head and parking checks; it is not inferred solely from the
constant for one read/write/move. The explicit last term pays current raw
retirement, including encoded blanks and origin work. Every reached symbol
costs a unit move or initialization in this call, so
`Z=O(T_old+V+(E+1)^4+Q)`. Substitution gives the shape of (1), with a fixed
codec factor and the displayed new setup/conversion bill. In contrast to
#3087's specialized f=1 unused-G observation, this adapter reads the complete
current descriptor and charges its E even when a field is unused.

For occupied workspace, keep the inherited conservative monomial allowance

```
6*Vraw+2*delta*M*a'+M+O_m(A+log(C+1))
    +W_B(v0,(f-1)G)+F_native,
```

with ordinary and exceptional terms omitted at f=1. Add the borrowed current
field V, header E, setup/header guides `O(E+A)`, and the current field guide
`O(V)`, multiply old-symbol owned extents by twelve, and include the fixed
parking roles. For fresh backing also retain each inherited parent role's
maximum `O(Vraw+A+log(C+1))`, each Compact role's maximum
`O(v0+delta*M0*a'+A+log(C+1))`, protected output, and the actual ordinary
supplier's per-role allowance. Fixed role capacities are genuine constants.
For reuse use the historical maxima in Section 5 rather than fresh size alone.

A favorable production specialization must state its hypotheses. If `H=dG`,
`m>=2`, and `mf+remainder<=d`, then `f<=d/2` and

```
s>=H-(f-1)G>=dG/2,
R=2*h*r*2^s >= 2*h*r*2^(dG/2).
```

For m=1 this automatic inequality is unavailable; long-record growth remains
an explicit extra domain premise. In a root regime with `d->infinity`,
`G=4ceil(log2 p)+6`, `A=O(p)`, and `E=O_m(p+log(C+1))`, R exceeds every fixed
power of p. The selected schedule's `K=128G` satisfies the sufficient retained
guard inequality `K>=G+4ceil(log2 p)+10`, giving `delta=O(p^-3)` for `f<=p`.
Then `M*A^6/Vraw=A^6/R` and
`delta*M*A*(R+A)/Vraw=delta*A*(1+A/R)` are bounded by the claimed lower order
terms. The E-polynomial is absorbed using superpolynomial R and
`log(C+1)^k=O_k(C)` for each fixed k. These are additional stated domain
conditions, not consequences of an arbitrary valid finite header.

If the admitted ordinary supplier has `T_B(v,beta)<=K_q*v*(1+beta^tau_B)`,
the favorable specialization is
`O_(q,m)(V*(1+((f-1)G)^tau_B))`. The retained historical exponent is
`tau_B=99830289/100000000`. It does not imply the smaller current selected
node exponent. Equations (1) and (2), the source supplier premises, and the
backing envelopes remain the complete all-size statement; no new kappa is
claimed.

## 7. One actual selected source boundary

`selected_service.py` authenticates the current selected word and canonical
Clifford source. It locates raw event 9896,
`["MOVE",236,3,7,false]`, through the current lifecycle `current_local` lowering.
The exact service token is `("move-in","local",9896,raw_record)` on owner
236, with the matching `move-out` cut. This raw four-field token is the
established source boundary. The guard also accepts a syntactically flat prefix
before that tuple, but this optional flat-prefix ABI is **not** the nested
token emitted by `source_ir.remap`. The actual `caller-local` token contains
the old token as its last tuple member, and is not accepted by this binder.
An enclosing caller therefore still needs a separate typed token adapter;
no complete nested caller-occurrence binding is claimed. The physical owner is
bound explicitly through the event's field list; it is not an implicit global
array reference.

The event token alone does not normalize the enclosing occurrence's header.
At this boundary the caller must expose the nine current vector blocks and
their span with `selected_axes=9*f+remainder`, in the coordinates admitted in
Section 2. A larger compiler occurrence needs its existing paid placement and
descriptor service to establish this premise, in addition to the token adapter
above. Matching a raw token or flat suffix is not a proof of that geometry.

The literal comes from the authenticated canonical frame transition 3 to 7.
The existing #6930 audit supplies the width-one phase interpretation. Its
right monomial has constant 1 and the exact rows

```
matrix=(21,17,2,20,8,32,64,128,256), offset=1,
linear=(3,0,3,0,2,0,0,0,0), quadratic=(5,0,5,0,0,0,0,0,0).
```

The resulting record hash and complete left literal are in `SELECTED-MOVE.json`.
`Service` compiles the right monomial at `move-in`, and the left at `move-out`.
The intermediate rank-one Fourier child is outside this contribution. This
is not a new primary-phase audit, and not a numerical proof of the full MOVE.

Four selected physical phase-control calls use the actual 23-field descriptor,
native recipe, and codec with f=2,3,4. The zero-column f=2 case produces phase2,
not a copied one-column phase1. A wrong residue and wrong frame token are
discriminating negative controls. These execute the actual selected control
interface but do not materialize its complete rank-nine packet. The all-size
endpoint follows from Sections 2-5 and inherited monomial correctness; the
finite evidence cannot replace those arguments.

## 8. Evidence, limits, and remaining work

The author fixture uses a separately coded signed/address endpoint oracle and
complete current physical packets. It covers f=1 with nontrivial K/rho
orientation, f=2 forward and inverse with real Compact/ordinary calls, all
coefficient fields, multiple outer/inner rows, dirty spectators, folded suffix
fibres, nonzero translated origins, later-field signed-headroom rejection and
valid retry, and historical backing reuse. Both normal and optimized Python
must reproduce the same exact action and endpoint receipts. It uses the actual
ordinary elementary branch, never an oracle supplied to the numerical engine.
Independent review is registered separately when its receipt is frozen.

The selected rank-nine complete packet is not executed. These tests admit
neither the retained faster ordinary rate nor the selected native exponent.
The current placement/row service, actual complete numerical caller, flat-table
export, global width/headroom allocation, full selected recurrence budget,
coefficient arithmetic and analytic recovery remain outside this scoped join.
All five selected framework assumptions remain listed in the receipt.

## Open next questions

1. Export the bounded current adapter control into the lifecycle controller's
   literal transition-table syntax. First preserve this exact complete-format
   endpoint and signed-error boundary on one occurrence; the existing semantic
   service token alone is not a machine table.
2. Supply a completed binary ordinary service at the current required rate,
   or a different full invoice. Its source preservation, private cleanup and
   output consumption must accompany the rate; this adapter cannot upgrade
   the historical exponent.
3. Join the current numerical caller's width/common-grid allocation to these
   phase-specific headroom conditions and to the paid rank-one child between
   the two MOVE monomials. The first useful check is a complete small actual
   caller occurrence with its live descriptor and suspended private bank.
