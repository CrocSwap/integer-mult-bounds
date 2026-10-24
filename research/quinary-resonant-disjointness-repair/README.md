# Repeated-root disjointness repair in characteristic five

For every h=4k>=4 over every characteristic-five field, the actual proper-subset
disjointness repair has rank **2^h−1−b_h**, where b_h counts the Jordan blocks
in the explicit five-state recurrence in [PROOF.md](PROOF.md). This is also
its exact additive scalar rank-one correction count. First values are9 at
h4 and185 at h8.

The new mechanism is nonsemisimple: the source tensor factor has a repeated
root in characteristic five. Five fixed Jordan tensor identities yield the
all-h block multiplicities; a nonzero fourth-power endpoint witness proves
that deleting empty/full subsets lowers rank by exactly one. The written
induction and endpoint argument supply the quantifier. Finite h4/h8 ranks
are calibration, not extrapolation.

This follows the source matrix and attribution of Ali Romman's PR4962 and
Nick Petalas's distinct odd-characteristic-three PR5173. Their exact proof
bytes are live inputs pinned in SOURCES.json. The separately claimed even
characteristic-three scope in Discussion5194 is excluded. No binary invoice
is reused, and no physical quinary supplier, nonadditive repair, selected κ
change, human review or proof-kernel acceptance is claimed.

## Reproduction

```sh
python3.12 -B research/quinary-resonant-disjointness-repair/verify.py
python3.12 -B research/quinary-resonant-disjointness-repair/independent.py
python3.12 scripts/research_package.py --package research/quinary-resonant-disjointness-repair
```

Standard library, below one second for each direct check. The mandatory typed
RESULT records all five fixed tensor rules, source ranks, actual endpoint
witnesses and domain controls. The independent checker uses literal Kronecker
products, column-space reduction and a complete625-vector tiny kernel census.
No large predecessor replay is required.

## Open next questions

Nonresonant dimensions require their own endpoint analysis. A physical quinary
application requires an actual caller and paid preparation, movement, precision,
restoration and retained backing; none is supplied. TASK.json records these
separate obligations.

## Credit

Ali Romman PR4962; Nick Petalas PR5173; mikey1201 PR172; icekylinx/#144 and the
retained endpoint/compiler lineage. Classical Jordan theory and rank
factorization retain their attribution. Prepared by JoyboyBrian with substantial
OpenAI Codex assistance; Apache-2.0.
