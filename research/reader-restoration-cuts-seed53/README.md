# Restoration cuts that allow workspace readers

This recursive-interface construction removes four of five restorations in a
batch where every child reads the dirty workspace. It also provides an exact
planner for the cheapest checkpoint-correct partition of a fixed diagonal
batch. No supplier, paid moment, runtime improvement or new kappa is claimed.

The counterexample corrects the stated necessity of read-free children in
[PR1155](https://github.com/CrocSwap/integer-mult-bounds/pull/1155). Its retained
verifier reproduces both its original certificate and this new example. The
original failing-reader example remains valid; it does not establish necessity.
The added value is a checked applicability correction and a usable cut planner,
not a claim that linear cancellation or dynamic programming is new.

## Five readers, one restoration

Use scalar state D,W with arbitrary initial values. Each child first performs
`D += b_i W`, then `W = -W`, with reader coefficients

```
b = [1, 1, 1, -1, 1].
```

Eager execution restores W after every child. Deferred execution lets it drift
until the batch ends. In both cases D ends at `D_initial + 3 W_initial`, and
one final negation restores deferred W. All five readers are nonzero, including
readers of the changed workspace. The restoration bill is five negations versus
one. With `D_initial=11,W_initial=7`, both end at `(32,7)`.

After child two, eager D is 25 and deferred D is 11. Requiring an observation
and restoration there makes the optimal bill five again. Output timing is part
of the contract. This is not safe substitution under arbitrary prefix observers.

## Reproduce and use

Python 3.11 or newer, standard library only, from the repository root:

```sh
rtk proxy python3 -I -O -B research/reader-restoration-cuts-seed53/verify.py
rtk proxy python3 -I -O -B research/reader-restoration-cuts-seed53/test_package.py
rtk proxy python3 -I -B research/reader-restoration-cuts-seed53/planner.py research/reader-restoration-cuts-seed53/fixture.json
```

The verifier prints
`PASS_READER_RESTORATION_CUTS restoration=5->1 forced_cut=5 exhaustive=2851 seeded=160`.
The package test reports relocation, canonical regeneration and four rejected
corruptions. The planner emits cost 1, cuts `[5]` and a final negation of coordinate
zero. Adding `"required": [2]` to a copy of the fixture yields cost 5 and all five
cuts. Coordinates are zero based; cuts count completed children, from one to r.

Planner input contains `children`, each with equally sized integer `reader` and
`signs` arrays, and positive integer `prices` for complete coordinate negations.
Signs must be -1 or 1. Optional `overhead` is a nonnegative complete per-nonempty-
restoration dispatch charge. `required` lists mandatory cuts. An empty batch is
valid. Zero reader coefficients represent workspace-independent data work;
such independent increments can be added unchanged outside this model.

## Exact criterion and proof

Let D,W have N coordinates over a characteristic-zero field. Child i applies

```
D <- D + diag(b_i) W
W <- diag(g_i) W,             g_ij in {-1,1}.
```

The child restores its private work and preserves all other data. Source and
target do not alias. There are no intermediate observers except declared cuts,
no hidden state, no rounding and no other dependence on W or old D. The eager
comparator restores W after each child. The planner accepts integer readers;
the proof itself also holds for rational or complex readers.

For an interval [a,b), define `p_a=1` componentwise and
`p_(i+1)=g_i p_i`. Just before child i the deferred workspace is `p_i W_entry`.
The deferred-minus-eager data increment is therefore

```
diag(E_ab) W_entry,      E_ab = sum_(i=a)^(b-1) b_i (p_i - 1).
```

The interval is correct for every input exactly when every coordinate of E_ab
is zero. Sufficiency follows by substitution. For necessity, a nonzero entry
is detected by its workspace basis vector. Applying the final diagonal sign
`p_b` restores W since each sign is its own inverse. Read-free intervals set
every b_i to zero, but they are only one sufficient case. The example above
has two nonzero residual terms that cancel.

For general linear readers B_i and invertible workspace maps G_i the same
calculation gives `sum B_i(P_i-I)=0`, with ordered prefixes P_i. This is context
for the correction, not an implemented general-matrix optimizer. Unlike earlier
dirty-response transport, this tool changes no reader and moves no supplier gate.

## Restricted optimum

Every selected cut must reproduce eager D and W. This requirement applies even
to additional cuts introduced by the planner. A legal interval cannot cross a
mandatory cut. Its price is the sum of the supplied prices of the coordinates
with final sign -1, plus overhead if that set is nonempty. Identity restoration
emits no command and costs zero under this explicit model.

Set `F(0)=0`. For b from one through r, minimize

```
F(b) = min_(legal [a,b)) F(a) + restore_price(a,b).
```

Every legal partition has a final interval and its preceding prefix is a legal
partition. Conversely, adjoining a legal interval to a correct prefix gives a
correct partition. Induction proves the recurrence gives the minimum in this
class. Ties use fewer segments, then lexicographic cuts. Single-child intervals
are always correct, so an input satisfying the schema always has a plan.

This does not optimize schedules whose errors persist across an inserted cut
and cancel later, reordering, changed child implementations, non-diagonal
restorations, or arbitrary reversible programs. The literal-column checker
enumerates partitions independently and tests equality at every proposed cut.

The implementation computes residuals and prefixes with O(r^2 N) integer
arithmetic operations, plus O(r^3) worst-case required-cut tests and tuple
copying/tie comparisons. Storage is O(r^2 N + r^2), including candidate masks
and saved cut tuples. Integer bit costs are additional. No precomputed plan or
descriptor is assumed free.

## Complete node bill and precision

Let C_i be the complete cost of child i under the deferred interface, including
its recursive descendants, source/coefficient accesses, private work and its
restoration, data readout, workspace sign change, routing and frame adapters.
The same fixed upper price and common precision must be valid for every allowed
incoming state and for both eager and deferred schedules. Children cannot have
unpriced dependence on the current workspace value.

For node v, the complete conditional recurrence is

```
T_v = admission_v + preparation_v + planning_v + program_storage_and_reads_v
    + sum_i T_child_i + sum_i local_child_work_i
    + sum_(emitted restorations h) Restore_v(h)
    + batch_control_v + routing_or_frame_work_not_in_children_v.
```

Here `T_child_i + local_child_work_i = C_i`. Restore_v must include reads,
negations, writes, mask/descriptor access, dispatch, head return and any private
work. If a backend realizes Restore_v as the supplied additive prices plus the
supplied overhead, the planner is optimal for that restoration term. Otherwise
this price model must not be used for that backend. Eager replaces the emitted
restorations by each child's inverse sign. All other terms stay explicitly
charged; different preparation/program/control costs must be compared too.
Repeated nodes use the displayed recurrence, paying planning where it occurs.
There is no claimed improvement to the selected unequal-rank child moment.

For exact integer input bounds `|W_j|<=U`, `|D_j|<=V`, both schedules satisfy
`|W_j|<=U` and `|D_j|<=V+U sum_i |b_ij|` at all prefixes. Products obey the
same majorant. A sufficient common signed width is one plus the bit length of
the maximum of U, `V+U max_j sum_i |b_ij|`, and all coefficient magnitudes.
The fixture takes U=7,V=11 and seven signed bits. This is an exact integer
headroom bound, not a numerical rounding theorem.

For the fixture, the specified scalar interpreter reads W,D and b,g per child,
multiplies bW, adds to D, writes D, and negates/writes W for g=-1. A restoration
reads W, negates it and writes W. Both programs execute five multiplies and five
adds, and read ten coefficients. Eager/deferred data reads are 15/11, data writes
15/11, negations 10/6 and program records 10/6. Each record's bit decoding and
travel cost, storage, initial admission, preparation and planner work are the
separate terms above. The interpreter also reverses the literal program.
These are counted operations, not a runtime benchmark or fixed-tape compiler.

## Evidence, sources and remaining work

[CERTIFICATE.json](CERTIFICATE.json) records 1,555 exhaustive scalar batches of
length zero through four, 1,296 exhaustive two-coordinate two-child batches,
and 160 deterministic seed-53 longer batches of length five through eight.
All binary cut masks are exhausted within each declared batch, after enforcing
mandatory cuts. The independent interpreter retains every D and W basis column.
The certificate records the exact partition counts. Finite tests support the
written proof; they are not a formal proof of the multiplication theorem.

Controls change the cancelling reader, add an intermediate observation, reorder
a read around a workspace change, corrupt an emitted cost and mutate source or
certificate bytes. Nine input errors and one unknown CLI field are rejected.
The unchanged PR1155 certificate still passes. Its exact Batch implementation
also confirms the new construction on real and imaginary basis inputs and a
nontrivial dirty Gaussian input. No claim is made against its valid negative
example or its finite recorded counts. Its heterogeneous-cost discussion is
outside this contribution's scope.

Base `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe` selected PR1094 at conditional
kappa `836330098538459/500000000000000000`. [SOURCES.json](SOURCES.json) binds
the runtime predecessor files and records separate context-only selected pins.
The package replays offline from its own directory. It does not depend on a
future moving selected record. [CLAIM.md](CLAIM.md) records assignment, rejected
covered candidates, exact heads and overlap. [NOTICE.md](NOTICE.md) preserves
credit and license. [VALIDATION.md](VALIDATION.md) records environments and checks.

Supplier realization, common labels and frames, whole-call hosting, fixed-tape
routing, precision/recovery beyond the exact integer model, and analytic transfer
remain unproved here. No selected source, frozen upstream file or other PR is
modified. No full cold replay or proof-assistant verification is claimed.
