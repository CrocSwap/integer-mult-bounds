# Local validation

Validated on macOS arm64, Python 3.12.13 and Python 3.14.2. Base commit:
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`.

The registered Python 3.12 command in the README passed. It checks exact
Git and SHA256 source identities, freshly reconstructs both committed
receipts, runs ten primary semantic controls and two independent boundary
controls, and passes four public-entrypoint tests. Those tests reject a
changed primary certificate, a changed independent receipt and source drift
in both engines, and check both optimized engines in a minimal read-only
export with spaces in its path. The export's file hashes remain unchanged.

The primary replay covers all twelve block interfaces, 3060 support cases,
4560 input-frame pairs, 1056 foreign high/input tests, 4608 input/target
tests and 24 rank-seven kernel frames. The separate set/integer-minor
implementation agrees, checks 240 scalar columns including target dirt,
and establishes joint boundary rank 192 over each of two checked primes.
Its rank-deficient controls return 191.

Both direct replays also passed with isolated, optimized Python 3.14.
`make selected-record-check` passed with the original selected kappa
`836330098538459/500000000000000000`. No selected input or predecessor was
regenerated. The patch is confined to this new research directory.

Before submission, main remained at the recorded base and PR1429 remained
open at `591582004d82302268da3b264a6ba5edec1521de`, with no review comments.
Its two consulted file blobs were checked against the exact GitHub tree.
The overlap refresh covered 758 open PR bodies and 68 discussion bodies
with their last six comments. Nested replies, all historical comments and
every code diff were not searched. PR1429 is the nearest contribution; this
package explicitly changes its no-cross-block premise and credits it.

The all-length argument is written mathematics supported by these finite
premises. No proof-assistant build, independent human review, full selected
cold replay, new native/global supplier admission, hosted CI success or new
kappa is claimed. Both checking implementations are by the same assisted
author. The fixed early source versions and late target frames remain
essential restrictions.
