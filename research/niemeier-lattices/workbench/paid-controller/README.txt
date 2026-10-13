Paid-controller research replay
===============================
These files retain conditional helper budgets and scoped obstructions.
They do not supply a complete native word, compiler admission, or improved
kappa. The original comparison is PR592's declared historical frontier,
0.001612719427075359; later endpoint experiments pin PR600 separately.

From the checkout root, run:
  python3 -I -O research/niemeier-lattices/workbench/paid-controller/verify_portable.py --workspace /path/outside-checkout/paid-replay
  python3 -I research/niemeier-lattices/workbench/paid-controller/verify_portable.py --normal --workspace /path/outside-checkout/paid-normal

The workspace argument is optional; its default is a fresh temporary
directory. The scripts use only the Python standard library. Child scripts
read NIEMEIER_WORKSPACE and write generated receipts and logs there. They
never overwrite these frozen JSON files. The verifier compares every JSON
field, pins the inherited cost engine, and rejects workspace locations
inside the checkout. All checks in the replayed scripts use exceptions and
remain active under -O. Module imports disable bytecode writes.

Seven receipt-generating entry points are replayed. banked.py is the main
rank-mass accounting model with balanced child caps and spectator-aware
helper banks. encoder.py and encoder_conservative.py price the stated
partial encoder schedules; they leave compensation unpaid. full_centers.py
prices a simpler complete-width encoder and conditional compensation
allowances. unfused/verify.py and RECTANGLE-LOWER/verify.py prove scoped
all-stage obstructions and include negative controls. Their proofs are in
the adjacent PROOF.txt files.

screen.py and model.py retain an earlier, looser nomination model. They pay
idle slots at unsplit true ranks and do not certify the strict child cap.
Their optimistic numbers are historical search context, not an admissible
controller. RESULT.json is that preliminary screen; BANKED.json is the
later banked model. The unused model.py library is retained as research
context and is not a distinct claimed receipt.

Receipt values are unchanged from the scratch experiments. Absolute source
paths were replaced by package-relative paths; source hashes track the
portable scripts where a script itself is the dependency. PAID-CONTROLLER.txt
explains the rank-mass equations, bank padding and remaining obligations.

Prepared for DominikScholz with OpenAI GPT-6 Astra assistance in T3 Code.
The package NOTICE and sources/COST-SOURCES.json preserve the inherited
supplier, exact-arithmetic and contributor lineage. In particular, the
historical PR592 comparison credits Jeremy Kothe / jeremykothe2 and the
Claude Opus 5.5 assistance disclosed there. No fresh upstream supplier
verification is represented by these accounting replays.
