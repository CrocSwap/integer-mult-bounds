# Space-capped dirty echoes: 152 calls instead of 160

**Recursive-interface research / construction refinement; no new kappa.**
Allowing unbalanced contiguous groups and mixed arities in PR673's multiway
echo reduces a 15-factor composition from PR689's **160 to 152 complete leaf
calls, with the same five arbitrary borrowed arrays**. Every inverse and
restoration call is counted. The supplied dynamic program proves the minimum
within the stated sequential echo-tree class, rather than only finding a
better tree. It also supports unequal positive integer leaf costs without
reordering the factors.

**Concurrent #730 also optimizes unbalanced trees and unequal prices, restricted
to binary/ternary nodes.** Its pinned optimizer still gives 160 at this primary
instance. Admitting the four-child node yields the strict **160 -> 152** gain.
Concurrent #744 independently audits the ternary class with broader finite
coverage. Neither package admits our higher arities. We credit their prior
publication and make no priority claim for unbalanced or weighted optimization.

For the pinned radix-16 cyclic factors on a length-five cycle, weighting actual
phase accesses selects another 152-call tree: **3656 phase reads**, versus
3840 for the balanced baseline and 3696 for the uniform-price tie choice.
These are exact operation counts, not measured runtime speedups. Arbitrary
dirty source/scratch restoration and complete-word inversion hold in the
rounded test cases; approximation error is separately bounded.

| Five-array comparison, 15 ordered factors | Complete calls | Phase reads at length 5 |
|---|---:|---:|
| PR673's original ternary partition | 208 | Not used as the phase baseline |
| PR689's improved balanced ternary tree | 160 | 3840 |
| This package, uniform-price optimum | 152 | 3696 |
| This package, phase-price optimum | 152 | 3656 |

The new search class matters: PR689 explicitly excludes unbalanced splits,
other arities and unequal costs. Seed 58 happens to match PR689's assignment
seed; the distinct contribution is the enlarged, exactly optimized tree class
and actual weighted fixture, not the seed. The echo identity, its generic
nonlinear restoration argument, and the rounded leaf are predecessor work.
Concurrent #714 instead supplies a clean-root checkpoint and a different
binary-root optimization; it requires one initially clean array. Our pool is
entirely arbitrary dirty input, and that work is credited in NOTICE.md.

## Reproduce

From the repository root, with Python 3.11+ and the standard library:

```sh
python3 -I -B research/space-capped-dirty-echo/verify.py
python3 -I -O -B research/space-capped-dirty-echo/test_contracts.py
python3 -I -O -B research/space-capped-dirty-echo/compare_concurrent.py
```

Expected final line of the first command:

```
PASS_SPACE_CAPPED_DIRTY_ECHO calls=160->152 scratch=5 no_new_kappa
```

The second command runs nine tests and reports `OK`. Checks use explicit
exceptions and remain active under optimized Python. The verifier checks every
field of [EXPECTED.json](EXPECTED.json); it does not write files by default.
`--write /new/path.json` writes a new certificate and refuses an existing file.
The test harness needs a writable current directory for temporary corruption
fixtures and removes only those fixtures. No network or solver is required.
The third command runs the byte-exact #730 optimizer, checks its literal words,
and compares all fields of [CONCURRENT.json](CONCURRENT.json), ending with
`PASS_HIGHER_ARITY_COMPARISON`:

| Factors / array cap | #730 binary/ternary minimum | All-arity minimum |
|---|---:|---:|
| 15 / 5 | 160 | 152 |
| 15 / 6 | 144 | 128 |
| 27 / 6 | 464 | 448 |
| 58 / 8 | 1728 | 1600 |

On the actual weighted radix-16 instance, #730 gives 3840 phase reads; the
all-arity result is 3656. This comparison uses two separately pinned files in
[CONCURRENT-SOURCES.json](CONCURRENT-SOURCES.json). It is a scoped replay of
the optimizer/word, not a review of the rest of #730.

The package consumes its vendored files plus exactly three repository context
files: `certificates/selected-result.json`,
`research/community-k492-audit/pr626/replay/ASSEMBLY.json`, and
`docs/research/community-k492-review.md`. Their hashes, as well as all vendored
bytes, are pinned in [SOURCES.json](SOURCES.json). A full supplier rebuild is
not performed by this command.

## Result, coverage and limits

[PROOF.md](PROOF.md) states the contract, recurrence, optimality induction,
workspace rule, full execution/preparation/precision invoice and integration
limit. [planner.py](planner.py) emits both signs of the literal word.
[verify.py](verify.py) contains separate exhaustive-tree and all-root-cut
oracles, and symbolic interpreters that consume the emitted instructions.

Completed finite coverage retained in the certificate:

- **5440 whole ordered trees** on 1–8 leaves; four weight vectors and every
  cap 0 through n-1, giving 144 feasibility/optimum comparisons.
- Every primary 15-factor cap from 4 through 14 checked by explicit root-cut
  enumeration, plus the weighted five-array optimum (18,212 root partitions
  considered for that weighted recurrence).
- Uniform plans for n=1–32 at the minimum feasible cap and one extra array,
  and the seed-related n=58/cap=8 diagnostic. There are 63 complete symbolic
  word checks including the weighted primary tree. The n=58 object is generic;
  it is not described as a prime-power kernel at radix 59.
- **48 generic rounded compositions and eight radix-16 compositions** using
  the byte-exact PR628 leaf. Both cycle directions, two nonzero dirty fixtures,
  an untouched spectator, dense rational references, actual phase-read counts
  and exact whole-word inverses are checked. These are finite input tests,
  not an exhaustive rounded-input proof.
- **326 rejecting controls**, including omission/sign changes at every one
  of the 152 primary leaves, wrong factor/inverse order, scratch aliases and
  invalid public inputs. Five actual implementation mutations are detected
  by the additional tests; source/context corruption is rejected. A concrete
  nonlinear example distinguishes exact restoration from dirt-independent
  output, and a target-dependent callback demonstrates a violated premise.

For the uniform 15-factor instance the full optimum row is:

| Allowed arrays | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Complete leaf calls | 224 | 152 | 128 | 112 | 100 | 92 | 84 | 76 | 68 | 60 | 56 |

The stopping rule was one exact planner with this fixed verification domain.
The four small-tree weight vectors are uniform, increasing, decreasing, and
generated by Python `random.Random(58)` with entries 1–58; this pseudorandom
test sequence is separate from the OS-random assignment draw. Enumeration
completes the declared domain. It does not exclude other reversible programs,
alternative scratch-sharing rules, or mechanisms outside the echo-tree class.

PR673's all-role adapter still has an unfavorable optimistic bill. Even after
this local improvement, its 15-group moment is **76/5 at saving zero**, and
the inherited class bound remains at least 3 for every nonnegative saving and
n>=2. No integration search is reopened, no selected supplier changes, and no
new kappa follows. A different physical integration and complete pricing would
be needed before this primitive could affect the multiplication bound.

## Provenance and handoff

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Selected construction: #626/#622/#623 with #543,
`kappa = 51110230636731/31250000000000000 = 0.001635527380375392`.
The linked assembly's SHA-256 is
`6127732e2fcdd470dab349c1c51d03cd9f0787ad0309b1b4a7c811a908028f4e`.
The review retains the all-size/compiler/common-label/mutable-basis, hosting,
normalized-residual, precision/tape/exact-recovery and analytic assumptions.

Exact predecessor heads:

- PR628: `0768f97d06c623b8211e651543c66135796b62bf`.
- PR673: `bfff94e78f0e75ebd2593e3cc7710ae5290e8be3` (including its later
  full-transform cost obstruction, not just its original local echo).
- PR689: `0dedef12f05f9a06faf9d4e1c8b1462c0e3bff3a`.
- Concurrent comparator PR730: `d222e348179cc02a54d6d26dbd2838944f62c6e5`.
- Concurrent credited audit PR744: `576c6b20065fff3402c1eed2ad74c5c7d03029e8`
  (no executable dependency).

No predecessor PR must be merged for reproduction. All additions are in this
directory. `upstream/`, generators, accepted suppliers, selected frontier and
the review ledger are unchanged. [CLAIM.json](CLAIM.json) records the three
candidate tasks, selected scope, random assignment and overlap checks.
[VALIDATION.md](VALIDATION.md) separates fresh checks from inherited evidence.

Prepared for **Koroffstrogov**, with substantial **OpenAI Codex assistance** in
the mathematics, implementation, checks and documentation. See
[NOTICE.md](NOTICE.md) for predecessor credit. Apache-2.0. No independent
human peer review, proof-assistant proof, full multiplication theorem, global
algorithmic optimality, or practical runtime improvement is claimed.
