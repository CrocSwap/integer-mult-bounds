# R420 quad 4: all-length reverse-positive amplification minimum is 9

**Scoped mathematical proof and exact instance certificate. No new kappa.**

For Chris Barber's fixed six-register positive integer target in PR1058, every finite positive ADD factorization has reverse-positive cleanup infinity norm at least **9**. The existing 11-ADD witness from PR1266 attains 9. This closes the longer-word question explicitly left open by that shortest-word enumeration; it supplies no new circuit witness or gate-minimum search.

The decisive inverse row, in zero-based register 1, is `[-1, 0, 1, -3, 1, -1]`. Its absolute row sum is 7. Every reverse-positive product has diagonal at least one and is congruent to the signed inverse modulo two. Its zero inverse diagonal therefore forces an even positive cleanup diagonal, at least two, raising the row floor to **9**. The [proof](PROOF.md) derives all three invariants for arbitrary word length. Finite replay checks the exact instance and the attaining witness.

## Reproduce

From the repository root, using Python's standard library:

```sh
python3 -I -O -B research/r420-all-length-cleanup-floor/verify.py
```

Expected:

```text
PASS_R420_ALL_LENGTH_CLEANUP_FLOOR lower=9 attained=9 adds=11 columns=6 boolean=64 controls=5
```

The verifier checks archive hashes, reconstructs the target and signed inverse with two exact engines, checks the lower-bound matrix, replays the witness and all 64 local Boolean inputs, and compares every field of [CERTIFICATE.json](CERTIFICATE.json). The engines use matrix multiplication/rational inversion and separate primitive basis-column ADD/SUB replay. SUB is an inverse-checking oracle, outside the allowed factorization alphabet.

Run the meaningful mathematical and packaging controls with:

```sh
python3 -I -O -B research/r420-all-length-cleanup-floor/test_package.py
```

The regression domain contains every three-register ADD word through length five (9,331 words), an actual 19-ADD same-target predecessor word, a three-gate zero-diagonal fixture, invalid gate alphabets, a free-SWAP scope counterexample, corrupted archives/receipts, refused receipt overwrite, and optimized replay after relocation. This finite domain tests the implementation; the all-length theorem rests on the written algebraic proof.

`VERIFY.json` opts into the repository's bounded Python 3.12 replay hook. `TASK.json` records the declared scope change from the helper-interface catalogue card. `SOURCES.json` contains the exact base, Git blobs and SHA-256 pins, with self-contained frozen archives for the pending predecessor inputs. The verifier works without Git or network access after this directory is copied.

Local checks passed on Python 3.14.7, and the complete registered replay passed on Python 3.12.15. The standalone runtime release, asset and published digest are recorded in [VALIDATION.json](VALIDATION.json). Remote CI and a selected cold replay are separate checks.

## Exact result and cost scope

| Quantity | Value |
|---|---:|
| Absolute-inverse infinity norm | 7 |
| Positive diagonal and parity floor | **9** |
| Attaining reverse-positive infinity norm | **9** |
| Existing PR1058 word's reverse-positive norm | 11 |
| Attaining word length | 11 ADDs |
| Longer same-target fixture | 19 ADDs, reverse-positive norm 46 |

The lower-bound row sums are `[2, 9, 3, 7, 3, 2]`. The witness row sums are `[2, 9, 5, 7, 3, 2]`. The complete matrices and operations are in the certificate. The objective is the positive bound map used for cleanup magnitudes; the signed inverse has its own norm.

The witness uses six existing registers at the inherited quad frame 306, with 11 forward ADDs and 11 literal reverse bit-cleanup ADDs. This proof adds no source access, helper, frame change, COPY/ERASE, restoration or recursive child. It does not reprice the full native word. Its norm optimum is for a common incoming coordinate bound; the witness increases some entries of the predecessor bound matrix, so it need not improve a nonuniform entering budget.

The target remains a historical R420 local transfer. Full native/frame/precision bindings, selected-supplier adoption, hosting and outer assembly require their corresponding checks. The selected bit side is nonbinding at this base. No full multiplication theorem or proof-assistant formalization is claimed.

## Open next questions

Does either of PR1266's two norm-9 cleanup matrices lower the complete PR1058 word's positive-prefix invoice for its actual nonuniform incoming bounds? This would turn the local optimum into an application-specific benefit. A feasible first step is to substitute each pinned 11-ADD witness into the original constructor, rebuild literal C, and compare both orientations using the unchanged exporter and native checker. The blocker is that the matrices trade entries rather than dominate the predecessor entrywise, and composition with the selected R439 word is a separate question. The structured question is in `TASK.json`.

## Sources, credit and assistance

Base: `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`. The selected record and originating catalogue are pinned as historical provenance, and remain unchanged. Coordination: [discussion 1279](https://github.com/CrocSwap/integer-mult-bounds/discussions/1279); assignment seed **0**, from OS randomness.

Chris Barber (@cbarber1), [PR1058](https://github.com/CrocSwap/integer-mult-bounds/pull/1058), head `d148d200f2d64c90504fa3a9608e455aaa4c0c21`, supplies the target and gate-minimum construction. Cinna Davis (@1337isnot1337), [PR1266](https://github.com/CrocSwap/integer-mult-bounds/pull/1266), receipt source `8edfb5d97aea03d26316964f35359d1864731dbe`, supplies the reused norm-9 witness and shortest-word cleanup envelope. The latter receipt remains byte-identical after an attribution-only follow-up. The underlying R420 word, helper architecture and native interface are by eumemic in PR543; all further lineage in the unchanged `inputs/PR1058-NOTICE.md` is retained. PR1194's semantic-D contract and PR1253's first-contact kernel classification informed task selection; neither is a mathematical dependency of this proof.

New work by **Cinna Davis**, with substantial **OpenAI Codex assistance** in the proof, exact checks, tests and packaging. The two engines are part of this same AI-assisted contribution, with no independent human review implied. Apache-2.0; see `LICENSE` and the retained predecessor notice.
