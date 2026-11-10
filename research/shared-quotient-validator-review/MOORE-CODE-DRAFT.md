# Source-aware audit of the shared-bank certificate implementation

## Verdict and evidence boundary

PASS for the source's generated-graph/certificate path, under its fixed ordered-coin, first-stopping and counted-residual-state model. No material proof/code discrepancy or source correction was identified. This is an external written code-association audit of Nick Petalas's existing PR6124 construction and minimality theorem. It does not compute or newly verify the22482-state partition or84578-byte bank.

Source: `petalas/integer-mult-bounds`, exact head `9ae1d82f4e248dd830e32c4d2a0330b62cddc1dd`, directory `research/shared-residue-dispatcher/`. Inert files were fetched again for this audit: PROOF.md blob346ae141ac82ea807b3a0863932766ba4d23280a, dispatcher.py blob2e00e0bfd034e1e3804be1735932c884a1fbae72, verify.py blobe78ac558f4c8f932da14ab2a4890ad7dfaf75f32, README.md bloba02be1c83fec155aa134bc90b19b5f8d7a76c3db. Line numbers below refer to these exact code bytes.

I had already read these files during the earlier session04 orientation scout and participated in B13S3's separate6072 single-graph written audit. That historical/source exposure is reused openly; this is not a fresh blind role. No current-session primary/coordinator draft was read before sealing. No source/new scientific program, constructor, census, mutant, import, compilation, test, numeric experiment or kernel was run. Hash/time/source-byte operations are metadata only. Original counts, refinement histories, packed hashes, finite tapes and five reported source controls remain source evidence, not new executed results.

## 1. Exact graph and input domain

`dispatcher.pair_graph`20–43 requires genuine integers a,b in1..12 and reconstructs the fixed6072 ordered graph. Its increasing output list is equivalent to6072's first-negative subtraction rule: each probability digit is0/1; the initial child rank allocates the consecutive leaf list first, and subtracting its length indexes the survivors. Phase/node enumeration and the known312 count are the predecessor graph's specification, not an additional new result here.

`disjoint_bank`46–58 loops through all144 pairs lexicographically. Each local pending identifier is translated by that table's offset, while all four output codes go to the same final four identifiers. Since each pair has312 states, the offsets give the stated disjoint bank of44928 pending plus4 output states. Only those four observations are identified at this stage; parameters do not silently relabel outputs. The appended output self-loops are proof devices, not extra sampled coin operations after returning a result.

`validate_graph`61–68 enforces at least one pending state, binary rows, genuine integer in-range targets and the four specific absorbing terminal rows. `minimize`84–87 checks in-range genuine integer pending roots and starts exactly the empty-word observation coloring: pending0, then terminal observations1,2,3,4. In the actual caller, roots are the complete144-element tuple made by `disjoint_bank`, not an arbitrary partial subset.

The observed model is deterministic forward behavior on the NEXT ordered coin, initialized by a parameter-selected entry. After entry, all behavior-relevant residual data must belong to the counted state: configuration, phase, node, counters, history, any consulted external register or tape position. There is no free retained parameter oracle, random initial state, coin reorder or output recoding. This is a finite controller-state model, not a lower bound on the control-state count of a machine allowed uncounted work tapes. Preserving a probability distribution alone is a weaker task than preserving the fixed tape function and first stopping depth.

## 2. `refine`: why its missing previous own color is harmless here

For each state s let obs(s) be pending or its particular output. Put P0 equality of these observations. At step h, the actual signature is

    (obs(s), P_h(delta(s,0)), P_h(delta(s,1))).

`dispatcher.refine`71–79 interns exactly that signature, one color appended per original state. It need not explicitly include the state's previous own color. Inductively, P_h identifies exactly pairs with equal observations for every continuation of length at most h. Their new signatures agree exactly when observations agree for the empty word and the two first-bit choices have equal observations for every remaining word of length at most h. Hence the next equivalence is exactly P_(h+1).

This also proves monotonicity: equality for all words of length at most h+1 implies equality for all words of length at most h. The argument depends on the correct P0 and exact prior refinements; an arbitrary coloring is not necessarily refined by the same signature operation.

`ids.setdefault` assigns one consecutive identifier to each distinct tuple, with duplicates retaining their first identifier. Since all original pending states precede all four terminals in enumeration, all observation0 signatures are seen before any terminal observation. The four distinct terminal observations then receive the final four consecutive colors in the original output order. Thus the minimizer's eventual convention “pending codes followed by four outputs” is justified by actual enumeration, not assumed from a generic interning routine.

At lines91–94, equality of consecutive class COUNTS is safe because the partitions refine monotonically on the same finite state set. A strict refinement must increase the number of nonempty classes. Therefore equal counts mean the same relation, even if integer names change. It is equality of partitions, not raw color tuples, that matters. Stability makes transitions on equivalence classes well-defined; any distinct classes already have a finite distinguishing word from the refinement induction.

The16-round cap is not a universal Moore convergence theorem. A graph outside this particular family can require more rounds; the code then raises rather than emitting a false success. The actual source's depth9/confirmation10 figures are inherited declared finite evidence, not rerun here.

## 3. Actual sorted refinement certificate: both gates are necessary

`verify.partition_certificate`30–43 separately reconstructs signatures and sorts state indices by them. For its actual generated history, every before/after tuple has exactly one genuine integer color per graph state, because `refine` appends once per state. The validator's initial history equality establishes P0.

At each sorted equal-signature block, the adjacent check forces all after-colors equal by transitivity. Across adjacent unequal-signature blocks it requires different colors. Adjacent checks alone, however, do not forbid the same color appearing in NONADJACENT blocks. The separate line41 equality

    number of after-colors = number of signatures

closes exactly that gap. Once each signature block is constant, there are as many possible block-colors as blocks; equality of cardinalities forces all block-colors distinct. Together the two tests give the full biconditional

    same new color  iff  same reconstructed signature.

Thus every history row is a true Moore step, not merely an arbitrary refinement or a partial local check. `history[-1]==mapping` binds the emitted map to that certified last row. The final equal-count check then establishes stability with the monotonicity argument above.

The shape/type assumption is part of this actual generated path. This helper is not a complete hostile external-certificate parser: it does not separately validate every intermediate history length/type, and arbitrary extra color entries would invalidate the cardinality proof if allowed. The current producer guarantees the relevant lengths and integer colors; its source is read in this audit. No source JSON/history admission endpoint is advertised or exercised by the normal script. A future external certificate service would need independent typed/shape validation rather than citing this audit for all possible Python objects.

## 4. Quotient construction and complete homomorphism

`minimize`97–105 allocates one row per consecutive color. For every original row, it translates both targets through the final map and requires that all members of the same class propose the same row. Every color occurs, so the quotient is completely filled. It returns translated entries in the same root order. Stable equivalence already proves this consistency mathematically; the explicit code gate independently checks the installed rows.

`verify.quotient_certificate`17–27 then checks:

- map length equals the original state count;
- its range is exactly every quotient identifier;
- original ordered terminal i maps to the corresponding final quotient terminal i;
- every original pending state maps to a pending state, preventing premature zero-bit output;
- each entry equals the mapped original root;
- EVERY original edge, including artificial terminal loops, commutes with the map.

For the generated integer mapping/table/entry types, these clauses imply

    map(delta_original(s,w)) = delta_quotient(map(s),w)

for every finite binary word w, by induction on its length. The observation clauses make observations equal at every prefix. Therefore if one execution first reaches output i after exactly h consumed coins, the other has been pending for all shorter prefixes and reaches that same label at h. They have the same first stopping depth and output, not merely the same final label on selected tapes.

For each infinite ordered tape, either some finite prefix first terminates, in which case both do so identically, or every finite prefix remains pending in both. Thus even the set of nonterminating infinite tapes is preserved pointwise. Almost-sure termination or equal distributions would not suffice for this implication. Artificial terminal self-loops extend observations to longer words; the actual sampler still stops when its first terminal is reached.

`run`59–68 implements this convention: pending start, one bit/edge, immediate terminal return. Its initial-terminal branch is consistent with empty-word observation, although valid mapped entries remain pending. Finite exhaustion returns unresolved with the consumed length. It trusts valid source-built tables, starts and binary sequences; arbitrary malformed-bit/table validation is outside this path. The direct controls use finite tuples, so its final `len(bits)` is defined.

## 5. Reachability and the scoped minimum

`verify.reachable`46–56 is a finite breadth-first discovery. Every state is inserted into `seen` once and appended at most once; valid targets keep the list within the graph. The bounded loop either reaches the current frontier end or processes all graph states. Its final cardinality asserts there are no unreachable states. The original disjoint bank and the installed quotient are checked from their respective complete entry lists.

Any original pending state reached from an entry has a prefix that has not stopped: a path cannot pass through an absorbing output and later reach a pending state. Consequently every final pending residual class has an actual configuration/prefix witness. The complete quotient homomorphism and onto condition give an upper construction with one pending state per such class; source reachability prevents counting inaccessible extra classes in its lower bound.

By the refinement induction, distinct stable classes have a finite continuation with different observations. If two witness prefixes reached the same counted internal state of a deterministic same-function dispatcher, every future continuation would behave the same from that state, contradiction. Thus each different reachable pending residual behavior requires a distinct counted pending state. The four output observations are excluded from the reported INTERNAL minimum; their artificial absorption does not add four pending states.

This proves the source theorem's interpretation of its reported partition, conditional on the actual finite certificate values. It does not independently recount22482, prove ROM byte optimality, minimize among samplers with the same distribution, or bound a machine with additional uncounted registers/tape. A selected parameter may choose an entry, but may not remain an uncounted consulted oracle after entry.

`sharp_separation`81–106 follows a certified P8-equal/P9-different pair down successor classes. At remaining depth d, differing signatures with the same observation provide a child separated at d-1; its selected bit reduces the witness depth. Agreement through8 prevents an earlier observable separation. The final nine-bit `run` comparison checks the extracted witness. The named source states244/8149 and literal111111100 are source outputs not independently computed here.

## 6. Packing and finite controls are accurately scoped

`pack_codes`108–120 checks genuine integer width1..16, a finite code-count bound and genuine integer in-range codes. It starts a zeroed byte array and writes each code bit to its unique little-endian fixed-width position. `unpack_codes`123–134 reads exactly those positions after checking count, width and payload length. Distinct fields do not overlap, so generated code sequences roundtrip exactly; unused high padding bits stay zero under the writer.

`main`148–157 drops the four artificial terminal rows, packs two targets per pending state and the144 entry codes, and compares every unpacked code. With the credited22482 pending states, the fixed15-bit transition payload is ceiling(22482*2*15/8)=84308bytes;144 entries take270bytes, total84578. These are consequences of the reported source count and fixed encoding, not a new partition run or minimum-byte theorem. The last four high transition-padding bits carry no codes. The reader does not reject nonzero unused padding; this is not a claim of canonical hostile binary-packet validation. The generated writer's zero padding is nevertheless correct.

The source's eight-bit tapes and five corruption cases are finite supplementary controls. The every-edge/every-step arguments, rather than those tapes, imply all-depth preservation and minimality. This audit reads their actual code but does not execute or newly certify their outcomes. It likewise does not compare regenerated binary hashes, rerun source CI or claim a physical packed lookup service.

## 7. Discriminating written controls — all UNEXECUTED

1. **Nonadjacent reuse:** sorted distinct signature groupsA,B,C colored0,1,0 pass adjacent inequality checks alone. Their global after-color count2 differs from signature count3, exposing why line41 is necessary. Conversely splitting one equal-signature block fails the adjacent equality gate.
2. **False count-stability premise:** partitionsAB|CD andAC|BD have equal class counts but different relations. A correct P0/history induction is needed; count equality alone on arbitrary colorings proves nothing. A mere global renaming of the SAME classes should not be mistaken for further refinement.
3. **Missing terminal observation:** a pending abstract state with both children output00 and the absorbing00 state can have equal successor signatures if observation is omitted, although their empty-word observations and stopping depths differ. The source observation component and pending-map check prevent that identification.
4. **Wrong roots/output labels:** commuting internal edges alone does not select the required function for every parameter. A wrong entry into a different residual class or an exchanged01/10 terminal map changes some ordered tape even if certain symmetric marginal distributions agree. The explicit entry and terminal clauses are required.
5. **Unreachable padding:** adding an unreachable pending component can inflate a claimed state minimum while preserving every entry's behavior. Onto mapping alone is insufficient for that lower bound if original states were unreachable. Source reachability checks both graphs.
6. **Short tape coverage:** two pending chains can agree on every continuation of length8 and differ at9. The source's complete certificate covers such distinctions; a finite eight-bit comparison alone does not. The cited sharp source witness is not independently executed here.
7. **Hidden residual storage:** one nominal control state plus an uncounted register storing the entire original residual identifier can reproduce transitions via that register. It defeats a claim about nominal control states alone, but not the actual theorem counting all transition-relevant residual information. Persistent parameters, history/clock or tape-position oracles require the same accounting.
8. **Packing control sensitivity:** changing a used payload bit changes a decoded code; changing an unused high padding bit need not. Do not claim arbitrary-bit corruption rejection merely from generated pack/unpack equality. This source path is generated data, not a general canonical binary admission API.
9. **Cap/model changes:** a valid arbitrary graph may need more than16refinements. The source's explicit error is a bounded implementation limit, not an incorrect minimum. Similarly changing coin order, output recoding, a parameter oracle or accepting only equality in probability changes the fixed-function problem.

These are written implications about removed gates/changed premises, not observed mutations, new finite data or claims that malformed hostile certificates were tested. No source code repair follows from the trusted-path qualifications.

## Conclusion, predecessor credit and remaining work

The source construction, actual sorted certificate logic, complete quotient conditions and reachable residual argument jointly justify its fixed-function minimum under the counted-state model. Its22482/84578 and finite refinement/packed hashes remain unreplayed source certificates. No new graph, count or classical Moore algorithm is claimed.

Nick Petalas6124 owns the shared quotient, original certificate and packing construction. zxv6072 owns the ordered-coin graph, law, expected-bit optimum and sharing question; B13S3's distinct written audit is prior context, not recounted here. Moore refinement/residual-state lower bounds are classical. Retain JoyboyBrian's inverse/6102 reversal lineage,6096 actual ABI, Nick6127 counterless fixed-graph work and the original notices/license. Forward merging does not preserve predecessor uniqueness or transfer a reversible cleanup tariff.

Physical parameter selection, lookup, random tape movement, outputs, retained discriminator/stopping cleanup, complete caller bill, all native/ownership/compiler/precision/analytic/outer obligations, human/kernel acceptance and selected frontier remain outside this written audit. No runtime improvement, full supplier, κ, adoption or merge follows.
