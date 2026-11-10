# Rigidity and exact counts for saturated cubic pairs

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. No new kappa.

Over any characteristic-two field, every ordered pair

    A+B=D,   A^3=B^3=0,   D^2=D,   dim V=3s,   rank D=2s

has the same simultaneous similarity class: s copies of one
three-dimensional core. The joint centralizer is the diagonal copy of
M_s(F). For each fixed D over F_q, the exact number of ordered pairs is

    |GL_(2s)(F_q)| = product_(j=0..2s-1) (q^(2s)-q^j).

In dimension six over F2 the answer is 20,160. The [proof](PROOF.md)
answers the saturated portion of CubeJerry's
[PR #6768](https://github.com/CrocSwap/integer-mult-bounds/pull/6768),
Open next question 2, on equality cases of its sharp capped spectrum.
Its extremal value and attaining family are cited, not audited or replayed.
The new observation-coordinate proof and count are self-contained.

## Evidence and reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/saturated-cubic-pair-rigidity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/saturated-cubic-pair-rigidity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/saturated-cubic-pair-rigidity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/saturated-cubic-pair-rigidity --check-source-history
```

On another machine, replace the interpreter path with its CPython 3.12 path.
Expected markers are `PASS_SATURATED_CUBIC_PAIR_RIGIDITY` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. The direct verifier prints a generated
JSON receipt bound to all six package-file hashes and writes no files.

The declared finite checks cover:

- All 512 binary and 262,144 four-element-field matrices A in dimension
  three, with B determined by the fixed endpoint. Exactly six and 180
  pairs satisfy the hypotheses. Each passes the actual observation
  conjugacy check.
- Every binary 4 by 4 matrix, retaining all 20,160 invertible ones to
  enumerate distinct six-dimensional fixed-endpoint pairs. Each pair
  passes both cubic equations and the observation normal form. This is
  an orbit enumeration, not an ambient 2^36 matrix census. Completeness
  in dimension six follows from the written classification.
- All 276 declared block forms, including noncommuting 2 by 2 binary
  free blocks, checking the ordered first-row identity and cubic rigidity.
- Four joint-commutant linear systems, twelve larger conjugates through
  dimension 24, and six rejecting controls for the endpoint, each cubic
  hypothesis, dimension, singularity and field domain.

Normal and optimized runs retain explicit checks. F4 is represented as
F2[a]/(a^2+a+1). The standalone verifier requires no Git, network or
third-party dependency. [VERIFY.json](VERIFY.json) registers both modes.

## Sources and scope

[SOURCES.json](SOURCES.json) pins canonical base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, the original catalogue and
selected record. Its separate external-predecessor record identifies the
exact #6768 head and read proof/question bytes. These are citations, not
runtime inputs; no foreign commit is needed to replay this package.

The `bit-helper-contract` card is explicitly changed to an algebraic side
result. It restricts extremal shared-block models; it does not implement
a changed G20 path or price a complete supplier. The selected JSON gives
conditional kappa 0.003125804 and five retained assumptions. Older
priority prose does not override that record.

Live PR and Discussion searches, main-branch README searches and the
overlap cache were checked before claiming. The cache covered 744 open
PRs and 6,859 Discussion records at its recorded refresh, but the sparse
local search covered only 135 of 8,917 HEAD note paths. Main Git searches
covered omitted README content for the distinctive terms. These are
bounded overlap checks, not proof of novelty or a complete literature
survey. Relevant Schur and nilpotent-compilation results use different
contracts. No predecessor scientific engine was run.

The finite verifier has no recursion or dynamic execution and uses fixed
domains. Its largest square matrix has dimension 24; its stored orbit has
20,160 matrices of dimension six. Managed Python allocation is a stated
deviation from fixed-memory execution. All loops have bounds from these
domains; the longest function has fewer than 40 lines. Warning-strict
normal and optimized runs provide the interpreted diagnostics. A native
fixed-memory implementation is outside scope.

## Limitations

Universal quantifiers rest on the written proof. No independent human or
formal proof-kernel review is claimed. This classifies the saturated
cubic case only. Nonsaturated dimensions, other caps, nonzero-primary
parts, physical realization, native chronology, ownership, dirty
restoration, precision/tape, compiler closure and complete paid/target
accounting remain open. No selected assumption or selected frontier is
changed. No Lean, Docker or full selected-supplier replay was run.

## Open next questions

- Classify nonsaturated cap-three maximizers, starting with corank two.
  For globally cubic-nilpotent pairs in dimension four, the observation
  map is injective into a larger space; classify its invariant images.
  Dimension-five maximizers can have nonzero-primary parts and require
  separate analysis before using this map. Both cases need new arguments.
- Determine whether the saturated odd-cap-five case is rigid. First
  compute the ordered first block row of the fifth power in observation
  coordinates. The cubic proof makes no claim about its remaining free
  blocks or their physical applicability.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).

## Credit

Credit CubeJerry's #6768 for the sharp capped spectrum, surviving-kernel
idea, attaining family and explicit equality question. Retain Nick
Petalas's earlier #5928 spectral-envelope credit, JoyboyBrian's #5507
two-owner model, Ali Romman's #5456 early-helper model, and the credited
#5452/#5388/#589/#555 native, owner and compiler lineage. The triangular
positive-characteristic example of Ferrero, Puczylowski and Sidki is
classical, as are Jordan theory and orbit-stabilizer. The exact context
and primary literature reference are in the proof.
