# Asynchronous whole-owner replica scheduling

## Sufficient construction

Start with any admitted complete-invocation supplier with the following literal properties. Each invocation is an arbitrary-dirt-valid shear on its two active data banks; each helper belongs to a distinct full physical family, distinct from every active data family; its paid entry/exit wrappers restore all borrowed spectator coordinates and leave exactly its prescribed residual transform on its assigned pending coordinate block. The retained PR484/496 complex supplier provides these properties. No split residual or interleaved incomplete invocation is used here.

Take T independent copies of the complete nine-stage controller. Their data banks are disjoint. A schedule is any shuffle of the T per-replica controller event lists that preserves each list's order and keeps every complete cover invocation indivisible. A pending idle child of replica r becomes available after its previous data/bridge touch and must be completed before its own next touch. A helper may use a disjoint block of that child whenever its complete invocation falls in this actual open interval. It does not matter whether the helper invocation and owner replica currently have the same stage number.

The correctness proof is induction over the shuffled event list. At a local invocation its active data action is exactly the retained shear. Arbitrary dirty state in each borrowed family is allowed by the full local theorem. Its only persistent helper action is the specified residual transform on a previously unconsumed pending block; borrowed spectators are restored. These residual blocks are disjoint within each idle child, so their product with the paid leftover transform is exactly the retained full idle transform. Complete that product by the child's deadline. At a bridge or terminal event, its own replica is therefore in exactly its retained controller state. Different replicas have disjoint active data banks. After every replica completes, apply the retained full-stock correction. Thus the resulting global operator is unchanged.

This is a sufficient finite scheduling theorem under the SAME retained complete-invocation/compiler/analytic contracts. It is not an unconditional integer-multiplication theorem, a split-owner lift, or permission to commute scalar gates through unfinished invocations. The new scheduler requires a fresh global prefix bound because intermediate dirty states may pass between replicas.

## Constructive packing and exact ownership

ASYNC-3.json freezes the order sorted by (stage + 3*replica/7, stage, replica). It also freezes an integer pattern nomination for each (owner replica, pending child):120 actual port families, each with a list of consecutive residual block widths. The local widths remain {5:4,7:14,8:104,9:438}. There are 72 calls and 40320 helper occurrences.

The initial aggregate time assignment is only a nomination. It is replaced by a joint integer flow assigning each pattern's width slots to legal call times. For a pattern used on n families, at most n slots may be assigned to one time. For each pattern, form a bipartite multigraph between call times and its width-slot positions. Each slot position has degree n and each call time has degree at most n. Pad with dummy vertices and edges to an n-regular bipartite graph, then remove n perfect matchings. Each matching is one physical port family: it receives exactly the selected width pattern and at most one helper at any call time. This produces literal family, port, child, offset, width and call records. Existing arbitrary dirty helpers can then be assigned by matching width.

The actual ASYNC-OWNERS.json.gz passes all 40320 occurrences, all 72 calls,560 distinct helper families per call, and no active-data overlap. This is an exact finite witness; floating MILP pricing is not its correctness evidence. The replay consumes the frozen witness and needs no optimizer.

## Changed paid profile

Ambient73, live7680, deficit 2496, physical8258 remain. The exact integer paid profile is:

    1:148240, 2:66816, 3:7032, 4:19728, 5:26109,
    6:144, 7:2209, 8:1224, 16:1, 48:408.

Its exact admitted moment lower bound, including the inherited bad-cover allowance, is0.001359547617819233570818. The exact composed kappa is0.001357701757628940. Independent literal chronology, chart, scalar/prefix invoice and 47-inequality checks pass. The maximum child increases to48, but73^2=5329>2*48^2=4608, so depth2 remains sufficient.

## Research provenance and scope

PR496 supplies whole-owner pooling, exact normalization and the original matching-based owner construction. PR484 supplies the gauge/kernel local word; PR493 supplies the nonbinding stronger bit side. The new contribution is removing replica lockstep while retaining complete invocation boundaries and owner-relative pending windows. Generic bipartite matching is inherited mathematics, not a claimed new theorem.

The downloaded OpenAI common-integer-polymatroid work (problem114), especially the tight-set augmentation/base calculus in its preprint, motivated looking for exchanges of capacity across previously fixed stage partitions. The actual finite feasible family is not asserted to be a matroid or M-convex set; no FPRAS theorem is imported as a packing certificate. The sufficient construction above is direct and the final ownership witness is exact.

## Other bounded screens preserved

Uniform stage counts K3,K6,K7, stage-selective local kernel component portfolios, optional paid whole banks, and the siblings' joint gauge/kernel variants did not beat PR496 under the tested lockstep packing. The component words remain valid local constructions but are not kappa gains. Their failures are restricted screens, not universal impossibility theorems. No Lean certification or publication was performed.

## Finite prefix and explicit retained conditions

The completed invocation/bridge L2 argument gives 20+37+72+72+4=205bits; charge512bits. The two-level row coefficient includes another2*512 and is16467<20161. The new schedule is sufficient under the unchanged PR493 bit supplier and PR484/496 all-size compiler, mutable-basis/common-label, Lemma A realization, restored-row, precision/tape and analytic-transfer contracts. This is not a proof of those inherited contracts.
