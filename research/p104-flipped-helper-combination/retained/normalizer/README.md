# Lower global LAMBDA normalizers to paid ordinary passes

**Scoped all-width implementation and source-bound cost proof. No new κ.**

The two-chain proposal CrocSwap/integer-mult-bounds#6902 asks whether its
global `LAMBDA` gates may be ordinary work. Charging each as a rank-one
Gaussian child would destroy its positive rank surplus. This package gives
an explicit alternative: one initialized scratch bank, one inherited
monomial translation, a Gaussian-dyadic pair combination, then a clear.
Every use is charged separately. The macro has no recursive Gaussian child
and no productive output credit.

At every positive width `f`,

\[
\Lambda_{s,f}=\frac{1+si}{2}I+
              \frac{1-si}{2}(C_q^{\otimes f})^2
            =\frac{1+si}{2}I+
              \frac{1-si}{2}X_q^{\otimes f}.
\]

The translation uses the fixed `NOT` record list of #5445. This is not the
tensor product of the width-one normalizers. The convention is credited to
#6726/#6763/#6735; the new result is its explicit ordinary lowering, scratch
and numerical contract, and the complete source-specific allowance check.

## Exact result

For #6902 at `e4d42607f24d7a049b0fca329dc4c34882405c25`:

| Item | Exact count |
| --- | ---: |
| Caller events / roles / ports | 2492 / 40 / 104 |
| Normalizer events | 124 |
| Separately charged translation passes | 12,896 |
| Extra route charge at the source's 1000-unit allowance | 12,896,000 |
| Expanded actual caller charge | 16,671,616 |
| Existing caller envelope | 331,735,040 |
| Reviewed complete raw bound, freshly reconstructed | 971,071,328 |
| Conservative total adding every route again | 983,967,328 |
| Remaining margin below 10^9 | 16,032,672 |
| New owned slots / paid Gaussian calls / target credits | 0 / 0 / 0 |
| Peak live owned fields | 30, unchanged |

The reserved query scratch is reused only between completed caller macros,
with all ports processed sequentially. Dirty-copy residuals remain in the
numerical error bound `E_out ≤ 2E+D+R`; a subsequent clear does not erase
their contribution. The source's local height allowance remains sufficient.

`1000` is a finite route-accounting constant, not a physical tape step count.
The retained movement tariff, complete control fields, owned resets,
precision/storage and compiler premises remain explicit. No fixed-tape
primitive or complete multiplication theorem is proved here. The owned
ascent assumption of #6902 is not addressed by this package.

## Reproduction

Python 3.12, standard library:

```sh
python3 -B scripts/research_package.py --package research/global-lambda-lowering
```

Expected: `PASS_GLOBAL_LAMBDA_LOWERING`,
`PASS_INDEPENDENT_GLOBAL_LAMBDA` in normal and optimized Python, followed by
`PASS_REGISTERED_RESEARCH_PACKAGE`. `RESULT.json` records exact deterministic
coverage and counts. `PROOF.md` contains the all-width argument and complete
limitations; `RETAINED.json` pins every unmodified source byte.

The code-disjoint checker uses Fourier-character inversion and rational real
pair matrices. The same research agent wrote both implementations; the lead
researcher separately reviewed the mathematics and source contracts. The
checker imports no primary or predecessor scientific code. Controls
detect the wrong tensor convention, a single-column route, wrong orientation,
omitted clear, discarded numerical residuals, corrupted retained bytes,
mismatched Git-blob pins, redirected source symlinks and missing inputs.
These finite tests support
the written scoped theorem; they are not a proof of the full multiplier.

## Open next questions

Connect this fixed record list to a fully authenticated physical translation
and owned-reset implementation at the actual compiled caller. A first step
is to discharge the retained movement and complete-control reservations for
the expanded program. This matters for the remaining physical assumptions;
no such discharge or rounded full-program execution is claimed here.

## Provenance and credit

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Selected κ remains
0.003125804. The source proposal #6902 is open and not promoted or admitted.
All original instructions, selected records and predecessor packages remain
unchanged.

Prepared for **@CubeJerry**, with substantial **OpenAI Codex assistance** and
separate algebraic checking. Credit DreamingOfClouds (#6902/#6833), zxv
(#6726), the #6763 physical review, the #6735 even-normalizer audit,
Matarener (#5445), and their retained native, compiler and movement authors.
Apache-2.0; no independent human or proof-kernel acceptance claimed.
