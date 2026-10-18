# One ordinary-source tap repairs the QQ16 h witness

**New local interface mechanism; no full controller or κ claim.** On the exact
three-port ordinary-source witness from [PR #2093](https://github.com/CrocSwap/integer-mult-bounds/pull/2093), keep the sum-preserving
`X_T += X_A; Y_T -= X_A` shear from [PR #2216](https://github.com/CrocSwap/integer-mult-bounds/pull/2216) and add one paired tap at the shared `completed(0)` frame:

```text
X_21 <- X_21 + X_2
Y_21 <- Y_21 - X_2
```

This uses one already-live ordinary register (`U` port 2) and one existing
selected pair (`T` port 21). It adds no query, helper, recursive child or frame
transition. The paired operations preserve `X_21 + Y_21` and leave `X_2`
unchanged.

## Exact result

The pinned hidden witness is

```text
h_p(d) = c_p bit_0(d b_(p,0))
c_2 = -1, c_8 = 1, c_85 = 1; all other c_p = 0.
```

After F0 it is supported on ordinary ports 2, 8 and 85; all selected A/T
fields are zero. The existing A-to-T shear by itself still produces no selected
output through the retained tail. With the extra `U2 -> T21` tap, the exact
full-tail result contains 34 selected outputs, four forward-history values and
65 completed-X values. In final bank 0, component X, port 21 is exactly
`11 f_37`; at the identity owner its value is 11. This is a concrete selected
endpoint that distinguishes the witness from the zero input.

The tap also preserves PR #2216's eight-direction B1 result: the pinned
post-B1 T-output family remains rank eight, with exact minor determinant
`-1/4096`. This check ends at B1; those eight directions have not been replayed
through the remaining tail here.

The search uses the witness support to reduce the one-port/one-T-pair domain to
3 × 8 = 24 nontrivial taps. All 24 were visible at B1. The first tested tap,
`U2 -> T21`, survived the complete retained tail, so the search stopped there.
The other 23 full tails were not run.

## Cost and scope

The added tap costs exactly **2 scalar additions per owner**. Its coefficients
are `+1` and `-1`, so it adds no coefficient precision. By the triangle bound,
charge up to a factor of two in the two changed field envelopes (one extra
magnitude bit) at this local interface. The source is read in the common
`completed(0)` frame and is not changed. No dirty helper is introduced.

This establishes one exact kernel-witness repair, not full injectivity. Global
precision, controller coverage, owner placement, restoration outside this
local state change, all-size admission and the complete recursive moment remain
open. The selected record and κ are unchanged.

## Reproduce

From the repository root:

```sh
python3 -I -B research/qq16-ordinary-source-tap-seed3794b3/verify.py
python3 scripts/research_package.py --package research/qq16-ordinary-source-tap-seed3794b3 --check-only
```

The first command authenticates the selected archive and both pinned
predecessor verifiers, checks the no-tap and wrong-source controls, replays the
whole retained tail, compares the complete exact output receipt, and runs the
eight-direction B1 control. The package runner is registered for Python 3.12;
local direct checks use the available Python runtime and are reported
separately from hosted CI.

## Provenance and coordination

Scientific base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; selected-record
SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
The exact predecessor heads and copied verifier hashes are in
[SOURCES.json](SOURCES.json). The selected QQ16 maps and witness are pinned
from the base commit; the two unmerged predecessor verifiers are retained under
`references/` for reproducible comparison.

Cycle 30 seed: `3794b3df6e4fb4a017103a787d6f6b32`, track
`recursive-interfaces`, priority revision 4, task `joint-query-controller`
(refined). The live overlap refresh at 2026-10-15 02:18 UTC covered 482 open
PRs and 960 Discussion records with complete pagination and no warnings; the
exact one-port ordinary-source-tap terms had no direct match. The claim and
handoff are in [Discussion #2205](https://github.com/CrocSwap/integer-mult-bounds/discussions/2205#discussioncomment-18938845).

## Open next questions

- Does the one-bit local envelope fit the complete QQ16 precision and all-size
  contracts?
- Do the eight PR #2216 directions remain visible through the retained tail
  after the new tap?
- Can the full ordered kernel be made injective with this and other priced
  existing-field changes?

## Credit

PR #1969 supplies the retained QQ16 maps and local words. PR #2093 supplies the
three-port hidden h witness and its exact tail. PR #2216 supplies the existing
A-to-T shear and eight-direction B1 certificate. PR #2079 supplies the earlier
ordinary-source observation context. New mechanism, integration and replay:
Cinna Davis with substantial OpenAI Codex assistance. No independent human
review is claimed. Apache-2.0.

## Maintainer integration note (2026-10-15)

The predecessor task catalogue is authenticated at its original Git commit;
its subsequent priority changes do not alter this mathematical replay. All live
computational inputs of the B1 subcheck are declared for replay selection and
remain hash-bound. The subprocess budget is 540 seconds inside a 600-second
package budget to accommodate slower hosts; no checked equation or receipt
field changes. The initial maintainer run reached the former 180-second B1
limit and is retained separately from the completed replay.
