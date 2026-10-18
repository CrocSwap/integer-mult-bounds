# T16 packing moments: 63 uniform orders and three genuine crossings

**Adversarial audit; no new construction or kappa.** Among the 66 unordered
pairs of the twelve accepted same-word T16 packing profiles in batch1099,
63 have the same strict moment ordering throughout `0<a<1`. Three pairs
actually reverse order. This is a complete classification of these named
pairs, not a search over owner maps or all possible profiles.

The new evidence applies the predecessor majorization argument to the entire
retained packing batch, supplies exact crossings from accepted constructions,
and resolves the sole remaining incomparable pair by a short exponential
tangent certificate. It does not discover majorization, challenge the selected
endpoint, or repair/repeat the root-bracketing audit in pending PR1182.

## Exact domain and result

Base: `dd6403f774a0891093a006ae9716c02e371b1fdb`. The selected result at that
base is PR1094, conditional `kappa=0.001672660197076918`, with PR589 on PR555
on the bit side. Its construction review is
[`community-batch1099-review.md`](../../docs/research/community-batch1099-review.md).

The twelve profiles are PRs **1050, 1053, 1055, 1056, 1061, 1063, 1065,
1068, 1074, 1082, 1087, 1094**. They have ambient dimension `m=73`, live
stock `W=14336`, rank mass `1041408`, deficit `5120`, and 144 copies of
the same local word. Only idle-remainder profiles differ. The native complex
moment has no surcharge. Charged precision, row coefficient and bit-supplier
identity agree. These facts are read from the frozen replay archives, checked
against each other and bound by SHA256; their construction admission is reused.

For each pair, `new` denotes the larger **recorded lower endpoint**, not PR
number order; PR1063 precedes PR1061 in this ordering. Let

```
Delta(a) = sum_r (n_new[r] - n_old[r]) * r**(1-a).
```

The normalized moment difference is the same-sign quantity
`73**(a-1) * Delta(a) / 14336`. Negative means the larger-endpoint profile
has the smaller bill. Exactly four pairs fail the sufficient majorization
test:

| Old → new | Delta rank histogram | At a=1/650 | At a=1/2 | At a=64/65 | Complete conclusion |
| --- | --- | --- | --- | --- | --- |
| 1050 → 1053 | `{1:+7,3:-3,7:-2,16:+1}` | negative | positive | positive | genuine crossing |
| 1053 → 1055 | `{1:-7,3:-4,7:+5,16:-1}` | negative | negative | negative | negative for every `0<a<1`, by tangent proof below |
| 1074 → 1087 | `{1:+6,2:-1,3:-6,7:+2}` | negative | negative | positive | genuine crossing |
| 1082 → 1087 | `{1:+6,3:-5,5:-1,7:+2}` | negative | positive | positive | genuine crossing |

All other 62 pairs have strict majorization certificates. In particular,
the selected PR1094 profile strictly improves the native moment of every
other profile here for all `0<a<1`. None of these comparisons changes a
recorded root or proves a new physical construction.

The three crossing statements follow from strict signs and continuity. We
do **not** claim the crossing locations, number of crossings, or a maximal
interval around the admitted endpoints. The points `1/650` and `64/65`
diversify this seed-65 audit; they are not purported certified supplier roots.

## Two whole-interval certificates

### Truncated rank / zero-padded majorization

For equal rank mass, put `C(t)=sum_r Delta_n[r]*min(r,t)`. This is piecewise
linear, so checking the union of rank knots, including zero, determines its
sign everywhere. It is zero above the largest rank. If `C(t)<=0` at every
knot and the two positive-rank histograms differ, then strict concavity of
`r**p`, `0<p<1`, gives `sum Delta_n[r]*r**p<0`.

For completeness, one direct justification is

```
r**p = r*p*R**(p-1) + p*(1-p)*integral_0^R min(r,t)*t**(p-2) dt,
```

for `0<=r<=R`. The common mass cancels the linear term. The integral is
finite at zero, its weight is positive, and a nonzero nonpositive continuous
`C` is strictly negative on an interval. This proves the strict conclusion.

The code also independently checks the equivalent inequalities for sums of
the largest `k` entries in the two rank multisets, padded with zeros to equal
length. No materialized half-million-entry array is needed. Small tests
compare this sparse implementation with literal expanded multisets.

This is the existing concavity/stop-loss argument in
[`gauge44-slots-t16/hosting/PROOF.md`, §§4–5](../gauge44-slots-t16/hosting/PROOF.md).
That predecessor establishes local greedy-update guarantees; the present
audit tests all 66 global profile pairs. Failure of majorization is
**inconclusive**, not proof of a moment crossing.

### The one pair majorization misses

For PR1053 → PR1055 set `p=1-a` and

```
F(p) = 5*7**p - 7 - 4*3**p - 16**p,
G(p) = F(p)/7**p = 5 - 7*(1/7)**p - 4*(3/7)**p - (16/7)**p.
```

`G` is strictly concave on the real line, because its second derivative is
a sum of strictly negative exponential terms. Equal rank mass gives
`G(1)=0`, while

```
G'(1) = log(7**35 / (3**12 * 16**16)) / 7 > 0.
```

The final inequality is checked by an exact integer comparison, with no
numerical logarithms. Concavity places `G(p)` below its tangent at one:
`G(p)<=G'(1)*(p-1)<0` for every `p<1`. This proves the missing whole-interval
order. It is an elementary certificate, not a claimed new general theorem.

The reusable checker admits this certificate only when the histogram
difference has exactly one positive rank, equal total mass, and the correct
strict integer-product inequality. Reversing that inequality is unsafe:
the maintainer's PR1048 fixture `{1:-14,2:+15,4:-4}` passes neither this
certificate nor universal ordering and has explicitly checked opposite
moment signs. That fixture and its attribution are retained as a control.

## Reproduction and coverage

From the repository root, with Python 3.12 or later and no third-party packages:

```sh
python3 -B scripts/research_package.py --package research/t16-moment-order-audit
```

Expected result: `PASS_T16_MOMENT_ORDER_AUDIT`, **63 uniform orders, three
certified crossings, 17 rejected input/contract controls, and five passing
tests**. The command checks source/provenance pins and the registered commands.
The direct verifier takes about a quarter of a second on the development
host; timings are not performance claims.

[`EVIDENCE.json`](EVIDENCE.json) contains all 66 differences and knot
certificates, the one tangent certificate, and exact rational intervals for
each of the four initially incomparable pairs at all three exponents.
For `a=u/v`, interval bounds are obtained by finding integers `L,U` satisfying
`L**v <= r**(v-u)*2**(40*v) <= U**v`; exact power comparisons certify every
enclosure. Signed interval propagation respects negative coefficients.
No existing moment engine, floating-point power, logarithm or bisection
root estimate is imported.

Tests cover all **1,191 equal-mass pairs** of positive rank multisets on
`1..6` with one to four children, exact rational-power enclosures, both real
crossing directions and the non-majorization tangent case. Controls reject
changed ambient dimension, live stock, surcharge mode, local word, call
count, charged precision, row coefficient, bit source, invalid ranks/counts,
unequal mass and excluded exponents. Equality is never reported as strict.
All rejection logic works with optimized Python (`-O`) as well.

To regenerate this package's receipt intentionally:

```sh
python3 -B research/t16-moment-order-audit/verify.py --write research/t16-moment-order-audit/EVIDENCE.json
```

The verifier reads archives in place and never extracts or rewrites predecessor
files. Immutable archive bytes are pinned; selected decompressed member
digests are also reported. Nothing here regenerates a compressed container.

## Scope, provenance and prior work

[`SOURCES.json`](SOURCES.json) records exact base, Git blobs and SHA256 hashes.
Each profile's original reviewed PR head and three archive-member digests
appear in the receipt. Historical selected-record and catalogue bytes are
Git provenance; subsequent frontier selection does not change this domain.

The source-bound profile, owner and assembly receipts are **reused evidence**.
We do not rerun local/native circuits, reconstruct physical ownership, prove
exact root brackets, discharge the outer analytic inequalities, or remove
the all-size/compiler, common-label/mutable-source, hosting, precision/tape
and bit H1–H5 assumptions. The all-a comparisons concern the native complex
moment with the stated common contract. Changed overheads or a conservative
surcharge need a separate comparison. Universal moment order alone does not
establish physical feasibility.

This follows the deferred PR1048 warning that an arbitrary fixed-exponent
score does not order roots, but adds actual accepted-profile evidence and a
complete finite-domain classification. PR1182 separately audits false
root brackets; its code and fixtures are not reused. The current reviewed
bound is not contradicted by crossings away from its admitted endpoint.

Credit: Jeremy Kothe's PR1050/1053/1055/1061/1065/1068/1074/1087 packing,
Rohan Arun's PR1056/1063/1082/1094 packing and slot work, Hao Yan's T16
controller, icekylinx's concavity/majorization hosting argument, Josie
Elliston's retained owner audit, Sagar Thakrar's retained pricing audits,
Douglas Colkitt's integration review and PR1048 counterexample, and the
preserved local supplier and PR589/555 bit ancestry. The predecessor notices
and licenses remain unchanged.

Contribution by **mightyOil**, with substantial **OpenAI Codex, GPT-6 Astra**
assistance in task selection, mathematical derivation, implementation,
verification, documentation and packaging. Apache-2.0 applies.

## Open next questions

1. Can the three crossing pairs be certified to retain their favorable order
   throughout one common small-a interval containing the admitted roots?
   Start with interval bounds on the exponential derivatives, with explicit
   endpoints. This would support safe local search pruning; the present
   point witnesses do not prove interval-wide order or crossing uniqueness.
2. Can the single-positive tangent certificate safely accelerate a named
   owner-search acceptance loop? First log how often it applies to that
   loop's feasible equal-mass proposals, then compare all accepted/rejected
   decisions with its existing exact endpoint engine. Different surcharges
   and changes to the physical interface must be priced before integration.

Structured scope, OS seed, stop rule and next steps are in [`TASK.json`](TASK.json).
