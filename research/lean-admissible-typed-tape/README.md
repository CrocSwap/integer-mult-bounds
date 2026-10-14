# Typed admissible-tape inverse and support composition

This standalone Lean 4.21 source imports only Init. It proves nine reusable facts for dependent, chronological finite tapes. Primitive input/output domain labels must match at concatenation boundaries, while semantic domain membership is propagated from explicit primitive closure proofs.

Forward and undo functions are separate inputs. Whole-tape left cancellation uses only local left inverses plus forward closure; right cancellation separately requires local right inverses plus backward closure. Observable coordinates and primitive write supports are parameters. Forward and undo spectator preservation each use their own domain-restricted primitive support laws. No whole-tape endpoint or spectator equation is assumed.

The source compiled unchanged in 0.458179662 seconds. Independent readback accepted all nine probes and both complete printed types: eight facts have no axioms; touches_append uses only propext. There were no warnings. The run used the official 317-module Init closure, with no retained research objects or Mathlib dependency. Saved source/API and terminal reviews and original raw output/receipt are included. The source header's uncompiled-candidate wording is the preserved pre-check text; these exact bytes subsequently passed.

An application must still bind actual primitive functions, establish initial admissibility and local laws, and interpret observable coordinates and supports. Physical allocation, parsing/lowering, charts, rounded arithmetic and bit cost are outside this generic result. Empty domain predicates do not certify an application.

With Lean 4.21 installed, compile the file directly, for example with lean -j1 -o AdmissibleTypedTape.olean AdmissibleTypedTape.lean. This package includes no installer, inherited archive replay or selected literal table.

Attribution: James Chang with OpenAI assistance, Apache-2.0 under the repository LICENSE. This develops the admissible-domain bookkeeping motivated by Hanson Sun (@bbMisk), PR1530, and the accepted PR590/597 ordered-interpreter reversal interface. Those specialized interpreters and their primitive proofs are not copied or re-proved here. The duplicate screen was bounded to previously reviewed interfaces; no exhaustive novelty claim is made.

Author-checked pinned numerical context: upstream main 0b1cccf86e2f5132ed286a26ef0a681a495740ea records kappa=836330098538459/500000000000000000=0.001672660197076918, with assembly SHA2561122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045. This context is unchanged by the generic theorem and is not a selected multiplication proof or a current publication lease.
