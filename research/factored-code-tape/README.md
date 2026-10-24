# A smaller local tape bound for inverse recoding

This conditional arithmetic construction lowers the actual source mode code
to a 130-tape classical machine. Its complete local bound is
`N(2298W+4722)+34W+132`, compared with the source bound
`N(2898W+5922)+18W+100`. The new bound is smaller for every N>=1.
The machine uses eight extra temporary words. Its rounded numerical map,
eight division calls and two-grid-unit local error are unchanged.

[PROOF.md](PROOF.md) gives the fixed-word schedule, range and sweep proof.
[kernel.py](kernel.py) emits 308 gather and 280 scatter instructions and
allocates at most eight temporary words. [RESULT.json](RESULT.json) records
the exact replay. [SOURCES.json](SOURCES.json) pins all consumed input bytes
at canonical main ff3cc58e370d0f678e529246f8c73e8094e18fcf, priority 7.

This adds the physical arithmetic bill left open by
[Discussion #5314](https://github.com/CrocSwap/integer-mult-bounds/discussions/5314),
whose scalar factorization is reused with credit. The
[scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5314#discussioncomment-19150518)
excludes the complete coded caller. All112 owner tapes are distinct and
provided at common coordinates. All17 owned scratch words return zero;
this is paid classical overwriting, not reversible cleanup.

## Reproduce

Use CPython 3.12 and the standard library from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/factored-code-tape
python3.12 -I -O -W error -B research/factored-code-tape/verify.py
```

Expected marker: PASS_FACTORED_CODE_TAPE. Both registered modes check all 112
and eight basis columns, 36 batches, 48 mixed/extreme source comparisons,
N=0/1/3, dirty scratch return, independent tariff addition and numerical-sign
and alias controls. Source imports use authenticated bytes. The emitted bit
instructions execute; the complete target TM is specified by a sweep proof,
not measured as a full physical caller.

No native Gaussian, compiler, outer ledger, Lean or selected replay ran.
The Gaussian paid profile and complete kappa calculation are unchanged.
Common-coordinate access, wrappers, field movement and full error funding
remain caller obligations. This is author-checked evidence; independent
human or proof-kernel acceptance is not claimed.

## Open next questions

Bind the tariff and 17-word workspace to one affordable complete caller with
legal common-coordinate access. First charge its wrappers and physical
movement and retain its error budget. Those missing caller contracts block
admission; they are not zero-cost operations. The structured question is in
TASK.json.

## Credit

[PR #5035](https://github.com/CrocSwap/integer-mult-bounds/pull/5035) by JoyboyBrian
supplies the finite divider, rounding, validation and original sweep tariff.
[PR #4933](https://github.com/CrocSwap/integer-mult-bounds/pull/4933) by Dillon
supplies the source physical mode factorization. Dugongue and retained
native, ownership, precision and compiler authors keep their source credit.
Standard Walsh butterflies are not claimed as new. New lowering, allocation,
tariff and checks: Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. Frozen sources and notices remain unchanged.
