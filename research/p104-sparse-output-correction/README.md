# A 74-gate correction for the scaled P104 transport word

The 569 final scalar correction gates in [PR6529](https://github.com/CrocSwap/integer-mult-bounds/pull/6529)
can be replaced by 74 ADDs with exactly the same operator. The replacement
uses two existing public fields and restores them to their required outputs.
It adds no owned field, native map or productive target.

The complete source real scalar allowance falls from **137,218 to 132,256**.
This saves **4,962** units per native call, or **89,316** across eighteen calls.
The source's paid rank profile and conditional kappa are unchanged.

Read [PROOF.md](PROOF.md), [correction.py](correction.py) and the literal word
in [RESULT.json](RESULT.json). The factorization has rank two and four zero
pairings. The new correction is the exact source operator on all 799 fields.
The complete scalar word also passes forward and independent reverse checks.

## Scope and evidence

The finite optimization covers 78,408 pivot, signed scale and direction-order
choices. All 44 minimum-cost programs pass exact operator checks. The chosen
program costs 696 source scalar units, compared with 5,658 before. It is not
proved optimal among arbitrary linear circuits; the simple global lower bound
is 28 target writes.

Correction-only prefix norm rises from 21 to 28. The complete-word maximum
row l1 norm remains 838, and maximum coefficient magnitude remains 17.
All 74 omission and 74 doubling controls, three full-word controls, five
invalid inputs and six source-byte corruptions are checked.

Source heads, original Git blobs and SHA256 values are in
[SOURCES.json](SOURCES.json). Frozen files stay unchanged. Source native,
physical, compiler and outer evidence is retained, not rerun or admitted here.
The five framework assumptions and independent scientific review remain.

## Reproduce

```sh
python3.12 -I -Werror -B research/p104-sparse-output-correction/verify.py
python3.12 -I -O -Werror -B research/p104-sparse-output-correction/verify.py
python3.12 -B scripts/research_package.py --package research/p104-sparse-output-correction
```

Only the standard library is required. The exact source word, correction,
receipt, proof, notice and scalar checker are retained under `inputs/`.
The package has no external runtime input.

## Open next questions

Can an unrestricted scalar program close the 28-to-74 gate gap? Start with
the exact rank-two matrix and a circuit model that counts all temporary work.
The present finite parameter search does not decide this question.

Can an emitted rounded caller use the smaller correction allowance? Bind the
new prefix to that caller's precision and tape contract, and recheck its full
ordinary budget. The exact scalar proof alone does not supply that contract.

## Credit

New source-bound factorization, program, proof and checks: Ali Romman with
substantial OpenAI Codex assistance; no subagents. PR6529 retains its transport
construction and kappa gain. Rohan Arun supplied the PR6399 donor-merge
precedent. Erwan L. supplied PR6453. Credit DreamingOfClouds, Cinna Davis,
David Arias, Gareth Davidson, Jacob Alan Sussman, zxv, Cao Yifan and all
retained native, helper, controller and compiler authors. The original notices
and checker header remain in `inputs/`. Classical low-rank algebra retains
its classical credit. New work is Apache-2.0.
