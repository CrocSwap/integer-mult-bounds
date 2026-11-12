# Persistent restart of the encoded balanced CRT endpoints

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Apache-2.0. Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
This is a source-relative successful-call composition theorem. **No new kappa.**

## 1. Claim and retained premises

The exact forward and inverse endpoints are those of
[CrocSwap/integer-mult-bounds#7351](https://github.com/CrocSwap/integer-mult-bounds/pull/7351)
and [#7352](https://github.com/CrocSwap/integer-mult-bounds/pull/7352), at heads
`d2ed3959c30528b0b85fc6d815d4ad4f94f6be86` and
`8c0e55c9ba25ff2c8199b01539a4d56ae71a1473`.
Their algebra, current-coordinate numerical arithmetic, encoded traversal,
same-source staging/commit, and successful retirement are inherited results.
The inverse's PROOF section 5 and Open next question 2 leave same-inventory restart
open and charge 158 private histories for a fresh forward/inverse pair.

For every call there are `d >= 2` axes, where d is a power of two. Declared
widths satisfy `h_i in {ell-1,ell}`, `ell >= 2`; moduli are pairwise coprime
and satisfy `2 <= s_i < 2^h_i`; coordinates satisfy `0 <= x_i < 2^h_i`.
These conditions force `h_i >= 2`. The #5353 padded source encoding is
already supplied on a disjoint source port at local head one. Set

```
A = sum_i h_i,       M = 2 + 3A + 4d,       P* = A+1.
```

The source is mutable only by its owner outside a numerical lease. Source
production, re-encoding after a geometry change, acquisition of a different
source, and any payload routing remain caller operations with their own bill.
The restart adapter does not perform or price them as zero. The theorem can
use one physical source throughout; an environment retaining several source
ports must count all those external histories separately.

The private inventory consists of 79 disjoint roles. On initial admission
each role has its head at local one and **every cell in its complete retained
local backing is blank**, including local zero. The inventory may be freshly
acquired or have arbitrary, already paid blank historical lengths `k_r`.
Local checks of cells zero and one do not establish the whole-tail premise.
For translated origins, an opaque prefix to the left of each local zero is
separately retained, charged, and never accessed.

**Theorem.** Under the pinned predecessor contracts and the linear-use
discipline below, `Restart` implements any finite sequence of successful
forward and inverse endpoint calls on this same 79-role inventory. Each
call takes only the supplied source and one direction bit. It derives all
geometry from the current physical source, applies the correct complete
padded address-state map, preserves all source bytes outside coordinates,
and returns all 79 complete historical backings blank at their original
local heads. No Port, numerical Word, or Arena backing is reacquired after
initial admission, and no backing or meter is reset, shortened, or replaced.

Thus both `F^-1(F(x))=x` and `F(F^-1(x))=x` use 79 private histories on the
same admitted shape, rather than the predecessor's fresh-pair 158. Both
complete invocation costs remain charged. Calls with different legal shapes,
moduli, coordinate values, or directions may be interleaved at retired
boundaries; they are not asserted to be inverse to each other when their
mathematical maps differ.

This does not discharge the full selected `owned_erasure`, `precision_tape`,
or `analytic_recovery` assumptions. It resolves this specific restart
implication using the inherited successful numerical and source contracts.
The selected conditional kappa remains **0.00363005817**.

## 2. Exact fixed-role interface

The numerical owner has 63 roles in its unchanged acquisition order:

| Roles | Count | Use |
|---|---:|---|
| 0 | 1 | Current precision guide |
| 1–2 | 2 | Canonical left/right node input streams |
| 3–59 | 57 | Fifty-six numerical words and one template |
| 60–62 | 3 | Padded left/right inputs and whole-node output |
| 63–70 | 8 | Protected current-width numerical guards |
| 71–76 | 6 | `axis`, `depth`, `halve_a`, `halve_b`, `half`, `double` |
| 77 | 1 | Reusable source width guide |
| 78 | 1 | Full-source staged update |

`Restart` retains the existing `Bank` object and its first 63 ports. The
unchanged owner's `open` resets only its bounded role cursor and busy flag;
its adapter obtains each current numerical role from the same port tuple.
The remaining sixteen ports are returned by a fixed constructor facade in
the order above. A facade acquisition performs exactly these five Port
actions: read local one; move to zero; read zero; write LEFT; move to one.
It does not inspect a length or assign a decoded runtime width.

The unchanged frontend constructor immediately retires its eight guards,
keeps the seven topology markers while manufacturing the encoded shape,
and then the unchanged endpoint constructor retires its staging role.
Hence it sees exactly the logical entry state created by a fresh Port,
but on the actual existing backing and meter. The fresh numerical bank
constructor is replaced only by a factory returning the retained bank.
No numerical producer, forward/inverse frontend method, or source writer
is changed. `EXPORT-PINS.json` authenticates all ten imported files.

The forward writer's exported bytes originate at commit `532b60a...`; its
Git blob `b084d893bdb2ce5571ef00196a9ec6a60e723964` was also checked at
the current #7351 head `d2ed395...`. The inverse frontend and subtractive
producer are exact #7352 bytes. The canonical sources and immediate
predecessor notices are retained without edits.

The facade cursor is in the fixed set 0,…,16. Direction, ownership, and
active/retired flags have fixed finite domains. Identity/disjointness checks
are checks of the fixed physical role assignment, not an input-sized
addressing service. As in the predecessor, Python objects representing
the one current lease are an interpreter representation of fixed control;
the theorem does not compile an unbounded history of stale Python aliases.

## 3. Restart invariant and successful induction

Let `R` be the boundary predicate: no endpoint or numerical lease is active;
all 79 local heads are one; all 79 complete historical local backings are
blank; physical role identities and meters are unchanged; and the source is
disjoint and supplied in its admitted format. Initial admission provides R.

Assume R before a call. The sixteen facade acquisitions change only cell
zero of their selected roles and preserve all old blank tails. Their fixed
order is exactly the predecessor constructor order. The numerical owner
remains the same retired owner and acquires its 63 roles in its already
proved order. Consequently the predecessor's complete-call theorem applies
with the new encoded source, not with a cached shape or precision.

For one call, the source-driven forward or descending inverse frontend
manufactures shape, node starts, half sizes, and exact current precision.
The inverse startup and level hook remain unchanged. Each numerical lease
borrows the actual current source, stages a full equal-length replacement,
retires numerical/guard inputs, and only then commits the coordinate update.
The writer pays these stages at every node. At the natural end of the full
traversal, the frontend also retires all seven topology roles.

The older-tail part requires explicit justification. Every owned stream is
contiguous within its current logical extent. Each successful consumer
erases the whole extent it used, including its current delimiters and
marker, before release. Every previously longer part of a role is blank
by the induction hypothesis. A shorter current extent therefore leaves
the old suffix blank, while a later larger extent either overwrites blank
old cells or extends into new blank backing. Guard RIGHT markers and
numeric templates are manufactured from the **new** guide; historical
root delimiters are never reused as current precision. The predecessor's
within-call argument already handles shrinkage followed by regrowth;
this argument supplies the identical premise across complete calls.

It follows that every historical cell is blank again at complete return.
`finish` then checks the finite lifecycle flags and each role's local
marker/body/head by 316 paid Port actions and releases the endpoint reference.
It does not erase or forget capacity. Thus R holds after the call, proving
the theorem by induction over every finite successful sequence.

**Why no old-capacity scan is omitted.** The algorithm uses the proved
successful-retirement invariant, not a supposed scan of an invisible blank
tail. An arbitrary nonblank cell behind a blank separator violates initial
admission or the no-external-mutation rule. The adapter cannot certify that
such a cell is absent by two local reads, and makes no such claim. Rescanning
all old capacity would give an additional history-dependent time term and
would not be covered by the current-call bound after a large shrink. Here
that rescan is unnecessary because successful execution establishes the
stronger invariant before every restart. The verifier includes a dirty-tail
countercontrol demonstrating this exact distinction.

## 4. Linear use, failures, and translated origins

The supported path is `start`, zero or more endpoint `step` calls followed by
complete `run`/natural termination, then `finish`; `Restart.run` executes the
whole path. A second start is rejected while the owner remains active.
Finish is rejected while the traversal, numerical lease, or staged source
commit remains unfinished. A failed start or numerical call does not yield
a fresh retired owner. No crash recovery, malformed-stream termination,
or rollback theorem is claimed.

Clients must not invoke internal iterator-close hooks, change ports, retain
borrowed numerical aliases, or use old endpoint/lease objects after finish.
Finite flags do not grant arbitrary stale handles renewed access. The API
checks named misuses; it is not a capability-security scheme against a
caller mutating interpreter objects. This is the predecessor's successful
linear-use machine contract, now extended across whole calls.

All port operations have unit local movement and fixed symbol tests. A
translation by a fixed origin for each physical role changes no local
transition. The program never moves left of local zero, because admitted
rewinds encounter their current LEFT marker. Its returned head is physical
origin plus one. Therefore arbitrary opaque left prefixes are preserved,
and their length is added to storage rather than discarded. The verifier's
shifted backing views test this translation without supplying runtime
geometry to the scientific code. Distinct views there have distinct
underlying physical backings; arbitrary aliased views are not admitted.

## 5. Complete source time

The source model counts Port and numerical Word reads, writes, and unit
moves, together with a fixed input-independent control refinement. It is
not a literal binary-TM instruction certificate. The source, writer,
numerical, guard, and owner bills remain those of #7351/#7352.

Fresh initial Port acquisition and retirement cost 12 raw actions per
role: two for initial marker placement and ten for retirement. Thus all
79 roles cost 948. The wrapper's additional initial local validation
costs four actions per role, 316. Fresh initialization therefore has
**1264 raw Port actions**; admission of an already owned blank inventory
pays the **316** validation actions, with the cost of supplying that
inventory belonging to its caller.

Every successful call has **80** facade rearm actions (16×5) and **316**
finish actions (79×4), exactly **396** additional raw actions. The old
per-call acquisition allowances are not subtracted to claim a tighter
theorem. All shape scans, copies, numerical operations, current-width
preparation, source staging/commit, cleanup and head returns stay charged.

Let G range over the d−1 balanced nodes of a call and let
`P_G=1+sum_(i in G) h_i`. A safe inherited-plus-restart envelope is

```
C_R (M+2)^2 + 4096 + 396
  + sum_G [2^21(P_G+2)^4 + 2^16(P_G+2)^2 + 4096].
```

`C_R` is a fixed control refinement constant. As before, the raw observed
frontend/adapter traffic is checked against `2^19(M+2)^2`; that raw value
is not represented as a certified literal binary-control constant.
The factor 2^21 safely covers either direction. The predecessor proves
the numerical sum is O(A^4), and M=O(A). Hence q successful calls have

```
T <= T_initial + sum_(i=1)^q O(A_i^4),
```

with no `q*K0` term. Since every admitted A_i≥4, the fixed 396-per-call
overhead is absorbed. Caller source acquisition, source re-encoding,
payload transport, and outer application are separate nonzero obligations.
No multiplication recurrence or new saving follows from this helper bound.

## 6. Historical backing, counted by physical role

For one call use the predecessor's rolewise backing bounds:

```
R(A,d) =
  [P*+1]
  + [2A+2d+2] repeated twice
  + [P*+2] repeated 57 times
  + [d(P*+2)+2] repeated three times
  + [P*+2] repeated eight times
  + [d+2] repeated six times
  + [A+2, M].
```

This vector has 79 entries in the table's physical order. Its sum is

```
D(A,d) = 3Ad + 74A + 23d + 223.
```

For a finite call sequence define A_max=max_i A_i and d_max=max_i d_i.
Every component of R is nondecreasing in both arguments. Because no role
is replaced or shortened, its final local backing is bounded by

```
max(k_r, max_i R_r(A_i,d_i))
    <= max(k_r, R_r(A_max,d_max)).
```

Thus total private local backing is at most

```
sum_r max(k_r,R_r(A_max,d_max)) <= K0 + D(A_max,d_max),
K0 = sum_r k_r.
```

Since d_max≤A_max/2, this is `K0+O(A_max^2)`, independent of the number
of successful calls. All opaque left prefixes and complete source backing
are added separately. The envelope uses **the sum of per-role historical
maxima**. Taking a maximum of observed total fresh footprints would be
invalid in general: capacities (9,1) and (1,9) have maximum total 10 but
their persistent roles require 18.

As in the predecessors this is a retained backing bound. A Port may step
onto a blank cell immediately beyond its written backing; a visited-span
ledger must also include that reached cell. Adding one cell per fixed
role is a safe conservative adjustment for these admitted streams. It
does not turn the source-level theorem into a literal binary space proof.

## 7. Verification and remaining obligations

`verify.py` authenticates ten exports and runs 174 whole calls containing
270 actual numerical nodes. The source-driven `run()` controls every
traversal. A verifier-only defining-congruence oracle checks every node
and final result; no decoded value or schedule is passed to runtime.
The first two sequences exhaust all 32 padded pairs for (3,5) and test
eight adversarial four-axis inputs in both composition orders. The third
sequence changes 2→8→4→2→4→8→2 axes, grows/shrinks/regrows widths, changes
moduli, starts with nontrivial clean histories, and translates all origins
behind opaque prefixes. Source tails, complete private tails, current
precisions, identities, meters and complete costs are checked each time.

The tests prohibit new Port/Word/Arena constructors after acquisition and
poison frontend geometry-decoding names. Fourteen controls address active
reentry, incomplete finish/commit, repeated finish, nonfinite direction,
source/private aliasing, short or aliased inventories, a live origin,
missing rearm, hidden fresh allocation, wrong direction, an inadmissible
hidden dirty tail, and max-of-total space undercharging. Finite controls
corroborate the induction; they do not establish universal validity by
enumeration, independent human acceptance, or a proof-kernel theorem.

The concrete progress is a persistent source-relative endpoint boundary.
The arithmetic, encoded CRT maps and within-call ownership contracts remain
inherited. Payload routing, source acquisition, exceptional-key adaptation,
literal binary lowering and a full analytic recovery caller remain open.
