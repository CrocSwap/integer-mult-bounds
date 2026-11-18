# Signed replay of the #7658 role-379 candidate

The observed application used exact caller PR #7113 at head `07a76c5e2738882c0cb322278e56f6cae3c9885d` and the role-379 word with decoded SHA-256 `f0753b6614b2d351723dddc307a39b6ecd748a43008c6fdb9335b01feeec9669`. It regenerated and replayed the full 17-call signed program. The complete invoice has 108,581 paid positions, 22,461 productive fields and rank surplus 1,424. The verified application claim is conditional κ ≥ 0.0037170835567. The independently directed invoice crossing interval is [0.0037170835568, 0.0037170835569]. [#7113 signed caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) [#7658 source](https://github.com/CrocSwap/integer-mult-bounds/pull/7658)

The observed exact application checked all 3,030 paid and helper maps, 104 main boundaries, 234 CLEARs and 1,156 reserved owned banks. All 54 strict and four functional outer predicates passed. It charged 815,804,876 conservative ordinary units including native-scale conversions, and bounded 83,895,232 scalar services, 294,932 map slots and 25,147,082,048 elementary records. Each catalogue slice rejected a wrong phase. Further controls rejected aliased main owners, a probe at the lower crossing, stale native launch bindings and seven tape mutations.

## Reproduction

Use Linux CPython 3.12 and the entire role-379 package. From that package's root, the following command verifies the exact #7113 source closure and the retained prerequisites without launching the scientific replay.

```sh
python3.12 -I -B application-evidence/signed-replay/replay.py --core . check
```

The next command rebuilds the candidate using the core package and runs the complete signed application in a fresh directory.

```sh
python3.12 -I -B application-evidence/signed-replay/replay.py --core . run --out /tmp/role379-signed
```

Use a fresh output directory for each run. By default the harness picks one available CPU and uses the original 2 GiB per-process address-space and 900-second signed wall bounds. The original signed stage took 305.15 seconds with peak RSS 122,868 KiB. The launcher unpacks a bounded local source capsule and restores the layout expected by the exact signed driver, using the core package's pricing code and the application appendix's retained native, grid and ordinary receipts. It runs offline from the complete package.

The annex stores the original signed gzip once in `data/WORD.json.gz` at SHA-256 `4e9cd9cc70a5423db44f870b35d8d6da9ac5746aa352f3af1420443f6dda350e`. The verifier checks that compressed pin and its decoded pin, independently rebuilds the candidate through the core verifier, and compares every decoded byte. It then passes the original gzip to the unchanged signed driver. The rebuilt gzip may differ across compressors. The transport controls accept a gzip with an altered header, modification time and compression level when the decoded word is identical. They reject a one-byte change to the decoded word.

When `--out` is omitted, the command uses a fresh temporary directory and prints the candidate hash, checked claim and catalogue count after comparing the replay. The registered command can use `run --wall 560` in its 600-second verification slot.

The run produces the raw driver outputs and child receipts under the new directory. `REPLAY-RESULT.json` requires agreement with the observed scientific result, omitting elapsed time and stderr hashes affected by the relocated traceback paths. `data/OBSERVED.json` records original digests, resource measurements and all 14 child receipts without workspace paths. The source capsule retains the exact 68-file verification freeze used by the observed driver. Its 67 upstream members carry their exact Git blob and SHA-256 pins. The local predecessor runner within that freeze is authenticated as provenance and kept inert. The two pricing engines use the copies already in the core package. The archive includes the original caller's Apache license and the retained nested notices.

## Open next questions

The conditional application requires the five framework assumptions and the inherited common-U owned-bank contract covering all 234 lifetimes at the same tariff. A supplier implementation must still establish that contract, its backing and return semantics, and the compiler and analytic recovery obligations. The replay evaluates the finite model under those assumptions.

## Credit

Rohan Arun authored the signed caller. DreamingOfClouds authored the #7658 word and its #7641 predecessor. The application uses their sources and the inherited work credited in the retained #7113 archive, including Ali Romman and SYLforge. Clear1nsight prepared the role-379 construction, independent application and relocation with substantial OpenAI Codex assistance. Apache-2.0.
