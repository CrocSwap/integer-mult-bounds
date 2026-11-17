# The zero spectral projector needs denominator 12,480

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: exact finite certificate with a scoped arithmetic obstruction.
For the historical `A_1` joint `(+1,+1)` block pinned by unpaidmoon's
[PR #6964](https://github.com/CrocSwap/integer-mult-bounds/pull/6964), the
zero-eigenspace projector has least integral denominator

```text
P = Q / 12480,    12480 = 2^6 * 3 * 5 * 13.
```

[PROJECTOR.json](PROJECTOR.json) supplies every entry of the integer matrix
`Q`. Four reduced entries force the denominator, with indices starting at zero:

```text
P[10,60] = 9/4160
P[4,4]   = 47/156
P[6,6]   = 71/260
P[0,0]   = 5/416
lcm(4160,156,260,416) = 12480.
```

Consequently this particular exact spectral filter cannot be a linear program
using only dyadic rational coefficients in the pinned basis. In particular,
no polynomial in `A_1` with dyadic coefficients equals `P`. Its matrix has
entries outside `Z[1/2]`. This does not exclude another invariant filter,
a rational implementation with paid odd division, or an approximate filter.

No kappa improvement, supplier admission or selected-frontier change is claimed.
The selected record at the package base is #7000, with conditional
`kappa = 363005817/100000000000`. This result concerns a historical centre block.

## Exact evidence

The proof is in [PROOF.md](PROOF.md). The verifier authenticates the predecessor
matrix and orbit basis, then checks

```text
M = 4 A_1
Q^2 = 12480 Q
M Q = Q M = 0
D M = M^T D,   D Q = Q^T D
 det(M+Q) mod 1000003 = 905182 != 0.
```

`D` is the positive diagonal Gram matrix of the disjoint signed-orbit basis.
Nonsingularity of `M+Q` proves that the image of `P` is the whole kernel, rather
than an unspecified part. The identities and weighted symmetry uniquely
identify its orthogonal projector. Its rank is 24 and `Q` has 4,608 nonzero
entries, both enumerated by the checker. The characteristic polynomial and
predecessor nullity packages are not replayed.

The verifier accepts a weighted, nonsymmetric two-dimensional fixture and
rejects four false certificates: one altered numerator entry, the source
shifted by the identity, a doubled unreduced fraction, and the zero projector.
The zero projector satisfies the annihilation and idempotence identities but
fails completeness, so the determinant check supplies necessary coverage.
All checks use explicit exceptions and also run under optimized Python.

The full source pins, scope and replay contract are in [SOURCES.json](SOURCES.json),
[TASK.json](TASK.json) and [VERIFY.json](VERIFY.json). Source-file hashes bind the
scientific inputs; the package runner also checks metadata and source pins.
The separate publication preflight checks declared source-history availability.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/a1-zero-projector-denominator/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B -O research/a1-zero-projector-denominator/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/a1-zero-projector-denominator
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/a1-zero-projector-denominator --check-source-history
```

Other machines may substitute their CPython 3.12 path. The direct marker is
`PASS_A1_ZERO_PROJECTOR_DENOMINATOR`. The registered marker is
`PASS_REGISTERED_RESEARCH_PACKAGE`. Local environment is CPython 3.12.15 on
macOS arm64, recorded in TASK.json. Lean, Docker, the degree-216 and degree-881
spectral replays, the selected cold replay and a physical implementation are
outside this package's checks.

The checker writes nothing. Matrix dimension is at most 216, each JSON input
is bounded by one MiB, and orbit supports have at most 16 entries among 4,096
addresses. Python allocates during arithmetic; the finite capacities bound live
storage instead of claiming allocation-free execution. Functions are below
60 lines and no recursion or external dependencies are used.

## Related work and credit

unpaidmoon #6964 supplies the exact matrix, the signed-orbit basis and the
characteristic polynomial. The new result is the explicit projector, its sharp
arithmetic denominator and the resulting dyadic obstruction. The new certificate
uses that matrix as its mathematical input and does not independently establish
its derivation from the historical query.

Related open work #7018, #7064 and #7066 computes kernel dimensions, while #7008
and #7065 split the same block by normalizer symmetries. They are distinct from
this projector-denominator question. Their results are credited without replay.
JoyboyBrian posed the earlier decomposition handoff. Retain the sign-stabilizer
construction, Ali Romman's #4958/#4720 query and Bell-action work, Krzysztof
Wojt's #5168 one-slot polynomial, Nick Petalas's #5120 lower bound, and #1719's
doubled representation. Those results are background rather than new claims here.

## Open next questions

- Price an exact physical filter with odd division and full output restoration.
  First choose a legal division contract and factor `Q/12480`; native delivery
  and the complete paid/target invoice are unresolved.
- Identify whether a different invariant filter needed by a stated centre
  consumer can be dyadic. Begin with that consumer identity; this package
  supplies no reason to substitute an arbitrary different projector.
