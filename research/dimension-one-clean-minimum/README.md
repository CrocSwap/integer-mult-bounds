# Dimension-1 clean support is exactly 41

On the fixed PR #5745 source, every nonzero clean relation among the 119
dimension-1 frames has cancelled frame support at least 41, and two explicit
relations meet 41. The ten-channel certificate left this minimum open and
recorded only the upper bound γ ≤ 41. Inside the dimension-1 subfamily the
upper bound is tight.

This is an exhaustive finite census of a 28-ray list, plus an exact 6-span
enumeration that proves the list is complete. It is not a heuristic search.
The selected frontier κ = 363005817/100000000000 is unchanged. No schedule and
no mixed-dimension support is priced here.

The complete argument is in [PROOF.md](PROOF.md).

## Reproduce

From the repository root, with a C compiler (`cc`, `gcc` or `clang`) on `PATH`:

```sh
python3 -B research/dimension-one-clean-minimum/verify.py
python3 -O -B research/dimension-one-clean-minimum/verify.py
```

Both commands replay the orthogonal census, rebuild the 14-dimensional
dimension-1 kernel, evaluate the 28 low-weight projected rays and enumerate
the 6-spans of the three heavier zero-sets. They print
`PASS_DIMENSION_ONE_CLEAN_MINIMUM`. The span program is
[span_bound.c](span_bound.c). Tested with CPython 3.12 and gcc. One command
takes about two minutes here; the registered timeout is 600 seconds. Proof
checks raise `SystemExit` rather than using assertions, including under
`python -O`.

## Open next questions

- Can a sum that uses at least one frame of response dimension 2 or more meet
  the clean mode on fewer than 41 frames? The dimension-1 subfamily cannot
  improve the upper bound γ ≤ 41, so any shorter relation has to leave that
  subfamily. The first step is one dimension-2 frame whose nuisance image
  meets a dimension-1 frame, then the shortest clean support in that sum.
  The census here does not see mixed supports.
- Is the clean generation number at least 11 on this source? That is still
  the missing inequality for an 8 H_8 floor at ten channels. The first step
  is a four-frame screen on the 3,782 intersecting pairs from the ten-channel
  certificate. Supports 4 through 10 remain open.
- Can either 41-frame mode be scheduled as legal channels whose complete
  transport, restoration and ordinary bill beats 8 H_8? Price one of the two
  witnesses under the PR #5745 contract. No schedule is constructed here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The census method and the nine-channel pair theorem are Ali Romman's. The
41-frame upper bound and the three-frame obstruction are the ten-channel
certificate's. Predecessor source attribution is retained in PROOF.md.
