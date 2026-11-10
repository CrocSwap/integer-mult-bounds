# Connected L18 root and emitted dyadic caller

This package constructs a connected, integral, rho=1 root with 38 roles, 39
rank-one units and 18 commuting stage masks. It emits a 2,370-event caller and
checks its exact operator on arbitrary inputs in
Q(i)[Q,D_0,...,D_17]/(Q^4-1). The result is
`Q diag(product of D_j over the role's mask)`.

The emitted caller invokes **18 explicitly specified HOST(t=-1) macros**; their
native implementation remains unbuilt. It does not certify a multiplier or
claim a new kappa. **No new κ.** All 181 idle
calls, three thin queries and 2,168 ordinary events are present. No same-label
idle fusion, clean scratch, discarded main plane or free native rescaling is
credited. `PROOF.md` gives the identities; `NATIVE.md` fixes the native obligation
and complete substitution equation.

The family includes an 8-role L3 instance and a 20-role L9 control. The L3
instance has the joint-mask dimensions retained by #6937. This extends that
mask pattern, not its literal rational parameter vectors. The L9 raw single
chain is byte-bound to #6936's retained type A root. The new L18 construction
joins both arms in one complete sign Gram; it is not six independent L3 copies
or the two-chain rho=2 source root.

| Instance | Roles | Units | HOST | IDLE_ONE | QUERY | Ordinary events |
|---|---:|---:|---:|---:|---:|---:|
| L3 | 8 | 9 | 3 | 6 | 3 | 179 |
| L9 | 20 | 21 | 9 | 52 | 3 | 712 |
| L18 | 38 | 39 | 18 | 181 | 3 | 2,168 |

For L18 the ordinary count is 1,041 ADD, 189 SCALE, 858 SWAP and 80 LAMBDA.
Every emitted rational scalar is dyadic, maximum absolute value 5/2. Primary
forward replay at Q=1,-1,i,-i retains every independent D variable; its
characterwise prefix coefficients have common denominator at most 2 and
maximum row l1 norm 83. These are caller measurements, not a native precision
certificate. Independent chronological majorants are retained separately.

The target histogram is
`H145 + H81 + 4H73 + 5H65 + 4H57 + 5H49 + 3H41 + 4H33 + 5H25 + 3H17 + 3H9`.
The paid work outside the native is `181H8 + 3H1`. At pending complex comparison
kappa 0.00362701882, each native call's signed paid-minus-helper cost per port
must be below **17.13134090285433**, before ordinary and outer margins.
The direct `2H8+2H1` baseline fails. These are conditional comparison gates,
not exponent certificates or admission of pending source assumptions.

Two scoped completion screens are included. Same-frame boundary remixing of
the retained two-plane native cannot supply this resonant endpoint. For the
fixed coordinate-role idle-merging model, even its exact optimum cannot repay
the F+H1 native deficit: maximum saving9.70728992518 versus required
10.08182803488 per port. Arbitrary noncoordinate idle directions, changed
roots and larger native rewrites remain open; see `NATIVE.md` and
`IDLE-COALESCING.md`.

From this package directory, run with Python 3.12 and the standard library:

```
python3 -I -B generate.py
python3 -I -B replay.py
python3 -I -B cost.py
python3 -I -B review.py
python3 -I -B independent.py --package . --out INDEPENDENT.json
python3 -I -B idle_coalescing.py --receipt IDLE-COALESCING.json
```

`generate.py` checks local input SHA256, regenerates each root and caller
without writing, compares the g=9 chain to the retained source, and checks both
retained L3 sector normalizations and joint masks. `--write` explicitly
regenerates output. `replay.py` checks all four Q characters and rejects deletion
of HOST, QUERY, IDLE_ONE, LAMBDA and ADD. Independent root, formal-ring caller
and tariff checks are registered in `VERIFY.json`. Registered commands are
read-only. Expected receipts are package-local.

Exports are authenticated by `INPUT-PINS.json`, including original commit/path
and SHA256. Catalogue and selected-record provenance is bound at main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a` in `SOURCES.json`. Replay requires no
unmerged source Git history.

## Open next questions

1. Can a physical native implement resonant HOST below its signed gate,
   including owned lifetimes, helper outputs, ordinary work and frame delivery?
   Start from `NATIVE.md`; a profitable native word is missing.
2. Can the 181 separate rank-eight idles be fused by an emitted legal caller?
   Start with a common carrier/basis schedule and replay it before pricing.
3. What raw scalar, LAMBDA, tape and width tariff supports caller, native and
   outer reduction? The dyadic caller removes one alphabet obstacle, but those
   framework and physical obligations remain.

Structured questions are in `TASK.json`. The five framework assumptions
(native_all_columns, owned_erasure, compiler, precision_tape, analytic_recovery)
are neither proved nor discharged. Pending per-port/HOST/LAMBDA/IDLE forms need
their own admission. No frontier changes.

Credit: DreamingOfClouds's #6937 data and #6842 sector normalization; #6936's
retained root and grammar, including @CubeJerry (Jerry Chen)'s #6912 type A root, Ali Romman's
helper mechanism, unpaidmoon's phase tests and icekylinx's grid. The complete
sign header and bare sector endpoint are prior mechanisms; the new contribution
is the connected eighteen-stage mask geometry and its emitted dyadic caller.
Substantial OpenAI Codex assistance; separate implementations supplied independent
checks. No human or maintainer review. Apache-2.0; see `NOTICE` and `REVIEW.json`.

From the repository root, the registered replay command is:

```
python3.12 -B scripts/research_package.py --package research/connected-l18-root-caller
```

Direct checks end with `PASS_ROOT_CALLER 18 2370`,
`PASS_FOUR_CHARACTER_CALLER`, `PASS_EMITTED_CENSUS` and
`PASS_INDEPENDENT_CONNECTED_ROOT`.

The source-bound window check in [COALESCING-WINDOW.md](COALESCING-WINDOW.md)
extends the fixed coordinate-role repair exclusion to every κ in
[0.00362701882, 0.01], using a uniformly negative derivative of its complete
signed moment. It does not exclude noncoordinate idle directions, different
natives or changed roots.
