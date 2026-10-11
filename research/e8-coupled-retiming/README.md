# E8 complex cost from four coupled frame changes

This package changes Jacob Sussman's E8 circuit at commit
`9c94857bbaee886f8649edee0bc2d3c738f9555e`. It gives a smaller recursive moment with
the same 783 helpers, copy cost 72, rank mass 56,715, and deficit 120.

| Quantity | Original | Candidate |
| --- | ---: | ---: |
| Conditional complex saving under PR352's fallback convention | 876248285600677 / 10^18 | 876412559609473 / 10^18 |
| Children in one invocation | 3974 | 3973 |
| Children in five stages | 20830 | 20825 |
| Scalar additions, including scatter | 3876 | 3876 |

The conditional saving increases by about 0.01875%.

Four phase-A additions move to two later frames. Two sets of phase-B gates use
larger frames. The original frame table gains two entries. All scalar coefficients,
retained totals, and scatter coefficients stay the same. The complete rational
scalar operator also stays the same, including its dependence on every initial
helper value.

[PROOF.md](PROOF.md) gives the exact edits and a strict cost inequality for every
saving between zero and one. It does not rely on the approximate moment root.

## Reproduce

From the repository root, run:

```sh
python3 -B research/e8-coupled-retiming/verify.py
```

The script uses Python and its standard library. It checks source hashes,
rebuilds the candidate, checks every frame path, reconstructs the scalar source
map and histogram, and compares all 1,046,529 entries of the complete scalar maps.
A coefficient identity checks the
strict-concavity proof for the full saving interval. Exact rational bounds prove both
reported savings. In each case the next 10^-18 grid point fails. Four damaged
inputs must fail for their stated reasons.

To write the candidate to another file, run:

```sh
python3 -B research/e8-coupled-retiming/retime.py /tmp/e8-retimed.json.gz
```

The saved verification result is `verification.json`. Run the script to obtain
a fresh result; the script does not use that saved result as an input.

## Scope

This is a finite complex-circuit improvement. It does not change the selected
integer-multiplication result, the bit circuit, or its saving.

The new certificate has not been compiled in Lean. The original certificate's
Lean data and theorem do not certify this changed file. A formal extension must
generate and compile new data. The general frame-transfer, helper cleanup,
recursive construction, and multiplication assembly remain inherited
dependencies. The complete scalar-map comparison does not prove those steps.
The script does not run the upstream checkers or their Lean representation
checks for separate positive and negative parts and digit limits.

## Source and search

The baseline is Sussman's `tools/certificate/gcert1-e8-r783.json.gz`. The exact
commit and original-data hash are in `sources.json`. The E8 complex
connection and fallback convention follow CrocSwap PR352 at
`04b4c3c478b5bd8797d2663d89d8db4dfd0ad9f2`. The exact reference paths and
hashes are recorded as mathematical provenance in `sources.json`; those files
are not imported or run. Earlier retiming
work includes Sussman's `tools/e8/sched.py` and CrocSwap PR328 and PR350.
This package supplies a new E8 witness; it does not claim to invent retiming.

The candidate came from bounded searches over pairs of moves and common
intermediate frames. Frames came from existing stops and their joins or
intersections. A later search moved two more complete gates to one common
intermediate frame. These searches do not establish
global optimality. The search is not needed to reproduce or verify the witness.

See [NOTICE.md](NOTICE.md) for attribution and AI assistance.
