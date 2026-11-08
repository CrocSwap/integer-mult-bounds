# An exact FFT scalar owner for the synchronized Full caller

The published Full global caller used exact Karatsuba products at every
width. Its diagonal cost was subordinate to the retained H service only
when the grouping exponent exceeded approximately .586. This package adds
an explicit, source-bound `FftWord` owner to the same physical Full stages.
The complete scalar and radius term becomes
`O((D+1)V log^2(p+2))`, removing that Karatsuba grouping threshold under the
same stated source-width and native-H premises. **No new κ.**

The exact fast word multiplier already exists in
CrocSwap/integer-mult-bounds#3787. The new result is its actual integration
with the synchronized source-emitted Full program: one authenticated tape
cohort, all nested private owners, full-width signed returns, protected
output consumption and the complete cost/space consequences. The old
Karatsuba-only constructor remains unchanged. Eight execution methods are
literally inherited from the pinned Full implementation; the new class
declares its own constructor and stronger nested-child idle condition.

## Result and dependencies

For every legal invocation satisfying the explicitly retained Full and
child-runtime contracts, every scalar return, rounded suffix/data value
and final output is the same as in the published Full execution. The
global coefficient precision and data roundings are unchanged. The
source preparation, complete H bill, all-stage controls, constructor work,
source preparation peak and retained blank backing remain separately paid.

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The exact source and proof pins are in SOURCES.json and VENDOR.json.
The executed Full source is the published
[@CubeJerry Full caller](https://github.com/CubeJerry/integer-mult-bounds/tree/d51859e7816771f627033b23db0f9786ada863f8/research/full-global-tensor-caller).
Only the files used by this composition are retained byte-identically.
The independently reviewed
[normalized-product refinement](https://github.com/CubeJerry/integer-mult-bounds/tree/85e0534b3a86dc0237f368ff0e5fb646fe4744ec/research/normalized-product-source-refinement)
addresses the inherited CrocSwap/integer-mult-bounds#3709 numerical source premise. It retains exact
integer/ownership premises and is not a formal proof-kernel certificate.

PROOF.md gives the complete replacement argument, actual owner inventory,
precision compatibility and invoice. The condition
`beta*.99827101 > log2(3)-1` is removed for the stated growing-group family;
the complete sum is retained for constant or slowly growing groups. This
does not admit an actual outer Gaussian/CRT cohort, establish the selected
native tariff, or prove a complete sub-n-log-n multiplication theorem.

## Reproduce

From the repository root with Python 3.12 and its standard library:

```sh
python3 -B scripts/research_package.py --package research/full-fft-scalar-join
```

Expected marker: `PASS_FULL_FFT_SCALAR_JOIN`.
The normal and optimized commands compare the complete typed RESULT.json,
excluding only the three elapsed-time measurements. Verification neither
rewrites nor silently regenerates the receipt; `--emit` is explicit author
receipt creation. RECEIPT.json records executed commands, source hashes and
their measured outcomes.

The complete source fixture retains F407/W608, 21 physical stages and the
actual stored inverse of `(2+i)I_2`. The fixed **production cutoff is 4096**,
so all 92 scalar calls in this fixture use FftWord's retained base branch.
No source precision is reduced to make the run affordable. The H child is
the credited standard q2 finite native fixture; this does not execute a
complete production GL64 payload.

A separate small invocation of the exact inherited Full complex-product
method uses fixed **fixture cutoff 2** and width 3. All four real products
execute the actual FFT branch; negative components and two nonzero final
component truncations are checked. The complete normalized-product child
runs without injected numerical results or payload decoding. Observer-on
and observer-erased runs must have the same output and physical tape
read/write/move totals.

Controls reject forged warm modules, a representative alias from each of
the five nested scalar pools, aliases with all five child outputs, and
unconsumed scalar/global returns.
The legal Full invocation after the child-output rejection demonstrates
reuse at that specific boundary. Arbitrary interrupted-child recovery is
not claimed. The two fixture scopes are kept distinct in RESULT.json.

## Scope and remaining obligations

This composition inherits CrocSwap/integer-mult-bounds#3787's exact radix/carry theorem and complete
unamortized FFT setup, the independently audited CrocSwap/integer-mult-bounds#3709 numerical target,
exact Count/WordProduct primitives and successful child ownership contracts.
The RingProduct's internal multiplier remains WordProduct, so the dependency
is acyclic. The retained H's native, stock, word-margin, physical tariff and
global-domain clauses remain separate. Finite agreement is not a universal
proof of those inherited clauses.

The cold source boundary derives the complete nested archive module-name
inventory and checks actual imported source bytes. It does not defend
against concurrent mutation during a verifier run. The implementation uses
fixed owners and encoded unbounded loop state; retained emulator statistics
remain the predecessor's separate observation layer.

## Open next questions

1. Can one actual outer cohort satisfy this Full producer's domain, precision,
   preparation and global H grouping requirements? Start from its actual
   matrices and complete grouping invoice, not an optimized scalar alone.
2. Can the all-stage control program be replaced by a charged sequential
   producer when constant-axis storage matters? Its source generation,
   rounding, disposal and retained backing must all be priced.
3. Which remaining native semantic or word-margin implication can be proved
   independently in the exact retained H source? The scalar join leaves
   those premises explicit. TASK.json records first steps and blockers.

## Credit

Prepared for **@CubeJerry**, with substantial OpenAI Codex assistance in
mathematics, source analysis, implementation, independent checks and writing.
Separate AI review is not independent human or formal-kernel acceptance.

Credit Jose Manuel/jmbarrancoml for CrocSwap/integer-mult-bounds#3709, CrocSwap/integer-mult-bounds#3787 and the physical source
lineage; the previous @CubeJerry Full and numerical-refinement packages for
their source compiler, owner and independent audit; Vlado Vojdanovski for
the fixed-H compiler; and the original FFT/Karatsuba, interval, tape and
Gaussian authors retained in the source notices. CrocSwap/integer-mult-bounds#5110 supplies the known
all-width setup bound, CrocSwap/integer-mult-bounds#3808 and CrocSwap/integer-mult-bounds#6252 the existing carry analyses, and
CrocSwap/integer-mult-bounds#3935 an earlier Gaussian application. CrocSwap/integer-mult-bounds#6024's outer reversal result is
distinct. No original notice or frozen predecessor is modified.
