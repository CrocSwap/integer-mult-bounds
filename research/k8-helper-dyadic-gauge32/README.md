# Exact one-helper dyadic rescaling of the selected k8 word

The retained PR1094 k8 provider admits a complete scalar-word replacement that
saves **332 primitive operations per complex invocation in each orientation**,
using the stronger retained unit/copy-init lowering. Scale helper L427 by 1/4
at forward entry, conjugate its 123 incident ADD coefficients, and scale it by4
after full-frame cleanup. The backward word uses the reciprocal basis scale.
Both boundary scales are paid. Existing SCALEs remain where they were.

This is the exact optimum over **one of477 non-center helpers and every integer
power-of-two basis exponent**, with all other coordinates fixed. Helpers224,
240 and256 are excluded because they supply center COPYs; data registers are
outside the class.149 helpers have a strict improvement in each orientation.
The winning helper is cold, FULL-ended, and unwrapped. The477-helper optimum is
a formal scalar-cost class; only the materialized winner receives the complete
boundary-placement checks, and admission of every other rescaling is not claimed.
This scalar-program result does not update the selected construction or kappa.

| Lowering, real+imaginary total | Forward before | Forward after | Backward before | Backward after |
|---|---:|---:|---:|---:|
| Retained unit/copy-init |149002|148670|149018|148686|
| Original Horner |198766|198510|198814|198558|

The candidate has two extra scalar macros per orientation. Its paid climb and
center profile, all non-scalar events, frame identifiers, wrapper events, ports,
and helper inventory are unchanged. The complete positive scalar-prefix maximum
is unchanged: forward `2765345294379392599/1024` (52bits), backward
`14824960514781440791821/64` (68bits), both below the retained192-bit local cap.
This reports the maximum, not pointwise prefix domination.

Run from the repository root with Python3.14 standard library:

```text
python -I -O -B research/k8-helper-dyadic-gauge32/verify.py
python -I -O -B research/k8-helper-dyadic-gauge32/independent.py
python -I -O -B research/k8-helper-dyadic-gauge32/controls.py
```

The main replay compares every one of712 formal input columns (704 data/helper
plus8 arbitrary dirty center registers) for both original and candidate streams.
The independent checker imports the pinned predecessor lowerer, enumerates8774
integer/helper cases across both orientations, checks linear tails, and executes
893064 literal primitive steps on six exact dirty-input cases including arbitrary
coefficient work. Thirteen rejection controls and a unit-discount regression
exercise the stated boundaries. `--write` regenerates the certificate/program;
ordinary verification compares both artifacts without changing them.

`SOURCES.json` has an exact mandatory inventory. Frozen `BASE-SELECTED.json`
records base `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`, selected PR1094 with
kappa `836330098538459/500000000000000000`. The program, canonical word and local
receipts are read from the PR1042 archive and independently matched byte for byte
to the actual PR1094 archived provider. A future moving selected pointer does
not invalidate this frozen experiment.

The arbitrary-input scalar identity is exact. The proof explains commutation
with unchanged per-register linear frame operations. A native checker, complete
hosted/global precision invoice, provider registry integration and new assembly
were **not** run. No new kappa, all-size supplier admission, simultaneous-helper
optimum, or composition with other savings is claimed. See PROOF.md for the
unbounded-domain proof and PROVENANCE.md for credit and overlap boundaries.

@woklerx, substantial OpenAI Codex assistance. Apache-2.0; retained source notices
and upstream source files are unchanged.
