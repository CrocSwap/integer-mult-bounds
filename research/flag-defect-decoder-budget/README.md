# Exact flag-defect decoder budget

A fitting matrix with unequal payloads and prescribed one-dimensional flag
levels has the exact compatible minimum B=sum_t mu(Z[I_t]). Gaps in each
port's levels are allowed. For an arbitrary fitting matrix M, let E retain
only entries that move to a higher flag level. Then **rank M+rank E>=B**.
A query saving of s therefore needs at least s defect rank.

The [proof](PROOF.md) shows that this bound is sharp for every positive s,
over every field. For s copies of the classical width-two odd-cycle edge
code, the minimum defect rank over ALL local complete flags and adapted
bases is exactly s. The code and its rank advantage are credited prior
work; the new result is their exact defect budget, together with the
unequal/gapped interface and the complete linear operation word.

The literal implementation preserves sources, updates arbitrary dirty
outputs, and restores one reused scratch field. It pays six ADDs per
edge-copy with initially clean scratch, or eight with arbitrary dirty
scratch. The integer prefix range is at most 3H, and this is sharp. A
four-ADD direct-source implementation exists too. This package therefore
claims no scalar-operation or physical speedup from the query-rank gain.

## Evidence and replay

```sh
python3.12 -B scripts/research_package.py --package research/flag-defect-decoder-budget
```

Standalone: `python3.12 -I -Werror -B verify.py` in this directory, and
again with `-O`. The [receipt](RESULT.json) is recomputed. The verifier
uses only the standard library and retained files. No Git or network is
needed. It covers all 180,625 binary fitting matrices for the unequal
(1,2,2) payload, independent image ranks, gapped profiles over F2/F3/F5,
all 7,776 local GL2 basis tuples for C5, larger sharp cases and complete
clean/dirty literal words. Failure controls include an actual retained
source corruption and omitted ADDs. Exact counts are in the receipt.

Canonical base: main 7c49fe32c55de02c2c873655c804b16e4c3fef0a,
priority 8, selected 6030. The selected binding example passed. The
02:55Z overlap cache covered 476 open PRs and 6,464 Discussion records.
Live handoffs and PRs were also checked. No competing quantitative defect
scope was found. Sparse history, nested diffs and unpublished work remain
coverage limits. The theorem is written; finite checks corroborate it.

## Open next questions

Bind the inequality to an actual decoder with a full native and physical
invoice. The first test must include its input access, flags, payload
volume, monomial maps, dirty restoration and complete caller costs.
A separate useful question is efficient defect minimization in a specific
source family; the exact odd-cycle family is a calibration input.

No native supplier, actual profitable caller, kappa gain or selected-frontier
change is claimed. Precision, stock, tape, compiler, outer admission and
all five selected assumptions remain. Independent human and proof-kernel
review are unclaimed. Lean, Docker and the selected cold replay were not run.

## Credit

Ali Romman with substantial OpenAI Codex assistance; no subagents.
Nick Petalas / PR6471 supplies the equal-width flag theorem. Credit
also ywz65 / PR2541, Aaron Wang / navinor / PR825, Cinna Davis, Bukh,
Cox, Blasiak and the retained geometry/native/compiler lineage. The
source proof is retained byte for byte. The odd-cycle representation,
scalar minrank facts and elementary rank inequalities are classical.
No global literature-priority claim is made. New work is Apache-2.0.
