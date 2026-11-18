# CensusComplete (Nov 17): census completeness for #7630, kernel-checked

Files: `Nov15/CensusComplete.lean` (imports NativeColumns + generated `Nov15/CensusData.lean`);
generator script (stdlib, not shipped; reads the #7630 data files: word.json.gz,
base-7623-word.json.gz, affected-pairs-new.json, affected-pairs-7623.json). Kernel-only (`decide +kernel`, no
native_decide, no sorry), axioms [propext, Quot.sound], 9 s / 2.3 GB (CensusData olean 7 s / 0.8 GB).
Data: census 981, census7623 964, used(#7630) 3,024 distinct MOVE (from,to) pairs, used(#7623) 3,021.

## FINDING (correction to the earlier narrowing item "a")
The premise as first stated (and in NativeColumns's item a) "every MOVE pair used by #7630 lies in the 981-pair census" is FALSE as stated:
`used_not_subset_census` (witness (0,249); generator count 2,143 of 3,024 used pairs are outside the census,
881 inside, 100 census pairs unused). The census is a DELTA census (pairs touched by the edits relative to the
inherited chain), not a census of all adapter calls. check.py itself only asserts
`move_pairs(W) - move_pairs(B) <= allp`.

## Proved (kernel, on extracted data)
- `used_subset_base_or_census`: used(#7630) ⊆ used(#7623) ∪ census (= check.py's assertion, now a kernel fact).
  `new_in_census`: the 5 new pairs are in the census; `leaving_in_census`: the 2 leaving pairs are too;
  `newPairs_facts`/`leavePairs_facts` (exactly 5 new, 2 leaving). `census_extends`: all 964 of #7623's pairs stay.
- `all_used_correct`: for any predicate `Correct` on pairs, (Correct on all 981 census pairs) and (Correct on
  all pairs used by #7623's word) imply Correct on every pair used by #7630. Composes with
  `NativeColumns.census_coverage`; "Correct on a pair" is instantiable by NativeColumns' exact-rows/columns lemmas.
- Lengths/smallness checks tying lists to the package files; subset checks are linear merge-walks whose
  soundness is proved for arbitrary lists (sortedness only matters for the check returning true).

## Still assumed for `native_all_columns`
1. `hcensus`: the per-pair column checks (check.py columns1/2, 512+512 exact columns per pair) pass on the
   981 pairs: tool fact, not re-run.
2. `hbase`: correctness of the 3,021 pairs used by #7623's word, inherited from #7623/#7620 (only 866 of them
   even lie in the 964-pair census; the other ~2,155 were never column-tested by THIS package). This is now the
   real residue of "census completeness": it is an inheritance premise on #7623, not a code fact about #7630.
3. Operator realization (Pauli frame/complex phase), compiler/precision halves, checker itself (NativeColumns b-d).
Nothing in the package is shown false; the wording "census covers every used pair" should read
"census covers every pair that differs from #7623's used set; the rest is inherited".
