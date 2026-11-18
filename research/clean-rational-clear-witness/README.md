# Clean rational CLEAR witnesses: exact validity flags and reversible cleanup

This no-kappa contribution implements a finite-width rational-witness circuit. Its useful boundary is precise: the target output and diagnostic bit are both zero **if and only if the exact signed integer witness relation holds**. Invalid fraction, overflow or target mismatch is retained rather than mistaken for erasable zero. Internal work bits are uncomputed for every input.

## Why a target-zero check alone is insufficient

| Input | Naive low-bit floor check | Required behavior |
|---|---|---|
| N=1, D=2, t=0 | floor(1/2)=0, apparently clean | Fraction flag=1 |
| signed width 3, N=6, D=1, t=-2 | 6 mod8 equals encoded -2, apparently clean | Overflow flag=1 |
| N=2, D=1, t=3 | Different target/witness | Nonzero target mismatch |

These are counterexamples to an incomplete **local erasure criterion**, not reachable-input counterexamples against the project or any contributor. The included negative controls exercise all three cases.

## Exact result
For immutable signed w-bit donor limbs x_i, fixed integer a_i, D>0 and signed target t, put N=sum(a_i*x_i), q=floor(N/D). The generated X/CNOT/Toffoli network returns:

1. unchanged donor bits;
2. target XOR (q modulo 2^w);
3. a diagnostic for nonzero N mod D or q outside signed w-bit range;
4. every internal ancilla restored to zero.

Hence target_output=0 AND diagnostic=0 iff N=D*t. PROOF.md gives the bound and division-loop invariants and explains compute/copy/uncompute. This is an all-bitstring proof for this local circuit, not an assertion that every rounded caller state lies in its zero-output domain. Standard Boolean arithmetic and compute-copy-uncompute are prior methods, not new inventions here.

## A reproducible public-project coordinate
The package reconstructs the published #7669 word from its unchanged predecessor and edit, pinned to eaef5d1580e5761feaed09262b964871f3e5f553. At zero-based event 88937, CLEAR target 1502 is in chart 353; its certificate is donor 1072 minus donor 500, both live in chart 359.

Using the unchanged published exact native interpreter, all 512 complex source basis columns determine the real output at address 0. That row is

    (u_Re0 + u_Re102 + u_Im0 + u_Im102
     - v_Re0 - v_Re102 - v_Im0 - v_Im102) / 2,

where u=field 1072 and v=field 500. This gives the concrete integer coefficients [1,1,1,1,-1,-1,-1,-1], D=2 used by the full-width circuit. A wrong global phase is rejected.

This is one selected output row. The original interpreter and reconstruction routine are reused explicitly, not presented as independent implementations. No full native application or original complete scientific suite is rerun.

## Reproduce
Python 3.10+ standard library, no network or external checkout:

    python -I -B verify.py

Expected marker: PASS_CLEAN_REVERSIBLE_WITNESS. RESULT.json and EXAMPLE-PROVENANCE.json are regenerated. -O is explicitly rejected because these tests use assertions. This differs from packages supporting optimized replay; we do not claim -O support. VENDORED.json authenticates retained source bytes; MANIFEST.json covers the final package. Hashes are provenance receipts, not eligibility rules for other candidates.

Evidence includes 308 baseline cases, 100 additional random contracts, three false-clean/mismatch controls, 100 arbitrary-initial-state inverse roundtrips, and complete 1076-bit circuit runs at signed maximum, signed minimum, fractional and overflow inputs. The first two edge runs are clean; the latter two preserve diagnostic 1 even when target bits become 0. An earlier independent agent audit additionally exercised 1686 source/target pairs and 100 inverse roundtrips; its unchanged receipts are clearly marked version 1. No human or formal-kernel review is claimed.

## Space and gate count for the displayed row

| Source width | Arithmetic width | Input bits | Internal ancillas | Complete gate count |
|---:|---:|---:|---:|---:|
|4|9|32|765|2425|
|1076|1081|8608|86525|277929|
|1108|1113|8864|89085|286153|

Counts are generated from actual gate lists and include output copying plus inverse execution. Internal ancillas exclude immutable inputs and target/diagnostic output wires.1076-bit edge cases execute the actual network; widths 4 and 1108 in this table are generated resource counts. Arithmetic width alone is not total workspace. These are X/CNOT/Toffoli counts, not tape actions, an optimized implementation claim or a physical cost bound for all CLEARs.

## Credit, overlap and limits
The published composition, certificates and native/caller/helper lineage are prior project work, including SYLforge's #7669. Unchanged PROVENANCE.md and LICENSE accompany the reused source; native_verify.py retains its own attribution. Ali Romman's #7671 sharpened the distinction between rational identity and a specified rounded execution. #7680 distinguishes completed-state precision from temporary product precision. Those observations motivate precise contracts here; their proofs and results are not claimed as ours. REFERENCES.md records pinned comparisons and how they shaped this document. Prepared with OpenAI Codex assistance.

This contribution adds the runnable local clean-witness implementation, explicit false-clean controls and resource accounting. It does NOT replace existing ideal CLEAR checks or impose a new mandatory verifier. No kappa change, selected frontier update, supplier admission, source-program error or unchanged-cost claim follows.

Open closure steps: prove which rounded states satisfy the relation; bind every required row and coherent extent; map gates and zero-workspace service to the project's physical tape model; account for reset/backing and complete schedule costs. If x_t=L_t*z+e_t and R_t*L_t=0, the remaining rounded residual is R_t*e_t. Fresh helper payload must not be silently treated as zero scratch. See PROOF.md for the precise boundary.

## Open next questions

1. Which actual rounded producer states satisfy this exact witness domain? First bind one reached input lattice; blocked by the producer contract.
2. What complete physical tape cost implements the generated gates and zero workspace? First lower one source-bound row and count routing/reset; no free scratch or supplier admission is assumed.
3. Can a smaller reversible arithmetic circuit preserve this validity/cleanup interface? Compare complete gates, outputs and scratch against this explicit baseline, not just arithmetic width.

## Registered replay and scope

From the repository root: `python -B scripts/research_package.py --package research/clean-rational-clear-witness`. The package uses the existing runner without changing shared code. TASK.json narrows the supplier-boundary audit to this local enabling implementation. Base e54523517d0f03e58352e647c403a5af3e525a57; priority revision 8; selected #7000 unchanged.

## Submission validation and CI boundary

Local CPython 3.12.14 on Windows: standalone and registered replay passed. The unchanged base test `CurrentCiNavigationTests.test_current_ci_section_matches_selected_record` fails because docs/ci-verification.md still names frontier6030 while the selected record requires `make frontier7000-verify`. This package changes neither file nor any shared workflow. No hosted CI success is claimed; a shared planning failure may skip scientific replay. See REFERENCES.md for the latest related-work refresh, including #7681's distinction between reusable homes and full initialization/retirement services.
