# PR256 complex program: reproduction and proof consistency audit

This adds a separate reproduction of Chafik Boukhalfa's PR256 and its instantiation
of Jacob Sussman's Lean framework. **No new multiplication kappa, network, or
Fourier exponent is claimed.** The contribution is a reproducible audit linking
the two source packages, exact arithmetic checks, and retained build evidence.

## Pinned sources

| Source | Revision | Role |
| --- | --- | --- |
| [CrocSwap PR256](https://github.com/CrocSwap/integer-mult-bounds/pull/256) | `db3f75cdc5f03f3131d48fb220f6bf1958404ff3` | Explicit complex program and source regeneration |
| [Fourier proof PR2](https://github.com/jacobalansussman/wht-power-saving-lean/pull/2) | `fd19e46b728faa414cbfbf91b01a6a0b7903375d` | Sussman's framework with Boukhalfa's PR233 instantiation |
| [OpenAI formal sources](https://github.com/openai/math/tree/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean) | `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb` | Original model, Fourier reduction, and challenge |
| [Downstream reproduction](https://github.com/shea256/fourier-transform-below-nlogn/tree/a101b363b38e6bf7d309042c94ba5fa18a424fad) | `a101b363b38e6bf7d309042c94ba5fa18a424fad` | Ryan Shea's checks, source audit, and build receipts |

The proof extends Sussman revision `f010392c923279e3dd59ef3aa5fedad23affc5fd`.
Lean is 4.34.1; Mathlib is `d13f23b723b8a846827a245b89c10fc7d3f11612`.
The complete 456-file proof source archive is included, without compiled objects.
Only the PR256 inputs needed for the finite audit are copied here; its complete
producer is available at the pinned revision above. Original notices are retained.

## Offline finite audit

From the repository root, using Python 3.11 or later and no third-party packages:

```sh
python3 -B research/pr256-fourier-audit/verify.py
python3 -B research/pr256-fourier-audit/test_audit.py
```

The first command:

1. Checks source pins and runs Sussman's unmodified `gx.check1` on the explicit
   PR233 program: 12,052 registers, 18,248 frames, 52,300 gates, and 69,683
   invocation blocks. Exact scalar replay covers all source columns; restoration
   of arbitrary dirty scratch is supplied by the Lean invocation theorem.
2. Reconstructs the five-stage histogram and checks `m=110`, `W=14692`, rank
   1613040, deficit 3080, 358975 children and maximum child width 46.
3. Independently bounds the normalized moment using exact rational logarithm and
   exponential enclosures at `a=7547361/10^10`. It checks the Lean engine's
   finite-fill correction at `s=40`, the positive Fourier gap
   `a - delta = 1/10^10`, and failure at `7547365/10^10` for this histogram.
4. Requires the PR256 and Lean programs to agree in every mathematical field
   (only the descriptive `derived_from` string differs), then checks the Lean
   histogram and exponent literals. It compares the Fourier challenge with the
   original after accounting for comments, seven renamed declarations and the
   stronger exponent.
5. Checks all 89 imported OpenAI Lean modules, the original challenge and the
   toolchain against the 91-file origin ledger. These were fetched separately
   from the immutable OpenAI revision during the recorded source audit.
6. Binds the historical reproduction receipts to their compressed logs and all
   456 archived source hashes. Checking a recorded receipt does not rerun Lean.

Optional full-checkout comparisons require no network:

```sh
python3 -B research/pr256-fourier-audit/verify.py \
  --program-source /path/to/pr256-checkout \
  --proof-source /path/to/pinned-fourier-checkout \
  --openai-source /path/to/pinned-openai-checkout
```

They compare the 20 program-package files, 456 proof-source files and 91 original
OpenAI files with the pinned ledgers, irrespective of the checkout's branch name. The default audit
does not rerun the producer or a full Clifford/DFT computation.

## Reproducing the Lean build

Install `leanprover/lean4:v4.34.1`, then run:

```sh
python3 -B research/pr256-fourier-audit/reproduce_lean.py \
  --work-dir /tmp/pr256-lean-rebuild --lake lake --threads 2 \
  --receipt /tmp/pr256-lean-rebuild-receipt.json
```

This extracts the complete pinned source (or checks existing source bytes),
downloads the pinned Mathlib cache, regenerates the 41 certificate and 14
Fourier-chain files, builds the proof, audits axioms, and runs upstream
`tools/Compare.lean` for WHT, DFT and convolution. The two large scalar reductions
are staged sequentially to reduce peak memory. Allow several GB of storage and
substantial memory; the recorded reproduction used a 32 GiB macOS arm64 machine.

The original fresh project build passed in 2625.5 seconds, with Mathlib's compiled
cache. The WHT and Fourier comparisons passed in 33.7 and 42.6 seconds. The three
audited final theorems used only `propext`, `Classical.choice`, and `Quot.sound`.
The original combined build temporarily paused one large scalar reduction until
the other completed; it then resumed successfully, without changing source.
The script now stages those targets sequentially. The receipt retains the actual
original commands and is not relabeled as a new run.

The full PR256 producer regeneration also passed (188.6 seconds), using Python
3.11, NumPy 2.3.5 and SciPy 1.17.0. To rerun that separately:

```sh
git clone https://github.com/chafreaky/integer-mult-bounds /tmp/pr256-source
git -C /tmp/pr256-source checkout --detach db3f75cdc5f03f3131d48fb220f6bf1958404ff3
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  uv run --python 3.11 --with numpy==2.3.5 --with scipy==1.17.0 \
  python -B /tmp/pr256-source/research/gcert-program-233/verify.py
```

## What this establishes for multiplication

| Evidence | Established scope | Multiplication obligations remaining |
| --- | --- | --- |
| Exact program and histogram checks | The pinned finite complex program and its five-stage accounting agree with the formal input | No bit-side construction or outer multiplication assembly is checked here |
| Lean project and statement comparisons | The upstream WHT and all-length exact DFT/convolution theorems in OpenAI's family-130 RAM model | Finite precision/recovery, bit costs, fixed-tape implementation and the inherited multiplication-specific all-size interfaces are not proved |
| OpenAI source comparison | Imported model/reduction files match the identified OpenAI revision | Human assessment of formal statements and assumptions remains separate |
| Receipt and log hashes | The recorded successful runs are bound to these sources | Hashes alone do not independently attest that an execution occurred |

The Fourier theorem has `delta=7547360/10^10`. It is an exact-complex-arithmetic
result with supplied roots and unrestricted coefficients, not a multiplication
theorem or practical FFT benchmark. The historical reproduction ran neither the
official Linux comparator nor a second kernel and is not independent human
mathematical review. Boukhalfa later reported official-comparator success in
[`837dc313`](https://github.com/chafreaky/wht-power-saving-lean/commit/837dc3130adc79f7b7ab4ddd56c15576bbd766b0);
that documentation-only update is distinct from this pinned local reproduction.

See [NOTICE](NOTICE) for attribution and [VALIDATION.md](VALIDATION.md) for the
checks of this contribution. The root selected result and all existing witnesses
remain unchanged.
