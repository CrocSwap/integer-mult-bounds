# PR259 lineage and selected inputs

PR249: 96495746c786d6d0339dbb38c7f553d4af3f88ed.
PR259: a53ec0ca4d59634f16630dd16adf035c9f12595c, repository
Dugongue/integer-mult-bounds, research/multicut-kernel-condensation/.
Its candidate gzip is included byte-for-byte as kernel-candidates.json.gz:
SHA256 5f6863ad27eb9f2fcb14db10320c00607451c01e12da303def13e48eda7a5d2d;
Git blob ca1360f111e32a699ae687d979dec1d473083377.

hybrid-selection.json declares the five removals and seven exact interval
witnesses. retiming25-selection.json declares the uniquely scalar-keyed 25
retimings and their exact old/new subspaces. No optimizer or external source
path is required during verification. Optional annihilator annotations in
the upstream candidate search data are not trusted: they are reconstructed
from the basis, matching the actual upstream compiler's behavior.

The sixteen extra PR251 entrances are not included: all conflict with the
new PR259 selection. Historical copied interval/kernel witnesses are omitted.
The current interval data are in hybrid-selection.json, and the byte-exact
upstream PR259 witness is kernel-candidates.json.gz. portable_bit.py calls
the current hybrid_transform.py and retiming25.py for this construction.

PR258: cf82ca09322d1327ab887cfd1cce97591b8d3cfa.
PR260: 87aa555a455cca84a3e3296ced2440623d39fc4d.
These independently published retiming witnesses identify the same 25
scalar gates and replacement subspaces; the changes are applied once.
See [HERITAGE.md](HERITAGE.md) for contributor attribution and exact boundaries.
