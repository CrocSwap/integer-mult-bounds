**FINDING / DONE / RELEASED — 2026-10-15 21:48 UTC, priority revision 5.**

The unchanged PR2586 physical P104 word has the **sharp uniform exact fractional guard**

`g(lambda) = ceil(9*lambda/2)+2, for every integer lambda>=1.`

Seven bits suffice and are necessary at one layer, improving PR2772's sufficient fifteen-bit guard. This answers its correlated-relative-prefix format question, conditional on the same native-correctness and tensor-lift premises. Next useful work: bind one admissible recursive representation and fully price its bit operations, access, movement, scratch and restoration. This bounded investigation is finished and its advisory claim is released.

**Why the bound holds.** A dyadic Gaussian n-qubit Clifford has flat stabilizer support of size 2^h in each column. A reduced amplitude (a+ib)/2^d satisfies a^2+b^2=2^(2d-h); Gaussian parity forces d=ceil(h/2)<=ceil(n/2). Apply this to the entire relative chart/native prefix on 9*lambda binary coordinates. The independently reconstructed scalar rows and every ADD product lie in (1/4)Z, adding at most two bits. Disjoint-pair partial writes, exact halvings, scalar temporaries and all eight strict-zero erasures are covered.

**Sharp source-bound witness.** Set initial Y2=2^-f delta_0 and all other public inputs to zero. At zero-based event 2142, D18 has Y2 coefficient -1/4, empty initial source frame and full nine-coordinate target frame. Its first coordinate is

`-2^-f * (1/4) * ((1-i)/32)^lambda,`

whose exact common dyadic denominator needs ceil(9*lambda/2)+2 extra bits. At one layer it is (-1+i)/128. This is an atomic-boundary witness independent of the order of internal commuting tensor gates. It does not exclude a changed word, field-dependent grids, rescaling or an approximate endpoint contract.

**Evidence.** Written all-depth proof and separate AI mathematical audit; all 5,398 events, 445 frames, 1,245 native records/2,070 occurrences, and 7,999,488 exact Pauli derivatives for 1,736 monomials. Two complete seven-bit fixtures each match 183,296 complex endpoint coordinates against PR2772's preserved canonical-chart oracle and erase all eight private fields. Independent code checks 30,007 scalar products, all 96 one-qubit C/S matrices, 2,112 deterministic larger prefixes and depths 1–64 of the sharp witness. Six-bit, non-Clifford, scalar-product, native-binding and cleanup defects reject. Registered CPython 3.12 replay and read-only Git-free optimized CPython 3.14 replay pass, including typed/source corruption and overwrite refusal.

**Artifact and reproduction.** The attached ZIP contains all 22 committed package files, including original notices and Apache-2.0. Retained local commit: `f698adae55881bdcdb76801a94276a8677f1a9a6`. ZIP SHA256: `e23b559711a0106d9a6aab4f52cc8d686481e6897fa56aaade3e4774fdf5b7ae`.

`python3 -I -O -B research/p104-clifford-grid/verify.py`

`python3 -I -O -B research/p104-clifford-grid/independent.py`

**Scope and credit.** Scientific base a571dfa6e21bbe2d3b9cac48e5b078df59e49b68; PR2772 head 69ba5a423246a1c9281bdd5c1f51240b454f2aa6, rechecked unchanged. Credit Nick Petalas/PR2772 and 2754, Arham Tahir/PR2674 and 2665, ywz65/PR2586 and 2730, Alejandro Zarzuelo Urdiales and retained native/P104 lineage. Ross Richardson with substantial OpenAI Codex assistance and a separate AI specialist audit. Native correctness remains inherited; finite physical fixtures cover one layer. No efficient recursive implementation, complete supplier, new kappa, formal-kernel/human review or hosted-CI pass is claimed.

Submission refresh 21:42:49Z reached main 6ca6f217708b075814de409ad693fea9a2aaa760 with guidance/selected hashes unchanged. The 21:43:28Z overlap snapshot paginated all 717 open PRs including drafts and 1,975 local records; live hubs 1163/1166/1167 and this thread were reread. Older hidden Discussion replies remain incomplete after API 403; no novelty guarantee.

<details><summary>Original bounded claim</summary>

CLAIM / 2026-10-15 21:38 UTC / priority revision 5.

Question: can the unchanged PR2586 physical P104 word use the Gaussian-Clifford dimension bound to reduce PR2772's sufficient whole-prefix grid? Base main a571dfa6e21bbe2d3b9cac48e5b078df59e49b68; predecessor PR2772 69ba5a423246a1c9281bdd5c1f51240b454f2aa6, retaining PR2674/2754 and their source lineage.

Method/domain: independently prove or refute that a dyadic Gaussian Clifford on n binary coordinates has denominator at most 2^ceil(n/2); bind every relative chart/native prefix and every logical scalar coefficient in the frozen word. Candidate sufficient guard: ceil(9*lambda/2)+2 for every integer lambda>=1 (seven bits at one layer), with exact complete one-layer fixtures and an independent proof/checker. Check partial pair writes, scalar-product temporaries and all eight zero erasures. Stop if any non-Clifford or scalar-grid premise fails; no larger search.

Expected artifact: source-pinned proof, executable positive/defect controls and a public finding. This targets the correlated-prefix format question in PR2772, not recursive-child pricing, hosting or a kappa improvement. Fresh overlap covered all716 open PRs including drafts; Discussion API rate limiting leaves older hidden replies incomplete, with live hubs and this thread read. Credit Nick Petalas, Arham Tahir, ywz65, Alejandro Zarzuelo Urdiales and retained native/P104 lineage. Ross Richardson with substantial OpenAI Codex assistance and an independent AI mathematical audit; no human/formal review implied.

Advisory claim expires 2026-10-15T23:38:00Z. Next: validate the Clifford and quarter-grid premises, then test the seven-bit execution.

</details>

[p104-clifford-grid.zip](https://github.com/user-attachments/files/33516620/p104-clifford-grid.zip)
