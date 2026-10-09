# Further frame refinement from PR195

The exact conditional exponent saving is

    kappa = 662832575455842015647/1000000000000000000000000
          = 0.000662832575455842015647.

This improves the pinned PR195 witness, kappa=0.000662651985348746, by
**0.0272526%**, and the reviewed PR186 witness by **0.1430801%**.
The candidate changes **468 operation frames relative to PR195**. The scalar
word, aliases, compensation deadlines, all 46 terminal sinks and bit supplier
remain fixed. This is an incremental search-catalogue refinement within the
existing parameter domain.

PR195 already implements arbitrary-subspace joins and intersections. Those
moves and directed cuts are not new here. This package contributes an
independent standard-library implementation, a finite catalogue of coordinate
planes and frequent small annihilators, local/group cleanup, and the resulting
fully checked additive witness. No dominance over other search implementations
or current-record claim across pending suppliers is made. PR197 reports a
larger bound with different suppliers; it is not a dependency of this package.

## Verify

From a checkout of the repository, with Python 3.11+ and assertions enabled:

    python3 -B research/subspace-bundle-frames/check_moves.py
    python3 -B research/subspace-bundle-frames/verify.py
    python3 -B research/subspace-bundle-frames/check_report.py

The default verifier replays the complete pinned PR186 complex and bit package,
then checks the changed physical frames, terminal trajectories, every formal
source/target/dirty column under both signs, exact interval moments, 47 strict
assembly inequalities and seven margins. It must match certificate.json exactly.
The --changed-witness-only flag omits the original baseline replay but still
checks all original manifest pins and the immutable prerequisite archive.
The --write flag is an explicit authoring option. Optimized Python modes reject.

The final complex supplier saving is 0.000663272213885600106064.
The unchanged bit supplier remains larger. Total rank=878196, W=13326,
R=10686, deficit=1320 and maximum child=20 remain fixed. All retained scalar,
routing and row-stock charges stay paid. See PROOF.md for the move reduction
and retained dependency argument. certificate.json contains exact evidence;
changes.json gives all before/after frames relative to PR195.

See [VALIDATION.md](VALIDATION.md) for the local readiness audit and its limits.

## Rebuild and optional discovery

The builder automatically checks and extracts the parent's pinned prerequisite
archive. No pre-existing local-investigation directory or separately downloaded
Python dependency is needed. Choose fresh output paths:

    python3 -B research/subspace-bundle-frames/build.py --output /tmp/subspace-rebuild

Its gzipped candidate inputs must reproduce the frozen candidate bytes. To
repeat the search from the exact pinned PR195 seed:

    python3 -B research/subspace-bundle-frames/build.py --frames research/subspace-bundle-frames/seed/pr195-frames.json --output /tmp/subspace-seed
    python3 -B research/subspace-bundle-frames/search.py --candidate /tmp/subspace-seed --output /tmp/subspace-search.json
    python3 -B research/subspace-bundle-frames/build.py --frames /tmp/subspace-search.json --output /tmp/subspace-discovered

Discovery tries local endpoints and equal-frame groups, then 231 coordinate
planes and 96 frequent two/three-dimensional annihilators, in contraction
and expansion modes, followed by local/group cleanup. Floating discovery
scores and rounded cut capacities do not certify an exponent. Discovery is
optional; the stored exact witness is independently verifiable. Exhausting
this catalogue proves no global frame optimum. Python/platform variations in
floating search can change its path without affecting frozen verification.

## Sources, credits and scope

Base main: 3b6b66891c0ac888521cf591fe306c6286601d4f.
PR195 seed: d3e6b83af33c3aad940e737776937706e25b0b19.
SOURCE.json records the exact seed hash. PR195-NOTICE preserves its notice;
NOTICE and the unchanged parent notices retain the construction's lineage.
Prepared with substantial OpenAI Codex assistance; new work is Apache-2.0.

- [PR195, huxint's coordinated cuts](https://github.com/CrocSwap/integer-mult-bounds/pull/195)
- [PR186, reviewed parent](https://github.com/CrocSwap/integer-mult-bounds/pull/186)
- [PR197, larger reported bound with different suppliers](https://github.com/CrocSwap/integer-mult-bounds/pull/197)
- [Parent bank scheduling supplement](../community-round8-audit/BANK-SCHEDULE.md)

The inherited all-size analytic, weighted compiler, common-frame, restored-row,
routing, precision/recovery, prime-supply, uniform-setup and fixed-tape interfaces
remain conditional. Finite certificate success is not formal verification of
the complete multiplication theorem or evidence of a practical runtime speedup.
