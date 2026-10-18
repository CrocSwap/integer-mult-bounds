# Four fractional bits give exact local P104 collector cleanup

For the first physical collector in [Arham Tahir's PR2665](https://github.com/CrocSwap/integer-mult-bounds/pull/2665),
**four extra fractional bits are sufficient and necessary for all-input
strict-zero cleanup in the stated completed-output grid model**. The five
dirty sources and initial query lie on the coordinatewise complex grid
`h Z[i]`, where `h=2^-b` and `b>=0`. Retain the outbound collector and exact
query output on `(h/16) Z[i]`; return the collector on `h Z[i]`.
All five sources remain unchanged and private `C` erases exactly.

This answers the predecessor's explicit mixed-precision question for every
input at this one cut. PR2665 already gave the same-grid obstruction and a
four-bit positive control for one witness. Its result and native inputs are
retained unchanged and replayed. The new result is the all-input grid contract,
sharpness, an explicit precision/storage bill and an independent matrix check.
It does not establish an internally rounded recursive child or a full caller.

## Source and entrance contract

PR2665 is pinned at `f9e96e979b7630b7a70705c9774d00fc07014110`. Its word and
native archive come from ywz65's [PR2586](https://github.com/CrocSwap/integer-mult-bounds/pull/2586)
at `7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`. Use zero-based events
**2025 through 2039** in that 5,398-event physical word. The chart convention
is the source's `Delta_W=conjugate(Gamma_W)=Gamma_W^(-T)`.

The common source frame is `[256,136,64,40,16,4,2,1]`, of dimension eight;
the query frame is `[364]`, of dimension one. The checker tracks every frame
from the actual initial frame table through the 2,025 preceding events,
including common-frame ADDs and signs, to bind **all five** sources and `Q7`
to these current charts. It then binds both native recipes to their exact
events. The physical chart interpretation itself is inherited from PR2586;
this package does not rerun its entire Clifford compiler.

At this cut, every real and imaginary coordinate of each of
`D31,D30,D29,D28,D27,Q7` is an arbitrary integer multiple of `h`. Each register
contains 512 complex coordinates. The five `D` values may be independent,
nonzero and dirty; no relation between them is required. The `D` values are
read only. `Q7` is written once and never read by this local collector.

The literal program allocates zero `C`, gathers the five sources with coefficient
`+1`, applies `U` at event 2031, adds `C` to `Q7` with coefficient `+1`, applies
`V` at event 2033, subtracts the same five sources in reverse order with
coefficient `-1`, and erases `C`. ADD and Gaussian monomial operations are exact.
Each native transport is evaluated exactly internally, followed by one
componentwise nearest-even quantization: `U` uses spacing `h/16`, `V` uses `h`.
Integer range is unbounded unless the explicit range bound below is supplied.

This entrance-grid hypothesis is on the **physical values in these charts**.
It is not implied by an h-grid at the original caller entrance, by the symbolic
frame labels alone, or by any unverified rounded prefix.

## All-input proof

Write each native recipe as a Gaussian monomial, seven commuting binary
`C_e=((1+i)I+(1-i)X_e)/2` factors, and a Gaussian monomial. On a basis column,
the middle factor has 128 entries. If the input/output low-bit addresses differ
in `k` positions, its coefficient is

```
(1+i)^(7-k) (1-i)^k / 2^7 = (1-i) (-i)^k /16.
```

The monomials only permute coordinates and multiply them by powers of `i`.
Thus every nonzero entry of `U` and `V` has real and imaginary parts `+/-1/16`.
The exact recipes satisfy `VU=I`. The verifier checks this identity on all 512
columns with separate integer matrix multiplication; finite basis equality
proves the equality of these explicitly finite linear maps on arbitrary arrays.

Let `S=D31+D30+D29+D28+D27`. Exact unit gathers give `C=S` in `h Z[i]^512`.
Since every entry of `U` lies in `(1/16)Z[i]`, the entire `US` lies in
`(h/16)Z[i]^512`, so completed outbound quantization is the identity.
The one-way write gives `Q7'=Q7+US`, also on that fine grid, without modifying
`C`. The return receives **this actual `US`**, not an arbitrary fine-grid
vector. Consequently `VUS=S` lies on the coarse h-grid and completed return
quantization is also the identity. The five `-1` cleanup ADDs give `C=0`
exactly. There is no retained rounding history or residual to erase.

This is an algebraic proof for all integers, all `b>=0`, and all six entrance
arrays under the stated domain. Dense test cases illustrate the contract;
they are not the reason arbitrary dirty values are covered.

## Why four is sharp in this model

Keep the h-grid entrance domain and h-grid completed return, but use spacing
`h/2^g` on the outbound operation, for `g=0,1,2,3`. Set `D31=h delta_0` and
the other sources to zero. Every nonzero real/imaginary component of `U D31`
has magnitude `h/16`. For `g<3` it is below half a rounding interval; for
`g=3` it is exactly a tie between zero and the adjacent grid point, and
nearest-even selects zero. The outbound vector, query increment and return
are zero, so cleanup leaves `-h delta_0`. This proves the four-bit minimum
for this fixed quantizer/cleanup contract. It does not rule out other cleanup
algorithms, stored residues, different quantizers or restricted entrances.

The small witness need not satisfy PR2665's local relative-error inequality.
For a separate witness that does, take `D31=(1+h)delta_0`, `b>=5` and `g<=3`.
Let `z=U delta_0`; its norm is one. The components of `z` are even multiples
of the outbound interval (already true at `b=5,g=0`). The perturbation `hz`
rounds away, including the `g=3` ties. The outbound output is `z`, the return
is exactly `delta_0`, and cleanup again leaves `-h delta_0`. The outbound
defect has norm `h <= h(1+h)`, while the return defect is zero. This separates
all-input sharpness from an execution satisfying the old tolerance test.

## Complete local bill and consumer boundary

The unchanged fifteen-event local word costs two rank-seven children
(rank mass 14), eleven unit ADDs, one fresh-zero initialization and one
strict-zero erasure. There are no added child calls or history registers.

Relative to storing each real/imaginary component with b fractional bits,
the private 512-complex-coordinate buffer needs **4,096 additional fractional
storage bits** while holding `US`. The exact persistent query output also
needs **4,096 additional fractional storage bits**. These are separate
storage locations; neither is free. The five dirty sources need no additional
fractional precision for this local execution. The four-bit minimum is a
precision result, not a minimum over arbitrary compressed storage schemes.

For magnitude, suppose the absolute value of every real and imaginary
entrance component of all six registers is at most `B`. Gathers and cleanup
partial sums have components at most `5B`. Each U row has 128 nonzero entries,
with both real and imaginary coefficient magnitude `1/16`; hence components
of `US` are at most `128*(2*5B)/16=80B`. Query components are at most `81B`.
These are sufficient local range bounds, not minima. They price completed
values only: child-internal intermediates and their implementation are outside
the completed-output model. Sign bits, magnitude encoding, monomial/tape work
and physical placement still require an implementation bill.

A caller requiring a coarse h-grid query may round **only the one-way query
write**, without feeding it back into `C`. Cleanup remains exact, but the
promised query changes: its absolute Euclidean error is at most
`sqrt(1024)*(h/2)=16h`. That weaker endpoint is not the exact-query theorem
and has no claimed relative error or downstream admissibility. The verifier
includes a case where this output actually differs. An arbitrary `(h/16)`-grid
input to `V` also fails exact h-grid return; it is an explicit negative control.

## Reproduction and controls

Python 3.12 or later, standard library, no network or Git needed for replay:

```sh
python3.12 -I -O -B research/p104-mixed-grid-collector/verify.py
python3.12 -I -O -B research/p104-mixed-grid-collector/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-mixed-grid-collector
```

The independent column builder uses the closed expression above and its own
monomial parser, cross-checking all 1,024 U/V columns against the predecessor's
butterfly evaluator. Its separate matrix product checks all 512 inverse columns.
The predecessor's entire original receipt is replayed unchanged. Five dense
fixtures (`b=0,1,4,17,64`) populate every source and the dirty query; the literal
15 instructions are checked against an independently computed matrix sum.
The four insufficient guards and twelve scaled witnesses are retained.
Wrong cleanup sign and inverse phase fail, as do the excluded fine-grid return
and coarse-query exact endpoint. Source hashes and Git blob IDs are checked
before importing predecessor code; the complete receipt has recursive typed
equality and duplicate-key rejection. `--out NEW.json` refuses overwrite.

`test_verify.py` checks Git-free relocation, read-only replay, source corruption
before execution, integer/Boolean receipt substitutions, duplicate keys,
unknown CLI options, and occupied output. Its temporary files are separate
from committed artifacts. This is exact finite verification plus a written
all-input argument, not proof-assistant or independent human verification.

Author validation: the registered suite passed on CPython 3.12.14, and the
Git-free optimized integrity suite also passed on CPython 3.14.5. Separate
OpenAI Codex agents reviewed the proof, source binding and precision bill;
this is not independent human review or hosted-CI confirmation.

## Family decision and limits

**Narrow and finish this local mixed-grid closure.** It closes the specifically
excluded all-input cleanup question for one published collector under a changed,
priced entrance/output precision contract. It does not establish that a rounded
P104 prefix supplies those grids, that every later consumer preserves them,
or that exact internal native evaluation has an admitted recursive cost.
No full channel/correction/idle/owner invoice, remaining 102 corrections,
all-size compiler, selected-frontier improvement or new kappa is claimed.

## Open next questions

- Can an actual internal rounded implementation preserve this completed map?
  First price the intermediate dyadic grids for these two exact recipes and
  produce a uniform implementation; the output-only model does not supply it.
- Can the whole physical caller supply these entrance grids and accept the
  fine query output? Trace one real preceding source path and one succeeding
  query consumer, retaining precision and magnitude at every boundary. The
  missing obligations are global precision, native execution and hosting cost.

## Credit and freshness

The exact negative example, local instruction binding and native source bytes
are Arham Tahir's PR2665 result, with OpenAI Codex assistance, under Apache-2.0.
The physical dual is ywz65's PR2586. Its predecessors include PR2497's logical
dual, Nick Petalas's PR2549 precision/lifecycle question and PR2550 complementary
charts, and PR2551's physical boundary distinction. The retained predecessor
README preserves the complete P104/native lineage and contributor notices.
This package's derivation, checker and writing are prepared for ywz65 with
substantial OpenAI Codex assistance.

Base main `b97accd36a3e8ee0a11d008671f0b3950d27dca8`, priority revision 5.
The assigned `p104-side-correction` card's baseline command passed before this
local interface was selected. See TASK.json for the scope, bounded overlap
coverage and final refresh. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/pull/2665#issuecomment-6199396889).
