# Source-aware actual-rule audit of the marked DDG reversal

## Verdict, source and exposure

**Verdict: qualified PASS for the stated fixed-graph, two-tape partial-machine contract. No material proof-to-rule gap was found.** The local rules implement the source's delimiter/forward/XOR/reverse/erase path under its entry invariant. This audits Nick Petalas6127's existing construction and tariff; it does not establish a new reversal, count or physical cost.

Exact retained head: `116dbe505704a4aca043364b8cff97580990d6dd`, `petalas/integer-mult-bounds`, `research/marked-tape-ddg-reversal/`. Read as inert text:

| Source path | Git blob |
| --- | --- |
| `PROOF.md` | `5a042f225103a33d7192cdbaa7aa5e9e77d5c4c8` |
| `machine.py` | `ab970cf8ad640fbfdbc9f503bce485ff6750747a` |
| `README.md` | `1d45919d30ee72170bdfd09757d57367edda29d8` |
| `verify.py` | `5e46534753d890330810c1d3c9e44b2b8df2da01` |

The first three were already read during this account's bounded orientation; the verifier was read for this assignment. Historical source exposure and previous6072/6124 context are disclosed: this is not a blind role. No current peer draft was read before sealing. The current canonical7c49 machine blob was separately observed during orientation to match the retained-head blob.

No source/new scientific program, import, compilation, constructor, rule enumeration, sampler/census, test, mutation, numerical experiment, native operation or kernel was executed. Metadata/hash/time operations for this note are not scientific execution. Original controller counts, rule counts, finite test outcomes, mean and payload/tariff numbers remain source evidence. The source explicitly inherits JoyboyBrian6102's phase-and-coin inverse; this note binds that premise to the new machine and does not claim a fresh audit of the predecessor proof.

## 1. Exact entry and machine model

There are two distinct tapes. The first has binary symbols beginning at coordinate s, and its cell s-1 is an owned blank `_`. Cells farther left are protected. The random head begins at s. The second head is stationary on a four-symbol cell A, identified with a two-bit accumulator; all other second-tape cells are spectators. The fixed(1,1) DDG and its finite rule set are chosen before reading the tape. Initial control is ENTRY and successful return control is the fixed HALT label, not a claim that the initial control label is restored.

The source statement uses an infinite binary suffix. The pathwise theorem concerns each suffix whose first DDG output occurs after finite T>=1 bits. No fairness, independence or probability is needed for that deterministic implication. The dirty value A and arbitrary protected/ambient data may be correlated with that suffix. Distinct tapes are a storage-model condition, not a statistical-independence condition; an aliased caller layout is not supplied by this two-tape statement.

A transition reads the control, current first-tape symbol and output symbol; writes the replacement symbols; changes control; and moves the first head by-1,0 or1. The output head never moves. Source rule keys contain only those finite components. Python observer head coordinates, step bounds, counted moves and revisit counters never enter a rule key. No absolute position, elapsed-time counter or growing history controls rule selection.

## 2. Actual local rule families

Use F for tuple controls `('forward',phase,state)`, B for `('back',phase,target)`, and R for `('read',phase,target)`. The state field is the source's literal DDG identifier; leaf identifiers retain their fixed output ordering. Phase is modulo156.

**Entry and marking.** For each binary first symbol and each A, the ENTRY rule preserves both symbols and moves left to PREPARE. The PREPARE rule exists only on `_`; it writes `#`, moves right and enters the fixed root F(0,0). Thus no arbitrary protected cell is overwritten by preparation under a weakened nonblank-entry assumption. This is actual marking, not a marker assumed already present for free.

**Forward.** `forward_rules` reads the resident coin, follows the exact source table edge and moves right. An internal target enters its next F state without changing A. A leaf target i changes A to A XOR i and enters its next-phase B leaf control. Output retention is therefore included in the last forward transition, and it occurs at the source's first output, not after reading a later coin or as an uncharged separate copy.

**Back move.** For every generated phase/target pair, B on either binary symbol preserves both symbols, moves left and enters the corresponding R control. This step inspects the cell immediately after the prefix before moving onto the bit to undo. Its read requirement matters even though its destination does not depend on which binary symbol was seen.

**Reverse read.** `reverse_rules` iterates the source edge `(state,bit)->target` at its known phase and installs

    R(next_phase,target), bit, A  ->  B(phase,state), bit, A, move0.

The credited phase-and-resident-coin inverse makes these keys unambiguous; `add_rule` also rejects duplicate keys. This is how the source inverse is associated with an actual rule, rather than a numerical stopping counter. The output is not XORed a second time during reversal.

**Delimiter return.** The only R marker rule is R(0,0) on `#`; it writes `_`, moves right and returns at HALT. No other R state has a marker rule. A binary symbol in R(0,0) instead follows an ordinary inverse edge. The root control alone therefore never licenses early return.

## 3. Path and frame invariant

After marking, k forward steps place the first head at s+k and put F at the exact source state/phase after k coins, until the source stops. At its first stop T the head is s+T, A is the original dirty value XOR the source label, and B carries the actual leaf target and phase after T.

During reversal, the useful invariant is: after undoing T-k edges, B stores the source state after k edges, its phase is k modulo156, its head is s+k, and the retained output remains A XOR i. For k>0 the next B move shifts to s+k-1. The R rule then reads exactly the resident coin consumed on that edge and the credited inverse restores the preceding state without moving. It reaches B with k reduced by one.

At k=0, B is the root with its head at s. Its left move reaches the marked owned cell s-1. The R(0,0) marker rule erases that marker and returns the head to s. For a positive root revisit after a phase wrap, the preceding cell is inside the binary segment; R(0,0) reads a binary symbol and continues reversing. Thus the delimiter, rather than a phase/root test, distinguishes initial entry. This applies to arbitrary finite T, not just the verifier's bounded fixture depths.

The first-head locations and read region on such a path are contained in the interval[s-1,s+T], and both endpoints are actually read. The only symbol changes on the first tape are at s-1: blank-to-marker and marker-to-blank. All binary values are preserved. The second head remains fixed; only its selected cell is XOR-updated and every other second-tape cell is untouched. Protected first-tape cells below s-1 are never visited. The actual full infinite suffix is consequently unchanged on return, with arbitrary surrounding values preserved.

“Data read-only” here means value preservation in the finite-alphabet transition model. Each transition still carries a replacement-symbol field, and the Python observer assigns that symbol even when it equals the old value. The observer's marker-write metric counts *changes*, not zero-cost physical write instructions. No inference of write-forbidden capability compatibility or a different native read/write tariff follows from these unchanged values.

## 4. The right lookahead is an existing source precondition and control

After the last consumed coin at s+T-1, the terminal forward transition moves the head to s+T. A B rule must read a binary symbol there before moving left. Hence a finite caller must provide at least that readable unconsumed lookahead cell as well as the consumed transcript and owned blank. The source's infinite-binary assumption provides it.

This is already reflected in source validation, not a newly discovered defect. `short_paths` provides ten bits while searching for stops in the first nine; `wrap_paths` appends a guard zero to each terminating prefix. `controls` explicitly rejects the one-symbol fixture `(0,)`, with its comment explaining the extra guard bit for the one-bit termination. These are source-controlled fixtures, not executions performed by this review.

A finite host exposing only T consumed bits is outside the literal machine contract. The lookahead does not add a sampled coin to the DDG output and does not change its first stopping depth; it is a read-position requirement of reversal. Its B transition is already inside the source's coarse step bill.

## 5. One-step injectivity: what the checker conditions imply

The source verifier checks two different facts for every generated rule: every destination control has a single incoming head displacement, and the triples `(destination_control,written_first_symbol,output_symbol)` are unique. These conditions together suffice for global one-step injectivity of this partial machine on any configuration where a rule is defined.

Given a resulting configuration, its control determines the incoming displacement d, hence the previous first-head location is the current location minus d. The written first symbol is visible at that location, and the output symbol is visible at the stationary second head. Their triple selects at most one incoming rule. That rule recovers the prior control, prior symbols and head; all other tape cells were unchanged. Thus at most one predecessor configuration exists. The conditions do not assert totality or that arbitrary malformed configurations can make progress.

The actual families fit this reasoning structurally. PREPARE has only incoming left-moving ENTRY rules. F controls have right-moving predecessors; at F root the prepare-written marker is disjoint from the binary symbols written by recurrent forward edges. Leaf B controls arise from right-moving leaf edges; their output label identifies the XOR inverse on A, while the credited inverse supplies the unique source edge for phase/coin. Internal B controls arise from zero-moving inverse rules; source forward determinism identifies the corresponding R target. R controls have only left-moving B predecessors, and HALT receives only the marker-clearing right move. The marker and binary ranges remain separate. The finite checker is the source's complete verification of all generated instances; it was read but not rerun here.

This one-step property is distinct from the reachable-path induction. It does not by itself establish that an arbitrary initial configuration reaches HALT. The reachable induction proves that for valid entry and finite T, and also proves the endpoint map `(tape,A)->(same_tape,A XOR i(tape))`. That data map is invertible for a fixed retained tape, but no explicit binary reverse program, reverse lookup price or physical cleanup service is inferred. In particular the shared6124 forward quotient's predecessor uniqueness is not established by this fixed graph's rules.

## 6. Source charge association, observer and probability limits

The source step decomposition is consistent with the rules: two preparation transitions; T right-moving forward transitions including the output XOR; two reverse transitions per consumed edge; and the final B-left/R-marker-right pair. This associates the source's3T+4 coarse two-tape transitions with actual rule families. The source's2T+4 movement count includes the two preparation and two final moves plus forward/backward movement for each consumed coin. The greatest right head displacement is T; the left boundary is one cell below s. No new count, measured transition run, mean calculation or controller/rule enumeration was performed.

`execute` is a bounded observer, not the machine's decision procedure: its length/start/step caps, head coordinate, saved initial tape, `Trace` counters and full restored-tuple comparisons observe or bound tests. They do not appear in rule keys. The source explicitly limits this observer's fixture domain and errors on exhaustion. A successful finite replay is not the all-T proof; the rule/path invariant supplies that implication.

The source's expected tariff is inherited from its cited sampler mean. No mean or fraction was recalculated here. Every charged unit is the stated finite-alphabet simultaneous transition, not a binary gate, unit paid scalar call, RAM access or wall-time sample. Converting to another alphabet/machine/native primitive requires a separate implementation and constant.

Pathwise restoration is valid pointwise for arbitrary allowed tape, dirty A and correlated ambient data. Sampling claims require the separate hypothesis of fresh fair bits relative to the conditioning information at the actual caller. Keeping the sampled output can correlate that information with the restored tape. Neither symbol restoration nor erasing the marker supplies conditional freshness, a new random reservoir or authority to reuse it. Existing6096 actual-residue/availability work and6546 numerical caller/inverse work are not declared missing; neither is silently charged into this particular local tape placement.

## 7. Written weakening controls — all UNEXECUTED

1. **Stop on a root, rather than on the marker.** A positive phase-wrap root revisit still precedes binary tape, so early HALT there skips part of the resident transcript and returns the wrong head. The source already includes an altered-rule control for this; it is not a new observed failure here.
2. **Omit the readable lookahead.** A terminating prefix with no following binary cell reaches B outside the finite fixture. The source already rejects the one-bit fixture without its guard. Infinite binary input or a correctly bounded finite extension is required; the sampler's output does not consume that extra coin.
3. **Omit phase or resident coin from inverse selection.** The actual reverse key needs both to identify the predecessor edge, as credited to6102. A root/wrapped phase or wrong-coin substitute is not licensed by mere forward determinism.
4. **Assign the leaf label instead of XORing dirty A.** That loses the arbitrary old output value. The contract is A XOR i, not an output cell assumed zero; checking only zero accumulators could miss this distinction.
5. **Accept a nonblank owned boundary or borrow a protected neighbor.** PREPARE only has an underscore rule. Moving the delimiter into a cell with caller data changes the ownership premise; value restoration cannot be asserted merely because the symbol resembles a marker elsewhere.
6. **Drop the incoming-direction check.** Two rules with the same destination, different moves and different written symbols can pass a written-image-triple uniqueness test yet have preimages at different head locations for one resulting tape. The destination's unique incoming displacement is what identifies the previous write position. Both checker clauses are required.
7. **Drop written-image uniqueness.** Distinct source keys can be made to emit the same target/written/output triple with the same displacement. Unique direction alone then gives two predecessors. The source checks the additional triple uniqueness.
8. **Treat restored symbols as fresh conditional randomness.** With a known zero dirty output, retaining its nontrivial sampled label already reveals information about the tape. Erasing only the delimiter does not remove that correlation. A different correlated dirty mask does not justify a universal freshness claim either.
9. **Transfer the bill to a different graph/alphabet/caller.** A phase-merged quotient can lack the fixed graph's inverse, an aliased output/input layout can violate the frame, and binary lowering has an additional constant. None is certified just by the source's coarse3T+4 equation.

These are deductions about changed rules or hypotheses and existing source control intentions, not new test receipts, new discovered defects or an independent numerical campaign.

## Conclusion and credit

The actual local rule path matches the owned-marker/first-output/restoration contract; the injectivity predicates have a valid global partial-machine interpretation, and the observer does not smuggle a stopping counter into finite control. Exact unbounded path reasoning, existing finite fixtures and complete rule checks remain distinct evidence types. No source correction is requested within this scope.

Nick Petalas6127 retains the marked-tape construction, state/rule inventory and tariff. zxv6072 retains the fixed DDG law/mean; JoyboyBrian6102 retains the phase-and-coin inverse, with6096 and the inverse lineage credited. The6124 forward-sharing and6546 numerical work retain their distinct results. Classical recorded-computation reversal/local finite-state reasoning is not newly invented here. Preserve all source notices and AI-assistance disclosures.

Actual ownership placement, conditionally fresh input, binary lowering, physical dispatch/read/write/coin movement, full error/resource and cleanup bills, native/caller admission, human/formal-kernel acceptance and selected-frontier status remain separate. This is an external source-aware written proof-to-rule audit, not a new supplier, runtime improvement, kappa or adopted frontier result.
