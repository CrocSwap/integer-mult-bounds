# Exterior injectivity for 60 changed BIT carriers

**NO VERIFIED GAIN.** With the old MOVE geometry and ordinary suffix fixed, none of the 60 existing paid ingress events into the ten singleton marked banks can carry a nonzero coframed linear payload change while preserving the 114 required exterior public rows. This holds even when each changed MOVE may use any combination of its own original row and all other live rows in its source chart. The independent exterior coefficient rank is 148 out of 148 under that grant, with no new singleton expansion. The narrower other-owner source model has rank 88 out of 88.

The pinned complete comparator is [#7244](https://github.com/CrocSwap/integer-mult-bounds/pull/7244) at scientific head `4156504fa39efb51c550d218a9b94fe69dbce8f6`, with independently reproduced conditional κ `0.003645372367832` and retained effective BIT premise `376669/100000000`. The campaign target is `10018846261809/2500000000000000`. The κ change is exactly zero.

## Offline replay

From this directory in a clean checkout, use CPython 3.12 with assertions enabled. The standard-library replay was tested on CPython 3.12.14 in an empty current directory and with an empty executable `PATH`.

```sh
python3.12 -I -B replay.py --controls
```

Expect exit 0 and both markers.

```text
PASS_FORGED_COFRAMED_SOURCE_AND_EXTERIOR_MASK_REJECTION
PASS_BIT_CHANGED_CARRIER_EXTERIOR impulses=60 source_ranks=88/88/148 kernel=0 expansions=0 no_new_kappa
```

The command authenticates every replay dependency by stable path, rejects duplicate paths, and regenerates three predecessor receipts and the joint price in fresh scratch. It regenerates the detailed 300,884-byte `RESULT.json` by exact SHA-256, checks `SUMMARY.json`, and independently replays all 60 scalar impulses. The primary positive controls exercise two individually leaking changes that cancel jointly and a synthetic quotient exchange. The negative controls forge a coframed source row and remove an exterior marker observation. Each must fail in the independent audit before scientific stdout. A separate byte mutation and duplicate-path check also fail closed.

`--inputs /path/to/inputs` accepts the same exact seven source files from an explicit root. `--write-result /path/to/new-result.json` exports the verified full receipt for a follow-up. [PROOF.md](PROOF.md) defines the scope and price. `PROVENANCE.tsv` records Git blob IDs, SHA-256 and exact public commits. `SOURCES.tsv` preserves the original scientific manifest and its regenerated receipt pins.

## Open next questions

Can an already paid field carry a new component if its old row can be reconstructed and restored from live coframed peers before its first old contact? That changes the ordinary restoration chronology, which the exclusion holds fixed. [NEXT.md](NEXT.md) starts with a 60-event recovery census and gives the price and signed compatibility gates.
