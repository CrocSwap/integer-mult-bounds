# Review of the literal marked-tape reversal and its frame

**Verdict: no material proof-to-rule gap found under the exact source entry contract.** Nick Petalas’s PR #6127 implements its stated dirty-XOR endpoint on every terminating path of the fixed `(1,1)` paired DDG. This is an external written audit of that existing construction. The reversal, source tariff, controller/rule inventory, finite fixtures and expected mean are not new results or freshly executed evidence here.

The original head is `116dbe505704a4aca043364b8cff97580990d6dd`. Exact core blobs are PROOF `5a042f225103a33d7192cdbaa7aa5e9e77d5c4c8`, machine `ab970cf8ad640fbfdbc9f503bce485ff6750747a`, verifier `5e46534753d890330810c1d3c9e44b2b8df2da01` and README `1d45919d30ee72170bdfd09757d57367edda29d8`; all match canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Eleven exact inert source/context/license objects and their nineteen canonical provenance bindings are retained. No source import, constructor, rule builder, observer, verifier, finite control or proof kernel was run.

## 1. Exact domain and inherited facts

The first tape has a binary suffix starting at position `s` and a caller-owned blank `_` at `s-1`. Its head starts at `s`. Positions below that boundary are protected. A distinct second tape has a stationary head on an arbitrary dirty four-symbol accumulator `A`, interpreted as two bits. Other second-tape cells are spectators. Distinct storage is required; statistical independence between tapes or ambient data is not needed for the deterministic endpoint.

The fixed graph is zxv’s PR #6072 `(1,1)` graph. JoyboyBrian’s PR #6102 phase-and-resident-coin inverse is a credited premise, retained in the source vendor context. The graph law, mean and inverse are not independently audited again here. At each graph edge the previous phase, resident binary coin and current target identify the unique previous node. Terminal phase annotation matters: the literal machine stores the **next** phase with its target, so the previous phase is recovered by subtraction modulo 156. Using a parent-phase annotation instead is equivalent only after that explicit convention change.

The theorem is conditional on a first source output after a finite `T>=1` consumed coins. It is not a total-halting theorem for every infinite binary string. Fairness and conditional freshness are separate premises for probabilistic applications, rather than requirements for this pathwise implication.

## 2. Every actual rule family has a role in the invariant

`build_rules` uses the fixed graph/phase layout and four accumulator symbols. Rule keys contain only finite control, current first-tape symbol and current output symbol. Python observer positions, elapsed steps and counters never enter those keys.

- `ENTRY` on a binary symbol preserves it and moves left to `PREPARE`.
- `PREPARE` is defined only on the owned blank; it writes `#`, moves right and enters `F(0,0)`.
- `forward_rules` follows the exact source edge, preserves the coin and moves right. An internal target enters its next-phase `F`; a leaf enters next-phase `B` while applying `A -> A XOR label`. Retention is part of that last forward transition.
- A `B(phase,target)` rule on either binary symbol preserves both symbols and moves left into corresponding `R` control.
- An `R` rule on the resident coin applies the credited predecessor edge, preserves the symbols and enters the previous pending `B` without moving. Duplicate keys are rejected when the source builds the rules. The leaf output is not XORed a second time.
- Only `R(0,0)` has a marker rule. It changes `#` back to `_`, moves right and returns at the fixed `HALT` label. A binary symbol at the same root control instead follows an ordinary predecessor rule.

Successful return is therefore `ENTRY -> HALT`, with restored tape heads and data except the specified XOR output. It is not literal restoration of the initial control label or a free `HALT -> ENTRY` reuse wrapper.

## 3. The all-finite-path induction covers wrapped roots

After marking and `k` forward edges, before the first leaf, control is the actual source state/phase after those edges and the first head is at `s+k`. The first leaf at depth `T` leaves `B` holding its target and next phase, the head at `s+T`, and the accumulator equal to its original value XOR the leaf label.

The reverse invariant uses `k` as a proof index, not stored machine data: after undoing `T-k` edges, `B` holds exactly the source state after `k` edges, phase `k mod 156`, head `s+k`, unchanged coins and retained XOR output. For `k>0`, the left-moving `B` rule reaches cell `s+k-1`. The stationary `R` rule reads the resident coin used on that edge and the credited inverse yields the exact source state after `k-1` edges. This establishes the invariant with one fewer edge.

For `k=0`, the head is `s` and `B` is the root. Its left move reaches the owned marker at `s-1`; the marker return clears it and restores head `s`. At a positive-depth root/phase-zero revisit, the cell on the left is still a binary coin, so reversal continues. The spatial marker, rather than equality of root controls or a hidden stopping counter, determines the actual boundary. No finite fixture depth substitutes for this induction.

## 4. Exact read, value-change and frame footprint

On a valid terminating path, the first head visits and reads exactly within `[s-1,s+T]`, including both endpoints. Its only value-changing first-tape writes are the two marker changes at `s-1`. Every binary coin and the unconsumed lookahead are preserved. Protected cells below `s-1` are never accessed; neither are cells beyond `s+T` on this path. The output head never moves and no other output cell is accessed. The selected output may remain numerically unchanged when its XOR label is zero; the contract is the XOR operation, not a claim that its value necessarily changes.

The first reverse `B` rule reads at `s+T` **before** moving left. Thus a finite caller must supply a readable binary cell beyond the last consumed coin at `s+T-1`. This cell is not an additional DDG draw and does not change `T`, but it is part of the literal machine’s access domain. The source’s infinite-binary suffix supplies it. A finite service offering only the consumed prefix does not satisfy this invocation contract without a guard or a separately specified adaptation.

That qualification is already present in source controls: `short_paths` provides ten bits for stops in the first nine; `wrap_paths` appends a zero to each terminating prefix; and `controls` rejects the single-bit `(0,)` fixture that lacks the guard. These are read source intentions, not newly run controls or a newly discovered defect.

The marker need only be unique in the traversed binary/owned boundary region. Arbitrary markers in protected ambient cells cannot affect the run because those cells are never visited. With a passive frame extension, surrounding data may have any admissible values and any correlations with tape/output; the deterministic rules still leave that frame unchanged.

The source transition model includes a replacement-symbol field even when old and new symbols agree, and the observer performs a same-symbol assignment. “Read-only coins” means **value preservation** in this model. The observer counts marker writes by changed values. Nothing here proves zero physical write attempts under an unrelated write-forbidden capability or a zero-cost read/write service.

## 5. Endpoint invertibility is separate from one-step reversibility

On a valid terminating data configuration `x`, write `i(x)` for the source leaf. The endpoint is `(x,A) -> (x,A XOR i(x))` with fixed entry/exit ports. It is pointwise bijective on that data domain because `x` is retained and XOR is a bijection for every fixed `x`. This remains true for arbitrary dirty `A` and ambient correlations. It does not assert that an arbitrary malformed machine state returns, or that an endpoint injection alone proves reversible local implementation.

The source’s `check_local_injectivity` checks two clauses on every generated rule: all rules entering a given destination control have one common head displacement, and triples `(destination control, written first symbol, output symbol)` are unique. Together these suffice for global **one-step injectivity of the partial transition relation**. From a resulting control one knows the incoming displacement and hence the prior head/write location. The symbol at that location and stationary output symbol give the unique incoming rule triple. That rule recovers the previous control and overwritten symbols; all other cells were unchanged.

The actual families match this condition structurally. `PREPARE` is entered by left moves; `F` by right moves; `R` by left moves; internal `B` by stationary predecessor updates; leaf `B` by right-moving leaf updates; and `HALT` by the right-moving marker return. At recurrent `F(0,0)`, prepare’s written `#` is disjoint from the binary symbols of ordinary incoming forward edges. The credited inverse and dirty-XOR permutation recover forward inputs; forward determinism recovers inverse-rule inputs. Marker and binary ranges remain disjoint. The complete finite rule checker’s reported success and inventory remain source evidence, not a replay by this review.

Both clauses matter. For example, two altered rules can enter one control with different moves and different written symbols. Their image triples can be distinct, while a resulting tape has each required written symbol at the respective prior head location; two predecessor configurations can then share that result. Unique incoming displacement rules this out. Conversely, unique displacement without unique image triples allows two old keys to merge at the same prior position. These are written, **UNEXECUTED** weakening arguments.

## 6. Coarse charges and probability remain in their source models

The source’s charged decomposition associates with actual rules: two preparation transitions, `T` forward transitions including leaf XOR, two reversal transitions per consumed edge, and the final `B`-left/marker-return pair. This explains the existing source expressions `3T+4` finite-alphabet transitions and `2T+4` first-head moves. It is an association of an existing all-path charge proof, not a new tariff, enumerated inventory or measured run. No expected fraction or bound was recalculated.

`execute` is a bounded observer. Its fixture lengths, saved initial tuple, start coordinate, maximum-step cap and `Trace` fields observe tests; they are not the partial local machine’s decision procedure. Its errors on exhausted fixtures do not refute the infinite-binary contract. Its finite cap and successful tests also do not establish the all-`T` theorem without the induction.

All charged units are simultaneous two-tape finite-alphabet steps. They are not binary gates, native scalar calls, unit RAM accesses or wall-clock speedups. A fixed controller and one owned delimiter do not bound the total resident random transcript or unbounded head excursion. Binary lowering, physical placement/access and caller/native integration need their own complete bill.

Pathwise correctness uses no fairness. Sampling law and conditional expected-cost conclusions require the appropriate fresh fair input relative to the actual caller/ambient conditioning information. With a known zero output, retaining a nonconstant sampled label reveals information about the tape even though its symbols are restored; replaying the same prefix gives the same label. If dirty `A` is itself correlated with the tape, the resulting accumulator’s distribution need not equal the clean-output law. Neither the XOR endpoint nor marker erasure supplies fresh independent randomness.

## 7. Scope, controls, exposure and remaining work

The abstract first draft has eight written weakening controls; the source-aware rule draft has nine. Their overlapping deductions are not seventeen independent experiments. All are **UNEXECUTED**. They cover missing lookahead or owned blank, premature root halt, lost phase/resident coin, dirty-output overwrite, missing direction or image uniqueness, lost transcript, conditional-freshness confusion, endpoint versus local reversibility, and transfer to a different graph/alphabet/caller. Source control intentions retain source credit; no source defect is asserted from a changed premise.

The known-target abstract role sealed before opening current source/peer; the source-aware role separately sealed before peer reading, with prior scouting disclosed. Root’s earlier scout/body exposure and informal reasoning are also disclosed. Source/peer and exact assembled-version checks follow the seals. These are substantial OpenAI Codex written roles, without blind, human or kernel acceptance.

Nick Petalas owns PR #6127’s counterless protocol and tariff. zxv owns #6072’s graph/law/mean with disclosed assistance; JoyboyBrian owns #6102’s credited edge inverse and #6096’s actual ABI/window work. Classical recorded-computation reversal and the retained source/native/compiler lineage keep their credit, original notices and licenses. Existing #6546 numerical joining is not declared absent. A forward-equivalent #6124 shared quotient need not preserve the inverse premise and does not inherit this reversal or tariff.

Original formal/kernel acceptance is unmet. Source numeric counts, fixtures, means and historical CI are not freshly certified. Actual owned blank/head/guard placement, conditional freshness, selection/access/movement, binary lowering, native/recursive implementation, full invoice/error, owned erasure, compiler, precision/tape, analytic recovery, outer assembly, full supplier and all five selected assumptions remain obligations. No κ/frontier/adoption or merge change follows.
