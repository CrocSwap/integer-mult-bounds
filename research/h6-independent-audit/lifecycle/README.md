# Finite dirty-helper Walsh lifecycle probe

This probe emits and independently replays a small legal common-frame scalar
word on actual PR606 E8-squared port labels. It addresses the useful first
experiment proposed in the adjacent helper audit. It establishes a lifecycle
example, not an all-port H6 compensation construction or an admissible supplier.
Prepared with OpenAI Codex assistance; Apache-2.0. Geometry and frame conventions
are attributed to Dominik Scholz's PR606; the H6/Walsh question is attributed to
DreamingOfClouds. Frozen predecessor files remain unchanged.

## Exact result

Sources are actual ports 0 and 3; targets are actual ports 287 and 288. Their
17-bit labels are reconstructed from the pinned `e8_cubed.py`, whose SHA256 is
recorded in `RESULT.json`. Every one of the four source-to-target binary
pairings is zero, checked against its actual odd lattice pairing. Consequently
the rank-two frame `F = span(p_0,p_3)` is contained in both target caps.

The emitted word acts on six independent arbitrary scalar inputs:

```text
s0' = s0                  a' = a
s1' = s1                  b' = b
t0' = t0 + s0 + s1
t1' = t1 + s0 - s1
```

This is a two-by-two Walsh shear supported on permitted incidences. Its
coefficients are a chosen positive control; they are **not asserted to be the
corresponding entries of H6's `I-K`**. It does not establish a shared circuit
for that complete 30,960-port matrix.

There is also an emitted **literal compensation subword** for these same
incidences. The actual lattice pairing matrix is `[-1,1;1,-1]`, so the actual
off-diagonal `I-K` matrix is `[-1,1;1,-1]/16`. Its one-helper word is:

```text
frame 0: t0 += a/16; t1 -= a/16
frame F: a += s0-s1; t0 -= a/16; t1 += a/16
FULL:    a -= s0-s1
```

All operand joins and final climbs are emitted. Exact five-column replay
checks the intended actual compensation matrix and independent arbitrary
helper dirt in both orientations. This gives a concrete first actual
compensation example, while leaving the all-port problem open.

1. At frame zero, precompensate target dirt by `t0 -= a+b`, `t1 -= a-b`.
2. Climb both sources, both targets and both ordinary helpers to F. Sources
   start at their actual rank-one label spans; all targets/helpers start zero.
3. Gather `a += s0`, `b += s1`; execute the invertible dyadic Walsh transform
   `(a,b) -> (a+b,a-b)` at F; scatter `t0 += a`, `t1 += b` at F.
4. Climb sources/helpers to FULL. Undo the Walsh transform and both gathers
   there. Helpers therefore retain their independent arbitrary initial dirt.
5. Climb each target from F to its own rank-16 cap.

The exact rational replay checks all six input columns, including both helper
dirt columns. A separate frame interpreter verifies equal *current* frames
for every addition, ascending nested ordinary transitions, and each endpoint.
The inverse-transpose scalar orientation is replayed in the same event order
with the same frame chronology; all six columns also agree exactly.

## Paid local profile and limits

| Role | Initial dimension | Transition ranks | Final dimension |
| --- | ---: | --- | ---: |
| Each of 2 sources | 1 | `[1,15]` | 17 |
| Each of 2 targets | 0 | `[2,14]` | 16 |
| Each of 2 ordinary restored helpers | 0 | `[2,15]` | 17 |

The emitted local transition mass is `2*16 + 2*16 + 2*17 = 98`, and there
are no private copies or descents. The one-helper literal compensation
subword has the same data paths, helper path `[2,15]`, and local rank mass
`2*16 + 2*16 + 17 = 81`. These are recounted local profiles only.
The physical Clifford transition/compiler replay, controller stages,
replication stock, helper-bank pads, and any actual supplier invoice remain
outside this probe. No numerical kappa is inferred from it. The existence of
this small example says nothing about whether the H6 proposed helper count
can implement its complete matrix or preserve its proposed coarse data paths.

## Negative controls

The same exact replay rejects or detects five tempting shortcuts:

- Omitting the FULL cleanup changes the non-target scalar block.
- Omitting compensation for independent dirt b leaves coefficients +1 and -1
  in the two target rows even though the helpers are subsequently restored.
- Reusing a helper after its FULL climb to gather a source still at F has
  different operand frames.
- Sending an ordinary helper back from F to zero is a prohibited descent.
- Loading a source at its rank-one frame into a frame-zero accumulator has
  different operand frames.

These are scoped controls. Sequential helper reuse can be legal while its
frame is unchanged and its scalar state is properly restored; this probe
does not claim a universal obstruction to Walsh circuits or scratch reuse.

## Reproduction

From the repository root, with a NumPy-capable Python:

```sh
python3 -B research/h6-independent-audit/lifecycle/probe.py
python3 -O -B research/h6-independent-audit/lifecycle/probe.py
```

The script imports only predecessor geometry. Its scalar and binary frame
interpreters are independent of predecessor circuit audits. It writes only
the adjacent `RESULT.json`; checks remain active under `-O`. The receipt
contains the actual port vectors and labels, incidence checks, complete event
stream, endpoint frames, transition ranks, exact forward/dual matrices and
all counterexample matrices or rejection reasons.

## Open next questions

- Find a larger low-frame incidence cover that produces the actual `I-K`
  coefficients, then emit its complete compensated word. The first step is
  a small actual compensation submatrix with multiple source/target frames.
- Determine whether channels can share helpers before FULL while retaining
  arbitrary-dirt restoration and a useful target chronology. Emit every
  reused lane's inverse and next gather; linear dependence alone is insufficient.
- Once a full word exists, compile its actual transitions and run its complete
  helper-bank, stock, pad and private-copy invoice. This probe supplies none
  of those all-size admission obligations.
