# Frame-aware native construction tools (no new κ)

No improved multiplication saving was established in this session. The rechecked conditional baseline is kappa = 0.00302015 from #4470, not a change to the selected frontier. Canonical main was frozen at f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc; the live PR refresh covered additions through #4533 (whose stated scope is a compiler improvement at unchanged kappa).

Four useful sufficient construction results are preserved:

1. **Noncommuting controller stages:** the fixed p16 operator identity holds without pairwise stage commutation, provided the stages commute with the invertible central query. The standalone free-associative certificate checks all 1,024 matrix entries, dyadic scalar boundaries and two rejection controls. Read noncommuting-controller/PROOF.md.
2. **Unequal-chart monomial adapters:** an exact scalar monomial block can permute physical buffers and coordinate tags, including all dyadic coefficients, without forcing a common chart. Read MONOMIAL-ADAPTER.md.
3. **Complete owned-response retiming:** scalar contacts may be retimed when every live C-wire transition is paid, warp phases and charts are preserved, and the final ABI and erasure are restored. Read OWNED-C-RETIMING.md.
4. **Deferred linear responses:** responses may be propagated symbolically when their coefficients vanish at all intervening warps and captures. For this native word, each of eight responses has 56 final Y entries; all 5,056 coefficients and zero-at-warp conditions check exactly. Read LAZY-RESPONSE.md. Eight simultaneous owned buffers and all final transports still require payment.

These are informal algebraic proofs with exact finite certificates, not Lean formalizations or independent human acceptance. Classical identities and predecessor constructions retain their attribution. No priority over all literature or historical PRs is claimed.

## Replay

From the repository root, run the registered check:

    python3.12 scripts/research_package.py --package research/frame-aware-native

Or run the self-contained check without Git or network access:

    python3 -I -O -B research/frame-aware-native/verify.py

The two component checks, from this package directory, are:

    python3 -I -O -B noncommuting-controller/verify.py
    python3 -I -O -B verify_lazy_response.py

Both scripts authenticate serialized input bytes before parsing. Tested with Python 3.12.10 on Windows; no Linux execution is claimed. The copied full_identity_rebuild.py is a source anchor, not a standalone executable target; owned-C-source.json records its upstream path and hash. NATIVE-SOURCE-HASHES.json records constructing source pins. BASELINE-INDEPENDENT.json and AUDIT-CONTROLS.json describe separate original-environment native checks, rather than claiming the two commands above repeat the entire native audit.

## Rejected candidate

The apparent replacement of 56 rank 1 plus 56 rank 4 jobs by 56 rank 5 jobs was rejected because its optimizer omitted changed owned-C transport costs. Corrected reruns produced no gain. That rejected bill is excluded from this package. This contribution claims construction lemmas and finite certificates, not an improved κ.

An actual improved complete invoice, exact native endpoints in both orientations, new absolute-phase receipts, tail/compiler arithmetic and the inherited physical, analytic, precision, tape, stock, prime and recovery premises remain necessary for the requested saving.

## Predecessor credit

Cinna Davis's #4470 (b9a13c1673e0e9697de410de16e8bbf3207a7363), #4440, #4441 and #4447 supply the native/controller lineage. Retain zxv's native, higher-moment and logarithmic compiler work, Jacob Alan Sussman's #4268 mixed-target recursion, and the original scalar, Clifford, geometry, physical and outer-ledger notices. #4516 independently replays the commutative controller; #4483 and #4532 concern compiler and critical-root improvements without a new invoice. Existing SymplecticTI inverse-dual/Levi lemmas inspired basis searches; tensor-isomorphism equivalence itself supplied no unpriced gain.

Prepared for Dugongue with substantial OpenAI assistance, using one primary worker and three collaborating workers. Apache-2.0.

## Open next questions

Can consistent owned-response placement and changed scalar graphs reduce the complete paid moment? Begin with the retiming theorem, serialize every C-wire edge and exact phase, and recredit changed whole-helper jobs. A fully checked cheaper invoice remains missing; the existing certificates do not assume one.
