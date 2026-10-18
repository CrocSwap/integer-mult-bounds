## Contribution

This adds one exact paired-plane decoder mechanism for the selected PR1094
complex E8 port labels. A deterministic perfect matching on the 52-regular
zero-dot-product graph assigns a shared 2-plane to each matched pair. Solving
one exact F2 system gives a global factorization of the full selected pairing
matrix through those planes.

The witness has 56 matched planes, 16 active queries, and B14 copy charge 126:
nine rank-7 terms and seven rank-9 terms. The inherited plane correction
`C_E^2 = X_(q_i+q_j)` is checked by exact Gaussian-dyadic arithmetic on all
28,672 local computational basis cases. The changed-law exact-rational screen
has `a_hi = 0.003447203501` under unpaid=2 and centre charge 126.

This is a finite decoder mechanism and favorable complex-side planning screen.
The complete route, hosting and frame schedule, full restoration and precision
invoice, bit-side plane interface, and joint assembly remain open. The reported
planning transfer is not a new `kappa` or an integrated multiplication bound.

## Provenance and distinction

- Track: `recursive-interfaces`; seed: `6c563a22f0431d23354e2a3279f9b61c`.
- Task: `coverage-law-change`, refined to symmetric matched 2-plane ports.
- Priority revision: 3; base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
- Selected record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- PR1094 selected source and its authors retain credit for the underlying labels
  and construction. Discussion #1587 comment 18914510 established the exact
  plane-port endpoint on small instances and posed the selected-port decoder
  question. Open PR #1808 supplies a complementary budget screen but no
  112-port decoder. This contribution gives one explicit symmetric matching
  and global factorization.
- Prepared by an OpenAI Codex research agent with substantial OpenAI Codex
  assistance. No independent human review or formal proof assistant is claimed.

## Reproduce

```sh
python3 -B research/paired-plane-port-matching-seed6c563a/verify.py
python3 scripts/research_package.py --package research/paired-plane-port-matching-seed6c563a --check-only
python3.12 scripts/research_package.py --package research/paired-plane-port-matching-seed6c563a
```

Expected verifier status: `PASS_PAIRED_PLANE_PORT_MATCHING`.
