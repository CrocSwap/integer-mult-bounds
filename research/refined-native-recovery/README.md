# Optimal refined recovery with a mode-preserving integer frame

**Sharp abstract 52-bit recovery tag on the actual 112-owner source;
No new κ.** For two rounded native invocations, with one relative precision
bit before the first, an explicit integer frame reduces the exact worst-case
recovery alphabet to **2,601,832,488,601,921 states**, requiring **52 bits**.
This is optimal over every fixed known integer unimodular frame preserving
the eight native mode projections. The parity-I subclass requires 56 bits.

The output function changes with the frame. These are abstract tag counts,
not a physical memory or runtime saving at an existing caller. Restoring
the exact unframed output without retaining additional side data restores
its 56-bit lower bound. [COST_SCOPE.md](COST_SCOPE.md) gives the explicit
reachable witness, full symbolic cost obligations and remaining interface.

## Technical result and novelty

With the inherited matrix M and literal half-away rounded map

    K(z)=z−M R(Mᵀz/52),     H_U(x)=K(U K(2x)),

let G contain all U∈GL_112(Z) satisfying MᵀU=Mᵀ. Then

    min_(U∈G) max_y |H_U^−1(y)|
      = ((13^8+14·13^4+1)/16)^2 = 2,601,832,488,601,921.

A frame attains this minimum exactly when the binary images of M and
U^−1M intersect only at zero. The package supplies a sparse rank-four
transvection U=I+VE, its exact inverse, source identities and dual witnesses
proving that condition. Zero output attains the maximum; an independent
all-output Fourier argument proves no output has a larger fiber.

This resolves the two-step mixed-refinement question from
[`precision-state-frontier/README.md`](../precision-state-frontier/README.md),
[zxv's #5444](https://github.com/CrocSwap/integer-mult-bounds/pull/5444),
within the entire mode-preserving integer-frame class. It does not settle
mode-changing frames. The predecessor one-step frontier, source binary code
and same-grid history counts remain predecessor work. The new result is
the complete composition theorem, optimal-frame criterion, explicit source
construction and effective full-output recovery codec.

As a complementary result, every fixed sequence of mode-preserving
parity-I frames has sharp finite-depth maximum

    A_t=(13^(8t)+14·13^(4t)+1)/16.

At t=2 this is 41,588,538,787,713,121 states. It is strictly below the
naive product of isolated maxima, but both require 56 bits. Explicit
parity-I frames fail to commute with the rounded kernel and each other.
This all-finite-depth theorem is in [CHAIN_PROOF.md](CHAIN_PROOF.md);
the optimal two-stage theorem is in [PROOF.md](PROOF.md).

`optimal_codec.py` ranks and unranks every attained output using at most
256 code-pair blocks and at most 169 scalar candidates per mode. It checks
literal forward replay after decoding. `recovery.py` supplies the companion
parity-I chain codec for depths 1 through 8. These exact integer programs
are not reversible bit/tape implementations or paid native callers.

## Reproduce and verification

From the repository root, CPython 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/refined-native-recovery
```

Expected markers include `PASS_REFINED_NATIVE_RECOVERY`,
`PASS_INDEPENDENT_REFINED_NATIVE_RECOVERY`,
`PASS_INDEPENDENT_OPTIMAL_FRAME`, and `PASS_REGISTERED_RESEARCH_PACKAGE`.
The registered commands run normal and optimized Python. They check the
literal source, exact frame/inverse and dual identities, scalar tie cases,
all zero-output parity blocks, arbitrary-output codec roundtrips and
rejecting controls. Separately written checkers import no primary code.
[VALIDATION.md](VALIDATION.md) records exact executed coverage and limits;
[RESULT.json](RESULT.json) binds the package and source hashes.

The canonical base is `a7638a4ce2a29947457ae8d6bf8cd70a234dfeac`.
[SOURCES.json](SOURCES.json) pins the actual fixture, predecessor question
and proof sources, and task context. Only the fixture is a live external
input. No predecessor executable or selected artifact is changed.
The selected conditional κ=0.003125804 remains unchanged.

## Scope and limitations

The theorem assumes fixed known frames, unrestricted exact integer inputs,
the stated relative grid, and final output plus a retained tag. It does
not automatically apply on a prescribed finite box. Source access,
finite-width arithmetic, intermediate workspace, physical movement,
cleanup and accepting/restoring the changed output remain unpaid.

## Open next questions

1. What is the sharp optimum for a genuinely mode-changing two-step frame?
   Derive its coupled quotient equations; common-mode scalar recursion
   no longer applies.
2. Can a named physical caller accept this output map with a favorable
   complete paid bill? Bind its grids, range, workspace, source access,
   routing, restoration and cleanup before claiming a supplier gain.
3. What is the optimal recovery alphabet for longer parity-changing chains
   or nonuniform refinement? The finite-depth theorem here covers only
   the parity-I class.

All five selected assumptions remain: native_all_columns, owned_erasure,
compiler, precision_tape and analytic_recovery. No selected cold replay,
physical caller admission, formal proof-kernel build or human acceptance
is claimed. Structured scope and next steps are in [TASK.json](TASK.json).

## Credit

Prepared for **@CubeJerry** with substantial **OpenAI Codex assistance** in
primary derivation and codec, complementary sparse-frame construction,
independent mathematical/implementation checking and caller-cost audit.
Credit zxv/#5444, Ali Romman/#5323, Brian/#5035 and the retained source,
normalizer, native/caller and precision contributors. Character duality,
binary linear algebra and mixed-radix coding are classical. New proofs and
code are Apache-2.0; no general literature-priority claim is made.
