# Stage-6 stock audit: containment lemma and missing call map

**Result:** the retained PR185 row proof gives zero *additional external row
reserve* at its completed high-part call. The child's internal borrowing is
not zero: it uses the two chunks already passed to it and restores the row
coordinate before returning. The parent and child ledgers overlap by
containment and sequential reuse; adding the child borrow again as fresh
external stock would double-count that range.

The selected native recurrence's sixth exponent matches its sixth algebraic
step, but the frozen PR1087 assembler does not bind that arithmetic stage to a
physical `A6 → A5` call map. Therefore the zero-increment lemma remains
conditional at the selected boundary; the actual selected-stage increment and
parent-stock coefficient remain unknown.

## Evidence

The selected record is bound at base `20ecf2891d80b5acf18f980b2164fb44ea7faa90`
and priority revision 6. The selected `ASSEMBLY.json` has seven native stages;
the frozen PR1087 assembler starts from `a0 = 384599/10^10` and applies the
same recurrence seven times. The verifier independently reconstructs all seven
exact exponents and confirms that entry 6 is the `a6` recurrence value. PR387
separately describes a six-level `A_j` construction, but its retained proof
does not bind the selected PR1087 stage to that physical call map.

## Reproduce

From the repository root:

```sh
python3 -B research/selected-stock-boundary-audit/verify.py
```

The verifier checks source hashes and the recurrence mapping. It does not
verify a physical selected `A6 → A5` call map. The conditional row-range proof
is in [PROOF.md](PROOF.md), not a formal proof-kernel result or cold producer
replay.

## Scope limits

- The parent stock remains `O(w log e)` in the retained proof; its numerical
  coefficient and selected width-domain binding remain open.
- The zero increment is proved only for the retained completed-call interface
  and only where its parent split `k < e/2` is valid. The selected cutoff is
  not shown here to imply that premise.
- The selected source does not bind stage 6 to a physical `A6 → A5` call map.
  Applying the conditional lemma there remains unresolved.
- The selected producer keeps its 252 allowance. This result neither treats
  that value as the internal reserve nor removes it from the bill.
- No supplier admission, new κ, selected-frontier change, or multiplication
  theorem is claimed.

## Open next questions

1. Does the selected stage-6 implementation actually instantiate the retained
   completed `A6 → A5` interface? This determines whether the zero-increment
   lemma applies to the selected stock ledger. First trace the selected
   producer's physical call map from the frozen PR1087 source and its pinned
   dependencies; the available assembler archive binds cutoffs and moment
   inputs but not this call map.

## Credit

The completed ordinary-call contract is retained from PR185/PR182. Rohan Arun's
PR387 source extends its fixed-depth composition to six levels. The selected
seven-stage assembly is Rohan Arun's PR1094 lineage; the frozen T16 source is
Jeremy Kothe's PR1087 work. This package adds the exact stage-6 recurrence
alignment and records the missing physical binding; it claims no predecessor
construction or result as new. Prepared by OpenAI Codex (GPT-6 Luna xhigh),
laptop-10, with AI assistance. Apache-2.0 follows the repository's license;
retained source attribution remains intact.
