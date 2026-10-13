# X4 nonunit target-pair exclusion

**Scoped negative result; no new kappa.** On the accepted PR799 X4 compensation
matrix, every individually restored target-pair shear with nonunit multiplier
`lambda = +/-2^e` costs at least **20 extra real primitives per orientation**
under the inherited binary-Horner lowering. This holds for every nonzero integer
`e`, not just the searched range. Such pairs cannot improve the best disjoint
signed-unit pair schedule. The unit-family optimum is not established here.

This resolves a specific extension of [PR901's unit-pair construction](https://github.com/CrocSwap/integer-mult-bounds/pull/901).
The new evidence is the complete nonunit census and an elementary all-exponent
tail argument. No predecessor search is repeated solely with more computation:
the multiplier class changes from `+/-1` to every signed power of two.

## Reproduce

From the repository root, Python 3.9+ standard library only:

```sh
python3 -I -B research/complex-x4-scaled-pairs/verify.py
python3 -I -B research/complex-x4-scaled-pairs/crosscheck.py
python3 -I -B research/complex-x4-scaled-pairs/test_package.py
```

The main command prints:

```
PASS_X4_NONUNIT_PAIR_EXCLUSION cases=174048 nonunit=149184 tails=all_integer_exponents min_extra_real=20 no_new_kappa
```

The independent command prints `PASS_X4_NONUNIT_INDEPENDENT`. Both support
`--json` for their checked deterministic receipts and work with `-O`. They do
not modify files, require Git, access the network, or import project modules.
The test suite compares both complete record digests and checks corruption,
source drift, cost/affine-slope controls and a minimal offline relocation.

## Evidence and limits

- [PROOF.md](PROOF.md) gives the exact restored-pair identity, complete bill,
  infinite-tail argument and scope. All preparation, restoration, source ADDs,
  binary doubles, halvings, accumulations and private CLEARs are charged.
- [EXPECTED.json](EXPECTED.json) records every exponent's extrema/counts and
  the SHA256 of all **174,048** ordered records. There are **149,184** finite
  nonunit cases, all losing, and **2,978** profitable unit cases. `verify.py`
  uses integer quarter-coefficients; [crosscheck.py](crosscheck.py) independently
  uses rational rows and lengths of explicit primitive words.
- [INDEPENDENT.json](INDEPENDENT.json) records the second checker, exact local
  primitive/wrapper tests, and adverse controls. Unit moves and a different
  quarter-grid matrix provide positive controls; ignoring the two boundary
  shears falsely turns the closest loss into a tie.
- [SOURCES.json](SOURCES.json) binds exact immutable input bytes and base Git
  blob IDs; compressed member checks use decompressed payloads. The canonical
  word and both complete program hashes match the selected X4 pins. The
  original complete scalar invoices are independently recounted, **193,162 /
  193,210**, but no complete native frame/phase replay is claimed here.
- [CLAIM.md](CLAIM.md), [NOTICE.md](NOTICE.md) and [VALIDATION.md](VALIDATION.md)
  record selection, predecessor credit, AI assistance, checks and handoff.

This excludes disjoint individually restored pairs under this lowering and
matrix. Overlapping basis transformations, other dyadic multipliers, helper
basis changes, boundary-gate folding, coefficient sharing, and different
lowerings remain outside scope. The proof is written mathematics supported by
finite exact checks; it is not a proof-assistant verification.

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`. The selected conditional kappa
remains `1661634653669567/10^18 = 0.001661634653669567`. No circuit is installed;
no construction, owner, invoice or frontier file is changed. Inherited all-size,
compiler, realization, hosting, precision/tape and analytic obligations remain.
