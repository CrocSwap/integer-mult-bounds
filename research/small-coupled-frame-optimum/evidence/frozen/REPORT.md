# Exact restricted small-component optimum at the fixed power price

The 18 small components in both source orientations have the **same optimal paid histogram as the source**, at the exact parameter C=15108879/5000000000=0.0030217758. The optimum is

    {1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}.

Its histogram difference from the source is identically zero. There is no favorable native paid delta in this restricted domain, so this result does not justify a physical expansion. It does not optimize the 1,271-variable large component or any changed contact, scalar, warp, helper or caller contract.

## Source and domain

The input is 1337isnot1337's #4994 at ef2810fe43829960789f783e44ee6484d0368f09, retaining Dugongue's #4971 at 0130b196145a43a7d305de41f49e56e8e8556378. Astra's authenticated eight-blob SOURCE-MANIFEST and inspect_graph.py loader are reused, with their hashes recorded in RESULT.json. The loader executes only the retained swap constructor and loads the frozen frame-DAG code. This is an independent optimizer implementation using that source graph, not an independent reimplementation of the source graph or physical native semantics.

#4994 PROOF.md, “Binding the graph to the native word,” identifies its input as #4971's frame-carrying representation of Cao Yifan's native round-three source. Its SOURCES.json has base #4971 and pins SOURCE-WORD.json.gz SHA256 7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05, the retained native source used in the #4610 stream. The original histogram above reproduces that source's invoice, including eight owned rank8 calls. The graph representation and potential new frame realizations are successor contracts. Equal or improved local prices do not by themselves transfer the literal #4610 phase implementation, complete p16 caller, finite compiler reserve, rounding or outer theorem. No such transfer is claimed here.

For each small variable v the domain is every actual binary subspace S satisfying L_v<=S<=H_v. The implementation selects a complement of L_v in H_v, lists all quotient vectors and closes the set of possible subspaces under adjoining each quotient vector. Every quotient subspace is spanned by such vectors, so this procedure is complete. Actual subspaces are represented by 512-bit pointset integers, deduplicated and sorted. It checks binary closure, interval containment, complete Gaussian-binomial cardinality and source inclusion. The 68 domains are exactly 53 of size2,12 of size5 and3 of size16. The stored domain lists and chosen indices are in RESULT.json.

All 1,271 large-component variables and every determined contact remain at their original source subspaces. The 18 small components are derived from the variable graph; their node sets are compared with the frozen source-specific elimination ordering. No factor connects a small component to another variable component. Fixed neighbors become unary factors and remain in the objective. All parallel mapped edges are retained separately.

## Factors, recurrence and traceback

For every original mapped edge a→b with map G, its factor is H_(dim(S_b)−dim(S_a)) when G(S_a)<=S_b and is 5328 H1 otherwise. H0=0 and Hr=r^(1−C). This includes all internal multiedges and every fixed-neighbor unary. Edges with neither endpoint in the solved component are a constant and are excluded only from that component's minimization. Full reconstruction prices every one of the 29,790 mapped edges and adds the eight owned H8 calls.

The finite penalty is genuine: it is stored as 5328 units of H1, not discarded or silently converted to infinity. Every factor is nonnegative. The source provides a feasible component assignment whose cost is at most its rank mass, at most5327. Hence a minimizing component cannot pay even one infeasibility penalty. Full graph containment is independently checked after traceback rather than inferred from the objective.

At variable v, collect all factors whose scope contains v, sum them, and minimize over the complete domain of v for each assignment of the union scope minus v. Store both the resulting separator factor and the first minimizing domain index. Subsequent buckets operate on those exact factors. Reversing the elimination order reconstructs each v from its stored separator assignment. The original factor sum at the reconstructed assignment is checked equal to the bucket optimum. The source assignment's original factor cost is evaluated separately in every component and must be no smaller than the optimum. Equal histograms use the first sorted domain index, so ties are deterministic. Distinct unresolved histograms never use a source preference or floating-point tiebreak.

The fixed order visits 1,095 bucket assignments per orientation; its largest bucket has125 assignments. These are measured enumeration counts, separate from elapsed time. Both orientations select four contact changes under the equal-histogram tie rule. The source assignment itself is also optimal; these changes produce no improvement.

## Certified arithmetic

Costs remain integer histograms throughout summation and elimination. For a signed difference d, its interval uses d_r*lower(Hr) on a nonnegative coefficient and d_r*upper(Hr) on a negative coefficient for the lower endpoint; the upper endpoint reverses these choices.

The weights use rational series bounds. Write r=2^k u with1<=u<2. For x=2 or u put z=(x−1)/(x+1), so0<=z<=1/3. With n terms,

    A=2 sum_(j=0)^(n−1) z^(2j+1)/(2j+1),
    A <= ln(x) <= A+2 z^(2n+1)/((2n+1)(1−z²)).

Combine these bounds to bound ln(r). For positive y=C ln(r), bound exp(y) by the degree-n positive Taylor sum. The first omitted term is t_n*y/(n+1), and successive tail ratios are at most y/(n+2); therefore dividing that first term by1−y/(n+2) is an upper tail bound. Reciprocal bounds then enclose Hr=r/exp(C ln(r)). H1=1 and H0=0 are exact.

Start with24 terms. Each distinct histogram comparison must have a strictly signed rational enclosure; otherwise double the term count through at most384 and STOP on an unresolved distinct histogram. The executed runs required119 distinct comparisons,24 terms and zero refinements. The receipt retains each signed histogram difference, sign, series length and outward decimal interval, together with exact rational final weight endpoints. These decimals are display certificates derived by integer floor/ceiling; they never select an optimum. No floating-point number is used in the cost arithmetic. Runtime metadata alone uses a clock.

## Replays and controls

Run from this worktree:

    python3 outputs/pr4994-small-frame-dp/optimize.py
    python3 -I -O outputs/pr4994-small-frame-dp/optimize.py --output outputs/pr4994-small-frame-dp/OPTIMIZED.json

The default source path is the project-level outputs/mathematics-paper-research-20261023/frame-optimization snapshot. An explicit --source-root can replace its location; the loader still authenticates all eight frozen source hashes. No source file is written. The only generated artifact is the requested output JSON. The normal and optimized semantic receipts agree after removing elapsed-time fields. Logs retain measured runtimes.

Both orientations reproduce all original/least/greatest profiles, making six exact source-profile controls. Additional controls reject an actual out-of-interval full-space contact assignment by the full graph checker; detect the histogram change from removing a paid mapped edge; and exhibit an actual mapped edge where replacing its native map with identity violates the source containment. The source fallback, complete domain census, original-factor traceback equality, all29,790 final containments and fixed large-component assignment are checked in both normal and optimized runs. The implementation uses explicit checks rather than Python assert, so optimized mode retains them.

The later independent review must audit these domains, factors, arithmetic bounds and traceback before this packet is treated as independently verified. No phase, physical emitter, arbitrary-input native replay, compiler or kappa campaign is included. Any extension to other price objectives requires its own authorization; this fixed-C result alone is not an all-concave optimality theorem.

## Credit and open boundary

1337isnot1337 supplies #4994's sharp intervals and realization contract; Dugongue supplies #4971's weighted frame-carrying swaps; Cao Yifan and the native/helper lineage supply the underlying source. Astra supplies the published bucket-elimination fit and bounded source-specific proposal. Rina Dechter's 1999 min-sum bucket elimination theorem supplies the general recurrence. This packet implements and executes only the declared18-component restricted optimization. The large component and changed productive/native/caller mechanisms remain outside its result.
