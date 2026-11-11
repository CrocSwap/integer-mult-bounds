# Compose the chart-237 split with the complete chart-595 word

This is a new source-bound instance of Ali Romman's causal-history split.
The same recipe is used on a different, longer word. Neither parent's result
alone establishes composition: changing event order or role contacts can
invalidate a path, prefix coefficient, suffix guard, or resource limit.

The common parent is [#7145](https://github.com/CrocSwap/integer-mult-bounds/pull/7145)
at `db8f31c4a1d9e191976e2c92951e6d2dea886a27`. Start from dillona's completed
[#7148](https://github.com/CrocSwap/integer-mult-bounds/pull/7148) at
`154ef929894225674df48df2d6ea3b7a7d1f39a0`. Translate Rohan Arun's
[#7147](https://github.com/CrocSwap/integer-mult-bounds/pull/7147) recipe at
`3b61d41d81a4bc8f78252240c8fb02473dd3d94f`. The witness, paths and native word
in the latter are byte-identical to the initially inspected draft.

## Literal paths and guarded observations

Positions are zero-based cuts immediately before the numbered event. The
chart-237 helper belongs to the `3 → 127` group. Its pivot is role 1082.
Retirement moves from cut 36,813 on #7145 to 37,222 on #7148. Each of eight
neutral intervals and the one paid interval is identified on the new word
by its two consecutive scalar contacts and the literal MOVE between them.
A read of the role is a contact. The checker verifies the role renumbering
caused by the chart-595 insertion and requires exactly one match per bracket.
The paid path for role 820 now has its old MOVE at 45,971. Splitting
`734 → 127` at chart 237 changes rank 6 to ranks 1 and 5; its injection
is before its departure. The complete path boundaries are in PATHS.json
and CERTIFICATE.json. The productive split is rank 9 to ranks 4 and 5.

Write `P(t,r)` for the prefix row of role r at cut t, over all public input
coordinates. Write `S(t,r)` for its suffix response in all final public
and owned coordinates, augmented by one coordinate for the precondition
of each subsequent COPY. That coordinate records the perturbation to the
destination just before the overwrite. In the reverse pass, send the output
adjoint to the source with the COPY coefficient, then replace the destination
adjoint by the unit coordinate for that COPY guard. INIT and CLEAR reset
the appropriate row or adjoint. Chart and ownership checks are done on the
actual paths; coefficient replay uses normalized rows in their respective frames.

The exact new-word combinations are

```
c =  P(37222,794) + P(37216,1092)
  = -4 e229

d = -S(37754,795)/4 - S(45976,1095) - S(45461,878)/2
    + S(45973,820)/2 + S(37761,1082)/4 - S(46914,794)/4
  = -(e229 + e233 + e1082)/4 - e549/2.
```

Here e denotes a coordinate unit row or column as appropriate. All other
coordinates vanish, including those for interior COPY guards and final
owned fields. Both vectors lie in the same helper group and `c d = 1`.
For example, the negative control injects a perturbation that is invisible at
the final output because a COPY overwrites it, but whose interior guard
coordinate is nonzero. The two prefix observations precede or meet
retirement; all six injections follow it.

## Why this preserves the arbitrary-input endpoint

The retained exact basis constructor produces a matrix G whose pivot row
is c and for which `G d = e1082`. Apply G inverse at the entry chart, so the
gathered prefix combination is the original arbitrary pivot input x. Call the
new public input z, and let v be the current pivot value at retirement.
The credited two-buffer sequence moves v to the successor public role,
retires the pivot with x, and stores z−x in the second buffer. The remaining
source events run on the successor role. The six injections add precisely
`d (z−x)` in the source output coordinates, with zero change at the
interior COPY guards and final owned fields. Applying G at the exit chart
adds z−x to the successor coordinate, restores the other helper coordinates,
and returns z there. Both owned buffers are explicitly created and cleared.
The exact full forward and adjoint checks also test the emitted word directly.

The chart-595 change remains in the source; this construction does not revert
its four charged scalar refinements or rerun its normalization rule. Every
emitted ADD, COPY and SCALE numerator is checked against the existing 24-bit
contract. The new word adds 23 ADDs, 2 SCALEs, one MOVE, two INITs and two
CLEARs to #7148. The retiming is not a free paid path: the complete 17-stage
caller pays the new rank-1 and rank-5 positions and the added scalar and
owned-stock costs. See APPLICATION.md for both complete parent comparisons.
