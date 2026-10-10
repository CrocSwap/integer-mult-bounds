# Twenty-five exact frame retimings after PR254

**Conditional κ = 71046804825911 / 100000000000000000 = 0.000710468048259110.**

This composes 25 explicit rational gate-frame changes with
[Dugongue's PR254](https://github.com/CrocSwap/integer-mult-bounds/pull/254),
pinned to `9ce32efb421132420242cfdb91ddd9eabe2c3795`.
The parent value is `0.000710465200632830`; the exact increase is
`71190657/25000000000000000`, approximately `2.84762628e-9` (0.0004008115%).
These are prices of the complete combined construction, not added estimates.

Twenty-four surviving forward additions replace paid children `(5,5)` by
`(4,6)`. One equal-response read replaces `(2,2,11,17)` by `(13,13,6)`.
The full scalar/COPY sequence, data and dirty endpoints, stock, rank mass and
entrance bank assignment stay identical to PR254. The 40-replica five-stage
word removes **200 recursive calls**. All intermediate frames remain nested
and nondegenerate. See [RETIMING-PROOF.md](RETIMING-PROOF.md).

## Reproduce

Python 3.11+, SymPy 1.14.0, GNU g++ with C++17 and Boost headers are required.
On Ubuntu install `g++ libboost-dev`, then:

```sh
python3 -m pip install -r research/cohort-kernel-retiming25/requirements.txt
python3 -B research/cohort-kernel-retiming25/verify.py --output /tmp/retiming25-replay
```

The output directory must be new and outside the package. Replay requires no
network, credentials, GPU or Lean installation. Keep assertions enabled.
`--cxx` and `--boost-include` allow a nonstandard compiler/header location.
Only the complete fresh-source mode is exposed by this entry point.

The command checks the outer and inner manifests, regenerates the pinned
PR249/source527 baseline, executes the PR254 response-kernel transform and
the new retiming, compiles all seven native checkers, evaluates every used
cleared Gram determinant, and independently repeats pricing with two Python
moment engines. Frozen receipts are comparison targets, never replacements
for execution. Both manifests are rechecked after replay.

## Evidence and paid profile

- Local forward/inverse F2 correctness on 20,107 arbitrary formal columns;
  the post-retiming scalar/COPY projection is byte-identical to that checked word.
- Fresh global replay on all 23,627 formal F2 columns, including arbitrary dirt.
- Independent chronological frame/COPY legality; 98,443 exact frame pairs and
  both reflected annihilator ledgers.
- All 26,610 used-basis cleared Gram determinants freshly evaluated; every
  remaining excluded factor below the retained `2^80` prime lower bound.
- The same 132 new entrance charts and all 3,317,400 bank assignments as PR254.
- Native exact rational pricing, two independent Python interval engines,
  all 47 strict outer inequalities, seven margins and adjacent-grid rejection.
- The finite invoice consumes the actual retimed word and its fresh price.

| Quantity | PR254 | This package |
| --- | ---: | ---: |
| Literal stock | 869,195 | 869,195 |
| Literal positive-rank children | 19,675,400 | 19,675,200 |
| Literal rank mass | 104,127,400 | 104,127,400 |
| Literal deficit | 176,000 | 176,000 |
| Normalized stock | 173,839 | 173,839 |
| Normalized children | 3,935,080 | 3,935,040 |

`RETIMING-CERTIFICATE.json` records the top-level replay result.
`CERTIFICATE.json` records the inner native admission; additional fresh
receipts are under `lead/`, `review/`, `compiler/` and `temporal/` in the chosen
output directory. `INDEPENDENT-PYTHON-PRICE.json` gives the separate exact pricing.

## Dependencies, attribution and scope

The byte-preserved inner package has manifest SHA256
`c9221f3e1bfc4d5a869ff1f73cd1b90ec2a22b0e647ffa8d161207e0e4a8d8ed`.
It includes PR254's native checkers and pinned PR249 source archive; no pending
PR needs to be merged to reproduce this contribution. Its historical README
and proof notes describe the parent; the inner `OVERLAY-NOTICE.txt` and this
README identify the added retiming. Source attributions and licenses remain
in [source/NOTICE.md](source/NOTICE.md) and
[source/vendor/UPSTREAM-NOTICE.md](source/vendor/UPSTREAM-NOTICE.md).

Predecessors include eumemic's source527 construction, PR244 common-frame
retiming, PR249/251 transported entrances, and Dugongue's PR254 response-kernel
entrances. The original contributors' notices are retained. New search,
composition, wrapper and documentation were prepared with substantial
OpenAI Codex assistance. New code is Apache-2.0; vendored files retain their
original terms.

This is a finite conditional construction under the retained public all-size
compiler, common weighted chart, routing, prime supply, complex recovery,
symbolic correctness and analytic-reduction interfaces. Those general
theorems are not independently reproved here. The payload cancellation is
over F2; odd-prime address algebra is separate. The modified word is admitted
through the PR254 native pipeline and new exact Python checks, not a verbatim
replay of the public eight-stage Python command. No unconditional theorem,
practical timing result, new Lean certificate or current leaderboard claim
is made. The separate five-cube larger-bank global schedule remains open and
is not part of this contribution.
