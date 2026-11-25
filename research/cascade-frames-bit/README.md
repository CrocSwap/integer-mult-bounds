# Cascade-optimized frames on PR200's banked bit word

Under the retained multiplication interfaces, this finite witness certifies

$$
T(n)=O\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{683847872495777}{10^{18}}=0.000683847872495777 .
$$

That is **+0.0962%** over PR207 (`1366380910073/(2*10^15)` = 0.0006831904550365) and **+0.1152%** over PR205 (0.000683061299399923). The bit supplier still binds; PR193's complex saving `700918443859411/10^18` is unchanged.

| Construction | Unpacked bit coarse | Packed bit coarse | Conditional kappa |
|---|---:|---:|---:|
| PR205: PR200 word + completed banks | 6.77774e-4 | 6.835282e-4 | 0.000683061299399923 |
| PR207: 302 coordinated frames + banks | | | 0.0006831904550365 |
| **This: 6,191 cascade-optimized frames + banks** | **6.785484e-4** | **6.843158e-4** | **0.000683847872495777** |

## What is new

PR207 showed that PR200's operation frames are not optimal for the paid moment and admitted 302 rational frame changes. This package pushes the same lever much further with a different search.

**Exact chain model.** Every physical chain of PR200's word (donor + recipient splices, root frames, terminal full frame) is a sequence of slots. Each operation frame is shared by its destination and source chains. A frame is feasible when it contains the operation's value span, is G-nondegenerate, and is nested between its neighbours on both chains. The cost of a chain is the sum of `t*ln(72/t)` over its rank increments `t`, the first-order paid-moment weight.

**Cascading moves.** For an operation, try raising its frame to a later neighbour frame on either chain (up to four slots ahead), or to its global feasible maximum. Joining the new frame forward along every affected chain repairs nesting. Lowering mirrors this: meet backward down to the global feasible minimum. Root frames, gauge frames, start frames and alias endpoints stay fixed. A move is accepted on exact cost decrease. Single-operation moves stall almost at once; the cascades plus short annealing (T = 0.5, 1.0, 0.3) reach a deeper local optimum. Internal chain cost falls from 804,451.6 to 803,364.5 (−0.135%).

**Admission by PR200's own checkers.** Frames are the only change; 6,191 operations receive new rational bases (`opframe-bases.json`). PR200's modules re-check:

- every replacement frame for value span and nondegeneracy;
- all physical chain nestings and the 1,760 alias containments;
- the 34-sink terminal-modified word on all 1,760 source, 1,760 target and 17,114 dirty columns, over F2 and over the integers (residual bound 39,780, 24-bit packed digits);
- Gram/prime witnesses for all 24,611 used frames, each with residual factor below 2^80;
- the paid coarse and atom certificate.

The resulting unpacked coarse saving is `135709678471459/(2*10^17)`.

**Banks.** Same as PR205. Role counts, gauges and aliases are unchanged, so there are 45,842 banks, W = 56,402, deficit 5,808, maximum child 22, and at most 171 chart factors. The conservative selector-call bound is 5,368,513,266.

**Composition.** The finite ordinary-leaf recurrence uses three levels from the re-certified ordinary saving. It is followed by the balanced 47-constraint assembly with eta = beta = 10^-24. The next 10^-18 grid point fails.

## Reproduce

```sh
git -C <pr193> checkout 187e1010ac8b259af8e9b5166f68b64bc27b4b47
git -C <pr200> checkout a1175449f34d39ff933d9d8ab23ced1f32b290ec
python -B research/cascade-frames-bit/verify.py --complex-root <pr193> --bit-root <pr200> --full
```

The full run takes about 6 minutes on two cores. It re-runs PR193's complex verifier, re-admits every frame through PR200's exact checkers, rebuilds charts and banks, and reproduces `certificate.json` byte for byte. Without `--full`, it re-derives the arithmetic from the stored physical record.

## Scope

This is a conditional finite supplier certificate. It inherits, without proving, the same all-size compiler, the completed weighted/restored selector, routing, precision, the fixed analytic tape, and the finite bridge hypotheses as PR193/197/200/205/207. The frame search is a heuristic local optimum with no optimality claim. The search scripts are not needed for verification: only the frozen frame list is a mathematical input.

## Credits

- PR200 (Chafik Boukhalfa): word and checkers.
- PR193: complex supplier.
- PR197 (Evan McKinney): bank packing.
- PR185/187: finite composition.
- PR207 (Dugongue): first showed that frame re-optimization pays and how to admit frames through PR200's checkers.

Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
