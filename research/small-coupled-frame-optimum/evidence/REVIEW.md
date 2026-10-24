# Independent review: fixed-price optimum and separate cut-three witness

**PASS within the declared restricted geometric model.** At the exact parameter
`C=15108879/5000000000`, the 18 small components have the source paid histogram
in both orientations:

    {1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}.

The chosen minimizing assignments change four contact labels under the author's
deterministic tie rule. They have exactly the source histogram; the source
assignment is itself a minimizer. There is no paid saving in this restricted
product. This is not uniqueness of the source assignment.

The separately authorized integer objectives give source/minimum values
`3298/3298` at k=1, `4395/4395` at k=2, and `5080/5075` at k=3 in both
orientations. The k=3 witness is feasible and has histogram

    {1:2223, 2:421, 3:490, 4:132, 5:40, 8:8}.

Its source difference is `22H1+9H2−20H3+5H4`; its rank mass remains 5327.
The nine min-rank prefix differences are `[16,10,-5,0,0,0,0,0,0]`.
At the fixed power price it instead increases cost by the rigorously enclosed
interval

    [0.077586985710037469603912620755,
     0.077586985710037469603912620756].

Thus the cut-three result and fixed-price optimum are consistent. The cut witness
prevents the proposed source-optimality statement for every concave rank price.
Objectives k=4 through 8 were not executed. No common-minimizer premise, Pareto
enumeration or all-concave ceiling is used.

## Exact inputs and independence

The source is #4994 at `ef2810fe43829960789f783e44ee6484d0368f09`, carrying
#4971 at `0130b196145a43a7d305de41f49e56e8e8556378`. The eight frozen source
blobs are authenticated by `source/SOURCE-MANIFEST.json`; the retained source
word SHA256 is `7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`.
The authenticated retained constructor and frame-DAG implementation supply the
source graph. This review does not independently reimplement that graph or
replay native phase semantics.

The author's frozen fixed-price manifest is
`389138c4b5389d141090a9b66eba769ef0a70381b7803b248c90eef97399e72d`;
`optimize.py` is
`b1536a86967312bb8c9da7b177dacd54093bea71462bbbfeffdf7325260d96bc`.
The cut manifest is
`09844d8e7767cbc82dd576f7f74ac836fe3a0a9d0f73118171367fe8320ba4ee`;
`min_rank_cuts.py` is
`d2fb2a56426cc94c9c9149316c93e83536a316f04bbc033603a715e3ae3e82d2`.
All these files were copied unchanged and rechecked against the live author
directory after the audit. Their manifests remain in `frozen/`.

The independent `check.py` imports neither the author's domain generator,
factor builder, solver nor price comparator. It reconstructs the following
items and verifies the stored optimality certificates directly.

* It derives all variable components from the actual mapped edge list: one
  component with 1271 variables and 18 with 68 variables in total. It verifies
  the exact solved partition, keeps every other value at source, and checks
  every prescribed boundary.
* For every stored domain it checks actual binary subspace closure, uniqueness,
  interval containment, source inclusion and the full Gaussian-binomial
  cardinality. These together prove that no interval subspace was omitted.
  The 68 domains comprise 53 of size 2, 12 of size 5 and 3 of size 16.
* It builds factors from every original mapped multiedge incident to each small
  component, including parallel edges and fixed-neighbor unaries. It evaluates
  each map on every point of the candidate subspace and authenticates the exact
  factor inventory. No cross-component variable factor is discarded.
* For each objective and orientation it verifies every stored separator choice
  against every possible eliminated-variable value, constructs the resulting
  messages independently, reverses the traceback, and checks the assignment's
  cost against the original factors. Across fixed C and k=1,2,3 this verifies
  8760 bucket candidate evaluations; each objective/orientation has 1095.
* It reconstructs the full histogram, including eight owned H8 calls, and checks
  all 29790 mapped containments for every resulting assignment. It also checks
  the exact list of changed contacts and that the large component is unchanged.

The finite infeasibility penalty is 5328H1. All factor costs are nonnegative;
the feasible source component cost is at most the full source rank mass 5327
for these power and integer-cut weights. Therefore a true component minimizer
cannot contain an infeasible factor. The independent full-containment checks
also verify feasibility directly.

## Arithmetic and recurrence

The usual min-sum elimination recurrence is correct here: sum the factors
containing the eliminated variable, minimize over its complete finite domain
for each separator assignment, and retain an argmin. Reverse traceback recovers
a minimizing complete assignment. The independent check validates each finite
argmin inequality rather than accepting the author's printed objective value.

The author's rational logarithm/positive-exponential tail bounds and reciprocal
endpoint ordering were inspected and are valid for ranks 1 through 9 at the
declared C. Every actually used distinct-histogram comparison has a strictly
signed enclosure. Independently, the review uses the frozen interval functions
from `20bb93cd990d2ff683e4d0fc56b87a42cd5d3296`,
`research/higher-moment-strictification/verify.py`, SHA256
`0ce7e7137422d5ffeda22085c81fa88471bbe963100fdad62e659f1e3bf89326`.
Its 80-term logarithm bounds, 64-term scaled exponential bounds and outward
192-bit fixed-point rounding produce finer enclosures contained in every
author final weight interval. They independently verify all 119 strict signed
comparison certificates and all reconstructed fixed-price argmin inequalities.
Integer-cut comparisons are exact integer dot products, allowing genuine ties
between distinct histograms.

The completed capped run does not require an algebraic non-tie theorem or a
claim that all future comparisons terminate. An unresolved comparison would
stop the author solver; none occurred in the reviewed run.

## Replays and controls

Fresh author fixed-price and cut-driver normal/optimized replays were run to
private review outputs with an explicit `--source-root`, preserving all author
files. They match the frozen semantic receipts after removal of elapsed-time
metadata. Summary receipt hashes necessarily change when they bind that timing
metadata; comparison still checks every underlying semantic receipt. The cut
driver stops at k=3 in both modes. `REPLAY-CHECK.json` records these comparisons.

Independent normal and optimized runs produce byte-identical results:

    python3 -I -W error -B outputs/pr4994-small-frame-dp-independent-review/check.py
    python3 -I -O -W error -B outputs/pr4994-small-frame-dp-independent-review/check.py

The checker is read-only unless `--emit` explicitly regenerates its own
`REVIEW-RESULT.json`. All required source bytes are local. It uses only the
Python standard library and does not require Git or a network connection.

The independent controls delete a unary factor and an edge factor from the
inventory checked by the same validation routine, substitute a strictly
nonminimizing traceback choice in the same argmin validator, and corrupt a full
histogram. Each is rejected. An actual native-map-to-identity containment
counterexample is separately recorded. These controls test specific audit
guards, not a physical native implementation.

The author's original dropped-edge control only demonstrated a changed
histogram, and its identity-map control exhibited a violated source
containment; they were not full mutated-optimizer replays. The frozen
`CONTROL-CLARIFICATION.md` correctly states that limitation. This review does
not reinterpret the stronger-looking original JSON field names as stronger
tests.

## Scope and credit

This establishes a fixed-price zero-saving optimum on the declared 18-component
product with the 1271-variable component fixed at source, plus the distinct
cut-three non-generalization witness. It establishes no optimum on the large
component, intact zero-edge-region campaigns, the global contact model, changed
graphs, helpers, scalars, warps or callers. In particular, chart containment and
rank-difference costs here are the frozen #4994 geometric model; the review
does not emit new native phase-correct words or transfer them to the complete
#4610 compiler. There is no new kappa result.

Credit remains with 1337isnot1337 for #4994, Dugongue for #4971 and the native
frame work, Cao Yifan and predecessors for the underlying source, Astra for
the authenticated graph proposal and literature fit, and the parent/author
agents for the bounded implementation and authorization. This independent
review and its checker were produced with substantial OpenAI Codex assistance.
