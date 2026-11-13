# Direct canonical Beneš bits for padded modular rotations

One switch bit of the canonical network for `x -> (x+a) mod s` on
`x<s<=2^h`, fixing the padded addresses, can be computed in `O(h^2)` bit
operations and `O(h)` working bits. No permutation, component graph or
whole row ROM is constructed by the new evaluator.

This is a scoped written proof and arithmetic construction, with finite
exact corroboration. It computes precisely Cinna Davis's #4100 canonical
tables, including the deterministic component orientations. No new kappa,
physical tape tariff or supplier admission is claimed.

## Result

For `h>1`, the first row is zero except for the pair `{s-1,s}` when both
`s` and `a` are odd. The last row has the following one-bit predicate at
the current wire address `x`.

| Parameters | Last-row bit |
| --- | --- |
| s even | `[a odd] [x<s]` |
| s odd, a even | `[x<a]` |
| s odd, a odd | `[a-1<=x<=s]` |

For child branch `c` in `{0,1}`, the canonical child is itself a padded
rotation with

```
s_c = floor(s/2) + [s odd and c=(a mod 2)]
a_c = (floor(a/2) + c(a mod 2)) mod s_c.
```

An empty child is identity. The only possible reduction is equality with
`s_c`, which is replaced by zero. An interior point query follows branch
`x mod 2`, halves `x`, and reduces both height and row index by one. The
base row at height one has constant bit `a`. Thus at most `h` iterations
suffice. [PROOF.md](PROOF.md) proves the formulas by identifying the
source's colored matching components and its exact child permutations.

At the handoff's `h=5,s=17,j=6` geometry this supplies any of the 544
offset/address bits without constructing that whole ROM. It does not yet
provide a literal physical predicate-return service.

## Evidence and scope

The verifier checks all 713 networks with `1<=h<=5`, every modulus
`1<=s<=2^h` and every offset `0<=a<s`. All 168,862 directly computed switch
entries equal the pinned canonical definition. It extracts and checks 710
root decompositions, and independently checks 19,406 routed endpoints
using the new point queries. Twelve invalid-domain cases and six semantic
controls pass. Twenty large-width queries, including full-depth paths
through `h=4096`, need no exponentially sized reference network.

The finite counts describe the new evaluator's checks. The generic source
compiler is an oracle, not a predecessor scientific result audited here.
The universal claim rests on the written proof, not extrapolation.
`--receipt` writes a generated report bound to all seven package-file
SHA256 hashes and the live canonical source hash. No receipt is hand-written.

The public implementation caps `h` at 4096 to bound managed-runtime
allocation. The recurrence and proof have no such mathematical cap.
PROOF.md records the bounded Python-allocation and immutable-oracle
recursion/loader deviations from Power of Ten. The production evaluator
itself is iterative and uses no imported scientific implementation.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/canonical-rotation-switch-query/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/canonical-rotation-switch-query/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/canonical-rotation-switch-query
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/canonical-rotation-switch-query --check-source-history
```

Another CPython 3.12 executable may replace the local path. Direct verification
ends with `PASS_CANONICAL_ROTATION_SWITCH_QUERY`. Add
`--receipt /absolute/path/outside/checkout.json` to produce the hash-bound
report. Each registered command is bounded to 120 seconds. All generated
output belongs outside the checkout.

## Provenance and overlap

Scientific base is canonical main
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8. The
`uniform-transfer-audit` card explicitly changes scope to this original
construction. JoyboyBrian's [Discussion #4709 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/4709)
identifies the whole-ROM versus one-predicate bottleneck. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19591481)
states the exact source-compatible question.

[SOURCES.json](SOURCES.json) pins the canonical definition and its unchanged
notice as live inputs, and the catalogue, selected record and predecessor
context as provenance.
Live PR/Discussion checks, merged-PR searches and main-tree README searches
found no same-scope result within that coverage. The cached overlap helper
had incomplete sparse local coverage and older remote coverage; it was
supplemented by live reads and main-tree searches. This is not a guarantee
against unpublished or differently worded work.

Nick Petalas's #4876 prices optimal active swaps for full dyadic cycles.
Its tariff construction and proof are not used here. This result concerns
pointwise evaluation of a fixed deterministic compiler for arbitrary padded
moduli. It does not settle optimal padded-cycle swap counts.

## Open next questions

1. Lower the point evaluator to a literal fixed tape program returning one
   caller-owned predicate. Begin with encoded `h,s,a,j,x` and the `h=5,s=17,
   j=6` boundary. Charge comparisons, scans, initialization, erasure and all
   head returns. The arithmetic proof does not supply that physical bill.
2. Join it to the exceptional key's current-state CRT offset producer.
   Begin with the complete `(0,1,4)` key and stale-second-offset control from
   Discussion #4709. Descriptor conversion, borrowed-state restoration and
   uninterrupted ownership remain obligations. A supplied offset is not
   free CRT reconstruction.

Structured first steps and blockers are in [TASK.json](TASK.json).

## Credit

This contribution was produced by Nick Petalas. Cinna Davis /
1337isnot1337 supplies the deterministic Beneš compiler and padded rotation
in #4100. ToikY's #4192 supplies the generic arena lowering; JoyboyBrian's
#5092 and #5496 supply the encoded producer and current-row query context.
Their results and retained predecessor lineage are cited premises. The
source-specific [notice](../unconditional-batched-crt/NOTICE.md) is unchanged.
Parity coloring and binary integer arithmetic are standard ingredients;
the formulas, padded-rotation closure and direct canonical evaluator are
the result contributed here. Independent human and formal proof-kernel
review are unclaimed. Apache-2.0.
