# Optimal reflection compilation of a nilpotent chain

This contribution was produced by Nick Petalas.

For a binary nilpotent Jordan chain J_n, the exact fixed-involution
reflection-call minimum is **2 floor(n/2)**, with arbitrary free binary scalar
mixing and any finite restored dirty workspace. An explicit stream attains
it without extra roles, using exactly 2(n-1) scalar XORs. Claim type: scoped
written algebraic proof with exact finite corroboration.

The first new case, n=3, costs two reflections and four XORs. Applying
ywz65's [PR2716](https://github.com/CrocSwap/integer-mult-bounds/pull/2716)
factorwise lowering to its two edges costs four reflections and four XORs.
Pairing adjacent edges saves address work without adding scalar operations.
The improvement stops here; multiple-block optimization is left open.

The endpoint is I+(1+[g])J_n over full formal F2[C2], for one fixed nonidentity
involution g. A paid call has a binary rank-one idempotent coupling. Every
input is arbitrary dirty data; spectators must be restored. [PROOF.md](PROOF.md)
derives the full endpoint, its rank/trace lower bound and the complete
chronological primitive invoice. [compiler.py](compiler.py) emits the literal
stream for 1<=n<=64; the written theorem covers every positive n.

At complete stationary primitive prices R,C, the supplied local bill is
2 floor(n/2)R+2(n-1)C instead of 2(n-1)R+2(n-1)C. Common basis transport
must be charged separately. No native prices or scalar-network optimum are
claimed. The result gives no new kappa or selected-frontier change.

## Reproduce and evidence

From the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/nilpotent-chain-reflection-compiler/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/nilpotent-chain-reflection-compiler/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/nilpotent-chain-reflection-compiler
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/nilpotent-chain-reflection-compiler --check-source-history
```

Substitute another CPython 3.12 interpreter elsewhere. Direct replay prints
`PASS_NILPOTENT_CHAIN_REFLECTION_COMPILER` in a generated JSON receipt bound
to the package-file hashes. Normal verification writes nothing. Registered
normal and optimized modes use explicit checks that remain active under -O.

The verifier checks 64 complete formal endpoints and their inverses, 2,048
rank-one idempotent summands, and every primitive invoice. A separate literal
bit-array interpreter checks all 87,380 two-address states at chain lengths
1 through 8, another 21,504 states with two dirty spectators, and 52,083
complete input columns across every involutory permutation on one through
six addresses. This last domain contains 119 permutations, including identity
actions as upper-bound controls. Literal checks compare against simultaneous
updates of immutable original inputs, so an in-place ordering error is exposed.

Separate complete two-call domains contain 784 ordered projector pairs on
three roles and 14,400 on four roles. Each has exactly two witnesses for the
new J_3 endpoint and no one-call witness. These small enumerations corroborate
the construction; the universal minimum comes from the written rank/parity
argument. All 84 single-primitive omissions at n=3 through 8 fail. Six invalid
compiler boundaries, a noninvolutory address substitution and a wrong reflection
role are rejected. No predecessor executable or census is imported or replayed.

## Scope and provenance

The `bit-new-register-model` card is changed to this constructive compiler side
question. It does not satisfy the card's native-supplier admission gate.
The prescribed current selected-baseline metadata command passed before work;
that check is not a mathematical premise. Canonical base is
7c49fe32c55de02c2c873655c804b16e4c3fef0a, priorities revision 8, selected PR6030
with conditional kappa 0.003125804 and all five framework assumptions retained.
[TASK.json](TASK.json) records the scope change and source diversity.
[SOURCES.json](SOURCES.json) pins cited proof context as historical provenance;
the verifier needs no predecessor input, Git, network or third-party package.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19370175)
followed live PR bodies, recent account submissions, handoffs, local reservations,
all-main README searches and merged distinctive-term searches. The overlap
helper's initial local coverage was 133 of 8,917 HEAD notes, so sparse no-match
results were supplemented by full main-tree searches. Its complete remote
pagination covered 506 open PR bodies at 09:05:30 UTC and 6,500 Discussion
records at 09:06:46 UTC on November 3, 2026. Remote text snapshots,
unpublished work and arbitrary historical diffs limit novelty coverage.

Only the fixed-involution formal endpoint and the supplied primitive stream
are settled. Several Jordan blocks, other paid labels, clean or discarded
workspace, native reflection legality, complete routing/frame/basis/ownership,
precision/tape/stock, recursive admission and the multiplication theorem remain
outside scope. No selected cold scientific replay, Lean or Docker run is supplied.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Determine the exact joint tariff for several nilpotent Jordan blocks. Start
  with one specified partition and its rank/trace lower bound; independent
  block compilation can leave parity or sharing opportunities. This proof
  supplies no general minimum over all nilpotent matrices.
- Bind one actual native caller to the two-edge stream. Price the coordinate
  reflection, every scalar XOR, basis transport and all movement, ownership,
  restoration, precision and stock obligations before drawing a supplier or
  multiplication-bound consequence. Those native contracts remain unknown.

## Credit and implementation limits

Credit ywz65/PR2716 for the arbitrary-coupling interface, square-zero coefficient
product and factorwise dirty lowering; Adam Gall/PR1911 and the retained
eumemic/PR288, Ali Romman/PR468, woklerx/PR1443, Gareth Davidson/PR1333,
Arham Tahir/PR1589 and Cinna Davis/PR2290 register-model lineage. Rank, trace,
Jordan chains and elementary conjugation are classical. Nick Petalas/PR4912
settles square-zero couplings, JoyboyBrian/PR5007 supplies a returned-clean
compiler, and Nick Petalas/PR5857 optimizes that clean stream's scalar work.
Their results and credits are retained. The new result is the non-square-zero
single-chain compiler and its exact reflection tariff. Apache-2.0.

Build the Lever led to the literal stream emitter and repeatable checker.
Prove It Works led to full dirty-column execution and omission controls.
Power of Ten bounds the emitter to 64 roles and the census to 87,380 main
states, 21,504 spectator states, 720 candidate permutations per size and
14,400 ordered projector pairs per case. Functions are below 60 physical
lines; there is no recursion, subprocess, network or runtime code generation.
The one-shot verifier reads at most one MiB per package file.

Rule 3 has a managed-runtime deviation at compiler.py and verify.py: CPython
allocates bounded lists, tuples and integers dynamically. There is no
fixed-pool or steady-service claim. Live state is bounded by 64 role rows,
at most 190 operation records and 120 four-role projectors; exhaustive input
states are streamed. A fixed-storage runtime would require a separate port.
Rule 9 has one fixed local import and standard sorting of the seven local
file names; no unknown callback or dynamic target is accepted. Warning-strict
normal and optimized execution provide interpreter diagnostics. No unavailable
external static analyzer or formal kernel is claimed.
