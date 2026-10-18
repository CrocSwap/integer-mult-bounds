# Validation and overlap record

Validated on macOS arm64, 2026-10-13, with CPython 3.14.8 and 3.11.15.

```sh
python3 -I -B research/complex-jp8-fanin/verify.py
python3 -I -O -B research/complex-jp8-fanin/verify.py
python3.11 -I -O -B research/complex-jp8-fanin/verify.py
python3.11 -I -O -B research/complex-jp8-fanin/check_columns.py
make selected-record-check
```

All passed. The main result is 999 batches, 3,022 additions and 19,688 saved
real primitives, with twelve controls. The independent column checker covers
5,020 local input columns and rejects the omitted final clear in every block.
The independent checker also passed normal and isolated optimized CPython
3.14.8 execution. No Python assertion is required for these checks.

The original and replacement full scalar projections have the same exact
endpoint on all 716 live columns, eight arbitrary centre inputs and one
arbitrary coefficient-work input. Original complete costs and prefix envelopes
match the pinned source receipts. The replacement backward peak remains
`16753412757380464429924108070201913461/8388608`, or 101 bits.
The selected-record/source-inventory check preserves
`kappa=51110230636731/31250000000000000`.

Additional in-memory I/O controls monkeypatched only `Path.read_bytes` or
`Path.read_text`, without modifying any source file. Recompressing the exact
program payload with gzip level 1 and timestamp 123 passed source admission.
Changing its `zero_frame_precondition` marker failed the payload pin. Replacing
`EXPECTED.json` with an empty object failed with `receipt mismatch` after the
full computation. The twelve committed controls separately exercise semantic,
cost and prefix obligations.

Two separately delegated Codex workers checked the narrowly claimed algebra
and implementation. One independently reconstructed all 999 block identities,
complete prices and prefix envelope. The other supplied `check_columns.py`
using a separate grouping method and flat-vector column execution. Their
findings agree. This is scoped AI review, not independent human review.

## Overlap and dependency check

The initial open queue through #725 and the negative results #719 and #698
guided selection. The later queue snapshot contained 566 open PRs through
#747; main remained at `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Descriptions, source heads and file inventories were inspected for the closest
related contributions. Those implementation bytes were not imported or
independently verified here.

The immediate pre-submission refresh contained 567 open PRs through #748.
The new #748 concerns R420 decoder source cosets and does not overlap this
JP8 backward circuit. The pinned-issue list was still empty.

| PR | Inspected head | Relationship |
| --- | --- | --- |
| #722 | `a0766ab0fab379e1997fadc3ca157578d57986c1` | Direct sharing predecessor, forward common-source runs |
| #739 | `abb9825202dba6f9bc95c7df8d12d86088fdff1a` | Forward sharing across magnitudes; reports no backward joins |
| #696 | `5a3f983715027c4fd83f50bc9001d4b18463bed1` | Individual macro lowering |
| #723 | `d3bc41b87fc7d23f50d064a0f06f1a89e3ab02a7` | Individual signed-digit lowering |
| #734 | `ba76ba3321d000c8996b0b254bcf0d7260e1bbb6` | Prefix-bounded signed Horner and private-input replay |
| #745 | `fc6ebccca3bd61a6eaf6ec3fcbf2e99d2888c35c` | Independent reverse replay of original JP8 private centres |
| #719 | `a3d9c0aa0a16b68b1f4dd064671ad018013e6dd4` | Fixed-middle CK pair obstruction |
| #681 | `fdc2e4f3c6825530b02143b30deab5de10209479` | Raw factory resynthesis |
| #729 | `deaed262cebc50bdb0c27c6ba132b8f8289b3eef` | Standalone helper-frame lifetime audit |

## Not executed

Repository-wide `make verify`, selected cold supplier regeneration, fresh
native wrapper/phase replay, global invoice/admission/assembly regeneration,
Lean and remote Linux CI were not run for this isolated addition. The new
full-frame batches preserve scalar maps and lifetimes; other geometry and
physical/analytic obligations remain inherited. No existing generator,
production emitter, selected certificate, or upstream source was changed.
