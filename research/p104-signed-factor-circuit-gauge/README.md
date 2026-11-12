# Certify signed Type A factor circuits and gauge

This package studies the exact 38-factor normalized Type A relative word from [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d` against [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace`. Unselected relative factors retain their chronology. The exact tests use 36 roles and central signs +1 and −1. **NO VERIFIED GAIN.**

- With all bodies unit, two exact methods find minimum rank-dependent support 19, with two ties. The lexicographic choice has rank-18 displacement and is an involution. Its shortest rational transvection length is 19.
- Add the other leg of J1 to that choice. The new residual has rank 19 and an exact 19-factor witness. Any 19-factor realization crosses the fixed gathered 18+18 coordinate split in every factor. The witness uses dyadic entries. This is a normalized construction, with no native supplier.
- For the legal profile D8 = −1 and every other body unit, the same 20-factor residual is conjugated by a diagonal sign gauge on zero-based roles 9–17 and 27–35. Both literal engines agree on all 36 columns and rank 19. Conjugating the actual 19-factor witness also reproduces the complete residual.

The literal 17-host direct rebuild loses more than 680.3199 raw before extra routing. The optimistic one-host quote is about +50.33412118538 raw, conditional on reusing the other 16 embedded hosts with their existing contracts. [Proof and invoice](PROOF.md).

From a clean POSIX checkout with CPython 3.12:

```sh
python3.12 -I -B research/p104-signed-factor-circuit-gauge/replay.py
```

The standard-library replay authenticates the bundled engines and exact receipts by path, runs both literal engines and independently multiplies the actual gauged factor witness. It requires no network, local cache, or user-specific paths. [Verification](VERIFICATION.md).

## Open next questions

Test one candidate direction in the actual frame of a reused J host. Require its image and covector to lie inside the old body projector, cross-annihilate the unchanged mate, and have a legal owned split. The other required 15 compatible hosts, arbitrary bodies, nonreal sectors, physical compilation and restoration, and the fully charged recurrence remain open. The other tied minimum subset is not factored here.

[#7419](https://github.com/CrocSwap/integer-mult-bounds/pull/7419) supplied the proper-window ranks and forward engine. [#7420](https://github.com/CrocSwap/integer-mult-bounds/pull/7420) supplied the exact original relative factor labels and directed invoice. [#7435](https://github.com/CrocSwap/integer-mult-bounds/pull/7435) supplied the four-factor scope and the pinned source bundle. #7334 supplied the complete comparator and #7113 the literal signed caller and physical sector construction. OpenAI Codex and its subagents materially assisted proof, implementation, independent replay and packaging.
