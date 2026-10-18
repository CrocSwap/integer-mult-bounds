# Independent local replay: R439 frame 509

This package independently replays the local matrix claim in Hanson Sun's
[PR #1221](https://github.com/CrocSwap/integer-mult-bounds/pull/1221) at exact
head `6deda901721316fcb61c6e2a6dd6b537de183452`, against Cinna Davis's PR #973
block at `c05dc72734c25dd069077157224d4dd30c6e8c19` and the selected PR589 word
pinned in `SOURCES.json`.

The direct row-bitset interpreter checks the complete 11-register local map
over GF(2), independently of the proposal verifier's column/truth-table code.
An integer coefficient-vector replay checks the exact local difference. The
word builder then confirms that the splice yields the reported whole-word ADD
counts and preserves all 661 ordered frame paths. This is an independent
replay of those finite claims; it does not reprove H1-H5 or native legality.

The exact local result is:

| Local splice | ADDs | Boolean map | Integer map |
|---|---:|---|---|
| PR973 predecessor | 21 | same as candidate | baseline |
| PR1221 candidate | 20 | same as predecessor | predecessor minus `2 e_468 e_33^T` |

The full selected / predecessor / candidate word invoice recomputes as
24,305 / 24,285 / 24,283 ADDs. The builder changes only the B/C ADD lists; all
other pinned word fields, including the ret/scatter schedule, remain equal, and
all 661 ordered frame paths match. The separate PR #1221 checker replay also
confirms its complete paid profile. This scalar circuit saving does not change
the selected conditional `κ = 836330098538459/500000000000000000`; the complex
supplier remains binding.

## Reproduce

From the repository root, with Python 3.11+ and only the standard library:

```sh
python3 -I -B research/seed18-r439-b509-independent-replay/verify.py
python3 -I -B research/seed18-r439-b509-independent-replay/test_audit.py -v
```

Expected verifier marker:

```text
PASS_R439_B509_MATRIX_AUDIT local_f2_inputs=11 integer_delta=2*e468e33 frame_paths=661 ADDs=24305/24285/24283 no_new_kappa
```

As an additional independent-host replay, the exact PR #1221 package passed
its own verifier, ten package tests, and unchanged C++ native checks here on
Linux x86_64 / CPython 3.14.7 / GCC 16.2.1 / Boost 1.92.0. The reproduced
markers are recorded in `VALIDATION.json`. This supplements the source author's
macOS arm64 run; it does not substitute for human review or hosted CI.

## Scope

The result validates only the local finite matrix identity, the pinned splice,
its frame paths, and the listed ADD invoices. The PR #1221 H1-H5/native
obligations are inherited from the candidate's own checks and were rerun as
described above. No global minimum, hosted-supplier adoption, new kappa, or
complete multiplication theorem is claimed.
