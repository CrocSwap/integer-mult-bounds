# Independent written review: fixed-width recursive core

**Verdict: proved conditionally for the stated two-site bit grammar, under the explicitly retained isolated machine/router/shape contracts and owned-growth entry ABI.** The literal static code supports the all-depth address, CALL/RETURN, output-protection and backing-reuse induction below. This is external source-aware written review of an author-claimed theorem, not a new recursion theorem, finite replay, scientific acceptance or supplier admission. No constructor, interpreter, checker, source program, compiler or kernel was executed. The review does not cover the natural-root extension or its prefix cost.

Exact source: thu-nmrc PR6719, head `e4e52d6ba2c805fa78bb57778c3b7bbc064edba5`, repository prefix `research/delayed-cover-physical-batch-routing/`. Core PROOF SHA256 `09e3fcc919afc65fc47a9f1dbe3597320c1a2ff1408e2c1170913ea3a4d72dda`; core `recursive.py` Git blob `af24b2efd2381f080e36eb6b68813e3a64a53022`, SHA256 `0db666747ebcb6633102c7dbfbb51ec9d975aa82bf479668add7c9e4d1a2d5ad`. The round SOURCE-PINS authenticates13 exact objects. I read the core README/CONTRACT/PROOF/code, underlying retained instruction contracts and the narrow `ENTRY-EXCERPT.txt` initialization excerpt. The latter, rather than any observer/result, supplies the explicit physical encoding/layout discussed below. Source author-side proof and AI-assisted evidence were exposed; their runtime outputs are not adopted as this review's evidence.

## 1. Premises and exact entry domain

Fix L>=2, odd q>=3 and N>=1; put b=q^(N*N), so b>=3. For the actual delayed cover, eligibility of q and L=B*|GL_N(F_q)| is an external source premise. The core arithmetic/return argument uses only these fixed integer constants and b>=3. Runtime supplies positive canonical binary w,A0,R0, an arbitrary complete source packet, and a readonly unary depth of d>=0 ones. Assume

`H=b^(w-1), A0=T*(L*H)^d, R0=H*R_body, T,R_body>=1`.

H is computed by the core width prefix; it is not a supplied list of per-node values. The source is a complete packet of V0=L*A0*R0 logical bits. We retain the isolated binary converter, shape producer, router split/merge and machine-instruction semantics as premises, including positive/canonical headers, sufficient blank owned growth, distinct ports, successful head restoration and their stated resource envelopes. This review does not reprove generic converters or admit their native implementation by a finite test.

Every payload tape has an actual physical LEFT delimiter. To its right is a contiguous word over physical Z/O, followed by physical BLANK. A logical packet is encoded three physical bits per logical symbol, including its logical LEFT and RIGHT. Its logical body head is three cells after the physical body origin. Nonpayload tapes instead have a physical BASE delimiter. The initialization excerpt establishes these two marker classes and exact head placement. Payload left prefixes below the current physical delimiter may contain arbitrary retained backing; they are not free or overwritten. All marker-free owned growth used by this invocation must initially be available/blank under the contract.

The core does not create the outer physical LEFT/BASE markers or manufacture the supplied root source/A/R/width/depth packets. Their valid preparation and owned blank growth are explicit entry premises. The invocation time bound starts at this prepared entry; their preparation time is separately required by a complete caller invoice and is not set to zero. K_entry is the retained-space term, not a payment for preparation time.

The codec's logical BLANK is a physical000 triple. It is not an unallocated physical blank cell. Raw retirement must erase these triples, as the actual `retire` helper does, and visited backing remains charged afterward. No malformed-global-store recognition, failure rollback or termination with a missing delimiter is claimed.

## 2. Static role and codec checks

Let K=max(16,L+11). Router roles are banks0..L-1, source L, output L+1, binary A/R at L+2/L+3, unary A/R at L+4/L+5 and conversion work L+6. The new grant roles L+7/L+8 and extra guide L+9 are distinct. The reserved return role K-1 is at least L+10: for L<=5 it is15>L+9, and for L>=6 it is exactly L+10. Thus it aliases neither a grant nor the extra guide. Control, phase, four relays, depth, width and H are K..K+8, outside all payload frames. Tape count is K+9, independent of runtime width/depth.

The shape-port map in code lines220-221 is injective: its three sources are current A, immutable global H and current R; its two outputs are the two grants; its four work ports are distinct router scratch/extra guide roles. It neither sources an old grant nor aliases an original input with an output. The width-prefix map at206-207 is likewise injective. Old isolated helper premises therefore apply at the actual named ports once the blank/head invariants below are established.

`code_write` emits the three bits of the compile-time logical symbol and returns three steps to the same code origin. `code_branch` restores the same origin after reading all three bits; a physically blank origin takes the logical-BLANK branch without moving. Its unused111 code fails. `code_move(+1)` first materializes000 when departing a physically blank logical cell, then makes exactly three unit moves; reverse movement makes three unit moves. Hence logical data remain a contiguous physical binary word rather than leaving physical holes that would falsely terminate a raw copy/retirement. These are source-level finite-control cases, not runtime decoded integers.

`logical` statically labels every old PC, remaps every operand/branch/default/goto, sends every success HALT to the named continuation and sends rejection to the common failure PC. There is no runtime callback. Direct inspection of each lowered instruction gives at most32 physical transitions: branch needs at most nine, write nine, forward move at most thirteen and reverse move three; goto/continuation need one. The bound32 is conservative and includes each lowered control transfer. The proof does not assert a separately regenerated20,897-row table or a runtime replay.

## 3. Raw packet helper lemma

Within a valid local segment, `origin(t,marker)` searches left to its own delimiter and returns one cell right; it never crosses that delimiter. `body` then advances exactly one three-bit logical LEFT symbol. `copy` scans the full contiguous Z/O word from source origin to its first physical BLANK, requiring blank target cells before each write, and returns both heads to their respective origins. It copies the encoded logical markers too, which is required for a transferred source/header packet. It does not replace the independent source with a host-decoded value.

`retire` scans that same complete binary word, writes physical BLANK to every bit and returns to the origin. It preserves the physical delimiter. It clears coded logical BLANK000, logical LEFT/RIGHT and all packet data alike. `body` is used only after a genuine marked logical packet is present, not on an empty raw return role. Global relay/high operations explicitly pass BASE rather than accidentally searching for LEFT.

These helper properties require valid delimiters, complete physical binary segments and sufficient owned target growth. They do not recognize arbitrary corrupt backing. In particular, a missing physical delimiter is outside the theorem, and passing only a decoded-output test would not establish this lemma.

## 4. Physical push/pop lemma, including saved heads

Immediately before push each payload head is within its current segment; all positions from its physical origin to one cell before the head are Z/O. The current segment is a contiguous Z/O word terminated by physical BLANK. The global phase has one bit naming site0 or site1; relays contain the complete selected bank and two freshly generated headers. The reserved return role is empty at its origin.

In `push` (152-170), the control stream appends LEFT, then one fixed presence/tag bit for each of K payloads. For a payload whose origin is o and current head is o+h, its initial move left and scan append precisely h unary O marks followed by Z: the scan counts the h binary positions between the origin and head. It then parks at the first physical BLANK after the complete parent segment, writes a new physical LEFT there and moves one cell right. No parent data/marker is changed. Empty parent segments and h=0 are valid; their appended child delimiter is immediately after the old delimiter. After all payloads, SEP, the complete one-bit phase and END are appended to control, and the local phase is blanked. The control head finishes one beyond END.

At pop entry every child payload is physically blank at its child origin. `pop` (172-196) verifies the top END, finds its matching frame LEFT through only binary fields/SEP, and erases the control record as it consumes it. For each payload it checks the fixed tag, verifies the blank child origin and its immediately preceding child LEFT, erases that child delimiter, then searches left inside the preserved parent word to its parent LEFT. Starting at the parent origin, the saved h O marks move its head right h positions, checking binary content on each departure. It therefore restores **the exact old head**, not merely some packet start. The terminating Z is erased.

The phase is restored from the record, and the control head returns to one beyond the preceding END or BASE. Hence push followed by successful child retirement/pop preserves every parked parent byte and head, the previous control stack and the phase bit. It releases no backing: deleted frame/child symbols become blank but their physical positions remain visited. The reserved-role Z tag is checked consistently in both routines; it is not an unproved claim that the role's tape does not exist.

## 5. Node-entry and CALL/RETURN invariant

At depth j (0<=j<=d), set

`A_j=T*(L*H)^(d-j), R_j=H^(j+1)*R_body, V_j=L*A_j*R_j=V0/L^j`.

The node has canonical physical A_j/R_j at their logical body heads, a complete arbitrary source packet of V_j bits, blank owned banks/output/work/grants/return role, immutable global H at its correct header head, blank relays/phase and depth head j positions from its original unary origin. It reads O iff j<d, otherwise BLANK. The root may have already used two scratch roles for H generation; the explicit raw retirements209 restore the same node-entry blank invariant.

The unchanged split first produces all L private banks of V_j/L bits and restores its source/headers while clearing its scratch. At an internal node j<d, exact divisibility A_j divisible by L*H follows from d-j>=1. Thus the shape call immediately preceding **each** site returns Q=A_j/(L*H) and K_child=H*R_j, from that current frame's A/R and the same global H. It is not a root-precomputed grant cache. The source bank and generated grants are copied to distinct BASE relays; the grants and all physically coded scratch are retired before suspension.

Code228 records the actual fixed site in phase, and230 invokes push. Code231-234 installs complete relayed source/Q/K packets in the blank child segments and retires all three input relays. Code235 consumes exactly one readonly depth position and reenters the same node label. The child therefore satisfies the invariant for j+1, with source size V_j/L and all original high/ancestor coordinates retained. Both sites use this sequence; the second runs after site0's restored parent, not on site0's child headers.

After a child merges its completed output, code246 physically retires its private banks/scratch. For a nonroot node the top-control marker is END. Code250 copies the **actual changed child output** to the separate global output relay, before code252 retires all K child payload segments and before pop253. The output relay is outside those segments and outside pop's payload loop. It therefore survives destruction of the child frame. Pop restores the parked parent and its site phase; moving depth left once restores its old position and checks the O mark that justified CALL.

Code254 copies the protected output to the previously blank reserved parent role and immediately clears the relay. The phase selects the appropriate owned parent bank0 or1; code257-259 clears phase, retires that old private bank, installs the protected result, clears the reserved role and restores that bank's logical body head. Site0 resumes at the independently generated site1 call; site1 resumes at merge. Original source/A/R of that parent are untouched. Every global relay is empty before the next CALL, including after nested returns.

Root completion sees BASE rather than END, restores the control head to its original position, retires H and halts without pop or a spurious depth decrement. This distinction handles depth zero without inventing a parent frame.

## 6. Whole-high address and all-depth endpoint

At a fixed complete parent bank write `a_parent=(a_child*L+l_child)*H+h_child`, with h_child in[0,H). For r_parent in[0,R_j), the exact address is

`a_parent*R_j+r_parent = (a_child*L+l_child)*(H*R_j)+h_child*R_j+r_parent`.

The new inner coordinate `h_child*R_j+r_parent` ranges over all H*R_j=R_(j+1) values bijectively. Thus passing the complete parent bank to the child preserves the fresh high coordinate **and every earlier ancestor/body coordinate inside r_parent**. It removes only the next low label, not a factor H from payload volume. Equality of volumes alone would not prove this address claim. It is the credited whole-high address identity, applied to these actual live descriptors.

Define the semantic endpoint recursively: split all L banks; at remaining depth zero complement every bit in bank0 and leave the other banks unchanged; otherwise recursively transform banks0 and1 using their complete child shapes; then merge all L banks in their original address order. The source's literal leaf240-243 does exactly the base transformation through the codec, including the full RIGHT check and head restoration. It is a bit-complement leaf, not BIT/Gaussian semantics.

Induct on remaining depth d-j. Base zero uses the retained split/merge inverse-address contracts and the literal complement loop; no CALL/pop occurs. For the step, each child has smaller remaining depth, so by induction it returns its exact complete changed packet with its local/relay work retired. The physical push/pop/protection lemma installs only that packet into its corresponding private parent bank and restores the original parent inputs/heads. The untouched banks remain identical. Retained merge then gives the defined full endpoint. Each subtree terminates by the strictly shorter finite unary remainder, and all helper loops terminate on finite valid packets. This proves all finite depths, not an inference from a two-level fixture.

At final halt original root source/A/R/width/depth bytes and heads are preserved, the root output remains a separate owned result, all other owned body/relay/phase/control/H regions are blank, and permanent delimiters/backing remain charged. No newly copied output earns productive credit.

## 7. Time: actual occurrences, not94V for a tree

The retained split/merge contracts charge at most188V_j logical instructions together. There are two source shape generations at an internal node, each with actual guide/packet retirement; the source's deliberately coarse1000V_j allowance is sufficient for each under the current internal-node inequalities A_j>=L*H and H*R_j<=V_j/L^2. Codec factor32 charges these by at most70,016V_j physical transitions. Leaves use fewer operations. Original counter setup and failed terminal tests are included by the isolated premises; no new host arithmetic is substituted into execution.

For the raw continuation work, group loops over all payload tapes by the sum of their participating extents, not by K copies of a largest extent. The listed local streams/output/return, binary headers, guides, work and grants have total coded extent below100*K*V_j, including fixed markers: stream lengths are at most V_j, header lengths at most their positive values, A_j,R_j,H<=V_j, and internally H*R_j<=V_j/L^2. Push's unary saved-head record is bounded by that same sum plus O(K), since each offset lies inside its local word. Global input/grant/output relays hold only complete selected packets/headers of those sizes. These bounds are deliberately loose.

The raw helpers are fixed scan/rewind loops with fewer than128 transitions per participating physical position. A conservative static count below64 aggregate helpers per call site covers bank/grant copying and retirement, four scratch retirements, phase operations, push, three child installations and relay clearances, depth operations, output protection, complete child retirement, pop, reserved-return installation and parent-bank replacement. Each uses at most four scans/rewinds of its participating aggregate extent. For two sites this gives at most512 passes and hence at most6,553,600*K*V_j raw transitions. The loops over K payloads and L banks are already charged by aggregate extents here; this is not an uncharged tape loop. Root/leaf fixed checks fit the remaining slack.

The once-only H prefix has finite-carry multiplication, not a runtime arithmetic primitive: for each digit, x*b+c is assembled into one fixed write/next-state pair; carry stays below b. A binary multiplication/rewind scans at most O(ell(b)*w) logical digits at its largest width. Summing w-1 passes, width conversion and physical retirement costs O((ell(b)+1)*w^2). The elementary bound w^2<=2*b^(w-1)=2H for b>=3 follows by checking w=1,2 and observing ((w+1)/w)^2<=9/4<3 for w>=2. Since H<=R0<=V0, it is charged once to O((ell(b)+1)*V0). Natural-root A/R generation is outside this core.

These explicit loose scan estimates fit the source envelope `C_time=10^8*(K+ell(b)+1)` with ample slack; the principal raw coefficient is6,553,600*K, and codec/root-width terms are much smaller than the remaining10^8 factors. They establish a template constant local charge, rather than deriving a constant by fitting author timings. No20,897-instruction census or measured microtransition total is independently claimed by this written review.

Let T_r(V) be time after node entry with remaining depth r. Then

`T_0(V)<=C_time*V`,
`T_r(V)<=2*T_(r-1)(V/L)+C_time*V` for r>0.

Adding the once-only width prefix yields the stated safe envelope `C_time*V0 + C_time*sum_actual_nodes V_node`, whose actual node sum is `V0*sum_(j=0..d)(2/L)^j`. In particular L=2 gives a depth factor d+1; this is **not** a claim that the full tree always costs94V0 or O(V0). A different final template with c sites must use c, not two, in its own recurrence.

## 8. Space: active chain and physical suffix reuse

At an active depth j, the current local packet/work extents and its parked frame/control record are bounded by a template constant times V_j as above. Global relays take only their maximum currently live payload, not one unretired packet per completed child. The width/H/unary-depth inputs and work are charged to O_template(V0): d<=A0 when d>=1 because A0>=L^d, and w/width work is bounded by H. Their markers are included even when d=0. Previously inaccessible prefixes/input backing form K_entry.

The critical reuse claim is positional. Push appends a child delimiter at the parent's first physical BLANK; successful retirement/pop blanks the entire child body and removes precisely that delimiter. The next sibling appends again at this restored first-BLANK position. Parent packet lengths, headers and returned head offsets depend on the shapes, not payload values; both sites receive equal-length complete banks. Thus siblings reuse the same suffix and do not allocate a new retained block merely because another call completed. The same induction applies at every depth. Erasure does not subtract cells from the visited bill; the proof bounds their reused maximum extent.

Consequently the union of visited/retained local positions is bounded along one active chain by

`K_entry + C_space*V0*sum_(j=0..d)L^(-j) < K_entry+2*C_space*V0`,

with the source's loose `C_space=1000*(K+ell(b)+1)` covering local coded extents, saved-head control words, relays and once-only width work. The strict inequality holds because d is finite and L>=2. Time counts both sibling occurrences, whereas maximum space counts their reused active-chain suffix. Replacing either of these with the other would be unsound.

## 9. Controls, qualifications and remaining work

Useful unexecuted adversarial distinctions follow directly from the invariants: (i) replacing immutable H by current R passes a one-edge shape when R0=H but corrupts grandchildren where R1=H^2; (ii) copying after child retirement/pop cannot preserve a genuinely changed child output; (iii) omitting the CALL right move or RETURN left move misroutes the second sibling or final return; (iv) a missing default relocation is not repaired by a successful-path volume check; (v) freeing backing when symbols become blank invalidates the active-chain accounting. These are written reasoning controls, not newly run source mutations. This review does not adopt author mutation outcomes as its own tests.

The theorem remains conditional on valid packet encoding/blank owned growth and the retained isolated helper semantics/resources. It is source-code proof review, not actual emitted-table equality or execution, malformed-store admission, numeric-resource measurement, machine/kernel formalization or a complete paid invoice. Natural-root T/R_body-to-A0/R0 generation and its price are excluded. The complete child receives all high coordinates, but a shape header does not compute numerical ancestor-weight/Good/Pair descriptors. Two fixed sites and a complement leaf do not implement the final production template, BIT/Gaussian child, route/fallback, stock, precision, compiler, outer input preparation or all five selected assumptions.

Credit thu-nmrc/PR6719 for this author-claimed core, exact code/proof and author checks; Ali Romman/PR5829 for whole-high address and geometric allocator; David Arias/PR2776 for finite machine, assembler and counter; retained stack/codec/output-before-pop and binary-control/R437 authors; PR6722/6725/6727 for the earlier bounded external interfaces. No new exponent, paid profile, kappa or frontier change is claimed. This written audit used substantial OpenAI Codex assistance and is not independent human/proof-kernel acceptance.

## 10. Additional explicit boundary controls (written, unexecuted)

**One-edge validity is insufficient.** Let L=4,H=3,w=2,d=2,A0=24,R0=3. The first grant is positive/integral: A1=24/12=2,R1=9, and its child packet has the correct V0/L volume. But that child still has positive remaining depth and 2 is not divisible by12. Hence the next source producer rejects its grant domain. This root does not satisfy A0=T*(LH)^d for positive integral T; it is a control against weakening the global premise, not a counterexample to the source theorem. The actual natural-root producer could supply the stronger condition, but that separate source implication is outside this audit.

**L=2 requires a depth factor in time.** With w=1,H=1,T=R_body=1 and A0=2^d, each level has total node volume V0=2^(d+1), so the occurrence sum is (d+1)V0. Retained backing still follows the active-chain geometric sum. A proof using the space sum as the time invoice would lose a factor d+1. The healthy source retains both sums.

**Initializer/physical backing boundary.** Missing a required outer delimiter can make an origin scan leave the intended segment; this code is not an arbitrary-store recognizer. Treating the encoded000 triple as physical blank would prematurely stop raw copying/retirement, and counting only nonblank sparse dictionary cells after erasure would lose visited backing. These written distinctions do not assert newly executed failing fixtures. The retained machine's visits set only gains positions during branch/write/unit movement; sparse Tape.cells erasure does not remove those visits.

The coordinator traced the actual source in ROOT-CODE-NOTES before assembling this document. A wording correction distinguishes CALL's right/increment from RETURN's left/decrement; the separately retained original draft remains unchanged. Peer code/adversarial and final assembled reviews are separate evidence. All universal conclusions here are written conditional arguments; no finite source run, new implementation, emitted-table comparison or kernel result supplies them.
