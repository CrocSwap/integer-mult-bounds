# The QQ16 eighteenth-position witness survives the local native core

**Finite native error-channel certificate.** The B1,2 child-error witness in
[Tekalign's PR3189](https://github.com/CrocSwap/integer-mult-bounds/pull/3189)
survives the literal retained native core, including its changing frames and
occupied residual adapters. It is not an artifact of replacing those maps by
identities. This answers PR3189's second **Open next question** for one local
512-coordinate payload factor. It does not supply a rounded recursive child,
a global producer accuracy bound, or an affordable consumer.

All event numbers below are zero-based in the expanded `B_1_2` program of the
unchanged [joint-query certificate](../joint-query/certificate.json.gz).
The retained backward core starts at event 1864. Its suffix after the named
injection contains no cover maps or new native-line wrappers.
`ONE` is the real vector of 512 ones. The complete Gaussian-integer injection
is recorded explicitly in `RESULT.json`, so it can also be used without relying
on its frame-based description.

| Item | Exact value |
| --- | --- |
| Injection | After child 13489: `['climb','A',344,226,236,1]` |
| Error direction | `w = T_236 ONE`, source frame basis `[416,75,19]` |
| Components of w | Real and imaginary entries in `{-1,0,1}`; squared Hilbert norm 512 |
| Attaining cut | After 26472: `L93 += -L103/8`, local frame 1 |
| Error at that cut | `(-81921/262144) ONE` |
| Largest component denominator exponent at completed events | 18, first attained at this cut |
| Largest absolute component in this error trace | `81921/4` |
| Final data error | `L75 = -ONE/2`, `L93 = ONE/2`; all other data fields zero |
| Final helper error support | L337, L338, L339, L341, L343, L346 |
| Final private error | All eight fields zero |

The helper defect is material: this error channel does **not** restore borrowed
state. The six helper squared norms are respectively `32,128,128,32,128,128`.
Their full component histograms and vector hashes are in `RESULT.json`; for
example the final coordinate zero of L337 is `i/2`. The originally perturbed
L344 itself has zero final error.

## What this proves about a grid

Let the ideal and perturbed computations agree until this completed child.
Insert the additive defect `h w`, for any positive grid quantum h, then apply
the subsequent native maps and scalar operations exactly. Linearity makes the
error at each cut h times the checked trace, regardless of the underlying
ideal data and dirty-helper values. This is a completed-child defect model,
not a claim that a particular child or rounding algorithm produces this error.

The injection is on the Gaussian component lattice `h Z[i]`. At the attaining
cut, a real component expressed in units of `h/2^17` is `-81921/2`, which is
not an integer. Thus 17 fractional guard positions cannot represent even this
one channel exactly. If the ideal component at this cut is on the working
grid, the perturbed component is off it; rounding that component to the grid
incurs absolute error at least `h/2^18`. The exact error trace is on
`h/2^18 Z[i]` at every
**completed program event**, so 18 is necessary and sufficient for this
particular direction and these cuts.

This is a lower-bound witness for a more general native error-lattice contract,
not a sharp upper bound for every child direction. It does not bound the
intermediate arithmetic inside a child recipe. The final data and helper
errors need only one fractional position, so an endpoint-only grid check would
miss the intermediate requirement.

## Evidence and reproduction

From the repository root, standard-library Python 3.12:

```sh
python3 -Werror -I -B scripts/research_package.py \
  --package research/qq16-native-noise-lift
```

Expected markers:

```text
PASS_QQ16_NATIVE_NOISE_LIFT guard=18 coefficient=-81921/262144 data_fields=2 helpers=6 private=0
PASS_QQ16_NATIVE_NOISE_FORWARD guard=18 complete_trace_and_endpoint=matched
PASS_QQ16_NATIVE_NOISE_DUAL coefficient=-81921/262144 checks=4 coordinate=0
```

Nine behavioral test groups and the registered-package PASS follow. The
primary replay is read-only; `verify.py --write PATH` exclusively creates an
absent receipt. It authenticates four live inputs and three archive members.
The regenerated receipt compares every proof-relevant field, including the
explicit injected vector, all endpoint vectors' canonical hashes, every
changed-field cut's trace digest, source event bytes and the scalar-projection
positive control.

The primary interpreter executes the 13,529-event local suffix on Gaussian
dyadic vectors. Zero operands may skip a linear native kernel because that
kernel maps zero to zero; no cost saving is attributed to this shortcut.
There are 16 child occurrences, nine adapter occurrences, four residual
adapter occurrences and 584 scalar occurrences with nonzero changed outputs.
The other suffix events are still visited and authenticated.

`independent.py` imports neither the primary checker nor predecessor executable
code. Its sparse Gaussian `Fraction` engine independently executes the complete
single-channel suffix, matching the full changed-field trace digest, the 18-bit
guard, all 512 attaining components and every endpoint vector. It also applies
backward adjoints of the literal monomial/line recipes. Starting from coordinate
zero of L93 at the attaining cut, it derives the response to the explicit
witness input. Three additional dual calculations check terminal L75, L93 and
the occupied residual output L337. This is independent arithmetic coverage of
one channel, not an all-child census or an independent review of native semantics.

Controls reject changed global phase, an unframed injection, injection before
instead of after the child, a changed attaining ADD sign, a residual-adapter
orientation error, source corruption, changed injection bytes and unknown
events. Zero and signed dyadic scaling are positive controls. A nonzero complex
adjoint identity tests the independently implemented kernel order; duplicate
JSON keys and boolean/integer receipt confusion are also checked.

## Scope, costs and expansion decision

The certificate concerns the actual **local retained core recipes** at one
nine-axis payload factor, after a single independent completed-child defect.
It checks local physical component values, including nonzero residual outputs.
It does not execute the earlier B1 cover sweeps or validate a global owner
placement, 73-axis embedding, tensor-depth extension or selected supplier.
Those are inherited or open interfaces, and no payload-only replacement for
a cover action is made here: no cover map remains in the studied suffix.

The ideal native recipes and their access interpretation are inherited from
the reviewed QQ16/native work. The numerical replay checks their exact linear
response, not their implementation at the retained recursive tariff.
Actual child-return rounding and correlations, errors within recipes, dirty
input bounds, fixed-format overflow and a receiver-compatible grid remain
unresolved. Nor does this certificate price storage, movement, cleanup,
hosting, the F17 consumer or a complete recursive invoice. These unknown costs
are not zero. [PR2965's conditional output-error transfer](../qq16-producer-defect-transfer/README.md)
is unchanged; its producer accuracy and restoration premises are not supplied.

Family decision: **narrow and stop** after this one handoff. No new search,
controller implementation, selected-frontier change or kappa improvement is
claimed. The selected cold replay, complete predecessor suites, all 7,004
projected error columns and a formal proof kernel were not run. The result is
author-checked with a separately implemented arithmetic check; no independent
human review or hosted CI pass is claimed.

## Open next questions

Can an actual child implementation exclude or correctly price this error
channel? Begin with the named `226 -> 236` child on L344, its returned-value
and defect lattices, and the following receiver operations. A returned-value
grid and a norm bound alone do not establish defect-lattice closure. This
requires a specific child implementation and dirty-input/grid contract.

Can the all-cut local guarantee be extended to the actual global caller's
physical grid while restoring every borrowed helper? Bind the retained-core
embedding and owner placement, then propagate its actual errors and charge
native arithmetic, movement, storage and F17 consumption together. The local
channel certificate does not establish an affordable full producer/consumer.
See `TASK.json` for the structured handoff and stop rules.

## Sources and credit

Base main: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
The claim is in discussion #2727. `SOURCES.json` pins the live certificate,
selected archive, native primitive evaluator and PR3189 receipt. Exact
predecessor heads are recorded in `TASK.json`:

- Tekalign (`tekuuu`), PR3189 `70537595e46444c8a63455523d9851a5efe55385`:
  the child-error lattice criterion, projected witness and explicit native-lift handoff.
- dcharb78, PR3181 `80fc72d14546088e9fce3c06dc12bc67270da0af`:
  ideal scalar interior/grid and adjoint work motivating the audited implication.
- Tekalign, PR3017 `0f493f4c264fbc70ee14364b68af260d858c143c`:
  exact Gaussian-dyadic primitives and local native execution conventions.
- Ross Richardson, PR3067 `e1e28b4070ae52efa5a9d0aa826bc588be7206f2`:
  physical F0 execution/rounding methodology. The new primary event dispatcher
  adapts the PR3017/3067 conventions; it is not an independent native implementation.
- Nick Petalas, PR2965 `526f2c242202b31b15e09a7502dfb8ff757b2bad`;
  Arham Tahir, PR2995/3036; Ali Romman and the joint-query team; Sagar Thakrar,
  DLamdata, ywz65, starship-s, Douglas Colkitt and the retained selected/native lineage.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New work is Apache-2.0. No predecessor bytes or notices are changed.

The checks use managed Python integers and collections, fixed 712 fields and
512 coordinates, bounded serialized input sizes and explicit replay timeouts.
They are research verifiers, not fixed-storage or constant-time machine programs.
