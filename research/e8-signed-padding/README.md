# Signed prefixes with bank-padding fusion

Conditional kappa **0.001001256225581264**, combining PR395's 25 signed target-prefix pairs, PR394's three free sink helpers and padding fusion, PR390's heterogeneous banks, and PR392's exact finite bootstrap.

Run `python -B research/e8-signed-padding/verify.py /fresh/output` after installing the unchanged PR390 requirements. C++17 and Boost headers are required. This runs the full signed-prefix baseline, including all twelve original PR390 stages, then constructs and checks the fused program and global template, recompiles its finite invoice, and freshly replays the bit composition at the changed complex bound. Expected files are comparisons after computation, not substitutes for it.

The scope remains conditional. The operator-level padding timing replacement from PR394 is explicit in PROOF.md, including the retained arbitrary-dirty invocation assumption. This is not an unconditional multiplication theorem.

Credits: Chafik Boukhalfa / chafreaky (PR394 free sinks, padding fusion and bracket compiler), Dugongue (PR390 prefix construction, dirty preconditioning and heterogeneous banks), Rohan Arun with OpenAI Codex assistance (signed prefixes, combination, mixed-child phase certificates, global placement record and recomputed invoice), and all contributors in the retained supplier notices. Apache-2.0. Unchanged PR394 source and notices are in vendor394/.
