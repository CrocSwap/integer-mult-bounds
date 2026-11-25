# PR1154 adaptive T16 word: packing relaxation

## Question and result

Does the fixed aggregate paid profile in the merged PR1154 adaptive rank-seven
T16 construction still have room under the standard nine-stage complex packing
relaxation? The profile is named and source-pinned; this is a different word
from the selected PR1094 word and from the staged544 supplier in PR3815.

The answer is yes, but the remaining headroom is small. From PR1154's frozen
owner-audit receipt, subtracting its idle histogram from the complete profile
gives the following average local paid profile over 144 calls:

```text
H1=42949/18, H2=8135/18, H3=15623/36,
H4=4753/36, H5=82, H8=8
```

Applying `research/complex-local-word-ceiling/ceiling.py::ceiling()` with
`m=73`, `families=896`, `stages=9`, `centre=64`, and grid `10^-15` brackets
the relaxed complex saving root by

```text
421850048701/250000000000000 <= a* <= 337480038961/200000000000000.
```

Thus the retained transfer gives the PR1154 word a packing cap
`kappa <= a*/(1+a*) <= 0.001684557671861340916...`. Its source-reported
`kappa=0.001673260706543984` realizes 99.3293809% of the cap. This is an
upper bound from a fractional idle relaxation, not an attained packing optimum
or a supplier-admission result.

## Derivation and scope

The source receipt gives the complete rank profile
`{1:344363,2:65097,3:62855,4:19012,5:11808,7:8,8:1152,11:2,48:4873}` and
idle profile `{1:771,2:17,3:363,7:8,11:2,48:4873}`. Their difference is the
aggregate local profile. Rank mass is 1,041,408, exactly `72*14336 + 64*144`;
the idle mass is 58,969/36 per call and the local mass is 201,383/36 per call.
The outer halving guard permits idle rank at most 51.

The ceiling proof uses only aggregate local counts. Even though PR1154 selects
different local prefixes on different calls, their moment contributions add.
For each `a >= 0`, the cost per unit of idle rank,
`(r/73)^(1-a)/r`, is non-increasing in `r`; therefore every idle histogram
with rank at most 51 costs at least the fractional placement of all remaining
mass at rank 51. The exact interval engine certifies the two sides of the root
bracket. This covers every repacking of PR1154's fixed aggregate local profile
under this coverage law and guard. It does not cover changes to the local word,
port count, coverage law, template, centre charge, or outer recipe.

The candidate's exact complex saving in `expected/EXACT-PRICE.json` is
`1676065200585730447963/10^24`, below the ceiling. Its required saving for the
reported kappa is `104578794158999/62395421205841001`. The selected bit
supplier's source-bound saving remains
`1733427039589844234749/10^24`, above that requirement, so the complex side
still binds for this comparison. The selected-record baseline is a bindings
and arithmetic check only.

PR1154 remains a partially reviewed archive. Its whole-head native/provider,
physical-owner, and complete-admission obligations were not rerun here. The
source `OWNER-AUDIT.json` and exact-price receipt are hash-checked and their
profile arithmetic is reconstructed; their underlying owner/native replay is
not independently reproduced by this package. No kappa is selected or
promoted.

## Reproduce

From the repository root:

```sh
python3 -B research/pr1154-packing-relaxation/verify.py --write
python3 scripts/research_package.py --package research/pr1154-packing-relaxation --check-only
python3 scripts/research_package.py --package research/pr1154-packing-relaxation
```

The first command regenerates `RESULT.json`; the default verifier checks it.
The calculation uses Python's standard library and the pinned ceiling module.
The registered hook checks input hashes, the coverage identity, rank split,
exact interval endpoints, the candidate and bit-side comparison, and three
failure controls. It does not run PR1154's full replay.

## Open next questions

Can an independent source-level reconstruction of PR1154's adaptive local
profiles and idle histogram reproduce the hash-pinned owner-audit receipt?
This matters because the present cap trusts that receipt as its input. The
first step is to run `research/adaptive-kernel-demotion/audit_owner_table.py`
against its frozen inputs in a separately budgeted audit. Its remaining blocker
is the inherited native/provider and complete supplier-admission chain.

## Credit

PR1154 was contributed by Dugongue, building on PR1117, PR1111, and the
retained T16 supplier lineage. The packing-ceiling lemma and exact interval
engine come from `research/complex-local-word-ceiling/`, credited there to
Douglas Colkitt with Claude assistance. This scoped application was prepared
with OpenAI Codex assistance. The source construction retains its Apache-2.0
license and notices; this new result is Apache-2.0.
