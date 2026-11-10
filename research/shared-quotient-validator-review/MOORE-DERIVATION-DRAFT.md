# Abstract derivation for the shared-dispatcher refinement review

## Scope, verdict and exposure

**Verdict: the supplied refinement, homomorphism and residual-state implications hold under the explicit hypotheses below.** In particular, omitting the previous state's own color from the refinement signature is sound when refinement starts exactly from observable behavior. Equality of successive class counts then implies equality of relations, even if integer color IDs are renamed.

This is a source-aware written derivation of propositions supplied for the review of Nick Petalas's PR6124, head `9ae1d82f4e248dd830e32c4d2a0330b62cddc1dd`, `research/shared-residue-dispatcher`. The target propositions and earlier source/dispatcher context were known; historical source exposure is not excluded and no blind-discovery claim is made. No current source proof/code or peer draft was opened for this assignment before sealing this note. The eventual source-to-validator correspondence has not yet been checked by this abstract argument.

No scientific/source program, import, compilation, constructor, census, finite experiment, native operation or proof kernel was executed. This does not establish new dispatcher counts or resource values. The source result and classical Moore-machine/minimization methods retain their credit. Physical state accounting and stop conventions are explicit rather than inferred from a color count.

## 1. A precise finite observation-graph model

Let S be a finite nonempty set, B={0,1}, and delta:S×B→S a total deterministic transition function. Let o:S→O be the observation map. Observation values are exact semantic labels, not auxiliary implementation identities. Declared roots are rho(x) in S for a specified set of external configurations x.

For a word w=b1...bn, write delta*(s,w) for successive transition application and delta*(s,empty)=s. The complete observation behavior from s is the observation at every finite prefix, including at the initial state. For stopped samplers, observations must distinguish continuation from every terminal output. A run stops on its *first* terminal observation, possibly at depth zero, and consumes one bit per transition before that observation.

To identify this total Moore behavior with stopped behavior, terminal observations are represented canonically by absorbing terminal states (one behavior per terminal label), or equivalent unobservable post-stop transitions are explicitly ignored in the definition. Otherwise arbitrary transitions after a stop can create irrelevant distinctions. The proof below uses the absorbing normalization. Introducing those terminal states is a modeling convention; whether their labels are counted inside or outside an implementation's control-state bill must be stated separately.

No probability assumption is needed for trace preservation. Fair iid bits can later assign probabilities to these pointwise behaviors, but cannot repair a wrong transition or justify an uncounted random initial state.

## 2. Refinement without the previous own color

Define relations R_h on S inductively by

    s R_0 t  iff  o(s)=o(t),
    s R_(h+1) t  iff
        o(s)=o(t) and
        delta(s,0) R_h delta(t,0) and
        delta(s,1) R_h delta(t,1).

Each is an equivalence relation. If c_h encodes R_h classes bijectively onto the used color IDs, the next equivalence is exactly equality of signatures

    sigma_(h+1)(s)=(o(s),c_h(delta(s,0)),c_h(delta(s,1))).       (1)

No previous own color c_h(s) is present in (1). No assumption is made that old and new integer IDs correspond numerically.

### Finite-word characterization

For every h>=0,

    s R_h t  iff  o(delta*(s,w))=o(delta*(t,w))
                     for every word w of length at most h.    (2)

At h=0 this is the observation definition. For h+1, the empty word tests the immediate observation. Every nonempty word begins with one bit b, followed by a word of length at most h, so the two successor R_h conditions are precisely the remaining tests. This proves (2) by induction.

Consequently R_(h+1) is a refinement of R_h: matching all words of length at most h+1 implies matching all words of length at most h. Equivalently, one can prove monotonicity directly from R_1⊆R_0 and the successor recursion. Starting from the observation relation is essential to this implication. It is not a fact about arbitrary initial colorings when the old own color is omitted.

### Equal class counts mean a stable relation

Let K_h be the *actual* number of R_h equivalence classes. Since S is finite and R_(h+1) refines R_h, every old class is a disjoint union of one or more new classes. If K_(h+1)=K_h, no old class can split; therefore

    R_(h+1)=R_h.                                             (3)

This is equality of relations, not equality of their numeric color arrays. Renaming every ID leaves (3) true.

The recursion is a function of the relation itself. Thus once (3) holds, every future relation is the same. If it does not hold, at least one class splits and the count strictly increases. There can be at most |S|-K_0 strict splitting rounds. At a stable relation R_*, formula (2) and continued stability prove

    s R_* t  iff  their observations agree for every finite word.   (4)

For any pair not in R_*, some finite word distinguishes them; indeed the first depth at which their relations differ supplies one. This is a finite distinguishing-continuation result, not a test limited to the recorded iteration depth.

## 3. The quotient and complete homomorphism preservation

Because R_* refines R_0, observation is constant on each class. Because it is stable, successors of equivalent states remain equivalent for both bits. Thus the quotient has well-defined observation and transition functions

    o_bar([s])=o(s),
    delta_bar([s],b)=[delta(s,b)].

The class projection is surjective and preserves both edges and every named root. More generally, let Q be another deterministic observation graph and let h:S→Q satisfy all of the following:

1. h is defined on every source state and surjective onto all claimed target states;
2. o_Q(h(s))=o_S(s) for every state;
3. h(delta_S(s,b))=delta_Q(h(s),b) for every state and both bits;
4. the target root for each declared configuration x is exactly h(rho_S(x)).

Induction on word length gives

    h(delta_S*(s,w))=delta_Q*(h(s),w)

and therefore equal observations at every finite prefix. Surjectivity is not necessary for this forward trace equality, but ensures that the claimed target state inventory contains no extraneous behavior not covered by the source. Exact root mapping prevents a correct graph map from being used with a wrong configuration entry.

Terminal status is part of the preserved observation. Hence the initial state and every later prefix are terminal on one side exactly when they are terminal with the same label on the other. Their first stop index, output and number of consumed bits agree for every finite bit tape, including tapes ending before either run stops. A tape ending before the first terminal observation is unresolved on both sides; it is not an additional output.

For an infinite bit stream, equality at all its finite prefixes proves the same dichotomy pointwise: both runs stop at the same finite index with the same label, or neither ever reaches a terminal state. There is no inference from finitely many tested tapes and no appeal to probability-zero exceptional paths. In particular, a possible infinite nonterminating tape is preserved even if fair-bit probability later assigns it measure zero.

## 4. Distinguishing continuations and the correct lower-bound scope

Consider a reachable R_* class. Reachability here means that some declared root and a bit prefix before the first stop reach a representative, or reach a terminal class as the first stop. For two distinct such classes, (4) supplies a finite continuation w on which observations differ. With absorbing terminal normalization, a shortest distinguishing continuation cannot depend on transitions after a common identical terminal output: those would remain identical. Thus it is a real difference in immediate observation, continuation versus stop, stopping output or stopping index.

Any deterministic realization of exactly this residual behavior must distinguish those two situations in its *complete behavior-relevant configuration*. If it placed them in the same complete configuration, then on the same future bit stream and the same future external inputs it would behave identically, contradicting that finite distinguishing continuation. Therefore it needs at least as many distinguishable reachable configurations as there are reachable R_* classes. The quotient realizes exactly those residual classes, so it is minimal in this deterministic observation-graph model.

Several qualifications cannot be omitted when converting that statement into an implementation bill:

- If some source/quotient classes are unreachable from the declared roots before first stop, they do not prove a lower bound for those executions. Either restrict to the reachable part or separately establish each counted class's reachability.
- “Complete configuration” includes any retained parameter, external table selector, phase, input cursor, tape/history location or entropy state that can influence future behavior. A free external residue parameter can distinguish two residuals even if the mutable local control register has the same value. A bound on all residual configurations is not automatically a bound on that register alone.
- Terminal outputs may be emitted on edges rather than retained in internal control states. The minimum number of Moore observation states, including terminal classes, must not be relabelled as the minimum number of nonterminal machine-control states without matching that representation convention. Counting a combined control/output configuration is different from charging only a mutable control register.
- If C distinct complete configurations must be encoded by a binary state representation, at least ceil(log2(C)) bits are needed for that representation. This is an information-capacity consequence, not a physical transition, movement, cleanup, table-access or stock invoice.
- The comparison is deterministic given the bit stream and all accounted inputs. Free initial random state or a different observational contract changes the realization problem.

Thus the finite-continuation argument is rigorous, but an unqualified physical-memory minimum or a count of only some retained fields would need further source/interface premises. No new numerical class count is established by this abstract proof.

## 5. What sorted-adjacent validation actually proves

Fix a refinement round. For every source state s, suppose a validator receives its exact signature sigma(s) from (1) and a claimed next color c(s). Before the following argument, the source state list must be complete and duplicate-free, both transitions/observations must be bound to the actual source graph, and the sort/comparison must use exact signature equality and a consistent total order. Otherwise validating a sorted subset would not validate the full graph.

Sort the states by signature. They split into B nonempty consecutive signature blocks. Check for every adjacent pair in that sorted list:

    same signature -> same claimed color,
    different signature -> different claimed color.          (5)

The first check, propagated through each block, proves that c is constant on each entire signature block. It therefore defines a function f from the B signature blocks onto the set of actually used claimed colors. The second check says neighboring blocks have different colors, but **does not alone prevent nonadjacent blocks from sharing a color**.

Now require that the actual number of distinct used colors is exactly B. Because f is a surjection between finite sets of the same size, it is a bijection. Thus distinct signature blocks never reuse a color, adjacent or not, and

    c(s)=c(t)  iff  sigma(s)=sigma(t).                       (6)

This is precisely the required next equivalence relation. The different-signature adjacent check is a useful local guard, but the global used-color count is what excludes nonadjacent reuse. In fact constant-on-blocks plus that exact global cardinality already implies the bijection.

If a declared class count K is used, it must be tied to the *actual* distinct-used-color count, for example by genuine bounded IDs and verified use of every ID. Merely comparing a declared K or max(color)+1 to B is insufficient when some IDs are unused. Signatures and used classes must be counted in the same complete state domain. This argument certifies one round's relation; the stable-count conclusion additionally needs the observation start and monotonicity from Section2.

An implementation may assign completely different integer IDs on successive rounds. Relation correctness (6), not numerical ID continuity, is the essential invariant. When actual class counts are equal in consecutive valid rounds, Section2 proves stable semantics despite that renaming.

## 6. Written weakening controls — all UNEXECUTED

These examples challenge altered hypotheses/validators; they are hand deductions, not observed tests or source defects.

1. **Arbitrary initial colors can invalidate equal-count stopping.** Take three states a,b,c with the same observation and delta(s,0)=delta(s,1), with a→a, b→c, c→a. If the initial coloring is artificially `{a,b}|{c}`, successor-signature refinement gives `{a,c}|{b}`: the count stays two but the relation changes. The next round merges all states. Starting exactly from the observation relation would already place all three together and avoids this false premise.
2. **Nonadjacent reuse survives adjacent inequality.** Three distinct sorted signature blocks A<B<C assigned colors0,1,0 pass every neighboring different-signature/color check. They are not a bijection. The actual global count is two rather than three, so the required cardinality check catches it. Declaring count3 with an unused ID2 must not be accepted as if the distinct-used count were three.
3. **Cardinality alone does not make colors constant on a block.** Sorted signatures A,A,B,B with colors0,1,0,1 have two signatures and two used colors, and the different-signature boundary changes color. They still split each equal-signature block. The same-signature adjacent checks are necessary.
4. **Omitting one edge can destroy tape preservation.** Two states with the same immediate continuation observation and the same0-successor can have1-successors with different terminal labels. A validator checking only0-edges merges a pair distinguished by the one-bit continuation1. Both successor coordinates in (1) and both homomorphism edges matter.
5. **Wrong roots can invalidate a valid graph map.** Even an otherwise valid homomorphism does not certify a configured run if its selected target root is not the image of the named source root. Root/configuration binding is separate from edge/label preservation.
6. **A finite prefix is not a fixed point.** A long chain ending in a terminal output and a continuing loop can have the same observations through an arbitrarily chosen finite test depth while differing later. Valid stable refinement excludes this; testing some tapes without the stable-relation proof does not.
7. **Post-stop distinctions can be irrelevant.** Two states both immediately return the same output, but artificially defined outgoing edges lead to different labels. A total-graph refinement could split them for differences after the run already stopped. Absorbing terminal normalization, or a stop-aware equivalence operator, is required before using such a split for stopped-behavior minimality.
8. **A free retained selector changes state accounting.** Two configurations may use the same mutable local control label but different externally retained parameters to choose future outputs. Counting only that label does not count complete residual state. The configuration lower bound applies after the selector is accounted for, not by pretending it is absent.
9. **ID renaming is not semantic instability.** Two distinct observable absorbing states remain two singleton classes even if the next encoder swaps their color IDs. Equality of relations and counts holds; requiring bytewise equality of raw color vectors would be stronger than the abstract fixed-point criterion.

## 7. Credit and remaining proof-to-source obligations

Nick Petalas6124 supplies the shared-dispatcher result and its actual claimed values; no such value has been recomputed or established here. Moore refinement, behavioral quotienting and distinguishing-continuation minimality are classical. Retained paired-sampler/DDG predecessors and their notices keep their separate law/expected-bit/resource scopes. Historical source familiarity and AI assistance do not become blind, human or formal-kernel acceptance.

After this abstract draft is sealed, a source-to-validator review must still bind the actual observation alphabet, terminal convention, source/root/state coverage, signature computation/sort, actual-used cardinality checks, quotient surjectivity, both edges, class reachability and the exact implementation state-count convention. Without that binding, the note proves the implications above, not that an arbitrary certificate or implementation satisfies them. No source execution, native/physical hosting or cleanup invoice, adaptive/numerical integration, new optimal sampling law, kappa or selected-frontier change follows.
