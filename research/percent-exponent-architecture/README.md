# Architecture screens for kappa = 0.01

This package identifies structural costs that exclude a saving of 0.01 in
specified continuations of the current construction, and tests a different
small-network route. **It establishes no new multiplication exponent.**

The target is the saving in `n (log n)^(1-kappa)`, not a measured runtime
improvement. All inherited all-size and analytic assumptions remain in place.

## Checked results

| Scope | Result |
| --- | --- |
| Keep PR193's complex data calls; grant every auxiliary call and all center loss for free | `a < 0.008866683` |
| Keep PR187's bit data calls under the same relaxation | `a < 0.008897440` |
| Proposed odd-dimensional paired cubes, copied t-star centers and the retained data flags | `a < 0.005164`, all odd dimensions in the stated domain |
| Same odd-cube family, allowing arbitrary local data chains of the required endpoint distance | `a < 0.008094` |
| Paired triples, p>=5, exactly h independent copied centers | Center loss is at least `h(h-2)`; the current stars attain it |
| General finite bit contract with a common triangular frame flag | `s >= Wm`; no rank deficit |
| All 87 chronological balanced-Fano stub reuses, all local GL(2,F2) gates, any full output permutation | Every completed scalar permutation is routable; no rational-frame deficit in any dimension |

Here `a` is an ordinary supplier saving; the retained assembly has `kappa<a`.
Every bound has a stated interface. These are not impossibility results for
integer multiplication, new center implementations, cross-stage fusion,
overcomplete center factors, arbitrary label families or different recurrences.

The first two rows follow from the paid-moment inequality `a C < D`, applied
only to data children. The center-basis result explains why changing the
linear basis of a rank-minimal center factor cannot reduce the current
triple loss. The odd-cube screen includes an exact finite calculation and
an analytic infinite tail. The Fano screen changes the graph before scalar
synthesis and keeps all initial inputs independent.

See [PROOF.md](PROOF.md) for the arguments, assumptions and open directions.
The exact inputs and arithmetic are in [ceiling-certificate.json](ceiling-certificate.json)
and [center-basis-certificate.json](center-basis-certificate.json).
[fano-all-permutations.json](fano-all-permutations.json) records the full
finite search; [fano-reuse-certificate.json](fano-reuse-certificate.json)
independently replays the 16 cases preserving the original three demands.

## Reproduce

Python 3.11+ and a C++17 compiler are sufficient. No network or Python package
installation is needed for the exact verifier.

```sh
python3 -B -S research/percent-exponent-architecture/verify.py --deep
```

The default verifier checks the immutable package sources, regenerates the
data and family ceilings, tests the sharp center bound, runs adverse controls,
and exhausts all scalar permutations on all 87 topologies. It compares the
C++ matching algorithm with direct full-word enumeration on eight small
cases. `--deep` additionally regenerates the independent Python half-searches
for all 16 prescribed-terminal cases. Verification uses a temporary build
directory and leaves the package unchanged. `--write` is authoring mode.

## Separate vector-code experiments

`discovery/vector_fano.py` allows each edge to carry k bits and each local
vertex to use an arbitrary binary 2k-by-2k map. The final transfer must be a
permutation on every independent input bit; this forces all local maps to
be invertible. No clean workspace or appended decoder is supplied.

With Z3 5.1.0.0, all 16 retained-obstruction cases returned `unsat` for k=2
without a basis restriction, and for k=3,4 when internal edge bases were
put in reduced row-echelon form.
Those receipts are optional discovery evidence, not independent UNSAT
certificates and not a theorem for larger blocks. Unnormalized runs include
timeouts, which remain explicitly recorded as `unknown`.

```sh
python3 -m pip install z3-solver==5.1.0.0
python3 research/percent-exponent-architecture/discovery/vector_fano.py \
  --block 3 --canonical-edges --timeout-ms 30000
```

No vector result is used to prove any ceiling or scalar exclusion above.

## A concrete budget for a different construction

In the raw uniform bit recurrence, a *hypothetical* complete network with
`m=3`, `W=30` and one rank unit of deficit would have ordinary saving
greater than `0.010170376`, above the balanced assembly's necessary `1/99`
threshold. At W=31, one rank unit no longer suffices. These inequalities are
checked with rational logs in the certificate.

This is a useful small-network search target, not an achieved supplier.
It still requires the all-input scalar permutation, a nonroutable topology,
exact rational frames and endpoint checks, a sufficiently strong complex
companion, and the full finite bridge and assembly. The tested Fano family
does not provide it.

Original sources, licenses and assistance disclosures are preserved in
[NOTICE](NOTICE), the input provenance and [references/SOURCE.json](references/SOURCE.json).
