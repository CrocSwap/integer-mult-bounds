# Sequential stack proof and invoice

## Alphabet and entry state

The alphabet has binary symbols 0 and 1, LEFT, SEP, END, BASE and BLANK.
Payload tapes use only binary data, LEFT and BLANK. The control tape uses
BASE at its initial top boundary. A complete older frame ends in END. The
descriptor tape has BASE immediately before its word. The initial dirty
prefixes may be arbitrary; none of the routines must inspect them.

Fix k. Role i has word x_i of length s_i and head h_i, with 0<=h_i<=s_i.
If its presence bit is zero, x_i is empty and h_i=0. The entry head is
immediately after the first h_i data cells. The payload is contiguous and
the first cell after it is BLANK. Let H=sum h_i, S=sum s_i and let A count
absent roles. The parent descriptor has length d. The child descriptor has
length q when pop begins. Recursive work must retire its payloads and put
their heads at their current origins before pop. That retirement is child
work; the source adapter executes and charges it explicitly.

## Push invariant

Push first emits LEFT on the control tape. For each role it emits its presence
bit, moves the payload head left until LEFT, and emits one unary 1 for each
crossed binary cell. It then emits 0. There are exactly h_i such binary cells.
The payload head moves right to the origin, scans the unchanged word to BLANK,
writes LEFT at that end, and moves right once. The child segment is empty.
No prefix cell to the left of the previous LEFT is read or written.

The role record is therefore `presence 1^h_i 0`. Push emits SEP, copies each
descriptor bit to the control tape while clearing the descriptor tape, returns
its descriptor head to the origin, and emits END. The control head is now at
the blank cell after END. The frame length is

    L = H + 2k + d + 3.

No extent, origin, frame length or parent reference is saved. The unary header
is produced by the payload head's actual unit moves. Empty head offsets have
an explicit 0 terminator; zero never has a missing representation.

## Pop invariant

Pop clears the current child descriptor and rewinds that tape to BASE. From
the free control top, it moves left, checks END, and continues left to LEFT.
Neither a role record nor a descriptor can contain LEFT, so this is exactly
the current frame start. SEP is distinct from all binary header/descriptor
symbols. BASE before a frame start is rejected; it is not crossed.

Pop clears the frame as it parses it. For each role, it checks the empty child
origin, moves left to the child delimiter and erases it. It moves left through
the unchanged parent word until its previous LEFT, then right to its origin.
For each 1 in the saved unary offset it checks a binary payload cell and moves
right once. The terminating 0 ends the offset. Thus the final physical head
is exactly the old head. An excessive offset reaches BLANK and is rejected.
The parsed presence bit restores the finite role bitmap. An absent role must
be empty. The recorded size and offset counters in the simulator are observers;
the physical motion does not depend on those integer values.

After k roles, pop checks SEP. It copies the saved descriptor back to its tape
and clears each control cell. END terminates that copy. After clearing END,
pop walks left across the now blank frame until the preceding END or BASE,
then moves right once. This returns the control head to its exact old free top.
It rewinds the descriptor head to its BASE. All current frame cells are blank.
Older complete frames, all parent words and every earlier prefix remain exact.

Push and pop use finite branches on the current symbol and a fixed k-role
index. Their returned integer observer counts can be omitted without changing
any tape action. The hardware simulator's absolute head index is a tape-model
implementation detail; the routines cannot read it or the backing array.

## Composition

The child entry has the same form as the parent entry, with one extra delimiter
per payload tape and one complete older control frame. Apply the same argument
at each child. At a leaf, retirement establishes pop's entry condition. Pop
restores its immediate parent exactly. Induction on any finite properly nested
call tree gives complete restoration at every return. This proof has no bound
on depth, ancestor size, descriptor lengths or binary contents. It does require
the stated lexical ownership and successful child-retirement contract.

## Exact operation count

Every read, write and unit move costs one. Symbol tests and the fixed role
index are finite control. The following counts refer to the literal routines
in stack.py, including their explicit checks. H is the sum of offsets from the
left end, not the sum of distances to the right end.

| Component | Cost |
| --- | ---: |
| Push control: L writes, L moves, one initial read | 2L+1 |
| Push payload sweeps and delimiters | 2H+2S+6k+A |
| Push descriptor copy, clear and rewind | 5d+4 |
| Pop child descriptor clear and rewind | 5q+4 |
| Pop control: find, parse, clear and return | 7L |
| Pop payload return and head replay | 2S+2H+7k+A |
| Pop saved descriptor write and rewind | 4d+3 |

For pop control, location takes L reads and L moves. Forward parsing takes
L-1 reads and L-1 moves. The final backward scan takes L+1 reads and L+1 moves;
the repeated boundary check is included. Exactly L control cells are cleared.
These counts give 7L. The descriptor lengths are unrestricted and may differ.

Substitute L to obtain the two exact formulas in README.md. Since H<=S and
A<=k, their sum is at most 17S+33k+18d+5q+39. No term contains the ancestor
extent or depth. A frame retains L control cells and k payload delimiters.
The descriptor tape is reused at every level. The deepest live prefix therefore
uses the sum of the live frame lengths, with no per-depth tape allocation.

This result supplies a local linear boundary, not a full recursion-space
theorem. To absorb it into a concrete caller one must still prove bounds for
the sum of active payload and descriptor sizes. No geometric reserve estimate
can be substituted for those implementation premises without proof.

## Retained source boundary

The source adapter implements the retained local Tape operations by actual
unit reads, writes and moves. Its byte snapshot is used only by checkers.
The local size and head counters are obtained from current operations and
from the observer counts of the just-decoded physical frame. They do not save
an ancestor origin or choose a return address. A weak-reference registry models the predecessor's lexical lifetime premise.
Its live-handle keys are depth and slot. It is consulted only for allocation,
never for push/pop, and is neither serialized nor recovered by pop. The registry
is a simulator oracle for allocation, not a proved physical allocator. This interface is for properly scoped source
handles, not arbitrary stale-handle reuse or a new dynamic allocator.

Each source primitive's sequential call trace is therefore interpreted on the
current segment. Its new delimiter checks add constant work per crossed cell.
Its original mathematical endpoint and physical controller premises remain
inherited. The finite source tests exercise compact repair, ordinary fallback,
radix work and the actual right-recipe phase under nested suspension. They do
not establish the general allocation schedule, full affine payload rectangle,
recursive C output, or a selected supplier admission.

The new proof and code are by Ali Romman with substantial OpenAI Codex
assistance. The source interface and all predecessor mathematics retain the
credit and limitations in README.md and the unchanged source notices.
