# Independent review of the single-stream obstruction

Prepared with OpenAI Codex assistance for the second local session on
2026-10-11. That review modified no source files in the existing contribution
and published nothing at the time.

## Verdict

The Lean statements are correct and freshly replay successfully, but they
formalize abstract necessary conditions, not a faithful execution model of the
entire disputed PR448 interface. The existing README states this limitation
accurately. In particular, this package does not establish an impossibility
theorem for PR448's priced word or reproduce RaD's finite program enumeration.
Its strongest directly relevant statement is the single-owner residual support
obstruction. No mathematical error was found in the proved statements.

The fresh independent replay used the following command, with installation
and output paths shown as portable examples:

```sh
python3 research/lean-single-stream-obstruction/replay.py \
  --lean /path/to/lean-4.33.0-linux/bin/lean \
  --receipt /tmp/interface-review-replay.json
```

Result: PASS; one fresh module, all 15 expected transitive axiom reports,
five mathematically rejected negative controls. The recorded proof SHA-256 is
`c7d41804b1fed5b4349ff89f6d244283aa004f7e6413b6a8643fdb910ae32f29`.

## Pinned sources checked

- Main: `12a4934d15006e8c10f9b2264f13f8f341be802b`.
- PR397: `cb6455fa1e9af68be47c33948d3d1a6f0717a5e4`.
- PR448: `359022bcd71143e45d48def0dd005bf67f339aa7`.
- Jacob Sussman: `9c94857bbaee886f8649edee0bc2d3c738f9555e`.
- PR442 API snapshot in this session:
  `4e16d001d505d4f21dd2bcfc44591f9be4c279bd`.

The first four hashes were independently read from local Git HEADs. PR442
text references below are the inherited files present in the pinned PR448
checkout; identifying them does not assert that this review compared every
byte to the separate PR442 head.

## Findings, in order of significance

1. **The missing source-to-model refinement remains the main obligation.**
   `SingleStream.lean:24-25` assumes that a read factors through one projection;
   `SingleStream.lean:62-64` assumes every visible update ignores hidden state.
   No theorem proves those premises for a lowered repository instruction or a
   complete GWord. This restriction does match a fixed helper operand under
   a verified ownership invariant. It does not describe the whole upstream
   language: Sussman's `Work/Block/Word.lean:27-30,197-200` includes arbitrary
   scalar role mixing through `localM`, and
   `Work/GFrame/Engine/Route.lean:56-60` admits cross-role gates when frames
   agree. A separate proof must establish which roles may feed the particular
   operand and throughout which interval. See the existing explicit scope
   warning in `README.md:84-91`.

2. **The dirty-read witness is illustrative, not the disputed operand.**
   `SingleStream.lean:83-101` proves that scalar `x+a+b` depends on both
   independent inputs. PR448 splits *address-coordinate residual directions*
   between entire physical stream arrays; it does not define the replacement
   helper payload as a sum of two scalar values. RaD's pinned
   `job1_stream_model.py:14-21,89-94,141-145` (upstream URL and hash in
   [AUDIT.json](../lean-single-stream-obstruction/AUDIT.json)) instead executes
   a wrapper with a genuine helper read `x += A h`, residual action,
   inverse cancellation, and target action. A source binding would have to
   specify the proposed multi-stream helper read and prove its dependence
   witnesses; the scalar theorem does not supply that binding.

3. **Gate failure cannot imply endpoint failure.**
   The wrapper's dirty reads cancel. Its endpoint on the live target is `T x`
   regardless of the original helper value. Consequently
   `dirty_read_no_local_program` does not rule out that endpoint. Indeed the
   definition `Step` permits the single abstract step
   `visible (x,a) = (T x,f a)`, `hidden _ b = g b`, which realizes the whole
   endpoint `(T x,f a,g b)` while satisfying visible noninterference. This is
   compatible with, rather than a counterexample to, the proved theorem.
   `README.md:77-82` already explains the cancellation caveat. RaD compares
   complete live-stream endpoints including remainder children
   (`job1_stream_model.py:177-218`); the Lean package does not yet do so.

4. **Residual support is a sound local abstraction, with a useful source
   correspondence.** `split_residual_no_owner` (`SingleStream.lean:114-132`)
   captures the fact that a single role-local operation preserves every other
   role. Sussman's `DirectionalWords.lean:12,31-32` represents data as one
   array per role and `roleAct` changes only its named role;
   `Work/GFrame/Engine/Letters.lean:151-154` applies permutations and phases
   through `roleAct`. An address adapter acting on one role cannot change the family
   owner. PR442 specifies owner `(F,d·σ⁻¹)` with the same `F`
   (`idle-axis-hosting/PROOF.md:43-45`), and its generators store exactly one
   family plus a route descriptor (`bit_hosted.py:75-83`,
   `complex_hosted.py:49-57`). PR448 stores the second family *inside* that
   descriptor while retaining the first as the owner (`bit_split.py:89-97`,
   `complex_split.py:50-58`); its audit explicitly checks this representation
   (`audit_split.py:53-59`). Neither the Lean package nor these schema checks
   defines a physical implementation of that second-family access.

5. **The bit and complex witnesses are small exact examples, not the full
   coordinate theorem.** `SingleStream.lean:134-172` uses a two-element bit
   address alphabet and one complex coordinate. RaD's bit model uses
   arbitrary `q`-ary addresses and tests `q=3,5`
   (`job1_stream_model.py:51-62,223-225`). The generic support lemma applies
   once actual nontriviality witnesses are supplied, but the package does
   not prove all nonempty coordinate factors nontrivial at the construction's
   parameters. Its README describes them as one-coordinate instances, which
   is appropriately limited.

The author's acknowledged gap in PR448 remains independent evidence of the
claimed bound's unestablished status. It must not be promoted to a stronger
consequence of these Lean theorems.

## Requirements for the proposed positive whole-hosting lemma

PR442's surviving argument is in
`research/idle-axis-hosting/PROOF.md:12-57` in the pinned PR448 checkout
identified above. The finite window
finder ignores idle children (`hosting_core.py:13-27`), relying on their
commutation rather than literal absence of operations on a family. A useful
formalization should therefore allow intervening idle factors and prove:

- Exact coordinate factorization on one stream, over arbitrary payloads and
  arbitrary address-coordinate types. For swaps, disjoint masks combine by
  union; masks with overlap combine by symmetric difference. State the
  disjointness condition when using union, and the subset condition when
  using a remainder. For several slots, pairwise disjointness and exact
  coverage of the removed set must be explicit.
- A complete invocation endpoint, valid for every initial dirty value,
  factors into its other-role action and exactly the hosted residual on the
  selected physical family. Move this *complete macro*, after cleanup;
  internal dirty gates can read the hosted family and cannot in general be
  moved individually. Restored scratch must be included in the endpoint
  contract or explicitly hidden by a sound projection.
- Each intervening macro commutes with that residual on the *complete
  state*. Merely preserving the family's output is too weak: on state
  `(f,z)`, `W(f,z)=(f,z+f)` preserves `f`, but fails to commute with
  `R(f,z)=(-f,z)`. Sufficient cases are an independent map on other roles,
  or another coordinate factor in the same chart. For conjugated factors,
  prove common-chart or actual commutation conditions; different names for
  coordinate sets do not establish commutation across arbitrary charts.
- After moving hosted residuals through the allowed window, compose them
  with the child's exact remainder and recover the original complete child.
  This equality is pointwise for arbitrary correlated inputs because it is
  an equality of full state transformations.

Instantiation still needs the actual owner injection (including absence of
aliasing with live data/scratch within an invocation), coordinate route
conjugacy, and the ordering of the cover sweeps. The parent construction
emphasizes phase-major cover execution in
`research/five-stage-gen4-banks/proof/INTEGRATED_PROOF.md:23-25`. A local
absorption theorem can close the algebraic/window obligation while keeping
these compiler refinements and every cost or κ claim explicitly separate.
