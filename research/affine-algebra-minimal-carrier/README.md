# Smallest faithful carriers for affine group algebras

This result was produced by Nick Petalas. New material is Apache-2.0.
Claim type: scoped written proof with exact finite corroboration. No new kappa.

For every finite field F_q of characteristic p, every subgroup H of F_q*
of order h, and every coefficient field K of characteristic different from p,
the smallest faithful linear carrier of K[F_q semidirect H] has dimension

    q+h-1.

The sum-zero part of the natural permutation module, of dimension q-1,
together with the regular H quotient, of dimension h, attains the bound.
This replaces the regular group carrier's qh coordinates. It works even
when char K divides h. [PROOF.md](PROOF.md) gives the explicit coefficient
inverse and matching dimension lower bound. These are algebraic verifier
sizes, not native operation costs or physical memory measurements.

| Address field | h | Regular dimension | Smallest faithful linear dimension |
| --- | ---: | ---: | ---: |
| F3 | 2 | 6 | 4 |
| F4 | 3 | 12 | 6 |
| F7 | 3 | 21 | 9 |
| F7 | 6 | 42 | 12 |
| F9 | 8 | 72 | 16 |

The natural q-point action has an exactly (h-1)-dimensional algebra kernel,
spanned by differences of complete translation coset sums. Its faithfulness
on group elements does not make it a formal-identity checker. Ali Romman's
#5394 already supplies an explicit warning and alias; that warning is
credited background. The new result is the complete kernel, explicit
repaired carrier and exact optimal linear dimension.

## Construction and evidence

Write an algebra element as sum c_(a,b)[(a,b)] for a in H, b in F_q,
acting by x -> ax+b. Let M be its natural matrix, s_a=sum_b c_(a,b), and
C=sum_a s_a. Its coefficients satisfy the line-sum inverse

    c_(a,b) = (sum_x M_(ax+b,x) - C + s_a)/q.

The quotient regular block supplies s_a. The augmentation block and C
reconstruct M after removing its redundant constant direction. Only q is
inverted. The lower bound uses a central translation-average idempotent,
the degree-h minimal polynomial needed for a faithful cyclic H algebra,
and the q-1 nontrivial translation-character idempotents. These ingredients
are classical; no literature-priority claim is made for them.

The checker builds every multiplicative subgroup of F2,F3,F4,F5,F7,F8,F9.
It checks all integer carrier products and, over coefficient fields
F2,F3,F5,F7 of different characteristic, independently eliminates the
flattened matrix banks to measure their exact span ranks. Every formal
basis vector and twelve mixed vectors per context are recovered. A separate
rational calculation checks the line inverse directly on natural matrices.
No predecessor scientific verifier is imported or replayed.

The result is zero errors in 54 coefficient contexts, 13,269 group-product
pairs, 1,808 field triples, 1,683 recovered coefficient vectors, 1,380 rational
coefficient recoveries, and 96 natural-kernel basis vectors. Nine controls
cover malformed images, invalid domains and the excluded characteristic.
The latter F3/S3 construction has algebra rank three over F3 instead of six;
this is only a boundary fixture. The span-rank checks also reject omitting
quotient information. The all-parameter claims rest on the written proof.

## Reproduce

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/affine-algebra-minimal-carrier
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/affine-algebra-minimal-carrier/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/affine-algebra-minimal-carrier/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/affine-algebra-minimal-carrier --check-source-history
```

Other machines may substitute their CPython 3.12 path. Direct runs print
`PASS_AFFINE_ALGEBRA_MINIMAL_CARRIER`; the generic runner adds
`PASS_REGISTERED_RESEARCH_PACKAGE`. JSON output includes counts, per-context
ranks and SHA256 hashes of every package file. Default replay writes nothing.
To save a generated receipt, add `--receipt /absolute/external/scratch/receipt.json`;
an existing destination or a destination inside the checkout is rejected.

No timing speedup is claimed. Both registered runs have a 120-second bound.
The standard-library code uses fixed fields with q<=9, at most 72 group
elements, 16 carrier coordinates and 256 flattened matrix entries. It uses
no recursion, subprocesses, dynamic code generation or external scientific
input. Functions stay below 60 lines. Managed Python allocations are a
Power of Ten rule-3 deviation bounded by these domains. Warning-strict
normal and optimized replay provide interpreter diagnostics; no shared
analyzer configuration is changed.

## Scope, provenance and overlap

The `bit-new-register-model` card changes scope to a side result about exact
finite formal-identity checking, rather than a new paid word. A formal affine
matrix identity can be checked entrywise on this smaller carrier; the result
does not construct a bit supplier. The baseline binding command passes on
canonical main e54523517d0f03e58352e647c403a5af3e525a57. Its selected record is
#7000; the revision-8 catalogue describes the older #5599 assessment. No
selected file changes. [TASK.json](TASK.json) preserves the original card.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19592134)
records the question before the proof checks. Live open/account PR lists,
handoffs, local reservations, all-main README searches for the quantity and
general group family, and merged-PR searches were checked. The overlap
helper's remote snapshot covers 810 open PRs and 7,424 Discussion records
with reported complete pagination; its local note search is sparse and
incomplete. This is bounded overlap evidence, not a novelty certificate or
an unpublished-work search.

## Open next questions

- Determine a smallest permutation carrier under an explicit admissible
  action class. Start with the natural q-point orbit and an H quotient orbit;
  the linear optimum here need not be a permutation representation.
- Determine the smallest faithful carrier in the excluded address
  characteristic p. Start with the F3/S3 fixture and account for the complete
  group-algebra radical; the averaging inverse and proof here do not apply.
- Bind one actual formal-word checker to this carrier, including its coefficient
  field and every basis column, then measure its complete costs. Algebraic
  dimension reduction alone establishes no runtime speedup.

## Credit and limitations

Credit Ali Romman #5394 for the formal/natural distinction and order-21 alias,
retaining Cinna Davis #2011's order-21 model, the Q8 comparison and
JoyboyBrian's formal support lineage. They are cited background rather than
replay targets. Translation averaging, finite-field character orthogonality,
cyclic group algebras and Cayley-Hamilton are classical. No predecessor
package supplies the main construction or coefficient inverse used here.

The optimum permits arbitrary linear matrices. It does not price their
realization as permutations, recursive native operations or physical tapes.
Precision, source preparation, routing, ownership, dirty restoration,
compiler closure, complete invoices, outer use and all five selected
assumptions remain. No selected scientific replay, Lean, Docker, native
execution or complete multiplication theorem is claimed. Independent human
and formal proof-kernel review are unclaimed.
