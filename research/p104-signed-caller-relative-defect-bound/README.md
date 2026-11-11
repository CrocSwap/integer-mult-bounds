# Relative defect bound for signed P104 caller edits

**NO VERIFIED GAIN. Exact conditional κ change 0%.** The exact
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
signed caller reused by [#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277)
excludes all 15 nonempty Type A subsets of four QUERY removals and all
15 nonempty Type B subsets of four rank-nine IDLE_ODD demotions to
rank-eight IDLE_ONE. The 17 literal J blocks and original 36-role ports
stay fixed. The proof permits arbitrary invertible q-even mixing
within each port. Zero subsets remain unresolved in either family.

At unit body values and q = ±1, each required relative endpoint is
negative identity. The [relative defect-slack proof](PROOF.md) shows
that the sum of defect ranks must be at least 38 in both families.
Type A loses one rank per removed QUERY. In Type B eight subsets fail
the determinant condition, one fails ordinary defect rank, and six
fail rank saturation. The independent matrix checks verify both
literal specialized endpoints and the fixed J factors, then replay all
literal mutations. These finite mutation checks are controls for the
general obstruction, which allows arbitrary q-even mixing.

## Price and evidence

Each primary replay saves its directed complete #7277 price before
testing support. Type A has 96 ports, so removing the four QUERYs
would save 384 raw rank-one units if feasible. Type B has eight
ports, so demoting all four idles would save about 31.63562 raw units
if feasible. All other terms remain in the signed 17-copy invoice.
The exact intervals and crossing pin are in the
[Type A price](receipts/type-a/PRICE.json) and
[Type B price](receipts/type-b/PRICE.json). The certified savings upper
after support is zero. The complete comparable witness remains
κ = 0.003645669928698 on #7277.

The [Type A support](receipts/type-a/SUPPORT.json) and
[Type B support](receipts/type-b/SUPPORT.json) receipts record every
subset and J block. The separate
[Type A phase](receipts/type-a/PHASE.json) and
[Type B phase](receipts/type-b/PHASE.json) receipts cover the original
specialized endpoints, local factors and mutation controls. A
synthetic negative-identity product built from suitable reflections
passes the saturation control, while the unchanged-rank shear or
rotation illustrates the obstruction.

## Replay

Use CPython 3.12 with assertions enabled and the standard library.

~~~sh
python3.12 -B scripts/research_package.py --package research/p104-signed-caller-relative-defect-bound
python3.12 -B scripts/check_research_commit.py --package research/p104-signed-caller-relative-defect-bound --check-modes --check-source-history
~~~

A Git-free export can run
`python3.12 -I -B research/p104-signed-caller-relative-defect-bound/replay.py`.
[PROVENANCE.json](PROVENANCE.json) records public commits, paths, Git
blobs and SHA-256 for the native word, crossing receipt, caller and
retained exact-grid phase reference. The bundled scripts and receipts
are SHA-256 pinned by package-relative path. No external checkout,
prior temporary state or network fetch is required.

## Predecessors

[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
at `07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies the signed
caller and phase reference. [#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277)
at `ed090b57ed88f8859e5ff4643645099e6ba856ea` supplies the exact
comparable invoice. [#7144](https://github.com/CrocSwap/integer-mult-bounds/pull/7144)
supplies a separate fixed-caller body-gauge rigidity proof and leaves
phase-only edits open. [#7295](https://github.com/CrocSwap/integer-mult-bounds/pull/7295)
bounds rank-additive caller idle stock, and
[#7296](https://github.com/CrocSwap/integer-mult-bounds/pull/7296)
bounds displaced volume for one signed Type B idle pair. Earlier
local-only Type A work applies saturation to body derivatives to force
HOST support. This package instead applies the two-q relative factor
inequality to the fixed caller. OpenAI Codex and subagents materially
assisted.

## Open next questions

Can one existing paid J supply higher relative phase rank through a
changed provider at a favorable complete price? Pin that provider
contract and price the compatible stock before building. A surviving
proposal still needs arbitrary-input signed action, ownership,
restoration and complete routing, precision and tape pricing.
Cross-port mixing is a separate mechanism.
