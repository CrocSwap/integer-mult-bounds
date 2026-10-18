# A single framed accumulator cannot serve all four late ports

## Statement

Fix one block interface in `research/complex-block-rank-optimum/CERTIFICATE.json`.
Let its eight independent read-only external inputs have frames
`F_1,...,F_8`, and let its four additive targets end at the distinct
rank-eight caps `H_1,...,H_4`. The required external-input contribution is the
four-by-eight rational matrix `Q` in the certificate. Every column of `Q` has
nonzero entries at exactly two distinct output ports.

Consider the following added resource and no other routing change: one extra
array `c` receives all eight external inputs and is the sole carrier of their
`Qz` contributions to the four targets. Its frame grows only by inclusion.
The existing helper values and `Ry` contributions may follow their retained
route, but no existing helper can become an alternate carrier of `Qz`. Inputs
are read-only; targets are additive and retain their certified final caps;
there is no direct input-to-target operation, second `Qz` accumulator, target
scratch, or frame descent.

For every one of the 12 selected-word blocks, and also for each of the 24
blocks in the two pinned PR1319 comparison words, this route is infeasible.
This is a fixed-interface obstruction. It does not rule out multiple
accumulators, direct source-to-target routes, earlier target access, or changed
caps.

## Proof

Put `S = F_1 + ... + F_8`. When `c` is updated from an input at frame `F_i`,
the common operation frame must contain both the current frame of `c` and
`F_i`. Monotonicity therefore leaves the connector frame containing every
input frame after all eight independent values have been read. In particular,
its frame `C` then contains `S`.

Choose the last external input whose value is first incorporated into `c`.
Its column of `Q` is nonzero at two distinct targets. Since that input is
independent and the one connector is the sole carrier, both target increments
still require a later operation that transfers information from `c`. For any
such operation on target `j`, the common frame contains `C`, and hence `S`.
The target frame also grows to that common frame. Because target frames only
grow and the final frame is `H_j`, a legal update must keep its common frame
inside `H_j`. Thus a necessary condition is `S ⊆ H_j`.

The certificate's exact binary spans give, for every block and every output
cap,

```text
dim(S + H_j) = 9,       dim(H_j) = 8.
```

So `S` is not contained in any `H_j`; every required connector-to-target
update would force the target to rank nine and violate its endpoint. This
contradicts the required nonzero two-port contribution of the last input.
The contradiction is independent of scalar coefficients and gate count.

The conclusion also holds if the connector reads inputs more than once or
changes its scalar value between reads: its frame cannot forget a frame it
has already visited. Reading the final independent input and writing through
the connector are distinct two-array operations, so the required target
update occurs after the connector contains `S`.

## Exact certificate check

`verify.py` recomputes ranks over the nine-dimensional binary frame space from
the pinned certificate. It checks all eight input frames contain the common
frame, all eight columns of `Q` have weight two, all four caps have rank eight,
and all 144 input-join/cap pairs force a rank-nine common frame. There are 12
selected blocks and 24 comparison blocks. In the selected blocks, the source
join has rank eight in bases 592 and 696 and rank nine in the other ten blocks;
the rank-eight joins still differ from every target cap.

The verifier also checks that its containment predicate accepts a synthetic
cap containing the source join and that it rejects a rank-mutated target cap.
The source certificate is pinned by SHA-256 and its predecessor's exact
source-bound verifier is run separately.

## Complete-cost screen and limits

There is no feasible completed cost for this one-connector route under the
stated endpoint contract. Charging source reads, the extra connector's
hosting/restoration children, output updates, precision or tape cannot repair
the frame contradiction; charging the necessary rank-nine target climb
violates the cap. The screen therefore stops before any scalar schedule or
recursive-moment search. No improvement to the selected paid moment or `kappa`
is claimed.

This does not bound a design with two or more accumulators, does not establish
a global lower bound for the complex supplier, and does not modify the
selected construction. It is a scoped negative result for one additional
monotone accumulator routing all eight external source columns through the
four retained late target caps.
