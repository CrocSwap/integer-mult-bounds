# Physical replay of the P104 fixed-boundary variant

`verify_physical.py` replays the native physical, ordinary and outer checks for graph `eb8a9cbf477308f8baa949a780a5a3b6d998ff9a64934591839a4b5690186702` on the fixed #7761 2,048-call caller. It binds the caller word `3b326189234984d7797566fa4732d4e2698db778f117cd09bb5654ea740c5563` and the predecessor native graph `c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84`. [Caller package at the pinned head](https://github.com/CrocSwap/integer-mult-bounds/tree/d5219594c9b0e80c002a75e79b85766256496b07/research/p104-mixed-batch-boundary)

## Run from public sources

Use CPython 3.12, Git and the full public #7761 package. The reconstruction script is at the root of this kit. A sparse or partial Git repository also works when it already has the four pinned canonical blobs available locally. The verifier reads the two Clifford modules and arithmetic scripts at `e54523517d0f03e58352e647c403a5af3e525a57` from Git and stages them temporarily after checking their blob and SHA-256 pins. The #7761 package carries the required #7756 files under `pr7756/`. [Canonical base](https://github.com/CrocSwap/integer-mult-bounds/tree/e54523517d0f03e58352e647c403a5af3e525a57) · [Native predecessor](https://github.com/CrocSwap/integer-mult-bounds/pull/7756)

Fetch the parent and create its worktree. In these commands `kit` is the path to the directory containing `verify.py` and `physical/`.

```bash
kit=/path/to/p104-paid-relays
workspace="$PWD"
repo="$workspace/upstream"
checkout="$workspace/parent-7761"
parent_head=d5219594c9b0e80c002a75e79b85766256496b07
base=e54523517d0f03e58352e647c403a5af3e525a57

git clone https://github.com/CrocSwap/integer-mult-bounds.git "$repo"
git -C "$repo" fetch origin refs/pull/7761/head
git -C "$repo" cat-file -e "$base^{commit}"
git -C "$repo" worktree add --detach "$checkout" "$parent_head"
parent_package="$checkout/research/p104-mixed-batch-boundary"

python3.12 -I -B "$kit/verify.py" \
  --parent-package "$parent_package" \
  --variant seventeen \
  --write-graph "$workspace/applicant.json" \
  > "$workspace/reconstruction.json"

python3.12 -I -B "$kit/physical/verify_physical.py" \
  --parent-package "$parent_package" \
  --repository "$repo" \
  --graph "$workspace/applicant.json" \
  --output "$workspace/physical-replay.json"
```

The replay accepts canonical JSON or gzip and binds the decoded graph to the default candidate pin. To check another graph with the same public charts, supply its exact canonical SHA-256 using `--expected-graph-sha256`. The baseline and caller pins stay fixed.

## Checks

- Rebuild the frozen native predecessor and independently recount its paid and productive ranks. Authenticate the caller expansion, baseline physical receipt, comparison invoice and qualification source files.
- Lower each changed chart transfer from the canonical frame. Check absolute phase, signed Pauli action and every one of the 512 exact Gaussian columns in both directions. Perturb the global phase as a rejection control.
- Replay the full applicant integer-grid native map on all independent owners and the held schedule with protected inputs, sender alias rejection and guarded `CLEAR`. Recompute exact scalar services and the fixed caller’s 2,048-call ownership, ordinary phase adapters, primitive component envelopes and common root.
- Rebuild both full signed invoices and ordinary budgets. Compare productive and paid ranks and itemize changed ordinary costs. Recheck the baseline compiler and applicant's directed price, depth guard, selected BIT margin, 54 strict inequalities and four functional outer predicates.

`status: passed` records the finite replay. The separate `meets_target` field reports the comparison with `0.00383069832566`. The five public conditional interfaces remain the premises of the bound. [Predecessor qualification and proof](https://github.com/CrocSwap/integer-mult-bounds/pull/7761)

## Attribution

The wrapper adapts the round’s fixed-boundary physical replay and reuses the public #7761 qualification and #7756 physical, scalar and mixed caller code. Ali Romman and the credited prior contributors supplied the baseline and native reconstruction. The retained Clifford, physical, caller and interval engines preserve their upstream authorship and Apache-2.0 notices. The changed-route replay follows the #7756 catalogue’s use of the original Clarke-style compiler and independent exact Gaussian checker in the canonical repository. [Native source credits](https://github.com/CrocSwap/integer-mult-bounds/blob/6b0044123aad114cf71ca2bb0e98741e5a27c7b5/research/p104-parallel-bank-punctures/CREDITS.md) · [Inherited licenses and notices](https://github.com/CrocSwap/integer-mult-bounds/tree/d5219594c9b0e80c002a75e79b85766256496b07/research/p104-mixed-batch-boundary/pr7756)
