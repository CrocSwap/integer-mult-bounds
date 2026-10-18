# P112 with one common fourteen-line cut

For any two binary label spaces of dimension at most six and ONE common deletion set of at most fourteen P112 lines, all directions with residual label rank at most six span at most five dimensions. This is an author-checked finite theorem over every characteristic-zero field. Sharpness is not claimed.

Combined with [PR3185](https://github.com/CrocSwap/integer-mult-bounds/pull/3185)'s fifteen-line supplement lemma, it excludes the actual TWOSIDE `(b,t)=(6,5)` profile `2,3,4,6^8`. PR3185 supplied its five-piece quotient basis but left this precise common-cut implication open. [PROOF.md](PROOF.md) states the theorem, completeness argument and application.

The replay covers all 788,035 six-space annihilators, 776,806 distinct live masks and 160 first-mask orbits, including the empty mask. A separate least-coset enumeration checks the complete flat inventory. The 1,144 possible projective directions have support sizes 53, 56, 70 and 73. Testing only the 120 root directions would be incomplete.

The shared-cut algorithm enumerates unions of feasible minimal cuts. It never replaces a common deletion set by independent per-direction sets. All final rank decisions use arbitrary-precision integers. Controls include a direct short-lattice reconstruction of the direction list, 96 native/Fraction rank comparisons, basis deletion identities and three compiled semantic mutants.

## Reproduce

Requires Python 3.12 or later, an x86-64 POSIX host with POPCNT, and `g++` with Boost multiprecision headers. No third-party Python packages are used. `CXX` may select a compatible compiler.

```sh
mkdir -p "$HOME/.cache/integer-mult-bounds-runs"
RUN=$(mktemp -d "$HOME/.cache/integer-mult-bounds-runs/p112-common-fourteen.XXXXXX")
export TMPDIR="$RUN"
python3.12 -W error -B research/p112-common-fourteen-cut/verify.py --output-dir "$RUN/replay"
python3.12 -O -W error -B research/p112-common-fourteen-cut/test_verify.py
python3.12 scripts/research_package.py --package research/p112-common-fourteen-cut --check-only
```

The first command replays both complete 80-orbit ranges and compares every row with [RESULT.json](RESULT.json). The registered hook runs these ranges separately, followed by controls. Prefixes, reordered or missing rows, capacity exhaustion and timeouts fail. Outputs stay outside the checkout. The verifier and behavioral controls also work in a source export with the two declared data inputs; they need no Git history or unmerged dependency commits. The separate metadata checker requires Git history.

[CHECKS.json](CHECKS.json) records the checked environments and commands. [ENGINEERING.md](ENGINEERING.md) gives resource bounds and runtime-library deviations. There is no selected-supplier cold replay because no supplier or selected artifact changes.

## Sources and limits

- DreamingOfClouds, [PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154), head `708f0ad8928c383de8294aea3c126e9461d2066d`, supplied TWOSIDE, its original profile filters and the reduction/handoff. Its unchanged script reproduces all 24 original cell counts, including 174 historical `(6,5)` survivors. This is not a current count of unresolved profiles.
- Nick Petalas, [PR3185](https://github.com/CrocSwap/integer-mult-bounds/pull/3185), head `f4fa017730cb3d9978c31b3fe57a751fc15b505a`, supplied the quotient-basis cover lemma. Its proof is retained unchanged. The native replay recomputes its exact two-flat root-cover bound because this application needs that premise.
- Geometry, signed-Gram and dual-code methods retain Nick Petalas's PR3161/3162 attribution. The independent flat enumeration descends from PR3163. The E8/P112 label, root-code and decoder lineage, including joaqcoo's model, remains credited in the retained sources.

[SOURCES.json](SOURCES.json) pins inputs, public source heads, Git blobs and hashes. Vendored source bytes are checked on every replay. Their origin blobs were compared locally; a source export does not claim to authenticate unavailable Git objects.

The Weyl-chamber theorem and the original TWOSIDE reduction are explicit mathematical dependencies. This is not a proof-kernel formalization or independent human review. Full C5, `C(P112)>=64`, physical supplier admission and a new multiplication exponent are not established. The selected frontier is unchanged.

Nick Petalas. Apache-2.0. Development and local checking used substantial automated assistance.

## Open next questions

Which other actual remaining profiles have the same affordable quotient cover and at least six nonbasis rank-six directions? First pin the latest residue ledger and publication heads, then verify each candidate's quotient independence, common support union and nonbasis weights. This can reuse the theorem without a larger census. An up-to-date overlap-aware caller binding is the blocker. [TASK.json](TASK.json) records the scope change and this next step.
