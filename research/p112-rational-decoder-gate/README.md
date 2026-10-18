# A P112 cover with scalar rank 57 and sharp canonical-span cost 334

**Constructive finite result and cost audit; no new supplier or kappa.** For the same 112 selected labels used by PR2041, this package supplies a different cover by 37 orthonormal triads and one residual line. Its strict scalar endpoint mask has minimum fitting rank **exactly 57**, with an explicit 57-term integral fit and a matching principal-submatrix lower bound. For the fixed cover in PR2041, PR2532 identified a rank-at-least-99 obstruction; this package also supplies a matching 99-term fit. Thus the exact fixed-mask minimum changes from **99 to 57** when the cover changes. This opens more scalar sharing without reusing the invalid binary decoder target.

This is a partial result toward a rational decoder. Charging the full port spaces gives the displayed fit the profile `3 H3 + 53 H6 + H7`, of mass **334**. Even with the proposed coverage law and all additional costs set to zero, its zero-saving moment is **32871/32704 > 1**. A follow-up theorem proves that **every exactly-57-term rational fit on this mask costs at least 334**, including asymmetric factors and arbitrary nonzero common normalization. Moreover, at **any factor count**, a rank-57 fit costs at least **334** if both factor families remain in its column and row spaces: with `m=57+s` nonzero terms, the sharper bound is `C >= 334+2s`. The saved construction attains this minimum at `s=0`. A further [exterior-factor theorem](EXTERIOR-58-PROOF.md) proves that **every rational fit using at most 58 nonzero rank-one terms costs at least 297**, whether its matrix rank is 57 or 58. These floors exceed the necessary charge of at most 296. The number 57 counts rank-one scalar terms; it is not a verified number of physical child calls.

## Exact object and contract

Scientific base: `7ef5f7150476fdf995b286b9cdbed262c631939c`, priority revision 5. The labels come from [selected-replay.tar.gz](../community-frontier1094-audit/selected-replay.tar.gz), member `candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json`, payload SHA256 `c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa`. Exact source pins are in [SOURCES.json](SOURCES.json). No selected record or frozen predecessor is changed.

Write the selected labels as `q_p` in `F2^9`, indexed by ports `p=0,...,111`. They are distinct and have odd weight. [CANDIDATE.json](CANDIDATE.json) partitions the ports into singleton `G0={55}` and 37 triples `G1,...,G37`. Within each group the label Gram matrix is the identity. Set

\[
E_g=\operatorname{span}_{\mathbf F_2}\{q_p:p\in G_g\},\qquad E_p=E_g\ (p\in G_g).
\]

The inherited proposed endpoint is source `E_p -> FULL`, target `0 -> E_p^perp`. Under the strict scalar mask of PR1889 and PR2532, an addition from source `q` into target `p` is free only if `E_q` is orthogonal to `E_p`. A scalar fitting matrix `K` needs a common nonzero diagonal `c` and

\[
K_{pq}=0\quad\text{for }p\ne q\text{ whenever }E_p\not\perp E_q.
\]

Other off-diagonal entries are free. This condition uses the whole group space at each port, not just the two original labels. Distinct ports in the same group also have forced zero entries because that group is nondegenerate. The new cover has **420 free ordered port pairs**; the predecessor cover has 102. These counts exclude diagonal entries.

## A complete rank-57 certificate

For `j=1,...,18`, the groups `G_(2j-1)` and `G_(2j)` are orthogonal. For each `k=0,1,2`, form a support from the `k`th stored port in each triad of this pair, giving 54 supports. The residual line is orthogonal to both `G15` and `G16`; append port 55 to their first support, giving `{9,39,55}`. Make the three ports of `G37={54,60,69}` singleton supports.

These 57 supports `S_t` partition all 112 ports. Each contains at most one port from any group, and its represented groups are pairwise orthogonal. With `v_t` the indicator of `S_t`, define

\[
K=\sum_{t=1}^{57}v_t v_t^T.
\]

Each diagonal entry is one. Nonzero off-diagonal entries occur only within supports, where they are free. Thus this is an exact fit. One chosen port from each support gives an identity minor of size 57; the displayed factorization gives rank at most 57.

Conversely, the 19 odd-indexed triads `G1,G3,...,G35,G37` are pairwise nonorthogonal. The verifier checks every cross-group pairing matrix is nonzero. Among their 57 ports all off-diagonal entries are forced to zero, both within and between groups. Every valid fit therefore restricts to `c I57`, forcing rank at least 57. Together the certificates prove **minimum scalar fitting rank 57 for this fixed mask**, over any field with `c != 0`. They do not prove this cover is optimal among all covers of the selected labels.

For comparison, the old cover attains rank 99 by pairing corresponding coordinates of its orthogonal triad pairs `(6,13)`, `(7,12)`, `(9,19)`, `(22,25)`, pairing the residual port with the first port of group 1, and leaving every other port singleton. This makes 99 disjoint supports. The 33 triads excluding groups `12,13,19,25` force a principal identity of size 99. Both certificates are replayed; the old fit costs `86 H3 + H4 + 12 H6 = 334` under the same tariff.

For any nonsingular rational diagonal matrix `S`, there is also a rational fitting family

\[
K_S=SKS^{-1}=\sum_t(Sv_t)(S^{-1}v_t)^T.
\]

Its diagonal, zero pattern and rank are unchanged. The positive fixture alternates diagonal entries 1 and 2, so actual even-denominator coefficients are checked. Their presence alone supplies no 2-adic cost gain: every factor has the same support as before.

## Full port-space charge and stopping decision

For a rank-one term `a b^T`, use the inherited one-total tariff: span **all group spaces** touched by the nonzero coordinates of `a`, do the same for `b`, then charge the `F2` rank of their bilinear pairing. This is the port-space convention of PR2532 and the native multiplicity issue made concrete in PR2203. Scalar coefficient rank and original-label support rank do not replace this charge.

Here both spans are equal. Each ordinary pair support touches two orthogonal nondegenerate three-spaces and costs 6. The support also containing the residual line costs 7. Each singleton still touches its complete three-space and costs 3. Hence

\[
n_3=3,\qquad n_6=53,\qquad n_7=1,\qquad C=3\cdot3+53\cdot6+7=334.
\]

This remains true after any diagonal conjugation above. The [minimum-length cost theorem](RANK-TIGHT-PROOF.md) extends this floor to every exactly-57-term rational scalar fit on this mask. The minimum-length theorem alone does not bound decompositions with more terms. The [canonical-span refinement](CANONICAL-SHARP-PROOF.md) does: every overcomplete decomposition retaining both spans costs at least `334+2s`. Exterior directions and larger fitting ranks remain outside that refinement. The integral construction does not evade the earlier 2-integral floor of 334 for this 37-triad/one-line contract.

The exact average unpaid dimension is

\[
u=\frac{37\cdot3\cdot3+1}{112}=\frac{167}{56}.
\]

Using uniform `u=3` would overcredit the residual port. Grant the mixed-group coverage law, selected non-centre profile `{1:2412, 2:418, 3:432, 4:142, 5:82}` of mass 5522, width `m=73`, and `w=896/9` live families per call. Adding the displayed decoder gives profile `{1:2412, 2:418, 3:435, 4:142, 5:82, 6:53, 7:1}`. Ideal idle mass is

\[
I=(73-u)w-5522=\frac{4346}{3}.
\]

Its packing does not matter at zero saving:

\[
M(0)=\frac{5522+C+I}{73w}
=1+\frac{C-2672/9}{65408/9}
=1+\frac{334}{65408}
=\frac{32871}{32704}>1.
\]

Every child rank is below 73, so `(r/73)^(1-a)` is nondecreasing for `a>=0`. Failure at zero rules out positive saving for the displayed profile before extra costs. This conditional screen does not establish a native implementation of the coverage law. Its necessary centre budget for any positive saving is `C < 2672/9`, hence `C<=296` for an integer invoice. Reaching the selected saving requires a substantially smaller bill, around 261 even under favorable rank-1-through-9 packing; PR2532's incumbent-tie screen is planning context, not a feasibility certificate.

## Sharp cost floor for every minimum-length rational fit

The follow-up starts from canonical main `936fac15b1b1b59dc5285c713a77f9f3c07b2906`
and pins the published construction at PR2757 head
`c8216fca1ed2a301a95e7e0b1e5844d4cfda02c6`. Its source inputs are unchanged.

[RANK-TIGHT-PROOF.md](RANK-TIGHT-PROOF.md) proves a sharp floor of 334 for
**exactly 57 nonzero rational rank-one terms**, over all fitting matrices on
this fixed mask. The principal identity forces a zero Schur complement. Two
additional forbidden blocks eliminate the exceptional couplings, leaving 18
inverse paired blocks, the isolated final triad and the residual line.
Biorthogonality and 324 checked support-pairing ranks then force every term to
cost at least six, except at most three terms costing three. The residual
diagonal requires a separate term costing at least seven. Hence the total is
at least `54*6 + 3*3 + 1 = 334`, attained by the saved construction.

The argument does not reduce rational coefficients modulo two and covers
nonintegral, nonsymmetric and nongauge factorizations. It closes optimization
at minimum factor count. For any number `m=57+s` of terms retaining both canonical spans, the
[sharp refinement](CANONICAL-SHARP-PROOF.md) proves `C >= 334+2s`. It keeps the
same pure-J term count in two acyclic-subset inequalities: one for all 57
latent coordinates and one for the 54 ordinary coordinates. Their exact
convex combination cancels that count. The same complete 40-space closure
and 272 low-price rectangles suffice. This supersedes the earlier valid but
weaker lower bound of 308; no new geometry or minimality assumption is added.
The new independent vector-set checker validates both probability budgets,
source pins and the affine combination; [its receipt](CANONICAL-SHARP-RESULT.json)
is retained. The symbolic argument remains a written proof, not a proof-assistant certificate.

Thus **at least 59 factors and a change of span or fitting rank are necessary for
charge <=296**, not sufficient; the 59-term necessity follows from the extension below. Exterior factor directions may cancel in the
sum, and fitting matrices of larger rank remain open. Changed covers and
operator contracts also remain open. Neither theorem establishes physical
implementation or an improved multiplication bound.

## Exterior factors: every decoder with at most 58 terms misses the gate

[EXTERIOR-58-PROOF.md](EXTERIOR-58-PROOF.md) closes both matrix-rank cases
possible with 58 terms. It permits arbitrary rational coefficients, asymmetric
factors, exterior directions that cancel, and changes of fitting matrix:

\[
    m\le58\quad\Longrightarrow\quad C\ge297>2672/9.
\]

This floor is not claimed sharp. For rank 57, Sylvester's rank inequality forces
one factor family to remain in the fitting matrix's span. The other has one
exterior direction. Compressing the affected coordinates handles a sparse
direction; a complete closure of **1,750 physical-triad spans** and **2,318
affected-set unions** handles a dense direction. The key bound uses the union
of every compatible cheap-source support for the same affected set.

For rank 58, the Schur complement has rank one. Its permitted group blocks
form a forest. All **314 nonempty support rectangles** localize the defect to
either a small compression, the exceptional groups 4/24, or a residual-only
six-neighbor case. The proof handles singular paired maps and a zero retained
source column explicitly. It invokes the prior 40-space acyclic cost argument
after compression; it does not reduce rational coefficients modulo two.

The new [primary checker](check_exterior_58.py) and
[independent checker](independent_exterior_58.py) reconstruct these finite
premises using echelon bases and explicit vector sets, respectively. They do
not execute or import one another. Separate AI agents also audited the written
algebra. This is not independent human review or formal proof verification.

Consequently the next scalar construction must use **at least 59 nonzero terms**,
and must still escape the earlier rank-57/both-spans floor. No cheaper decoder,
native implementation, or improved exponent is supplied by this obstruction.

## Discovery and replay

Discovery optimized the actual free mask. A bounded randomized exact-cover search, seed `2026101501`, packed orthogonal six-label sets and split each into two triads, obtaining 17 disjoint orthogonal triad pairs. A local repair, seed `2026101502`, repacked 22 ports: two six-label blocks plus ten remaining ports became three six-label blocks, one triad and one line. This produced the 18-pair cover. Attaching the residual line as above gives rank 57.

These were bounded heuristic searches, not an exhaustive optimization over covers. The finite certificate is independent of discovery order, random choices and time limits. Scientific replay uses the saved cover and witnesses, without rerunning discovery.

From the repository root, standard library only:

```sh
python3 -I -O -B research/p112-rational-decoder-gate/verify.py
python3 -I -O -B research/p112-rational-decoder-gate/independent_check.py
python3 -I -O -B research/p112-rational-decoder-gate/check_rank_tight_floor.py
python3 -I -O -B research/p112-rational-decoder-gate/independent_cost_floor.py
python3 -I -O -B research/p112-rational-decoder-gate/check_overcomplete_closure.py
python3 -I -O -B research/p112-rational-decoder-gate/check_exterior_58.py
python3 -I -O -B research/p112-rational-decoder-gate/independent_exterior_58.py
python3 -I -O -B research/p112-rational-decoder-gate/check_canonical_sharp.py
python3 scripts/research_package.py --package research/p112-rational-decoder-gate --check-only
python3.12 scripts/research_package.py --package research/p112-rational-decoder-gate
```

The primary and separately implemented checker reconstruct labels, the cover, the whole-space mask, rank witnesses, rational fitting entries and term charges. Commands, controls and input requirements are in [VERIFY.json](VERIFY.json); the receipt is [RESULT.json](RESULT.json). Neither checker is a native word compiler or proof-assistant kernel. Independent checks here are AI-agent checks, not independent human review.

## Predecessors, overlap and credit

- **Cinna Davis (`1337isnot1337`), [PR2041](https://github.com/CrocSwap/integer-mult-bounds/pull/2041):** selected P112 three-plane cover, endpoint proposal and binary factorization. That binary identity and local correction remain valid in their algebra. This package changes the cover and certifies the stricter scalar mask.
- **Adam Gall (`adamgall`), [PR1889](https://github.com/CrocSwap/integer-mult-bounds/pull/1889):** paired-plane scalar-mask obstruction. **ctoth and collaborators** and **Philippe Van Velzen (`philippeVV`)**, in [Discussion1587](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587), supplied the port endpoint, masked-set count, whole-space pricing and 2-integral/Smith framework used by the later audit.
- **Sagar Thakrar (`thakrarsagar`), [PR2532](https://github.com/CrocSwap/integer-mult-bounds/pull/2532), head `bcb6f278503bd2a6b3ffb9bdcfcda9f36c18d2f4`:** exact application of that mask and pricing to PR2041, including its 102 free pairs, rank-at-least-99 obstruction and 334 floor. The changed triad cover is the new premise here; the new fit does not contradict that fixed-cover audit.
- **Cinna Davis, [PR2126](https://github.com/CrocSwap/integer-mult-bounds/pull/2126), and Jeremy Diviney (`jeremydiviney`), [PR2203](https://github.com/CrocSwap/integer-mult-bounds/pull/2203):** paired-plane scalar identity fit and native payload accounting. Their distinction between coefficient blocks, independent payloads and native occurrences is retained.
- **Sagar Thakrar, [PR2484](https://github.com/CrocSwap/integer-mult-bounds/pull/2484), head `4823273c8163e4c72472bdf7d42202e2c12d2e46`, following ywz65's PR2471:** exact scalar minimum rank 49 on a different, fixed paired-plane mask, including disjoint-support upper and submatrix lower certificates. Those proof methods are prior work. This package supplies a different three-plane cover, its exact rank and full charge; rank 57 versus 49 does not compare complete supplier costs.

- **Hanson Sun (`bbMisk`), [decoder-excess-rank](../decoder-excess-rank/README.md), following joaqcoo/PR1224:** the general Sylvester excess-rank and projection framework is prior work. The new contribution here is the source-bound cost consequence for this different full-group mask, not that rank inequality.

At the scientific base the central ledger marks PR1889, PR2041, PR2126 and PR2203 incorporated as scoped results, which does not admit a new supplier. PR2532 and PR2484 are pinned pending sources for context and overlap. The selected PR1094 lineage, including Rohan Arun and Jeremy Kothe, retains credit for the labels. Native frame-distance work by icekylinx and its independent check by woklerx retain their credit through the predecessors.

Prepared by flyingviper with substantial OpenAI Codex assistance in search, proof development, implementation and separate-agent checking. No independent human review, formal verification of the full theorem, selected-result change or new exponent is claimed. New work is Apache-2.0.

## Open next questions

1. **Can a different rational factorization exploit this mask to lower the full port-space bill?** Start with at least 59 nonzero terms, and either introduce factor directions outside the fitting matrix's column/row spaces or increase the fitting rank. The cost theorems exclude every rational fit with at most 58 terms and all overcomplete decompositions of rank-57 fitting matrices that retain both spans, including asymmetric ones. Enforce every diagonal and forbidden entry exactly before pricing whole source and reader spaces. A useful first gate is `C < 2672/9`; a selected-bound candidate needs a full moment below one near the incumbent saving, requiring roughly `C<=261` even in the favorable rank-9 relaxation. Stop a factorization family when its favorable complete invoice misses that gate. Diagonal rescaling of the saved factors costs 334 and does not reopen it.
2. **Can a different block or native contract realize useful sharing with every independent payload charged?** First supply the complete operator identity, dirty-input behavior and actual occurrences, rather than charging a geometric rank once for a multi-array block. Before another construction round, update the family budget and consumer boundary: source preparation, chart conversion, routing, hosting, chronological ownership, storage, erasure/restoration, precision, all-size recursion and a compatible bit supplier remain unproved here. Their costs are unknown, not zero. This finite certificate supplies neither physical compilation nor the selected cold replay.

## Canonical-span refinement checkpoint

This refinement extends PR2757 head `2c54b99055aaa21d0bd3c8c8e4c48ce3c7fb1dd9`.
Canonical main was refreshed to `28f54620ff770dd051d5df35882bd84303d13c6f`;
guidance, the selected record and consumed inputs were unchanged. Two separate
AI agents checked the proof and exact geometry, followed by the parent replay.
The sharp 334 result closes optimization inside both canonical spans. It is
a partial research result; the search for an exterior or changed-cover decoder
of charge at most 296 continues under the user's explicit persistent budget.
