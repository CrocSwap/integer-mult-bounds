# Nonfaithfulness does not save these two-stream GL2 targets

At exactly one binary point column and two arbitrary dirty streams, all
36 ordered GL2(F2) monomial target pairs still cost their direct word lengths.
This answers the corresponding finite case of PR2599's open question. Its
nonfaithful stream action admits a legal formal/actual endpoint alias, but
that fact alone does not provide a cheaper monomial target.

Every coordinate CNOT applied to a role costs one, including inverses and
restoration; scalar GL2 role mixing is free. There are no extra roles or clean
inputs. [PROOF.md](PROOF.md) justifies normalization using arbitrary payloads
at the fixed zero address, reducing to twelve paid projector/address maps.
The result concerns complete actual eight-column stream operators, not just
their formal group-algebra endpoints.

The BFS reaches **20,160 states**, with diameter 8. A separate checker
independently enumerates the full active GL4 domain and checks **241,920
directed transitions**, every distance inequality and every descending path.
It then checks all 36 minima and **288 full dirty input columns** of attaining
words. The minimum histogram at costs 0..6 is `1,4,8,10,8,4,1`. Both checkers
use exact integers and the standard library.

```sh
python3.12 -I -O -B research/binary-gl2-width-one-minima/verify.py
python3.12 -I -O -B research/binary-gl2-width-one-minima/check.py
python3.12 scripts/research_package.py --package research/binary-gl2-width-one-minima
```

Default verification is read-only. `verify.py --write-new NEW_DIRECTORY`
regenerates both evidence files and refuses an existing directory. Negative
controls exercise incomplete graph domains, false distances, missing paid
calls, target coverage, source drift and typed evidence. The independent
checker imports no producer or predecessor executable.

Sources: PR2599 at `cfafdd633cf4e2e534704ec3ddd684cb0c32734f` supplies the
declared stream action, faithfulness threshold and credited legal norm alias.
Ross Richardson's retained symmetric-adjacent theorem supplies the formal
S3 direct-length baseline. PR2544's asymmetric SWAP tariff is related credit.
Earlier four-wire XOR and block-shear censuses have different paid alphabets.
Exact SHA256/Git blobs and retained source bytes are in SOURCES.json.

No third role, affine translation, alternate width/alphabet or physical
supplier is covered. Free scalar mixing remains an optimistic convention.
No selected record, native compiler, tape reserve or exponent is changed.
Finite certificate checks are not a proof-kernel or human theorem audit.

## Open next questions

Does a third dirty role permit a cheaper width-one monomial pair while that
role is fully restored? First specify the resulting active six-dimensional
space and seek an exact witness; the 20,160-state two-role domain no longer
applies. No such probe is included here.

Can the twelve-label target floor be proved without this finite census?
Start with an invariant of the actual nonfaithful stream representation,
without importing a cut through a quotient that the physical operator does
not determine. A written all-role conclusion remains open.

Canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0;
predecessor attribution is preserved in the retained documents and proof.
