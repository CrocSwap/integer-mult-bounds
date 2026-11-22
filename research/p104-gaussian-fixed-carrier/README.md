# Fixed-carrier Gaussian coupling for the retimed P104 multiplier

The candidate installs Gaussian price `1071523491/2^38` in the retimed signed multiplier of [#8052](https://github.com/CrocSwap/integer-mult-bounds/pull/8052) at `baaec65bf8e4c7e92be110a00d5b06522177931f`. The directed complete price at Gaussian height 20,000,000 is **κ = 0.0038981721342**. The binary heights are 60,000 and 960,000. The stopping denominator is 10^18 and the root uses 36 binary and 48 Gaussian calls.

The exact difference against #8052's reported κ = 0.003898171 is `5671/5000000000000`, or exactly `(5671/194908550)%` (approximately **+0.00002909569641762765%**). This exceeds the previous installed Gaussian ceiling by `242818712673/409600000000000000000`. On the same candidate budget, the former Gaussian price (2092819/2^{29}) fails by that exact amount. The old ceiling is the installed price less (39/(256H)) and five stopping-gap units.

The changed price enters actual transport construction. It changes 45 of the 54 routing shares. The scaled numerical word retains 105,216 productive and 564,144 paid labels. Every cell meets the same rank-descent, minimum-share, coefficient-width and finite-height bounds. The ordinary supplier and the 54 strict and four functional signed checks are evaluated with the new rate. The computed activation exponent is 21,020,646. The fixed setup, recurring clocks, storage, precision and conditional machine contracts follow the stock retimed installation under the same five inherited framework premises. The registered jobs check the constructive graph and negative control, cost and chronology, installation, physical binary and Gaussian suppliers, weighted receiver, stage tapes, and signed product. Production-size execution and independent formal verification of the inherited premises remain open.

## Replay

Use CPython 3.12 and Git from a clean checkout with the recorded base history.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-gaussian-fixed-carrier
python3.12 -IB scripts/research_package.py --package research/p104-gaussian-fixed-carrier-installation
```

Every replay mode authenticates and materializes the complete 48-file peer package from `peer8052.tar.gz`. [PEER-SOURCE.json](PEER-SOURCE.json) records its origin and file hashes by path. The predecessor notice and license are preserved in the archive. [RESULT.json](RESULT.json) records the exact recalculated prices and resource bounds. The selected record is outside this package.

## Open next questions

The raw Gaussian crossing lies between adjacent 50-bit dyadics around 0.003898180344795. A follow-up that moves this crossing should identify one exact native rewrite, rebuild the signed grade inventory and preserve controller ownership and restoration. Replay the unchanged raw supplier and its two-scale paid ledger before testing a rewrite.

## Credit

SYLforge supplied the seven-MOVE binary reduction and its full signed installation in [#8052](https://github.com/CrocSwap/integer-mult-bounds/pull/8052). Ali Romman supplied the unpowered two-scale Gaussian supplier and associated resource proof in [#8042](https://github.com/CrocSwap/integer-mult-bounds/pull/8042). Clear1nsight supplied retimed financing and directed cost precedent in [#8050](https://github.com/CrocSwap/integer-mult-bounds/pull/8050). The predecessor's archived NOTICE credits the inherited compiler, controllers and CI work. OpenAI Codex assisted the derivative and separation checks, implementation and replay.
