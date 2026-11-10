# Source-bound physical lifecycle for the retained complex compiler

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.

## 1. Claim, prior coverage and exact boundary

This package constructs a physical lifecycle refinement of the **current
selected raw word and the complete finite compiler grammar**. Its new content
is the binding between actual source events and an executable sequential-tape
controller: current private lifetimes, chronological product substitutions,
compiler matches on borrowed private fields, complete smaller-program batches,
initialization, arithmetic COPY, dirty retirement, suspended parent contents,
saved finite return state, and output installation before parent resumption.
The proof is quantified over all legal runtime sizes for every fixed finite
template produced by that construction. Its force is the induction below;
the executed small instances are discriminating implementation evidence.

The generic allocation argument already exists in
[#5814](https://github.com/CrocSwap/integer-mult-bounds/pull/5814), especially
`selected-owned-dispatch/ALLOCATION-THEOREM.md`, `FRESH-NAMES.md` and
`BINDING-STATUS.md`. That work includes coded logical blanks, the output bridge,
COPY as addition, and the distinction between current volume and retained
backing. Those ideas are credited dependencies, not new discoveries here.
The present contribution instantiates them with the current source word and a
literal controller, and supplies a source-driven lowerer which executes the
complete lockstep compiler rather than replacing large subprograms by an
interface check.

All five assumptions in selected #6030 remain in the selected record. A native
Gaussian implementation and its numerical error bound are not supplied here.
A physical lifecycle theorem relative to explicit native and row services is
different from a complete multiplication theorem.

`SOURCES.json` pins canonical inputs at
`7c49fe32c55de02c2c873655c804b16e4c3fef0a` by Git blob and SHA256:

| Source | Use in this result |
| --- | --- |
| #6030 `p104-helper470-twin-rung-removal/WORD.json.gz` | Every current local operand, chart, INIT, COPY, MOVE and CLEAR |
| `p104-productive-controller/CONTROLLER.json` | Actual 18 LOCAL sites, 15 copied queries, boundaries, IDLE jobs and productive roles |
| #5443 `lockstep-completion-pass/executor.py` | Unchanged Pascal matching, replication, complete source/complement batches, exits and ownership stack |
| `p7-TENSOR.md` and `FINITE-PRECOMPILATION.md` | Chronological product, completion/splitting and finite compiler semantics |
| #5356 `delimited-continuation-stack/stack.py` | Unchanged local-read/write/unit-move continuation implementation |
| #5814 allocation, fresh-name and binding proofs | Prior allocator and historical source-boundary analysis |

Byte-identical proof exports in `vendor/` have public commit and Git/SHA256
pins in `DEPENDENCIES.json`: #6878 at
`41febf890fbbb852c6059d4c0cc8c593ae9dfa5c` supplies occurrence geometry,
complements, inverse routes and the complete-row ABI; #6900 at
`c46339035fccd571effb48434d80f572e20f1092` supplies the current ideal caller
grid; #6901 at `4c7a4f00f09665276e145ac2cc1d12f8b8f9a7ac` supplies
compiler-wide ideal dyadic precision and headroom under its endpoint premises.
The verifier authenticates these proof bytes, without rerunning their whole
dependency suites. The all-column selected algebra of #6890 and the newer
#6902/#6914 owned-rise audit are not repeated or claimed as new results.

### Relative theorem

Fix the current raw unit and a finite sequence of the specified products,
completion and splitting operations which produces a separated rule: maximum
paid rank is smaller than minimum target rank. Fix a legal finite integer
compiler rank N. Run `source_ir.lower` on authenticated #5443, without partial
copies or non-base blackbox fallback. Let the resulting fixed template have
productive width w, private inventory o and finite program P. All construction
work precedes varying runtime input size.

Assume these service conditions, which do **not** assume private initialization,
arithmetic COPY, dirty erasure, or preservation of suspended parent banks:

1. **Full-field and arithmetic ABI.** Numerical fields are complete common-format
   arrays, with common fixed-point scale and signed component width. Native and
   geometry services return the exact declared array extent, including arbitrary
   spectators, at the origin. Actual additions fit the signed width. The frontier
   is exactly the declared number of complete records: no trailing coded logical
   blanks or native scratch remain in a numerical field. Descriptors are separate
   contiguous raw binary payloads. The ideal format of #6900/#6901 is compatible
   when their premises hold; it does not certify an approximate native service.
2. **Fixed native tables.** Each SERVICE and elementary PAID leaf has a fixed
   finite transition table with its source endpoint, time and local backing
   bound. Its accessible ports are exactly its event fields, fixed auxiliary
   ports and explicitly borrowed binary context ports. Tables cannot access
   another field or an ancestor segment. The full-field conjugations of #6878
   are charged services, not free relabelings.
3. **Ordinary child services.** A terminating encoded stopping test and
   `prepare/install/collect` implement actual ordinary recursion at the
   supplied ordered PAID site. `prepare` preserves parent payloads and stages
   a complete child descriptor; `install` distributes a complete owner bridge
   into all w productive fields and installs that descriptor; `collect`
   reconstructs the owner from **all** returned productive fields. They use
   fixed supplied ports, return canonical heads and format, and have explicit
   time/backing bounds. Rank reduction, elementary remainders, placement,
   whole-row stock and numerical leaf cutoff belong to this interface.
   A stock-depth fixture is not their proof.
4. **Imported finite source theorem.** The named compiler has its stated
   ordered matching, integral complete batches, strict smaller-rank substitutions
   and semantic endpoints. This is an imported theorem, not an assertion that
   finite testing proves it. The added lifecycle annotation is proved below
   by structural induction over that exact construction.

Then `machine.Controller` refines the emitted program on every legal runtime
input and every finite current dirty private body. INIT produces canonical
zero; COPY adds into the actual destination; CLEAR erases the complete physical
body. A child cannot change a parked parent field, descriptor or continuation.
Every output is captured before retirement; the correct occupied parent owner
is replaced; all other parent words and heads return unchanged. The number of
physical tapes is fixed by P and its service inventories, independently of
runtime size and recursion depth.

Sections 6–7 give a positive action invoice and a coordinatewise retained
backing bound, including dirty contents and auxiliary high-water marks. Under
the stated current-volume bounds and whole-row contraction
`V_child=V_parent/w`, w>=2, they imply `K0+C_P V_root` retained backing and
linear lifecycle work per ordinary node, with finite template-dependent
constants. Arbitrarily occupied dirty input is not silently absorbed into K0.

## 2. Actual raw lifetimes and the finite wrapper grammar

`current_local` reads every instruction of the authenticated word. It checks
the chart of every accessed field, exact Boolean ownership flags on MOVE,
equal charts at scalar contacts, positive MOVE rank from the source chart
dimension difference, and complete final charts. Every private access lies
between the actual INIT and CLEAR. Each current COPY has coefficient one and
an INIT destination unchanged by intervening operations. The machine still
implements it by actual addition; this check does not license an overwrite.

The exact local word has 770 public fields, 29 private names, 31 private
lifetimes, peak logical ownership 13, and 23 COPY sites. The lowering uses a
separate conservative 29-name inventory at each actual LOCAL occurrence; it
does not reuse an ancestor's live bank because the local peak is smaller.

`current_caller` maps the selected 104 local ports and their partners to the
32 main factors. It allocates distinct sets of 562 local helpers and 29 private
names for each of 18 LOCAL sites, retaining every caller boundary and physical
event. Each QUERY_SHEAR gets the literal sequence

`INIT z; COPY(z,x); query-in; PAID(z); query-out; query-add(y,z); CLEAR z`.

Its 104 query banks are reused only after CLEAR. There are 15 query sites.
Actual field maps are injective; productive inputs are not copied to satisfy
another productive role. Normalizers are explicit SERVICE events, including
the re-emitted whole-job canonicalizers of #6878.

The derived caller has 13,444 productive fields, 626 private names, 2,118
private lifetimes, 1,974 arithmetic COPYs and 66,834 paid jobs. Its annotated
raw word has 642,410 events: 569,366 SERVICE, 66,834 PAID, 2,118 INIT,
2,118 CLEAR and 1,974 COPY. Both complete paid and target histograms are
compared with selected `RESULT.json`, rather than inferred from these totals.
Added services incur positive ordinary work; this package does not claim
that they fit the historical numerical raw `10^9` allowance.

For a chronological product U*V, each V role j has a separate U copy. Its
private names are `('left',j,name)`. At U's chronological paid position ell,
the distinct current owners, in V-role order, become V's productive fields;
V's private names are `('right',ell,name)`. A V input can be a live private
field of U: it is borrowed, not allocated, copied or cleared by V. All V events
and inverse normalizers finish before U resumes. Left and right path tags are
disjoint. Induction on event position preserves each INIT/use/CLEAR lifetime,
including later reuse of a private label in a disjoint lifetime.

Let B_U,O_U,P_U count productive fields, private names and paid events, and
I_U,C_U,A_U,S_U count INIT, CLEAR, COPY and SERVICE. The actual loops give

\[
B_{UV}=B_UB_V,\quad P_{UV}=P_UP_V,\quad O_{UV}=B_VO_U+P_UO_V,
\]

\[
X_{UV}=B_VX_U+P_UX_V\quad(X=I,C,A),
\]

\[
S_{UV}=B_VS_U+P_US_V+2B_UB_V+2P_UB_V.
\]

The final terms count charged complete-field entry/return services. The
verifier checks this full bill on a product with private owners on both sides.
These equalities define every fixed finite product power without requiring
materialization of the selected 1,024-fold product.

Completion appends the source job on [K,L) to a field with target K<L,
retaining whole-job canonicalizers around the complete old word. Splitting
replaces rank R by consecutive pieces of size at most J, with entry and inverse
return around every piece. Original normalizers remain outside the replacement.
No new private bank appears. If c fields are completed and p' is the sum of
the ceiling counts of pieces, INIT/CLEAR/COPY counts stay fixed and SERVICE
increases by 2c+2p'. Every piece keeps its actual owner. The executed fixture
contains a nonleading split piece and a genuine completion job.

## 3. Refinement of the actual integer compiler

`lower` supplies the exact roles and ordered (rank,owner) rounds to the
authenticated `Rule`. It reuses `Compiler.plan`, `compile`, `uniform`,
`run_class`, Pascal buckets and source order unchanged. With the source's
`owned_policy='unit'`, every static owned field is `('own',g,name)`, where g
is the fresh source unit identifier. It gets one fixed physical port. Distinct
unit occurrences never share a private bank just because their depths agree.

| Source boundary | Added event and invariant |
| --- | --- |
| `push(field,(g,role),expected)` | Complete-field occurrence entry on that exact field; retain g, role, copy, Pascal point, column and program rank |
| Before the next child/exit round | Emit the entire preceding nonpaid fragment for every unit, with its full field map |
| `sub(n,fields,tops)` | Entry for the exact ordered distinct fields, complete smaller program, inverse returns |
| Elementary n<m | `base-axis-enter`, rank-one PAID, `base-axis-return` for each actual axis and field |
| After all deepest exit batches return | Final nonpaid fragment before releasing private names |
| `pop(field,(g,role))` | Matching full-field inverse return before the source permission pop |

The predecessor executor can replace large subprograms by an interface check
for an audit budget, or execute only some replicas. This lowerer removes those
shortcuts: `copies` must be `None`; every non-base `sub` has its exact compiled
width and expands recursively. Only the elementary rank base makes rank-one
leaves. The source budget does not gate this override. Python recursion and
construction records are finite template construction, not runtime storage.

Each scalar fragment is emitted only after all productive and private fields
of the class are matched. Every ADD therefore receives its actual two complete
fields in the common occurrence order. Replication can split a deepest exit
round into several complete batches. A static pending set groups the batches; synchronous source construction
calls prevent advancing the parent fragment or releasing its banks until the
last batch and its inverse services have returned. The set becomes empty when
the last batch is issued, before that synchronous call returns.
That construction record becomes a fixed sequence of program counters.

For the proof, induct on the source's strict smaller-rank calls, then on the
finite class tree and chronological rounds. A fresh class receives injective
source fields or the exact live fields handed by issuers; its private ports
are fresh. The nonpaid fragment uses only these bindings, with every private
access in a lifetime checked by `Unit.check`. While a child runs, the parent
fragment is not emitted. A live private owner can thus be borrowed without
being reinitialized or cleared. The child induction restores full fields and
orders. The next parent fragment has its previous permission and shape. The
final fragment closes all actual lifetimes before source release. The source
LIFO returns give each actual field back to the issuer named by the matching.

This proves the annotation property for every finite source instance, under
the imported matching/termination theorem. `check_flat_ownership` separately
replays the emitted word without calling the Compiler, tracking lifetime owners
and nested occurrence, program and base-axis scopes. A parent cannot resume
through an outstanding borrow; only the actual owner clears an unborrowed
private field. This checker is extra evidence, not the universal argument.

Only a rank-one PAID site makes an ordinary runtime recursive call on one
owner. A compiler `sub` already has its complete ordered matched-field list.
It consumes neither another row divisor nor another runtime bank frame.
Products, completions and compiler substitutions are inside the fixed program.
Their private names increase the template constant o; they allocate no new
physical tapes at runtime.

## 4. Geometry is an explicit service obligation

Changing supports inside an unchanged scalar word would not be justified.
The #6878 construction instead conjugates each **complete field** into the
common occurrence order and inverse-routes it on return. For ordered support
A its extension lists A followed by the increasing ambient complement. Every
spectator remains present, without a zero assumption. An entry/return pair
costs at most 6(N-1) selected-block movement records at that occurrence scale,
besides native monomial, scalar, descriptor and row work. Movements act at
the chosen bit plane rho; applying every bit plane requires its actual calls.

The IR retains the needed source information at each boundary:

* `occurrence-enter/return` identifies the actual field, unit, role, Pascal
  point, column c and containing program. Full unit ambient satisfies
  m*c<=n, and the matched target has its source rank k*c.
* `program-enter/return` retains the ordered actual field list, source
  complement or deepest-exit tag, and exact rank. A source complement uses
  [s,n_parent), before the source job on [0,s). An exit uses its actual ordered
  request, the smaller uniform program and the full complement. Return
  services are emitted in reverse field order.
* `base-axis-enter/return` retains the axis and base rank around every
  elementary rank-one PAID. Ordinary row installation may use a canonical
  prefix only after the requested axis is placed there and restored afterward.
* Raw MOVE, LOCAL, QUERY, IDLE and whole-job normalizers, product transposes,
  completed targets and split pieces remain explicit source-tagged services.
  None is an additional row split.

The finite source path determines the fixed movement recipe. Runtime scale,
rank/placement values and rho are read from explicit binary context ports,
not a hidden Python closure. Context is read-only and its head is normalized
on return. Additional mutable scratch uses fixed `primitive_work` ports,
included in the physical inventory and each continuation, and retired before
and after the table.

This package binds the positions and operands of these services and proves
their lifecycle. It does not implement the charged compact selected-bit
movement primitives or numerical native endpoints. Their table supplier must
still meet the declared geometry, full-format return and tariff. A codec or
head convention of an older native implementation is not automatically this
ABI; an adapter and its cost must be supplied if they differ.

## 5. Literal initialization, addition and physical continuation

### Encoded fields and native ports

The physical alphabet is 0,1,LEFT=2,SEP=3,END=4,BASE=5,BLANK=6.
Every occupied payload body is a contiguous string of physical 0/1 cells,
preceded by its current LEFT marker. Physical BLANK terminates that body.
A logical symbol in 0..6 is coded by three physical bits; the logical blank
is 4, encoded 100. It therefore cannot terminate a physical body. Native
rightward motion at an unwritten frontier first materializes code 100, so it
cannot jump over an unrepresented hole. Left motion rejects at the current
origin and cannot access the parked parent. Code alignment is invariant.

A signed component is a little-endian two's-complement word followed by logical
COMPONENT=2, encoded 010. A complex record has two components. A numerical
zero row consequently contains separator codes; it is **not** a string of
physical zero bits. At a fixed fractional scale this representation is a
common dyadic grid. #6901's ideal choice F=p+D and signed width
p+h+2D+3 can be encoded this way under its assumptions. This package additionally
requires actual arithmetic headroom and a provider's canonical return format.

`CodedPort` is used for numerical fields and native auxiliaries. A separate
`BinaryContextPort` exposes a raw binary descriptor: its frontier read returns
physical BLANK=6, not logical blank4. Writes and movement beyond either its
origin or frontier reject. The table's port order is event fields, then
`primitive_work`, then `primitive_context`. The last group must be protected
descriptor ports disjoint from event and scratch ports. They are included
in the payload inventory, so a single physical stack preserves them too.

`execute_table` accepts only finite branch/write/move/goto/halt/reject rows.
It cannot call a Python numerical function or inspect a tape address. After
the table it rewinds every bound port. Each table must return numerical fields
to the declared full-record extent; trimming an extended numerical tail is
part of that table's separately charged return contract. Native scratch is
retired by the controller even when nonzero. Two-sided native machines need
an explicit translation to one-sided ports, with its inventory and tariff;
the present code does not silently assume that adaptation.

### INIT, COPY and CLEAR

`initialize(target,shape)` first retires every old byte of target, including
coded logical blanks, then scans the complete format of productive field0.
It writes zero for each value bit and preserves every component separator.
All numerical fields have that same complete shape at a program boundary;
native services do not change the guide's declared format. The guide's data
and head are preserved. Every private name is initialized before access.

`copy_as_add(target,source)` scans equal complete component boundaries and
does finite carry addition into the **actual destination**. It retains only
carry and previous sign bits. At a terminator it resets carry and rejects
equal-sign overflow. It thus computes exact signed addition whenever the
result fits. Existing destination residue is included, even if the ideal
source word called that destination zero. It does not assign a host copy.

`retire` scans to the physical frontier, writes BLANK on every occupied cell,
and returns to the local origin. It is independent of the numerical value.
Numerical zeroing does not substitute for retirement. Old high-water backing
remains reserved after retirement; no space claim treats it as deallocated.

### One physical stack, output before pop

There are q fixed payload tapes: all productive and static private fields,
row descriptors, and every row/native auxiliary. Four additional tapes hold
the stack control, the active finite-PC descriptor, the owner bridge and the
staged child header. The last two are reused at every depth. The bridge and
header are not unrecorded per-depth arrays.

At a non-leaf PAID site the controller performs this sequence:

1. Copy the actual complete owner bytes into the empty bridge, without changing
   the owner. Run `prepare` to stage the child's complete binary descriptor.
2. Write the fixed-width binary PC of the following instruction. The source
   site and its actual owner are recoverable from this finite PC.
3. Run the inherited `Stack.push` on **all** q payload ports. It scans their
   current bodies, leaves them intact, and installs a child LEFT delimiter at
   each actual frontier. Every child head is at a new empty local origin.
4. Run `install` into all productive ports and the new descriptor. Retire the
   bridge and staged header. Begin the same fixed program at PC0.

At child RET, `collect` first builds the complete returned owner in the bridge.
The controller then retires all q child bodies, including every private bank,
descriptor and dirty auxiliary. Only now does it call `Stack.pop`, which removes
the child delimiters and restores every parent payload head and the saved PC.
It consumes that PC, locates the exact parent owner from its preceding PAID
instruction, retires the owner's old body, installs the bridge output, and
retires the bridge. The next fixed instruction is the matching source
continuation, including its inverse coordinate route where applicable.

The stack does not save host pointers or origins. It finds current delimiters
and the previous control top by local scans. The source implementation's
returned sizes/heads and hardware counters are observers; the controller
ignores them. Removing these observations changes no branch or tape action.
The runtime PC and its bit loop have bounds fixed by the template and can be
expanded into finite control. There is no host recursion in `Controller.run`.
An observation callback used by the verifier is absent from the machine claim.

Induct on the terminating ordinary recursion tree. At a leaf, the supplied
finite table has its stated endpoint; INIT/COPY/CLEAR have the proved meanings.
At an internal call, the delimiter isolates every child from all parent
segments. The row service and induction hypothesis provide all child outputs.
Capturing them before retirement preserves them independently of pop. Pop
restores all parents, then only the actual issuing owner is replaced. Thus the
next source instruction receives exactly the required data and descriptor.
At the root, unprotected private and auxiliary payloads are retired; productive
outputs and protected borrowed descriptors remain. This proves the physical
part of the relative theorem without assuming erased intermediate values.

## 6. Complete positive time invoice

Count one local physical read, write or unit move as one action. The following
are exact for `machine.py` and the pinned Stack, with canonical entry heads.
Lengths refer to physical occupied binary bytes, not ideal nonzero values.

| Routine | Exact actions |
| --- | --- |
| Rewind a head at offset h to its local origin | 2h+3 |
| Transfer L bytes into an empty marked target | 8L+14 |
| Retire L bytes | 5L+7 |
| INIT, old dirty length D and n logical format symbols | 5D+25n+17 |
| COPY addition with B value bits and C component terminators | 35B+26C+14 |
| Stack.push, total parent length S, q ports, fixed PC width b | 2S+10q+7b+11 |
| Stack.pop under the same conditions | 2S+21q+11b+28 |
| Write / consume the active saved PC | 4b+4 / 5b+4 |
| Test for a parent at a canonical control top | 3 |

For example, the signed-addition bit scan performs its source and target
three-bit reads and target rewrite; delimiter processing checks/reset carry.
Rewinds give the final affine terms. These counts are derived from literal
loops, not timing extrapolations. The verifier measures translated-origin
cases, and the root reviewer separately derived the scan and stack bills.

Let S be the sum of parent body lengths, C the sum of child body lengths just
before their retirement, L_in and L_out the input/output owner lengths, and H
the staged child header length. Here H is a header byte count, not the paper's
control-field parameter dG. Descend plus ascend, excluding the three row
service calls and separate leaf/top tests, has exact administrative cost

\[
\boxed{4S+5C+18L_{in}+13L_{out}+5H+38q+27b+103.}
\]

This includes both bridge copies, bridge/header retirement, all child
retirement, parent-owner replacement, PC production/consumption and both
stack operations. It allows unequal input/output physical lengths for the
administrative identity, although the numerical row ABI returns the same
complete declared shape. The nine boundary fixtures subtract measured row
service actions and recover this exact bill, independently of ancestor prefix
length. No child-time, numerical-value or source-error term is used to pay it.

The total execution invoice is the sum of these administrative costs over
ordinary calls; every actual INIT, COPY and CLEAR scan; every `prepare`,
`install`, `collect` and encoded leaf test; every native/geometry/elementary
kernel table; every primitive auxiliary pre/post retirement; root cleanup;
and initial/final conversion or loading. All source adapters remain SERVICE
costs. Fixed finite-control transitions contribute an additional fixed
constant per emitted instruction and table transition in a standard TM model.

A coded native read costs at most 10 physical actions, write 9, and unit
movement at most 13, including materialized logical blanks. Read-only binary
context reads cost 1 and legal unit moves at most 2. Thus a finite table using
t such primitive steps costs at most 13t, plus each bound port's final rewind
2h+3 and the explicit auxiliary retirements. This constant-factor simulation
does not establish that a particular native table has the required tariff.

If each current body, descriptor and service local peak is at most a fixed
template constant times current complete-field volume V, then each lifecycle
and boundary charge is O_P(V). A fixed program has finitely many events, so
its total nonrecursive lifecycle charge at one ordinary node is O_P(V), in
addition to its explicit primitive tariff. This is absorbable only where the
retained node tariff already pays a full scan. We do not certify a new raw
numerical allowance or silently discard geometry constants.

Occupied dirty input of length D costs its actual 5D term. A very large warm
blank capacity costs no traversal merely because it exists. Conversely, K0
alone cannot justify an O(V) time bound for arbitrarily large **occupied**
private bodies. The exact invoice applies without a small-D assumption; the
linear-time corollary requires the stated current-volume entry bound.

## 7. Retained backing, including erased and visited cells

Use absolute physical extents, including every previously reserved or visited
cell. Let K_i be entry backing of physical tape i, and b_i its current root
payload origin. For a payload port at ordinary node v, let e_{v,i} bound the
largest locally visited offset, expressed as a length from that node's origin.
This includes native work, descriptor scratch, blanks subsequently erased and
the first visited frontier cell. At a call boundary let s_{v,i} be its actual
current parent-body length. The child origin on that same tape is exactly

\[
b_{child,i}=b_{v,i}+s_{v,i}+1,
\]

because push writes one LEFT delimiter at the actual parent frontier. Define
the prospective extent recursively by

\[
E_{v,i}=\max\bigl(e_{v,i},
 \max_{v\to u}(s_{v,i}+1+E_{u,i})\bigr).
\]

This is a resource proof, not a runtime address computation. A sequential
child reuses the same suffix, so siblings enter a maximum rather than a sum.
On every payload tape final retained backing is bounded coordinatewise by
`max(K_i,b_i+E_root,i)`. Even if e and s bounds are conservative, this remains
valid. Using `max(sum K_i, sum E_i)` instead is generally false: one tape can
retain warm capacity while another extends cold backing.

Control frames have length exactly 2q+b+3 when all payload heads are normalized.
Thus control backing is bounded by the maximum live depth times that length,
plus its entry prefix and visited frontier. The active PC tape needs b bits
and its frontier. The shared bridge needs the largest complete owner or output
encountered; the shared staged-header tape needs the largest staged descriptor.
Their capacities are maxima across the execution, not per-depth allocations.
Include their coordinatewise maxima with K_i too. Parent descriptors and
all fixed row/native work tapes are already among the q payload ports.

Suppose each node's local peaks, its current cut bodies, descriptor/auxiliary
sizes, and the finitely many marker/PC costs are bounded by C_P V_v, with
V_v>=1. Suppose each actual ordinary whole-row child satisfies
V_u=V_v/w and w>=2, using the complete unchanged within-row format. Along any
active path,

\[
\sum_j V_j\leq V_{root}\sum_{j\geq0}w^{-j}
=\frac{V_{root}}{1-1/w}.
\]

Summing the coordinatewise inequalities and adding the fixed shared ports
gives `K0+C'_P V_root`, where K0=sum_i K_i. Deleted dirty values and cleared
native work remain included through their local peaks. There is no sum over
all completed siblings, no depth-dependent tape inventory, and no separate
unpriced descriptor stack. Without the local service bound, or without volume
contraction, retain the explicit path/coordinate formula; do not assert the
linear corollary. In particular, w=1 requires its own argument.

The checker computes per-port prospective extents from the fixed source word,
canonical field lengths and legal call cuts **before** execution. It then
compares every individual physical tape's retained capacity. A separate
observer tracks all reads, writes and unit moves, adding the visited frontier
even where the inherited simulator has not extended its written-cell list.
Both written backing and visited backing are recorded. Repeated invocations
must reuse their retained suffixes exactly, and translated protected prefixes
must be preserved. These are finite resource tests of the formula, not a
replacement for the path induction.

## 8. What is closed, what remains, and how to check it

The proved implication replaces an abstract compiler-owned allocation step
with a source-bound executable implementation: every current private lifetime
and borrowed owner has an actual port; every source occurrence has explicit
entry/return; initialization and COPY use the full numerical format; dirty
contents are physically retired; complete ordinary child outputs survive pop;
and all continuation, descriptor, scratch and historical backing is charged.
There is no remaining allocator oracle inside this implementation.

The result remains relative to the finite compiler source theorem and to the
explicit native/geometry/ordinary-row services. It does not provide the compact
movement tables, exact or rounded Gaussian tables, source-specific numerical
stopping/stock producer, global numerical error analysis, BIT admission, or
analytic recovery. A row implementation must treat the numerical zero-row
pattern canonically, preserve complete within-row fields and spectators,
divide only at actual ordinary children, handle decreasing rank and remainders,
and charge its padding and descriptor arithmetic. Those are concrete interface
obligations, rather than silently successful callbacks in the theorem.

The current selected constants remain power1024, cutoff16, floor17, ambient145,
and compiler N=2^65807000000000. The final template is defined constructively
but is not materialized here. Its nonmaterialization is not itself a gap in
an existence proof. Conversely, no finite fixture is described as executing
that template or removing one of the five selected assumptions.

Run the package verifier in normal and optimized Python. It authenticates all
source bytes before parsing or executing and uses captured-source `compile`,
not a stale bytecode cache. It checks current complete profiles, raw lifetimes,
product and completion/splitting invoices, complete small compiler expansions,
independent flat ownership, literal physical replays, exact boundary action
bills, signed arithmetic, raw context access and retained backing. The current
raw word is executed twice with distinguishing synthetic native tables; all
2,118 private lifetimes are physically cleared on each invocation. That fixture
is not a numerical Gaussian replay. An independent value-level oracle uses
host recursion only in the checker, never in the controller.

Adverse controls include borrowed CLEAR, a changed COPY coefficient, mistyped
ownership flag, omitted INIT, early parent CLEAR, one bank per depth, missing
occurrence/program/base-axis returns, an ancestor probe, COPY overwrite losing
actual residue, numerical zero substituted for physical retirement, child
output discarded before collection, wrong return PC, a logical blank collapsed
to physical blank, source drift, and illegal binary context operations. Tests
are rejection evidence for these specific faults. No proof-kernel acceptance
or independent human approval is claimed.

Credit the predecessor authors: Ali Romman's continuation and P104 work;
JoyboyBrian's query/owned-interface work; Mason Hale's #5814 allocation binding;
zxv's backing and chronological-product analysis; Jacob Alan Sussman's integer
compiler; Mark / Matarener's lockstep implementation; Douglas Colkitt's compact
layout and retained framework; DreamingOfClouds and the selected local-word
lineage; Chris R / Clear1nsight's whole-job/contact audit; and the precision
contributors including Ross Richardson. The #6878/#6900/#6901 source exports
retain their original notices. This new source refinement, implementation,
proof and checks were prepared for @CubeJerry with substantial OpenAI
assistance. Concurrent root review is separate AI-assisted review, not a human
or formal theorem certification.
