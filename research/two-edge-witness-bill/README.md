# The two-edge witness pays 112 extra monomial passes, and the scalar suffix clears no final bank

**Scoped bill and suffix identity; no new κ.** On the one reused owned
bank of
[research/coded-active-feedback](../coded-active-feedback/README.md), the
witness `F1 = Q`, `F2 = C1 Q` replaces the published `I` and `C1 Q^2`.
Under the predecessor's uniform field units the witness pays one extra
`Q` on the saved FULL output, 112 monomial passes, and changes the
response monomial from `Q^2` to `Q` at the same 112-pass count. The
existing scalar suffix is a signed permutation of the four query-4 banks.
It clears none of them to an uncoded target. Final banks 0 and 3 stay the
explicit nonzero rows below.

The selected frontier is unchanged. This does not re-prove the one-edge
coupling of
[research/active-feedback-outside-edge](../active-feedback-outside-edge/README.md).

## Result

`Q` and `I` disagree on three columns of the common saved bank

```text
h = [Q^{-1} C1 D1, D1, -Q^{-1} C1 D1, 0].
```

`Q h` cancels the query-2 argument down to the single monomial `C1 D1`.
`C1 Q` then returns `D1` on that response. `C1 Q^2` on the same response
returns `C1 Q C1 D1`.

The additional ledger, with each uniform power charged as 112 monomial
passes, is 1120 scalar ADDs, 448 monomial passes, 16 mode CLEARs, 224
COPYs, 336 resets, 112 owned fields and 8 reused mode fields. The
published feed pays 336 monomial passes and the same other totals. No
Gaussian child is charged while `Q` uses that monomial unit. The unit is
not a tape proof.

After query 4 the suffix sends banks `(A, B, C, D)` to `(B, -A, D, -C)`.
The witness finals are

```text
bank 0 = [2 Q^{-1} C1 D1, D1, -Q^{-1} C1 D1, 0]
bank 1 = [0, C1 Q D1, 0, 0]
bank 2 = [D1 Q^{-1}, 0, Q^{-1} C3 D1 D3, 0]
bank 3 = [C3 C1 D1 D3, C3 Q D1 D3, -D1 D3, C3 Q D1 D3].
```

Bank 1 matches the published pure y0 monomial. Banks 0 and 3 do not match
the published feed or their uncoded targets. No rational word-free
combination of these four banks hits any of the four targets: the only
target monomial present is bank 2's restored `D1 Q^{-1}`, and it is tied
to the x1 monomial `Q^{-1} C3 D1 D3`. [PROOF.md](PROOF.md) gives the
cancellations, the ledger, and the support check.

Evidence class: the operator comparison, the suffix identity, and the four
final rows are proofs in the predecessor's formal algebra. The word-free
miss is a complete support check of these sixteen columns, not a search
and not a census of other pairs. The ledger is an upper bound under
inherited units.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/two-edge-witness-bill --check-only
python3 -B scripts/research_package.py --package research/two-edge-witness-bill
```

Direct replay:

```sh
python3 -I -W error -B research/two-edge-witness-bill/verify.py
python3 -I -O -W error -B research/two-edge-witness-bill/verify.py
```

The optimized command still executes the checks. They are `need` failures,
not assertions. Allow a few seconds. No network, native build, or full
multiplier replay is used.

## Scope

Original card: `joint-query-controller`. Scope status: **refined**. The
card asks whether one changed caller removes real work. This package does
not change the query demand and does not add a call. It takes the first
open question of
[research/active-feedback-outside-edge](../active-feedback-outside-edge/README.md):
compare `Q` and `C1 Q` with the published `I` and `C1 Q^2` on the same
owned bank, then read final banks 0 and 3.

Base commit: `17469fff78c22941280f04d39dc5a1faee09c840`. Pins are in
[SOURCES.json](SOURCES.json). The catalogue and selected record are
provenance. The selected conditional result remains
`781451/250000000`. `search.py` and `gauge.py` are live inputs.

Local overlap at this base found the witness named only as that open
question. The one-edge theorem, the owner-indexed y0 charge, and the
owner-indexed x1 obstruction are different objects and are not redone.

## Open next questions

Does one source monomial primitive implement a single power of `Q` at the
same 112-pass unit as `Q^2`? The witness bill charges two such powers, one
on `h` and one on the response, and its zero Gaussian-child line is false
if either power is a Gaussian child. The first step is to bind that
primitive for one `Q` on one 112-field bank and reprice those two lines.
No native word is replayed here. This is the primitive left open by the
owner-indexed y0 charge, now used twice.

Can one charged monomial, still with no new call, turn final bank 0 or
final bank 3 into its uncoded target while bank 2 stays the autonomous
row? Word-free rational combinations cannot. The first step is one left
monomial on bank 0 or bank 3, charged at 112 passes, checked against that
target and against bank 2. This is not the published-feed x1 owner index
and not a new saved-bank source.

## Credit

The schedule, algebra, owned-bank lifetime, and field units are Cinna
Davis's `research/coded-active-feedback`, using Dugongue's PR4948
chronology, Dillon's PR4933 code, and the passive ceiling packaged by
Chris R / Clear1nsight. The gauge engine remains the inherited
`research/coded-native-caller/gauge.py`. The witness pair and the one-edge
identities are
[research/active-feedback-outside-edge](../active-feedback-outside-edge/README.md).
The monomial unit for one power of `Q` is the convention in
[research/owner-indexed-y0-clearance](../owner-indexed-y0-clearance/README.md),
whose primitive question stays open. New work is the owned-bank comparison,
the witness ledger, the suffix identity, and the support check for banks
0 and 3.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0.
