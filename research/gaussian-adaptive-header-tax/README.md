# A public routing header pays a Gaussian copy-cost penalty

The fixed-support nonlinear Gaussian bound in [PR888](https://github.com/CrocSwap/integer-mult-bounds/pull/888)
explicitly excludes adaptive supports and variable-length messages. We extend
its observation model to a paid public prefix-free header which selects the
payload supports and their prefix-free codes. Payload encoders and receivers
may be nonlinear. This is an expected-cost theorem under uniform independent
input demands, not a pointwise bound or a native supplier.

Write B = sum b_t, L = E[length of header], and H = entropy of the header.
Charge a header bit four Gaussian units (the full-space pairing rank), and
each payload bit its declared source/reader pairing rank. Then

    E[C] >= (2/3)B + 4L - (10/3)H >= (2/3)(B + L).

For every nonorthogonal clique Q there is also a concentration inequality:

    E[C] >= sum_(t in Q) b_t + 4L - H
         >= sum_(t in Q) b_t + 3L.

Equal b-bit demands retain the floor 40b and incur at least 2L/3 extra Gaussian
units when a nonempty public routing code is used. The entropy form charges
a useless constant header its full 4L. An empty constant header recovers the
existing bound. Expected charges need not be integers: no ceiling is applied.

The distinction from Jerry Chen's Hurwitz adaptive-routing argument is the
Gaussian geometry's strict gap: total weighted-clique weight 10/3 is less than
the full-space header rank 4. The entropy method is credited, not claimed new.
Variable prefix-free payloads are admitted as well as variable headers. The
precise model and all-width proof are in [PROOF.md](PROOF.md).

## Reproduce

Python3.12, standard library, from the repository root:

```
python3.12 -I -O -B research/gaussian-adaptive-header-tax/verify.py
python3.12 -B scripts/research_package.py --package research/gaussian-adaptive-header-tax
```

The replay checks exact SHA256/Git-blob source pins, runs PR738's unchanged
full geometry calculation in a separate assertion-enabled process, compares
its complete receipt, and checks all 640 weighted clique incidences. The child
ignores inherited PYTHONOPTIMIZE. No historical selected-result entry point
is used. The new actual-geometry fixture has 12 active independent bits, a
nonlinear AND header, adaptive payload supports and a variable-length prefix
payload. All 4096 inputs decode for all 12 receivers; every weighted clique's
conditional transcript injection is checked.

Separate rational elimination checks the fixture's source/reader prices.
Controls reject omitted payloads, undeclared sources, illegal side information,
uncharged headers and non-prefix payloads. The last is an actually decoded
orthogonal-frame parity using an empty/one-bit code: apparent expected cost 2
violates the 8/3 floor because termination is free. A valid variable header
costs 4 on the all-zero input, below expected floor 8, preventing a false
pointwise conclusion. These finite examples corroborate the written argument;
they do not prove the entropy theorem by enumeration.

Default replay is read-only and offline. `--write NEW.json` writes the verified
receipt exclusively to a new file. The registered input list is the complete
external replay closure. Source or receipt changes need explicit review.

## Limits and selection

The rank 4 tariff requires the header's declared source and reader spans to be
the full four-dimensional Gaussian space. Localized or private headers have
a different contract. Additive per-bit pairing pricing remains an explicit
premise, not a physical cost theorem for arbitrary nonlinear circuits. Every
input-dependent choice of payload count, order, supports or codebooks must
come from the paid header. Payloads do not relay other payloads. Correlated
inputs, errors, uncharged termination, private routing, interactive relays,
sub-line operations and changed physical pricing are outside scope.

Only with the additional inherited Gaussian Dfc stage identity does the
worst-case budget imply D/T <=40b(s-3) -(4s/3)L. A nonempty header therefore
makes the favorable three-stage screen strictly negative. This conditional
screen is not a completed construction or exponent improvement. No hosting,
all-size compilation, precision or whole multiplication theorem is admitted.

Fresh base 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2, priority 4, picker
822a27d6015294b31b90467ba9f189a5 selected complex mechanisms. The prescribed
P104 binding and complex-ceiling commands passed before this changed
helper-observation scope. P104 correction work was reserved by another worker.
The original ceiling is not applied to this different geometry. TASK.json
records the detour. The selected record is unchanged.

## Open next questions

Can localized paid headers beat this public-header penalty while preserving
a valid weighted transcript bound? Start with a single header whose source
and reader spans have rank below 4, and include every dependency of the payload
schedule. Receivers cannot obtain private schedule information for free.
The Gaussian nonlinear optimum between 40b and60b also remains open; this
result supplies no attaining 40b construction.

## Credit

Sagar Thakrar's PR738 supplies the Gaussian geometry and full flat-pair
certificate; ToikY's PR888 supplies its nonlinear transcript composition.
Alexander Templeton's PR785 and Michael Fischler's PR814 supply the underlying
conditional transcript method. Jerry Chen's Hurwitz adaptive-routing proof
supplies the paid-header entropy argument. Joel Pulikkan, Douglas Colkitt,
DreamingOfClouds and the retained lineage keep their original credit.
PR2607's adaptive affine Eisenstein theorem is distinct: these payload queries
may be nonlinear and use Gaussian costs.

Prepared by ywz65 with substantial OpenAI Codex assistance in proof, code,
verification and writing. Apache-2.0; no independent human review or proof
assistant verification is claimed.

## Revision5 expansion decision

Before submission, main advanced to b4560d9e7216f72b73c5aa940ac099c05e33ccf9.
The changed guidance and family record were read and the branch fast-forwarded;
scientific inputs retain their unchanged historical pins. Decision: narrow and
finish this interface obstruction, without a dependent implementation campaign.
The bound rules out public adaptive routing as a repair of this stated
three-stage budget even when all other nonnegative costs are omitted. Native
tariff realization, consumer/hosting and restoration remain unknown; favorable
local examples do not admit a complete supplier.
