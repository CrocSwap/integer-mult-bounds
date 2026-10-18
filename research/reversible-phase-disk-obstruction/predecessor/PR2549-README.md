# Precision and private-erasure debt in the corrected P104 dual

A scoped precision and lifecycle audit submitted for review. No supplier or new kappa is claimed.

[PR2497](https://github.com/CrocSwap/integer-mult-bounds/pull/2497), exact head
`7f2cf129d42030d3eb3975b7d1b07392c6d32a1b`, supplies a 4,982-event two-target
P104 backward word with eight private collectors restored to exact zero.
This package independently computes its signed error response at every cut.
It also exhibits a state-relative native defect that breaks zero-at-erasure.
This does not contradict the predecessor's exact theorem. Physical precision
and erasure were explicitly outside that theorem.

## Exact result

The norm is the maximum of individual register Hilbert norms. Each of the
358 arbitrary persistent inputs has norm at most B. Canonical native charts
and completed ideal transports are unitary. The main error model treats
signs and endpoint monomials as exact and permits independent defects after
all 3,104 ADDs and 1,654 native calls, for 4,758 sites.

| Quantity | Sharp independent-input/defect coefficient | First attaining completed-event cut |
| --- | ---: | --- |
| Ideal input prefix P | 127/2 | 3327, X12 |
| Unit absolute defects A | 4761/4 | 4772, X7 |
| Weighted defects K | 6039/4 | 4772, X7 |
| Native-only unit defects | 839/2 | 4772, X7 |

Weights are `1+abs(a)` for `dst += a src` and one for native calls. If the
208 sign operations also receive independent defects, there are 4,966 sites.
Then A is 4769/4 and K is 6047/4, both first attained at cut 4886 in X7.
P and the native-only coefficient do not change. Cuts count completed events;
individual event indices in the witnesses are zero-based.

The unchanged positive profile is
`1216H1 + 74H2 + 86H3 + 104H4 + 48H5 + 42H6 + 76H7 + 8H8`, rank mass 3,126.
Neither that local bill nor this error calculation supplies global owners,
idle/residual costs, the remaining 102 target corrections or a supplier moment.

### A conditional 17-bit feedback bound

Suppose each native output defect is at most `u*norm(actual input)` and each
ADD defect is at most `u*(norm(actual dst)+abs(a)*norm(actual src))`.
Allocation is exact zero. The perturbed execution must permit disposal of a
possibly nonzero private residual. Let M bound the actual individual register
norm at every cut, including private collectors. With exact signs and
`K*u < 1`, the signed response implies

```text
M <= (127/2)*B / (1 - (6039/4)*u)
max_cut_error <= (766953/8)*u*B / (1 - (6039/4)*u).
```

For each integer b at least zero, `u <= 2^(-b-17)` suffices for error at most
`B*2^-b` at every cut. Indeed `K*(P+1) = 779031/8 < 2^17`.
The sign-defective model also admits 17 bits, using `780063/8 < 2^17`.
Sixteen bits fail this sufficient inequality. This is not a lower bound on
actual rounding precision, and the feedback estimate need not be attained
by correlated arithmetic errors.

The disposal premise matters. These bounds do not implement a strict zero-only
erase or prove that such an execution can proceed past its first residual.

## Exact zero restoration does not survive arbitrary local defects

Each collector has n unchanged D gather sources, with n equal to 3, 4 or 5.
It gathers them at its line, climbs rank seven, updates Q, returns to its line,
then subtracts the same D values. In logical coordinates its pre-erasure
residual is exactly the sum of defects in its own `2n` scalar updates and two
native transports. Earlier D errors cancel, and the Q update has no feedback
into C. The independent symbolic and reverse checks verify this exact support
at all eight erasures.

Thus the sharp pre-erasure coefficients are `2n+2` for unit absolute defects,
`4n+2` for weighted defects, and two for native-only unit defects. In order,
the absolute coefficients are `12,10,8,10,10,10,8,12`; weighted coefficients
are `22,18,14,18,18,18,14,22`. Every exact input row at erasure is zero.

A concrete state-relative counterexample uses only the first collector:

```text
Initial D31 = v, norm(v)=1; all other logical inputs zero.
Before event 1825's rank-seven return, C has norm 1.
Inject the permitted return defect eta = v/1024, with u=1/1024.
Immediately before event 1831's erase, C = v/1024, not zero.
```

Under residual-tolerant disposal this particular return defect affects no
persistent output. A defect at the preceding climb, event 1823, also leaves
C nonzero and persists in Q7 and 52 source outputs. `RESULT.json` records
both exact impulse responses and the last inverse-gather impulse. Therefore
an error analysis for the exact word alone cannot admit its clean-storage
contract. A rounded implementation needs exact reversible cleanup, a justified
residual-tolerant disposal rule, or an explicit changed lifecycle and bill.

## Proof and replay

Conjugate each physical register and each new output defect by its actual
unitary chart. Transport preserves the logical value; ADD and sign are literal
rational row operations. Exact forward propagation keeps signs in all input
and defect rows. It takes absolute sums only when evaluating a norm. Examining
the updated register after each instruction covers every live register at every
cut, since unchanged rows retain their previous bounds.

A separately implemented reverse-functional recurrence checks all 358 complete
endpoint rows and every attaining row, plus all eight private residual rows.
It agrees on 70,231 nonzero endpoint input/error coefficients. Literal collinear
executions attain each reported independent-input/defect maximum. A further
execution injects nonzero rational defects at all 4,966 sites and checks every
persistent output. Frame containment, common ADD charts, exact private zeros
and the inverse-transpose endpoint matrix are also checked.

The certificate imports no predecessor executable, native compiler or
interpreter. Native correctness and normalization remain inherited premises
from the exact PR2497 realization. The full unchanged predecessor native replay
was run separately in a source-pinned local copy and passed, including its
12 controls. That replay is not part of this package's scalar replay hook.
PR2503's original uncorrected G/2-dual coefficients are not substituted here.

Standard-library Python 3.12 or later, from the repository root:

```sh
python3.12 -I -O -B research/p104-clean-dual-precision/verify.py
python3.12 -I -O -B research/p104-clean-dual-precision/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-clean-dual-precision
```

Default replay writes nothing and needs neither Git nor network. Byte-level
SHA256 and Git-blob pins authenticate inputs before mathematical execution.
`--write-result NEW_PATH` creates an independent receipt and refuses overwrite.
Controls reject omitted/wrong-sign cleanup, a missing return chart, an incorrect
source-sign boundary, source drift and a numerically equal but wrongly typed
receipt. The positive CLI control runs from a Git-free source export.
`RESULT.json` contains exact peak rows, private debts and a complete signed
updated-row stream hash.

Local checks used CPython 3.12.15 and 3.13.5 on Linux x86_64 under WSL2.
No hosted CI, proof assistant, human review, rounded recursive child, full
selected cold replay, all-size theorem or physical tape program is claimed.
Code/resource limits and managed-runtime deviations are in `CHECKS.md`.

## Sources and credit

Scientific base and entry fetch are canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
`WORD.json` is byte-identical to PR2497's `CLEAN-DUAL.json`, authenticated in
`PREDECESSOR.json`; it is not a new construction. `SOURCES.json` pins the
retained channel and root fixture. Original sources and selected records stay
unchanged.

Credit ywz65 / PR2497 for the complete zero-restored corrected word and
PR2503 for the original-dual precision precedent; Adam Gall / PR2096 for the
Hilbert-defect and feedback method; PR2458 for native two-target binding;
Ross Richardson / PR2445, commdata2338 / PR2393, Hiroki Kumazaki / PR2353,
Philippe Van Velzen, Chafik Boukhalfa / PR1991, Rohan Arun / PR1972,
Adam Gall / PR1940, Josie Elliston / PR1071, Ali Romman / PR1125 and PR1862,
icekylinx / PR531 and the retained geometry/compiler lineage. Predecessor notices
remain under `research/p104-native-channel/notices/`. New material is Apache-2.0.
No maintainer acceptance or supplier admission is claimed.

## Open next questions

1. Bind one actual rounded rank-seven return to the completed-output Hilbert
   contract, then test pre-erasure storage. This determines whether the exact
   cleanup can be implemented or needs a residual-tolerant lifecycle. Begin
   with the literal event 1825 witness. The blocker is physical arithmetic and
   disposal, not another scalar norm estimate.
2. Price a repaired collector lifecycle within the complete forward/backward
   interface. First state how private residue is handled and count every
   reset, cleanup, adapter and precision cost. Global hosting, the remaining
   target corrections and all-size admission are still missing.
