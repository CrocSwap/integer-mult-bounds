# External review of the generated-grant/router fixed jump

Source: thu-nmrc PR6719, exact head `3bad39ffd4faf7e8cb1bc5b47769cbb28511f797`, `shape/producer.py:linked_split`, its isolated producer contract, unchanged `core/router.py` and retained `machine.py` grammar. Prepared by ToikY with substantial OpenAI Codex assistance. Apache-2.0.

**Verdict: no gap found in this linking implication under the isolated component contracts below.** The source-to-source linker has a valid injective tape renaming and PC translation for every fixed L>=2. The delivered grant ABI matches the actual child router, and exactly one parent-bank input has its claimed child addresses. This is a written source-code proof audit. No source constructor, emitted table, interpreter, scientific checker or proof kernel was executed. It is not an independent execution certificate or approval of PR6719's complete arithmetic, physical or resource claim.

## Premises and exact boundary

Fix L>=2 at compilation. All L+11 roles denote genuinely distinct physical tapes; supplying aliased host Tape objects under different indices is outside this hardware contract. A,H,R are positive canonical LSB-first binary marked input tapes, heads at1, with L*H dividing A. The isolated nine-port producer successfully returns A_c=A/(L*H), R_c=H*R on roles3,4, with LEFT0/body1.../RIGHT and heads1; preserves inputs0,1,2 and their heads; and leaves scratch5,6,7,8 blank with heads0. Its output and scratch regions start genuinely blank at0. Every successful halt reachable from a valid input must satisfy this exit ABI; correctness at only one nominated halt would be insufficient because the linker replaces all halts. Correct arithmetic, input validation, unary conversion, all-size running-time/space bounds and rejected-input cleanup are inherited component obligations, not proved here.

The isolated split router on L+7 roles is a valid retained Program. Its banks are0..L-1; source is L; unused split-output is L+1; positive binary repeat/block inputs are L+2,L+3; unary repeat/block and binary work are L+4,L+5,L+6. On a marked source of exactly a*L*r arbitrary bits and inputs a,r, with blank destination banks/scratch at0, it preserves source and descriptors, returns source/destination/descriptor heads1 and its scratch blank at0, and sends each source bit[a,l,r0] to bank_l[a,r0]. The router/counter correctness and opaque-bit protocol are premises; the linker is not used to infer their validity.

The retained machine grammar has exactly six tags: branch, write, move, goto, halt and reject. Valid Programs have finite in-range targets; write/move have a valid following instruction. Branch follows either its matching symbol target or its explicit default, write/move advance PC by1, goto selects its target, halt stops and reject terminates exceptionally. This is the machine source's specified semantics, read as inert text.

The linked entry state additionally contains ONE parent split bank as a marked, arbitrary-bit packet on role L+9, with head1 and A*R bits; roles9..L+8 begin blank at0. Role L+10 is the declared spare split-output port and is unused by the split body. This audit does not generate or stage that source packet. It proves the linkage assuming that stated physical entry contract, not volume alone or an arbitrary source length.

## 1. Tape renaming is total and injective, including L=2

The exact source dictionary implements:

| Router role | Linked role |
| --- | --- |
| bank j, 0<=j<L | 9+j |
| source L | L+9 |
| unused output L+1 | L+10 |
| repeats input L+2 | 3 |
| block input L+3 | 4 |
| unary repeats L+4 | 5 |
| unary block L+5 | 6 |
| binary work L+6 | 8 |

The original domains partition0..L+6. The images are the distinct set {3,4,5,6,8} and the interval9..L+10. Thus the map is total on every valid router tape index, injective, and contained in0..L+10, the linked L+11-tape inventory. None of original producer inputs0,1,2 or retired spare guide7 is an image. There is no hidden overlap between an initial bank key and dictionary.update's other keys, because the banks stop at L-1 and those keys begin at L.

At L=2 the banks are9,10, source11 and unused output12, with inputs3,4 and work5,6,8. This includes the case where the original router's source role2 would numerically coincide with a producer input if it were not renamed. Larger L changes the finite table/inventory, not a runtime tape address. No runtime A,H,R, bit length or depth enters this dictionary.

## 2. PC translation covers default branches and implicit successors

Let the valid producer and router row counts be s and t, and their entries p and r. Both are nonempty. The linked row count is s+t and its entry is p. The source preserves every producer row at its original index except that every producer halt becomes goto(s+r), without adding or removing a row. Producer branch/goto targets consequently stay valid in0..s-1. Producer write/move successors stay inside that interval, because the original Program rejects a last-row write/move. A producer reject is unchanged. There is no accidental fallthrough from the producer's last row into the router: only the declared successful-halt replacement crosses the boundary.

For each router row j, the linked PC is s+j. The branch case renames its scanned tape, preserves each symbol, and adds s to EVERY explicit target and the default. A goto adds s to its sole target. All translated targets lie in s..s+t-1. A write/move renames its tape and keeps its symbol/direction; its implicit next PC is s+j+1, which is exactly the translated original successor and remains in range. A halt or reject has no tape or PC operand, so leaving it unchanged is correct. No other tag is allowed by the retained grammar; the source else branch cannot hide an unrelocated control-transfer instruction under that premise.

This establishes a step-for-step correspondence between router states and linked states after the successful jump: PC translates by s, and each router tape/head is identified with its renamed linked tape/head. Branches, including default paths, see identical symbols. Writes and unit moves preserve the correspondence; halt and rejection have the same outcome. Extra linked tapes are untouched. No host callback, decoded shape, coordinate or runtime computed jump is introduced by this transformation.

The producer phase has the analogous correspondence at untranslated PCs, except that its success halt dispatches exactly once to the router entry. Rejection before success never dispatches. The same proof covers every finite run prefix and every valid fixed-L compilation; it does not infer validity from a grid of small L executions.

Under the SAME one-instruction-per-transition counting convention, replacing the producer halt by one goto has the same cost. A successful linked run therefore has exactly T_producer+T_router transitions, when each isolated count includes its halt. Read/write/unit-move counts add under the renaming. Visited cells are a union of the two phase footprints, so scratch reuse does not demand their sum as extra simultaneous storage. These are conditional composition facts, not an independent proof of either component's numeric bound or of the source1000V/100V/codec/stack bills.

## 3. The actual boundary state satisfies the router ABI

The producer only touches roles0..8. Hence the preloaded source role L+9 and initially blank banks9..L+8 are unchanged throughout the producer phase. On producer success, generated A_c,R_c are already marked positive binary words on3,4 at head1. Those are exactly the renamed router repeat/block inputs, not values supplied to an interpreter by a decoded host integer.

The router's work roles map to5,6,8, which the producer has genuinely erased and rewound to0. It can install its own LEFT markers there. In particular an old unary H guide on role6 is not reused while live; the premise is physical erasure before the jump. Role7 stays erased and unused. Fresh bank roles remain blank at0. Router input/source roles are distinct from its outputs/work and original parent headers.

The required source length is

    A_c * L * R_c = (A/(L*H))*L*(H*R) = A*R.

All factors are positive integers by the divisibility premise. This is the supplied one-parent-bank length. If V=L*A*R is the parent's full volume, the child input has V/L bits, not V. Each new child bank has A_c*R_c=A*R/L bits. The isolated router's source/descriptor preservation then preserves linked source L+9 and generated grants3,4 at head1, leaves its work5,6,8 blank at0, and returns every child bank9..L+8 at head1. Original headers0,1,2 and retired guide7 are excluded from the router map, hence unchanged. The spare L+10 is not secretly a delivered bank.

The grants and copied banks are owned data, not free productive targets. Their later retention/merge/retirement is a separate caller obligation; this audit does not validate retire_delivered, the codec GrantBridge, continuation pop or production reuse.

## 4. Exact high addresses, not just equal volume

Write each parent repeat index uniquely as

    a_p=(a_c*L+l_c)*H+h_c,
    0<=a_c<A_c, 0<=l_c<L, 0<=h_c<H.

Existence and uniqueness follow by Euclidean division first by H and then by L, since A=L*H*A_c. For 0<=r_p<R define r_c=h_c*R+r_p. Then 0<=r_c<H*R=R_c and

    a_p*R+r_p = (a_c*L+l_c)*R_c+r_c.

Conversely, r_c uniquely determines h_c,r_p by division by R. Thus every position of the supplied parent bank corresponds bijectively to the actual child tuple (a_c,l_c,r_c), preserving the complete high field and all remaining coordinates in their original linear address. The child's split only separates l_c; it does not transpose h_c into another bank. This is Ali Romman's retained whole-high map, checked here only for this literal stream/descriptor interface.

## 5. Written interface scope controls, no executable tests

- **Default relocation matters.** A complete written control has producer rows [goto2, halt, halt], entry0, so s=3; router rows [branch(tape0,{BLANK:0},default1), reject(default)], entry0. Let the renamed scanned tape contain ONE. Correct relocation reaches linked row4 and rejects. If only the default remains untranslated, linked row3 instead jumps to producer row1, now goto3, and loops between3 and1. All original toy targets and producer successors are valid, and both producer halts are replaced. Translating named cases alone is insufficient; the actual source translates both. This toy is hand-derived and was not constructed or executed by a program.
- **Implicit successors matter.** Translating only explicit jumps does not prove a linker correct. Here write/move row order is unchanged and the original Program's successor constraint proves s+j+1 remains inside the router piece. A new tag carrying a target would require a new relocation case; the six-tag premise is essential.
- **Roles must remain disjoint.** Mapping the router unary block and repeat guides both to5 violates the injective renamed-state relation and the two-live-guide ABI; a tape-count inequality alone would not rule out that alias. The actual map uses5 and6.
- **Same volume can still mean wrong addresses.** Take L=2,H=2,A_c=1,R=1, hence A=4,R_c=2 and source offsets0..3. The correct child low index is floor(a_p/2) mod2: 0,0,1,1. A stale low classifier a_p mod2 gives0,1,0,1 at the same total length. In particular offset1 belongs to childbank0, not1. The actual high-address equation selects the former classifier.
- **The full parent stream is not this child source.** Passing V=L*A*R bits rather than A*R would violate the isolated router's exact source-end requirement for these generated grants. This audit assumes the one-bank marked source, not a zero-cost parent-to-child staging theorem.

These are hand-derived semantic checks of the stated proof boundary, not machine-run mutant or first-execution receipts.

## Credit and remaining work

The emitted producer, linked router and new child-grant implementation belong to thu-nmrc PR6719 with substantial OpenAI Codex assistance. Ali Romman PR5829 supplies geometry, complete-high address law and allocator lineage; David Arias PR2776 supplies the exact machine, assembler and binary-to-unary framework. Mason Hale and retained codec/stack/return authors, Jose Manuel's selected-binary-control and the binary-divisor lineage retain their source-specific contributions. Original notices and immutable source pins remain preserved. Typed renaming/simulation, Euclidean division and integer identities are classical tools; no new generic arithmetic theorem is claimed.

Remaining: isolated producer/counter/router correctness and all-size bound review, literal constructor/table execution, consumer/codec/GrantBridge/stack protection and return, H-from-width, generated ancestor weights/descriptors, arbitrary-depth production, routes/fallbacks, Gaussian children, precision/stock/tape/compiler/outer application, and all five framework assumptions. No complete physical supplier, new paid tariff/kappa, frontier change, human review or proof-kernel acceptance follows.
