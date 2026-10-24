# Source pins and portable dependency closure

The supplier source is the historical commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Its
[selected replay archive](https://github.com/CrocSwap/integer-mult-bounds/blob/bce54fb3f895cbe5cd4c0eb477c3afeed100190f/research/community-frontier1042-audit/selected-replay.tar.gz)
has SHA256
`22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754`.
The packaging step checked all 19,299,540 archive bytes, required one
regular member at each selected path, and copied only the four consumed
members. The portable replay checks the member hashes. It does not need
or re-download the full archive.

| Original archive member | SHA256 of stored bytes |
| --- | --- |
| `slots/local/CANONICAL-WORD.json.gz` | `16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219` |
| `slots/local/LOCAL-PROGRAMS.json.gz` | `241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a` |
| `t16/global/base/work/complex-nine-native/DATA-PHASES.json` | `c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa` |
| `t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz` | `a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518` |

The actual query interface has SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
The snapshot source has decompressed SHA256
`3dd1d7388c7d3bca104a21e642b5fcafe175d83a2f1dfce1a3ee3e86b864276c`.
The clean scalar programs have decompressed SHA256
`fa60b4af013dd8b8db289845e3ed597720ff955751ad270c3d58236b64080877`.
These payload hashes define mathematical equality independently of gzip
container metadata.

The campaign results were local source files. Their original paths and
SHA256 values are recorded in [SOURCE-MANIFEST.json](SOURCE-MANIFEST.json).
Do not treat their local paths as prior public commit links. Their first
public commit must preserve that provenance. The manifest also records each
portable edit, its old hash, its new hash, and its reason.

The portable checkers use the same exact calculations. The fourth-moment,
snapshot-source, residual, and independent cover loaders read bundled
members. The dependent moment checker pins use the new checker hashes.
The narrow source-matrix checker extracts the reviewed reverse-propagation
routine from `temporal-reuse/review_spectral_bound.py`. It does not rerun
or claim the separate spectral subset theorem.

The copy of `source-domain/verify_domain.py` supplies only its source
constants, member hash check, and exact forward centre reconstruction to
the cover reviewer. The remaining functions are retained source context
and are not executed by this package. The historical spectral checker is
also retained as provenance for the extracted routine; its old `main`
entry point is not part of the portable replay.

The native application dependencies are the local lift and the global
endpoint normal form. Their proofs and receipts are included under
`payload/lanes/interface-proof` and `payload/lanes/encoded-controller`.
They are inherited application evidence. The package reruns the exact
scalar and algebraic claims listed in the README, not a native supplier
admission or its complete price.

Publication base:
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`.
The selected frontier at that pin is the conditional joint-helper result
from [PR #4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470).
It has kappa `60403/20000000`. The historical source pins above are not
changed to match that newer construction. Applicability to it is unproved.
