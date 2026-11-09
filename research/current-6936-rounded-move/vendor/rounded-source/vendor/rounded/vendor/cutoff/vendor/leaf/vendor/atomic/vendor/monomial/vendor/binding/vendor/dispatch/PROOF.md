# Encoded whole-row dispatch for the retained occurrence compiler

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.

## 1. Proposition, source boundary, and novelty

Fix one finite uniform template produced by the retained chronological
product, completion/splitting and integer compiler. Write its final rank,
productive width, conservative owned inventory and ordinary paid count as
`N >= 2`, `W >= 1`, `O >= 0`, and `P`. These are constants before the numerical
input varies. They are not the raw P104 width or its local private peak.
Fix its complete native services and finite list of physical field IDs.

**Row/occurrence dispatch theorem.** Given an admissible encoded complete-row
descriptor, the fixed tables in `row_programs.py` implement exact whole-row
division and reassembly for every fixed positive divisor, physically produce
the quotient row and stock descriptors, and update the ordinary numerical
child geometry `e -> floor(e/N)`. They preserve complete front/back control
fields, every spectator bit plane, the selected offset `rho`, and the parent's
descriptor. The source binder in `compiler_routes.py` connects these services
to the actual flat compiler event grammar: compiler-internal matched fields
receive complete coordinate routes and inverse returns, while only final
ordinary rank-one calls consume row stock. The local time and backing bounds
in sections 8 and 9 hold at every input size in the stated domain. There is
no extra row-address-width, recursion-depth, or `e` factor in the row-copy toll.

This refines a specific retained boundary. The older full physical controller
(#3385), complex compact package (#3055), literal two-role parking caller, and
physical row padding package already provide substantial infrastructure. The
two-role caller takes a supplied row guide. The padding package already proves
amortized linear binary-to-unary conversion; its implementation is retained
byte for byte. The new work is the arbitrary final divisor, encoded descriptor
production, canonical encoded-zero padding, ordinary geometry update, and
binding to the current source's distinct matched-occurrence and ordinary-child
events. It is not a new generic existence proof for leaves or controllers.
Earlier raw reservations in #5480 and generic allocation/backing work in
#5814 are also predecessors, not new claims of this package.

The occurrence package #6878 supplies the geometric extension and symbolic
tariff. Here each added transposition becomes six charged selected-XOR records,
three on entry and three on return. Its native, monomial, compact and all-column
premises remain. The owned lifecycle export supplies physical initialization,
COPY-as-ADD, suspension, output preservation and parent restoration. Its proof
is not replaced by a row-count argument. Exact source bytes, Git object IDs
and SHA256 values are in `DEPENDENCIES.json` and `SOURCES.json`.

The selected record remains #6030 with
`kappa = 781451/250000000 = 0.003125804`. All five selected framework assumptions
remain recorded. This theorem supplies a narrower implementation implication
under explicit retained interfaces. Finite execution supports the written
proof; it is not a proof-assistant admission or a complete multiplier replay.

## 2. Complete rows and the descriptor ABI

A physical field has the serialization

`[outer prefix c in 0..C-1][row ordinal u in 0..R-1][complete row v in 0..J-1]`.

Here `C,R,J` are positive. A complete row contains `2^a` numerical records,
each of exactly `b` physical bits, so `J=b*2^a`. It includes every front control,
active coordinate, back control, spectator and record suffix, rather than one
representative of a control fibre. Volume `V=CRJ` counts actual physical bits.
The general splitter needs the complete row length. Geometry specialization
also uses its valid factorization `a,b` and the complete numerical format.

The current lifecycle alphabet is physical `0,1,LEFT=2,SEP=3,END=4,BASE=5,BLANK=6`.
Payload bodies contain physical bits only. Numerical virtual symbols use
three physical bits; component delimiter 2 is `010`. The row tables operate
on physical bits through `PhysicalPort` and never treat virtual blank code
`100` as the physical frontier. Payload origins follow `LEFT`; bridge and
staged-header origins follow `BASE`. All exposed heads enter and return at
their own origins. Physically distinct tapes are an ABI premise, not an
uncharged runtime pointer comparison.

For two signed components of fixed root width `w`, one Gaussian record has
`b=6*(w+1)` physical bits, including both terminators. The common-grid supplier
chooses `w`; it stays fixed through ordinary recursion. The ideal precision
parameters of #6900/#6901 and their error/overflow obligations remain separate
from this exact encoding compatibility.

There are forty fixed row work ports, one row descriptor port, and the `W`
already declared public ports. Lifecycle bridge/header ports are reused. No
new tape is allocated at a recursive call. A finite template may have a large
constant tape inventory, independent of input size and recursion depth.

Each descriptor integer is canonical least-significant-first binary, including
the single symbol `0` for zero. For binary length `ell`, the header writes
`1^ell 0` followed by the `ell` digits. Its twenty-three entries are:

| Entry | Meaning |
| --- | --- |
| `outer`, `rows`, `stock`, `row_bits` | Positive `C,R,S,J` at a row invocation |
| `within_bits`, `record_bits` | Complete-row factorization `a,b` |
| `p,d,K,G,H,q0,qF,qB,D` | Fixed global precision/layout/reservation parameters |
| `f` | Width of each rank-one block of the current uniform program |
| `rho` | Selected bit plane, `0 <= rho < K` |
| `active_start` | Current `N*f` rectangle start, within the complete row |
| `back_start` | Fixed complete back-control start, within the row |
| `selected_axes` | Current ordinary input width `e` |
| `entry_start` | Start of the ordinary input's `e` chunks, within the row |
| `remainder` | `r=e mod N` at an internal ordinary node |
| `cutoff` | One certified global integer phase cutoff `t >= N` |

**All three starts are within-row coordinates.** The root producer converts
the source's global offsets once: `entry_start=o-q0*K` and
`back_start=z-q0*K`. Front fields begin at within-row coordinates 0 and `H`.
After padding or division, `rows` need not be a power of two. Nothing subtracts
a new `ceil(log2(rows))`, changes `q0`, or moves a control field after an imagined
new binary row prefix. Row ordinal and within-row coordinates remain a pair.

An admissible root header certifies the source's complete geometry and compact
domain, including `H=dG`, the full two front and one back control fields,
`entry_start >= 2H`, `entry_start+e*K <= back_start`, `back_start+H <= a`,
the record-fibre conditions and every numerical provider's size/precision
guards. The tables check header syntax, positive extents, exact divisibilities
and the cutoff lower bound. They do not re-prove every mathematical precondition
of the root parameter producer. The selected global parameters, stock law and
phase cutoff remain an explicit caller premise. The new root table physically
derives `J,f,r,active_start`; these are not obtained by host integer decoding.
Those derived fields in a root preheader may be canonical placeholders;
the root table overwrites them before that header is used for routing.

Each numerical provider must return exactly the same encoded extent and
component boundaries, with physical `BLANK` immediately after it. Temporary
encoded virtual blanks beyond that frontier must be removed by its charged
return routine. This is necessary for the router and current `CodedPort`
implementation to compose.

## 3. Literal split, inverse, and complete stock

For a fixed divisor `g >= 1`, assume `g | S` and `S | R`. Put `Q=R/g` and
`S'=S/g`. The child retains all fields except the row/stock quotients and, in
numerical mode, the ordinary geometry of section 4. The literal split is

`(c, u=g*q+w, v) -> role w at (c,q,v)`.

This is a bijection for `w<g,q<Q,v<J`. Each role receives `CQJ` physical bits
and the same complete within-row rectangle.

`compile_prepare(g)` scans canonical encoded row and stock counts using
finite-state binary division by constant `g`. It starts at the highest digit.
State `h in 0..g-1` is the remainder; input bit `x` emits quotient bit
`floor((2h+x)/g)` and enters state `(2h+x) mod g`. The quotient bit is 0 or 1.
Exact division returns only at remainder zero, trims leading quotient zeroes,
and requires a positive quotient. The `g` remainder states are finite control,
not an input-dependent register.

`compile_router(g)` decodes the child header, builds unary guides of lengths
`C,Q,J,S'` with the retained decoder, and verifies `S' | Q` by traversing the
row guide and cyclic stock guide together. Each stock rewind is charged to
consumed stock marks. It scans in order `c,q,w,v`: the source advances through
one complete row, role `w` receives every bit, and the `J` guide rewinds at
the row end. Role numbers are static states. Source and header are preserved;
all guides, decoded integers and temporary words are erased.

The merger uses the same order with source and destination exchanged. It
copies every bit of every role to a distinct return bridge and erases the
consumed role bits. It is exactly the inverse index equation, including all
controls and spectators. Exact physical frontier checks reject short or extra
packets. All heads return to local origins. These are success-domain machines;
malformed-header rejection does not promise arbitrary transactional rollback.

The stock invariant is

`S | R and g | S  =>  (S/g) | (R/g)`.

Consequently the product of all unreleased divisors on a nested path must
divide the original stock. Iterate in actual call order and restore parent
descriptors on return. A maximum factor is insufficient: nine rows can be
divided by 3 twice, but stock `max(3,3)=3` is exhausted at the first division;
stock 9 supports both. Independent factors 2 and 3 likewise cannot be replaced
by 3.

A retained source-style sufficient reservation is

`S0=[W*(O+1)]^L*S_other`, where `N^L >= 2d`.

A different schedule may use a smaller justified stock, but each actual path
product must divide it. Reserving `O+1` row labels does not initialize private
memory, convert productive input to erased scratch, or create output credit.
The owned lifecycle proof supplies those actions. Compiler-internal matched
occurrences below consume no further row factor.

## 4. Ordinary geometry and the actual phase leaf test

At an internal node of encoded width `e` and entry `s`, write

`e=N*f+r`, `0 <= r < N`, `active_start=s+r*K`.

The required remainder service completes the `r` elementary selected kernels
at chunks `[s,s+r*K)` on **every** complete public field. The uniform program
then acts on its `N` blocks of `f` chunks, selecting the same `rho` in each.
The remainder's numerical/physical proof and charge remain separate; an
identity test fixture cannot admit it. Complete-row splitting commutes with
this rowwise map, so `install` may invoke it after public splitting and
descriptor installation.

Before an ordinary rank-one call, the source-emitted axis route makes the
requested `f`-chunk block canonical first. A recursive child has

`e_child=f`, `entry_child=active_start_parent`,
`f_child=floor(e_child/N)`, `r_child=e_child mod N`,
`active_start_child=entry_child+r_child*K`.

`derive_geometry` copies old `f` to `selected_axes` and old `active_start` to
`entry_start`. Fixed-rank binary division emits the child quotient/remainder.
At most `N-1` encoded additions form `r_child*K`, then one addition forms the
active start. The work is a finite `N`-dependent constant times descriptor
length. There is no loop over the decreasing ordinary width `e_child`.

The child fits because

`active_start_child+N*f_child*K = entry_child+e_child*K`,

which is inside the parent's first requested block and hence its active
rectangle. Fixed front/back geometry and `a,b,J,d,D,H,K,rho,q0,qF,qB` survive.
Completed remainder coordinates remain arbitrary spectators. The parent's
complete encoded descriptor is parked and restored byte for byte.

At root, `compile_prepare(...,root=True)` retains `selected_axes=e` and the
supplied within-row entry. It derives `J=b*2^a` by repeated binary doubling
and emits the same `f,r,active_start` equations. The root width factor is
consumed only after receiving a padded row count and stock divisible by `W`.
The root parameter/padding producer stages that count in the header; its
actual staging and parameter construction are separately billed.

The selected deferred schedule (#6115) uses one phase cutoff
`s_phase=max(N,h^eta)`, `eta=1/1400000000`, shared by descendants. For integer
widths define `t=max(N,floor(h^eta))`. A requested child is elementary exactly
when `f <= t`. `compile_leaf(N)` decodes the header, checks `t >= N`, and
compares encoded `f,t`. Least-significant-first comparison retains the sign
of the latest differing bit, which is the highest differing bit at the end;
unequal canonical digit lengths determine their order. The descriptor is
preserved and all work erased before returning a finite Boolean terminal.
`prepare` rejects recursive descent when `f <= t`.

Elementary children and the root branch `e <= t` retain the source leaf
providers. `StockLeafFixture` is explicitly a structural integration fixture,
not the numerical stopping condition. Root geometry, child geometry and leaf
comparison are distinct executable tables and distinct test groups.

## 5. Actual source grammar and charged occurrence routes

The exact owned-lifecycle source lowerer refines #5443's unchanged compiler.
It emits actual physical IDs, unique occurrence-owned banks, complete ordered
matched field lists, source-complement and deepest-exit brackets, private
lifetime actions, and explicit elementary-axis brackets. Raw unit/native
wrapper services retain their precise identities; their endpoints are not
replaced by a rank profile.

For the selected raw source, complete ambient 145 equals maximum target rank
145; its authenticated current lifecycle receipt binds that fact for all
13,444 productive roles. Chronological products multiply both quantities,
completion keeps the maximum target, and paid-job splitting changes no target.
Thus the prepared selected unit retains equality between complete ambient and
the compiler's maximum-target parameter. The source column fit applies to
that actual ambient. A different unit with a larger declared ambient needs a
separate fit check; rank equality itself is not an address adapter.

There are two invocation kinds:

| Kind | Physical input | Row action |
| --- | --- | --- |
| `MATCHED_FIELDS_OCCURRENCE` | Complete ordered list of existing distinct fields, with the actual borrowed owner for each role | Preserve fields and stock; emit full coordinate entry/return routes |
| `SINGLE_OWNER_ROW_CHILD` | One final ordinary rank-one owner's complete field | Divide into final `W` public fields, update ordinary geometry, recurse or invoke the leaf, merge every output on return |

The public `sites` map admits only the second kind to ordinary row descent.
Compiler substitution is flattened into one fixed finite word. It creates
no numerical runtime frame and consumes no stock. A finite program counter
retains static compiler contexts. Only input-dependent ordinary recursion
uses the physical continuation stack.
The source lowerer's pending set becomes empty when its last deepest-exit
batch is issued. Synchronous construction and the inverse-return service
sequence, not that empty set alone, enforce completion before the parent
fragment or owned cleanup resumes.

The binder reads these source token forms without inventing owners:

* `program-enter/return` carries the complete `matched-program` field list and
  exact role index. A source complement of rank `n` in parent rank `m` uses
  `[m-n,m)`. A deepest exit uses normalized first `n` coordinates supplied by
  its retained paid-job normalizers.
* `occurrence-enter/return` carries actual occurrence ID, lattice copy, point,
  column, enclosing rank and raw role. At column `c`, target `k*c` uses the
  first `k*c` coordinates and full unit ambient is `m*c`. The fit
  `m*c <= enclosing_rank <= N` is checked. Retained normalizers make the
  issuing job canonical before its child occurs.
* `base-axis-enter/return` contains the actual terminal ordinary token,
  physical owner, axis and enclosing rank. It routes that axis to coordinate
  zero before the unchanged rank-one `PAID` and restores it after return.
  Axis zero may have an empty route. A later axis is not free merely because
  its rank is one.

For a requested ordered list `A`, the complete permutation is `A` followed by
its increasing complement in `0..N-1`, exactly #6878's construction. The first
complete child ambient positions form its frame; the remaining positions stay
present. If the parent chart is `B`, the child chart is `B[order[i]]`. Full
parent charts and inverse swap words are compile-time descriptors, not an
input-dependent Python stack. The binder verifies complete parent restoration
on every nested return. All descriptors become fixed constants with the
template.

A block swap `(a,b)` is the selected-XOR word
`b ^= a; a ^= b; b ^= a`, applied to all `f` selected columns at fixed `rho`.
Three records implement the transposition. Reversed swaps supply the inverse
with another three records. An entry/return pair with `t_occ` entry swaps
therefore emits exactly `6*t_occ` records. Each record names two fixed block
numbers and reads runtime `f,K,rho` and the within-row start through the
protected encoded descriptor. It invokes the retained compact service and
pays its tariff. It is not a host-list permutation or an all-`K` plane sweep.

All matched fields are routed before a complete native class word executes,
so scalar contacts see common canonical coordinates. Every route is undone
before the enclosing word resumes. Whole-job binary monomial normalizers and
quadratic phases remain separate charged native services; their prices are
not replaced by the coordinate-permutation tariff. Product and completion/
splitting service endpoints retain #6878's construction. The new binder
refines the integer-compiler/elementary-axis grammar; it does not implement
every raw monomial provider.

The original source event stream remains in order, including descriptor-only
enter/return services after their routes are lowered. The separate flat
ownership replay can therefore check the original owners and LIFO borrows.
Added routing changes neither paid count, rank nor owner. Rebinding an already
routed word rejects, as do missing elementary-axis brackets.

A matched occurrence must not be row split. For example, fields `00` and `11`,
each of two one-bit rows, would be mistaken for packet `0011`. The actual
`g=2` table returns `01` and `01`. Field count, field size, total bit count and
nominal rank can agree while physical owners change. This is a counterexample
to that proposed wrong composition, not an allegation about the source.

## 6. Canonical zero padding and exact restriction

Let the complete root divisor be `S0`. The accelerated branch requires
`R0 >= S0`, alongside every layout/source guard. Pad once to
`R'=S0*ceil(R0/S0)`. Then

`R0 <= R' < R0+S0 <= 2R0`.

If `R0 < S0`, reject this branch or invoke its declared elementary fallback.
Padding to `S0` then does not retain the factor-below-two bound.
The caller establishes the valid-volume fit before invoking this wrapper;
malformed-input rejection is not assigned the successful `V0` bound.

In the common numeric encoding, a zero Gaussian record retains component
delimiters while its value bits are zero. Its physical string is not all
zeros. Let `Z` be a complete canonical zero row of length `J`. It can be
produced by a charged copy of one complete source row as shape and the owned
initializer, which maps numeric symbols to zero and preserves terminators.
Both scans have length `J`. A different producer must supply its actual cost
`T_Z(J)` and backing `S_Z(J)`. The immutable zero row is not constant-size.

`pattern_padding.py` retains the predecessor's decoder, cover test, round-up
planner, genuine-row scans and cleanup. Only the added-row writer/restrictor
changes. Padding traverses `Z` in lockstep with the complete `J` guide,
appends whole patterns after each outer prefix's genuine rows, and rewinds
both guides. Restriction requires every returned added row to equal `Z` and
copies genuine rows to a distinct output. The complete pattern is validated
even when no padding is needed. Extents, marker checks, writes, comparisons,
movement, rewinds and cleanup are actual instructions.

The endpoint premise is a **completed zero-preserving rowwise numerical map**,
with identity on row ordinals, complete controls/spectators restored, valid
extent and borrowed input/descriptor restoration. A completed linear map with
this rowwise action supplies the zero property. Local pattern checks alone
do not establish semantics: an incorrect callee could zero the genuine rows
and still pass. Rounded residuals cannot be silently deleted. Exact canonical
zero return, or a separately proved rounded restriction contract, is required.
Each selected deferred phase restricts before inverse exposure and the next
phase; this construction does not multiply padding factors over phases.
The borrowed zero pattern also returns unchanged, with its head at its
origin. Local comparisons do not prove this promise for an arbitrary callee.

## 7. Physical composition with the owned lifecycle

At a nonleaf ordinary `PAID`, the owned controller makes a charged
administrative bit copy of that actual owner's field to its distinct `BASE`
bridge. `prepare` reads the protected active descriptor and emits the child
header on the staged `BASE` tape. The controller parks all fixed payload ports,
including the complete parent header, using the delimited stack. Row work is
already blank. A finite saved PC identifies the actual caller owner.

`install` splits the bridge into the ordered public ports, copies the staged
binary header to the child descriptor origin, and invokes the required
elementary remainder service in numerical mode. The controller retires bridge
and staged header. Native tables access the runtime descriptor through a
counted read-only raw `BinaryContextPort`, distinct from coded numerical
views. Every numerical and row head returns to its local origin.

On return, `collect` first merges **all** child public outputs into the protected
bridge and retires their bodies. The controller retires other child payloads,
pops the continuation, reads its saved PC, erases the designated old owner,
and copies the preserved bridge to it. The parent's header returns from saved
bytes. Popping before output preservation would lose the child result and is
not permitted by the interface.

The row service does not implement private initialization, scalar COPY,
dirty-bank erase, numerical rounding or suspension. The owned machine does
not prove geometry merely by preserving an opaque header. Their contracts
meet at exact physical encoding, extent, origin, public field order, protected
metadata and invocation kind. All fixed scratch ports join the suspension
inventory even when blank at the boundary. No hidden host address, dynamic
saved frame object, or uncounted field-length slice is a runtime operation.

## 8. All-size local time, including guide construction

Count one emitted local read/branch, one-cell write, unit move, or fixed jump
as one step. A fixed interpreter or tape encoding changes constants only.
Let `E` be the larger of the complete incoming and produced header lengths
(root production of the potentially longer encoded `J` is also charged to
`J` below), and define

`c(N,g)=2^16*(N+g+1)`.

For row-only mode take `N=2`. A prepare/split/merge bundle and its descriptor
copies cost at most

`c(N,g)*(V+E+1)`

on the admissible success domain, excluding numerical/remainder services and
the owned bridge/continuation actions. This deliberately loose bound follows
from table-level accounting, not fixture elapsed times:

1. Fixed-schema encode, decode, copy, clear, positive validation, division and
   comparison each make a bounded number of scans. Twenty-three fields and
   forty work ports are fixed. `1024*(E+1)` per descriptor-only invocation
   covers its scans, canonicality, quotient trim and origin checks.
2. The retained converter performs `n` consecutive binary decrements. If
   `z(t)` counts low zero digits, then
   `sum_{t=1}^n z(t)=sum_{j>=1} floor(n/2^j)<n`. Rewind follows only the borrow
   chain just crossed. The exact predecessor table bound is `60n+40`, including
   copy, trim and rewind. Guides `C,Q,J,S'` cost at most `240V+160`, since
   `S'<=Q` and every extent is at most `V`. There is no full binary `Count(J)`
   scan per payload bit.
3. The `Q,S'` divisibility scan is linear in `Q`: each stock rewind is charged
   to its consumed cells. The payload loop has a fixed number of instructions
   per bit, and its `J` rewind costs `3J+O(1)` per row. Row/prefix loops and
   output rewinds are linear in `V`. `1024*(V+E+g+1)` for either split or merge
   covers those loops, guide/descriptor cleanup, role checks and frontiers.
4. Ordinary geometry performs one fixed-`N` division and at most `N-1`
   additions of `K`, plus one entry addition, on `O(E+1)` digits. The allocation
   `1024*(N+1)*(E+1)` covers these operations, temporary copies/erases and
   cutoff comparison. Finite remainder states depend on `N`, not `e`.
5. Root extent construction starts from binary `b`, doubles `a` times, and
   pays for a unary guide for `a`. Its cost is
   `O(a*ell(b)+a^2+a+ell(b)+1)`. Since `ell(b)<=b`, `a<=2^a`, and
   `a^2<=2^(a+1)`, it is `O(b*2^a+1)=O(J+1)`. Deriving `J` therefore hides no
   factor `log J` on a full-row scan, even when `log J` is polynomial in `p`.

The displayed coefficient dominates the sum, including finitely many
descriptor copies and the leaf test. Separate prepare/split/merge calls may
instead each be billed with the same generous coefficient. Template/table
compilation costs one fixed `F_T`. It is not charged to the historical raw
`10^9` allowance. All count-dependent work occurs on encoded tapes. Small
fixed `N,g` fixtures do not limit the theorem or claim a feasible materialization
of the selected astronomical word.

Pattern padding costs at most `4096V0+4096`, excluding `T_Z(J)` and the callee,
where `V0=C*R0*J`. The predecessor bound is `2048V0+2048`. Pattern validation,
reads/moves and its second guide rewind add a constant number of steps per
appended/checked bit and one full `J` scan, fitting the doubled allowance.
The hypothesis `S0<=R0` remains necessary.

Coordinate routes have a separate exact finite invoice. If binding `j` uses
`t_j` entry swaps, charge `6*t_j` selected compact-XOR services on the actual
complete field. With retained bound `C_X*v*((f*G)^tau+1)`, added routing is
the **sum** of these charges at actual field volume `v`. Raw native, monomial,
phase, scalar, elementary and owned services retain their complete bills.
Equal ranks never make value movement free.

## 9. Backing, complete global invoice, and selected implication

At a successful row invocation, decoded binary words occupy `O(E)` cells;
unary guides occupy at most `C+Q+J+S'<=4V`; prepared header occupies `O(E)`;
destination roles together occupy `V`; merger bridge occupies `V`. A generous
fresh-interval bound `128*(V+E+g+1)` includes markers, guards and temporary
words. Root padding uses at most `128*(V0+1)+S_Z(J)`, including zero-row backing.

These are fresh active-interval bounds, not claims that erasure shrinks
previous backing. For each reusable work port `i`, let `M_i` be the maximum
extent ever visited. Retained backing is pre-existing backing plus `M_i` up
to a fixed guard. Across repeated calls charge these historical maxima for
the forty fixed work ports, not the current smaller extent. Parent payloads
and headers are parked and charged by the owned lifecycle inventory. Blank
row ports still acquire physical frame delimiters, included in that lifecycle
bill. Numerical provider scratch/backing remain separate explicit terms.

A complete favorable invoice before asymptotic absorption is

`T_total <= F_T + G_root + T_Z(J) + 4096*(V0+1)`

`            + sum_{ordinary invocations nu} c(N,W)*(V_nu+E_nu+1)`

`            + T_owned + T_remainders + T_leaves + T_native_original`

`            + sum_{emitted route records j} T_compact(j)`.

The row-invocation sum includes the initial root split when that entry is
used. If the retained recurrence `T(e,U)` measures the complete incoming
ordinary packet, its `W` public fields each have volume `U/W`. Every paid
rank-one child receives one such packet, hence the source child volume
`U/W` is unchanged. An active header counts rows in each current public
field; a root preheader counts the unsplit root packet. These distinct
conventions explain the root/ordinary versions of `prepare`.

`G_root` is the actual selected descriptor/stock/cutoff/padded-count producer,
not host integer arithmetic. `T_owned` includes bridges, private lifecycles,
suspension, protected return and header restoration. Every term is implemented
here or names an explicit retained provider. Backing adds actual owned
continuation backing, numerical provider backing, root padding/zero-row
backing, and historical maxima of fixed row work. These are not all inferred
from `V` without a contract.

The frozen owned-lifecycle supplier makes `T_owned` concrete. For one ordinary
descent/return, let `S_body` be total parent body length, `C_body` total child
body length just before retirement, `L_in,L_out` the owner bridge lengths,
`E_child` staged header length, `q` fixed payload ports, and `b_PC` fixed
return-PC bits. Its exact administrative physical-action bill is

`4*S_body+5*C_body+18*L_in+13*L_out+5*E_child+38*q+27*b_PC+103`.

This excludes row callbacks and leaf/top tests, already separately listed.
Add each actual INIT at `5*D_dirty+25*n_symbols+17`, COPY addition at
`35*n_value_bits+26*n_terminators+14`, and dirty retirement at `5*L+7`.
Native work is retired before/after each service and at root cleanup using
those same actual-length charges. Each parent-top test costs 3. Native table
steps cost at most thirteen physical actions each, plus explicit final port
rewinds `2*h+3` and auxiliary retirement. Fixed control transitions add a
template-dependent multiple of event counts. These positive summands provide
the administrative invoice without assuming private contents numerically zero
or treating erased backing as deallocated.

For the favorable retained caller, complete record precision covers its
short global parameter encodings, stock fits the root row range, and header
length is `O_T(V+polylog p)`. Although `ell(J)` can be large, `ell(J)<=J<=V`.
Fixed-root precision and the root producer must justify the other descriptor
bounds. Under #6878's current-volume and compact contracts, the new linear
terms and finite sum of selected-XOR charges fit its ordinary node tariff by
enlarging a fixed coefficient. They change neither `P/W`, width recurrence,
nor exponents.

The selected deferred proof #6115 has `mu_tau<2^-94010` and
`mu_sigma<2^-47005`. Its internal tariff already includes movement, owned
storage, restoration and fewer than `N` elementary remainders. Substituting
this linear physical row interface changes finite constants and the eventual
threshold, provided the other providers meet their bills. It does not alone
establish the full physical/precision/compiler assumption, an unconditional
multiplier, or a new `kappa`.

## 10. Executed evidence and limits

The registered checker authenticates dependency bytes before import. It runs
the row tables normally and under Python `-O`, with explicit checks rather
than removable assertions. Coverage includes fixed divisor examples,
translated origins, retained blank backing, genuine coded numeric records,
non-power-of-two quotients, full output merge and role retirement. Encoded
geometry tests cover long integers, root extent, cutoff boundaries, and an
actual table mutant that omits the geometry update.

The source-route checker uses actual outputs of the frozen source lowerer
and a separate coordinate oracle. That oracle forms complements independently
and applies emitted selected XORs to GF(2) coordinate masks. It checks all
selected columns and complete controls/spectators at native boundaries.
Deleting a nonzero-axis route, omitting an inverse XOR, or changing an actual
owner rejects. The tested raw unit is a compiler-control fixture with private
lifetimes, not a proposed Gaussian identity. Its native numerical endpoint is
opaque in the placement test.

The joined replay uses the exact frozen owned machine and real row service
on two source-generated words. Its width-six structural case makes 72 ordinary
children and 512 leaves per run through two stock divisions and includes
compiler-private borrows. Its width-one rank-two case exercises the encoded
width path `6 -> 3`, child remainder/start update and actual `f<=t` leaf test
through a physical continuation. That fixture checks descriptor arithmetic,
not the selected compact-domain parameter inequalities. Both run twice on
retained backing and compare every productive output to a separate value
interpreter. Native/coordinate services are identity fixtures, with a literal
cyclic value-bit leaf and counted raw-context read in the remainder fixture.
The join establishes physical ABI composition; the separate route oracle
checks coordinate meaning. No Gaussian or precision admission is inferred.

Counterexamples exercise the actual row table on an incorrect matched-field
composition and exhausted repeated stock. They explain why invocation kind,
owner identity and path-product divisibility are required; they do not refute
a retained theorem. Independently written reviewer interpreters add nested-row
and geometry evidence. Their exact executed scripts/logs, when included, are
independent checks of this scoped implication, not full theorem acceptance.

## Open next questions

1. Bind the selected global phase descriptor/stock/cutoff producer to this
   twenty-three-field ABI, including padded-count staging, and substitute its
   actual all-size charge for `G_root`.
2. Supply retained compact selected-XOR, raw monomial, native and elementary
   remainder/leaf providers through the read-only context port, including
   exact frontier restoration and full precision.
3. Combine dispatcher and owned-lifecycle invoices with those providers and
   the selected common-grid proof. This may strengthen the concrete machine
   implication while retaining analytic recovery and every other unproved
   selected hypothesis explicitly.
