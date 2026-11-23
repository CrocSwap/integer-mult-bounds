# Selected dyadic route supplement

This is an appendix for the existing
`research/dyadic-selected-compiler-bases` package in PR #8092. It adds
explicit prime-independent route words for all 513 dimension-eight nested
differences, with complete representative carry and a paid ordinary-swap,
ordered-shift and fixed-scale invoice. It does not duplicate the earlier
general dyadic-basis theorem or #7840's generic GL route theorem.

The maxima per directed full route are 472 ordinary swaps, 496 ordered
shifts including 64 carries, and 64 fixed scales. The scales expand to at
most 128 signed-dyadic physical atoms of #5052. The inverse is separately
charged. These counts do not extend to generated compiler matrices of
other dimensions or larger coefficient heights.

`PROOF.md` gives the all-odd-prime argument, non-raw witness
`P266-P11 -> P270-P2`, spectator semantics, source tariffs and unresolved
caller, low-carry and ordinary-machine obligations. `INPUTS.json`
authenticates retained sources; `NOTICE.md` preserves credit.
`CATALOGUE.json` contains complete matrices and operation descriptors.

## Reproduce

Python 3.12, standard library only. From this directory:

```sh
python3 -I -B route_words.py
python3 -I -B verify_routes.py
python3 -I -O -B verify_routes.py
```

The producer deterministically regenerates `CATALOGUE.json` and emits
`PASS_Q_INDEPENDENT_ROUTE_PRODUCTION`. Both verifier forms regenerate the
same `EVIDENCE.json` and emit `PASS_SOURCE_DYADIC_ROUTE_CERTIFICATES`.
Checks use explicit exceptions; optimization cannot remove them.

The checker imports no generator or earlier scientific engine. It rebuilds
source projectors and endpoint differences, checks both complete-basis
summands, interprets rational words and inverses, lowers upper updates into
paid swaps, and checks full carry and opaque-record semantics. Exact
identities prove the universal q,w claim. Finite corroboration has 20,520
modular basis rows, 192 full 64-field cases, the entire 6,561-row high cube,
and 39,366 opaque records with exterior spectators. The full production GL
cover and a complete physical route machine are not executed.

## Integration

Copy the files in `FILES.json` under `routing/` of the existing dyadic
package, add the separate peer review, and register the three commands
using their integrated paths. Preserve proof and catalogue hashes in
`AUTHOR-RECEIPT.json`. Exploratory `scan.py` and `scan.json` are excluded.
The complete-basis input is a new independent review artifact with exact
byte provenance, not claimed to exist at the canonical source commit.

This is model-assisted research with independent model-run review. No
independent human, Lean, proof-kernel, full machine, selected cold replay,
new kappa or assumption discharge is claimed.
