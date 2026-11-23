# Audit actual compiler cuts and cancel shared perturbations across intervals

This follow-up to #8093 completes a recovered source audit and adds one
relative-interval lemma. The actual rational FFT, parity, generator and full
compiler hierarchy retains its original four-way cut envelope at arbitrary
subsets of a matching layer. The argument uses exact bank unitarity and the
source's disjoint-support recursion, with explicit zero-duration atoms and
same-stored inverse coefficients.

For the retained ideal-downset bound `B`, fragment bound `H` and normalized
perturbation spend `theta<=1/4`, any stored interval and its inverse have norm
at most

```
B^2*H^2/(1-theta) < 2*B^2*H^2.
```

The predecessor's generic prefix-quotient bound is
`4*L0^2*B^2*H^2`. The reduction comes from a common legal linearization of two
nested completed downsets and one consecutive normalized error product. It
does not assume that approximate scalar or shear gates are unitary, or replace
an inverse with an adjoint.

For the unchanged direct-circulant word, the permitted original gate envelope
improves from `2^196*t^104` to `2^189*t^100`. The published production selector
is unchanged in this supplement. Its full error accounting remains valid, and
a further selector revision needs separate complete propagation and review.

The universal argument is in [PROOF.md](PROOF.md). `audit.py` executes retained
source factories with independent exact matrix and PSD oracles; its bounded
coverage is recorded in `EVIDENCE.json`. It runs offline with Python 3.12 and
the standard library:

```sh
python3 -I -W error -B audit.py
```

Expected marker: `PASS_SOURCE_ORDERED_FOUR_WAY_CUT_AUDIT`. The checker uses
explicit exceptions, so the same audit remains active with `-O`.

Brian/JoyboyBrian's #4755 has priority for the asynchronous cut factorization;
his #4976 supplies the generic interpolation theorem. Jose Manuel supplied
the full rational compiler and numerical hierarchy, with Vlado's recursive
construction and Chafik's certified phases. Nick Petalas's #4852 and Brian's
#4977 are retained as prospective sharpening references, not newly claimed
results. Ali Romman supplied the direct-circulant consumer. Complete source
pins are in `ORIGINS.json` and the original files/notices remain unchanged.

This is local numerical-interface progress with retained phase, rank,
conditioning, coefficient and native-service premises. No physical output
write/storage tariff, selected assumption removal or new kappa is claimed.
Prepared for Jerry Chen / `@CubeJerry` with substantial OpenAI assistance;
independent human or formal-kernel acceptance is not claimed.
