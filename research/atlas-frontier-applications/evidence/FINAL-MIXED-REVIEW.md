# Final independent review of the mixed cover/fibre certificate

**Disposition:** no unresolved mathematical or source-loading issue found in the reviewed finite magnitude certificate. The admitted payload remains 2048 bits. This review does not certify a completed 256-bit release, a changed paid moment or a new kappa.

Reviewed immutable versions:

- `metric/mixed_fibre_certificate.py`: SHA-256 `c9a9d0553c6242d28af988327381043c7d15c173f0f31ba924910021a9c6a09a`.
- `metric/CURRENT-RESULT.json`: SHA-256 `e602e8cdf19895ae8c53aaf70e2889b98e73745662736d0bc2fff3771656a8a6`. Its bytes exactly equal the final `mixed-current-03/RESULT.json` receipt.
- `metric/MIXED-FIBRE-PROOF.md`: SHA-256 `317ec397b53622d3ed559a7929f9de5f15c68e8b07e0e953a5944754dbab8f0f`.

## Authenticated source execution

The earlier stale-bytecode concern is fixed. `load_module` reads the source bytes, checks their SHA-256 against the supplied expected digest, constructs a fresh `ModuleType`, and executes `compile(body, filename, 'exec')`. The production callers supply the expected digest for both endpoint and stream modules. No `SourceFileLoader` selects dependency bytecode in this path.

The added control constructs a timestamp-based `.pyc` with the current interpreter magic, matching source timestamp and source size, but a different marker in its code object. I independently inspected its header and unmarshalled constants: it is the intended timestamp-valid stale-code fixture. The receipt records that authenticated source wins. This closes the identified loader gap without changing the mathematical predicates. The final receipt contains 13 controls, including this one.

## Primitive and ownership semantics

The checker rejects unknown native event tags and shapes, unknown numerical phase markers, noninvertible selected-bit address matrices and unexpected monomial fields. Actual `phase` events are known section markers; numerical phases live in the exact recipes. Scalar add, copy, scale, clear and Horner work are included in the norm envelope. Dense child/frame maps act on the selected-bit fibre; static owner charts permute cover labels independently of that selected address.

I independently inspected the actual current provider programs and recipe schema before this final revision: both providers contain only the classified event kinds; every scalar coefficient is dyadic; the private centre work has first and terminal clears; all 72 zero-buffer lifetimes close; and each provider has 6,278 Clifford plus 150 residual monomial recipes with invertible binary address matrices and unit-modulus phase data. The final classifier additionally retains fresh five-stage native receipts and exact arbitrary-dirty endpoints in both orientations. Canonical provider paths are explicitly tied to the completed native receipt, and all pinned primary source files are checked.

The final receipt covers 1,365,984 helper roles, 3,348 calls and 16,242 static orthogonal charts for the actual 372-replica witness. Owner descriptors have a closed integer-field schema; charts use fixed port, child, offset, width and spectator data. The check prevents two live roles in one invocation from sharing a physical family and excludes active-data aliasing. The source controller has a closed global event inventory and the literal nine local calls and nine bridges. Complete source and native-cache hashes are guarded before and after checking. Other admission checks still own the full owner-window and physical realization obligations.

## Sufficient norm conclusion and its limit

The norm takes the maximum over cover labels separately for each physical family, then takes the direct sum over ports. Static cover permutations and unitary maps inside each selected-bit fibre preserve this norm, including port-dependent charts. Arbitrary unitary averaging across cover labels would not preserve it and is expressly excluded. The distinction is substantive, rather than an inference from generic full-register unitarity.

The stream majorant and exact weighted Schur witness give the stated factor below 16. With the selected-bit input conversion, physical-family aggregation, local scalar envelope and retained margins, the arithmetic is 121 actual magnitude bits and 179 conservative magnitude bits. The proposed 256-bit value bounds that magnitude reserve only. No norm argument shortens the denominator chain: all separate arithmetic-depth, primitive, mass, C0, precision, tape, halving, recovery and ordinary-recursion conditions remain required. A full changed admission must verify those conditions before adopting a smaller paid payload.

This was a source-semantic and informal mathematical review, with small header/hash checks only. I did not rerun the long owner census, native chains or complete release, edit the classifier or launch Lean. The public result remains a sufficient finite magnitude certificate under the retained primitive interfaces, with the inherited 2048-bit release unchanged.
