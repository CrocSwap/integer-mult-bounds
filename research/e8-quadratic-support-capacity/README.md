# Analytic E8/P112 support capacities 12 and 20

Any subset of the declared full 120 E8 root labels of binary rank at most
five has at most 12 elements; at rank at most six it has at most 20.
Both bounds are attained on the fixed P112. [PROOF.md](PROOF.md) replaces
the global flat-exhaustion dependency with a short signed character-sum
argument. It does not add a shortening threshold or profile exclusion.

The exact label convention matters. The nine-bit labels have leading bit
one followed by simple-root coordinates modulo two. The replay checks all
112 existing live labels and all 120 full root residues against the
eight-dimensional norm quadratic form. It checks polar rank eight and
positive Gauss sum 16. These give affine dimension-four/five maxima12/20;
opposite-sign controls attain16/24 and show why nondegeneracy alone fails.

The proof directly replaces the global support-capacity bounds used in
PR3249, PR3255 and PR3260. Their Weyl-chamber, A2-fiber, lifting,
shortening and caller obligations are separate. No selected frontier,
supplier, decoder-floor or kappa claim follows.

## Reproduce

Python 3.12+, standard library, from the repository root:

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/e8-quadratic-support-capacity
```

For a Git-free export containing this package and the single input declared
in `VERIFY.json`, run the three direct commands:

```sh
python3.12 -W error -B research/e8-quadratic-support-capacity/verify.py
python3.12 -W error -B research/e8-quadratic-support-capacity/independent.py
python3.12 -W error -O -B research/e8-quadratic-support-capacity/test_verify.py
```

Set TMPDIR to an external session-owned directory if required locally.
The source loader authenticates bounded raw bytes before executing the
single fixed geometry module and does not consult bytecode caches.
`verify.py --output NEW_EXTERNAL_PATH` writes an exclusive new receipt.
The 3,309,747 five-flats and 788,035 six-flats are not replayed.

## Open next questions

An analogous argument may give further support capacities at other ranks.
First state the precise affine dimension and signed radical cases; do not
infer a new decoder theorem from a larger list of local capacities. A
physical label convention needs its own explicit invertible rank-preserving
map before this result can be applied to it.

Existing shortening proofs may replace their global upper-bound dependency
with this lemma. Recheck the exact root-label convention, and retain their
other source and proof obligations. No automatic changes to frozen packages
or their receipts are included here.

## Sources and status

Base canonical main `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority
revision6. `SOURCES.json` pins the geometry, catalogue and selected record.
Only the geometry is a mathematical input; no pending PR objects or
executables are required in CI or an offline export.

Credit Nick Petalas/PR3249, PR3255, PR3260 and the root-simplex sources,
David Arias's `masked-root-star-assembly` quadratic model, and the retained
E8/P112 lineage including joaqcoo. New work is Apache-2.0. The canonical
investigation is Discussion3156, comment19003593. An earlier duplicate
mixed-support38 claim was released before this distinct obligation.

The result is a scoped written proof with exact finite model binding.
Independent human or proof-kernel verification is not claimed. Lean,
Docker and the selected-supplier cold replay are unrun because no selected
source or supplier changed. See `ENGINEERING.md` for code and resource bounds.
