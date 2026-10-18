# T185 attains the shared-kernel packing optimum

**Conditional κ = 0.001720100805416885927944 − 10⁻⁴⁶ − 10⁻⁷⁰.**

The exact increase over the full pinned PR #2857 headline is **4.176732053326972 × 10⁻⁹**. The new allocation attains the fractional packing optimum at the moment root for the explicitly fixed current native words, helper inventory and bin capacities. This is a constructed optimum in that model, not a maximum over all multiplication algorithms or future native circuits.

## The compatible combination

| Ingredient | Source | Actual use |
|---|---|---|
| Cheaper staged shared kernels | Yiyang/Lyy-iiis, PR #2857 | Both complete changed words, including compensation and inverse cleanup. |
| Dirty A-phase entry and prior native improvements | Philippe Van Velzen, PR #2853; Jeremy Kothe, PR #2833; their retained lineage | Source and ABI precedents, with the shared-kernel schedule replacing the more expensive alternative for the same quartet. |
| Cost-neutral vacancy paths | Marius-Paul Dumitrean, PR #2856 | A checked width 9 relay moves the unique unused rank 9 to a useful source window. |
| Concentration and interleaved copies | PR #2848, PR #2855 and retained replica contracts | Five exact copies, followed by filling all five rank 9 vacancies from one actual donor. |
| Exact fixed-inventory packing relaxation | PR #2857 precedent and the new symbolic certificate | A matching rational primal and dual across every one of the 1,163 capacity-feasible patterns. |

The construction has ten literal whole-role moves. In each of five copies, helper 208 at source call 320 moves from bin (28,16,76) to (35,16,37), transferring the vacancy without changing its paid profile. Five actual width 9 roles from the capacity 48 donor (32,13,94) then fill the five resulting vacancies. Interleaving preserves every replica's source-event order; the literal full checker establishes the strict bridge-aware windows, physical-family separation and all masks.

Relative to five complete incoming profiles, the entire cost changes by

    H₄₈ − H₃ − 5H₉ < 0,  where Hᵣ = rᵖ and 0 < p < 1.

The inequality follows from strict subadditivity and 48 = 3 + 5 × 9. Native paid work is included and unchanged. All 679,320 roles in 1,665 calls, live stock 165,760 and physical stock 166,250 are counted. The final profile is

    {1:4029300, 2:1068930, 3:458874, 4:213120,
     5:65490, 8:13320, 48:66896}.

## Why this reaches the packing bound

Each replica has bin counts {8:672, 16:448, 32:448, 48:448} and nine copies of the fixed 408-helper inventory {4:26, 5:2, 7:62, 8:84, 9:234}. Every integral packing, regardless of its chronology, induces a feasible point of the same fractional pattern program after dividing by its replica count.

`review/PROOF.md` gives exact rational primal multiplicities and explicit symbolic dual prices. `review/profile_lp_certificate.py` checks all 1,163 patterns, handles 11 tight identities symbolically, and proves every other inequality by directed integer series uniformly around the moment root. The actual T185 histogram equals that rational optimum multiplied by 185. Combined with the literal causal witness, this proves attainment rather than just an optimistic numerical cap.

Every paid rank is at most 48 < 73, so each feasible normalized moment increases strictly with the saving parameter. The exact dual upper-endpoint check bounds all packings in this fixed model. The independent root bracket is [0.00172010080541688592794400, 0.00172010080541688592794401]. The released outer headline uses the conservative 24-digit endpoint above. A finer moment bracket is not silently promoted to a finer outer claim.

## Fast offline replay

Python 3.12 or newer with its standard library suffices. Keep assertions enabled. From this folder:

```text
python -B tools/verify_package.py --hash-only
python -B tools/verify_package.py --work ../t185-check
```

Choose a fresh external work directory. This authenticates the complete file inventory and hashes, regenerates all five data files byte-for-byte without a solver, runs the separate source-event and exact rational moment auditors, runs the second independently implemented owner/provider/moment check, and regenerates the complete fixed-model primal/dual certificate. The source words and baseline allocation are included in `vendor/pr2857/` as byte-preserved immutable inputs. The package remains unchanged during replay.

`CONSTRUCTION.md` contains the explicit ten moves and universal paid-cost proof. `review/PROOF.md` defines the restricted optimality model and dual. `review/SOURCE-COMPATIBILITY.md` records the separate local operator/frame review. Review by Codex agents is identified as such; it is not independent human peer review.

## Complete fresh native and outer replay

Fetch the exact original PR #2833 source into a fresh external directory:

```text
node --use-system-ca tools/fetch_source.cjs ../original-source
```

This checks all 541 manifest entries at immutable head `e9307b48d7d1b690939935ecef0f8e524e6d92f4`, using normal certificate verification. It does not change an installed checkout. `tools/materialize_source.py` can instead export exact local Git objects.

For the complete replay, use Python 3.13 with NumPy, SciPy, SymPy and mpmath. The actual runs used NumPy 2.5.4, SciPy 1.18.1, SymPy 1.14.0 and mpmath 1.4.1; gmpy2 and psutil were absent. On Windows, create an isolated interpreter that reuses those installed packages read-only and gives generated `Path.write_text` output an LF default:

```text
python -B tools/make_lf_runtime.py --out ../t185-runtime
../t185-runtime/Scripts/python.exe -B reproduce.py --source ../original-source --work F:/proof/t185-run --jobs 3
```

Use a short fresh absolute work path. On a POSIX system with LF defaults, run `python -B reproduce.py` directly with the same arguments. The isolated helper changes no global configuration or validator predicate. Native bootstrap jobs may overlap. The complete admission runs its mutation controls in one process: the inherited parallel sharder shares a temporary receipt filename and the first parallel attempt hit a Windows receipt-read failure. Serial replay retains every control and predicate. See `evidence/REPLAY-NOTE.json`.

The default wrapper freshly bootstraps the retained source/native/parent evidence, builds the byte-exact 547-entry shared-kernel overlay, runs both changed native chains freshly, and runs complete admission. `--prepared-retained` explicitly reuses a completed authenticated bootstrap; the strict preparer still checks the entire cache, exact retained source, native word identities and all 16 retained parent stages. One exact receipt pin is rebound to that bootstrap, with a derivation receipt; no semantic predicate is removed. `--dry-run` authenticates inputs and prints commands without replay.

The actual campaign ran four fresh predecessor chains and the retained parent, then both changed shared-kernel chains freshly; the final admission explicitly reused the authenticated retained evidence. The underlying complete admission and new native stages were executed. The published orchestration wrapper's command plan is separately preflighted; a second cold replay of that wrapper is not claimed.

## Scope and source lineage

The root `CLAIM.json` and `evidence/RELEASE-RECEIPT.json` are the authoritative outer headline. Legacy supplier receipts may retain historical κ/status labels; their current source manifests, complex endpoint and outer arithmetic are explicitly bound.

All inherited all-size compiler, common-label/source-access, mutable-source, hosting, precision/tape, recovery, ordinary recursion, BIT and analytic-transfer assumptions remain. This is informal mathematics plus exact finite computational certification, not a new unconditional multiplication theorem or Lean kernel/axiom audit. The fixed packing optimum does not cover different native words, helper inventories, capacities or controllers. No measured runtime or hardware gain is asserted.

See `CREDITS.md` for the relevant PRs, exact source heads and overlap scope; all original licenses and notices remain. `UPLOAD.md` gives the branch, PR title/body and short hash-checked upload batches. The canonical Lean tree and authoritative DAG remain on D:.

## Open next questions

The fixed-word gap is closed near the moment root. A further gain would require an actual changed native/consumer contract with a better complete paid bill, or another changed source premise with a proved applicable normalization. The contract must account for arbitrary dirt, restoration, transport and precision before its benefit is counted; none is assumed here.

A separate useful direction is a sufficient all-size compiler or precision/tape transfer theorem for the actual words. This package does not settle that inherited question. `TASK.json` records these directions and the bounded completed scope. `VERIFY.json` registers the standard-library finite/LP replay for the repository's Python 3.12 research-package CI; the actual campaign ran Python 3.13.5, while a full native replay uses the separately documented dependency runtime.
