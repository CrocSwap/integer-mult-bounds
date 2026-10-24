# Three-SWAP cap-two physical interface and direct-comparator ceiling

**Source-pinned research package.** The physical interpretation of Nick Petalas's
[#5083](https://github.com/CrocSwap/integer-mult-bounds/pull/5083) needs a stronger
price gate than its sound restricted formal-word comparison. With reversed BIT
generators the target is an ordinary swap, and the retained source supplies a
direct implementation. Beating that explicit recipe requires

```
B < (2F + 6Q - Delta)/4,       Delta = wNew - wDirect.
```

This is a scoped necessary comparison against a constructive upper recipe.
The recipe is not asserted optimal. No actual cap-two supplier, bound eligible
caller, changed P/T inventory, universal physical obstruction or new κ follows.
The selected record remains unchanged. The retained independent review checks
the exact arithmetic and orientation; it does not certify a physical supplier.

## Result and physical boundary

The formal source has owner-rank profile `(2,2,1,2,2)`, price `c1+4c2`, and
comparator `3c1+3c2`. Its formal saving `2c1-c2` is credited to Nick Petalas.
That theorem and its formal-word checker are not duplicated or rerun here.
Ross Richardson's GL2(F2)/S3 bridge identifies `a=(12), b=(23), s=(13)`;
David Arias's rank-priced theorem and the retained group/cut lineage remain
predecessor work.

The missing attaining ABI is

```
Cap2(g,{i,j}): (u0,u1,u2,dirty...)
  -> (rho_f(g)u_i, rho_f(g)u_j, all other original fields unchanged), g=a or b.
```

Each owner is an arbitrary independent payload function on the same complete
address range. Two original inputs require two independent transformed outputs;
the unselected active owner, arbitrary dirty owners, untouched rows and every
spectator must each be restored. A sum of owners, a zero input or a discarded
owner does not meet this ABI. Entry/exit charts, atom order, orientation,
weights, width lifting, buffers, copies, reset and all outputs must be explicit.
Scalar owner rank, address width, logical volume, column multiplicity and native
recursive-child rank are separate dimensions. The existing BIT supplier's
width-`rf` call acts on one role at volume `V/W`; putting two owners in ROW
values increases volume to `2V/W`. It does not establish the cap-two discount.

For unweighted reversed generators, write `C=C_f`, `C^2=I`. Source convention
reverses atom positions, without reversing digits inside an atom. Then

```
(x,y,z) --F12--> (Cy,Cx,z) --F23--> (Cy,Cz,x) --F12--> (z,y,x).
```

Thus `aba` produces ordinary `J13` and restores the middle chunk. The source's
`J_A=R_tail F_A R_tail` recipe gives one width-`f` reversed call and two
width-`floor(f/2)` calls, all on the same complete logical volume. Put `F,Q`
for their complete prices, `B` for the complete width-`f` cap-two transaction,
and `wNew,wDirect` for costs outside these complete calls only. The candidate
cost is `F+4B+wNew`; the available direct upper recipe costs `3F+6Q+wDirect`.
Their strict comparison gives the displayed threshold. In-call work must not
be charged again in `Delta`; unknown outside work is unknown.

Uniform prices must hold for both labels and every selected owner pair.
Otherwise use the actual sum, initially `F_a+2B_a+2B_b`, and any further
pair-dependent terms. The unweighted identity does not identify different
ancestor-dependent weight arrays. Weighted jobs require matched actual weights,
reversed pairing, orientation, precision and complete returned inventory.
For raw-F targets the word has the wrong endpoint: the particular wrapper
adds six half-width calls and loses against three direct F calls when `B>=F`.
A proved caller layout absorbing reversals would be a changed premise.
For ordinary-J generators the direct three-target competitor is already `3J`.

## Exact conditional tariff screen

Under the separately declared hypothetical same-volume model

```
F=K*f^(1-C), Q=K*floor(f/2)^(1-C), B=2^(1-C)*F,
K>0, H_0=0, Delta=0, 0<=C<=17/5000,
```

the nominal cap-two price loses. The exact integer inequality
`399^5000 < 2^4983 * 200^5000` proves `2^(1-C)>399/200`.
The necessary price satisfies `B/F<333/266`, while the hypothetical nominal
price is `B/F>399/200`; the normalized recursive disadvantage exceeds
`19767/6650`. Even widths attain the underlying bound; odd floors strengthen
it, and width one is covered with `Q=0`. The checker includes sign reversal
outside the screened regime. These conclusions reject this tariff/comparator
combination, not every cap-two implementation. A sufficiently favorable actual
outside-cost difference or different complete B could change the full decision.

## Evidence, provenance and reproduction

The scientific packets under `evidence/` are exact retained bytes:

- [Physical ABI and feasibility report](evidence/physical-interface/REPORT.md),
  its complete source snapshots and original manifests.
- [Direct-comparator derivation](evidence/outputs/new-approach-ceilings-20261023/DIRECT-COMPARATOR-PROOF.md),
  exact checker/receipts, candidate interface and baseline obligation ledger,
  with all 16 scientific snapshots.
- [Independent direct-comparator review](evidence/outputs/new-approach-verification-20261023/DIRECT-COMPARATOR-REVIEW.md),
  unchanged direct-only checker and both frozen direct receipts.

`EVIDENCE.json` binds all 51 retained files. Original reports and proposed drafts
retain historical local status and worker names; they are evidence of that
checkpoint, not current publication text or instructions. The full original
`FREEZE.json` is retained with SHA256
`22deada00ef988bdc99b7fd01480fc86136111a8483513d00ce2ae0eea711975`.
Its unrelated centre-p2 entries are not vendored or replayed in this package.
The direct-only checker authenticates only this package's direct source packet.

The originating catalogue card `bit-new-register-model` and selected record
remain pinned to canonical main `81e9bd69e4a5b00ba9c713a1620e36d576d5522e`.
The scope is explicitly **changed** to a physical ABI/orientation/price audit.
Root supplied the bounded overlap checkpoint and owns the final live/publication
check; this package does not claim a complete current board survey or novelty.
It complements #5083 instead of claiming its formal construction again.

The original #5083 source head
`d2b3f35275cab6fbf18bee40e3fb411496732e54` was not an ancestor of that canonical
base. Provenance-only merge `ea40685a28ebf1489f74e91e39b143930dbfee53` uses
`git merge -s ours --no-ff` to retain that exact history, with an unchanged tree.
The separate arithmetic/source head
`20bb93cd990d2ff683e4d0fc56b87a42cd5d3296` was already ancestral.
`SOURCES.json` keeps original paths and original head pins as provenance, and
pins every retained live input at its same path in ancestor commit
`a84a22d3f6e0ce75a9e433c6438f01cf25ed384c`. No silent source repin or scientific
rewrite is used. Package `.gitattributes` disables text conversion to preserve
scientific bytes, including CRLF.

Standard-library Python 3.12; run either from the repository root:

```sh
python3 -I -W error -B research/three-swap-cap2-physical-ceiling/verify.py
python3 -I -O -W error -B research/three-swap-cap2-physical-ceiling/verify.py
python3 scripts/research_package.py --package research/three-swap-cap2-physical-ceiling
```

Both direct commands print `PASS_CAP2_PHYSICAL_CEILING_PACKAGE` in about two
seconds each locally, with a 180-second registered cap each. The adapter copies
unchanged scientific code and packets into a private temporary layout matching
their original relative paths. It captures stdout, compares the author result
and independent generated direct receipt byte for byte with frozen receipts,
checks all original manifests and retained freeze entries, and rejects a real
corruption of a frozen source in both unchanged checkers. It verifies package
bytes before and after. Scratch results are removed. No Git, network, compiler,
Lean, native execution or third-party library is needed for direct replay.

The retained author controls cover 40 exact rational factor/sign cases,
64 floor cases, five complete-tariff scenarios, six semantic rejections and
three reserve controls. The independent review adds exact orientation/dirty
spectator cases and independent rational economics. Normal/optimized results
must equal their corresponding frozen receipts. This bounded check does not
execute the source author's formal-word verifier or admit all-width physical
implementations.

For a committed package, also use the repository's byte/source-history preflight
and official exporter. Transport integrity and ancestry availability are separate
from mathematical validation. Root retains local validation receipts and the
checked Git-free export; publication and hosted CI remain separate actions.

## Remaining obligations and stopping rule

No eligible chronological occurrence or autonomous output inventory is bound.
No actual complete `F,Q,B,wNew,wDirect` bill, strict child contraction, finite
work, preparation/routing/storage/cleanup, precision/rounding amplification,
ordinary BIT stock, outer rows, both paid tails or funded compiler reserve is
supplied. In the complex ABI, Fourier rank and exact Clifford phases differ
from scalar owner rank and binary permutation labels; a BIT-only improvement
does not establish a changed complex supplier. The retained #4610 obligations
remain partial/conditional. No root search, changed histogram, emitter, physical
fixture or new P/T/κ is reported.

Stop implementation expansion until the complete bill for one actual occurrence
passes the strict direct-recipe comparison. A positive relaxed moment must also
retain `T<=U`, `P>=L`, hence `M<=U-L`, and the strict reserve screen
`L<(1-e)U`; passing an optimistic bound is not admission.

## Open next questions

The structured questions in `TASK.json` give relevance, first steps and blockers.
First name one eligible caller, actual cap-two ABI and complete prices, and test
the strict inequality. A failure stops that candidate; unknown prices remain a
blocker. Only after a pass should a separately scoped physical fixture
with width two or larger distinguish ordinary/reversed orientation using
independent owner impulses and dirty spectators. A finite fixture still needs
a uniform exact operator/address argument. Then audit the changed full complex
inventory, finite work, both tails, compiler reserve and outer transfer.

## Credit and license

Prepared by **Chris R / Clear1nsight**, with substantial **OpenAI Codex**
assistance in research, independent review and packaging. Predecessor authors
are credited for their source work, not described as commissioning clients.
Nick Petalas owns #5083's formal word; David Arias, Ross Richardson, Adam Gall
and the retained group/cut lineage retain their mathematical credit. The source
BIT, native, row-cover, Clifford, precision/compiler and analytic contributors
include Cao Yifan, Cinna Davis, zxv, Dugongue, Jacob Alan Sussman, eumemic and
their predecessors. The frozen reports retain fuller attribution. Source
extraction, economic derivation and the independent review are retained with
their original attribution and scope. Apache-2.0, with all source notices kept.
