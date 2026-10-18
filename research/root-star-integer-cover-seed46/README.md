# Independent verification of the P112 root-star copy floor

**Independent verification of PR1236's scoped cost-64 result; no new kappa.**

David Arias' concurrent [PR1236](https://github.com/CrocSwap/integer-mult-bounds/pull/1236)
closes the assembly window left by Navinor's
[PR1226](https://github.com/CrocSwap/integer-mult-bounds/pull/1226): its
fractional frame-cover bound is `784/13`, but the exact minimum is **64**.
This package independently corroborates that result for the same 240 indexed
root-star supports, arbitrary real or complex coefficients, any finite term
count and additional cost-zero corrections. It makes no priority claim.

The shared proof uses simultaneous frame coverage. Nine cost-seven terms would
require nine distinct, pairwise nonorthogonal live trimmed endpoints. The
complete P112 graph has maximum clique eight. Eight terms below cost 64 are
also impossible, since a cost-seven term misses a frame. The existing eight
coordinate stars attain 64. The distinct verification uses a complete
**pivoted maximal-clique census and all of its subsets**, rather than
PR1236's quadratic-form checker, and retains every individual atom rank.
It independently matches all five geometric sections of PR1236's exact
certificate, including its root, support, frame and full atom-stream hashes.

From the repository root, Python 3.10+ and the standard library:

```sh
python3 -I -O -B research/root-star-integer-cover-seed46/test_package.py
```

Expected: **six test groups pass (`Ran 6 tests`, `OK`)**. The suite runs both
complete implementations, optimized standalone replay, mathematical failure
controls, certificate/source mutations and overwrite protection.

Direct primary replay:

```sh
python3 -I -B research/root-star-integer-cover-seed46/verify.py
```

Expected marker:

```text
PASS_ROOT_STAR_INTEGER_COVER_S46 atoms=57600 frames=1260 cliques=482577 omega=8 copy_floor=64 no_new_kappa
```

[PROOF.md](PROOF.md) gives the finite premises and term-count argument.
[CERTIFICATE.json](CERTIFICATE.json) contains all 57,600 binary ranks as 240
single-digit rows, and the full clique census. The separate checker imports no generator or predecessor
code and uses different root, rank and graph algorithms.
[CLAIM.json](CLAIM.json), [SOURCES.json](SOURCES.json),
[OVERLAP.json](OVERLAP.json) and [VALIDATION.json](VALIDATION.json) record the
assignment, exact pins, scope and executed checks.

The claim requires exact C(alpha)/N(alpha) supports. Arbitrary proper
sub-supports, further trims, unions, other punctures and changed copy or stage
accounting are excluded. This is a finite computer-assisted proof with a
written implication, not proof-assistant or full multiplication verification.

## Open next questions

* Can a specified further-trimmed or union-of-stars support escape the missed
  endpoint argument at a favorable full cost? First compute its exact binary
  pairing ranks and missed frames. The current obstruction applies only to
  the stated alphabet; a new decoder would still need every source access,
  frame change, helper, restoration and recursive child priced.
* Does the same endpoint obstruction survive another explicit puncture?
  First recompute pair-to-frame completion and the nonorthogonality clique
  bound. Those finite premises are the blockers to transferring this proof.

Exact base: `49b3157d1d89adcef16df8be98445451672be5ba`; OS seed **46**.
Audited PR1236: `ee8437bd9879272094e20c024cd34a53c4e84cd8`.
The structural investigation reached the same argument before the submission
refresh revealed PR1236; the final contribution is explicitly corroboration.
Credit Navinor's PR1226 census/open assembly question, DreamingOfClouds'
PR717/595 masked model and Joel Pulikkan / GamingPuzzled's PR620 coordinate
decoder lineage. Concurrent PR1212/1213 handle the broader eight-term case;
their code and proofs are not premises here. See [NOTICE.md](NOTICE.md).

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex
assistance** in research, proof, both implementations, verification and
writing. No independent human review is claimed. Apache-2.0.
