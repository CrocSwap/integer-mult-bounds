# Independent agent review: PG(2,9) matched-stub completion

Result: PASS for the stated finite scalar identity and its exact input
promise. One verifier robustness issue was fixed and checked. No material
mathematical finding remains open. This review used a separate OpenAI
Codex agent. It is not independent human review or a formal-kernel proof.

The contribution supplies a checked scalar boundary contract and explicit
correction matrices for the historical PG(2,9) transcript. It gives a new
local capability: nine independent matched junk values can pass through
the transcript with the 157 message values intact, and the stated scalar
correction restores those nine values. It does not construct the physical
matched-input preparation, physical return, or complete supplier. There
is no verified complete kappa improvement.

The reviewed files and their exact hashes are in `CHECKED-FILES.json`.
The PR description standard at
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`
was read. The coordinator must check the final description, public source
targets, and GitHub rendering before publication.

## Mathematical contract

The saved transcript defines a 175 by 175 transfer over
`F3[t]/(t^2+1)`. Both replay implementations check all 182 local invertible
five by five maps, follow the 735 transmitted edge values, and reconstruct
every boundary coefficient. The first 157 by 157 block is the identity.
The off-diagonal block ranks are nine and nine; the final 18 by 18 block
has rank 18. The full transfer and the Schur matrix `H-GF` are invertible.
The saved transfer is not a role permutation.

The matched-input map duplicates each of nine independent values on the
two stubs of one C edge. The resulting message block has no junk term.
The two outputs of each J edge then agree, so one output per pair gives
the map `(x,z) -> (x,Bx+Dz)`. The checked nine by nine D is invertible.
Applying `D^-1` and then subtracting `D^-1 Bx` gives `(x,z)`.
The original completion replay checks all 166 formal GF9 input columns,
both inverse products, and every entry of all saved factor matrices.

This review also used a third arithmetic representation. It maps
`a+bt` to the matrix `[[a,-b],[b,a]]` over F3. It checked all 81 addition
and multiplication table entries in both implementations, all eight
nonzero inverses, and irreducibility of `t^2+1` over F3. With these
two by two blocks, the final identity holds on all 332 formal F3 columns.
The 74 nonzero D entries and 1,243 nonzero correction entries agree with
the saved counts. These are matrix entries, not native call prices.

The matched-input promise is necessary. For example, the transfer entry
from boundary input column 157 to message output row 0 is the nonzero
GF9 element encoded by 3. With all other inputs zero, this independent
stub contaminates that message. Adding its matched partner cancels the
message contribution. Thus arbitrary values on all 18 C stubs do not
satisfy the nine-value contract. The proof states this restriction.

Selecting one J output is an injective quotient only on the stated
matched subspace. It is not a free physical erasure of a second arbitrary
register. The theorem does not restore an additional nine independent
borrowed values. Preparation of the input equality, handling of duplicate
outputs, legal common rational frames, inverse-correction access and
operations, physical return, recursive children, hosting, and the complete
compiler bill remain open. The 735 edge transmissions are network-code
transmissions, not an admitted multiplication-supplier profile.

## Checks and the fixed finding

The package wrapper passed normally. This review then ran the fixed
wrapper with both `PYTHONOPTIMIZE=1` and `-O`. It passed both child replays
and compared their complete receipts. The wrapper now starts the children
with `-I`, which prevents the inherited environment from disabling their
assertions. It does not pass `-O` to them.

The issue was specific: the original wrapper removed its own `-O` flag
from child arguments but still inherited `PYTHONOPTIMIZE`. That variable
could disable the child checks. The packaging worker added `-I`; no
mathematical source or saved transcript was changed.

To check the fix, this review changed one saved correction factor in a
scratch copy and updated only its source-hash entry. The wrapper rejected
the changed factor at `factors == independent_factors`, even under the
optimized environment. A separate scratch mutation made one local map
singular; the first independent replay rejected its rank. The lifted
matrix check also shows that omitting the message correction or D
normalization fails. Original package files were unchanged by the tests.

Commands run from the workspace root include:

```sh
python3 -I -B work/project-final-cleanup-20261022/early-remainder-audit/packages/pg29-matched-dirty-completion/verify.py
env PYTHONOPTIMIZE=1 python3 -O -B work/project-final-cleanup-20261022/early-remainder-audit/packages/pg29-matched-dirty-completion/verify.py
python3 -I -B work/project-final-cleanup-20261022/reviews/pg29-completion/check_review.py --package work/project-final-cleanup-20261022/early-remainder-audit/packages/pg29-matched-dirty-completion --out work/project-final-cleanup-20261022/reviews/pg29-completion/fresh --primary-dir work/p518-next/architecture/small-motif
```

The last command printed `PASS_PG29_INDEPENDENT_REVIEW_CHECKS`. Its
reports and logs are under `fresh/`. It needs a new output directory.
The review script accepts explicit paths; `--primary-dir` is optional.
Without that option, it runs all scalar checks and rejection controls
without the historical source folder. The runtime was Python 3.14.7.
No Lean, full supplier, frame realization, outer kappa calculation, or
hosted CI check was run.

## Provenance, credit, and overlap

The live pinned GitHub tree at
`3436359a85d13a1bf6e87c3a3dbdaa64788277f4` confirms the local verifier and
parameter file blob hashes. Their SHA-256 values agree with SOURCES.
The tree has no license file. The package does not redistribute that
companion implementation. Its Apache-2.0 statement applies to the new
work; the mathematical transcript and newly written separate replay
implementations are the submitted material.

The credited primary authors are Mark Braverman and Zhongtian He, as
listed on [the pinned paper](https://arxiv.org/abs/2610.10108v1). This
review reran their pinned original verifier and the historical transcript
generator in a temporary directory. The transcript regenerated byte for
byte. This is a provenance replay that uses primary-source utilities,
not a second independent derivation of the projective geometry. No
primary source code is copied into the review output.

All seven ORIGINS entries match their old source hashes. The six entries
marked unchanged are byte-identical. The adapted completion script has
unchanged mathematical function syntax trees. Its source paths were made
local, its unsupported conditional-price section was removed, and its
receipt was limited to the scalar result.

A bounded search of all tracked Markdown, TeX, and text files at main
`cef4b52f2a59009865bf8eabde1be3f159063703` found eight related literature
or sign-gauge mentions, but no submitted scalar completion. The related
PR #288 text concerns a rational common-target frame obstruction.
The parent-fetched 315 open PR titles and bodies found
[PR #349](https://github.com/CrocSwap/integer-mult-bounds/pull/349), which
gives an explicit witness for that obstruction. It does not supply the
matched-stub scalar completion and is not resolved by it. The README
correctly retains the physical-frame limitation and predecessor credit.
These checks do not establish novelty against all closed diffs,
compressed archives, Discussions, unpublished work, or outside literature.
