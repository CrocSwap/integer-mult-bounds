# Dirty-workspace compression by pairing rank

A full formal rank-one word can retain just the dirty directions that feed
back into its calls. If U is its dirty column span and V its dirty row span,
let `t=rank(V x U -> F2)`. The word compresses from `h+k` roles to `h+t`,
preserving the active endpoint and restoring every retained arbitrary dirty
role. Every ordered contraction is preserved over any unital F2-algebra,
including noncommutative ones. Letter counts never increase.

The uniform [proof](PROOF.md) constructs binary maps F,G with `FG=I` and
`vGFu=vu`, then expands the ordered rank-one product. These maps describe a
new legal word; they are not additional physical operations. Idempotent factors
remain nonzero idempotents; nilpotent factors may become identity and be removed.
The exact pairing rank is minimal among replacements preserving the active
components and every contraction, not among all words for the same endpoint.

## Concrete consequence

For `diag([z],[uz],I_rest)` in the formal F2[UT4(F2)] adjacent-letter alphabet,
the inherited span inequalities give

```
roles needed <= 2 + floor((L - 13) / 2).
```

In particular, every possible 15- or 16-call word reduces to at most three
roles, uniformly over any original finite dirty workspace. This extends the
prior one-excess/common-orientation reduction.

At letter prices `(a,b,c)=(1,3,1)`, the direct word costs 26. Building on the
pinned [PR2314](https://github.com/CrocSwap/integer-mult-bounds/pull/2314)
weighted boundary, any cheaper word costs exactly 25 and has counts
`(6,5,4)`, `(5,5,5)` or `(4,5,6)`. The new lemma preserves those counts and
reduces existence to exactly three roles, with all b couplings supported on
the active two-role block. **Whether such a word exists remains open.**

This is a formal-model reduction and a concrete missing-workspace handoff.
No new native supplier, physical cost saving, weighted optimum or kappa is
claimed. Geometry, support restrictions, compilation, hosting, precision,
reserves and all-size transfer need their own arguments.

## Evidence and reproduction

```sh
python3.12 -B scripts/research_package.py --package research/register-pairing-compression
```

The registered commands use `-I -O -B`, standard library only. They check:

- Every ordered pair of binary subspaces of workspace dimensions 0 through 4:
  4,775 pairs, with an independent set-image pairing-rank oracle and complete
  noncommutative product comparison for each constructed word.
- All 2,401 ordered rank-one coupling pairs on three roles with one active role;
  384 expose the failure of naive active-corner projection.
- 29 complete dirty-endpoint fixtures on up to eight roles, including changed
  dirty bases, idempotents, nilpotents, and bidirectional orthogonal workspace.
  A separate literal group-action checker evaluates all 18,176 basis columns.
- All 4,096 literal UT4 group products, fourteen semantic controls,
  the integer span budgets and exact cost-25 count splits.
- Four actual source/proof/receipt corruption controls and a Git-free relocated
  preflight. Occupied output paths are rejected.

[RESULT.json](RESULT.json) records exact coverage and transcript digests. The
finite checks corroborate the new construction; [PROOF.md](PROOF.md) establishes
the general quantifiers. The PR2175/2314 quotient homomorphism and exclusion
censuses are credited inherited premises and are **not rerun here**. Their exact
proofs are archived unchanged, with author, public head, Git blob and SHA256
bindings in [SOURCES.json](SOURCES.json). Three main-branch proof inputs are
also pinned and declared to the replay planner. Historical catalogue and
selected-result pins are provenance, not new results.

Direct replay from a Git-free export requires this package plus the three
`usage=input` paths in SOURCES.json. It reads its inputs and uses temporary
copies for corruption controls. To regenerate a receipt for review, use
`verify.py --write-result /an/unoccupied/path.json`; normal verification never
rewrites RESULT.json.

## Open next questions

Decide the three 15-call count splits on three roles, keeping all b couplings
inside the active block. A complete necessary-quotient exclusion would settle
the formal price at 26; any survivor needs the full group-algebra endpoint.
Start by deriving a complete normal form or coverage certificate for the single
dirty direction. No three-role census or witness is provided here.

A separate application could replace the whole image-span bound in a different
rank-one alphabet, provided that alphabet is closed under the constructed
couplings. The first step is an explicit closure check; native or geometric
restrictions cannot be assumed preserved. Structured questions and the changed
card scope are in [TASK.json](TASK.json).

## Attribution and scope change

Credit CinnaDavis / 1337isnot1337 PR1541 for image-span restriction; ToikY
PR1662/1680 for UT4 spans and common-orientation compression; Nick Petalas /
petalas PR2175 for the mixed-middle inequality; Gareth Davidson PR2027/2314 for
the mixed tariff and weighted boundary; Aaron Wang / navinor PR1690 for the
inherited census method and its predecessor lineage. This package adds the
pairing reduction, not those bounds or the direct word. No literature-priority
claim is made for the underlying linear algebra.

The single OS draw selected `bit-new-register-model`. Scope is explicitly
changed to the missing workspace implication in this nonabelian formal model;
it does not meet the card's native-construction gate. The baseline and the
specified predecessor boundaries were checked first. Coordination is the
[scoped follow-up in Discussion2019](https://github.com/CrocSwap/integer-mult-bounds/discussions/2019#discussioncomment-18941076).

Prepared by Gareth Davidson / @bitplane with substantial OpenAI Codex assistance.
No subagents, independent human review or proof-kernel check. Apache-2.0.
