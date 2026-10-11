# Signed target-prefix refinement

Conditional kappa **0.001001090245731051**, using 25 signed disjoint target pairs in the PR390 supplier and the PR392 exact finite bootstrap. This changes the finite local word; it is not an unconditional multiplication theorem.

Run `python -B research/e8-signed-prefix/verify.py /fresh/output` with the PR390 requirements, C++17 and Boost. The verifier first executes all twelve original PR390 stages, reconstructs the changed word, then reruns its scalar, frame, phase, bank, global-template and bit-composition audits before deriving the refined exponent. Expected records do not replace execution.

The inherited PR390 packaging repair in PR392 restores all manifest-pinned source bytes. All original licenses and notices are preserved. Construction credit: Dugongue, PR390 and the attributed supplier lineage. Signed extension and matching discovery: Rohan Arun with OpenAI Codex assistance. Apache-2.0.
