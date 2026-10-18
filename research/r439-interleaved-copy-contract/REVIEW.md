# Applicability audit: the interleaved immutable COPY window

The 303 target-only undo ADDs and ten taps in PR2407 fit the generic
frame-relative snapshot simulation already written in PR1627. The parent-run
certificate now binds the exact changed programs to that proof's unchanged
ideal owner schedule and exact transports. The native legality interface does
not require every ADD inside a COPY window to read the copy. This separate
mathematical audit checks the implication and its hypotheses. It does not
reprove or rerun PR2421's native replay, introduce a new snapshot theorem,
or establish an all-size compiler or supplier admission.

Scientific base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
PR2407 head: `4944211cee666eb8631b990cb0f33cfa68666485`.
Its `research/r439-single-copy-interleaving/verify.py`, `WITNESS.json` and
`proof-audit.md` were inspected using `git show`. PR2421's supplied replay
head is `71d10b283795d071c3680797f0e63856e6499fd2`; its replay is predecessor
evidence, not a check executed in this audit.

## Sources and what they actually require

1. [PR1627's whole-call proof](../pr589-five-helper-hosting/PROOF.md), section 3
   (lines 117--159), gives event induction for arbitrary equal-frame ADDs,
   frame-relative MOVE/COPY, and guarded ERASE. Its generic argument is credited
   there to PR540's `FramedReplay` and `OwnerTransport`. Section 2 proves
   injective owners for the particular PR589 source, including its private
   stream; section 4 composes complete calls before commuting residuals.
   The proof covers an ideal stream model over fields of characteristic other
   than two, using the full finite orthogonal group for cover sweeps. Boolean
   payload arithmetic remains over F2. Its admission limitations are explicit.
2. The retained [copied-center lemma](../five-stage-source527-banks/proof/copied-centers-lemma.tex),
   lines 29--35 and 49--75, specifies a complete source-role stream, including
   controls and spectators, of volume `V/W`; one extra fixed work stream;
   parked inactive originals; a paid rank-r transform of the copy; immutable
   source values; and forward/reverse relative transports. Its displayed
   scatter-only schedule is a construction, not a prohibition of other
   operations on disjoint targets.
3. [The native legality checker](../e8-bit-carrier-skeleton/code/bit/checkers/legality_h.cpp),
   line 11, checks common operand frames, an active temporary, distinct ADD
   operands, and no ADD destination equal to the copied source or temporary.
   It does not inspect the phase field to impose a scatter-only window.
   [The column checker](../e8-bit-carrier-skeleton/code/bit/checkers/columns_h.cpp),
   lines 27--30, imposes the same source/temporary immutability and lifecycle
   restrictions. `columns_k.cpp` has the corresponding checks at lines 36--39.
   These are event-level checks, not a proof of physical scratch allocation.
4. [The original exporter](../e8-bit-carrier-skeleton/code/bit/export_records.py),
   lines 57--64, emits only scatter reads within each COPY pair. PR2407's
   `interleave` explicitly constructs a different literal event list. The
   exporter's normal-form output is not the native execution alphabet.
5. The retained [fixed-tape schedule](../../upstream/build/sections/04-swap.tex),
   lines 215--242, parks inactive streams, isolates child I/O, restores stack
   heads, and forbids scans through parked ancestors. The corresponding
   equal-row/spectator contract is in `05-layers.tex`, lines 563--596.
   Those hypotheses are needed when moving from ideal events to a recursive
   implementation; an endpoint matrix does not check them.
6. PR2195's `research/selected-bit-local-ring-sweeps/PROOF.md` at
   `3a1cf78a1ba6322129e42d80c50d21765524d612` was inspected with `git show`.
   Its sections 2--3 extend the common-label induction to complete local-ring
   packets only after proving separation of the owned low classes. Its
   section 6 gives a counterexample to inferring high-packet separation from
   point-owner injection. This audit retains PR1627's finite orthogonal-field
   stream domain; it does not import PR2195's stronger packet conclusion.

## The exact interface

Fix any admitted address set X and an F2-module M. A decoded row is an element
of `M^X`. The argument is uniform in X and M and does not assume clean or
independent payloads. In particular, helpers and targets may contain arbitrary
correlated Boolean functions. The temporary is different: it is an explicitly
reserved blank stream at entry, and must again be blank at exit.

At the selected COPY entrance let `c` be the decoded value of retained helper
472, let `y` be the vector of 111 target rows, and let `w` collect every other
live row and arbitrary dirty implementation workspace. Write `q` for the
temporary. The required boundary is

```
(c, y, q=0, w) -> (c, H y + b c, q=0, w).
```

Here H is the prescribed ordered 303-gate target operator, and b is the
prescribed sum of ten transported tap responses. This is an interface for the
selected window only; the surrounding source word supplies its complete dirty
helper restoration and final decoder identity.

The sufficient physical prerequisites are the following.

* **Distinct storage owners.** At each common invocation, all target rows,
  helper472, the temporary, and reserved unrelated rows have injective owners.
  Equal contents or equal family labels do not identify storage. A reserved
  stream may be parked; it is not thereby available as descendant scratch.
* **The same exact frames and address alignment.** Let decoded rows be
  `c_i = f_i composed with Gamma_i`, with bijective gauges. Both target operands
  of each undo ADD, and the target and temporary of each tap, must have the same
  gauge and common native address correspondence. Merely matching ranks or
  frame dimensions is insufficient. Helper472 stays at its source gauge;
  the copy is transported to the common target gauge.
* **A complete snapshot.** COPY maps a blank private row to the transported
  full source stream, with all controls and spectators. At the decoded level
  it establishes `q=c`. The source and snapshot remain unchanged until ERASE.
  An ERASE is authorized by the transported-source equality, not by a claim
  that the temporary was once copied.
* **The literal ordered word.** The undo order and each tap's cut are preserved.
  Each operation is an exact F2 shear with source preserved. The whole window
  exposes no intermediate observer or delivery requirement that the original
  scalar endpoint proof omitted.
* **Complete child and workspace contracts.** The paid COPY transport must
  implement its exact relative address map on the full stream and restore its
  own work. Child allocations exclude parked ancestors and all unrelated live
  ports. The temporary is the active input/output of its COPY-transform child,
  not immutable during that transform; immutability begins when the transform
  returns. Subsequent ADD implementations must realize their advertised shear
  and preserve the source, copy and other live ports. Disjoint private scratch
  is sufficient. A different borrowing implementation needs its own complete
  arbitrary-input boundary proof; restoration of borrowed cells alone is not
  enough.

In PR2407's selected open interval, every operation after COPY and before ERASE
is an ADD: 303 target-to-target ADDs at frame zero and ten temporary-to-target
taps at frame zero. No MOVE or nested COPY is introduced. Thus there is no
new recursive transform in the interval between completed COPY and ERASE.
The recursive scratch exclusion matters for the initial COPY transport and
for any lower-level implementation used to realize the pointwise ADDs.

## Derivation and both orientations

PR1627's gauges give the physical snapshot equation

```
f_q = f_472 composed with Gamma_472 composed with Gamma_q^{-1}.
```

COPY establishes it. Injective owners and exact target-only operations leave
both sides unchanged. A tap updates only its target, so it also preserves the
equation. Hence induction through the literal window proves the ERASE guard
and permits erasure without losing arbitrary dirty information. At the same
time, equal-frame ADDs give exactly the decoded target shears. This is the
generic event induction of PR1627 applied to the changed window, not a
consequence of a new rank calculation.

Write the undo gates in execution order as `H_0,...,H_302`, and put
`H = H_302 ... H_0`. A tap into target i at cut k has final response

```
H_302 ... H_k e_i c,
```

with the empty product at cut 303 equal to identity. The complete result is

```
y_out = H y_in + sum_(k,i tapped) H_302 ... H_k e_i c.
```

No independence of c and y is used. PR2407's supplied finite witness fixes
cuts `(0,13), (0,26), (0,34), (0,58), (0,79), (0,90), (0,95), (104,6),
(126,24), (182,3)`. Its existing exact matrix equality supplies b. This audit
does not repeat that matrix or native endpoint census.

For the literal inverse, reverse the ADD order and exchange COPY and ERASE:
the first reverse operation creates a fresh transported snapshot from the
unchanged original. F2 shears are involutions. Reversing an ERASE thus creates
a fresh copy rather than recovering an erased stream. In the complemented orientation the original
helper frame and common target frame change together, as in PR1627's
rank-seven calculation: `D_(I-P) D_I = D_P`. The same relative rank-seven map
therefore supplies the snapshot, and the same event induction applies.
This statement does not claim that uncompiled integer-valued ADD endpoints
equal the F2 endpoint; signed lifts and physical precision remain separate.

## Reusing the 288 owner descriptors

There is a direct conditional transfer to PR1627's hosted model. Fix its
unchanged 288 stage/replica owner descriptors, port charts, host supports,
idle intervals and private-family convention. Replace only the literal local
programs, provided the following checks hold: the same 111 ports and 439
helpers, the same root-line geometry, the same entry and exit frames, every
new event's common-label/transport/lifecycle obligations, and the same complete
decoded endpoint on arbitrary inputs. Every call's program binding must name
the replacement word rather than its old hash.

Under these hypotheses section 3's event induction works for the replacement
word. Its complete local endpoint induces the same helper residual and data
map as before. Section 4 then uses the same complete-call chronology and
disjoint-support completion to recover the same hosted/unhosted identity.
There is no need to commute any of the new undo gates through a different
hosted call. An exact equality of the COPY/ERASE projectors is needed; equal
rank-seven counts alone would not supply the same physical transport.

This reuse is visible in PR1627's `verify.py`: `ownership(t,w,g)` checks the
geometry, stock, owner routes, supports and schedule without inspecting ADD
chronology. `local_replay` separately checks each literal event and the complete
endpoint. Combining those interfaces after rebinding program hashes is the
appropriate source-specific applicability check. The original source's
syntactic H2/K conditions are not hypotheses of this generic event induction;
the parent-run exact local replay supplies the replacement endpoint evidence
for this fixed word.

The owner claim is about logical streams `(family,g)` at a fixed common
invocation. Two target roles can have different data charts: the equality
`g sigma=d` aligns both operands before applying the common-address ADD. It
is not a claim that their raw physical indices coincide. Nor does injection
for each d authorize batching many d values into one high packet. PR2195's
low-class separation, complete-spectator and whole-packet callee contracts
would have to be rebound before making that stronger statement.

## Review of the completed consumer binding

The separate review agent inspected the parent implementation in `verify.py`,
its `RESULT.json`, the registered source pins, and the behavioral checks. It
did not rerun native replay or claim an independent implementation of PR1627's
engines. The parent reports the verifier and eight controls passing, with all
six behavioral test groups passing under Python 3.12. The resulting receipt
records the exact RAW6 digest
`856873eac7d6d9d737e83a28c321b6e760ee183d9648bd98e80761b8d4dc9aba`.

The binding checks equality of `v`, `R`, `h`, `lines`, `frames`, `start`,
`final` and `ret` against the pinned PR589 source. It then reconstructs the
exact PR2407 record list and applies PR1627's rational projectors and full
chronological `local_replay` to both orientations. Consequently it checks
661 independent dirty columns, both final frame lists, all COPY/ERASE guards,
and the complete replacement endpoint rather than only the isolated window.
The fixed window is records 9070 through 9384, inclusive of COPY and ERASE;
all 313 interior events have the required typed footprint and ordered taps.

The RAW6 translation preserves the predecessor's precise inverse convention:

| Original event | Reverse event in the complemented interpreter |
| --- | --- |
| `MOVE(a,u,v,r)` | `MOVE(a,v,u,r)`; swap frame labels, retain the positive rank |
| `ADD(a,b,c,f)` | `ADD(a,b,-c,f)` |
| `ERASE(a,q,u,v,0)` | Fresh `COPY(a,q,u,v,rank(u-v))` |
| `COPY(a,q,u,v,r)` | `ERASE(a,q,u,v,r)` |

The source/temporary frame labels in the last two rows are deliberately not
swapped: the reverse interpreter complements both projectors. For this source
they become `I-P` and `I`, whose relative swap is the same rank-seven `D_P`.
The rank field carried into a reverse ERASE is a schema/lifecycle check; the
replay charges the fresh reverse COPY and does not charge the ERASE again.
This agrees branch-for-branch with PR1627's `literal_programs` translation.

The implementation reruns `ownership` on all 288 original descriptors, checks
the inherited owner receipt, and rebinds only the two local programs, RAW6
source digest and per-call local program hashes. Its exact comparison retains
all other call fields and template data. The profile is then rebuilt from the
replacement local profiles and unchanged idle remainders, giving rank mass
1,808,352 and deficit 10,272. These checks establish the finite premises of
the transfer above. The written argument supplies uniformity over arbitrary
Boolean functions and the ideal field/group domain; neither the receipt nor
this review claims a machine-level proof.

No mathematical blocker to the claimed ideal hosted/unhosted equality was
found. In particular, the same decoded helper endpoint together with the same
entry/exit gauges gives the same physical helper residual. Complete calls may
therefore be substituted in the unchanged chronological hosting proof before
that proof moves residuals. This argument does not require an independence
assumption on evolving helper contents or a fresh-input assumption between
cover classes.

## Exact failure witnesses

**Wrong cut despite safe COPY.** Work at one address with `c=q=1` and
`(y1,y2)=(0,0)`. Let `T` be `y1 += q` and `H` be `y2 += y1` over F2.
Executing T then H yields `(1,1)`; H then T yields `(1,0)`. In both cases the
source and copy are unchanged, every ADD is legal at one common frame, and
ERASE is valid. Thus the snapshot contract does not make target operations
commute with taps. A count-preserving permutation can be wrong.

**A target aliases the copied source.** Let `c=q=1` and another target `z=1`.
If an alleged target-only ADD physically writes `c += z`, then the source
becomes zero while the copy remains one. The physical ERASE guard fails.
Distinct logical role numbers do not exclude this if the owner map aliases.

**Restoration alone does not justify borrowing the snapshot.** With
`q=c=1`, `z=1`, and `y=0`, execute `q += z; y += q; q += z`. The source and
snapshot finish unchanged, and ERASE succeeds, but y is zero instead of the
required one. A footprint check must reject the transient writes to q, or a
different complete macro contract must prove the actual output independent
of the borrowed dirt. This witness is not a prohibition of every possible
fully proved scratch-sharing implementation.

## Cost boundary and remaining implications

Let L be the complete role-stream volume `V/W`. At the abstract interface the
window uses one rank-seven COPY transport, its ordinary copy/erase passes,
303 already counted target ADDs and ten taps. Its pointwise work is `O(313 L)`
with a constant fixed by this finite word. It needs one retained snapshot
stream and no additional independent row coordinate. Keeping that snapshot
alive longer does not itself add a recursive call or change child volume.

This does not establish the numerical physical invoice. Bringing two target
streams into elementary-operation work areas, preserving the live snapshot,
and returning all heads may change finite movement constants. The original
fixed-tape proof can support a uniform linear overhead only after a concrete
allocation shows that the reserved snapshot and parked parents survive every
child and cleanup. Temporary storage remains outside the logical-volume
denominator. Reordering also changes prefix magnitudes; PR2407's existing
finite majorants concern its actual order and do not by themselves discharge
the common-grid or rounded-machine obligations.

The covered result is a written, all-address-size *conditional interface
argument* plus an applicability audit of retained source contracts. It is not
an all-size emitted-program proof, a new finite native replay, a formal-kernel
proof, or a stronger multiplication theorem. PR1627's original finite
certificate is bound to its frozen PR589 program; the parent-run consumer
certificate now supplies the changed-word binding to its generic proof.
That conclusion uses exact geometry, event, endpoint, owner and program-hash
checks, not merely the unchanged MOVE list.

The remaining concrete obligations are to show the all-size compiler keeps
the snapshot out of unrelated recursive scratch, and to pay the complete
movement, work restoration and precision invoice. Rebinding complete local-ring
high packets is also separate. These physical obligations remain open here;
the finite event/ideal-owner binding is complete. No new kappa or
selected-frontier change follows.

Credit: PR2407's construction and PR2421's native replay; alephnan's PR1627
whole-call hosting proof; cheesegrader's PR540 generic frame/owner simulation;
Paureel's retained copy/transform/read/discard interface; and the original
supplier/exporter authors retained in the linked packages. Prepared by Ross
Richardson with substantial OpenAI Codex assistance in a separate recursive-
interface review agent. This is AI-assisted mathematical review, not independent
human review. New text is Apache-2.0; inherited sources are unchanged.
