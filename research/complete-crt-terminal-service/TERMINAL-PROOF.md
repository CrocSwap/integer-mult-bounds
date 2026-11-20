# Literal retirement of the current CRT Entry

Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.
Apache-2.0. This terminal-component proof is part of the complete successor package.
The public joined predecessor is unchanged. PROOF.md supplies the fresh
complete prefix/producer/consumer/terminal integration.

## 1. Result and exact boundary

The frozen 70-role join is commit
7a6334dceef9d03fb5b1aeec4269a2911c0112b4, package
research/combined-crt-literal-services. It combines numerical arithmetic at
ee6005fe241ab947e511fe9f6d86f5f4fa58478b with literal lifecycle at
39c309f1aa72af12669d37ae055da0ece1ae0e7d. The scientific base remains
e54523517d0f03e58352e647c403a5af3e525a57. SOURCE-PINS.json authenticates the
exact original Entry, Word, record and producer files used here.

The frozen producer/consumer interval ends with a retained Entry.close.
At P=7 after consumption it performs 468 native symbol actions. Those split
as 392 to remove 56 numerical L markers, 46 to erase the template and its
marker, and 30 to retire three already-cleared owned record ports. Its live
queries are separately literal in the predecessor.

**Fixed-70 obstruction.** The three owned record ports are not among the
70 bound owners. Every R/W/M instruction in a program on that fixed binding
acts on one of those 70 owners. Induction on instructions therefore leaves
each other owner unchanged. Entry.close must change the L marker on each
of its three record ports to blank. Consequently no such fixed-70 program
implements the complete terminal contract. Rebinding a role or identifying
different owners would require another physical contract.

**Fixed-73 construction.** Keep all 70 existing owner bindings, and bind the
three existing owned record ports to roles 70,71,72. A single finite literal
terminal graph then implements the admitted Entry-close effects and metadata
CLOSE, with no Word, Port-clear, Entry-close or host live-set service.
It has 2,949 R/W/M/J/H states, independent of precision and record lengths.
It can be appended by a constant state offset to the unchanged frozen union,
giving 1,438,047 states and 73 fixed roles.

This adds three addressed roles, not three newly allocated physical owners.
The predecessor's complete source context already counted all three. The
physical context still has 76 owners when its borrowed guide and two borrowed
canonical input tapes are included. Under the requirement that the original
70 physical bindings stay fixed and distinct, those three additional roles
are necessary as well as sufficient. This is not a lower bound for a
redesigned machine with different storage or rebinding services.

The terminal graph's canonical SHA-256 is
f060e7097028921bda8945724d0b9668cdc20e9d6552d65215a925ee5bd78914.

## 2. Admission and ownership contract

The current successful producer/consumer supplies the following ready state.
The proof also permits nonempty record prefixes with the same stated framing.

* Numerical roles 0..63, four selectors 64..67, template 68, stack 69 and
  record ports 70..72 have pairwise distinct actual backing. Their physical
  identity, retained capacity and current heads are fixed at entry.
* Roles 0..7 are protected borrowed owners. Their contents can be dirty and
  their heads can be suspended; the terminal graph never addresses them.
* Each numerical owner s in 8..63 has head 1, an L marker at cell 0 and a
  blank suffix throughout its retained historical backing. In particular
  its current P+2-cell frame has already been freed. P>=4 is inherited.
* Template role 68 has head 1 and L, P zeros, R in cells 0..P+1. Every older
  retained cell beyond that frame is blank.
* The four selectors have head 0 and at least eight backed blank cells, with
  any older retained suffix also blank.
* Stack role 69 has head 0. Its framing is L followed by m six-bit records,
  followed by R, then blanks. The inherited lifecycle invariant says these
  records are distinct codes in {8,...,63}; live roles are their complement
  in {0,...,63}. The supplied stack window has at least 338 cells. No host
  set, list or decoded m is supplied to terminal execution.
* Record role j in 70..72 has head 1 and framing L followed by n_j nonblank
  record symbols, then a backed blank cell. No body symbol is L. All later
  retained cells are blank. After the exact successful consumer, n_j=0.
  Nonempty prefixes are additionally tested and priced. A read from a
  nonempty prefix's first blank needs an actually supplied cell; an implicit
  out-of-range blank read is not a grant.
* The caller is in its live Entry phase, corresponding to closed=False.
  No source work resumes once the service returns its CLOSED finite tag.
  That tag implements the source's finite closed=True transition. The
  changing-Entry caller and its phase attachment are outside this study.

The complete numerical terminal condition is m=56. Given the inherited
distinct-owned-stack invariant, that is equivalent to live={0,...,7}:
there are precisely 56 possible owned codes. The new guard checks m=56
physically. It does not independently establish stack uniqueness. A duplicate
record control makes this retained premise explicit.

The instruction set is the same R/W/M/J/H set. The complete source already
has the finite tape alphabet 0..13. Numerical and metadata instructions use
its five-symbol 0/1/L/R/blank subset; record-body reads additionally admit
the existing finite record tags. On the consumed source fixture the record
paths encounter only L and blank. No unbounded symbol, data-dependent tape
operand, scientific integer or precision counter enters finite control.

## 3. Literal implementation and proof

### Physical guard

The graph checks and returns over the first eight blank cells of each of
four selectors. It then checks L on the stack, exactly 336 binary cells and
R, returning the stack head to zero. No cell has yet been written. Under
the inherited invariant, successful completion of this guard proves the
terminal live condition without querying or decoding any host membership.

If metadata was already closed, the stack's first symbol is blank and the
guard rejects. If any owned role remains live, the legal stack has fewer
than 56 records, and an R occurs among the 336 expected binary cells. That
case rejects before any erasure. Rejection does not promise rollback or
head restoration in general.

### Numerical markers and template

For each of the 56 compile-time numerical roles, seven literal instructions
perform the original ready-head rewind/check and remove L, finishing at
head 1. The rest of that owner's historical backing is untouched and was
already blank. No runtime owner selector is needed: the roles are fixed.

The template code checks L, scans its zero digits until R, and replaces
digits and R by blanks. It returns left through the just-erased interval
while L still exists, restores head 1, then removes L and again ends at
head 1. A loop invariant after k digits is that precisely the first k
template digits are blank; its forward head is at k+1 and L is intact.
The return loop decreases the position by one until L. This proves
termination and the final blank frame for every P; no host P is used.

### Three record ports

Each record port receives the same literal loop specialized to its fixed
role. After checking L, it reads each nonblank body symbol, writes blank
and moves right. On the first blank it rewinds through the erased prefix
to L, restores head 1, removes L and again ends at head 1. The forward and
backward invariants are the template invariants with n_j in place of P.
An existing record tag chooses the same erase branch as every other legal
nonblank tag. The graph neither interprets records nor decodes n_j.

The existing three record roles are distinct from each other and from all
70 predecessor owners. There is no role rebinding, temporary alias or
movement of historical capacity between owners.

### Final metadata retirement

The final block executes the inherited successful metadata CLOSE path:
check its two shared selectors blank, erase L, 336 binary stack cells and
R, return the stack head to zero, and halt. The two other selectors remain
blank. It costs 1,395 instructions including the terminal H.

The numerical and record L markers have already been removed, but the
metadata block never reads those owners. Conversely, metadata stays live
until the physical terminal guard has completed. This resolves the
predecessor's terminal-order seam without a final host live-set query.

At successful return every owned role is blank throughout its admitted
historical backing; numerical, template and record heads are 1, and all
metadata heads are 0. Protected owners and the three additional borrowed
source ports are unchanged. The source's finite closed flag is represented
by CLOSED. A second call encounters a blank stack and rejects.

### Appending to the frozen union

Let A=1,435,098 be the old state count. Add A to every R target and J target
of the new terminal graph and use A as its entry state. Its role operands
are already the final fixed 0..72 labels. Keep the old graph byte-for-byte
as the prefix and add three unused ports to its physical context. Every
old instruction retains its role, target and semantics; no old instruction
addresses a new port. Every new branch stays inside the appended segment.

Induction on instructions proves this composition. The new checker verifies
the bounded target and role sets and independently executes the small
terminal segment. The small component checker does not regenerate the predecessor graph.
The complete package additionally generates and executes the appended graph
on a fresh whole producer/consumer/terminal invocation, as detailed in PROOF.md.

## 4. Exact all-width price

The exact original native symbol cost at ready heads is

    T_original = 5P + 5(n_70+n_71+n_72) + 433.

The 56 numerical markers cost 56*7=392. Template erasure and marker removal
cost 5P+11. Each record retirement costs 5n_j+10. Thus at P=7 after the
consumer, the cost is 392+46+30=468. This native-action comparison does not
include the predecessor's separately literal live-membership queries.

The new literal price, including physical guard and metadata retirement, is:

| Segment | Instructions |
|---|---:|
| Four blank-selector checks | 88 |
| Full-length stack check and head return | 1012 |
| 56 numerical markers | 392 |
| Template and its marker | 7P+11 |
| Record role j and its marker | 7n_j+10 |
| Metadata CLOSE, including final H | 1395 |

Therefore

    T_terminal = 7P + 7(n_70+n_71+n_72) + 2928.

The difference between native loop action counts and literal loop costs is
one J per forward digit and one J per backward digit. All fixed branches
have their explicit graph cost. No source interpreter cost or silent
callee dispatch is substituted for these instructions.

For the consumed P=7 source state, T_terminal=2977, with R=862, W=406,
M=1694, J=14 and H=1. The exact counts sum to 2977.

The addressable 70-role subset, omitting the three record routines, has
2,904 states and price 7P+2898. It leaves all three record L markers intact
and is not a complete Entry retirement.

## 5. Physical histories and resource accounting

No instruction grows, replaces, truncates, refunds or exchanges a backing.
For old history H_s and current precision P, the numerical/template
obligation is max(H_s,P+2), per actual owner. Metadata contributes
max(H_s,8) per selector and max(H_stack,338). Each added record role j costs

    max(H_j, n_j+2),

including the first backed blank cell read by its scan. After consumption,
n_j=0 but H_j remains the full old record history. All three terms must be
added separately; the maximum across the three roles is not their sum.
These record owners were already in the predecessor's 76-owner context.

The checker compares full contents, every physical identity and every
capacity before/after execution. A dirty older suffix is not erased by a
routine that stops at the current first blank or R. Two controls place a
dirty old cell on a numerical and a record owner, respectively: the local
path returns but the complete historical cleanup predicate fails. These
are counterexamples to dropping the blank-inactive-history premise, not
unhandled admitted inputs.

This is terminal erasure under supplied windows. Constructing blank grants
or validating arbitrary dirty historical regions is still a separate task.

## 6. Exact finite evidence and limits

The checker uses exact original source bytes from the frozen package.
For P in {4,5,7,19,257}, it tests record-length triples (0,0,0), (1,2,3),
(13,0,19), (131,6,47), with stack rotations 0,7,31,55 respectively. Thus
there are 20 fully declared packets. Each has unequal numerical histories,
unequal metadata histories, unequal record histories and dirty protected
owners with nonuniform heads. Each result and source native-action count
is compared to an independent run of the exact original Entry.close.

One additional fixture runs the exact original current producer at P=7,
left [(5,1)], right [(7,2)], then its consumer. The original providers are
used only to prepare that fixture. The terminal interval uses the new graph
while every raw Word primitive/macro, relevant Arena macro, Entry.close,
Port primitive/macro and host live/free access is replaced by a throwing
sentinel. There are zero sentinel calls. Its 73 service roles and all 76
complete context owners retain their identities and histories.
Every one of its 76 capacities also matches the frozen source receipt:
8,808 cells total. The three record owners retain 20 cells each. Their
60 separately charged cells extend the 8,719-cell predecessor service
context to 8,779 cells, with the other three borrowed ports still outside it.

The 21 positive packets total 77,483 literal instructions. TERMINAL-RESULT.json
lists every phase, count, touched interval and capacity. Both normal and
optimized CPython reproduce the same deterministic receipt.

Controls cover premature metadata CLOSE, an owned live slot, record-owner
aliasing, active raw-service and host-membership sentinels, necessary
stack uniqueness, necessary clean inactive tails, reclosure, and a
returning mutation that skips a record marker erase. The fixed-70 partial
program is an executable witness of the missing record footprint.

The replay takes about 0.3 seconds and under 18 MiB RSS in this environment.
The component checker generates no million-state graph; the primary full
replay does. These are verifier observations, not
a multiplication or whole-caller tariff.

## Remaining obligations and credit

The original numerical admission and lifecycle invariant remain credited
premises. The study does not lower producer control, canonical input pad,
record interpretation, Word predicates, the consumer, blank grants or the
changing-Entry wrapper. It does not provide rejection rollback or erase
arbitrary dirty tails. Attaching the finite CLOSED phase to a fully lowered
controller remains separate.

JoyboyBrian supplied the current Entry/Word/record/CRT source and its
admission lineage. CubeJerry's #7596 and published lifecycle package supply
the predecessor graphs, numerical correctness and ownership invariant.
Literal finite graph union and sentinel-delimited tape clearing are
classical methods. This contribution is the exact terminal seam, its
physical-footprint obstruction, complete fixed extension and costs.

All five selected framework assumptions and kappa 0.00363005817 remain
unchanged. Model-assisted proof writing and replay are not human peer
review or formal-kernel verification.

## Open next questions

1. Independently review the complete 73-role integration in PROOF.md,
   including its source flags, residual invoice and supplied physical histories.
2. Lower the successful consumer and its record clear operations; the
   terminal proof exposes their precise ready-head/blank-history handoff.
3. Carry the same physical histories through the changing-Entry wrapper,
   and supply the actual blank windows rather than assuming their grants.
