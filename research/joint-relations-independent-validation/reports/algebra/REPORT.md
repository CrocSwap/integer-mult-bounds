# Independent joint algebra audits of #5383 and #5387

Candidate: Ali Romman's `4bd6efa51a495a7c7b7754915cf0244e7e60969e`, based on canonical main `1ec1119972c9aefe42525172d07b332fcff81cb4`. Original native word: Cao Yifan's round-three source. This review owns only the algebra packet; ownership/invoice, physical applicability and acceptance have separate reviewers.

The parent extended scope to Dugongue's #5387, head `b1ab650d36f59e5be682a813145b7c67e219e341`. Its literal word is separately checked. This candidate changes the eighth snapshot from event 11306/L288 to 11296/L256 and the eighth zero replacement from 17580/L288 to 17233/L256, all in frame 281; its last surrendered pivot is 261 rather than 288. Equal paid/target histograms do not imply equal word semantics or equal retained domains. No #5383 algebra receipt is inherited for this changed word.

## Execution status

**Both #5383 and #5387 passed separate independent full joint-algebra replays.** `RUN-REQUEST.json` requests root-only serial runs, each with a 300-second wall deadline and 1 GiB memory guard. Source custody's `coordination/SOURCE-READY.json` declares the frozen working bytes ready. No existing package or source was changed.

The first full attempt failed in the independent checker's scalar parser at source event 109: the legal rational SCALE encoding `[2,-1]` carries a negative denominator. This was a checker defect, not a candidate failure. The engine now normalizes the rational sign before validating the power-of-two denominator. Follow-up cheap probes compared addition and scaling against `Fraction` for all 30 scalar encodings present across both source orientations and 1,000 additional signed random cases; all matched. Zero and non-dyadic denominator controls rejected. The failed root-run receipt is preserved; the corrected frozen checker is `3ee4ae79a55188d5abf2306f678179f4aafb799602ffb970fc1bc8f76cb061d9`.

The successful #5383 result is in `RESULT.json`. It replays all 21,449 source backward events with 632 independent logical inputs plus arbitrary center dirt, derives all 16 unrestricted identities and rank-eight pivots `225,227,229,230,241,245,257,288`, then replays all 21,551 candidate backward events on 624 retained independent inputs and 17 arbitrary owned entry inputs. Every retained endpoint/frame and zero owned return passes. All eight snapshots are live simultaneously before the first center. All seven local negative controls reject. The independently counted changed local paid profile is `{1:2193,2:412,3:510,4:127,5:40}`; the source profile is `{1:2201,2:412,3:510,4:127,5:40,8:8}`. This establishes the specified algebra component, subject to the retained physical interpretation contracts.

`RUNTIME.json` records the three root-serial guard receipts; their raw receipt and stdout SHA256 hashes were rechecked in this lane. The initial failed attempt took 0.504773205 seconds and sampled 83,087,360 bytes peak descendant RSS. Corrected #5383 passed in 1.107352950 seconds with 98,623,488 bytes sampled peak; #5387 passed in 1.107757847 seconds with 98,639,872 bytes sampled peak. Both successful runs exited 0 under the 300-second/1024-MiB guard on CPython 3.12.3. These are sampled-watchdog measurements, not cgroup hard memory guarantees. The raw paths and log/receipt hashes are retained in `RUNTIME.json`; the failed receipt is never overwritten.

The exact source decompressed SHA256 is `cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`, raw source SHA256 `7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`. The #5383 candidate decompressed SHA256 is `2aee5e997df99726fc763e510d9cb69fbe4f86114dc8d2cd33ad26c6c462a21d`, raw candidate SHA256 `7883ba0faefc96505bb61ca7312d588fa22dfe2164050c817c1718b8fa28693a`.

The successful #5387 result is in `RESULT-5387.json`. A separate replay of all 21,449 unrestricted source events derives its own 16 identities and rank-eight pivots `225,227,229,230,241,245,257,261`. The full changed word has 21,553 backward events; it preserves its own 624 retained independent inputs and erases all 17 arbitrary owned entry inputs, with the same independently counted paid histogram and seven rejecting local controls. Its eighth unrestricted center delta, in frame 281, is minus one quarter of

```
h225 - h257 + h259 + h261 - h263 - h268 + h269 + h270 - h271
 - h324 + h326 + h328 - h333 - h384 - h388 + h390 + h391 + h392 - h397.
```

The actual saved row comes from L256 after source event 11296; its later unrestricted row at event 17233 is the negative of this center delta. Consequently #5387 retains arbitrary L288, whereas #5383 makes L288 an owned dependent pivot and retains L261. This is a real algebra/domain difference despite their common invoice. The #5387 decompressed word SHA256 is `9aa0d7112b4e13f1aa13a93dab0af6f4435ffe99b842aad841685becdafee492`, raw SHA256 `6412632c28e265597fb088087048091d81c19500fb28a0c9c9d2a48f61b8665b`. Both results bind the corrected frozen checker hash above. Dugongue receives credit for the #5387 modified word/compiler-margin contribution, alongside Ali Romman's credited predecessor mechanism and Cao Yifan's source word.

Executed cheap prechecks under a 15-second CPU/wall limit and 128 MiB address-space cap:

- Python syntax parsed successfully.
- 1,000 deterministic dyadic row additions agreed with a separate `fractions.Fraction` implementation.
- Free-generator inverse cancellation worked; distinct generators remained noncommuting.
- Literal delta decoding found 62 preparation events, eight snapshot captures, eight center replacements, eight later zero replacements and eight final pivot clears. All eight snapshot captures precede the first center replacement.

`probe_engine.py` and `PROBES.json` retain a reproducible version of the final cheap arithmetic checks: 2,060 exact addition/scaling comparisons, all 30 actual signed source encodings, the three invalid-denominator rejections, free inverse/noncommutation checks and alternate-pivot reduction. The saved probe ran successfully under the same hard 15-second/128-MiB limits. The separate literal delta decoding was read-only inspection; the full science receipts repeat and enforce it.

## Independent method

`check_joint.py` imports no author checker, native interpreter, expected `RESULT.json`, `VERIFY.json`, relation basis or `WITNESS.json`. It reads only the actual original and candidate word JSON. It decodes their chronological correspondence: every original event is retained in place except the named center/zero replacements, and every insertion has an exact position and frame. This is stronger than comparing separate operation-kind subsequences.

The new row engine represents each register as integer numerators over a common power-of-two denominator. Terms are pairs `(independent input, reduced free operator word)`. Row addition uses integer arithmetic and normalization; warp action prefixes a signed generator and cancels only its adjacent inverse. This is separately implemented from the author's dictionary of per-term Fractions and predecessor interpreter.

An unrestricted source replay retains all 632 independent logical inputs and arbitrary initial center dirt. At each literal snapshot and center it records the full formal row. The center-minus-snapshot rows are derived from those actual rows, rather than read from declared relations. They must contain only scalar cold helper inputs. At the actual later zero sites, the unrestricted row must equal the negative of its matching center delta. Eight exact source differences plus eight later rows give the 16 identities.

A conventional exact rational matrix reduction of the eight derived rows determines the common rank and canonical reduced pivots. A second elimination with the actual prepared pivot columns first checks that those chosen columns have full rank and derives their unique assignments. The emitted preparation must equal these independently derived assignments. Thus a valid alternative pivot choice is allowed; no declared author relation or basis is accepted as an oracle. No pivot is allowed to occur on another pivot's right-hand side; all nonpivot coefficients must be dyadic. These checks establish simultaneous preparation for arbitrary nonpivot inputs, rather than assuming that eight separately valid substitutions commute. A cheap separate probe checked matrix reduction with two different valid pivot sets.

The changed backward program is then replayed on all 624 retained independent inputs plus all 17 arbitrary owned entry inputs: eight helper pivots and nine C registers. Every scalar frame, paid transition, native warp, zero replacement, retained endpoint and final frame is checked. Owned fields must return zero. The forward literal program and all canonical frames/operators must match the original exactly; no new forward semantics are claimed by this checker.

## All-column lift

A formal row is a finite sum of rational coefficients multiplying reduced words acting on independent vector inputs. For any positive width, assign each generator its actual source tensor-power operator and its inverse the inverse operator. Evaluation respects concatenation and adjacent inverse cancellation, so every formal free-word identity remains an identity of operators at that width. Rational coefficients stay outside evaluation. In particular, the argument never distributes a tensor power over a sum.

The pivot preparations use same-frame scalar linear operations, so setting their eight scalar relations to zero imposes the corresponding vector relations on entire payloads. Their independent reduced pivot system leaves the 624 other payloads arbitrary. Same-frame COPY then substitutes exactly the derived source value, and a complete zero vector is fixed by the removed linear Gaussian transition. Chronological preservation follows through each unchanged event. This argument is conditional on the retained native realization and allowed owned-erasure assumptions; it does not establish those assumptions afresh.

## Controls and limits

The planned full run contains local exact controls for a wrong preparation coefficient, sign, pivot, snapshot, COPY gauge, zero row and missing independent relation. These test the independent derived algebra or literal frame contract. An independent falsifier has been given the direct in-memory replay entry for stronger changed-program controls, including arbitrary owned dirt; their receipts are separate.

No source absolute-phase lowering, finite physical tape execution, all-size compiler theorem, pricing/outer inequality or Lean proof is performed here. Source phase and physical interpretations remain inherited assumptions and independently assigned reviews. Algebra-only success must not be described as complete conditional admission.

The low-level `replay` entry is an algebra-and-frame engine, not a standalone validator of every admissible physical scalar recipe. In particular, its SCALE action accepts algebraic dyadic rationals beyond the unit-power-of-two physical SCALE grammar. For the two fixed audited words, the full `decode_edits` chronological source binding and independently derived preparation equality prevent any such extra opcode from being introduced: retained SCALE operations are literal source operations and all new preparation scalars are the checked ADD/CLEAR assignments. The pricing review separately checks the physical scalar allowance grammar. The falsifier identified and bounded this interpreter-interface limitation; it is not a candidate defect.
