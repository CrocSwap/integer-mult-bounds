# Exact bounded modular replay of the selected backward endpoint

**Independent finite verification; no new kappa.** The selected #741 backward
scalar program has the expected shear endpoint on all **728 native and eight
arbitrary private-center inputs**. This implementation uses modular sparse
matrices and an explicit integer reconstruction bound, importing neither the
constructor nor an existing verifier. It uses no rational-matrix library.

```sh
python3 -I -B research/sw4-crt-endpoint/verify.py
```

Expected: `PASS_SW4_EXACT_MODULAR_ENDPOINT columns=736 moduli=2 controls=7`.
Python 3.11+ and the standard library suffice; normal verification is offline
and read-only. `--write NEW_FILE` explicitly regenerates the receipt without
overwriting an existing file.

The complete domain is all 19,197 scalar macros in the pinned backward
program. There is no randomized mathematical search. OS assignment seed 80
chose this verification mechanism and the backward orientation; alternatives
and the local coordination fallback are in CLAIM.md. Every matrix column is
checked, including arbitrary dirty centers, rather than sampled inputs.

## Why the modular result is exact

Maintain a positive row-L1 envelope `N_r` and a denominator exponent `D_r`.
Initially every row is an independent input with envelope 1 and exponent 0.
Clear sets both to zero; copy copies both. For a reduced dyadic coefficient
`q=n/2^d`, scale multiplies the envelope by `abs(q)` and changes the exponent
bound to `max(0,D_r+d-v2(abs(n)))`. An addition adds the scaled source
envelope and takes the maximum of the target and scaled-source denominator
bounds. These recurrences follow directly from addition and multiplication
of dyadic matrix entries, without needing their values.

At the endpoint the maximum denominator exponent is **19** and the ceiling
of the largest positive row envelope is **3018702981239539556129**. Each
desired entry is 0 or +/-1, so every integer residual after multiplication by
`2^19` has absolute value at most

```text
B = 1582669748628115714804285440.
```

The two moduli are **4294967297** and **18446744073709551617**. They are odd
and pairwise coprime, checked by integer gcd; primality is neither assumed
nor needed. Dyadic denominators are invertible modulo each. Their product
is **79228162532711081671548469249**, which exceeds `2B`.

Both modular matrices equal the desired endpoint. Thus their product divides
every scaled integer residual. Its strict magnitude bound forces that
residual to be zero. This is deterministic exact reconstruction, not a
probabilistic modular screen or a formal proof of the multiplication theorem.

## Failure detection and limits

Seven controls reject insufficient modulus coverage, duplicated moduli,
a unit endpoint error, a change invisible modulo the first modulus, a change
invisible modulo **both** moduli, an omitted initial dirty-center clear and
a nondyadic denominator. The all-moduli-blind mutant first passes both raw
modular replays; recomputing its height bound then rejects the insufficient
product. This explicitly exercises the proof obligation that modular-only
checking would miss. Explicit guards remain active under Python `-O`.

This checks the finite backward **scalar projection**. Native frames, child
execution, wrappers, coefficient-work primitive lowering, physical hosting,
precision/tape and all-size/analytic transfer remain inherited obligations.
Private coefficient-work primitives are not expanded here; eight private
center columns are included. No forward replay, full cold rebuild, CI or
Lean proof is claimed. The selected conditional kappa remains
`1661202643272239/1000000000000000000`.

## Provenance and validation

Base: `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`; selected #741 source:
`e516b1463606840a15f80aac1995d64ce0092e89`. SOURCES.json pins decompressed
native/program payloads and the accepted assembly. EXPECTED.json records the
program digest, both residue-matrix digests, row-bound digests, exact bound
and seven controls. Compression-container differences are not mathematical
differences.

Windows Python 3.14 normal and optimized replay pass; Linux Python 3.12 replay
and Ruff also pass. No existing source or selected record is
modified. The method independently corroborates the accepted rational replay.
#668's CRT work concerns cyclic resultants; #777 checks frame geometry.

Credit Chafik Boukhalfa's #741, Jeremy Kothe's #699/#676 and earlier provider
work, icekylinx, DreamingOfClouds, Jeremy Diviney, eumemic, Rohan Arun and the
retained construction/audit lineage. The current maintainer review preserves
the full attribution and inherited assumptions. No pending code is imported.

Prepared by **Ryan Haines (@Ryan-Haines)** with substantial **OpenAI Codex**
assistance. Apache-2.0. Independent implementation does not imply independent
human review.
