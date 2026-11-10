# Sharp block dimensions for the P104 Hall mask

**No new κ.** Under the exact asymmetric label-pattern hypothesis of
CrocSwap/integer-mult-bounds#6846, the complete P104 mask requires inner
dimension **at least `9k` over every field**, for every positive integer block
size `k`. This closes the interval `8k < d < 9k` left open there. The proof
transfers the established four-isolates-plus-Petersen obstruction to an
authenticated P104 subconfiguration; it does not introduce a new general
Petersen rank theorem.

The predecessor's original fourteen ports behave differently: their exact
minimum is **`ceil(17k/2)` over every field**. In particular, `k=2,d=17` is
possible on that subsystem. Replacing just port `57` by port `61` produces
another fourteen-port subsystem whose exact minimum is `9k`. The distinction
explains both why the original Hall witness cannot exclude the whole block
interval and why the full source mask nevertheless does.

| Object, with the zero convention below | Proven minimum / lower bound |
|---|---|
| Original fourteen ports from #6846 | Exact `ceil(17k/2)` over every field |
| Same selection with `57` replaced by `61` | Exact `9k` over every field |
| All 104 source ports | At least `9k` over every field |
| All 104 source ports in characteristic two | Exact `9k` |

No dimension-`9k` upper bound for the full mask in other characteristics is
asserted. No supplier circuit or complete paid invoice is constructed.

The same exact certificates also give an index-coding corollary: even with
arbitrary nonlinear deterministic encoding, the minimum fixed-length binary
broadcast for independent `k`-bit messages is `ceil(17k/2)` on the original
subsystem and `9k` on the replacement subsystem and full 104-port graph.
Section 6 of [PROOF.md](PROOF.md) supplies the entropy reduction and explicit
attaining parity broadcasts. This abstract side-information model does not
establish a physical supplier or change κ.

## Exact object and hypothesis

The input is the unchanged
[#5561 word](../p104-designer-toolkit-v2/words/5561.json.gz) at canonical base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Its compressed SHA256 is
`b3701d78bee3661382ebe5414e678dfc9ee292e254cb9dc56339c2d2f45fdf44`;
Git blob `c367d865a154ffd2ae0b6f6053469580a139f487`.
The `ports` array contains 104 distinct odd-weight nine-bit integers. All
indices below are zero-based array positions, not port integer values.

For a field `F`, choose arbitrary `k × d` matrices `U_v,W_v` for each retained
port. Require `W_v U_v^T` to be invertible and require
`W_v U_w^T=0` whenever `v != w` and
`popcount(ports[v] & ports[w])` is even. Both ordered products are constrained
on a forced-zero pair; no symmetry or equality of `U` and `W` is assumed.
Additional zeros are permitted.

This is exactly the explicit pattern hypothesis in #6846. It is **not**
established here for every legal multiplier, caller, frame change, or decoder.
In particular, it must not be confused with the opposite parity convention
used for the real-valued completion in
[P104-LEMMAS.md](../p104-designer-toolkit-v2/P104-LEMMAS.md).

## What is new relative to the archive

DreamingOfClouds' #6846 proves impossibility at `d=8k` from
`K={62,63,69,74,81,86,91,99}` and `O={57,67,68,95,100,101}`.
Its second open question explicitly leaves intermediate block dimensions
unsettled. The reviewed predecessor head is
`01651795be9570c47977a73f9cf3e8eeb3fbe64a` in
`DreamingOfClouds/integer-mult-bounds`; the scope here is that stated mask and
question, not an unmerged circuit dependency.

The relevant earlier archive result is Thiago's merged #1744,
[research/p112-characteristic-two-minrank](../p112-characteristic-two-minrank/README.md),
head `78033981ec296b545b3cb50435668fe98e764e65`. It already proves the same
all-field `9k` obstruction on P111 and P112 by embedding four isolates and a
Petersen graph, with an exact 113-term certificate in an augmented-rank
formulation. It credits the known Petersen broadcast-rate theorem to
[Blasiak, Kleinberg and Lubetzky, Fact 5.6(1)](https://www.cs.cornell.edu/~ablasiak/papers/bkl-beta.pdf).
The present package connects that mechanism to the precise P104 question:

- It authenticates a concrete P104 embedding using only fourteen source ports.
- It proves the sharp `ceil(17k/2)` value of the predecessor's original
  fourteen-port selection, including a `k=2,d=17` witness.
- It gives a separate 43-row exact subspace-rank certificate for the Petersen
  core and checks it with two separately written implementations.
- It explicitly separates the full-mask lower bound, subsystem sharpness,
  characteristic-two full-mask sharpness, and unproved supplier applicability.

The smaller certificate is given for inspectability; its row count is not a
performance comparison with the different formulation in #1744. No novelty is
claimed for fractional Haemers representations, coordinate-cover upper
bounds, the Petersen value, or the natural binary upper construction. See also
[Bukh and Cox, *On a fractional version of Haemers' bound*, arXiv:1802.00476v2](https://arxiv.org/abs/1802.00476v2),
Section 2, for the block-fitting framework.

## Proof and exact witnesses

[PROOF.md](PROOF.md) gives the linear-algebra argument and a short hand proof
of the original subsystem's lower bound. For any admissible labels, let
`f(A)` be the dimension of the sum of the row spaces of the matrices `U_v`
for `v in A`. This is a monotone submodular rank function. If `v` is forced
zero to every member of `A`, the invertible diagonal pairing implies the
exact identity `f(A+v)=f(A)+k`. This elementary fact handles asymmetric labels
and every characteristic.

Four ports `I={74,81,86,91}` are isolated in the allowed-pair graph. Their
common forced-zero neighborhood is exactly
`P={61,62,63,67,68,69,95,99,100,101}`. The allowed-pair graph on `P` is the
Petersen graph. The exact certificate establishes `f(P)>=5k`, hence
`d>=f(P+I)>=9k`. The same four isolated ports combined with
`S=P-{61}` give the original subsystem's `17k/2` lower bound. A two-coordinate
assignment per port attains it at `k=2`, and direct sums give all block sizes.

The universal statements follow from the displayed proof and exact axiom
combination, not from finite searches. The numerical linear programs used to
discover the certificate are absent from the trusted replay.

## Reproduce and expected result

From the repository root, with Python 3.12 and no external dependencies:

```sh
python3.12 scripts/research_package.py --package research/p104-sharp-block-hall-dimension
```

The registered replay runs both verifiers normally and with `-O`. Expected
markers are `PASS_P104_SHARP_BLOCK_HALL_DIMENSION` and
`PASS_P104_PETERSEN_EXACT_RANK_PROOF`, each twice. Direct standalone replay is
`python3.12 -I -B research/p104-sharp-block-hall-dimension/verify.py`.

The main verifier authenticates the source bytes and index convention,
expands all 17 axiom rows of the short proof, regenerates all 43 Petersen
certificate rows as sets of actual port IDs, checks their coefficient sum
exactly, verifies an explicit Petersen isomorphism, checks all ordered
required pairings of the coordinate witnesses for `k=1,...,12`, and computes
all 10,816 entries of the binary full-mask Gram matrix. `audit_petersen.py`
was separately written and checks the same Petersen certificate using an
integer-mask coefficient accumulator. Neither implementation imports the
other, a predecessor verifier, or a numerical optimizer.

Ten main negative controls reject a source-byte mutation, a removed required
zero, the reversed parity convention, a reversed inequality sign, a deleted
inequality, a changed equality coefficient, a false zero premise, a corrupted
upper witness, deletion of its seventeenth coordinate, and a singular
diagonal. The separate audit has four coefficient/premise controls. All
acceptance gates use explicit exceptions and remain active under `-O`.
The finite block-size runs check implementations of the explicit witnesses;
the direct-sum proof establishes all positive integer block sizes.

## Scope, assumptions and completion status

This is a completed rank-geometry side result, not a completed answer to the
catalogue's supplier-budget question. The original catalogue card is retained
in [TASK.json](TASK.json), with the scope change recorded. Exact live input and
historical provenance pins are in [SOURCES.json](SOURCES.json). Reproduction
commands and input-trigger declarations are in [VERIFY.json](VERIFY.json).
The coordinated claim was local-only because the connected GitHub interface
could not post to the current Discussion board; no reservation issue was
created.

The selected record at the base reports `κ=0.003125804`. This package leaves
that record and its five framework assumptions untouched: `native_all_columns`,
`owned_erasure`, `compiler`, `precision_tape`, and `analytic_recovery`. The
rank proof itself uses none of those assumptions; applying it to a proposed
supplier requires a separate proof that the supplier obeys the label pattern.
No partial numerical improvement or optimistic invoice is promoted to a
multiplication bound.

## Open next questions

1. **Applicability or paid relaxation.** For a particular legal caller, which
   operations force exactly this zero pattern, and can a priced helper change
   enough contacts to remove the Petersen witness? A useful first step is to
   map the fourteen required contacts to that caller's explicit operations,
   then price every altered boundary, restoration and ownership cost. An
   abstract graph relaxation alone cannot improve the selected bound.
2. **Full-mask upper bounds outside characteristic two.** What is the exact
   block-rank parameter over a specified field such as the rationals or
   complex numbers? The present `9k` lower bound remains valid, but the binary
   upper construction does not transfer merely by interpreting its entries
   as integers. A first step is a source-pinned fitting construction or a
   stronger exact rank certificate; no such construction is supplied here.

## Attribution

Prepared by **@CubeJerry**, with substantial **OpenAI GPT-6 Astra Pro**
assistance for mathematical exploration, proof writing, exact checks and
packaging. The original-subsystem proof and the Petersen extension were
independently developed within the research team and then cross-checked;
the two certificate checkers were written separately. The final arguments
and their precise limits are recorded above.

The entropy corollary was derived separately by the lead and checked by the
rank-proof worker before integration. It uses the same verified source contacts,
axiom coefficients and upper-witness Gram entries; no finite experiment is
presented as a proof about all nonlinear codes.

Credit DreamingOfClouds for the Hall witness and open question in #6846;
Thiago for the source-bound P111/P112 obstruction and verification approach
in #1744; Blasiak, Kleinberg and Lubetzky for the underlying Petersen result;
Bukh and Cox for the fractional Haemers framework; and the authors of #5561
and its credited predecessors for the unchanged P104 native word. Inputs are
referenced without modification or re-vendoring. New work is Apache-2.0;
existing source attribution and licenses remain applicable.

## Concurrent work checked at completion

DreamingOfClouds' open #6854, head
`3d355ae61f174c5f7101c9eb292722afa5a5f9ac`, excludes dimension exactly `8k`
for every subset of at least 97 of the 120 E8 lines under its stated mask.
It explicitly leaves `8k<d<9k` outside its scope. The present result concerns
the exact P104 source and sharp subsystem dimensions; it does not establish
the corresponding fractional bound for every 97-line subset, audit that
contribution's large certificate, or depend on its unmerged files.
