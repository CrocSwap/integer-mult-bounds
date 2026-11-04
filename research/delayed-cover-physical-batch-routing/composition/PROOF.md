# Physical one-edge router/continuation composition

Scope: an exact physical boundary with a fixed finite grammar, not the selected
production recursion. The router tables are unchanged root-agent source. The
codec and continuation composition follow the selected-owned-dispatch prototype;
the actual stack and relay-before-pop routines are unchanged retained sources.
The new contribution is their execution on a genuine smaller V/L child input,
return to an occupied parent bank, two sequential sibling uses, and complete
physical scratch retirement. thu-nmrc with substantial OpenAI Codex assistance,
Apache-2.0. All original source notices remain in inputs/.

## Contract

Compile L=2 or L=3. Sixteen physical payload tapes remain fixed, as do one
control tape, one phase-descriptor tape, four BASE tapes and a unary-depth tape:
23 total at every stage. The four BASE tapes are input staging, read-only child-A
grant, read-only child-R grant, and output relay. No execution allocates a tape.
The router uses L+7<=10 of the payload roles; role15 is a distinct empty return
destination. Its fixed port indices are compile-time labels, not data addresses.

Let A_child>=1 and R>=1. The root has A_parent=L*A_child, so its input volume is
V=A_parent*L*R=L^2*A_child*R. Each input bit is arbitrary and all original source
bits remain on the source tape. Canonical positive LSB-first binary A/R values
are actual input tapes. Child A/R grants are also physical read-only inputs;
this module does not compute them from a production descriptor. They must satisfy
the displayed shape relation. The unary-depth input is either empty or one ONE.
Extra depth is rejected: no unimplemented arbitrary recursive grammar is claimed.

Each payload lives after its physical LEFT delimiter, with arbitrary inaccessible
ancestor bytes before it. Input router streams have a logical LEFT, the data or
binary descriptor, and a logical RIGHT; input heads are at the first body symbol.
Empty destination/work roles are at their physical segment origin. Return role15
and both staging/return relays are genuinely empty. There is no role alias.

## Codec and literal table execution

Every router symbol0..6 has its fixed three-bit code, including logical BLANK0
as000 and logical LEFT1 as001. The physical stack alphabet's BLANK6 is distinct
from every code bit and terminates the segment. Unused code111 rejects. Code
reads move three positions forward and back. Writes replace exactly three bits.
A logical unit move costs three physical unit moves. Moving right across an
unwritten logical blank first writes000, so no interior gap can falsely terminate
a live segment. No facade stores an origin, extent, or logical-head coordinate.

execute() follows the original router Program.instructions literally. Its only
runtime state is the finite table PC and finite decoded symbols. Branches read
one facade symbol, writes use one constant symbol, and moves are unit moves.
The fixed L table unrolling never treats a high address or descriptor as a tape
index. The unchanged table's split sends source[a,l,r] to bank_l[a,r], preserving
source, and its merge restores that order. Counts/heads/cell arrays are not
read by the program. Instrumentation belongs exclusively to the tape hardware
and the verification observer.

## One real unequal child boundary

After the root split, bank0 and bank1 are visited at two statically distinct
call sites. Each has A_parent*R=V/L bits. For one site, copy the complete encoded
bank into the BASE input relay. Write the fixed resume phase1 on the descriptor
and use the retained Stack.push with its fixed sixteen-role bitmap. This parks
every actual parent packet, saves heads by physical unary markers, saves the
descriptor, and opens distinct child segments on the same physical tapes.

Copy the staged packet into the child's source port. Copy the physical child-A
and child-R grants into its descriptor ports and erase the input relay. This is
the actual input of the router child, not a host list permutation or a named
address oracle. The child volume is A_child*L*R=V/L and differs from the root.
The now-exhausted depth tape enforces this grammar's one-edge limit.

The child performs the unchanged split table. Its complete bank0 is complemented
bitwise by a sequential finite-symbol routine, and the unchanged merge table
produces the complete child output. This observable leaf is deliberately a bit
fixture; it is not a Gaussian or recursively admitted numerical child.

The retained return_output first copies the whole child output to the separate
BASE relay. Only then does it retire all child payloads, pop the actual physical
continuation, and install the protected result in the empty parent role15.
The parent's occupied bank is not aliased with that empty role. After pop,
consume the restored phase1, explicitly retire the old parent bank, copy role15
into it, and retire role15. Thus replacement happens after the old parent state
and every parent head have been restored. The second static sibling repeats
the same procedure with the same relays/control/backing; the first bank's result
is preserved while the second child is live. There is no host recursion or list
of invocation frames in this runtime.

After both sibling calls the root merge reinstalls all returned banks at their
original full-root addresses. The source input and root A/R descriptors remain
unchanged. The exact endpoint is identity on all root bits except those in the
first internal child bank of root bank0 or bank1, which are complemented. With
depth zero no child is invoked and the endpoint is the split/merge identity.
This description follows the two invertible address maps and the explicit leaf;
it does not infer an arbitrary-input property from a finite numeric sample.

## Preservation, erasure, and resources

The 3-bit codec makes every parent segment a contiguous binary string, even when
it contains logical blank work. The retained stack proof therefore applies to
its actual segment boundaries. A child operates after its new delimiter; no
parent byte is needed or overwritten before the declared pop. Pop recovers the
parked bytes and exact saved heads. The verification hardware independently
rejects child access across that delimiter and checks all parent bytes/heads at
each pop. Its observer snapshots never provide an input, count, address or
branch to the executed program; the unchanged Stack.pop's observer return list
is likewise ignored by the runtime.

After the root merge, all copied bank packets and encoded logical-blank work
are physically erased. All stack frames, phase data, staging and output relays
are blank and rewound. Grant tapes and source/shape/depth inputs are restored.
Only the complete delivered root output remains; the explicit fixture consumer
then retires it when checking subsequent invocation reuse. No owned buffer is
credited as a productive independent target.

The core routers use O_L(V) microinstructions. A coded symbol read/write/move
uses at most10/9/13 physical read/write/unit-move actions. Staging, relay copying,
retirement, unary saved-head headers and push/pop each scan a constant number
of complete packets. Their lengths are O_L(V) for this one-edge contract; the
child packet is V/L and fixed descriptor lengths are no larger than the supplied
positive extents. Two sequential siblings reuse the same buffers. Thus this
composition has O_L(V) physical action count and O_L(V)+K0 visited/backing space,
where K0 is the pre-existing inaccessible ancestor backing. It introduces no
per-depth tape and no free zeroing. RESULT records actual hardware actions,
visited cells and retained backing for the finite controls, not an independently
flattened full transition-table count. The router is literal microcode; codec
and stack routines are the retained sequential physical procedures, not a new
flattened all-production 23-tape microtable.

## Verification and remaining boundary

verify.py authenticates copied source bytes before importing them. It replays
all sixteen four-bit inputs at L2, L2/L3 unequal shapes and nonzero ancestor
prefixes, continuous sibling reuse and a second complete invocation without
backing growth. It also executes a seven-symbol interior-blank push/pop control.
Semantic controls reject pop before output protection, aliasing an occupied
parent destination, an omitted child leaf, unsupported extra depth and treating
logical blank as the physical segment delimiter. Normal and optimized checks
use explicit exceptions and compare a stable RESULT by default.

Still absent: final compiled selected grammar, a generated ancestor-weight and
child-shape evaluator, arbitrary-depth production traversal, the old ordinary
BIT local-space binding, numerical child/precision and full routing/fallback
admission. These costs are not zero. The result completes a concrete physical
boundary fixture and a parameterized one-edge composition argument, not the
repository's entire owned-erasure assumption, a physical supplier, kappa gain,
selected-frontier update, human review or proof-kernel verification.
