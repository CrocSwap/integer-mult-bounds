# Semantic D contract for a fixed helper-mixing bit word

The existing PR1062 R439 word passes a precise replacement scalar-interface contract despite its two known syntactic H2/K failures. Its frame-zero D is exactly (x,y,h)->(x,y+N h,h) on all 661 inputs, including arbitrary helper dirt, and its semantic N equals the raw word's helper response K. The inherited H1/H3/H4/H5 and U/J/C checks remain enforced. No predecessor checker or selected supplier is modified.

The new result is the quantified scalar substitution lemma in PROOF.md and an independent, source-bound certificate on this completed word. The 11,500 ADD count is Sagar Thakrar's existing PR1062 result; this package creates no additional saving or new kappa. It does not declare native or hosted supplier admission complete.

## Reproduce

From the repository root, with Python 3.10+ and the standard library:

~~~text
python -I -O -B research/r439-semantic-d-contract-seed10/verify.py
python -I -O -B research/r439-semantic-d-contract-seed10/test_package.py
~~~

Expected: PASS_SEMANTIC_D_CONTRACT columns=661 ADDs=11500 controls=7 no_new_kappa. The package test checks minimal relocation and five corruptions. --write regenerates RESULT.json. Checks remain active under -O. Four mandatory consumed dependencies are pinned in SOURCES.json at base c0e3631dc24e3c24a861f7d3d79e0608481cccec; the selected PR1094 complex assembly still retains PR589 on the bit side.

## What changed in the contract

The old H2 requires every D gate to write a target directly from helpers. The new H2-sem permits temporary helper and target basis changes, subject to zero-frame source-free operands, the retained no-target-feedback restriction, and complete restoration of every helper and target basis at D's boundary. The remaining target increment must be N times the original helper inputs. The K check compares that semantic matrix with the actual helper block of raw A/scatter/B, instead of counting literal source indices inside D.

For example h0 += h1; y += h0; h0 += h1 restores both arbitrary helpers and adds h0+h1 to y. Its individual helper write violates old H2, but its complete boundary satisfies H2-sem. An omitted final helper restoration, residual target mixing, illegal source read or changed frame remains rejected.

The original checker is called unchanged and must retain exactly its two documented H2/K failures on the candidate. All its other geometry, full endpoint, interface and cleanup checks pass. Our row engine extracts semantic N; a separate numeric input-column engine checks all 661 D columns without importing that engine or producer code. RESULT.json stores all 111 rows of N as exact hexadecimal masks. A proof-only splice keeps the candidate continuation and restores original PR589 D; every unchanged interface flag must pass on that splice. The two zero-frame D prefixes give identical values and frames before the unchanged chronological continuation, as proved explicitly in PROOF.md. The virtual D is not charged. The actual full literal COPY/ERASE stream is checked in both directions.

## Complete local accounting

| Quantity | Selected PR589 | Fixed PR1062 candidate |
| --- | ---: | ---: |
| ADDs |24,305|11,500|
| D ADDs |18,085|5,548|
| COPY / ERASE |9 /9|9 /9|
| COPY rank sum |63|63|
| Paid rank mass |5,129|5,129|
| Positive forward / reverse envelope |49,347 /1,113,070|25,717 /5,911,840|
| Local / nine-stage guard bits |93 /177|95 /182|

The profile remains {1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}, and every ordered register frame path is unchanged. Both words satisfy the strict 104-bit local and 192-bit nine-stage guards. The new contract does not make helper writes, restoration, copied information, frame changes or recursive children free. Scalar ADDs are fully counted, and zero-frame D introduces no recursive frame child. No complete hosted invoice is regenerated.

Seven semantic controls include six negative mutations and one positive restored-helper fixture. Five separate packaging controls reject a missing dependency, duplicate key, nonfinite JSON, altered consumed source and Boolean substituted for an integer receipt count.

## Scope and credit

The universal statement concerns coefficient matrices over F2 acting on arbitrary F2 modules; it discharges the named scalar H2/K substitution obligation. It retains the common-frame realization premise and does not prove physical/numerical semantics from an endpoint alone. Native C++/Boost, stage hosting, all-size compiler, rounding/tape, phase/Gram, outer assembly and analytic obligations remain unexecuted or inherited. The proof explicitly distinguishes the old raw J=I check from the H1-H5 shape conditions.

PR967 helper stars and PR1062 B/star composition previously retained the syntactic H2/K mismatch. Prior copy-path sharing research identified that restriction but did not change it. Fresh PR1122 composes further A savings and reports native replay, but explicitly retains the same syntactic H2/K failures and interface-adoption obligation; this package makes no claim to its circuit or native results. PR1188 further reduces the composed word to 10,492 ADDs and likewise explicitly retains the H2/K interface obligation. This package does not repeat their searches, the PR1043 source-boundary deletion, or the earlier precision/omission/matching audits. It preserves all original files.

Credit Zhihao Chen's PR425 scalar-interface lemma, eumemic's R420/PR555 checker adaptation, DreamingOfClouds' PR589 tuning, Gareth Davidson's PR926 pair line, @theon199's PR967 helper stars, Sagar Thakrar's PR1062 composition, Aaron Wang's PR1015 B circuits and Ross Richardson's PR923 frame520 circuit. Contributor @woklerx with substantial OpenAI Codex assistance; Apache-2.0. No independent human review or full multiplication-theorem proof is claimed.
