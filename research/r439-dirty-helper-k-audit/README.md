# One dirty helper bit breaks the literal K mask in the pinned R439 star word

**Scoped counterexample. No new exponent or supplier claim.**

## Question and result

For the pinned PR967 helper-star word, does restoring the helper-star center at the end imply that each target's literal K mask names the full dirty helper contribution at the read?

No. On the pinned word, start with only helper register 260 set. The raw A/scatter/B map sends that bit to target register 112, while the literal D-source mask for target 112 omits helper 260. The exact coefficient is 1 in the raw map and 0 in K. The center helper 280 is restored by the end of D.

The word's first star edge is D gate 0, 280 ^= 260. D gate 528 writes target 112 from a source list containing 280 but not 260. D gate 1164 restores 280 ^= 260. On the dirty basis input e_260, an exact D replay has helper 280 equal to 1 at the read, toggles target 112, and returns helper 280 to 0 at D exit. Thus endpoint restoration does not justify treating the source label 280 as its unchanged boundary column during the intervening target read.

For target 112, the full literal K helper mask has 79 bits; the independently replayed raw A/scatter/B helper mask has 121 bits. Their helper-only symmetric difference has 66 bits. The single bit at helper 260 is a concrete counterexample. Helper 280 is a positive control: its coefficient appears in both masks.

The assigned orientation command also passed. Its receipt checks all 661 columns, both directions, equality of the candidate D boundary with the PR589 word, and the unchanged paid profile. This audit does not replace that full verifier; it identifies one exact K mismatch.

## Scope and limits

This is one finite witness in the pinned R439 word. It disproves the implication that restoring a helper endpoint alone preserves the inherited literal K mask. It does not establish a replacement H2/K contract, show that all helper-star words fail, or price a new construction. The paid profile and selected result are unchanged. No full frontier replay, supplier admission, new kappa, or formal proof-kernel review is claimed.

Open PR [#3533](https://github.com/CrocSwap/integer-mult-bounds/pull/3533) already gives the abstract three-gate mechanism and does not replay the 661-column candidate. This package supplies the exact selected-word target, helper IDs, gate positions, and dirty basis witness. It is a scoped complement to that work, not a claim to the abstract example.

## Reproduce

From the repository root:

    python3 -I -B research/r439-dirty-helper-k-audit/verify.py
    python3 scripts/research_package.py --package research/r439-dirty-helper-k-audit --check-only

The verifier uses only the Python standard library. Inputs and hashes are listed in [SOURCES.json](SOURCES.json).

## Open next questions

Does replacing each literal source label by its actual cut-time helper column produce the full correct K interface across all 111 targets, with a complete unchanged paid profile? A bounded first step is to compute the per-target symmetric differences and associate each extra bit with its star edge. That repair is outside this result and should proceed only if it changes the interface or complete invoice.

## Credit

The source is Sricharan Vagvala’s PR967 helper-star candidate, prepared with substantial OpenAI Codex assistance; the original package retains Gareth Davidson’s PR915/926, DreamingOfClouds’ PR589 and eumemic’s PR555/543 lineage. James Reed’s independent abstract three-gate illustration in open PR #3533 remains credited to him. This verifier is a finite audit of that pinned source word; no independent human review is claimed. Apache-2.0.
