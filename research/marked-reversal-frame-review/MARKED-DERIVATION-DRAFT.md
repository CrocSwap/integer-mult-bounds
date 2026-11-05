# Abstract marked counterless reversal derivation

## Verdict, role and exposure

The target marked-reversal implication is valid under the explicit annotated-predecessor and footprint hypotheses below. This is an abstract derivation of a known target for the external review of Nick Petalas's PR6127, not a new counterless protocol, machine count, tariff, sampling-law or expected-bit theorem.

The coordinator supplied the target statement, including the crucial binary lookahead at s+T. Before this draft was sealed I did NOT read the current6127 PROOF, machine, peer or coordinator draft. Historical source context is not excluded: I previously read6124's discussions and earlier6127 PR-body/search snippets about the6127 fixed-(1,1) successor and participated in B13S3's6072 all-depth review. This is target-known, not blind discovery. No source/new scientific program, machine, constructor, import, compilation, census, numerical experiment, test or kernel was executed. Only this written note and metadata hash/time operations were authored. Actual source/table binding remains for post-seal review.

## 1. Precise graph and ABI hypotheses

Let Q be a finite set of pending graph states, q0 its fixed initial root, and H a set of phase-annotated terminal states. Each h in H has output label ell(h) in the four-symbol XOR group {0,1}^2. The deterministic forward transition is

    delta: Q × {0,1} -> Q union H.

A source terminal annotation retains every graph phase needed for inversion, not only its two-bit output label. There is a partial predecessor function pred(z,b) with the following property on all declared forward edges:

    pred(delta(p,b),b)=p,    p in Q, b in {0,1}.

Equivalently, for each destination z and resident coin b there is at most one pending predecessor p, and the function returns it whenever that edge exists. This condition includes edges into phase-annotated terminals. No assertion is made about the artificial absorbing terminal loops used for unrelated forward-Moore proofs; they are not sampling transitions to invert here.

For a fixed starting tape position s, let a finite terminating graph path consume b1,...,bT at cells s,...,s+T-1. Its states are q0,q1,...,qT, with qk=delta(q_(k-1),bk), qk pending for k<T and qT terminal. For the fixed DDG the root is pending and T>=1. The theorem covers every such finite T, with no cap and no fairness assumption. A zero-bit-terminal extension would need its separate trivial entry case and is not asserted for this fixed graph.

The complete invocation footprint requires:

- the consumed cells s,...,s+T-1 contain those binary coins;
- the unconsumed cell s+T is also READABLE BINARY, even though its value is not used as a graph coin;
- s-1 is a separately owned blank cell, available to mark and restore;
- the output is a stationary, arbitrary dirty four-symbol cell A, with its head fixed;
- source coin cells are never overwritten; moves/read/write/marker domains are respected; mode/phase controls retain the information specified below.

All other input/output tape cells and heads outside the declared footprint can contain arbitrary data and can be arbitrarily correlated with this input and A. Other markers outside the footprint do not matter. A global assumption of one marker everywhere is unnecessary; the scanned prefix/looking cell must be binary and the particular s-1 marker must be owned. The source machine's local symbol rules must actually implement these premises before this abstract argument applies.

## 2. Why phase plus a resident coin can supply a unique predecessor

For the original phase/node DDG form, let phase phi have an increasing list of leaf labels, of length c_phi. A pending state is(phi,j), and coin b chooses child v=2j+b. If v<c_phi it enters annotated terminal(phi, leaf_at_v); otherwise it enters pending((phi+1) mod L, v-c_phi).

For a pending destination(phi',j'), its predecessor phase is phi=phi'-1 mod L and its predecessor child rank is j'+c_phi. With b resident, the only possible old node is

    j=(j'+c_phi-b)/2,

subject to being an integer in that phase's allowed range. For a terminal(phi,i), label i occurs at most once in the phase's leaf list. If its position is v, the only possible old node is `(v-b)/2`, again subject to range/parity. Thus annotated destination plus resident b determines at most one predecessor. This is a structural reason for the hypothesis, not a run of the6127 table or a recomputation of its inventory.

Discarding the terminal phase can invalidate that uniqueness: the same label may occur at different phases. Likewise a phase-merged forward quotient does not automatically inherit this inverse condition. The predecessor relation must be checked for the exact original graph and terminal annotations used by the actual machine.

## 3. A counterless marked scan with an exact reverse invariant

First prepare the owned marker at s-1 and return the input head to s. Keep separate forward, backward-look and predecessor-read modes. This is an explicit use of one owned blank and actions on it, not free marker creation.

Forward traversal keeps qk and places the input head at s+k after k consumed coins. Each forward edge reads bk+1 at the current head, updates by delta and moves right. On termination it therefore holds annotated qT and has head at s+T. Retain that terminal annotation while applying

    A -> A XOR ell(qT)

at the stationary output cell. Do not overwrite A by the leaf or discard the terminal annotation before inverse stepping.

The backward invariant is:

    mode B(qk), input head s+k, coin tape unchanged,

where k is a proof index, NOT a stored counter. Initially k=T. Implement one reverse cycle as follows:

1. In mode B(z), read the current binary cell without changing it and move LEFT, entering a predecessor-read mode R(z).
2. If that cell is binary b, replace z by pred(z,b), leave the cell unchanged, and enter B(pred(z,b)) at the same head.
3. If it is the owned marker, accept cleanup only when z=q0. Restore the marker cell to blank, move RIGHT to s, and finish at the fixed exit port.

For k>0, step1 moves to s+k-1, which contains bk. The predecessor property gives pred(qk,bk)=q_(k-1), so step2 establishes the invariant with k-1. For k=0, B(q0) is at s; its left move reaches precisely s-1, the marker. Cleanup restores the owned blank and returns the original head s. It does not attempt to invert an incoming positive-depth edge into q0 that pred might otherwise permit.

The first B step at k=T reads s+T BEFORE moving left. That is why the unconsumed binary lookahead is inside the actual readable footprint. Each later B step reads a consumed binary cell. None of these ignored lookahead reads supplies an additional graph coin or changes the logical T, but they are real machine accesses whose bill belongs to the source's separate cost proof.

A positive-depth revisit qk=q0 is harmless. For k>0, the cell to the left is still bk, not the owned marker, so the procedure continues. Root control alone cannot distinguish the original entry from a wrapped forward cycle; the marker supplies that spatial discriminator. No T or stopping counter is retained.

The reversal ends with every input coin, the lookahead and all ambient cells unchanged; the owned marker cell is blank again; input/output heads are at their declared original positions; and the sole data change is the dirty XOR. Final finite control is the declared exit port, not silently identified with the initial entry control.

## 4. Exact endpoint map and arbitrary correlations

For a valid terminating input configuration x let i(x) be its deterministic leaf label. The data endpoint is

    F(x,A)=(x,A XOR i(x)).

For each fixed x, XOR is a bijection on all four dirty output values. Because x is restored, the inverse data formula is the same XOR using the same i(x). Identifying the fixed service entry/exit ports as an ABI map, this is an involution on its valid terminating data domain. It does NOT mean a halted literal machine can be invoked again without the caller supplying its proper entry control, or that an unrelated control reset is free.

The proof is pointwise for every valid x and A. It therefore tolerates arbitrary correlations with protected ambient data and between the output and tape; no product-distribution assumption was used. Under an independently supplied fair tape one may separately inherit the original sampler's law, but neither fairness nor almost-sure termination is needed for this conditional endpoint identity. Nonterminating forward paths have no completed return endpoint here; finite graph control is not a finite T bound or a total halting theorem for all infinite tapes.

Restoring a tape's symbols is not restoring its statistical independence from the output. The output mask i(x) is a function of the resident tape. For a nonconstant output function, observing it changes the distribution of that tape under a random input law. Reusing the same restored prefix gives the same leaf, not an independent fresh sample. No unconditional fresh-entropy, zero information-retention or cost-free reversible-cleanup claim follows.

## 5. Endpoint injection versus reversible finite rules

The preceding invariant proves endpoint injectivity and a data inverse for the declared reached states. Calling the actual machine a reversible partial finite-rule implementation additionally requires its actual transition semantics to have a unique predecessor on the claimed configuration domain. An injective endpoint map alone is insufficient: a program can erase and later recreate information from an uncounted record while still having that endpoint.

Sufficient local obligations include disjoint scan modes, retention of terminal phase through the XOR handoff, no loss of resident coins, the exact delta/pred edge correspondence, valid partial marker write/erase domains, and uniquely reversible move/control/output updates. The forward edge can be recovered from its retained destination and the untouched coin immediately to the left. The predecessor-read update can be recovered from its pending predecessor and resident coin because delta is deterministic. Plain moves retain tape data, and XOR with a retained leaf is locally bijective. Marker preparation/cleanup use the known owned blank and dedicated entry/exit modes. Their compiled rules still need source inspection for unintended incoming-rule collisions, directions, read-symbol coverage and invalid-state behavior; this abstract note does not certify an unseen transition table.

No reversibility promise is made for arbitrary malformed states, invalid marker layouts or unrelated ambient configurations that violate the symbol/ownership hypotheses. A claim of a global permutation on all same-size hardware states, or cleanup of every retained stochastic service, would be strictly stronger than this reached-domain theorem.

## 6. Written weakening controls — UNEXECUTED

1. **Omitted lookahead.** A terminating coin prefix may be followed immediately by blank or a nonbinary marker. The graph path itself remains defined, but the actual B step's initial binary-read premise fails at s+T. Hence “arbitrary data just outside the consumed T cells” is too weak; that one extra readable cell must be in the contract.
2. **Unowned dirty marker cell.** Overwrite an arbitrary old symbol at s-1 with the marker and clear it to blank later. Different original symbols merge unless their old value is retained/restored. The declared owned blank avoids that loss; it is an input resource, not something the procedure manufactures.
3. **Stop on root rather than marker.** For any terminating path with a positive-depth root return, stopping as soon as reverse control becomes q0 ends at the wrapped root, leaving the head displaced and marker uncleared. The marker test instead continues until the actual left boundary. This is a hand weakening argument, not an executed long-path fixture.
4. **Forget terminal phase / wrong inverse.** If two same-coin incoming edges from distinct pending states reach one unannotated terminal label, a reverse rule using only that label and coin cannot choose both predecessors. Choosing an arbitrary predecessor fails one path. Correct phase annotations and pred are necessary; a forward-equivalent phase merge does not prove their preservation.
5. **Overwrite dirty output.** Replace XOR by `A=i`. Two distinct dirty initial values then have the same final input/output data. The required XOR preserves both cases and gives the stated bijection.
6. **Delete resident coins early.** Clear consumed bits before their predecessor-read steps, or move left twice before decoding a coin. The retained destination may then be paired with the wrong bit and select a wrong/nonexistent predecessor. Tape restoration at the final endpoint cannot be inferred after losing that invariant.
7. **Claim fresh restored randomness.** Even a one-coin nonconstant output b leaves a restored b correlated with output b. The same information issue applies to a DDG leaf function. Symbol restoration alone supplies no unconditional independence or fresh-input entropy claim.
8. **Conflate endpoint and local reversibility.** Add a lossy hidden overwrite followed by reconstruction from an uncounted extra record. A correct public endpoint does not certify that operation's partial inverse or record/stock cost. Actual local finite-rule claims need their own predecessor check.

These are deductions about weakened hypotheses, not source defects or observed mutation outcomes. No source tariff/controller count, expected draw formula, sampling law or numerical certificate was recomputed.

## Credit and remaining obligations

Nick Petalas6127 retains the known owned-marker counterless protocol and its actual resource theorem. JoyboyBrian6102 retains resident-transcript reversal and its predecessor condition; zxv6072 retains the fixed paired-DDG construction/law/expected-bit result. The prior6124 forward-sharing quotient is a different interface and does not transfer inverse uniqueness. Classical reversible-computation and XOR/data-retention principles are not new here. Substantial OpenAI Codex assistance produced this known-target written derivation.

Post-seal source review must bind actual terminal annotations, inverse table, lookahead-read grammar, owned marker preparation/erasure, head/output modes and protected cells. This note does not rediscover or accept source3T+4/2T+4 tariffs or controller inventories, price sampling/tape movement, establish fresh randomness or global-state physical reversibility, admit an actual caller, discharge any selected framework hypothesis, or change κ/frontier/adoption.
