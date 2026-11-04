# A checked single-stream interface obstruction

This standalone Lean contribution supplies a small acceptance test for a
fixed-owner helper interface: which reads and residual actions can be
implemented when the helper operand has access to only one physical stream?
It adds no exponent claim. Prepared with substantial OpenAI Codex assistance;
Apache-2.0 under the repository license. Attribution is in `NOTICE.md`.

## Checked statements

`SingleStream.lean` imports only the installed `Std` library.

- `realizes_iff`: a read can use one owned stream exactly when it is constant
  on the fibres of that stream's projection. The stream may be an entire
  array, and the local read may be any function, including address adapters.
- `no_owner_of_two_dependencies`: two explicit witnesses of dependence on
  independent streams exclude both fixed owners.
- `run_visible_eq`: any finite sequence whose visible update cannot read
  hidden state preserves visible indistinguishability. This is a universal
  induction over lists, with no length or coefficient bound. Hidden updates
  may depend on visible and hidden state. Visible state may contain scratch.
- `dirty_read_no_owner` and `dirty_read_no_local_program`: the gate-level read
  `x += a+b` cannot be obtained in those interfaces for arbitrary independent
  `a,b`. The latter permits arbitrary fixed-length sequences of operations.
- `split_residual_no_owner`: an operation on one stream cannot act as two
  nontrivial factors on two independent streams. Exact one-coordinate bit
  address-swap and complex Gaussian-phase instances are included.
- Positive controls implement whole-helper reads and two separate residual
  operations. An integer dirty wrapper with two helper reads, sign-flip
  residuals, inverse cancellation and an arbitrary target map has its exact
  endpoint, also pointwise for correlated inputs.

The generic factorization, list induction and bit/complex support results
use **no axioms**. Three integer arithmetic results use only `propext` and
`Quot.sound`. All 15 transitive axiom reports are checked by the replay.
There are no project axioms, `sorry`, `native_decide`, or Mathlib dependencies.

## Why this target

Main was inspected at `12a4934d15006e8c10f9b2264f13f8f341be802b`.
PR397 at `cb6455fa1e9af68be47c33948d3d1a6f0717a5e4` already proves the
normalized scalar B_K bridge and binds B3, assuming complete invocation
contracts. Its fresh local replay passed all three modules, 22 axiom reports
and five negative controls. Repeating that algebra would duplicate work.

Jacob Sussman's `wht-power-saving-lean` was inspected at
`9c94857bbaee886f8649edee0bc2d3c738f9555e`: the README, generalized engine
letters/routes and carrier invocation theorem were read. His RAM Fourier/WHT
results and their existing proofs are distinct from a new integer-multiplication
claim. His full Mathlib development was not rebuilt here.

PR448 was inspected at `359022bcd71143e45d48def0dd005bf67f339aa7`, including
its latest discussion. In the [author's acknowledgement](https://github.com/CrocSwap/integer-mult-bounds/pull/448#issuecomment-6113842081),
the split presupposes a read/write interface across two streams that the hub
has not stated; a second helper changes the local word and must be paid.
The advertised gain is **unestablished**. The new proof does not assume that
interface or use its numerical certificate as evidence of realizability.

The scan covered the titles/bodies of all 502 open/closed PRs returned by the
API, plus relevant main Lean sources and PR430's structural Lean module.
PR487's exact port bijection and PR488's input preparation concern other
obligations. No matching completed Lean single-stream read/support obstruction
was identified in the inspected material. This is a bounded nonduplication
audit, not an assertion about every pending implementation or global priority.
`AUDIT.json` pins the sources, discussion and inspection scope, including
the hash of the original full API snapshot. That snapshot was retained
locally during the initial audit and is not included in this package.

## Assumptions and limits

The formal interface assumes independent arbitrary stream values, a fixed
owner, and no flow of hidden values into visible state. The supplied witnesses
are essential: a read insensitive to the other piece, or inputs restricted
by a correlation such as `b=a`, need not have this obstruction. Encoding both
streams into one value, rebinding the helper, routing data between streams,
or admitting another helper changes the model and requires separate accounting.

The program theorem concerns implementing the **dirty-read gate**; helper
reads can cancel in a complete word, so failure to implement that gate alone
is not a proof that every whole-word realization is impossible. The bit and
complex theorems concern a **single owned-stream residual operation**; two
operations on two streams do implement the product. They do not forbid a
compiler from emitting such a sequence and charging it.

This is not a translation or certification of PR448's word, owner table,
remainder children or charts. It does not formalize RaD's whole-program matrix
enumeration. The original pinned Python enumeration was separately replayed
during the audit: all 152 tested single-register programs failed equality
over 18 split cases, while whole-hosting and two-register controls passed. The integer two-helper control is a scalar example, not the
actual D_S/C_S wrapper. Connecting these abstract premises to a particular
physical invocation remains a reviewed proof obligation. No register-cost,
all-size compiler, analytic-transfer or integer-multiplication theorem is proved.
No new bridge mechanism or mathematical priority is claimed.

## Reproduce locally, offline

Use an already installed official Lean **4.33.0** executable (not a launcher
that downloads toolchains), and Python 3.9+. The runner downloads nothing.

```sh
python3 research/lean-single-stream-obstruction/replay.py \
  --lean /absolute/path/to/lean-4.33.0-linux/bin/lean \
  --receipt /tmp/single-stream-replay.json
```

Replay checks the proof-source hash, compiles in a fresh temporary directory
at trust level zero with inherited extra Lean paths removed, checks every
axiom report, then asks Lean to reject five false mathematical controls:
missing either dirty piece, bit and complex single-owner splits, and a wrong
cleanup sign. These are explicit failure witnesses, not a whole-program search.
Each compilation has a 60-second timeout. Temporary objects are removed.
`replay-result.json` records the executed local check. Compiler and installed
standard-library correctness remain trust boundaries; this is not a CI report.
See `VALIDATION.md` for repository-level checks and their scope.
