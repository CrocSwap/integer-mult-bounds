# Independent review of the portable paired-gap package

The reviewed local theorem, fixed paired word, and declared replay pass.
No material defect was found in the reviewed scope. This is a separate
OpenAI Codex agent review. It is not a human review or a formal proof.

The frozen package is
`publication/original-paired-gap-package`, relative to the campaign.
Its `PACKAGE-HASHES.json` has SHA-256
`727b5b524c26ab5b9617fb8cbe259a501e121e6067d6b4ddb533ec6a277dca51`.
The manifest binds 29 files and 673,318 bytes. This review did not change
those files. The source commit is
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.

## Proof review

For invertible Q, set S=Q squared and
`A=[[0,I],[S^-1,0]]`. Direct multiplication gives
`T=QA=[[0,Q],[Q^-1,0]]`, `T^2=I`, and `SA=A^-1`.
These identities do not require Q to have order four. Legal monomial
implementations of S and its inverse remain hypotheses.

The physical conversion uses the stated common productive frames and
the two R/K intertwiners. In the forward word, the mode preload gives
`u=z-RTx`. The mode output update gives `v=-z-R(I-T)x`. Only then does
the target update add `TKv`, which gives `y'=y+x+(I+T)Kv`.
In the backward word, the input target update must read old z. It gives
`x-=8TKz` before the mode preload. The raw word and output mode update
then give `x'=x-y-8(I+T)Kz` and `v=-z-R(I-T)y/8`.
The formulas and both inverse orders hold for arbitrary mode inputs.
No step moves A through R or K or defines A on the mode space.

After actual routes identify one global T, the cancellation
`R_s(I-T)(I+T)K_t=0` holds at every stage pair. It also gives the stated
pairwise-zero residual products and their finite product formula.
An intervening data map must meet the stated commutation condition.
Matching replica views are required. The proof does not infer a terminal
mode transport identity from the data-side A.

The fixed line identity has its full complex phase:
`C_p=((1+i)I+(1-i)X_p)/2`, so `C_p^2=X_p`. Exact tensoring gives the
same relation at every positive depth. Two replicas are used once at
each depth; the proof does not tensor the replica index. An actual
affine route fixes p. Its owner-dependent direction is therefore
unchanged, and its address translation commutes with the line. This
proves the stated route covariance at every tensor depth.

An additional exact check, written for this review without package or
producer imports, uses three data coordinates and two mode coordinates
per replica. It has rectangular R/K, nontrivial productive frames,
`Q^4 != I`, and `QKR != KRQ`. Both physical words agree with the claimed
logical formulas on all 16 input columns. Both inverse orders pass.
Missing frame intertwiners and reversed backward old-mode order fail.
The example supports the general proof; it does not replace that proof.
See `independent_algebra.py` and `INDEPENDENT-ALGEBRA.json`.

## Cold replay and checker inspection

The cold run copied only the 29 declared files to a new temporary
directory. Its separate bare Git database contains the source commit,
the three required trees, the selected archive blob, and two attribute
blobs. It has no alternates, checkout, parent commits, or campaign code.
The archive blob is byte-identical to the original pinned Git object.
Python ran with `-I -O -B`; the replay uses explicit failures, not
assertions. All four documented PASS lines were produced. The output
receipts match the producer receipts byte for byte:

| Output | SHA-256 |
| --- | --- |
| PAIR-CHECKS.json | `89c50c9ece5c209c3f17ed9cea7dfd79715a8ef7c4031603adbc8e1a274f6089` |
| NATIVE-CHECKS.json | `ee369640862c4961be56327cd248599257469fbd090ba3b60814184be2f7f074` |
| ALGEBRA-CHECKS.json | `49ed9629670af3825290409ef890e62850d71bec89aba9e3355277ec3303785a` |
| REPLAY.json | `12481f1fdb5464bd1bcba8950599da05a5ea0994e1e3559157d21423ef254e75` |

See `cold_review.py` and `COLD-REPLAY.json` for the isolated paths and
exact command. The replay took about 6.54 seconds on this run. This is
not a performance claim.

The review read all five executable files. The scalar checker compares
the complete 704-column core maps and 1,408-column paired maps. It
keeps arbitrary modes, verifies all ordinary helper columns, verifies
private-field non-use, and checks both inverse orders. The frame ledger
and native-event equality bind the retained core to the historical
source. The formal port words preserve operator order and only reduce
the individual native fourth-power identities.

The native checker verifies all literal wrapper groups, coefficients,
frames, and translation sandwiches. It checks 57,344 exact spatial
line columns and reconstructs all 1,008 actual routes from the original
phase ledger. The general checker uses only inverse cancellation for
Q and proves the displayed formal identities under the typed premises.

The wrapper controls are also meaningful for the actual native lines.
This review evaluates each formal mutation difference on a spatial
Fourier character with the exact eigenvalue `i^parity(character & p)`.
Every missing graph, omitted translation, and wrong order has an exact
nonzero witness at depth one. For example, omitted translations produce
errors -2 in the forward word and 4i in the backward word at character
1. See `check_negative_witnesses.py` and `NEGATIVE-WITNESSES.json`.
This extra witness check uses declared package row generation and a
new character evaluator; it is not a second independent full simulator.

## Local invoice and source lineage

An independent event census gives 2,688 wrapper ADDs and 448 literal
translations in each direction. The forward wrapper has 1,792 ADDs of
absolute coefficient 1 and 896 of coefficient 1/4. Its scalar allowance
is 25,088. The backward wrapper has 1,792 ADDs of coefficient 1/8 and
896 of coefficient 2. Its allowance is 34,048. With two core allowances
of 204,418, the totals are 433,924 and 442,884.

The native profile of each core is
`{1:2412, 2:418, 3:432, 4:142, 5:82}`. Its computed rank mass is 5,522,
so the pair has mass 11,044. The pair retains 10,112 native events and
adds no native child. Wrapper infinity-norm bounds 57/58 and 9/8 follow
from the stated chronological order and the exact R/K row norms.

The loader is byte-identical to its declared earlier Git source.
All five retained license and contributor notices are byte-identical
to the pinned source objects. The package preserves the earlier
lineage and discloses AI assistance. See `PINS-AND-INVOICE.json`.

## Scope and limits

The review accepts the declared local result and portable verification.
It does not repeat every old native kernel calculation. The old core
kernel and full helper interface remain inherited, as the package says.
The review inspected the inherited local and native review evidence.
It did not rerun the separate owner patch, one-shot histories, or their
global invoice.

The scalar totals exclude native child execution, native wrapper and
address-map execution, owner access, mode histories, displaced-owner
backfills, the final decoder, storage, precision, and recursive assembly.
A literal translation count is not a scalar execution cost. The zero
product does not give free odd-phase reads or injections.

No complete global word, arbitrary-mode closure for a supplier, recursive
admission, kappa improvement, or repository-wide verification is claimed
or established by this review. Owner composition is separate archival
evidence. The package states these limits clearly. GitHub link and
rendering checks remain part of the coordinator's publication review.
