# Physical adapter of selected helper 759

**Result.** On the selected #7000 word, public helper 759 has two executed
physical adapters, and neither record instantiates a rank-dependent target
fee. **No new κ.** The selected record stays
`363005817/100000000000`.

This is a proof for one helper, with an exact recomputation of the published
constructor and of one chart lowering. It is not a census of the other
helpers, not a search, and not an application of either theorem in #7299.

## The helper

In `research/shared-wire-split-composition/data/final.json.gz`, public field
759 runs from frame 3 to frame 660. Frame 3 is empty and frame 660 has seven
axes, so the head target has rank 7. The same split's tail is the unique
field 1478, from frame 660 to frame 127, rank 2. In the #6936 base used by
the chart receipt, field 759 still runs from frame 3 to frame 127, rank 9.
The witness is `data/split759.proof.json`: `a·b = c·d = 1` and `c_759 = 1`.

## Named adapter

The argument is [PROOF.md](PROOF.md).

**Scalar basis adapter.** The published `basis` constructor, with no swap and
no SCALE, inserts eight coefficient-±1 ADDs. They are `B0^{-1}` at frame 3,
`BC` and the tail-renamed `BC^{-1}` at frame 660, and the tail-renamed `BF`
at frame 127, where the tail rename sends register 759 to 1478. Each
instruction occurs once, at event indexes `9, 10, 11, 42546, 42547, 71249,
71250, 71251`. Their coefficients do not depend on the dimension gaps 7 and 2.

**Whole-job chart adapter.** The pair `(3, 660)` is an introduced chart, it
is not a MOVE, and it is field 759's endpoint. Its lowered circuit is the
right monomial, the Fourier child `C_1, …, C_64`, and the left monomial, of
child rank 7, equal to the frame transition. The pair `(660, 127)` is not a
new recipe: four MOVEs already use it in both words. Its lowering has rank 2
and is not a second fee.

## Fee contract

#7299 applies only after a reading and a fee `c + d φ(r_i)` are identified.
These records do not contain that identification. The chart rank 7 is the
head target itself. The eight ADDs are one ordinary program, not two
rank-dependent charges, and they contain no per-ADD unit price. In
particular the identity-tariff values 7 and 2 are not coefficients. Neither
Reading A nor Reading B is applied. A later proof that the eight ADDs cost a
constant in the units of `φ` would be the case `d = 0`, which this package
does not establish.

Discussion comment 19530156 asks for fixed-paid-profile split ceilings. This
package does not evaluate `18(7^p + 2^p - 9^p)` and does not compute those
ceilings.

## Scope

Catalogue card `coverage-law-change`, priority revision 8, base
`e54523517d0f03e58352e647c403a5af3e525a57`. Scope status: **changed**. The
card asks for a completed call. The assigned question is the naming step in
open question 2 of #7299, on one selected helper, before either theorem is
applied. Overlap was checked against local package notes and against upstream
PR and code search for `helper 759`. The construction text in #7000 states
the split and does not name this circuit or this fee gap. Open #7299 states
the question and does not open the ledger. No match is not a novelty
certificate.

The orientation command `python3 -B scripts/research_selected_baseline.py`
was not required for this identification. The selected κ was read from
`certificates/selected-result.json` and not modified.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3 -B research/helper759-physical-adapter/verify.py
python3 -O -B research/helper759-physical-adapter/verify.py
python3 -B scripts/research_package.py --package research/helper759-physical-adapter --check-only
```

The marker is `PASS_HELPER759_PHYSICAL_ADAPTER`.

Not run: `make frontier7000-verify`, any selected-invoice export, the #7299
halving census, and any native replay beyond the one chart lowering and the
word scan above.

## Open next questions

- What is the physical adapter of public helper 450, the other new #7000
  split, whose witness carries coefficients 2 and 4? Rebuild it from
  `data/split759_450.proof.json`. Do not turn that naming into the shared
  adapter optimum of #6651, and do not compute the ceilings of discussion
  comment 19530156.
- Does a proved ordinary unit price make these eight ADDs a flat fee `c`
  with slope `d = 0`? The adapter records do not contain that unit. At
  `d = 0` the #7299 readings reduce to the uniform-fee theorem; applying
  that theorem is a later step.

## Credit

CubeJerry and Jerry Chen, #7000, for the selected word and the helper 759
split. DreamingOfClouds, #6936 and #6937, for the base word and the wires
that enable the split. Ali Romman, #5599, for the basis mechanism, and
#5769, for the fee-charged partition contract. Nick Petalas, #6651, for the
uniform-fee theorem, and #7299, for the rank-dependent theorems whose
naming step this package answers without replaying the optima. The signed
mixed-target invoice model is zxv's, as credited in
`docs/research/recursive-invoice-preflight.md`; it is context, not an input
to the checker.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review or proof-kernel check is claimed.
