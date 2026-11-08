# Root-word duality, Gram-class floor for 16 to 24 deleted lines, flag-chain flattening and exact frame facts for the P104 setting (no kappa)

**No new kappa.** No word is built and nothing is priced. This package states seven results about the E8 line model behind the P104 caller, each with its hypotheses and a check. Statements and proofs are in `THEOREM.md`.

Tag discipline (as in `THEOREM.md`): **[C]** exact computation reproduced by `check.py` (one PASS line per claim); **[P]** hand proof; **[P+C]** both; **CONDITIONAL** stated with its missing premise. A verifier or package restriction is never called a law: the labels are SPEC (outer framework or paper, quoted with file and line and checked), package convention, verifier behaviour, derived, family assumption.

## Results

1. **Theorem G, duality [P+C].** N isotropic transvections in dimension n with product -I correspond, on gauge classes, to N reflections in dimension rho = N - n with product -I (characteristic not 2). Both directions are checked exactly on reduced words of w_0 for D4, B3, F4, I2(4), I2(6) and on random rho = 2 words. The real-window law for three hosted pairs, which rests on citations not checkable here, is not included.
2. **Theorem O, Gram-class floor [P+C].** For any set D of 16 to 24 deleted lines and any Gram-class design (any number of terms, any invertible M), the owned cost is at least 56; so v - c <= 64 - |D| <= 48, with equality at |D| = 16 attained by an explicit design (c = 56, every term price 7). The proof is Cauchy-Binet plus a Sylvester rank bound plus a domination lemma plus a computed census (cost of making a codimension-2 drop is at least 25 on all eight ray types). It does not cover |D| <= 15 or |D| >= 25, carriers outside col(E), or other line systems.
3. **Theorem F, flattening [P+C].** A chain of nested frames equals, on the mask N, one rank-one term, at price at most the chain's frame-dimension change. Corollary F2 (CONDITIONAL on the word being a disjoint union of such chains whose flattened terms form a Gram-class design) transfers the floor 56.
4. **A2 toy [P + C].** The naive transfer "any N-diagonal rank-one decomposition costs at least the Gram value" is false: Gram value 4, identity decoder 3 on A2.
5. **Theorems I and R [P+C for h <= 4].** Subspace frames are exactly the Lagrangians on a geodesic from L_0 to L_F, and rho(L) = L_{pi_1 L} is a retraction that does not increase adjacency distance. Network reading CONDITIONAL on two stated Clifford premises.
6. **Exact tile caps [C].** On the 104-line port set of the package data, over all subspaces: maximum area 32, 32 and 36 for (dim A, dim B) = (2,3), (3,4), (4,5).
7. **Schur law and leak identity [P+C].** An exact complement formula for the public inverse of a map with owned lifetimes, and the per-register identity L_X L_Y = r f.

## Scope and what is not claimed

No bound on kappa; nothing about the denominator; Theorem O is about the scalar Gram model with F2 mask-rank price, not about any particular word's owned layer; Corollary F2 and the network reading of Theorem R are conditional as stated; the tile caps are counting facts and no claim is made that geodesic tiles reduce to linear tiles. No word from any pull request is replayed or checked here.

## Exact checks

`python3.12 -I -B research/p104-duality-ceiling-flag-note/check.py` from the repository root (or `verify.sh` from anywhere). About 30 s. Standard library only, no dependencies. The quote checks read four repository files named in `data/quotes.json` (9 lines) and fail if a file is absent or a line changed; the same files are pinned in `SOURCES.json`. The run ends with `PASS_P104_DUALITY_CEILING_FLAG_NOTE`.

## Open next questions

1. Can the floor of Theorem O be proved for 25 or more deleted lines, and for 15 or fewer, in the Gram class?
2. Is a given word's owned layer a disjoint union of flag chains with Gram-class flattened terms, so that Corollary F2 applies?
3. Do the floors survive owned networks that are not flag chains (forks with later reads or writes, relays, owned ascent)?
4. Does the retraction of Theorem R extend to helpers with non-family endpoints, and do geodesic tiles reduce to linear tiles?

The structured form with first steps and blockers is in `TASK.json`.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
