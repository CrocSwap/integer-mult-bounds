# Cold44 hosting: frozen owner map and exact callwise matching

This directory contains the owner assignment used to turn the new cold44 local
word into a global improvement. All 72 calls use the new local signature. The
assignment is frozen; no search, tuning, or optimization is needed to consume
it in the global verifier.

The local word reduces the helper width sum from 3894 for the previous `jp8`
provider to 3794. Simply shrinking the old allocations leaves many small idle
remainders. The matcher below moves helpers to other physical families that are
already idle at the same call, concentrating those remainders while respecting
every parent capacity and window. This recovers a substantial part of the local
saving in the global moment calculation.

## Frozen result

The exact finite data are in [frozen/MANIFEST.json](frozen/MANIFEST.json) and
[frozen/MATCHING-RECEIPT.json](frozen/MATCHING-RECEIPT.json).

| Quantity | Frozen value |
| --- | ---: |
| Calls | 72 |
| Helpers per call | 492 |
| Owner roles | 35,424 |
| Ambient dimension | 73 |
| Live streams | 7,168 |
| New local width sum | 3,794 |
| New local paid rank mass | 5,650 |
| Global paid rank mass | 520,704 |
| Global deficit | 2,560 |
| Maximum child rank | 48 |
| Equal-width updates with exact majorization receipts | 288 |
| Final callwise optima independently checked | 72 |

The new local width inventory is `{4:52, 5:48, 7:34, 8:114, 9:244}` and its paid
profile is `{1:2514, 2:404, 3:448, 4:160, 5:56, 8:8}`. The final global paid
profile, including all idle remainders, is:

```json
{"1":181093,"2":29164,"3":32429,"4":11520,"5":4032,"7":7,
 "8":582,"12":13,"16":33,"19":1,"20":2,"28":4,"32":62,
 "36":1,"40":1,"44":6,"48":2289}
```

Its floating moment screen is `b = 0.0016522089943684115`, giving the analytic
screen `b/(1+b) = 0.0016494837025589793`. Relative to PR #635's reported
`0.001636241501576388`, that is approximately **0.8093%**. These decimal screens
are diagnostic values; the package's exact moment and outer assembly determine
the admitted exponent. The owner replay never uses the floating root to choose
an expanded-matching move.

The frozen owner file has byte SHA-256:

```text
90ff7657a23dcfb67532b49c0800c5fc259b27c89005081e24bf184869e1bd57
```

Its semantic SHA-256, computed from sorted-key compact uncompressed JSON, is:

```text
c09faf298565c1388c02370fdd4e61dd542579fe1898e842d5096cc97b68191d
```

Semantic hashes are the portable replay criterion. The gzip byte hash is also
reported, but compressor implementations need not produce identical streams.

## Reproduce with the Python standard library

Supply the PR #635 parent `PLAN.json` and `OWNERS.json.gz`, plus either the new
verified native provider directory or the new raw word. The expected parent
hashes are pinned in the manifest. The command below is run from the package
root; replace the example input paths with actual paths.

```sh
python hosting/reproduce.py \
  --parent-plan /path/to/pr635/research/complex-571-cold14-st2/data/PLAN.json \
  --parent-owners /path/to/pr635/research/complex-571-cold14-st2/data/OWNERS.json.gz \
  --local44 /path/to/verified/local44 \
  --out /path/to/new/hosting-replay
```

For the raw provider, replace `--local44 ...` with
`--raw-word /path/to/FULL-WORD.json.gz`. Reading a raw word here only extracts a
nomination signature; it does not replace independent local verification.

The default replay copies the frozen mixed-provider seed, checks its semantic
hash, derives its profile afresh, and runs the exact expanded matcher. It then
compares the final owner and majorization transcript with the frozen semantic
hashes and independently checks the final map's 72 callwise fixed points.
Outputs include `all72/OWNERS.json.gz`, `all72/PROFILE.json`, recomputed
remainders, `FROZEN-AUDIT.json`, and `REPRODUCTION.json`.

The seed has 71 cold44 calls and one inherited `ck` call. Expanded matching first
replaces that last call using newly available legal families. This changed-width
bootstrap is checked for feasibility and is explicitly excluded from the
equal-width majorization count. The following four passes use cold44 at all 72
calls:

| Pass | Calls with strict majorization | Changed helper owners |
| --- | ---: | ---: |
| 1 | 70 | 1,245 |
| 2 | 41 | 169 |
| 3 | 8 | 13 |
| 4 | 0 | 0 |

Pass 4 changes neither the map nor its remainder histogram. The independent
audit additionally recomputes the optimal remainder histogram for each call
with all other calls fixed.

## Optional: reproduce seed discovery

Add `--rebuild-seed` to the same command to rebuild the mixed seed from the
original PR #635 owners. This step first matches sorted new helper widths to
sorted old owner slots, then performs two fixed-family Hungarian passes.
Discovery used Python 3.12.14, NumPy 2.3.5, and SciPy 1.17.0. Equal-cost matching
tie choices may vary across SciPy versions, so the script compares the rebuilt
seed with the frozen semantic hash and fails if it differs. Default frozen-seed
replay has no NumPy or SciPy dependency.

The two discovery passes are an optional way to recover the recorded seed.
Their floating costs are not needed for feasibility, for the final fixed-point
proof, or for the package's admitted exponent.

## Audit without regenerating the assignment

```sh
python hosting/audit_frozen.py \
  --parent-plan /path/to/pr635/research/complex-571-cold14-st2/data/PLAN.json \
  --parent-owners /path/to/pr635/research/complex-571-cold14-st2/data/OWNERS.json.gz \
  --local44 /path/to/verified/local44 \
  --out /path/to/FROZEN-AUDIT.json
```

This integer audit checks helper coverage, capacity, allowed call times, active
data exclusion, physical-family uniqueness within each call, disjoint compacted
coordinate prefixes, the exact global profile and rank mass, and callwise
optimality of the frozen remainder histograms. It reads the explicit parent
window catalogue. The package's separate global verifier must also derive
those windows and all 73-column charts from the actual program.

## Files and scope

| File | Purpose |
| --- | --- |
| `frozen/OWNERS.json.gz` | The final all-cold44 map consumed by global assembly |
| `frozen/SEED-OWNERS.json.gz` | Pinned feasible mixed seed for dependency-free replay |
| `frozen/MAJORIZATION.json.gz` | Integer stop-loss margins for every expanded update |
| `frozen/MANIFEST.json` | Parent, provider, artifact, profile, and parameter bindings |
| `frozen/SEED-RECEIPT.json` | Recorded sorted matching and two seed discovery passes |
| `frozen/MATCHING-RECEIPT.json` | Recorded expanded passes and exact finite totals |
| `reproduce.py` | End-to-end parameterized hosting replay |
| `reuse_owners.py` | Optional original-family seed constructor |
| `expand_owners.py` | Exact greedy matching over all eligible physical families |
| `audit_frozen.py` | Independent feasibility and final callwise fixed-point audit |
| `PROOF.md` | Capacity, exchange, majorization, and integration arguments |

The expanded matcher is individually optimal for each call when other calls
are fixed, for every concave remainder cost simultaneously. The frozen map is
a verified coordinate fixed point. **No joint global optimality claim is
made.** New local algebra, changed center carriers, phase compatibility,
actual owner charts, the finite invoice, and exact exponent admission remain
the responsibility of the package's global verification pipeline.
