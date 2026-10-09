# Deferred readouts on both stopped networks

Conditional κ = 429239/5000000000 = **8.58478 × 10^-5** (+10.1% over PR #104's 7.79476 × 10^-5).

PR #104's stopped product-ring interchange compiles every projector residual of rank r as one child of width r.
Under that rule deferred readouts pay on both networks:

- **bit**: Swapnil Jain's round-seven deferred word (h = 23), unchanged, gives a stopped saving of 1.2402 × 10^-4;
- **complex**: PR #104's h = 24 network, with lifted binary frames and deferred readouts on 8,893 of its 44,918
  roles, gives 214657/2500000000 = 8.58628 × 10^-5, which is now the binding side.

See [PROOF.md](PROOF.md) for the construction, the checks and the inherited assumptions.

## Reproduce

From the repository root (standard-library Python 3; about two minutes):

```sh
python3 research/deferred-stopped/complex_deferred.py
python3 research/deferred-stopped/bit_round7.py DIR
python3 research/deferred-stopped/certificate.py
```

`DIR` holds Swapnil's two round-seven files, `witness_23.json.gz` and `deferred_23.json.gz`, for example
`certificates/round7/` of https://github.com/Swapnil-jain/integer-mult-kappa at commit
`741e7aa078392553815df7926ee17ac5e25a8c38`, or PR #97's copy in `research/deferred-signed/swapnil-round7/`.
`bit_round7.py` checks both files against their SHA-256 pins. The three scripts write `complex-profile.json`,
`bit-profile.json` and `certificate.json`.

## Files

| file | content |
|---|---|
| `complex_deferred.py` | complex DAG (PR #104 producer), matching, roles, lifted frames, deferral, replay and exact F2 checks |
| `bit_round7.py` | one-child bit profile of the round-seven deferred word |
| `certificate.py` | exact moments, stopped bit saving, finite bridge, 47-constraint assembly, κ |
| `*-profile.json`, `certificate.json` | generated outputs |
