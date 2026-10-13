# complex-571-hpeq5: conditional κ 0.0016127213726553

## Definition

The witness `hpeq5` is the PR558 geometry (112 data columns, h = 9, 504 helpers, 8 centres, 9 stages × 8 replicas = 72 calls) served by 2 provider words, each a pinned base word followed by typed build steps: **ck** (53 calls) = PR571's `frontier-composition/combined-prefix-word/FULL-WORD.json.gz` → `greedy_kernels` (12 multi-cut cold kernels, PR568's constructor) → `frame_coalesce` (6 frame coalescences, PR583's constructor) → `gate_move_coalesce` (2 coalescences, each after moving an addition past commuting additions; 2 moves) → `hyperplane_end` (38 helpers end at a hyperplane U instead of FULL); **atm3** (19 calls) = PR571's `frontier-composition/combined-prefix-word/FULL-WORD.json.gz` → `promote` (40 entrance promotions, PR569's constructor) → `greedy_kernels` (12 multi-cut cold kernels, PR568's constructor) → `frame_coalesce` (6 frame coalescences, PR583's constructor) → `gate_move_coalesce` (2 coalescences, each after moving an addition past commuting additions; 2 moves) → `hyperplane_end` (38 helpers end at a hyperplane U instead of FULL). Each step runs a pinned, unchanged constructor plus its paired omission or negative-control audit; a hyperplane-ended helper starts at its entrance frame E, ends at the hyperplane U, and pays residual width |U| − |E| (every other helper ends at FULL, so its width stays h − |E|). The dispatch (which provider serves each (stage, replica) call), the asynchronous call order and the literal owner map are `data/PLAN.json` (`provider_calls`, `order`) and `data/OWNERS.json.gz`, both nominated by a window MILP with lazy cross-time Hall cuts; the resulting paid profile is {1:182817, 2:34192, 3:22561, 4:14584, 5:4032, 6:4032, 8:576, 12:1, 48:1969} with live 7168, physical 7682 and deficit 2560, giving κ = 16127213726553/10000000000000000 = 0.0016127213726553 (conservative model 0.001612721369804261).

## Files

| file | role |
|---|---|
| `data/WITNESS.json` | **inputs only**: geometry, pinned sources, the provider build chains above, dispatch and call order, and PLAN/OWNERS/recipes by SHA-256 |
| `data/EXPECTED.json` | **expected values only**, all derived by recomputation (`spec.py generate`): per-step word hashes and control counts, per-provider artifacts, programs and profiles, global profile and counts, κ. Bound to WITNESS.json by hash |
| `data/PLAN.json`, `data/OWNERS.json.gz` | dispatch, call order and literal owner map (inputs, pinned by WITNESS.json) |
| `data/recipes/` | the package's own step recipes (inputs, pinned by WITNESS.json); `data/recipes/jp8-step4-hyperplane_end.json` is not referenced by any build chain and is not an input |
| `data/SPEC.json`, `verify.py`, `code/` | the original combined spec and package verifier, unchanged; they still verify the same record |

`data/PLAN.json` carries `"status": "LITERAL_OWNER_NOMINATION_PENDING_ADMISSION"`. That label was written by the owner nominator before admission and is kept unchanged because WITNESS.json pins PLAN by hash; admission is what the verifiers below establish, and the label carries no meaning for them.

## Verification

The pinned sources are not merged; fetch their pinned commits first:

```sh
git fetch origin pull/568/head:pr568 pull/571/head:pr571 pull/569/head:pr569 pull/575/head:pr575 pull/583/head:pr583
git worktree add --detach ../pr568 71c99ac935a33bb7b59a1b4a7af8725a939b0b90
git worktree add --detach ../pr571 b7bdc5a8de18fcf418cfb9c7d83a2b1097a5e4a3
git worktree add --detach ../pr569 897213a855b7fb8a1b8b0e552a2f5c42e6c1b326
git worktree add --detach ../pr575 eac6f7e378ab622dac50a2fd4b7ef6eab014de44
git worktree add --detach ../pr583 89be768f0157f5a3d8e4db69cf1748768605eac9
```

Generic verifier (`research/witness-spec-tools`, PR587 with the `frame_coalesce`, `gate_move_coalesce` and `hyperplane_end` step types). It builds everything from `data/WITNESS.json` and only compares against `data/EXPECTED.json`:

```sh
T=research/witness-spec-tools
python3 $T/spec.py check --package research/complex-571-hpeq5 \
  --source multicold=../pr568/research/complex-multicold \
  --source structural_gain=../pr571/research/structural-gain \
  --source larger_gain=../pr569/research/larger-gain \
  --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing
python3 $T/verify.py --package research/complex-571-hpeq5 --work /tmp/complex-571-hpeq5 \
  --source multicold=../pr568/research/complex-multicold \
  --source structural_gain=../pr571/research/structural-gain \
  --source larger_gain=../pr569/research/larger-gain \
  --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing
# kappa 0.0016127213726553
```

`verify.py` checks the package MANIFEST and every source, PLAN, OWNERS and recipe pin; replays PR558; rebuilds each provider word through its build chain (each step's input and output content hash pinned, 9 steps); localizes each word (hyperplane-ended words through the generalised native chain); then runs binding, the physical owner audit with 23 controller mutants, a fresh finite invoice, both exact moment engines, 114 assembly controls, the phase-timing controls and the generated-identity controls.

The original package verifier gives the same result from `data/SPEC.json`:

```sh
python3 -B research/complex-571-hpeq5/verify.py --work /tmp/complex-571-hpeq5-spec \
  --source multicold=../pr568/research/complex-multicold \
  --source structural_gain=../pr571/research/structural-gain \
  --source larger_gain=../pr569/research/larger-gain \
  --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing
```

Both use only the Python standard library and require assertions (no `-O`). The result is conditional on the inherited assumptions listed in NOTICE.md.
