# Discussion 1516: independent audit of the dirty-host cut-rank implication

**Date:** 2026-10-14
**Author/workflow:** Andrey Mas with GPT-6 Pro through ChatGPT; AI-assisted written mathematical audit, not independent human or kernel verification.
**Scope:** the inequality in ctoth's comment 18913724, with comment 18913740's branching-tree lemma as a separate control. No selected-word search, new decoder, price, frontier, or multiplication theorem.
**License:** original review and checker: Apache-2.0 (SPDX: Apache-2.0).

## 1. Verdict

**Conditional corroboration, with an explicit remaining interface obligation.**

The literal branching-descent-tree lemma is correct. Its reported selected-word consequence, eight units for each of eight centres, remains conditional on the author's unpublished final-frame/served-target computation. That tree proof does not by itself establish anything about arbitrary mixed or cyclic dirty-host implementations. The source does not provide a tree-reduction proof, and this review does not attribute one to it. [D2]

The stronger dirty-host inequality has a rigorous **direct cut-rank proof**, without a tree reduction, under the clean-boundary contract in §5. That contract permits finite non-tree mixing, multiple centres, upward moves, cancellation, free common-frame copies, and reuse. In that model, if the scatter matrix is S, the carrier entrance heights are at least 8, and the targets receive their clean scatter at height 0, then

\[
 M\ \ge\ H_{\mathrm{end}}+8\operatorname{rank}_{\mathbb Q}S,
 \qquad H_{\mathrm{end}}=\sum_\alpha |a_\alpha-b_\alpha|,
\]

where each designated independent dirty host enters at height a_alpha, leaves at height b_alpha, and is restored logically at that endpoint. The charged region includes all operations used for those obligations.

**The remaining issue is identifying the source's “hosted useful mass” with a quantity justified by that boundary, not proving that mixing is impossible.** Common-frame legality alone does not identify the hosting credit, exclude pre-positioned information, fix the restoration checkpoint/gauge, or certify that all proposed modifications have the requisite boundary. The inherited admitted word is substantially more restrictive than a general dirty-host circuit. The post itself says the modified programs were not globally admitted and the experiment scripts are local. [D1], [S4], [S5]

Accordingly:

* Accept the tree lemma in its literal model, and the stronger inequality under the stated contract below.
* Do not yet certify the broader hosting conclusion for every implementation intended by the informal extension, or treat 64 as an independently recomputed selected-word result.
* No counterexample inside an unambiguously specified public dirty-host extension is established here. The side-information example in §7 is explicitly outside the clean-boundary contract, not a refutation of the author's fixed selected-word claim.

## 2. Evidence and the public operation boundaries

### Evidence classes

| Class | What this review actually establishes or observes |
|---|---|
| Written proof | The literal tree lemma (§3); the general chronological cut-rank lemma (§4); the clean-boundary hosting corollary (§5). |
| Finite exact checks run here | Small rational logical-row examples; binary subspaces of F2^3; 11 rejection controls. Normal and `-O` executions pass (§8). |
| Source observation | Public comments and pinned text were read using the web tool. Relevant emitter, auditor, common-frame, and ownership conditions are described below. |
| Author-reported, not independently reproduced | Selected scatter rank 8; all eight final-frame meets zero; the modified selected programs; the GF(3) searches and their rule sets; numerical prices. |
| Unrun obligation | Selected byte binding, selected geometry extraction, production admission, full dirty-host operator/owner/continuation accounting, and any source-wide replay. |

### Inherited admitted word versus the proposed extension

The emitter creates a private centre copy, moves that copy along one descending chain in the forward orientation, scatters at matching target levels, and clears it. The backward centre block gathers along the reversed ascending path. Ordinary emitted frame changes are ascending. This is a concrete construction, not a declaration that every semantically exact replacement must have this form. [S4]

The auditor requires common frames for scalar operands; a centre transition has exactly its named private centre live; ordinary climbs require no live private centre; direction and nesting are checked. Phase boundaries have no private work. Its final row test is the arbitrary-dirt shear identity on ordinary registers. These are observed predicates, not an executed admission result in this review. In particular, I do not claim the standalone function compares every scalar gate against fixed A/B lists, or rejects every conceivable same-frame scalar mixing. [S5]

The centre-guard review distinguishes ordinary active owners from private centres, requires distinct active owners, and explains that the original centre carrier is not cleared. Its statements concern the inherited program and its admission context; replacing a private centre with an idle-family owner changes that interface. [S3]

The common-frame proof uses invertible representatives T_F and logical values T_F^{-1}h. Its semantic conjugation identity is distinct from its monotone-chain, lifetime, and accounting conditions. Its helper-hosting discussion specifies whole residuals, wrappers, spectators, and ownership constraints. Those are not an automatic admission of a newly borrowed centre. [S2]

The older idle-axis hosting argument moves an exact whole helper residual into an idle window and removes the matching pending factor. Its credit rests on an exact operator identity and a disjoint pending-coordinate allocation, not simply on the existence of a child of the right numerical rank. [S6]

| Feature | Emitted/admitted centre construction | Literal tree model in D2 | Dirty-host extension in D1 |
|---|---|---|---|
| Several centres | Sequential private-centre blocks | One root/centre per tree; summing assumes separate charged trees | Pooling is discussed negatively; the full permitted simultaneous-mixing grammar is not supplied |
| Branching copies | Emitted path is a chain | Explicitly allowed, free at a node | Exact copy/overwrite/clear rules for hosts and extra work are not completely specified |
| Mixing/merging payloads | Actual centre emission does not mix different centre copies | Not an operation of the single-payload tree | Some repair algebra is supplied; a complete merge/reuse alphabet is not |
| Upward moves/cycles | Ordinary climbs; forward private centre moves down only | Ruled out by descent-tree definition | The reported three-move repair explicitly uses an ascent; it was not globally admitted |
| Reuse | Private storage can be reused after clearing | Copies branch but no cyclic reuse | Cross-call storage reuse is mentioned; general lifetime/credit rules are not supplied |
| Restoration | Complete prescribed shear and private erasure | Not a dirty-host model | Arbitrary dirt must be handled, but its exact labelled restoration checkpoint and credit need specification |

It would be wrong either to exclude the author's three-move experiment merely because the old emitter cannot emit it, or to declare every common-frame cyclic circuit admitted because that experiment was considered.

## 3. Source control: the literal branching-tree lemma

This is ctoth's lemma, independently checked here, not a newly claimed result. [D2]

Let F be a finite-dimensional vector space over any field. A finite rooted tree has root label F. Each edge e has labels M_e -> N_e with N_e contained in M_e and costs

\[
 c_e=\dim M_e-\dim N_e.
\]

Copies of a payload at a node are free. Every served target t is assigned a node whose label is contained in a prescribed final frame V_t. A served internal node can be treated as a leaf by adding a zero-cost duplicate. Let C=sum_e c_e. Then

\[
 C\ge \dim F-\dim\left(F\cap\bigcap_t V_t\right). \tag{T}
\]

**Proof.** Work in ambient F. For each edge choose a complement B_e to M_e in F and set

\[
 H_e=N_e\oplus B_e.
\]

Then M_e intersect H_e=N_e and codim_F H_e=c_e. Let Z be the intersection of all H_e inside F. Starting at the root, induction on a path shows Z is contained in every node label: if Z is contained in M_e, it is contained in M_e intersect H_e=N_e. Hence Z is contained in every served V_t. Also

\[
 \operatorname{codim}_F Z\le\sum_e\operatorname{codim}_F H_e=C,
\]

for example by stacking defining linear functionals of the H_e. Thus dim(F intersect all V_t) >= dim Z >= dim F-C, proving (T). No positive-definite form, characteristic-zero assumption, or independence of the edge constraints is needed. ∎

If V_t=ker(phi_t), the right side is rank of the map F -> K^{targets}, v -> (phi_t(v))_t, by rank-nullity. For more general final subspaces, use a generating set of annihilating functionals for each. In the source's application these are **binary** frame/functionals calculations. They are not the rational scatter-rank calculation in D1.

With only the stated final-containment constraints, the bound is sharp: descend once to K=F intersect all V_t and serve there, at cost dim F-dim K. This is not a claim of attainability when additional fixed waiting levels, B gates, or timing constraints forbid that placement. In particular, (T) is a lower bound, not an exact optimizer for trees with prescribed rank-six leaf labels.

The author reports dim F_k=8 and K_k=0 for each selected centre. Conditional on those values and separate charged per-centre trees, (T) gives 8 each and 64 in total. Neither the rank-zero meets nor a reduction from jointly mixed circuits to these trees was recomputed or proved here. The latter reduction is unnecessary for the different conditional theorem below.

## 4. Direct chronological cut-rank lemma

### 4.1 Precisely named model: scalar common-frame transport

Fix a field K (Q suffices), a nonzero K-vector space V of register payloads, finitely many independent formal input payloads z_1,...,z_n, and frame labels F with integer height nu(F)=dim F. For the Clifford setting, frame geometry is over F2 while scalar coefficients are over Q; these fields must not be conflated.

At every time, register r has logical content

\[
 \ell_r=\sum_i c_{ri}z_i,\qquad c_r\in K^n.
\]

The following rules define the model being proved, not a claim of production admission:

1. An add, scale, copy, or other scalar linear operation is local to one common frame. Copy can overwrite a destination provided the full dirty endpoint is eventually satisfied. Free zero-work allocation and erasure of private work are allowed. They cannot insert previously uncharged nonzero information at a new frame.
2. A transport acts on one payload register, leaves its logical coefficient row unchanged, and changes its frame A -> B. Its paid mass c is at least |nu(A)-nu(B)|. All such movements, including returns, preparation, and cleanup inside the chosen region, are counted.
3. No uncharged cross-frame copy, relabelling of nonzero data, or multi-payload transport masquerades as one one-register event. Renaming a register together with its value and frame causes no communication and is harmless.
4. The entry state, all additional work, and the demanded logical outputs/checkpoints are specified. Any pre-existing side information belongs to the entry state. The same finite charged region must be used for both the lower bound and its credit subtraction.

These rules allow more interior freedom than the original centre emitter. They do not impose trees, monotone trajectories, a bound on word length, or a ban on target feedback. Restrictions of the source grammar only reduce this model's set of circuits if the boundary and pricing rules also agree.

For nested source frames the paid transport rank equals the height difference. More generally the supplied frame formula is

\[
 d(L_A,L_B)=\dim A+\dim B-2\dim(A\cap B)
             \ge |\dim A-\dim B|.
\]

Thus the height-accounting inequality is justified for those transitions; it is not postulated as an information-capacity identity. [S1]

### 4.2 Why physical transport preserves a coefficient row

For exact representative T_F, write physical content h_r=T_F ell_r. A frame transport T_B T_A^{-1} changes T_A ell_r to T_B ell_r. At a common F, an add is

\[
 T_F\ell_t+qT_F\ell_s=T_F(\ell_t+q\ell_s).
\]

Copies and clears have the same interpretation. This is the inherited common-frame conjugation mechanism. [S2] The new cut proof counts its coefficient rows, not the binary dimensions of their values. A payload may itself have 512 or more coordinates: one moved logical row is still one generator in K^n. This does not assume a frame dimension literally measures how much information the payload contains.

### 4.3 Statement and proof

For a positive integer j, call a register **low** if nu(F)<j, and **high** otherwise. Let W_j^0 be the span of all low coefficient rows at entry. Let D_j count all high-to-low transports across this cut. Let Q_j be any collection of coefficient rows that the computation actually produces on the low side, possibly at different times. Then

\[
 D_j\ \ge\ \dim(W_j^0+\operatorname{span}Q_j)-\dim W_j^0. \tag{C-down}
\]

There is a symmetric statement for high-side observations, their entry span, and the number U_j of low-to-high transports.

**Proof.** Retain, for purposes of the proof only, the span of every row ever available on the low side. Initially it is W_j^0. Common-frame scalar operations on low registers only form linear combinations of rows already in that span. High-side operations do not affect it. Sending a low register upward cannot add a low-side direction. Clearing work or overwriting a row cannot add one either. A high-to-low transport introduces exactly its one current row, increasing the retained span's dimension by at most one. Induction over the finite event sequence proves (C-down). The retained history is a mathematical device, not free physical storage. ∎

**Consequences.** Cancellation, several centres, merging combinations, upward detours, and repeated use of a physical wire cannot invalidate the lemma. Nor must all demanded low rows coexist. What matters is their joint rank modulo the entire initial low span. Initial side information is explicitly accounted for rather than implicitly assumed absent.

For a move from height a to height b, the number of integer cuts it crosses is |a-b|. Consequently, over all cuts,

\[
 M\ge\sum_j(D_j+U_j). \tag{A}
\]

This supplies the missing justification for summing cut counts into paid mass. The proof is directional; no acyclic-network or tree-normal-form assumption is used.

## 5. Conditional dirty-host corollary

### 5.1 Clean-boundary contract

Consider a replacement region satisfying §4. At entry its ordinary logical register values are independent input coordinates; extra private work is zero. Among these coordinates are:

* m distinct carrier payloads X=(x_1,...,x_m), at heights at least q;
* target old values Y=(y_1,...,y_t), at height 0;
* independent dirty host values d_alpha, on roles disjoint from the carriers and targets, at specified heights a_alpha.

Additional independent ordinary registers are permitted. At the region's exit, require:

\[
 Y'=Y+SX\quad\hbox{at height }0,
 \qquad d'_\alpha=d_\alpha\quad\hbox{at height }b_\alpha.
\]

No host dirt contaminates the target outputs and no carrier contribution contaminates restored host outputs. The remaining ordinary outputs must satisfy the replacement's prescribed full endpoint, and private work is erased. The proof needs only the displayed obligations, so retaining all others cannot weaken it.

“Logical restoration” is deliberate. If a host enters with gauge T_A and leaves with T_B, its physical map is T_B T_A^{-1}, not necessarily physical identity. The claim that this is precisely a useful pending idle factor, including its wrappers and spectators, is a separate operator/credit obligation.

Define

\[
 H_{\rm end}=\sum_\alpha|a_\alpha-b_\alpha|,
 \qquad r=\operatorname{rank}_K S.
\]

**Corollary.** Every finite circuit with this contract has

\[
 M\ge H_{\rm end}+q r. \tag{H}
\]

### 5.2 Proof, including the host subtraction

Fix cut j. Let h_j^- count hosts with b_alpha<j<=a_alpha and h_j^+ count hosts with a_alpha<j<=b_alpha.

For 1<=j<=q, all carrier input coordinates are initially high. The initial target rows are low, so subtracting them from the required final low target rows exhibits the r-dimensional row space SX modulo W_j^0. Every descending host contributes its own further independent coordinate d_alpha, absent initially below this cut. Because the entry variables are independent and these host roles are disjoint from the carriers, the combined required quotient rank is

\[
 r+h_j^-.
\]

Thus D_j>=r+h_j^-. Conversely, ascending host dirt is initially low and must appear independently at a high endpoint; the symmetric lemma gives U_j>=h_j^+. For j>q, retain just the host inequalities D_j>=h_j^- and U_j>=h_j^+.

Summing (A),

\[
 M\ge qr+\sum_j(h_j^-+h_j^+)
   =qr+\sum_\alpha|a_\alpha-b_\alpha|.
\]

That proves (H). ∎

For hosts that all travel logically from height 8 to height 0, H_end=8 times the number of independent hosts. If their useful hosting credit is exactly that endpoint quantity, q=8 gives the author's displayed inequality. With r=8 it gives 64 mass beyond that credit. This is arithmetic substitution into a proved conditional theorem, not an independent verification of the selected S.

The rank over Q remains the same over C for a rational matrix: a nonzero maximal rational minor remains nonzero, while larger minors already vanish. The binary ranks of frame functionals in §3 have a different role and do not supply r here.

### 5.3 Less restrictive checkpoints and fixed continuations

The simultaneous exit above is convenient, not essential. By the history version of the cut lemma, targets may acquire their clean low rows first and hosts may be restored at appropriate low/high frames later, provided every intervening transport is included and the same joint quotient-rank demands hold. Thus a later restoration is not automatically an escape. Restoration **only above a cut**, however, does not give a clean host row below that cut.

When an unchanged prefix is invertible on the ordinary state and the unchanged suffix is invertible on that state, with no extra interactions outside the replacement, exact whole-program equality fixes the replacement map by cancellation. This is one sufficient way to justify the centre-boundary shear Y -> Y+SX. A prefix invertible on the ordinary boundary state preserves the independence of those ordinary coordinates. Private work that is zero at the chosen boundary adds no entry information; reversibility only on a larger live state does not establish either condition.

But “A and B fixed” alone does not say whether extra host interactions may be inserted after B, whether cleanup changes, or whether gauges/owners/targets can be moved at additional times. One must provide that continuation contract. Enlarging the billed interval to include later fixed operations also changes the invoice being bounded: their cost cannot simultaneously be ignored and used to finance the required crossings.

## 6. Exactly what remains to instantiate the stronger public claim

The following are specific interface/data obligations, not a demand for a tree normal form.

**Entry and communication boundary.** Supply the entry register/frame list, the host roles, their independent arbitrary-dirt contract, and any saved values or pre-positioned copies. Either justify an independent ordinary-register coordinate basis at the chosen boundary, or provide the actual coefficient rows. In the latter case apply (C-down) directly. Distinct physical owners prevent aliasing but are not, by themselves, a proof about the current coefficient-row span.

**Endpoint and credit binding.** For each credited host, provide its entry/exit gauges, the exact physical pending factor it replaces, and the time/frame at which its original logical value is restored. Show that the claimed hosting credit is H_end, or supply another justified per-cut credit allocation with the requisite independent rank demands. Count each useful pending factor once. A loop or repeated use of the same dirt is not automatically another independent hosted direction.

A concrete reason this matters is that two different one-dimensional frames A=span(e_1), B=span(e_2) have transition rank 2 in the supplied frame metric, but equal heights. Thus “useful width” is not generally identical to endpoint height displacement. This is an accounting-interface warning, not a counterexample to the proposed selected-word bound. The inherited canonical wrappers and host charts may establish a suitable identification on a specified implementation; it has not been supplied for all proposed dirty-centre replacements. [S1], [S2], [S6]

The frame notes supply a further concrete source control. For a dirty role entering with gauge T_sigma, they prescribe terminal gauge F T_sigma and a tail of rank h-dim U+dim sigma after its last active frame U containing sigma. The complete endpoint on that role is F. Writing e=dim sigma, their complementary terminal preimage frame has height h-e, so its entrance-to-terminal height displacement is |h-2e|, whereas F has Fourier rank h. The notes do not misprice this: the active ascent and the prescribed tail together have rank mass h. This illustrates why a whole useful factor cannot universally be replaced by H_end under every inherited gauge convention. It does not contradict an explicitly normalized 8-to-0 dirty-centre contract; it makes that normalization/credit binding an actual obligation. [S1]

**Permitted events and billing window.** Fix copy/overwrite/erase permissions, zero versus dirty extra work, whether centres can interact, any nonnested transports, and all frame-changing adapter/route actions. All nonzero communication across a cut must be represented. State whether temporary target/source modifications, borrowing through later B/tail operations, and delayed restoration are allowed. Interior cycles need not be banned if this contract holds.

**Small selected-data receipt for the cut claim.** Supply the actual rational 88-by-8 scatter matrix with carrier and target ordering, centre entry frames, target observation frames, and an exact rank certificate, such as a nonzero 8-by-8 minor. Bind these to the selected canonical word/replay artifact. This is enough to check the numerical rank premise without rerunning an optimization or supplier suite. The selected registry alone is not that matrix. [D1], [S7]

**Separate small receipt for the tree application.** Supply each F_k, its served target list, and those targets' final binary frames/functionals, with artifact hashes. Exact intersection ranks then suffice. The unpublished `relaxed_levels.py` computation cannot be inferred from a generic emitter or older ancestor geometry. [D2]

The local GF(3) search scripts and all five rule sets would additionally be needed to certify the reported exhaustive searches. They are not needed for the quantified written theorem above, and were not replaced here by an unrelated finite search. No assessment of Discussion 1587's separate bound or follow-up is included.

## 7. Exact scope illustration: why the entry condition is real

This is a small example in a deliberately broader common-frame model, **not an in-scope counterexample to the fixed selected word**.

Use frames F of dimension 8 and 0. Let X=x and H=d initially be at F; let Y=y be at 0. In addition, suppose a register B=d is **already at 0**. The underlying x,d,y are arbitrary independent values, but B is a pre-positioned duplicate of H, not a fourth independent dirty input.

At common frames perform

```
H += X                 at F
H: F -> 0              one rank-8 transport
Y += H                 at 0
Y -= B                 at 0
H <- B                 at 0
```

The endpoints are X=x, Y=y+x, H=d, B=d. The only transport in this deliberately truncated region costs 8. The host itself has an F -> 0 endpoint, and the scatter matrix is [1]. Nevertheless, the naive subtraction would incorrectly demand 8+8=16.

The actual cut lemma is not violated: the initial low span already contains d and y. Modulo that span, the demanded x and d have joint rank **one**, not two. Including the earlier copy/transport that prepared B at frame 0 would restore the missing charge in the straightforward preparation. This demonstrates why the interval and its complete entry state must be fixed before asserting a rank sum. It does not assert that such a preparation is permitted for the author's selected A/B interface.

The final overwrite is legal in the named scalar relaxation. Even if overwriting an ordinary dirty register is not primitive, it can be replaced at frame 0 by `P <- H; H -= P; H += B; clear P` using zero private work, without additional transport. That substitution does not repair the violated entry hypothesis.

## 8. Finite checks actually run

`check.py` is original standard-library code. It imports no repository module, executes no downloaded program, performs no network access, and is not a replacement production checker. Its input rows are exact Fractions; its frame subspaces are explicit binary bases. It checks logical coefficient identities, not 512-address Gaussian-dyadic implementations, phases, routers, or owner maps.

| Exact fixture | Paid mass in the toy model | What it checks |
|---|---:|---|
| Three-transition dirty repair | 24 | Clean scatter and host restoration; source's abstract three-move algebra, not its selected receipt |
| Independent two-transition save/reload | 16 | An explicit attaining small contract with hosting credit 8; not claimed to reproduce the unpublished script |
| Two mixed independent carriers | 16 | Two independent combinations still require two rank-8 down transports |
| Same mixing with an upward/downward round trip | 32 | Cycles are accepted by the named model and fully counted |
| Ascending independent host plus clean scatter | 16 | Opposite-direction host demand is counted by U_j |
| Pre-positioned dirt example from §7 | 8 | Outside-contract illustration; the correct joint quotient rank is one |

The checker also enumerates all 16 subspaces of F2^3, verifies the ambient H_e construction for all 66 ordered contained pairs, checks 256 two-leaf trees, and checks a tight three-leaf example. It explicitly distinguishes a rational rank-two matrix from its rank-one reduction modulo two.

Eleven rejection controls cover contaminated endpoints, cross-frame add/copy, zero/underpaid transitions, ordinary dirty erasure, nonzero private work, incomplete endpoints, equal-height unequal frames, and the falsely asserted independent host rank in the pre-positioned example. These controls use explicit exceptions, not `assert`.

Commands actually run, exit status zero:

```
python check.py > check-normal.json
python -O check.py > check-optimized.json
cmp check-normal.json check-optimized.json
```

Both executions report `PASS_SMALL_EXACT_AUDIT_CONTROLS`; their JSON outputs are identical. See `execution.json` for environment and hashes, and the two JSON outputs for the exact fixture/cut counts. These checks support implementations of small algebraic controls. They do not machine-certify the universal written proofs or any selected-word rank-8/64 premise.

## 9. Prospective Discussion finding (not posted)

**FINDING — independent conditional proof/interface audit.** I checked ctoth's literal branching-tree proof: it is valid with free node copies, nested descent costs, and served nodes contained in final target frames. The reported eight trivial final-frame meets remain source premises; I did not rerun `relaxed_levels.py`.

For the earlier dirty-host inequality, a tree reduction is unnecessary. In the scalar common-frame transport model, cut at each height j and quotient all low-side coefficient rows by their complete entry span. Each high-to-low one-register transport adds at most one direction, even with mixing, upward moves, cancellation, and reuse. For independent carrier/host inputs, clean height-zero scatter of rank r, and restored hosts whose endpoint height changes justify hosting credit H, summing the directional bounds gives paid mass >= H+8r.

This is a quantified conditional corroboration, not admission of every proposed dirty-host implementation. The remaining binding is the exact entry/endpoint and hosting-credit contract, including pre-positioned values, late cleanup, wrappers, and the complete charged interval. Common-frame legality alone does not supply that binding; the old private-centre checker is not the extended hosting grammar. A small exact example with dirt already copied below the cut illustrates the missing entry condition, not a counterexample to the selected word. No independent selected scatter/meet computation, price, or frontier result is claimed.

Credit ctoth and the disclosed GPT-6/Codex, Gemini 3.8 Flash/Antigravity, and Claude Opus 5.5 reviewers; retain icekylinx and inherited frame/emitter/checker attribution. New audit work: Andrey Mas with GPT-6 Pro through ChatGPT. Small original checks pass normally and under `-O`; not human- or kernel-verified.

## 10. Source access, attribution, and reproducibility limits

Both Discussion comments and the pinned mathematical/checker texts were accessible as text through the web tool. The supplied inline excerpts were also used. The main checkpoint's AGENTS, autoresearch guide, revision-3 catalogue, and Discussion 1163 were consulted for scope/context; no repository command or supplier suite was run.

**Byte-fetch failure:** direct raw-file downloads into the execution container failed with DNS resolution errors; a separate download-tool attempt for the selected record also failed. Therefore this review does not claim an independent raw-byte SHA256 or Git-blob verification. Web text access is not byte binding. `source_manifest.json` records successful text observations separately from those download failures.

The supplied selected-record SHA256 is `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`; it was **not independently verified here**. Mathematical/checker source URLs retain pin `81e81af67714bdc8d1693b0bf5c29468b92f62ff`; guidance was read at `0a201997097b8a89b638f3a2afcb35db4184c8b2`. The operator's byte-identity statement between those checkpoints is not relabelled as this review's computation.

Credit for the original findings, experiments, and tree proof belongs to ctoth and the explicitly disclosed reviewing models: GPT-6 via Codex, Gemini 3.8 Flash via Antigravity, and Claude Opus 5.5. Their reported finite reruns are kept distinct from their hand argument. The frame exposition credits icekylinx with OpenAI GPT-6 Astra assistance and Codex integration; the emitter retains icekylinx/PR425/PR433 and DreamingOfClouds gauge-extension attribution; the auditor identifies its PR514/PR433 lineage. The source owners' inherited contributions are not claimed anew.

New substantive proof audit and small checker: Andrey Mas with GPT-6 Pro through ChatGPT. Per the handoff, Codex collected sources/coordinated; no external agent supplied the mathematical derivation in this review. No external post or repository change was made. This artifact makes no H2/K, native/hosting-admission, precision/tape, all-size, analytic-transfer, or kappa claim.

### References

[D1]: https://github.com/CrocSwap/integer-mult-bounds/discussions/1516#discussioncomment-18913724
[D2]: https://github.com/CrocSwap/integer-mult-bounds/discussions/1516#discussioncomment-18913740
[S1]: https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/81e81af67714bdc8d1693b0bf5c29468b92f62ff/notes/general-clifford-frames.tex
[S2]: https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/81e81af67714bdc8d1693b0bf5c29468b92f62ff/research/e8-complex-gauge-kernel/PROOF.md
[S3]: https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/81e81af67714bdc8d1693b0bf5c29468b92f62ff/research/gauge44-barch/independent/CENTRE-GUARD-REVIEW.md
[S4]: https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/81e81af67714bdc8d1693b0bf5c29468b92f62ff/research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/code/hpe_emit_local.py
[S5]: https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/81e81af67714bdc8d1693b0bf5c29468b92f62ff/research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/code/hpe_audit_local.py
[S6]: https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/81e81af67714bdc8d1693b0bf5c29468b92f62ff/research/idle-axis-hosting/PROOF.md
[S7]: https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/81e81af67714bdc8d1693b0bf5c29468b92f62ff/certificates/selected-result.json

The references resolve to D1 (original FINDING), D2 (separate DONE/RELEASED tree argument), S1 (frame geometry), S2 (common-frame semantics and helper interfaces), S3 (centre/owner guard context), S4 (emitter), S5 (auditor), S6 (older idle-axis hosting), and S7 (selected registry). Source-file observations are not production replay certificates.
