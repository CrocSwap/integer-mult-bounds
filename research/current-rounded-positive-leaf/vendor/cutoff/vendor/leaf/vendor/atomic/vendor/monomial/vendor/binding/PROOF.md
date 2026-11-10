# Retained Compact on the current complete coded field

Prepared for **@CubeJerry**, with substantial OpenAI assistance in source
analysis, mathematics, implementation, checking and prose. Apache-2.0.

## 1. Scoped result and exact predecessors

This package supplies one selected-bit XOR service for the actual record grammar
emitted by the current compiler/occurrence route binder. It produces the retained
Compact layout from the current twenty-three-field encoded descriptor, executes
the actual retained operation on A's coded ports, and returns the same complete
field and unchanged descriptor, with all private current segments physically
blank. Both source orders and the separate `f=1` case are covered.

This is a **structured finite-control, fixed-tape source refinement**. It is not
an emitted flat transition table, and its tests do not run this service through
A's `Controller.execute_table`. Section 6 gives the finite-control refinement
argument. A table-format exporter remains an integration task, not an experiment
claimed to have been performed here.

The exact predecessors are:

* [#3055](https://github.com/CrocSwap/integer-mult-bounds/pull/3055),
  `research/physical-complex-compact`, at canonical
  `7c49fe32c55de02c2c873655c804b16e4c3fef0a`: encoded Compact controls,
  literal rotations, complete exceptional repair, final bit gate, fixed roles,
  and the completed ordinary boundary. These mechanisms are inherited.
* Its ordinary supplier [#2899](https://github.com/CrocSwap/integer-mult-bounds/pull/2899)
  at `2f0911ad735643a069b9790302fbf179e49f74f8`, and compact word
  [#2250](https://github.com/CrocSwap/integer-mult-bounds/pull/2250) at
  `d404b48a1e7b147556b309497d55089c837dddb2`.
* [#5445](https://github.com/CrocSwap/integer-mult-bounds/pull/5445),
  `research/selected-monomial-tape-lift`, at the same canonical base:
  `XROW(target,source)` acts on every selected column with zero phase.
* [#5443](https://github.com/CrocSwap/integer-mult-bounds/pull/5443)'s executor
  and [#6878](https://github.com/CrocSwap/integer-mult-bounds/pull/6878)'s
  occurrence interface, through the exact public current-source exports
  [A, owned lifecycle](https://github.com/CubeJerry/integer-mult-bounds/tree/ab239cb6ee884e7a900dd9101c34448077fad0b0/research/compiled-owned-bank-lifecycle)
  and [B, row/occurrence dispatcher](https://github.com/CubeJerry/integer-mult-bounds/tree/5c59d247d51c6e1fca0dead3ed2139b6802b3a15/research/compiled-row-stock-dispatch).

The new content is the actual complete-field/descriptor/encoding join and its
whole current-call cleanup. It is not another construction of Compact or a
record-list census. The ordinary supplier's all-size endpoint, rate and backing
contracts remain named predecessors. A valid common numeric record format,
current source placement, root descriptor and ordinary-caller contract are
inherited from A/B. No Gaussian phase, nonpermutation native operation, scalar
precision estimate, root producer or analytic recovery theorem is supplied.

The pinned historical exponent is `tau_B1=99830289/100000000`. It is not the
selected `.0034` primitive saving. Section 9 gives the exact rate implication
limit. All five selected assumptions and `kappa=781451/250000000` remain unchanged.

## 2. Complete current input and requested endpoint

Fix a final template rank `N>=2` and distinct compiled block indices `s,t<N`.
They are finite template constants, never decoded runtime integers. The current
header supplies `f>=1`, `K,G,H>0`, `0<=rho_B<K`, within-row address width `a`,
numeric record width `b`, and positive outer/row counts `C0,R0`. Put `C=C0*R0`.
The public field, protected context and every work role are pairwise disjoint
current segments. Every work segment is physically blank at entry, with its
declared local origin marker. These are the owned caller's interface premises;
the service never borrows an ancestor segment or aliases the public input with
private workspace.
One complete field contains

```
V=C*J physical bits,                 J=2^a*b.
```

Every row quotient retains this same within-row rectangle. A numeric record has
two signed little-endian binary components of fixed positive width `w`, each
followed by component delimiter2. A encodes each virtual symbol in three physical
bits, so `b=6(w+1)`. The delimiter is `010`, not an all-zero filler. A permutation
of complete records does not change the common precision grid.

The two full front fields begin at within-row positions 0 and H. Write
`u=active_start`, `z=back_start`. Require

```
2H<=u,     u+N*f*K<=z,     z+H<=a,     (f-1)G<=H.
```

These intervals suffice for the service endpoint. The production B header also
has `H=dG`, `e=Nf+r<=d`, `0<=r<N`, and its root precision/reservation premises.
The producer checks the required intervals, offset, exact row length and
`e=Nf+r` geometry. It preserves every header field, including stock.

**All starts are already within-row positions.** The B root producer has
subtracted `q0*K` once. This service never subtracts it again, reinterprets a row
quotient as a new binary prefix, or rounds the row count to a power of two.

The endpoint changes exactly

```
address[u+(t*f+j)*K+rho_B] ^= address[u+(s*f+j)*K+rho_B],   0<=j<f,
```

where positions are numbered from the left within a row. It preserves every
other address coordinate, every outer row, each complete numeric record and the
order of its bits. Arbitrary dirty helper addresses and arbitrary coefficient
values are allowed. A complete canonical zero row remains the same zero row.

## 3. Encoded layout production without moving the field

Set `n=f-1`, `h=nG`, `c=fK`, `l=u+min(s,t)c`, `r=u+max(s,t)c`,
`S=a-z-h`, and `R=b*2^S`. The fixed native schema is:

| Name | Encoded width | Existing consecutive interval |
|---|---:|---|
| `u` | `h` | first front-field prefix |
| `u_rest` | `H-h` | rest of first front field |
| `t` | `h` | second front-field prefix |
| `t_rest` | `H-h` | rest of second front field |
| `before` | `l-2H` | every coordinate before the earlier block |
| `x` | `c` | earlier selected block |
| `middle` | `r-l-c` | all intervening coordinates |
| `y` | `c` | later selected block |
| `after` | `z-r-c` | all remaining coordinates before the back field |
| `b` | `h` | back-field prefix |

All widths are nonnegative. The last field ends at `z+h`; all following
coordinates remain in one opaque R-bit record. The width sum is `a'=z+h=a-S`, so

```
2^a'*R = 2^(a-S)*b*2^S = J.
```

This is an equality of existing consecutive stream intervals. No movement,
sorting, dropped spectator or tensor-rank argument is hidden in it. Only the
interpretation of a complete suffix fibre changes. Its encoded construction is
paid. Both helper suffixes remain complete spectators, and no helper prefix is
assumed zero. Choose native source `x`, target `y` for `s<t`, and source `y`, target `x`
for `s>t`. Both front prefixes precede both wide blocks and the back prefix
follows both, satisfying the retained ordering contract.

The native layout numbers selected bits from the least significant end of a
wide field. It therefore needs

```
rho_native=K-1-rho_B.
```

In a block starting at L, native low bit `rho_native+jK` is at position

```
L+fK-1-rho_native-jK = L+(f-1-j)K+rho_B.
```

This reverses the enumeration of selected columns in both source and target,
pairing exactly the same bits. It requires no chunk reversal. The actual
wrong-rho control fails a complete coded `K=2,f=1` endpoint check.

`read_header` consumes the exact B format: `1^ell 0` followed by ell LSF bits for
each of 23 fields. A unary length guide supplies each digit count; another guide
records all consumed header positions and rewinds the read-only context. Binary
canonicality uses finite last-bit states. All subsequent products, powers,
differences and comparisons use retained Count tapes. No host numerical layout
or decoded address supplies the operation.

Let E be the physical header length. On valid inputs its `row_bits` field has
bit length at least a. Thus constructing `2^a` is short-operand setup, not a
payload-bit counter. Intermediate word lengths are `O_N(E+1)`. The fixed number
of binary products, subtractions and repeated doublings costs `O_N((E+1)^2)`;
we conservatively use `O_N((E+1)^4)` below. Setup occurs once per service.

## 4. Exact alphabet and complete record bridge

A's virtual alphabet is 0..6 with physical code length 3. The old native alphabet
is 0..13, with blank 4, LEFT 2 and RIGHT 3. `SymbolPort` represents each old symbol
by four virtual binary digits, most significant first, using A's unchanged
`CodedPort` for each digit: **twelve physical bits per old symbol**.

At an unmaterialized old cell the first virtual read is blank 4. At an occupied
cell all four virtual digits are 0/1 and decode below 14. A read or write returns
to the codeword origin. An old unit move makes four virtual moves. Before a
right move over an unmaterialized cell, the full old blank code is written;
there is no partial codeword or physical hole. Each old unit read/write/move
takes fewer than 128 physical cell actions, including blank materialization.

The old LEFT marker is coded inside the current A segment. A's physical LEFT
remains outside that segment, and its local guard prevents ancestor access.
Old tape bodies contain no internal LEFT 2: payloads are bits, Counts use RIGHT 3,
and finite records use the retained higher tags. Retained completed-head guards
are refined by preceding-marker reads, not host head addresses. Old host backing
inspection rejects during execution; tests inspect the supplied physical ports.

The input bridge scans every public virtual symbol 0/1/2 and appends its three
physical code bits as three old opaque bit symbols. A unary field guide records
one step per public symbol and rewinds the unchanged field. Native Compact gets
the entire V-bit bridge, encoded widths, record width R and exact row count C.

Return consumes three old output bits per guided public symbol, checks a valid
code 0/1/2, and overwrites precisely that existing codeword. The guide and output
must end together, at the unchanged public frontier. Moving right from the last
occupied codeword reaches that frontier without extending it. A guided rewind
restores the public head, and the raw descriptor remains unchanged.

Native movement preserves complete R-bit records and R is a multiple of b. Thus
each output triple is the original triple in an original complete numeric
record. This proves delimiter, sign-bit, fixed-width and grid preservation for
every positive w, with no arithmetic, rounding or coefficient truncation.

## 5. Actual native execution and successful return

For `f>=2`, `n>=1`. The unchanged `CompactEngine.run` executes four ordinary
swaps/four rotations for an earlier source or twelve swaps/ten rotations for a
later source, complete exceptional-record repair, and the highest selected bit.
The retained #3055 endpoint gives Section 2's all-f XOR and restores all compact
labels on every complete outer row. No identity replacement or indexed payload
oracle is used.

For `f=1`, `n=0` is outside the old positive-n Control domain. The separately
paid `single` procedure builds the same encoded Layout, copies each complete row
to an owned lease and invokes the retained four-bucket `digit_permutation` on
the two selected bits. Its map is `(0,1,3,2)` for an earlier source and
`(0,3,2,1)` for a later source. All intervening/suffix fibres are copied. No
compact swaps, rotations or repair are required in this case. It is not a claim
that the old positive-n guard accepted zero.

Both branches preserve the protected output until it has been copied into the
actual public field. They close numerical leases and erase old input, guides,
output and owned markers. Old-symbol erasure leaves nonblank twelve-bit codes
for blank 4, so the wrapper additionally performs A's literal raw retirement on
**every** native work port. This erases the current call's complete encoded
high-water prefix and restores each physical current origin. These ports belong
to A's fixed continuation inventory; none is an unparked host bank.

The ordinary object's two parking tapes are also coded physical ports.
`ParkingAdapter` runs its unchanged seven-symbol transition table through local
operations. An empty-stack guard requires blank at the current head and LEFT 2
immediately before it. A nonempty stack with its head at a blank top therefore
fails. The packet guard checks its expected marker, the immediately preceding
LEFT 2, and blank body. Matched begin/push/pop/end preserve a contiguous prefix:
push appends at the blank top and pop erases every removed suffix cell. This
invariant excludes a hidden nonblank tail beyond a completed blank prefix.
The actual table and nonempty/dirty/displaced-head controls are replayed.

The guarantee is for successful admitted calls. No rollback after an arbitrary
interruption or rejecting native operation is claimed.

## 6. Fixed control and physical inventory

The constructor receives compiled N, the ordered pair and an unchanged Ordinary
factory. That factory is called once before runtime input exists. Arbitrary
native observation/payload callbacks reject. `Service.bind` fixes the actual
owner and context from the emitted token. Runtime `run()` gets no callback,
address list, coefficient dictionary or decoded numerical parameter.

All old Tape objects are allocated at template construction. Runtime Count and
stream creation leases fixed roles, and old physical constructors remain sealed
during native calls. The provider adds a fixed 160-slot setup pool, four bridge/
guide tapes and the coded parking pair. Compact retains `8m+256` roles (`m=10`)
and Binary retains 96; native ordinary roles and protected outputs are included.
The exercised q2/capacity64 supplier uses 1413 physical work ports. That is a
fixture inventory, not a selected supplier or eligible-prime certificate.

Schema indices, multipliers such asN, source records, program counters and pool
slots range over fixed finite sets. Unbounded values stay in Count/word tapes.
Scratch/live maps range over fixed role sets. A fixed number of references is
live in each bounded source frame; identity tests can be a finite alias relation
on them, rather than an unbounded generation counter. Temporary contexts and
cleanup callback lists have fixed static bounds. Native input-dependent
recursion already uses encoded continuations. Observation counters never select
instructions or operands.

Replace these bounded choices and fixed-depth calls by finite states, and each
symbol operation by its constant-size codec fragment. This yields fixed
multitape control on the physical0..6 alphabet with the declared inventory.
This is the supplied source-level physical refinement. Neither a flattened
table nor a proof-assistant certificate is claimed.

## 7. Full all-size time bill

Define

```
a'=z+(f-1)G,  M0=2^a',  v0=M0*R=J,  M=C*M0,  V=C*v0,
A0=2+a'+ceil(log2(R+1)),
delta=min(1,(f-1)*(2*2^(-G)+8*2^(G-K))).
```

Let `T_B(v,beta)` be the retained completed binary ordinary-interchange bill,
including actual padding/restriction, native output consumption and cleanup.
The fixed eligible radix q and its proof constants are part of this contract;
they are not inferred from the q2 fixture. For `f>=2`, #3055 supplies the complete
old-symbol charge

```
T_compact <= s * sum_(j=1)^C T_B(v0,(f-1)G)
            + O_m(V + M*A0^6 + delta*M*A0*(R+A0)),       (1)
s=4 for an earlier source; s=12 for a later source.
```

There are actually sC ordinary calls. Treating the entire packet as one s-call
volume without proving that interface would change the invocation bill. Both
exceptional-fraction terms, complete keys, global repair scans, highest-bit
operation, outer-row counter and rewinds remain in (1).

Let Q be the fixed number of work ports. Let Z be the sum of relative old-symbol
high-water extents reached **during this call**, including setup, bridge, guides,
native and parking roles. The new wrapper has the explicit envelope

```
T_new <= C_codec*T_compact
         + C_N*(V+(E+1)^4+Q) + 64*(Z+Q).                (2)
```

`C_codec` is a fixed constant for the complete guarded source-control refinement,
including the bounded `OriginHead` and `ParkingView` local marker checks. The
separate primitive lemma bounds one old read/write/step by 128 physical actions;
it alone is not a bound for an entire guarded source instruction. The source
bill in (1) includes its primitive and bounded-control operations, and each
added marker check occurs at one such fixed source site. Thus a uniform fixed
`C_codec` exists without multiplying by an input-dependent pass count.

`C_N` is a finite constant for the stated fixed setup and bridge programs, not
an additional input-dependent pass count. The constant64 covers A's complete
raw retirement of a twelve-bit old-symbol extent and its fixed origin work.
This separate Z term keeps encoded blank tails and cleanup from being free.

Every newly reached old-symbol position costs a unit move or initial write in
this invocation. Hence `Z=O(T_compact+V+(E+1)^4+Q)`. Substituting in (2) gives
the full shape of(1), with a fixed codec factor and `O_N(V+(E+1)^4+Q)` extra.
It does not scan a backing array's historical length. For `f=1`, set the ordinary
sum and exceptional term to zero and use the conservative actual bucket/setup
charge `O_m(V+M*A0^6)` in place of(1).

There is no `V log J` generic counter loop in the new bridge. Payload traversal
uses end markers and lockstep guides. Encoded length arithmetic occurs once on
the binary descriptor. The retained Counter loops use their amortized binary
traversal proof, not unit-cost random-access integers.

## 8. Current workspace, retained backing and favorable absorption

Keep the completed binary ordinary supplier's workspace and per-role backing
maxima explicit. Compact's retained occupied envelope is

```
4V + 2*delta*M*a' + M + O_m(A0+log(C+1)),
```

with the completed binary/ordinary private allowance added separately. The new
borrowed public field contributes V physical bits; the bridge is already the old
borrowed Compact input. Field/header guides and the fixed setup pool add
`O(V+E+A0)` old symbols. Multiply coded owned extents by 12 and add the two
parking roles. This accounts for current occupied space without omitting the
ordinary implementation's workspace.

For fresh backing, the compact pool has per-role maximum
`O(v0+delta*M0*a'+A0+log(C+1))`, and its fixed capacity is charged. Add the global
input/output/guide extents and actual completed binary supplier maxima. For
reuse, take each role's maximum over all preceding calls. On A's changing
current segments the absolute bound is the maximum of `current origin + coded
relative extent`; A's continuation/lifecycle bill separately covers those
origins. Erasure and smaller children do not shrink retained arrays.

Fresh blank current segments make the time claim different from the historical
footprint claim. Each previous successful call physically erased its complete
encoded extent. A new call materializes a contiguous prefix, and raw retirement
stops at that prefix's physical frontier even if the allocated array is longer.
The reuse replay checks the useful distinction: a smaller call following a
larger six-row call has exactly its fresh-call action count while retaining
the larger backing. This supports the invariant; it does not replace its proof.

For the production B geometry, `H=dG` and `f=floor(e/N)<=d/2`. Consequently

```
S=a-z-(f-1)G >= H-(f-1)G >= dG/2,
R >= b*2^(dG/2).
```

With `G=4ceil(log2 p)+6`, any retained root regime with `d->infinity` makes R
larger than every fixed power ofp. Moreover

```
A0 <= 3+a+ceil(log2(b+1)) = O(p)
```

under the actual common-format address/precision premise. Arbitrary row division
does not change this estimate because it preserves the full root rectangle.

The selected deferred schedule has `K=128G`, not `K/log p -> infinity`. The
actual sufficient guard estimate in #3055's proof only requires
`K>=G+4ceil(log2 p)+10`, which 128G satisfies. With `f-1<=p`,

```
delta <= 5/(128*p^3),
M*A0^6/V = A0^6/R -> 0,
delta*M*A0*(R+A0)/V = delta*A0*(1+A0/R) = O(p^-2).
```

For setup, the retained root format gives `E=O_N(p+log(C+1))`; in particular
fitted stock does not exceed its row count. Every fixed polynomial of E is
absorbed by the superpolynomial R and `log(C+1)^k=O_k(C)` for fixed k. The outer
count's logarithm does not enter each record's compact arithmetic. Initializing
and cleaning Q fixed roles changes a fixed constant.

Thus an admitted completed binary supplier
`T_B(v,beta)<=K_q*v*(1+beta^tau_B)` yields

```
T_new = O_(q,N)(V*(1+((f-1)G)^tau_B))                 (3)
```

in this favorable domain. Current workspace is linear when the corresponding
completed ordinary workspace premise is linear. Equations (1)--(2), with the
explicit backing allowances, remain the full all-size statement.

## 9. Current source binding and the rate boundary

B emits

```
('selected-bit-xor', route_id, 'enter' or 'return', s, t, source_token)
```

on exactly one owner. `Service` retains that owner and token and converts it to
#5445's `('XROW',t,s)` convention. Parameters come from the protected current
header. A transposition's entry/return still comprises six charged services.
Compiler-internal matched-field events consume no row stock: this provider
neither divides rows nor allocates an ordinary child. B's exact occurrence map
supplies the placement contract, rather than an imagined new row prefix.

The fixture runs the actual #5443 executor, A's `lower` and B's `bind` on a
declared compiler-control rule. At final rank 2 its elementary program emits
actual axis entry/return words, including both source orders. The native tests
bind those exact emitted tokens. This control rule is not a new Gaussian
identity or the materialized selected uniform template. The proof applies to
every valid emitted record using its fixed owner, ordered pair and common
descriptor contract.

For the frozen #6030 specialization in [#6115](https://github.com/CrocSwap/integer-mult-bounds/pull/6115),

```
tau_node = 1-kappa-4/1400000000 = 872264919/875000000,
tau_B1   = 99830289/100000000,
tau_B1-tau_node = 5000439/3500000000 > 0.
```

The historical upper bound (3) alone does not imply the selected node tariff.
For growing f its extra positive power cannot be hidden by a fixed constant; in
a polynomial active-width regime it cannot be hidden by a fixed polylogarithm
either. This is a limit of this upper-bound implication, **not an algorithmic
lower bound**. A stronger completed ordinary contract can be composed with the
same geometry/codec proof. No new κ, current `.0034` primitive proof or
assumption-status edit follows.

## 10. Evidence, provenance and open next questions

`verify.py` authenticates 32 exact public source exports and 51 bounded runtime/
NOTICE exports from the authenticated ordinary archives. Their hashes are
anchored in the freshly fetched public ordinary loader. Public archive Git
blobs, lengths and exact member hashes are recorded in `DEPENDENCIES.json`.
The new computational bootstrap replaces repository discovery, not a theorem
verifier. It does not claim to rerun the old full selected proof chain.

Physical fixtures use distinct complete signed-record labels, compare every
output record with an independent address oracle, check exact physical
frontiers/heads and descriptor bytes, and preserve translated-origin ancestor
sentinels. The `f=2` early/late tests execute actual Compact rotations, repair
and ordinary calls. They deliberately reduce helper widths and use a q2
elementary supplier; they do not instantiate the huge selected root or establish
an eligible-prime faster-rate theorem. Separate encoded producer tests satisfy
`H=dG` and include an outer count above `10^70`.

Adverse controls change rho conversion, omit raw retirement or the actual owner,
introduce invalid codewords, mutate source bytes and alter geometry parameters.
Parking controls reject nonempty blank-top stacks, a dirty packet and a displaced
head. Normal and optimized registered replays compare a complete deterministic
receipt. Finite execution is evidence for the all-size argument, not a substitute.

Open next questions:

1. Export this bounded source control into A's flat table syntax and run the
   complete lifecycle controller with these native events. Start with the fixed
   codec/parking fragments and actual emitted service tokens.
2. Bind a completed ordinary supplier with a sufficiently small exponent.
   Check its exact rate, stock and retained-backing contracts; do not relabel
   the historical B1 estimate.
3. Bind the retained phase/nonpermutation services, including the physical
   Gaussian phase predecessor [#3087](https://github.com/CrocSwap/integer-mult-bounds/pull/3087),
   to the current common record grid with their error and full cost bills.
   This permutation introduces no coefficient error and supplies only XROW.

Credit remains with the Compact identity/guard/repair authors and physical
Compact/ordinary, record-lift, compiler, continuation and precision lineages.
In particular retain Jose Manuel (`jmbarrancoml`), Douglas Colkitt, the authors
credited in unchanged #2250 NOTICE, Mark (`Matarener`)'s record lift, and the
contributors credited by the ordinary exports. No independent human review
or proof-kernel admission is claimed.
