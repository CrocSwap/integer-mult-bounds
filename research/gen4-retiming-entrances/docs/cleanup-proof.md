# Early restoration of 440 gen4 helpers

The source word is the literal `retimed880/COHORT249-RECORDS.bin`, SHA256
`2d22a9530f0b04a7a794d15077459234ef52183d6e7a70f813cfa849b79f2ebe`.
This construction composes with its880 source-partner frame retimings.
It changes no scalar coefficient and adds no scalar gate.

At record662145, the first category3 cleanup ADD, all1,760 data targets
already have their required scalar endpoints. There are440 helper roles a
with the following properties, checked against the complete remaining word:

* The only later scalar incidence of a is `a -= b`.
* The donor b is never written between the cut and that incidence.
* All440 destinations and440 donors are distinct, with the two sets disjoint.
* Both roles have current frame dimension22. Their rational span is a
  nondegenerate frame E of dimension23.
* Helper a has entrance dimension20 and previously ended at FULL, dimension24.

The ADD `a -= b` commutes over the integers with every intervening scalar
gate. Moving it to the cut therefore preserves the exact signed scalar
operator, including all dirty columns. There is no COPY/ERASE after this cut.
These440 moves can be made simultaneously because their destinations and
donors do not overlap. The original maximum formal coefficient bound does
not increase: early-restored a has exactly its old value after the later
restoration, while every other role has the same value at every unaffected
event. No gate reads a on the crossed interval.

For each pair, advance a and b from their rank22 frames to E, perform the
unchanged `a -= b`, and retire a at E. Continue every remaining scalar gate
in its original order and at its original frame. The donor later reaches
FULL. Every new connector is checked by exact rational annihilator products;
all other source, target, helper, and COPY endpoints remain unchanged.

Per pair, two old rank2 climbs become three rank1 climbs: a→E, b→E, and
b:E→FULL. Hence the local histogram change is exactly

    ΔH[1] = +1320, ΔH[2] = -880.

The local paid rank drops440. The helper endpoint changes from
`D_(FULL-sigma)` of rank4 to `D_(E-sigma)` of rank3. Its reflected inverse
goes from `I-E` to `I-sigma` and has the same residual rank3. The ordinary
completed-bank construction must be repacked for these actual residuals;
the old FULL-endpoint assumption may not be silently retained.

With PR276's60 local replicas, each stage loses26,400 residual coordinates,
or220 complete width120 banks. This is only the volume calculation: an exact
block assignment and normalizer/selector invoice are separate required
admission checks. The resulting five-stage literal stock drop is1,100 and
the normalized stock drop220 if that tiling closes.

`cleanup_emit.py` freshly checks every new frame's full annihilator, exact cleared
Gram determinant and nonvanishing modulo the retained prime2^127−1. It
replays all19,930 formal columns forward, backward with fresh copies in
place of reversed erasures, and as a complete roundtrip. Omitting one moved
restoration fails one formal row. It also independently checks the integer
commutation conditions above. The complete global five-stage, bank, chart,
and recurrence checks remain the caller's responsibility.

The final all440 output word SHA256 is
`8dfff69cc400256746443089817175a3345ac096c924957ef04b32c038964373`.
The438-helper precursor is preserved separately; the all440 word is the
intended final candidate under the60-replica normalization.


## Portable reproduction

Run from the package root with Python3 and SymPy (validated with SymPy1.14):

```sh
python code/cleanup.py --source-dir RETIMED --export-dir EXPORT --output CANDIDATE
```

`RETIMED` is the preceding880-retiming output. `EXPORT` contains the source
`gen4-states.json` and `frames.json`. The fixed recipe freshly reconstructs
all440 helper/donor pairs; it rejects a changed input word, changed candidate
count/geometry, or changed emitted word hash. It preserves the source's COPY
lifetimes and signed coefficients. No network access, NumPy, SciPy, or native
compiler is needed for this cleanup step. Global verification remains in the
package verifier.

The rational basis utilities in `cleanup_reference.py` are derived from
[PR271's sandwich263.py](https://github.com/CrocSwap/integer-mult-bounds/pull/271).
This gen4 construction uses a single cleanup gate per retired helper rather
than PR271's three-gate sandwich selection.
