# A coherent native inverse and the two-full border's paid precision cost

The eight owned-center macros in each orientation of the actual round-three
native word have a
same-cost inverse: recompute the **same** deterministic center operation on
its unchanged source, subtract its fanout, then clear the owned field. No
additional Gaussian call is needed. This supplies one missing inverse-interface
construction for the [two-full Laurent border](https://github.com/Lyy-iiis/integer-mult-bounds/tree/e0bebf54d8cf8549ead24aef929fc40e44313bc0/research/two-full-laurent-border).

A complementary source-level census shows why independently bounding every
child's error is too expensive. The result is a constructive partial interface
and a rejection of a specified precision policy. **It is not a new kappa or an
admission of the border's formal crossing C = 0.0048568755777092.** The selected
result is unchanged.

## What is established

| Result | Exact scope |
|---|---|
| [Native inverse construction](inverse-interface/PROOF.md) | All 16 center macros across both orientations, actual capture/fanout roles, a typed inverse recipe for each complete 632-role word, unchanged paid inventory |
| [Paid-site sensitivity](paid-sensitivity/PROOF.md) | All 6,596 actual paid sites across two calls; 5,639 sites have explicit independent relative-error poles proportional to 1/epsilon |
| Main-output witnesses | After disjoint-axis splitting, 3,608 rank-one jobs have poles visible in main outputs even when all original helpers are zero; rescaling helper boundaries cannot remove them |
| Conditional price rejection | If each such site is charged twice the leading precision, the paid rank mass is already at least 14,262 versus target mass 10,750; strict rank separation rejects every moment exponent t in [0,1] |

The first result improves on literal reversal of an owned erasure. For a macro
`y_j += a_j A(x)`, the source x is unchanged. Its inverse uses the same A(x)
and subtracts the same increments. The backward gather macros similarly
recompute their unchanged linear combination of sources. A need not be
invertible or linear. The
complete native inverse additionally requires every ordinary persistent child
to have the inverse of its **same actual realization**, at the stated rank
charge, with clean private workspace. The construction does not supply those
child interfaces for free.

The precision result assumes robustness to independently chosen relative
operator errors at each paid site. It proves a necessary accuracy request,
not a universal computational lower bound. Turning extra accuracy into extra
cost requires the explicitly stated linear precision tariff. Adaptive,
correlated or different implementations are outside that rejection.

## Source, bill and evidence

The actual source is Cao Yifan's round-three word in the PR4610 lineage:
`research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`, Git blob
`46d929df83817b85a5387bcdb9745e0627d6366e`. The same blob is present at the
earlier border citation `0ce1b5c9fb7163d0b2f0ac3db95fc418dbbcec62`, the retained
source `1eb8da6cfb35512c0cc2533413e5ca42f48e13c6`, and this contribution's
main-branch base `cef4b52f2a59009865bf8eabde1be3f159063703`.

Each full call retains the paid profile `{1:2201,2:412,3:510,4:127,5:40,8:8}`
and all 408 independent helpers. The two-full split invoice remains

```
targets = {4:56,7:14,8:94,9:652,17:224}
paid    = {1:4656,2:920,3:1386}.
```

Owned buffers earn no productive credit. The inverse construction adds no
recursive paid calls under its declared child contract; scalar, routing,
range and precision obligations remain explicit.

The standard-library replay checks the exact source, rational sensitivities,
the conditional integer tariff, both complete inverse recipes, eight full-word
round trips on 632-role inputs, and fourteen primary rejecting controls. Round trips use
independent perturbed paid operators and nonlinear deterministic centers; they
test inverse closure, not the intended Gaussian endpoint. The accompanying
proofs state the general claims beyond these finite fixtures.

[Independent agent review](independent-review/REVIEW.md) supplies a separate
exact recount of all 6,596 site coefficients, 36 direct rational fault
trajectories and an audit of the inherited warp semantics. This is independent
AI implementation/review, not human review or formal-kernel verification.

The registered replay also runs the separate moving-frame checker and
[inverse checker](inverse-interface/INDEPENDENT-REVIEW.md): 96 local and eight
whole-word round trips with five further rejection controls. The NumPy recount
remains an optional independent replay.

## Reproduction

Python 3.12 and its standard library suffice for the registered checks:

```sh
python3 -I -B -O research/two-full-border-paid-precision/verify.py
python3 scripts/research_package.py --package research/two-full-border-paid-precision
```

Default verification compares frozen scientific payloads and does not rewrite
them. Gzip container bytes are not used to compare regenerated recipes or
receipts. The root source manifest declares the live source word. The optional
independent recount has its own recorded environment and invocation.

## Open next questions

1. Bind the coherent inverse to an actual paired recursive caller. Inverting
   a full native word also reverses its productive D factor; it does not
   automatically produce the required second fresh-D opposite shear. First
   prove both complete main/helper endpoints with their actual adapters.
2. Prove compatibility of approximate paid operations with the native frame
   identities. Consistent frame potentials and their free-warp intertwining
   would be a concrete sufficient structure; independent inverse pairs alone
   do not establish it.
3. Charge fixed-point arithmetic, private workspace and all scalar operations
   at that caller. Recomputing identical rounded increments can be reversible;
   rounding accumulators, changing precision or allowing overflow can break
   it. Nonlinear rounded bijectivity also does not imply the linear identities
   used by the Laurent controller. BIT admission remains separate.

These are construction tasks, not claims that the formal invoice is attainable.
[TASK.json](TASK.json) records first steps and blockers. The canonical
[Discussion continuation](https://github.com/CrocSwap/integer-mult-bounds/discussions/4611#discussioncomment-19129674)
and [overlap snapshot](OVERLAP.json) retain the coordination scope.

Credit Dillon/#4623 for the border/recovery question; Cao Yifan/#4610 for the
actual source and profile; Jacob Alan Sussman for mixed-target compilation;
Cinna Davis, DaysSky, Dugongue, zxv and the retained native/Clifford, owner and
precision lineage. New construction and checks prepared by Yiyang (@Lyy-iiis)
with substantial OpenAI Codex and parallel-agent assistance. Apache-2.0.
