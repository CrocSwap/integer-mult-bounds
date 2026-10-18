# Attribution and license

Prepared for **ToikY** with substantial assistance from **OpenAI Codex**,
including bounded circuit search, implementation, exact replay, documentation
and separate AI review. The independent implementation is independent code,
not an independent human review. New material is licensed under the repository's
Apache-2.0 license. Existing source notices remain unchanged.

The mathematical object is inherited from:

- eumemic's [PR493](https://github.com/CrocSwap/integer-mult-bounds/pull/493),
  E8 carrier skeleton and native verification framework.
- DreamingOfClouds's [PR503](https://github.com/CrocSwap/integer-mult-bounds/pull/503)
  and [PR510](https://github.com/CrocSwap/integer-mult-bounds/pull/510), the
  R480 word and nine-stage replay. Their exact source heads and the retained
  word hash are recorded in `SOURCES.json`.
- Hao Yan's [PR823](https://github.com/CrocSwap/integer-mult-bounds/pull/823),
  related R480 six-wire quad1 resynthesis. This submission instead changes
  the twelve-source Q-node2 matrix.

Bounded XOR resynthesis builds on the research approach represented by
Jeffrey Cox's PR754, Gareth Davidson's PR904/952 and Ross Richardson's PR936.
PR857/906/980 provide precedent for complete precision admission without
requiring local positive-envelope domination. No priority claim is made for
that general mechanism.

`native.py` adapts Ross Richardson's retained PR925 harness, which credits
Ali Romman's PR688 work, together with the PR503/510 verification commands.
It runs the existing exporter, stage-cohort builder, legality and column
checkers, relaxed mutable-source checker, PR425 interface and Gram checker.
Credit for those inherited components includes Dylan Crow, Zhihao Chen,
DaysSky and the contributors named in the retained carrier-skeleton notice.
No imported checker has been edited.
