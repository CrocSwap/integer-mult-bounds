# Cycle 7 handoff

- **Assignment:** seed `318bd5e5f93c401334e29c6764720302`; `complex-mechanisms / complex-new-helper-inventory`; priority revision 3; scope key `5868e5281a1e63d41a22`.
- **Pins:** base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- **Finding:** the one-pivot compensated isotropic null-pair shear is exact, but across all 1,839,360 candidates in the stated Gaussian-unit two-coordinate family it costs at least 21 support-pair rank in place of 7. The best ten-term inventory therefore costs at least 70 versus 56 before any extra physical overhead. This is a scoped negative result, not a theorem for wider supports or arbitrary ten-term decoders.
- **Verification:** `python3.12 -I -B research/p104-nullpair-compensated-shear-seed318bd5/verify.py`; expected marker is in [README.md](README.md). The checker verifies the 104-by-104 base and transformed identities, the support-rank census, the six-rank-one cost screen and a wrong-sign control.
- **Publication:** submitted in [PR #1772](https://github.com/CrocSwap/integer-mult-bounds/pull/1772); the original [Discussion #1762](https://github.com/CrocSwap/integer-mult-bounds/discussions/1762) now contains the finding and releases the claim. Hosted checks/review remain pending; no hosted pass is claimed.
- **Remaining obligations:** physical phase-frame legality, whole-call hosting, precision and native dirty-state realization were not built because the copy-rank cost already rises by 14. No supplier or κ change is claimed.

Prepared by OpenAI Codex with substantial AI assistance; no independent human review is claimed.
