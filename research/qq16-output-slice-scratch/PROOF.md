# Scratch reuse in unproduced QQ16 output slices

This is a conditional allocation refinement of commdata2338's PR2651, which
retains ywz65's PR2540 decoder. It answers PR2651's second explicit open
question. Standard storage reuse is credited; the contribution is the exact
source-bound lifetime and owner-access proof, with the complete word and bill.

## Changed access contract

Retain PR2651's 224 owned full-cover output banks Z/W, its sixteen early Z
records, 224 borrowed current X/Y fields and all native/frame obligations.
Owned output contents may be arbitrary but are disposable: their caller does
not require their entry contents to survive. Borrowed X/Y contents are arbitrary
and must restore exactly. No borrowed input may be substituted for a W slice.

Add one explicit storage/access premise. At each owner h of either original
private sweep, the caller can give exclusive writable access to the same
complete payload slice W_j[h] for j=0..15, with the same extent and component
ordering as an original local scratch array at h. Ordinary scalar CLEAR/ADD
operations can address that slice together with the original current-owner
Z slices. Different owner slices are disjoint. All these W banks remain
unobserved and unproduced until the source's later W construction. The view
does not permit changing an owner, accessing only a smaller projection,
identifying different scratch roles, or applying a global native operation
inside a local sweep.

This is an **owner-access contract**, not an assertion that every tape layout
provides it without movement. A caller must implement and bill that access.
Giving a writable view is not a data copy or a physical allocation; any actual
seek, dispatch, admission or staging needed to provide it has its own charge.
If access requires staging arrays, the claimed zero *additional* scratch does
not apply to those arrays. No global storage or runtime saving is inferred.

## Exact lifetimes and transformation

Event indices are zero-based in the pinned PR2651 WORD.json (2,415 events).

| Interval, inclusive markers | Original scratch | Output-slice view |
|---|---|---|
| 633..1066, L2 | C | W0[h] |
| 1172..2125, F0 inverse | F0..F7, G0..G7 | W0[h]..W7[h], W8[h]..W15[h] |

Every event strictly inside those markers is a scalar CLEAR or ADD. There is
no native kernel, cover map, history cut, or other owner permutation there.
No W bank occurs in the original word before event 2127. Every original W
bank's first future use is a charged CLEAR. In each scratch lifetime the
first access to each scratch role is likewise a charged CLEAR; the last
access clears it to zero with identity-frame metadata. All those CLEARs,
including the later output CLEARs, remain in the transformed word.

Replace C/F/G field references by the indicated W fields only within their
own intervals. The markers borrow/release existing W slices; they allocate
no hidden local rows. No other instruction is changed. In particular all
448 native events retain their exact field, port, rank, sign, order and
orientation. The two owner sweeps remain distinct; the slices can be reused
because both release at zero before their next acquisition or output use.

## Per-owner simulation and whole-cover consequence

Fix an arbitrary owner h, payload dimension, temporal input and initial owned
dirt. Before each private interval, every nonscratch field in the two runs
agrees. A scratch role and its W slice may initially have different arbitrary
contents, but the first access CLEAR sets both to the same zero in the same
current frame. This discards only authorized owned dirt. Each subsequent
scalar operation has identical sources, destination and rational coefficient
under the injective alias map, so induction preserves equality on all active
scratch and nonscratch fields. The final CLEAR produces zero in the identity
frame on each alias. Its release therefore requires neither a copy nor a
basis conversion. Frame labels here describe local zero/current views; no
global nonzero frame is relabeled for free.

The argument is independent for each owner. Different owners access disjoint
slices, and the body contains only pointwise scalar operations. Hence its
event-major and owner-major executions agree: moving one owner's scalar event
past another owner's event commutes because the addressed storage is disjoint.
This justifies borrowing one current-owner slice at a time without allocating
sixteen additional full-cover scratch banks. Original ordinary accesses to Z
retain their own source contracts; this lemma introduces no cross-owner read.

After a complete sweep the two runs agree on every field the remaining word
can read before its next charged W CLEAR. Old W dirt need not agree: it is
unobserved, disposable, and its first future use discards it. That CLEAR restores
full state agreement. Identical subsequent native and scalar events then yield
the same 224 outputs in F_U1, both 112-output checkpoints, and all 224 borrowed
current fields with their original physical frames. This transfers PR2651's
endpoint conditional on its inherited native/decoder theorems; it does not
independently prove those theorems or restore the original pre-F0 output frames.

## Complete local bill and limits

The 224 owned full-cover banks and sixteen early retained values remain.
Maximum additionally allocated local payload arrays changes from sixteen to
zero, while at most sixteen existing output slices are borrowed at one owner.
This is an allocation upper bound, not a minimum live-information theorem.
The scalar bill remains 840 unit ADDs, 832 quarter ADDs and 288 CLEARs:
`840*8+832*12+288*2=17280`. Native bill remains 224 rank-one plus sixteen
rank-eight children, mass352, 480 wrappers and 208 cover maps. The inherited
F0/B1 history work remains charged by its caller.

No arithmetic or native operation is removed. No improvement to the selected
moment or kappa follows. A physical caller must price the view-access contract,
bank retention, cover movement, child hosting, precision, output consumption,
root metadata and instructions. Any storage saved here may be outweighed by
access costs; these are unknown rather than assigned zero. The revision-5
decision is to stop at the conditional lifetime/access result.

The primary exact formal replay reuses PR2651's credited polynomial algebra
and baseline interpreter; its new state machine tracks actual W identities
and forbids hidden private rows. The separate JSON-only finite checker runs
owner-major bodies on two-component payloads over 2,3,5 owners with invertible
noncommuting toy native actions. It checks physical allocation equivalence,
not actual native-kernel admission. Wrong owner, alias collisions, premature
output use, missing clear and illegal native-in-body controls enforce the
boundaries. These tests support the quantified proof rather than replace it.
