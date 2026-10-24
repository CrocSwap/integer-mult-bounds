# Reversible native ports for the repaired complex prefix

For every positive tensor width, the repaired two-call prefix extends to **two arbitrary independent input arrays**, with an explicit two-call reverse and Euclidean condition number at most 16. Its third-call lift exposes the exact target-bearing residual on a dirty target. On either explicitly stated swap sector, a free residual subtraction completes the canonical rank-three target in three calls. These are sufficient implementation theorems with proofs, not just rank tests.

**No improved κ, complete five-input/fourteen-call unit, or complete multiplication theorem is established.** The two-call port's independent diagonal outputs each have rank one; its off-diagonal term is dependent information. The three-call port has diagonal ranks one and two. Neither interface licenses credit for an extra independent rank-three output. The selected conditional frontier remains 0.00302015 (#4470); the stronger open 0.0030217758 claim (#4610/#4713) is not surpassed here.

The useful change from #4710 is that the second bank is arbitrary and remains explicitly present throughout the interface and inverse. A controller can now compose a literal reversible block instead of assuming a clean scratch target. The source prefix, phase repair and residual word identities remain credited to their predecessors.

## Proofs and implementation

- [FULL-INPUT-PORT.md](FULL-INPUT-PORT.md): exact two- and three-call schedules, both inverse orders, uniform conditioning, and a bounded-word precision contract.
- [SECTOR-COMPLETION.md](SECTOR-COMPLETION.md): canonical output on both swap sectors, absolute Pauli phase, an all-width identity criterion, and O(N) native address/phase generation for N = 8^f.
- [WORD-REVIEW.md](WORD-REVIEW.md): independent agent review of the universal algebra and finite replay.

All tensor powers apply to individual letters before scalar mixing. Tensoring the whole sum would give a different algorithm. The native implementation charges array passes, owned workspace initialization and cleanup. Its two- and three-call schedules use only dyadic mixing. The optional mathematical inverse of P_f + 2 Q_f has denominator 15 and is outside those native schedules; numerical use needs its own exact-grid or rounded-arithmetic invoice.

## Reproduce

Python 3.12 or later and the standard library suffice on Windows, Linux or macOS. From any working directory:

```sh
python3 -I -B /path/to/research/complex-prefix-native-ports/verify.py
python3 -I -O -B /path/to/research/complex-prefix-native-ports/verify.py
```

Expected final line: `PASS_COMPLEX_PREFIX_NATIVE_PORTS`.

The registered repository replay is:

```sh
python3 -B scripts/research_package.py --package research/complex-prefix-native-ports
```

The verifier authenticates every package file and the unchanged predecessor residual engine, then runs exact Gaussian-rational block/sector checks, an independently implemented vector replay at widths 1 and 2, the native odometer check, and a finite geometry census. Expected deterministic receipts are in CHECKS.json. The finite checks corroborate the written all-width proofs; they do not replace them. No network, solver, GPU, Lean, Docker or complete selected-supplier replay is required or claimed. Committed-byte preflight passes. Full source-history preflight could not complete in this shallow checkout; the exact main parent and declared provenance objects are available, but a full-history ancestry audit is not claimed.

## Frontier and overlap

Canonical main was fetched repeatedly at b58ad9ef4d4e861b0eaa5dba41742bdc072dca51. The live PR-body search was refreshed through #4740, including #4710, #4713, #4717, #4724–#4729 and #4733–#4740. The newer centre-code and response packages explicitly use historical inputs and do not claim a higher complete κ. The overlap helper could not refresh Discussions because its API request was rate-limited; the local checkout covered only 7 note records out of 5,860 tracked note paths. No exhaustive novelty claim follows.

The broader four-worker investigation also examined the actual #4610/#4694 reader, its E₈ geometry, and guarded owned-zero specialization. Those experiments are preserved outside this focused package. An early positive specialization was rejected because an initial owned-centre CLEAR had accidentally erased an independent helper input; it is not evidence for an improved bound. The final claims here do not use that parser or witness. Canonical Lean sources and the authoritative DAG were not modified. Targeted library retrieval was source-level discovery, not a new Lean audit.

## Open next questions

1. Compose the arbitrary-target block into a complete five-input/fourteen-call unit, retaining all independent outputs and paying every call. The full block and explicit inverse provide a concrete starting interface.
2. Find a nonmonomial free group-algebra encoding that cancels the residual across channels without discarding complementary input pieces. The exact 14-neighbor geometry is a search coordinate system; its symplectic quotient alone omits phases.
3. If using a dyadic degeneration, prove stability and precision for the complete recursive substitution. Fixed Laurent degree in one macro does not by itself bound the degree or precision of the recursive algorithm.

## Credit

Prepared for Dugongue with substantial OpenAI Codex assistance from four workers. Credit Yiyang (@Lyy-iiis), [#4710](https://github.com/CrocSwap/integer-mult-bounds/pull/4710), for the phase repair and residual identity; lee-phys, [#4688](https://github.com/CrocSwap/integer-mult-bounds/pull/4688), for the original two-image prefix and rank engine; and Jacob Alan Sussman, [#4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628), for the complex engine problem and hook framework. Exact heads, URLs and SHA-256 hashes are in SOURCE-PINS.json; original notices are retained in PREDECESSOR-NOTICE.md and the unchanged source READMEs. See NOTICE.md and LICENSE. Independent review here means a separate Codex worker, not human peer review or a formal kernel certificate.
