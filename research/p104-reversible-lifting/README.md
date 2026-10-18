# Reversible numerical cleanup for the first P104 collector

The first physical P104 collector can use a **nonlinear, same-grid integer
lifting transform with an exact paired inverse**. Its five arbitrary dirty
sources are unchanged and its private field returns to zero exactly, although
the query receives an approximate native transform. No rounding residues or
per-coordinate history are retained. The output grid and the original entrance
grid remain explicit parameters.

This supplies a changed numerical interface following Arham Tahir's
[PR2999 collision and history obstruction](https://github.com/CrocSwap/integer-mult-bounds/pull/2999),
head `ac6025235b6f1233291000d35a067198628569e9`. That obstruction remains valid
for its independently nearest-rounded map. Here we change the map itself.
Generic integer lifting and reversible rounded shears are established tools;
the contribution is their explicit binding, accuracy and cleanup contract,
and complete scalar-reference bill for this actual collector.

**This is a local numerical construction, not a fast recursive supplier or a
new kappa.** The return must execute the inverse of the *same* lifting program,
on the *retained* working grid. Applying the predecessor's independently
rounded inverse recipe does not implement this contract. The new map is not
linear; exact native/supplier identities cannot silently be applied to it.

## Pinned object and boundary

Base: `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
[SOURCES.json](SOURCES.json) authenticates every external input by SHA256 and
Git blob, before executing the old arithmetic used only as a negative control.
The source-native word is ywz65's PR2586 at
`7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`, retained by
[PR2665](../p104-rounded-collector/README.md). We bind zero-based events
2025–2039, including the two rank-seven calls at 2031 and 2033:

1. Allocate zero C and gather D31,D30,D29,D28,D27 into it.
2. Apply the outbound transport U, add C to Q7, apply the return V.
3. Subtract the original five sources in reverse order and erase zero C.

The exact ideal recipes have `V U = I`. All 512 complex basis columns check
this identity with integer numerators. A separate direct tensor-convolution
formula checks every outbound column. Those are checks of the **ideal linear**
recipes only. The lifting inverse theorem below supplies arbitrary-input
numerical restoration; it is not inferred from basis tests.

Admit five Gaussian-dyadic source arrays and one query array on a common
grid `2^-f`, `f>=0`, each of width N=512. Arrays are distinct; source access and
addition are exact. Integers do not overflow or saturate. Sources may have
arbitrary finite magnitude and may cancel. The local result is conditional
on the inherited interpretation of these native recipes and frames; it does
not establish physical hosting or execute the rest of the word.

## All-input pair identity

For Gaussian integers a,b, with componentwise floor `q(z)=floor(z/2)`, define

```
d = a - b
s = b + q(d)
d = i*d
b' = s - q(d)
a' = b' + d
```

This is four target-independent rounded/exact additive lifts and an exact
quarter turn. The inverse is the **same displayed program with `-i` in place
of `i`**. Indeed `a'-b'=i(a-b)` and `b'+q(a'-b')=s`; reverse rotation then
recovers d, b and a exactly. This proves a bijection of `Z[i]^2`, including
negative values and ties, without any residue history. It is a classical
state-map statement, not a claim about thermodynamically reversible hardware.

The ideal butterfly is

```
C(a,b) = ((a+b+i(a-b))/2, (a+b-i(a-b))/2).
```

Write `a-b=p+iq` and `t=(q mod 2)-(p mod 2)`. Both output discrepancies are
exactly `t(1-i)/2`. Thus their combined squared Hilbert error is `t^2<=1`,
attained whenever p and q have different parity. Scaling by the grid spacing
delta gives pair error at most delta. This parity formula also demonstrates
nonlinearity; the returned value carries the information which ordinary
rounding discarded, rather than hiding it in a separate transcript.

For N entries, a disjoint butterfly stage has error at most
`sqrt(N/2)*delta`. Each ideal stage and Gaussian monomial wrapper is unitary.
The usual telescoping perturbation argument therefore gives, after r stages,

```
|| U_lift(x) - U(x) ||_2 <= r*sqrt(N/2)*delta.
```

For N=512,r=7 this is `112*delta`. This uses the established unitary
perturbation argument credited to Nick Petalas/PR2771 and Arham Tahir/PR2891;
the changed local map has the same sufficient absolute bound. Reverse the
stage order, invert both monomial wrappers, and use the inverse pair to obtain
`U_lift^-1`. Nonlinear stages need not commute. Independent re-lowering of V
is deliberately excluded from the paired contract.

## Both relative contracts, exact private cleanup

Let S be the sum of the five source arrays, represented by Gaussian integer
numerators on grid f. If S is nonzero, let M be its maximum absolute integer
component, `h=floor(log2 M)-f`, and choose

```
F = max(f, b+8-h),       b >= 0.
```

For S=0 choose F=f. Embed S and the query exactly on grid F. The extra bit
relative to the predecessor's seven-bit guard reserves a margin for the
return's relative error. With `epsilon=2^(-b-1)`,

```
e = || U_lift(S)-U(S) || <= 112*2^-F <= epsilon*||S||.
```

Set y=U_lift(S). The paired inverse returns S exactly and, because V=U^-1
is unitary, its defect against the ideal return is *the same number*:

```
|| S - V(y) || = e,
||y|| >= (1-epsilon)*||S||,
e/||y|| <= epsilon/(1-epsilon) <= 2^-b.
```

The zero case is exact. Thus both completed native calls meet relative
Hilbert error `<=2^-b` **on this paired execution**. This is not a uniform
relative guarantee for every arbitrary inverse input at the same F.

The query is updated exactly by y and remains on grid F. The restored C is
exactly the original S, so its downshift from F to f is an exact division.
Subtracting the five unchanged sources leaves literal zero. No recovery scan
rounds a nonzero private residue to zero. Grid metadata F is retained with
the query; no uncharged final downcast is asserted. Given f,b and F, no other
input-dependent metadata is required. Since nonzero M>=1, `0<=F-f<=b+8`.

The control from PR2999 uses `A=2^(b+8)` and entrance numerators
`R^-1(A delta_0)` and `R^-1((A+1) delta_0)`, where R is U's right wrapper.
Both old and new policies use the same grid f. The old returned arrays
coincide; the new arrays differ by squared norm 1 and both restore exactly.
The predecessor's `2^256` collision family is likewise separated by the
proved bijection, without enumerating that family. The output remains
approximate; exact cleanup alone is not an exact Fourier computation.

## Complete local scalar bill and recurrence

The execution uses C plus constant pair scratch. Monomial wrappers run
in place: start each permutation cycle by swapping its first value with a
zero Gaussian scratch, rotate and swap along the cycle, and close the cycle
by swapping back into its zero first position. The scratch is then exactly
zero. Each wrapper needs N+c Gaussian swaps, N unit phases, where c is its
cycle count. Our four wrappers have total c=384: **2,432 swaps** and
**2,048 phase applications**. This is not a free address relabeling.

Let A(W), H(W), R(W) denote costs of a W-bit signed real add/subtract,
floor-half, and Gaussian quarter turn. Each pair uses 8 A + 4 H + R;
reading/writing its four real components is additional. The direct tensor
recurrence, excluding separately charged wrappers, is

```
P(N,0)=0,
P(N,r)=2 P(N/2,r-1) + (N/2)*(8 A(W)+4 H(W)+R(W)+pair I/O(W)),
P(N,r)=(r*N/2)*(8 A(W)+4 H(W)+R(W)+pair I/O(W)).
```

The full collector costs **2 P(N,7)**, four wrappers, five gathers, one
query addition, five ungathers, exact embedding/downshift, initialization,
magnitude/zero scans and plan setup. No recursive child, source access,
return or cleanup has been omitted or priced at a smaller-rank supplier rate.

| Logical operation, N=512 | Full collector count |
|---|---:|
| Paired butterflies | 3,584 |
| Signed real additions/subtractions (including gather/query/ungather) | 39,936 |
| Floor halvings | 14,336 |
| Butterfly quarter turns | 3,584 |
| Wrapper Gaussian swaps / phase applications | 2,432 / 2,048 |
| Source real-component reads (included in field-add I/O) | 10,240 |
| Embedding C/query components / exact C downshifts | 2,048 / 1,024 |
| Magnitude scan / zero scan / private initialization components | 1,024 each |
| Reference entrance type-validation component inspections | 6,144 |

[RESULT.json](RESULT.json) also records the operand I/O: four real reads and
writes per butterfly, four real reads/writes per Gaussian swap (including
scratch), and four reads/two writes per real-pair field update. The entrance
validation scan is charged separately from those arithmetic accesses. Subtotals such
as source reads are **not** added twice. Scalar floor divisions and phases
are counted separately from additions. Query storage grows to F; it is the
returned output, not an erased helper. No per-stage history arrays exist.
The Python verifier retains snapshots/defect scores solely as instrumentation;
they are unnecessary to the displayed executable schedule.

Wrapper plans are compiled from the exact nine-bit affine/quadratic records:
O(N*9^2) bit operations per plan, inverse/cycle tables O(N*9), and the
reference's bijection sort O(N log N) comparisons. At most four static plans
and cycle lists need O(N*9) address/phase bits up to a constant. They are
input-independent, explicitly retained recipe data. A single wrapper's
Gaussian scratch returns zero; pair temporaries are recomputable classical
scalar work, not retained numerical history.

For a conservative finite-width envelope, suppose every entrance component
has magnitude `<2^w`, w>=1, and write Delta=F-f. The gathered norm is at most
`5 sqrt(2N) 2^(w+Delta)`. The outbound prefixes add at most 112 in numerator
norm and return prefixes at most another 112, so at N=512 every such
component is below `272*2^(w+Delta)`.
The displayed pair's intermediates are at most five times that maximum.
**W=w+Delta+12 signed bits** therefore suffice for scalar data, intermediates,
query updates and cleanup. Precision/exponent metadata additionally needs
O(log(f+b+w+1)) bits. With linear fixed-width arithmetic and random access,
the whole direct reference has O(N*(r+1)*W + N*9^2) bit work plus table
validation. A sequential tape may pay additional routing; this is no
machine-step, allocator, owner-placement or physical tape tariff.

This bill is useful for rejecting an unjustified cheap implementation claim:
it performs every butterfly. A favorable whole-supplier moment, affordable
consumer, numerical error transfer through the full word and all-size
admission are unresolved. Existing fixed-profile consumer objections remain.
There is no justification here for expanding a dependent supplier search.

## Replay and limits

```
python3.12 -B scripts/research_package.py --package research/p104-reversible-lifting
```

Expected: `PASS_P104_REVERSIBLE_LIFTING`, eight behavioral groups, then
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`.

Local validation passed on Linux with registered CPython 3.12.14 and
optimized CPython 3.14.7 behavioral checks, including a read-only Git-free
export and deliberate failures. Hosted CI and independent review are separate.

The check covers 6,561 signed pairs; all 512 ideal complex basis columns;
15 sparse old-collision comparisons with b=0,1,8,64,256 and f=0,19,300;
14 six-array dense/cancellation fixtures, including 400-bit dirt and eight
nonzero-error cases. Domain, seed 53 and stopping rule are in
[TASK.json](TASK.json). There is no candidate search or extrapolated finite
proof. The all-input lifting and error statements are written arguments,
not formal-kernel proofs. Source/receipt corruption, wrong rotation, changed
native phase/occurrence, wrong reverse chronology, dirty wrapper scratch,
underprecision, nonexact downshift, broken cleanup and invoice controls are
included. The registered replay is bounded and works without Git in a
read-only export; all consumed sources are authenticated before execution.

## Open next questions

Can a viable consumer preserve this paired inverse contract and bound its
nonlinear query defects throughout the complete word? Start from one consumer
with a known allowance; propagate the error without assuming complex
linearity, and compare the complete implementation bill with that allowance.
An admitted fast implementation, legal physical access/hosting and a
favorable whole-supplier recurrence are blockers. Further precision-constant
tuning or repeating this local inverse would not resolve them.

## Credit and license

Tekalign, with substantial OpenAI Codex assistance in research, implementation,
mathematics, verification and writing. No independent human review is claimed.
New work is Apache-2.0 under the repository license.

Credit Arham Tahir/PR2999 for the collision and retained-history boundary,
PR2891 for the authenticated comparison kernel and prior numerical contract,
and PR2665 for the collector fixture; ywz65/PR2586 for the physical word and
native recipes and PR2730 for the exact-internal mixed-grid alternative;
Nick Petalas/PR2754 for exact internal execution and PR2771 for the unitary
perturbation/block-scale argument. The exact-grid alternative remains valid.
Credit ywz65/PR2555 (`ff522ee7f46d09c9ff8b00bf6fd11d5995f5523f`),
Chafik Boukhalfa/PR628 and their lineage for the distinct rounded-shear
restoration/full-grid boundary. Standard reversible lifting is not new here.
Retain commdata2338, Vasek/flyingviper, Ross Richardson, Rohan Arun,
Adam Gall, Josie Elliston, Ali Romman, icekylinx and the geometry/native/compiler
lineage in the pinned predecessor notices. Frozen source files are unchanged.
