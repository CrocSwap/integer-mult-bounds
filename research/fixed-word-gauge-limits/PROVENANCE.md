# Source binding and package changes

The consumed source is historical commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f` in
`CrocSwap/integer-mult-bounds`. The selected archive is
[the pinned replay archive](https://github.com/CrocSwap/integer-mult-bounds/blob/bce54fb3f895cbe5cd4c0eb477c3afeed100190f/research/community-frontier1042-audit/selected-replay.tar.gz).
Its SHA-256 is
`22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754`.

Only these members are needed for the fixed-word theorem:

| Archive member | Compressed SHA-256 |
| --- | --- |
| `slots/local/CANONICAL-WORD.json.gz` | `16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219` |
| `slots/local/LOCAL-PROGRAMS.json.gz` | `241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a` |

The extraction checked the complete archive and both member hashes. The
package stores the exact member bytes. The replay checks the member hashes
before it reads the source. Expanded payload hashes are also recorded in
`SOURCES.json`; compressed headers are not a test of regenerated
mathematical equality.

`SOURCES.json` records the original campaign paths and exact hashes for
every copied certificate, proof, historical receipt, and adapted checker.
Original paths are provenance labels. They are not runtime inputs.
`MANIFEST.json` binds every retained package file except itself.

The eight checkers have only input-path, output-path, and corresponding
source-reader hash changes. They use the packaged source data in place of
`git show` and write receipts to the requested external directory. The
all-line negative controls call the packaged checker. Unused archive
imports and an unused search-script hash entry were removed. No search
producer, floating optimizer, solver dependency, or source monkey patch
is needed.

The new replay driver checks the manifest and runs the nine check commands
in sequence under `-I -O -B`. The source-domain span calculation and the
encoded-controller pairing calculation remain distinct methods. Historical
review receipts are evidence of earlier checks; the new replay receipts
are evidence of the present package check.

The publication base is
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`. No source pin was changed to
that base. The current selected construction uses a changed scalar word.
No claim in this package is automatically a bound for that word.
