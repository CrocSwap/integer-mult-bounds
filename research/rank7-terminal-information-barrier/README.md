# A nonlinear recovery obstruction at every rank-seven endpoint

For the two PR2894 providers pinned by PR2918, **no endpoint of rank at most
seven permits exact recovery of any nonconstant function of the eligible
entrance state**. This remains true with arbitrary nonlinear decoding,
arbitrary recoding confined to eligible entrances, and arbitrary appended
processing whose complete data dependencies obey monotone frame inclusion.
All inputs retain the independent arbitrary-dirty contract. The word, entrance
cut, protected inputs and observation interface are fixed.

The entrance cut is immediately after the 84-event prelude. The separate
target-only center cut uses the inherited, checked `center_frames` convention;
this package does not reconstruct extra physical moves for its unspecified
frames. Output registers and frames in the suffix are fixed independently of
data, with all branch and control dependencies included.

This strengthens PR2918's one-helper, one-endpoint, scalar paired-boundary
obstruction. It concerns deterministic recovery for every input, not statistical
mutual information. [PROOF.md](PROOF.md) gives the complete theorem and limits.

## Exact evidence

Each provider has 520 live non-target registers and 226 eligible entrances.
We enumerate all **43,435** rank-seven subspaces of `GF(2)^9`, obtaining **239**
distinct complete terminal supports, of size at most 16. Every support has a
square purely scalar minor on protected input columns with determinant a unit
of `Z[1/2]`. The census covers all 58 eligible helper slots whose current terminal
frames have rank at most seven. Lower-rank endpoints follow by containment.

| Determinant | Support classes, per provider |
| --- | ---: |
| 1 | 157 |
| -1 | 34 |
| 1/2 | 11 |
| -1/2 | 17 |
| 1/4 | 8 |
| -1/4 | 12 |

The empty support has determinant one by convention. Each nonempty certificate
includes the entire terminal support, a representative annihilator, its endpoint
multiplicity, and the forbidden input columns. All nonempty operator coefficients
on the chosen blocks are zero. Thus these certificates remain valid under every
invertible linear specialization of the formal warps on every dyadic module.

The mathematical reason is simple. In `y=A h+B z`, protected inputs `z` can
produce every observation because `B` is invertible. Any eligible-input change
can be canceled by `z -> z+B^-1 A(h-h')`. No decoder can distinguish those
states. Monotone frame dependencies confine any output at endpoint `E` to the
already masked terminal support `R(E)`.

The known PR2908 rank-eight paired extraction passes both verification paths.
For every nonzero dyadic module, eight is the sharp endpoint threshold in this
frozen interface
when the permitted eligible-input preprocessing is included. This does not
assert that an output-only suffix can attain the threshold.

## Reproduction and verification scope

```sh
python3.12 scripts/research_package.py --package research/rank7-terminal-information-barrier
```

The two direct commands are:

```sh
python3.12 -I -O -B research/rank7-terminal-information-barrier/verify.py
python3.12 -I -O -B research/rank7-terminal-information-barrier/verify_independent.py
```

`verify.py` authenticates and directly executes PR2918's existing forward
operator/frame engine, then regenerates the census and checks the fixed
`certificates.json`. It checks both inverse products for every minor, eight
rejecting controls per provider, a row/column reordering control, and the
rank-eight construction. This path deliberately reuses the predecessor engine.

`verify_independent.py` imports no predecessor code. It parses the two source
providers, propagates 164 terminal covectors backward, enumerates endpoints by
two-row reduced echelon normal matrices, and verifies complete scalar minors
using fraction-free Bareiss determinants. It checks seven rejecting controls per
provider and separately reconstructs the rank-eight positive pairing by a row
pullback and inverse column. Its adjoint approach follows the credited PR2918
checker; the implementation and all-endpoint coverage are separate.

Both paths use exact rational arithmetic and explicit checks that remain active
under Python `-O`. This is finite exhaustive computational evidence plus a
written all-parameter argument. It is not a formal-kernel proof or independent
human review. Four authenticated predecessor files are live inputs, declared in
`VERIFY.json` and pinned by `SOURCES.json`; they are not duplicated here.

## Prior work and importance

PR2918 is pinned at `9360ba7312cf8961e672e9eb26c612719028d39d`; its sources bind
PR2908 at `51309592971e3b5be935599eed2a95404dc7781e` and PR2894 at
`18d03c447886895ef9abf888398178e0428533ca`.
[PR2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979), head
`be191346391661f4d35fc0d1508d0a6029572576`, already uses the all-43,435-endpoint
pairing screen on later words and reports a rank-seven positive example for
PR2917's changed word. We do not claim the enumeration technique or an
all-endpoint linear screen is new. The scoped strengthening here is the complete
unit-minor census on the old parent and its **nonlinear causal recovery
obstruction**, together with explicit side-information and repair requirements.
The underlying quotient and indistinguishability principles are standard.
No comprehensive literature novelty claim is made.

This excludes an entire family of endpoint/postprocessing repairs of the frozen
construction. It gives a necessary boundary for further design; it supplies no
new multiplication algorithm, improved kappa, paid recovery, owner allocation,
or native/outer theorem admission. A different middle word, additional retained
information, different entrance dependencies, a new warp reset, or a changed
observation contract can escape the theorem. Pooling observations from
incomparable low-rank endpoints is outside the single-common-endpoint result.

## Open next questions

The structured questions are in `TASK.json`. The useful next step is to identify
one paid change that destroys a certified nuisance block and then price the
entire resulting construction. A matrix-rank repair bound alone neither realizes
such a change nor proves it improves the complete recursive cost. Existing
changed-word rank-seven examples should be used as positive controls before
starting any further synthesis.

## Credit

Prepared for Ross Richardson with substantial OpenAI Codex assistance, including
separately assigned helper-boundaries, observation-kernels and exact-verification
specialists. PR2918 is Ross Richardson's scoped obstruction; Jeremy Diviney's
PR2908 supplies the rank-eight extraction, and Jeremy Kothe's PR2894 supplies the
parent words. Marius-Paul Dumitrean's PR2979 supplies the prior all-endpoint
screening comparison.
Earlier contributions and license notices remain in
`research/helper408-rank7-pairing/NOTICE.md` and its `sources/CREDITS.md`.
This package is under the repository's Apache-2.0 license. No new copies of
predecessor source files are vendored.
