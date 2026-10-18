# Gaussian nonlinear message copy floor

**Scoped negative result; no new kappa or physical supplier.** On the 60
Gaussian E8 lines, fixed-support, deterministic, zero-error nonlinear block
messages obey

    C >= max(ceil((2/3) sum b_t), max_Q sum_(t in Q) b_t).

Here a q-bit message pays q times its Gaussian reader/source pairing rank,
additively across messages. This pricing is an explicit premise, not a proved
physical cost law for arbitrary nonlinear circuits. Receivers may use all
orthogonal input ports as free side information. For uniform b-bit demand,
the lower bound is **40b Gaussian / 80b rational units**. Direct messages cost
60b; the optimum remains unresolved. Demand confined to any nonorthogonal
clique has sharp cost sum b_t.

The [proof](PROOF.md) composes PR738's exact Gaussian certificate with the
conditional transcript argument of PR785/PR814. PR738 covers scalar binary
totals; PR785 and PR814 cover Hurwitz and Eisenstein geometries. This adds the
Gaussian block/nonlinear case. The methods and predecessor work are credited
in [NOTICE.md](NOTICE.md); no priority for the methods is claimed.

Only with the additional inherited Dfc accounting does the optimistic screen
become D/T <= 40b(s-3). Three stages cannot give positive deficit, even granting
zero helper, source-access, encoding, decoding, frame, restoration and extra
recursive costs. Five or more stages and different accounting remain open.
No supplier implementation, physical invoice or improved exponent is claimed.

## Reproduce

From the repository root, with **Python 3.10+ and the standard library**:

```sh
python3 -I -B research/gaussian-nonlinear-copy-floor/verify.py
python3 -I -B research/gaussian-nonlinear-copy-floor/test_package.py
```

Expected primary marker:

```text
PASS_GAUSSIAN_NONLINEAR_COPY_FLOOR lines=60 cliques=640 flat_pairs=2579856 floor=40b no_new_kappa
```

The verifier is offline and read-only by default. `--output NEW.json` writes a
verified receipt only to a new file. `--check-sources` checks immutable inputs
only and does **not** replay the theorem. Optimized Python (`-O`) is deliberately
rejected because the retained PR738 geometry uses assertions.

The driver hashes every retained input before import, calls PR738's unchanged
exact calculation and compares its complete certificate, checks every port's
128 clique incidences, and runs a separately implemented nonlinear truth-table
checker. Its own manifest binds today's selected source context; it does not
call the retained verifier's historical selected-record entry point.
All 2,579,856 nonempty flat pairs are covered. Closure and symmetry explain
why this covers every ordered support pair. The finite nonlinear checks cover
a three-parity Boolean shear on twelve active ports, all 4,096 inputs, every
receiver and every conditional clique transcript. Pricing and illegal side
information have correct-code boundary examples; omitted decoding work has
failure controls. Exact counts are in [CERTIFICATE.json](CERTIFICATE.json).

Package tests check zero, uniform and concentrated unequal demands on all five
maximal-clique sizes, invalid demands, receipt corruption, source tampering,
missing input, minimal relocated input closure and deliberate `-O` rejection.
[VALIDATION.md](VALIDATION.md) records actual execution and its limits.

## Pins and scope

- Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
- OS assignment seed44, structural decoder track; local [claim](CLAIM.json).
- Gaussian certificate PR738: `9671c5d72f3119ba26f3774f40aa7130c67bcf77`.
- Hurwitz method PR785: `83e78085ae9c110a34bff87e71387292d85e47c0`.
- Eisenstein composition PR814: `d91c5152b314391406b0ec792b6765a5cf0af2f1`.
- Exact immutable input SHA256/Git-blob pins: [SOURCES.json](SOURCES.json).

Fixed supports and widths, independent demands, deterministic zero-error
recovery, whole Gaussian-line pairing and additive per-bit pricing are essential.
Interactive/adaptive encoding, correlated demands, error, variable/average length,
sub-line supports, extra nonorthogonal side information and cheaper physical
coordinate sharing are excluded. No previously closed decoder search is reopened;
there is no candidate search or claim of decoder optimality.

The selected conditional kappa remains **1661634653669567/10^18**. Its
all-size/compiler, realization, hosting, precision/tape/exact-recovery and
analytic assumptions remain. Finite replay and the written argument are not
formal verification of the integer multiplication theorem. Only this research
package is added; existing files, the selected frontier and upstream/ stay intact.
