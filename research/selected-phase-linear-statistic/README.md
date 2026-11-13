# The selected tensor phase needs exactly f+1 linear observations

Scoped written proof with exact finite corroboration, produced by Nick Petalas.
No new kappa is claimed. For every positive tensor column count f, the right
diagonal phase of selected MOVE24472 has exact binary linear observation
rank **f+1**, even when observations mix columns arbitrarily.

CubeJerry / Jerry Chen's [#7426](https://github.com/CrocSwap/integer-mult-bounds/pull/7426)
supplies the nine-coordinate recipe. Its fifteen quadratic pairs form the
clique on S={0,1,2,3,5,6}. The classical parity identity contracts the recipe
to

    q(x) = 1 + 3 XOR_(i in S) x_i + 2 x_7 (mod 4).

For f columns, retain their f separate S-parities r_j and the single parity
b of all coordinate-7 bits. The complete absolute phase exponent is

    Q_f(x) = f + 3 sum_j r_j + 2b (mod 4).

This removes all fifteen pair terms from each column's description and saves
f-1 observation bits compared with retaining the two natural parities per
column. It does not assert that #7426 allocates 2f physical bits to them.
The new lower bound follows from the complete translation-period subgroup,
of dimension 8f-1. Any affine-linear statistic determining the phase must
have its kernel inside that subgroup. [PROOF.md](PROOF.md) proves this for
all f; finite checks corroborate the stated source-specific identities.

The observation restriction matters. Computing Q_f directly is nonlinear
and always gives a two-bit output. The f+1 bound concerns linear measurements
before arbitrary decoding, rather than output size or streaming workspace.

## Reproduce

From the repository root, with the supplied CPython 3.12 interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/selected-phase-linear-statistic/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/selected-phase-linear-statistic/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/selected-phase-linear-statistic
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/selected-phase-linear-statistic --check-source-history
```

Another machine may substitute its CPython 3.12 path. Only the standard library
is required. Direct replay is read-only and works in a Git-free export. It
prints `PASS_SELECTED_PHASE_LINEAR_STATISTIC` inside a generated JSON receipt
bound to all seven package-file hashes. No receipt is handwritten or stored
as an expected answer. Normal and optimized commands use explicit exceptions.

The literal polynomial oracle uses the source's strict-upper quadratic rows
and all nine linear coefficients. The contracted evaluator uses only parity
and the displayed decoder. They agree on all 512 one-column and 262,144
two-column addresses. A complete 262,144-comparison one-column truth-table
derivative calculation finds 128 periods. Its constant-derivative table
classifies all 262,144 two-column shifts, finding 32,768 periods. This last
classification uses independence of the two input columns, not 2^36 pairwise
comparisons. All 512 possible one-bit linear maps fail on their actual
one-column fibers. These are new phase-information checks; no predecessor
binding, tape program or mathematical suite is imported or replayed.

An additional 1,024 deterministic fixtures cover f=1..64, with 3,072 Gaussian
forward/inverse pairs. Seven semantic negative controls, one positive
joint-column cancellation control and five invalid-domain controls pass.
The larger fixtures are not exhaustive. The unbounded theorem rests on the
written proof, with no human or proof-kernel acceptance claimed.

## Sources, scope and credit

Credit CubeJerry #7426 at `172f4535ce8dcff79f626410af845f757c1563be`
for the supplied MOVE24472 recipe, its binding and literal phase implementation.
[PREDECESSOR-RECIPE.json](PREDECESSOR-RECIPE.json) retains that factual file
byte for byte; its original native matrices and event metadata are unchanged.
The SHA256 and exact download URL are in [TASK.json](TASK.json). Its scientific
source-binding theorem is cited. Checking this exported recipe's hash does
not independently establish its connection to the selected native catalogue.
Publication requires no pending predecessor commit in local Git history.

Retain Ali Romman #5375's multicounter phase-production lineage and #7000's
DreamingOfClouds, Ali Romman, Cinna Davis, zxv, unpaidmoon, icekylinx and earlier
native/Gaussian contributors. Dennys / antunishdPursuit #6500 also records the
classical parity expansion for a different phase-contact family. Parity
expansion and quotienting by translation periods are credited methods. The
contribution is this recipe's contraction and its sharp tensor information
bound, rather than a new general identity or a source audit. Apache-2.0.

Base main is `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8.
The catalogue assessment predates selected #7000; its frozen bytes remain
provenance in [SOURCES.json](SOURCES.json). The selected-binding first control
passed. The `formal-interface-lemma` card explicitly changes scope to a
written phase-information side result, with no proof-assistant build.
Live PR bodies, recent account work, current claims, local reservations,
merged searches and main README searches were checked. Search absence does
not certify novelty; arbitrary code diffs and unpublished work remain outside
coverage. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19591467)
states the same mathematical scope.

Physical acquisition, decoder work, dirty restoration, layout, owner return,
precision, historical backing and the complete recursive invoice are unpriced.
The result alone reduces neither tapes nor runtime and admits no new supplier.
It changes neither the affine address map nor the central C tensor. All five
selected framework assumptions remain. No selected cold replay, Lean, Docker
or complete multiplication proof was run.

## Open next questions

- Can a literal producer exploit this contraction with a lower complete phase
  bill? Start with the supplied #7426 packed interface, replacing quadratic
  updates while charging every parity read, carry and cleanup. Its full
  time/backing invoice is the blocker; information rank alone supplies none.
- Can a producer compute the nonlinear two-bit phase without retaining the
  f linear observations? Start with one explicitly ordered sequential scan
  and its reversible state/return contract. The theorem permits arbitrary
  decoding but does not price that different streaming interface.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).
No follow-on scope is reserved.

## Verifier constraints

Build the Lever supplies the retained deterministic verifier. Prove It Works
requires the literal phase and truth-table checks above. Functions are below
60 lines, loops have fixed bounds, and no recursion, subprocess, network,
dynamic code loading or output-file write is used. Package reads are capped
at one MiB per file; the recipe is capped at 64 KiB. The public column input
is restricted to 1..64 nine-bit integers, rejecting Booleans.

Power-of-ten rule 3 deviation: CPython allocates managed integers and containers.
Live mathematical state is bounded by the fixed domains, including 512-entry
phase/derivative tables and sets of at most four phase values. The 262,144
two-column cases are streamed. File hashes cover seven bounded files.
Warning-strict ordinary/optimized replay and an AST/function-length inspection
are the available diagnostics; no project-wide tooling change is made.
