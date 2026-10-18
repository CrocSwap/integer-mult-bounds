Task: fstar-joint-label-census (handoff-first; census-pruning-audit scope changed).
Base: 18aacb215fc3717b06be8ceb9fca62aeca0d3e99, priority revision 6.
Predecessors: Aaron Wang/navinor PR2978 at 12eb7b832de9239a314a7cddf6c6033d618cd8f2;
PR3031 at e75906fc4e8b9f756a9877b2e467f4e564851c7d, methodological caveat.
Question: enumerate every three-line tau>=1 joint mask/zero-arc configuration
under GLOBAL total permutations and line permutations; compare the 3023-state
legacy census and identify exactly what its quotient omits or identifies.
Changed scope: the catalogue census audit starts with the already-covered F7
parity prune. This takes PR3031's explicit joint-sound-v3 follow-up instead.
Method/domain: a0,b0 in 0..7 with nonempty intersection on each of three lines;
Z any subset of the six off-diagonal arcs with even anchor dot product.
Use a definition-level exact label/order checker, correct group action and an
independent Burnside orbit count. Check tiny controls and legacy mutants.
Success: corrected counts, a concrete loss witness, and explicit downstream
limits. Stop at that finite classification; no rational realizability census,
F-star proof, new supplier, paid moment, kappa, or frontier update.
Budget: about 60 minutes including review and handoff. Cleanup requested by the
user is separate from the mathematical scope.
Nearest overlap: PR3031 identifies the issue but does not do the corrected
census. PR2978 supplies the flawed census and earlier realized box gap.
Attribution: F-star/L8/cert from DreamingOfClouds PR1590; box machinery and
canonicalization warning from Aaron Wang/navinor. New code: Arham Tahir with
substantial OpenAI Codex assistance. Apache-2.0.
Expected reproduction: python3 -B research/fstar-joint-label-census/verify.py
