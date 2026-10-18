# Six-source connector with one charged TRIO call: exact scoped exclusion

**Scoped negative result; no supplier, assembled bound, or new `kappa`.** On
the six-source connector over `F_2^6`, a closed source path with twelve calls,
eleven singleton calls, and one weight-three call cannot produce all 63
nonzero pairwise prefix differences. The complete normalized census contains
1,098,204 simple paths; 709,812 have the required weight-three closing edge.
Their maximum coverage is 49/63, attained by 4,992 candidates, with no full
cover. This excludes only this exact call and source-add profile.

The operation family is the universal connector's singleton source call
extended by `TRIO_{jkl}: z += B_j x_j + B_k x_k + B_l x_l`. It reads three
source rows and charges all three source additions; the rows stay read-only.
For a closed source word, the prefix states are distinct elements of `F_2^6`,
and each output mask must occur as a difference of two prefixes. The pairwise
difference test is the connector endpoint condition for arbitrary dirty
inputs.

## Exact search and result

There are twelve prefix vertices in a twelve-call closed word; the last call
returns from the twelfth vertex to the first. Full coverage of 63 nonzero
masks needs at least twelve distinct vertices because `binom(11,2) = 55`.
Thus twelve calls meet the counting floor. In the tested profile, the eleven
singleton edges form a simple path and the TRIO edge closes it.

Normalize any candidate by translating its first vertex to zero, rotating the
unique TRIO edge to the closing position, and permuting coordinates so the
first two singleton edges are `1` and `2`. The vertices then start
`(0, 1, 3)`. A self-avoiding unit walk adds nine more vertices, and its last
vertex must have Hamming weight three so the closing TRIO returns to zero.
This is a complete orbit representative: simplicity forces the first two
unit edges to use distinct coordinates, and coordinate permutations act
transitively on those ordered pairs.

[`search.py`](search.py) uses a depth-first walk and incrementally packs the
pairwise differences into an integer. [`verify.py`](verify.py) independently
enumerates all `6^9` coordinate suffixes, filters repeated vertices, and
recomputes each eligible difference set from scratch. Both exact methods
agree on the census and a SHA-256 digest over all 709,812 endpoint records.
The coverage histogram, maximal example, and exact census counts are in
[`CERTIFICATE.json`](CERTIFICATE.json).

The maximum example has prefixes
`0, 1, 3, 7, 6, 14, 15, 31, 29, 61, 57, 41` and misses the fourteen masks
listed in the certificate. A positive control replays the 14-call, 16-source-
add witness in [PR #2128](https://github.com/CrocSwap/integer-mult-bounds/pull/2128),
which covers all 63 nonzero masks under the same pair-difference test.

## Fully charged comparison

Both schedules use two readouts for each of 63 outputs, so each has 126
readouts. Let `o` be the complete cost of each root call and `p` the cost of
each source addition. The PR #2128 schedule has fourteen source calls and
sixteen source additions: `140 o + 142 p` including readouts. A hypothetical
schedule in this profile would have twelve source calls and fourteen source
additions: `138 o + 140 p`. The TRIO is charged as `o + 3p`; it is not a free
three-source operation. If an implementation adds a further TRIO surcharge
`tau`, the modeled saving survives only when `tau < 2o + 2p`.

This profile has no full-coverage path, so that favorable completed budget
does not materialize here. Other arities, other weight profiles, mixed TRIO
and DUO paths, implementation surcharges, and supplier availability remain
open. No connector supplier is currently supplied by this experiment, so it
does not establish a recursive saving or change the selected frontier.

## Reproduction

From the repository root:

```sh
python3 -I -B research/connector-trio-cycle25-seed1b82df/verify.py
python3 scripts/research_package.py --package research/connector-trio-cycle25-seed1b82df --check-only
```

Expected verifier output:

```text
PASS_TRIO_CYCLE_VERIFY walks=1098204 endpoints=709812 max=49 full=0 pr2128=63/63 controls=3
```

The repository's registered replay runtime is Python 3.12. The local runtime
used for this handoff is Python 3.14.7; Python 3.12 is not installed in the
research environment.

## Open next questions

- Does a twelve-call six-source cycle with ten singleton edges and two
  charged TRIO edges attain all 63 nonzero differences? Its source-add count
  is sixteen, so a witness would match PR #2128's add count while saving two
  complete calls before any TRIO-specific surcharge. First step: normalize
  both weight-three edges under cyclic rotation and coordinate permutation,
  then enumerate only simple paths whose total XOR is zero. Stop at a full
  exact census of that fixed `10×weight-1 + 2×weight-3` profile. Blocked by:
  no complete covering word has been identified.

## Attribution

The source-call operation and pair-difference endpoint follow the universal
connector in `research/universal-connector-boundary/`. The cost comparator
and positive witness are from Aaron Wang's [PR #2128](https://github.com/CrocSwap/integer-mult-bounds/pull/2128).
Substantial OpenAI Codex assistance was used for the mathematical modeling,
search implementation, and verification. No independent human review is
claimed.
