# Working glossary for a first research session

These are orientation descriptions. The selected supplier's exact definitions
and contracts govern a proof; historical packages may use different conventions.
For the latest checkpointed review and remaining obligations, see the [current
reviewed status](current-status.md); the live candidate and priority queue are
in [current priorities](current-priorities.md).

| Term | Meaning here |
|---|---|
| κ (kappa) | The exponent saving in `n (log n)^(1-κ)`. Larger is better; it is not a runtime benchmark. |
| Supplier / primitive | A finite construction and its implementation contract supplying one recursive operation to the outer algorithm. |
| Bit and complex sides | Distinct primitive families. Improving one need not improve the final bound if the other is limiting. |
| `a` / primitive saving | A supplier's recursive exponent saving before the outer conversion to κ. |
| Word / scalar program | The chronological list of local linear operations. Its addition count is only one part of the total cost. |
| Role / register / helper | A logical data or workspace position. A helper may hold arbitrary initial data; it is not automatically zero or disposable. |
| Dirty state / restoration | A routine must work for arbitrary initial workspace and return the state required by its caller's contract. |
| Frame / label | The representation attached to a role or operation. Changing frames can require paid recursive work. |
| Controller | A program combining native invocations into independent target jobs. Owner, helper, routing and error contracts determine which [two-FULL result](two-full-controller-contract-map.md) applies; inverse recipes and a favorable invoice alone do not establish a complete caller. |
| Decoder / copy cost | In the complex E8 algebraic model, a sum of support-pair terms realizing the required Gram identity; each term is charged its binary label-pairing rank. Term count, all-pairs versus masked exactness and retained readers change which [decoder bound](complex-decoder-scope-map.md) applies. A decoder alone does not supply a physical COPY program. |
| Rank / paid profile / histogram | The size of each recursive child and the count at each size, derived from the actual frame transitions and other charged calls. |
| Moment / invoice | The normalized recursive cost at a proposed saving, including the applicable extra charges. It must satisfy strict inequalities. |
| Owner / bank | A physical allocation used to host logical helper families. Compatibility, capacity and timing must be established; reuse is not free by declaration. |
| Hosting | Realizing logical calls and frames on actual data/streams with the promised layout and access costs. |
| H1–H5 | Named hypotheses of the selected bit scalar-interface lemma, covering gate directions, frames, ordering and cleanup. They are not five universal laws for all networks. See the [checker’s interface description](../../research/e8-bit-p111-tuned/code/xcheck_p.py). |
| H2/K gap | A failure of the original D-stage gate restriction or literal D/K comparison. Fixed R439 words already have a [semantic replacement and finite hosted follow-up](../../research/r439-semantic-d-navigation/README.md); a different word still needs the full boundary and continuation contract. The original syntactic flags can remain false. |
| All-size / uniform | Correctness for the algorithm's whole permitted parameter range, rather than only the finite address sizes tested. |
| Cold replay | Reconstruct and check the relevant construction from its pinned inputs, under its declared environment and coverage. |
| Scoped obstruction | An exclusion with explicit hypotheses. Changing a hypothesis may escape it; increasing search size inside an excluded class does not. |

Use [the bottleneck brief](bottleneck-brief.md) to connect these terms to a first
experiment, and the selected record for the precise active sources.
