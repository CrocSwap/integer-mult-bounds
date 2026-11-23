# Ordinary ancestor composition at the current retimed source

This supplement makes the ancestor charge explicit for PR #8042 at
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`. It follows the installed
`ordinary_carrier -> binary_receiver` path and keeps the current source's
binary owner/mass, local-work, header and fixed-tape premises explicit.

For a stage with `B` compiler owners, assume its binary bank capacity is at
most `beta B`. All twenty named heads, including historical compiler banks
and inherited pending/answer prefixes, satisfy

\[
 H_{named}\le
 \frac{(\beta+4)B+75/8}{B-1}W_{stage}.
\]

For the retained `beta=2` premise and production `B>=17`, the coefficient
is less than seven. This is independent of same-stage recursive depth and
sibling count. The generic small-rank `B=1` branch lacks this contraction;
its first weighted head can grow by another complete argument per level.

Let `A` bound the sum of the uniform coordinatewise envelopes for the
remaining transient work roles. Exclude the separately counted public
rectangle, five stage-root files and cold-interchange roles. At seven stages,
the historical sum of every ordinary role is bounded by

\[
 H_{ordinary}<(4196+254A)T<(37764+2286A)X,
\]

where `X` is the public unpadded binary slab volume and `T<9X` its ternary
rectangle. The source uses a fixed shape for all public prefix slabs; taking
their maximum also states the intended normalization explicitly. Earlier
stage work is charged in separate role sets. Borrowed parent input/output
intervals remain part of the parent charge. No scratch coefficient inflates
the true child argument.

The full proof, source role table and assumptions are in [PROOF.md](PROOF.md).
The [entry-history note](ENTRY-HISTORY.md) states its native-entry and
fresh-capacity boundary explicitly. Reused fixed heads require the per-role
grant `max(entry_capacity, new_peak)`; alternatively `X` must bound every
call in the reservation history under the same uniform envelopes.
This does not instantiate the unknown complete coefficient `A`, prove the
binary owner/mass premise from the Gaussian census, discharge any selected
assumption, or change kappa or an activation threshold.

## Reproduce

Requires Python 3.11 or newer and the standard library. The retained source
export needs no network, installation, production-rank execution or library.
From this directory:

```sh
python3 -B check.py --output /tmp/ordinary-ancestor-composition.json
python3 -B check_history.py --output /tmp/ordinary-entry-history.json
```

Expected marker: `PASS_SOURCE_BOUND_ORDINARY_ANCESTOR_COMPOSITION`.
The entry-history control separately returns `PASS_NATIVE_ENTRY_HISTORY_BOUNDARY`.
`SOURCE-BINDINGS.json` authenticates twenty-two exact resolved source files.
The checked proof and checker hashes are recorded with the result.

The caller checks execute source-extracted function bodies with independent
call-description and extent-only interpreters. They exercise 576 compiled
shapes, 576 direct empty lines, 1,152 direct wrappers, 1,728 covered children,
160 scalers with 1,016 preceding calls, and 96 root padding/return cases.
The physical checks run the actual page/packet-stack implementations on
in-memory streams and 32 cold interchanges against a direct-index oracle.
Exact controls reject an omitted low divisor, enlarged scaler tail,
nondecreasing predecessor stage and replacement of summed historical maxima
by a maximum instantaneous sum. The `B=1` boundary is symbolic, and the
allocator traces are role-bounded adversarial traces rather than a production
calendar. The written induction provides the all-depth statement.

## Open next questions

The next bounded task is to supply the uniform local work coefficients `a_r`
for every use of the remaining shared ordinary call-site heads, then add
them to `A`. Start with direct scaling and stopped weighted-pair helpers;
take a maximum across use shapes before summing fixed-role coefficients.
The reviewed type and wide-owner route envelopes can already contribute
`9+8/B`, with other uses of shared heads separately covered. This composition
proof then applies without reopening the ancestor argument.

The binary simultaneous-owner/mass premise is separate. The Gaussian census
does not establish it. Header/private-control, outer numerical storage and
complete fixed-tape movement remain separate source contracts as well.

Credit: Ali Romman and the retained source authors, together with the existing
packet and byte audit contributors. The coordinatewise historical accounting
in Hiroki Kumazaki's [#5286](https://github.com/CrocSwap/integer-mult-bounds/pull/5286)
and the nineteen modeled continuation tapes in
[#5404](https://github.com/CrocSwap/integer-mult-bounds/pull/5404) are credited
as prior work. Their contracts differ from the current source's twenty named
heads and actual production caller composition.
Prepared for Jerry Chen / @CubeJerry with
substantial OpenAI assistance. This is model-assisted written proof and finite
regression evidence, not formal-kernel or independent human admission.
Apache-2.0.
